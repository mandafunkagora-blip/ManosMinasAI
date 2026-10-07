param([int]$Port=8000)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$prefix = "http://127.0.0.1:$Port/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host ""
Write-Host "MANOS E MINAS AI" -ForegroundColor Cyan
Write-Host "SITE: $prefix" -ForegroundColor Green
Write-Host "PASTA: $Root" -ForegroundColor DarkGray
Start-Process "$prefix"
$mime=@{'.html'='text/html; charset=utf-8';'.js'='application/javascript';'.css'='text/css';'.mp4'='video/mp4';'.png'='image/png';'.jpg'='image/jpeg';'.jpeg'='image/jpeg';'.svg'='image/svg+xml';'.json'='application/json';'.txt'='text/plain; charset=utf-8'}
function Send-File($ctx,$file){
  $fi=Get-Item -LiteralPath $file
  $start=0;$end=$fi.Length-1
  $range=$ctx.Request.Headers['Range']
  if($range -match '^bytes=(\d+)-(\d*)$'){
    $start=[int64]$matches[1]
    if($matches[2]){$end=[int64]$matches[2]}
    if($end -ge $fi.Length){$end=$fi.Length-1}
    $ctx.Response.StatusCode=206
    $ctx.Response.AddHeader('Content-Range',"bytes $start-$end/$($fi.Length)")
  }
  $len=$end-$start+1
  $ctx.Response.ContentLength64=$len
  $ext=[IO.Path]::GetExtension($file).ToLower()
  if($mime.ContainsKey($ext)){$ctx.Response.ContentType=$mime[$ext]}
  $fs=[IO.File]::OpenRead($file);$fs.Position=$start
  try{
    $buf=New-Object byte[] 65536;$left=$len
    while($left -gt 0){$n=$fs.Read($buf,0,[int][Math]::Min($buf.Length,$left));if($n -le 0){break};$ctx.Response.OutputStream.Write($buf,0,$n);$left-=$n}
  }finally{$fs.Dispose();$ctx.Response.OutputStream.Close()}
}
while($listener.IsListening){
 try{
  $ctx=$listener.GetContext();$url=$ctx.Request.Url.AbsolutePath.TrimStart('/')
  if([string]::IsNullOrWhiteSpace($url)){$url='index.html'}
  $safe=[Uri]::UnescapeDataString($url).Replace('/','\')
  $full=[IO.Path]::GetFullPath((Join-Path $Root $safe))
  if(-not $full.StartsWith([IO.Path]::GetFullPath($Root),[StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $full -PathType Leaf)){ $ctx.Response.StatusCode=404;$ctx.Response.Close();continue }
  Send-File $ctx $full
 }catch{}
}
