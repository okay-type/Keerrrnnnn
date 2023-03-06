from AppKit import NSScreen
from AppKit import NSDragOperationMove, NSDragOperationCopy, NSFilenamesPboardType
from AppKit import NSColor
from AppKit import NSTextAlignmentRight, NSTextAlignmentCenter, NSTextAlignmentLeft
from AppKit import NSAttributedString, NSForegroundColorAttributeName, NSParagraphStyleAttributeName, NSMutableParagraphStyle, NSFont, NSFontAttributeName
from mojo.subscriber import Subscriber, WindowController
from mojo.subscriber import registerRoboFontSubscriber, unregisterRoboFontSubscriber, roboFontSubscriberEventRegistry
from vanilla import Window, Group, EditText, TextBox, Button
from vanilla import ProgressBar, VerticalLine, HorizontalLine
from vanilla import List, CheckBoxListCell
from merz import MerzView
from mojo.UI import NumberEditText
from mojo.UI import GetFile
from mojo.UI import PostBannerNotification
from mojo.events import extractNSEvent
from mojo.events import postEvent
from mojo.extensions import setExtensionDefault, getExtensionDefault, registerExtensionDefaults
from glyphNameFormatter import GlyphName
from os import path as ospath
from random import random
from itertools import repeat

'''
SN30 controller setup in Enjoyable

Button 5    option      left shoulder                   option
Button 6    shift       right shoulder                                  shift

Button 9    f13         select          toggle AB/BA
Button 10   f14         start           mirror flip
Button 4    comma       x               up pair
Button 3    period      a               down pair
Button 1    f17         y                               zero pair
Button 2    f15         b               copy to flip    copy from flip

Axis 1                  up/down         change font     top/bottom font
Axis 2                  left/right      +5 kerning      +10 kerning     apply to all ufos

'''

testpairlist = '#header\nA A\nA B\nB B\nA C\nA D\nparenleft H\n'
openclosepairs = {"‘": "’", "“": "”", "«": "»", "»": "«", "⸄": "⸅", "⸉": "⸊", "⸠": "⸡", "”": "”", "’": "’", "'": "'", '"': '"', "¡": "!", "¿": "?", "←": "→", "→": "←", "(": ")", "[": "]", "{": "}", "parenleft.sups": "parenright.sups", "parenleft.subs": "parenright.subs", "parenleft.uc": "parenright.uc", "bracketleft.uc": "bracketright.uc", "braceleft.uc": "braceright.uc", "bracketangleleft.uc": "bracketangleright.uc", "guillemetleft": "guillemetright", "guillemetleft.uc": "guillemetright.uc", "commaheavydoubleturnedornament": "commaheavydoubleornament", "parenleft.vert": "parenright.vert", "bracketleft.vert": "bracketright.vert", "braceleft.vert": "braceright.vert", "bracketangleleft.vert": "bracketangleright.vert", "guillemetleft.vert": "guillemetright.vert", "parenleft.uc.vert": "parenright.uc.vert", "bracketleft.uc.vert": "bracketright.uc.vert", "braceleft.uc.vert": "braceright.uc.vert", "bracketangleleft.uc.vert": "bracketangleright.uc.vert", "guillemetleft.uc.vert": "guillemetright.uc.vert", "less.vert": "greater.vert", "less.vert.uc": "greater.vert.uc", "<": ">", ">": "<", "less": "greater", "less.uc": "greater.uc", "exclamdown": "exclam", "questiondown": "question", "exclamdown.uc": "exclam", "questiondown.uc": "question", "༺": "༻", "༼": "༽", "᚛": "᚜", "⁅": "⁆", "⁽": "⁾", "₍": "₎", "⌈": "⌉", "⌊": "⌋", "〈": "〉", "❨": "❩", "❪": "❫", "❬": "❭", "❮": "❯", "❰": "❱", "❲": "❳", "❴": "❵", "⟅": "⟆", "⟦": "⟧", "⟨": "⟩", "⟪": "⟫", "⟬": "⟭", "⟮": "⟯", "⦃": "⦄", "⦅": "⦆", "⦇": "⦈", "⦉": "⦊", "⦋": "⦌", "⦍": "⦎", "⦏": "⦐", "⦑": "⦒", "⦓": "⦔", "⦕": "⦖", "⦗": "⦘", "⧘": "⧙", "⧚": "⧛", "⧼": "⧽", "⸢": "⸣", "⸤": "⸥", "⸦": "⸧", "⸨": "⸩", "〈": "〉", "《": "》", "「": "」", "『": "』", "【": "】", "〔": "〕", "〖": "〗", "〘": "〙", "〚": "〛", "〝": "〞", "⹂": "〟", "﴿": "﴾", "︗": "︘", "︵": "︶", "︷": "︸", "︹": "︺", "︻": "︼", "︽": "︾", "︿": "﹀", "﹁": "﹂", "﹃": "﹄", "﹇": "﹈", "﹙": "﹚", "﹛": "﹜", "﹝": "﹞", "（": "）", "［": "］", "｛": "｝", "｟": "｠", "｢": "｣", }
defaultKey = 'com.okay.KernKernKern'


'''

    - update lineview
        - get last notification
        - on font list shuffle
        - on pairlist selection change 
        - on flip sides
        - on currentpair change

    - update line preview positions 
        - get all notifications
        - on lineview change 
        - on kerning change
            - update button values instantly
        - maybe have a loading icon for unupdated lineview

SPEED UP

get kern values as little as possible
use fontdict or button values

IMPROVE

alias -> references
left alias
right alias
how to set both easily

needs some kind of solution for groups...
    show key glyph?
    show group list? 
    shortcut to see group
    indication that alias is group?

'''


class KernKernKern(Subscriber, WindowController):

    debug = False

    # control variables
    adjustSmall = 5
    adjustBig = 10

    # ui varaibles
    smallFontSize = 24
    bigFontSize = 50
    rowHeight = 100
    labelOffsetSmall = -500
    kernColorPos = (0, .7, .6, 1)
    kernColorNeg = (1, 0, 0, 1)
    control = 'H'

    # internal data
    listcount = 0
    paircount = len(testpairlist)
    addedUIbuttons = []
    noUIfonts = []
    kernUIData = None
    focusOn = [0, False]
    activeUFO = None
    hold = False

    def build(self):
        initialDefaults = {
            defaultKey + '.aliases': {},
            defaultKey + '.pairCurrent': ['O', 'k'],
        }
        registerExtensionDefaults(initialDefaults)
        self.pairAliases = getExtensionDefault(defaultKey + '.aliases')
        self.pairCurrent = getExtensionDefault(defaultKey + '.pairCurrent')
        self.pairCurrent = [self.pairCurrent[0], self.pairCurrent[1]]
        # self.pairFlipped = [self.pairCurrent[1], self.pairCurrent[0]]

        (screenX, screenY), (screenW, screenH) = NSScreen.mainScreen().visibleFrame()

        self.w = Window(
            (0, 0, screenW*.75, screenH),
            'MultiKern',
            minSize=None,
            maxSize=None,
            textured=False,
            fullScreenMode=None,
            titleVisible=False,
            fullSizeContentView=True,
        )
        self.w.getNSWindow().setBackgroundColor_(
            NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))

        self.w.ui = Group((20, 0, 330, -0))

        self.w.kerningMerzView = MerzView(
            (350, 0, -300, -0),
            backgroundColor=(1, 1, 1, 1),
            delegate=self,
        )
        self.fontlist = []
        self.w.fontlist = List(
            (-300, 0, -0, screenH * .25),
            items=self.fontlist,
            columnDescriptions=[
                {'title': '', 'key': 'fontname', 'editable': False},
                {'title': '', 'key': 'visibile', 'width': 22},
                {'title': '', 'key': 'ufo', 'width': 0},
            ],
            showColumnTitles=False,
            enableDelete=True,
            editCallback=self.listEditCallback,
            allowsMultipleSelection=True,
            drawFocusRing=False,
            dragSettings=dict(
                type='genericListPboardType',
                callback=self.listDragCallback
            ),
            selfDropSettings=dict(
                type='genericListPboardType',
                operation=NSDragOperationMove,
                callback=self.listDropCallback
            ),
            otherApplicationDropSettings=dict(
                type=NSFilenamesPboardType,
                operation=NSDragOperationCopy,
                callback=self.listAddNoUIUFO
            ),
        )

        self.w.controls = Group((20, -110, 300, -0))
        self.w.controls.progress = ProgressBar(
            (0, 78, -0, 22),
            minValue=0,
            maxValue=1,
            sizeStyle='small',
            progressStyle='bar',
        )
        self.w.controls.load = Button(
            (0, 54, 44, 22), 'Load', sizeStyle='mini', callback=self.loadPairlist)
        self.w.controls.save = Button(
            (44, 54, 44, 22), 'Save', sizeStyle='mini', callback=self.saveFiles)
        self.w.controls.save.enable(False)

        #

        # univeral adjust
        self.w.controls.universal = Group((0, 0, -0, 22))
        y, x, h, b = (0, 0, 20, 18)
        self.w.controls.L = Group((10, 0, 140, -0))
        self.w.controls.L.minus2 = okButton(
            (x, y, b, b),
            title='◀︎◀︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustLminus2,
        )
        x += b
        self.w.controls.L.minus = okButton(
            (x, y, b, b),
            title='◀︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustLminus,
        )
        x += b
        self.w.controls.L.edit = okNumberEditText(
            (x + 3, y + 2, -x - 3, 22),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i='AllFonts',
            callback=self.editL,
        )
        self.w.controls.L.edit.setPlaceholder('?')
        self.flatEditText(self.w.controls.L.edit, 'center')
        x = -x
        self.w.controls.L.plus = okButton(
            (x, y, b, b),
            title='▶︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustLplus,
        )
        x += b
        self.w.controls.L.plus2 = okButton(
            (x, y, b, b),
            title='▶︎▶︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustLplus2,
        )
        x += b
        self.flatButton(self.w.controls.L.minus2)
        self.flatButton(self.w.controls.L.minus)
        self.flatButton(self.w.controls.L.plus)
        self.flatButton(self.w.controls.L.plus2)

        self.w.controls.divider = VerticalLine((154, 0, 2, 23))

        # flipped pair controls
        self.w.controls.R = Group((160, 0, -0, -0))
        self.w.controls.R.minus2 = okButton(
            (x, y, b, b),
            title='◀︎◀︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustRminus2,
        )
        x += b
        self.w.controls.R.minus = okButton(
            (x, y, b, b),
            title='◀︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustRminus,
        )
        x += b
        self.w.controls.R.edit = okNumberEditText(
            (x + 3, y + 2, -x - 3, 22),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i='AllFonts',
            callback=self.editR,
        )
        self.flatEditText(self.w.controls.R.edit, 'center')
        self.w.controls.R.edit.setPlaceholder('?')
        x = -x
        self.w.controls.R.plus = okButton(
            (x, y, b, b),
            title='▶︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustRplus,
        )
        x += b
        self.w.controls.R.plus2 = okButton(
            (x, y, b, b),
            title='▶︎▶︎',
            sizeStyle='small',
            i='AllFonts',
            callback=self.adjustRplus2,
        )
        x += b
        self.flatButton(self.w.controls.R.minus2)
        self.flatButton(self.w.controls.R.minus)
        self.flatButton(self.w.controls.R.plus)
        self.flatButton(self.w.controls.R.plus2)

        # univeral alias
        self.w.controls.alias = Group((0, 22, -0, 22))
        y, x, h, b = (0, 0, 20, 25)
        self.w.controls.alias.L = Group((3, 0, 140, -0))
        self.w.controls.alias.L.Z = okButton(
            (x, y, b, b),
            title='◯',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasLeftZero,
        )
        x += b
        self.w.controls.alias.L.A = okButton(
            (x, y, b, b),
            title='ⓐ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasLeft,
        )
        x += b
        self.w.controls.alias.L.B = okButton(
            (x, y, b, b),
            title='ⓑ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasLeft,
        )
        x += b
        self.w.controls.alias.L.C = okButton(
            (x, y, b, b),
            title='ⓒ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasLeft,
        )
        self.w.controls.alias.R = Group((153, 0, -0, -0))
        x = 0
        self.w.controls.alias.R.Z = okButton(
            (x, y, b, b),
            title='◯',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasRightZero,
        )
        x += b
        self.w.controls.alias.R.A = okButton(
            (x, y, b, b),
            title='ⓐ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasRight,
        )
        x += b
        self.w.controls.alias.R.B = okButton(
            (x, y, b, b),
            title='ⓑ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasRight,
        )
        x += b
        self.w.controls.alias.R.C = okButton(
            (x, y, b, b),
            title='ⓒ',
            sizeStyle='small',
            i='Alias',
            callback=self.universalAliasRight,
        )
        self.flatButton(self.w.controls.alias.L.Z)
        self.flatButton(self.w.controls.alias.L.A)
        self.flatButton(self.w.controls.alias.L.B)
        self.flatButton(self.w.controls.alias.L.C)
        self.flatButton(self.w.controls.alias.R.Z)
        self.flatButton(self.w.controls.alias.R.A)
        self.flatButton(self.w.controls.alias.R.B)
        self.flatButton(self.w.controls.alias.R.C)

        self.pairlist = self.prepPairList()
        self.w.pairlist = List(
            (-300, screenH * .25, -0, -0),
            self.pairlist,
            columnDescriptions=[{'title': 'Left'}, {'title': 'Right'}],
            allowsSorting=True,
            selectionCallback=self.pairlistSelectionCallback,
        )
        self.w.controls.progress.set(
            (self.w.pairlist.getSelection()[0] + 1) / self.paircount)
        self.w.pairlist.setSelection([0])

    def started(self):
        self.fontListAddOpen()
        self.w.open()
        self.buildKernUI()

    def windowWillClose(self, sender):
        for font in self.fontlist:
            if font['visibile'] == '👻':
                font['ufo'].close()
        setExtensionDefault(defaultKey + '.aliases', self.pairAliases)
        setExtensionDefault(defaultKey + '.pairCurrent', self.pairCurrent)

    def saveFiles(self, sender):
        for i, font in enumerate(self.fontlist):
            ufo = font['ufo']
            ufo.save()
        self.w.controls.save.enable(False)

    def loadPairlist(self, sender):
        # open pair list file
        self.hold = True
        savepair = self.pairCurrent
        pairlist = []
        with open(GetFile(message='Open a pairlist.txt file.'), encoding='utf-8') as userFile:
            if userFile is not None:
                lines = userFile.read()
                lines = lines.splitlines()
                for line in lines:
                    pairlist.append(line)
        self.pairlist = self.prepPairList(pairlist)
        self.w.pairlist.set(self.pairlist)
        self.paircount = len(self.pairlist)

        # find index of last saved current pair in pair list and set it
        self.pairCurrent = getExtensionDefault(defaultKey + '.pairCurrent')
        self.pairCurrent = [self.pairCurrent[0], self.pairCurrent[1]]

        try:
            i = self.pairlist.index(
                {'Left': self.pairCurrent[0], 'Right': self.pairCurrent[1]})
        except:
            print(self.pairCurrent[0], self.pairCurrent[1], 'not in pairlist')
            i = 0
        self.hold = False
        self.w.pairlist.setSelection([i])

    def prepPairList(self, pairlist=None):
        cleanpairs = []
        if pairlist is None:
            pairlist = testpairlist.split('\n')
        for pair in pairlist:
            if pair[:0] != '#' and pair.count(' ') == 1:
                left, right = pair.split(' ')
                pairdict = {}
                pairdict['Left'] = left
                pairdict['Right'] = right
                cleanpairs.append(pairdict)
        return cleanpairs

    def pairlistSelectionCallback(self, sender):
        if self.hold is False:
            pairindex = sender.getSelection()
            if pairindex == []:
                pairindex = [0]
            pairindex = pairindex[0]
            progress = (pairindex + 1) / self.paircount
            self.w.controls.progress.set(progress)
            self.pairCurrent = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
            if self.kernUIData is not None:
                self.makeKernUIPositionData()
                self.addKernUIGlyphLayers()
                self.positionKernUIGlyphLayers()
                self.updateUIbuttons()
            for notifyAt in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]:
                if pairindex/self.paircount < notifyAt and progress >= notifyAt:
                    print('You are ' + str(progress*100) + '% done with this kerning list!')
                    PostBannerNotification('Robofont', 'You are ' + str(progress*100) + '% done with this kerning list!')
                    if notifyAt+.05 < 1:
                        print('The next benchmark pair is:', self.pairlist[int(self.paircount * (notifyAt+.05))])
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def fontListAddOpen(self):
        allFonts = FontsList(AllFonts())
        allFonts.sortBy('magic')
        for i, f in enumerate(allFonts):
            self.hold = True
            if i >= len(allFonts) - 1:
                self.hold = False
            font = {}
            font['open'] = True
            font['fontname'] = f.info.familyName + ' ' + f.info.styleName
            font['ufo'] = f
            font['visibile'] = ''
            self.w.fontlist.append(font)

    def listDragCallback(self, sender, indexes):
        return indexes
        #

    def listDropCallback(self, sender, dropInfo):
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
            self.buildKernUI()
        return True

    def listAddNoUIUFO(self, sender, dropInfo):
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
                f = OpenFont(path, showInterface=False)
                self.noUIfonts.append(f)
                font = {}
                font['open'] = True
                font['fontname'] = f.info.familyName + ' ' + f.info.styleName
                font['ufo'] = f
                font['visibile'] = '👻'
                items.insert(rowIndex, font)
                rowIndex += 10
            sender.set(items)
        self.buildKernUI()
        return True

    def listEditCallback(self, sender):
        if self.hold is False:
            self.fontlist = self.w.fontlist.get()
            if len(self.fontlist) != self.listcount:
                self.listcount = len(self.fontlist)
                for noUIfont in self.noUIfonts:
                    toclose = True
                    for font in self.fontlist:
                        if font['ufo'] == noUIfont:
                            toclose = False
                    if toclose is True:
                        print('closing', noUIfont)
                        noUIfont.close()
                self.buildKernUI()

    def acceptsFirstResponder(self, view):
        return True
        #

    def keyDown(self, view, event):
        shiftDown = extractNSEvent(event)['shiftDown']
        commandDown = extractNSEvent(event)['commandDown']
        capLockDown = extractNSEvent(event)['capLockDown']
        optionDown = extractNSEvent(event)['optionDown']
        controlDown = extractNSEvent(event)['controlDown']
        keycode = event.keyCode()

        LshoulderDown = optionDown
        RshoulderDown = shiftDown

        if keycode == 47:  # period
            index = self.w.pairlist.getSelection()[0]
            if index + 1 < self.paircount:
                self.w.pairlist.setSelection(
                    [self.w.pairlist.getSelection()[0] + 1])
        if keycode == 43:  # comma
            index = self.w.pairlist.getSelection()[0]
            if index > 0:
                self.w.pairlist.setSelection(
                    [self.w.pairlist.getSelection()[0] - 1])

        if keycode == 125:  # down arrow
            if RshoulderDown != 0:
                self.incrementFocusOnBottom()
            else:
                self.incrementFocusOn(1, 0)
        if keycode == 126:  # up arrow
            if RshoulderDown != 0:
                self.incrementFocusOnTop()
            else:
                self.incrementFocusOn(-1, 0)
        if keycode == 105:  # f13 / select
            self.incrementFocusOn(0, 1)

        if keycode == 64:  # f17 / y
            if RshoulderDown != 0:
                # zero
                pair = self.pairCurrent
                if 1 == self.focusOn[1]:
                    pair = self.pairFlipped
                self.updateKerning(self.activeUFO, pair, 0)

        if keycode == 107:  # f14 / start
            # self.incrementFocusOn(0, 1) # flip font focus
            self.pairCurrent = self.reversePairSmart(self.pairCurrent)
            self.makeKernUIPositionData()
            self.addKernUIGlyphLayers()
            self.positionKernUIGlyphLayers()
            self.updateUIbuttons()

        if keycode == 113:  # f15 / b
            ufo = self.fontlist[self.activeUFO]['ufo']
            pair = self.pairCurrent
            flip = self.pairFlipped
            if 1 == self.focusOn[1]:
                pair = self.pairFlipped
                flip = self.pairCurrent
            if RshoulderDown != 0:
                # copy to opposite
                kernValue = ufo.kerning.find(flip)
                self.updateKerning(self.activeUFO, pair, kernValue)
            # elif LshoulderDown != 0:
            #     kernValue = ufo.kerning.find(pair)
            #     for i, font in enumerate(self.fontlist):
            #         self.updateKerning(i, pair, kernValue)
            else:
                # copy from opposite
                kernValue = ufo.kerning.find(pair)
                self.updateKerning(self.activeUFO, flip, kernValue)

        if keycode == 123 or keycode == 124:  # leftarrow # rightarrow

            adjustAmount = self.adjustSmall
            if RshoulderDown != 0:
                adjustAmount = self.adjustBig

            pair = self.pairCurrent
            if 1 == self.focusOn[1]:
                pair = self.pairFlipped

            mod = 1
            if keycode == 123:
                mod = -1
            if LshoulderDown > 0:  # + option /
                # adjust pair in all fonts
                for i, font in enumerate(self.fontlist):
                    ufo = self.fontlist[i]['ufo']
                    kernValue = ufo.kerning.find(pair) or 0
                    self.updateKerning(i, pair, kernValue + (mod * adjustAmount))
            else:
                # adjust pair in active font
                ufo = self.fontlist[self.activeUFO]['ufo']
                kernValue = ufo.kerning.find(pair) or 0
                self.updateKerning(self.activeUFO, pair, kernValue + (mod * adjustAmount))

    def incrementFocusOn(self, y, x):
        self.focusOn[0] += y
        if self.focusOn[0] > self.listcount - 1:
            self.focusOn[0] = 0
        if self.focusOn[0] < 0:
            self.focusOn[0] = self.listcount - 1
        if x == 1:
            self.focusOn[1] = not self.focusOn[1]
        self.activeFontIndicator()

    def incrementFocusOnTop(self):
        self.focusOn[0] = 0
        self.activeFontIndicator()

    def incrementFocusOnBottom(self):
        self.focusOn[0] = self.listcount - 1
        self.activeFontIndicator()

    def activeFontIndicator(self):
        for i, font in enumerate(self.fontlist):
            name = 'buttons' + str(i)
            ui = getattr(self.w.ui, name)
            ui.activeL.show(False)
            ui.activeR.show(False)
            if i == self.focusOn[0]:
                self.activeUFO = i
                if 0 == self.focusOn[1]:
                    ui.activeL.show(True)
                if 1 == self.focusOn[1]:
                    ui.activeR.show(True)
        return

    def mouseEntered(self, event):
        return
        #

    def fontDocumentDidOpenNew(self, notification):
        f = notification['font']
        font = {}
        font['open'] = True
        font['fontname'] = f.info.familyName + ' ' + f.info.styleName
        font['ufo'] = f
        font['visibile'] = True
        self.w.fontlist.append(font)
        self.buildKernUI()

    def fontDocumentDidOpen(self, notification):
        f = notification['font']
        font = {}
        font['open'] = True
        font['fontname'] = f.info.familyName + ' ' + f.info.styleName
        font['ufo'] = f
        font['visibility'] = True
        self.w.fontlist.append(font)
        self.buildKernUI()

    def fontDocumentWillClose(self, notification):
        font = notification['font']
        for i, x in enumerate(self.w.fontlist):
            if font == x['ufo']:
                del self.w.fontlist[i]
        self.buildKernUI()

    def buildKernUI(self):
        self.kernUIData = {}
        self.kernUIData['baseLayer'] = None
        self.kernUIData['fontData'] = []

        view = self.w.kerningMerzView
        container = view.getMerzContainer()
        container.clearSublayers()
        yInv = view.height()

        self.buildUIbuttons()

        baseLayer = container.appendBaseSublayer(
            size=(view.width(), view.height()),
        )
        self.kernUIData['baseLayer'] = baseLayer

        with baseLayer.sublayerGroup():
            for i, font in enumerate(self.fontlist):
                fontlayer = container.appendBaseSublayer(
                    position=(0, yInv - (self.rowHeight * (i + 1.5))),
                    size=(view.width(), self.rowHeight),
                )
                fontlayer.addSublayerScaleTransformation(self.bigFontSize / 1000, name='scale', center=(0, 0))

                fontlayersmall = container.appendBaseSublayer(
                    position=(0, yInv - (self.rowHeight * (i + 1.5))),
                    size=(view.width(), self.rowHeight),
                )
                fontlayersmall.addSublayerScaleTransformation(self.smallFontSize / 1000, name='scale', center=(0, 0))
                fontlayersmall.addTranslationTransformation((view.width()/2, 0), name='translateX')

                fontData = {}
                fontData['ufo'] = font['ufo']
                fontData['fontLayer'] = fontlayer
                fontData['fontLayerSmall'] = fontlayersmall
                fontData['glyphLayers'] = []
                fontData['glyphLayersSmall'] = []
                fontData['glyphs'] = []
                fontData['xadvance'] = []
                fontData['kerns'] = {}
                self.kernUIData['fontData'].append(fontData)

        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()

    def makeKernUIPositionData(self):
        if self.kernUIData is None:
            return

        # build new data
        for i, fontData in enumerate(self.kernUIData['fontData']):
            # reset data
            fontData['glyphs'] = []
            fontData['xadvance'] = []
            fontData['kerns'] = {}

            ufo = fontData['ufo']
            ufoGlyphOrder = ufo.glyphOrder

            H = B = self.control
            if '.sc' in self.pairCurrent[1] and 'h.sc' in ufoGlyphOrder:
                B = 'h.sc'
            elif self.pairCurrent[1].islower() and len(self.pairCurrent[1]) == 1:
                B = 'n'

            text = [H, H, H, H, self.pairCurrent[0], self.pairCurrent[1], B, B, B, B, self.pairFlipped[0], self.pairFlipped[1], H, H, H, H]

            if '.numr' in self.pairCurrent[0]:
                text = [H, H, H, H, self.pairCurrent[0], 'fraction', 'zero.dnom', H, H, H, H]
            if '.dnom' in self.pairCurrent[1]:
                text = [H, H, H, H, 'zero.numr', 'fraction', self.pairCurrent[1], H, H, H, H]

            # build new data
            x = kernvalue = 0
            for n, glyphName in enumerate(text):
                if glyphName in ufoGlyphOrder:
                    fontData['glyphs'].append(glyphName)
                    fontData['xadvance'].append(x)
                    x += ufo[glyphName].width
                    kernvalue = 0
                    if n < len(text) - 1:
                        pair = (glyphName, text[n+1])
                        if pair not in fontData['kerns']:
                            kernvalue = ufo.kerning.find((glyphName, text[n + 1])) or 0
                            fontData['kerns'][tuple(pair)] = kernvalue
                        x += kernvalue

                    if n == len(text)-1:
                        fontData['xadvance'].append(x+ufo[glyphName].width)

    def addKernUIGlyphLayers(self):
        baseLayer = self.kernUIData['baseLayer']
        if self.kernUIData is None or baseLayer is None:
            return
        with baseLayer.sublayerGroup():
            for i, fontData in enumerate(self.kernUIData['fontData']):

                # reset data
                fontData['glyphLayers'] = []
                fontData['glyphLayersSmall'] = []
                ufo = fontData['ufo']
                fontlayer = fontData['fontLayer']
                fontlayer.clearSublayers()
                fontlayersmall = fontData['fontLayerSmall']
                fontlayersmall.clearSublayers()

                # build new data
                for glyphName in fontData['glyphs']:
                    glyphPath = ufo[glyphName].getRepresentation('merz.CGPath')

                    glyphLayer = fontlayer.appendPathSublayer(position=(0, 0),)
                    glyphLayer.setPath(glyphPath)
                    fontData['glyphLayers'].append(glyphLayer)

                    glyphLayerSmall = fontlayersmall.appendPathSublayer(position=(0, 0),)
                    glyphLayerSmall.setPath(glyphPath)
                    fontData['glyphLayersSmall'].append(glyphLayerSmall)

    def positionKernUIGlyphLayers(self):
        if self.kernUIData is None:
            return

        biggestX = 0
        for i, fontData in enumerate(self.kernUIData['fontData']):
            for n, glyphLayer in enumerate(fontData['glyphLayers']):
                x = fontData['xadvance'][n]

                kern = 0
                if n < len(fontData['glyphLayers'])-1:
                    pair = (fontData['glyphs'][n], fontData['glyphs'][n+1])
                    try:
                        kern = fontData['kerns'][tuple(pair)]
                    except:
                        kern = 0

                glyphLayer.setPosition((x, 0))
                glyphLayer.clearSublayers()
                if kern != 0:
                    if kern < 0:
                        c = self.kernColorNeg
                    if kern > 0:
                        c = self.kernColorPos
                    glyphLayer.appendTextLineSublayer(
                        position=(fontData['xadvance'][n+1]-x, self.labelOffsetSmall),
                        size=(10, 1),
                        pointSize=10,
                        text=str(kern),
                        fillColor=(*c,),
                        horizontalAlignment='center',
                    )
                if n == len(fontData['glyphLayers'])-1:
                    x = fontData['xadvance'][n+1]
                if x > biggestX:
                    biggestX = x

        for i, fontData in enumerate(self.kernUIData['fontData']):
            x = biggestX/(1/(self.bigFontSize/1000))
            fontLayerSmall = fontData['fontLayerSmall']
            fontLayerSmall.removeTransformation('translateX')
            fontLayerSmall.addTranslationTransformation((x, 0), name='translateX')
            for n, glyphLayersSmall in enumerate(fontData['glyphLayersSmall']):
                x = fontData['xadvance'][n]
                glyphLayersSmall.setPosition((x, 0))

    def buildUIbuttons(self):
        # remove old buttons
        for added in self.addedUIbuttons:
            if hasattr(self.w.ui, added):
                delattr(self.w.ui, added)

        self.addedUIbuttons = []
        width = 300
        ypos = self.rowHeight * 1.12
        height = self.rowHeight

        # labels
        pair = Group((0, ypos - 59, width, height))
        pair.left = EditText(
            (0, 0, width / 4, -0),
            sizeStyle='mini',
            placeholder='left',
            continuous=False,
            callback=self.pairOverride1,
        )
        pair.right = EditText(
            (width / 4 + 10, 0, width / 2, -0),
            sizeStyle='mini',
            placeholder='right',
            continuous=False,
            callback=self.pairOverride2,
        )
        self.flatEditText(pair.right)
        self.flatEditText(pair.left)
        pair.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
        pair.left2 = EditText(
            (width / 2, 0, width / 4, -0),
            sizeStyle='mini',
            placeholder='right',
            continuous=False,
            callback=self.aliasChanged0,
        )
        pair.right2 = EditText(
            (width / 2 + width / 4 + 10, 0, -0, -0),
            sizeStyle='mini',
            placeholder='left',
            continuous=False,
            callback=self.aliasChanged1,
        )
        self.flatEditText(pair.right2)
        self.flatEditText(pair.left2)
        pair.left2.getNSTextField().setAlignment_(NSTextAlignmentRight)
        setattr(self.w.ui, 'pair', pair)
        self.addedUIbuttons.append('pair')

        for i, font in enumerate(self.fontlist):
            y, x, h, b = (0, 0, 20, 18)
            ui = Group((0, ypos, width, height))

            # kern pair controls
            ui.L = Group((10, y, width / 2 - 10, -0))
            ui.L.minus2 = okButton(
                (x, y, b, b),
                title='◀︎◀︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustLminus2,
            )
            x += b
            ui.L.minus = okButton(
                (x, y, b, b),
                title='◀︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustLminus,
            )
            x += b
            ui.L.edit = okNumberEditText(
                (x + 3, y + 2, -x - 3, 22),
                text='',
                allowEmpty=True,
                allowFloat=False,
                decimals=0,
                continuous=False,
                sizeStyle='small',
                i=i,
                callback=self.editL,
            )
            self.flatEditText(ui.L.edit, 'center')
            x = -x
            ui.L.plus = okButton(
                (x, y, b, b),
                title='▶︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustLplus,
            )
            x += b
            ui.L.plus2 = okButton(
                (x, y, b, b),
                title='▶︎▶︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustLplus2,
            )
            x += b
            self.flatButton(ui.L.minus2)
            self.flatButton(ui.L.minus)
            self.flatButton(ui.L.plus)
            self.flatButton(ui.L.plus2)

            ui.divider = VerticalLine((width / 2 + 4, y, 2, 23))

            # flipped pair controls
            ui.R = Group((width / 2 + 10, y, width / 2 - 10, -0))
            ui.R.minus2 = okButton(
                (x, y, b, b),
                title='◀︎◀︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustRminus2,
            )
            x += b
            ui.R.minus = okButton(
                (x, y, b, b),
                title='◀︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustRminus,
            )
            x += b
            ui.R.edit = okNumberEditText(
                (x + 3, y + 2, -x - 3, 22),
                text='',
                allowEmpty=True,
                allowFloat=False,
                decimals=0,
                continuous=False,
                sizeStyle='small',
                i=i,
                callback=self.editR,
            )
            self.flatEditText(ui.R.edit, 'center')
            x = -x
            ui.R.plus = okButton(
                (x, y, b, b),
                title='▶︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustRplus,
            )
            x += b
            ui.R.plus2 = okButton(
                (x, y, b, b),
                title='▶︎▶︎',
                sizeStyle='small',
                i=i,
                callback=self.adjustRplus2,
            )
            x += b
            self.flatButton(ui.R.minus2)
            self.flatButton(ui.R.minus)
            self.flatButton(ui.R.plus)
            self.flatButton(ui.R.plus2)

            # alt one
            margin = 2
            y += h + 4
            kbut = (width - 18) * .25 - b
            ui.alt1 = Group((10, y, -0, h))
            ui.alt1.left = TextBox((0, 0, kbut, -0), sizeStyle='mini',)
            ui.alt1.kern = TextBox((kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt1.right = TextBox(
                (kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt1.flipleft = TextBox(
                ((width / 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt1.flip = TextBox(
                ((width / 2) + kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt1.flipright = TextBox(
                ((width / 2) + kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt1.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt1.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt1.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
            ui.alt1.flip.getNSTextField().setAlignment_(NSTextAlignmentCenter)

            # alt 2
            y += h
            ui.alt2 = Group((10, y, -0, h))
            ui.alt2.left = TextBox((0, 0, kbut, -0), sizeStyle='mini',)
            ui.alt2.kern = TextBox((kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt2.right = TextBox(
                (kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt2.flipleft = TextBox(
                ((width / 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt2.flip = TextBox(
                ((width / 2) + kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt2.flipright = TextBox(
                ((width / 2) + kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt2.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt2.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt2.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
            ui.alt2.flip.getNSTextField().setAlignment_(NSTextAlignmentCenter)

            # alt 3
            y += h
            ui.alt3 = Group((10, y, -0, h))
            ui.alt3.left = TextBox((0, 0, kbut, -0), sizeStyle='mini',)
            ui.alt3.kern = TextBox((kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt3.right = TextBox(
                (kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt3.flipleft = TextBox(
                ((width / 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt3.flip = TextBox(
                ((width / 2) + kbut, 0, b * 2, -0), sizeStyle='mini')
            ui.alt3.flipright = TextBox(
                ((width / 2) + kbut + (b * 2), 0, kbut, -0), sizeStyle='mini',)
            ui.alt3.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt3.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt3.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
            ui.alt3.flip.getNSTextField().setAlignment_(NSTextAlignmentCenter)

            ui.activeL = HorizontalLine((10, b + 3, width / 2 - 4, 1))
            ui.activeL.setBorderColor(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1))
            ui.activeR = HorizontalLine((width / 2 + 5, b + 3, 0, 1))
            ui.activeR.setBorderColor(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1))

            ui.activeL.show(True)
            ui.activeR.show(False)

            name = 'buttons' + str(i)
            setattr(self.w.ui, name, ui)
            self.addedUIbuttons.append(name)
            ypos += height

        self.updateUIbuttons()

    def updateUIbuttons(self):
        grey = NSColor.colorWithCalibratedRed_green_blue_alpha_(.7, .7, .8, 1)
        black = NSColor.blackColor()
        red = NSColor.redColor()

        self.activeFontIndicator()

        pair = self.w.ui.pair
        pair.left.set(self.pairCurrent[0])
        pair.right.set(self.pairCurrent[1])
        pair.left2.set(self.pairFlipped[0])
        pair.right2.set(self.pairFlipped[1])

        self.w.controls.alias.L.A.show(False)
        self.w.controls.alias.L.B.show(False)
        self.w.controls.alias.L.C.show(False)
        self.w.controls.alias.R.A.show(False)
        self.w.controls.alias.R.B.show(False)
        self.w.controls.alias.R.C.show(False)
        self.w.controls.alias.L.A.i = None
        self.w.controls.alias.R.A.i = None
        self.w.controls.alias.L.B.i = None
        self.w.controls.alias.R.B.i = None
        self.w.controls.alias.L.C.i = None
        self.w.controls.alias.R.C.i = None

        for i, font in enumerate(self.fontlist):

            name = 'buttons' + str(i)
            ui = getattr(self.w.ui, name)
            ufo = font['ufo']

            if self.kernUIData['fontData'] == []:
                kernValue = ufo.kerning.find(self.pairCurrent) or 0
                flipValue = ufo.kerning.find(self.pairFlipped) or 0
            else:
                kernValue = 0
                flipValue = 0
                fontData = self.kernUIData['fontData'][i]
                if tuple(self.pairCurrent) in fontData['kerns']:
                    kernValue = fontData['kerns'][tuple(self.pairCurrent)] or 0
                if tuple(self.pairFlipped) in fontData['kerns']:
                    flipValue = fontData['kerns'][tuple(self.pairFlipped)] or 0

            ui.L.edit.set(kernValue)
            ui.R.edit.set(flipValue)

            leftAB, rightAB = self.pairCurrent
            leftBA, rightBA = self.pairFlipped
            pairsAB = []
            pairsBA = []
            if leftAB in self.pairAliases:
                l = self.pairAliases[leftAB]
                r = rightAB
                if rightAB in self.pairAliases:
                    r = self.pairAliases[rightAB]
                    pairsAB.append([l, r])
                    pairsAB.append([leftAB, r])
                    pairsAB.append([l, rightAB])
                else:
                    pairsAB.append([l, r])
            else:
                l = leftAB
                r = rightAB
                if rightAB in self.pairAliases:
                    r = self.pairAliases[rightAB]
                    pairsAB.append([l, r])

            if leftBA in self.pairAliases:
                l = self.pairAliases[leftBA]
                r = rightBA
                if rightBA in self.pairAliases:
                    r = self.pairAliases[rightBA]
                    pairsBA.append([l, r])
                    pairsBA.append([leftBA, r])
                    pairsBA.append([l, rightBA])
                else:
                    pairsBA.append([l, r])
            else:
                l = leftBA
                r = rightBA
                if rightBA in self.pairAliases:
                    r = self.pairAliases[rightBA]
                    pairsBA.append([l, r])

            ui.alt1.show(False)
            ui.alt2.show(False)
            ui.alt3.show(False)

            if len(pairsAB) > 0:
                if self.kernUIData['fontData'] != [] and tuple(pairsAB[0]) in fontData['kerns']:
                    altkern = fontData['kerns'][tuple(pairsAB[0])] or 0
                else:
                    altkern = ufo.kerning.find(pairsAB[0]) or 0
                if self.kernUIData['fontData'] != [] and tuple(pairsBA[0]) in fontData['kerns']:
                    altflip = fontData['kerns'][tuple(pairsBA[0])] or 0
                else:
                    altflip = ufo.kerning.find(pairsBA[0]) or 0

                groupsL_cp = self.notNone([s for s in ufo.groups.findGlyph(self.pairCurrent[0]) if 'public.kern1' in s])[0]
                groupsR_cp = self.notNone([s for s in ufo.groups.findGlyph(self.pairCurrent[1]) if 'public.kern2' in s])[0]
                groupsL_fp = self.notNone([s for s in ufo.groups.findGlyph(self.pairFlipped[0]) if 'public.kern1' in s])[0]
                groupsR_fp = self.notNone([s for s in ufo.groups.findGlyph(self.pairFlipped[1]) if 'public.kern2' in s])[0]

                ui.alt1.show(True)

                ui.alt1.left.set(pairsAB[0][0])
                ui.alt1.kern.set(str(altkern))
                ui.alt1.right.set(pairsAB[0][1])

                ui.alt1.flipleft.set(pairsBA[0][0])
                ui.alt1.flip.set(str(altflip))
                ui.alt1.flipright.set(pairsBA[0][1])

                if altkern != kernValue:
                    ui.alt1.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.alt1.kern.getNSTextField().setTextColor_(black)
                if altflip != flipValue:
                    ui.alt1.flip.getNSTextField().setTextColor_(red)
                else:
                    ui.alt1.flip.getNSTextField().setTextColor_(black)

                if groupsL_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[0][0]) if 'public.kern1' in s])[0]:
                    ui.alt1.left.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt1.left.getNSTextField().setTextColor_(black)
                if groupsR_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[0][1]) if 'public.kern2' in s])[0]:
                    ui.alt1.right.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt1.right.getNSTextField().setTextColor_(black)
                if groupsL_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[0][0]) if 'public.kern1' in s])[0]:
                    ui.alt1.flipleft.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt1.flipleft.getNSTextField().setTextColor_(black)
                if groupsR_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[0][1]) if 'public.kern2' in s])[0]:
                    ui.alt1.flipright.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt1.flipright.getNSTextField().setTextColor_(black)

                self.w.controls.alias.L.A.show(True)
                self.w.controls.alias.R.A.show(True)
                self.w.controls.alias.L.A.i = str(pairsAB[0][0] + ' ' + pairsAB[0][1])
                self.w.controls.alias.R.A.i = str(pairsBA[0][0] + ' ' + pairsBA[0][1])

            if len(pairsAB) > 1:
                if self.kernUIData['fontData'] != [] and tuple(pairsAB[1]) in fontData['kerns']:
                    altkern = fontData['kerns'][tuple(pairsAB[1])] or 0
                else:
                    altkern = ufo.kerning.find(pairsAB[1]) or 0
                if self.kernUIData['fontData'] != [] and tuple(pairsBA[1]) in fontData['kerns']:
                    altflip = fontData['kerns'][tuple(pairsBA[1])] or 0
                else:
                    altflip = ufo.kerning.find(pairsBA[1]) or 0

                ui.alt2.show(True)

                ui.alt2.left.set(pairsAB[1][0])
                ui.alt2.kern.set(str(altkern))
                ui.alt2.right.set(pairsAB[1][1])

                ui.alt2.flipleft.set(pairsBA[1][0])
                ui.alt2.flip.set(str(altflip))
                ui.alt2.flipright.set(pairsBA[1][1])

                if altkern != kernValue:
                    ui.alt2.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.alt2.kern.getNSTextField().setTextColor_(black)
                if altflip != flipValue:
                    ui.alt2.flip.getNSTextField().setTextColor_(red)
                else:
                    ui.alt2.flip.getNSTextField().setTextColor_(black)

                if groupsL_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[1][0]) if 'public.kern1' in s])[0]:
                    ui.alt2.left.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt2.left.getNSTextField().setTextColor_(black)
                if groupsR_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[1][1]) if 'public.kern2' in s])[0]:
                    ui.alt2.right.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt2.right.getNSTextField().setTextColor_(black)
                if groupsL_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[1][0]) if 'public.kern1' in s])[0]:
                    ui.alt2.flipleft.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt2.flipleft.getNSTextField().setTextColor_(black)
                if groupsR_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[1][1]) if 'public.kern2' in s])[0]:
                    ui.alt2.flipright.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt2.flipright.getNSTextField().setTextColor_(black)

                self.w.controls.alias.L.B.show(True)
                self.w.controls.alias.R.B.show(True)
                self.w.controls.alias.L.B.i = str(pairsAB[1][0] + ' ' + pairsAB[1][1])
                self.w.controls.alias.R.B.i = str(pairsBA[1][0] + ' ' + pairsBA[1][1])

            if len(pairsAB) > 2:
                if self.kernUIData['fontData'] != [] and tuple(pairsAB[2]) in fontData['kerns']:
                    altkern = fontData['kerns'][tuple(pairsAB[2])] or 0
                else:
                    altkern = ufo.kerning.find(pairsAB[2]) or 0
                if self.kernUIData['fontData'] != [] and tuple(pairsBA[2]) in fontData['kerns']:
                    altflip = fontData['kerns'][tuple(pairsBA[2])] or 0
                else:
                    altflip = ufo.kerning.find(pairsBA[2]) or 0

                ui.alt3.show(True)

                ui.alt3.left.set(pairsAB[2][0])
                ui.alt3.kern.set(str(altkern))
                ui.alt3.right.set(pairsAB[2][1])

                ui.alt3.flipleft.set(pairsBA[2][0])
                ui.alt3.flip.set(str(altflip))
                ui.alt3.flipright.set(pairsBA[2][1])

                if altkern != kernValue:
                    ui.alt3.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.alt3.kern.getNSTextField().setTextColor_(black)
                if altflip != flipValue:
                    ui.alt3.flip.getNSTextField().setTextColor_(red)
                else:
                    ui.alt3.flip.getNSTextField().setTextColor_(black)

                if groupsL_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[2][0]) if 'public.kern1' in s])[0]:
                    ui.alt3.left.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt3.left.getNSTextField().setTextColor_(black)
                if groupsR_cp == self.notNone([s for s in ufo.groups.findGlyph(pairsAB[2][1]) if 'public.kern2' in s])[0]:
                    ui.alt3.right.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt3.right.getNSTextField().setTextColor_(black)
                if groupsL_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[2][0]) if 'public.kern1' in s])[0]:
                    ui.alt3.flipleft.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt3.flipleft.getNSTextField().setTextColor_(black)
                if groupsR_fp == self.notNone([s for s in ufo.groups.findGlyph(pairsBA[2][1]) if 'public.kern2' in s])[0]:
                    ui.alt3.flipright.getNSTextField().setTextColor_(grey)
                else:
                    ui.alt3.flipright.getNSTextField().setTextColor_(black)

                self.w.controls.alias.L.C.show(True)
                self.w.controls.alias.R.C.show(True)
                self.w.controls.alias.L.C.i = str(pairsAB[2][0] + ' ' + pairsAB[2][1])
                self.w.controls.alias.R.C.i = str(pairsBA[2][0] + ' ' + pairsBA[2][1])

    def notNone(self, grouplist):
        if len(grouplist) > 0:
            return grouplist
        else:
            return ['fffffff']

    def updateUIbuttonsQuicker(self, i, pair, value):
        black = NSColor.blackColor()
        red = NSColor.redColor()

        if value == '' or value == 'None' or value is None:
            value = 0
        name = 'buttons' + str(i)
        ui = getattr(self.w.ui, name)

        if pair == self.pairCurrent:
            ui.L.edit.set(value)

        if pair == self.pairFlipped:
            ui.R.edit.set(value)

        if ui.alt1.isVisible() is True:
            if [ui.alt1.left.get(), ui.alt1.right.get()] == pair:
                ui.alt1.kern.set(value)

            if [ui.alt1.flipleft.get(), ui.alt1.flipright.get()] == pair:
                ui.alt1.flip.set(value)

            if pair == self.pairCurrent:
                kern = ui.alt1.kern.get() or 0
                if str(value) == str(kern):
                    ui.alt1.kern.getNSTextField().setTextColor_(black)
                else:
                    ui.alt1.kern.getNSTextField().setTextColor_(red)

            if pair == self.pairFlipped:
                kern = ui.alt1.flip.get() or 0
                if str(value) == str(kern):
                    ui.alt1.flip.getNSTextField().setTextColor_(black)
                else:
                    ui.alt1.flip.getNSTextField().setTextColor_(red)

        if ui.alt2.isVisible() is True:
            if [ui.alt1.left.get(), ui.alt2.right.get()] == pair:
                ui.alt2.kern.set(value)

            if [ui.alt2.flipleft.get(), ui.alt2.flipright.get()] == pair:
                ui.alt2.flip.set(value)

            if pair == self.pairCurrent:
                kern = ui.alt2.kern.get() or 0
                if str(value) == str(kern):
                    ui.alt2.kern.getNSTextField().setTextColor_(black)
                else:
                    ui.alt2.kern.getNSTextField().setTextColor_(red)
            elif pair == self.pairFlipped:
                kern = ui.alt2.flip.get() or 0
                if str(value) == str(kern):
                    ui.alt2.flip.getNSTextField().setTextColor_(black)
                else:
                    ui.alt2.flip.getNSTextField().setTextColor_(red)

        if ui.alt3.isVisible() is True:
            if [ui.alt3.left.get(), ui.alt3.right.get()] == pair:
                ui.alt3.kern.set(value)

            if [ui.alt3.flipleft.get(), ui.alt3.flipright.get()] == pair:
                ui.alt3.flip.set(value)

            if pair == self.pairCurrent:
                kern = ui.alt3.kern.get() or 0
                if str(value) == str(kern):
                    ui.alt3.kern.getNSTextField().setTextColor_(black)
                else:
                    ui.alt3.kern.getNSTextField().setTextColor_(red)
            elif pair == self.pairFlipped:
                kern = ui.alt3.flip.get() or 0
                if str(value) == str(kern):
                    ui.alt3.flip.getNSTextField().setTextColor_(black)
                else:
                    ui.alt3.flip.getNSTextField().setTextColor_(red)

    def alt(self, sender):
        i = sender.i
        pair = sender.pair
        adjust = sender.adjust
        print(i, pair, adjust)
        self.updateKerning(i, pair, adjust)

    def adjustLminus2(self, sender):
        adjust = -self.adjustBig
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairCurrent, adjust, hold)
        else:
            self.adjust(i, self.pairCurrent, adjust)

    def adjustLminus(self, sender):
        adjust = -self.adjustSmall
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairCurrent, adjust, hold)
        else:
            self.adjust(i, self.pairCurrent, adjust)

    def adjustLplus(self, sender):
        adjust = self.adjustSmall
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairCurrent, adjust, hold)
        else:
            self.adjust(i, self.pairCurrent, adjust)

    def adjustLplus2(self, sender):
        adjust = self.adjustBig
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairCurrent, adjust, hold)
        else:
            self.adjust(i, self.pairCurrent, adjust)

    def adjustRminus2(self, sender):
        adjust = -self.adjustBig
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairFlipped, adjust, hold)
        else:
            self.adjust(i, self.pairFlipped, adjust)

    def adjustRminus(self, sender):
        adjust = -self.adjustSmall
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairFlipped, adjust, hold)
        else:
            self.adjust(i, self.pairFlipped, adjust)

    def adjustRplus(self, sender):
        adjust = self.adjustSmall
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairFlipped, adjust, hold)
        else:
            self.adjust(i, self.pairFlipped, adjust)

    def adjustRplus2(self, sender):
        adjust = self.adjustBig
        i = sender.i
        if i == 'AllFonts':
            for n, font in enumerate(self.fontlist):
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.adjust(n, self.pairFlipped, adjust, hold)
        else:
            self.adjust(i, self.pairFlipped, adjust)

    def adjust(self, i, pair, adjust, hold=False):
        kern = self.fontlist[i]['ufo'].kerning.find(pair) or 0
        self.updateKerning(i, pair, kern + adjust, hold)

    def editL(self, sender):
        i = sender.i
        value = sender.get()
        if i == 'AllFonts':
            if value is not None:
                sender.set('')
                for n, font in enumerate(self.fontlist):
                    hold = True
                    if n+1 == len(self.fontlist):
                        hold = False
                    self.updateKerning(n, self.pairCurrent, value, hold)
        else:
            self.updateKerning(i, self.pairCurrent, value)
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def editR(self, sender):
        i = sender.i
        value = sender.get()
        if i == 'AllFonts':
            if value is not None:
                sender.set('')
                for n, font in enumerate(self.fontlist):
                    hold = True
                    if n+1 == len(self.fontlist):
                        hold = False
                    self.updateKerning(n, self.pairFlipped, value, hold)
        else:
            self.updateKerning(i, self.pairFlipped, value)
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def pairOverride1(self, sender):
        self.pairCurrent[0] = sender.get()
        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()
        self.updateUIbuttons()
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def pairOverride2(self, sender):
        self.pairCurrent[1] = sender.get()
        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()
        self.updateUIbuttons()
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def aliasChanged0(self, sender):
        new = sender.get()
        sender.set(self.pairFlipped[0])
        self.aliasChanged(self.pairFlipped[0], new)
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def aliasChanged1(self, sender):
        new = sender.get()
        sender.set(self.pairFlipped[1])
        self.aliasChanged(self.pairFlipped[1], new)
        nsObject = self.w.kerningMerzView.getNSView()
        nsObject.window().makeFirstResponder_(nsObject)

    def aliasChanged(self, g, new):
        if new == '':
            del self.pairAliases[g]
        elif new != g:
            self.pairAliases[g] = new
        setExtensionDefault(defaultKey + '.aliases', self.pairAliases)
        self.updateUIbuttons()

    def universalAliasLeftZero(self, sender):
        for n, font in enumerate(self.fontlist):
            hold = True
            if n+1 == len(self.fontlist):
                hold = False
            self.updateKerning(n, self.pairCurrent, 0, hold)

    def universalAliasRightZero(self, sender):
        for n, font in enumerate(self.fontlist):
            hold = True
            if n+1 == len(self.fontlist):
                hold = False
            self.updateKerning(n, self.pairFlipped, 0, hold)

    def universalAliasLeft(self, sender):
        self.universalAlias(self.pairCurrent, sender.i.split(' '))

    def universalAliasRight(self, sender):
        self.universalAlias(self.pairFlipped, sender.i.split(' '))

    def universalAlias(self, targetpair, aliaspair):
        if aliaspair is not None:
            for n, font in enumerate(self.fontlist):
                ufo = font['ufo']
                kernValue = ufo.kerning.find(aliaspair) or 0
                hold = True
                if n+1 == len(self.fontlist):
                    hold = False
                self.updateKerning(n, targetpair, kernValue, hold)

    def updateKerning(self, index, pair, value, hold=False):
        self.w.controls.save.enable(True)

        left, right = pair
        f = self.fontlist[index]['ufo']

        matching = [s for s in f.groups.findGlyph(left) if 'public.kern1' in s]
        if len(matching) > 0:
            left = matching[0]
        matching = [s for s in f.groups.findGlyph(right) if 'public.kern2' in s]
        if len(matching) > 0:
            right = matching[0]

        if value == 0 or value == '' or value == 'None' or value is None:
            f.kerning[(left, right)] = 0
            f.kerning.remove((left, right))
        else:
            f.kerning[(left, right)] = value

        # maybe it's worth it to update the kerndata dict manually?
        if hold is False:
            self.makeKernUIPositionData()
            self.positionKernUIGlyphLayers()
        self.updateUIbuttonsQuicker(index, pair, value)

    @property
    def pairFlipped(self):
        flippedPair = [self.asGlyphName(
            self.pairCurrent[1]), self.asGlyphName(self.pairCurrent[0])]
        for openclosepair in openclosepairs.items():
            if flippedPair[0] == self.asGlyphName(openclosepair[0]):
                flippedPair[0] = self.asGlyphName(openclosepair[1])
            elif flippedPair[0] == self.asGlyphName(openclosepair[1]):
                flippedPair[0] = self.asGlyphName(openclosepair[0])
            if flippedPair[1] == self.asGlyphName(openclosepair[0]):
                flippedPair[1] = self.asGlyphName(openclosepair[1])
            elif flippedPair[1] == self.asGlyphName(openclosepair[1]):
                flippedPair[1] = self.asGlyphName(openclosepair[0])
        return flippedPair

    def reversePairSmart(self, pair):
        left = self.asGlyphName(pair[0])
        right = self.asGlyphName(pair[1])
        flippedPair = [right, left]
        for openclosepair in openclosepairs.items():
            if flippedPair[0] == self.asGlyphName(openclosepair[0]):
                flippedPair[0] = self.asGlyphName(openclosepair[1])
            elif flippedPair[0] == self.asGlyphName(openclosepair[1]):
                flippedPair[0] = self.asGlyphName(openclosepair[0])
            if flippedPair[1] == self.asGlyphName(openclosepair[0]):
                flippedPair[1] = self.asGlyphName(openclosepair[1])
            elif flippedPair[1] == self.asGlyphName(openclosepair[1]):
                flippedPair[1] = self.asGlyphName(openclosepair[0])
        return flippedPair

    def asGlyphName(self, character):
        if len(character) > 1:
            return character
        else:
            return GlyphName(ord(character)).getName()

    def flatButton(self, this):
        ns = this.getNSButton()
        ns.setBordered_(False)

    def colorText(self, this, color=None):
        ns = this.getNSButton()
        textcolor = NSColor.grayColor()
        if color == 'red':
            textcolor = red
        paragraphalignment = NSMutableParagraphStyle.alloc().init()
        paragraphalignment.setAlignment_(2)
        customFont = NSFont.menuBarFontOfSize_(10)
        attributes = {}
        attributes[NSFontAttributeName] = customFont
        attributes[NSForegroundColorAttributeName] = textcolor
        attributes[NSParagraphStyleAttributeName] = paragraphalignment
        attributedText = NSAttributedString.alloc(
        ).initWithString_attributes_(ns.title(), attributes)
        ns.setAttributedTitle_(attributedText)

    def flatEditText(self, this, align=None):
        ns = this.getNSTextField()
        ns.setBordered_(False)
        ns.setFocusRingType_(1)
        if align == 'center':
            ns.setAlignment_(NSTextAlignmentCenter)

    #
    #
    #
    def updateMerzLayers(self):
        print('COALESCE', 'updateMerzLayers')
        # - update lineview
        #     - get last notification
        #     - on font list shuffle
        #     - on pairlist selection change 
        #     - on flip sides
        #     - on currentpair change

    def updateMerzPositions(self):
        print('COALESCE', 'updateMerzPositions')
        # - update line preview positions 


class okButton(Button):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        super(okButton, self).__init__(*args, **kwargs)


class okNumberEditText(NumberEditText):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        super(okNumberEditText, self).__init__(*args, **kwargs)


# if f'{defaultKey}.updateMerzGlyphs' not in roboFontSubscriberEventRegistry:
#     registerSubscriberEvent(
#         subscriberEventName=f'{defaultKey}.updateMerzGlyphs',
#         methodName='updateMerzGlyphs',
#         lowLevelEventNames=[f'{defaultKey}.updateMerzGlyphs'],
#         dispatcher='roboFont',
#         delay=0.5,
#     )
#     registerSubscriberEvent(
#         subscriberEventName=f'{defaultKey}.updateMerzPositions',
#         methodName='updateMerzPositions',
#         lowLevelEventNames=[f'{defaultKey}.updateMerzPositions'],
#         dispatcher='roboFont',
#         delay=0.5,
#     )

if __name__ == '__main__':
    registerRoboFontSubscriber(KernKernKern)
