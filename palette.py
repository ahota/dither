from collections import OrderedDict
import json,os

palettes = OrderedDict()
available_palettes = []

def _build_c64_palettes():
    global palettes

    print 'building C64 palette'

    # gamma corrected colors from
    # http://unusedino.de/ec64/technical/misc/vic656x/colors/
    palette = [
            [  0.0,           0.0,           0.0        ],
            [254.999999878, 254.999999878, 254.999999878],
            [103.681836072,  55.445357742,  43.038096345],
            [111.932673473, 163.520631667, 177.928819803],
            [111.399725075,  60.720543693, 133.643433983],
            [ 88.102223525, 140.581101312,  67.050415368],
            [ 52.769271594,  40.296416104, 121.446211753],
            [183.892638117, 198.676829993, 110.585717385],
            [111.399725075,  79.245328562,  37.169652483],
            [ 66.932804788,  57.383702891,   0.0        ],
            [153.690586380, 102.553762644,  89.111118307],
            [ 67.999561813,  67.999561813,  67.999561813],
            [107.797780127, 107.797780127, 107.797780127],
            [154.244479632, 209.771445903, 131.584994128],
            [107.797780127,  94.106015515, 180.927622164],
            [149.480882981, 149.480882981, 149.480882981],
    ]
    palettes['c64'] = [[c/255. for c in color] for color in palette]

def _build_websafe_palettes():
    # note that there is only an _accepted_ set of 216 "websafe" colors, but
    # there is no fully standardized set
    # this is using the common set of 216 6-bit colors

    global palettes

    print 'building websafe palette'

    palette = []
    for r in range(6):
        for g in range(6):
            for b in range(6):
                palette.append([r/5.0, g/5.0, b/5.0])
    palettes['websafe'] = palette

def _build_grayscale_palettes():
    global palettes

    print 'building grayscale palettes'

    for bit_depth in range(1, 8):
        levels = 2**bit_depth - 1
        #print '\tbit depth = {}, levels = {}'.format(bit_depth, levels)
        pname = '{}bit_gray'.format(bit_depth)
        palette = [ [0.0, 0.0, 0.0] ]
        for l in range(levels):
            val = float(l+1)/(levels)
            #print '\tl = {}, val = {}'.format(l, val)
            palette.append([val, val, val])
        palettes[pname] = palette

def _build_cga_palettes():
    # this actually builds all possible colors based on rgb combinations of
    # on/off, though some of the colors were not available on CGA

    global palettes

    print 'building cga palettes'

    # generate all the low/dark colors
    low = []
    off_on = (0.0, 2./3.)
    for r in off_on:
        for g in off_on:
            for b in off_on:
                low.append([r, g, b])
    # set brown
    low[6][1] /= 2.

    # generate all the high colors
    high = []
    off_on = (1./3., 1.0)
    for r in off_on:
        for g in off_on:
            for b in off_on:
                high.append([r, g, b])

    # add the colors to their respective palettes

    palettes['cga_mode4_1'] = [ low[0],  # black
                                low[3],  # low cyan
                                low[5],  # low magenta
                                low[7] ] # low white
    palettes['cga_mode4_2'] = [ low[0],  # black
                                low[2],  # low green
                                low[4],  # low red
                                low[6] ] # low yellow (brown)
    palettes['cga_mode4_1_high'] = [ low[0],   # black
                                     high[3],  # high cyan
                                     high[5],  # high magenta
                                     high[7] ] # high white
    palettes['cga_mode4_2_high'] = [ low[0],   # black
                                     high[2],  # high green
                                     high[4],  # high red
                                     high[6] ] # high yellow
    palettes['cga_mode5'] = [ low[0],  # black
                              low[3],  # low cyan
                              low[4],  # low red
                              low[7] ] # low white
    palettes['cga_mode5_high'] = [ low[0],   # black
                                   high[3],  # high cyan
                                   high[4],  # high red
                                   high[7] ] # high white

def _build_ega_palettes():
    global palettes

    print 'building ega palettes'

    # generate all the low/dark colors
    low = []
    off_on = (0.0, 2./3.)
    for r in off_on:
        for g in off_on:
            for b in off_on:
                low.append([r, g, b])
    # set brown
    low[6][1] /= 2.

    # generate all the high colors
    high = []
    off_on = (1./3., 1.0)
    for r in off_on:
        for g in off_on:
            for b in off_on:
                high.append([r, g, b])

    palettes['ega_default'] = low + high # how convenient

def _build_palettes():
    print 'building palettes'
    _build_grayscale_palettes()
    _build_cga_palettes()
    _build_ega_palettes()
    _build_websafe_palettes()
    _build_c64_palettes()

    global palettes

    with open('palettes.cache', 'w') as pf:
        json.dump(palettes, pf)

    global available_palettes
    available_palettes = palettes.keys()

# check if a palette file exists
if os.access('palettes.cache', os.R_OK):
    # check its mtime
    me = os.path.realpath(__file__)
    my_mtime = os.stat(me).st_mtime
    cache_mtime = os.stat('palettes.cache').st_mtime

    if my_mtime > cache_mtime:
        # rebuild cache
        _build_palettes()
    else:
        # read in the cache
        with open('palettes.cache', 'r') as pf:
            palettes = json.load(pf, object_pairs_hook=OrderedDict)
        available_palettes = palettes.keys()
else:
    _build_palettes()

if __name__ == '__main__':
    print available_palettes

    from PIL import Image, ImageDraw

    width = max([len(palettes[p]) for p in palettes])*16
    height = len(available_palettes) * 16

    swatches = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(swatches)

    for p_i, pname in enumerate(available_palettes):
        for c_i, color in enumerate(palettes[pname]):
            pil_color = tuple([int(255*e) for e in color])
            draw.rectangle([c_i*16, p_i*16, (c_i+1)*16, (p_i+1)*16],
                    fill=pil_color, outline=None)

    del draw

    swatches.show()
