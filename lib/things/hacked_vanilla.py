from vanilla import Button
from mojo.UI import NumberEditText
from vanilla import EditText
from vanilla import TextBox
from AppKit import NSColor, NSTextAlignmentRight, NSTextAlignmentCenter, NSTextAlignmentLeft

class okButton(Button):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        super(okButton, self).__init__(*args, **kwargs)
        ns = self.getNSButton()
        self._nsObject.setBordered_(False)


class okNumberEditText(NumberEditText):
    def __init__(self, *args, **kwargs):
        self.i = kwargs['i']
        del kwargs['i']
        align = kwargs['align']
        del kwargs['align']
        super(okNumberEditText, self).__init__(*args, **kwargs)
        ns = self.getNSTextField()
        ns.setBordered_(False)
        ns.setFocusRingType_(1)
        ns.setBackgroundColor_(NSColor.clearColor())
        if align == 'center':
            ns.setAlignment_(NSTextAlignmentCenter)


class okEditText(EditText):
    def __init__(self, *args, **kwargs):
        self.align = kwargs['align']
        del kwargs['align']
        super(okEditText, self).__init__(*args, **kwargs)
        ns = self.getNSTextField()
        ns.setBordered_(False)
        ns.setFocusRingType_(1)
        ns.setBackgroundColor_(NSColor.clearColor())
        if self.align == 'center':
            ns.setAlignment_(NSTextAlignmentCenter)
        elif self.align == 'right':
            ns.setAlignment_(NSTextAlignmentRight)


class okTextBox(TextBox):
    def __init__(self, *args, **kwargs):
        align = kwargs['align']
        del kwargs['align']
        super(okTextBox, self).__init__(*args, **kwargs)
        ns = self.getNSTextField()
        if align == 'center':
            ns.setAlignment_(NSTextAlignmentCenter)
        elif align == 'right':
            ns.setAlignment_(NSTextAlignmentRight)
