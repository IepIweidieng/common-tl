from typing import List, Optional, Tuple, Type, Union
import ctl_dict
import ctl_segment
from phonetic import ctl_util
from phonetic.common_tl import ipa_pair_to_tl_pair
from phonetic.zhuyin import zhuyin_syllable_to_ipa
from phonetic.tl import tl_syllable_to_ipa
from phonetic.thrs import thrs_syllable_to_ipa
from phonetic.common_tl import IpaPair, CtlPair

PhoneticSylList = Union[List[Union[ctl_dict._Phonetic, str]], List[ctl_dict._Phonetic], List[str]]
IpaWord = List[IpaPair]
CtlWord = List[CtlPair]

lang_opt = ctl_util.lang_opt
Lang = ctl_util.def_lang(
      ['hokkien', 'mandarin', 'hakka', 'common_tl'])
lang = ctl_util.namedtuple_ctor(Lang, default=lang_opt())


def chinese_word_to_phonetic(word: str, dict_: ctl_dict.CtlDict) -> ctl_dict.DictPronounCandList:
    """
    依照中文詞典檔轉成拼音 \n
    Convert a Chinese word into phonetic word with the dictionary.
    """
    return dict_.chinese_phonetic.get(word, [])


def phonetic_word_to_ipa(phonetic_word: PhoneticSylList, dialects: Lang=lang(), phonetic: Optional[Type[ctl_dict._Phonetic]]=None) -> IpaWord:
    """
    將拼音轉成國際音標 \n
    Convert a phonetic word into IPA.
    """
    ipa_word: IpaWord = []

    for syllable in phonetic_word:
        if isinstance(syllable, str):
            assert phonetic is not None
            syllable = phonetic(syllable)
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


def ipa_pair_to_tl(ipa_pair: IpaWord, *args, **kwargs) -> CtlWord:
    """
    將國際音標轉成廣義臺羅拼音 \n
    Convert an IPA initial-final pair into Common TL initial-final pair.
    """
    return [ipa_pair_to_tl_pair(syllable, *args, **kwargs) for syllable in ipa_pair]

def phonetic_word_to_tl(phonetic_word: PhoneticSylList, dialects: Lang=lang(), phonetic: Optional[Type[ctl_dict._Phonetic]]=None) -> CtlWord:
    """
    Convert a word in phonetic notation to Common TL.
    """
    ipa_pair_word = phonetic_word_to_ipa(phonetic_word, dialects, phonetic)
    return ipa_pair_to_tl(ipa_pair_word,
        **(getattr(dialects, 'common_tl')._asdict()
            or getattr(dialects, 'hokkien')._asdict()))


def chinese_to_roman(sentence: str, dict_: ctl_dict.CtlDict, dialects: Lang=lang()) -> List[CtlWord]:
    """
    Convert a Chinese sentence to Common TL.
    """
    words_of_sentence = ctl_segment.split_chinese_word(sentence, dict_)

    tl_pair_list: List[CtlWord] = []
    for word in words_of_sentence:
        # Currently only use the first phonetic of candidate phonetics
        candidate_phonetic_word = chinese_word_to_phonetic(word, dict_)[0:1]
        for phonetic_word in candidate_phonetic_word:
            tl_pair_list.append(phonetic_word_to_tl(phonetic_word, dialects))

    return tl_pair_list


def _print_pairs(pairs: List[Tuple[str, str]]) -> str:
    return ' '.join((''.join(pair_item) for pair_item in pairs))

def phonetic_to_tl(sentence: str, dialects: Lang=lang(), phonetic: Type[ctl_dict._Phonetic]=ctl_dict.TL) -> List[CtlWord]:
    """
    Convert a TL-like phonetic sentence to Common TL.
    """
    # Handle punctuation and capitalization before splitting
    for punc in ('.', ',', ';', ':', '"', "'", '?', '!', '─', '—'):
        sentence = sentence.replace(punc, '')
    words_of_sentence = sentence.lower().split()

    tl_pair_list: List[CtlWord] = []
    for word in words_of_sentence:
        # Handle neutral tone before splitting
        word = word.replace('--', ' 0').replace('-', ' ').replace(' 0', ' --')
        phonetic_word = word.split()
        tl_pair_list.append(phonetic_word_to_tl(phonetic_word, dialects, phonetic))

    return tl_pair_list


def demonstrate() -> None:
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

        tl_pair_list: List[CtlWord] = []
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
def main() -> None:
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

if __name__ == '__main__': main()
