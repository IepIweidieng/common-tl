from . import ctl_util
from .ctl_util import str_get_greedy

# Used by ipa_pair_to_tl_pair

Dialect = ctl_util.def_dialect([])
dialect = ctl_util.namedtuple_ctor(Dialect)

GENERAL_VARIANT_LIST = ['southern', 'northern']
VARIANT_LIST = Dialect()

Variant = ctl_util.def_variant(GENERAL_VARIANT_LIST, VARIANT_LIST)
variant = ctl_util.namedtuple_ctor(Variant)

_COMMON_TL_INITIAL_LIST = {
    # *: Not in original TL

    # IPA consonants.
    'd': 'd',  # TL "j" is pronounced as [dz] in Taiwanese Choân-chiu accent
    #   Always followed by [z] or [ʑ]; just keep it
    'z': 'j',  # TL "j" is pronounced as [z] in Taiwanese Chiang-chiu accent

    'ʈ': 't',  # Rhotic consonant; always followed by [ʂ]
    'ʂ': 'sr',  # * Rhotic consonant
    'ʐ': 'jr',  # * Rhotic consonant

    'ʃ': 'sr',  # * As a rhotic consonant; used in Taiwanese Hakka
    'ʒ': 'jr',  # * As a rhotic consonant; used in Taiwanese Hakka
    'ɹ': '',  # An allophone of the zero consonant in Southern Sixian dialect of Taiwanese Hakka

    'ɕ': 'sc',  # * TL: "s" before an "i"
    'ʑ': 'jz',  # * TL: "j" before an "i"
    'x': 'h',  # Taiwanese Mandarin "ㄏ" is pronounced as either [x] or [h].

    'ȵ': 'gn',  # Used in Taiwanese Chiang-chiu accent.
    'ŋ': 'ng',

    'ᵈ': 'd',  # * Pre-plosion d; distinguish from normal [l]
    'ʰ': 'h',

    'ʔ': '',  # As initial

    u'\u0320': '',  # ' ̠ '; retracted; used in Southern Sixian dialect of Taiwanese Hakka
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

    'ɤ': variant(
        northern='or',  # For Taiwanese northern accent
        southern='o'),  # For Taiwanese southern accent
    'ə': variant(
        northern='or',
        southern='o'),
    #   They are allophones.  Use only one symbol for them.

    'ʊ': variant(
        northern='o',  # More accurate transcription for Taiwanese northern accent
        southern='oo'),

    'ɔ': 'oo',

    'ɛ': 'ee',  # Used in Taiwanese Chiang-chiu accent
    # 'a'    #   The "a" in TL "-ian" and "-iat"
                #     And in the "ㄢ" of bopomofo finals "ㄧㄢ" and "ㄩㄢ"
                #     Also are pronounced as [ɛ].
                #   In these conditions, replace the 'ee' with 'a' later.

    # Still IPA vowels. Erization-related part.
    'ɚ': variant(
        northern='orrr',    # * Rhotic vowel; see u'\u02DE' ' ˞ '.
        southern='orr'),

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
    u'\u030D': '',  # ' ̍ '; syllabic consonant
    u'\u0329': '',  # ' ̩ '; syllabic consonant
                      #   Just drop all of them.
}


def _compare_and_replace_append(src, prev_pos_list, current_symbol,
                                replace_append_list, target=None):
    """Side effect: prev_pos_list (rw)"""
    new_src = None
    (str_replaced, str_replacer, str_append) = replace_append_list
    target = target if target is not None else str_replaced

    str_replaced_len = len(str_replaced)
    str_replacer_len = len(str_replacer)
    new_src_len = len(src)

    if current_symbol.endswith(target):
        if (str_replaced in prev_pos_list
                and prev_pos_list[str_replaced] != -1):
            new_src = (
                f'{src[:prev_pos_list[str_replaced]]}'
                f'{str_replacer}'
                f'{src[prev_pos_list[str_replaced] + str_replaced_len:]}'
                f'{str_append}')

            new_src_len = len(new_src)

            for (symbol, pos) in prev_pos_list.items():
                if pos > prev_pos_list[str_replaced]:
                    prev_pos_list[symbol] += (
                        str_replacer_len - str_replaced_len)

            prev_pos_list[str_replaced] = -1
            if str_append:
                prev_pos_list[str_append] = (
                    new_src_len + len(current_symbol) - len(str_append))
                return new_src

        if target in prev_pos_list:
            prev_pos_list[target] = (
                new_src_len + len(current_symbol) - len(target))

    return new_src


def ipa_pair_to_tl_pair(ipa_pair, dialect=None, variant='southern'):
    """Convert an IPA syllable to common TL."""
    (ipa_initial, ipa_final) = ipa_pair
    (tl_initial, tl_final) = ('', '')
    prev_symbol_pos = {
        'nn': -1, 'rr': -1,
    }

    offset = 0
    while offset < len(ipa_initial):
        (_, offset, tl_phone) = str_get_greedy(
            ipa_initial, offset, _COMMON_TL_INITIAL_LIST, None)
        if not tl_phone:
            tl_phone = ipa_initial[offset]
            offset = offset + 1
        tl_initial = f'{tl_initial}{tl_phone}'

    offset = 0
    while offset < len(ipa_final):
        (phone, offset, tl_phone) = str_get_greedy(
            ipa_final, offset, _COMMON_TL_FINAL_LIST, None)
        if not tl_phone:
            phone = tl_phone = ipa_final[offset]
            offset = offset + 1

        if isinstance(tl_phone, Variant):
            tl_phone = getattr(tl_phone, variant)

        # Merge multiple 'nn'
        new_tl_final = _compare_and_replace_append(
            tl_final, prev_symbol_pos, tl_phone, ('nn', '', ''))
        if new_tl_final is not None:
            tl_final = new_tl_final

        # 'rr' should comes after 'nn'
        new_tl_final = _compare_and_replace_append(
            tl_final, prev_symbol_pos, tl_phone, ('rr', 'nn', 'rr'), target='nn')
        if new_tl_final is not None:
            tl_final = new_tl_final
            continue

        # Merge multiple 'rr'
        new_tl_final = _compare_and_replace_append(
            tl_final, prev_symbol_pos, tl_phone, ('rr', '', ''))
        if new_tl_final is not None:
            tl_final = new_tl_final

        tl_final = f'{tl_final}{tl_phone}'

    return (tl_initial, tl_final)
