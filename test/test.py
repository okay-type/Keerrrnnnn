from importlib import reload

from things import data
reload(data)
from things import data

print(data.extension_key)
print(data.openclose_pairs)



from things import hacked_vanilla
reload(hacked_vanilla)
from things.hacked_vanilla import okButton
from things.hacked_vanilla import okNumberEditText
from things.hacked_vanilla import okEditText
from things.hacked_vanilla import okTextBox

print(okButton)
print(okNumberEditText)
print(okNumberEditText)
print(okEditText)
print(okTextBox)



from things import helpers
reload(helpers)
from things.helpers import *

print(subtest('yo'))
print(c(1,2,3))



from things import sub
reload(sub)
from things.sub import *

class this():
    def __init__(self):
        self.x = 2
        y = sub_test(self)
        print(y)


this()
