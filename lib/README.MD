
'''
about the tool

goal: faster kerning process without sacrificing control
- do all sources at once
- do double pairs at once

goal: more consistent kerning
- all sources simultaneously help ensure spacing is consistent throughout family
- smartly mirrored pairs help ensure spacing is consistent on symmetrical pairs
- reference glyphs help the gap between class kerning and completely separate glyph kerning

choices:
- context string should be as simple as possible
- control character spacing is the baseline for consistent kerning
- some changes make sense, control characters can differ for different chunks of glyphs

'''



'''

active indicator to left and right of text  > HHHHABHHHBAHHHH <

open glyph with double click

open string in spacecenter with groups
    string
    left group glyphs
    right group glyphs

position update doesn't update kerning of glyphs in same group
- get groups when building position data

ADD

copy all of one side to the other side
edittext flipped glyphs

if keycode == 113
- get kerning from dict first

kern dict
- does it rewrite every time
- should it cache values for longer
- max 100 pairs?

better string builder

undo

improve controls
- make pair_reverse labels edittext (so its easier to copy names out of them)
- universal zero buttons are unclear
- universal reference buttons - color red if there is a mismatch in any font?
- align rules and arrows

universal control toggle
- all ufos, all romans, all italics, all family, selected fonts, unselected fonts

reference glyphs - [left, right]

toggle kerning values in merzview
- show all
- only current
- only active
- none

link size control to drawing
- set globals
- reposition elements
- save/load as pref

filter pairlist
- find
- only show pairs with selected or searched-for glyph

see the group members of current pair

create and manage exceptions

'''
