"""Run MLZero chat mode (`mlzero chat`) against a local Ollama server with Gemma 4.

    python mlzero_chat.py -i data/adult.csv
    python mlzero_chat.py -i data/adult.csv --ollama-url http://192.168.1.20:11434 --model gemma4:26b
"""
import argparse
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

from omegaconf import OmegaConf

HERE = Path(__file__).parent

p = argparse.ArgumentParser(description="MLZero chat with a local Ollama model")
p.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
               help="Ollama server URL (default: $OLLAMA_URL or http://localhost:11434)")
p.add_argument("--model", default="gemma4", help="Ollama model tag (default: gemma4)")
p.add_argument("-i", "--input", help="data file or folder given to the assistant as context")
p.add_argument("-o", "--output", help="folder for session logs (default: chat_sessions/...)")
p.add_argument("-s", "--session-id", help="resume a previous session (use with -o)")
p.add_argument("-v", "--verbosity", type=int, default=1)
args = p.parse_args()

base = args.ollama_url.rstrip("/").removesuffix("/v1") + "/v1"   # OpenAI-compatible endpoint
model = args.model if ":" in args.model else args.model + ":latest"

# 1) Is the model served?
try:
    with urllib.request.urlopen(base + "/models", timeout=10) as r:
        served = [m["id"] for m in json.load(r)["data"]]
except OSError as e:
    sys.exit(f"Cannot reach Ollama at {base}: {e}")
if model not in served:
    sys.exit(f"'{model}' not on {args.ollama_url}. Run: ollama pull {model}\nServed: {served}")

# 2) MLZero has no Ollama provider: use its OpenAI provider pointed at Ollama.
os.environ["OPENAI_BASE_URL"] = base
os.environ.setdefault("OPENAI_API_KEY", "ollama")       # any non-empty string

# MLZero checks the model against OpenAI names (gpt-4*, o1*, ...); accept Ollama's names instead.
from autogluon.assistant.llm import llm_factory  # noqa: E402
llm_factory.get_openai_models = lambda: served

# 3) Inject provider / model / URL into every agent section of the config.
cfg = OmegaConf.load(HERE / "ollama_chat.yaml")
for name, section in cfg.items():
    if OmegaConf.is_dict(section):
        section.update(provider="openai", model=model, proxy_url=base)
cfg_file = Path(tempfile.mkdtemp()) / "chat.yaml"
OmegaConf.save(cfg, cfg_file)

from autogluon.assistant.chatting_agent import run_chat_agent  # noqa: E402

print(f"MLZero chat · model {model} · {base}")
run_chat_agent(input_data_folder=args.input, output_folder=args.output, config_path=str(cfg_file),
               session_id=args.session_id, verbosity=args.verbosity, interactive=True)
