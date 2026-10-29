FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download xx_ent_wiki_sm

# Download fasttext language model
RUN mkdir -p /app/models && \
    cd /app/models && \
    wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin && \
    wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz

# Download argos-translate language packages
RUN argospm update && \
    argospm install translate-en_es && \
    argospm install translate-en_de

COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
