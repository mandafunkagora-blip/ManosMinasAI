$ErrorActionPreference = "Stop"

$index = "D:\ManosMinasAI\ManosMinasAI_Abertura_v2\index.html"

if (!(Test-Path $index)) {
    Write-Host "ERRO: index.html nao encontrado." -ForegroundColor Red
    exit 1
}

$html = [System.IO.File]::ReadAllText($index, [System.Text.Encoding]::UTF8)

if ($html.Contains("mmImageModal")) {
    Write-Host "JANELA GERAR IMAGEM JA EXISTE." -ForegroundColor Yellow
    exit 0
}

$block = @'
<!-- MANOS E MINAS AI - GERAR IMAGEM -->
<div id="mmImageModal" style="display:none;position:fixed;inset:0;z-index:999999;background:rgba(0,0,0,.90);align-items:center;justify-content:center;font-family:Arial,sans-serif;">
  <div style="width:min(850px,94vw);max-height:92vh;overflow:auto;background:#101018;border:1px solid rgba(255,255,255,.20);border-radius:22px;padding:25px;color:#fff;box-shadow:0 0 60px rgba(170,0,255,.40);">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <div>
        <div style="font-size:12px;letter-spacing:4px;opacity:.60;">MANOS E MINAS AI</div>
        <h2 style="margin:5px 0;font-size:30px;">GERAR IMAGEM</h2>
      </div>

      <button onclick="mmCloseImage()" style="width:42px;height:42px;border:0;border-radius:50%;background:#222;color:#fff;font-size:24px;cursor:pointer;">×</button>
    </div>

    <div style="background:#181824;border-radius:14px;padding:14px 18px;margin-bottom:18px;display:flex;justify-content:space-between;">
      <span>Seus créditos</span>
      <strong id="mmCredits" style="font-size:22px;">100</strong>
    </div>

    <label style="display:block;margin-bottom:8px;font-weight:bold;">Descreva a imagem</label>

    <textarea
      id="mmImagePrompt"
      placeholder="Descreva a imagem que você quer criar..."
      style="width:100%;height:140px;box-sizing:border-box;background:#08080d;color:#fff;border:1px solid #333;border-radius:14px;padding:15px;font-size:16px;resize:vertical;"
    ></textarea>

    <div style="display:flex;gap:12px;align-items:center;margin-top:15px;flex-wrap:wrap;">

      <select id="mmImageStyle" style="background:#181824;color:#fff;border:1px solid #333;border-radius:10px;padding:12px;">
        <option value="realista">Realista</option>
        <option value="cinematografico">Cinematográfico</option>
        <option value="anime">Anime</option>
        <option value="3d">3D</option>
        <option value="fantasia">Fantasia</option>
        <option value="arte_digital">Arte digital</option>
      </select>

      <span style="opacity:.7;">
        Custo: <strong>10 créditos</strong>
      </span>

      <button
        id="mmGenerateImageBtn"
        onclick="mmGenerateImage()"
        style="margin-left:auto;border:0;border-radius:12px;padding:13px 24px;background:linear-gradient(90deg,#8b00ff,#ff008c,#00d9ff);color:#fff;font-weight:bold;cursor:pointer;"
      >
        GERAR IMAGEM
      </button>

    </div>

    <div id="mmImageStatus" style="display:none;margin-top:18px;padding:14px;border-radius:12px;background:#181824;"></div>

    <div id="mmImageResult" style="margin-top:20px;text-align:center;"></div>

  </div>
</div>

<script>
(function(){

  const MM_IMAGE_COST = 10;
  const MM_CREDITS_KEY = "manos_minas_credits";

  function getCredits(){
    let value = parseInt(localStorage.getItem(MM_CREDITS_KEY) || "100", 10);

    if(isNaN(value) || value < 0){
      value = 0;
    }

    localStorage.setItem(MM_CREDITS_KEY, value);
    return value;
  }

  function updateCredits(){
    const el = document.getElementById("mmCredits");

    if(el){
      el.textContent = getCredits();
    }
  }

  window.mmOpenImage = function(){

    const modal = document.getElementById("mmImageModal");

    if(modal){

      modal.style.display = "flex";

      updateCredits();

      setTimeout(function(){

        const input = document.getElementById("mmImagePrompt");

        if(input){
          input.focus();
        }

      },100);

    }

  };

  window.mmCloseImage = function(){

    const modal = document.getElementById("mmImageModal");

    if(modal){
      modal.style.display = "none";
    }

  };

  window.mmGenerateImage = async function(){

    const prompt = document.getElementById("mmImagePrompt").value.trim();
    const style = document.getElementById("mmImageStyle").value;
    const status = document.getElementById("mmImageStatus");
    const result = document.getElementById("mmImageResult");
    const button = document.getElementById("mmGenerateImageBtn");

    if(!prompt){

      status.style.display = "block";
      status.textContent = "Digite o que você quer criar.";

      return;
    }

    let credits = getCredits();

    if(credits < MM_IMAGE_COST){

      status.style.display = "block";
      status.textContent = "Você precisa de 10 créditos para gerar uma imagem.";

      return;
    }

    status.style.display = "block";
    status.textContent = "Gerando sua imagem...";

    result.innerHTML = "";

    button.disabled = true;
    button.style.opacity = ".5";

    try{

      const response = await fetch("/api/image/generate", {

        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({

          prompt: prompt,
          style: style,
          credits: MM_IMAGE_COST

        })

      });

      const data = await response.json();

      if(!response.ok){

        throw new Error(
          data.detail || "Não foi possível gerar a imagem."
        );

      }

      if(!data.image_url){

        throw new Error(
          "O servidor não retornou a imagem."
        );

      }

      localStorage.setItem(
        MM_CREDITS_KEY,
        String(credits - MM_IMAGE_COST)
      );

      updateCredits();

      result.innerHTML =
        '<img src="' + data.image_url + '" style="max-width:100%;border-radius:16px;">' +
        '<div style="margin-top:12px;opacity:.7;">10 créditos utilizados</div>';

      status.textContent = "Imagem criada com sucesso.";

    }catch(error){

      status.textContent = error.message;

    }finally{

      button.disabled = false;
      button.style.opacity = "1";

    }

  };

  document.addEventListener("keydown", function(event){

    if(event.key === "Escape"){
      window.mmCloseImage();
    }

  });

  updateCredits();

})();
</script>
'@

$html = $html.Replace("</body>", $block + "`r`n</body>")

[System.IO.File]::WriteAllText(
    $index,
    $html,
    (New-Object System.Text.UTF8Encoding($false))
)

Write-Host ""
Write-Host "============================================"
Write-Host " JANELA GERAR IMAGEM INSTALADA"
Write-Host "============================================"
Write-Host "Arquivo:"
Write-Host $index
Write-Host ""