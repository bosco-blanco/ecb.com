# Credenciales pendientes

**Estado:** 11 de 12 bloques ejecutados con el token Admin API generado desde client_credentials (`shpat_a33d…`). Solo el Bloque 10 quedó bloqueado.

## Bloque 10 — Necesita Search Console API (no es Shopify)

Para analizar las 7.654 URLs "rastreadas sin indexar" + 46 soft 404 necesito:

- Un **Service Account JSON** de Google Cloud con scope:
  - `https://www.googleapis.com/auth/webmasters.readonly`
- El Service Account debe estar **verificado como "User"** en la propiedad `https://www.encopadebalon.com/` en Search Console (Settings → Users and permissions → Add user).

Cómo generarlo:
1. Google Cloud Console → IAM & Admin → Service accounts → Create
2. Otorgar rol: ninguno a nivel proyecto (no hace falta)
3. Manage keys → Add key → JSON → download
4. Search Console → settings → users → invitar al email del service account con permiso "Restricted" o "Full"

Cuando lo tengas, pásalo como ruta a un archivo local (no me lo pegues completo aquí porque es JSON multilínea). Algo como:

```
~/.auto-memory/secrets/gsc-service-account.json
```

Sin esto, no puedo consultar GSC API para listar las URLs por cubo. El análisis quedaría manual desde el dashboard de GSC en navegador.
