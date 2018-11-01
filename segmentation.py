import os

chinese = []
chinese_zhuyin = []

# 中文辭典檔前處理
def preprocess():
    inFile = open('./chinese_dict.txt', 'r+', encoding='utf8')
    outFile = open('./chinese_dict.txt_out', 'w', encoding='utf8')
    fileContent = inFile.read().splitlines()
    inFile.close()

    for line in fileContent:
        line = re.sub(r'\(.*\)', '', line)
        line = re.sub(r'（.*）', '', line)
        outFile.write(line + '\n')

    outFile.close()
    return

# 建立辭典檔
def createDict(path):
    dictFile = open(path, 'r', encoding = 'utf8')
    dictContent = dictFile.read().splitlines()
    dictFile.close()

    for phrase in dictContent:
        phraseParts = phrase.split('\t')
        chinese.append(phraseParts[0])
        chinese_zhuyin.append(phraseParts[1])

    return

def isRomanOnly(text):
    # Usage and result: isRomanOnly('abc') == True, isRomanOnly('我abc') == False
    for char in text:
        if not ((r'A' <= char <= r'Z') or (r'a' <= char <= r'z')
             or (r'0' <= char <= r'9') or (char == r'-')
             or (r'\u00C0' <= char <= r'\u1EFF')
             or (r'\u2C60' <= char <= r'\u2C7D')
             or (r'\uA720' <= char <= r'\uA78C')
             or (r'\uA7FB' <= char <= r'\uA7FF')
             or (r'\uFB00' <= char <= r'\uFB06')):

            return False

    return True

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

# 有空白的都併在一起然後斷詞
def taiwanese_split_binary_search(sentence):
    spiltedStrs = []
    mergedStrs = merge(sentence)
    debugCount = 0

    for sentence in mergedStrs:
        strLen = len(sentence)
        wordOffset = 0
        while wordOffset < strLen:
            maxWordBound = strLen - wordOffset
            possibleChinese = lambda: (phrase for phrase in chinese if len(phrase) <= maxWordBound)

            # binary search
            lBound = 1
            rBound = maxWordBound
            wordBound = (lBound + rBound + 1) // 2

            while 1 < wordBound <= maxWordBound:
                if wordBound < maxWordBound  and  sentence[wordOffset : wordOffset + wordBound + 1] in chinese:
                    lBound = min(wordBound + 1, rBound)
                elif sentence[wordOffset : wordOffset + wordBound] in chinese:
                    break
                else:
                    rBound = max(wordBound - 1, lBound)

                wordBound = (lBound + rBound) // 2
            else:
                lBound = 1
                rBound = maxWordBound
                wordBound = (lBound + rBound + 1) // 2

                while wordBound <= maxWordBound:
                    if wordBound < maxWordBound  and  isRomanOnly(sentence[wordOffset : wordOffset + wordBound + 1]):
                        lBound = min(wordBound + 1, rBound)
                    elif isRomanOnly(sentence[wordOffset : wordOffset + wordBound]):
                        break
                    elif wordBound <= 1:
                        wordBound = 1
                        break
                    else:
                        rBound = max(wordBound - 1, lBound)

                    wordBound = (lBound + rBound) // 2

            spiltedStrs.append(sentence[wordOffset : wordOffset + wordBound])
            wordOffset += wordBound

    return spiltedStrs

# 斷詞程式
# 將中羅併在一起羅羅分開
#   ^^^^  wut
def merge(sentence):
    mergedStrs = []
    words = sentence.strip().split(' ')
    mergedWords = ''
    isLastWordRoman = False
    for wordItem in words:
        if wordItem != '':
            # 代表全羅馬字
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
    if os.path.isfile(path)  and  os.path.splitext(path) == '.trn':
        trnFile = open(path, 'r+', encoding = 'utf8', newline = '\n')
        trnContent = trnFile.read().splitlines()
        srcWords = taiwanese_split(trnContent[0])
        trnFile.truncate(0)
        trnFile.seek(0)
        isFirstWord = False
        for word in srcWords:
            if isFirstWord:
                trnFile.write(' ' + word)
            else:
                isFirstWord = True
                trnFile.write(word)

        trnFile.write('\n' + trnContent[1] + '\n' + trnContent[2])
        trnFile.close()

# Usage: split_for_each_file(path_to_the_folder)
# Example: split_for_each_file("/home/thh101u/Desktop/333_sentence_trn0629/")
# 資料夾下的 trn 重新斷詞
def split_for_each_file(path = ''):
    truePath = os.path.join(os.curdir, path)

    for subpath in os.listdir(truePath):
        trueSubpath = os.path.join(truePath, subpath)
        if os.path.isdir(trueSubpath):
            for subfile in os.listdir(trueSubpath):
                split_file(os.path.join(trueSubpath, subfile))
        else:
            split_file(trueSubpath)

    print("Split for each file done!")
    return

if __name__ == '__main__':
    createDict("chinese_dict.txt_out")

    import time

    t0 = time.clock()
    print(taiwanese_split('你 是 鬱tiau5誰 a2 無a7好 se ven 買 泡 麵 和 感 心 測試'))

    t1 = time.clock()
    print(t1 - t0)

    t1 = time.clock()
    print(taiwanese_split_binary_search('你 是 鬱tiau5誰 a2 無a7好 se ven 買 泡 麵 和 感 心 測試'))

    t2 = time.clock()
    print(t2 - t1)

    print("Done!")
