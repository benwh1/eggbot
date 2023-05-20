from PIL import Image, ImageDraw, ImageFont
import math
import colorsys

def color(index, total):
    frac = index / total
    hue = 330 * frac
    lum = (0.5 
        + 0.25 * math.cos(math.tau * (0.65 + hue / 720))
        + 0.35 * math.exp(-hue/100))
    r,g,b = colorsys.hls_to_rgb(hue/360, lum, 1)
    return '#{:02x}{:02x}{:02x}'.format(int(255 * r), int(255 * g), int(255 * b))

def getIndex(width, height, y, x):
    # wide puzzle, outside of square end region
    if width - x > height:
        return x
    # tall puzzle, outside of square end region
    if height - y > width:
        return y
    # square end region
    offset = abs(width-height)
    if width > height: 
        x -= offset
    elif height > width: 
        y -= offset
    return offset + 2 * min(x, y) + (1 if x < y else 0)

def makeImage(w, h):
    img = Image.new("RGB", (w, h))
    return img, ImageDraw.Draw(img, 'RGBA')

def drawSquare(img, x, y, r, color):
    shape = [(x, y), (x+r, y+r)]
    img.rectangle(shape, fill=color)
    return img

def drawTile(im, draw, xP, yP, col, number):
    size = 100
    x = xP*size
    y = yP*size
    font = ImageFont.truetype("font.ttf", int(size/2))
    W = size
    H = size
    w, h = draw.textsize(str(number), font=font)
    if number != 0:
        drawSquare(draw, x, y, size, col)
        draw.text(((W-w)/2+x, (H-h)/2+y), str(number), fill="black", font=font)
    else:
        mask = Image.new('L', im.size, color=255)
        mask_d = ImageDraw.Draw(mask)
        drawSquare(mask_d, x, y, size, 0)
        im.putalpha(mask)

def draw_state(state, bypass_limit=False):
    w, h = state.size()
    if (w > 20 or h > 20 or w < 2 or h < 2) and not bypass_limit:
        raise ValueError(f"puzzle size {state.size()} must be between 2x2 and 20x20")

    num_colors = w + h - 2

    img, draw = makeImage(w*100, h*100)

    for y in range(state.height()):
        for x in range(state.width()):
            n = state.arr[y][x]
            if n == 0:
                mycolor = "#000000"
            else:
                c_index = getIndex(w,h,*divmod(n-1,w))
                mycolor = color(c_index,num_colors)
            drawTile(img, draw, x, y, mycolor, n)

    return img
