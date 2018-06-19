from PIL import Image
import numpy
import sys

import palette
import utils

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

# floyd-steinberg
def dither(image_matrix, palette_name):
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

            # distribute the error forward into the surrounding pixels
            if x + 1 < cols:
                new_matrix[x + 1][y    ] = new_matrix[x + 1][y    ] + quant_error * 7. / 16
            if x - 1 >= 0 and y + 1 < rows:
                new_matrix[x - 1][y + 1] = new_matrix[x - 1][y + 1] + quant_error * 3. / 16
            if y + 1 < rows:
                new_matrix[x    ][y + 1] = new_matrix[x    ][y + 1] + quant_error * 5. / 16
            if x + 1 < cols and y + 1 < rows:
                new_matrix[x + 1][y + 1] = new_matrix[x + 1][y + 1] + quant_error * 1. / 16
    return new_matrix


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

    dither_matrix = dither(image_matrix, args.palette)
    dither_image = utils.numpy2pil(dither_matrix)

    dither_image.show()
