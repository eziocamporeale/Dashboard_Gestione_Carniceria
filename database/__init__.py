"""
Database module for Dashboard Gestión Carnicería
Módulo de base de datos para el Dashboard de Gestión de Carnicería

Created by: Ezio Camporeale
"""

# Import main database managers
try:
    from .hybrid_database_manager import get_hybrid_manager
    from .supabase_manager import SupabaseManager
    from .database_manager_simple import SimpleDatabaseManager
    __all__ = ['get_hybrid_manager', 'SupabaseManager', 'SimpleDatabaseManager']
except ImportError as e:
    print(f"⚠️ Warning: Some database modules could not be imported: {e}")
    __all__ = []
