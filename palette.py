from collections import OrderedDict

palettes = OrderedDict()
available_palettes = []

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

    global available_palettes
    available_palettes = palettes.keys()

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
