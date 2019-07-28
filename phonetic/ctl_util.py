from collections import namedtuple
import unicodedata

def namedtuple_ctor(Tuple, default=None):
    return (lambda *args, **kwargs:
        Tuple(*([*args] + [default]*(len(Tuple._fields)-len(args))))._replace(**kwargs))

def def_lang(lang_list):
    return namedtuple('Lang', lang_list)
def def_dialect(dialect_list):
    return namedtuple('Dialect', dialect_list)
def def_variant(general_variant_list, variant_list):
    return namedtuple('Variant', sum(variant_list, general_variant_list))

class Lang_opt(namedtuple('Lang_opt', ['dialect', 'variant'])):
    def _asdict(self):
        res = super()._asdict()
        return {k: res[k] for k in res if res[k] is not None}
lang_opt = namedtuple_ctor(Lang_opt)

def normalize(str_):
    '''Decompose precomposed characters'''
    return type(str_)(unicodedata.normalize("NFD", str(str_)))

def find_first_non_roman(text):
    """
    Usage & result:
        find_first_non_roman('abcdef')   == 6
        find_first_non_roman('abc我def') == 3
        find_first_non_roman('我abcdef') == 0
    """
    for (pos, char) in enumerate(text):
        if not is_char_roman(char):
            return pos
    return len(text)


def is_char_roman(char):
    if not (('A' <= char <= 'Z') or ('a' <= char <= 'z')
            or ('0' <= char <= '9') or (char == '#') or (char == '*')
            or (char == '-') or (char == ' ')
            or (r'\u00C0' <= char <= r'\u1EFF')
            or (r'\u2C60' <= char <= r'\u2C7D')
            or (r'\uA720' <= char <= r'\uA78C')
            or (r'\uA7FB' <= char <= r'\uA7FF')
            or (r'\uFB00' <= char <= r'\uFB06')):
        return False

    return True


def linear_search_rightmost(first, last, eq_func):
    """
    Find the rightmost element which the value equals to the target. \n
    Search in the range [first, last) of an unsorted array. \n
    Adopted from Wikipedia. \n
    Example:
        Value is whether the string prefix is a word
        String: '行政院會議'
        Value:   T T T F T  (Target: T)
        Result:          ^
    Side effect: eq_func: [split_chinese_word] sentence (r),
        tl_dict.chinese_phonetic (r)
    """
    right = last - 1

    while right > first:
        if eq_func(right):
            return right

        right -= 1

    return None


def get_max_length(dict_):
    result = 0
    for key in dict_:
        result = max(len(key), result)

    return result


def str_get_gready(str_, offset, source_dict, default_):
    new_offset = offset
    str_max_length = min(get_max_length(source_dict), max(len(str_) - offset, 0))
    for length in range(str_max_length, 0, -1):
        new_offset = offset + length
        if str_[offset : new_offset] in source_dict:
            matched_str = str_[offset : new_offset]
            matched_item = source_dict[matched_str]
            return (matched_str, new_offset, matched_item)

    return (None, offset, default_)


def str_get_tone(str_, tone_list, default_):
    tone = None
    str_tone_len = 0
    str_max_length = min(get_max_length(tone_list), len(str_))
    for offset in range(0, len(str_), 1):
        (_, new_offset, tone_k) = str_get_gready(str_, offset, tone_list, None)
        if tone_k and new_offset - offset >= str_tone_len:
            tone = tone_k
            str_tone_len = new_offset - offset
            str_no_tone = f'{str_[:offset]}{str_[new_offset:]}'
            if len(tone) == str_max_length: break
    if tone:
        return (tone, str_no_tone)
    return (default_, str_)
