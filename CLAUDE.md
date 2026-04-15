# ECDB - En Copa de Balon - Mejora Web

## Contexto
Tienda Shopify de vinos (eb9117-4.myshopify.com / encopadebalon.com). 1.521+ productos, 6 tiendas fisicas en Madrid, restaurantes. Tema Viola v1.0.8. Migracion desde PrestaShop.

## Conexion Shopify
```bash
shopify store auth --store eb9117-4.myshopify.com --scopes read_themes,write_themes,read_products,write_products,read_content,write_content,read_locales,write_locales,read_inventory
shopify theme push --store eb9117-4.myshopify.com  # subir cambios al tema live
shopify store execute --store eb9117-4.myshopify.com --query 'GRAPHQL' # ejecutar queries
```

## Metafields reales de productos (VERIFICADOS)
- `custom.a_ada` - Anada/vintage (number_integer)
- `custom.denominaci_n_de_origen` - D.O. (single_line_text_field)
- `custom.bodega` - Bodega (single_line_text_field)
- `custom.bodega_link` - Link a metaobject de bodega (metaobject_reference)
- `custom.tipo_de_uva` - Variedad de uva (single_line_text_field)
- `custom.tipo_de_vino` - Tipo: Tinto, Blanco, Rosado (single_line_text_field)
- `custom.pa_s_de_origen` - Pais (single_line_text_field)
- `custom.grado_alcoh_lico` - Grado como decimal: 0.14 = 14% (number_decimal)
- `custom.estilo` - Ej: "Maduros y elegantes" (single_line_text_field)
- `custom.envejecimiento` - Crianza (single_line_text_field)
- `custom.puntos_robert_parker` - Puntuacion Parker (number_integer)
- `custom.puntos_guia_pe_in` - Puntuacion Penin (single_line_text_field)
- `custom.formato` - Volumen (volume)
- `prestify.features` - JSON legacy de PrestaShop con todos los datos
- `reviews.rating` - Rating de Judge.me (ya instalado)
- `reviews.rating_count` - Conteo de resenas

## Problemas criticos pendientes

### 1. Vendor incorrecto (URGENTE)
1.691 productos tienen vendor "En Copa de Balon" en vez de la bodega real. El dato correcto esta en `custom.bodega`. Hay que iterar todos los productos y hacer `productUpdate` para copiar el valor de `custom.bodega` al campo `vendor`.

### 2. Product cards sin info de vino
Las cards en colecciones solo muestran titulo y precio. Hay que modificar `snippets/card-product.liquid` para mostrar: anada, D.O., score mas alto, tipo de vino (con color).

### 3. Sticky Add to Cart
Cuando el usuario hace scroll en la pagina de producto, pierde el boton de comprar. Crear un sticky bar que aparezca al scrollear.

### 4. Perfil de sabor visual (estilo Vivino)
Barras visuales para: Cuerpo, Tanino, Acidez, Dulzor. Requiere crear metafields nuevos.

### 5. Maridaje con iconos
Iconos de comida: carne, pescado, queso, pasta, marisco. Metafield `custom.maridaje` por crear.

## Archivos clave del tema
- `layout/theme.liquid` - Layout principal (ya tiene hreflang, visual-polish)
- `sections/main-product.liquid` - Pagina de producto (ya tiene wine-product-info, trust-badges, stock-urgency)
- `sections/wbquickview.liquid` - Vista rapida (ya tiene wine-product-info)
- `snippets/card-product.liquid` - Tarjeta de producto en grid
- `snippets/wine-product-info.liquid` - Ficha rica del vino (Parker, Penin, D.O., bodega, uva, grado, estilo, notas de cata)
- `snippets/trust-badges.liquid` - Badges de confianza
- `snippets/stock-urgency.liquid` - Indicador "Ultimas X unidades"
- `snippets/visual-polish.liquid` - CSS global (contraste, tipografia, cards, mobile)
- `snippets/mobile-ux-enhancements.liquid` - Mejoras mobile (bottom nav, scroll-to-top)
- `snippets/price.liquid` - Precios (fix de badges de descuento aplicado)
- `snippets/schema-stores.liquid` - Schema LocalBusiness tiendas fisicas
- `config/settings_data.json` - Colores: cream #f0ede1, olive #9fa185, gold #d4b974, green #3d5a3c, wine #6b1d3a
- `scripts/` - Scripts Python auxiliares para limpieza CSV, meta descriptions, redirects

## Competencia benchmark (de la auditoria)
- Lavinia: 6.500 refs, 9.100+ resenas Trustpilot, Club 3 niveles
- Coalla Gourmet: cestas tematicas, Escolinas (marca propia)
- Dona Tomasa: builder de cestas, 1.618 resenas Trusted Shops
- Santa Cecilia: 5.000+ refs, 25.000 miembros club, cursos y enoturismo

## Principios (AutoReason)
- "No hacer nada" es siempre una opcion valida
- Separar diagnostico de prescripcion
- Cada cambio compite contra el status quo
- Validar con `shopify theme check` o MCP `validate_theme` antes de pushear
