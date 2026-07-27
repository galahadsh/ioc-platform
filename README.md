# IOC Platform

Plataforma de Ciberinteligencia para la gestión, enriquecimiento y análisis de Indicadores de Compromiso (IOC).

El proyecto está diseñado para evolucionar hacia una plataforma centralizada para equipos de:

- Ciberinteligencia
- Threat Hunting
- Respuesta a Incidentes
- Threat Intelligence

---

# Estado del proyecto

Versión actual

```
v0.3.0-alpha
```

Estado

- ✅ Backend modular
- ✅ PostgreSQL
- ✅ Collector VirusTotal
- ✅ Dashboard inicial
- ✅ API REST
- ✅ Docker
- ✅ Nginx
- 🚧 IOC Explorer
- ⏳ Threat Intelligence
- ⏳ Threat Hunting
- ⏳ Reportes

---

# Arquitectura

```
                    IOC Platform

        +------------------------------+
        |         Frontend             |
        +--------------+---------------+
                       |
                       v
                FastAPI REST API
                       |
      +----------------+----------------+
      |                                 |
      v                                 v
   Services                      Collector
      |                                 |
      v                                 v
Repositories                  VirusTotal API
      |
      v
 PostgreSQL
```

---

# Estructura del proyecto

```
ioc-platform/

├── api/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── static/
│   ├── uploads/
│   └── main.py
│
├── collector/
│   ├── clients/
│   ├── repositories/
│   ├── services/
│   └── main.py
│
├── database/
│   ├── init.sql
│   └── migrations/
│
├── scheduler/
│
├── nginx/
│
├── uploads/
│
├── docker-compose.yml
│
└── README.md
```

---

# Componentes

## API

FastAPI

Funciones

- Carga de IOC
- Dashboard
- Historial
- Estadísticas
- Health Check

---

## Collector

Enriquece automáticamente los IOC utilizando VirusTotal.

Actualmente obtiene:

- Malicious
- Suspicious
- Harmless
- Undetected
- HTTP Status
- Errores
- Reintentos

---

## Base de datos

PostgreSQL 16

Tabla principal

```
iocs
```

Optimizada con índices para:

- Tipo
- Estado
- Fecha
- Score
- Última consulta

---

# Docker

Servicios

| Servicio | Puerto |
|----------|--------|
| API | 8000 |
| Nginx | 80 |
| PostgreSQL | 5432 |
| Adminer | 8080 |
| Collector | Interno |
| Scheduler | Interno |

---

# Variables de entorno

Ejemplo

```
POSTGRES_DB=cyberintel
POSTGRES_USER=cyberintel
POSTGRES_PASSWORD=********

VT_API_KEY=xxxxxxxxxxxxxxxx
```

Nunca subir el archivo `.env` al repositorio.

---

# Ejecutar

Levantar todos los servicios

```bash
docker compose up -d
```

API

```
http://localhost:8000
```

Adminer

```
http://localhost:8080
```

---

# API

## Dashboard

```
GET /api/stats
```

---

## Health

```
GET /api/health
```

---

## IOC

```
POST /api/upload
```

---

# Migraciones

Las migraciones se encuentran en:

```
database/migrations/
```

Ejemplo

```
002_vt_error_tracking.sql

003_ioc_indexes.sql
```

---

# Roadmap

## v0.3

- Dashboard Profesional
- IOC Explorer

---

## v0.4

- IOC Collections

---

## v0.5

- Threat Intelligence

---

## v0.6

- Threat Hunting

---

## v0.7

- Integración con TheHive

---

## v0.8

- Reportes Ejecutivos

---

## v1.0

Plataforma completa de Ciberinteligencia

- IOC Explorer
- Threat Intelligence
- Threat Hunting
- Integración TheHive
- Reportes
- Dashboard Ejecutivo
- Automatización

---

# Tecnologías

- FastAPI
- PostgreSQL
- Docker
- Nginx
- VirusTotal API
- Python
- JavaScript
- HTML
- CSS

---

# Licencia

Proyecto interno de investigación y desarrollo.