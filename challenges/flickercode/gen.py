import flicker
from random import randint

random = str(randint(0, 99999)).zfill(5)
mask = flicker.Two_Masks(flicker.Mask.ACCOUNT_NUMBER_OLD, '13244', flicker.Mask.ACCOUNT_NUMBER_IBAN, 'Hello World!', random)

code = flicker.generate_code(mask)

print(code)
flicker.gif_flicker_custom(code)