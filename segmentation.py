import os

chinese = []
chinese_zhuyin=[]

#建立辭典檔
def createDict(path):
    dictFile = open(path, 'r', encoding='utf8')
    dictContent = dictFile.read().splitlines()
    dictFile.close()

    for phrase in dictContent:
        phraseParts = phrase.split('\t')
        chinese.append(phraseParts[0])
        chinese_zhuyin.append(phraseParts[1])

    return

def isRomanOnly(text):
    #Usage and result: isRomanOnly('abc') == True, isRomanOnly('我abc') == False
    for char in text:
        if not (('A' <= char <= 'Z') or ('a' <= char <= 'z')
             or ('0' <= char <= '9') or (char == '-')
             or ('\u00C0' <= char <= '\u1EFF')
             or ('\u2C60' <= char <= '\u2C7D')
             or ('\uA720' <= char <= '\uA78C')
             or ('\uA7FB' <= char <= '\uA7FF')
             or ('\uFB00' <= char <= '\uFB06')):

            return False

    return True

#有空白的都併在一起然後斷詞
def taiwanese_split(sentence):
    spiltedStrs = []
    mergedStrs = merge(sentence)

    for sentence in mergedStrs:
        strlen = len(sentence)
        lBound=0
        while lBound < strlen:
            rBound = strlen
            while rBound > lBound:
                if(sentence[lBound : rBound] in chinese):
                    break
                rBound -= 1
            if lBound == rBound:
                rBound += 1
                while rBound < strlen  and  isRomanOnly(sentence[lBound : rBound + 1]):
                    rBound += 1
            spiltedStrs.append(sentence[lBound : rBound])
            lBound = rBound

    return spiltedStrs

#斷詞程式
#將中英併在一起英英分開
def merge(sentence):
    mergedStrs = []
    words = sentence.strip().split(' ')
    mergedWords = ''
    isLastWordRoman = False
    for wordItem in words:
        if wordItem == '':  continue
        #代表全英文
        if isRomanOnly(wordItem):
            if not isLastWordRoman:
                mergedWords += wordItem
                isLastWordRoman = True
            else:
                mergedStrs.append(mergedWords)
                mergedWords = wordItem
        else:
            mergedWords += wordItem
            isLastWordRoman = False
    if mergedWords != '':
        mergedStrs.append(mergedWords)

    return mergedStrs


def split_file(path):
    if os.path.isfile(path)  and  re.match('\.trn$', path) != None:
        trnFile = open(path, 'r+', encoding='utf8', newline='\n')
        text = trnFile.read().splitlines()
        srcWords = taiwanese_split(text[0])
        trnFile.truncate(0)
        trnFile.seek(0)
        isFirstWord = False
        for word in srcWords:
            if isFirstWord:
                trnFile.write(' ' + word)
            else:
                isFirstWord = True
                trnFile.write(word)

        trnFile.write('\n' + text[1] + '\n' + text[2])
        trnFile.close()

#Usage: split_for_each_file("/home/thh101u/Desktop/333_sentence_trn0629/")
#資料夾下的trn重新斷詞
def split_for_each_file(directory):
    if directory != '':
        path = directory
        if path[-1] != '/':
            path += '/'
    else:
        path = './'

    for subpath in os.listdir(path):
        if os.path.isdir(path + subpath):
            for subfile in os.listdir(path + subpath):
                split_file(subpath + i + '/' + subfile)
        else:
            split_file(path + subpath)

    print("Split for each file done!")
    return

if __name__  == '__main__':
    createDict("chinese_dict.txt_out")
    print(taiwanese_split('你 是 鬱tiau5誰 a2 無a7好 se ven 買 泡 麵 和 感 心'))

    print("Done!")
