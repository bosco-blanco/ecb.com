#!/usr/bin/env python3
"""
Genera un CSV de redirecciones 301 de URLs legacy de PrestaShop
a las URLs equivalentes en Shopify.

Mapea patrones conocidos de PrestaShop a la estructura de Shopify:
- /module/... -> eliminadas (no hay equivalente)
- /content/... -> /pages/...
- /es/XX-nombre -> /collections/nombre o /products/nombre
- /en/XX-nombre -> /en/collections/nombre

USO:
  1. Obtener la lista de URLs 404 desde Google Search Console
     (Paginas > No encontrada > Exportar)
  2. Guardar como CSV con columna "URL" o "Page"
  3. python3 map_prestashop_redirects.py urls_404.csv
  4. Resultado: shopify_redirects.csv
  5. Importar en Shopify Admin > Online Store > Navigation > URL Redirects

ALTERNATIVA sin Google Search Console:
  Puedes crear el CSV manualmente listando las URLs antiguas conocidas.
  El script genera las mejores aproximaciones de redireccion.
"""

import csv
import sys
import re
from pathlib import Path


def map_url(old_url):
    """Mapea una URL legacy de PrestaShop a su equivalente en Shopify."""

    # Limpiar la URL
    url = old_url.strip()
    if not url.startswith("/"):
        # Extraer path de URL completa
        from urllib.parse import urlparse
        parsed = urlparse(url)
        url = parsed.path

    # Eliminar trailing slash
    url = url.rstrip("/")

    if not url:
        return None, "URL vacia"

    # Patron: /module/... -> no hay equivalente directo
    if "/module/" in url:
        return "/", "Modulo PrestaShop sin equivalente -> Home"

    # Patron: /content/XX-nombre -> /pages/nombre
    match = re.match(r'^/(?:es|en)/content/\d+-(.+)$', url)
    if match:
        slug = match.group(1).lower().replace("_", "-")
        return f"/pages/{slug}", "Pagina de contenido"

    # Patron: /es/XX-nombre-categoria -> /collections/nombre
    match = re.match(r'^/(?:es|en)/(\d+)-(.+)$', url)
    if match:
        slug = match.group(2).lower().replace("_", "-")
        # Intentar determinar si es producto o coleccion
        # Los IDs bajos suelen ser categorias, los altos productos
        item_id = int(match.group(1))
        if item_id < 50:
            return f"/collections/{slug}", "Coleccion (estimada)"
        else:
            return f"/products/{slug}", "Producto (estimado)"

    # Patron: /XX-nombre (sin /es/ prefix)
    match = re.match(r'^/(\d+)-(.+)$', url)
    if match:
        slug = match.group(2).lower().replace("_", "-")
        return f"/products/{slug}", "Producto (sin locale)"

    # Patron: /es/... o /en/... generico
    match = re.match(r'^/(es|en)/(.+)$', url)
    if match:
        rest = match.group(2).lower().replace("_", "-")
        return f"/collections/{rest}", "Redireccion generica"

    # Patron: archivos estaticos de PrestaShop
    if url.endswith((".js", ".css", ".map")):
        return None, "Archivo estatico - ignorar"

    # Patron: URLs de login/cuenta de PrestaShop
    if "my-account" in url or "login" in url or "password" in url:
        return "/account/login", "Pagina de cuenta"

    # Patron: URLs de carrito
    if "cart" in url or "order" in url:
        return "/cart", "Carrito"

    # Default: redirigir a home
    return "/", "Sin mapeo claro -> Home"


def process_csv(input_path):
    output_path = "shopify_redirects.csv"

    mapped = 0
    skipped = 0
    total = 0

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        # Buscar la columna con las URLs
        url_column = None
        for col in reader.fieldnames:
            if col.lower() in ("url", "page", "page url", "path", "redirect from"):
                url_column = col
                break

        if not url_column:
            # Intentar con la primera columna
            url_column = reader.fieldnames[0]
            print(f"AVISO: No se encontro columna 'URL'. Usando '{url_column}'.")

        redirects = []
        for row in reader:
            total += 1
            old_url = row[url_column]

            new_url, reason = map_url(old_url)

            if new_url:
                redirects.append({
                    "Redirect from": old_url.rstrip("/"),
                    "Redirect to": new_url,
                    "Reason": reason,
                })
                mapped += 1
            else:
                skipped += 1

    # Escribir CSV en formato Shopify (Redirect from, Redirect to)
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Redirect from", "Redirect to"])
        writer.writeheader()
        for r in redirects:
            writer.writerow({"Redirect from": r["Redirect from"], "Redirect to": r["Redirect to"]})

    # Tambien escribir version detallada para revision
    detail_path = output_path.replace(".csv", "_detailed.csv")
    with open(detail_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Redirect from", "Redirect to", "Reason"])
        writer.writeheader()
        writer.writerows(redirects)

    print(f"\nMapeo de redirecciones completado.")
    print(f"Total URLs procesadas: {total}")
    print(f"Redirecciones generadas: {mapped}")
    print(f"URLs ignoradas: {skipped}")
    print(f"\nArchivos generados:")
    print(f"  Para Shopify:    {output_path}")
    print(f"  Para revision:   {detail_path}")
    print(f"\nIMPORTANTE: Revisa {detail_path} antes de importar.")
    print(f"Algunas redirecciones son estimaciones y pueden necesitar ajuste manual.")
    print(f"\nPara importar: Shopify Admin > Online Store > Navigation > URL Redirects > Import")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 map_prestashop_redirects.py <urls_404.csv>")
        print("\nEl CSV debe tener una columna 'URL' o 'Page' con las URLs antiguas.")
        print("Puedes obtenerlo de Google Search Console > Paginas > No encontrada > Exportar")
        sys.exit(1)

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"ERROR: No se encuentra '{input_file}'")
        sys.exit(1)

    process_csv(input_file)
