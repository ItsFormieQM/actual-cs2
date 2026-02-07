import os
import shutil

# Folder where this Python file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Folder where cleaned files will be copied
destination_folder = r"D:\actual cs2 projc\actually\static\music\Deltarune OST"  # <-- Change this to your folder

# Make sure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Loop through all files in the current folder
for filename in os.listdir(current_dir):
    # Skip directories
    if os.path.isdir(os.path.join(current_dir, filename)):
        continue

    # Remove the first 3 characters from the filename (but keep the extension)
    name, ext = os.path.splitext(filename)
    if len(name) > 3:
        new_name = name[3:] + ext
    else:
        # If the name is shorter than 3 characters, just keep the extension
        new_name = ext

    # Remove leading/trailing spaces
    new_name = new_name.strip()

    # Paths
    source_path = os.path.join(current_dir, filename)
    dest_path = os.path.join(destination_folder, new_name)

    # Copy the file with the new name
    shutil.copy2(source_path, dest_path)
    print(f"Copied: {filename} -> {new_name}")

print("All files have been copied with first 3 letters removed!")
