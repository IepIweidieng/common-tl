import re
import segmentation as TLseg
# Pinyin != Zhuyin

chinese = TLseg.chinese
chinese_zhuyin = TLseg.chinese_zhuyin

# Converts a zhuyin syllable to IPA
def zhuyinWord_to_commonIPA(zhuyin):
    def get(str, pos):
        return len(str) > pos and str[pos] or ''

    def isBopomofo(ch):
        return u'\u3105' <= ch <= u'\u3129'  # 'ㄅ' ~ 'ㄩ'

    bopomofoToneList = {
        ''       : "01",
        u'\u02C9': '01',  # 'ˉ'
        u'\u02CA': '02',  # 'ˊ'
        u'\u02C7': '03',  # 'ˇ'
        u'\u02CB': '04',  # 'ˋ'
        u'\u02D9': '05',  # '˙'
    }

    offset = 0
    tone = bopomofoToneList.get(get(zhuyin, offset), '')
    if tone != '':
        if tone == '05':
            tone = '00'

        offset = 1


    bopomofoInitial = get(zhuyin, offset)
    initial = {
        'ㄅ': 'p'  , 'ㄉ': 't'  ,                          'ㄍ': 'k'  ,
        'ㄆ': 'pʰ' , 'ㄊ': 'tʰ' ,                          'ㄎ': 'kʰ' ,
        'ㄇ': 'm'  , 'ㄋ': 'n'  ,
                     'ㄌ': 'l'  ,
                     'ㄗ': 'ts' , 'ㄓ': 'ʈʂ' , 'ㄐ': 'tɕ' ,
                     'ㄘ': 'tsʰ', 'ㄔ': 'ʈʂʰ', 'ㄑ': 'tɕʰ',
        'ㄈ': 'f'  , 'ㄙ': 's'  , 'ㄕ': 'ʂ'  , 'ㄒ': 'ɕ'  , 'ㄏ': 'x'  ,
                                  'ㄖ': 'ʐ'  ,
    }.get(bopomofoInitial, '')

    if initial != '':
        offset += 1
    else:
        bopomofoInitial = ''


    bopomofoMedial = get(zhuyin, offset)
    medial = {'ㄧ': 1, 'ㄨ': 2, 'ㄩ': 3}.get(bopomofoMedial, 0)

    if medial != 0:
        offset += 1
    else:
        bopomofoMedial = ''


    bopomofoRhyme = get(zhuyin, offset)
    rhyme = {
        'ㄦ': 0,
        'ㄛ': 1, 'ㄜ': 1, 'ㄝ': 1,
        'ㄟ': 2, 'ㄡ': 3, 'ㄣ': 4, 'ㄥ': 5,
        'ㄚ': 6, 'ㄞ': 7, 'ㄠ': 8, 'ㄢ': 9, 'ㄤ': 10,
    }.get(bopomofoRhyme, None)

    if rhyme != None:
        offset += 1
    else:
        bopomofoRhyme = ''
        rhyme = 0

    f00 = {
        'ts': 'ɹ', 'tsʰ': 'ɹ', 's': 'ɹ',
        'ʈʂ': 'ɻ', 'ʈʂʰ': 'ɻ', 'ʂ': 'ɻ', 'ʐ': 'ɻ',
    }.get(initial, 'ə')

    f010 = {
        'p': 'wo', 'pʰ': 'wo', 'm': 'wo',
    }.get(initial, 'o')

    f05 = {
        'p': 'ʊŋ', 'pʰ': 'ʊŋ', 'm': 'ʊŋ', 'f': 'ʊŋ',
    }.get(initial, 'əŋ')

    f25 = initial and 'ʊŋ' or 'wəŋ'

    finalList = [
    # Nucleus ∅     /ə/                                             /a/
    # Coda    ∅       /o/   /ɤ/   /e/    /i/    /u/    /n/    /ŋ/     ∅     /i/    /u/    /n/    /ŋ/
    # Medial
            [f00  , [f010, 'ɤ' , 'e' ], 'ei' , 'ou' , 'ən' , f05  , 'a'  , 'ai' , 'au' , 'an' , 'aŋ' ],
            ['i'  , ['jo', None, 'je'], None , 'jou', 'in' , 'iŋ' , 'ja' , 'jai', 'jau', 'jɛn', 'jaŋ'],
            ['u'  , ['wo', None, None], 'wei', None , 'wən', f25  , 'wa' , 'wai', None , 'wan', 'waŋ'],
            ['y'  , [None, None, 'ɥe'], None , None , 'yn' , 'jʊŋ', None , None , None , 'ɥɛn', None ],
    ]

    final = finalList[medial][rhyme]

    if type(final) == list:
        final = final[{
            'ㄛ': 0, 'ㄜ': 1, 'ㄝ': 2,
        }.get(bopomofoRhyme)]



    bopomofoSuffix = get(zhuyin, offset)
    if bopomofoSuffix  == 'ㄦ':
        bopomofoSuffixTone = get(zhuyin, offset + 1)
    else:
        bopomofoSuffixTone = bopomofoSuffix
        bopomofoSuffix = get(zhuyin, offset + 1)

    if bopomofoSuffixTone in bopomofoToneList:
        offset += 1


    if bopomofoSuffix == 'ㄦ' or bopomofoRhyme == 'ㄦ':
        f010 = {
            'p': 'wo˞', 'pʰ': 'wo˞', 'm': 'wo˞',
        }.get(initial, 'o˞')

        f05 = {
            'p': 'ʊ̃˞', 'pʰ': 'ʊ̃˞', 'm': 'ʊ̃˞', 'f': 'ʊ̃˞',
        }.get(initial, 'ɚ̃')

        f25 = initial and 'ʊ̃˞' or 'wɚ̃'

        finalList = [
        # Nucleus ∅     /ə/                                                /a/
        # Coda    ∅       /o/    /ɤ/    /e/     /i/    /u/    /n/    /ŋ/     ∅     /i/    /u/    /n/    /ŋ/
        # Medial
                ['ɚ'  , [f010 , 'ɤ˞' , 'eɚ' ], 'ɚ'  , 'ou˞', 'ɚ'  , f05  , 'aɚ' , 'aɚ' , 'au˞' , 'aɚ' , 'ãɚ̃' ],
                ['jɚ' , ['jo˞', 'jɚ' , 'jeɚ'], None , 'jou', 'jɚ' , 'jɚ̃' , 'jaɚ', 'jaɚ', 'jau˞', 'jɐɚ', 'jãɚ̃'],
                ['u˞' , ['wo˞', 'wɚ' , None ], 'wɚ' , None , 'ʊ˞' , f25  , 'waɚ', 'waɚ', None  , 'waɚ', 'wãɚ̃'],
                ['ɥɚ' , [None , 'ɥɚ' , 'ɥeɚ'], None , None , 'ɥɚ' , 'jʊ̃˞' , None , None , None  , 'ɥɐɚ', None ],
        ]

        final = finalList[medial][rhyme] or ''

        if type(final) == list:
            final = final[{
                'ㄛ': 0, 'ㄜ': 1, 'ㄝ': 2,
            }.get(bopomofoRhyme)]

        offset += 1

    if tone == '':
        tone = bopomofoToneList[bopomofoSuffixTone]

    return initial + (final or '') + tone

# Converts an IPA syllable to commonized TL
def commonIPA_to_commonTL(ipa, useOr = False):
    tl = ''
    afterIY = False
    lastNN = -1
    lastRR = -1

    for i, ipaPhone in enumerate(ipa):
        tlPhone = {
            # IPA consonants.
            'd': ''  ,  # TL "j" is pronounced as [dz] in Taiwanese Choân-chiu accent
                        # always followed by [z] or [ʑ]; just drop it
            'z': 'j' ,  # TL "j" is pronounced as [z] in Taiwanese Chiang-chiu accent

            'ʈ': 't' ,  # rhotic consonant; always followed by [ʂ]
            'ʂ': 'sr',  # rhotic consonant
            'ʐ': 'jr',  # rhotic consonant

            'ɕ': 's' ,  # an allophone of TL "s"
            'ʑ': 'j' ,  # an allophone of TL "j"
            'x': 'h' ,  # Taiwanese Mandarin "ㄏ" can be pronounced as either [x] or [h].

            'ȵ': 'gn',  # used in Taiwanese Chiang-chiu accent.
            'ŋ': 'ng',

            'ʰ': 'h' ,

            'ʔ': 'h' ,  # as coda; not used as initial for now.

            # Also IPA consonants. Semi-vowel part.
            'j': 'i',
            'w': 'u',
            'ɥ': 'y',   # Use only the vowel characters.

            # IPA vowels.
            'ɨ': 'ir',  # used in Taiwanese Choân-chiu accent

            'ɹ': 'ir',  # Also writen as "ɯ" in IPA sometimes.
            'ɻ': 'ir',  # Also writen as "ɨ" in IPA sometimes.
                        # They are allophones. Let's use only one symbol for them.

            'ɘ': 'er',  # used in Taiwanese Choân-chiu accent

            'ɤ': useOr
             and 'or'   # for Taiwanese northern accent
             or  'o' ,  # for Taiwanese southern accent
            'ə': useOr
             and 'or'
             or  'o' ,
                        # They are allophones. Let's use only one symbol for them.

            'ʊ': useOr
             and 'o'    # more accurate transcription for Taiwanese northern accent
             or  'oo',

            'ɔ': 'oo',

            'ɛ': afterIY
             and 'a'    # produced by bopomofo finals "ㄧㄢ" and "ㄩㄢ"
                        # In TL, the "a" in "-ian", "-iat" also are pronounced as [ɛ].
                        # For now, just leave it as is.
             or  'ee',  # used in Taiwanese Chiang-chiu accent

            # Still IPA vowels. Erization-related part.
            'ɚ': 'orr',  # See u'\u02DE'.
            'ɐ': 'a'  ,  # produced by rhotic bopomofo finals "ㄧㄢㄦ" and "ㄩㄢㄦ"

            # IPA symbols.
            u'\u0303': 'nn',  # ' ̃ '; vowel nasalization
            u'\u02DE': 'rr',  # ' ˞ '; erization
                              # Alternatives:
                              #   rh:  from Wade–Giles Romanization system for Mandarin Chinese
                              #        causes ambiguity, e.g., "orh" as either "o -rh" or "or -h".
                              #   rr:  digraph
                              #        doesn't cause ambiguity, e.g., "orr" as "o -rr".
                              #        seems cumbersome sometimes, e.g., "orrr" as "or -rr".

            u'\u031A': ''  ,  # ' ̚ '; unreleased plosive, which is used in entering tones (入聲)
                              # Just drop it.
        }.get(ipaPhone, ipaPhone)

        if tlPhone == 'i' or tlPhone == 'y':
            afterIY = True

        if tlPhone[-2:] == 'nn':
            if lastNN != -1:
                tl = tl[:lastNN] + tl[lastNN+2:]
                if lastRR > lastNN:  lastRR -= 2
            lastNN = len(tl) + len(tlPhone) - 2
            if lastRR != -1:
                tl = tl[:lastRR] + 'nn' + tl[lastRR+2:] + 'rr'
                if lastNN > lastRR:  lastNN -= 2
                lastRR = -1
                continue

        if tlPhone[-2:] == 'rr':
            if lastRR != -1:
                tl = tl[:lastRR] + tl[lastRR+2:]
                if lastNN > lastRR:  lastNN -= 2
            lastRR = len(tl) + len(tlPhone) - 2

        tl += tlPhone

    return tl

#中文辭典檔前處理
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

#依照中文辭典檔轉成中文注音
def chinese_to_zhuyin(word):
    zhuyin = ''

    for item in enumerate(chinese):
        if item[1] == word:
            zhuyin = chinese_zhuyin[item[0]] + '\t'
            break

    return zhuyin[:-1].split('\t')

#將中文注音轉成國際音標
def zhuyinWord_to_IPA(zhuyin):
    if zhuyin == '':
        return ''

    ipa = ''
    zhuyinSyllables = zhuyin.replace('　', ' ').split(' ')
    for syllable in zhuyinSyllables:
        ipa += zhuyinWord_to_commonIPA(syllable) + ' '

    return ipa[:-1]

#將國際音標轉成台羅拼音
def IPAWord_to_TL(ipa):
    if ipa == '':
        return ''

    tl = ''
    ipaSyllables = ipa.split(' ')
    for syllable in ipaSyllables:
        tl += commonIPA_to_commonTL(syllable) + ' '

    return tl[:-1]


if __name__ == '__main__':
    TLseg.createDict('chinese_dict.txt_out')
    sentence = '''
測 試  這        兒 捧  日 心 拔 了 一 個 尖  兒 隔  牆 掠 見腔  兒 皮 靴 兒   沒番 正  不的 個   風 兒 就  雨兒 打   通 兒
'''
    wordsOfSentence = TLseg.taiwanese_split(sentence)

    output = ''
    for word in wordsOfSentence:
        output += word + '\t'

        candidateZhuyinWord = chinese_to_zhuyin(word)
        for zhuyinWord in candidateZhuyinWord:
            ipaWord = zhuyinWord_to_IPA(zhuyinWord)
            output += zhuyinWord + '\t' and ''
            output += ipaWord + '\t' and ''
            output += IPAWord_to_TL(ipaWord) + '\t'
        output += '\n'

    print(output[:-1])
    print('main done!')
