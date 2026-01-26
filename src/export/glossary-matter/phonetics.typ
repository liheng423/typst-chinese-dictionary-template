#import "../../doc/settings.typ": *
#import "../../../assets/fonts.typ": *

#align(center,
  text(20pt, font: ZhongSong)[*乐山话音系*] 

)



#text(font: font-family.KaiTi)[

#v(10pt)

#figure(

table(

  stroke: none,
	columns: 8,
  table.hline(start: 0),
	// [拼音方案], [], [], [], [], [], [], [], 
	// [声母], [], [], [], [], [], [], [], 
	[], [], table.vline(start: 0),[双唇], [唇齿], [齿后], [齿龈], [硬腭], [软腭], 
  table.hline(start: 0),
	[塞音], [不送气], [b  [p]], [], [], [d [t]], [], [g [k]], 
	[], [], [贝], [], [], [得], [], [古], 
	[], [送气], [p [pʰ]], [], [], [t [tʰ]], [], [k [kʰ]], 

	[], [], [配], [], [], [套], [], [可], 
    table.hline(start: 0),
	[塞擦音], [不送气], [], [], [ts [ts]], [], [j [tɕ]], [], 
	[], [], [], [], [早], [], [价], [], 
	[], [送气], [], [], [c [tsʰ]], [], [q [tɕʰ]], [], 
	[], [], [], [], [草], [], [巧], [], 
  table.hline(start: 0),

	[鼻音], [], [m [m]], [], [n [n]], [], [], [ng [ŋ]], 
	[], [], [没], [], [路那], [], [], [我], 
  table.hline(start: 0),
	[擦音], [清], [], [f [f]], [s [s]], [], [x [ɕ]], [h [x]], 
	[], [], [], [发], [速], [], [小], [好], 
	[], [浊], [], [v [v]], [z [z]], [], [], [], 
	[], [], [], [五], [认], [], [], [], 
  table.hline(start: 0),
	[零声母], [], [(不记)], [], [], [], [], [], 
	[], [], [衣乌], [], [], [], [], [], 
  table.hline(start: 0),
), caption: [乐山话声母表])

#v(10pt)

#figure(
table(
  stroke: none,
	columns: 14,
  table.hline(start: 0),
	[], table.cell(colspan: 5)[开尾],  table.cell(colspan: 4)[元音尾], table.cell(colspan: 4)[鼻音尾], 
  table.hline(start: 0),
	table.cell(rowspan: 3, align: horizon + center)[开口], table.vline(start: 0), [i], [a], [], [ee], [ae], table.vline(start: 0), [ai], [ei], [ao], [ou], table.vline(start: 0), [an], [en], [ang], [ong], 

	[[ɿ]], [[ɑ]], [], [[ɘ]], [[æ]], [[ai]], [[ei]], [[au]], [[əu]], [[ã]], [[ən]], [[aŋ]], [[oŋ]], 
	[磁], [茶], [], [尺], [拍撤格], [丐], [社培], [冒], [勾], [肝], [森生], [缸], [梦洪], 
  table.hline(start: 0),
	table.cell(rowspan: 3, align: horizon + center)[合口], [u], [ua], [o], [oe], [uae], [uai], [uei], [], [], [uan], [un], [uang], [], 

	[[u]], [[uɑ]], [[o]], [[ʊ]], [[uæ]], [[uai]], [[uei]], [], [], [[uã]], [[uən]], [[uaŋ]], [], 
	[姑], [瓜], [歌], [国骨], [刮], [淮], [回], [], [], [观], [准春], [光], [], 
  table.hline(start: 0),
	table.cell(rowspan: 3, align: horizon + center)[齐齿], [ii], [ia], [yoe], [ie], [iae], [iai], [], [iao], [iou], [ian], [in], [iang], [iong], 

	[[i]], [[iɑ]], [[yʊ]], [[ie]], [[iæ]], [[iɛi]], [], [[iau]], [[iəu]], [[iẽ]], [[in]], [[iaŋ]], [[ioŋ]], 
	[祭借], [架], [却屈], [吉], [甲], [介], [], [较], [救], [鉴], [近敬], [绛], [穷容], 
  table.hline(start: 0),
	table.cell(rowspan: 3, align: horizon + center)[撮口], [y], [], [], [], [], [], [], [], [], [yan], [yn], [], [], 
	[[y]], [], [], [], [], [], [], [], [], [[yẽ]], [[yn]], [], [], 
	[渠], [], [], [], [], [], [], [], [], [拳], [群琼], [], [], 
  table.hline(start: 0),
), caption: [乐山话韵母拼音方案表])<yunmu>

#v(10pt)

#figure(
table(
  stroke: none,
	columns: 5,
	// table.cell(colspan: 5, align: horizon + center)[声调],
  table.hline(start: 0),
	[阴平], [阳平], [上声], [去声], [入声], 
  table.hline(start: 0),
	[55], [21], [52], [224], [44], 
  table.hline(start: 0),
), caption: [乐山话声调表])<shengdiao>


]