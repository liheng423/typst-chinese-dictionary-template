#import "../doc/settings.typ": *
#import "../../assets/fonts.typ": *
#import "formats.typ": *
#import "config.typ": *
#import "@preview/hydra:0.6.1": hydra, selectors
#import "@preview/zh-kit:0.1.0": * 

// 页面设置为 A4纸张，双栏布局:contentReference[oaicite:4]{index=4}
#let background = rect(
  width: 1pt,
  height: 80%,
  fill: gray,
)

// ==============SETTING==================

// 页眉左上角换行 
#let header_size = 10
#let PINYIN_SEC = 3
#let HANZI_SEC = 4


// =============DATA=====================
// MAIN ENTRANCE
// 读取 JSON 数据文件:contentReference[oaicite:6]{index=6}
#let entries = json("../../library/glossary.json")
#let sorted = entries.sorted(key: e => e.pinyin)
#let filtered = sorted.filter(e => e.pinyin.find(reg_pinyin_index) != none)

// ==============COVER====================

#include("glossary-matter/cover.typ")
#pagebreak()

// ==============PREFACE==================

// #include("glossary-matter/phonetics.typ")
// ==============INDEX====================

#include("index.typ")
#pagebreak()
// =============CONTENT====================
#set page(numbering: "1")
// used for generate index and header
#let pinyin_sect = selectors.custom(
  heading.where(level: PINYIN_SEC),
)

#let hanzi_sec = selectors.custom(
  heading.where(level: HANZI_SEC)
)

//======================
#let right_or_wrong = [2] == [#1]
//======================


#set page(
  paper: "a4",
  columns: 2,
  margin: 2cm,
  header: context {
  let words_on_page = query(heading.where(level: 4)).filter(h => h.supplement == [#here().page()]).dedup()

  for (index, word) in words_on_page.enumerate() {
    [#word.body]
  }
  
  [
  #h(1fr) #hydra(pinyin_sect, use-last: false, skip-starting: true,
   prev-filter: (ctx, cands) => {
    cands.primary.prev != none and cands.primary.prev.supplement == here().page()
  }) --- #hydra(pinyin_sect, use-last: true, skip-starting: true)
  ]

  line(length: 100%)
},

  footer: context {

  align(center, [#here().page()])

  },
  background: background
)


#let dict-entry = (entry, idx) => block(breakable: true, [
  
  // 隐藏 heading（供 hydra 使用）
  #let number_func = (page, counter) => str(page) + "." + str(counter) 
  #context {
    let current_page = context {counter(page).display()}
    let first-pinyin = entry.pinyin.split(" ").at(0)
    show heading: none 
    heading(level: PINYIN_SEC, outlined: false, supplement: current_page)[#first-pinyin]
  }

  // Extract the first character and place it to the left of the header
  #{
    context {let current_page = counter(page).display()
      let first-zi = entry.item.at(0)
    show heading: none
    heading(level: HANZI_SEC, outlined: false, supplement: current_page)[#first-zi ]}
  }
  
  #render-word-title(entry.item, entry.pinyin, entry.benzi, idx)
  #render-meaning-box(entry.mean)
]) 

#for (idx, entry) in filtered.enumerate(start: 0) {
  let first-letter = entry.pinyin.find(reg_pinyin_index)
  let prev-letter = if idx == 0 {
    none
  } else {
    filtered.at(idx - 1).pinyin.find(reg_pinyin_index)
  }
  let first-pinyin = entry.pinyin.split(regex("[0-9]")).at(0)
  let prev-pinyin = if idx == 0 {
    none
  } else {
    filtered.at(idx - 1).pinyin.split(regex("[0-9]")).at(0)
  }

  // generate chapter
  if idx == 0 or first-letter != prev-letter {
    pagebreak()
    place(
      top + center,
      scope: "parent",
      float: true,
      text(1.4em, weight: "bold")[#heading(level: 1)[#upper(first-letter)]],
    )
  }

  // generate section (per pronounciation)
  if idx == 0 or first-pinyin != prev-pinyin { 
    line(start:(30%, 0%), end:(70%, 0%))
    align(center + top)[#text(1em, weight: "regular")[#heading(level: 2)[#first-pinyin]]]
  }

  [
   
    #dict-entry(entry, idx)
    #parbreak()
  ]
}

// ==============INDEX====================


