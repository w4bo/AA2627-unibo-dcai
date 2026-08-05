import os
import re
import shutil


def clean_unused_files(folder_name, allowed_extensions):
    """
    Move unused files from folder_name to 'removed-{folder_name}' based on Markdown references.

    Args:
        folder_name (str): The folder containing files, e.g., "img" or "vid".
        allowed_extensions (set): Set of lowercase extensions, e.g., {".png", ".jpg"}.
    """
    markdown_folder = "."
    source_folder = f"./{folder_name}/"
    removed_folder = f"./removed-{folder_name}/"

    os.makedirs(removed_folder, exist_ok=True)

    # --- 1. Collect all files recursively ---
    all_files = set()
    for root, _, files in os.walk(source_folder):
        for f in files:
            ext = os.path.splitext(f.lower())[1]
            if ext in allowed_extensions:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, source_folder)
                all_files.add(rel_path.replace("\\", "/"))

    # --- 2. Regex: match any folder_name/... or ./folder_name/... reference ---
    file_reference_pattern = re.compile(
        rf'(?:\.?\/)?{folder_name}\/([\w\d()\/\s.-]*(?:{"|".join(allowed_extensions)}))',
        re.IGNORECASE,
    )

    referenced_files = set()
    for dirpath, _, filenames in os.walk(markdown_folder):
        for filename in filenames:
            if filename.endswith(".md") or filename.endswith(".qmd") or filename.endswith(".ipynb"):
                with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = file_reference_pattern.findall(content)
                    for match in matches:
                        clean = match.split("?")[0].split("#")[0].replace("%20", " ")
                        referenced_files.add(clean)

    # --- 3. Determine unused files ---
    unused_files = all_files - referenced_files
    print(f"\nUnused files in '{folder_name}':")
    if unused_files:
        for f in sorted(unused_files):
            print("  -", f)
    else:
        print("  No unused files found.")

    # --- 4. Move unused files ---
    if unused_files:
        print(f"\nMoving unused files to '{removed_folder}'...")
        for f in unused_files:
            src_path = os.path.join(source_folder, f)
            dest_path = os.path.join(removed_folder, f)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                shutil.move(src_path, dest_path)
                print(f"  ✔ Moved: {f}")
            except Exception as e:
                print(f"  ❌ Error moving {f}: {e}")

    print("\nDone.\n")


# --- Example usage with existence check ---
folders_to_clean = {
    "img": {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".webp",
        ".bmp",
        ".tiff",
        ".pdf",
        ".wmf",
    },
    "vid": {".mp4", ".mkv"},
}

for folder_name, extensions in folders_to_clean.items():
    if os.path.exists(f"./{folder_name}"):
        clean_unused_files(folder_name, extensions)
    else:
        print(f"Folder '{folder_name}' does not exist, skipping.\n")
