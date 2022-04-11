'''
Common definition for Latin phonetic alphabets
'''

import sys
from typing import Callable, Dict, List, Literal, NamedTuple, Optional, Sequence, Set, Tuple, Type, Union
from .ctl_util import Str, normalize, strip_non_letter, str_get_greedy, str_get_tone

IpaPair = Tuple[str, str]

PhoneSegments = List[Optional[Str]]

# Syllable component types
class _Parts(NamedTuple):
    initial: PhoneSegments
    medial: PhoneSegments
    nucleus: PhoneSegments
    coda: PhoneSegments
    tone: PhoneSegments

class SrcParts(_Parts): # Components in the source phonetic system
    pass
class IpaParts(_Parts):
    pass

INITIAL = "initial"
MEDIAL = "medial"
NUCLEUS_I = "nucleus_i"  # Nucleus which nexts to initial or medial
NUCLEUS_F = "nucleus_f"  # Nucleus which nexts to final
NUCLEUS_IF = "nucleus_if"  # Nucleus which both nexts to initial or medial and nexts to final
CODA = "coda"
TONE = "tone"

_IPA_NASALIZATION = '\u0303'  # ' ̃ '

Part = Literal['medial', 'nucleus_i', 'nucleus_if', 'nucleus_f', 'tone', 'initial', 'coda']
Phone = PhoneSpec = Union[Str, Callable[[Part, SrcParts], 'PhoneSpec'], Sequence['PhoneSpec']]
PhoneSet = Set[Optional[Str]]
PhoneDict = Dict[Optional[Str], PhoneSpec]
PhoneCtxDict = Dict[Tuple[Optional[Str], Optional[Str]], PhoneSpec]

def def_phonetic(name: str, dialect: Sequence[str], variant: Sequence[str], tone_prefix: str,
        null_phones: Tuple[Phone, Phone, Phone, Phone, Phone],
        phone_lists: Tuple[PhoneDict, PhoneSet, PhoneDict, PhoneDict, PhoneDict],
        nasalization: str,
        post_process: Optional[Callable[[IpaParts], IpaParts]] = None) -> Type:
    (null_initial, null_medial, null_nucleus, null_coda, null_tone) = null_phones
    (initial_list, medial_list, nucleus_list, coda_list, tone_list) = phone_lists
    return type(name, (object,), dict(
        NAME=name, DIALECT=dialect, VARIANT=variant, TONE_PREFIX=tone_prefix,
        NULL_INITIAL=null_initial, NULL_MEDIAL=null_medial,
            NULL_NUCLEUS=null_nucleus, NULL_CODA=null_coda, NULL_TONE=null_tone,
        INITIAL_LIST=initial_list, MEDIAL_LIST=medial_list,
            NUCLEUS_LIST=nucleus_list, CODA_LIST=coda_list, TONE_LIST=tone_list,
        NASALIZATION=nasalization,
        POST_PROCESS=post_process,
    ))

def after_initial(parts: _Parts) -> Optional[Str]:
    return ([v for v in sum((parts.medial, parts.nucleus), []) if v] or [None])[0]

def _report_invalid(obj: PhoneSpec, catagory: str) -> None:
    print('Warning: ', obj,
        ' is an invalid ', catagory,'.  Continued.',
        sep='', file=sys.stderr, flush=True)

def phonetic_syllable_to_ipa(phone: Type, syll: Str, dialect: Optional[str], variant: Optional[str]) -> IpaPair:
    """
    Convert a syllable in a phonetic notation to IPA. \n
    Input syllable: f'{initial}{medial}{nucleus0}{nucleus1}{coda}' \n
    Output syllable: (initial, f'{medial}{nucleus0}{nucleus1}{coda}{phone.TONE_PREFIX}{tone}') \n

    The tone can appear at any position. \n
    A vowel becomes a medial if it is in the medial list and another vowel presents.
    """
    syll = normalize(syll)
    dialect = dialect and dialect.replace("'", '_').lower()
    variant = variant and variant.replace("'", '_').lower()

    src_parts = SrcParts([], [], [], [], [])
    ipa_parts = IpaParts([], [], [], [], [])

    tone_list = phone.TONE_LIST
    if isinstance(tone_list, phone.DIALECT):
        assert dialect is not None
        tone_list = getattr(tone_list, dialect)
    if isinstance(tone_list, phone.VARIANT):
        assert variant is not None
        tone_list = getattr(tone_list, variant)
    (str_tone, tone, phone_no_tone) = str_get_tone(syll, tone_list, phone.NULL_TONE)

    # Handle neutral tone
    (str_tone_neutral, tone_neutral, phone_no_tone_neutral) = str_get_tone(
        phone_no_tone, tone_list, None)
    if tone_neutral is not None:
        (str_tone, tone, phone_no_tone) = (
            str_tone_neutral, tone_neutral, phone_no_tone_neutral)

    if str_tone:
        src_parts.tone.append(str_tone)

    offset = 0

    (str_initial, offset, initial) = str_get_greedy(
        phone_no_tone, offset, phone.INITIAL_LIST, phone.NULL_INITIAL)

    if str_initial:
        src_parts.initial.append(str_initial)

    # Get nucleus0
    (str_medial, medial) = (None, '')
    (str_nucleus0, offset, nucleus0) = str_get_greedy(
        phone_no_tone, offset, phone.NUCLEUS_LIST, phone.NULL_MEDIAL)
    # If the nucleus0 gotten can be a medial, assume it to be the medial
    if str_nucleus0 in phone.MEDIAL_LIST:
        ((str_medial, medial), (str_nucleus0, nucleus0)) = (
            (str_nucleus0, nucleus0), (None, ''))

    # Get nucleus0 if medial presents
    if str_nucleus0 is None:
        (str_nucleus0, offset, nucleus0) = str_get_greedy(
            phone_no_tone, offset, phone.NUCLEUS_LIST, phone.NULL_NUCLEUS)
    (str_nucleus1, offset, nucleus1) = str_get_greedy(
        phone_no_tone, offset, phone.NUCLEUS_LIST, '')
    # If failed, the assumed medial is actually nucleus0
    if str_nucleus0 is None and str_medial is not None:
        str_nucleus0 = str_medial
        str_medial = ''
        nucleus0 = medial
        medial = phone.NULL_MEDIAL

    if str_medial:
        src_parts.medial.append(str_medial)
    if str_nucleus0:
        src_parts.nucleus.append(str_nucleus0)
        if str_nucleus1:
            src_parts.nucleus.append(str_nucleus1)

    (str_coda, offset, coda) = str_get_greedy(
        phone_no_tone, offset, phone.CODA_LIST, phone.NULL_CODA)

    if str_coda:
        src_parts.coda.append(str_coda)

    for part in src_parts:
        if len(part) == 0:
            part.append(None)

    def get_patched(phone_spec: Optional[PhoneSpec], self_type: Part, parts: SrcParts) -> str:
        """
        Perform a series of one-pass patches on a syllable component
        """
        result = phone_spec
        # Patch the syllable component according to the phonetic of non-nucleus syllable components
        if callable(result):
            result = result(self_type, parts)
        # Patch the syllable component according to the dialect and the variant
        if isinstance(result, phone.DIALECT):
            assert dialect is not None
            result = getattr(result, dialect)
        if isinstance(result, phone.VARIANT):
            assert variant is not None
            result = getattr(result, variant)
        # Concatenate the syllable component defined with multiple parts
        if isinstance(result, list):
            new_result = [get_patched(spec, self_type, parts) for spec in result]
            result = ''.join(new_result)
        # Patch failes if the result is not a string
        if not isinstance(result, str):
            _report_invalid(f'{parts} -> {phone_spec} -> {result}', self_type)
            result = f'{parts}?'
        return result

    def nasalize(segms: PhoneSegments) -> None:
        new_segms: PhoneSegments = []
        for vowels in segms:
            if vowels is None:
                continue
            new_vowels: List[str] = []
            for vowel in vowels:
                new_vowels.append(str(vowel))
                new_vowels.append(_IPA_NASALIZATION)
            new_segms.append(''.join(new_vowels))
        segms.clear()
        segms.extend(new_segms)

    # Patch syllable components
    medial = get_patched(medial, MEDIAL, src_parts)
    if medial:
        ipa_parts.medial.append(medial)
    nucleus0 = get_patched(nucleus0, NUCLEUS_I if nucleus1 else NUCLEUS_IF, src_parts)
    if nucleus0:
        ipa_parts.nucleus.append(nucleus0)
    nucleus1 = get_patched(nucleus1, NUCLEUS_F, src_parts)
    if nucleus1:
        ipa_parts.nucleus.append(nucleus1)
    tone = get_patched(tone, TONE, src_parts)
    ipa_parts.tone.append(phone.TONE_PREFIX)
    if tone:
        ipa_parts.tone.append(tone)

    # Patch consonantal syllable components
    initial = get_patched(initial, INITIAL, src_parts)
    post_initial = after_initial(ipa_parts)
    if post_initial:
        initial = initial.rstrip(str(strip_non_letter(post_initial)[0]))
    if initial:
        ipa_parts.initial.append(initial)
    coda = get_patched(coda, CODA, src_parts)
    if len(ipa_parts.nucleus) and ipa_parts.nucleus[-1]:
        coda = coda.lstrip(str(strip_non_letter(ipa_parts.nucleus[-1])[-1]))
    if coda:
        ipa_parts.coda.append(coda)

    # Apply nasalization to the vowels if needed
    if str_coda is not None and str_coda.startswith(phone.NASALIZATION):
        nasalize(ipa_parts.medial)
        nasalize(ipa_parts.nucleus)

    for part in ipa_parts:
        if len(part) == 0:
            part.append(None)

    if phone.POST_PROCESS is not None:
        ipa_parts = phone.POST_PROCESS(ipa_parts)

    ninitial = sum((bool(v) for v in ipa_parts.initial))
    ipa_list = [str(phone) for phone in sum(ipa_parts, []) if phone]

    # Validity check
    if offset != len(phone_no_tone) or any(v.endswith("?") for v in ipa_list):
        _report_invalid(f'{syll} -> {phone_no_tone}', phone.NAME)
        ipa_list = [v.rstrip("?") for v in ipa_list]
    return (''.join(ipa_list[:ninitial]), ''.join(ipa_list[ninitial:]))
