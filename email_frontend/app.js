const f = document.getElementById("form");
const text = document.getElementById("text");
const file = document.getElementById("file");
const go = document.getElementById("go");
const categoria = document.getElementById("categoria");
const resposta = document.getElementById("resposta");

f.addEventListener("submit", async (e) => {
  e.preventDefault();
  go.disabled = true;
  const original = go.textContent;
  go.textContent = "Processando...";

  try {
    const fd = new FormData();
    const t = (text.value || "").trim();
    if (t.length) fd.append("text", t);
    if (file.files.length) fd.append("file", file.files[0]);

    if (!fd.has("text") && !fd.has("file")) {
      throw new Error("Envie texto ou um arquivo (.txt, .pdf).");
    }

    const r = await fetch("/api/process-email", { method: "POST", body: fd });
    if (!r.ok) {
      let detail = "Falha ao processar";
      try {
        detail = (await r.json()).detail || detail;
      } catch {}
      throw new Error(detail);
    }
    const data = await r.json();
    categoria.textContent = data.categoria || "-";
    resposta.textContent = data.resposta || "-";
  } catch (err) {
    categoria.textContent = "Erro";
    resposta.textContent = err.message || String(err);
  } finally {
    go.disabled = false;
    go.textContent = original;
  }
});

document.getElementById("clear").addEventListener("click", () => {
  text.value = "";
  file.value = "";
  categoria.textContent = "-";
  resposta.textContent = "-";
});
