from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from openai import OpenAI

app = FastAPI(title="Manos e Minas AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://manosminasai.onrender.com", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_MODEL = "gpt-5-mini"

GOOGLE_CLIENT_ID = "971139851104-nbc8c854pcpc1c5d8hgu6p02t4vmq3v9.apps.googleusercontent.com"

class LyricsRequest(BaseModel):
    tema: str = ""
    estilo: str = ""
    clima: str = ""
    idioma: str = "português"
    estrutura: str = "verso, pré-refrão, refrão, ponte"

class GoogleCredential(BaseModel):
    credential: str

class GptRequest(BaseModel):
    session_id: str = ""
    message: str

@app.get("/")
def root():
    return {"status": "online", "system": "Manos e Minas AI"}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Manos e Minas AI API"}

@app.post("/api/auth/google")
def google_login(data: GoogleCredential):
    try:
        info = id_token.verify_oauth2_token(
            data.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        if info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("issuer invalido")
        if not info.get("email"):
            raise ValueError("email ausente")
        return {
            "ok": True,
            "name": info.get("name", ""),
            "email": info.get("email", ""),
            "picture": info.get("picture", ""),
            "sub": info.get("sub", "")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Token Google invalido")


@app.post("/api/lyrics/generate")
def generate_lyrics(data: LyricsRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada no servidor")
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Crie uma letra musical original em {data.idioma}. Tema: {data.tema}. Estilo: {data.estilo}. Clima: {data.clima}. Estrutura: {data.estrutura}. Não explique o processo. Entregue somente a letra, organizada com marcadores como [VERSO], [PRÉ-REFRÃO], [REFRÃO], [PONTE]."
        response = client.responses.create(model=OPENAI_MODEL, input=prompt)
        return {"ok": True, "lyrics": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar letra: {str(e)}")


class GptRequest(BaseModel):
    session_id: str = ""
    message: str

@app.post("/api/gpt/chat")
def gpt_chat(data: GptRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada no servidor")
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(model=OPENAI_MODEL, instructions="Voce e o GPT principal do Manos e Minas AI. Seja natural, criativo e inteligente. Para musica, crie letras completas, longas, originais e desenvolvidas. Nunca entregue uma letra curta ou generica.", input=data.message)
        return {"ok": True, "session_id": data.session_id, "response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no GPT: {str(e)}")


class ImageGenerateRequest(BaseModel):
    prompt: str
    style: str = "realista"
    credits: int = 10


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
