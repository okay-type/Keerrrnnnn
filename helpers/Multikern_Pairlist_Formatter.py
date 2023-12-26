from mojo.roboFont import CurrentFont, OpenFont
from mojo.UI import GetFile
from lib.UI.spaceCenter.glyphSequenceEditText import splitText

# this will turn a metrics machine pairlist into a multikern pairlist

# step one:
# make a pairlist in metrics machine
#     you should compress groups, but this tool will redo which glyph is shown from a group
#     don't create mirror pairs, this tool will do that instead
#     save it as a file

# step two:
# open a source font from your project
# this tool will use it to get:
#     the glyph order
#     the kerning groups

# step three:
# run this tool to make your mm pairlist into a multikern double pairlist
# it will do a few things:
#     sort the pairlist by the glyph order of your open font
#         consider creating a kerning-specific glyph order with key glyphs up front
#     reprocess each pair by looking for the kerning group then either:
#         picking a preset a key glyph (find 'keyglyphs =' below for the list)
#         or the first group member according to the glyph order
#     create mirrored/flipped pairs, so 'AV' becomes 'AV' and 'VA'
#         there is a dictionary of open/close pairs (find 'openclosepairs =' for the dictionary)
#         there is also a feature to help kern fractions, pairing /*.numr with /*.dnom
#         if mirror flipped pair already in list, add flag duplicate=True



class multikern_pairlist_formatter():

    def __init__(self):
        if CurrentFont():
            self.font = CurrentFont()
        else:
            self.font = OpenFont(GetFile(), showInterface=False)
        if self.font is None:
            return
        self.glyphOrder = self.font.glyphOrder

        pairlist_file = GetFile()
        # pairlist_file = '/Users/Ahh/Okay/Roboscripts/Kerning/pairlists/pairs_by_frequency_with_count.txt'
        # pairlist_file = '/Users/Ahh/Okay/Roboscripts/Kerning/pairlists/test.txt'
        self.pairs = self.openFile(pairlist_file)

        # self.pairlist_sort_by_glyphorder()
        self.make_multikern_double_pairlist()

        self.saveFile(pairlist_file)

        if self.font != CurrentFont():
            self.font.close()

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
                line = str(pair[0][0]) + ' ' + str(pair[0][1]) + ' ' + str(pair[1][0]) + ' ' + str(pair[1][1]) + ' ' + str(pair[2]) + '\n'
                newfile.write(line)
        print('saved multikern pairlist file as', save_file_name)

    def pairlist_sort_by_glyphorder(self):
        self.pairs = [i for j in self.glyphOrder for i in filter(lambda k: k[1] == j, self.pairs)]
        self.pairs = [i for j in self.glyphOrder for i in filter(lambda k: k[0] == j, self.pairs)]

        # https://github.com/robotools/fontParts/issues/552#issuecomment-687594518
    #     glyphOrderMap = {gn: index for index, gn in enumerate(self.glyphOrder)}
    #     self.pairs = self.sort_by_glyph_order_map(glyphOrderMap, self.glyphOrder)

    # def sort_by_glyph_order_map(self, glyphOrderMap, gname_list):
    #     return sorted(gname_list, key=glyphOrderMap.__getitem__)

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

    keyglyphs = 'H O n o l period bracketleft bracketright zero zero.lp zero.sc h.sc o.sc endash bracketleft.uc bracketright.uc h.sups n.sups o.sups'.split(' ')

    def make_multikern_double_pairlist(self):
        mirroredpairs = []
        double_pairlist = []
        for pair in self.pairs:
            mirrored_pair = [pair[1], pair[0]]
            if mirrored_pair[0] in self.openclosepairs:
                mirrored_pair[0] = self.openclosepairs[mirrored_pair[0]]
            if mirrored_pair[1] in self.openclosepairs:
                mirrored_pair[1] = self.openclosepairs[mirrored_pair[1]]
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
