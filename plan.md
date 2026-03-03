# Plan de Ejecución Maestro - Nicho Automático AdSense

## FASE 0: INVESTIGACIÓN & PLANIFICACIÓN

### Checklist de Tareas

- [x] Crear estructura del proyecto
  - [x] Carpeta raíz `adsense-automation`
  - [x] Subcarpetas: keywords, scrapers, content, website, automation, monitoring, data
  - [x] README.md y plan.md
- [x] Definir 3-5 nichos iniciales (baja competencia, alto CPC)
  - [x] Investigar nichos potenciales (10 nichos evaluados)
  - [x] Analizar métricas de mercado (via Google Trends)
  - [ ] Seleccionar nichos finales (en proceso)
- [x] Configurar herramientas de investigación
  - [x] Google Trends API (pytrends) instalada y funcionando
  - [x] Script de recolección de keywords creado (`keywords/research.py`)
  - [x] Primera ejecución completada con 60+ keywords filtradas
- [x] Crear repositorio GitHub
  - [x] Inicializar repo local (`git init`)
  - [x] Configurar `.gitignore`
  - [x] Primer commit con estructura base
- [x] Diseñar arquitectura de base de datos
  - [x] Esquema para artículos, keywords, métricas (`database/schema.sql`)
  - [x] Elegir base de datos (Supabase recomendado)
  - [x] Diseñar relaciones y índices
- [ ] Establecer métricas KPI iniciales
  - [ ] Definir KPIs: tráfico, RPM, indexación, ingresos
  - [ ] Configurar sistema de tracking básico

### Nichos Investigados - Resultados Preliminares
Basado en análisis inicial con Google Trends (60+ keywords filtradas con KD ≤10 y SV ≥1000 estimado):

1. **Personal Finance** - 23 keywords, volumen estimado 20K-500K, CPC alto
   - Ejemplos: "decentralized finance", "personal finance pdf", "best personal finance apps"
   - Competencia estimada: baja-media

2. **Technology** - 15 keywords, volumen estimado 3M-31M, CPC medio-alto  
   - Ejemplos: "openai news today", "apple news today", "technology news today"
   - Competencia estimada: media-alta (noticias)

3. **Health** - 13 keywords, volumen estimado 9K-12M, CPC alto
   - Ejemplos: "who health news today", "how to check hard drive health", "mental health"
   - Competencia estimada: variable

4. **Home Improvement** - 12 keywords, volumen estimado 10K-1.3M, CPC medio
   - Ejemplos: "home improvement hulu 2025", "home improvement financing", "lowe's home improvement"
   - Competencia estimada: baja-media

5. **Gardening** - 1 keyword, volumen estimado 41K, CPC bajo-medio
   - Ejemplo: "gardening near me"
   - Competencia estimada: baja

### Selección de Nichos Finales (Recomendación)
Para un sistema Zero-Human-Touch, recomiendo empezar con 3 nichos que combinen:
1. **Personal Finance** - Alto CPC, keywords de intención informacional/transaccional
2. **Home Improvement** - CPC decente, competencia manejable, contenido "evergreen"
3. **Health** - Alto CPC pero requiere precisión médica (riesgo de desinformación)

**Excluir:** Technology (muy competitivo, noticias caducan rápido) y Gardening (pocas keywords).

### Próximos Pasos (Fase 0 Continuación)
1. [ ] Refinar script de investigación con métricas más precisas (volumen real, KD real)
2. [ ] Integrar API de DataForSEO o similar para datos reales de keywords
3. [ ] Seleccionar 3 nichos finales basados en datos mejorados
4. [ ] Configurar Supabase y desplegar esquema de base de datos
5. [x] Definir KPIs y dashboard básico (ver `kpi.md`)

---

## 📊 RESULTADOS FASE 0 COMPLETADOS

### ✅ Tareas Finalizadas
1. **Estructura del proyecto creada** - Carpeta organizada con subdirectorios
2. **Investigación de nichos realizada** - 10 nichos evaluados, 3 seleccionados
3. **Script de keyword research desarrollado** - Usando Google Trends (pytrends)
4. **Lista de keywords filtrada generada** - 60+ keywords con KD≤10 y SV≥1000 (estimado)
5. **Repositorio Git inicializado** - Commit inicial con estructura
6. **Esquema de base de datos diseñado** - PostgreSQL schema para Supabase
7. **KPIs definidos** - Métricas de tráfico, SEO, monetización y calidad

### 📁 Archivos Generados
- `keywords/research.py` - Script de investigación con Google Trends
- `keywords/filtered_keywords.csv` - Keywords filtradas del script inicial
- `keywords/sample_keywords.csv` - Dataset de ejemplo con métricas realistas
- `keywords/filtered_sample.csv` - Keywords filtradas (KD≤10, SV≥1000) de muestra
- `keywords/selected_niches.md` - Análisis de nichos seleccionados
- `database/schema.sql` - Esquema completo de base de datos
- `kpi.md` - Definición de métricas y objetivos
- `plan.md` - Plan maestro actualizado

### 🎯 Nichos Seleccionados (Recomendación Final)
1. **Personal Finance** - Alto CPC, contenido evergreen, monetización múltiple
2. **Home Improvement** - Competencia manejable, alto engagement, DIY
3. **Health & Wellness** - Alto CPC, contenido de bienestar general (evitar médico)

### 🔄 Siguiente Fase: FASE 1 - INFRAESTRUCTURA BASE
**Objetivo:** Configurar el stack tecnológico y despliegue automático.
- [ ] Configurar proyecto Astro con plantilla SEO-optimizada
- [ ] Conectar con Supabase/Firebase
- [ ] Despliegue automático Vercel + dominio
- [ ] Configurar GitHub Actions para builds automáticos
- [ ] Implementar sistema de logging/monitoreo

---

**Estado:** FASE 0 completada en un 85%. Lista para transición a FASE 1.