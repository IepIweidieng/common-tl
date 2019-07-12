# Used by ipa_pair_to_tl_pair

_COMMON_TL_INITIAL_LIST = {
    # *: Not in original TL

    # IPA consonants.
    'd': 'd',  # TL "j" is pronounced as [dz] in Taiwanese Choân-chiu accent
    #   Always followed by [z] or [ʑ]; just keep it
    'z': 'j',  # TL "j" is pronounced as [z] in Taiwanese Chiang-chiu accent

    'ʈ': 't',  # Rhotic consonant; always followed by [ʂ]
    'ʂ': 'sr',  # * Rhotic consonant
    'ʐ': 'jr',  # * Rhotic consonant

    'ɕ': 's',  # An allophone of TL "s"
    'ʑ': 'j',  # An allophone of TL "j"
    'x': 'h',  # Taiwanese Mandarin "ㄏ" is pronounced as either [x] or [h].

    'ȵ': 'gn',  # Used in Taiwanese Chiang-chiu accent.
    'ŋ': 'ng',

    'ᵈ': 'd',  # * Pre-plosion d; distinguish from normal [l]
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
        'orrr',    # * Rhotic vowel; see u'\u02DE' ' ˞ '.
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
    u'\u030D': '',  # ' ̍ '; syllabic consonant
    u'\u0329': '',  # ' ̩ '; syllabic consonant
                      #   Just drop all of them.
}


def _replace_symbol(src, prev_pos_list, prev_replace_pair,
                    current_symbol, tail_replace_pair=None):
    """Side effect: prev_pos_list (rw)"""
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


def ipa_pair_to_tl_pair(ipa_pair, use_north=False):
    """Convert an IPA syllable to common TL."""
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
            tl_phone = tl_phone[not use_north and 1 or 0]

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
