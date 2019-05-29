from PIL import Image
from collections import OrderedDict
import numpy
import sys

import error_diffusion
import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode4_2_high'

if __name__ == '__main__':
    import argparse

    palette_help_str = 'Name of palette to use. Can be one of: ' + ', '.join(palette.available_palettes)

    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Path to an image file to dither')
    parser.add_argument('-p', '--palette', type=str, default=default_palette, help=palette_help_str)
    args = parser.parse_args()

    image = utils.open_image(args.image_filename)
    image_bands = list(image.split())

    for b in range(3):
        image_bands[b] = image_bands[b].convert('RGB')
        image_matrix = utils.pil2numpy(image_bands[b])
        dither_matrix = error_diffusion._available_methods['floyd_steinberg'](image_matrix, args.palette)
        image_bands[b] = utils.numpy2pil(dither_matrix)
        image_bands[b] = image_bands[b].convert('L')

    dither_image = Image.merge('RGB', image_bands)
    dither_image.show()
