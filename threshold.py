from PIL import Image
from collections import OrderedDict
import numpy
import sys

import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

def threshold(image_matrix, palette_name):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            new_pixel = numpy.array(utils.closest_palette_color(old_pixel,
                palette_name), dtype=numpy.float)
            new_matrix[x][y] = new_pixel
    return new_matrix

_available_methods = OrderedDict([
        ('threshold' , threshold),
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

    threshold_matrix = threshold(image_matrix, args.palette)
    threshold_image = utils.numpy2pil(threshold_matrix)

    threshold_image.show()
