"""Run MLZero chat mode (`mlzero chat`) against a local Ollama server with Gemma 4.

    python mlzero_chat.py -i data/adult.csv
    python mlzero_chat.py -i data/adult.csv --ollama-url http://192.168.1.20:11434 --model gemma4:26b

Both the chat model and the embedding model used for tutorial retrieval are served by Ollama.
"""
import argparse
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
from omegaconf import OmegaConf

HERE = Path(__file__).parent

p = argparse.ArgumentParser(description="MLZero chat with a local Ollama model")
p.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
               help="Ollama server URL (default: $OLLAMA_URL or http://localhost:11434)")
p.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "gemma4"),
               help="chat model (default: $OLLAMA_MODEL or gemma4)")
p.add_argument("--embed-model", default=os.environ.get("OLLAMA_EMBED_MODEL", "embeddinggemma"),
               help="embedding model for tutorial retrieval (default: $OLLAMA_EMBED_MODEL or embeddinggemma)")
p.add_argument("-i", "--input", help="data file or folder given to the assistant as context")
p.add_argument("-o", "--output", help="folder for session logs (default: chat_sessions/<timestamp>)")
p.add_argument("-s", "--session-id", help="resume a previous session (use with -o)")
p.add_argument("-v", "--verbosity", type=int, default=1)
args = p.parse_args()

# MLZero's own default is inside site-packages: keep sessions next to this script instead
output = args.output or str(HERE / "chat_sessions" / datetime.now().strftime("%Y%m%d_%H%M%S"))
base = args.ollama_url.rstrip("/").removesuffix("/v1") + "/v1"   # OpenAI-compatible endpoint
tag = lambda m: m if ":" in m else m + ":latest"                  # noqa: E731
model, embed_model = tag(args.model), tag(args.embed_model)

# 1) Are both models served?
try:
    with urllib.request.urlopen(base + "/models", timeout=10) as r:
        served = [m["id"] for m in json.load(r)["data"]]
except OSError as e:
    sys.exit(f"Cannot reach Ollama at {base}: {e}")
for m in (model, embed_model):
    if m not in served:
        sys.exit(f"'{m}' not on {args.ollama_url}. Run: ollama pull {m}\nServed: {served}")

# 2) Chat LLM: MLZero has no Ollama provider, so use its OpenAI provider pointed at Ollama.
os.environ["OPENAI_BASE_URL"] = base
os.environ.setdefault("OPENAI_API_KEY", "ollama")       # any non-empty string

# MLZero checks the model against OpenAI names (gpt-4*, o1*, ...); accept Ollama's names instead.
from autogluon.assistant.llm import llm_factory  # noqa: E402
llm_factory.get_openai_models = lambda: served


# 3) Embeddings: replace MLZero's Hugging Face model (BAAI/bge-base-en-v1.5) with Ollama.
class OllamaEmbedder:
    def encode(self, texts):
        req = urllib.request.Request(base + "/embeddings", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"model": embed_model, "input": list(texts)}).encode())
        with urllib.request.urlopen(req, timeout=300) as r:
            return np.array([d["embedding"] for d in json.load(r)["data"]], dtype=np.float32)


from autogluon.assistant.tools_registry.indexing import TutorialIndexer  # noqa: E402

_init = TutorialIndexer.__init__


def _ollama_init(self, embedding_model_name=None):
    _init(self, "ollama/" + embed_model)
    # one index per embedding model, kept next to this script (built on first use, then reused)
    self.index_dir = HERE / "indices" / self.sanitized_model_name.replace(":", "_")
    self.index_dir.mkdir(parents=True, exist_ok=True)


def _ollama_load(self):
    if self.model is None:
        self.model = OllamaEmbedder()


TutorialIndexer.__init__ = _ollama_init
TutorialIndexer._load_embedding_model = _ollama_load

# 4) Inject provider / model / URL into every agent section of the config.
cfg = OmegaConf.load(HERE / "ollama_chat.yaml")
for name, section in cfg.items():
    if OmegaConf.is_dict(section):
        section.update(provider="openai", model=model, proxy_url=base)
cfg_file = Path(tempfile.mkdtemp()) / "chat.yaml"
OmegaConf.save(cfg, cfg_file)

from autogluon.assistant.chatting_agent import run_chat_agent  # noqa: E402

print(f"MLZero chat · model {model} · embeddings {embed_model} · {base}")
run_chat_agent(input_data_folder=args.input, output_folder=output, config_path=str(cfg_file),
               session_id=args.session_id, verbosity=args.verbosity, interactive=True)
