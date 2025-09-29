#!/usr/bin/env python3
"""
Inicialización de Base de Datos para Dashboard Gestión Carnicería
Creado por Ezio Camporeale
Traducido al español para Argentina
"""

import os
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

# Añadir el path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config_es import DATABASE_PATH, APP_NAME, APP_VERSION, APP_AUTHOR
from database.database_manager_es import get_db_manager

def main():
    """Función principal de inicialización"""
    print(f"🥩 {APP_NAME} - Inicialización Base de Datos")
    print(f"Creado por {APP_AUTHOR}")
    print()
    print(f"🚀 Inicialización Base de Datos {APP_NAME}")
    print("=" * 60)
    
    # Crear directorios necesarios
    print("📁 Creando directorios necesarios...")
    try:
        data_dir = DATABASE_PATH.parent
        data_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Directorios creados correctamente")
    except Exception as e:
        print(f"❌ Error creando directorios: {e}")
        return False
    
    # Inicializar base de datos
    print("🗄️ Inicializando base de datos...")
    try:
        db_manager = get_db_manager()
        db_manager.init_database()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False
    
    # Test de conexión
    print("🔍 Test de conexión base de datos...")
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        print("✅ Conexión base de datos OK")
    except Exception as e:
        print(f"❌ Error en test de conexión: {e}")
        return False
    
    # Verificar tablas creadas
    print("📋 Verificando tablas creadas...")
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        table_names = [table[0] for table in tables]
        print(f"✅ {len(table_names)} tablas creadas:")
        for table_name in sorted(table_names):
            print(f"   - {table_name}")
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False
    
    # Verificar datos iniciales
    print("📊 Verificando datos iniciales...")
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        # Verificar roles
        cursor.execute("SELECT COUNT(*) FROM user_roles")
        roles_count = cursor.fetchone()[0]
        print(f"✅ {roles_count} roles de usuario insertados")
        
        # Verificar unidades de medida
        cursor.execute("SELECT COUNT(*) FROM units_of_measure")
        units_count = cursor.fetchone()[0]
        print(f"✅ {units_count} unidades de medida insertadas")
        
        # Verificar categorías de productos
        cursor.execute("SELECT COUNT(*) FROM product_categories")
        categories_count = cursor.fetchone()[0]
        print(f"✅ {categories_count} categorías de productos insertadas")
        
        # Verificar configuraciones del sistema
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        settings_count = cursor.fetchone()[0]
        print(f"✅ {settings_count} configuraciones del sistema insertadas")
        
        # Verificar usuarios
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"✅ {users_count} usuarios insertados")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error verificando datos iniciales: {e}")
        return False
    
    # Test de funcionalidades base
    print("🧪 Test de funcionalidades base...")
    try:
        db_manager = get_db_manager()
        
        # Test estadísticas dashboard
        stats = db_manager.get_dashboard_stats()
        print(f"✅ Estadísticas dashboard: {len(stats)} métricas disponibles")
        
        # Test categorías de productos
        categories = db_manager.get_product_categories()
        print(f"✅ Categorías de productos: {len(categories)} disponibles")
        
        # Test unidades de medida
        units = db_manager.get_units_of_measure()
        print(f"✅ Unidades de medida: {len(units)} disponibles")
        
        # Test roles de usuario
        roles = db_manager.get_user_roles()
        print(f"✅ Roles de usuario: {len(roles)} disponibles")
        
    except Exception as e:
        print(f"❌ Error en test de funcionalidades: {e}")
        return False
    
    # Información del archivo de base de datos
    print()
    print("📋 Información Base de Datos:")
    try:
        db_size = DATABASE_PATH.stat().st_size / 1024  # KB
        db_created = DATABASE_PATH.stat().st_ctime
        created_date = datetime.fromtimestamp(db_created).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"   📍 Ruta: {DATABASE_PATH}")
        print(f"   📏 Tamaño: {db_size:.1f} KB")
        print(f"   🗓️ Creado: {created_date}")
    except Exception as e:
        print(f"❌ Error obteniendo información de BD: {e}")
    
    # Credenciales por defecto
    print()
    print("🔐 Credenciales por Defecto:")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: admin123")
    print("   ⚠️  IMPORTANTE: ¡Cambia la contraseña después del primer acceso!")
    
    print()
    print("🎉 ¡Inicialización completada con éxito!")
    print("🚀 Puedes ahora iniciar la aplicación con: streamlit run app_es.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Inicialización exitosa")
            sys.exit(0)
        else:
            print("\n❌ Error durante la inicialización")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Inicialización cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
