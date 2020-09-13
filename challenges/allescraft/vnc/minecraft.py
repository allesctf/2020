import json
import os
import shutil
import subprocess
import sys
import zipfile
from hashlib import sha1

import requests

FORGE_HASH = 'fd44bd84072bd3b96641698ff96245849309efe0'
MOJANG_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{version}/{version}.json'
FORGE_URL = 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/{version_short}/{version}-installer.jar'
VERBOSE = False
JAVA_EXE = '/usr/bin/java'


# noinspection PyBroadException
def download(url, target, sha1_value=None):
    if target and sha1_value and os.path.exists(target):
        try:
            content = open(target, 'rb').read()

            if sha1(content).hexdigest() == sha1_value:
                if VERBOSE:
                    print(f'Skipping download: {url}')
                return content
        except Exception:
            pass

    if target and not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))

    for _ in range(3):
        try:
            r = requests.get(url=url)
            if not r.status_code == 200:
                raise ValueError(f'Error downloading from {url}')

            if sha1_value and sha1(r.content).hexdigest() != sha1_value:
                raise AssertionError('Invalid SHA hash')

            if target:
                with open(target, 'wb') as f:
                    f.write(r.content)

            return r.content
        except Exception as e:
            print(f'Download of {url} failed:', e, file=sys.stderr)

    raise RuntimeError(f'Maximum number of retries exceeded: {url}')


def download_artifact_(artifact, target):
    target = os.path.abspath(os.path.join(target, artifact['path']))

    for _ in range(3):
        if VERBOSE:
            print(f'Downloading artifact: {artifact["url"]}')
        content = download(artifact['url'], target)
        if sha1(content).hexdigest() != artifact['sha1']:
            if VERBOSE:
                print('SHA1 mismatch, retrying...')
        else:
            return target

    raise AssertionError(f'Download of {artifact["url"]} failed, SHA1 mismatch.')


def common_setup(version, target, version_json, cp_only=False):
    classpath = []

    # Download libraries
    if not cp_only:
        print(f'Downloading libraries for {version}')
    for lib in version_json.get('libraries', []):
        if 'natives' in lib:
            allowed = False
            for rule in lib.get('rules', [{'action': 'allow'}]):
                if 'os' in rule:
                    if rule['os']['name'] != 'linux':
                        continue

                allowed = (rule['action'] == 'allow')

            if not allowed:
                continue

            linux_alias = lib['natives']['linux']
            artifact = lib.get('downloads', {}).get('classifiers', {}).get(
                linux_alias, None)
            if artifact:
                artifact_path = os.path.join(target, 'libraries', artifact['path'])
                classpath.append(os.path.abspath(artifact_path))

                if not cp_only:
                    download(artifact['url'], artifact_path, artifact['sha1'])
                    excludes = lib.get('extract', {}).get('exclude', [])
                    with zipfile.ZipFile(artifact_path, 'r') as artifact_zip:
                        for to_extract in artifact_zip.filelist:
                            if any([to_extract.filename.startswith(x) for x in excludes]):
                                continue
                            artifact_zip.extract(
                                to_extract,
                                os.path.join(target, 'bin', 'natives'))

        if 'artifact' in lib['downloads']:
            artifact = lib['downloads']['artifact']
            artifact_path = os.path.join(target, 'libraries', artifact['path'])
            classpath.append(os.path.abspath(artifact_path))
            if not cp_only:
                download(artifact['url'], artifact_path, artifact['sha1'])

    if cp_only:
        return classpath

    asset_index = version_json.get('assetIndex', None)
    if asset_index:
        print(f'Downloading assets for {version}')
        assets = download(
            asset_index['url'],
            os.path.join(target, 'assets', 'indexes', f'{asset_index["id"]}.json'))
        assets = json.loads(assets)

        for asset in assets['objects'].values():
            h = asset['hash']

            asset_path = os.path.join(target, 'assets', 'objects', h[:2], h)
            download(f'https://resources.download.minecraft.net/{h[:2]}/{h}',
                     asset_path, h)

    return classpath


# noinspection PyShadowingNames
def install_minecraft(version, target):
    print('Downloading version meta-information')

    version_json = download(
        MOJANG_URL.format(version=version),
        os.path.join(target, 'versions', version, f'{version}.json'))
    version_json = json.loads(version_json)

    classpath = []

    # Download client
    client = version_json.get('downloads', {}).get('client', None)
    if client:
        print('Downloading client.jar')
        client = version_json['downloads']['client']
        client_path = os.path.join(target, 'versions', version, f'{version}.jar')
        download(client['url'], client_path, client['sha1'])
        classpath.append(os.path.abspath(client_path))

    classpath += common_setup(version, target, version_json)

    return classpath


# noinspection PyShadowingNames
def install_forge(version, target):
    mc_version = version.split('-')[1]
    version_short = version[6:]
    version_dir = os.path.join(target, 'versions', version)

    # Install base minecraft
    classpath = install_minecraft(mc_version, target)

    # Download the jar
    print('Downloading forge installer')
    forge_installer = os.path.join(target, f'{version}-installer.jar')
    download(
        FORGE_URL.format(version=version, version_short=version_short),
        forge_installer, FORGE_HASH)

    devnull = open(os.devnull, 'w')
    assert subprocess.call([
        'java',
        '-jar',
        forge_installer,
        '--extract',
        version_dir
    ], stdout=devnull) == 0
    devnull.close()

    with zipfile.ZipFile(forge_installer, 'r') as forge_installer_jar:
        found = False
        for file in forge_installer_jar.filelist:
            if file.filename.endswith('version.json'):
                forge_installer_jar.extract(
                    file, version_dir)
                os.rename(
                    os.path.join(version_dir, 'version.json'),
                    os.path.join(version_dir, f'{version}.json'))
                found = True
                break

        if not found:
            raise ValueError('Forge installer does not contain version json')

    os.remove(forge_installer)

    # Hacky forge fix
    target_dir = os.path.join(
        target, 'libraries', 'net', 'minecraftforge', 'forge', version_short)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copyfile(
        os.path.join(target, 'versions', version, f'{version}.jar'),
        os.path.join(target_dir, f'{version}.jar'))

    version_json = open(os.path.join(version_dir, f'{version}.json'), 'r').read()
    version_json = json.loads(version_json)

    classpath += common_setup(version, target, version_json)

    return classpath


def do_install(version, home, forge):
    print(f'Installing Minecraft {version} to {home}')
    if forge:
        install_forge(version, home)
    else:
        install_minecraft(version, home)


def do_run(version, home):
    version_json = open(
        os.path.join(home, 'versions', version, f'{version}.json'), 'r').read()
    version_json = json.loads(version_json)

    classpath = []

    if version_json.get('inheritsFrom', None):
        sub_version = version_json['inheritsFrom']
        sub_json = open(
            os.path.join(home, 'versions', sub_version,
                         f'{sub_version}.json'), 'r').read()
        sub_json = json.loads(sub_json)
        if not version_json.get('assetIndex', None):
            version_json['assetIndex'] = sub_json.get('assetIndex', None)

        classpath.append(
            os.path.join(home, 'versions', sub_version, f'{sub_version}.jar'))
        classpath += common_setup(sub_version, home, sub_json, True)

    classpath += common_setup(version, home, version_json, True)
    classpath.append(
        os.path.join(home, 'versions', version, f'{version}.jar'))

    jvm_extra_args = []
    max_mem = os.environ.get('MINECRAFT_RAM', None)
    if max_mem:
        jvm_extra_args.append(f'-Xms{max_mem}m')
        jvm_extra_args.append(f'-Xmx{max_mem}m')

    args = version_json['minecraftArguments'].split(' ')
    natives_path = os.path.abspath(os.path.join(home, 'bin', 'natives'))
    args = [
        JAVA_EXE,
        f'-Dorg.lwjgl.librarypath={natives_path}',  # Because lwjgl is retarded
        f'-Djava.library.path="{natives_path}"',
        *jvm_extra_args,
        '-cp',
        ':'.join(classpath),
        version_json['mainClass'],
        *args
    ]

    access_token = os.environ.get('ACCESS_TOKEN', '')
    player_name = os.environ.get('PLAYERNAME', 'ALLES')
    uuid = os.environ.get('UUID', '')
    args = [arg.replace('${auth_access_token}', access_token) for arg in args]
    args = [arg.replace('${auth_player_name}', player_name) for arg in args]
    args = [arg.replace('${auth_uuid}', uuid) for arg in args]
    args = [arg.replace('${user_type}', 'mojang') for arg in args]

    args = [arg.replace('${version_name}', version) for arg in args]
    args = [arg.replace('${game_directory}', os.path.abspath(home)) for arg in args]

    args = [arg.replace('${assets_root}',
                        os.path.abspath(os.path.join(home, 'assets')))
            for arg in args]
    args = [arg.replace('${assets_index_name}', version_json['assetIndex']['id']) for arg in args]

    args = [arg.replace('${version_type}', '') for arg in args]

    print('Running minecraft')

    if VERBOSE:
        print('Classpath:')
        print('\n'.join(classpath))

    os.execvp(JAVA_EXE, args)

    print('Something failed')
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f'Usage: {sys.argv[0].split("/")[-1]} [install/run/both] [version] [install-dir]')
        exit(1)

    mc_version = sys.argv[2]
    install_home = sys.argv[3]
    install_home = os.path.join(install_home, '.minecraft')
    is_forge = 'forge' in mc_version

    if sys.argv[1] == 'install':
        do_install(mc_version, install_home, is_forge)
    elif sys.argv[1] == 'run':
        do_run(mc_version, install_home)
    elif sys.argv[1] == 'both':
        do_install(mc_version, install_home, is_forge)
        do_run(mc_version, install_home)
    else:
        print('Invalid command', file=sys.stderr)
        exit(1)
