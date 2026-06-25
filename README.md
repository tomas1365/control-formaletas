# 🏗️ Control Formaletas — UNISPAN Colombia

Sistema de auditoría y trazabilidad de piezas metálicas mediante visión artificial (YOLOv8 + Roboflow).

## Arquitectura

```
control-formaletas/
├── frontend/        React 18 + Vite + TailwindCSS
├── backend/         Flask + YOLOv8 + Roboflow SDK
├── docker-compose.yml
└── .github/workflows/
```

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Recharts |
| Backend | Flask 3, YOLOv8 (ultralytics), Roboflow SDK |
| Modelo | `reconocimiento-de-piezas` (Roboflow, Object Detection) |
| Deploy | Render (backend) + Vercel (frontend) |
| CI/CD | GitHub Actions |

## Variables de entorno

```env
# backend/.env
ROBOFLOW_API_KEY=your_key_here
ROBOFLOW_PROJECT=reconocimiento-de-piezas
ROBOFLOW_VERSION=1

# frontend/.env
VITE_API_URL=http://localhost:5000
```

## Inicio rápido

```bash
# Con Docker
docker compose up --build

# Sin Docker
cd backend && pip install -r requirements.txt && flask run
cd frontend && npm install && npm run dev
```

## Módulos

1. **Escaneo IA** — Captura imagen → YOLOv8 → identificación de pieza
2. **Catálogo** — PM, PMA, EI con specs completas
3. **Historial** — Auditorías por operador, fecha, estado
4. **Indicadores** — Dashboard KPIs + exportación Power BI
5. **Operadores** — Gestión y asignación de técnicos
