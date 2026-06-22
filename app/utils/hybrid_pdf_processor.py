from app.utils.pdf_processer import process_pdf
from app.utils.table_validator import is_good_table

from app.pdf_table_extractor.extractor import (
    process_borderless_table
)


def process_hybrid_pdf(pdf_path):

    print("\nTrying structured table extraction...")

    table_data, outside_data = process_pdf(pdf_path)

    if is_good_table(table_data):

        print("✓ Structured table detected")
        print("✓ Using pdfplumber extraction")

        return table_data, outside_data

    print("✗ Structured extraction failed")
    print("✓ Switching to OCR extraction")

    records = process_borderless_table(pdf_path)

    if not records:
        return [], outside_data

    headers = list(records[0].keys())

    converted_table = [headers]

    for row in records:

        converted_table.append([
            row.get(h, "")
            for h in headers
        ])

    return converted_table, outside_data