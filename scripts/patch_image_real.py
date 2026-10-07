from pathlib import Path

p = Path(r"backend\main.py")
s = p.read_text(encoding="utf-8-sig")

start = s.find('@app.post("/api/image/generate")')
if start == -1:
    start = s.find("@app.post('/api/image/generate')")

if start == -1:
    raise SystemExit("ENDPOINT_IMAGE_NAO_ENCONTRADO")

new = r"""
@app.post("/api/image/generate")
def generate_image(data: ImageGenerateRequest):
    import base64
    import random
    import time
    import requests

    if not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt vazio.")

    if data.credits != 10:
        raise HTTPException(
            status_code=400,
            detail="Cada imagem custa 10 crÃ©ditos."
        )

    comfy_url = os.getenv(
        "COMFYUI_URL",
        "http://127.0.0.1:8188"
    ).rstrip("/")

    try:
        info = requests.get(
            comfy_url + "/object_info/CheckpointLoaderSimple",
            timeout=8
        )
        info.raise_for_status()

        ckpt_info = info.json()["CheckpointLoaderSimple"]
        ckpt_list = ckpt_info["input"]["required"]["ckpt_name"][0]

        if not ckpt_list:
            raise RuntimeError(
                "Nenhum checkpoint instalado no ComfyUI."
            )

        checkpoint = ckpt_list[0]

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "ComfyUI nÃ£o estÃ¡ disponÃ­vel ou "
                "nÃ£o hÃ¡ modelo instalado: " + str(e)
            )
        )

    seed = random.randint(1, 2**63 - 1)

    positive = (
        data.prompt.strip()
        + ", "
        + data.style
        + ", high quality, detailed"
    )

    negative = (
        "low quality, blurry, distorted, deformed, "
        "bad anatomy, text, watermark"
    )

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 20,
                "cfg": 7,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },

        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": checkpoint
            }
        },

        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },

        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive,
                "clip": ["4", 1]
            }
        },

        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["4", 1]
            }
        },

        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },

        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "ManosMinasAI",
                "images": ["8", 0]
            }
        }
    }

    try:

        queued = requests.post(
            comfy_url + "/prompt",
            json={
                "prompt": workflow
            },
            timeout=15
        )

        queued.raise_for_status()

        result = queued.json()

        prompt_id = result.get("prompt_id")

        if not prompt_id:
            raise RuntimeError(
                result.get("error")
                or "ComfyUI nÃ£o retornou prompt_id."
            )

        deadline = time.time() + 180
        image_meta = None

        while time.time() < deadline:

            time.sleep(1.5)

            history = requests.get(
                comfy_url + "/history/" + prompt_id,
                timeout=10
            )

            if history.status_code != 200:
                continue

            item = history.json().get(prompt_id)

            if not item:
                continue

            status = item.get("status", {})

            if status.get("status_str") == "error":
                raise RuntimeError(
                    "ComfyUI informou erro ao executar o workflow."
                )

            outputs = item.get("outputs", {})

            for node_output in outputs.values():

                images = node_output.get("images", [])

                if images:
                    image_meta = images[0]
                    break

            if image_meta:
                break

        if not image_meta:
            raise RuntimeError(
                "Tempo esgotado aguardando a imagem do ComfyUI."
            )

        view = requests.get(
            comfy_url + "/view",
            params={
                "filename": image_meta["filename"],
                "subfolder": image_meta.get("subfolder", ""),
                "type": image_meta.get("type", "output")
            },
            timeout=30
        )

        view.raise_for_status()

        encoded = base64.b64encode(
            view.content
        ).decode("ascii")

        return {
            "ok": True,
            "image_url": (
                "data:image/png;base64,"
                + encoded
            ),
            "prompt_id": prompt_id,
            "credits_used": 10,
            "checkpoint": checkpoint
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "Erro ao gerar imagem no ComfyUI: "
                + str(e)
            )
        )
"""

p.write_text(
    s[:start] + new.lstrip(),
    encoding="utf-8"
)

print("GERACAO REAL INSTALADA")
