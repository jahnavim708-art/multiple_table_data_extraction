import pdfplumber
from utils.text_cleaner import clean_text
from utils.key_value_extractor import extract_kv_from_line


def process_pdf(pdf_path: str):

    table_data = []
    outside_data = {}

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if table:
                if not table_data:
                    table_data.extend(table)
                else:
                    table_data.extend(table[1:])

            words = page.extract_words() or []
            tables = page.find_tables()

            table_bboxes = [t.bbox for t in tables] if tables else []

            lines = {}

            for w in words:

                skip = False

                for bbox in table_bboxes:
                    tx0, ty0, tx1, ty1 = bbox

                    if tx0 <= w["x0"] <= tx1 and ty0 <= w["top"] <= ty1:
                        skip = True
                        break

                if skip:
                    continue

                key = round(w["top"], 1)

                if key not in lines:
                    lines[key] = []

                lines[key].append((w["x0"], w["text"]))

            for _, line_words in sorted(lines.items()):

                line_words.sort(key=lambda x: x[0])

                line = " ".join(w[1] for w in line_words)
                line = clean_text(line)

                k, v = extract_kv_from_line(line)

                if k and v:
                    outside_data.setdefault(k, v)

    return table_data, outside_data