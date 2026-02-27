#import "@preview/hydra:0.6.1": hydra

#set page(paper: "a7", margin: (y: 4em), numbering: "1", header: context {

  align(left, emph(hydra(3, skip-starting: false)))
  line(length: 100%)
})
#show heading.where(level: 3): it => it

=== Introduction
#lorem(50)

=== Content
=== First Section
#lorem(50)
=== Second Section
#lorem(100)