param(
  [string]$Remote = ""
)
Write-Host "Initializing ai-collab-starter (Windows)"
python .\scripts\index_docs.py
git init
git add .
git commit -m "chore: init ai-collab-starter template"
if ($Remote -ne "") {
  git remote add origin $Remote
  git branch -M main
  git push -u origin main
}
Write-Host "Done."
