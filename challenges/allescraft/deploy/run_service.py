#!/usr/bin/env python3
import atexit
import os
import sys
import time
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

import docker
import requests
from docker.errors import NotFound

PREFIX = os.getenv('PREFIX', 'allescraft')
NUM_INSTANCES = 1 if len(sys.argv) < 2 else int(sys.argv[1])

client = docker.from_env()

# noinspection PyShadowingNames
def build_images():
    def build_image(path, tag):
        return client.images.build(path=path, tag=tag)

    errors = []
    images = {}
    images_to_build = [
        ('lobby', os.path.abspath('./lobby'), f'{PREFIX}_lobby:latest'),
        ('proxy', os.path.abspath('./proxy'), f'{PREFIX}_proxy:latest'),
        ('server', os.path.abspath('./server'), f'{PREFIX}_server:latest'),
    ]

    with ThreadPoolExecutor(max_workers=len(images_to_build)) as executor:
        future_to_name = {
            executor.submit(build_image, *x[1:]): x[0] for x in images_to_build}
        for future in futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                image = future.result()
            except Exception as e:
                print(f'Error building {name}:', e, file=sys.stderr)
                errors.append(e)
            else:
                print(f'Successfully built {name}')
                images[name] = image[0]

    return images, errors


# noinspection PyShadowingNames
def create_networks():
    # noinspection PyUnresolvedReferences
    # noinspection PyShadowingNames
    def create_network(name, config, subnet):
        ipam_pool = docker.types.IPAMPool(subnet=subnet)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        return client.networks.create(name, **config, ipam=ipam_config)

    errors = []
    networks = {}
    common_network_options = {
        'attachable': True,
        'internal': True,
        'check_duplicate': True
    }
    network_configurations = [
        (f'{PREFIX}_lobby', common_network_options, '10.0.0.0/24'),
        *[(f'{PREFIX}_server_{num}', common_network_options, f'10.0.{num + 1}.0/24') for num in range(NUM_INSTANCES)]
    ]

    with ThreadPoolExecutor(max_workers=len(network_configurations)) as executor:
        future_to_name = {
            executor.submit(create_network, *x): x[0] for x in network_configurations}
        for future in futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                network = future.result()
            except Exception as e:
                print(f'Error creating network {name}:', e, file=sys.stderr)
                errors.append(e)
            else:
                print(f'Successfully created network {name}')
                networks[name] = network

    return networks, errors


# noinspection PyShadowingNames
class Server(Thread):
    _stop_flag = False
    error_count = 0
    __common_options = {
        'detach': True,
        'remove': True,
        'tty': True,
        'stdin_open': True
    }
    daemon = True

    def __init__(self, image, name, networks, extra_options=None, kill=True):
        super(Server, self).__init__()
        self.name = name
        self.kill = kill
        self.image = image
        self.server = None
        self.networks = networks
        self.extra_options = extra_options if extra_options else {}

    # noinspection PyBroadException
    def run(self):
        while not self._stop_flag:
            try:
                if self.server is None:
                    self._start_server()
                    self.error_count = 0

                try:
                    self.server.reload()
                except NotFound:
                    # Server dead (presumably)
                    self.server = None

                if self.server:
                    self.server.wait(timeout=1)
            except (requests.exceptions.ConnectionError, NotFound):
                pass  # .wait() timeout or container dead
            except Exception as e:
                self.error_count += 1
                print(f'Error in server {self.name}:', e, file=sys.stderr)
                if self.error_count > 5:
                    raise Exception(f'Server {self.name} exceeded error limit')
                time.sleep(1)  # Wait at least a second before retrying

        if self.server is None:
            return

        try:
            self.server.reload()
        except Exception:
            return

        try:
            if self.kill:
                self.server.kill()
            else:
                self.server.stop()
        except Exception as e:
            print(f'Error stopping server {self.name}:', e, file=sys.stderr)
            return

        print(f'Stopped server {self.name}')

    def stop(self):
        self._stop_flag = True

    def _start_server(self):
        print(f'(Re-)creating server {self.name}')
        self.server = client.containers.run(
            self.image, name=self.name, **self.__common_options,
            **self.extra_options)

        for network in self.networks:
            network['network'].connect(
                self.server, **network['options'])


# noinspection PyShadowingNames
def cleanup(servers, networks):
    print('Stopping servers...')
    for server in servers:
        servers[server].stop()
    for server in servers:
        try:
            servers[server].join()
        except Exception as e:
            print(f'Error stopping server {server}:', e, file=sys.stderr)

    print('Removing networks...')
    with ThreadPoolExecutor(max_workers=len(networks)) as executor:
        future_to_name = {executor.submit(networks[x].remove): x for x in networks}
        for future in futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                future.result()
            except Exception as e:
                print(f'Error removing network {name}:', e, file=sys.stderr)
            else:
                print(f'Successfully removed network {name}')


if __name__ == '__main__':
    try:
        print('Building images...')
        images, errors = build_images()
        if len(errors) > 0:
            print('Error building images, exiting')
            exit(1)

        print(f'Creating networks...')
        networks, errors = create_networks()
        if len(errors) > 0:
            print('Error creating networks, exiting')
            cleanup([], networks)
            exit(1)

        print(f'Starting servers...')
        servers = {
            f'{PREFIX}_lobby': Server(
                image=images['lobby'], name=f'{PREFIX}_lobby',
                networks=[{
                    'network': networks[f'{PREFIX}_lobby'],
                    'options': {
                        'ipv4_address': '10.0.0.3',
                        'aliases': ['lobby']
                    }
                }]),
            f'{PREFIX}_proxy': Server(
                image=images['proxy'], name=f'{PREFIX}_proxy',
                networks=[{
                    'network': networks[f'{PREFIX}_lobby'],
                    'options': {
                        'ipv4_address': '10.0.0.2',
                        'aliases': ['proxy']
                    }
                }, *[{
                    'network': networks[f'{PREFIX}_server_{num}'],
                    'options': {
                        'ipv4_address': f'10.0.{num + 1}.2',
                        'aliases': ['proxy']
                    }
                } for num in range(NUM_INSTANCES)]],
                extra_options={
                    'ports': {25565: 25565},
                    'environment': {
                        'NUM_SERVERS': str(NUM_INSTANCES),
                        'IP_TEMPLATE': '10.0.%d.3',
                        'IP_START_VALUE': '1'
                    },
                    'volumes': {
                        os.path.abspath('./config.json'): {
                            'bind': '/bungeecord/plugins/ALLESQueue/config.json',
                            'mode': 'rw'
                        }
                    }
                }, kill=False)
        }
        for num in range(NUM_INSTANCES):
            servers[f'{PREFIX}_server_{num}'] = Server(
                image=images['server'], name=f'{PREFIX}_server_{num}',
                networks=[{
                    'network': networks[f'{PREFIX}_server_{num}'],
                    'options': {
                        'ipv4_address': f'10.0.{num + 1}.3',
                        'aliases': ['server']
                    }
                }]
            )

        for server in servers:
            servers[server].start()

        atexit.register(cleanup, servers, networks)
    except Exception as e:
        print('Error whilst starting up:', e, file=sys.stderr)
        exit(1)

    try:
        print('Waiting for Ctrl-C to terminate...')
        while True:
            time.sleep(600)
    except KeyboardInterrupt:
        pass

    exit(0)
