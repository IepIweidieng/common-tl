'''
Common definition for Latin phonetic alphabets
'''

import sys
from .ctl_util import normalize, str_get_greedy, str_get_tone

_IPA_NASALIZATION = u'\u0303'  # ' ̃ '

def def_phonetic(name, dialect, variant, tone_prefix,
        null_phones, phone_lists):
    (null_initial, null_medial, null_nucleus, null_coda, null_tone) = null_phones
    (initial_list, medial_list, nucleus_list, coda_list, tone_list) = phone_lists
    return type(name, (object,), dict(
        NAME=name, DIALECT=dialect, VARIANT=variant, TONE_PREFIX=tone_prefix,
        NULL_INITIAL=null_initial, NULL_MEDIAL=null_medial,
            NULL_NUCLEUS=null_nucleus, NULL_CODA=null_coda, NULL_TONE=null_tone,
        INITIAL_LIST=initial_list, MEDIAL_LIST=medial_list,
            NUCLEUS_LIST=nucleus_list, CODA_LIST=coda_list, TONE_LIST=tone_list,
    ))



def phonetic_syllable_to_ipa(phone, syll, dialect, variant):
    """
    Convert a syllable in a phonetic notation to IPA. \n
    Input syllable: f'{initial}{medial}{nucleus0}{nucleus1}{coda}' \n
    Output syllable: (initial, f'{medial}{nucleus0}{nucleus1}{coda}{phone.TONE_PREFIX}{tone}') \n

    The tone can appear at any position. \n
    A vowel becomes a medial if it is in the medial list and another vowel presents. \n

    Side effect: IO (w)
    """
    syll = normalize(syll)
    dialect = dialect and dialect.replace("'", '_').lower()
    variant = variant and variant.replace("'", '_').lower()

    tone_list = phone.TONE_LIST
    if isinstance(tone_list, phone.DIALECT):
        tone_list = getattr(tone_list, dialect)
    if isinstance(tone_list, phone.VARIANT):
        tone_list = getattr(tone_list, variant)
    (tone, phone_no_tone) = str_get_tone(syll, tone_list, phone.NULL_TONE)

    offset = 0

    (phone_initial, offset, initial) = str_get_greedy(
        phone_no_tone, offset, phone.INITIAL_LIST, phone.NULL_INITIAL)

    (phone_medial, medial) = (None, '')
    (phone_nucleus0, offset, nucleus0) = str_get_greedy(
        phone_no_tone, offset, phone.NUCLEUS_LIST, phone.NULL_MEDIAL)
    if phone_medial in phone.MEDIAL_LIST:
        ((phone_medial, medial), (phone_nucleus0, nucleus0)) = (
            (phone_nucleus0, nucleus0), (None, ''))

    if phone_nucleus0 is None:
        (phone_nucleus0, offset, nucleus0) = str_get_greedy(
            phone_no_tone, offset, phone.NUCLEUS_LIST, phone.NULL_NUCLEUS)
    (phone_nucleus1, offset, nucleus1) = str_get_greedy(
        phone_no_tone, offset, phone.NUCLEUS_LIST, '')
    if phone_nucleus0 == None and phone_medial != None:
        phone_nucleus0 = phone_medial
        phone_medial = ''
        nucleus0 = medial
        medial = phone.NULL_MEDIAL

    (phone_coda, offset, coda) = str_get_greedy(
        phone_no_tone, offset, phone.CODA_LIST, phone.NULL_CODA)

    def get_patched(vowel, is_initial=False):
        result = vowel
        if is_initial:
            if callable(result):
                result = result(phone_medial or phone_nucleus0)
        else:
            if callable(result):
                result = result(phone_coda)
            if callable(result):
                result = result(phone_medial)
            if callable(result):
                result = result(phone_initial)
        if isinstance(result, phone.DIALECT):
            result = getattr(result, dialect)
        if isinstance(result, phone.VARIANT):
            result = getattr(result, variant)
        if isinstance(result, list):
            new_result = [get_patched(ipa_part, is_initial) for ipa_part in result]
            result = ''.join(new_result)
        return result

    def nasalization(vowels):
        new_vowels = []
        for vowel_item in vowels:
            new_vowels.append(vowel_item)
            new_vowels.append(_IPA_NASALIZATION)
        return ''.join(new_vowels)

    initial = get_patched(initial, is_initial=True)
    medial = get_patched(medial)
    nucleus0 = get_patched(nucleus0)
    nucleus1 = get_patched(nucleus1)
    tone = get_patched(tone)

    if callable(initial):
        initial = initial(nucleus0)
    if callable(coda):
        coda = coda(nucleus0)

    if phone_coda != None and phone_coda.startswith('nn'):
        medial = nasalization(medial)
        nucleus0 = nasalization(nucleus0)
        nucleus1 = nasalization(nucleus1)

    if offset != len(phone_no_tone) or coda.endswith("?"):
        print('Warning: ', syll, ' -> ', phone_no_tone,
              ' is an invalid ', phone.NAME,'.  Continued.',
              sep='', file=sys.stderr, flush=True)
        return (initial, f'{medial}{nucleus0}{nucleus1}{coda.rstrip("?")}?{phone.TONE_PREFIX}{tone}')
    return (initial, f'{medial}{nucleus0}{nucleus1}{coda}{phone.TONE_PREFIX}{tone}')
