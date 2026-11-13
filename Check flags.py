"""Run this next to MAPPY.py to compare the country names in the code with
the PNG files in the MAPS folder. It prints any names that do not match."""
import os
import re

FOLDER = os.path.dirname(os.path.abspath(__file__))


def code_names() -> list[str]:
    """Return every country name listed in MAPPY.py."""
    with open(os.path.join(FOLDER, "MAPPY.py"), encoding="utf-8") as file:
        text = file.read()
    start = text.index("COUNTRY_REGIONS = {")
    block = text[start:text.index("\n}\n", start)]
    return re.findall(r'"([^"]+)"(?!\s*:)', block)


def file_names() -> list[str]:
    """Return the names (without .png) of the files in MAPS."""
    maps_folder = os.path.join(FOLDER, "MAPS")
    return [name[:-4] for name in os.listdir(maps_folder)
            if name.lower().endswith(".png")]


def main() -> None:
    """Print names with no matching file, and files with no name."""
    in_code = set(code_names())
    on_disk = set(file_names())
    print("In the code but NO file:", sorted(in_code - on_disk))
    print("File exists but NOT in the code:", sorted(on_disk - in_code))


main()
