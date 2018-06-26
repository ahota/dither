from PIL import Image
from collections import OrderedDict
import numpy
import random
import sys

import palette
import utils

import error_diffusion
import ordered_dithering
import randomized
import threshold

DEBUGMODE = False
default_method = 'bayer4x4'
default_palette = 'cga_mode4_2_high'

available_methods = OrderedDict()

available_methods.update(threshold._available_methods)
available_methods.update(randomized._available_methods)
available_methods.update(ordered_dithering._available_methods)
available_methods.update(error_diffusion._available_methods)

def _do_work(work_args):
    image_offset, image_matrix, method, palette_name = work_args

    dither_matrix = available_methods[method](image_matrix, palette_name)
    dither_image = utils.numpy2pil(dither_matrix)

    return (image_offset, dither_image)

def create_collage(image_filename):
    from multiprocessing import Pool, cpu_count
    from PIL import ImageDraw, ImageFont

    image = utils.open_image(image_filename)
    width, height = image.size

    n_palettes = len(palette.available_palettes)
    n_methods  = len(available_methods)

    canvas_size = (width * (n_palettes + 1), height * (n_methods + 1))
    canvas = Image.new('RGB', canvas_size)
    drawer = ImageDraw.Draw(canvas)
    font   = ImageFont.load_default()
    font_color = (255, 255, 255, 255)

    image_matrix = utils.pil2numpy(image)

    work_objects = []

    for p_i, p in enumerate(palette.available_palettes):
        text_pos = ((p_i + 1) * width, height / 2)
        drawer.text(text_pos, p, font=font, fill=font_color)
        for m_i, m in enumerate(available_methods):
            if p_i == 0:
                text_pos = (0, (m_i + 1) * height + height / 2)
                drawer.text(text_pos, m, font=font, fill=font_color)
            image_offset = ((p_i + 1) * width, (m_i + 1) * height)
            work_objects.append( (image_offset, image_matrix, m, p) )
    del drawer

    pool = Pool(cpu_count())

    results = pool.map(_do_work, work_objects)

    for r in results:
        image_offset, dither_image = r
        canvas.paste(dither_image, image_offset)

    canvas.save('collage.png')
    canvas.show()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Path to an image file to dither')
    palette_help_str = 'Name of palette to use. Can be one of: ' + ', '.join(palette.available_palettes)
    method_help_str = 'Method to use. Can be one of: ' + ', '.join(available_methods)
    all_help_str = 'Create a collage using all palettes and all dithering methods'
    parser.add_argument('-p', '--palette', type=str, default=default_palette, help=palette_help_str)
    parser.add_argument('-m', '--method', type=str, default=default_method, help=method_help_str)
    parser.add_argument('-a', '--all', action='store_true', help=all_help_str)
    args = parser.parse_args()

    if args.all:
        create_collage(args.image_filename)
    else:
        image = utils.open_image(args.image_filename)
        image_matrix = utils.pil2numpy(image)

        dither_matrix = available_methods[args.method](image_matrix, args.palette)
        dither_image = utils.numpy2pil(dither_matrix)

        dither_image.show()

