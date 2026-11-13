"""Execute course notebooks, including the live Ollama exercises in lab 07.

Examples (from slides/):
    python execute-notebooks.py
    python execute-notebooks.py lab-07-rag.ipynb --output-dir /tmp/rag-results

Start Ollama and pull the model first; CI supplies its container URL via
OLLAMA_URL. Model/API failures fail execution rather than silently skipping it.
"""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", help="Notebook names relative to slides/")
    parser.add_argument("--output-dir", type=Path, help="Save executed notebooks here instead of in place")
    parser.add_argument("--timeout", type=int, default=600, help="Per-cell timeout in seconds")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    paths = [root / name for name in args.notebooks] if args.notebooks else sorted(root.glob("*.ipynb"))
    paths = [path for path in paths if "lab-00" not in path.name.lower()]
    if not paths:
        parser.error("No notebooks selected")
    for path in paths:
        print(f"Executing {path.name}", flush=True)
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        target = args.output_dir / path.name if args.output_dir else path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            NotebookClient(
                notebook,
                timeout=args.timeout,
                kernel_name="python3",
                resources={"metadata": {"path": str(path.parent)}},
            ).execute()
        finally:
            # Keep partial output too: it identifies the cell/API failure in CI.
            nbformat.write(notebook, target)
        print(f"Saved {target}", flush=True)


if __name__ == "__main__":
    main()
