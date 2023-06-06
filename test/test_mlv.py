from things import merzy_lineview

from importlib import reload
reload(merzy_lineview)
from things.merzy_lineview import *

from vanilla import *

class test_mlv():
    def __init__(self):
        self.w = Window((900, 600),'test_mlv')
        self.w.open()

test_mlv()
