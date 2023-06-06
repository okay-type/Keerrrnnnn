from mojo.subscriber import Subscriber, WindowController, registerRoboFontSubscriber, roboFontSubscriberEventRegistry, registerSubscriberEvent
from mojo.roboFont import AllFonts
from mojo.events import postEvent
from vanilla import Window, EditText, Button
from lib.UI.spaceCenter.glyphSequenceEditText import splitText
from merz import MerzView
# from pprint import pprint
from mojo.UI import OutputWindow
OutputWindow().clear()
#
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' %(method.__name__, (te - ts) * 1000))
        return result
    return timed

'''
to do

vertical position
xPos padding

'''


MerzLineViewKey = 'okay.MerzLineView'

class MerzLineView(Subscriber, WindowController):

    debug = True

    def build(self):
        # set up variables
        self.fontlist = AllFonts()
        self.bigFontSize = 50
        self.smallFontSize = 25
        self.lineHeight = 92
        self.control = 'H'
        self.kernColorNegative =(1, 0, 0, 1)
        self.kernColorPositive = (0, .7, .6, 1)
        self.labelKerning = True
        self.hold = False
        self.textCache = []
        self.changeCache = []

        # ui
        self.w = Window((0, 0, 900, 300), 'MerzLineView')
        self.w.refresh = Button((0, 0, 50, 22), '↔', callback=self.buttonCallback)
        self.w.edit = EditText((50, 0, -0, 22), 'HHAVHHH TextText HHHH', callback=self.editCallback)
        self.w.merzLineView = MerzView((0, 22, -0, -0), backgroundColor=(1, 1, 1, 1), delegate=self)

    def started(self):
        self.textCache = [splitText(self.w.edit.get(), self.fontlist[0].getCharacterMapping())]
        self.w.open()
        self.merzLineView_build_initial_layers()
        self.merzLineView_get_position_data(self.textCache[-1])
        self.merzLineView_add_glyph_layers()
        self.merzLineView_position_glyph_layers()

    def editCallback(self, sender):
        if len(self.fontlist) > 0:
            text = splitText(sender.get(), self.fontlist[0].getCharacterMapping())
            postEvent(f'{MerzLineViewKey}.merzLineView_hold')
            postEvent(f'{MerzLineViewKey}.merzLineView_editText', text=text)
        else:
            print('there needs to be an open font')

    def buttonCallback(self, sender):
        # change = (fontIndex, pair, newkern)
        change = (0, ('A', 'V'), 50)
        postEvent(f'{MerzLineViewKey}.merzLineView_hold')
        postEvent(f'{MerzLineViewKey}.merzLineView_positionText', change=change)

    def merzLineView_build_initial_layers(self):
        # set up merz stuff
        view = self.w.merzLineView
        container = view.getMerzContainer()
        container.clearSublayers()
        height = view.height()
        width = view.width()
        baseLayer = container.appendBaseSublayer(size=(width, height))

        # set up data
        self.merzLayerData = {}
        self.merzLayerData['baseLayer'] = baseLayer
        self.merzLayerData['fontData'] = []

        # add font layers and data
        with baseLayer.sublayerGroup():
            for i, ufo in enumerate(self.fontlist):

                # big text
                y = height-(self.lineHeight*(i+1))
                fontlayer = container.appendBaseSublayer(position=(0, y), size=(width, self.lineHeight))
                fontlayer.addSublayerScaleTransformation(self.bigFontSize/1000, name='scale', center=(0, 0))

                # small text
                fontlayersmall = container.appendBaseSublayer(position=(0, y), size=(width, self.lineHeight))
                fontlayersmall.addSublayerScaleTransformation(self.smallFontSize/1000, name='scale', center=(0, 0))
                fontlayersmall.addTranslationTransformation((width/2, 0), name='translateX')

                # add font stuff to data
                fontData = {}
                fontData['ufo'] = ufo
                fontData['fontLayer'] = fontlayer
                fontData['glyphLayers'] = []
                fontData['fontLayerSmall'] = fontlayersmall
                fontData['glyphLayersSmall'] = []
                fontData['glyphs'] = []
                fontData['kerns'] = {}
                self.merzLayerData['fontData'].append(fontData)

    def merzLineView_get_position_data(self, text):
        if text is None:
            return

        for i, fontData in enumerate(self.merzLayerData['fontData']):
            # reset data
            fontData['glyphs'] = []
            fontData['kerns'] = {}

            ufo = fontData['ufo']
            ufoGlyphOrder = ufo.glyphOrder

            # build new data
            for n, glyphName in enumerate(text):
                if glyphName in ufoGlyphOrder:

                    # get kern value against next glyph
                    if n < len(text)-1:
                        pair = (glyphName, text[n+1])
                        if tuple(pair) not in fontData['kerns']:
                            kernValue = ufo.kerning.find(pair) or 0
                            fontData['kerns'][tuple(pair)] = kernValue

                    fontData['glyphs'].append((glyphName, ufo[glyphName].width))

    def merzLineView_change_position_data(self, changeCache):
        for change in changeCache:
            fontIndex, pair, newkern = change
            self.merzLayerData['fontData'][fontIndex]['kerns'][tuple(pair)] = newkern

    def merzLineView_add_glyph_layers(self):
        baseLayer = self.merzLayerData['baseLayer']
        if self.merzLayerData is None or baseLayer is None:
            print('\t self.merzLayerData is None or baseLayer is None')
            return

        with baseLayer.sublayerGroup():
            for i, fontData in enumerate(self.merzLayerData['fontData']):
                # reset data
                fontData['glyphLayers'] = []
                fontData['glyphLayersSmall'] = []
                ufo = fontData['ufo']
                fontlayer = fontData['fontLayer']
                fontlayersmall = fontData['fontLayerSmall']

                # reset layers
                fontlayer.clearSublayers()
                fontlayersmall.clearSublayers()

                # build new layers and data
                for glyphName, x in fontData['glyphs']:
                    glyphPath = ufo[glyphName].getRepresentation('merz.CGPath')

                    glyphLayer = fontlayer.appendPathSublayer(position=(0, 0),)
                    glyphLayer.setPath(glyphPath)
                    fontData['glyphLayers'].append(glyphLayer)

                    glyphLayerSmall = fontlayersmall.appendPathSublayer(position=(0, 0),)
                    glyphLayerSmall.setPath(glyphPath)
                    fontData['glyphLayersSmall'].append(glyphLayerSmall)

    def merzLineView_position_glyph_layers(self):
        if self.merzLayerData is None:
            print('\t self.merzLayerData is None')
            return

        # big text
        xPos = 0
        for fontData in self.merzLayerData['fontData']:
            glyphLayerCount = len(fontData['glyphLayers'])
            x = lastKernX = 0
            for n, glyphLayer in enumerate(fontData['glyphLayers']):
                glyphLayer.clearSublayers()

                # if not first glyph, get kern value
                kernValue = 0
                if n > 0:
                    pair = (fontData['glyphs'][n-1][0], fontData['glyphs'][n][0])
                    kernValue = fontData['kerns'][tuple(pair)] or 0

                # position glyph
                glyphLayer.setPosition((x+kernValue, 0))

                if self.labelKerning is True and kernValue != 0:
                    if kernValue < 0:
                        kernColor = self.kernColorNegative
                    if kernValue > 0:
                        kernColor = self.kernColorPositive
                    if x+kernValue-500 < lastKernX:
                        y = -550
                    else:
                        y = -300
                        lastKernX = x+kernValue
                    glyphLayer.appendTextLineSublayer(
                        position=(0, y),
                        size=(10, 1),
                        pointSize=10,
                        text=str(kernValue),
                        fillColor=(*kernColor,),
                        horizontalAlignment='center',
                    )

                # update x and check if it is the farthest of all the fonts
                x += fontData['glyphs'][n][1]+kernValue
                if x > xPos:
                    xPos = x

        # small text
        for fontData in self.merzLayerData['fontData']:
            # set up layers
            fontLayerSmall = fontData['fontLayerSmall']
            fontLayerSmall.removeTransformation('translateX')

            # use the biggest xPosition from above
            x = xPos/(1/(self.bigFontSize/1000))
            fontLayerSmall.addTranslationTransformation((x, 0), name='translateX')

            # position glyphs
            for n, glyphLayersSmall in enumerate(fontData['glyphLayersSmall']):
                kernValue = 0
                if n > 0:
                    pair = (fontData['glyphs'][n-1][0], fontData['glyphs'][n][0])
                    kernValue = fontData['kerns'][tuple(pair)] or 0

                glyphLayersSmall.setPosition((x+kernValue, 0))
                x += fontData['glyphs'][n][1]+kernValue

    def merzLineView_hold(self, notification):
        self.hold = False
        postEvent(f'{MerzLineViewKey}.testDidIncrement', text=None)

    def merzLineView_editText(self, notification):
        for event in notification['lowLevelEvents']:
            text = event['text']
            if text is not None:
                self.textCache.append(text)
        if self.hold is False:
            self.merzLineView_get_position_data(self.textCache[-1])
            self.merzLineView_add_glyph_layers()
            self.merzLineView_position_glyph_layers()
            self.textCache = []

    def merzLineView_positionText(self, notification):
        for event in notification['lowLevelEvents']:
            change = event['change']
            if change is not None:
                self.changeCache.append(change)
        if self.hold is False:
            self.merzLineView_change_position_data(self.changeCache)
            self.merzLineView_position_glyph_layers()
            self.changeCache = []


if f'{MerzLineViewKey}.merzLineView_hold' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{MerzLineViewKey}.merzLineView_hold',
        methodName='merzLineView_hold',
        lowLevelEventNames=[f'{MerzLineViewKey}.merzLineView_hold'],
        dispatcher='roboFont',
        delay=0.125,
    )
if f'{MerzLineViewKey}.merzLineView_editText' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{MerzLineViewKey}.merzLineView_editText',
        methodName='merzLineView_editText',
        lowLevelEventNames=[f'{MerzLineViewKey}.merzLineView_editText'],
        dispatcher='roboFont',
        delay=0.125,
    )
if f'{MerzLineViewKey}.merzLineView_positionText' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{MerzLineViewKey}.merzLineView_positionText',
        methodName='merzLineView_positionText',
        lowLevelEventNames=[f'{MerzLineViewKey}.merzLineView_positionText'],
        dispatcher='roboFont',
        delay=0.125,
    )


if __name__ == '__main__':
    registerRoboFontSubscriber(MerzLineView)
