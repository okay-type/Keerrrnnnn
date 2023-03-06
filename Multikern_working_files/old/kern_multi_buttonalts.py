from AppKit import NSScreen
from AppKit import NSDragOperationMove
from AppKit import NSDragOperationCopy
from AppKit import NSFilenamesPboardType
from AppKit import NSColor
from AppKit import NSTextAlignmentRight, NSTextAlignmentCenter, NSTextAlignmentLeft
from AppKit import NSAttributedString, NSForegroundColorAttributeName, NSParagraphStyleAttributeName, NSMutableParagraphStyle, NSFont, NSFontAttributeName
from mojo.subscriber import Subscriber
from mojo.subscriber import registerRoboFontSubscriber
from mojo.subscriber import unregisterGlyphEditorSubscriber
from mojo.subscriber import registerSubscriberEvent
from mojo.subscriber import roboFontSubscriberEventRegistry
from vanilla import Window
from vanilla import Group
from vanilla import EditText
from vanilla import TextBox
from vanilla import List
from vanilla import CheckBoxListCell
from vanilla import Button
from vanilla import ProgressBar
from vanilla import VerticalLine, HorizontalLine
from merz import MerzView
from mojo.UI import NumberEditText
from mojo.UI import GetFile
from mojo.events import extractNSEvent
from mojo.extensions import setExtensionDefault, getExtensionDefault, registerExtensionDefaults
from glyphNameFormatter import GlyphName
from os import path as ospath
from random import random
from itertools import repeat

import time
def time_it(f):
    time_it.active = 0
    def tt(*args, **kwargs):
        time_it.active += 1
        t0 = time.time()
        tabs = '\t'*(time_it.active - 1)
        name = f.__name__
        print('{tabs}Executing <{name}>'.format(tabs=tabs, name=name))
        res = f(*args, **kwargs)
        print('{tabs}Function <{name}> execution time: {time:.3f} seconds'.format(
            tabs=tabs, name=name, time=time.time() - t0))
        time_it.active -= 1
        return res
    return tt

testpairlist = '#header\nA A\nA B\nB B\nA C\nA D\nparenleft H\n'
openclosepairs = { "‘": "’", "“": "”", "«": "»", "»": "«", "⸄": "⸅", "⸉": "⸊", "⸠": "⸡", "”": "”", "’": "’", "'": "'", '"': '"', "¡": "!", "¿": "?", "←": "→", "→": "←", "(": ")", "[": "]", "{": "}", "parenleft.sups": "parenright.sups", "parenleft.subs": "parenright.subs", "parenleft.uc": "parenright.uc", "bracketleft.uc": "bracketright.uc", "braceleft.uc": "braceright.uc", "bracketangleleft.uc": "bracketangleright.uc", "guillemetleft": "guillemetright", "guillemetleft.uc": "guillemetright.uc", "commaheavydoubleturnedornament": "commaheavydoubleornament", "parenleft.vert": "parenright.vert", "bracketleft.vert": "bracketright.vert", "braceleft.vert": "braceright.vert", "bracketangleleft.vert": "bracketangleright.vert", "guillemetleft.vert": "guillemetright.vert", "parenleft.uc.vert": "parenright.uc.vert", "bracketleft.uc.vert": "bracketright.uc.vert", "braceleft.uc.vert": "braceright.uc.vert", "bracketangleleft.uc.vert": "bracketangleright.uc.vert", "guillemetleft.uc.vert": "guillemetright.uc.vert", "less.vert": "greater.vert", "less.vert.uc": "greater.vert.uc", "<": ">", ">": "<", "less": "greater", "less.uc": "greater.uc", "༺": "༻", "༼": "༽", "᚛": "᚜", "⁅": "⁆", "⁽": "⁾", "₍": "₎", "⌈": "⌉", "⌊": "⌋", "〈": "〉", "❨": "❩", "❪": "❫", "❬": "❭", "❮": "❯", "❰": "❱", "❲": "❳", "❴": "❵", "⟅": "⟆", "⟦": "⟧", "⟨": "⟩", "⟪": "⟫", "⟬": "⟭", "⟮": "⟯", "⦃": "⦄", "⦅": "⦆", "⦇": "⦈", "⦉": "⦊", "⦋": "⦌", "⦍": "⦎", "⦏": "⦐", "⦑": "⦒", "⦓": "⦔", "⦕": "⦖", "⦗": "⦘", "⧘": "⧙", "⧚": "⧛", "⧼": "⧽", "⸢": "⸣", "⸤": "⸥", "⸦": "⸧", "⸨": "⸩", "〈": "〉", "《": "》", "「": "」", "『": "』", "【": "】", "〔": "〕", "〖": "〗", "〘": "〙", "〚": "〛", "〝": "〞", "⹂": "〟", "﴿": "﴾", "︗": "︘", "︵": "︶", "︷": "︸", "︹": "︺", "︻": "︼", "︽": "︾", "︿": "﹀", "﹁": "﹂", "﹃": "﹄", "﹇": "﹈", "﹙": "﹚", "﹛": "﹜", "﹝": "﹞", "（": "）", "［": "］", "｛": "｝", "｟": "｠", "｢": "｣", }
defaultKey = 'com.okay.multiKern'


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

Axis 1                  up/down         change font                
Axis 2                  left/right      +5 kerning      +10 kerning     apply to all ufos

'''


'''
TODO

updateUIbuttons
    Function <updateUIbuttons> execution time: 1.2XX seconds
    needs to be much faster

clicking a ui element should set that font/pair as the activeFont

edit AB text to set current pair
    should this update the pairlist selection?
        if not, can there be a pairlist find?

dynamic context strings
    put open/closed pairs on the correct side 
    upper
    lower
    smallcap
    suffix match
    fractions
    other triplets
    change context strings with button?

buttons
    magic sort fontlist
    reverse fontlist
    sort pairlist by glyphorder
    find in pairlist
    invert colors

controllable big font size
controllable small font size
controllable spacing

'''

class MultiKern(Subscriber):

    debug = False

    # control variables
    adjustSmall = 5
    adjustBig = 10

    # ui varaibles
    smallFontSize = 24
    bigFontSize = 72
    rowHeight = 103
    kernColorPos = (0, .7, .6, 1)
    kernColorNeg = (1, 0, 0, 1)

    # internal data
    listcount = 0
    addedUIbuttons = []
    noUIfonts = []
    kernUIData = None
    focusOn = [0, False]
    activeUFO = None

    def build(self):
        initialDefaults = {
            defaultKey+'.aliases': {},
            defaultKey+'.pairCurrent': ['O','k'],
        }
        registerExtensionDefaults(initialDefaults)
        self.pairAliases = getExtensionDefault(defaultKey+'.aliases')
        self.pairCurrent = getExtensionDefault(defaultKey+'.pairCurrent')
        self.pairCurrent = [self.pairCurrent[0], self.pairCurrent[1]]
        # self.pairFlipped = [self.pairCurrent[1], self.pairCurrent[0]]

        (screenX, screenY), (screenW, screenH) = NSScreen.mainScreen().visibleFrame()

        self.w = Window(
            (0, 0, screenW, screenH*.96),
            'MultiKern',
            minSize=None,
            maxSize=None,
            textured=False,
            fullScreenMode=None,
            titleVisible=False,
            fullSizeContentView=True,
        )
        self.w.getNSWindow().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))

        self.w.ui = Group((20, 0, 330, -0))

        self.w.kerningMerzView = MerzView(
            (350, 0, -300, -0),
            backgroundColor=(1, 1, 1, 1),
            delegate=self,
        )
        self.fontlist = []
        self.w.fontlist = List(
            (-300, 0, -0, screenH*.25),
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

        self.w.controls = Group((20, -44, 300, -0))
        self.w.controls.progress = ProgressBar(
            (0, 22, -0, 22),
            minValue=0,
            maxValue=1,
            sizeStyle='small',
            progressStyle='bar',
        )
        self.w.controls.load = Button((0, 0, 44, 22), 'Load', sizeStyle='mini', callback=self.loadPairlist)
        self.w.controls.save = Button((44, 0, 44, 22), 'Save', sizeStyle='mini', callback=self.saveFiles)
        self.w.controls.save.enable(False)

        self.pairlist = self.prepPairList()
        self.w.pairlist = List(
            (-300, screenH*.25, -0, -0),
            self.pairlist,
            columnDescriptions=[{'title': 'Left'}, {'title': 'Right'}],
            allowsSorting=True,
            selectionCallback=self.pairlistSelectionCallback,
        )
        self.w.controls.progress.set((self.w.pairlist.getSelection()[0]+1)/len(self.pairlist))
        self.w.pairlist.setSelection([0])

    def started(self):
        self.fontListAddOpen()
        self.w.open()
        self.buildKernUI()

    def destroy(self):
        for font in self.fontlist:
            if font['visibile'] == '👻':
                font['ufo'].close()
        setExtensionDefault(defaultKey+'.aliases', self.pairAliases)
        setExtensionDefault(defaultKey + '.pairCurrent', self.pairCurrent)

        # unregisterGlyphEditorSubscriber(self)

    def saveFiles(self, sender):
        for i, font in enumerate(self.fontlist):
            ufo = font['ufo']
            ufo.save()
        self.w.controls.save.enable(False)

    def loadPairlist(self, sender):
        # open pair list file
        savepair = self.pairCurrent
        pairlist = []
        with open(GetFile(message='Open a pairlist.txt file.'), encoding='utf-8') as userFile:
            lines = userFile.read()
            lines = lines.splitlines()
            for line in lines:
                pairlist.append(line)
        self.pairlist = self.prepPairList(pairlist)
        self.w.pairlist.set(self.pairlist)

        # find index of last saved current pair in pair list and set it
        self.pairCurrent = getExtensionDefault(defaultKey+'.pairCurrent')
        self.pairCurrent = [self.pairCurrent[0], self.pairCurrent[1]]

        try:
            i = self.pairlist.index({'Left': self.pairCurrent[0], 'Right': self.pairCurrent[1]})
        except:
            print(self.pairCurrent[0], self.pairCurrent[1], 'not in pairlist')
            i = 0
        self.w.pairlist.setSelection([i])

    def prepPairList(self, pairlist=None):
        cleanpairs = []
        if pairlist == None:
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
        pairindex = sender.getSelection()
        if pairindex == []:
            pairindex = [0]
        pairindex = pairindex[0]
        self.w.controls.progress.set((pairindex+1)/len(self.pairlist))
        self.pairCurrent = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
        # self.pairFlipped = [self.pairCurrent[1], self.pairCurrent[0]]
        # self.buildKernUI()
        if self.kernUIData is not None:
            self.makeKernUIPositionData()
            self.addKernUIGlyphLayers()
            self.positionKernUIGlyphLayers()
            self.updateUIbuttons()

    def fontListAddOpen(self):
        allFonts = FontsList(AllFonts())
        allFonts.sortBy('magic')
        for i, f in enumerate(allFonts):
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
        paths = [path for path in paths if ospath.splitext(path)[-1].lower() in supportedFontFileFormats or ospath.isdir(path)]
        if not paths:
            return False
        if not isProposal:
            rowIndex = dropInfo['rowIndex']
            items = sender.get()
            for path in paths:
                f = OpenFont(path, showInterface=False)
                self.noUIfonts.append(f)
                font = {}
                font['open'] = True
                font['fontname'] = f.info.familyName + ' ' + f.info.styleName
                font['ufo'] = f
                font['visibile'] = '👻'
                items.insert(rowIndex, font)
                rowIndex += 1
            sender.set(items)
        self.buildKernUI()
        return True

    def listEditCallback(self, sender):
        self.fontlist = self.w.fontlist.get()
        if len(self.fontlist) != self.listcount:
            self.listcount = len(self.fontlist)
            for noUIfont in self.noUIfonts:
                toclose = True
                for font in self.fontlist:
                    if font['ufo'] == noUIfont:
                        toclose = False
                if toclose == True:
                    print('closing', noUIfont)
                    noUIfont.close()
            # can this not refire a bunch when starting up?
            # print('listEditCallback self.buildKernUI')
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
            if index+1 < len(self.pairlist):
                self.w.pairlist.setSelection([self.w.pairlist.getSelection()[0]+1])
        if keycode == 43:  # comma
            index = self.w.pairlist.getSelection()[0]
            if index > 0:
                self.w.pairlist.setSelection([self.w.pairlist.getSelection()[0]-1])

        if keycode == 125:  # down arrow
            self.incrementFocusOn(1, 0)
        if keycode == 126:  # up arrow
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
            self.pairCurrent = self.reversePairSmart(self.pairCurrent)
            self.buildKernUI()

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
            if LshoulderDown > 0: # + option /
                # adjust pair in all fonts
                for i, font in enumerate(self.fontlist):
                    ufo = self.fontlist[i]['ufo']
                    kernValue = ufo.kerning.find(pair)
                    if kernValue == None:
                        kernValue = 0
                    self.updateKerning(i, pair, kernValue+(mod*adjustAmount))
            else:
                # adjust pair in active font
                ufo = self.fontlist[self.activeUFO]['ufo']
                kernValue = ufo.kerning.find(pair)
                if kernValue == None:
                    kernValue = 0
                self.updateKerning(self.activeUFO, pair, kernValue+(mod*adjustAmount))

    def incrementFocusOn(self, y, x):
        self.focusOn[0] += y
        if self.focusOn[0] > self.listcount-1:
            self.focusOn[0] = 0
        if self.focusOn[0] < 0:
            self.focusOn[0] = self.listcount-1
        if x == 1:
            self.focusOn[1] = not self.focusOn[1]
        self.activeFontIndicator()

    def activeFontIndicator(self):
        for i, font in enumerate(self.fontlist):
            name = 'buttons'+str(i)
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
        self.kernUIData['smallLayer'] = None
        self.kernUIData['smallLayerGlyphs'] = []
        self.kernUIData['smallLayerXadvance'] =[]
        self.kernUIData['smallLayerXkerns'] =[]
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

            smallLayer = container.appendBaseSublayer(
                position=(0, yInv-self.rowHeight*.66),
                size=(view.width(), self.rowHeight),
                # backgroundColor=(random(), random(), random(), .2),
            )
            smallLayer.addSublayerScaleTransformation(self.smallFontSize/1000, name='scale', center=(0, 0))
            self.kernUIData['smallLayer'] = smallLayer

            for i, font in enumerate(self.fontlist):
                fontlayer = container.appendBaseSublayer(
                    position=(0, yInv-(self.rowHeight*(i+1.66))),
                    size=(view.width(), self.rowHeight),
                    # backgroundColor=(random(), random(), random(), .2),
                )
                fontlayer.addSublayerScaleTransformation(self.bigFontSize/1000, name='scale', center=(0, 0))

                fontData = {}
                fontData['ufo'] = font['ufo']
                fontData['fontLayer'] = fontlayer
                fontData['glyphLayers'] = []
                fontData['glyphs'] = []
                fontData['xadvance'] = []
                fontData['kerns'] = []
                self.kernUIData['fontData'].append(fontData)

        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()

    def makeKernUIPositionData(self):
        if self.kernUIData is None:
            return
        # reset data
        self.kernUIData['smallLayerXadvance'] =[]
        self.kernUIData['smallLayerXkerns'] =[]

        # build new data
        smallx = 0
        for i, fontData in enumerate(self.kernUIData['fontData']):
            # reset data
            fontData['glyphs'] = []
            fontData['xadvance'] = []
            fontData['kerns'] = []

            ufo = fontData['ufo']
            ufoGlyphOrder = ufo.glyphOrder

            control = left = right = 'H'            
            text = [control, control, self.pairCurrent[0], self.pairCurrent[1], control, control, self.pairFlipped[0], self.pairFlipped[1], control, control]

            # build new data
            x = kernvalue = 0
            for n, glyphName in enumerate(text):
                if glyphName in ufoGlyphOrder:
                    fontData['glyphs'].append(glyphName)
                    fontData['xadvance'].append(x)
                    self.kernUIData['smallLayerXadvance'].append(smallx)
                    x += ufo[glyphName].width
                    smallx += ufo[glyphName].width
                    kernvalue = 0
                    if n < len(text)-1:
                        kernvalue = ufo.kerning.find((glyphName, text[n+1]))
                        if kernvalue == None:
                            kernvalue = 0
                        x += kernvalue
                        smallx += kernvalue
                    fontData['kerns'].append(kernvalue)
                    self.kernUIData['smallLayerXkerns'].append(kernvalue)

    def addKernUIGlyphLayers(self):
        if self.kernUIData is None:
            return
        # reset data
        self.kernUIData['smallLayerGlyphs'] = []

        # build new data
        smallLayer = self.kernUIData['smallLayer']
        smallLayer.clearSublayers()
        baseLayer = self.kernUIData['baseLayer']
        with baseLayer.sublayerGroup():
            for i, fontData in enumerate(self.kernUIData['fontData']):
                # reset data
                fontData['glyphLayers'] = []

                ufo = fontData['ufo']
                fontlayer = fontData['fontLayer']
                fontlayer.clearSublayers()
                text = fontData['glyphs']

                # build new data
                for n, glyphName in enumerate(text):
                    glyphLayer = fontlayer.appendPathSublayer(position=(0,0),)
                    glyphPath = ufo[glyphName].getRepresentation('merz.CGPath')
                    glyphLayer.setPath(glyphPath)
                    fontData['glyphLayers'].append(glyphLayer)

                    smallGlyphLayer = smallLayer.appendPathSublayer(position=(0,0),)
                    smallGlyphLayer.setPath(glyphPath)
                    self.kernUIData['smallLayerGlyphs'].append(smallGlyphLayer)

    def positionKernUIGlyphLayers(self):
        if self.kernUIData is None:
            return
        smallLayerXAdvance = 0
        for i, fontData in enumerate(self.kernUIData['fontData']):
            for n, glyphLayer in enumerate(fontData['glyphLayers']):
                x = fontData['xadvance'][n]
                kern = fontData['kerns'][n]
                glyphLayer.setPosition((x,0))
                glyphLayer.clearSublayers()
                if kern != 0:                
                    if kern < 0: c = self.kernColorNeg
                    if kern > 0: c = self.kernColorPos
                    glyphLayer.appendTextLineSublayer(
                        position=(fontData['xadvance'][n+1]-x, -150),
                        size=(10, 1),
                        pointSize=10,
                        text=str(kern),
                        fillColor=(*c,),
                        horizontalAlignment='center',
                        # backgroundColor=(1, random(), 0, 1),
                    )

        for i, smallGlyphLayer in enumerate(self.kernUIData['smallLayerGlyphs']):
            x = self.kernUIData['smallLayerXadvance'][i]
            kern = self.kernUIData['smallLayerXkerns'][i]
            smallGlyphLayer.setPosition((x,0))
            smallGlyphLayer.clearSublayers()
            if kern != 0:                
                if kern < 0: c = self.kernColorNeg
                if kern > 0: c = self.kernColorPos
                smallGlyphLayer.appendTextLineSublayer(
                    position=(self.kernUIData['smallLayerXadvance'][i+1]-x, -350),
                    size=(10, 1),
                    pointSize=8,
                    text=str(kern),
                    fillColor=(*c,),
                    horizontalAlignment='center',
                    # backgroundColor=(1, random(), 0, 1),
                )

    def buildUIbuttons(self):
        # remove old buttons
        for added in self.addedUIbuttons:
            if hasattr(self.w.ui, added):
                delattr(self.w.ui, added)

        self.addedUIbuttons = []
        width = 300
        ypos = self.rowHeight*1.12
        height = self.rowHeight

        # labels
        pair = Group((0, ypos-59, width, height))
        pair.left = EditText(
            (0, 0, width/4, -0),
            sizeStyle='small',
            placeholder='left',
            callback=self.pairOverride1,
        )
        pair.right = EditText(
            (width/4+10, 0, width/2, -0),
            sizeStyle='small',
            placeholder='right',
            callback=self.pairOverride2,
        )
        self.flatEditText(pair.right)
        self.flatEditText(pair.left)
        pair.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
        pair.left2 = EditText(
            (width/2, 0, width/4, -0),
            sizeStyle='small',
            placeholder='right',
            continuous=False,
            callback=self.aliasChanged1,
        )
        pair.right2 = EditText(
            (width/2+width/4+10, 0, -0, -0),
            sizeStyle='small',
            placeholder='left',
            continuous=False,
            callback=self.aliasChanged0,
        )
        self.flatEditText(pair.right2)
        self.flatEditText(pair.left2)
        pair.left2.getNSTextField().setAlignment_(NSTextAlignmentRight)
        setattr(self.w.ui, 'pair', pair)
        self.addedUIbuttons.append('pair')

        for i, font in enumerate(self.fontlist):
            y = 0
            x = 0
            h = 20
            b = 18

            ui = Group((0, ypos, width, height))

            # kern pair controls
            ui.L = Group((10, y, width/2-10, -0))
            ui.L.minus2 = okButton(
                (x, y, b, b),
                title='◀︎◀︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.L.minus = okButton(
                (x, y, b, b),
                title='◀︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.L.edit = okNumberEditText(
                (x+3, y+2, -x-3, 22),
                text='',
                allowEmpty=True,
                allowFloat=False,
                decimals=0,
                continuous=False,
                sizeStyle='small',
                i=i,
                pair=[None, None],
                callback=self.edit,
                )
            self.flatEditText(ui.L.edit, 'center')
            x = -x
            ui.L.plus = okButton(
                (x, y, b, b),
                title='▶︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.L.plus2 = okButton(
                (x, y, b, b),
                title='▶︎▶︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            self.flatButton(ui.L.minus2)
            self.flatButton(ui.L.minus)
            self.flatButton(ui.L.plus)
            self.flatButton(ui.L.plus2)

            ui.divider = VerticalLine((width/2+4, y, 2, 23))

            # flipped pair controls
            ui.R = Group((width/2+10, y, width/2-10, -0))
            ui.R.minus2 = okButton(
                (x, y, b, b),
                title='◀︎◀︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.R.minus = okButton(
                (x, y, b, b),
                title='◀︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.R.edit = okNumberEditText(
                (x+3, y+2, -x-3, 22),
                text='',
                allowEmpty=True,
                allowFloat=False,
                decimals=0,
                continuous=False,
                sizeStyle='small',
                i=i,
                pair=[None, None],
                callback=self.edit,
                )
            self.flatEditText(ui.R.edit, 'center')
            x = -x
            ui.R.plus = okButton(
                (x, y, b, b),
                title='▶︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            ui.R.plus2 = okButton(
                (x, y, b, b),
                title='▶︎▶︎',
                sizeStyle='small',
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.adjust,
                )
            x += b
            self.flatButton(ui.R.minus2)
            self.flatButton(ui.R.minus)
            self.flatButton(ui.R.plus)
            self.flatButton(ui.R.plus2)

            # alt one
            margin = 2
            y += h
            kbut = (width-18)*.25-b
            ui.alt1 = Group((10, y, -0, h))
            ui.alt1.left = TextBox(
                (0, 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt1.kern = okButton(
                (kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt1.right = TextBox(
                (kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt1.flipleft = TextBox(
                ((width/2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt1.flip = okButton(
                ((width/2)+kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt1.flipright = TextBox(
                ((width/2)+kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt1.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt1.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            self.flatButton(ui.alt1.kern)
            self.flatButton(ui.alt1.flip)

            # alt 2
            y += h-4
            ui.alt2 = Group((10, y, -0, h))
            ui.alt2.left = TextBox(
                (0, 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt2.kern = okButton(
                (kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt2.right = TextBox(
                (kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt2.flipleft = TextBox(
                ((width/2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt2.flip = okButton(
                ((width/2)+kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt2.flipright = TextBox(
                ((width/2)+kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt2.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt2.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            self.flatButton(ui.alt2.kern)
            self.flatButton(ui.alt2.flip)

            # alt 3
            y += h-4
            ui.alt3 = Group((10, y, -0, h))
            ui.alt3.left = TextBox(
                (0, 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt3.kern = okButton(
                (kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt3.right = TextBox(
                (kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt3.flipleft = TextBox(
                ((width/2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt3.flip = okButton(
                ((width/2)+kbut, 0, b*2, -0),
                sizeStyle='mini',
                title=None,
                i=i,
                pair=[None, None],
                adjust=0,
                callback=self.alt,
            )
            ui.alt3.flipright = TextBox(
                ((width/2)+kbut+(b*2), 5, kbut, -0),
                sizeStyle='mini',
                text='',
            )
            ui.alt3.left.getNSTextField().setAlignment_(NSTextAlignmentRight)
            ui.alt3.flipleft.getNSTextField().setAlignment_(NSTextAlignmentRight)
            self.flatButton(ui.alt3.kern)
            self.flatButton(ui.alt3.flip)

            ui.activeL = HorizontalLine((10, b+3, width/2-4, 1))
            ui.activeL.setBorderColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1))
            ui.activeR = HorizontalLine((width/2+5, b+3, 0, 1))
            ui.activeR.setBorderColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1))

            ui.activeL.show(True)
            ui.activeR.show(False)

            name = 'buttons'+str(i)
            setattr(self.w.ui, name, ui)
            self.addedUIbuttons.append(name)
            ypos += height

        self.updateUIbuttons()

    @time_it
    def updateUIbuttons(self):
        self.activeFontIndicator()

        pair = self.w.ui.pair
        pair.left.set(self.pairCurrent[0])
        pair.right.set(self.pairCurrent[1])
        pair.left2.set(self.pairFlipped[0])
        pair.right2.set(self.pairFlipped[1])

        for i, font in enumerate(self.fontlist):

            name = 'buttons'+str(i)
            ui = getattr(self.w.ui, name)
            ufo = font['ufo']

            kernValue = ufo.kerning.find(self.pairCurrent)
            flipValue = ufo.kerning.find(self.pairFlipped)
            if kernValue == None:
                kernValue = 0
            if flipValue == None:
                flipValue = 0

            ui.L.minus2.pair = self.pairCurrent
            ui.L.minus2.adjust = kernValue-self.adjustBig
            ui.L.minus.pair = self.pairCurrent
            ui.L.minus.adjust = kernValue-self.adjustSmall
            ui.L.edit.set(kernValue)
            ui.L.edit.pair = self.pairCurrent
            ui.L.plus.pair = self.pairCurrent
            ui.L.plus.adjust = kernValue+self.adjustSmall
            ui.L.plus2.pair = self.pairCurrent
            ui.L.plus2.adjust = kernValue+self.adjustBig

            ui.R.minus2.pair = self.pairFlipped
            ui.R.minus2.adjust = flipValue-self.adjustBig
            ui.R.minus.pair = self.pairFlipped
            ui.R.minus.adjust = flipValue-self.adjustSmall
            ui.R.edit.set(flipValue)
            ui.R.edit.pair = self.pairFlipped
            ui.R.plus.pair = self.pairFlipped
            ui.R.plus.adjust = flipValue+self.adjustSmall
            ui.R.plus2.pair = self.pairFlipped
            ui.R.plus2.adjust = flipValue+self.adjustBig

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
                altkern = ufo.kerning.find(pairsAB[0])
                altflip = ufo.kerning.find(pairsBA[0])
                if altkern == None: altkern = 0
                if altflip == None: altflip = 0

                ui.alt1.show(True)
                ui.alt1.left.set(pairsAB[0][0])
                ui.alt1.kern.setTitle(str(altkern))
                ui.alt1.kern.pair = self.pairCurrent
                ui.alt1.right.set(pairsAB[0][1])

                ui.alt1.flipleft.set(pairsBA[0][0])
                ui.alt1.flip.setTitle(str(altflip))
                ui.alt1.flip.pair = self.pairFlipped
                ui.alt1.flipright.set(pairsBA[0][1])

                if altkern == kernValue:
                    self.colorButton(ui.alt1.kern)
                else:
                    self.colorButton(ui.alt1.kern, color='red')

                if altflip == flipValue:
                    self.colorButton(ui.alt1.flip)
                else:
                    self.colorButton(ui.alt1.flip, color='red')

            if len(pairsAB) > 1:
                altkern = ufo.kerning.find(pairsAB[1])
                altflip = ufo.kerning.find(pairsBA[1])
                if altkern == None: altkern = 0
                if altflip == None: altflip = 0

                ui.alt2.show(True)
                ui.alt2.left.set(pairsAB[1][0])
                ui.alt2.kern.setTitle(str(altkern))
                ui.alt2.kern.pair = self.pairCurrent
                ui.alt2.right.set(pairsAB[1][1])

                ui.alt2.flipleft.set(pairsBA[1][0])
                ui.alt2.flip.setTitle(str(altflip))
                ui.alt2.flip.pair = self.pairFlipped
                ui.alt2.flipright.set(pairsBA[1][1])

                if altkern == kernValue:
                    self.colorButton(ui.alt2.kern)
                else:
                    self.colorButton(ui.alt2.kern, color='red')

                if altflip == flipValue:
                    self.colorButton(ui.alt2.flip)
                else:
                    self.colorButton(ui.alt2.flip, color='red')

            if len(pairsAB) > 2:
                altkern = ufo.kerning.find(pairsAB[2])
                altflip = ufo.kerning.find(pairsBA[2])
                if altkern == None: altkern = 0
                if altflip == None: altflip = 0

                ui.alt3.show(True)
                ui.alt3.left.set(pairsAB[2][0])
                ui.alt3.kern.setTitle(str(altkern))
                ui.alt3.kern.pair = self.pairCurrent
                ui.alt3.right.set(pairsAB[2][1])

                ui.alt3.flipleft.set(pairsBA[2][0])
                ui.alt3.flip.setTitle(str(altflip))
                ui.alt3.flip.pair = self.pairFlipped
                ui.alt3.flipright.set(pairsBA[2][1])

                if altkern == kernValue:
                    self.colorButton(ui.alt3.kern)
                else:
                    self.colorButton(ui.alt3.kern, color='red')

                if altflip == flipValue:
                    self.colorButton(ui.alt3.flip)
                else:
                    self.colorButton(ui.alt3.flip, color='red')

    def alt(self, sender):
        i = sender.i
        pair = sender.pair
        adjust = sender.adjust
        print(i, pair, adjust)
        self.updateKerning(i, pair, adjust)

    def adjust(self, sender):
        i = sender.i
        pair = sender.pair
        adjust = sender.adjust
        self.updateKerning(i, pair, adjust)

    def edit(self, sender):
        i = sender.i
        pair = sender.pair
        value = sender.get()
        self.updateKerning(i, pair, value)

    def pairOverride1(self, sender):
        self.pairCurrent[0] = sender.get()
        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()
        self.updateUIbuttons()

    def pairOverride2(self, sender):
        self.pairCurrent[1] = sender.get()
        self.makeKernUIPositionData()
        self.addKernUIGlyphLayers()
        self.positionKernUIGlyphLayers()
        self.updateUIbuttons()

    def aliasChanged0(self, sender):
        new = sender.get()
        sender.set(self.pairCurrent[0])
        self.aliasChanged(self.pairCurrent[0], new)

    def aliasChanged1(self, sender):
        new = sender.get()
        sender.set(self.pairCurrent[1])
        self.aliasChanged(self.pairCurrent[1], new)

    def aliasChanged(self, g, new):
        if new == '' or new == g:
            del self.pairAliases[g]
        else:
            self.pairAliases[g] = new
        setExtensionDefault(defaultKey+'.aliases', self.pairAliases)
        self.updateUIbuttons()

    def updateKerning(self, index, pair, value):
        self.w.controls.save.enable(True)

        left, right = pair
        f = self.fontlist[index]['ufo']

        matching = [s for s in f.groups.findGlyph(left) if 'public.kern1' in s]
        if len(matching) > 0:
            left = matching[0]
        matching = [s for s in f.groups.findGlyph(right) if 'public.kern2' in s]
        if len(matching) > 0:
            right = matching[0]

        if value == 0 or value == '' or value == 'None' or value == None:
            f.kerning[(left, right)] = 0
            f.kerning.remove((left, right))
        else:
            f.kerning[(left, right)] = value

        self.makeKernUIPositionData()
        self.positionKernUIGlyphLayers()
        self.updateUIbuttons()
    @property
    def pairFlipped(self):
        flippedPair = [self.asGlyphName(self.pairCurrent[1]), self.asGlyphName(self.pairCurrent[0])]
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

    def colorButton(self, this, color=None):
        ns = this.getNSButton()
        textcolor = NSColor.grayColor()
        if color == 'red':
            textcolor = NSColor.redColor()
        paragraphalignment = NSMutableParagraphStyle.alloc().init()
        paragraphalignment.setAlignment_(2)
        customFont = NSFont.menuBarFontOfSize_(10)
        attributes = {}
        attributes[NSFontAttributeName] = customFont
        attributes[NSForegroundColorAttributeName] = textcolor
        attributes[NSParagraphStyleAttributeName] = paragraphalignment
        attributedText = NSAttributedString.alloc().initWithString_attributes_(ns.title(), attributes)
        ns.setAttributedTitle_(attributedText)

    def flatEditText(self, this, align=None):
        ns = this.getNSTextField()
        ns.setBordered_(False)
        ns.setFocusRingType_(1)
        if align == 'center':
            ns.setAlignment_(NSTextAlignmentCenter)

class okButton(Button):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        self.pair = kwargs['pair']
        del kwargs['pair']
        self.adjust = kwargs['adjust']
        del kwargs['adjust']
        super(okButton, self).__init__(*args, **kwargs)

class okNumberEditText(NumberEditText):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        self.pair = kwargs['pair']
        del kwargs['pair']
        super(okNumberEditText, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    registerRoboFontSubscriber(MultiKern)



