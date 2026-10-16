"""Save the UCI Adult dataset (same as lab-01) to data/adult.csv for the chat demo."""
from pathlib import Path

from sklearn.datasets import fetch_openml

out = Path(__file__).parent / "data" / "adult.csv"
out.parent.mkdir(exist_ok=True)
fetch_openml("adult", version=2, as_frame=True).frame.to_csv(out, index=False)
print(f"saved {out}")
