# Common TL

## Prerequisite

- Python >= 3.6

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
