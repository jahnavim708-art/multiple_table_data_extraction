from fastapi import FastAPI, HTTPException
import base64
import tempfile
import os
import numpy as np

# from models import PDFRequest
# from utils.pdf_processor import process_pdf
from app.models import PDFRequest
from app.utils.pdf_processer import process_pdf

app = FastAPI()


@app.post("/extract-table")
async def pdf_to_csv(request: PDFRequest):

    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            pdf_path = temp_pdf.name

        table_data, outside_data = process_pdf(pdf_path)

        os.remove(pdf_path)

        if not table_data:
            raise HTTPException(status_code=404, detail="No table found")

        # ----------------------------
        # TABLE → JSON
        # ----------------------------
        rows = [r for r in table_data if isinstance(r, list)]

        headers = rows[0]
        data_rows = rows[1:]

        json_data = []

        for row in data_rows:

            obj = {}

            for i, col in enumerate(headers):
                obj[col] = row[i] if i < len(row) else ""

            json_data.append(obj)

        # clean NaN
        for r in json_data:
            for k, v in r.items():
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    r[k] = ""

        return {
            "status": "success",
            "file_name": request.file_name,
            "outside_data": outside_data,
            "table_data": json_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))