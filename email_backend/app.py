from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import io

from pypdf import PdfReader
from .schemas import EmailResult
from .ai_providers import categorize_respond 

# Instancia da minha FastAPI
app = FastAPI(title="Email Backend API", version="0.2.0")

# Cors para permitir requisições de outros domínios e credenciais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_content_from_file(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    if filename.endswith(".txt"):
        raw = file.file.read()
        return raw.decode("utf-8", errors="ignore")
    elif filename.endswith(".pdf"):
        raw = file.file.read()
        reader = PdfReader(io.BytesIO(raw))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text_joined = "\n".join(pages_text).strip()
    if not text_joined:
        raise HTTPException(status_code=400, detail="Não foi possível extrair texto do .txt ou .pdf!")
    return text_joined

@app.post("/api/process-email", response_model=EmailResult)
async def process_email(
    text: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None)
):
    if not text and not file:
        raise HTTPException(status_code=400, detail="Envie um texto ou arquivo (.txt, .pdf)")

    if file:
        content = extract_content_from_file(file)
    else:
        content = (text or "")

    content = content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Conteúdo vazio após extração.")    

    categoria, resposta = categorize_respond(content)
    return EmailResult(categoria=categoria, resposta=resposta)


app.mount("/", StaticFiles(directory="email_frontend", html=True), name="email_frontend")

