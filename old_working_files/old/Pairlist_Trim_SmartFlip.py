from mojo.UI import GetFile
from mojo.UI import PutFile
from glyphNameFormatter import GlyphName


openclosepairs = {"‘": "’", "“": "”", "«": "»", "»": "«", "⸄": "⸅", "⸉": "⸊", "⸠": "⸡", "”": "”", "’": "’", "'": "'", '"': '"', "¡": "!", "¿": "?", "←": "→", "→": "←", "(": ")", "[": "]", "{": "}", "parenleft.sups": "parenright.sups", "parenleft.subs": "parenright.subs", "parenleft.uc": "parenright.uc", "bracketleft.uc": "bracketright.uc", "braceleft.uc": "braceright.uc", "bracketangleleft.uc": "bracketangleright.uc", "guillemetleft": "guillemetright", "guillemetleft.uc": "guillemetright.uc", "commaheavydoubleturnedornament": "commaheavydoubleornament", "parenleft.vert": "parenright.vert", "bracketleft.vert": "bracketright.vert", "braceleft.vert": "braceright.vert", "bracketangleleft.vert": "bracketangleright.vert", "guillemetleft.vert": "guillemetright.vert", "parenleft.uc.vert": "parenright.uc.vert", "bracketleft.uc.vert": "bracketright.uc.vert", "braceleft.uc.vert": "braceright.uc.vert", "bracketangleleft.uc.vert": "bracketangleright.uc.vert", "guillemetleft.uc.vert": "guillemetright.uc.vert", "less.vert": "greater.vert", "less.vert.uc": "greater.vert.uc", "<": ">", ">": "<", "less": "greater", "less.uc": "greater.uc", "༺": "༻", "༼": "༽", "᚛": "᚜", "⁅": "⁆", "⁽": "⁾", "₍": "₎", "⌈": "⌉", "⌊": "⌋", "〈": "〉", "❨": "❩", "❪": "❫", "❬": "❭", "❮": "❯", "❰": "❱", "❲": "❳", "❴": "❵", "⟅": "⟆", "⟦": "⟧", "⟨": "⟩", "⟪": "⟫", "⟬": "⟭", "⟮": "⟯", "⦃": "⦄", "⦅": "⦆", "⦇": "⦈", "⦉": "⦊", "⦋": "⦌", "⦍": "⦎", "⦏": "⦐", "⦑": "⦒", "⦓": "⦔", "⦕": "⦖", "⦗": "⦘", "⧘": "⧙", "⧚": "⧛", "⧼": "⧽", "⸢": "⸣", "⸤": "⸥", "⸦": "⸧", "⸨": "⸩", "〈": "〉", "《": "》", "「": "」", "『": "』", "【": "】", "〔": "〕", "〖": "〗", "〘": "〙", "〚": "〛", "〝": "〞", "⹂": "〟", "﴿": "﴾", "︗": "︘", "︵": "︶", "︷": "︸", "︹": "︺", "︻": "︼", "︽": "︾", "︿": "﹀", "﹁": "﹂", "﹃": "﹄", "﹇": "﹈", "﹙": "﹚", "﹛": "﹜", "﹝": "﹞", "（": "）", "［": "］", "｛": "｝", "｟": "｠", "｢": "｣", }

class PairListTrimSmartFlip():

    def __init__(self):

        pairlist = []
        with open(GetFile(message='Open a pairlist.txt file.'), encoding='utf-8') as userFile:
            lines = userFile.read()
            lines = lines.splitlines()
            for line in lines:
                pairlist.append(line)

        print('before filter', len(pairlist))

        cleanpairs = []
        for pair in pairlist:
            if pair[:0] != '#' and pair.count(' ') == 1:
                pair = pair.split(' ')
                if pair not in cleanpairs:
                    if self.reversePairSmart(pair) not in cleanpairs:
                        cleanpairs.append(pair)

        print('after filter', len(cleanpairs))

        with open(PutFile(message="Save Pairlist:"), 'w') as newfile:
            newfile.write('#KPL:P: My Pair List' + '\n')
            for pair in cleanpairs:
                line = str(pair[0]) + ' ' +str(pair[1]) + '\n'
                newfile.write(line)

    def reversePairSmart(self, pair):
        left = self.asGlyphName(pair[0])
        right = self.asGlyphName(pair[1])
        flippedPair = [right, left]
        for openclosepair in openclosepairs.items():
            if flippedPair[0] == self.asGlyphName(openclosepair[0]):
                flippedPair[0] = self.asGlyphName(openclosepair[1])
            elif flippedPair[0] == self.asGlyphName(openclosepair[1]):
                flippedPair[0] = self.asGlyphName(openclosepair[0])
            if flippedPair[1] == self.asGlyphName(openclosepair[0]):
                flippedPair[1] = self.asGlyphName(openclosepair[1])
            elif flippedPair[1] == self.asGlyphName(openclosepair[1]):
                flippedPair[1] = self.asGlyphName(openclosepair[0])
        return flippedPair

    def asGlyphName(self, character):
        if len(character) > 1:
            return character
        else:
            return GlyphName(ord(character)).getName()


PairListTrimSmartFlip()
