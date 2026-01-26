#import "../doc/settings.typ": *
#import "config.typ": *
// formatting





// ===============
#let background = rect(
  width: 1pt,
  height: 80%,
  fill: gray,
)

#let entries = json("../../library/glossary.json") 
#let filtered = entries.filter(e => e.pinyin.find(reg_pinyin_index) != none)
#let sorted = filtered.sorted(key: e => e.pinyin)

#set text(font: config.index.font, weight: config.index.weight, size: config.index.fontsize)
#set par(leading: 0.35em)




#set page(
  paper: "a4",
  margin: 2cm,
  background: background,
)


#align(center)[#heading(level: 1)[#text(size: 20pt)[索引]]]

#v(5pt)

#columns(4)[
  #for (idx, entry) in sorted.enumerate(start: 0) {
    let first-letter = entry.pinyin.find(reg_pinyin_index)
    let prev-letter = if idx == 0 {
      none
    } else {
      sorted.at(idx - 1).pinyin.find(reg_pinyin_index)
    }
    let first-pinyin = entry.pinyin.split(" ").at(0).replace(regex("[0-9]"), "")
    let prev-pinyin = if idx == 0 {
      none
    } else {
      sorted.at(idx - 1).pinyin.split(" ").at(0).replace(regex("[0-9]"), "")
    }
    if idx == 0 or first-letter != prev-letter {
      linebreak()
      align(center)[
      #text(size: config.index-h1.fontsize, weight: config.index-h1.weight)[
        #upper(first-letter)
      ]]
    }
    if idx == 0 or first-pinyin != prev-pinyin {
        align(center)[
        #text(size: config.index-h2.fontsize, weight: config.index-h2.weight)[
          #first-pinyin #linebreak()
      ]]
    }

    let item = entry.item
    [#link(label(str(idx)), item) #h(1fr) #link(label(str(idx)), ref(label(str(idx)), supplement: [], form: "page"))]
    linebreak()
  }
]
