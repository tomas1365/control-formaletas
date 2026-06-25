# Guía de despliegue — Control Formaletas UNISPAN

## 1. Crear el repositorio en GitHub

```bash
git init
git remote add origin https://github.com/tomas1365/control-formaletas.git
git add .
git commit -m "feat: initial commit — unispan auditoria ia"
git push -u origin main
```

## 2. Secrets de GitHub Actions

En `Settings → Secrets → Actions`:

| Secret | Valor |
|--------|-------|
| `ROBOFLOW_API_KEY` | Tu API key de Roboflow |
| `RENDER_DEPLOY_HOOK` | URL del deploy hook de Render (ver paso 4) |

## 3. Despliegue backend en Render

1. Ir a [render.com](https://render.com) → New Web Service
2. Conectar repo `tomas1365/control-formaletas`
3. **Root directory:** `backend`
4. **Build command:** `pip install -r requirements.txt`
5. **Start command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 "app:create_app()"`
6. Agregar variables de entorno:
   - `ROBOFLOW_API_KEY` = tu key
   - `ROBOFLOW_PROJECT` = `reconocimiento-de-piezas`
   - `ROBOFLOW_VERSION` = `1`
7. Copiar el **Deploy Hook URL** → guardarlo en GitHub Secrets como `RENDER_DEPLOY_HOOK`

## 4. Despliegue frontend en Vercel

```bash
cd frontend
npx vercel --prod
```

Configurar variable de entorno en Vercel:
```
VITE_API_URL=https://unispan-backend.onrender.com
```

## 5. Verificar

```bash
curl https://unispan-backend.onrender.com/api/health
# → {"status": "ok", "service": "unispan-backend"}

curl https://unispan-backend.onrender.com/api/catalog/
# → lista de piezas PM, PMA, EI
```

## 6. Actualizar alias de clases Roboflow

Editar `backend/app/utils/piece_mapper.py` → `CLASS_ALIAS`
para mapear los nombres exactos de las clases entrenadas en Roboflow:

```python
CLASS_ALIAS = {
    "nombre_en_roboflow": "PM-120",   # ajustar según tu proyecto
    ...
}
```

Verificar nombres en: Roboflow → proyecto → Dataset → clases.
