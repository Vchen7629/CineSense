import re 

# Extract year from movie title if its in the format 'Movie Name (1995)
def extract_year_from_title(title: str) -> int | None:
    if not title:
        return None
    match = re.search(r'\((\d{4})\)$', title.strip())
    return int(match.group(1)) if match else None

# Extract title without year from 'Movie Name (1995)
def extract_title_without_year(title: str) -> str:
    if not title:
        return title
    title = title.strip()
    year = extract_year_from_title(title)
    if year:
        return title.rsplit(' (', 1)[0]
    return title
