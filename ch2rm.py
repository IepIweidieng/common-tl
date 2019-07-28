import ctl_dict
import ctl_segment
from phonetic import ctl_util
from phonetic.common_tl import ipa_pair_to_tl_pair
from phonetic.zhuyin import zhuyin_syllable_to_ipa
from phonetic.tl import tl_syllable_to_ipa
from phonetic.thrs import thrs_syllable_to_ipa

lang_opt = ctl_util.lang_opt
Lang = ctl_util.def_lang(
      ['hokkien', 'mandarin', 'hakka', 'common_tl'])
lang = ctl_util.namedtuple_ctor(Lang, default=lang_opt())


def chinese_word_to_phonetic(word, dict_):
    """
    依照中文詞典檔轉成拼音 \n
    Convert a Chinese word into phonetic word with the dictionary.
    """
    return dict_.chinese_phonetic.get(word, [])


def phonetic_word_to_ipa(phonetic_word, dialects=lang()):
    """
    將拼音轉成國際音標 \n
    Convert a phonetic word into IPA. \n
    Side effect:
        tl_word_to_ipa: tl_syllable_to_ipa: IO (w)
        zhuyin_word_to_ipa: zhuyin_syllable_to_ipa: IO (w)
        thrs_word_to_ipa: thrs_syllable_to_ipa: IO (w)
    """
    ipa_word = []

    for syllable in phonetic_word:
        if isinstance(syllable, ctl_dict.TL):
            ipa_word.append(
                tl_syllable_to_ipa(syllable, **getattr(dialects, 'hokkien')._asdict()))
        elif isinstance(syllable, ctl_dict.Zhuyin):
            ipa_word.append(
                zhuyin_syllable_to_ipa(syllable, **getattr(dialects, 'mandarin')._asdict()))
        elif isinstance(syllable, ctl_dict.THRS):
            ipa_word.append(
                thrs_syllable_to_ipa(syllable, **getattr(dialects, 'hakka')._asdict()))

    return ipa_word


def ipa_pair_to_tl(ipa_pair, *args, **kwargs):
    """
    將國際音標轉成廣義臺羅拼音 \n
    Convert an IPA initial-final pair into common TL initial-final pair. \n
    """
    return [ipa_pair_to_tl_pair(syllable, *args, **kwargs) for syllable in ipa_pair]


def chinese_to_roman(sentence, dict_, dialects=lang()):
    """
    Convert a Chinese sentence to Roman. \n
    Side effect:
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    words_of_sentence = ctl_segment.split_chinese_word(sentence, dict_)

    tl_pair_list = []
    for word in words_of_sentence:
        # Currently only use the first phonetic of candidate phonetics
        candidate_phonetic_word = chinese_word_to_phonetic(word, dict_)[0:1]
        for phonetic_word in candidate_phonetic_word:
            ipa_pair_word = phonetic_word_to_ipa(phonetic_word, dialects)
            tl_pair_word = ipa_pair_to_tl(ipa_pair_word,
                **(getattr(dialects, 'common_tl')._asdict()
                    or getattr(dialects, 'hokkien')._asdict()))

            tl_pair_list.append(tl_pair_word)

    return tl_pair_list


def _print_pairs(pairs):
    return ' '.join((''.join(pair_item) for pair_item in pairs))


def demonstrate():
    """
    Side effect: IO (w), time (x)
        ctl_dict.DictSrc.create_dict:
            fileIO (rw), os (x), sys (x), pickle (x)
        zhuyin_word_to_ipa:
            zhuyin_syllable_to_ipa: IO (w)
    """
    import time
    time_loading_start = time.perf_counter()

    dict_src = ctl_dict.DictSrc()
    dict_src.add_dict_src(
        'dict_example/chinese_dict.txt', (ctl_dict.Word, ctl_dict.Zhuyin))
    dict_src.add_dict_src(
        'dict_example/Ch2TwRoman.txt', (ctl_dict.TL, ctl_dict.Word, ctl_dict.ETC))
    dict_src.add_dict_src(
        'dict_example/dictionary_num.txt', (ctl_dict.TL, ctl_dict.Word))

    dict_ = dict_src.create_dict()

    time_loading_end = time.perf_counter()
    print('Loading time: ', time_loading_end - time_loading_start, ' s',
          sep='', end='\n\n')

    dialect = 'chiang'
    variant = 'southern'

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
                ipa_pair_word = phonetic_word_to_ipa(
                    phonetic_word, lang(hokkien=lang_opt(dialect, variant)))
                tl_pair_word = ipa_pair_to_tl(ipa_pair_word, dialect, variant)
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
    from ctl_dict import Word, Zhuyin, TL, THRS, ETC

    sentence = '這是個範例！'

    dict_src = (ctl_dict.DictSrc()
          .add_dict_src('dict_example/chinese_dict.txt', (Word, Zhuyin))
          .add_dict_src('dict_example/Ch2TwRoman.txt', (TL, Word, ETC))
          .add_dict_src('dict_example/dictionary_num.txt', (TL, Word)))

    dict_ = dict_src.create_dict()

    print(chinese_to_roman(sentence, dict_))
    print(chinese_to_roman(sentence, dict_,
        dialects=lang(hokkien=lang_opt(variant='northern'))))
