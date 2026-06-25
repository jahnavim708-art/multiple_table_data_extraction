from fastapi import FastAPI, HTTPException
import base64
import tempfile
import os
import numpy as np
import uvicorn

from models import PDFRequest
from utils.hybrid_pdf_processor import process_hybrid_pdf


from utils.pdf_processer import process_pdf
from utils.hdfc_extractor import extract_transactions

app = FastAPI()


@app.post("/extract-table")
async def pdf_to_csv(request: PDFRequest):

    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            pdf_path = temp_pdf.name
        # DEBUG
        print("PDF Path:", pdf_path)
        print("File Exists:", os.path.exists(pdf_path))

        # ============================
        # Existing logic (UNCHANGED)
        # ============================
        table_data, outside_data = process_hybrid_pdf(pdf_path)
        print("After process_hybrid_pdf")
        print("File Exists:", os.path.exists(pdf_path))
        # ============================
        # 
        # ============================
        #transaction_data = extract_transactions(pdf_path)

        

        # ============================
        # EXISTING validation (unchanged)
        # ============================
        table_data = extract_transactions(pdf_path)

        if not table_data:
            raise HTTPException(
                status_code=404,
                detail="No data found in PDF"
            )


        return {
            "status": "success",
            "file_name": request.file_name,
            "outside_data": outside_data,
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


# ============================
# Nikhitha addition (entry point)
# ============================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )