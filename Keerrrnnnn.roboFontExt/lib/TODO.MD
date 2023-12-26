

break up into manageable files
    main
        data
        ui
        adjustments
        helpers
        string builder
        vanilla subclass

make extension

ui updates
    resizeable
    fix ui changes for current mac os
    string builder ui
    get colors from robofont preferences

preferences
    set a kerning unit
    change text size
    show/hide kerning values
    show/hide right side ui

bigger issues
    undo!
    see groups somehow
        cycle glyphs
        overlay glyphs
    make exceptions

can a glyph be flagged as related to another glyph?
    Naccent ~ N => Naccent pairs are shown with N pairs
        N O O N
        N O Naccent O
        O N O Naccent


fixes
    pairlist suffix matching (one.lp => zero.lp)
    metrics adjuster ... pick which glyph
    font list
        can't see full names
        family - style - weight - width - angle - select - open overview - open spacecenter - open glyph
