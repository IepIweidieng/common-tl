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
