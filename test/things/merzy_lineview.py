class merzy_lineview():

    debug = True

    # merzy_lineview guts

    def merzy_lineview_hold(self, notification):
        self.hold = False
        # send notification for whatever we were holding
        for event in notification['lowLevelEvents']:
            holdfor = event['holdfor']
            if holdfor == 'change_fonts':
                postEvent(f'{data.extension_key}.merzy_lineview_change_fonts')
            if holdfor == 'change_text':
                postEvent(f'{data.extension_key}.merzy_lineview_change_text', text=None)
            if holdfor == 'change_position':
                postEvent(f'{data.extension_key}.merzy_lineview_change_position', change=None)

    def merzy_lineview_build_initial_layers(self):
        # print('merzy_lineview_build_initial_layers')
        # set up merz stuff
        view = self.w.merzy_lineview
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

    def merzy_lineview_get_position_data(self, text):
        # print('merzy_lineview_get_position_data')
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

    def merzy_lineview_change_position_data(self):
        for change in self.cache_positions:
            fontIndex, pair, newkern = change
            self.merzLayerData['fontData'][fontIndex]['kerns'][tuple(pair)] = newkern

    def merzy_lineview_add_glyph_layers(self):
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

    def merzy_lineview_position_glyph_layers(self):  # kerning labels and indicators are built here too
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

    def merzy_lineview_change_fonts(self, notification):
        # print('merzy_lineview_change_fonts')
        if self.hold is False:
            # unique to fontlist
            self.merzy_lineview_build_initial_layers()
            self.update_window_controls_kerning_fonts()
            if len(self.ufolist) > 0:
                self.merzy_lineview_change_text(None)

    def merzy_lineview_change_text(self, notification):
        # print('merzy_lineview_change_text')
        if notification is not None:
            for event in notification['lowLevelEvents']:
                if 'text' in event.keys():
                    text = event['text']
                    if text is not None:
                        self.cache_text.append(text)
                else:
                    self.cache_text.append(string_builder(self.pair_current, self.pair_flipped, self.ufolist))
        if self.hold is False and len(self.ufolist) > 0:
            self.merzy_lineview_get_position_data(self.cache_text[-1])
            self.merzy_lineview_add_glyph_layers()
            self.merzy_lineview_change_position(None)
            self.update_window_controls_kerning_text()
            self.cache_text = [self.cache_text[-1]]

    def merzy_lineview_change_position(self, notification):
        # print('merzy_lineview_change_position')
        if notification is not None:
            for event in notification['lowLevelEvents']:
                if 'change' in event.keys():
                    change = event['change']
                    if change is not None:
                        self.cache_positions.append(change)
                else:
                    print('no change in notification')
        if self.hold is False:
            self.merzy_lineview_change_position_data()
            self.merzy_lineview_position_glyph_layers()
            self.update_window_controls_kerning_position()
            self.cache_positions = []

