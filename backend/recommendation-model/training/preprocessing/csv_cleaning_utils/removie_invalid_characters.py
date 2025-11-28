import re
from shared.path_config import path_helper
import os

# removes invisible unicode marks like U+200E and makes multi line quotes into one line
def remove_invalid_character() -> None:
    paths = path_helper()

    input_movies_metadata = paths.tmdb_all_movies_path
    output_clean = paths.tmdb_all_movies_cleaned_path
    hidden_chars = re.compile(r'[\u2028\u2029\u200E\u200F\u202A-\u202E\uFEFF]')

    with open(input_movies_metadata, "r", encoding="utf-8", errors="replace") as infile, \
        open(output_clean, "w", encoding="utf-8", newline="") as outfile:
        
        buffer = ""
        for line in infile:
            # Remove invisible unicode marks
            line = hidden_chars.sub("", line)
            buffer += line.rstrip("\r\n")
            
            # Count quotes so we know if we're inside or outside
            if buffer.count('"') % 2 == 0:
                # Finished a row — write and reset
                outfile.write(buffer + "\n")
                buffer = ""
            else:
                # Still inside a quoted field — keep merging
                buffer += " "
        
        if buffer.strip():  # write any remaining
            outfile.write(buffer + "\n")

    print(f"Cleaned and fixed CSV written to: {os.path.abspath(output_clean)}")