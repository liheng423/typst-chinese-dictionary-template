#import "config.typ": *
#import "utils.typ": *








#let render-word-title(word, pinyin, benzi, idx) = {
    grid(
    columns: 2,
    align: (left, top),
    column-gutter: 0.2cm,
    [
      #box(width: 100pt)[
        #text(
          font-size-map(word), 
          weight: "extrabold", 
          font: ZhongSong
        )[#word]
      ]
    ],
    [
      #text(12pt, font: config.pinyin.font)[#sup-pinyin(pinyin) ] #label(str(idx))
      // #linebreak()
      // #text(10pt, font: font-family.SongTi)[#benzi]
    ]
  )
}

#let render-meaning-box(mean) = {
  
  set text(
    font: config.meaning-box.font)
  for i in range(mean.len()) {
    let m = mean.at(i)
    let no = circled.at(str(i + 1))
    let label = m.at(2)
    let class = m.at(1)
    text(10pt, weight: "bold")[#no#{if not class == none {[(#class)]} else []}#{notnone(label)}]

    for (idx, eg) in m.slice(3, m.len()).enumerate(start: 1){
      if idx == 1 {[:]}
      if idx == m.len() - 3 {text(10pt)[#eg]}
      else {text(10pt)[#eg#config.meaning-box.seperator]}
      
    }
  }
}

