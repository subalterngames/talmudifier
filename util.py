from pathlib import Path


# Set and create the output directory.
output_directory = Path("../Output")
if not output_directory.exists():
    output_directory.mkdir()
output_directory = str(output_directory.resolve())
