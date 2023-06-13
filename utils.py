from PIL import Image
import math, numpy, sys

import palette

DEBUGMODE = False

def open_image(image_filename):
    return Image.open(image_filename).convert('RGB')


def pil2numpy(image):
    matrix = numpy.asarray(image, dtype=numpy.float)
    return matrix/255. 


def numpy2pil(matrix):
    image = Image.fromarray(numpy.uint8(matrix*255))
    return image


def clamp(val):
    return max(0.0, min(1.0, val))


def closest_palette_color(value, palette_name, bit_depth=1):
    if DEBUGMODE:
        print('\tvalue = {value}')

    # compute distance to colors in palette
    # TODO make this naive method more sophisticated
    min_dist = 10000.
    ci_use = -1
    for ci, color in enumerate(palette.palettes[palette_name]):
        pr, pg, pb = color
        vr, vg, vb = value
        dist = math.sqrt((vr-pr)*(vr-pr)+(vg-pg)*(vg-pg)+(vb-pb)*(vb-pb))

        if DEBUGMODE:
            print('\tcolor = {color}')
            print('\tdist = {dist}, min_dist = {min_dist}')

        if dist < min_dist:
            ci_use = ci
            min_dist = dist

    if ci == -1:
        return [0.0, 0.0, 0.0]
    else:
        return palette.palettes[palette_name][ci_use]

