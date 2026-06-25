from fastapi import FastAPI, HTTPException
import base64
import tempfile
import os
import numpy as np
import uvicorn

from models import PDFRequest



from utils.hdfc_extractor import extract_transactions

@app.post("/extract-table")
async def pdf_to_csv(request: PDFRequest):

    pdf_path = None

    try:

        pdf_bytes = base64.b64decode(
            request.pdf_base64
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_pdf:

            temp_pdf.write(pdf_bytes)
            pdf_path = temp_pdf.name

        print("PDF Path:", pdf_path)
        print("File Exists:", os.path.exists(pdf_path))

        table_data = extract_transactions(pdf_path)

        if not table_data:

            raise HTTPException(
                status_code=404,
                detail="No transaction data found"
            )

        return {
            "status": "success",
            "file_name": request.file_name,
            "outside_data": {},
            "table_data": table_data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)