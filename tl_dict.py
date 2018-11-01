import os
import pickle
import re
import sys

# Data structure:
#   chinese_zhuyin: {word: candidate_zhuyins, word2: candidate_zhuyins2, ...}
#   candidate_zhuyins: [zhuyin1, zhuyin2, ...]
#   zhuyin: [syllable1, syllable2, ...]
#   Overview: {word: [[syllable11, syllable12], [syllable21, syllable22]], ...}
chinese_zhuyin = {}


# 中文詞典檔前處理
# Do pre-process on a dictionary text file
# Side effect: IO (w), fileIO (rw), sys (x), re (x)

def preprocess_dict(dict_path):
    # Read un-processed file
    with open(dict_path, 'r', encoding='utf8') as in_file:
        file_content = in_file.read().splitlines()

    # For processing file content
    out_content = []
    file_ref_pattern = re.compile(r'^.*?&.+?\..+?;.*?$')
    multi_space_pattern = re.compile(r' {2,}')
    parenthesis_pattern = re.compile(r'[\(（].*?[\)）]')

    # For warning of invalid contents
    invalid_word_warnings = []
    mismatched_syllable_count_warnings = []

    # For warning of process-needing contents
    duplicate_zhuyin_warnings = []

    # Process each line in the file
    for (pos, line) in enumerate(file_content):
        # Ensure there are no file references in Chinese word
        if file_ref_pattern.fullmatch(line):
            warning = (
                f'Warning: In \'{dict_path}\': at line {pos}:\n'
                f'\t\'{line}\':\n'
                f'\tContains non-word characters.  Skipped.\n').expandtabs()
            invalid_word_warnings.append(warning)
            print(warning, file=sys.stderr, flush=True)
            continue

        # Handle spaces
        new_line = parenthesis_pattern.sub(
            '', multi_space_pattern.sub(' ', line.replace('　', ' ')))

        # Strip unnecessary spaces
        (word, zhuyin) = new_line.split('\t')
        new_word = word.strip()
        zhuyin_syllables = zhuyin.strip().split(' ')

        # Handle punctuations
        punctuation_count = 0
        for character in new_word:
            if character in {'。', '，', '、', '；', '：', '「', '」',
                             '『', '』', '？', '！', '─', '…', '《', '》',
                             '〈', '〉', '．', '˙', '—', '～'}:
                punctuation_count += 1

        # Handle erization
        erization_count = 0
        for syllable in zhuyin_syllables:
            if len(syllable) > 1 and syllable.endswith('ㄦ'):
                erization_count += 1

        word_len = len(new_word) - punctuation_count
        zhuyin_len = len(zhuyin_syllables)

        # If the Zhuyin duplicates, split the Zhuyin into two,
        #   and associate each one to a copy of the Chinese word
        if (not zhuyin_len % 2 and not erization_count % 2
                and (zhuyin_len + erization_count) / 2 == word_len):
            (splited_0, splited_1) = (
                (f'{new_word}\t'
                 f'{" ".join(zhuyin_syllables[: zhuyin_len // 2])}'),
                (f'{new_word}\t'
                 f'{" ".join(zhuyin_syllables[zhuyin_len // 2:])}'))
            out_content.append(splited_0)
            out_content.append(splited_1)

            warning = (
                f'Warning: In \'{dict_path}\': at line {pos}:\n'
                f'\t\'{line}\':\n'
                f'\tZhuyin word duplicated.  Splited to\n'
                f'\t\'{splited_0}\' and\n'
                f'\t\'{splited_1}\'\n').expandtabs()
            duplicate_zhuyin_warnings.append(warning)
            print(warning, file=sys.stderr, flush=True)
            continue

        # Ensure the length of Chinese word match the Zhuyin syllables
        if zhuyin_len + erization_count != word_len:
            warning = (
                f'Warning: In \'{dict_path}\': at line {pos}:\n'
                f'\t\'{line}\':\n'
                f'\tChinese word length and Zhuyin syllable count mismatched.'
                f'  Skipped.\n'
            ).expandtabs()
            mismatched_syllable_count_warnings.append(warning)
            print(warning, file=sys.stderr, flush=True)
            continue

        out_content.append(new_line)

    # Write processed dictionary to file
    with open(f'{dict_path}_out', 'w', encoding='utf8') as out_file:
        out_file.write('\n'.join(out_content))

    # Write Warnings to files

    for (warning, warning_name) in (
            (invalid_word_warnings, 'invalid_word_warnings'),
            (mismatched_syllable_count_warnings,
             'mismatched_syllable_count_warnings'),
            (duplicate_zhuyin_warnings, 'duplicate_zhuyin_warnings')):
        if warning:
            with open(f'{dict_path}_{warning_name}',
                      'w', encoding='utf8') as warn_file:
                warn_file.write('\n'.join(warning))


# Used on set_dict
# Side effect: func (x)

def _call(func, *arg, **kwarg): return func(*arg, **kwarg)


# 載入詞典檔
# Load the dictionary.
# Side effect: IO (w), fileIO (rw), os (x), sys (x) re (x), pickle (x)
#              [set_dict] loaded_dict (rw),
#              chinese (rw), chinese_zhuyin (rw)

@_call
def set_dict(*arg, **kwarg):
    loaded_dict = []

    # A safer unpickler which forbids pickling every classes.
    # Side effect: pickle (x)

    class _BasicUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            raise pickle.UnpicklingError(
                f'Global \'{module}.{name}\' is forbidden')

    # 讀取詞典檔並建立詞典資料
    # Parse and create dictionary data from a dictionary text file.
    # Side effect: fileIO (r)

    def _get_dict_data_from_text(path):
        text_chinese_zhuyin = {}

        with open(path, 'r', encoding='utf8') as dict_file:
            dict_content = dict_file.read().splitlines()

        for phrase in dict_content:
            (word, zhuyin) = phrase.split('\t')
            zhuyin_syllables = zhuyin.split(' ')
            if word in text_chinese_zhuyin:
                text_chinese_zhuyin[word].append(zhuyin_syllables)
            else:
                text_chinese_zhuyin.update({word: [zhuyin_syllables]})

        return (path, text_chinese_zhuyin)

    # 將詞典資料傾印到檔案
    # Dump the content of a dictionary data to a file.
    # Side effect: fileIO (w), pickle (x)

    def _create_dict_data_dump(dict_data, path):
        with open(path, 'wb') as pickle_file:
            pickler_ = pickle.Pickler(pickle_file, pickle.HIGHEST_PROTOCOL)
            pickler_.dump(dict_data)

    # 從先前傾印出的檔案取得詞典資料
    # Get directionary data from a dumped data file.
    # Side effect: IO (w), fileIO (r), os.path (x), sys (x),
    #              pickle.UnpicklingError (x)
    #              BasicUnpickler: pickle.unpickler (x)

    def _get_dict_data_from_dump(path):
        if os.path.isfile(path):
            with open(path, 'rb') as pickle_file:
                unpickler_ = _BasicUnpickler(pickle_file)
                try:
                    (source, new_chinese_zhuyin) = unpickler_.load()
                except pickle.UnpicklingError as e:
                    print(str(type(e))[8:-2], ': ', e, file=sys.stderr)
                    return None
                if (os.path.realpath(f'{source}.pickle')
                        == os.path.realpath(path)):
                    return (source, new_chinese_zhuyin)
                return (source, None)

    # 載入詞典檔到詞典表中
    # Load dictionary data into dictionary list.
    # Side effect: [set_dict] loaded_dict (w),
    #              chinese (w), chinese_zhuyin (w)

    def _load_dict_data(dict_data):
        (path, new_chinese_zhuyin) = dict_data

        for (word, zhuyin) in new_chinese_zhuyin.items():
            if word in chinese_zhuyin:
                chinese_zhuyin[word].append(*zhuyin)
            else:
                chinese_zhuyin.update({word: zhuyin})

        loaded_dict.append(path)

    # 載入詞典的對應傾印檔；
    #   若無，則讀取已經過前處理之詞典檔，並生成傾印檔；
    #   若無，則對詞典檔進行前處理
    # Load the dictionary data from the corresponding dumped data file.
    # Parse and create dictionary data from
    #   the pre-processed dictionary text file if needed.
    # Pre-process the dictionary text file if needed.
    # Side effect: os (x)
    #              [set_dict] loaded_dict (r),
    #              preprocess_dict: IO (w), fileIO (rw), sys (x), re (x)
    #              _get_dict_data_from_dump: IO (w), fileIO (r),
    #                                        os.path (x), sys (x),
    #                                        pickle.UnpicklingError (x)
    #                                        BasicUnpickler:
    #                                               pickle.unpickler (x)
    #              _get_dict_data_from_text: fileIO (r)
    #              _create_dict_data_dump: fileIO (w), pickle (x)
    #              _load_dict_data: [set_dict] loaded_dict (w),
    #                               chinese (rw), chinese_zhuyin (rw)

    def set_dict(path_list, recreate_dict=False):
        loaded_dict.clear()
        chinese_zhuyin.clear()

        if isinstance(path_list, str):
            path_list = [path_list]

        for path in path_list:
            # Prevent using root directory if path is an empty string
            true_path = os.path.join(os.curdir, path)
            dict_data_file = f'{true_path}.pickle'

            # Keep true_path to refer the pre-processed dictionary text file
            if not path.endswith('_out'):
                true_path_unprocessed = true_path
                true_path = f'{true_path}_out'
                dict_data_file = f'{true_path}.pickle'

            # If the dictionary text file is un-processed,
            #   do pre-processing on it
            if os.path.isfile(true_path):
                # Do not load the dictionary if it needs to be re-created
                if not recreate_dict:
                    # Do not load and do not create the loaded dictionary again
                    if true_path in loaded_dict:
                        continue
                    # Load the dictionary if exists
                    if os.path.isfile(dict_data_file):
                        dict_data = _get_dict_data_from_dump(dict_data_file)
                        if dict_data is None:
                            print('Warning: The dump file \'', dict_data_file,
                                  '\' can not be loaded.  Regenerated.',
                                  sep='', file=sys.stderr, flush=True)
                        elif dict_data[1] is not None:
                            _load_dict_data(dict_data)
                            continue
                        elif dict_data[0] is not None:
                            print('Warning: The dump file \'', dict_data_file,
                                  '\' and its source \'', dict_data[0], '\'',
                                  ' mismatched.  Regenerated.',
                                  sep='', file=sys.stderr, flush=True)
            else:
                preprocess_dict(true_path_unprocessed)

            dict_data = _get_dict_data_from_text(true_path)
            _create_dict_data_dump(dict_data, dict_data_file)
            _load_dict_data(dict_data)
        return

    return set_dict
