'''Phonetic notation definition
THRS - Taiwanese Hakka Romanization System (臺灣客家語拼音方案)
Compatible with Tongyong Pinyin for Taiwanese Hakka (臺灣客語通用拼音方案)
'''

from . import ctl_util
from . import phonetic

_PHONE_NAME = 'THRS'

Dialect = ctl_util.def_dialect(
      ['sixian', 'hailu', 'dabu', 'raoping', 'zhao_an', 'southern_sixian'])
#       四縣      海陸      大埔    饒平       詔安        南四縣
dialect = ctl_util.namedtuple_ctor(Dialect)

GENERAL_VARIANT_LIST = []
VARIANT_LIST = Dialect(
    sixian=[],
    hailu=[],
    dabu=[],
    raoping=['hsinchu', 'zhuolan'],
#             新竹       卓蘭
    zhao_an=[],
    southern_sixian=[],
)

Variant = ctl_util.def_variant(GENERAL_VARIANT_LIST, VARIANT_LIST)
variant = ctl_util.namedtuple_ctor(Variant)

_TONE_PREFIX = '2'

# For 'ˋ'
_vdf = Dialect('4', '8', '8', '4', '8', '4')
def _FALLING_TONE_BRANCH(thrs_coda):
    return {
        'b': _vdf, 'd': _vdf, 'nnd': _vdf, 'g': _vdf,
        'p': _vdf, 't': _vdf, 'nnt': _vdf, 'k': _vdf,  # From Tongyong Pinyin for Taiwanese Hakka
    }.get(thrs_coda, Dialect('2', '1', '3', Variant(hsinchu='3', zhuolan='5'), '5', '2'))

# For '^'
_vdlf = dialect(dabu='4')
def _LOW_FALLING_TONE_BRANCH(thrs_coda):
    return {
        'b': _vdlf, 'd': _vdlf, 'nnd': _vdlf, 'g': _vdlf,
        'p': _vdlf, 't': _vdlf, 'nnt': _vdlf, 'k': _vdlf,  # From Tongyong Pinyin for Taiwanese Hakka
    }.get(thrs_coda, dialect(dabu='2'))

_vd0 = Dialect('8', '4', None, '8', None, '8')
def _NULL_TONE_BRANCH(thrs_coda):
    return {
        'b': _vd0, 'd': _vd0, 'nnd': _vd0, 'g': _vd0,
        'p': _vd0, 't': _vd0, 'nnt': _vd0, 'k': _vd0,  # From Tongyong Pinyin for Taiwanese Hakka
    }.get(thrs_coda, Dialect('3', '5', None, Variant(hsinchu='5', zhuolan='7'), '7', '3'))

_THRS_TONE_LIST = Dialect(
    sixian={
        '24': '1', 'ˊ': '1',
        '11': '5', 'ˇ': '5',
        '31': '2', 'ˋ': _FALLING_TONE_BRANCH,
        '55': '3',  # '': _NULL_TONE_BRANCH,
        '2': '4',  # 'ˋ': _FALLING_TONE_BRANCH,
        '5': '8',  # '': _NULL_TONE_BRANCH,
    },
    hailu={
        '53': '1', 'ˋ': _FALLING_TONE_BRANCH,
        '55': '5',  # '': _NULL_TONE_BRANCH,
        '24': '2', 'ˊ': '2',
        '11': '3', 'ˇ': '3',
        '33': '7', '+': '7',
        '5': '4',  # '': _NULL_TONE_BRANCH,
        '2': '8',  # 'ˋ': _FALLING_TONE_BRANCH,
    },
    dabu={
        '33': '1', '+': '1',
        '35': '9', 'ˊ': '9',
        '113': '5', 'ˇ': '5',
        '31': '2', '^': _LOW_FALLING_TONE_BRANCH,
        '53': '3', 'ˋ': _FALLING_TONE_BRANCH,
        '21': '4',  # '^': _LOW_FALLING_TONE_BRANCH,
        '54': '8',  # 'ˋ': _FALLING_TONE_BRANCH,
    },
    raoping=Variant(
        hsinchu={
            '11': '1', 'ˇ': '1',
            '55': '5',  # '': _NULL_TONE_BRANCH,
            '53': '3', 'ˋ': _FALLING_TONE_BRANCH,
            '24': '7', 'ˊ': '7',
            '2': '4',  # 'ˋ': _FALLING_TONE_BRANCH,
            '5': '8',  # '': _NULL_TONE_BRANCH,
        },
        zhuolan={
            '11': '1', 'ˇ': '1',
            '53': '5', 'ˋ': _FALLING_TONE_BRANCH,
            '31': '3', '^': '3',
            '55': '7',  # '': _NULL_TONE_BRANCH,
            '2': '4',  # 'ˋ': _FALLING_TONE_BRANCH,
            '24': '12', 'ˊ': '12',
            '5': '8',  # '': _NULL_TONE_BRANCH,
        },
    ),
    zhao_an={
        '11': '1', 'ˇ': '1',
        '53': '5', 'ˋ': _FALLING_TONE_BRANCH,
        '31': '2', '^': '2',
        '55': '7',  # '': _NULL_TONE_BRANCH,
        '24': '4', 'ˊ': '4',
        '43': '8',  # 'ˋ': _FALLING_TONE_BRANCH,
    },
    southern_sixian={
        '24': '1', 'ˊ': '1',
        '33': '1', '+': '1',  # For Meinong District, Kaohsiung, etc.
        '11': '5', 'ˇ': '5',
        '31': '2', 'ˋ': _FALLING_TONE_BRANCH,
        '55': '3',  # '': _NULL_TONE_BRANCH,
        '2': '4',  # 'ˋ': _FALLING_TONE_BRANCH,
        '5': '8',  # '': _NULL_TONE_BRANCH,
    },
)

def _s(thrs_medial):
    return {
        'i': Dialect('ɕ', 's', 's', 's', 's', 'ɕ'),
    }.get(thrs_medial, 's')

def _INITIAL_M_BRANCH(nucleus):
    return {
        'm̩': ''
    }.get(nucleus, 'm')

def _m(thrs_medial):
    return _INITIAL_M_BRANCH

def _INITIAL_N_BRANCH(nucleus):
    return {
        'n̩': ''
    }.get(nucleus, 'n')

def _n(thrs_medial):
    return _INITIAL_N_BRANCH

def _INITIAL_NG_BRANCH(nucleus):
    return {
        'ŋ̍': ''
    }.get(nucleus, 'ŋ')

def _ng(thrs_medial):
    return {
        'i': 'ȵ',
    }.get(thrs_medial, _INITIAL_NG_BRANCH)


_THRS_INITIAL_LIST = {
    'b': 'p',   'd': 't',                                         'g': 'k',
    'p': 'pʰ',  't': 'tʰ',                                        'k': 'kʰ',
    'bb': 'b',  'l': 'l',
    'm': _m,    'n': _n,                                          'ng': _ng,
                'z': ['t', _s],       'zh': 'tʃ',    'j': 'tɕ',
                'c': ['t', _s, 'ʰ'],  'ch': 'tʃʰ',   'q': 'tɕʰ',
    'f': 'f',   's': [_s],            'sh': 'ʃ',     'x': 'ɕ',    'h': 'h',
    'v': 'v',                         'rh': 'ʒ',
                                      'r': 'ɹ̠',  # Used in Southern Sixian dialect
}

_THRS_MEDIAL_LIST = {'i', 'u'}

def _NULL_NUCLEUS_BRANCH_INITIAL(thrs_initial):
    return {
        'ng': 'ŋ̍', 'n': 'n̩', 'm': 'm̩'
    }.get(thrs_initial, '')

def _NULL_NUCLEUS_BRANCH_MEDIAL(thrs_medial):
    return _NULL_NUCLEUS_BRANCH_INITIAL

def _NULL_NUCLEUS_BRANCH(thrs_coda):
    return {
        'ng': 'ŋ̍', 'n': 'n̩', 'm': 'm̩',
    }.get(thrs_coda, _NULL_NUCLEUS_BRANCH_MEDIAL)


_THRS_NUCLEUS_LIST = {
    'a': 'a',
    'e': 'e',
    'ee': 'ɛ',  # Used in Zhao'an dialect
    'er': 'ə',  # Used in Hailu and Raoping dialects
    'o': 'o',
    'oo': 'ɔ',  # Used in Zhao'an dialect
    'i': 'i',
    'u': 'u',
    'ii': 'ɨ',
}


def _CODA_M_BRANCH(nucleus):
    return {
        'm̩': ''
    }.get(nucleus, 'm')

def _CODA_N_BRANCH(nucleus):
    return {
        'n̩': ''
    }.get(nucleus, 'n')

def _CODA_NG_BRANCH(nucleus):
    return {
        'ŋ̍': ''
    }.get(nucleus, 'ŋ')


_THRS_CODA_LIST = {
    'm': _CODA_M_BRANCH,
    'n': _CODA_N_BRANCH,
    'ng': _CODA_NG_BRANCH,
    'b': 'p̚', 'd': 't̚', 'g': 'k̚',
    'p': 'p̚', 't': 't̚', 'k': 'k̚',  # From Tongyong Pinyin for Taiwanese Hakka
    'nn': '',   # Nasalize the former vowels; mainly used in Zhao'an dialect
    'nnd': 't̚',  # Nasalize the former vowels and then append a 't̚'; used in Zhao'an dialect
    'nnt': 't̚',
}

'''
_FINAL_LIST = (
			[m]	[n]	[ŋ]	[p̚]	[t̚]		[k̚]
[ ̃ ]		nn
[a] 	a	ann	am	an	ang	ab	ad	ag
[aɪ]	ai	ainn
[aʊ]	au
[e] 	e		em	en		eb	ed
[ɛ] 	ee		eem	een			eed
[eʊ]	eu
[ə] 	er
[i] 	i	inn	im	in		ib	id
[ɨ] 	ii		iim	iin		iib	iid
[ɪa]	ia	iann	iam	ian	iang	iab	iad		iag
[ɪaʊ]	iau	iaunn
[ɪe]	ie		iem	ien		ieb	ied
[ɪeʊ]	ieu
[ɪo]	io			ion	iong		iod		iog
[ɪoɪ]	ioi
[iu]	iu	iunn		iun	iung		iud		iug
[o] 	o			on	ong		od		og
[oɪ]	oi
[ɔ] 	oo
[u] 	u			un	ung		ud		ug
[ua]	ua	uann		uan	uang		uad	uannd	uag
[uaɪ]	uai	uainn
[ue]	ue			uen			ued
[ui]	ui
[m̩]	m
[n̩]	n
[ŋ̍]	ng
'''

THRS = phonetic.def_phonetic(
    _PHONE_NAME, Dialect, Variant, _TONE_PREFIX,
    ('', '', _NULL_NUCLEUS_BRANCH, '', _NULL_TONE_BRANCH),
    (_THRS_INITIAL_LIST, _THRS_MEDIAL_LIST, _THRS_NUCLEUS_LIST, _THRS_CODA_LIST, _THRS_TONE_LIST)
)

def thrs_syllable_to_ipa(thrs_, dialect='sixian', variant=None):
    """
    Convert a THRS syllable to IPA. \n
    Side effect: IO (w)
    """
    return phonetic.phonetic_syllable_to_ipa(THRS, thrs_, dialect, variant)
