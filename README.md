# Email Classifier & Smart Reply

Aplicação web simples para **classificar emails** como **Produtivo** ou **Improdutivo** e **sugerir respostas automáticas**.
Interface em HTML/CSS/JS e backend em **FastAPI** (Python).
Suporta upload **.txt** e **.pdf** ou texto colado.

## Demo local

```bash
# 1) Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows PowerShell

# 2) Instale dependências
pip install -r requirements.txt

# 3) (Opcional) Defina a variável de ambiente para usar a OpenAI
# Powershell (Windows):
#   setx GROQ_API_KEY "sua_chave_aqui"
# Linux/Mac (bash):
#   export GROQ_API_KEY="sua_chave_aqui"

# 4) Rode o servidor
uvicorn backend.app:app --reload
```

Depois acesse: http://127.0.0.1:8000

> Sem `GROQ_API_KEY`, a aplicação usa um **classificador heurístico** como fallback.

## Estrutura

```
email-smart-reply/
  backend/
    app.py               # Endpoints FastAPI + leitura .txt/.pdf
    ai_providers.py      # Integração OpenAI + heurísticas fallback
    schemas.py           # Modelos Pydantic das respostas
  frontend/
    index.html           # UI HTML
    styles.css           # Estilos (gradiente escuro clean)
    app.js               # Lógica de chamada ao backend
  sample_emails/
    produtivo1.txt
    improdutivo1.txt
  requirements.txt
  render.yml            # Deploy 1‑click no Render
  .gitignore
  README.md
```

## Deploy (Render.com)

1. Crie um repositório no GitHub com estes arquivos.
2. No [Render](https://render.com), **New > Web Service** e conecte o repositório.
3. Ambiente: **Python**. O Render lerá `render.yml` com:
   - build: `pip install -r requirements.txt`
   - start: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
4. Adicione a env var `OPENAI_API_KEY` (opcional).
5. Deploy. A URL pública ficará disponível após o build.

## Como funciona (alto nível)

- Frontend envia `multipart/form-data` com `text` e/ou `file` para `/api/process-email`.
- Backend:
  - Extrai texto (inclui `.pdf` via PyPDF).
  - Se `GROQ_API_KEY` estiver setada, usa com prompt estruturado para devolver **JSON** com `categoria` e `resposta`.
  - Sem chave, roda um classificador **heurístico** simples (palavras‑chave) e gera resposta a partir de **templates**.
- A resposta volta como JSON e a UI exibe categoria e resposta.

## Observações de qualidade

- **Segurança**: o backend não salva arquivos no disco; processa em memória.
- **Robustez**: validação de tipos; fallback quando a API falha.
- **UX**: UI responsiva, status claro e mensagens de erro amigáveis.
- **Extensível**: é simples ligar outro provedor de IA em `ai_providers.py`.

---

## 👨‍💻 Autor

Desenvolvido por [Paulo Victor dos Santos Fonseca](https://github.com/victor0psf)  
Email: pvictorsf07@outlook.com
