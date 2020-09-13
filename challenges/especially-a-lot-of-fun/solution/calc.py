def calcChecksum(data):
    a12 = 0
    for i in range(0, len(data)):
       a12 += ord(data[i])*0x735*i
    return a12

print(hex(calcChecksum("s3cret_admin")))
#print(hex(calcChecksum("s3cret_admin")))