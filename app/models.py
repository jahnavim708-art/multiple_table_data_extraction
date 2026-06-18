from pydantic import BaseModel


class PDFRequest(BaseModel):
    file_name: str
    pdf_base64: str