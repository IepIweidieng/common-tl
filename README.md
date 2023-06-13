# Common TL

## Prerequisite

- Python >= 3.8

## Usage examples

### Convert a sentence written in Chinese characters to Common TL

A dictionary composed of tab-separated values is required, see [Dictionary Preparation](#Dictionary-Preparation).

```python-repl
>>> import ch2rm, ctl_dict
>>> dict_ = ctl_dict.DictSrc().add_dict_src('dict_example/Ch2TwRoman.txt', (ctl_dict.TL, ctl_dict.Word, ctl_dict.ETC)).create_dict()
>>> sentence = ch2rm.chinese_to_roman('你是誰？', dict_)
>>> print(sentence)
[[('dl', 'i2')], [('sc', 'i7')], [('tsc', 'ia5')]]
>>> print(' '.join('-'.join(''.join(syll) for syll in word) for word in sentence))
dli2 sci7 tscia5
```

### Convert a sentence written in TL to Common TL

Punctuation and capitalization are ignored.

```python-repl
>>> import ch2rm
>>> sentence = ch2rm.phonetic_to_tl("Thài-khong pîng-iú, lín hó! Lín tsia̍h-pá bē? Ū-îng, tō-lâi gún-tsia tsē--ooh.")
>>> print(sentence)
[[('th', 'ai3'), ('kh', 'oong1')], [('p', 'iong5'), ('', 'iu2')], [('dl', 'in2')], [('h', 'o2')], [('dl', 'in2')], [('tsc', 'iah8'), ('p', 'a2')], [('b', 'e7')], [('', 'u7'), ('', 'iong5')], [('t', 'o7'), ('dl', 'ai5')], [('g', 'un2'), ('tsc', 'ia1')], [('ts', 'e7'), ('', 'ooh0')]]
>>> print(' '.join('-'.join(''.join(syll) for syll in word) for word in sentence))
thai3-khoong1 piong5-iu2 dlin2 ho2 dlin2 tsciah8-pa2 be7 u7-iong5 to7-dlai5 gun2-tscia1 tse7-ooh0
```

### Convert a *string-form sentence* in Bopomofo (Zhuyin) and TL into IPA or Common TL

*String-form sentence* means a Python list of *string-form word*s. A *string-form word* is a Python list of a *phonetic syllable*. (Explained below)

Custom function definitions:

```python3
import ch2rm
import ctl_dict

def phonetic_sentence_to_ipa(sentence, phonetic=None):
     return [ch2rm.phonetic_word_to_ipa(word, phonetic=phonetic) for word in sentence]

def phonetic_sentence_to_ctl(sentence, phonetic=None):
     return [ch2rm.phonetic_word_to_tl(word, phonetic=phonetic) for word in sentence]
```

Execution (continued):

```python-repl
>>> TL = ctl_dict.TL
>>> Zhuyin = ctl_dict.Zhuyin
>>> sentence = [["ㄍㄢˇ", "ㄒㄧㄝˋ"], ["ㄍㄜˋ", "ㄨㄟˋ"], [TL("lâng"), TL("kheh")]]
>>> #            感謝                 各位               人客
>>> phonetic_sentence_to_ipa(sentence, phonetic=Zhuyin)
[[('k', 'an03'), ('ɕ', 'je04')], [('k', 'ɤ04'), ('', 'wei04')], [('ᵈl', 'aŋ5'), ('kʰ', 'eʔ4')]]
>>> phonetic_sentence_to_ctl(sentence, phonetic=Zhuyin)
[[('k', 'an03'), ('s', 'ie04')], [('k', 'o04'), ('', 'uei04')], [('dl', 'ang5'), ('kh', 'eh4')]]
```

## Term Definitions/Concepts Used in This Project

### Terms/Concepts about Phonetic Notation Systems

#### *[Common TL](https://hackmd.io/@IID/Common-TL-Phonetic)* (*CTL*) (as a phonetic transcription system)

A phonetic transcription system based on modified [Taiwanese Romanization System (TL)](https://en.wikipedia.org/wiki/Taiwanese_Romanization_System "Taiwanese Romanization System - Wikipedia").

CTL uses only ASCII symbols and can be used to transcribe some Chinese languages and dialects other than Taiwanese Hokkien.

Currently applicable Chinese languages and dialects:

* Taiwanese Hokkien
    * Chiang-chiu and Chôan-chiu dialects are applicable.
* Standard Mandarin
* Taiwanese Hakka
    * Sixian, Hailu, Dabu, Raoping, Zhao'an, and Southern Sixian dialects are applicable.

The commonly used phonetic notations used by these languages and dialects can be converted into CTL and then be converted back without losing any information other than the following:

* The citation tone of neutral tone syllables is lost for TL.
* TL o vs. oo for variants of Taiwanese Hokkien where TL o is pronounced as [o] if the Southern transcription variant of CTL is used.

The strict form of CTL can also spells out non-phonemic features so that every grapheme at the same position within a syllable represents the same range of speech sound among all applicable language and dialects. This is the form used by this project.

CTL has two transcription variants as listed in the following table:

CTL Variant | [ə] | [o]~[ʊ] | /ɔ/
--- | --- | --- | ---
Southern | `o` | `oo` | `oo`
Northern | `or` | `o` | `oo`

#### *[International Phonetic Alphabet](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet "International Phonetic Alphabet - Wikipedia")* (*IPA*)

A phonetic transcription system based on the Latin script.

IPA uses non-ASCII symbols and diacritics to transcribe speech sounds.

In this project, a modified form of IPA is used, where the tone is represented by a number instead of IPA tone letters.

CTL can be converted into the modified form of IPA and be converted back without losing any information.

#### Syllable Component Definition

* *Initial*: Initial
* *Final*: Medial, nucleus, coda, **and tone number**

[Reference for Typical Linguistic Syllable Component Definitions](https://en.wikipedia.org/wiki/Syllable "Syllable - Wikipedia")

#### Syllable forms (forms to represent a syllable)

* *String form*: A `str` or an instance of `_Phonetic` (a subclass of `UserString`; see below)
* *Pair form*: An *initial-final pair* (see below)

#### *Initial-final pair* (*pair-form syllable*)

A pair of an *initial* string and a *final* string in phonetic notation which represents a syllable \
*I.e.*, `(initial, final)`

An *initial-final* pair can also be one of …

* *IPA pair*, if the *initial* and *final* are both in IPA (*phonemic*) notation, except that the tone is represented by a number instead of IPA tone letters. (typing hint: `phonetic.phonetic.IpaPair`)
* *CTL pair*, if the *initial* and *final* are both in CTL. (typing hint: `phonetic.phonetic.CtlPair`)

Example:

Word | IPA | IPA, pair form | TL, pair form
--- | --- | --- | ---
*拼* *phing* <br> (Taiwanese Hokkien, Kaohsiung) | /pʰiəŋ˥˥/ | `('pʰ', 'iəŋ1')` | `('ph', 'ing1')`

#### Word forms

* Ordinarily written text
* Phonetic string: A single string of the phonetic notation of the whole word.
* String form: A list of string-form syllables of the word (typing hint: `ch2rm.PhoneticSylList`)
* Pair form: A list of pair-form syllables of the word (typing hints: `ch2rm.IpaWord` & `ch2rm.CtlWord`)

Example:

Word | IPA | IPA, string form | IPA, pair form
--- | --- | --- | ---
*拼音* *phing-im* <br> (Taiwanese Hokkien, Kaohsiung) | /pʰiəŋ˥˥.im˥˥/ | `['pʰiəŋ1', 'im1']` | `[('pʰ', 'iəŋ1'), ('', 'im1')]`

#### *Sentence* forms

* Ordinarily written text
* Segmented written text: A list of ordinarily written words of the sentence
* Phonetic string: A single string of the phonetic notation of the whole sentence.
* String form: A list of string-form words of the sentence
* Pair form: A list of pair-form words of the sentence

In the string form, each string-form word can have independent type (`str` or one of the subclasses of `_Phonetic`; see below)

Example:

Sentence | Words | TL, string form | TL, pair form
--- | --- | --- | ---
*咱人生來自由* <br> *Lán-lâng senn-\-lâi tsū-iû* <br> (Taiwanese Hokkien, Kaohsiung) | *咱人* *lán-lâng*, <br> *生來* *senn-\-lâi*, <br> *自由* *tsū-iû* | `[['lan2', 'lang5'], ['senn1', 'lai0'], ['tsu7', 'iu5']]` | `[[('l', 'an2'), ('l', 'ang5')], [('s', 'enn1'), ('l', 'ai0')], [('ts', 'u7'), ('', 'iu5')]]`

#### Comparison of Text Forms

Form | Sentence | Word | Syllable
--- | --- | --- | ---
Ordinarily written text | Sentence text <br> & segmented text | Word text |
Phonetic string | Phonetic sentence (string) | Phonetic word (string) | Phonetic syllable
String form <br> (\* of string(s)) | String-form sentence (list of …) | String-form word (list of …) | Phonetic syllable
Pair form <br> (\* of pair(s)) | Pair-form sentence (list of …) | Pair-form word (list of …) | Initial-final pair

Note that:

* There are no ordinarily written syllable texts. One-syllable texts are treated as one-word text.
* There are no lists of phonetic word strings. However, a list of ordinarily written word texts can result from word segmentation.

### Terms/Concepts about the Dictionary

#### *Dictionary*

typing hint: `ctl_dict.CtlDict`

A word-to-phonetic-notation dictionary built from any number of *dictionary text file*s

#### *Dictionary text file*

A file composed of tab-separated values.

Each line in the file should be separated into $n$ fields by $n - 1$ tabs and should at least contains a `Word` field and a `_Phonetic` field

#### *(pre-)processing* (for dictionary text files)

* Lines with XML escapes are ignored.
* Fullwidth spaces are replaced with halfwidth spaces, and then successive spaces are reduced into a single space.
* Character in parentheses are removed along with the parentheses.
* Latin phonetic alphabet are normalized into [NFD](https://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms "Unicode equivalence - Wikipedia") form.
* Words with the syllable count not consistent with the phonetic notation are ignored.

#### *Dictionary format specification*

typing hint: `ctl_dict.Format`

A tuple of *dictionary format token*s used for specifying the fields of a dictionary text file.

#### *Dictionary format token*

A set of subclass of `UserString`.

Current support format tokens (only those not prefixed with `_` should be used):
* `Word`: Field for the word
* `_Phonetic`: Field for the word in phonetic notation (syllables are separated by spaces) \
Subclasses:
    * `_RomanPhonetic`: Phonetic notation systems using Latin alphabet
        * `TaiwaneseRomanization` (`TL`)
        * `TaiwaneseHakkaRomanization` (`THRS`)
    * `Zhuyin`
* `ETC`: Ignored field

#### *Dictionary text file specification item*

typing hint: `ctl_dict.SrcItem`

Either a string of the path to a dictionary text file or a tuple with such a string and *dictionary format specification*.

#### *Dictionary text file specification*

typing hint: `ctl_dict.SrcSpec`

Either a list of (typing hint: `ctl_dict.SrcList`) or a single dictionary text file specification item.

#### Comparison of Dictionary Text File Specification Components

Component | typing hint <br> (`ctl_dict.*`) | typing hint (partially expanded)
--- | --- | ---
Dictionary format token | | `Union[str, Type[UserString]]`
Dictionary format specification | `Format` | `Sequence[Union[str, Type[UserString]]]]`
Dictionary text file specification item | `SrcItem` | `Union[str, Tuple[str, Format]]`
Dictionary text file specification | `SrcSpec` | `Union[List[SrcItem], SrcItem]`

## Text Conversion Functions

These functions perform word segmentation and pronunciation querying and thus require the use of a dictionary, see [Dictionary Preparation](#Dictionary-Preparation).

### Word level (ordinarily written)

#### `ch2rm.chinese_word_to_phonetic(word: str, dict_: ctl_dict.CtlDict) -> ctl_dict.DictPronounCandList`

Return a list of the possible phonetic notations of the ordinarily written `word` in the dictionary `dict_`

### Sentence level (ordinarily written)

#### `ch2rm.chinese_to_roman(sentence: str, dict_: ctl_dict.CtlDict, dialects: Lang = ch2rm.lang()) -> List[CtlWord]`

Segment the ordinarily written `sentence` into words, and then convert the result into a pair-form CTL sentence

## Phonetic Notation Conversion Functions

These functions only perform conversions between phonetic notations and thus do not require the use of dictionaries.

### Syllable level (string form)

#### `phonetic.*.*_syllable_to_ipa(syll: Str, dialect: Optional[str] = ?, variant: Optional[str] = ?) -> IpaPair`

Convert a syllable string `syll` written in the phonetic notation system `*` into an IPA pair

*E.g.*,

* `phonetic.tl.tl_syllable_to_ipa(tl_: Str, dialect: Optional[str] = 'chiang', variant: Optional[str] = 'southern') -> phonetic.IpaPair`
    * Convert a Taiwanese Hokkien syllable written in TL `syll` into an IPA pair
* `phonetic.zhuyin.zhuyin_syllable_to_ipa(zhuyin: Str, dialect: Optional[str] = None, variant: Optional[str] = None) -> IpaPair`
    * Convert a Standard Mandarin syllable written in Zhuyin/Bopomofo `zhuyin` into an IPA pair

### Syllable level (pair form)

#### `phonetic.common_tl.ipa_pair_to_tl_pair(ipa_pair: IpaPair, dialect: Optional[str] = None, variant: Optional[str] = 'southern') -> CtlPair`

Convert an IPA pair into a CTL pair

### Word level

#### `ch2rm.phonetic_word_to_ipa(phonetic_word: PhoneticSylList, dialects: Lang = ch2rm.lang(), phonetic: Optional[Type[ctl_dict._Phonetic]] = None) -> IpaWord`

Convert a string-form phonetic word into a pair-form IPA word

The phonetic notation system of each syllable is specified by its type (one of the subclasses of `_Phonetic`) or `phonetic` if its type is `str`.

#### `ch2rm.ipa_pair_to_tl(ipa_pair: IpaWord, *args, **kwargs) -> CtlWord`

Convert a pair-form IPA word into a pair-form CTL word

Its non-positional arguments are forwarded to `phonetic.common_tl.ipa_pair_to_tl_pair()`.

#### `ch2rm.phonetic_word_to_tl(phonetic_word: PhoneticSylList, dialects: Lang = ch2rm.lang(), phonetic: Optional[Type[ctl_dict._Phonetic]] = None) -> CtlWord`

Convert a string-form word into a pair-form CTL word

This function is the combination of the previous two functions.

### Sentence level (phonetic string)

#### `ch2rm.phonetic_to_tl(sentence: str, dialects: Lang = ch2rm.lang(), phonetic: Type[ctl_dict._Phonetic] = ctl_dict.TL) -> List[CtlWord]`

Segment the TL-like phonetic `sentence` into words, and then convert the result into a pair-form CTL sentence

## Comparison of Conversion Functions

To→ <br> From↓ | Phonetic \* <br> (string-form) | IPA \* <br> (pair-form) | CTL \* <br> (pair-form)
--- |:---:|:---:|:---:
Ordinarily written | <br> (`chinese_word_to_phonetic()`) | | `chinese_to_roman()` <br> &nbsp;
Phonetic string | | | `phonetic_to_tl()` <br> &nbsp;
Phonetic \* <br> (string-form) | | <br> `phonetic_word_to_ipa()` <br> `*_syllable_to_ipa()` | <br> `phonetic_word_to_tl()` <br> &nbsp;
IPA \* <br> (pair-form) | | | <br> `ipa_pair_to_tl()` <br> `ipa_pair_to_tl_pair()`

Note that:

* `chinese_word_to_phonetic()` returns a list of string-form words, which resembles a string-form sentence but every syllable is ensured to be of a subtype of `_Phonetic`. The return value is treated as in the word level and has the typing hint `ctl_dict.DictPronounCandList`.
* There are no other conversion functions which directly convert texts from a level (sentence/word/syllable) to another.

### Dialect-specifying arguments

Except for `chinese_word_to_phonetic()`, all sentence-level and word-level conversion functions accept an optional argument `dialects` (typing hint: `Lang`) for specifying the (sub-)dialect for each applicable language/dialect. Its default value is equivalent to:

```python3
ch2rm.lang(
    hokkien=ch2rm.lang_opt(dialect='chiang', variant='southern'),
    mandarin=ch2rm.lang_opt(dialect=None, variant=None),
    hakka=ch2rm.lang_opt(dialect='sixian', variant=None),
    common_tl=ch2rm.lang_opt(dialect=None, variant='southern'))
```

All arguments of `ch2rm.lang()` and `ch2rm.lang_opt()` are optional. All arguments of `ch2rm.lang_opt()` can be positional.

Expected combinations of arguments to `ch2rm.lang()` are listed in the following table:

Keyword | Language/Dialect | `(dialect, variant)` | Valid `*`
--- | --- | --- | ---
`hokkien` | Taiwanese Hokkien | `('chiang', *)` <br> `('choan', *)` | `'southern'` <br> `'northern'`
`mandarin` | Standard Mandarin | `(None, None)` |
`hakka` | Taiwanese Hakka | `('sixian', None)` <br> `('hailu', None)` <br> `('dabu', None)` <br> `('raoping', 'hsinchu')` <br> `('raoping', 'zhuolan')` <br> `('zhao_an', None)` <br> `('southern_sixian', None)` |
`common_tl` | (For choosing CTL variant) | `(None, *)` | `'southern'` <br> `'northern'`

For choosing CTL variant, if the argument `common_tl` is omitted, the argument `hokkien` is used if provided.

For syllable-level conversion functions, the arguments `dialect` and `variant`  can be used for specifying the (sub-)dialect. See the above table for expected combinations of `dialect` and `variant`.

## Word Segmentation Functions

These functions require the use of a dictionary, see [Dictionary Preparation](#Dictionary-Preparation).

### String level

#### `ctl_segment.split_chinese_word(sentence: str, dict_: ctl_dict.CtlDict) -> List[str]`

Segment the ordinarily written `sentence` into words. Currently, the forward maximum matching algorithm is used.

Before the segmentation, the spaces within `sentence` are reduced to 1 space between TL-like words and removed otherwise.

### File level

#### `ctl_segment.split_file(path: str, dict_: ctl_dict.CtlDict) -> None`

Perform word segmentation for the first line of the `.trn` file at `path` in-place

A backup file whose path is `_bk` suffixed to the original `path` is created.

### Directory level

#### `ctl_segment.split_for_each_file(path: str, dict_: ctl_dict.CtlDict) -> None`

Perform word segmentation for the first line of all `.trn` files under `path` and its all (direct or indirect) sub-directories in-place

It calls `ctl_segment.split_file()` and thus also creates backup files.

## Dictionary Functions

These functions are used to create a `CtlDict` object.

### Module functions

#### `ctl_dict.create_dict(path_list: SrcList, *args, **kwargs) -> CtlDict`

Create a dictionary using the given dictionary text file specification

A `ctl_dict.DictSrc` object is created internally.

### Dictionary Builder Methods

These are methods of the class `ctl_dict.DictSrc`.

#### `DictSrc.add_dict_src(self, path: str, format_: Format)`

Add the given dictionary text file with given format specification into the dictionary text file specification

#### `DictSrc.reset_dict_src(self)`

Clear the dictionary text file specification

#### `DictSrc.set_dict_src(self, path_list: SrcSpec)`

Specify the dictionary text file specification

#### `DictSrc.create_dict(self, reprocess: bool = False, recreate_dump: bool = False) -> CtlDict`

Create a dictionary. All the specified dictionary text files are separately loaded and dumped and then combined in-order and dumped again. By default, the already dumped data are loaded if exist.

## Dictionary Preparation

A dictionary is required only when text segmentation or pronunciation querying is needed.

The dictionary text files under `dict_example/` are minimal examples which merely sufficient to demonstrate these functionalities.

For practical use, it is viable to use the dictionary data from the online dictionaries compiled by the Ministry of Education of Taiwan. The already released dictionary data should be used.

### Get Released Dictionary Data

Among these online dictionaries, the following ones are recommended to use and their released data are available:

* *臺灣閩南語常用詞辭典* (*Dictionary of Frequently-Used Taiwan Minnan*). Ministry of Education.
    * Dictionary data: Currently officially not available.
    * Unofficial past release: https://github.com/g0v/moedict-data-twblg/blob/master/uni/詞目總檔.csv (comma-separated values)
* *國語辭典簡編本* (*Concised Mandarin Chinese Dictionary*). Ministry of Education.
    * Dictionary data:  https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html
    * Filename: `dict_concised_2014_20220627.zip` (`.xlsx`; Excel Spreadsheet XML)
* *臺灣客家語常用詞辭典* (*Dictionary of Frequently-Used Taiwan Hakka*) Ministry of Education.
    * Dictionary data: No official permanent links available.
    * Please go to <https://hakkadict.moe.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=HSJwxI/newsearch> and then refer to the post *提供《臺灣客家語常用詞辭典》文字內容資料下載* (*The text data of «Dictionary of Frequently-Used Taiwan Hakka» has been made available for download*) 
    * Format: `.ods` (OpenDocument Spreadsheet)

### Convert Dictionary Data

To allow these dictionary data files to be read into a `CtlDict` object, these files should be converted into tab-separated values.

There are many tools available for such conversion. which are not covered here.

The converted dictionary text files should be able to be loaded into a `CtlDict` object by using suitable dictionary text file specifications.
