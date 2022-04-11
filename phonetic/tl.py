'''Phonetic notation definition
TL - Taiwanese Romanization System (臺灣閩南語羅馬字拼音方案)
'''

from typing import List, Optional, cast
from . import ctl_util
from . import phonetic
from .phonetic import Str, Part, SrcParts, IpaParts, PhoneSpec, PhoneSet, PhoneDict, PhoneCtxDict, after_initial

_PHONE_NAME = 'TL'

Dialect = ctl_util.def_dialect(
      ['chiang', 'choan'])
#       漳        泉
dialect = ctl_util.namedtuple_ctor(Dialect)

GENERAL_VARIANT_LIST: List[str] = ['southern', 'northern']
VARIANT_LIST = Dialect(
    chiang=[],
    choan=[],
)

Variant = ctl_util.def_variant(GENERAL_VARIANT_LIST, VARIANT_LIST)
variant = ctl_util.namedtuple_ctor(Variant)

_TONE_PREFIX = ''

def _NULL_TONE_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.TONE:
        return cast(PhoneDict, {
            'p': '4', 't': '4', 'k': '4', 'h': '4', 'nnh': '4',
        }).get(tl.coda[-1], '1')
    return _NULL_TONE_BRANCH

_TL_TONE_LIST: PhoneDict = {
    '0': '0', '--': '0',
    '1': '1',  # '': _NULL_TONE_BRANCH,
    '2': '2', '\u0301': '2',  # ' ́ '
    '3': '3', '\u0300': '3',  # ' ̀ '
    '4': '4',  # '': _NULL_TONE_BRANCH,
    '5': '5', '\u0302': '5',  # ' ̂ '
    '6': '6', '\u030C': '6',  # ' ̌ '
    '7': '7', '\u0304': '7',  # ' ̄ '
    '8': '8', '\u030d': '8',  # ' ̍ '
    '9': '9', '\u030B': '9',  # ' ̋ '
}

def _s(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.INITIAL:
        return cast(PhoneDict, {
            'i': 'ɕ',
        }).get(after_initial(tl), 's')
    return _s

def _z(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.INITIAL:
        return cast(PhoneDict, {
            'i': 'ʑ',
        }).get(after_initial(tl), 'z')
    return _z


_TL_INITIAL_LIST: PhoneDict = {
    'p': 'p',   't': 't',                    'k': 'k',
    'ph': 'pʰ', 'th': 'tʰ',                  'kh': 'kʰ',
    'b': 'b',   'l': 'ᵈl',                   'g': 'g',
                'dl': 'ᵈl',
    'm': 'm',   'n': 'n',     'gn': 'ȵ',     'ng': 'ng',
                'ts': ['t', _s],
                'tsh': ['t', _s, 'ʰ'],
                'ch': ['t', _s],
                'chh': ['t', _s, 'ʰ'],
                'dj': [Dialect('d', ''), _z],  # For Taiwanese Choân-chiu accent
                'j': [Dialect('d', ''), _z],   # For Taiwanese Chiang-chiu accent
                's': [_s],                     'h': 'h',
}

_TL_MEDIAL_LIST: PhoneSet = {'i', 'u', 'er', 'ir'}

def _A_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.NUCLEUS_I or self_type == phonetic.NUCLEUS_IF:
        return cast(PhoneCtxDict, {
            ('i', 'n'): 'ɛ', ('i', 't'): 'ɛ',
        }).get((tl.medial[-1], tl.coda[0]), 'a')
    return _A_BRANCH

def _O_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.NUCLEUS_I or self_type == phonetic.NUCLEUS_IF:
        return cast(PhoneDict, {
            'ng': 'ɔ', 'm': 'ɔ', 'p': 'ɔ', 'k': 'ɔ',
            'nn': 'ɔ', 'ⁿ': 'ɔ', 'nnh': 'ɔ', 'ⁿh': 'ɔ',
        }).get(tl.coda[0], variant(northern='o', southern='ə'))
    return _O_BRANCH

def _E_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.NUCLEUS_I or self_type == phonetic.NUCLEUS_IF:
        return cast(PhoneDict, {
            'ng': 'ɛ', 'k': 'ɛ'
        }).get(tl.coda[0], 'e')
    return _E_BRANCH

def _I_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if (self_type == phonetic.MEDIAL
        or self_type == phonetic.NUCLEUS_I or self_type == phonetic.NUCLEUS_F):
        return 'i'
    if self_type == phonetic.NUCLEUS_IF:
        return cast(PhoneDict, {
            'ng': 'iə', 'k': 'iə'
        }).get(tl.coda[0], 'i')
    return _I_BRANCH

def _NULL_NUCLEUS_BRANCH(self_type: Part, tl: SrcParts) -> PhoneSpec:
    if self_type == phonetic.NUCLEUS_I or self_type == phonetic.NUCLEUS_IF:
        return cast(PhoneDict, {
            'ng': 'ŋ̍', 'ngh': 'ŋ̍',
            'm': 'm̩', 'mh': 'm̩',
        }).get(tl.coda[0]) or cast(PhoneDict, {
            'ng': 'ŋ̍', 'm': 'm̩',
        }).get(tl.initial[-1], '')
    return _NULL_NUCLEUS_BRANCH


_TL_NUCLEUS_LIST: PhoneDict = {
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


_TL_CODA_LIST: PhoneDict = {
    'm': 'm', 'mh': 'mʔ',
    'n': 'n',
    'ng': 'ŋ', 'ngh': 'ŋʔ',
    'p': 'p̚', 't': 't̚', 'k': 'k̚', 'h': 'ʔ',
    'nn': '', 'ⁿ': '',   # Nasalize the former vowels
    'nnh': 'ʔ', 'ⁿh': 'ʔ',  # Nasalize the former vowels and then append a 'ʔ'
}
_TL_NASALIZATION = 'nn'

def _TL_POST_PROCESS(ipa: IpaParts) -> IpaParts:
    if ipa.coda[-1] in {'mʔ', 'ŋʔ'}: # Stray pseudo-coda
        ipa.coda[-1] = f'{ipa.coda[-1]}?' # Mark as an invalid combination
    return ipa

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
[m̩]	m								mh
[ŋ̍]	ng								ngh
)'''

TL = phonetic.def_phonetic(
    _PHONE_NAME, Dialect, Variant, _TONE_PREFIX,
    ('', '', _NULL_NUCLEUS_BRANCH, '', _NULL_TONE_BRANCH),
    (_TL_INITIAL_LIST, _TL_MEDIAL_LIST, _TL_NUCLEUS_LIST, _TL_CODA_LIST, _TL_TONE_LIST),
    _TL_NASALIZATION,
    _TL_POST_PROCESS,
)

def tl_syllable_to_ipa(tl_: Str, dialect: Optional[str] = 'chiang', variant: Optional[str] = 'southern') -> phonetic.IpaPair:
    """
    Convert a TL syllable to IPA.
    """
    return phonetic.phonetic_syllable_to_ipa(TL, tl_, dialect, variant)
