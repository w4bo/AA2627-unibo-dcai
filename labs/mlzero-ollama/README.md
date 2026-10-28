# MLZero chat mode + Ollama (Gemma 4) - self-contained Docker demo

[MLZero](https://github.com/autogluon/autogluon-assistant) chat mode answers data-analysis and ML questions
about a dataset, grounded in AutoGluon tutorials it retrieves. It **does not run any code**.
Everything runs in Docker: Ollama (Gemma 4 for chat, EmbeddingGemma for tutorial retrieval), MLZero and the
demo dataset (UCI Adult).

| File | Purpose |
|---|---|
| `docker-compose.yml` | Ollama + model download + chat |
| `docker-compose.gpu.yml` | optional: gives Ollama the NVIDIA GPU |
| `Dockerfile` | extends the course image `w4bo/python:1.0.7` with MLZero and the data |
| `requirements.txt` | packages added on top of the base image |
| `mlzero_chat.py` | launcher: `--ollama-url`, `--model`, `--embed-model`, `-i <data>` |
| `ollama_chat.yaml` | per-agent settings (temperature, max tokens, memory) |
| `prepare_data.py` | writes the Adult dataset to `data/adult.csv` (run at build time) |

## Run

```bash
cd labs/mlzero-ollama
docker compose build          # once (needs internet: base image, MLZero, dataset)
docker compose run --rm chat  # starts Ollama, pulls the models on first run, opens the chat
docker compose down           # stops Ollama; downloaded models stay in the `ollama-models` volume
```

With an NVIDIA GPU (much faster), add the override file to every command:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml run --rm chat
```

Type `exit` to quit. Each answer is saved on the host in `chat_sessions/<timestamp>/conversations/`.
The first chat also embeds MLZero's ~170 tutorial summaries and saves the index in `indices/`; later chats
reuse it.

Example questions:

- *What are the data types and missing values? Which columns need cleaning?*
- *Is the target `class` imbalanced? How should I evaluate a model on it?*
- *Which features are likely most predictive of income, and why?*
- *Write the AutoGluon code to train a classifier on this file with a 5-minute budget.*

## Options

Set these in the shell or in a `.env` file next to `docker-compose.yml`:

| Variable | Default | |
|---|---|---|
| `OLLAMA_MODEL` | `gemma4` (= `gemma4:e4b`) | e.g. `gemma4:26b` (MoE), `gemma4:31b` - pulled automatically |
| `OLLAMA_EMBED_MODEL` | `embeddinggemma` | embedding model for tutorial retrieval (one index per model) |
| `OLLAMA_URL` | `http://ollama:11434` | point to another Ollama server instead of the bundled one |

```bash
OLLAMA_MODEL=gemma4:26b docker compose run --rm chat           # Bash
$env:OLLAMA_MODEL="gemma4:26b"; docker compose run --rm chat    # PowerShell
```

Command-line flags still work and win over the variables:

```bash
docker compose run --rm chat python mlzero_chat.py -i data/adult.csv --model gemma4:26b --ollama-url http://192.168.1.20:11434
```

Your own data: mount it and pass it with `-i`, e.g.
`docker compose run --rm -v "${PWD}/mydata:/lab/mydata" chat python mlzero_chat.py -i mydata/file.csv`.

## How it works

`docker compose run chat` starts `ollama` (waits until healthy), then the one-shot `ollama-pull`
(downloads the model, a no-op afterwards), then the chat container.

MLZero has no Ollama provider, but Ollama serves an OpenAI-compatible API at `<url>/v1`. The launcher:

1. checks that the model is served (`<url>/v1/models`);
2. uses MLZero's `openai` provider with `OPENAI_BASE_URL=<url>/v1` and a dummy API key;
3. replaces MLZero's model-name check (which only accepts `gpt-4*`, `o1*`, ...) with the list Ollama serves;
4. replaces MLZero's embedding model (`BAAI/bge-base-en-v1.5` from Hugging Face) with Ollama's
   `/v1/embeddings`, and stores the tutorial index in `indices/<embedding model>/`;
5. writes provider, model and URL into every agent section of `ollama_chat.yaml` and starts the chat.

## Notes

- First run downloads the models (`gemma4` ≈ 10 GB, `embeddinggemma` < 1 GB). On CPU only, expect slow answers; prefer the GPU file.
- The base image has Python 3.14; MLZero declares `<3.13`, so it is installed with `--ignore-requires-python`
  (chat mode tested on 3.14). It also downgrades `transformers` to 4.48 (MLZero pins `<4.49`), which is why
  this is a separate image rather than a change to `w4bo/python`.
- Only the first ~5,000 characters of each data file go into the prompt: the model sees the schema and a
  sample, not the whole dataset.
- After editing `mlzero_chat.py` or `ollama_chat.yaml`, rebuild with `docker compose build`.
