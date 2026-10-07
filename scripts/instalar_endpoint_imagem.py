from pathlib import Path

p = Path(r"D:\ManosMinasAI\backend\main.py")
s = p.read_text(encoding="utf-8-sig")

if "/api/image/generate" in s:
    print("ENDPOINT /api/image/generate JA EXISTE")
else:
    bloco = r'''

class ImageGenerateRequest(BaseModel):
    prompt: str
    style: str = "realista"
    credits: int = 10


@app.post("/api/image/generate")
def generate_image(data: ImageGenerateRequest):
    import requests

    if not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt vazio.")

    if data.credits != 10:
        raise HTTPException(
            status_code=400,
            detail="Cada imagem custa 10 creditos."
        )

    comfy_url = os.getenv(
        "COMFYUI_URL",
        "http://127.0.0.1:8188"
    )

    try:
        response = requests.get(
            comfy_url + "/system_stats",
            timeout=5
        )
        response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="ComfyUI nao esta disponivel. Inicie o ComfyUI."
        )

    raise HTTPException(
        status_code=501,
        detail="ComfyUI conectado, mas o workflow de imagem ainda precisa ser configurado."
    )
'''

    p.write_text(
        s + bloco,
        encoding="utf-8"
    )

    print("ENDPOINT /api/image/generate CRIADO")

