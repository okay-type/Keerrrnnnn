
def subtest(x=None):
    return('subtest'+x)

def set_first_responder(ns_view):
    # set_first_responder(self.w.merzLineView.getNSView())
    # nsObject = self.w.merzLineView.getNSView()
    nsObject = ns_view
    nsObject.window().makeFirstResponder_(nsObject)

# def colorText(this, color=None):
#     ns = this.getNSButton()
#     textcolor = NSColor.grayColor()
#     if color == 'red':
#         textcolor = red
#     paragraphalignment = NSMutableParagraphStyle.alloc().init()
#     paragraphalignment.setAlignment_(2)
#     customFont = NSFont.menuBarFontOfSize_(10)
#     attributes = {}
#     attributes[NSFontAttributeName] = customFont
#     attributes[NSForegroundColorAttributeName] = textcolor
#     attributes[NSParagraphStyleAttributeName] = paragraphalignment
#     attributedText = NSAttributedString.alloc(
#     ).initWithString_attributes_(ns.title(), attributes)
#     ns.setAttributedTitle_(attributedText)

def c(c, g, no):
    # helper to make columns
    return c*no + g*no
