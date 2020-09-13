import math
import re
import time
from PIL import Image, ImageDraw, ImagePalette
import randomcolor
import struct
from binascii import hexlify

def divide_and_ceil(v1, v2):
    return -(-v1//v2)

def generate_code_bcd_payload(value):
    if not value.isnumeric():
        raise Exception(f'BCD can only contain numbers, "{value}" has non numric characters!')

    if (len(value)) % 2 == 1:
        value += 'f'

    return value

def generate_code_bcd(value):
    if not value.isnumeric():
        raise Exception(f'BCD can only contain numbers, "{value}" has non numric characters!')

    value = generate_code_bcd_payload(value)

    length = hex(divide_and_ceil(len(value), 2))

    code = f'{length[2:]}{value}'

    return f'0{code}'

def decode_bcd(code):
    if code[0] != '0':
        raise Exception(f'Code is not encoded as BCD "{code}"!')

    length = int(code[1], 16)

    bcd = code[2: 2+length*2]
    bcd = bcd.replace('f', '')

    remaining = code[2+length*2: ]

    return (bcd, remaining)

def generate_code_din66003_payload(value):
    value = value.replace('§', '@')
    value = value.replace('Ä', '[')
    value = value.replace('Ö', '\\')
    value = value.replace('Ü', ']')
    value = value.replace('ä', '{')
    value = value.replace('ö', '|')
    value = value.replace('ü', '}')
    value = value.replace('ß', '~')

    code = hexlify(value.encode()).decode()

    return code

def generate_code_din66003(value):
    length = hex(len(value))

    code = generate_code_din66003_payload(value)

    return f'1{length[2:]}{code}'

def decode_din66003(code):
    if code[0] != '1':
        raise Exception(f'Code is not encoded as DIN 66003 "{code}"!')

    length = int(code[1], 16)

    encoded = code[2: 2+length*2]
    decoded = bytearray.fromhex(encoded).decode()
    decoded = decoded.replace('@', '§')
    decoded = decoded.replace('[', 'Ä')
    decoded = decoded.replace('\\', 'Ö')
    decoded = decoded.replace(']', 'Ü')
    decoded = decoded.replace('{', 'ä')
    decoded = decoded.replace('|', 'ö')
    decoded = decoded.replace('}', 'ü')
    decoded = decoded.replace('~', 'ß')

    remaining = code[2+length*2: ]

    return (decoded, remaining)

def decode_encoding(code):
    try:
        return decode_bcd(code)
    except Exception as e:
        try:
            return decode_din66003(code)
        except Exception as e:
            raise Exception(f'Code has an unkown encoding "{code}"!')

class Mask:
    AMOUNT = '1'
    ACCOUNT_NUMBER = '2'
    ONLINE_BANKING_PIN = '3'
    PHONE = '4'
    DETAILS = '5'
    NUMBER = '6'
    ACCOUNT_NUMBER_OLD = '7'
    ACCOUNT_NUMBER_IBAN = '8'

    random = ''
    def __init__(self, random):
        self.random = random

    def string_mask(self, x):
        if x == self.AMOUNT:
            return 'AMOUNT'
        elif x == self.ACCOUNT_NUMBER:
            return 'ACCOUNT_NUMBER'
        elif x == self.ONLINE_BANKING_PIN:
            return 'ONLINE_BANKING_PIN'
        elif x == self.PHONE:
            return 'PHONE'
        elif x == self.DETAILS:
            return 'DETAILS'
        elif x == self.NUMBER:
            return 'NUMBER'
        elif x == self.ACCOUNT_NUMBER_OLD:
            return 'ACCOUNT_NUMBER_OLD'
        elif x == self.ACCOUNT_NUMBER_IBAN:
            return 'ACCOUNT_NUMBER_IBAN'        

class One_Mask(Mask):
    mask = ''
    value = ''

    def __init__(self, mask, value, random):
        super().__init__(random)
        self.mask = mask
        self.value = value
    @classmethod
    def decode(cls, code):
        (start, code) = decode_encoding(code)

        if start[0] != '7':
            raise Exception(f'Code does not match One_Mask')

        mask = start[1]
        random = start[2:]

        (value, code) = decode_encoding(code)

        if len(code) != 0:
            raise Exception(f'Code does not follow protocol and contains extra values {code}!')

        return cls(mask, value, random)

    def parse_mask_payload(self):
        code = generate_code_bcd_payload('7' + self.mask + self.random)
        return code

    def parse_mask(self):
        code = generate_code_bcd('7' + self.mask + self.random)
        return code

    def parse_value_payload(self):
        code = ''

        if self.value.isnumeric():
            code += generate_code_bcd_payload(self.value)
        else:
            code += generate_code_din66003_payload(self.value)

        return code

    def parse_value(self):
        code = ''

        if self.value.isnumeric():
            code += generate_code_bcd(self.value)
        else:
            code += generate_code_din66003(self.value)

        return code

    def mask_to_string(self):
        return f'Value: {super().string_mask(self.mask)} = "{self.value}"'

class Two_Masks(Mask):
    mask1 = ''
    value1 = ''

    mask2 = ''
    value2 = ''

    def __init__(self, mask1, value1, mask2, value2, random):
        super().__init__(random)
        self.mask1 = mask1
        self.value1 = value1
        self.mask2 = mask2
        self.value2 = value2

    @classmethod
    def decode(cls, code):
        (start, code) = decode_encoding(code)

        if start[0] != '8':
            raise Exception(f'Code does not match Two_Masks')

        mask1 = start[1]
        mask2 = start[2]
        random = start[3:]

        (value1, code) = decode_encoding(code)
        (value2, code) = decode_encoding(code)

        if len(code) != 0:
            raise Exception(f'Code does not follow protocol and contains extra values {code}!')

        return cls(mask1, value1, mask2, value2, random)

    def parse_mask_payload(self):
        code = generate_code_bcd_payload('8' + self.mask1 + self.mask2 + self.random)
        return code

    def parse_mask(self):
        code = generate_code_bcd('8' + self.mask1 + self.mask2 + self.random)
        return code

    def parse_value_payload(self):
        code = ''

        if self.value1.isnumeric():
            code += generate_code_bcd_payload(self.value1)
        else:
            code += generate_code_din66003_payload(self.value1)

        if self.value2.isnumeric():
            code += generate_code_bcd_payload(self.value2)
        else:
            code += generate_code_din66003_payload(self.value2)

        return code

    def parse_value(self):
        code = ''

        if self.value1.isnumeric():
            code += generate_code_bcd(self.value1)
        else:
            code += generate_code_din66003(self.value1)

        if self.value2.isnumeric():
            code += generate_code_bcd(self.value2)
        else:
            code += generate_code_din66003(self.value2)

        return code

    def mask_to_string(self):
        return f'Values: {super().string_mask(self.mask1)} = "{self.value1}" and {super().string_mask(self.mask2)} = "{self.value2}"'

class Base_Two_Masks(Two_Masks):
    SINGLE_NATIONAL = '1'
    SINGLE_SEPA = '2'
    SINGLE_INTERNATIONAL = '3'
    MULTIPLE_NATIONAL = '4'
    MULTIPLE_SEPA = '5'
    MULTIPLE_INTERNATIONAL = '6'
    BOND = '7'
    PRE_PAID = '8'
    OTHERS = '9'

    base = ''

    def __init__(self, base, mask1, value1, mask2, value2, random):
        super().__init__(mask1, value1, mask2, value2, random)
        self.base = base

    @classmethod
    def decode(cls, code):
        (start, code) = decode_encoding(code)

        if start[0] != '9':
            raise Exception(f'Code does not match Base_Two_Masks')

        base = start[1]
        mask1 = start[2]
        mask2 = start[3]
        random = start[4:]

        (value1, code) = decode_encoding(code)
        (value2, code) = decode_encoding(code)

        if len(code) != 0:
            raise Exception(f'Code does not follow protocol and contains extra values {code}!')

        return cls(base, mask1, value1, mask2, value2, random)

    def parse_mask_payload(self):
        code = generate_code_bcd_payload('9' + self.base + self.mask1 + self.mask2 + self.random)
        return code

    def parse_mask(self):
        code = generate_code_bcd('9' + self.base + self.mask1 + self.mask2 + self.random)
        return code

    def string_base(self, x):
        if x == self.SINGLE_NATIONAL:
            return 'SINGLE_NATIONAL'
        elif x == self.SINGLE_SEPA:
            return 'SINGLE_SEPA'
        elif x == self.SINGLE_INTERNATIONAL:
            return 'SINGLE_INTERNATIONAL'
        elif x == self.MULTIPLE_NATIONAL:
            return 'MULTIPLE_NATIONAL'
        elif x == self.MULTIPLE_SEPA:
            return 'MULTIPLE_SEPA'
        elif x == self.MULTIPLE_INTERNATIONAL:
            return 'MULTIPLE_INTERNATIONAL'
        elif x == self.BOND:
            return 'BOND'
        elif x == self.PRE_PAID:
            return 'PRE_PAID'  
        elif x == self.OTHERS:
            return 'OTHERS'  

    def mask_to_string(self):
        return f'Base: {string_base(self.base)}, {super().mask_to_string()}'

def digitsum(n):
    q = 0
    while n != 0:
        q += n % 10
        n = math.floor(n / 10)
    return q

def luhn_checksum(code):
    luhnsum = 0
    for i in range(0, len(code), 2):
        luhnsum += 1 * int(code[i], 16) + digitsum(2 * int(code[i + 1], 16))

    m = luhnsum % 10
    if m == 0:
        return "0"
    r = 10 - m
    ss = luhnsum + r
    luhn = ss - luhnsum
    return hex(luhn)[2:]

def xor_checksum(payload):
    xorsum = 0
    for c in payload[:-1]:
        xorsum ^= int(c, 16)
    return hex(xorsum)[2:]

def generate_code(mask):
    length = 0

    code = ''
    code += mask.parse_mask()
    
    code += mask.parse_value()

    payload = ''
    payload += mask.parse_mask_payload()
    payload += mask.parse_value_payload()

    code += luhn_checksum(payload)
   
    length = hex((len(code) + 1) // 2)[2:].zfill(2)
    code = str(length) + code

    code += xor_checksum(code)

    return code

def decode_mask(code):
    mask = ''

    try:
        mask = One_Mask.decode(code)
    except Exception as e:
        try:
            mask = Two_Masks.decode(code)
        except Exception as e:
            try:
                mask = Base_Two_Masks.decode(code)
            except Exception as e:
                raise Exception(f'Code does not match any mask')

    return mask

def decode(code):
    length = int(code[:2], 16)

    xor_check = code[-1]
    code = code[:-1]

    if xor_checksum(code) != xor_check:
        raise Exception(f'XOR checksum does not match!')

    code = code[2:]

    luhn = code[-1]
    code = code[:-1]

    mask = decode_mask(code)

    payload = ''
    payload += mask.parse_mask_payload()
    payload += mask.parse_value_payload()
    
    if luhn_checksum(payload) != luhn:
        raise Exception(f'Luhn checksum does not match!')

    print(f'The code mask is {mask.__class__.__name__}. The random value is {mask.random}.')
    print(mask.mask_to_string())

def swap_bytes(s):
    b = ""
    for i in range(0, len(s), 2):
        b += s[i + 1]
        b += s[i]
    return b

def base_convert(n, base):
    if n == 0:
        return '0'
    nums = []
    while n:
        n, r = divmod(n, base)
        nums.append(str(r))
    return ''.join(reversed(nums))

def gif_flicker_default(code, field_width=30, space_width=15, height=50, wait=50):
    color_count = 2

    data = swap_bytes(code)

    stream = ['10000', '00000', '11111', '01111', '11111', '01111', '11111']
    for c in data:
        v = int(c, 16)
        stream.append('1' + str(v & 1) + str((v & 2) >> 1) + str((v & 4) >> 2) + str((v & 8) >> 3))
        stream.append('0' + str(v & 1) + str((v & 2) >> 1) + str((v & 4) >> 2) + str((v & 8) >> 3))

    width = 5 * field_width + 6 * space_width
    images = []

    colors = [(0,0,0),(255,255,255)]

    for frame in stream:
        im = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(im)
        
        x = space_width
        for c in frame:
            draw.rectangle([(x, 0), (x+field_width, height)], fill= colors[int(c, color_count)], width = 0)

            x += space_width + field_width

        im = im.convert('P', palette=Image.ADAPTIVE, colors=color_count)
        images.append(im)

    images[0].save('flicker.gif', save_all=True, append_images=images[1:], optimize=True, duration=wait, loop=0, disposal=2)
    
def gif_flicker_custom(code, field_width=30, space_width=15, height=50, wait=50):
    color_count = 4

    data = swap_bytes(code)

    stream = []
    
    for j in range(0, color_count):
        for i in range(color_count-1 , -1, -1):
            stream.append(str(i) + str(j) * 4)

    stream.append(str(color_count-1)*5)
    
    hex_count = math.floor(math.log(color_count ** 4, 16))
    
    for i in range(0, len(data), hex_count):
        c = data[i:i+hex_count]
        v = int(c, 16)
        v = base_convert(v, color_count).zfill(4)[::-1]

        for i in range(color_count-1 , -1, -1):
            stream.append(str(i) + v)

    width = 5 * field_width + 6 * space_width
    images = []
    
    rand_color = randomcolor.RandomColor()
    colors = rand_color.generate(count = color_count, format_ = 'rgb')
    #print(stream)
    for frame in stream:
        im = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(im)
        
        x = space_width
        for c in frame:
            draw.rectangle([(x, 0), (x+field_width, height)], fill= colors[int(c, color_count)], width = 0)

            x += space_width + field_width

        im = im.convert('P', dither = None, palette=Image.ADAPTIVE, colors=color_count)

        images.append(im)

    images[0].save('flicker.gif', save_all=True, append_images=images[1:], optimize=False, duration=wait, loop=0, disposal=2)
    
