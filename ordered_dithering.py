from PIL import Image
import numpy
import random
import sys

import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

_bayer4x4map = 1./17. * numpy.array([
    [ 1,  9,  3, 11],
    [13,  5, 15,  7],
    [ 4, 12,  2, 10],
    [16,  8, 14,  6]
])

_bayer8x8map = 1./65. * numpy.array([
    [ 0, 48, 12, 60,  3, 51, 15, 63],
    [32, 16, 44, 28, 35, 19, 47, 31],
    [ 8, 56,  4, 52, 11, 59,  7, 55],
    [40, 24, 36, 20, 43, 27, 39, 23],
    [ 2, 50, 14, 62,  1, 49, 13, 61],
    [34, 18, 46, 30, 33, 17, 45, 29],
    [10, 58,  6, 54,  9, 57,  5, 53],
    [42, 26, 38, 22, 41, 25, 37, 21]
])

_clusterdot4x4map = 1./15. * numpy.array([
    [12,  5,  6, 13],
    [ 4,  0,  1,  7],
    [11,  3,  2,  8],
    [15, 10,  9, 14]
])

_clusterdot8x8map = 1./64. * numpy.array([
    [24, 10, 12, 26, 35, 47, 49, 37],
    [ 8,  0,  2, 14, 45, 59, 61, 51],
    [22,  6,  4, 16, 43, 57, 63, 53],
    [30, 20, 18, 28, 33, 41, 55, 39],
    [34, 46, 48, 36, 25, 11, 13, 27],
    [44, 58, 60, 50,  9,  1,  3, 15],
    [42, 56, 62, 52, 23,  7,  5, 17],
    [32, 40, 54, 38, 31, 21, 19, 29]
])

def _bayer(image_matrix, palette_name, size):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            if DEBUGMODE:
                print '<{}, {}>'.format(x, y)
                print 'old = {}'.format(new_matrix[x][y])

            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            if size == 4:
                old_pixel += old_pixel * _bayer4x4map[x % 4][y % 4]
            elif size == 8:
                old_pixel += old_pixel * _bayer8x8map[x % 8][y % 8]
            else:
                pass
            new_pixel = numpy.array(utils.closest_palette_color(old_pixel,
                palette_name), dtype=numpy.float)
            new_matrix[x][y] = new_pixel
    return new_matrix

def bayer4x4(image_matrix, palette_name):
    return _bayer(image_matrix, palette_name, 4)

def bayer8x8(image_matrix, palette_name):
    return _bayer(image_matrix, palette_name, 8)

def _cluster_dot(image_matrix, palette_name, size):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            if DEBUGMODE:
                print '<{}, {}>'.format(x, y)
                print 'old = {}'.format(new_matrix[x][y])

            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            if size == 4:
                old_pixel += old_pixel * _clusterdot4x4map[x % 4][y % 4]
            elif size == 8:
                old_pixel += old_pixel * _clusterdot8x8map[x % 8][y % 8]
            else:
                pass
            new_pixel = numpy.array(utils.closest_palette_color(old_pixel,
                palette_name), dtype=numpy.float)
            new_matrix[x][y] = new_pixel
    return new_matrix

def cluster_dot4x4(image_matrix, palette_name):
    return _cluster_dot(image_matrix, palette_name, 4)

def cluster_dot8x8(image_matrix, palette_name):
    return _cluster_dot(image_matrix, palette_name, 8)

_available_methods = {
        'bayer4x4' : bayer4x4,
        'bayer8x8' : bayer8x8,
        'cluster4x4' : cluster_dot4x4,
        'cluster8x8' : cluster_dot8x8,
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

    dither_matrix = bayer8x8(image_matrix, args.palette)
    dither_image = utils.numpy2pil(dither_matrix)

    dither_image.show()
