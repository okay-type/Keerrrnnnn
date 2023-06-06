from mojo.subscriber import Subscriber
from mojo.subscriber import registerRoboFontSubscriber, unregisterRoboFontSubscriber
from mojo.subscriber import WindowController
from vanilla import Window, TextBox
from mojo.roboFont import OpenWindow
from mojo.events import addObserver



class keydowntest(WindowController):

    debug = True

    def build(self):
        print('build keydowntest WindowController')
        self.w = Window((200,200), 'keydowntest')
        self.w.t = TextBox((0,0,-0,-0), '-')
        self.w.open()
        addObserver(self, "keyDown", "keyDown")

    def started(self):
        Tool.controller = self
        registerRoboFontSubscriber(Tool)

    def destroy(self):
        unregisterRoboFontSubscriber(Tool)
        Tool.controller = None

    def keyDown(self, event):
        print('keyDown')
        # keycode = event.keyCode()
        self.w.t.set('?')



class Tool(Subscriber):

    debug = True
    controller = None

    def build(self):
        print('build Subscriber Tool')

    def destroy(self):
        print('destroy Subscriber Tool')

    def keyDown(self, event):
        print('keyDown 2')
        # keycode = event.keyCode()



OpenWindow(keydowntest)
