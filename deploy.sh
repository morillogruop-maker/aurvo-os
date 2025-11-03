#!/bin/bash
set -euo pipefail

echo "💎 Iniciando despliegue AURVO OS — Oro en movimiento..."

# Sincroniza y limpia
if ! git diff --quiet; then
  git add .
  git commit -m "🚀 Actualización automática — AURVO OS"
fi
git push origin main

# Activa GitHub Pages si no está habilitado
if command -v gh >/dev/null 2>&1; then
  echo "⚙️ Activando GitHub Pages..."
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    /repos/morillogruop-maker/aurvo-os/pages \
    -f source='{"branch":"main","path":"/"}'

  echo "🚀 Lanzando workflow de backend en GitHub Actions..."
  gh workflow run aurvo-backend --ref main || true

  echo "🛠 Fuerza build de la página"
  gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    /repos/morillogruop-maker/aurvo-os/pages/builds
else
  echo "⚠️ GitHub CLI no disponible; omitiendo automatizaciones remotas."
fi

echo "✅ Despliegue completado."
echo "🌐 https://morillogruop-maker.github.io/aurvo-os"
echo "📦 Imagen del backend: ghcr.io/morillogruop-maker/aurvo-backend:latest"
