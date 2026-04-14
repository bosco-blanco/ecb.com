#!/usr/bin/env python3
"""
Optimiza titulos de producto para Google Shopping y SEO.

Reformatea los titulos de los productos para incluir:
[Nombre] [Anada] [D.O.] | [Tipo] | Comprar Online

USO:
  1. Exportar CSV desde Shopify Admin > Products > Export
  2. python3 optimize_product_titles.py products_export.csv
  3. Resultado: products_seo_titles.csv
  4. Importar en Shopify Admin

NOTA: Revisar el CSV resultante antes de importar. Los titulos generados
pueden necesitar ajustes manuales para productos especiales.
"""

import csv
import sys
import re
from pathlib import Path


def extract_vintage(title):
    """Extrae el ano/anada del titulo si existe."""
    match = re.search(r'\b(19|20)\d{2}\b', title)
    return match.group(0) if match else ""


def optimize_title(row, fieldnames):
    """Genera un titulo SEO-optimizado a partir de los datos del producto."""
    title = row.get("Title", "")
    product_type = row.get("Type", "")
    vendor = row.get("Vendor", "")

    if not title:
        return title

    vintage = extract_vintage(title)

    # Determinar tipo de vino para el sufijo
    type_map = {
        "vino tinto": "Vino Tinto",
        "vino blanco": "Vino Blanco",
        "vino rosado": "Vino Rosado",
        "espumoso": "Espumoso",
        "cava": "Cava",
        "champagne": "Champagne",
        "cerveza": "Cerveza",
        "destilado": "Destilado",
        "whisky": "Whisky",
        "gin": "Gin",
        "ron": "Ron",
        "vodka": "Vodka",
        "tequila": "Tequila",
        "vermut": "Vermut",
        "licor": "Licor",
    }

    suffix = ""
    type_lower = product_type.lower() if product_type else ""
    title_lower = title.lower()

    for key, val in type_map.items():
        if key in type_lower or key in title_lower:
            suffix = val
            break

    # No modificar si el titulo ya esta optimizado
    if "| Comprar" in title or "| comprar" in title:
        return title

    # Construir titulo optimizado
    # Si ya tiene el tipo en el titulo, no duplicar
    if suffix and suffix.lower() not in title_lower:
        new_title = f"{title} | {suffix} | Comprar Online"
    else:
        new_title = f"{title} | Comprar Online"

    # Limitar a 150 caracteres (limite de Google Shopping)
    if len(new_title) > 150:
        new_title = title[:140] + " | Comprar"

    return new_title


def process_csv(input_path):
    output_path = input_path.replace(".csv", "_seo_titles.csv")
    if output_path == input_path:
        output_path = input_path.replace(".csv", "") + "_seo_titles.csv"

    modified = 0
    total = 0

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        rows = []
        for row in reader:
            total += 1

            # Solo modificar la primera fila de cada producto (Handle unico)
            # En el CSV de Shopify, las variantes comparten Handle
            original_title = row.get("Title", "")

            if original_title:  # Solo filas con titulo (primera variante)
                new_title = optimize_title(row, fieldnames)

                # Tambien generar SEO Title si existe el campo
                if "SEO Title" in fieldnames:
                    if not row.get("SEO Title"):
                        row["SEO Title"] = new_title[:70]  # Google trunca a ~60-70 chars

                if new_title != original_title:
                    row["Title"] = new_title
                    modified += 1

            rows.append(row)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nOptimizacion de titulos completada.")
    print(f"Total filas: {total}")
    print(f"Titulos modificados: {modified}")
    print(f"Resultado guardado en: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 optimize_product_titles.py <ruta_al_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"ERROR: No se encuentra '{input_file}'")
        sys.exit(1)

    process_csv(input_file)
