<<<<<<< HEAD
=======
# IOC Platform

Plataforma de Cyber Threat Intelligence (CTI) para la gestión, análisis y enriquecimiento de Indicadores de Compromiso (IOCs).

## Características

- Carga masiva de IOCs desde CSV
- Enriquecimiento con VirusTotal
- Dashboard web
- Historial de análisis
- API REST con FastAPI
- Base de datos PostgreSQL
- Docker Compose
- Exportación de IOCs
- Arquitectura modular

---

## Arquitectura

```
Usuario
    │
    ▼
FastAPI
    │
    ▼
PostgreSQL
    ▲
    │
Collector
    │
VirusTotal
```

---

## Tecnologías

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker
- Nginx
- JavaScript
- HTML
- CSS

---

## Estado

Versión:

```
v1.0.0-alpha
```

---

## Roadmap

- [ ] Dashboard avanzado
- [ ] MISP
- [ ] OTX
- [ ] AbuseIPDB
- [ ] GreyNoise
- [ ] ThreatFox
- [ ] URLHaus
- [ ] Reportes PDF
- [ ] Exportadores Fortigate
- [ ] Exportadores Sentinel
- [ ] API pública

---

Autor

MAVERICK
>>>>>>> 5aa44b0 (Initial version v1.0.0-alpha)
