# 🔒 ROADMAP INTERNO - GB Bot WhatsApp

---

## 📌 ESTADO ACTUAL DEL PROYECTO (Junio 2026)

### ✅ Completado
- Fase 1: Arquitectura local y modular
- Fase 2: Despliegue en Railway + CI/CD GitHub Actions
- Fase 3: Integración OpenAI (GPT-4o-mini)
- **NEW**: System Prompt basado en State Routing (Stateless) - Versión 3.0

### 🟡 En Progreso
- **Mejora del System Prompt**: Funcionalidades de clasificación, scoring y objeciones

### 🔴 Bloqueado / Pausado
- Fase 4: PostgreSQL (depende de decisión sobre dashboard)
- Fase 5: Dashboard Admin (depende de arquitectura de respuesta)

---

## 🎯 OPCIONES ESTRATÉGICAS ABIERTAS

### DECISIÓN #1: Sistema de Almacenamiento y Respuesta

#### Opción A: **WhatsApp Directo (MVP Simple)**
```
Cliente → Web Widget → OpenAI → Derivación al Número de GB WhatsApp
↓
Tú respondes directamente en WhatsApp
↓
SIN historial centralizado ni dashboard
```
- **Ventajas**: Rápido implementar, directo, natural
- **Desventajas**: Sin analytics, sin historial, sin centralización
- **Esfuerzo**: 0 (ya funciona así)
- **Costo**: $0 (solo OpenAI)
- **Recomendado para**: MVP, validación de mercado

#### Opción B: **Dashboard + Base de Datos (Profesional)**
```
Cliente → Web Widget → OpenAI → PostgreSQL (guardar conversación)
↓
Notificación (Email/Discord/Slack)
↓
Tú ves en Dashboard Admin
↓
Abres WhatsApp desde Dashboard para responder
↓
Respuesta se guarda en DB + analytics
```
- **Ventajas**: Centralizado, profesional, analytics, escalable
- **Desventajas**: Más desarrollo, más costo (PostgreSQL)
- **Esfuerzo**: 3-4 semanas
- **Costo**: ~$10-20/mes extra (Database en Railway)
- **Recomendado para**: Empresa seria, múltiples clientes, tracking

#### Opción C: **Híbrido Smart (LO MEJOR)**
```
Cliente → Web Widget → OpenAI → PostgreSQL
↓
Notificación SMART (solo si ESTADO B, lead calificado)
↓
Opción 1: Dashboard + WhatsApp (profesional)
Opción 2: WhatsApp directo (si quieres ir rápido ese día)
↓
Respuesta se trackea en ambos
```
- **Ventajas**: Flexibilidad, siempre profesional, escalable
- **Desventajas**: Un poco más de setup
- **Esfuerzo**: 3-4 semanas
- **Costo**: ~$10-20/mes extra
- **Recomendado para**: Tu caso (agencia creciente)

---

### DECISIÓN #2: Widget Web (Flotante en tu sitio)

#### Opción A: **Widget Simple (HTML + JS)**
- Implementar en tu web sin framework
- Conecta directo a FastAPI
- Rápido, pero estático
- Esfuerzo: 2-3 días

#### Opción B: **Widget React (Recomendado)**
- Componente React embebible como iframe
- Professional, responsive, Mobile-First
- Estilos GB (#4c87a4/#e5f2f0)
- Esfuerzo: 1 semana
- **RECOMENDADO**: Este

#### Opción C: **Widget con Libería (Crisp, Intercom, etc)**
- Usar servicio tercero
- Menos desarrollo
- Menos control
- Más costo
- NO RECOMENDADO: Queremos que sea nuestro

---

### DECISIÓN #3: Mecanismo de Notificaciones

Si implementas Dashboard (Opción B o C), ¿A dónde notificar cuando llega un ESTADO B?

#### Opción A: Email
- Simple, confiable
- Lento (no es tiempo real)
- ✅ Implementar

#### Opción B: Discord
- Rápido, integración fácil
- Si tienes servidor Discord
- ✅ Implementar

#### Opción C: Slack
- Profesional, integración nativa
- Si tienes workspace Slack
- ✅ Implementar

#### Opción D: Telegram
- Súper rápido, personal
- Si prefieres Telegram
- ✅ Implementar

#### Opción E: Múltiples (RECOMENDADO)
- Email + Discord + Slack
- No conflictúan
- ✅ HACER ESTO

---

## 🛣️ ROADMAP RECOMENDADO (Fases + Timing)

### **Fase 3.5: Mejora del System Prompt** (AHORA)
**Timeline: 1-2 días**
- ✅ State Routing sin loops
- ✅ Clasificación de intención (E-commerce, SPA, etc)
- ✅ Scoring de leads (hot/cold/medium)
- ✅ Preguntas de calificación (presupuesto, timeline)
- ✅ Manejo de objeciones menores

**Deliverable**: System Prompt v3.5 con funcionalidades extras

---

### **Fase 4: Base de Datos + Almacenamiento** (2-3 semanas)
**Dependencia**: Decisión sobre Opción A, B o C

Si **Opción A (WhatsApp directo)**: SKIP esta fase por ahora

Si **Opción B o C (Dashboard)**:
- Crear schema PostgreSQL
  - `conversations` table
  - `leads` table
  - `lead_intents` (categorización)
  - `metrics` (analytics)
- Conectar FastAPI a DB
- Guardar conversaciones en tiempo real

**Stack recomendado**:
- PostgreSQL en Railway
- SQLAlchemy ORM
- Alembic para migraciones

---

### **Fase 5: Widget Web Flotante** (1-2 semanas)
**Dependencia**: Ninguna (puedes hacerlo en paralelo)

- Crear componente React
- Embed en tu sitio web
- Estilos GB (naranja/arena)
- Mobile-First
- Conectar a FastAPI

**Stack recomendado**:
- React + TypeScript
- Tailwind CSS
- iframe embebible

---

### **Fase 6: Dashboard Admin** (2-3 semanas)
**Dependencia**: Fase 4 (Database)

- Panel para ver leads
- Listar conversaciones
- Botón "Abrir en WhatsApp"
- Etiquetar/asignar leads
- Búsqueda y filtros

**Stack recomendado**:
- Next.js + TypeScript
- Tailwind CSS
- SWR o React Query (datos)

---

### **Fase 7: Notificaciones en Tiempo Real** (3-5 días)
**Dependencia**: Fase 4 (Database)

- Webhook cuando ESTADO B
- Enviar a Email + Discord + Slack
- Link pre-rellenado a WhatsApp

**Stack recomendado**:
- Discord.py o similar
- SendGrid para email
- Slack SDK

---

### **Fase 8: Analytics** (1 semana)
**Dependencia**: Fase 4 (Database)

- Dashboard de métricas
- Conversión de leads
- Tiempo de respuesta promedio
- Servicios más consultados
- ROI

---

## 📊 TIMELINE TOTAL (Escenarios)

### Escenario A: MVP WhatsApp Directo (RECOMENDADO AHORA)
```
Fase 3.5 (Prompt mejorado): 1-2 días
TOTAL: 1-2 días
Costo: $0
Resultado: Bot listo para producción, stateless, sin loops
```

### Escenario B: Profesional (En 2-3 meses)
```
Fase 3.5: 1-2 días
Fase 4 (DB): 2-3 semanas
Fase 5 (Widget): 1-2 semanas
Fase 6 (Dashboard): 2-3 semanas
Fase 7 (Notificaciones): 3-5 días
Fase 8 (Analytics): 1 semana
TOTAL: ~6-8 semanas
Costo: ~$50-100 (Database + Hosting)
Resultado: Sistema profesional, centralizado, escalable
```

### Escenario C: Enterprise (En 4-5 meses)
```
Todas las fases + features adicionales
Multi-usuario, permisos, audit logs, etc
TOTAL: ~12-16 semanas
Costo: ~$200-300
```

---

## 🎯 MI RECOMENDACIÓN PERSONAL

**Para ti (agencia GB en crecimiento)**:

### Corto Plazo (Próximas 2 semanas):
1. ✅ Mejorar System Prompt (Fase 3.5) - LO HACES AHORA
2. ✅ Probar en producción WhatsApp
3. ✅ Validar que NO hay loops, que detecta bien ESTADO A vs B

### Mediano Plazo (Próximo mes):
4. Decidir: ¿Opción A (simple) o B/C (profesional)?
5. Si es A: Listo, no hay más que hacer
6. Si es B/C: Empezar Fase 4 (Database)

### Largo Plazo (En 2-3 meses):
7. Implementar Widget + Dashboard (si es B/C)
8. Empezar a trackear leads, hacer analytics
9. Optimizar System Prompt según datos reales

**AHORA MISMO**: Enfócate en el System Prompt v3.5. El resto es opcional.

---

## 🔑 PUNTOS CRÍTICOS A MONITOREAR

### Métrica 1: Tasa de loops
- ¿El bot cae en loops A→B→A?
- **Target**: 0 loops
- **Check**: Revisar conversaciones cada semana

### Métrica 2: Clasificación correcta
- ¿Detecta bien ESTADO A vs B?
- **Target**: >95% accuracy
- **Check**: Manual sampling cada 10 conversaciones

### Métrica 3: Derivaciones
- ¿Cuántos leads llegan a ESTADO B?
- **Target**: Depende de tráfico, pero >20% es bueno
- **Check**: Contar ESTADO B vs total

### Métrica 4: Respuesta humana
- ¿Cuánto tardás en responder?
- **Target**: <2 horas
- **Check**: Trackear si implementas Dashboard

### Métrica 5: Conversión final
- ¿Cuántos ESTADO B → Proyectos cerrados?
- **Target**: >10% (1 de 10 leads cierra)
- **Check**: Después de 3 meses de data

---

## 💾 VARIABLES DE ENTORNO (Para futuro)

Cuando implemente Fase 4+, necesitarás:

```bash
# OpenAI (ya tienes)
OPENAI_API_KEY=sk-...

# WhatsApp (ya tienes)
WHATSAPP_TOKEN=...
VERIFY_TOKEN=...
PHONE_NUMBER_ID=...

# Database (futuro)
DATABASE_URL=postgresql://user:pass@host/db

# Notificaciones (futuro)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SLACK_BOT_TOKEN=xoxb-...
SENDGRID_API_KEY=SG.xxx

# Frontend (futuro)
NEXT_PUBLIC_API_URL=https://bot.gbsolucionesdigitales.com.ar/api
```

---

## 🚀 SIGUIENTE ACCIÓN

**HOY**: 
1. Implementar System Prompt v3.5 mejorado
2. Testear en producción
3. Monitorear conversaciones los próximos 3-5 días

**SEMANA QUE VIENE**:
1. Analizar datos: ¿Qué le consultan más?
2. Decidir: ¿Opción A, B o C?
3. Si es B/C: Empezar diseño de Database

---

## 📞 CONTACTOS / REFERENCIAS

- **Railway Dashboard**: https://railway.app
- **OpenAI API Docs**: https://platform.openai.com/docs
- **Meta for Developers**: https://developers.facebook.com
- **GitHub Repo**: https://github.com/Brian13b/backend_gb_soluciones_digitales

---
