import re
import os
import argparse


# ==============================
# REGEX CLEANING FUNCTIONS
# ==============================
def clean_text(text: str) -> str:
    """
    Apply all regex cleaning rules to the text.
    """
    # 2️⃣ Remove the backslash before + - , . symbols and braces
    text = re.sub(r"\\([+\-.,\}\{\(\)\[\]_#])", r"\1", text)

    # 3️⃣ Replace <span style="color:#XXXXXX">content</span> with just content
    text = re.sub(r'<span style="color:#([A-Fa-f0-9]{6})">(.*?)</span>', r"\2", text)

    # 4️⃣ Replace newline + * + space (\n* ) with two newlines (\n\n)
    text = re.sub(r"\n\*\s", "\n\n", text)

    # 5️⃣ Reduce spaces after newline before * by 2 (but never negative)
    def reduce_spaces(match):
        spaces = match.group(1)
        num_spaces = max(len(spaces) - 2, 0)
        return "\n\n" + " " * num_spaces + "*"

    text = re.sub(r"\n([ ]*)\*", reduce_spaces, text)

    # 6️⃣ Remove any spaces before punctuation: , . ! ? ; but NOT after newline
    text = re.sub(r"\s+([,\.?;])", r"\1", text)
    text = re.sub(r" !", r"!", text)

    # 1️⃣ Remove more than 2 consecutive newline characters
    text = re.sub(r"\n{3,}", "\n\n", text)

    # replace \t with \s
    text = re.sub(r"\t", " ", text)

    # replace ’ with '
    text = re.sub(r"’", "'", text)

    # replace … with ...
    text = re.sub(r"…", "...", text)

    # replace – with -
    text = re.sub(r"–", "-", text)

    # replace (cont.) with nothing
    text = re.sub(r"\s\(cont\.\)", "", text)

    # replace (e.g. ) with e.g.,
    text = re.sub(r"\s\(e\.g\.\)", " e.g., ", text)

    # replace (i.e. ) with i.e.,
    text = re.sub(r"\s\(i\.e\.\)", " i.e., ", text)

    # replace %20 with space in image paths
    # text = re.sub(r"%20", " ", text)

    # replace “ with "
    text = re.sub(r"“", '"', text)
    # replace ” with "
    text = re.sub(r"”", '"', text)
    return text


# ==============================
# MAIN PROGRAM
# ==============================


def process_file(file_path: str):
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return

    # Read the original file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply regex cleaning
    cleaned_content = clean_text(content)

    # Save cleaned file
    base, ext = os.path.splitext(file_path)
    output_path = f"{base}-clean{ext}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)

    print(f"Processed {file_path} → {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean markdown files with regex rules"
    )
    parser.add_argument("files", nargs="+", help="Markdown files to process")
    args = parser.parse_args()

    for file_path in args.files:
        process_file(file_path)


if __name__ == "__main__":
    main()
