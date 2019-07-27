import sys

# Used by zhuyin_syllable_to_ipa


def _str_get(str_, pos):
    return len(str_) > pos and str_[pos] or ''

_TONE_PREFIX = '0'

_BOPOMOFO_TONE_LIST = {
    '': "1",
    u'\u02C9': '1',  # 'ˉ'
    u'\u02CA': '2',  # 'ˊ'
    u'\u02C7': '3',  # 'ˇ'
    u'\u02CB': '4',  # 'ˋ'
    u'\u02D9': '5',  # '˙'
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



def zhuyin_syllable_to_ipa(zhuyin, dialect=None, variant=None):
    """
    Convert a zhuyin syllable to IPA. \n
    Side effect: IO (w)
    """
    offset = 0

    # Handle neutral tone
    tone = _BOPOMOFO_TONE_LIST.get(_str_get(zhuyin, offset), '')
    if tone:
        if tone == '5':
            tone = '0'

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
        return (initial, f'?{_TONE_PREFIX}{tone}')
    return (initial, f'{final}{_TONE_PREFIX}{tone}')
