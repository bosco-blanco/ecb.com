#!/usr/bin/env python3
"""
Genera meta descriptions unicas para productos que no las tienen.

Crea descriptions optimizadas para CTR a partir del titulo, tipo,
vendor y descripcion existente del producto.

USO:
  1. Exportar CSV de productos desde Shopify Admin
  2. python3 generate_meta_descriptions.py products_export.csv
  3. Resultado: products_meta_desc.csv
  4. Importar en Shopify

FORMATO DE META DESCRIPTION:
  "Compra [Titulo] de [Bodega]. [Tipo] [D.O.]. Envio seguro a toda Espana.
   Seleccionado por sumilleres | En Copa de Balon."
"""

import csv
import sys
import re
from pathlib import Path


def generate_meta_description(row):
    """Genera una meta description unica para un producto."""
    title = row.get("Title", "").strip()
    vendor = row.get("Vendor", "").strip()
    product_type = row.get("Type", "").strip()
    body = row.get("Body (HTML)", "").strip()

    if not title:
        return ""

    # Limpiar HTML del body para extraer primera frase util
    body_text = re.sub(r'<[^>]+>', ' ', body)
    body_text = re.sub(r'\s+', ' ', body_text).strip()

    # Construir description
    parts = []

    # Inicio con accion
    if vendor and "copa de bal" not in vendor.lower():
        parts.append(f"Compra {title} de {vendor}")
    else:
        parts.append(f"Compra {title}")

    # Tipo de producto
    if product_type:
        parts.append(f"{product_type}")

    # Extracto del body si existe (primera frase util, max 60 chars)
    if body_text:
        first_sentence = body_text.split(".")[0].strip()
        if len(first_sentence) > 15 and len(first_sentence) < 80:
            parts.append(first_sentence)

    # Cierre con CTA y marca
    parts.append("Envio seguro a toda Espana")
    parts.append("Seleccionado por sumilleres | En Copa de Balon")

    description = ". ".join(parts) + "."

    # Truncar a 155 caracteres (limite de Google)
    if len(description) > 155:
        description = description[:152] + "..."

    return description


def process_csv(input_path):
    output_path = input_path.replace(".csv", "_meta_desc.csv")
    if output_path == input_path:
        output_path = input_path.replace(".csv", "") + "_meta_desc.csv"

    generated = 0
    skipped = 0
    total = 0

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        # Verificar que el campo SEO Description existe
        if "SEO Description" not in fieldnames:
            print("AVISO: El CSV no tiene campo 'SEO Description'.")
            print("Se anadira la columna automaticamente.")
            fieldnames = list(fieldnames) + ["SEO Description"]

        rows = []
        for row in reader:
            total += 1
            title = row.get("Title", "")

            if title:  # Solo primera variante de cada producto
                existing_desc = row.get("SEO Description", "").strip()

                if not existing_desc:
                    row["SEO Description"] = generate_meta_description(row)
                    generated += 1
                else:
                    skipped += 1

            rows.append(row)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nGeneracion de meta descriptions completada.")
    print(f"Total filas: {total}")
    print(f"Descriptions generadas: {generated}")
    print(f"Descriptions existentes (no modificadas): {skipped}")
    print(f"Resultado: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generate_meta_descriptions.py <ruta_al_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"ERROR: No se encuentra '{input_file}'")
        sys.exit(1)

    process_csv(input_file)
