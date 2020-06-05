import hashlib
import os
import pickle
import re
import sys
from collections import UserString

import phonetic.ctl_util as ctl_util

# Dictionary format tokens
class Word(UserString): pass
class _Phonetic(UserString): pass
class _RomanPhonetic(_Phonetic): pass
class Zhuyin(_Phonetic): pass
class TaiwaneseRomanization(_RomanPhonetic): pass
TL = TaiwaneseRomanization
class TaiwaneseHakkaRomanization(_RomanPhonetic): pass
THRS = TaiwaneseHakkaRomanization
class ETC(UserString): pass

_FORMAT_TYPE_LIST = {
    'Word': Word,
    'Zhuyin': Zhuyin,
    'TaiwaneseRomanization': TaiwaneseRomanization,
    'TaiwaneseHakkaRomanization': TaiwaneseHakkaRomanization,
    'ETC': ETC
}

_FORMAT_TYPE_ABBRV_LIST = {
    'Word': Word,
    'Zhuyin': Zhuyin,
    'TL': TaiwaneseRomanization,
    'THRS': TaiwaneseHakkaRomanization,
    'ETC': ETC
}


def parse_line_in_format(line, format_):
    """
    Side effect: ValueError (x),
        Word (r), Zhuyin (r), TL (r), THRS (r), _Phonetic (r), ETC (r)
    """
    etcs = []
    splited = line.split('\t')

    for (splited_item, parse_item) in zip(splited, format_):
        if parse_item in _FORMAT_TYPE_LIST:
            parse_item = _FORMAT_TYPE_LIST[parse_item]
        elif parse_item in _FORMAT_TYPE_ABBRV_LIST:
            parse_item = _FORMAT_TYPE_ABBRV_LIST[parse_item]

        if parse_item not in _FORMAT_TYPE_LIST.values():
            raise ValueError(
                f'Invalid parse item \'{parse_item}\'.  '
                f'Parse item must be one of {", ".join(_FORMAT_TYPE_ABBRV_LIST.keys())}')
        elif parse_item is Word:
            word = Word(splited_item)
        elif issubclass(parse_item, _Phonetic):
            phonetic_type = parse_item
            phonetic = phonetic_type(splited_item)
        elif parse_item is ETC:
            etcs.append(ETC(splited_item))

    return (word, phonetic, phonetic_type, etcs)


def create_line_from_format(phrase_data, format_):
    """Side effect: Word (r), Zhuyin (r), TL (r), THRS (r), _Phonetic (r), ETC (r)"""
    (word, phonetic, *additional) = (phrase_data)
    etcs = len(additional) > 1 and additional[1] or []
    etcs_len = len(etcs)
    etcs_index = 0
    out_content = []

    for parse_item in format_:
        if parse_item in _FORMAT_TYPE_LIST:
            parse_item = _FORMAT_TYPE_LIST[parse_item]
        elif parse_item in _FORMAT_TYPE_ABBRV_LIST:
            parse_item = _FORMAT_TYPE_ABBRV_LIST[parse_item]

        if parse_item is Word:
            out_content.append(word)
        elif issubclass(parse_item, _Phonetic):
            out_content.append(phonetic)
        elif parse_item is ETC:
            etcs_item = ''
            if etcs_index < etcs_len:
                etcs_item = etcs[etcs_index]
                etcs_index += 1

            out_content.append(etcs_item)

    return '\t'.join(map(str, out_content))


_PUNCTUATION_LIST = {'。', '，', '、', '；', '：', '「', '」',
                     '『', '』', '？', '！', '─', '…', '《', '》',
                     '〈', '〉', '．', '˙', '—', '～'}


def preprocess_dict(dict_path, format_):
    """
    中文詞典檔前處理 \n
    Do pre-process on a dictionary text file \n
    Side effect: IO (w), fileIO (rw), os (x), sys (x), re (x)
                 parse_line_in_format: ValueError (x),
                                       Word (r),
                                       Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                                       ETC (r)
                 create_line_from_format: Word (r),
                                          Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                                          ETC (r)
    """
    # Read un-processed file
    with open(dict_path, 'r', encoding='utf8') as in_file:
        file_content = in_file.read().splitlines()

    # Remove duplicated items
    file_content = list(dict.fromkeys(file_content))

    # For processing file content
    out_content = []
    markup_ref_pattern = re.compile(r'^.*?&[^\t]+?;.*?$')
    multi_space_pattern = re.compile(r' {2,}')
    parenthesis_pattern = re.compile(r'[\(（].*?[\)）]')

    # For warning of invalid contents
    invalid_word_warnings = []
    mismatched_syllable_count_warnings = []

    # Process each line in the file
    for (pos, line) in enumerate(file_content):
        # Ensure there are no file references in Chinese word
        if markup_ref_pattern.fullmatch(line):
            warning = (
                f'Warning: In \'{dict_path}\': at line {pos}:\n'
                f'\t\'{line}\':\n'
                f'\tContains non-word characters.  Skipped.\n')
            invalid_word_warnings.append(warning)
            print(warning, file=sys.stderr, flush=True)
            continue

        # Handle spaces
        new_line = multi_space_pattern.sub(' ', line.replace('　', ' '))

        # Strip parentheses and unnecessary spaces
        (word, phonetic, phonetic_type, etcs) = (
            parse_line_in_format(new_line, format_))
        new_word = parenthesis_pattern.sub('', str(word)).strip()
        new_phonetic = parenthesis_pattern.sub('', str(phonetic)).strip()

        if issubclass(phonetic_type, _RomanPhonetic):
            # Decompose precomposed characters
            new_phonetic = ctl_util.normalize(new_phonetic)

        phonetic_syllables = new_phonetic.split(' ')

        # Handle punctuations
        punctuation_count = 0
        for character in new_word:
            if character in _PUNCTUATION_LIST:
                punctuation_count += 1

        word_len = 0
        is_prev_char_roman = False
        for char in f'{new_word} ':
            if ctl_util.is_char_roman(char) and (char != ' ' and char != '-'):
                is_prev_char_roman = True
            else:
                if is_prev_char_roman:
                    word_len += 1
                if not (char == ' ' or char == '-'):
                    word_len += 1
                is_prev_char_roman = False
        word_len -= punctuation_count

        # Handle erization
        erization_count = 0
        if issubclass(phonetic_type, Zhuyin):
            for syllable in phonetic_syllables:
                if len(syllable) > 1 and syllable.endswith('ㄦ'):
                    erization_count += 1

        syllable_len = len(phonetic_syllables)

        # Ensure the length of Chinese word match the phonetic syllables
        if syllable_len + erization_count != word_len:
            warning = (
                f'Warning: In \'{dict_path}\': at line {pos}:\n'
                f'\t\'{line}\':\n'
                f'\tChinese word length and phonetic syllable count mismatched.'
                f'  Skipped.\n'
            )
            mismatched_syllable_count_warnings.append(warning)
            print(warning, file=sys.stderr, flush=True)
            continue

        out_content.append(create_line_from_format(
            (new_word, new_phonetic, phonetic_type, etcs), format_))

    # Write processed dictionary to file
    with open(f'{dict_path}{PROCESSED_SUFFIX}',
              'w', encoding='utf8', newline='\n') as out_file:
        out_file.write('\n'.join(out_content))

    # Write Warnings to files
    for (warning, warning_name) in (
            (invalid_word_warnings, 'invalid_word_warnings'),
            (mismatched_syllable_count_warnings,
             'mismatched_syllable_count_warnings')):
        warning_file = f'{dict_path}_{warning_name}'
        if warning:
            with open(warning_file,
                      'w', encoding='utf8', newline='\n') as warn_file:
                warn_file.write('\n'.join(warning))
        elif os.path.isfile(warning_file):
            os.remove(warning_file)


# Data structure:
#   chinese_phonetic: {word: candidate_phonetics, word2: candidate_phonetics2, ...}
#   candidate_phonetics: [phonetic1, phonetic2, ...]
#   phonetic: [syllable1, syllable2, ...]
#   Overview: {word: [[syllable11, syllable12], [syllable21, syllable22]], ...}
class CtlDict:
    def __init__(self):
        self.chinese_phonetic = {}
        self.max_word_length = 0

PROCESSED_SUFFIX = '_out'
PICKLED_SUFFIX = '.pickle'


# Used on _
# Side effect: func (x)
def _call(func, *arg, **kwarg): return func(*arg, **kwarg)

@_call
def _():
    # Used by class SrcDict

    # Public functions

    global create_dict

    def create_dict(path_list, *args, **kwargs):
        """
        載入指定詞典 \n
        Load the specified dictionaries. \n
        Side effect: set_dict_src: __dict_src (w)
            create_dict: os (x), DEFAULT_FORMAT (r)
            preprocess_dict:
                IO (w), fileIO (rw), sys (x), re (x)
            _get_dict_data_from_dump: IO (w), fileIO (r),
                os.path (x), sys (x),
                pickle (x)
                BasicUnpickler:
                        pickle (x)
            _get_dict_data_from_text: fileIO (r),
                Word (r),
                Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                ETC (r)
            _create_dict_data_dump: fileIO (w), pickle (x)
        """
        res = DictSrc()
        res.set_dict_src(path_list)
        return res.create_dict(*args, **kwargs)
    create_dict = create_dict

    # Private functions

    class _BasicUnpickler(pickle.Unpickler):
        """
        A safer unpickler which allows pickling only the format type classes. \n
        Side effect: pickle (x)
        """

        def find_class(self, module, name):
            if module == 'ctl_dict' and name in _FORMAT_TYPE_LIST:
                return _FORMAT_TYPE_LIST[name]
            raise pickle.UnpicklingError(
                f'Global \'{module}.{name}\' is forbidden')

    def _get_dict_set_file(path_list):
        """Side effect: hashlib (x)"""
        hashed_path_list = hashlib.md5(str(path_list).encode()).hexdigest()
        return f'dict_set_{hashed_path_list}{PICKLED_SUFFIX}'

    def _get_src_path(dict_src_item):
        if isinstance(dict_src_item, str):
            return dict_src_item

        (dict_src_item_path, _) = dict_src_item
        return dict_src_item_path

    def _get_dict_data_from_text(source, format_):
        """
        讀取詞典檔並建立詞典資料 \n
        Parse and create dictionary data from a dictionary text file. \n
        Side effect: fileIO (r),
            parse_line_in_format: ValueError (x),
                Word (r),
                Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                ETC (r)
        """
        text_chinese_phonetic = {}
        text_max_word_length = 0

        with open(source, 'r', encoding='utf8') as dict_file:
            dict_content = dict_file.read().splitlines()

        for phrase in dict_content:
            (word, phonetic, phonetic_type, _) = (
                parse_line_in_format(phrase, format_))

            phonetic_syllables = phonetic.split(' ')
            new_phonetic_syllables = [
                phonetic_type(syllable) for syllable in phonetic_syllables]

            if word in text_chinese_phonetic:
                # Prevent duplicating
                if not phonetic_syllables in text_chinese_phonetic[word]:
                    text_chinese_phonetic[word].append(new_phonetic_syllables)
            else:
                text_max_word_length = max(len(word), text_max_word_length)
                text_chinese_phonetic.update({word: [new_phonetic_syllables]})

        return (source, text_chinese_phonetic, text_max_word_length)

    def _create_dict_data_dump(dict_data, path):
        """
        將詞典資料傾印到檔案 \n
        Dump the content of a dictionary data to a file. \n
        Side effect: fileIO (w), pickle (x)
            get_dict_set_file: hashlib (x)
        """
        out_path = path
        if not isinstance(path, str):
            out_path = _get_dict_set_file(path)
        with open(out_path, 'wb') as pickle_file:
            pickler_ = pickle.Pickler(pickle_file, pickle.HIGHEST_PROTOCOL)
            pickler_.dump(dict_data)

    def _is_path_list_eq(lhs, rhs, lhs_suffix='', rhs_suffix=''):
        """Side effect: os.path (x)"""
        if not isinstance(lhs, str) and not isinstance(rhs, str):
            lhs_src_paths = map(_get_src_path, lhs)
            rhs_src_paths = map(_get_src_path, rhs)
            return all(
                os.path.realpath(f'{lhs_item}{lhs_suffix}')
                == os.path.realpath(f'{rhs_item}{rhs_suffix}')
                for (lhs_item, rhs_item) in zip(lhs_src_paths, rhs_src_paths)
            )
        return f'{lhs}{lhs_suffix}' == f'{rhs}{rhs_suffix}'

    def _get_dict_data_from_dump(path):
        """
        從先前傾印出的檔案取得詞典資料 \n
        Get directionary data from a dumped data file. \n
        Side effect: IO (w), fileIO (r), os.path (x), sys (x),
            pickle.UnpicklingError (x)
            BasicUnpickler: pickle.unpickler (x)
            get_dict_set_file: hashlib (x)
        """
        src_path = path
        if isinstance(path, str):
            in_path = path
            if PICKLED_SUFFIX and path.endswith(PICKLED_SUFFIX):
                src_path = path[:-len(PICKLED_SUFFIX)]
        else:
            in_path = _get_dict_set_file(path)

        if os.path.isfile(in_path):
            with open(in_path, 'rb') as pickle_file:
                unpickler_ = _BasicUnpickler(pickle_file)
                try:
                    (source, new_chinese_phonetic, new_max_word_length) = (
                        unpickler_.load())
                except pickle.UnpicklingError as e:
                    print(str(type(e))[8:-2], ': ', e, file=sys.stderr)
                    return (None, in_path)
                if (_is_path_list_eq(source, src_path)):
                    return (
                        (source, new_chinese_phonetic, new_max_word_length),
                        in_path)
                return ((source, None, None), in_path)
        return (None, None)

    def _check_dict_data(dict_data, dict_data_path, __dict_src):
        if dict_data is None:
            if dict_data_path is not None:
                print('Warning: The dump file \'', dict_data_path,
                        '\' can not be loaded.  Regenerated.',
                        sep='', file=sys.stderr, flush=True)
            return False

        (data_source, data_chinese_phonetic, _) = dict_data

        if data_chinese_phonetic is not None:
            return True

        if data_source is not None:
            if isinstance(__dict_src, str):
                dict_src_text = __dict_src
            else:
                dict_src_text = '\', \''.join(map(_get_src_path, __dict_src))

            if isinstance(__dict_src, str):
                data_source_text = data_source
            else:
                data_source_text = '\', \''.join(
                    map(_get_src_path, data_source))

            print('Warning: The dump file \'', dict_data_path,
                    '\' is meant for \'', dict_src_text, '\',\n',
                    '    but its source is \'', data_source_text, '\',\n',
                    '    which mismatches.  Regenerated.',
                    sep='', file=sys.stderr, flush=True)
        return False

    global DictSrc

    class DictSrc:
        """
        詞典檔紀錄清單 \n
        The dictionary entry list. \n
        Side effect: IO (w), fileIO (rw), os (x), sys (x) re (x), pickle (x)
        """
        def __init__(self):
            self.__loaded_dict = []
            self.__dict_src = []

        # Public methods

        def add_dict_src(self, path, format_):
            """
            新增要讀取的詞典檔 \n
            Add the dictionary file to the dictionary source. \n
            Side effect: DEFAULT_FORMAT (r)
            """
            self.__dict_src.append((path, format_))
            return self

        def reset_dict_src(self):
            """
            重設要讀取的詞典檔 \n
            Reset the dictionary source. \n
            """
            self.__dict_src.clear()
            return self

        def set_dict_src(self, path_list):
            """
            指定要載入的詞典 \n
            Specify the dictionaries to be loaded. \n
            """
            self.__dict_src = path_list

            if isinstance(path_list, str):
                self.__dict_src = [path_list]
            return self

        def create_dict(self, reprocess=False, recreate_dump=False):
            """
            載入詞典的對應傾印檔； \n
            若無，則讀取已經過前處理之詞典檔，並生成傾印檔；
            若無，則對詞典檔進行前處理
            Load the dictionary data from the corresponding dumped data file. \n
            Parse and create dictionary data from \n
            the pre-processed dictionary text file if needed.
            Pre-process the dictionary text file if needed. \n
            Side effect: os (x), DEFAULT_FORMAT (r)
                preprocess_dict: IO (w), fileIO (rw), os (x), sys (x), re (x)
                    parse_line_in_format: ValueError (x),
                        Word (r),
                        Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                        ETC (r)
                    create_line_from_format:
                        Word (r),
                        Zhuyin (r), TL (r), THRS (r), _Phonetic (r),
                        ETC (r)
                _get_dict_data_from_dump:
                    IO (w), fileIO (r), os.path (x), sys (x),
                    pickle.UnpicklingError (x)
                    BasicUnpickler:
                            pickle.unpickler (x)
                    get_dict_set_file: hashlib (x)
                _get_dict_data_from_text:
                    fileIO (r),
                    Word (r), _Phonetic (r), ETC (r)
                _create_dict_data_dump:
                    fileIO (w), pickle (x)
                    get_dict_set_file: hashlib (x)
            """
            dict_ = CtlDict()

            if not (reprocess or recreate_dump):
                # Load the dumped data of the dictionaries to be loaded if exists
                (dict_data, dict_data_file) = _get_dict_data_from_dump(self.__dict_src)
                if _check_dict_data(dict_data, dict_data_file, self.__dict_src):
                    self.__load_dict_data(dict_, dict_data)
                    return dict_

            will_create_dict_data_dump = True
            for path_item in self.__dict_src:
                (path, format_) = path_item
                dict_data_file = f'{path}{PICKLED_SUFFIX}'

                # Keep path to refer the pre-processed dictionary text file
                if not path.endswith(PROCESSED_SUFFIX):
                    path_unprocessed = path
                    path = f'{path}{PROCESSED_SUFFIX}'
                    dict_data_file = f'{path}{PICKLED_SUFFIX}'

                # If the dictionary text file is un-processed,
                #   do pre-processing on it
                if not reprocess and os.path.isfile(path):
                    # If the dictionary dump data needs to be re-created,
                    # do not load it
                    if not recreate_dump:
                        # If the dictionary is loaded,
                        # do not load and do not create the dump data of it again
                        if path in self.__loaded_dict:
                            continue
                        # Load the dictionary dump data if exists
                        if os.path.isfile(dict_data_file):
                            (dict_data, _) = _get_dict_data_from_dump(
                                dict_data_file)
                            if _check_dict_data(dict_data, dict_data_file, path):
                                self.__load_dict_data(dict_, dict_data)
                elif os.path.isfile(path_unprocessed):
                    preprocess_dict(path_unprocessed, format_)

                if os.path.isfile(path):
                    # Create the dictionary from scratch
                    dict_data = _get_dict_data_from_text(path, format_)
                    _create_dict_data_dump(dict_data, dict_data_file)
                    self.__load_dict_data(dict_, dict_data)
                else: will_create_dict_data_dump = False

            if will_create_dict_data_dump:
                _create_dict_data_dump(
                    (self.__dict_src, dict_.chinese_phonetic, dict_.max_word_length), self.__dict_src)
            return dict_

        # Private methods

        def __load_dict_data(self, dict_, dict_data,):
            """
            載入詞典檔到詞典表中 \n
            Load dictionary data into dictionary list. \n
            """
            (path, new_chinese_phonetic, new_max_word_length) = dict_data
            dict_.max_word_length = max(new_max_word_length, dict_.max_word_length)

            if self.__loaded_dict:
                for (word, phonetics) in new_chinese_phonetic.items():
                    if word in dict_.chinese_phonetic:
                        # Prevent duplicating
                        if not phonetics in dict_.chinese_phonetic[word]:
                            dict_.chinese_phonetic[word].extend(phonetics)
                    else:
                        dict_.chinese_phonetic.update({word: phonetics})
            else:
                dict_.chinese_phonetic = new_chinese_phonetic

            self.__loaded_dict.append(path)

    DictSrc = DictSrc
