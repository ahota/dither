from PIL import Image
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

_available_methods = {
        'floyd_steinberg' : floyd_steinberg,
        'jajuni' : jajuni,
}

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
