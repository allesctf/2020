# ESPecially a lot of fun
You received a nice gadget via mail: an espressif ESP32! You have your local device for testing, but you'll need to pwn the remote server to get the real flag.
The provided image differs from the remote image only in the following points:
 - The password of the second user has been changed
 - The flag string has been replaced

For flashing and wifi configuration see the documentation below


# Instructions how to flash

## Preperations
Install `esptool` via pip (maybe in a `venv` if you like)
```
python3 -m pip install esptool
```
Check that it works:
``` 
$ esptool.py
esptool.py v2.8
usage: esptool [-h] [--chip {auto,esp8266,esp32}] [--port PORT] [--baud BAUD]
```

Verify that the included `spiffsgen.py` script works:
```
python spiffsgen.py
usage: spiffsgen.py [-h] [--page-size PAGE_SIZE] [--block-size BLOCK_SIZE] [--obj-name-len OBJ_NAME_LEN]
[...]
```

Windows users might need the `CP210x USB to UART` driver: https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers


## Change Wifi Config
The challenge can work in two wifi modes:
 - The ESP32 hosts a wifi network (AP) for you to connect. If can be reached by 192.168.4.1 by default
 - The ESP32 connects to a wifi and prints its IP, assigned via DHCP

Either way you have to edit the `data/wificonfig.json` file. Use `CONNNECT` as `WifiMode` to connect to a existing network or use `AP` to host a new wifi network. Change the `WifiName` and `WifiPass` accordingly. 

## Build Filesystem
The content of the `data` folder, including your modified `wificonfig.json`, will be used as filesystem on the ESP32. You can build it via:

```
python spiffsgen.py 1507328 data spiffs.bin
```

## Upload firmware and filesystem
Upload Firmware:
```
python esptool.py --chip esp32 --port "COM6" --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 bootloader_dio_40m.bin 0x8000 partitions.bin 0xe000 boot_app0.bin 0x10000 firmware.bin
```

Upload Filesystem:
```
python esptool.py --chip esp32 --port "COM6" --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_size detect 2686976 spiffs.bin
```

Adjust the `--port ` argument to your own port. On Unix you have to use `/dev/ttyUSB0` or similar.

## Troubleshooting
For some reason the wifi connect fails from time to time. If you see the following messages on the serial output, you most likly ran into that problem:
```
[...]
Connecting to WiFi..
4
Connecting to WiFi..
4
Connecting to WiFi..
4
```
Just push the `RST` button on your ESP32. It reboots and should connect right away:
```
[...]
Connecting to WiFi..
3
Connected to wifi. IP:
192.168.178.75
```


