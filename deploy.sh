#!/bin/bash
echo "💎 Iniciando despliegue AURVO OS — Oro en movimiento..."

# Sincroniza y limpia
git add .
git commit -m "🚀 Actualización automática — AURVO OS"
git push origin main

# Activa GitHub Pages si no está habilitado
echo "⚙️ Activando GitHub Pages..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/morillogruop-maker/aurvo-os/pages \
  -f source='{"branch":"main","path":"/"}'

# Fuerza build de la página
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/morillogruop-maker/aurvo-os/pages/builds

echo "✅ Despliegue completado. Verifica tu sitio en:"
echo "🌐 https://morillogruop-maker.github.io/aurvo-os"
