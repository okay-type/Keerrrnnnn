
import os
from AppKit import NSFilenamesPboardType, NSDragOperationCopy
from vanilla import Window, List, Button
from mojo.roboFont import OpenFont


action = 'Do Thing'


class doThing():

    def __init__(self, path):

        self.f = OpenFont(path, showInterface=False)

        self.compress_groups()

        for g in self.f.glyphOrder:
            self.f[g].markColor = None

        for g in 'plus minus plusminus divide multiply equal less greater lessequal greaterequal approxequal notequal logicalnot infinity plus.uc minus.uc plusminus.uc divide.uc multiply.uc equal.uc less.uc greater.uc lessequal.uc greaterequal.uc approxequal.uc notequal.uc logicalnot.uc infinity.uc a.sups b.sups c.sups d.sups e.sups f.sups g.sups h.sups i.sups j.sups k.sups l.sups m.sups n.sups o.sups p.sups q.sups r.sups s.sups t.sups u.sups v.sups w.sups x.sups y.sups z.sups zero.sups onesuperior twosuperior threesuperior threesuperior.l four.sups five.sups five.l.sups six.sups six.l.sups seven.sups eight.sups nine.sups nine.l.sups plus.sups minus.sups equal.sups parenleft.sups parenright.sups zero.subs one.subs two.subs three.subs three.l.subs four.subs five.subs five.l.subs six.subs six.l.subs seven.subs eight.subs nine.subs nine.l.subs plus.subs minus.subs equal.subs parenleft.subs parenright.subs zero.numr one.numr two.numr three.numr three.l.numr four.numr five.numr five.l.numr six.numr six.l.numr seven.numr eight.numr nine.numr nine.l.numr zero.dnom one.dnom two.dnom three.dnom three.l.dnom four.dnom five.dnom five.l.dnom six.dnom six.l.dnom seven.dnom eight.dnom nine.dnom nine.l.dnom exclam exclamdown question questiondown interrobang interrobanginverted exclamdown.uc questiondown.uc interrobanginverted.uc'.split(' '):
            self.f[g].markColor = [1, 0, 0, 1]

        self.f.save()
        self.f.close()

        # speed up kerning

        # compress some groups
    def compress_groups(self):
        singles = 'quotesingle quoteleft quoteright'.split(' ')
        doubles = 'quotedbl quotedblleft quotedblright'.split(' ')
        for i, g in enumerate(singles):
            g_left_group = self.get_kern_group(g, 'left')
            g_right_group = self.get_kern_group(g, 'right')
            for kerningPair in self.f.kerning.keys():
                if g_left_group == kerningPair[0] or g_right_group == kerningPair[1]:
                    del self.f.kerning[kerningPair]
            self.f.groups.remove(g_left_group)
            self.f.groups.remove(g_right_group)
            d = doubles[i]
            d_left_group = self.get_kern_group(d, 'left')
            if g not in d_left_group:
                group = list(self.f.groups[d_left_group])
                group.append(g)
                self.f.groups[d_left_group] = group
            d_right_group = self.get_kern_group(d, 'right')
            if g not in d_right_group:
                group = list(self.f.groups[d_right_group])
                group.append(g)
                self.f.groups[d_right_group] = group

    def get_kern_group(self, glyph, side):
        if side == 'left':
            groups = self.f.groups.side1KerningGroups
        if side == 'right':
            groups = self.f.groups.side2KerningGroups
        for key, value in groups.items():
            if glyph in value:
                glyph = key
                break
        return glyph

        # adjust some spacing
        #     sups and subs should be ~20 looser, then kern tighter to themselves
        #     litre, looser on left
        #     math glyphs should be ~10-30 looser
            # for glyph in list
            # increase leftmargin
            # increase width
            # make sure compoents didnt fuck up

        # glyphs to tweak drawings
        #     default parens: longer, below baseline
        #     case parens: keep the same

        # before
        #     You are 32.9809% done with this kerning list.
        #     The next benchmark pair is: four p.sups
        # zero litre


class getListofFiles():

    supportedFontFileFormats = ['.ufo']

    def __init__(self):

        L = T = 0  # top / left
        W = 600  # width
        H = W / 2  # height
        p = 10  # padding
        buttonHeight = p * 2

        title = action + ' To These Files'
        self.w = Window((W, H), title, minSize=(W / 3, H / 3))
        self.w.fileList = List(
            (L, T, -0, -(p * 2 + buttonHeight)),
            [],
            columnDescriptions=[
                {"title": "Files", "allowsSorting": True}],  # files
            showColumnTitles=False,
            allowsMultipleSelection=True,
            enableDelete=True,
            otherApplicationDropSettings=dict(
                type=NSFilenamesPboardType,
                operation=NSDragOperationCopy,
                callback=self.dropCallback
            ),
        )
        buttonText = action
        buttonPos = (p, -(p + buttonHeight), -p, buttonHeight)
        self.w.button = Button(buttonPos, buttonText, callback=self.buttonCallback)
        self.w.open()

    def buttonCallback(self, sender):
        for path in self.w.fileList:
            doThing(path['Files'])

    def dropCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingPaths = sender.get()
        paths = dropInfo["data"]
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if os.path.splitext(path)[-1].lower() in self.supportedFontFileFormats or os.path.isdir(path)]
        if not paths:
            return False
        if not isProposal:
            for path in paths:
                item = {}
                item['Files'] = path
                self.w.fileList.append(item)
        return True


getListofFiles()

