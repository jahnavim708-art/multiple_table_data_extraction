def extract_kv_from_line(line: str):

    if ":" not in line:
        return None, None

    key, value = line.split(":", 1)

    key = key.strip()
    value = value.strip()

    if not key or not value:
        return None, None

    if len(key) > 80:
        return None, None

    return key, value