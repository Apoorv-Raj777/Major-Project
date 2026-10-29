#!/bin/bash
# Build script for Render deployment

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm

# Create models directory
mkdir -p models

# Download fasttext model
cd models
wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
cd ..

# Install argos-translate language packages
argospm update
argospm install translate-en_es
argospm install translate-en_de

echo "Build completed successfully"
