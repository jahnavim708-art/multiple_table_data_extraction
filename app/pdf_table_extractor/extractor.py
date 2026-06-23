import cv2

from pdf_table_extractor.pdf_loader import (
    PDFLoader
)

from pdf_table_extractor.table_detector import (
    TableDetector
)

from pdf_table_extractor.ocr_engine import (
    OCREngine
)

from pdf_table_extractor.table_reconstructor import (
    TableReconstructor
)

from pdf_table_extractor.json_exporter import (
    JSONExporter
)


def merge_multiline_rows(records):

    if not records:
        return []

    columns = list(records[0].keys())

    if not columns:
        return records

    first_column = columns[0]

    merged = []

    current = None

    for row in records:

        first_value = str(
            row.get(first_column, "")
        ).strip()

        if first_value:

            if current:
                merged.append(current)

            current = row.copy()

        else:

            if current is None:
                continue

            for key, value in row.items():

                value = str(value).strip()

                if not value:
                    continue

                existing = str(
                    current.get(key, "")
                ).strip()

                if existing:
                    current[key] = (
                        existing +
                        " " +
                        value
                    )
                else:
                    current[key] = value

    if current:
        merged.append(current)

    return merged


def process_borderless_table(pdf_path):

    pdf = PDFLoader()

    detector = TableDetector()

    ocr = OCREngine()

    reconstructor = TableReconstructor()

    exporter = JSONExporter()

    pages = pdf.load_pdf(pdf_path)

    print(f"\nTotal pages being processed: {len(pages)}")

    all_records = []

    for page_idx, page in enumerate(pages):

        print("\n" + "=" * 60)
        print(f"PAGE {page_idx + 1}/{len(pages)}")
        print("=" * 60)

        tables = detector.detect(page)

        print(f"Tables found: {len(tables)}")

        for table_idx, table_box in enumerate(tables):

            print(
                f"\nProcessing table "
                f"{table_idx + 1}/{len(tables)}"
            )

            try:

                x1, y1, x2, y2 = map(
                    int,
                    table_box
                )

                # padding for better OCR
                pad = 15

                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(page.shape[1], x2 + pad)
                y2 = min(page.shape[0], y2 + pad)

                table_img = page[
                    y1:y2,
                    x1:x2
                ]

                table_img = cv2.copyMakeBorder(
                    table_img,
                    10, 10, 10, 10,
                    cv2.BORDER_CONSTANT,
                    value=(255, 255, 255)
                )

                if table_img.size == 0:
                    print("Empty crop, skipping.")
                    continue

                words = ocr.extract(table_img)

                print(f"OCR words: {len(words)}")

                rows = reconstructor.build_table(words)

                print(f"Rows reconstructed: {len(rows)}")

                json_rows = exporter.convert(rows)

                print(f"JSON rows: {len(json_rows)}")

                json_rows = merge_multiline_rows(json_rows)

                print(f"After merge: {len(json_rows)}")

                if json_rows:
                    print("\nSample Record:")
                    print(json_rows[0])

                all_records.extend(json_rows)

            except Exception as e:

                print(
                    f"Error processing table "
                    f"{table_idx + 1}: {e}"
                )

    print("\n" + "=" * 60)
    print("OCR EXTRACTION COMPLETED")
    print("=" * 60)

    print(f"Records extracted: {len(all_records)}")

    return all_records