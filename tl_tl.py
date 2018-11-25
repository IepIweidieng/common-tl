import sys

from tl_util import str_get_tone, str_get_gready


# Used by tl_syllable_to_ipa

_TL_TONE_LIST = {
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    u'\u030d': '8',
    u'\u030B': '9',  #
}

def _s(tl_medial):
    return {
        'i': 'ɕ',
    }.get(tl_medial, 's')

def _z(tl_medial):
    return {
        'i': 'ʑ',
    }.get(tl_medial, 'z')


def _INITIAL_M_BRANCH(nucleus):
    return {
        'm̩': ''
    }.get(nucleus, 'm')

def _m(tl_medial):
    return _INITIAL_M_BRANCH

def _INITIAL_NG_BRANCH(nucleus):
    return {
        'ŋ̍': ''
    }.get(nucleus, 'ŋ')

def _ng(tl_medial):
    return _INITIAL_NG_BRANCH


_TL_INITIAL_LIST = {
    'p': 'p',   't': 't',                    'k': 'k',
    'ph': 'pʰ', 'th': 'tʰ',                  'kh': 'kʰ',
    'b': 'b',   'l': 'ᵈl',                   'g': 'g',
                'dl': 'ᵈl',
    'm': _m,    'n': 'n',     'gn': 'ȵ',     'ng': _ng,
                'ts': ['t', _s],
                'tsh': ['t', _s, 'ʰ'],
                'ch': ['t', _s],
                'chh': ['t', _s, 'ʰ'],
                'dj': [('d', ''), _z],  # For Taiwanese Choân-chiu accent
                'j': [('d', ''), _z],   # For Taiwanese Chiang-chiu accent
                's': [_s],                     'h': 'h',
}

_TL_MEDIAL_LIST = {'i': 1, 'u': 2, 'er': 3, 'ir': 4}

def _A_BRANCH_MEDIAL(tl_medial):
    return {
        'i': 'ɛ'
    }.get(tl_medial, 'a')

def _A_BRANCH(tl_coda):
    return {
        'n': _A_BRANCH_MEDIAL, 't': _A_BRANCH_MEDIAL
    }.get(tl_coda, 'a')

def _O_BRANCH(tl_coda):
    return {
        'ng': 'ɔ', 'm': 'ɔ', 'p': 'ɔ', 'k': 'ɔ',
        'nn': 'ɔ', 'ⁿ': 'ɔ'
    }.get(tl_coda, ('o',    # For Taiwanese northern accent
                    'ə' ))  # For Taiwanese southern accent

def _E_BRANCH(tl_coda):
    return {
        'ng': 'ɛ', 'k': 'ɛ'
    }.get(tl_coda, 'e')

def _I_BRANCH(tl_coda):
    return {
        'ng': 'iə', 'k': 'iə'
    }.get(tl_coda, 'i')

def _NULL_NUCLEUS_BRANCH_INITIAL(tl_initial):
    return {
        'ng': 'ŋ̍', 'm': 'm̩'
    }.get(tl_initial, '')

def _NULL_NUCLEUS_BRANCH_MEDIAL(tl_medial):
    return _NULL_NUCLEUS_BRANCH_INITIAL

def _NULL_NUCLEUS_BRANCH(tl_coda):
    return {
        'ng': 'ŋ̍', 'm': 'm̩'
    }.get(tl_coda, _NULL_NUCLEUS_BRANCH_MEDIAL)


_TL_NUCLEUS_LIST = {
    'a': _A_BRANCH,
    'e': _E_BRANCH,
    'ee': 'ɛ',  # Used in Taiwanese Chiang-chiu accent
    'or': 'ə',
    'o': _O_BRANCH,
    'oo': 'ɔ',
    'o͘': 'ɔ',
    'i': _I_BRANCH,
    'u': 'u',
    'er': 'ɘ',  # Used in Taiwanese Choân-chiu accent
    'ir': 'ɨ',  # Used in Taiwanese Choân-chiu accent
}


_IPA_NASALIZATION = u'\u0303'  # ' ̃ '

def _CODA_M_BRANCH(nucleus):
    return {
        'm̩': ''
    }.get(nucleus, 'm')

def _CODA_NG_BRANCH(nucleus):
    return {
        'ŋ̍': ''
    }.get(nucleus, 'ŋ')


_TL_CODA_LIST = {
    'm': _CODA_M_BRANCH, 'n': 'n', 'ng': _CODA_NG_BRANCH,
    'p': 'p̚', 't': 't̚', 'k': 'k̚', 'h': 'ʔ',
    'nn': '',   # Nasalize the former vowels
    'nnh': 'ʔ'  # Nasalize the former vowels and then append a 'ʔ'
}

'''
_FINAL_LIST = (
				[m]	[n]	[ŋ]	[p̚]	[t̚]	[k̚]	[ʔ]
[a] 	a	ann	am	an	ang	ap	at	ak	ah	annh
[aɪ]	ai	ainn							aih	ainnh
[aʊ]	au								auh
[e] 	e	enn							eh	ennh
[i] 	i	inn	im	in	'ing'	ip	it	'ik'	ih	innh
[ɪa]	ia	iann	iam	'ian'	iang	iap	'iat'	iak	iah	iannh
[ɪaʊ]	iau	iaunn							iauh
[ɪə]	io								ioh
[ɪɔ]					'iong'			'iok'
[iu]	iu	iunn							iuh	iunnh
[ə] 	o								oh
[ɔ] 	oo	'onn'	'om'		'ong'	'op'		'ok'	ooh	'onnh'
[u] 	u			un			ut		uh
[ua]	ua	uann		uan			uat		uah
[uai]	uai	uainn
[ue]	ue								ueh
[ui]	ui
)'''


def tl_syllable_to_ipa(tl_, use_north=False, use_choan=False):
    """
    Convert a TL syllable to IPA. \n
    Side effect: IO (w)
    """

    (tone, tl_no_tone) = str_get_tone(tl_, _TL_TONE_LIST, 1)

    offset = 0

    (tl_initial, offset, initial) = str_get_gready(
        tl_no_tone, offset, _TL_INITIAL_LIST, '')

    (tl_medial, offset, medial) = str_get_gready(
        tl_no_tone, offset, _TL_MEDIAL_LIST, 0)
    medial = _TL_NUCLEUS_LIST.get(tl_medial, '')
    if callable(initial):
        initial = initial(tl_medial)
    if isinstance(initial, list):
        new_initial = []
        for ipa_part in initial:
            if isinstance(ipa_part, tuple):
                ipa_part = ipa_part[use_choan and 0 or 1]
            if callable(ipa_part):
                ipa_part = ipa_part(tl_medial)
            new_initial.append(ipa_part)
        initial = ''.join(new_initial)

    (tl_nucleus0, offset, nucleus0) = str_get_gready(
        tl_no_tone, offset, _TL_NUCLEUS_LIST, _NULL_NUCLEUS_BRANCH)
    (tl_nucleus1, offset, nucleus1) = str_get_gready(
        tl_no_tone, offset, _TL_NUCLEUS_LIST, '')
    if tl_nucleus0 == None and tl_medial != None:
        tl_nucleus0 = tl_medial
        tl_medial = ''
        nucleus0 = medial
        medial = ''

    (tl_coda, offset, coda) = str_get_gready(
        tl_no_tone, offset, _TL_CODA_LIST, '')

    def get_vowel(vowel):
        result = vowel
        if callable(result):
            result = result(tl_coda)
        if callable(result):
            result = result(tl_medial)
        if callable(result):
            result = result(tl_initial)
        if isinstance(result, tuple):
            result = result[use_north and 0 or 1]
        return result

    def nasalization(vowels):
        new_vowels = []
        for vowel_item in vowels:
            new_vowels.append(vowel_item)
            new_vowels.append(_IPA_NASALIZATION)
        return ''.join(new_vowels)

    medial = get_vowel(medial)
    nucleus0 = get_vowel(nucleus0)
    nucleus1 = get_vowel(nucleus1)

    if callable(initial):
        initial = initial(nucleus0)
    if callable(coda):
        coda = coda(nucleus0)

    if tl_coda != None and tl_coda.startswith('nn'):
        medial = nasalization(medial)
        nucleus0 = nasalization(nucleus0)
        nucleus1 = nasalization(nucleus1)

    if offset != len(tl_no_tone):
        print('Warning: ', tl_, ' -> ', tl_no_tone,
              ' is an invalid TL.  Continued.',
              sep='', file=sys.stderr, flush=True)
        return (initial, f'{medial}{nucleus0}{nucleus1}{coda}?{tone}')
    return (initial, f'{medial}{nucleus0}{nucleus1}{coda}{tone}')
