from PIL import Image
import numpy
import random
import sys

import palette
import utils

import error_diffusion
import ordered_dithering
import randomized

DEBUGMODE = False
default_method = 'bayer4x4'
default_palette = 'cga_mode4_2_high'

available_methods = {}

available_methods.update(ordered_dithering._available_methods)
available_methods.update(randomized._available_methods)
available_methods.update(error_diffusion._available_methods)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Path to an image file to dither')
    palette_help_str = 'Name of palette to use. Can be one of: ' + ', '.join(palette.available_palettes)
    method_help_str = 'Method to use. Can be one of: ' + ', '.join(available_methods)
    parser.add_argument('-p', '--palette', type=str, default=default_palette, help=palette_help_str)
    parser.add_argument('-m', '--method', type=str, default=default_method, help=method_help_str)
    args = parser.parse_args()

    image = utils.open_image(args.image_filename)
    image_matrix = utils.pil2numpy(image)

    dither_matrix = available_methods[args.method](image_matrix, args.palette)
    dither_image = utils.numpy2pil(dither_matrix)

    dither_image.show()

