import unicodedata

# string builder

'''
center align strings

parts
    before between after

list of contexts
    HHHH AV HHHH VA HHHH            uppercase
    HHHH An nnnn nA HHHH            lowercase
    HHHH Ah hhhh hA HHHH            smallcaps
    HH00 13 00HH00 1/3 00HHH        fractions

positional contexts?
    begin/end characters ¡A A!

maybe
    toggle before/between/after visibility (ui buttons, cycle on controller button?)
    rotate contexts on key press
    standard
        HHHH AV HHHH VA HHHH
    no between
        HHHH AVA HHHH
        HHHH AVWA HHHH
    no ends (before/after)
        AV HHHH VA
        AV HHHH VA
    with referneces
        HH ÄÖ HH AO HH ÄO HH AÖ HH
    repeater
        HHH AVAVAVA HHH
'''


def string_builder(pair_current, pair_flipped, ufolist):
    H = B = 'H'

    # check left glyph
    g = pair_current[0]
    if '.sc' in g:
        H = 'h.sc'
    elif is_this_lower(g, ufolist) is True:
        H = 'n'
    elif g in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
        H = 'zero'
    elif '.' in g or 'superior' in g:
        if '.sups' in g or 'superior' in g:
            H = 'space'
        elif '.subs' in g:
            H = 'H'
        elif g.split('.')[0] in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
            H = 'zero.lp'
    # if '.lp' in g:
    #     H = H + '.lp'

    # check right glyph
    g = pair_current[1]
    if '.sc' in g:
        B = 'h.sc'
    elif is_this_lower(g, ufolist) is True:
        B = 'n'
    elif g in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
        B = 'zero'
    elif '.' in g or 'superior' in g:
        if '.sups' in g or 'superior' in g:
            B = 'space'
        elif '.subs' in g:
            B = 'H'
        elif g.split('.')[0] in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
            B = 'zero.lp'
    # if '.lp' in g:
    #     B = B + '.lp'

    if '.sups' in pair_current[0] or 'superior' in pair_current[0]:
        if '.sups' in pair_current[1] or 'superior' in pair_current[1]:
            H = 'H'
            for g in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
                if g in pair_current[0] or g in pair_current[1]:
                    B = 'zero.sups'
                    break
                else:
                    B = 'n.sups'
    if '.subs' in pair_current[0] and '.subs' in pair_current[1]:
        H = 'H'
        for g in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'):
            if g in pair_current[0] or g in pair_current[1]:
                B = 'zero.subs'
                break

    text = [H, H, H, H, H, pair_current[0], pair_current[1], B, B, B, pair_flipped[0], pair_flipped[1], H, H, H, H, H]

    # check if fractions
    H = 'H'
    if '.numr' in pair_current[0] and '.numr' in pair_current[1]:
        text = [H, H, H, 'zero.numr', 'zero.numr', pair_current[0], pair_current[1], 'zero.numr', 'zero.numr', pair_flipped[0], pair_flipped[1], 'zero.numr', 'zero.numr', H, H, H]
    if '.dnom' in pair_current[0] and '.dnom' in pair_current[1]:
        text = [H, H, H, 'zero.dnom', 'zero.dnom', pair_current[0], pair_current[1], 'zero.dnom', 'zero.dnom', pair_flipped[0], pair_flipped[1], 'zero.dnom', 'zero.dnom', H, H, H]

    if '.numr' in pair_current[1] and '.numr' not in pair_current[0]:
        text = [H, H, H, H, H, pair_current[0], pair_current[1], 'fraction', pair_flipped[0], pair_flipped[1], H, H, H, H, H]

    if '.numr' in pair_current[0] and 'fraction' in pair_current[1]:
        text = [H, H, H, H, 'zero.numr', 'zero.numr', pair_current[0], pair_current[1], 'zero.dnom', 'zero.dnom', H, H, 'zero.numr', 'zero.numr', pair_flipped[0], pair_flipped[1].replace('numr', 'dnom'), 'zero.dnom', 'zero.dnom',H, H, H, H]

    if 'fraction' in pair_current[0] and '.dnom' in pair_current[1]:
        text = [H, H, H, H, 'zero.numr', 'zero.numr', pair_current[0], pair_current[1], 'zero.dnom', 'zero.dnom', H, H, 'zero.numr', 'zero.numr', pair_flipped[0].replace('dnom', 'numr'), pair_flipped[1], 'zero.dnom', 'zero.dnom',H, H, H, H]

    return text

def is_this_lower(g, ufolist):
    answer = False
    if g.islower() and len(g) == 1:
        answer = True
    # what about extended lowercase? eth agrave etc?
    elif len(ufolist) > 0:
        # use first font
        if g in ufolist[0]['ufo'].glyphOrder:
            uni = ufolist[0]['ufo'][g].unicode
            if uni is not None:
                x = unicodedata.category(chr(uni))
                # Ll -- lowercase
                # Lu -- uppercase
                # Lt -- titlecase
                # Lm -- modifier
                # Lo -- other
                if x == 'Ll':
                    answer = True
    return answer
