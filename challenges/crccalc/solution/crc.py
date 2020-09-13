import binascii

from sage.all import *
from sage.geometry.hyperplane_arrangement.affine_subspace import AffineSubspace

R = PolynomialRing(GF(2), "x")
x = R.gen()

def bitstring(n, bits):
    return ("{:0%db}" % bits).format(n)

def reflect_int(n, bits):
    return int(bitstring(n, bits)[::-1], 2)

def reflect_bytes(data):
    return bytes(reflect_int(byte, 8) for byte in data)

def reflect_poly(poly, size):
    n = poly2int(poly, size)
    n = reflect_int(n, size)
    return int2poly(n, size)

def int2poly(n, size):
    bits = bitstring(n, size)[::-1]
    return R(list(map(int, bits)))

def bytes2poly(data):
    n = int.from_bytes(data, "big")
    return int2poly(n, 8 * len(data))

def poly2bytes(poly):
    bits = (poly.degree() + 8) // 8 * 8
    n = poly2int(poly, bits)
    return n.to_bytes(bits // 8, "big")

def poly2int(poly, bits):
    coeffs = "".join(map(str, poly.list()))
    coeffs = (bits - len(coeffs)) * "0" + coeffs[::-1]
    return int(coeffs, 2)

def crc32(data, poly, init, refin, refout, xorout):
    length = len(data)
    mod = x**32 + int2poly(poly, 32)
    xor1 = int2poly(init, 32)
    xor2 = int2poly(xorout, 32)
    if refin:
        data = reflect_bytes(data)
    data = bytes2poly(data)
    data *= x**32
    data += xor1 * x**(8 * length)
    data %= mod
    if refout:
        data = reflect_poly(data, 32)
    data = data + xor2
    return poly2int(data, 32)

def ipoly32(checksum, length, poly, init, refin, refout, xorout):
    mod = x**32 + int2poly(poly, 32)
    xor1 = int2poly(init, 32)
    xor2 = int2poly(xorout, 32)
    data = int2poly(checksum, 32)
    data = data + xor2
    if refout:
        data = reflect_poly(data, 32)
    data += xor1 * x**(8 * length)
    data *= inverse_mod(x**32, mod)
    data %= mod
    return data

def equation(checksum, length, param):
    return (
        ipoly32(checksum, length, *param),
        x**32 + int2poly(param[0], 32)
    )

p = lambda a: bytes2poly(reflect_bytes(poly2bytes(a)))

def affine_subspace(V, a, m, ref=False):
    n = V.degree()
    diff = n - m.degree() - 1
    base = [x**i * m for i in range(diff + 1)]
    if ref:
        base = [p(b) for b in base]
    W = V.subspace([
        V(list(base[i]) + [0] * (n - base[i].degree() - 1)) for i in range(diff + 1)
    ])
    if ref:
        a = p(a)
    return AffineSubspace(
        V(a.list() + [0] * (n - a.degree() - 1)),
        W
    )

params32 = [
    (0x04C11DB7, 0xFFFFFFFF, True,  True,   0xFFFFFFFF),
    (0x04C11DB7, 0xFFFFFFFF, False, False, 	0xFFFFFFFF),
    (0x1EDC6F41, 0xFFFFFFFF, True,  True, 	0xFFFFFFFF),
    (0xA833982B, 0xFFFFFFFF, True,  True, 	0xFFFFFFFF),
    (0x04C11DB7, 0xFFFFFFFF, False, False, 	0x00000000),
    (0x04C11DB7, 0x00000000, False, False, 	0xFFFFFFFF),
    (0x814141AB, 0x00000000, False, False, 	0x00000000),
 	(0x04C11DB7, 0xFFFFFFFF, True,  True, 	0x00000000),
 	(0x000000AF, 0x00000000, False, False, 	0x00000000)
]

# values for crccalc1
data = [
    0x8A7B9617,
    0x58653D65,
    0x822681C1,
    0xB6608BDC,
    0xA79AC29A,
    0x51F96944,
    0x28D0D4AD,
    0x758469E8,
    0x6DEE8406,
]

# values for crccalc2
if True:
    data = [
        0xB60C1196,
        0x540FB6E5,
        0x0472FC19,
        0xCD3BFFA5,
        0xABF0491A,
        0xAFA3CADF,
        0xC4B409AD,
        0x49F3EE69,
        0x0B91E517
    ]

for n in range(1, 13):
    a1, m1 = equation(data[0], n, params32[0])
    a2, m2 = equation(data[2], n, params32[2])
    a3, m3 = equation(data[3], n, params32[3])
    res = CRT_list([a1, a2, a3], [m1, m2, m3])
    sol = reflect_bytes(poly2bytes(res))
    if len(sol) != n:
        print(n, "no solution")
    else:
        print(n, sol)

# 24 ok
for n in range(13, 25):
    V = VectorSpace(GF(2), 8 * n)
    Ws = []

    for checksum, param in zip(data, params32):
        a, m = equation(checksum, n, param)
        W = affine_subspace(V, a, m, param[2])
        Ws.append(W)

    W = Ws[0]
    for U in Ws[1:]:
        W = W.intersection(U)
        if W is None: break
    if W is None:
        print(n, "no solution")
        continue

    print(n, poly2bytes(R(list(map(int, W.point())))))
