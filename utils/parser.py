# Text Parser & Formatter Helpers
def clean_title(title: str) -> str:
    return title.strip().replace("/", "_")
