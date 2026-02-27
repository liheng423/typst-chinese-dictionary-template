
# Typst-Based Chinese Dictionary

A Chinese dictionary generator written in [Typst](https://typst.app), designed for formatting and printing customized dictionary entries in beautiful typesetting.

## Features

- Easy-to-edit EXCEL or JSON entries
- Automatic pinyin superscript (TODO)
- Clean Typst layout with dynamic font sizing
- Ideal for language learners and custom dictionary printing

## Quick Start

1. Clone the repository:
   ```bash
      git clone https://github.com/liheng423/typst-chinese-dictionary.git
   ```

2. Specify the glossary excel in build.sh that you want to compile, which later will be converted into a json file.
   ```bash
      typst compile --root . mainmatter/glossary.typ output/dictionary.pdf # <=== This line, edit glossary to glossary-example, or your glossary file
      if [ $? -eq 0 ]; then
      echo "✅ Build successful: ../dictionary.pdf"
      else
      echo "❌ Typst compile failed."
      exit 1
      fi
   ```

3. Open `main.typ` in [Typst Web App](https://typst.app/) or compile locally using CLI:
   ```bash
      ./build.sh
   ```

## Contributing

Pull requests and issues are welcome! For major changes, please open an issue first.

```text
1. Fork the repo  
2. Make your changes  
3. Submit a pull request
```

## License

The MIT License (MIT)
Copyright © 2025 liheng423
