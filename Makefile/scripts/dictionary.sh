#!/bin/bash

# 1. Run the Python script to convert Excel to JSON
conda activate data-science

# python src/utils/convert_excel.py 
# if [ $? -ne 0 ]; then
#   echo "❌ Python script failed. Aborting build."
#   exit 1
# fi

# 2. Create output folder
mkdir -p output

# 3. Compile Typst to output folder
typst compile --root . src/doc/glossary.typ output/dictionary.pdf
if [ $? -eq 0 ]; then
  echo "✅ Build successful: ../dictionary.pdf"
else
  echo "❌ Typst compile failed."
  exit 1
  
fi

# # 4. Compile Phonetic book Typst to output folder
# typst compile --root . book.typ output/phonetics.pdf
# if [ $? -eq 0 ]; then
#   echo "✅ Build successful: ../phonetics.pdf"
# else
#   echo "❌ Typst compile failed."
#   exit 1
# fi