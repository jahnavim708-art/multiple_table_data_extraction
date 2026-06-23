import re
import pdfplumber


def extract_transactions(pdf_path):

    all_rows = []

    def is_valid_date(text):
        if not text:
            return False

        pattern = r"\b\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}\b"
        return bool(re.search(pattern, text))

    with pdfplumber.open(pdf_path) as pdf:

        columns = []
        headers = []
        current_row = None

        for page in pdf.pages:

            tables = page.find_tables()
            if not tables:
                continue

            table = tables[0]

            raw = table.extract()

            # header detection (first valid occurrence)
            if raw and not headers:
                headers = [str(x).strip() for x in raw[0]]

                xs = sorted({c[0] for c in table.cells} | {c[2] for c in table.cells})

                columns = [
                    {
                        "name": headers[i] if i < len(headers) else f"col_{i}",
                        "x0": xs[i],
                        "x1": xs[i + 1]
                    }
                    for i in range(len(xs) - 1)
                ]

            if not columns:
                continue

            words = page.extract_words() or []

            lines = []

            for w in words:

                if w["top"] < table.bbox[1] or w["top"] > table.bbox[3]:
                    continue

                placed = False

                for line in lines:
                    if abs(w["top"] - line["top"]) <= 5:
                        line["words"].append(w)
                        placed = True
                        break

                if not placed:
                    lines.append({"top": w["top"], "words": [w]})

            lines.sort(key=lambda x: x["top"])

            for line in lines:

                row = {c["name"]: "" for c in columns}

                for w in sorted(line["words"], key=lambda x: x["x0"]):

                    mid = (w["x0"] + w["x1"]) / 2

                    for c in columns:
                        if c["x0"] <= mid <= c["x1"]:
                            row[c["name"]] += " " + w["text"]
                            break

                row = {k: v.strip() for k, v in row.items()}

                if not any(row.values()):
                    continue

                text = " ".join(row.values()).lower()

                if "date description narration" in text:
                    continue

                date_col = columns[0]["name"]
                for c in columns:
                    if "date" in c["name"].lower():
                        date_col = c["name"]

                if is_valid_date(row.get(date_col, "").replace(" ", "")):

                    if current_row:
                        all_rows.append(current_row)

                    current_row = row

                else:

                    if current_row:
                        desc_col = None

                        for c in columns:
                            if "desc" in c["name"].lower() or "narration" in c["name"].lower():
                                desc_col = c["name"]
                                break

                        if desc_col and row.get(desc_col):
                            current_row[desc_col] += " " + row[desc_col]

        if current_row:
            all_rows.append(current_row)

    return all_rows