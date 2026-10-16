# MLZero chat mode + local Ollama (Gemma 4)

[MLZero](https://github.com/autogluon/autogluon-assistant) chat mode answers data-analysis and ML questions
about your data, grounded in AutoGluon tutorials it retrieves. It **does not run any code**.

| File | Purpose |
|---|---|
| `mlzero_chat.py` | launcher: `--ollama-url`, `--model`, `-i <data>` |
| `ollama_chat.yaml` | per-agent settings (temperature, max tokens, memory) |
| `prepare_data.py` | saves the Adult dataset to `data/adult.csv` |

## 1. Ollama

```bash
OLLAMA_CONTEXT_LENGTH=32768 ollama serve   # prompts include tutorials: raise the context
ollama pull gemma4                         # = gemma4:e4b; bigger: gemma4:26b (MoE), gemma4:31b
```

On Windows, set `OLLAMA_CONTEXT_LENGTH` as a user environment variable and restart Ollama.
If the chat runs in WSL2 or on another machine, also set `OLLAMA_HOST=0.0.0.0` on the Ollama machine.

## 2. Environment (Linux or WSL2 — MLZero is Linux-only)

```bash
conda create -n mlzero python=3.11 -y && conda activate mlzero
pip install uv && uv pip install git+https://github.com/autogluon/autogluon-assistant.git scikit-learn
```

## 3. Chat

```bash
python prepare_data.py
python mlzero_chat.py -i data/adult.csv
python mlzero_chat.py -i data/adult.csv --model gemma4:26b --ollama-url http://192.168.1.20:11434
# WSL2 -> Ollama on the Windows host:
python mlzero_chat.py -i data/adult.csv --ollama-url http://$(ip route | awk '/default/{print $3}'):11434
```

`--ollama-url` defaults to `$OLLAMA_URL`, then `http://localhost:11434`. Type `exit` to quit.

Example questions:

- *What are the data types and missing values? Which columns need cleaning?*
- *Is the target `class` imbalanced? How should I evaluate a model on it?*
- *Which features are likely most predictive of income, and why?*
- *Write the AutoGluon code to train a classifier on this file with a 5-minute budget.*

Each answer is saved under `chat_sessions/<session>/conversations/qa_iterNNN.md`; resume a session with
`-o <that folder> -s <session id>`.

## How it works

MLZero has no Ollama provider, but Ollama serves an OpenAI-compatible API at `<url>/v1`. The launcher:

1. checks that the model is served (`<url>/v1/models`);
2. uses MLZero's `openai` provider with `OPENAI_BASE_URL=<url>/v1` and a dummy API key;
3. replaces MLZero's model-name check (which only accepts `gpt-4*`, `o1*`, ...) with the list Ollama serves;
4. writes provider, model and URL into every agent section of `ollama_chat.yaml` and starts the chat.

Notes: only the first ~5,000 characters of each data file go into the prompt, so the model sees the schema
and a sample, not the whole dataset. On first run MLZero downloads a small embedding model
(`BAAI/bge-base-en-v1.5`) from Hugging Face for tutorial retrieval.
