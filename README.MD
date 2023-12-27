# Sharing with friends, message me if you're interested.

Robofont Multikern - a basic extension to kern a family of ufo sources simultaneously

---

## Update v1.0

- Finally packaged this into a .roboFontExt but did nothing to make it more user friendly

---

## Limitations
- I made this for kerning one specific font. It's usefulness in kerning other fonts will be limited. Hoping to add some more universal features and flexibility in the future.
- This is setup to kern in increments of 5. Not hard to change that, but WWJDD?
- Kerning exceptions are complicated and I didn't bother to figure out how to handle them. Instead I put problematic glyphs in their own groups and used the reference glyphs (below) to keep them in line with their base glyphs. Not a great solution.

## The tool is intended to be used with a gaming controller
- I use enjoyable.app to turn controller button presses into keycodes (see /helpers/SN30_Mapping.enjoyable)
- This is hard coded for my preferences and my controller. It shouldn't be hard to reverse engineer and adjust to your own needs.
- Jump to the keyDown() function to see the keycodes and logic
  - up/down - change the focused ufo (indicated by a white background)
  - select (f13) - flip which pair is focused, AB or BA
  - a/x (./,) - next/previous pair
  - start (f14) - flip the pairs ABBA becomes BAAB
  - left/right - make a small kerning adjustment to the focused pair - self.adjust_S = 5
  - left/right+shift - make a medium kerning adjustment to the focused pair - self.adjust_M = 10
  - left/right(+shift)+option - make the small or medium kerning adjustment to both pairs
  - b (f15) - copy the kerning value of the unfocused pair to the focused pair
  - b+shift (f15+shift) - copy the kerning value of the focused pair to the unfocused pair
  - y (f17) - zero the focused pair
  - (s) - save UFOs

## To load fonts
- Drag UFOs files into the bottom-right list area
- You can drag the list to adjust
- [Sort] autosorts the files.
- [Reverse] flips the order of the files. Useful when autosort is backwards.
- [Save UFOs] will save your files. Occasionally useful.
- There are some checkbox controls in the list:
  - *️⃣ Wildcard - Select which fonts are used by the transformation panel just above (romans are automatically checked, italics are automatically unchecked)
  - 🔤 Spacecenter - Open (check) or Close (uncheck) a spacecenter for this UFO
  - 🔡 Font Overview - Open (check) or Close (uncheck) the font overview for this UFO
- You can also select groups of UFOs on the list to use transformation panel just above (e.g. select the normal widths and leave condensed unselected)
- Open UFOs are automatically added (not recommended)

## To load a pairlist
- Use Metrics Machine to generate pairlists
- Click the "Load Pairlist" button or drag the file onto the top-right list area
- You can also make custom mirrored pairlists with different glyphs for the leftside-rightside and rightside-leftside pairs (useful for group kerning). e.g.:
  - H H H H
  - H O O H
  - H A A H
  - H J U H
  - H M M H
- You can use /helpers/Multikern_Pairlist_Formatter.py to turn a MM pairlist into a mirror-pair pairlist (this does some useful things like compressed groups in a way that prioritizes key glyphs and sorts pairs by the glyph order of a reference UFO)
- There were some other things in here that were useful but have been forgotten.

---

## Left Column - Global Adjustments
- At the bottom of the left UI panel is useful panel for global adjustments
- It shows the glyph names of the current kerning pairs
- Clicking the arrows will nudge the kerning value in every UFO
- You can enter a numeric value in the ? box to apply it to every UFO
- Clicking the 0 will reset the kerning pair in every UFO
- Holding a modifier will apply these changes to a subset of every UFO
  - ⌘ will only effect the UFOs selected in the file list
  - ⌘⌥ will only effect the UFOs not selected in the file list
  - ⌃ will only effect the UFOs with *️⃣ Wildcard checks in the file list
  - ⌃⌥ will only effect the UFOs without *️⃣ Wildcard checks in the file list

## Left Column - Reference glyphs
- You can set reference glyphs to see their kerning values
  - To set/unset: click one of the greyed out glyph names in the global adjustments panel and type in the name of a reference glyph
  - This will show you the kerning values of that reference glyph for each ufo
  - e.g.: if you're kerning 'T agrave' you can set 'a' as a reference glyph for 'agrave' and see the kerning values for 'T a'
  - If a reference glyph kerning value doesn't match, it will appear red
  - Clicking the up-triangle will copy the reference pair's kerning value to the current pair


