# GB Soluciones Digitales - Backend (Bot & Admin Panel)

Solución empresarial de **atención automatizada y gestión de leads** para GB Soluciones Digitales. Sistema de dos servicios independientes (Bot y Admin) compartiendo una base de datos PostgreSQL, desplegado en Railway con integración de WhatsApp Cloud API y OpenAI GPT-4o-mini.

## 🎯 Descripción General

- **Bot Service:** Webhook de WhatsApp stateless que clasifica intenciones de clientes usando State Routing (ESTADO A: Exploración vs ESTADO B: Captura de lead).
- **Admin Service:** Dashboard protegido con JWT para gestionar conversations, leads y analytics.
- **Base de Datos Compartida:** PostgreSQL con modelos para Conversation, Message, ContactAttempt, User.
- **Despliegue:** Railway PaaS con CI/CD automático desde GitHub Actions.

---

## 📋 Requisitos

- **Python:** 3.13+
- **Base de Datos:** PostgreSQL 15+
- **Entorno:** Railway (producción) / Local con .env

### Dependencias Principales

Ver `requirements.txt` para lista completa. Principales:

```
fastapi>=0.110.0            # Framework web asíncrono
uvicorn[standard]>=0.28.0   # Servidor ASGI
sqlalchemy>=2.0.0,<2.1.0    # ORM para base de datos
psycopg2-binary>=2.9.9      # Driver PostgreSQL
pydantic>=2.7.0             # Validación de datos
openai>=1.52.0              # API de OpenAI (GPT-4o-mini)
PyJWT>=2.10.0               # Tokens JWT para autenticación
```

---

## 📂 Estructura del Proyecto

```
backend_gb_soluciones_digitales/
├── .github/
│   └── workflows/
│       └── main.yml                 # CI/CD Pipeline (GitHub Actions)
├── bot/                             # Bot Service
│   ├── __init__.py
│   ├── main.py                      # FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # chatweb y webhook de whatsapp
│   ├── bot_logic.py                 # OpenAI integracion y logica de ruteo
│   ├── crud.py                      # Database
│   ├── database.py                  # SQLAlchemy
│   ├── models.py                    # ORM 
│   ├── schemas.py                   
│   ├── SYSTEM_PROMPT.md             # Prompt para GPT-4o-mini
│   └── services/
│       ├── __init__.py
│       ├── data_servicios.json      # Catalogo de servicios
│       └── servicio_manager.py      # logica de servicio
├── admin/                           # Admin
│   ├── __init__.py
│   ├── main.py                      # FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  # JWT authentication
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py              
│   │       ├── conversations.py     
│   │       ├── contact_attempts.py  
│   │       └── stats.py             
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                
│   │   └── security.py              
│   ├── database.py                  # SQLAlchemy
│   ├── models.py                    
│   ├── schemas.py                   
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── shared/                          # Schemas unificados
│   ├── __init__.py
│   └── schemas.py                   # Todos los schemas
├── .env                             
├── .env.example                     
├── .gitignore
├── Procfile                         # Comando deploy Railway
├── requirements.txt                 
└── README.md                        
```

---

## 🏗️ Arquitectura

### Flujo de Datos

```
┌──────────────────────────────────────────────────────┐
│                   CLIENTE                            │
├──────────────────────────────────────────────────────┤
│     WhatsApp (via Meta Cloud API) OR Web Widget      │
└──────────────────────┬───────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │          BOT SERVICE             │
        ├──────────────────────────────────┤
        │ POST /webhook       ← WhatsApp   │
        │ POST /api/chat-web  ← Web        │
        │ GET /health         ← Monitoring │
        └──────────────┬───────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │  OpenAI API (GPT-4o-mini)        │
        └──────────────┬───────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │    PostgreSQL Database           │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────┴───────────────────┐
        │                                  │
        ↓                                  ↓
   ┌─────────────────────┐      ┌───────────────────────────────┐
   │ ADMIN               │      │ CLIENTE (WhatsApp)            │
   └─────────────────────┘      │ Obtiene respuesta de la IA    │
                                └───────────────────────────────┘
```

---

## 🚀 Instalación y Ejecución

### Local

```bash
# 1. Clonar repositorio
git clone https://github.com/Brian13b/backend_gb_soluciones_digitales.git
cd backend_gb_soluciones_digitales

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear archivo .env
cp .env.example .env
# Editar .env con credenciales reales
```

### Ejecutar Servicios Localmente

#### **Bot Service**
```bash
# Terminal 1
uvicorn bot.main:app --reload --host 0.0.0.0 --port 8000

curl http://localhost:8000/health
# Response: {"status": "ok"}
```

#### **Admin Service**
```bash
# Terminal 2
uvicorn admin.main:app --reload --host 0.0.0.0 --port 8001

curl http://localhost:8001/health
# Response: {"status": "ok"}
```

#### **Test Chat Endpoint**
```bash
# Terminal 3
curl -X POST http://localhost:8000/api/chat-web \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Hola, necesito una app web",
    "sender_phone": "1234567890"
  }'
```

---

## 🚢 Despliegue en Railway

### Deploy Automático

1. Push a `main` en GitHub
2. GitHub Actions ejecuta validación (linting, tests)
3. Railway detecta cambios y redeploy automático
4. Health check en `GET /health` valida startup
---

## 📡 Endpoints Disponibles

### Bot

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Health check (usado por Railway) |
| `POST` | `/api/chat-web` | Chat desde widget web |
| `POST` | `/webhook` | Webhook de WhatsApp Cloud API |
| `GET` | `/webhook` | Verificación de webhook (Meta) |

### Admin

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login` | ❌ | Obtener JWT token |
| `GET` | `/api/conversations` | ✅ JWT | Listar conversaciones |
| `GET` | `/api/conversations/{id}` | ✅ JWT | Detalle de conversación |
| `GET` | `/api/contact-attempts` | ✅ JWT | Historial de intentos |
| `GET` | `/api/stats` | ✅ JWT | Analytics (cuentas, scores) |
| `GET` | `/health` | ❌ | Health check |

---

## 🔐 Seguridad

- ✅ Credenciales en `.env` (no en código)
- ✅ JWT tokens con expiración
- ✅ CORS configurado para dominios específicos
- ✅ Password hashing con bcrypt
- ✅ Variables de entorno cifradas en Railway
- ⚠️ **TODO:** Rate limiting en endpoints públicos
- ⚠️ **TODO:** HTTPS enforcement

---

## 📄 Licencia

Propietario de **GB Soluciones Digitales**. Uso interno únicamente.
