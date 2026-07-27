# IOC Platform

> Plataforma de **Cyber Threat Intelligence (CTI)** para la gestión, enriquecimiento, análisis y exportación de Indicadores de Compromiso (IOC).

---

# Descripción

IOC Platform es una plataforma desarrollada para centralizar el ciclo de vida de los IOC utilizados por equipos de:

* Cyber Threat Intelligence (CTI)
* Threat Hunting
* Incident Response (IR)
* Security Operations Center (SOC)

El objetivo es evolucionar hacia una plataforma propia que permita consumir múltiples fuentes de inteligencia, enriquecer indicadores automáticamente, generar métricas y exportar IOC a herramientas de seguridad.

---

# Estado del Proyecto

**Versión**

```
v0.2.0-alpha
```

Estado:

* En desarrollo activo

---

# Arquitectura

La aplicación sigue una arquitectura por capas para separar responsabilidades.

```
Cliente
    │
    ▼
Routes (FastAPI)
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
PostgreSQL
```

## ¿Qué hace cada capa?

### Routes

* Reciben las solicitudes HTTP.
* Validan parámetros.
* Devuelven respuestas.

**No contienen SQL.**

---

### Services

Contienen la lógica de negocio.

Ejemplos:

* cálculo de estadísticas
* validaciones
* enriquecimiento
* transformación de respuestas

---

### Repositories

Acceso a PostgreSQL.

Toda consulta SQL debe vivir aquí.

---

# Estructura del Proyecto

```
ioc-platform/
│
├── api/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   │
│   ├── models/
│   ├── repositories/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   └── utils/
│
├── collector/
├── dashboard/
├── database/
├── exports/
├── logs/
├── nginx/
├── scheduler/
├── uploads/
│
├── docker-compose.yml
├── CHANGELOG.md
└── README.md
```

---

# Tecnologías

* Python 3.12
* FastAPI
* SQLAlchemy
* PostgreSQL 16
* Docker Compose
* Uvicorn
* Nginx
* Pandas
* OpenPyXL

---

# Funcionalidades Implementadas

## Gestión de IOC

* Importación de CSV
* Detección automática de tipo IOC
* Normalización de indicadores

Tipos soportados:

* IPv4
* URL
* Dominio
* MD5
* SHA1
* SHA256

---

## Dashboard

Actualmente permite visualizar:

* Total de IOC
* IOC maliciosos
* IOC limpios
* IOC pendientes de análisis

---

## Historial

Registro de cargas realizadas.

---

## Enriquecimiento

Actualmente:

* VirusTotal

En desarrollo:

* GreyNoise
* AbuseIPDB
* ThreatFox
* URLHaus
* AlienVault OTX
* Intel471

---

# API REST

## Health

```
GET /health
```

---

## Estadísticas

```
GET /api/stats
```

---

## Historial

```
GET /api/analysis/history
```

---

## IOC maliciosos

```
GET /api/iocs/malicious
```

---

## Carga de IOC

```
POST /api/upload
```

---

# Base de Datos

Motor:

```
PostgreSQL 16
```

Acceso mediante:

* SQLAlchemy

Actualmente se almacenan:

* IOC
* Tipo
* Estado
* Resultado VirusTotal
* Fechas de análisis

---

# Arquitectura de Desarrollo

El proyecto sigue las siguientes reglas:

## 1. Routes

Nunca deben contener:

* SQL
* conexiones a PostgreSQL
* lógica de negocio

---

## 2. Services

Contienen:

* reglas de negocio
* validaciones
* procesamiento
* transformación de respuestas

---

## 3. Repositories

Contienen únicamente:

* consultas SQL
* inserciones
* actualizaciones
* eliminaciones

---

# Roadmap

## Fase 1 — Base

* [x] Docker Compose
* [x] PostgreSQL
* [x] FastAPI
* [x] Dashboard inicial
* [x] Importación CSV
* [x] Enriquecimiento VirusTotal

---

## Fase 2 — Refactor

* [x] Separación de rutas
* [x] Configuración centralizada
* [x] Base de datos centralizada
* [x] Directorio utils
* [x] Directorio services
* [x] Directorio repositories
* [x] Directorio models
* [x] Directorio schemas
* [x] Migración de `/api/stats` a arquitectura por capas

Pendiente:

* [ ] Migrar `/api/upload`
* [ ] Migrar `/api/analysis/history`
* [ ] Migrar `/api/iocs/malicious`

---

## Fase 3 — Backend Profesional

* [ ] SQLAlchemy ORM
* [ ] Alembic
* [ ] Pydantic Schemas
* [ ] Repository Pattern completo
* [ ] Service Layer completa
* [ ] Logging estructurado
* [ ] Manejo centralizado de errores
* [ ] Variables mediante `.env`
* [ ] Autenticación JWT
* [ ] Control de usuarios
* [ ] Tests unitarios

---

## Fase 4 — Threat Intelligence

Integración con:

* [ ] VirusTotal
* [ ] GreyNoise
* [ ] AbuseIPDB
* [ ] ThreatFox
* [ ] URLHaus
* [ ] AlienVault OTX
* [ ] Intel471

---

## Fase 5 — Dashboard

Visualizaciones:

* [ ] IOC por país
* [ ] IOC por ASN
* [ ] IOC por malware
* [ ] IOC por actor
* [ ] IOC por campaña
* [ ] IOC por familia
* [ ] IOC por severidad
* [ ] IOC por técnica MITRE
* [ ] IOC por fuente
* [ ] Tendencias
* [ ] Evolución temporal

---

## Fase 6 — Exportadores

Exportación automática hacia:

* [ ] FortiGate
* [ ] Palo Alto
* [ ] Microsoft Defender
* [ ] Splunk
* [ ] Elastic
* [ ] TheHive
* [ ] MISP
* [ ] STIX/TAXII

---

## Fase 7 — Automatización

* [ ] Scheduler
* [ ] Reanálisis automático
* [ ] Depuración automática
* [ ] Enriquecimiento periódico
* [ ] Alertas
* [ ] Integración con correo
* [ ] Integración con Teams
* [ ] Integración con Slack

---

# Principios del Proyecto

* Arquitectura modular.
* Separación de responsabilidades.
* Código reutilizable.
* Escalable.
* Fácil de probar.
* Preparado para múltiples desarrolladores.

---

# Convenciones

## Código

* Un archivo = una responsabilidad.
* Sin lógica de negocio en las rutas.
* Sin SQL en las rutas.
* Sin duplicar código.

---

## Documentación

Todo cambio importante debe actualizar:

* `README.md`
* `CHANGELOG.md`

antes de considerarse finalizado.

---

# Objetivo Final

Construir una plataforma integral de Cyber Threat Intelligence capaz de:

* Centralizar IOC de múltiples fuentes.
* Enriquecer indicadores automáticamente.
* Relacionar IOC con malware, campañas y actores de amenaza.
* Generar métricas y dashboards ejecutivos.
* Integrarse con plataformas SIEM, SOAR y EDR.
* Exportar IOC hacia firewalls, EDR, SIEM y herramientas de respuesta a incidentes.
* Servir como plataforma de apoyo para los equipos de Ciberinteligencia, Threat Hunting e Incident Response.
