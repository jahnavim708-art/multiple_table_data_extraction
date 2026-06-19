from fastapi import FastAPI, HTTPException
import base64
import tempfile
import os
import numpy as np
import uvicorn

# from models import PDFRequest
# from utils.pdf_processor import process_pdf
from models import PDFRequest
from utils.pdf_processer import process_pdf
from utils.transaction_extractor import extract_transactions
app = FastAPI()


@app.post("/extract-table")
async def pdf_to_csv(request: PDFRequest):

    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            pdf_path = temp_pdf.name

        # Existing extraction
        table_data, outside_data = process_pdf(pdf_path)

        # HDFC transaction extraction
        transaction_data = extract_transactions(pdf_path)

        os.remove(pdf_path)

        if not table_data and not transaction_data:
            raise HTTPException(
                status_code=404,
                detail="No data found in PDF"
            )

        # ----------------------------
        # TABLE → JSON
        # ----------------------------
        json_data = []

        if table_data:

            rows = [r for r in table_data if isinstance(r, list)]

            if rows:

                headers = rows[0]
                data_rows = rows[1:]

                for row in data_rows:

                    obj = {}

                    for i, col in enumerate(headers):
                        obj[col] = row[i] if i < len(row) else ""

                    json_data.append(obj)

                # Clean NaN values
                for r in json_data:
                    for k, v in r.items():
                        if v is None or (
                            isinstance(v, float)
                            and np.isnan(v)
                        ):
                            r[k] = ""

        return {
            "status": "success",
            "file_name": request.file_name,
            "outside_data": outside_data,
            "table_data": json_data,
            "transaction_data": transaction_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
if __name__ == "__main__":
    uvicorn.run(
        "main:app",      # filename:app_instance
        host="0.0.0.0",
        port=8000,
        reload=True
    )        