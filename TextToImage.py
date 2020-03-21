import numpy
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import math


def subsection(string):
    return string.split('\n')


def carry(x, y):
    if x % y != 0:
        return (x // y + 1)
    return x // y


def linefeed(sections, length):
    stringlins = []
    for section in sections:
        strs = textwrap.fill(section, length).split('\n')
        stringlins = stringlins + strs
    return stringlins


def text2lins(string, length):
    segments = subsection(string)
    string_lins = linefeed(segments, length)
    return string_lins


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def add_watermark(image, text, font, alpha=100, space=100):
    new_img = Image.new(
        'RGBA', (image.size[0] * 3, image.size[1] * 3), (0, 0, 0, 0))
    new_img.paste(image, image.size)
    font_len = len(text)
    rgba_image = new_img.convert('RGBA')
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)

    for i in range(0, rgba_image.size[0], font.size*font_len+space):
        for j in range(0, rgba_image.size[1], font.size+space):
            image_draw.text((i, j), text, font=font, fill=(0, 0, 0, alpha))
    text_overlay = text_overlay.rotate(45)
    image_with_text = Image.alpha_composite(rgba_image, text_overlay)

    image_with_text = image_with_text.crop(
        (image.size[0], image.size[1], image.size[0] * 2, image.size[1] * 2))
    return image_with_text


def add_single_watermark(image, text, font, alpha=100, position=''):
    fontsize = font.size
    new_img = Image.new(
        'RGBA', image.size, (255, 255, 255, 255))
    new_img.paste(image)
    from functools import reduce
    # 中文占一个宽度，英文占半个宽度
    width = int(reduce(lambda x, y: x + y,
                       list(map(lambda x: 1 if is_Chinese(x) else 0.5, text))) * fontsize)
    picture = Image.new('RGBA', (width, width), (255, 255, 255, 0))
    draw = ImageDraw.Draw(picture)
    draw.text((0, (width - fontsize)//2), text,
              font=font, fill=(0, 0, 0, alpha))
    x = 0
    y = 0
    picture = picture.rotate(45)
    if position == 'topleft':
        x = 0
        y = 0
    elif position == 'bottomright':
        x = image.width - width
        y = image.height - width
    else:
        x = (image.width - width) // 2
        y = (image.height - width) // 2
    picture2 = Image.new(
        'RGBA', (image.width, image.height), (255, 255, 255, 0))
    picture2.paste(picture, (x, y, x+width, y+width))
    new_img.alpha_composite(picture2)
    return new_img


def text2piiic(string, length, font, x=20, y=40, spacing=20, cut=False):
    fontsize = font.size
    lins = text2lins(string, length)
    heigh = y * 2 + (fontsize + spacing) * (len(lins)-1) + fontsize
    width = x * 2 + fontsize * length
    if cut:
        width = x*2 + fontsize * max(list(map(lambda x: len(x), lins)))
    picture = Image.new('RGBA', (width, heigh), (255, 255, 255, 255))
    draw = ImageDraw.Draw(picture)
    for i in range(len(lins)):
        y_pos = y + i * (fontsize + spacing)
        draw.text((x, y_pos), lins[i], font=font, fill=(0, 0, 0))
    return picture


def text2multigraph(string, backdrop, font, x=20, y=40, spacing=20):
    fontsize = font.size
    row = (backdrop.width - x * 2) // fontsize
    lin = carry((backdrop.height - y * 2), (fontsize + spacing))
    str_lin = text2lins(string, row)
    str_lin_len = len(str_lin)
    num_lin = carry(str_lin_len, lin)
    imgs = []
    for num in range(num_lin):
        img = backdrop.copy()
        draw = ImageDraw.Draw(img)
        for i in range(lin):
            if (num * lin + i) < str_lin_len:
                draw.text((x, y + i * (fontsize + spacing)),
                          str_lin[num * lin + i], font=font, fill=(0, 0, 0))
            else:
                break
        imgs.append(img)
    return imgs


if __name__ == "__main__":
    f = open("a.txt")
    str = f.read()
    f.close()
    font = ImageFont.truetype('./simhei.ttf', 20, encoding="utf-8")
    img = text2piiic(str, 40, font, cut=True)
    img1 = add_watermark(img, 'hello啊', font=font, alpha=100)
    img2 = add_single_watermark(img, 'hello啊', font=font, alpha=100)
    img.show()
    img1.show()
    img2.show()
