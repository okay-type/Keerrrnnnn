'''build RoboFont Extension'''

import os
from mojo.extensions import ExtensionBundle

# get current folder
basePath = os.path.dirname(__file__)
basePath = '/Users/Ahh/Okay/Roboscripts/_Extensions/Multikern'

# source folder for all extension files
sourcePath = os.path.join(basePath, 'source')

# folder with python files
libPath = os.path.join(sourcePath, '')

# folder with html files
# htmlPath = os.path.join(sourcePath, 'documentation')
htmlPath = None

# folder with resources (icons etc)
resourcesPath = os.path.join(sourcePath, 'resources')

# load license text from file
# see choosealicense.com for more open-source licenses
# licensePath = os.path.join(basePath, 'license.txt')

# boolean indicating if only .pyc should be included
pycOnly = True

# name of the compiled extension file
extensionFile = 'Keerrrnnnn.roboFontExt'

# path of the compiled extension
buildPath = os.path.join(basePath, '')
extensionPath = os.path.join(buildPath, extensionFile)

# initiate the extension builder
B = ExtensionBundle()

# name of the extension
B.name = 'Keerrrnnnn'

# name of the developer
B.developer = 'Okay Type'

# URL of the developer
B.developerURL = 'http://github.com/okay-type'

# extension icon (file path or NSImage)
imagePath = os.path.join(resourcesPath, 'Khan.png')
B.icon = imagePath

# version of the extension
B.version = '1.0.0'

# should the extension be launched at start-up?
B.launchAtStartUp = False

# script to be executed when RF starts
B.mainScript = 'hello.py'

# does the extension contain html help files?
B.html = False

# minimum RoboFont version required for this extension
B.requiresVersionMajor = '4'
B.requiresVersionMinor = '0'

# scripts which should appear in Extensions menu
B.addToMenu = [
    {
        'path' : 'keerrrnnnn.py',
        'preferredName': 'Keerrrnnnn!',
        'shortKey' : '',
    },
]

# license for the extension
# with open(licensePath) as license:
    # B.license = license.read()
B.license = 'Friends Only'

# expiration date for trial extensions
# B.expireDate = '2019-12-31'

# compile and save the extension bundle
print('building extension...', end=' ')
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=['3.7'])
print('done!')

# check for problems in the compiled extension
print()
print(B.validationErrors())
