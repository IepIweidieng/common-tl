import os
import shutil

import tl_dict


# Usage & result: is_roman_only('abc')   is True
#                 is_roman_only('我abc') is False

def is_roman(text):
    for char in text:
        if not (('A' <= char <= 'Z') or ('a' <= char <= 'z')
                or ('0' <= char <= '9') or (char == '-') or (char == ' ')
                or (r'\u00C0' <= char <= r'\u1EFF')
                or (r'\u2C60' <= char <= r'\u2C7D')
                or (r'\uA720' <= char <= r'\uA78C')
                or (r'\uA7FB' <= char <= r'\uA7FF')
                or (r'\uFB00' <= char <= r'\uFB06')):
            return False

    return True


# Find the rightmost element which the value equals to the target.
# Search in the range [first, last) of an unsorted array.
# Adopted from Wikipedia.
# Example  : '行政院會議'  Condition: Is the string prefix a word?
# Condition:  T T T F T  (Target: T)
# Result   :          ^
# Side effect: eq_func: [split_chinese_word] sentence (r),
#                       tl_dict.chinese_zhuyin (r)

def linear_search_rightmost(first, last, eq_func):
    right = last - 1

    while right > first:
        if eq_func(right):
            return right

        right -= 1

    return None


# Find the rightmost element which the value equals to the target.
# Search in the range [first, last) of a sorted array.
# Adopted from Wikipedia.
# Example  : 'lo5-ma2-ji7拼音方案'  Condition: Is the prefix roman-only?
# Condition:  TTTTTTTTTTTF F F F  (Target: T)
# Result   :            ^
# Side effect: eq_func: [split_chinese_word] sentence (r)
#              gt_func: [split_chinese_word] sentence (r)

def binary_search_rightmost(first, last, eq_func, gt_func):
    (left, right) = (first, last)

    while left < right:
        middle = (left + right) // 2
        if gt_func(middle):
            right = middle
        else:
            left = middle + 1

    if left > first and eq_func(left - 1):
        return left - 1

    return None


# 斷詞程式
# 有空白的都併在一起然後斷詞
# Chinese word spliter
# Merge the spaces in a sentence, and then split the merged sentence into words.
# Side effect: tl_dict.chinese_zhuyin (r)

def split_chinese_word(sentence):
    spilted_words = []
    merged_sentence = merge(sentence)

    for merged_str in merged_sentence:
        str_len = len(merged_str)
        current_offset = 0
        while current_offset < str_len:
            max_word_bound = str_len - current_offset

            # Find the longest word start from current_offset
            word_bound = linear_search_rightmost(
                1, max_word_bound + 1,
                # Side effect: [split_chinese_word] sentence (r),
                #              tl_dict.chinese_zhuyin (r)
                lambda new_bound:
                    (merged_str[current_offset: current_offset + new_bound]
                        in tl_dict.chinese_zhuyin)
            )

            # If no word found,
            #   use the whole roman word from current_offset instead
            if word_bound is None:
                # Side effect: [split_chinese_word] sentence (r)
                def eq_func(new_bound): return is_roman(
                    merged_str[current_offset: current_offset + new_bound])

                word_bound = binary_search_rightmost(
                    0, max_word_bound + 1, eq_func,
                    # Side effect: [split_chinese_word] sentence (r)
                    lambda new_bound: not eq_func(new_bound)
                ) or 1

            spilted_words.append(
                merged_str[current_offset: current_offset + word_bound])
            current_offset += word_bound

    return spilted_words


# 將中羅併在一起羅羅分開
# Merge Chinese characters, while keep roman words delimited by a space.
# Roman words followed by or led by Chinese characters are also merged
#   with the characters into a single word.

def merge(sentence):
    merged_sentence = []
    merge_units = sentence.strip().split(' ')
    merged_str = ''
    is_prev_merge_unit_roman = False

    for merge_unit_item in merge_units:
        if merge_unit_item:
            # 代表全羅馬字
            # Check whether the part of string is a Roman word
            if is_roman(merge_unit_item):
                # Led by Chinese characters
                if not is_prev_merge_unit_roman:
                    merged_str = f'{merged_str}{merge_unit_item}'
                    is_prev_merge_unit_roman = True
                # Neither followed by nor led by Chinese characters
                else:
                    merged_sentence.append(merged_str)
                    merged_str = merge_unit_item
            # Chinese characters or a Roman word followed by Chinese characters
            else:
                merged_str = f'{merged_str}{merge_unit_item}'
                is_prev_merge_unit_roman = False

    if merged_str:
        merged_sentence.append(merged_str)

    return merged_sentence


# Split Chinese words for a .trn file.
# Side effect: os.path (x), fileIO (rw)
#              split_chinese_word: tl_dict.chinese_zhuyin (r)

def split_file(path):
    if os.path.isfile(path) and os.path.splitext(path) == '.trn':
        shutil.copy(path, f'{path}_bk')
        with open(path, 'r+', encoding='utf8', newline='\n') as trn_file:
            lf = '\n'
            (trn_chinese, *trn_roman) = trn_file.read().splitlines()
            trn_chinese_words = split_chinese_word(trn_chinese)

            trn_file.truncate(0)
            trn_file.seek(0)
            trn_file.write(
                f'{" ".join((word for word in trn_chinese_words))}\n'
                f'{lf.join(trn_roman)}')


# 資料夾下的 trn 重新斷詞
# Split Chinese words for every .trn file in the folder and subfolders.
# Usage: split_for_each_file(path_to_the_folder)
# Example: split_for_each_file("/home/thh101u/Desktop/333_sentence_trn0629/")
# Side effect: os (x), IO (w)
#              tl_dict.set_dict: fileIO (rw), os (x), sys (x), pickle (x)
#                                [tl_dict.set_dict] loaded_dict (rw),
#                                chinese_zhuyin_zhuyin (rw)
#              split_file: fileIO (rw)
#                          split_chinese_word: tl_dict.chinese_zhuyin (r)

def split_for_each_file(path='', dict_paths=['chinese_dict.txt']):
    tl_dict.set_dict(dict_paths)

    # Prevent using root directory if path is an empty string
    standard_path = os.path.join(os.curdir, path)

    for subpath in os.listdir(standard_path):
        standard_subpath = os.path.join(standard_path, subpath)
        if os.path.isdir(standard_subpath):
            for subfile in os.listdir(standard_subpath):
                split_file(os.path.join(standard_subpath, subfile))
        else:
            split_file(standard_subpath)

    print("Split for each file done!")


# Side effect: IO (w)
#              tl_dict.set_dict: fileIO (rw), os (x), sys (x), pickle (x)
#                                [tl_dict.set_dict] loaded_dict (rw),
#                                chinese_zhuyin (rw)
#              split_chinese_word: tl_dict.chinese_zhuyin (r)

def main():
    tl_dict.set_dict(["chinese_dict.txt"], True)

    sentence = '你 是 鬱tiau5誰 a2 無a7好 se ven 買 泡  麵 和 感 心測  試 '

    print(split_chinese_word(sentence))
    print("Done!")


if __name__ == '__main__':
    main()
