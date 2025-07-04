#import "../setting.typ": *
#import "../fonts.typ": *
#import "@preview/hydra:0.6.1": hydra, selectors, anchor

// 页面设置为 A4纸张，双栏布局:contentReference[oaicite:4]{index=4}
#let background = rect(
  width: 1pt,
  height: 80%,
  fill: gray,
)



#let pinyin_sect = selectors.custom(
  heading.where(level: 3),
)

#let kanji_sect = selectors.custom(
  heading.where(level: 4)
)


//======================
#let right_or_wrong = [2] == [#1]
//======================



#set page(
  paper: "a4",
  columns: 2,
  margin: 2cm,
  header: context {
  // [#hydra(kanji_sect, skip-starting: true, use-last: false,
  // prev-filter: (ctx, cands) => {
  //   cands.primary.prev != none and cands.primary.prev.supplement == here().page()
  // })
  // 
  let words_on_page = query(heading.where(level: 4)).filter(h => h.supplement == [#here().page()]).dedup()

  
  for word in words_on_page {
    [#word.body  ]
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



// #let dict-entry = entry => block(breakable: false, [
//   #{
//   show heading: none
//   heading(level: 3, outlined: false)[#entry.拼音]
// }

// #{
//   show heading: none
//   heading(level: 4, outlined: false)[#entry.词语]
// }

//   #grid(
//   columns: 2,
//   align: (left, top),
//   column-gutter: 0.2cm,
//   [  // 左列：词语（加大加粗）
//     #pad(right: 10pt)[#text(22pt, weight: "extrabold", font: "STZhongSong")[#entry.词语]]
//   ],
  
//   [  // 右列：两行小字（拼音 + 释义）
    
    
//     #text(10pt, font: font-family.HeiTi)[#entry.释义]
//     #linebreak()
//     #text(10pt, font: "Times New Roman")[#entry.拼音]
//   ]
// )
// #text(10pt, font: font-family.SongTi)[#entry.例句]

// ])
#let dict-entry = (entry, chap, item_counter) => block(breakable: true, [
  
  // 隐藏 heading（供 hydra 使用）
  #let number_func = (page, counter) => str(page) + "." + str(counter) 
  #{
    context {let current_page = counter(page).display()
    let first-pinyin = entry.pinyin.split(" ").at(0)
 
    show heading: none 
    heading(level: 3, outlined: false, supplement: current_page)[#first-pinyin]}
    
  }
  #label(str(item_counter))
  
  // #item_positions.push(item_counter)
  #{

    context {let current_page = counter(page).display()
      let first-zi = entry.item.at(0)
    show heading: none
    heading(level: 4, outlined: false, supplement: current_page)[#first-zi]
    
    }
    
  }

  // 顶部 词语+拼音

  #grid(
    columns: 2,
    align: (left, top),
    column-gutter: 0.2cm,
    [
      #box(width: 100pt)[
        #text(
          font-size-map(entry.item), 
          weight: "extrabold", 
          font: ZhongSong
        )[#entry.item]
      ]
    ],
    [
      #text(10pt, font: "Times New Roman")[#sup-pinyin(entry.pinyin)]
      #linebreak()
      #text(10pt, weight: "bold", font: font-family.SongTi)[#entry.benzi]
    ]
  )
  
  
  // 展示每条 mean 内容（含圈号）
  #set text(font: ZhongSong)
  #for i in range(entry.mean.len()) {
    let m = entry.mean.at(i)
    let no = circled.at(str(i + 1))
    text(10pt, weight: "bold")[#no#m.at(2) (#m.at(1))：]

    for (idx, eg) in m.slice(3, m.len()).enumerate(start: 1){
      if idx == m.len() - 3 {text(10pt)[#eg。]}
      else {text(10pt)[#eg；]}
      
    }
  }
]) 

// 读取 JSON 数据文件:contentReference[oaicite:6]{index=6}
#let entries = json("../library/glossary.json")
#let sorted = entries.sorted(key: e => e.pinyin)

#let current-letter = none
#let current-pinyin = none
#let item_counter = 0
#let index_page_list = ()
#for entry in sorted {
  let first-letter = entry.pinyin.find(reg_pinyin_index)
  let first-pinyin = entry.pinyin.split(regex("[0-9]")).at(0)


  // generate chapter
  if current-letter != first-letter {
    
    pagebreak()


    place(
      top + center,
      scope: "parent",
      float: true,
      text(1.4em, weight: "bold")[#heading(level: 1)[#upper(first-letter)]],
    )
    current-letter = first-letter
  }

  // generate section (per pronounciation)
  if current-pinyin != first-pinyin {
    line(start:(30%, 0%), end:(70%, 0%))
    align(center + top)[#text(1em, weight: "regular")[#heading(level: 2)[#first-pinyin]]]
    
    current-pinyin = first-pinyin
  }

  // generate section (per pronounciation)
  if current-letter != none {
    // 获取页码

    // 收集页码信息

    dict-entry(entry, current-letter, item_counter)

    item_counter += 1
  }

  parbreak()
  
}

