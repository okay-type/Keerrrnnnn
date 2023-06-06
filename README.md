# Multikern

Robofont Multikern

Privately sharing with friends.

It's been a year since I've used this and details about how it works are fuzzy. Let's see...

The preview strings are deliberately simple
- There is a kerning pair "AB", and it's mirror "BA"
- There are very simple control strings before, between, and after the mirrored kerning pairs "HHH" "AB" "HHH" "BA" "HHH"
- There is a big(ish) text string and a smaller duplicate of this string. It's setup this way for the fonts I build this to kern. It would be a good idea to adjust them to suit the target size of your design (I'm guessing this was built in a complicated way, sorry).

Kerning limitations
- This is setup to kern in increments of 5. Not hard to change that, but WWJDD?
- Kerning exceptions are complicated and I didn't figure out how to handle them. Instead I put problematic glyphs in their own groups and used the reference glyphs (below) to keep them in line with their base glyphs. Wouldn't work for every design but it would good enough for the the font I was working on.

The control panel on the right-side is harder to explain
- The tool is intended to be used with a gaming controller
- I use enjoyable.app to turn controller button presses into keycodes
- This is all just setup for my preferences and my controller.
- You can dig through keyDown() to see the keycodes and logic
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
  - (s) - save ufos

At the bottom of the control panel is a global control
- It shows the glyph names of the current mirror pair
- You can click the arrows to adjust every ufo
- You can enter a value in the ? box to apply it to every ufo
- I don't remember what the 0 is for
- Reference glyphs:
  - If you click one of the greyed out glyph names at the bottom, you can type in the name of a reference glyph
  - This will show you the kerning values of that reference glyph for each ufo
  - e.g.: if you're kerning 'T agrave' you can set 'a' as a reference glyph for 'agrave' and see the kerning values for 'T a'
  - Clicking the up-triangle will copy that reference pair's kerning value to the current pair


To load fonts: drag ufos into the bottom-right list area.
- There are some checkbox controls:
  - *️⃣ Wildcard - Used by the kerning transformation panel just above
  - 🔤 Spacecenter - Open (or close) a spacecenter for this UFO
  - 🔡 Font Overview - Open (or close) the font overview for this UFO
- You can also select groups of ufos on the list to use transformation panel just above
- The [Sort] button autosorts the files. You can drag them to adjust. Forgot exactly how this works...
- The [Reverse] button flips the order of the files. Useful when autosort is backwards.
- [Save UFOs] will save your files. Occasionally useful.

To load a pairlist: click the "Load Pairlist" button or drag the file onto the top-right list area.
- Multikern pairlists are based on the Metrics Machine format
- You should be able to use a Metrics Machine pairlist and it will load as leftside-rightside and rightside-leftside
- You can also make pairlists with different glyphs for the leftside-rightside and rightside-leftside pairs (useful for group kerning). e.g.:
  - H H H H
  - H O O H
  - H A A H
  - H J U H
  - H M M H
- There were some other things in here that were useful but have been forgotten.

There is little adjust panel between the ufo list and the kerning list. This is for when you want to make an adjustment to groups of ufos.
- The radio buttons let you pick which group of UFOs. This can be "All" but you can also set groups two other ways:
  - "Checked" and "Unchecked" use the *️⃣ Wildcard checkboxes in the ufo list. The tool attempts to automatically check non-roman ufos and uncheck "Italic" ufos, but you can do something else.
  - "Selected" and "Unselected" use the selected state of the items in the ufo list, useful for additional design parameters like width or optical size (I would select the normal width ufos and leave condensed unselected).

