from mojo.roboFont import CurrentFont, OpenFont
from vanilla import Window, TextBox, CheckBox, Button
from mojo.UI import GetFile
from lib.UI.spaceCenter.glyphSequenceEditText import splitText
from AppKit import NSEvent, NSShiftKeyMask, NSCommandKeyMask, NSAlternateKeyMask, NSControlKeyMask

# this will turn a metrics machine pairlist into a multikern pairlist
# you need to use a ufo as a reference for glyph order and kerning groups

# there are some options
    # sort by the glyph order of the reference font
        # sometimes I use a ufo with a custom glyph order
        # sometimes I use a pairlist from an different project
    # do key glyphs first
        # there is a hard-coded list of key glyphs that are useful to see first
        # it's at the top of the class, edit away
    # make mirror pairs
        # this will create a list in AB BA format
    # make open/close pairs
        # only useful with making mirror pairs
        # this uses another hard-coded list of open-close pairs, set in make_multikern_double_pairlist()


class multikern_pairlist_formatter():

    keyglyphs = 'H O n o l period bracketleft bracketright zero zero.lp zero.sc h.sc o.sc endash bracketleft.uc bracketright.uc h.sups n.sups o.sups'.split(' ')

    def __init__(self):
        self.temp_source_paths = []

        self.font = None
        self.font_close = False
        reference_font = 'Open a font to use as a reference for glyph order and kerning groups'
        if CurrentFont():
            self.font = CurrentFont()
            reference_font = self.font.info.familyName + ' ' + self.font.info.styleName
            print('reference_font', reference_font)
        else:
            print('CurrentFont', CurrentFont())

        u = 22
        self.w = Window((250, u*10.75), 'Multikern Pairlist Formatter')

        self.w.openreferencefont = Button((5, u*.2, -5, u), 'Open Reference Font', callback=self.openreferencefont)
        self.w.versionnew = TextBox((5, u*1.4, -5, u*2), reference_font)

        self.w.option_sort = CheckBox((5, u*4.25, -5, u), 'Sort by Reference Glyph Order', value=True, callback=self.checks)
        self.w.option_key = CheckBox((5, u*5.25, -5, u), 'Do Key Glyphs First', value=True, callback=self.checks)
        self.w.option_mirror = CheckBox((5, u*6.25, -5, u), 'Make Mirror Pairs', value=True, callback=self.checks)
        self.w.option_openclose = CheckBox((5, u*7.25, -5, u), 'Make Open/Close Pairs ', value=True, callback=self.checks)
        self.w.go = Button((5, u*9.5, -5, u), 'Go!', callback=self.format)
        if self.font is None:
            self.w.go.enable(False)

        self.w.open()

        self.checkboxes = [self.w.option_sort, self.w.option_key, self.w.option_mirror, self.w.option_openclose]
        self.w.open()

    def checks(self, sender):
        sender_value = sender.get()
        if NSEvent.modifierFlags() and NSShiftKeyMask:
            for checkbox in self.checkboxes:
                if checkbox != sender:
                    checkbox.set(not sender_value)
            return

    def openreferencefont(self, sender):
        self.font = OpenFont(GetFile(), showInterface=False)
        if self.font is not None:
            self.w.go.enable(True)
            reference_font = self.font.info.familyName + ' ' + self.font.info.styleName
            self.w.versionnew.set(reference_font)
            self.font_close = True

    def format(self, sender):

        self.glyphOrder = self.font.glyphOrder

        if self.w.option_key.get() == True:
            self.sort_keyglyphs()

        pairlist_file = GetFile(message='Select a pairlist to format', fileTypes=['txt'])
        self.pairs = self.openFile(pairlist_file)

        if self.w.option_sort.get() == True:
            self.pairlist_sort_by_glyphorder()

        self.make_multikern_double_pairlist()

        self.saveFile(pairlist_file)

        if self.font_close == True:
            self.font.close()
        self.w.close()

    def openFile(self, pairlist_file):
        # cmap = self.font.getCharacterMapping()
        pairs = []
        with open(pairlist_file, encoding='utf-8') as userFile:
            lines = userFile.read()
            lines = lines.splitlines()
        for line in lines:
            # line = line.replace('/', '//')  # splitText misses slashes
            pair = line.split(' ')
            # pair = splitText(pair, cmap)
            if len(pair) == 2:
                if pair[0] in self.glyphOrder and pair[1] in self.glyphOrder:
                    pairs.append(list(pair))
        return pairs

    def saveFile(self, pairlist_file):
        save_file_name = pairlist_file.replace('.txt', '-multikern.txt')
        with open(save_file_name, 'w', encoding='utf-8') as newfile:
            newfile.write('#KPL:P: My Pair List' + '\n')
            for n, pair in enumerate(self.pairs):
                line = ''
                if pair[0][0]:
                    line += str(pair[0][0]) + ' '
                if pair[0][1]:
                    line += str(pair[0][1]) + ' '
                if pair[1][0]:
                    line += str(pair[1][0]) + ' '
                if pair[1][1]:
                    line += str(pair[1][1]) + ' '
                if pair[2]:
                    line += str(pair[2]) + ' '
                line += '\n'
                newfile.write(line)
        print('saved multikern pairlist file as', save_file_name)

    def sort_keyglyphs(self):
        neworder = self.keyglyphs
        for g in self.glyphOrder:
            if g not in neworder:
                neworder.append(g)
        self.glyphOrder = neworder

    def pairlist_sort_by_glyphorder(self):
        self.pairs = [i for j in self.glyphOrder for i in filter(lambda k: k[1] == j, self.pairs)]
        self.pairs = [i for j in self.glyphOrder for i in filter(lambda k: k[0] == j, self.pairs)]

        # https://github.com/robotools/fontParts/issues/552#issuecomment-687594518
    #     glyphOrderMap = {gn: index for index, gn in enumerate(self.glyphOrder)}
    #     self.pairs = self.sort_by_glyph_order_map(glyphOrderMap, self.glyphOrder)

    # def sort_by_glyph_order_map(self, glyphOrderMap, gname_list):
    #     return sorted(gname_list, key=glyphOrderMap.__getitem__)


    def make_multikern_double_pairlist(self):

        openclosepairs = {
            'quoteleft': 'quoteright',
            'quoteright': 'quoteleft',
            'quotedblleft': 'quotedblright',
            'quotedblright': 'quotedblleft',
            'quotesinglbase': 'quoteright',
            'quotedblbase': 'quotedblright',
            'guilsinglleft': 'guilsinglright',
            'guilsinglright': 'guilsinglleft',
            'guillemetleft': 'guillemetright',
            'guillemetright': 'guillemetleft',
            'parenleft': 'parenright',
            'parenright': 'parenleft',
            'bracketleft': 'bracketright',
            'bracketright': 'bracketleft',
            'braceleft': 'braceright',
            'braceright': 'braceleft',
            'bracketangleleft': 'bracketangleright',
            'bracketangleright': 'bracketangleleft',
            'exclamdown': 'exclam',
            'exclam': 'exclamdown',
            'questiondown': 'question',
            'question': 'questiondown',
            'interrobanginverted': 'interrobang',
            'interrobang': 'interrobanginverted',
            'less': 'greater',
            'greater': 'less',
            'lessequal': 'greaterequal',
            'greaterequal': 'lessequal',
            'commaheavyturnedornament': 'commaheavyornament',
            'commaheavyornament': 'commaheavyturnedornament',
            'commaheavydoubleturnedornament': 'commaheavydoubleornament',
            'commaheavydoubleornament': 'commaheavydoubleturnedornament',
            'parenleft.sups': 'parenright.sups',
            'parenright.sups': 'parenleft.sups',
            'parenleft.subs': 'parenright.subs',
            'parenright.subs': 'parenleft.subs',
            'guilsinglleft.uc': 'guilsinglright.uc',
            'guilsinglright.uc': 'guilsinglleft.uc',
            'guillemetleft.uc': 'guillemetright.uc',
            'guillemetright.uc': 'guillemetleft.uc',
            'parenleft.uc': 'parenright.uc',
            'parenright.uc': 'parenleft.uc',
            'bracketleft.uc': 'bracketright.uc',
            'bracketright.uc': 'bracketleft.uc',
            'braceleft.uc': 'braceright.uc',
            'braceright.uc': 'braceleft.uc',
            'bracketangleleft.uc': 'bracketangleright.uc',
            'bracketangleright.uc': 'bracketangleleft.uc',
            'exclamdown.uc': 'exclam',
            'questiondown.uc': 'question',
            'interrobanginverted.uc': 'interrobang',
            'less.uc': 'greater.uc',
            'greater.uc': 'less.uc',
            'lessequal.uc': 'greaterequal.uc',
            'greaterequal.uc': 'lessequal.uc',
        }
        if self.w.option_openclose.get() == False:
            openclosepairs = {}

        mirroredpairs = []
        double_pairlist = []
        for pair in self.pairs:
            if self.w.option_mirror.get() == False:
                mirrored_pair = ['', '']
                unique = ''
            else:
                mirrored_pair = [pair[1], pair[0]]
                if mirrored_pair[0] in openclosepairs:
                    mirrored_pair[0] = openclosepairs[mirrored_pair[0]]
                if mirrored_pair[1] in openclosepairs:
                    mirrored_pair[1] = openclosepairs[mirrored_pair[1]]
                if 'dnom' in mirrored_pair[0]:
                    mirrored_pair[0] = mirrored_pair[0].replace('dnom', 'numr')
                if 'numr' in mirrored_pair[1]:
                    mirrored_pair[1] = mirrored_pair[1].replace('numr', 'dnom')

                # get group of mirrored_pair
                mirrored_pair[0] = self.get_kern_group(self.font, mirrored_pair[0], 'left')
                mirrored_pair[1] = self.get_kern_group(self.font, mirrored_pair[1], 'right')

                # get key glyph for those groups
                left = mirrored_pair[0]
                right = mirrored_pair[1]
                if 'kern1' in left:
                    leftgroupglyphs = self.font.groups[left]
                    # if keyglyph in group, use that
                    for keyglyph in self.keyglyphs:
                        if keyglyph in leftgroupglyphs:
                            left = keyglyph
                            break
                    # otherwise use the first glyph from the group
                    if left == mirrored_pair[0]:
                        for g in self.glyphOrder:
                            if g in leftgroupglyphs:
                                left = g
                                break
                if 'kern2' in right:
                    rightgroupglyphs = self.font.groups[right]
                    for keyglyph in self.keyglyphs:
                        if keyglyph in rightgroupglyphs:
                            right = keyglyph
                            break
                    if right == mirrored_pair[1]:
                        for g in self.glyphOrder:
                            if g in rightgroupglyphs:
                                right = g
                                break
                mirrored_pair = [left, right]

                # test if pair already exists in pairlist
                unique = True
                if mirrored_pair in self.pairs or mirrored_pair in mirroredpairs:
                    if mirrored_pair != pair:
                        unique = False
                mirroredpairs.append(mirrored_pair)

            # add to doubled pair list
            double_pairlist.append([pair, mirrored_pair, unique])

        self.pairs = double_pairlist


    def get_kern_group(self, f, glyph, side):
        if side == 'left':
            groups = f.groups.side1KerningGroups
        if side == 'right':
            groups = f.groups.side2KerningGroups
        for key, value in groups.items():
            if glyph in value:
                glyph = key
                break
        return glyph


multikern_pairlist_formatter()
