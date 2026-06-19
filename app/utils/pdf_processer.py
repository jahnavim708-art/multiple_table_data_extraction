import pdfplumber
from utils.text_cleaner import clean_text
from utils.key_value_extractor import extract_kv_from_line
from utils.transaction_extractor import extract_transactions

def process_pdf(pdf_path: str):
    table_data = []
    outside_data = {}   # ONLY ONCE

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            # ----------------------------
            # TABLE EXTRACTION
            # ----------------------------
            table = page.extract_table()

            if table:
                if not table_data:
                    table_data.extend(table)
                else:
                    table_data.extend(table[1:])

            # ----------------------------
            # OUTSIDE DATA (CLEANED)
            # ----------------------------
            page_text = clean_text(page.extract_text())

            words = page.extract_words()
            tables = page.find_tables()

            table_bbox = tables[0].bbox if tables else None

            lines_map = {}

            for w in words:

                x0 = w["x0"]
                x1 = w["x1"]
                top = w["top"]
                text = w["text"]

                # skip table region
                if table_bbox:
                    tx0, ty0, tx1, ty1 = table_bbox

                    if (x0 >= tx0 and x1 <= tx1 and
                        top >= ty0 and top <= ty1):
                        continue

                key = round(top, 1)

                if key not in lines_map:
                    lines_map[key] = []

                lines_map[key].append((x0, text))

            # rebuild clean lines
            for _, words_line in sorted(lines_map.items()):

                words_line.sort(key=lambda x: x[0])

                line = " ".join([w[1] for w in words_line])

                line = clean_text(line)

                k, v = extract_kv_from_line(line)

                if k and v:
                    outside_data[k] = v   # ONLY ONCE

    return table_data, outside_data