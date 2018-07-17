from PIL import Image
from collections import OrderedDict
import numpy
import random
import sys

import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

def block_randomized(image_matrix, palette_name):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    
    block_width, block_height = (max(1, cols/50), max(1, rows/50))

    for by in range(0, rows, block_height):
        for bx in range(0, cols, block_width):
            block = new_matrix[bx:bx+block_width,by:by+block_height,:]
            avg_color = numpy.sum(block, axis=(0,1))/(block_width*block_height)
            for y in range(block_height):
                for x in range(block_width):
                    ar, ag, ab = avg_color
                    ar = utils.clamp(ar + random.gauss(0.0, 1./6.))
                    ab = utils.clamp(ag + random.gauss(0.0, 1./6.))
                    ag = utils.clamp(ab + random.gauss(0.0, 1./6.))
                    new_pixel = numpy.array(utils.closest_palette_color([ar, ag, ab],
                        palette_name), dtype=numpy.float)
                    new_matrix[bx+x][by+y] = new_pixel
    return new_matrix

def randomized(image_matrix, palette_name):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            if DEBUGMODE:
                print '<{}, {}>'.format(x, y)
                print 'old = {}'.format(new_matrix[x][y])

            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            opr, opg, opb = old_pixel
            # add a random value in [-0.5, 0.5]
            opr = utils.clamp(opr + random.gauss(0.0, 1./6.))
            opg = utils.clamp(opg + random.gauss(0.0, 1./6.))
            opb = utils.clamp(opb + random.gauss(0.0, 1./6.))
            new_pixel = numpy.array(utils.closest_palette_color([opr, opg, opb],
                palette_name), dtype=numpy.float)
            new_matrix[x][y] = new_pixel
    return new_matrix

_available_methods = OrderedDict([
        ('random' , randomized),
        ('block_random' , block_randomized),
])

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Path to an image file to dither')
    parser.add_argument('-b', '--bit-depth', type=int, default=1, help='Number of bits in dithered image')
    palette_help_str = 'Name of palette to use. Can be one of: ' + ', '.join(palette.available_palettes)
    parser.add_argument('-p', '--palette', type=str, default=default_palette, help=palette_help_str)
    args = parser.parse_args()

    image = utils.open_image(args.image_filename)
    image_matrix = utils.pil2numpy(image)

    dither_matrix = randomized(image_matrix, args.palette)
    dither_image = utils.numpy2pil(dither_matrix)

    dither_image.show()
