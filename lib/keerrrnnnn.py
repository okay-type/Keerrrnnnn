from things import data
from things import hacked_vanilla
from things import helpers
from things import string_builder
# from things import adjustments

# reload fresh imports for dev
from importlib import reload
reload(data)
reload(hacked_vanilla)
reload(helpers)
reload(string_builder)
# reload(adjustments)
from things import data
from things.hacked_vanilla import okButton, okNumberEditText, okEditText, okTextBox
from things.helpers import *
from things.string_builder import *
# from things.adjustments import *

from AppKit import NSScreen
from AppKit import NSEvent, NSShiftKeyMask, NSCommandKeyMask, NSAlternateKeyMask, NSControlKeyMask
from AppKit import NSDragOperationMove, NSDragOperationCopy, NSFilenamesPboardType
from AppKit import NSColor
from AppKit import NSTextAlignmentRight, NSTextAlignmentCenter, NSTextAlignmentLeft
from AppKit import NSAttributedString, NSForegroundColorAttributeName, NSParagraphStyleAttributeName, NSMutableParagraphStyle, NSFont, NSFontAttributeName
from mojo.subscriber import Subscriber, WindowController
from mojo.subscriber import registerRoboFontSubscriber, unregisterRoboFontSubscriber, roboFontSubscriberEventRegistry, registerSubscriberEvent
from vanilla import Window, Group, EditText, TextBox, Button, Slider, RadioGroup
from vanilla import ProgressBar, VerticalLine, HorizontalLine, Box
from vanilla import List, CheckBoxListCell
from vanilla import ColorWell
from merz import MerzView
from mojo.UI import NumberEditText
from mojo.UI import GetFile
from mojo.UI import PostBannerNotification
from mojo.UI import AskYesNoCancel
from mojo.UI import OpenSpaceCenter
from mojo.events import extractNSEvent
from mojo.events import postEvent
from mojo.extensions import setExtensionDefault, getExtensionDefault, registerExtensionDefaults
from glyphNameFormatter import GlyphName
from os import path as ospath
from random import random
from itertools import repeat

from mojo.roboFont import AllFonts
from mojo.events import postEvent
from vanilla import Window, EditText, Button
from lib.UI.spaceCenter.glyphSequenceEditText import splitText
from merz import MerzView

# from pprint import pprint
from mojo.UI import OutputWindow
OutputWindow().clear()


def d(*args):
    if keerrrnnnn.debug == True:
        output = ''
        for a in args:
            output += str(a) + ' '
        print('~', output)


class keerrrnnnn(Subscriber, WindowController):

    debug = True

    def build(self):
        self.load_preferences()
        self.build_setup()
        self.build_window()

    def started(self):
        self.w.bind('should close', self.window_should_close)
        self.w.open()
        if len(self.ufolist) > 0:
            self.cache_text = [string_builder(self.pair_current, self.pair_flipped, self.ufolist)]
            postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_fonts')
            postEvent(f'{data.extension_key}.merzLineView_change_fonts')
        set_first_responder(self.w.merzLineView.getNSView())

    def load_preferences(self):
        initialDefaults = {
            data.extension_key + '.reference_glyphs': {},
            data.extension_key + '.pair_current': ['O', 'K'],
        }
        registerExtensionDefaults(initialDefaults)
        self.reference_glyphs = getExtensionDefault(data.extension_key + '.reference_glyphs')
        self.pair_current = getExtensionDefault(data.extension_key + '.pair_current')
        self.pair_current = [self.pair_current[0], self.pair_current[1]]
        self.pair_flipped = [self.pair_current[1], self.pair_current[0]]

    def build_setup(self):
        self.adjust_S = 5
        self.adjust_M = 10
        self.adjust_L = 50

        self.hold = False

        self.ufolist = []
        self.fonts_ui = []
        self.fonts_no_ui = []
        for f in AllFonts():
            font = {}
            if f.info.familyName and f.info.styleName:
                font['fontname'] = f.info.familyName + ' ' + f.info.styleName
            else:
                font['fontname'] = 'No font name'
            font['ufo'] = f
            font['checkable'] = True
            if 'talic' in font['fontname']:
                font['checkable'] = False
            font['spacecenter'] = False
            font['overview'] = True
            self.ufolist.append(font)
            self.fonts_ui.append(font)

        self.listcount = len(self.ufolist)
        self.pairlist = []
        self.paircount = 0
        self.focus = [0, False]  # [y, x]
        self.flip = False  # swap if current pair is on left (default) or right (True)

        self.cache_text = []
        self.cache_positions = []

        self.opened_windows = {}

        self.kern_color_negative =(1, 0, 0, .5)
        self.kern_color_positive = (0, .7, .6, .5)
        self.label_kerning_on = True

        self.focus_indicator_on = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, .8)
        self.focus_indicator_off = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0)
        self.merz_focus_indicators = []
        self.merz_focus_indicator_color = (0.6, 0.7, 0.8, 0.7)

        self.size_big = 50
        self.size_small = 25
        self.lineheight = 1.8

        self.notify_steps = []
        c = 20
        for i in range(c):
            step = 1-(c-i)/c
            self.notify_steps.append(round(step, 2))

    def build_window(self):

        (screenX, screenY), (screenW, screenH) = NSScreen.mainScreen().visibleFrame()

        self.ui_metrics = {
            'row_height': self.size_big*self.lineheight,
            'column_width': 420,
            'line': 22,
            'gutter': 6,
            'column_8th': ((420-(22*2))-(6*(8-1)))/8,  # ((column_width-(line*2))-(gutter*(8-1)))/8
            'ypos': self.size_big*self.lineheight*.5,  # row_height*.5 - this is the intial value... +(i*row_height) for row
        }

        self.w = Window(
            (screenW*.125, 0, screenW*.75, screenH),
            # (0, 0, screenW*.75, screenH),
            'Keerrrnnnn',
            minSize=(self.ui_metrics['column_width']*3, screenH/3),
            maxSize=None,
            textured=False,
            fullScreenMode=None,
            titleVisible=False,
            fullSizeContentView=True,
        )

        self.w.merzLineView = MerzView(
            (self.ui_metrics['column_width'], 0, -self.ui_metrics['column_width']*2/3, -0),
            backgroundColor=(1, 1, 1, 1),
            delegate=self,
        )

        self.build_window_lists(screenW, screenH)
        self.build_window_controls_universal(screenW, screenH)
        self.build_window_controls_kerning()

        # self.build_window_string_controls()
        # self.build_window_size_controls()

        # add ui buttons # size big size small # line height

    def build_window_lists(self, screenW, screenH):
        # lists - left side
        column = self.ui_metrics['column_width']*2/3
        line = self.ui_metrics['line']

        self.w.lists = Group((-column, 0, -0, -line))

        # vertical divider
        divide = screenH*-.333

        # font list
        self.w.lists.fontlist = List(
            (0, divide+(line*1.5), -0, -line),
            items=self.ufolist,
            columnDescriptions=[
                dict(title='ufo', key='ufo', width=0),
                dict(title='🛸', key='fontname', editable=False),
                dict(title='*️⃣', key='checkable', cell=CheckBoxListCell(), width=22),
                dict(title='🔤', key='spacecenter', cell=CheckBoxListCell(), width=22),
                dict(title='🔡', key='overview', cell=CheckBoxListCell(), width=22),
            ],
            showColumnTitles=True,
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

        # add fontlist buttons
        self.w.lists.fontlist_sort = Button(
            (0, -line, column/3, line),
            'Sort',
            sizeStyle='mini',
            callback=self.fontlist_sort,
        )
        self.w.lists.fontlist_reverse = Button(
            (column/3, -line, column/3, line),
            'Reverse',
            sizeStyle='mini',
            callback=self.fontlist_reverse,
        )
        self.w.lists.fontlist_save = Button(
            (column/3*2, -line, column/3, line),
            'Save UFOs',
            sizeStyle='mini',
            callback=self.fontlist_save,
        )
        self.w.lists.fontlist_save.enable(False)




        self.pairlist = self.pairlist_parse()
        # pairlist
        w = (column-100)/2
        self.w.lists.pairlist = List(
            (0, 0, -0, divide-(line*6)),
            items=self.pairlist,
            columnDescriptions=[
                {'title': 'Left', 'width': w},
                {'title': 'Right', 'width': w},
                {'title': 'Seen', 'width': 20},
                {'title': 'i', 'width': 20},
                {'title': 'Flip L', 'width': 0},
                {'title': 'Flip R', 'width': 0},
            ],
            showColumnTitles=True,
            allowsSorting=True,
            enableDelete=False,
            allowsMultipleSelection=False,
            drawFocusRing=False,
            # editCallback=self.pairlist_selection_changed,
            selectionCallback=self.pairlist_selection_changed,
            otherApplicationDropSettings=dict(
                type=NSFilenamesPboardType,
                operation=NSDragOperationCopy,
                callback=self.pairlist_dropfile
            ),
        )
        self.w.lists.pairlist.setSelection([0])

        # progress / bottom buttons / save / load

        self.w.lists.progress = ProgressBar(
            (6, divide-(line*6), -6, line),
            minValue=0,
            maxValue=1,
            sizeStyle='small',
            progressStyle='bar',
        )
        self.w.lists.percent = TextBox(
            (2, divide-(line*5.05), (column/2), line),
            '50.5%',
            sizeStyle='mini',
        )
        self.w.lists.load = Button(
            (column/3*2-6, divide-(line*5.25), column/3, line),
            'Load Pairlist',
            sizeStyle='mini',
            callback=self.pairlist_load,
        )
        pairindex = self.w.lists.pairlist.getSelection()
        if pairindex == []:
            pairindex = [0]
        pairindex = pairindex[0]
        progress = (pairindex + 1) / self.paircount
        self.w.lists.progress.set(progress)
        self.w.lists.percent.set(str(int(progress*100))+'%')


        self.w.lists.progress_line = HorizontalLine((2, divide-(line*4.55), -2, line))


        # which font is active radio group
        self.w.lists.whichfonts = Group((line, divide-(line*3.5), column/3-line+15, line*4))
        self.w.lists.whichfonts.radioGroup = RadioGroup(
            (0, 0, -0, -0),
            [
                'All',
                'Selected ⌘',
                'Unselected ⌘⌥',
                'Checked ⌃',
                'Unchecked ⌃⌥',
            ],
            isVertical=True,
            sizeStyle='mini',
            callback=None,
        )
        self.w.lists.whichfonts.radioGroup.set(0)

        self.w.lists.whichfonts_line = VerticalLine((column/3+15, divide-(line*3.5), line, line*4))

        # metric adjust shortcuts
        w = column/3*2-(line*2)
        metricnudge = self.w.lists.metricnudge = Group((column/3+line+15, divide-(line*3.5)-15, w, line*4))
        metricnudge.metric_nudge_glyph = okEditText(
            (0, 15, -0, line),
            'Nudge Glyph Merics',
            align='left',
            sizeStyle='mini',
        )
        metricnudge.metric_nudge_pL = Button(
            (0, line+10, w/2, line),
            '+ Right',
            sizeStyle='mini',
            callback=self.metric_nudge_pL,
        )
        metricnudge.metric_nudge_nL = Button(
            (0, line+10, w/2, line*2.5),
            '- Right',
            sizeStyle='mini',
            callback=self.metric_nudge_nL,
        )
        metricnudge.metric_nudge_pR = Button(
            (w/2, line+10, w/2, line),
            '+ Left',
            sizeStyle='mini',
            callback=self.metric_nudge_pR,
        )
        metricnudge.metric_nudge_nR = Button(
            (w/2, line+10, w/2, line*2.5),
            '- Left',
            sizeStyle='mini',
            callback=self.metric_nudge_nR,
        )

    def build_window_size_controls(self):
        # ui for font size and spacing
        left = self.ui_metrics['column_width']
        right = -self.ui_metrics['column_width']*2/3
        line = self.ui_metrics['line']

        self.w.sizes = Group((left, -line, right, -0))

        w_slider = left/2
        w_label = left/6
        x = w_label
        self.w.sizes.slider_big = Slider(
            (x, 0, w_slider-line/2, line),
            minValue=14,
            maxValue=244,
            value=self.size_big,
            tickMarkCount=False,
            stopOnTickMarks=True,
            continuous=True,
            sizeStyle='mini',
            # callback=self.controlValuesSlider,
        )
        x += w_slider
        self.w.sizes.value_big = NumberEditText(
            (x, 0, w_label-line, line),
            int(self.size_big),
            continuous=False,
            allowFloat=False,
            sizeStyle='mini',
            # callback=self.controlValuesText,
        )
        x += w_label
        self.w.sizes.slider_small = Slider(
            (x, 0, w_slider-line/2, line),
            minValue=14,
            maxValue=72,
            value=self.size_small,
            tickMarkCount=False,
            stopOnTickMarks=True,
            continuous=True,
            sizeStyle='mini',
            # callback=self.controlValuesSlider,
        )
        x += w_slider
        self.w.sizes.value_small = NumberEditText(
            (x, 0, w_label-line, line),
            int(self.size_small),
            continuous=False,
            allowFloat=False,
            sizeStyle='mini',
            # callback=self.controlValuesText,
        )
        x += w_label
        self.w.sizes.slider_line = Slider(
            (x, 0, w_slider-line/2, line),
            minValue=24,
            maxValue=300,
            value=self.lineheight,
            tickMarkCount=False,
            stopOnTickMarks=True,
            continuous=True,
            sizeStyle='mini',
            # callback=self.controlValuesSlider,
        )
        x += w_slider
        self.w.sizes.value_line = NumberEditText(
            (x, 0, w_label-line, line),
            int(self.lineheight),
            continuous=False,
            allowFloat=False,
            sizeStyle='mini',
            # callback=self.controlValuesText,
        )
        x += w_label

    def build_window_string_controls(self):
        left = self.ui_metrics['column_width']
        right = -self.ui_metrics['column_width']*2/3
        line = self.ui_metrics['line']
        width = 100

        self.w.string_controls = Group((left, -line*2, right, -0))

        # edit text for  control strings
        before = 'before'
        between = 'between'
        after = 'after'
        self.w.string_controls.set_ends = EditText((10+width*0, line*0, width, 20), before, True, callback=None)
        self.w.string_controls.set_between = EditText((10+width*1, line*0, width, 20), between, True, callback=None)
        self.w.string_controls.set_reference = EditText((10+width*2, line*0, width, 20), after, True, callback=None)

        # individual show toggles
        self.w.string_controls.show_ends = CheckBox((10+width*0, line*1, width, 20), 'Ends', True, callback=None)
        self.w.string_controls.show_between = CheckBox((10+width*1, line*1, width, 20), 'Between', True, callback=None)
        self.w.string_controls.show_reference = CheckBox((10+width*2, line*1, width, 20), 'Reference', True, callback=None)

        # # PopUpButton for view mode
        # view_modes = [
        #     'standard',         # HHHH AV HHHH VA HHHH
        #     'no between',       # HHHH AVA HHHH or HHHH AVWA HHHH
        #     'no ends',          # AV HHHH VA
        #     'with referneces',  # HH ÄÖ HH AO HH ÄO HH AÖ HH
        #     'repeater',         # HHH AVAVAVA HHH
        # ]
        # self.w.string_controls.popUpButton = PopUpButton((10, 10, -10, 20), view_modes, callback=None)
        # self.w.string_controls.set(0)

    def build_window_controls_universal(self, screenW, screenH):
        # universal controls - right side
        column = self.ui_metrics['column_width']
        line = self.ui_metrics['line']
        gutter = self.ui_metrics['gutter']
        column_8th = self.ui_metrics['column_8th']
        width = (column-(line*2))

        self.w.controls = Group((line, line*1.5, width, -line))

        # pair labels
        w = c(column_8th, gutter, 2)-gutter
        x = 0
        y = -line*6.25
        pair = self.w.controls.pairs = Group((0, y, -0, line))
        pair.left = okEditText(
            (0, 0, w, 16),
            self.pair_current[0],
            sizeStyle='mini',
            placeholder='left',
            align='right',
            continuous=False,
            callback=self.pair_override_left,
        )
        x += w + gutter
        pair.right = okEditText(
            (x, 0, w, 16),
            self.pair_current[1],
            sizeStyle='mini',
            placeholder='right',
            align='left',
            continuous=False,
            callback=self.pair_override_right,
        )
        x += w + gutter
        pair.flipped_left = okEditText(
            (x, 0, w, 16),
            self.pair_flipped[0],
            sizeStyle='mini',
            align='right',
            continuous=False,
            callback=self.pair_flip_override_left,
        )
        x += w + gutter
        pair.flipped_right = okEditText(
            (x, 0, w, 16),
            self.pair_flipped[1],
            sizeStyle='mini',
            align='left',
            continuous=False,
            callback=self.pair_flip_override_right,
        )
        pair.L_line = HorizontalLine((gutter, line-2, c(column_8th, gutter, 4)-(gutter*3), 1))
        pair.R_line = HorizontalLine((c(column_8th, gutter, 4)+gutter, line-2, -gutter, 1))


        # univeral adjustments / arrow buttons and edittext

        x = y = 0
        w = c(column_8th, gutter, 4)-gutter-(line*2)
        universal = self.w.controls.universal = Group((0, -line*4.25, -0, line*4.25))
        universal.L_minus = okButton(
            (x, y, line, line),
            title='◀︎',
            i='AllFonts',
            callback=self.adjust_pair_minus,
        )
        x += line
        universal.L_edit = okNumberEditText(
            (x, y+3, w, 19),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i='AllFonts',
            align='center',
            callback=self.edit_pair,
        )
        universal.L_edit.setPlaceholder('?')
        x += w
        universal.L_plus = okButton(
            (x, y, line, line),
            title='▶︎',
            i='AllFonts',
            callback=self.adjust_pair_plus,
        )
        x += line
        x += gutter
        universal.R_minus = okButton(
            (x, y, line, line),
            title='◀︎',
            i='AllFonts',
            callback=self.adjust_flip_minus,
        )
        x += line
        universal.R_edit = okNumberEditText(
            (x, y+3, w, 19),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i='AllFonts',
            align='center',
            callback=self.edit_flip,
        )
        universal.R_edit.setPlaceholder('?')
        x += w
        universal.R_plus = okButton(
            (x, y, line, line),
            title='▶︎',
            i='AllFonts',
            callback=self.adjust_flip_plus,
        )

        # univeral adjustments / match

        y += line
        box_width = line*1.5
        label_width = c(column_8th, gutter, 2)-(gutter/2)-(box_width/2)

        universal.reference_z = Group((0, y, -0, line))
        universal.reference_z.line = HorizontalLine((gutter, 0, c(column_8th, gutter, 4)-(gutter*3), 1))
        universal.reference_z.zero = okButton(
            (label_width, 0, box_width, 12),
            '0',
            i='AllFonts',
            callback=self.universal_reference_zero_pair_current,
            sizeStyle='mini')
        universal.reference_z.line2 = HorizontalLine((c(column_8th, gutter, 4)+gutter, 0, -gutter, 1))
        universal.reference_z.flip_zero = okButton(
            (box_width + label_width*3 + gutter, 0, box_width, 12),
            '0',
            i='AllFonts',
            callback=self.universal_reference_zero_pair_flipped,
            sizeStyle='mini')
        y += line*.8

        universal.reference_0L = Group((0, y, c(column_8th, gutter, 4)-gutter, line))
        universal.reference_0L.line = HorizontalLine((gutter, 0, -gutter, 1))
        x = 0
        universal.reference_0L.left = okEditText(
            (x, 0, label_width, 16),
            '',
            align='right',
            continuous=False,
            callback=self.universal_reference_set_pair,
            sizeStyle='mini',
        )
        universal.reference_0L.left.setPlaceholder('?')
        x += label_width
        universal.reference_0L.kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_current,
            sizeStyle='mini')
        x += box_width
        universal.reference_0L.right = okEditText(
            (x, 0, label_width, 16),
            '',
            align='left',
            continuous=False,
            callback=self.universal_reference_set_pair,
            sizeStyle='mini',
        )
        universal.reference_0L.right.setPlaceholder('?')
        x += label_width + gutter

        universal.reference_0R = Group((x, y, -0, line))
        universal.reference_0R.line = HorizontalLine((gutter, 0, -gutter, 1))
        x = 0
        universal.reference_0R.flip_left = okEditText(
            (x, 0, label_width, 16),
            '',
            align='right',
            continuous=False,
            callback=self.universal_reference_set_flip,
            sizeStyle='mini',
        )
        universal.reference_0R.flip_left.setPlaceholder('?')
        x += label_width
        universal.reference_0R.flip_kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_flipped,
            sizeStyle='mini')
        x += box_width
        universal.reference_0R.flip_right = okEditText(
            (x, 0, label_width, 16),
            '',
            align='left',
            continuous=False,
            callback=self.universal_reference_set_flip,
            sizeStyle='mini',
        )
        universal.reference_0R.flip_right.setPlaceholder('?')

        y += line*.8
        universal.reference_1L = Group((0, y, -0, line))
        x = 0
        universal.reference_1L.left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        universal.reference_1L.kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_current,
            sizeStyle='mini')
        x += box_width
        universal.reference_1L.right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')
        x += label_width + gutter

        universal.reference_1R = Group((x, y, -0, line))
        x = 0
        universal.reference_1R.flip_left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        universal.reference_1R.flip_kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_flipped,
            sizeStyle='mini')
        x += box_width
        universal.reference_1R.flip_right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')

        y += line*.8
        universal.reference_2L = Group((0, y, -0, line))
        x = 0
        universal.reference_2L.left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        universal.reference_2L.kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_current,
            sizeStyle='mini')
        x += box_width
        universal.reference_2L.right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')
        x += label_width + gutter

        universal.reference_2R = Group((x, y, -0, line))
        x = 0
        universal.reference_2R.flip_left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        universal.reference_2R.flip_kern = okButton(
            (x, 0, box_width, 12),
            '▲',
            i='AllFonts',
            callback=self.universal_reference_copy_pair_flipped,
            sizeStyle='mini')
        x += box_width
        universal.reference_2R.flip_right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')

        gray = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, .15)
        universal.reference_1L.left.getNSTextField().setTextColor_(gray)
        universal.reference_2L.right.getNSTextField().setTextColor_(gray)
        universal.reference_1R.flip_right.getNSTextField().setTextColor_(gray)
        universal.reference_2R.flip_left.getNSTextField().setTextColor_(gray)
        universal.reference_1L.show(False)
        universal.reference_2L.show(False)
        universal.reference_1R.show(False)
        universal.reference_2R.show(False)

    def build_window_controls_kerning(self):
        # kerning controls for each ufo
        column = self.ui_metrics['column_width']
        line = self.ui_metrics['line']
        gutter = self.ui_metrics['gutter']
        column_8th = self.ui_metrics['column_8th']
        row_height = self.ui_metrics['row_height']

        # fontlist elements

        # add seen inidicator
        self.seen_on = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, .06)
        self.seen_off = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0)
        seen = self.w.controls.seen = Group((0, 0, -0, -0))
        mid = c(column_8th, gutter, 4)
        seen.activeL = HorizontalLine((0, 0, mid-gutter, -0))
        seen.activeL.setFillColor(self.seen_off)
        seen.activeL.setBorderWidth(0)
        seen.activeR = HorizontalLine((mid, 0, mid-gutter, -0))
        seen.activeR.setFillColor(self.seen_off)
        seen.activeR.setBorderWidth(0)

        for n in range(len(self.ufolist)):
            self.build_window_controls_kerning_one_ufo(n)

    def build_window_controls_kerning_one_ufo(self, i):
        line = self.ui_metrics['line']
        gutter = self.ui_metrics['gutter']
        column_8th = self.ui_metrics['column_8th']
        row_height = self.ui_metrics['row_height']
        ypos = self.ui_metrics['ypos'] + (row_height * i)

        # add focus inidicator
        inidicator = Group((0, ypos-gutter*.4, -0, line*4))
        mid = c(column_8th, gutter, 4)
        inidicator.activeL = HorizontalLine((0, 0, mid-gutter, -gutter))
        inidicator.activeL.setFillColor(self.focus_indicator_off)
        inidicator.activeL.setBorderWidth(0)
        inidicator.activeR = HorizontalLine((mid, 0, mid-gutter, -gutter))
        inidicator.activeR.setFillColor(self.focus_indicator_off)
        inidicator.activeR.setBorderWidth(0)

        if i == self.focus[0] and self.focus[1] is False:
            inidicator.activeL.setFillColor(self.focus_indicator_on)
        elif i == self.focus[0] and self.focus[1] is True:
            inidicator.activeL.setFillColor(self.focus_indicator_on)

        name = 'indicator' + str(i)
        setattr(self.w.controls, name, inidicator)

        # add controls

        ui = Group((0, ypos, -0, line*4))

        # arrow / number edit
        x = y = 0
        w = c(column_8th, gutter, 4)-gutter-(line*2)
        ui.L_minus = okButton(
            (x, y, line, line),
            title='◀︎',
            i=i,
            callback=self.adjust_pair_minus,
        )
        x += line
        ui.L_edit = okNumberEditText(
            (x, y+3, w, 19),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i=i,
            align='center',
            callback=self.edit_pair,
        )
        ui.L_edit.setPlaceholder('?')
        x += w
        ui.L_plus = okButton(
            (x, y, line, line),
            title='▶︎',
            i=i,
            callback=self.adjust_pair_plus,
        )
        x += line
        x += gutter
        ui.R_minus = okButton(
            (x, y, line, line),
            title='◀︎',
            i=i,
            callback=self.adjust_flip_minus,
        )
        x += line
        ui.R_edit = okNumberEditText(
            (x, y+3, w, 19),
            text='',
            allowEmpty=True,
            allowFloat=False,
            decimals=0,
            continuous=False,
            sizeStyle='small',
            i=i,
            align='center',
            callback=self.edit_pair,
        )
        ui.R_edit.setPlaceholder('?')
        x += w
        ui.R_plus = okButton(
            (x, y, line, line),
            title='▶︎',
            i=i,
            callback=self.adjust_flip_plus,
        )

        # reference pairs

        y += line
        box_width = line*1.5
        label_width = c(column_8th, gutter, 2)-(gutter/2)-(box_width/2)

        ui.reference_0L = Group((0, y, c(column_8th, gutter, 4)-gutter, line))
        ui.reference_0L.line = HorizontalLine((gutter, 0, -gutter, 1))
        x = 0
        ui.reference_0L.left = okTextBox((x, 2, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_0L.kern = TextBox((x, 2, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_0L.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_0L.right = okTextBox((x, 2, label_width, 12), 'right', align='left', sizeStyle='mini')
        x += label_width + gutter

        ui.reference_0R = Group((x, y, -0, line))
        ui.reference_0R.line = HorizontalLine((gutter, 0, -gutter, 1))
        x = 0
        ui.reference_0R.flip_left = okTextBox((x, 2, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_0R.flip_kern = TextBox((x, 2, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_0R.flip_kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_0R.flip_right = okTextBox((x, 2, label_width, 12), 'right', align='left', sizeStyle='mini')

        y += line*.8+2
        ui.reference_1L = Group((0, y, -0, line))
        x = 0
        ui.reference_1L.left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_1L.kern = TextBox((x, 0, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_1L.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_1L.right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')
        x += label_width + gutter

        ui.reference_1R = Group((x, y, -0, line))
        x = 0
        ui.reference_1R.flip_left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_1R.flip_kern = TextBox((x, 0, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_1R.flip_kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_1R.flip_right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')

        y += line*.8
        ui.reference_2L = Group((0, y, -0, line))
        x = 0
        ui.reference_2L.left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_2L.kern = TextBox((x, 0, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_2L.kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_2L.right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')
        x += label_width + gutter

        ui.reference_2R = Group((x, y, -0, line))
        x = 0
        ui.reference_2R.flip_left = okTextBox((x, 0, label_width, 12), 'left', align='right', sizeStyle='mini')
        x += label_width
        ui.reference_2R.flip_kern = TextBox((x, 0, box_width, 12), '-100', sizeStyle='mini')
        ui.reference_2R.flip_kern.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        x += box_width
        ui.reference_2R.flip_right = okTextBox((x, 0, label_width, 12), 'right', align='left', sizeStyle='mini')

        gray = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, .15)
        ui.reference_1L.left.getNSTextField().setTextColor_(gray)
        ui.reference_2L.right.getNSTextField().setTextColor_(gray)
        ui.reference_1R.flip_right.getNSTextField().setTextColor_(gray)
        ui.reference_2R.flip_left.getNSTextField().setTextColor_(gray)

        name = 'buttons' + str(i)
        setattr(self.w.controls, name, ui)



    # self.w.lists.fontlist callbacks

    def fontlist_edit(self, sender):
        ufolist_new = sender.get()

        updatedufo_dict = []
        if ufolist_new != self.ufolist:
            for ufoitem in ufolist_new:
                updatedufo = {}
                updatedufo['ufo'] = ufoitem['ufo']
                updatedufo['checkable'] = ufoitem['checkable']
                updatedufo['fontname'] = ufoitem['fontname']
                updatedufo['spacecenter'] = ufoitem['spacecenter']
                updatedufo['overview'] = ufoitem['overview']
                updatedufo_dict.append(updatedufo)

        if len(ufolist_new) != len(self.ufolist):
            for font_no_ui in self.fonts_no_ui:
                if not any(item['ufo'] == font_no_ui for item in ufolist_new):
                    print('Closing', font_no_ui.info.familyName + ' ' + font_no_ui.info.styleName)
                    self.fonts_no_ui.remove(font_no_ui)
                    font_no_ui.close()

        if len(ufolist_new) == len(self.ufolist) and ufolist_new != self.ufolist:
            for i, ufoitem in enumerate(ufolist_new):
                ufo = ufoitem['ufo']

                if ufoitem['spacecenter'] != self.ufolist[i]['spacecenter']:
                    if ufoitem['spacecenter'] is True:
                        self.fontlist_open_ufo_spacecenter(ufo, i)
                    if ufoitem['spacecenter'] is False:
                        self.fontlist_close_ufo_spacecenter(ufo, i)

                if ufoitem['overview'] != self.ufolist[i]['overview']:
                    if ufoitem['overview'] is True:
                        self.fontlist_open_ufo_ui(ufo)
                    if ufoitem['overview'] is False:
                        self.fontlist_close_ufo_ui(ufo)

        if updatedufo_dict != []:
            self.ufolist = updatedufo_dict

        if self.hold is False:
            if self.listcount != len(self.ufolist):
                self.listcount = len(self.ufolist)
            postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_fonts')
            postEvent(f'{data.extension_key}.merzLineView_change_fonts')

    def fontlist_drag(self, sender, indexes):
        return indexes

    def fontlist_drop(self, sender, dropInfo):
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

    def fontlist_add_noUI_ufo(self, sender, dropInfo):
        supportedFontFileFormats = ['ufo', 'ttf', 'otf', 'woff', 'woff2']
        isProposal = dropInfo['isProposal']
        paths = dropInfo['data']
        paths = [path for path in paths if path not in sender.get()]
        paths = [path for path in paths if ospath.splitext(path)[-1].lower() in supportedFontFileFormats or ospath.isdir(path)]
        if not paths:
            return False
        if not isProposal:
            rowIndex = dropInfo['rowIndex']
            items = sender.get()
            for i, path in enumerate(paths):
                self.hold = True
                skip = False
                for ufo in self.fonts_no_ui:
                    if path == ufo.path:
                        skip = True
                if skip is False:
                    f = OpenFont(path, showInterface=False)
                    font = {}
                    font['fontname'] = f.info.familyName + ' ' + f.info.styleName
                    font['ufo'] = f
                    font['checkable'] = True
                    if 'talic' in font['fontname']:
                        font['checkable'] = False
                    font['spacecenter'] = False
                    font['overview'] = False
                    items.insert(rowIndex, font)
                    rowIndex += 1
                    self.fonts_no_ui.append(f)
                if i >= len(paths)-1:
                    self.hold = False
            sender.set(items)
        return True

    def fontlist_sort(self, sender):
        selection = self.w.lists.fontlist.getSelection()
        if len(selection) < 2:
            tempufos = []
            for f in self.ufolist:
                ufo = f['ufo']
                tempufos.append(ufo)
                if ufo.info.openTypeOS2WidthClass is None:
                    print('FYI:', ufo.info.familyName + ' ' + ufo.info.styleName, 'openType OS2 Width Class is None')
                if ufo.info.openTypeOS2WeightClass is None:
                    print('FYI:', ufo.info.familyName + ' ' + ufo.info.styleName, 'openType OS2 Weight Class is None')
            tempufos = FontsList(tempufos)
            tempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isRoman',))
            fonts = sorted(self.ufolist, key=lambda x: tempufos.index(x['ufo']))
            # if resort, put italics first and reverse to ... essentially reverses the weight order
            if fonts == self.ufolist:
                tempufos.sortBy(('familyName', 'widthValue', 'weightValue', 'isItalic',))
                tempufos = list(reversed(tempufos))
                fonts = sorted(self.ufolist, key=lambda x: tempufos.index(x['ufo']))
            if fonts != self.ufolist:
                self.ufolist = fonts
                self.w.lists.fontlist.set(self.ufolist)
        else:
            tempufos = []
            otherufos = []
            for i, f in enumerate(self.ufolist):
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
            fonts = sorted(self.ufolist, key=lambda x: assembledufos.index(x['ufo']))
            if fonts != self.ufolist:
                self.ufolist = fonts
                self.w.lists.fontlist.set(self.ufolist)

    def fontlist_reverse(self, sender):
        self.ufolist = list(reversed(self.ufolist))
        self.w.lists.fontlist.set(self.ufolist)

    def fontlist_save(self, sender=None):
        for font in self.fonts_ui:
            font.save()
            print('saved', font.path)
        for font in self.fonts_no_ui:
            font.save()
            print('saved', font.path)
        self.w.lists.fontlist_save.enable(False)
        pairindex = self.w.lists.pairlist.getSelection()
        if pairindex == []:
            pairindex = [0]
        pairindex = pairindex[0]
        self.report_progress(pairindex)

    def fontlist_open_ufo_ui(self, ufo):
        self.fonts_ui.append(ufo)
        if ufo in self.fonts_no_ui:
            self.fonts_no_ui.remove(ufo)
        ufo.openInterface()
        w = ufo.document().getMainWindow()
        w.bind('should close', self.ui_window_should_close)

    def fontlist_close_ufo_ui(self, ufo):
        self.fonts_no_ui.append(ufo)
        if ufo in self.fonts_ui:
            self.fonts_ui.remove(ufo)
        w = ufo.document().getMainWindow()
        w.close()

    def ui_window_should_close(self, sender):
        title = sender.getTitle()
        for ufo in self.fonts_ui:
            if title in ufo.path:
                for x in self.w.lists.fontlist:
                    if ufo == x['ufo']:
                        x['overview'] = False
        return False

    def whichfonts(self):
        # returns list of ufos
        # 0 'All',
        # 1 'Selected',
        # 2 'Unselected',
        # 3 'Checked',
        # 4 'Unchecked',
        usethese = []
        setting = self.w.lists.whichfonts.radioGroup.get()

        if NSEvent.modifierFlags():
            flags = NSEvent.modifierFlags()
            if NSCommandKeyMask == flags or NSCommandKeyMask+NSShiftKeyMask == flags:
                setting = 1
            if NSCommandKeyMask+NSAlternateKeyMask == flags or NSCommandKeyMask+NSAlternateKeyMask+NSShiftKeyMask == flags:
                setting = 2
            if NSControlKeyMask == flags or NSControlKeyMask+NSShiftKeyMask == flags:
                setting = 3
            if NSControlKeyMask+NSAlternateKeyMask == flags or NSControlKeyMask+NSAlternateKeyMask+NSShiftKeyMask == flags:
                setting = 4

        if setting == 0:
            for f in self.ufolist:
                usethese.append(f['ufo'])
        if setting == 1:
            selection = self.w.lists.fontlist.getSelection()
            for i, f in enumerate(self.ufolist):
                if i in selection:
                    usethese.append(f['ufo'])
        if setting == 2:
            selection = self.w.lists.fontlist.getSelection()
            for i, f in enumerate(self.ufolist):
                if i not in selection:
                    usethese.append(f['ufo'])
        if setting == 3:
            for f in self.w.lists.fontlist.get():
                if f['checkable'] is True:
                    usethese.append(f['ufo'])
        if setting == 4:
            for f in self.w.lists.fontlist.get():
                if f['checkable'] is not True:
                    usethese.append(f['ufo'])
        return usethese



    # pairlist and pair stuff

    def pairlist_parse(self, pairlist=None):
        cleanpairs = []
        if pairlist is None:
            pairlist = '#header\nA B C D True\nE F G H False\n'.split('\n')
        i = 1
        for pair in pairlist:
            if pair[:0] != '#' and pair.count(' ') == 4:
                left, right, flip_l, flip_r, seen = pair.split(' ')
                if seen == 'True':
                    seen = ''
                else:
                    seen = '✕'
                pairdict = {}
                pairdict['Left'] = left
                pairdict['Right'] = right
                pairdict['Flip L'] = flip_l
                pairdict['Flip R'] = flip_r
                pairdict['Seen'] = seen
                pairdict['i'] = i
                cleanpairs.append(pairdict)
                i += 1
            elif pair[:0] != '#' and pair.count(' ') == 3:
                left, right, flip_l, flip_r = pair.split(' ')
                pairdict = {}
                pairdict['Left'] = left
                pairdict['Right'] = right
                pairdict['Flip L'] = flip_l
                pairdict['Flip R'] = flip_r
                pairdict['Seen'] = ''
                pairdict['i'] = i
                cleanpairs.append(pairdict)
                i += 1
            elif pair[:0] != '#' and pair.count(' ') == 1:
                left, right = pair.split(' ')
                pairdict = {}
                pairdict['Left'] = left
                pairdict['Right'] = right
                pairdict['Flip L'] = right
                pairdict['Flip R'] = left
                pairdict['Seen'] = ''
                pairdict['i'] = i
                cleanpairs.append(pairdict)
                i += 1

        self.paircount = len(cleanpairs)
        return cleanpairs

    def pairlist_selection_changed(self, sender):
        if self.hold is False:
            pairindex = sender.getSelection()
            if pairindex == []:
                pairindex = [0]
            pairindex = pairindex[0]
            progress = (pairindex + 1) / self.paircount
            self.w.lists.progress.set(progress)
            self.w.lists.percent.set(str(int(progress*100))+'%')
            if self.flip is False:
                self.pair_current = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
                self.pair_flipped = [self.pairlist[pairindex]['Flip L'], self.pairlist[pairindex]['Flip R']]
            else:
                self.pair_current = [self.pairlist[pairindex]['Flip L'], self.pairlist[pairindex]['Flip R']]
                self.pair_flipped = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]

            postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
            postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
            self.seen_indicator(pairindex)

            self.w.lists.metricnudge.metric_nudge_glyph.set(self.pair_current[0])

        set_first_responder(self.w.merzLineView.getNSView())

    def pair_override_left(self, sender):
        self.pair_current[0] = sender.get()
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
        postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        set_first_responder(self.w.merzLineView.getNSView())

    def pair_override_right(self, sender):
        self.pair_current[1] = sender.get()
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
        postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        set_first_responder(self.w.merzLineView.getNSView())

    def pair_flip_override_left(self, sender):
        self.pair_flipped[0] = sender.get()
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
        postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        set_first_responder(self.w.merzLineView.getNSView())

    def pair_flip_override_right(self, sender):
        self.pair_flipped[1] = sender.get()
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
        postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        set_first_responder(self.w.merzLineView.getNSView())

    def swap_pair_with_flip(self):
        pairindex = self.w.lists.pairlist.getSelection()
        if pairindex == []:
            pairindex = [0]
        pairindex = pairindex[0]
        self.flip = not self.flip
        if self.flip is False:
            self.pair_current = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
            self.pair_flipped = [self.pairlist[pairindex]['Flip L'], self.pairlist[pairindex]['Flip R']]
        else:
            self.pair_current = [self.pairlist[pairindex]['Flip L'], self.pairlist[pairindex]['Flip R']]
            self.pair_flipped = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_text')
        postEvent(f'{data.extension_key}.merzLineView_change_text', text=string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        self.seen_indicator(pairindex)

    def pairlist_dropfile(self, sender, dropInfo):
        isProposal = dropInfo['isProposal']
        paths = dropInfo['data']
        paths = [dict(path=path) for path in paths if ospath.splitext(path)[-1].lower() in ['.txt']]
        if not paths:
            return False
        if not isProposal:
            self.pairlist_processfile(paths[0]['path'])
        return True

    def pairlist_load(self, sender):
        pairlist_file = GetFile(message='Open a pairlist.txt file.')
        self.pairlist_processfile(pairlist_file)

    def pairlist_processfile(self, pairlist_file):
        self.hold = True
        pairlist = []
        with open(pairlist_file, encoding='utf-8') as userFile:
            if userFile is not None:
                lines = userFile.read()
                lines = lines.splitlines()
                for line in lines:
                    pairlist.append(line)
        self.pairlist = self.pairlist_parse(pairlist)
        self.paircount = len(self.pairlist)

        # find index of last saved current pair in pairlist
        pc = getExtensionDefault(data.extension_key + '.pair_current') or ['A', 'V']
        self.pair_current = [pc[0], pc[1]]
        try:
            i = next(item for item in self.pairlist if item['Left'] == self.pair_current[0] and item['Right'] == self.pair_current[1])['i']-1
            print(self.pair_current[0], self.pair_current[1], 'in pairlist')
        except:
            print(self.pair_current[0], self.pair_current[1], 'not in pairlist')
            i = 0
        self.hold = False

        self.w.lists.pairlist.set(self.pairlist)
        self.w.lists.pairlist.setSelection([i])
        self.seen_indicator(i)
        self.report_progress(i)

    def seen_indicator(self, i):
        self.w.controls.seen.activeL.setFillColor(self.seen_off)
        self.w.controls.seen.activeR.setFillColor(self.seen_off)
        if self.flip is False:
            if self.pairlist[i]['Seen'] != '':
                self.w.controls.seen.activeR.setFillColor(self.seen_on)
        else:
            if self.pairlist[i]['Seen'] != '':
                self.w.controls.seen.activeL.setFillColor(self.seen_on)

    def report_progress(self, i):
        progress = (i+1) / self.paircount
        print('You are ' + str(round(progress*100, 4)) + '% done with this kerning list.')
        if progress >= 1:
            print('100% done with this list!')
        else:
            for i, notifyAt in enumerate(self.notify_steps):
                if i+1 == len(self.notify_steps):
                    n = self.pairlist[int(self.paircount)-1]
                    print('The last pair is:', n['Left'], n['Right'])
                else:
                    if progress >= notifyAt and progress < self.notify_steps[i+1]:
                        n = self.pairlist[int(self.paircount * (notifyAt+.05))-1]
                        print('The next benchmark pair is:', n['Left'], n['Right'])



    # ufo focus indicator

    def increment_focus(self, y, x):
        self.focus[0] += y
        if self.focus[0] > self.listcount-1:
            self.focus[0] = 0
        if self.focus[0] < 0:
            self.focus[0] = self.listcount-1
        if x == 1:
            self.focus[1] = not self.focus[1]
        self.active_ufo_indicator()

    def increment_focus_top(self):
        self.focus[0] = 0
        self.active_ufo_indicator()

    def increment_focus_bottom(self):
        self.focus[0] = self.listcount-1
        self.active_ufo_indicator()

    def active_ufo_indicator(self):
        for i in range(len(self.ufolist)):
            name = 'indicator' + str(i)
            indicator = getattr(self.w.controls, name)
            indicator.activeL.setFillColor(self.focus_indicator_off)
            indicator.activeR.setFillColor(self.focus_indicator_off)
            indicator_color = self.merz_focus_indicator_color
            if i == self.focus[0]:
                if self.focus[1] is False:
                    indicator.activeL.setFillColor(self.focus_indicator_on)
                if self.focus[1] is True:
                    indicator.activeR.setFillColor(self.focus_indicator_on)

                for merz_focus_indicator in self.merz_focus_indicators:
                    merz_focus_indicator.setFillColor((0, 0, 0, 0))
                    name, index = merz_focus_indicator.getName().rsplit('_', 1)
                    if int(index) == self.focus[0]:
                        if self.focus[1] is False and 'mark_pair_current' in name:
                            # get kern value from ui value
                            name = 'buttons' + str(i)
                            ui = getattr(self.w.controls, name)
                            kv = ui.L_edit.get()
                            if kv > 0:
                                indicator_color = self.kern_color_positive
                            if kv < 0:
                                indicator_color = self.kern_color_negative
                            merz_focus_indicator.setFillColor(indicator_color)
                        if self.focus[1] is True and 'mark_pair_flipped' in name:
                            # get kern value from ui value
                            name = 'buttons' + str(i)
                            ui = getattr(self.w.controls, name)
                            kv = ui.R_edit.get()
                            if kv > 0:
                                indicator_color = self.kern_color_positive
                            if kv < 0:
                                indicator_color = self.kern_color_negative
                            merz_focus_indicator.setFillColor(indicator_color)



    # subscriber events

    def window_should_close(self, sender):
        if self.w.lists.fontlist_save.isEnabled() is True:
            q = AskYesNoCancel('You have unsaved changes. Want to save these ufos before closing?')
            if q == -1:
                return False
            elif q == 1:
                self.fontlist_save()
                return True
            else:
                print('Closing without saving. Good luck!')
                return True

    def windowWillClose(self, sender):
        for font in self.fonts_no_ui:
            print('closing', font.info.familyName + ' ' + font.info.styleName)
            font.close()
            self.fonts_no_ui.remove(font)
        setExtensionDefault(data.extension_key + '.reference_glyphs', self.reference_glyphs)
        pairindex = self.w.lists.pairlist.getSelection()
        if pairindex == []:
            return
        pairindex = pairindex[0]
        if pairindex < 25:
            return
        savepair = [self.pairlist[pairindex]['Left'], self.pairlist[pairindex]['Right']]
        setExtensionDefault(data.extension_key + '.pair_current', savepair)

    def fontDocumentDidOpenNew(self, notification):
        f = notification['font']
        font = {}
        if f.info.familyName and f.info.styleName:
            font['fontname'] = f.info.familyName + ' ' + f.info.styleName
        else:
            font['fontname'] = 'No font name'
        font['ufo'] = f
        font['checkable'] = True
        if 'talic' in font['fontname']:
            font['checkable'] = False
        font['spacecenter'] = False
        font['overview'] = True
        self.w.lists.fontlist.append(font)
        self.fonts_ui.append(f)

    def fontDocumentDidOpen(self, notification):
        f = notification['font']
        if f not in self.fonts_ui:
            font = {}
            font['fontname'] = f.info.familyName + ' ' + f.info.styleName
            font['ufo'] = f
            font['checkable'] = True
            if 'talic' in font['fontname']:
                font['checkable'] = False
            font['spacecenter'] = False
            font['overview'] = True
            self.w.lists.fontlist.append(font)
            self.fonts_ui.append(f)

    def fontDocumentWillClose(self, notification):
        f = notification['font']
        if f in self.fonts_ui:
            for i, x in enumerate(self.w.lists.fontlist):
                if f == x['ufo']:
                    del self.w.lists.fontlist[i]
                    self.fonts_ui.remove(f)

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

        # increment focus
        # up/down with arrow keys
        # left/right with (select)

        if keycode == 125:  # down arrow
            if shiftDown != 0:
                self.increment_focus_bottom()
            else:
                self.increment_focus(1, 0)
        if keycode == 126:  # up arrow
            if shiftDown != 0:
                self.increment_focus_top()
            else:
                self.increment_focus(-1, 0)
        if keycode == 105:  # f13 / (select)
            self.increment_focus(0, 1)

        # change pair selections
        # up/down with .,

        if keycode == 47:  # period / (a)
            index = self.w.lists.pairlist.getSelection()[0]
            if index + 1 < self.paircount:
                self.w.lists.pairlist.setSelection(
                    [self.w.lists.pairlist.getSelection()[0] + 1])
        if keycode == 43:  # comma / (x)
            index = self.w.lists.pairlist.getSelection()[0]
            if index > 0:
                self.w.lists.pairlist.setSelection(
                    [self.w.lists.pairlist.getSelection()[0] - 1])

        # flip pair
        # start

        if keycode == 107:  # f14 / (start)
            self.swap_pair_with_flip()

        # adjust kerning
        # left/right arrow
        # shift = right shoulder
        # option = left shoulder

        if keycode == 123 or keycode == 124:  # leftarrow # rightarrow

            # which pair
            pair = self.pair_current
            if 1 == self.focus[1]:
                pair = self.pair_flipped

            # positive or negative
            mod = 1
            if keycode == 123:  # leftarrow
                mod = -1

            adjust_by = self.adjust_S*mod
            if shiftDown != 0:  # shift down
                adjust_by = self.adjust_M*mod

            if optionDown != 0:  # option down
                ufo = self.ufolist[self.focus[0]]['ufo']
                # adjust both sides at once
                pair = self.pair_current
                kernValue = ufo.kerning.find(pair) or 0
                self.update_kerning(self.focus[0], pair, kernValue+adjust_by)
                pair = self.pair_flipped
                kernValue = ufo.kerning.find(pair) or 0
                self.update_kerning(self.focus[0], pair, kernValue+adjust_by)

            else:
                # adjust pair in active font
                ufo = self.ufolist[self.focus[0]]['ufo']
                kernValue = ufo.kerning.find(pair) or 0
                self.update_kerning(self.focus[0], pair, kernValue+adjust_by)

        # copy value from/to opposite pair

        if keycode == 113:  # f15 / (b)
            ufo = self.ufolist[self.focus[0]]['ufo']
            pair = self.pair_current
            flip = self.pair_flipped
            if 1 == self.focus[1]:
                pair = self.pair_flipped
                flip = self.pair_current

            if shiftDown != 0:
                # copy to opposite
                kernValue = ufo.kerning.find(flip) or 0
                # FASTER: get from dict instead of ufo
                self.update_kerning(self.focus[0], pair, kernValue)
            else:
                # copy from opposite
                kernValue = ufo.kerning.find(pair) or 0
                # FASTER: get from dict instead of ufo
                self.update_kerning(self.focus[0], flip, kernValue)

        # zero selected pair

        if keycode == 64:  # f17 / (y)
            if shiftDown != 0:
                # zero
                pair = self.pair_current
                if 1 == self.focus[1]:
                    pair = self.pair_flipped
                self.update_kerning(self.focus[0], pair, 0)

        # save ufos

        if keycode == 1:  # s
            if commandDown != 0:
                self.fontlist_save()



    # adjust kerning

    def adjust_pair_plus(self, sender):
        adjust = self.adjust_S
        if NSEvent.modifierFlags() & NSShiftKeyMask:
            adjust = self.adjust_M
        self.adjust(sender.i, self.pair_current, adjust)

    def adjust_pair_minus(self, sender):
        adjust = self.adjust_S
        if NSEvent.modifierFlags() & NSShiftKeyMask:
            adjust = self.adjust_M
        self.adjust(sender.i, self.pair_current, -adjust)

    def adjust_flip_plus(self, sender):
        adjust = self.adjust_S
        if NSEvent.modifierFlags() & NSShiftKeyMask:
            adjust = self.adjust_M
        self.adjust(sender.i, self.pair_flipped, adjust)

    def adjust_flip_minus(self, sender):
        adjust = self.adjust_S
        if NSEvent.modifierFlags() & NSShiftKeyMask:
            adjust = self.adjust_M
        self.adjust(sender.i, self.pair_flipped, -adjust)

    def adjust(self, i, pair, adjust, hold=False):
        if i == 'AllFonts':
            whichfonts = self.whichfonts()
            for n in range(len(self.ufolist)):
                hold = True
                if n+1 == len(self.ufolist):
                    hold = False
                ufo = self.ufolist[n]['ufo']
                if ufo in whichfonts:
                    kern = ufo.kerning.find(pair) or 0
                    self.update_kerning(n, pair, kern+adjust, hold)
        else:
            kern = self.ufolist[i]['ufo'].kerning.find(pair) or 0
            self.update_kerning(i, pair, kern+adjust, hold)

    def edit_pair(self, sender):
        i = sender.i
        value = sender.get()
        if i == 'AllFonts':
            if value is not None:
                sender.set('')
                whichfonts = self.whichfonts()
                for n in range(len(self.ufolist)):
                    hold = True
                    if n+1 == len(self.ufolist):
                        hold = False
                    ufo = self.ufolist[n]['ufo']
                    if ufo in whichfonts:
                        self.update_kerning(n, self.pair_current, value, hold)
        else:
            self.update_kerning(i, self.pair_current, value)
        set_first_responder(self.w.merzLineView.getNSView())

    def edit_flip(self, sender):
        i = sender.i
        value = sender.get()
        if i == 'AllFonts':
            if value is not None:
                sender.set('')
                whichfonts = self.whichfonts()
                for n in range(len(self.ufolist)):
                    hold = True
                    if n+1 == len(self.ufolist):
                        hold = False
                    ufo = self.ufolist[n]['ufo']
                    if ufo in whichfonts:
                        self.update_kerning(n, self.pair_flipped, value, hold)
        else:
            self.update_kerning(i, self.pair_flipped, value)
        set_first_responder(self.w.merzLineView.getNSView())



    # universal buttons

    def universal_reference_set_pair(self, sender):
        g = None
        if sender.align == 'right':
            g = self.pair_current[0]
        if sender.align == 'left':
            g = self.pair_current[1]
        if g is not None:
            self.universal_reference_set(sender, g, sender.get())

    def universal_reference_set_flip(self, sender):
        g = None
        if sender.align == 'right':
            g = self.pair_flipped[0]
        if sender.align == 'left':
            g = self.pair_flipped[1]
        if g is not None:
            self.universal_reference_set(sender, g, sender.get())

    def universal_reference_set(self, edittext, g, new):
        if new == '':
            del self.reference_glyphs[g]
        elif new != g:
            self.reference_glyphs[g] = new
        setExtensionDefault(data.extension_key + '.reference_glyphs', self.reference_glyphs)
        set_first_responder(self.w.merzLineView.getNSView())
        self.update_window_controls_kerning_text()



    # zero values

    def universal_reference_zero_pair_current(self, sender):
        whichfonts = self.whichfonts()
        for n in range(len(self.ufolist)):
            hold = True
            if n+1 == len(self.ufolist):
                hold = False
            ufo = self.ufolist[n]['ufo']
            if ufo in whichfonts:
                self.update_kerning(n, self.pair_current, 0, hold)

    def universal_reference_zero_pair_flipped(self, sender):
        whichfonts = self.whichfonts()
        for n in range(len(self.ufolist)):
            hold = True
            if n+1 == len(self.ufolist):
                hold = False
            ufo = self.ufolist[n]['ufo']
            if ufo in whichfonts:
                self.update_kerning(n, self.pair_flipped, 0, hold)



    # copy from values

    def universal_reference_copy_pair_current(self, sender):
        self.universal_reference_copy_pair(self.pair_current, sender.i.split(' '))
        #

    def universal_reference_copy_pair_flipped(self, sender):
        self.universal_reference_copy_pair(self.pair_flipped, sender.i.split(' '))
        #

    def universal_reference_copy_pair(self, targetpair, referencepair):
        if referencepair is not None:
            whichfonts = self.whichfonts()
            for n in range(len(self.ufolist)):
                ufo = self.ufolist[n]['ufo']
                kernValue = ufo.kerning.find(referencepair) or 0
                hold = True
                if n+1 == len(self.ufolist):
                    hold = False
                ufo = self.ufolist[n]['ufo']
                if ufo in whichfonts:
                    self.update_kerning(n, targetpair, kernValue, hold)



    # kerning stuff

    def update_kerning(self, index, pair, value, hold=False):
        self.w.lists.fontlist_save.enable(True)

        left, right = pair
        f = self.ufolist[index]['ufo']

        left = self.get_kern_group(f, left, 'left')
        right = self.get_kern_group(f, right, 'right')

        if value == 0 or value == '' or value == 'None' or value is None:
            f.kerning[(left, right)] = 0
            f.kerning.remove((left, right))
        else:
            f.kerning[(left, right)] = value

        change = (index, pair, value)
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_position')
        postEvent(f'{data.extension_key}.merzLineView_change_position', change=change)
        set_first_responder(self.w.merzLineView.getNSView())

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



    # reference glyphs

    def reference_changed_left(self, sender):
        new = sender.get()
        sender.set(self.pair_flipped[0])
        self.reference_changed(self.pair_flipped[0], new)
        set_first_responder(self.w.merzLineView.getNSView())

    def reference_changed_right(self, sender):
        new = sender.get()
        sender.set(self.pair_flipped[1])
        self.reference_changed(self.pair_flipped[1], new)
        set_first_responder(self.w.merzLineView.getNSView())

    def reference_changed(self, g, new):
        if new == '':
            del self.reference_glyphs[g]
        elif new != g:
            self.reference_glyphs[g] = new
        setExtensionDefault(data.extension_key + '.reference_glyphs', self.reference_glyphs)
        # update reference buttons
        self.update_window_controls_kerning_text()



    # merzLineView guts

    def merzLineView_hold(self, notification):
        self.hold = False
        # send notification for whatever we were holding
        for event in notification['lowLevelEvents']:
            holdfor = event['holdfor']
            if holdfor == 'change_fonts':
                postEvent(f'{data.extension_key}.merzLineView_change_fonts')
            if holdfor == 'change_text':
                postEvent(f'{data.extension_key}.merzLineView_change_text', text=None)
            if holdfor == 'change_position':
                postEvent(f'{data.extension_key}.merzLineView_change_position', change=None)

    def merzLineView_build_initial_layers(self):
        # print('merzLineView_build_initial_layers')
        # set up merz stuff
        view = self.w.merzLineView
        container = view.getMerzContainer()
        container.clearSublayers()
        height = view.height()
        width = view.width()
        baseLayer = container.appendBaseSublayer()

        # set up data
        self.merzLayerData = {}
        self.merzLayerData['baseLayer'] = baseLayer
        self.merzLayerData['fontData'] = []

        ypos = self.ui_metrics['ypos']

        # add font layers and data
        with baseLayer.sublayerGroup():
            for i in range(len(self.ufolist)):

                # big text
                lineHeight = self.size_big*self.lineheight
                y = height-ypos-(lineHeight*(i+.85))
                fontlayer = container.appendBaseSublayer(
                    position=(0, y),
                    size=(width, lineHeight),
                    # backgroundColor=(1, 0, 0, .1),
                )
                fontlayer.addSublayerScaleTransformation(self.size_big/1000, name='scale', center=(0, 0))

                # small text
                fontlayersmall = container.appendBaseSublayer(
                    position=(0, y),
                    size=(width, lineHeight),
                    # backgroundColor=(0, 1, 0, .1),
                )
                fontlayersmall.addSublayerScaleTransformation(self.size_small/1000, name='scale', center=(0, 0))
                fontlayersmall.addTranslationTransformation((width/2, 0), name='translateX')

                # add font stuff to data
                fontData = {}
                # fontData['ufo'] = ufo['ufo']
                fontData['ufo'] = self.ufolist[i]['ufo']
                fontData['fontLayer'] = fontlayer
                fontData['glyphLayers'] = []
                fontData['fontLayerSmall'] = fontlayersmall
                fontData['glyphLayersSmall'] = []
                fontData['glyphs'] = []
                fontData['kerns'] = {}
                self.merzLayerData['fontData'].append(fontData)

    def merzLineView_get_position_data(self, text):
        # print('merzLineView_get_position_data')
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
                        if text[n+1] in ufoGlyphOrder:
                            pair = (glyphName, text[n+1])
                            if tuple(pair) not in fontData['kerns']:
                                kernValue = ufo.kerning.find(pair) or 0
                                fontData['kerns'][tuple(pair)] = kernValue

                    fontData['glyphs'].append((glyphName, ufo[glyphName].width))

    def merzLineView_change_position_data(self):
        for change in self.cache_positions:
            fontIndex, pair, newkern = change
            self.merzLayerData['fontData'][fontIndex]['kerns'][tuple(pair)] = newkern

    def merzLineView_add_glyph_layers(self):
        baseLayer = self.merzLayerData['baseLayer']
        if self.merzLayerData is None or baseLayer is None:
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

                    glyphLayer = fontlayer.appendPathSublayer(position=(0, 0), name=glyphName)
                    glyphLayer.setPath(glyphPath)
                    fontData['glyphLayers'].append(glyphLayer)

                    glyphLayerSmall = fontlayersmall.appendPathSublayer(position=(0, 0))
                    glyphLayerSmall.setPath(glyphPath)
                    fontData['glyphLayersSmall'].append(glyphLayerSmall)

    def merzLineView_position_glyph_layers(self):  # kerning labels and indicators are built here too
        if self.merzLayerData is None:
            return

        self.merz_focus_indicators = []

        # big text
        xPos = 0
        for i, fontData in enumerate(self.merzLayerData['fontData']):
            glyphLayerCount = len(fontData['glyphLayers'])
            x = lastKernX = 500  # start x position
            for n, glyphLayer in enumerate(fontData['glyphLayers']):
                glyphLayer.clearSublayers()

                # if not first glyph, get kern value
                # NEEDS TO TEST IF GLYPH IN DATA
                kernValue = 0
                if n > 0:
                    pair = (fontData['glyphs'][n-1][0], fontData['glyphs'][n][0])
                    kernValue = fontData['kerns'][tuple(pair)] or 0

                # position glyph
                glyphLayer.setPosition((x+kernValue, 0))

                # add value label
                y = -25
                kernColor = None
                if self.label_kerning_on is True and kernValue != 0:
                    if kernValue < 0:
                        kernColor = self.kern_color_negative
                    if kernValue > 0:
                        kernColor = self.kern_color_positive
                    if x+kernValue-400 < lastKernX:
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

                # add indicator
                indicator_color = self.merz_focus_indicator_color
                if kernColor is not None:
                    indicator_color = kernColor
                if n > 0:
                    pair = [fontData['glyphLayers'][n-1].getName(), glyphLayer.getName()]
                    mark_pair_name = None
                    if pair == self.pair_current:
                        mark_pair_name = 'mark_pair_current_'+str(i)
                    elif pair == self.pair_flipped:
                        mark_pair_name = 'mark_pair_flipped_'+str(i)
                    if mark_pair_name is not None:
                        merz_focus_indicator = glyphLayer.appendPathSublayer(
                            name=mark_pair_name,
                            position=(0, y-275),  # shift below kern value
                            fillColor=(0, 0, 0, 0)
                        )
                        pen = merz_focus_indicator.getPen()
                        pen.moveTo((-100, -50))
                        pen.moveTo((-100, -60))
                        pen.lineTo((100, -60))
                        pen.lineTo((100, -50))
                        pen.lineTo((0, 0))
                        pen.closePath()
                        self.merz_focus_indicators.append(merz_focus_indicator)
                        if i == self.focus[0]:
                            if self.focus[1] is False and 'mark_pair_current' in mark_pair_name:
                                merz_focus_indicator.setFillColor(indicator_color)
                            if self.focus[1] is True and 'mark_pair_flipped' in mark_pair_name:
                                merz_focus_indicator.setFillColor(indicator_color)

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
            x = xPos/(1/(self.size_big/1000))
            fontLayerSmall.addTranslationTransformation((x, 0), name='translateX')

            # position glyphs
            for n, glyphLayersSmall in enumerate(fontData['glyphLayersSmall']):
                kernValue = 0
                if n > 0:
                    pair = (fontData['glyphs'][n-1][0], fontData['glyphs'][n][0])
                    kernValue = fontData['kerns'][tuple(pair)] or 0

                glyphLayersSmall.setPosition((x+kernValue, 0))
                x += fontData['glyphs'][n][1]+kernValue



    '''
    how the events work

    change_fonts:
        started
        fontlist_edit

    change_text:
        change_fonts
        pairlist_selection_changed
        pair_override_left
        pair_override_right
        swap_pair_with_flip

    change_position:
        change_text
        update_kerning

    '''

    def merzLineView_change_fonts(self, notification):
        # print('merzLineView_change_fonts')
        if self.hold is False:
            # unique to fontlist
            self.merzLineView_build_initial_layers()
            self.update_window_controls_kerning_fonts()
            if len(self.ufolist) > 0:
                self.merzLineView_change_text(None)

    def merzLineView_change_text(self, notification):
        # print('merzLineView_change_text')
        if notification is not None:
            for event in notification['lowLevelEvents']:
                if 'text' in event.keys():
                    text = event['text']
                    if text is not None:
                        self.cache_text.append(text)
                else:
                    self.cache_text.append(string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        if self.hold is False and len(self.ufolist) > 0:
            self.merzLineView_get_position_data(self.cache_text[-1])
            self.merzLineView_add_glyph_layers()
            self.merzLineView_change_position(None)
            self.update_window_controls_kerning_text()
            self.cache_text = [self.cache_text[-1]]

    def merzLineView_change_position(self, notification):
        # print('merzLineView_change_position')
        if notification is not None:
            for event in notification['lowLevelEvents']:
                if 'change' in event.keys():
                    change = event['change']
                    if change is not None:
                        self.cache_positions.append(change)
                else:
                    print('no change in notification')
        if self.hold is False:
            self.merzLineView_change_position_data()
            self.merzLineView_position_glyph_layers()
            self.update_window_controls_kerning_position()
            self.cache_positions = []



    # update ui buttons too

    def update_window_controls_kerning_fonts(self):
        # print('update_window_controls_kerning_fonts')

        # if there are more buttons than fonts, remove the buttons
        count = len(self.ufolist)
        while hasattr(self.w.controls, 'buttons'+str(count)):
            delattr(self.w.controls, 'buttons'+str(count))
            delattr(self.w.controls, 'indicator'+str(count))
            count += 1

        # if there are less buttons than fonts, add
        count = len(self.ufolist)-1
        while not hasattr(self.w.controls, 'buttons'+str(count)):
            if count < 0:
                break
            self.build_window_controls_kerning_one_ufo(count)
            count -= 1

    def update_window_controls_kerning_text(self):
        # print('update_window_controls_kerning_text')

        # pair labels
        self.w.controls.pairs.left.set(self.pair_current[0])
        self.w.controls.pairs.right.set(self.pair_current[1])
        self.w.controls.pairs.flipped_left.set(self.pair_flipped[0])
        self.w.controls.pairs.flipped_right.set(self.pair_flipped[1])

        # get reference pairs
        all_reference_current = []
        all_reference_flipped = []
        g0 = None
        g1 = None
        f0 = None
        f1 = None

        if self.pair_current[0] in self.reference_glyphs:
            g0 = self.reference_glyphs[self.pair_current[0]] or None
        if self.pair_current[1] in self.reference_glyphs:
            g1 = self.reference_glyphs[self.pair_current[1]] or None

        if self.pair_flipped[0] in self.reference_glyphs:
            f0 = self.reference_glyphs[self.pair_flipped[0]] or None
        if self.pair_flipped[1] in self.reference_glyphs:
            f1 = self.reference_glyphs[self.pair_flipped[1]] or None

        # change fontlist reference pair data
        for i in range(len(self.ufolist)):
            ufo = self.ufolist[i]['ufo']
            name = 'buttons' + str(i)

            ui = getattr(self.w.controls, name)

            # get pair_current kern value
            pair_current_kern_value = 0
            if tuple(self.pair_current) in self.merzLayerData['fontData'][i]['kerns'].keys():
                pair_current_kern_value = self.merzLayerData['fontData'][i]['kerns'][tuple(self.pair_current)] or 0
            ui.L_edit.set(pair_current_kern_value)

            # get pair_flipped kern value
            pair_flipped_kern_value = 0
            if tuple(self.pair_flipped) in self.merzLayerData['fontData'][i]['kerns'].keys():
                pair_flipped_kern_value = self.merzLayerData['fontData'][i]['kerns'][tuple(self.pair_flipped)] or 0
            ui.R_edit.set(pair_flipped_kern_value)

            # reference groups
            xg0 = g0
            xg1 = g1
            xf0 = f0
            xf1 = f1
            if xg0 is not None and self.check_if_same_group(ufo, xg0, self.pair_current[0], 'left') is True:
                xg0 = None
            if xg1 is not None and self.check_if_same_group(ufo, xg1, self.pair_current[1], 'right') is True:
                xg1 = None
            if xf0 is not None and self.check_if_same_group(ufo, xf0, self.pair_flipped[0], 'left') is True:
                xf0 = None
            if xf1 is not None and self.check_if_same_group(ufo, xf1, self.pair_flipped[1], 'right') is True:
                xf1 = None

            reference_current = []
            if xg0 is not None:
                if xg1 is not None:
                    reference_current.append([xg0, xg1])
                    reference_current.append([self.pair_current[0], xg1])
                    reference_current.append([xg0, self.pair_current[1]])
                else:
                    reference_current.append([xg0, self.pair_current[1]])
            elif xg1 is not None:
                reference_current.append([self.pair_current[0], xg1])
            for g in reference_current:
                if g not in all_reference_current:
                    all_reference_current.append(g)

            # reference_flipped = []
            # if xf0 is not None:
            #     if xf1 is not None:
            #         reference_flipped.append([xf0, xf1])
            #         reference_flipped.append([self.pair_flipped[0], xf1])
            #         reference_flipped.append([xf0, self.pair_flipped[1]])
            #     else:
            #         reference_flipped.append([xf0, self.pair_flipped[1]])
            # elif xf1 is not None:
            #     reference_flipped.append([self.pair_flipped[0], xf1])
            # for g in reference_flipped:
            #     if g not in all_reference_flipped:
            #         all_reference_flipped.append(g)

            reference_flipped = []
            if xf0 is not None:
                if xf1 is not None:
                    reference_flipped.append([xf0, xf1])
                    reference_flipped.append([xf0, self.pair_flipped[1]])
                    reference_flipped.append([self.pair_flipped[0], xf1])
                else:
                    reference_flipped.append([xf0, self.pair_flipped[1]])
            elif xf1 is not None:
                reference_flipped.append([self.pair_flipped[0], xf1])
            for g in reference_flipped:
                if g not in all_reference_flipped:
                    all_reference_flipped.append(g)

            ui.reference_0L.show(False)
            if len(reference_current) > 0:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_0L, reference_current[0], 'current', pair_current_kern_value)
                ui.reference_0L.show(True)
            ui.reference_0R.show(False)
            if len(reference_flipped) > 0:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_0R, reference_flipped[0], 'flipped', pair_flipped_kern_value)
                ui.reference_0R.show(True)

            ui.reference_1L.show(False)
            if len(reference_current) > 1:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_1L, reference_current[1], 'current', pair_current_kern_value)
                ui.reference_1L.show(True)
            ui.reference_1R.show(False)
            if len(reference_flipped) > 1:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_1R, reference_flipped[1], 'flipped', pair_flipped_kern_value)
                ui.reference_1R.show(True)

            ui.reference_2L.show(False)
            if len(reference_current) > 2:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_2L, reference_current[2], 'current', pair_current_kern_value)
                ui.reference_2L.show(True)
            ui.reference_2R.show(False)
            if len(reference_flipped) > 2:
                self.set_info_in_reference_pair_group(i, ufo, ui.reference_2R, reference_flipped[2], 'flipped', pair_flipped_kern_value)
                ui.reference_2R.show(True)

            # change indicator size
            # change indicator size
            # change indicator size

        # change universal reference pair data
        universal = self.w.controls.universal

        if g0 is not None or g1 is not None:
            a = g0
            if a is None:
                a = self.pair_current[0]
            b = g1
            if b is None:
                b = self.pair_current[1]
            universal.reference_0L.kern.i = str(a + ' ' + b)
            universal.reference_0L.kern.show(True)
        else:
            universal.reference_0L.kern.show(False)
        if len(all_reference_current) == 0:
            universal.reference_0L.kern.show(False)
        universal.reference_0L.left.set(g0)
        universal.reference_0L.right.set(g1)
        universal.reference_0L.left.setPlaceholder(self.pair_current[0])
        universal.reference_0L.right.setPlaceholder(self.pair_current[1])

        if f0 is not None or f1 is not None:
            a = f0
            if a is None:
                a = self.pair_flipped[0]
            b = f1
            if b is None:
                b = self.pair_flipped[1]
            universal.reference_0R.flip_kern.i = str(a + ' ' + b)
            universal.reference_0R.flip_kern.show(True)
        else:
            universal.reference_0R.flip_kern.show(False)
        if len(all_reference_flipped) == 0:
            universal.reference_0R.flip_kern.show(False)
        universal.reference_0R.flip_left.set(f0)
        universal.reference_0R.flip_right.set(f1)
        universal.reference_0R.flip_left.setPlaceholder(self.pair_flipped[0])
        universal.reference_0R.flip_right.setPlaceholder(self.pair_flipped[1])

        universal.reference_1L.show(False)
        if len(all_reference_current) > 1:
            universal.reference_1L.left.set(all_reference_current[1][0])
            universal.reference_1L.right.set(all_reference_current[1][1])
            universal.reference_1L.kern.i = str(all_reference_current[1][0] + ' ' + all_reference_current[1][1])
            universal.reference_1L.show(True)
        universal.reference_1R.show(False)
        if len(all_reference_flipped) > 1:
            universal.reference_1R.flip_left.set(all_reference_flipped[1][0])
            universal.reference_1R.flip_right.set(all_reference_flipped[1][1])
            universal.reference_1R.flip_kern.i = str(all_reference_flipped[1][0] + ' ' + all_reference_flipped[1][1])
            universal.reference_1R.show(True)

        universal.reference_2L.show(False)
        if len(all_reference_current) > 2:
            universal.reference_2L.left.set(all_reference_current[2][0])
            universal.reference_2L.right.set(all_reference_current[2][1])
            universal.reference_2L.kern.i = str(all_reference_current[2][0] + ' ' + all_reference_current[2][1])
            universal.reference_2L.show(True)
        universal.reference_2R.show(False)
        if len(all_reference_flipped) > 2:
            universal.reference_2R.flip_left.set(all_reference_flipped[2][0])
            universal.reference_2R.flip_right.set(all_reference_flipped[2][1])
            universal.reference_2R.flip_kern.i = str(all_reference_flipped[2][0] + ' ' + all_reference_flipped[2][1])
            universal.reference_2R.show(True)

    def check_if_same_group(self, f, g1, g2, side):  # helper for update_window_controls_kerning_text
        if self.get_kern_group(f, g1, side) == self.get_kern_group(f, g2, side):
            return True
        else:
            return False

    def set_info_in_reference_pair_group(self, i, ufo, ui, referencepair, side, pair_value):  # helper for update_window_controls_kerning_text
        # print('set_info_in_reference_pair_group')
        red = NSColor.redColor()
        black = NSColor.controlTextColor()

        # get kerning value
        # try dict first
        if tuple(referencepair) in self.merzLayerData['fontData'][i]['kerns'].keys():
            kv = self.merzLayerData['fontData'][i]['kerns'][tuple(referencepair)]
        # otherwise, get from ufo
        else:
            kv = ufo.kerning.find(referencepair) or 0
            # should this be added to the kern dict or is that being erased evert text change?
        if side == 'current':
            ui.left.set(referencepair[0])
            ui.kern.set(kv)
            ui.right.set(referencepair[1])
            to_color = ui.kern
        if side == 'flipped':
            ui.flip_left.set(referencepair[0])
            ui.flip_kern.set(kv)
            ui.flip_right.set(referencepair[1])
            to_color = ui.flip_kern

        if kv != pair_value:
            to_color.getNSTextField().setTextColor_(red)
        else:
            to_color.getNSTextField().setTextColor_(black)

    def update_window_controls_kerning_position(self):
        # print('update_window_controls_kerning_position')
        red = NSColor.redColor()
        black = NSColor.controlTextColor()

        for change in self.cache_positions:
            fontIndex, pair, newkern = change
            name = 'buttons' + str(fontIndex)
            ui = getattr(self.w.controls, name)
            if pair == self.pair_current:
                ui.L_edit.set(newkern)
            if pair == self.pair_flipped:
                ui.R_edit.set(newkern)

            # check if reference value is a match or not now
            name = 'buttons' + str(fontIndex)
            ui = getattr(self.w.controls, name)

            if self.pair_current == pair and ui.reference_0L.isVisible():
                kv = int(ui.reference_0L.kern.get())
                if kv != newkern:
                    ui.reference_0L.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_0L.kern.getNSTextField().setTextColor_(black)

            if self.pair_flipped == pair and ui.reference_0R.isVisible():
                kv = int(ui.reference_0R.flip_kern.get())
                if kv != newkern:
                    ui.reference_0R.flip_kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_0R.flip_kern.getNSTextField().setTextColor_(black)

            if self.pair_current == pair and ui.reference_1L.isVisible():
                kv = int(ui.reference_1L.kern.get())
                if kv != newkern:
                    ui.reference_1L.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_1L.kern.getNSTextField().setTextColor_(black)

            if self.pair_flipped == pair and ui.reference_1R.isVisible():
                kv = int(ui.reference_1R.flip_kern.get())
                if kv != newkern:
                    ui.reference_1R.flip_kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_1R.flip_kern.getNSTextField().setTextColor_(black)

            if self.pair_current == pair and ui.reference_2L.isVisible():
                kv = int(ui.reference_2L.kern.get())
                if kv != newkern:
                    ui.reference_2L.kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_2L.kern.getNSTextField().setTextColor_(black)

            if self.pair_flipped == pair and ui.reference_2R.isVisible():
                kv = int(ui.reference_2R.flip_kern.get())
                if kv != newkern:
                    ui.reference_2R.flip_kern.getNSTextField().setTextColor_(red)
                else:
                    ui.reference_2R.flip_kern.getNSTextField().setTextColor_(black)



    # open spacecenter

    def fontlist_open_ufo_spacecenter(self, ufo, i):
        sc = OpenSpaceCenter(ufo, newWindow=False)
        sc.set(string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        self.opened_windows[sc] = i

    def fontlist_close_ufo_spacecenter(self, ufo, i):
        for sc, index in self.opened_windows.items():
            if index == i:
                del self.opened_windows[sc]
                sc.getNSView().window().windowController().close()
                break

    def spaceCenterWillClose(self, subscriberevent):
        sc = subscriberevent['spaceCenter']
        if sc in self.opened_windows.keys():
            i = self.opened_windows[sc]
            del self.opened_windows[sc]
            ufolist_updated = self.w.lists.fontlist.get()
            ufolist_updated[i]['spacecenter'] = False
            self.w.lists.fontlist.set(ufolist_updated)



    # nudge metrics

    def metric_nudge_nL(self, sender):
        self.metric_nudge(-5, 'Left')

    def metric_nudge_pL(self, sender):
        self.metric_nudge(5, 'Left')

    def metric_nudge_nR(self, sender):
        self.metric_nudge(-5, 'Right')

    def metric_nudge_pR(self, sender):
        self.metric_nudge(5, 'Right')

    def metric_nudge(self, amount, side):
        g = self.w.lists.metricnudge.metric_nudge_glyph.get()
        selection = self.w.lists.fontlist.getSelection()
        for ufo in self.whichfonts():
            if g in ufo.glyphOrder:
                if side == 'Left':
                    ufo[g].leftMargin += amount
                    ufo.changed()
                if side == 'Right':
                    ufo[g].rightMargin += amount
                    ufo.changed()
        self.w.lists.fontlist_save.enable(True)
        postEvent(f'{data.extension_key}.merzLineView_hold', holdfor='change_fonts')
        postEvent(f'{data.extension_key}.merzLineView_change_fonts')




delay=0.05
if f'{data.extension_key}.merzLineView_hold' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{data.extension_key}.merzLineView_hold',
        methodName='merzLineView_hold',
        lowLevelEventNames=[f'{data.extension_key}.merzLineView_hold'],
        dispatcher='roboFont',
        delay=delay,
    )
if f'{data.extension_key}.merzLineView_change_fonts' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{data.extension_key}.merzLineView_change_fonts',
        methodName='merzLineView_change_fonts',
        lowLevelEventNames=[f'{data.extension_key}.merzLineView_change_fonts'],
        dispatcher='roboFont',
        delay=delay,
    )
if f'{data.extension_key}.merzLineView_change_text' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{data.extension_key}.merzLineView_change_text',
        methodName='merzLineView_change_text',
        lowLevelEventNames=[f'{data.extension_key}.merzLineView_change_text'],
        dispatcher='roboFont',
        delay=delay,
    )
if f'{data.extension_key}.merzLineView_change_position' not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=f'{data.extension_key}.merzLineView_change_position',
        methodName='merzLineView_change_position',
        lowLevelEventNames=[f'{data.extension_key}.merzLineView_change_position'],
        dispatcher='roboFont',
        delay=delay,
    )

if __name__ == '__main__':
    registerRoboFontSubscriber(keerrrnnnn)

