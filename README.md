# Common TL

## Prerequisite

- Python >= 3.8

## Usage examples

### Convert a sentence written in Chinese characters to Common TL

A dictionary composed of tab-separated values is required.

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

### Convert a *sentence* (string form) in Bopomofo (Zhuyin) and TL into an IPA or Common TL

*Sentence* here means a Python list of `word`s. A `word` is either a string or a pair. (Explained below)

Preprocedure:

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
* TL o vs. oo for variants of Taiwanese Hokkien where TL o is pronunced as [o] if the Southern transcription variant of CTL is used.

The strict form of CTL can also spells out non-phonemic features so that every grapheme at the same position within a syllble represents the same range of speech sound among all applicable language and dialects. This is the form used by this project.

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

#### *Syllable forms* (forms to represent a syllable)

* *String form*: A `str` or an instance of `_Phonetic` (a subclass of `UserString`; see below)
* *Pair form*: An *initial-final pair* (see below)

#### *Initial-final pair* (a syllable in the pair form)

A pair of an *initial* string and a *final* string in phonetic notation which represents a syllable \
*I.e.*, `(initial, final)`

An *initial-final* pair can also be one of …

* *IPA pair*, if the *initial* and *final* are both in IPA (*phonemic*) notation, except that the tone is represented by a number instead of IPA tone letters. (typing hint: `phonetic.phonetic.IpaPair`)
* *CTL pair*, if the *initial* and *final* are both in CTL. (typing hint: `phonetic.phonetic.CtlPair`)

Example:

Word | IPA | IPA, Pair form | TL, Pair form
--- | --- | --- | ---
*拼* *phing* <br> (Taiwanese Hokkien, Kaohsiung) | /pʰiəŋ˦/ | `('pʰ', 'iəŋ1')` | `('ph', 'ing1')`

#### *Word* forms

A word represented by a list of syllables \
*I.e.*, `[syllable_0, syllable_1, ...]`

* String form: All the syllables are in the string form (typing hint: `ch2rm.PhoneticSylList`)
* Pair form: All the syllables are in the pair form (typing hints: `ch2rm.IpaWord` & `ch2rm.CtlWord`)

Example:

Word | IPA | IPA, String form | IPA, Pair form
--- | --- | --- | ---
*拼音* *phing-im* <br> (Taiwanese Hokkien, Kaohsiung) | /pʰiəŋ˦.im˦/ | `['pʰiəŋ1', 'im1']` | `[('pʰ', 'iəŋ1'), ('', 'im1')]`

#### *Sentence* forms

A sentence represented by a list of *word*s \
I.e., `[word_0, word_1, ...]`

* String form: All the *word*s are in the string form
* Pair form: All the *word*s are in the pair form

In the string form, each *word* can have independent type (`str` or one of the subclasses of `_Phonetic`; see below)

Example:

Sentence | Words | TL, String form | TL, Pair form
--- | --- | --- | ---
*咱人生來自由* <br> *Lán-lâng senn-\-lâi tsū-iû* <br> (Taiwanese Hokkien, Kaohsiung) | *咱人* *lán-lâng*, <br> *生來* *senn-\-lâi*, <br> *自由* *tsū-iû* | `[['lan2', 'lang5'], ['senn1', 'lai0'], ['tsu7', 'iu5']]` | `[[('l', 'an2'), ('l', 'ang5')], [('s', 'enn1'), ('l', 'ai0')], [('ts', 'u7'), ('', 'iu5')]]`

### Terms/Concepts about the Dictionary

#### *Dictionary*

typing hint: `ctl_dict.CtlDict`

A word-to-phonetic-notation dictionary built from any number of *dictionary text file*s

#### *Dictionary text file*

A CSV file which uses tabs (`'\t'`) as the separator character

Each line in the file should at least contains a `Word` field and a `_Phonetic` field

#### *(pre-)processing* (for dictionary text files)

* Lines with XML escapes are ignored.
* Fullwidth spaces are replaced with halfwidth spaces, and then successive spaces are reduced into a single space.
* Character in parentheses are removed along with the parentheses.
* Latin phonetic alphabet are normalized into [NFD](https://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms "Unicode equivalence - Wikipedia") form.
* Words with the syllable count not consistent with the phonetic notation are ignored.

#### *Dictionary format specification*

typing hint: `ctl_dict.Format`

A tuple of *dictinionary format token*s used for specifying the fields of a dictionary text file.

#### *Dictionary format token*

A set of subclass of `UserString`.

Current support format tokens (only those not prefixed with `_` should be used):
* `Word`: Field for the word (syllables separated by spaces)
* `_Phonetic`: Field for the word in phonetic notation
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

Either a list of (typing hint: `ctl_dict.SrcList`) or a single *dictionary text file specification item*.

## Text Conversion Functions

These functions perform word segmentation and pronunciation quering and thus require the use of a dictionary.

### Word level (single string)

#### `ch2rm.chinese_word_to_phonetic(word: str, dict_: ctl_dict.CtlDict) -> ctl_dict.DictPronounCandList`

Return a list of the possible phonetic notations of `word` in the dictionary `dict_`

### Sentence level (single string)

#### `ch2rm.chinese_to_roman(sentence: str, dict_: ctl_dict.CtlDict, dialects: Lang = ch2rm.lang()) -> List[CtlWord]`

Segment the `sentence` into words, and then convert the result into a CTL *sentence* in the pair form

## Phonetic Notation Conversion Functions

These functions only perform conversions between phonetic notations and thus do not require the use of dictionaries.

### Syllable level (string form)

#### `phonetic.*.*_syllable_to_ipa(syll: Str, dialect: Optional[str] = ?, variant: Optional[str] = ?) -> IpaPair`

Convert a syllable string `syll` written in `*` phonetic notation system into an IPA pair

*E.g.*,

* `phonetic.tl.tl_syllable_to_ipa(tl_: Str, dialect: Optional[str] = 'chiang', variant: Optional[str] = 'southern') -> phonetic.IpaPair`
    * Convert a Taiwanese Hokkien syllable in TL `syll` into an IPA pair
* `phonetic.zhuyin.zhuyin_syllable_to_ipa(zhuyin: Str, dialect: Optional[str] = None, variant: Optional[str] = None) -> IpaPair`
    * Convert a Standard Mandarin syllable in Zhuyin/Bopomofo `zhuyin` into an IPA pair

### Syllable level (pair form)

#### `phonetic.common_tl.ipa_pair_to_tl_pair(ipa_pair: IpaPair, dialect: Optional[str] = None, variant: Optional[str] = 'southern') -> CtlPair`

Convert an IPA pair into a CTL syllable in the pair form

### Word level (list of syllables)
    
#### `ch2rm.phonetic_word_to_ipa(phonetic_word: PhoneticSylList, dialects: Lang = ch2rm.lang(), phonetic: Optional[Type[ctl_dict._Phonetic]] = None) -> IpaWord`

Convert a list of syllable strings into a list of IPA pairs

The phonetic notation system of each syllable is specified by its type (one of the subclasses of `_Phonetic`) or `phonetic` if its type is `str`.

#### `ch2rm.ipa_pair_to_tl(ipa_pair: IpaWord, *args, **kwargs) -> CtlWord`

Convert a list of IPA pairs into a list of CTL initial-final pairs

Its arguments are forwarded to `phonetic.common_tl.ipa_pair_to_tl_pair()`.

#### `ch2rm.phonetic_word_to_tl(phonetic_word: PhoneticSylList, dialects: Lang = ch2rm.lang(), phonetic: Optional[Type[ctl_dict._Phonetic]] = None) -> CtlWord`

Convert a list of syllable strings into a list of CTL initial-final pairs

This function is the combination of the above two functions.

### Sentence level (single string)

#### `ch2rm.phonetic_to_tl(sentence: str, dialects: Lang = ch2rm.lang(), phonetic: Type[ctl_dict._Phonetic] = ctl_dict.TL) -> List[CtlWord]`

Segment the TL-like phonetic `sentence` into words, and then convert the result into a CTL *sentence* in the pair form

## Word Segmentation Functions

These functions require the use of a dictionary.

### String level

#### `ctl_segment.split_chinese_word(sentence: str, dict_: ctl_dict.CtlDict) -> List[str]`

Segment the `sentence` into words. Currently, the forward maximum matching algorithm is used.

Before the segmentation, the spaces within `sentence` are reduced to 1 space between TL-like words and removed otherwise.

### File level

#### `ctl_segment.split_file(path: str, dict_: ctl_dict.CtlDict) -> None`

Perform word segmentation for the first line of the `.trn` file at `path` in-place

A backup file whose path is `_bk` suffixed to the original `path` is created.

### Directory level

#### `ctl_segment.split_for_each_file(path: str, dict_: ctl_dict.CtlDict) -> None`

Perform word segmentation for the first line of all `.trn` files under `path` and its all (direct or indirect) sub-directories in-place

## Dictionary Functions

These functions are used to create a `CtlDict` object.

### Module functions

#### `ctl_dict.create_dict(path_list: SrcList, *args, **kwargs) -> CtlDict`

Create a dictionary using the given dictionary text file specification

A `ctl_dict.DictSrc` is created internally.

### Dictionary Builder Methods

These are methods of the class `ctl_dict.DictSrc`.

#### `DictSrc.add_dict_src(self, path: str, format_: Format)`

Add the given dictionary text files with given format specifications into the dictionary text file specification

#### `DictSrc.reset_dict_src(self)`

Clear the dictionary text file specification

#### `DictSrc.set_dict_src(self, path_list: SrcSpec)`

Specify the dictionary text file specification

#### `DictSrc.create_dict(self, reprocess: bool = False, recreate_dump: bool = False) -> CtlDict`

Create a dictionary and dump it. By default, a dumped `CtlDict` with the same dictionary text file specification is loaded if exists.


