import os
import shutil
import sys

# Check if a directory path is provided as a command-line argument
if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    print("Please provide a directory path as a command-line argument.")
    sys.exit(1)

# Expand user directory if '~' is used
directory = os.path.join(os.path.expanduser("~"),directory)


# Verify if the provided directory exists
if not os.path.isdir(directory):
    print(f"The directory '{directory}' does not exist.")
    sys.exit(1)

extensions = {
    ".jpg": "Images",
    ".png": "Images",
    ".jpeg": "Images",
    ".svg": "Images",
    ".pdf": "Pdfs",
    ".doc": "Documents",
    ".docx": "Documents",
    ".pptx": "Slides",
    ".ppt": "Slides",
    ".exe": "Programs",
    ".ipynb": "JupyterNotebooks",
    ".bib": "Bibfiles",
    ".bbl": "Bibfiles",
    ".zip": "Compressed",
    ".tar": "Compressed",
    ".gz": "Compressed",
    ".html": "webfiles",
    ".css": "webfiles",
    ".nb": "MathematicaNotebooks",
    ".bibtex": "Bibfiles",
    ".npz": "SavedData",
    ".csv": "Spreadsheeds",
    ".xlsx": "Spreadsheeds",
    ".py": "SourceFiles",
    ".jl": "SourceFiles",
}

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
        extension = os.path.splitext(filename.strip())[1].lower()
        if extension in extensions:
            foldername = extensions[extension]
            folder_path = os.path.join(directory, foldername)
            os.makedirs(folder_path, exist_ok=True)
            destination_path = os.path.join(folder_path, filename)
            shutil.move(filepath, destination_path)
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            print(f"{filename} was moved to {foldername}. Organize yourself better man!")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        else:
            print(extension)
            if extension == ".xpi":
                os.remove(filepath)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Zotero plugin {filename} was deleted, it is unnecessary")
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if (extension == ".tiff") or (extension == ".ttf"):
                os.remove(filepath)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Font family file {filename} was deleted, it is unnecessary")
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            print(f"{filename} was Skipped, its extension does not match the targeted ones")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

print("Files were sorted")