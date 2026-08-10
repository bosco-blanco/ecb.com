#!/usr/bin/env bash
# ============================================================
# EXPORTAR CONFIGURACIÓN DE CLAUDE — Ejecutar en el MAC VIEJO
# ============================================================
# Empaqueta la config de Claude (skills, plugins, sesiones,
# memoria, conectores) y la deja en iCloud Drive para que
# el Mac nuevo la pueda descargar.
# ============================================================
set -euo pipefail

CLAUDE_SRC="$HOME/Library/Application Support/Claude"
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="$ICLOUD_DIR/ClaudeMigracion-$STAMP"
ARCHIVE="$OUT_DIR/claude-config-$STAMP.tar.gz"
MANIFEST="$OUT_DIR/MANIFEST.txt"

echo "==> Comprobando rutas..."
if [[ ! -d "$CLAUDE_SRC" ]]; then
  echo "ERROR: no existe $CLAUDE_SRC"
  exit 1
fi
if [[ ! -d "$ICLOUD_DIR" ]]; then
  echo "ERROR: iCloud Drive no encontrado en $ICLOUD_DIR"
  exit 1
fi

echo "==> Cerrando procesos de Claude (si los hay)..."
pkill -f Claude 2>/dev/null || true
sleep 2
if pgrep -lf Claude >/dev/null 2>&1; then
  echo "    Forzando cierre..."
  pkill -9 -f Claude 2>/dev/null || true
  sleep 2
fi

echo "==> Creando carpeta de salida en iCloud:"
echo "    $OUT_DIR"
mkdir -p "$OUT_DIR"

echo "==> Calculando tamano del origen..."
SRC_SIZE=$(du -sh "$CLAUDE_SRC" | awk '{print $1}')
echo "    Tamano: $SRC_SIZE"

echo "==> Empaquetando (puede tardar varios minutos)..."
# -C cambia al directorio padre para que el tar contenga 'Claude/...'
tar -czf "$ARCHIVE" \
  --exclude='*/Cache/*' \
  --exclude='*/GPUCache/*' \
  --exclude='*/Code Cache/*' \
  --exclude='*/ShaderCache/*' \
  --exclude='*/.DS_Store' \
  -C "$HOME/Library/Application Support" "Claude"

ARCH_SIZE=$(du -sh "$ARCHIVE" | awk '{print $1}')
echo "    Archivo creado: $ARCH_SIZE"

echo "==> Generando manifiesto..."
{
  echo "Migracion Claude — generada $(date)"
  echo "Origen: $CLAUDE_SRC"
  echo "Tamano original: $SRC_SIZE"
  echo "Tamano comprimido: $ARCH_SIZE"
  echo "Mac de origen: $(scutil --get ComputerName 2>/dev/null || hostname)"
  echo "Usuario: $USER"
  echo ""
  echo "=== Skills detectadas ==="
  find "$CLAUDE_SRC" -maxdepth 6 -name SKILL.md 2>/dev/null \
    | sed "s|$CLAUDE_SRC/||"
  echo ""
  echo "=== Plugins detectados ==="
  find "$CLAUDE_SRC" -maxdepth 4 -type d -name "plugins" 2>/dev/null \
    | sed "s|$CLAUDE_SRC/||"
  echo ""
  echo "=== Tamano por subcarpeta de primer nivel ==="
  du -sh "$CLAUDE_SRC"/* 2>/dev/null | sort -h
} > "$MANIFEST"

echo "==> Forzando subida a iCloud..."
# brctl evict/upload le pide a iCloud que sincronice ya
/usr/bin/touch "$ARCHIVE" "$MANIFEST"
brctl upload "$ARCHIVE" 2>/dev/null || true

echo ""
echo "============================================================"
echo "LISTO."
echo ""
echo "Archivo:    $ARCHIVE"
echo "Manifiesto: $MANIFEST"
echo ""
echo "Siguientes pasos:"
echo "  1. Espera a que iCloud termine de subir (mira el icono"
echo "     de iCloud en Finder; debe desaparecer la nube con"
echo "     flecha hacia arriba)."
echo "  2. En el Mac nuevo abre Finder > iCloud Drive y descarga"
echo "     la carpeta 'ClaudeMigracion-$STAMP'."
echo "  3. Ejecuta en el Mac nuevo el script:"
echo "     restore-claude-mac-nuevo.sh"
echo "============================================================"
