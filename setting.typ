#let pinyin_index = (
  "b": 1,
  "c": 2,
  "d": 3,
  "f": 4,
  "g": 5,
  "h": 6,
  "j": 7,
  "k": 8,
  "l": 9,
  "m": 10,
  "n": 11,
  "ng": 12,
  "p": 13,
  "q": 14,
  "r": 15,
  "s": 16,
  "t": 17,
  "ts": 18,  // 特别处理，放在t之后
  "v": 19,
  "w": 20,
  "x": 21,
  "z": 22,
  "u": 23,  // 零声母开始
  "i": 24,
  "y": 25,
  "a": 26,
)

#let reg_pinyin_index = regex("^(ts|ng|[bcdfghjklmnpqrstvwxyz]|[uiya])")