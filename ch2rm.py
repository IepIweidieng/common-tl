import sys

import tl_split
from tl_split import tl_dict

# Used by zhuyin_syllable_to_ipa


def _str_get(str_, pos):
    return len(str_) > pos and str_[pos] or ''


_BOPOMOFO_TONE_LIST = {
    '': "01",
    u'\u02C9': '01',  # 'ˉ'
    u'\u02CA': '02',  # 'ˊ'
    u'\u02C7': '03',  # 'ˇ'
    u'\u02CB': '04',  # 'ˋ'
    u'\u02D9': '05',  # '˙'
}

_BOPOMOFO_INITIAL_LIST = {
    'ㄅ': 'p',  'ㄉ': 't',                             'ㄍ': 'k',
    'ㄆ': 'pʰ', 'ㄊ': 'tʰ',                            'ㄎ': 'kʰ',
    'ㄇ': 'm',  'ㄋ': 'n',
                'ㄌ': 'l',
                'ㄗ': 'ts',  'ㄓ': 'ʈʂ',  'ㄐ': 'tɕ',
                'ㄘ': 'tsʰ', 'ㄔ': 'ʈʂʰ', 'ㄑ': 'tɕʰ',
    'ㄈ': 'f',  'ㄙ': 's',   'ㄕ': 'ʂ',   'ㄒ': 'ɕ',   'ㄏ': 'x',
                'ㄖ': 'ʐ',
}

_BOPOMOFO_MEDIAL_LIST = {'ㄧ': 1, 'ㄨ': 2, 'ㄩ': 3}

_BOPOMOFO_RHYME_LIST = {
    'ㄦ': 0,
    'ㄛ': 1, 'ㄜ': 1, 'ㄝ': 1,
    'ㄟ': 2, 'ㄡ': 3, 'ㄣ': 4, 'ㄥ': 5,
    'ㄚ': 6, 'ㄞ': 7, 'ㄠ': 8, 'ㄢ': 9, 'ㄤ': 10,
}


def _f00(initial):
    return {
        'ts': 'ɹ', 'tsʰ': 'ɹ', 's': 'ɹ',
        'ʈʂ': 'ɻ', 'ʈʂʰ': 'ɻ', 'ʂ': 'ɻ', 'ʐ': 'ɻ',
    }.get(initial, 'ə')


def _f010(initial):
    return {
        'p': 'wo', 'pʰ': 'wo', 'm': 'wo',
    }.get(initial, 'o')


def _f05(initial):
    return {
        'p': 'ʊŋ', 'pʰ': 'ʊŋ', 'm': 'ʊŋ', 'f': 'ʊŋ',
    }.get(initial, 'əŋ')


def _f25(initial): return initial and 'ʊŋ' or 'wəŋ'


_FINAL_LIST = (
# Nucleus ∅    /ə/                                             /a/
# Coda    ∅     /o/    /ɤ/   /e/    /i/    /u/    /n/    /ŋ/    ∅    /i/    /u/    /n/    /ŋ/
# Medial
        (_f00, (_f010, 'ɤ',  'e'),  'ei',  'ou',  'ən',  _f05, 'a',  'ai',  'au',  'an',  'aŋ'),
        ('i',  ('jo',  None, 'je'), None,  'jou', 'in',  'iŋ', 'ja', 'jai', 'jau', 'jɛn', 'jaŋ'),
        ('u',  ('wo',  None, None), 'wei', None,  'wən', _f25, 'wa', 'wai', None,  'wan', 'waŋ'),
        ('y',  (None,  None, 'ɥe'), None,  None,  'yn', 'jʊŋ', None, None,  None,  'ɥɛn', None),
)


def _r010(initial):
    return {
        'p': 'wo˞', 'pʰ': 'wo˞', 'm': 'wo˞',
    }.get(initial, 'o˞')


def _r05(initial):
    return {
        'p': 'ʊ̃˞', 'pʰ': 'ʊ̃˞', 'm': 'ʊ̃˞', 'f': 'ʊ̃˞',
    }.get(initial, 'ɚ̃')


def _r25(initial): return initial and 'ʊ̃˞' or 'wɚ̃'


_RHOTIC_FINAL_LIST = (
# Nucleus ∅    /ə/                                            /a/
# Coda    ∅     /o/    /ɤ/   /e/     /i/   /u/    /n/   /ŋ/    ∅     /i/    /u/    /n/    /ŋ/
# Medial
        ('ɚ',  (_r010, 'ɤ˞',  'eɚ'),  'ɚ',  'ou˞',  'ɚ',  _r05, 'aɚ',  'aɚ',  'au˞',  'aɚ',  'ãɚ̃'),
        ('jɚ', ('jo˞',  'jɚ', 'jeɚ'), None, 'jou', 'jɚ', 'jɚ̃', 'jaɚ', 'jaɚ', 'jau˞', 'jɐɚ', 'jãɚ̃'),
        ('u˞',  ('wo˞ ', 'wɚ', None), 'wɚ',  None,  'ʊ˞',  _r25, 'waɚ', 'waɚ', None,  'waɚ', 'wãɚ̃'),
        ('ɥɚ', (None,  'ɥɚ', 'ɥeɚ'), None, None,  'ɥɚ', 'jʊ̃˞', None,  None,  None,  'ɥɐɚ', None),
)


def _final_branch(final, bopomofo_rhyme):
    return final[{
        'ㄛ': 0, 'ㄜ': 1, 'ㄝ': 2,
    }.get(bopomofo_rhyme)]


# Convert a zhuyin syllable to IPA.
# Side effect: IO (w)

def zhuyin_syllable_to_ipa(zhuyin):
    offset = 0

    # Handle neutral tone
    tone = _BOPOMOFO_TONE_LIST.get(_str_get(zhuyin, offset), '')
    if tone:
        if tone == '05':
            tone = '00'

        offset = 1

    bopomofo_initial = _str_get(zhuyin, offset)
    initial = _BOPOMOFO_INITIAL_LIST.get(bopomofo_initial, '')
    if initial:
        offset += 1
    else:
        bopomofo_initial = ''

    bopomofo_medial = _str_get(zhuyin, offset)
    medial = _BOPOMOFO_MEDIAL_LIST.get(bopomofo_medial, 0)
    if medial:
        offset += 1
    else:
        bopomofo_medial = ''

    bopomofo_rhyme = _str_get(zhuyin, offset)
    rhyme = _BOPOMOFO_RHYME_LIST.get(bopomofo_rhyme, None)
    if rhyme is not None:
        offset += 1
    else:
        bopomofo_rhyme = ''
        rhyme = 0

    final = _FINAL_LIST[medial][rhyme]
    if isinstance(final, tuple):
        final = _final_branch(final, bopomofo_rhyme)
    if callable(final):
        final = final(initial)

    # Handle the character after the final: tone or erization 'ㄦ'
    bopomofo_suffix = _str_get(zhuyin, offset)
    if bopomofo_suffix == 'ㄦ':
        bopomofo_suffix_tone = _str_get(zhuyin, offset + 1)
    else:
        bopomofo_suffix_tone = bopomofo_suffix
        bopomofo_suffix = _str_get(zhuyin, offset + 1)
    if bopomofo_suffix_tone in _BOPOMOFO_TONE_LIST:
        offset += 1

    # Process rhyme 'ㄦ' as erization 'ㄦ'
    if bopomofo_suffix == 'ㄦ' or bopomofo_rhyme == 'ㄦ':
        final = _RHOTIC_FINAL_LIST[medial][rhyme]
        if isinstance(final, tuple):
            final = _final_branch(final, bopomofo_rhyme)
        if callable(final):
            final = final(initial)

        offset += 1

    # Handle suffix tone if there is no prefix tone
    if not tone:
        tone = _BOPOMOFO_TONE_LIST[bopomofo_suffix_tone]

    if final is None:
        print('Warning: ', bopomofo_medial, bopomofo_rhyme,
              ' is invalid final bopomofo combination.  Continued.',
              sep='', file=sys.stderr, flush=True)
        return (initial, f'?{tone}')
    return (initial, f'{final}{tone}')


# Used by ipa_pair_to_tl_pair

_COMMON_TL_INITIAL_LIST = {
    # *: Not in original TL

    # IPA consonants.
    'd': '',  # TL "j" is pronounced as [dz] in Taiwanese Choân-chiu accent
    #   Always followed by [z] or [ʑ]; just drop it
    'z': 'j',  # TL "j" is pronounced as [z] in Taiwanese Chiang-chiu accent

    'ʈ': 't',  # Rhotic consonant; always followed by [ʂ]
    'ʂ': 'sr',  # * Rhotic consonant
    'ʐ': 'jr',  # * Rhotic consonant

    'ɕ': 's',  # An allophone of TL "s"
    'ʑ': 'j',  # An allophone of TL "j"
    'x': 'h',  # Taiwanese Mandarin "ㄏ" is pronounced as either [x] or [h].

    'ȵ': 'gn',  # Used in Taiwanese Chiang-chiu accent.
    'ŋ': 'ng',

    'ʰ': 'h',

    'ʔ': '',  # As initial
}

_COMMON_TL_FINAL_LIST = {
    # *: Not in original TL

    # IPA consonants.
    'ŋ': 'ng',

    'ʔ': 'h',  # As coda

    # Also IPA consonants. Semi-vowel part.
    'j': 'i',
    'w': 'u',
    'ɥ': 'y',   # * Use only the vowel characters.

    # IPA vowels.
    'ɨ': 'ir',  # Used in Taiwanese Choân-chiu accent

    'ɹ': 'ir',  # Also writen as "ɯ" in IPA sometimes.
    'ɻ': 'ir',  # Also writen as "ɨ" in IPA sometimes.
                #   They are allophones.  Use only one symbol for them.

    'ɘ': 'er',  # Used in Taiwanese Choân-chiu accent

    'ɤ': (
        'or',  # For Taiwanese northern accent
        'o'),  # For Taiwanese southern accent
    'ə': (
        'or',
        'o'),
    #   They are allophones.  Use only one symbol for them.

    'ʊ': (
        'o',  # More accurate transcription for Taiwanese northern accent
        'oo'),

    'ɔ': 'oo',

    'ɛ': 'ee',  # Used in Taiwanese Chiang-chiu accent
    # 'a'    #   The "a" in TL "-ian" and "-iat"
                #     And in the "ㄢ" of bopomofo finals "ㄧㄢ" and "ㄩㄢ"
                #     Also are pronounced as [ɛ].
                #   In these conditions, replace the 'ee' with 'a' later.

    # Still IPA vowels. Erization-related part.
    'ɚ': (
        'orrr',    # * Rhotic vowel; see u'\u02DE'.
        'orr'),

    'ɐ': 'a',  # Produced by rhotic bopomofo finals "ㄧㄢㄦ" and "ㄩㄢㄦ"

    # IPA symbols.
    u'\u0303': 'nn',  # ' ̃ '; vowel nasalization
    u'\u02DE': 'rr',  # * ' ˞ '; vowel erization
    #  Alternatives:
    # *  rh: From Wade–Giles Romanization system for Mandarin Chinese
    #        Causes ambiguity, e.g., "orh" as either "o -rh" or "or -h".
    # *  rr: Digraph
    #        Does not cause ambiguity, e.g., "orr" as "o -rr".
    #        Seems cumbersome sometimes, e.g., "orrr" as "or -rr".
    # *  hr: Reversed version of 'rh'
    #        Does not cause ambiguity, e.g., "ohr" as "o -hr".
    #        Does not seem cumbersome, e.g., "orhr" as "or -hr".

    u'\u031A': '',  # ' ̚ '; unreleased plosive; used in entering tones
                      #   Just drop it.
}


# Side effect: prev_pos_list (rw)

def _replace_symbol(src, prev_pos_list, prev_replace_pair,
                    current_symbol, tail_replace_pair=None):
    new_src = None
    (symbol_to_remove, symbol_to_insert) = prev_replace_pair
    (target_symbol, symbol_to_append) = tail_replace_pair or prev_replace_pair

    symbol_to_remove_len = len(symbol_to_remove)
    symbol_to_insert_len = len(symbol_to_insert)
    new_src_len = len(src)

    if current_symbol.endswith(target_symbol):
        if (symbol_to_remove in prev_pos_list
                and prev_pos_list[symbol_to_remove] != -1):
            new_src = (
                f'{src[:prev_pos_list[symbol_to_remove]]}'
                f'{symbol_to_insert}'
                f'{src[prev_pos_list[symbol_to_remove] + symbol_to_remove_len:]}'
                f'{symbol_to_append}')

            new_src_len = len(new_src)

            for (symbol, pos) in prev_pos_list.items():
                if pos > prev_pos_list[symbol_to_remove]:
                    prev_pos_list[symbol] += (
                        symbol_to_insert_len - symbol_to_remove_len)

            prev_pos_list[symbol_to_remove] = -1
            if symbol_to_append:
                prev_pos_list[symbol_to_append] = (
                    new_src_len + len(current_symbol) - len(symbol_to_append))
                return new_src

        if target_symbol in prev_pos_list:
            prev_pos_list[target_symbol] = (
                new_src_len + len(current_symbol) - len(target_symbol))

    return new_src


# Convert an IPA syllable to commonized TL.

def ipa_pair_to_tl_pair(ipa_pair, use_or=False):
    (ipa_initial, ipa_final) = ipa_pair
    (tl_initial, tl_final) = ('', '')
    prev_symbol_pos = {
        'nn': -1, 'rr': -1,
        'ieen': -1, 'ieet': -1, 'yeen': -1, 'yeet': -1
    }

    for ipa_phone in ipa_initial:
        tl_phone = _COMMON_TL_INITIAL_LIST.get(ipa_phone, ipa_phone)

        tl_initial = f'{tl_initial}{tl_phone}'

    for ipa_phone in ipa_final:
        tl_phone = _COMMON_TL_FINAL_LIST.get(ipa_phone, ipa_phone)

        if isinstance(tl_phone, tuple):
            tl_phone = tl_phone[not use_or and 1 or 0]

        # Replace 'ieen' with 'ian',     'yeen' with 'yan'
        #         'ieet' with 'iat', and 'yeet' with 'yat'
        for (medial, coda) in ((medial, coda)
                               for medial in ('i', 'y') for coda in ('n', 't')):
            _replace_symbol(tl_final[:-3], prev_symbol_pos,
                            ('', ''),
                            f'{tl_final[-3:]}{tl_phone}',
                            (f'{medial}ee{coda}', ''))
            new_tl_final = _replace_symbol(tl_final[:-3], prev_symbol_pos,
                                           (f'{medial}ee{coda}',
                                            f'{medial}a'),
                                           f'{tl_final[-3:]}{tl_phone}',
                                           (f'{medial}ee{coda}', ''))
            if new_tl_final is not None:
                tl_final = new_tl_final

        # Merge multipel 'nn'
        new_tl_final = _replace_symbol(
            tl_final, prev_symbol_pos, ('nn', ''), tl_phone)
        if new_tl_final is not None:
            tl_final = new_tl_final

        # 'rr' should comes after 'nn'
        new_tl_final = _replace_symbol(
            tl_final, prev_symbol_pos, ('rr', 'nn'), tl_phone, ('nn', 'rr'))
        if new_tl_final is not None:
            tl_final = new_tl_final
            continue

        # Merge multipel 'rr'
        new_tl_final = _replace_symbol(
            tl_final, prev_symbol_pos, ('rr', ''), tl_phone)
        if new_tl_final is not None:
            tl_final = new_tl_final

        tl_final = f'{tl_final}{tl_phone}'

    return (tl_initial, tl_final)


# 依照中文詞典檔轉成中文注音
# Convert a Chinese word into Zhuyin word with the dictionary.
# Side effect: tl_dict.chinese_zhuyin (r)

def chinese_word_to_zhuyin(word):
    return tl_dict.chinese_zhuyin.get(word, [])


# 將國際音標轉成台羅拼音
# Convert an IPA initial-final pair into commonized TL initial-final pair.

def ipa_pair_to_tl(ipa_pair, use_or=False):
    return [ipa_pair_to_tl_pair(syllable, use_or) for syllable in ipa_pair]


# 將中文注音轉成國際音標
# Convert a Zhuyin word into IPA.
# Side effect: zhuyin_syllable_to_ipa: IO (w)

def zhuyin_word_to_ipa(zhuyin_word):
    return [zhuyin_syllable_to_ipa(syllable) for syllable in zhuyin_word]


# Convert a Chinese sentence to Roman.
# Side effect: tl_dict.set_dict: fileIO (rw), os (x), sys (x), pickle (x)
#                                [tl_dict.set_dict] loaded_dict (rw),
#                                chinese (rw), chinese_zhuyin (rw)
#              tl_split.split_chinese_word: tl_dict.chinese_zhuyin (r)
#              chinese_word_to_zhuyin: tl_dict.chinese_zhuyin (r)
#              zhuyin_word_to_ipa: zhuyin_syllable_to_ipa: IO (w)

def chinese_to_roman(sentence, dict_paths=['chinese_dict.txt'], use_or=False):
    tl_dict.set_dict(dict_paths)

    words_of_sentence = tl_split.split_chinese_word(sentence)

    tl_pair_list = []
    for word in words_of_sentence:
        # Currently only use the first Zhuyin of candidate Zhuyins
        candidate_zhuyin_word = chinese_word_to_zhuyin(word)[0:1]
        for zhuyin_word in candidate_zhuyin_word:
            ipa_pair_word = zhuyin_word_to_ipa(zhuyin_word)
            tl_pair_word = ipa_pair_to_tl(ipa_pair_word, use_or)

            tl_pair_list.append(tl_pair_word)

    return tl_pair_list


def _print_pairs(pairs):
    return ' '.join((''.join(pair_item) for pair_item in pairs))


# Side effect: IO (w)
# Side effect: tl_dict.set_dict: fileIO (rw), os (x), sys (x), pickle (x)
#                                [tl_dict.set_dict] loaded_dict (rw),
#                                chinese (rw), chinese_zhuyin (rw)
#              tl_split.split_chinese_word: tl_dict.chinese_zhuyin (r)
#              chinese_word_to_zhuyin: tl_dict.chinese_zhuyin (r)
#              zhuyin_word_to_ipa: zhuyin_syllable_to_ipa: IO (w)

def main():
    tl_dict.set_dict(['chinese_dict.txt'])
    use_or = False

    sentence = (
        ' 測 試  這   兒 巴  陵郡  日zZㄈ=心  謗腹非 拔 了一 個 尖  兒八   面圓  通 '
        '描  樣 兒  撥魚   兒打   通   兒  '
    )
    words_of_sentence = tl_split.split_chinese_word(sentence)

    tl_pair_list = []
    output = ''
    for word in words_of_sentence:
        output = f'{output}{word}\t'

        # Currently only use the first Zhuyin of candidate Zhuyins
        candidate_zhuyin_word = chinese_word_to_zhuyin(word)[0:1]
        for zhuyin_word in candidate_zhuyin_word:
            ipa_pair_word = zhuyin_word_to_ipa(zhuyin_word)
            tl_pair_word = ipa_pair_to_tl(ipa_pair_word, use_or)
            output = (
                f'{output}'
                f'{" ".join(zhuyin_word)}\t'
                f'{_print_pairs(ipa_pair_word)}\t'
                f'{_print_pairs(tl_pair_word)}\t')

            tl_pair_list.append(tl_pair_word)
        output = f'{output}\n'

    print(output)
    print(tl_pair_list)
    print('main done!')


if __name__ == '__main__':
    main()
