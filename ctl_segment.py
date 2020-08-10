import os
import shutil

import ctl_dict
import phonetic.ctl_util as ctl_util


def split_chinese_word(sentence, dict_):
    """
    斷詞程式 \n
    有空白的都併在一起然後斷詞 \n
    Chinese word spliter \n
    Merge the spaces in a sentence,
      and then split the merged sentence into words.
    """
    spilted_words = []
    merged_sentence = merge(sentence)

    str_len = len(merged_sentence)
    current_offset = 0
    while current_offset < str_len:
        max_word_bound = str_len - current_offset

        # Find the longest word start from current_offset
        word_bound = ctl_util.linear_search_rightmost(
            1, min(max_word_bound + 1, dict_.max_word_length + 1),
            lambda new_bound:
                (merged_sentence[current_offset: current_offset + new_bound]
                    in dict_.chinese_phonetic)
        )

        # If no word found,
        #   use the whole roman word from current_offset instead
        if word_bound is None:
            word_bound = (
                ctl_util.find_first_non_roman(merged_sentence[current_offset:])
                or 1)

        spilted_words.append(
            merged_sentence[current_offset: current_offset + word_bound])
        current_offset += word_bound

    return spilted_words


def merge(sentence):
    """
    將中羅併在一起羅羅分開 \n
    Merge Chinese characters, while keep roman words delimited by a space. \n
    Roman words followed by or led by Chinese characters are also merged
      with the characters into a single word.
    """
    merged_sentence = []
    merge_units = sentence.strip().split(' ')
    merged_str = ''
    is_prev_merge_unit_roman = False

    for merge_unit_item in merge_units:
        if merge_unit_item:
            # 代表全羅馬字
            # Check whether the part of string is a Roman word
            if ctl_util.find_first_non_roman(merge_unit_item):
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

    return ' '.join(merged_sentence)


def split_file(path, dict_):
    """
    Split Chinese words for a .trn file.
    """
    if os.path.isfile(path) and os.path.splitext(path) == '.trn':
        shutil.copy(path, f'{path}_bk')
        with open(path, 'r+', encoding='utf8', newline='\n') as trn_file:
            lf = '\n'
            (trn_chinese, *trn_roman) = trn_file.read().splitlines()
            trn_chinese_words = split_chinese_word(trn_chinese, dict_)

            trn_file.truncate(0)
            trn_file.seek(0)
            trn_file.write(
                f'{" ".join((word for word in trn_chinese_words))}\n'
                f'{lf.join(trn_roman)}')


def split_for_each_file(path, dict_):
    """
    資料夾下的 trn 重新斷詞 \n
    Split Chinese words for every .trn file in the folder and subfolders. \n
    Usage:
        split_for_each_file(path_to_the_folder)
    Example:
        split_for_each_file("/home/thh101u/Desktop/333_sentence_trn0629/")
    """
    for subpath in os.listdir(path):
        standard_subpath = os.path.join(path, subpath)
        if os.path.isdir(standard_subpath):
            for subfile in os.listdir(standard_subpath):
                split_file(os.path.join(standard_subpath, subfile), dict_)
        else:
            split_file(standard_subpath, dict_)

    print("Split for each file done!")


def demonstrate():
    import time
    time_loading_start = time.perf_counter()

    dict_ = ctl_dict.create_dict([
        ('dict_example/chinese_dict.txt', (ctl_dict.Word, ctl_dict.Zhuyin)),
        ('dict_example/Ch2TwRoman.txt', (ctl_dict.TL, ctl_dict.Word, ctl_dict.ETC)),
        ('dict_example/dictionary_num.txt', (ctl_dict.TL, ctl_dict.Word))])

    time_loading_end = time.perf_counter()
    print('Loading time: ', time_loading_end - time_loading_start, ' s',
          sep='', end='\n\n')

    sentence = '你 是 鬱tiau5誰 a2 無a7好 se ven 買 泡  麵 和 感 心測  試 '

    while sentence:
        time_splitting_start = time.perf_counter()
        split_result = split_chinese_word(sentence, dict_)
        time_splitting_end = time.perf_counter()

        print(split_result)

        print('\n', 'Splitting time: ',
              time_splitting_end - time_splitting_start, ' s',
              sep='', end='\n\n')

        sentence = input('Enter a sentence: ')

    print("Done!")


# Usage example
def main():
    from ctl_dict import Word, Zhuyin, TL, ETC

    sentence = '這是個範例！'

    dict_ = ctl_dict.create_dict([
        ('dict_example/chinese_dict.txt', (Word, Zhuyin)),
        ('dict_example/Ch2TwRoman.txt', (TL, Word, ETC)),
        ('dict_example/dictionary_num.txt', (TL, Word))])

    print(split_chinese_word(sentence, dict_))

if __name__ == '__main__': main()
