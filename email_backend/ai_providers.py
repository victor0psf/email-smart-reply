import os, re, json
from typing import Tuple

# ---------------- Heurística ---------------- #

def category_by_rules(text: str) -> str:
    t = (text or "").lower()

    produtivo_kw = [
        "status","protocolo","andamento","prazo","suporte","erro","falha","bug",
        "problema","reclama","atualização","atualizacao","retorno","urgente",
        "comprovante","anexo","nota fiscal","boleto","pagamento","cobrança",
        "cancelamento","cancelar","cadastro","senha","acesso","bloqueio",
        "desbloqueio","fatura","contrato"
    ]
    improdutivo_kw = [
        "obrigado","agradeço","agradeco","grato","feliz natal","boas festas",
        "parabéns","parabens","bom dia","boa tarde","boa noite","agradecimento",
        "sem mais","att","atenciosamente"
    ]

    produtivo = any(k in t for k in produtivo_kw)
    improdutivo = any(k in t for k in improdutivo_kw)

    if produtivo and not improdutivo:
        return "Produtivo"
    if improdutivo and not produtivo:
        return "Improdutivo"

    if "?" in t or re.search(r"\b(nº|n°|n[uú]mero|protocolo|pedido\s*#?\d+)\b", t):
        return "Produtivo"

    return "Improdutivo"


def template_reply(category: str) -> str:
    if category == "Produtivo":
        return (
            "Olá! Obrigado pela sua mensagem. Para agilizar o atendimento, por favor confirme:\n"
            "- CPF/CNPJ do titular\n"
            "- Número de protocolo (se houver)\n"
            "- Breve descrição do problema\n\n"
            "Assim que recebermos, damos sequência e retornamos com a atualização do caso."
        )
    return (
        "Obrigado pelo contato! Registramos sua mensagem. "
        "Se precisar de suporte ou acompanhamento de atendimento, responda este email com mais detalhes."
    )

# ----------- Provedor de IA ------------ #

def use_ia() -> bool:
    """True se existir pelo menos um provedor configurado."""
    return bool(os.getenv("GROQ_API_KEY"))

def prompt_messages(text: str):
    system_prompt = (
        "Você é um assistente para uma empresa brasileira. "
        "Classifique emails em 'Produtivo' ou 'Improdutivo' e sugira uma resposta curta e educada. "
        "Regras:\n"
        "1) Se o email pede ação/status/suporte/dados/documentos ou relata problema => 'Produtivo'.\n"
        "2) Felicitações/agradecimentos/mensagens sem ação => 'Improdutivo'.\n"
        "3) Responda apenas JSON: {\"categoria\":\"Produtivo|Improdutivo\",\"resposta\":\"...\"}.\n"
        "4) Não invente dados; 2-5 linhas."
    )
    user_prompt = f"Email recebido (entre <<<>>>):\n<<<\n{text.strip()}\n>>>"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def groq(text: str):
    """Groq SDK (chave em GROQ_API_KEY)."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        out = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=prompt_messages(text),
            temperature=0.2,
            timeout=20,
            response_format={"type": "json_object"}
        )
        return out.choices[0].message.content
    except Exception:
        return None
    

def categorize_respond_ia(text: str) -> Tuple[str, str]:
    raw = None

    if os.getenv("GROQ_API_KEY"):
        raw = groq(text)

    if not raw:
        # sem resposta de nenhum provedor
        raise RuntimeError("Não foi possível obter resposta dos provedores de IA.")

    data = json.loads(raw)
    categoria = (data.get("categoria") or "").strip()
    resposta  = (data.get("resposta")  or "").strip()

    if categoria not in ("Produtivo", "Improdutivo"):
        raise ValueError("IA retornou categoria inválida.")

    if not resposta:
        raise ValueError("IA não retornou resposta.")

    return categoria, resposta

# ----------- Orquestrador com fallback ------------ #

def categorize_respond(text: str) -> Tuple[str, str]:

    if use_ia():
        try:
            raw = groq(text)
            if raw:
                data = json.loads(raw)
                categoria = (data.get("categoria") or "").strip()
                resposta = (data.get("resposta") or "").strip()
                if categoria in ("Produtivo", "Improdutivo") and resposta:
                    return categoria, resposta
        except Exception:
            pass
    categoria = category_by_rules(text)
    resposta  = template_reply(categoria)
    return categoria, resposta