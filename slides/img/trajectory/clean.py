import os


def clean_png_filenames(directory):
    # Loop through all files in the given directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(".jpg"):
            # Create new filename by removing spaces and '#'
            new_filename = filename.replace(" ", "").replace("#", "")

            # Only rename if different
            if new_filename != filename:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)

                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")


if __name__ == "__main__":
    folder = "."  # current directory, change if needed
    clean_png_filenames(folder)
