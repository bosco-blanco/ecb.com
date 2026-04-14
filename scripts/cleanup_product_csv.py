#!/usr/bin/env python3
"""
Limpieza masiva de metadatos de producto para ECDB.
Procesa el CSV de exportacion de Shopify y corrige:
1. Erratas de paises ("Hugria" -> "Hungria", "EE.UU" -> "Estados Unidos")
2. Estandariza variedades de uva (elimina blends largos como valor de filtro)
3. Convierte grados alcoholicos decimales a rangos legibles
4. Limpia "Default Title" de variantes
5. Rellena Vendor con nombre real de bodega cuando es "En Copa de Balon"

USO:
  1. Exportar CSV desde Shopify Admin > Products > Export
  2. python3 cleanup_product_csv.py products_export.csv
  3. El resultado se guarda en products_cleaned.csv
  4. Importar products_cleaned.csv en Shopify Admin > Products > Import

NOTA: Hacer backup del CSV original antes de reimportar.
"""

import csv
import sys
import re
from pathlib import Path

# --- CORRECCIONES DE PAISES ---
COUNTRY_FIXES = {
    "Hugría": "Hungría",
    "Hugria": "Hungría",
    "EE.UU": "Estados Unidos",
    "EEUU": "Estados Unidos",
    "EE. UU.": "Estados Unidos",
    "USA": "Estados Unidos",
    "Pago": "",  # "Pago" no es un pais, es una clasificacion vinicola
    "pago": "",
}

# --- ESTANDARIZACION DE UVAS ---
# Si el valor de uva contiene %, es un blend descriptivo -> extraer uva principal
def clean_grape_variety(value):
    if not value:
        return value

    # Si contiene porcentajes, es un blend -> extraer uvas individuales
    if "%" in value:
        # Extraer nombres de uva (palabras capitalizadas despues del %)
        grapes = re.findall(r'\d+%\s*([A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)?)', value)
        if grapes:
            # Devolver la uva principal (mayor porcentaje, que es la primera)
            return grapes[0].strip()

    # Limpiar espacios extra
    return value.strip()


# --- CONVERSION DE GRADOS ALCOHOLICOS ---
def alcohol_to_range(value):
    """Convierte valores decimales como '0.14' o '14.5' a rangos legibles."""
    if not value:
        return value

    try:
        val = float(value.replace(",", "."))

        # Si es < 1, probablemente esta en formato 0.XX (0.14 = 14%)
        if val < 1:
            val = val * 100

        if val < 10:
            return "Bajo (<10%)"
        elif val < 12:
            return "Ligero (10-12%)"
        elif val < 14:
            return "Medio (12-14%)"
        elif val < 15:
            return "Con cuerpo (14-15%)"
        else:
            return "Alto (>15%)"
    except (ValueError, TypeError):
        return value


# --- LIMPIEZA DE VARIANT TITLE ---
def clean_variant_title(value):
    if not value or value.strip().lower() == "default title":
        return ""
    return value


def process_csv(input_path):
    output_path = input_path.replace(".csv", "_cleaned.csv")
    if output_path == input_path:
        output_path = input_path.replace(".csv", "") + "_cleaned.csv"

    stats = {
        "total_rows": 0,
        "countries_fixed": 0,
        "grapes_cleaned": 0,
        "alcohol_converted": 0,
        "default_titles_fixed": 0,
        "vendor_flagged": 0,
    }

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames:
            print("ERROR: El CSV no tiene cabeceras. Verifica el formato.")
            sys.exit(1)

        rows = []
        for row in reader:
            stats["total_rows"] += 1

            # 1. Corregir paises
            for col in fieldnames:
                if "country" in col.lower() or "pais" in col.lower() or "origen" in col.lower():
                    original = row[col]
                    if original in COUNTRY_FIXES:
                        row[col] = COUNTRY_FIXES[original]
                        stats["countries_fixed"] += 1

            # 2. Limpiar variedades de uva
            for col in fieldnames:
                if "uva" in col.lower() or "grape" in col.lower() or "variedad" in col.lower():
                    original = row[col]
                    cleaned = clean_grape_variety(original)
                    if cleaned != original:
                        row[col] = cleaned
                        stats["grapes_cleaned"] += 1

            # 3. Convertir grados alcoholicos
            for col in fieldnames:
                if "alcohol" in col.lower() or "grado" in col.lower():
                    original = row[col]
                    converted = alcohol_to_range(original)
                    if converted != original:
                        row[col] = converted
                        stats["alcohol_converted"] += 1

            # 4. Limpiar "Default Title"
            for col in fieldnames:
                if "variant" in col.lower() and "title" in col.lower():
                    original = row[col]
                    cleaned = clean_variant_title(original)
                    if cleaned != original:
                        row[col] = cleaned
                        stats["default_titles_fixed"] += 1

            # 5. Flaggear vendor = "En Copa de Balon"
            for col in fieldnames:
                if col.lower() == "vendor":
                    if row[col] and "copa de bal" in row[col].lower():
                        stats["vendor_flagged"] += 1
                        # No cambiamos automaticamente - marcamos para revision manual
                        # porque necesitamos saber el nombre real de cada bodega

            rows.append(row)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"LIMPIEZA DE CSV COMPLETADA")
    print(f"{'='*60}")
    print(f"Archivo de entrada:  {input_path}")
    print(f"Archivo de salida:   {output_path}")
    print(f"{'='*60}")
    print(f"Total de filas:              {stats['total_rows']}")
    print(f"Paises corregidos:           {stats['countries_fixed']}")
    print(f"Uvas limpiadas:              {stats['grapes_cleaned']}")
    print(f"Grados alcohol convertidos:  {stats['alcohol_converted']}")
    print(f"'Default Title' eliminados:  {stats['default_titles_fixed']}")
    print(f"Vendor='ECDB' (revisar):     {stats['vendor_flagged']}")
    print(f"{'='*60}")

    if stats["vendor_flagged"] > 0:
        print(f"\n⚠  ATENCION: {stats['vendor_flagged']} productos tienen 'En Copa de Balon'")
        print(f"   como Vendor en lugar del nombre real de la bodega.")
        print(f"   Estos NO se han cambiado automaticamente.")
        print(f"   Revisa el CSV y actualiza manualmente los nombres de bodega.")

    print(f"\nSiguiente paso: Importar '{output_path}' en Shopify Admin > Products > Import")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 cleanup_product_csv.py <ruta_al_csv>")
        print("Ejemplo: python3 cleanup_product_csv.py products_export.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"ERROR: No se encuentra el archivo '{input_file}'")
        sys.exit(1)

    process_csv(input_file)
