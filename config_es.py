#!/usr/bin/env python3
"""
Configuración global para Dashboard Gestión Carnicería
Creado por Ezio Camporeale
Traducido al español para Argentina
"""

import os
from pathlib import Path
from datetime import timedelta

# ===== CONFIGURACIÓN GENERAL =====

# Nombre aplicación
APP_NAME = "Dashboard Gestión Carnicería"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Ezio Camporeale"

# Rutas archivos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = DATA_DIR / "uploads"
EXPORTS_DIR = DATA_DIR / "exports"

# Base de datos
DATABASE_PATH = DATA_DIR / "carniceria.db"
DATABASE_BACKUP_RETENTION_DAYS = 30

# ===== CONFIGURACIÓN STREAMLIT =====

# Configuraciones Streamlit
STREAMLIT_CONFIG = {
    "server": {
        "port": 8501,
        "headless": True,
        "enableCORS": False,
        "enableXsrfProtection": True,
    },
    "browser": {
        "gatherUsageStats": False,
    },
    "theme": {
        "primaryColor": "#FF6B35",  # Naranja carnicería
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
    }
}

# ===== CONFIGURACIÓN AUTENTICACIÓN =====

# Seguridad
SECRET_KEY = "carniceria_secret_key_2024_ezio_camporeale"
SESSION_TIMEOUT_HOURS = 8
PASSWORD_MIN_LENGTH = 8

# Roles usuario
USER_ROLES = {
    "admin": {
        "name": "Administrador",
        "permissions": ["all"],
        "description": "Acceso completo a todas las funcionalidades"
    },
    "manager": {
        "name": "Gerente",
        "permissions": ["inventario", "ventas", "clientes", "analytics"],
        "description": "Gestión operativa completa"
    },
    "vendedor": {
        "name": "Vendedor",
        "permissions": ["ventas", "clientes"],
        "description": "Gestión de ventas y clientes"
    },
    "almacenero": {
        "name": "Almacenero",
        "permissions": ["inventario"],
        "description": "Gestión de inventario y stock"
    },
    "viewer": {
        "name": "Visualizador",
        "permissions": ["analytics"],
        "description": "Solo visualización de reportes"
    }
}

# ===== CONFIGURACIÓN NEGOCIO =====

# Monedas
DEFAULT_CURRENCY = "ARS"  # Peso argentino
CURRENCY_SYMBOL = "$"

# Unidades de medida
UNITS_OF_MEASURE = {
    "weight": ["kg", "g", "hg"],
    "volume": ["L", "ml"],
    "pieces": ["pz", "piezas"]
}

# Categorías productos principales
PRODUCT_CATEGORIES = {
    "bovino": {
        "name": "Carne Bovina",
        "color": "#8B4513",
        "subcategories": ["vaca", "ternero", "buey", "novilla"]
    },
    "porcino": {
        "name": "Carne Porcina", 
        "color": "#FFB6C1",
        "subcategories": ["cerdo", "jabalí", "lechón"]
    },
    "aves": {
        "name": "Aves",
        "color": "#FFD700",
        "subcategories": ["pollo", "pavo", "pato", "conejo"]
    },
    "embutidos": {
        "name": "Embutidos",
        "color": "#CD853F",
        "subcategories": ["jamón", "salame", "mortadela", "panceta"]
    },
    "frescos": {
        "name": "Productos Frescos",
        "color": "#90EE90",
        "subcategories": ["verduras", "quesos", "lácteos"]
    },
    "congelados": {
        "name": "Congelados",
        "color": "#87CEEB",
        "subcategories": ["carne", "pescado", "verduras"]
    }
}

# Estados órdenes
ORDER_STATUSES = {
    "nuevo": {"name": "Nuevo", "color": "#FF6B35"},
    "en_preparacion": {"name": "En Preparación", "color": "#FFA500"},
    "listo": {"name": "Listo", "color": "#32CD32"},
    "entregado": {"name": "Entregado", "color": "#008000"},
    "cancelado": {"name": "Cancelado", "color": "#FF0000"}
}

# Métodos pago
PAYMENT_METHODS = {
    "efectivo": {"name": "Efectivo", "icon": "💰"},
    "tarjeta": {"name": "Tarjeta", "icon": "💳"},
    "transferencia": {"name": "Transferencia", "icon": "🏦"},
    "cheque": {"name": "Cheque", "icon": "📄"},
    "cuotas": {"name": "Cuotas", "icon": "📅"}
}

# ===== CONFIGURACIÓN NOTIFICACIONES =====

# Email
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "carniceria@example.com",
    "sender_password": "your_password_here"
}

# Configuración alertas
ALERT_CONFIG = {
    "low_stock_threshold": 10,  # Umbral stock bajo
    "expiry_warning_days": 3,   # Días antes vencimiento para alerta
    "payment_overdue_days": 7   # Días para pagos vencidos
}

# ===== CONFIGURACIÓN REPORTES =====

# Formatos exportación
EXPORT_FORMATS = {
    "excel": {"extension": ".xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "pdf": {"extension": ".pdf", "mime_type": "application/pdf"},
    "csv": {"extension": ".csv", "mime_type": "text/csv"}
}

# Plantillas reportes
REPORT_TEMPLATES = {
    "ventas_diarias": "Reporte ventas diarias",
    "inventario_stock": "Reporte stock inventario",
    "clientes_analisis": "Análisis clientes",
    "proveedores_pagos": "Reporte pagos proveedores"
}

# ===== CONFIGURACIÓN BACKUP =====

BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_frequency_hours": 24,
    "backup_retention_days": 30,
    "compress_backups": True
}

# ===== CONFIGURACIÓN LOGGING =====

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "carniceria.log",
    "max_size_mb": 10,
    "backup_count": 5
}

# ===== CONFIGURACIÓN PERFORMANCE =====

PERFORMANCE_CONFIG = {
    "cache_ttl_seconds": 300,  # Cache time-to-live
    "max_records_per_page": 100,
    "enable_query_optimization": True,
    "lazy_loading": True
}

# ===== CONFIGURACIÓN INTEGRACIONES =====

# APIs externas (opcionales)
EXTERNAL_APIS = {
    "pos_system": {
        "enabled": False,
        "endpoint": "http://localhost:8080/api",
        "api_key": "your_api_key"
    },
    "accounting_system": {
        "enabled": False,
        "endpoint": "http://localhost:8081/api",
        "api_key": "your_api_key"
    }
}

# ===== FUNCIONES UTILIDAD =====

def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    directories = [DATA_DIR, LOGS_DIR, BACKUPS_DIR, UPLOADS_DIR, EXPORTS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_database_path():
    """Retorna la ruta de la base de datos"""
    return str(DATABASE_PATH)

def get_static_path():
    """Retorna la ruta de la carpeta static"""
    return str(STATIC_DIR)

def get_upload_path():
    """Retorna la ruta de la carpeta uploads"""
    return str(UPLOADS_DIR)

def get_export_path():
    """Retorna la ruta de la carpeta exports"""
    return str(EXPORTS_DIR)

# ===== INICIALIZACIÓN =====

# Crea los directorios necesarios
ensure_directories()

# Configuración ambiente
if os.getenv("ENVIRONMENT") == "production":
    # Configuraciones para producción
    STREAMLIT_CONFIG["server"]["headless"] = True
    LOGGING_CONFIG["level"] = "WARNING"
else:
    # Configuraciones para desarrollo
    STREAMLIT_CONFIG["server"]["headless"] = False
    LOGGING_CONFIG["level"] = "DEBUG"

print(f"✅ Configuración {APP_NAME} v{APP_VERSION} cargada correctamente")
print(f"📁 Directorio base: {BASE_DIR}")
print(f"🗄️ Base de datos: {DATABASE_PATH}")
print(f"📊 Roles usuario: {len(USER_ROLES)} configurados")
print(f"🏷️ Categorías productos: {len(PRODUCT_CATEGORIES)} configuradas")
