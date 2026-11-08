FROM mirror.gcr.io/library/python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# The embedding model (minishlab/potion-base-8M, MIT licence, 30 MB), fetched
# once while building, at a fixed revision. Nothing is downloaded at run time.
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('minishlab/potion-base-8M', revision='bf8b056651a2c21b8d2565580b8569da283cab23', local_dir='/app/embedder', allow_patterns=['config.json', 'model.safetensors', 'tokenizer.json'])" \
    && chmod -R a+rX /app/embedder && rm -rf /app/embedder/.cache
# The decision log's folder: a new named volume copies its owner from here.
# data/ is made here so that COPY --chmod below sets only the files' mode.
RUN mkdir /data /app/data && chown 10001:10001 /data
COPY --chmod=644 app.py decisions.py memory.py routing.py pipeline.py gateway_client.py \
    evaluate.py replay.py ./
COPY --chmod=644 data/cases.jsonl data/inbox.jsonl ./data/
USER 10001:10001
ENV HOME=/tmp
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
