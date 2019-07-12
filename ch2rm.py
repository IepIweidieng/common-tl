import ctl_dict
import ctl_segment
from phonetic.common_tl import ipa_pair_to_tl_pair
from phonetic.zhuyin import zhuyin_syllable_to_ipa
from phonetic.tl import tl_syllable_to_ipa


def chinese_word_to_phonetic(word, dict_):
    """
    依照中文詞典檔轉成拼音 \n
    Convert a Chinese word into phonetic word with the dictionary.
    """
    return dict_.chinese_phonetic.get(word, [])


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
        if isinstance(syllable, ctl_dict.TL):
            ipa_word.append(tl_syllable_to_ipa(syllable, use_north, use_choan))
        elif isinstance(syllable, ctl_dict.Zhuyin):
            ipa_word.append(zhuyin_syllable_to_ipa(syllable))

    return ipa_word


def ipa_pair_to_tl(ipa_pair, use_north=False):
    """
    將國際音標轉成廣義臺羅拼音 \n
    Convert an IPA initial-final pair into common TL initial-final pair. \n
    """
    return [ipa_pair_to_tl_pair(syllable, use_north) for syllable in ipa_pair]


def chinese_to_roman(sentence, dict_, use_north=False, use_choan=False):
    """
    Convert a Chinese sentence to Roman. \n
    Side effect:
        ctl_dict.create_dict:
            fileIO (rw), os (x), sys (x), pickle (x)
            [ctl_dict.set_dict] loaded_dict (rw)
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    words_of_sentence = ctl_segment.split_chinese_word(sentence, dict_)

    tl_pair_list = []
    for word in words_of_sentence:
        # Currently only use the first phonetic of candidate phonetics
        candidate_phonetic_word = chinese_word_to_phonetic(word, dict_)[0:1]
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
        ctl_dict.set_dict:
            fileIO (rw), os (x), sys (x), pickle (x)
            [ctl_dict.set_dict] loaded_dict (rw)
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    import time
    time_loading_start = time.perf_counter()

    ctl_dict.add_dict_src(
        'dict_example/chinese_dict.txt', (ctl_dict.Word, ctl_dict.Zhuyin))
    ctl_dict.add_dict_src(
        'dict_example/Ch2TwRoman.txt', (ctl_dict.TL, ctl_dict.Word, ctl_dict.ETC))
    ctl_dict.add_dict_src(
        'dict_example/dictionary_num.txt', (ctl_dict.TL, ctl_dict.Word))

    dict_ = ctl_dict.create_dict()

    time_loading_end = time.perf_counter()
    print('Loading time: ', time_loading_end - time_loading_start, ' s',
          sep='', end='\n\n')

    use_north = False
    use_choan = False

    sentence = (
        ' 測 試  這   兒 巴  陵郡  日zZㄈ=心  謗腹非 拔 了一 個 尖  兒八   面'
        '圓  通 描  樣 兒  撥魚   兒打   通   兒 a7 khu2 lih '
    )

    while sentence:
        time_converting_start = time.perf_counter()

        words_of_sentence = ctl_segment.split_chinese_word(sentence, dict_)

        tl_pair_list = []
        output = ''
        for word in words_of_sentence:
            output = f'{output}{word}\t'

            # Currently only use the first phonetic of candidate phonetics
            candidate_phonetic_word = chinese_word_to_phonetic(word, dict_)[0:1]
            for phonetic_word in candidate_phonetic_word:
                ipa_pair_word = phonetic_word_to_ipa(phonetic_word, use_north, use_choan)
                tl_pair_word = ipa_pair_to_tl(ipa_pair_word, use_north)
                output = (
                    f'{output}'
                    f'{" ".join(map(str, phonetic_word))}\t'
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
    from ctl_dict import Word, Zhuyin, TL, ETC

    sentence = '這是個範例！'

    ctl_dict.add_dict_src('dict_example/chinese_dict.txt', (Word, Zhuyin))
    ctl_dict.add_dict_src('dict_example/Ch2TwRoman.txt', (TL, Word, ETC))
    ctl_dict.add_dict_src('dict_example/dictionary_num.txt', (TL, Word))

    dict_ = ctl_dict.create_dict()

    print(chinese_to_roman(sentence, dict_))
    print(chinese_to_roman(sentence, dict_, use_north=True))
