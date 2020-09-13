from PIL import Image
import math
import flicker as flicker_helper

def swap_bytes(s):
    b = ""
    for i in range(0, len(s), 2):
        b += s[i + 1]
        b += s[i]
    return b

class Flicker():
    flicker_image = 0

    flicker_codes = []

    width = 0
    height = 0

    space_width = 0
    field_width = 0
    colors = []

    def decode_frame(self, frame):
        value = ''
        
        first_value = self.space_width

        for x in range(first_value, self.width-self.space_width, self.field_width+self.space_width):
            current_color = frame.getpixel((x, self.height//2))
            value += str(self.colors.index(current_color))

        return value

    def __init__(self, flicker_image):
        self.flicker_image = flicker_image

        self.width, self.height = self.flicker_image.size

        self.flicker_image.seek(0)
        rgb_flicker = self.flicker_image.convert('RGB')

        background = rgb_flicker.getpixel((0,0))

        self.colors.append(background)
        for x in range(0, self.width):
            current_color = rgb_flicker.getpixel((x, self.height//2))
            if current_color != background:
                self.space_width = x

                break

        for x in range(self.space_width, self.width):
            current_color = rgb_flicker.getpixel((x, self.height//2))
            if current_color == background:
                self.field_width = (x - 1) - self.space_width

                break

        for frame in range(0,self.flicker_image.n_frames):
            self.flicker_image.seek(frame)
            rgb_flicker = self.flicker_image.convert('RGB')

            for x in range(self.space_width, self.width-self.space_width, self.field_width+self.space_width):
                current_color = rgb_flicker.getpixel((x, self.height//2))

                if current_color not in self.colors:
                    self.colors.insert(1,current_color)

        for frame in range(0, self.flicker_image.n_frames):
            self.flicker_image.seek(frame)
            rgb_flicker = self.flicker_image.convert('RGB')

            x = self.decode_frame(rgb_flicker)

            self.flicker_codes.append(x)
            
    def decode(self, start_sequence, clock_count):
        hex_count = math.floor(math.log(len(self.colors) ** 4, 16))

        for i in range(0, len(start_sequence)):
            if start_sequence[i] != self.flicker_codes[i]:
                raise Exception(f'Start sequence wrong {i}th elmeent expected to be {start_sequence[i]} but actually was {self.flicker_codes[i]}')

        code = ''
        for i in range(len(start_sequence), len(self.flicker_codes), clock_count):
            v = int(self.flicker_codes[i][1:][::-1], clock_count)
            code += hex(v)[2:].zfill(hex_count)

        return swap_bytes(code)

flicker_image = Image.open("./flicker.gif")

flicker = Flicker(flicker_image)

#start_sequence = ['10000', '00000', '11111', '01111', '11111', '01111', '11111']
start_sequence = []

for j in range(0, len(flicker.colors)):
        for i in range(len(flicker.colors)-1 , -1, -1):
            start_sequence.append(str(i) + str(j) * 4)
start_sequence.append(str(len(flicker.colors)-1)*5)

#print(flicker.space_width)
#print(flicker.field_width)
#print(flicker.colors)
#print(flicker.flicker_codes)

code = flicker.decode(start_sequence, len(flicker.colors))

print(code)
flicker_helper.decode(code)