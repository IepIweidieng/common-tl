import common_tl
import tl_dict
import tl_split
import tl_util
from common_tl import ipa_pair_to_tl_pair
from tl_zhuyin import zhuyin_syllable_to_ipa
from tl_tl import tl_syllable_to_ipa


def chinese_word_to_phonetic(word):
    """
    依照中文詞典檔轉成拼音 \n
    Convert a Chinese word into phonetic word with the dictionary. \n
    Side effect: tl_dict.chinese_phonetic (r) \n
    """
    return tl_dict.chinese_phonetic.get(word, [])


def phonetic_word_to_ipa(phonetic_word, use_north=False, use_choan=False):
    """
    將拼音轉成國際音標 \n
    Convert a phonetic word into IPA. \n
    Side effect:
        tl_word_to_ipa: tl_syllable_to_ipa: IO (w)
        zhuyin_word_to_ipa: zhuyin_syllable_to_ipa: IO (w)
    """
    ipa_word = []

    for syllable in phonetic_word:
        if tl_util.find_first_non_roman(syllable) == len(syllable):
            ipa_word.append(tl_syllable_to_ipa(syllable, use_north, use_choan))
        else:
            ipa_word.append(zhuyin_syllable_to_ipa(syllable))

    return ipa_word


def ipa_pair_to_tl(ipa_pair, use_north=False):
    """
    將國際音標轉成廣義臺羅拼音 \n
    Convert an IPA initial-final pair into common TL initial-final pair. \n
    """
    return [ipa_pair_to_tl_pair(syllable, use_north) for syllable in ipa_pair]


def chinese_to_roman(sentence, use_north=False, use_choan=False):
    """
    Convert a Chinese sentence to Roman. \n
    Side effect:
        tl_dict.create_dict:
            fileIO (rw), os (x), sys (x), pickle (x)
            [tl_dict.set_dict] loaded_dict (rw),
            tl_dict.chinese_phonetic (rw)
        tl_split.split_chinese_word:
            tl_dict.chinese_phonetic (r),
            tl_dict.max_word_length (r)
        chinese_word_to_phonetic:
            tl_dict.chinese_phonetic (r)
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    words_of_sentence = tl_split.split_chinese_word(sentence)

    tl_pair_list = []
    for word in words_of_sentence:
        # Currently only use the first phonetic of candidate phonetics
        candidate_phonetic_word = chinese_word_to_phonetic(word)[0:1]
        for phonetic_word in candidate_phonetic_word:
            ipa_pair_word = phonetic_word_to_ipa(phonetic_word, use_north, use_choan)
            tl_pair_word = ipa_pair_to_tl(ipa_pair_word, use_north)

            tl_pair_list.append(tl_pair_word)

    return tl_pair_list


def _print_pairs(pairs):
    return ' '.join((''.join(pair_item) for pair_item in pairs))


def demonstrate():
    """
    Side effect: IO (w), time (x)
        tl_dict.set_dict:
            fileIO (rw), os (x), sys (x), pickle (x)
            [tl_dict.set_dict] loaded_dict (rw),
            chinese_phonetic (rw)
        tl_split.split_chinese_word:
            tl_dict.chinese_phonetic (r),
            tl_dict.max_word_length (r)
        chinese_word_to_phonetic:
            tl_dict.chinese_phonetic (r)
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    import time
    time_loading_start = time.perf_counter()

    tl_dict.add_dict_src('chinese_dict.txt')
    tl_dict.add_dict_src(
        'Ch2TwRoman.txt', (tl_dict.TL, tl_dict.WORD, tl_dict.ETC))
    tl_dict.add_dict_src(
        'dictionary_num.txt', (tl_dict.TL, tl_dict.WORD))

    tl_dict.create_dict()

    time_loading_end = time.perf_counter()
    print('Loading time: ', time_loading_end - time_loading_start, ' s',
          sep='', end='\n\n')

    use_north = False

    sentence = (
        ' 測 試  這   兒 巴  陵郡  日zZㄈ=心  謗腹非 拔 了一 個 尖  兒八   面'
        '圓  通 描  樣 兒  撥魚   兒打   通   兒 a7 khu2 lih '
    )

    while sentence:
        time_converting_start = time.perf_counter()

        words_of_sentence = tl_split.split_chinese_word(sentence)

        tl_pair_list = []
        output = ''
        for word in words_of_sentence:
            output = f'{output}{word}\t'

            # Currently only use the first phonetic of candidate phonetics
            candidate_phonetic_word = chinese_word_to_phonetic(word)[0:1]
            for phonetic_word in candidate_phonetic_word:
                ipa_pair_word = phonetic_word_to_ipa(phonetic_word)
                tl_pair_word = ipa_pair_to_tl(ipa_pair_word, use_north)
                output = (
                    f'{output}'
                    f'{" ".join(phonetic_word)}\t'
                    f'{_print_pairs(ipa_pair_word)}\t'
                    f'{_print_pairs(tl_pair_word)}\t')

                tl_pair_list.append(tl_pair_word)
            output = f'{output}\n'

        time_converting_end = time.perf_counter()

        print(output)
        print(tl_pair_list)

        print('\n', 'Converting time: ',
              time_converting_end - time_converting_start, ' s',
              sep='', end='\n\n')

        sentence = input('Enter a sentence: ')

    print('main done!')


# Usage example
if __name__ == '__main__':
    from tl_dict import WORD, ZHUYIN, TL, PHONETIC, ETC

    sentence = '這是個範例！'

#    tl_dict.add_dict_src('chinese_dict.txt', (WORD, ZHUYIN))
#    tl_dict.add_dict_src('Ch2TwRoman.txt', (TL, WORD, ETC))
    tl_dict.add_dict_src('dictionary_num.txt', (TL, WORD))

    tl_dict.create_dict()

    print(chinese_to_roman(sentence))
    print(chinese_to_roman(sentence, use_north=True))
