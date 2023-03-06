from AppKit import NSDragOperationMove, NSDragOperationCopy, NSFilenamesPboardType
from vanilla import *
from mojo.roboFont import AllFonts

class Test():

    def __init__(self): 
        self.fontlist = []
        for f in AllFonts():
            font = {}
            if f.info.familyName and f.info.styleName:
                font['fontname'] = f.info.familyName + ' ' + f.info.styleName
            else:
                font['fontname'] = 'No font name'
            font['ufo'] = f
            font['visibile'] = ''
            self.fontlist.append(font)
        self.no_UI_ufos = []
        self.listcount = len(self.fontlist)

        self.w = Window((300, 0, 500, 500))

        self.w.fontlist = List(
            (0, 0, -0, -44),
            items=self.fontlist,
            columnDescriptions=[
                {'title': '', 'key': 'fontname', 'editable': False},
                {'title': '', 'key': 'visibile', 'width': 22},
                {'title': '', 'key': 'ufo', 'width': 0},
            ],
            showColumnTitles=False,
            enableDelete=True,
            editCallback=self.fontlist_edit,
            allowsMultipleSelection=True,
            drawFocusRing=False,
            dragSettings=dict(
                type='genericListPboardType',
                callback=self.fontlist_drag
            ),
            selfDropSettings=dict(
                type='genericListPboardType',
                operation=NSDragOperationMove,
                callback=self.fontlist_drop
            ),
            otherApplicationDropSettings=dict(
                type=NSFilenamesPboardType,
                operation=NSDragOperationCopy,
                callback=self.fontlist_add_noUI_ufo
            ),
        )
        self.w.fontlist_sort = Button(
            (0, -44, -0, 22),
            'Sort',
            sizeStyle='mini',
            callback=self.fontlist_sort,
        )
        self.w.fontlist_reverse = Button(
            (0, -22, -0, 22),
            'Reverse',
            sizeStyle='mini',
            callback=self.fontlist_reverse,
        )
        self.w.open()

    def fontlist_edit(self, sender):  # self.w.lists.fontlist callback
        # print('fontlist_edit')
        self.fontlist = self.w.fontlist.get()
        if self.listcount != len(self.fontlist):
            self.listcount = len(self.fontlist)
            for noUIfont in self.no_UI_ufos:
                toclose = True
                for font in self.fontlist:
                    if font['ufo'] == noUIfont:
                        toclose = False
                if toclose is True:
                    print('closing', noUIfont)
                    noUIfont.close()
                    self.no_UI_ufos.remove(noUIfont)

    def fontlist_drag(self, sender, indexes):  # self.w.lists.fontlist callback
        return indexes
        #

    def fontlist_drop(self, sender, dropInfo):  # self.w.lists.fontlist callback
        isProposal = dropInfo['isProposal']
        if not isProposal:
            indexes = [int(i) for i in sorted(dropInfo['data'])]
            indexes.sort()
            rowIndex = dropInfo['rowIndex']
            items = sender.get()
            toMove = [items[index] for index in indexes]
            for index in reversed(indexes):
                del items[index]
            rowIndex -= len([index for index in indexes if index < rowIndex])
            for font in toMove:
                items.insert(rowIndex, font)
                rowIndex += 1
            sender.set(items)
        return True

    def fontlist_add_noUI_ufo(self, sender, dropInfo):  # self.w.lists.fontlist callback
        supportedFontFileFormats = ['ufo', 'ttf', 'otf', 'woff', 'woff2']
        isProposal = dropInfo['isProposal']
        existingPaths = sender.get()
        paths = dropInfo['data']
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if ospath.splitext(
            path)[-1].lower() in supportedFontFileFormats or ospath.isdir(path)]
        if not paths:
            return False
        if not isProposal:
            rowIndex = dropInfo['rowIndex']
            items = sender.get()
            for i, path in enumerate(paths):
                self.hold = True
                if i >= len(paths) - 1:
                    self.hold = False
                add = True
                for x in self.fontlist:
                    if x['ufo'].path == path:
                        add = False
                if add is True:
                    f = OpenFont(path, showInterface=False)
                    self.no_UI_ufos.append(f)
                    font = {}
                    font['fontname'] = f.info.familyName + ' ' + f.info.styleName
                    font['ufo'] = f
                    font['visibile'] = '👻'
                    items.insert(rowIndex, font)
                    rowIndex += 10
            sender.set(items)
        return True

    def fontlist_reverse(self, sender):
        self.fontlist = list(reversed(self.fontlist))
        self.w.fontlist.set(self.fontlist)
        # redraw font stuff

    def fontlist_sort(self, sender):
        selection = self.w.fontlist.getSelection()
        if len(selection) < 2:
            tempufos = []
            for f in self.fontlist:
                ufo = f['ufo']
                tempufos.append(ufo)
                if ufo.info.openTypeOS2WidthClass is None:
                    print('FYI:', ufo.info.familyName + ' ' + ufo.info.styleName, 'openType OS2 Width Class is None')
                if ufo.info.openTypeOS2WeightClass is None:
                    print('FYI:', ufo.info.familyName + ' ' + ufo.info.styleName, 'openType OS2 Weight Class is None')
            tempufos = FontsList(tempufos)
            tempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isRoman',))
            fonts = sorted(self.fontlist, key=lambda x: tempufos.index(x['ufo']))
            # if resort, put italics first and reverse to ... essentially reverses the weight order
            if fonts == self.fontlist:
                tempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isItalic',))
                tempufos = list(reversed(tempufos))
                fonts = sorted(self.fontlist, key=lambda x: tempufos.index(x['ufo']))
            if fonts != self.fontlist:
                self.fontlist = fonts
                self.w.fontlist.set(self.fontlist)
        else:
            tempufos = []
            otherufos = []
            for i, f in enumerate(self.fontlist):
                ufo = f['ufo']
                if i in selection:
                    tempufos.append(ufo)
                    otherufos.append(None)
                else:
                    otherufos.append(ufo)
            sortedtempufos = FontsList(tempufos)
            sortedtempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isRoman',))
            if sortedtempufos == tempufos:
                sortedtempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isItalic',))
                sortedtempufos = list(reversed(sortedtempufos))
            n = 0
            assembledufos = []
            for x in otherufos:
                if x is None:
                    assembledufos.append(sortedtempufos[n])
                    n += 1
                else:
                    assembledufos.append(x)
            fonts = sorted(self.fontlist, key=lambda x: assembledufos.index(x['ufo']))
            if fonts != self.fontlist:
                self.fontlist = fonts
                self.w.fontlist.set(self.fontlist)


Test()
