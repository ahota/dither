from PIL import Image
from collections import OrderedDict
import numpy
import sys

import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

_floyd_steinberg_diffusion_matrix = numpy.array([
    [7./16],
    [3./16,5./16,1./16]
])

_jajuni_diffusion_matrix = numpy.array([
    [7./48,5./48],
    [1./16,5./48,7./48,5./48,1./16],
    [1./48,1./16,5./48,1./16,1./48]
])

# zeros are used to pad asymmetric downward diffusion rows
_fan_diffusion_matrix = numpy.array([
    [7./16],
    [1./16,3./16,5./16,0.,0.]
])

_stucki_diffusion_matrix = numpy.array([
    [4./21,2./21],
    [1./21,2./21,4./21,2./21,1./21],
    [1./42,1./21,2./21,1./21,1./42]
])

_burkes_diffusion_matrix = numpy.array([
    [.25,.125],
    [.0625,.125,.25,.125,.0625]
])

_sierra_diffusion_matrix = numpy.array([
    [5./32,3./32],
    [1./16,1./8,5./32,1./8,1./16],
    [1./16,3./32,1./16]
])

_two_row_sierra_diffusion_matrix = numpy.array([
    [1./4,3./16],
    [1./16,1./8,3./16,1./8,1./16]
])

_sierra_lite_diffusion_matrix = numpy.array([
    [0.5],
    [0.25,0.25,0]
])

def _error_diffusion(image_matrix, palette_name, diffusion_matrix):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            if DEBUGMODE:
                print '<{}, {}>'.format(x, y)
                print 'old = {}'.format(new_matrix[x][y])

            # calculate the new pixel value
            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            new_pixel = numpy.array(utils.closest_palette_color(old_pixel,
                palette_name), dtype=numpy.float)
            # replace the old pixel with the new value, and quantify the error
            new_matrix[x][y] = new_pixel
            quant_error = old_pixel - new_pixel

            if DEBUGMODE:
                print 'new = {}'.format(new_pixel)
                print 'quant = {}'.format(quant_error)
                print '-'*20
                if x > 5:
                    sys.exit()

            forward_diffusion = diffusion_matrix[0]
            for ci, coeff in enumerate(forward_diffusion):
                if x + ci + 1 < cols:
                    new_matrix[x + (ci + 1)][y] += quant_error * coeff
            for di, downward_diffusion in enumerate(diffusion_matrix[1:]):
                if y + di + 1 < rows:
                    offset = len(downward_diffusion) / 2
                    for ci, coeff in enumerate(downward_diffusion):
                        if 0 <= x + ci - offset < cols:
                            new_matrix[x + ci - offset][y + di + 1] += quant_error * coeff
    return new_matrix

def floyd_steinberg(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _floyd_steinberg_diffusion_matrix)

def jajuni(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _jajuni_diffusion_matrix)

def fan(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _fan_diffusion_matrix)

def stucki(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _stucki_diffusion_matrix)

def burkes(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _burkes_diffusion_matrix)

def sierra(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _sierra_diffusion_matrix)

def two_row_sierra(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _two_row_sierra_diffusion_matrix)

def sierra_lite(image_matrix, palette_name):
    return _error_diffusion(image_matrix, palette_name, _sierra_lite_diffusion_matrix)

_available_methods = OrderedDict([
        ('floyd_steinberg' , floyd_steinberg),
        ('jajuni' , jajuni),
        ('fan' , fan),
        ('stucki' , stucki),
        ('burkes' , burkes),
        ('sierra' , sierra),
        ('two_row_sierra' , two_row_sierra),
        ('sierra_lite' , sierra_lite),
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

    dither_matrix = floyd_steinberg(image_matrix, args.palette)
    dither_image = utils.numpy2pil(dither_matrix)

    dither_image.show()
