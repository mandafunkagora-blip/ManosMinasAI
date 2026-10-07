$ErrorActionPreference = "Stop"

$root = "D:\ManosMinasAI"
$main = Join-Path $root "backend\main.py"
$backup = Join-Path $root "backend\main.py.backup-antes-comfyui-20261006"

Write-Host "============================================"
Write-Host " MANOS E MINAS AI - BACKEND COMFYUI"
Write-Host "============================================"

if (!(Test-Path $main)) {
    Write-Host "ERRO: backend\main.py nao encontrado."
    exit 1
}

Copy-Item $main $backup -Force
Write-Host "BACKUP CRIADO:"
Write-Host $backup

python -m pip install requests

$pythonCode = @'
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

'@

$pythonFile = Join-Path $root "scripts\instalar_endpoint_imagem.py"

Set-Content -Path $pythonFile -Value $pythonCode -Encoding UTF8

python $pythonFile

Write-Host ""
Write-Host "[1] TESTANDO SINTAXE..."
python -m py_compile $main

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO DE SINTAXE."
    Copy-Item $backup $main -Force
    exit 1
}

Write-Host "PYTHON OK"

Write-Host ""
Write-Host "[2] VERIFICANDO ROTAS..."

python -c "from backend.main import app; print([r.path for r in app.routes])"

Write-Host ""
Write-Host "============================================"
Write-Host " CONCLUIDO"
Write-Host "============================================"
Write-Host ""
Write-Host "O endpoint /api/image/generate foi preparado."
Write-Host "Agora falta configurar o workflow/modelo do ComfyUI."