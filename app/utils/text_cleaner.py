import re

def clean_text(text: str):

    if not text:
        return ""

    # remove CID artifacts like (cid:9)
    text = re.sub(r"\(cid:\d+\)", "", text)

    # remove non-printable junk
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()