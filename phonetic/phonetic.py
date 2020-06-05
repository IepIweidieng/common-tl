'''
Common definition for Latin phonetic alphabets
'''

import sys
from .ctl_util import normalize, str_get_greedy, str_get_tone

# Syllable component types
INITIAL = "initial"
MEDIAL = "medial"
NUCLEUS_I = "nucleus_i"  # Nucleus which nexts to initial or medial
NUCLEUS_F = "nucleus_f"  # Nucleus which nexts to final
NUCLEUS_IF = "nucleus_if"  # Nucleus which both nexts to initial or medial and nexts to final
CODA = "coda"
INITIAL_IPA = "initial_ipa"
MEDIAL_IPA = "medial_ipa"
NUCLEUS_I_IPA = "nucleus_i_ipa"
NUCLEUS_F_IPA = "nucleus_f_ipa"
NUCLEUS_IF_IPA = "nucleus_if_ipa"
CODA = "coda"
TONE = "tone"

_IPA_NASALIZATION = u'\u0303'  # ' ̃ '

def def_phonetic(name, dialect, variant, tone_prefix,
        null_phones, phone_lists, nasalization):
    (null_initial, null_medial, null_nucleus, null_coda, null_tone) = null_phones
    (initial_list, medial_list, nucleus_list, coda_list, tone_list) = phone_lists
    return type(name, (object,), dict(
        NAME=name, DIALECT=dialect, VARIANT=variant, TONE_PREFIX=tone_prefix,
        NULL_INITIAL=null_initial, NULL_MEDIAL=null_medial,
            NULL_NUCLEUS=null_nucleus, NULL_CODA=null_coda, NULL_TONE=null_tone,
        INITIAL_LIST=initial_list, MEDIAL_LIST=medial_list,
            NUCLEUS_LIST=nucleus_list, CODA_LIST=coda_list, TONE_LIST=tone_list,
        NASALIZATION=nasalization
    ))

def _report_invalid(obj, catagory):
    """
    Side effect: IO (w)
    """
    print('Warning: ', obj,
        ' is an invalid ', catagory,'.  Continued.',
        sep='', file=sys.stderr, flush=True)

def phonetic_syllable_to_ipa(phone, syll, dialect, variant):
    """
    Convert a syllable in a phonetic notation to IPA. \n
    Input syllable: f'{initial}{medial}{nucleus0}{nucleus1}{coda}' \n
    Output syllable: (initial, f'{medial}{nucleus0}{nucleus1}{coda}{phone.TONE_PREFIX}{tone}') \n

    The tone can appear at any position. \n
    A vowel becomes a medial if it is in the medial list and another vowel presents. \n

    Side effect: _report_invalid: IO (w)
    """
    syll = normalize(syll)
    dialect = dialect and dialect.replace("'", '_').lower()
    variant = variant and variant.replace("'", '_').lower()

    tone_list = phone.TONE_LIST
    if isinstance(tone_list, phone.DIALECT):
        tone_list = getattr(tone_list, dialect)
    if isinstance(tone_list, phone.VARIANT):
        tone_list = getattr(tone_list, variant)
    (str_tone, tone, phone_no_tone) = str_get_tone(syll, tone_list, phone.NULL_TONE)

    # Handle neutral tone
    (str_tone_neutral, tone_neutral, phone_no_tone_neutral) = str_get_tone(
        phone_no_tone, tone_list, None)
    if tone_neutral is not None:
        (str_tone, tone, phone_no_tone) = (
            str_tone_neutral, tone_neutral, phone_no_tone_neutral)

    offset = 0

    (str_initial, offset, initial) = str_get_greedy(
        phone_no_tone, offset, phone.INITIAL_LIST, phone.NULL_INITIAL)

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

    (str_coda, offset, coda) = str_get_greedy(
        phone_no_tone, offset, phone.CODA_LIST, phone.NULL_CODA)

    def get_patched(component, self_type, str_component, custom_patch=None):
        """
        Perform a series of one-pass patches on a syllable component
        """
        result = component
        if callable(custom_patch):
            result = custom_patch(result, self_type)
        else:
            # Patch the syllable component according to the phonetic of non-nucleus syllable components, from coda to initial
            if callable(result):
                result = result(self_type, str_coda, CODA)
            if callable(result):
                result = result(self_type, str_medial, MEDIAL)
            if callable(result):
                result = result(self_type, str_initial, INITIAL)
        # Patch the syllable component according to the dialect and the variant
        if isinstance(result, phone.DIALECT):
            result = getattr(result, dialect)
        if isinstance(result, phone.VARIANT):
            result = getattr(result, variant)
        # Concatenate the syllable component defined with multiple parts
        if isinstance(result, list):
            new_result = [
                get_patched(ipa_part, self_type, str_component, custom_patch)
                    for ipa_part in result]
            result = ''.join(new_result)
        # Patch failes if the result is not a string
        if not isinstance(result, str):
            _report_invalid(f'{str_component} -> {component} -> {result}', self_type)
            result = f'{str_component}?'
        return result

    def nasalization(vowels):
        new_vowels = []
        for vowel_item in vowels:
            new_vowels.append(vowel_item)
            new_vowels.append(_IPA_NASALIZATION)
        return ''.join(new_vowels)

    # Patch syllable components
    medial = get_patched(medial, MEDIAL, str_medial)
    nucleus0 = get_patched(nucleus0, NUCLEUS_I if nucleus1 else NUCLEUS_IF, str_nucleus0)
    nucleus1 = get_patched(nucleus1, NUCLEUS_F, str_nucleus1)
    tone = get_patched(tone, TONE, str_tone)

    # Patch consonantal syllable components according to the nearest syllable component

    def patch_initial(initial, self_type):
        result = initial
        if callable(result):
            result = result(self_type, medial or nucleus0, MEDIAL_IPA)
        if callable(result):
            result = result(self_type, nucleus0, NUCLEUS_I_IPA)
        return result
    initial = get_patched(initial, INITIAL, str_initial, patch_initial)

    def patch_coda(coda, self_type):
        result = coda
        if callable(result):
            result = result(self_type, nucleus1 or nucleus0, NUCLEUS_F_IPA)
        return result
    coda = get_patched(coda, CODA, str_coda, patch_coda)

    # Apply nasalization to the vowels if needed
    if str_coda is not None and str_coda.startswith(phone.NASALIZATION):
        medial = nasalization(medial)
        nucleus0 = nasalization(nucleus0)
        nucleus1 = nasalization(nucleus1)

    # Validity check
    if (offset != len(phone_no_tone)
            or any(v.endswith("?") for v in (initial, medial, nucleus0, nucleus1, coda, tone))):
        _report_invalid(f'{syll} -> {phone_no_tone}', phone.NAME)
        (initial, medial, nucleus0, nucleus1, coda, tone) = (v.rstrip("?")
            for v in (initial, medial, nucleus0, nucleus1, coda, tone))
    return (initial, f'{medial}{nucleus0}{nucleus1}{coda}{phone.TONE_PREFIX}{tone}')
