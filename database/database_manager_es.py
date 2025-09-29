#!/usr/bin/env python3
"""
Gestor de Base de Datos para Dashboard Gestión Carnicería
Gestiona todas las operaciones de base de datos
Creado por Ezio Camporeale
Traducido al español para Argentina
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import bcrypt

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos para la carnicería"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from config_es import DATABASE_PATH
            self.db_path = str(DATABASE_PATH)
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas"""
        try:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Crear conexión y tablas
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tablas
            self._create_tables(cursor)
            
            # Insertar datos iniciales
            self._insert_initial_data(cursor)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Base de datos carnicería inicializada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            raise
    
    def _create_tables(self, cursor):
        """Crea todas las tablas necesarias"""
        try:
            # Leer esquema SQL
            schema_path = Path(__file__).parent / "schema.sql"
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Ejecutar esquema
            cursor.executescript(schema_sql)
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            raise
    
    def _insert_initial_data(self, cursor):
        """Inserta datos iniciales en la base de datos"""
        try:
            # Datos ya están en el schema.sql
            pass
            
        except Exception as e:
            logger.error(f"❌ Error insertando datos iniciales: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = "all") -> Any:
        """Ejecuta una consulta SQL"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            if fetch == "all":
                result = [dict(row) for row in cursor.fetchall()]
            elif fetch == "one":
                result = dict(cursor.fetchone()) if cursor.fetchone() else None
            elif fetch == "none":
                result = None
            else:
                result = cursor.fetchall()
            
            conn.commit()
            conn.close()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            raise
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas para el dashboard"""
        try:
            stats = {}
            
            # Ventas de hoy (con manejo de errores)
            today = date.today()
            try:
                sales_today = self.execute_query(
                    "SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total FROM sales WHERE DATE(created_at) = ?",
                    (today,), "one"
                )
                stats['sales_today'] = sales_today or {'count': 0, 'total': 0}
            except:
                stats['sales_today'] = {'count': 0, 'total': 0}
            
            # Órdenes de hoy (con manejo de errores)
            try:
                orders_today = self.execute_query(
                    "SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total FROM customer_orders WHERE DATE(created_at) = ?",
                    (today,), "one"
                )
                stats['orders_today'] = orders_today or {'count': 0, 'total': 0}
            except:
                stats['orders_today'] = {'count': 0, 'total': 0}
            
            # Total de clientes (con manejo de errores)
            try:
                total_customers = self.execute_query(
                    "SELECT COUNT(*) as count FROM customers", (), "one"
                )
                stats['total_customers'] = total_customers['count'] if total_customers else 0
            except:
                stats['total_customers'] = 0
            
            # Total de productos (con manejo de errores)
            try:
                total_products = self.execute_query(
                    "SELECT COUNT(*) as count FROM products", (), "one"
                )
                stats['total_products'] = total_products['count'] if total_products else 0
            except:
                stats['total_products'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas dashboard: {e}")
            return {}
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """Obtiene todas las categorías de productos"""
        try:
            return self.execute_query(
                "SELECT id, name, description, color FROM product_categories ORDER BY name"
            )
        except Exception as e:
            logger.error(f"❌ Error obteniendo categorías: {e}")
            return []
    
    def get_units_of_measure(self) -> List[Dict[str, Any]]:
        """Obtiene todas las unidades de medida"""
        try:
            return self.execute_query(
                "SELECT id, name, symbol, description FROM units_of_measure ORDER BY name"
            )
        except Exception as e:
            logger.error(f"❌ Error obteniendo unidades: {e}")
            return []
    
    def get_user_roles(self) -> List[Dict[str, Any]]:
        """Obtiene todos los roles de usuario"""
        try:
            return self.execute_query(
                "SELECT id, name, description, permissions FROM user_roles ORDER BY name"
            )
        except Exception as e:
            logger.error(f"❌ Error obteniendo roles: {e}")
            return []
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Obtiene todos los productos con información de categoría"""
        try:
            return self.execute_query("""
                SELECT p.*, pc.name as category_name, uom.symbol as unit_symbol
                FROM products p
                LEFT JOIN product_categories pc ON p.category_id = pc.id
                LEFT JOIN units_of_measure uom ON p.unit_id = uom.id
                ORDER BY p.name
            """)
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos: {e}")
            return []
    
    def create_product(self, product_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea un nuevo producto"""
        try:
            query = """
                INSERT INTO products (
                    name, code, barcode, category_id, unit_id, description,
                    brand, origin, cost_price, selling_price, min_stock_level,
                    max_stock_level, shelf_life_days, requires_temperature_control,
                    storage_temperature_min, storage_temperature_max, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                product_data['name'], product_data.get('code'), product_data.get('barcode'),
                product_data['category_id'], product_data['unit_id'], product_data.get('description'),
                product_data.get('brand'), product_data.get('origin'), product_data.get('cost_price', 0),
                product_data['selling_price'], product_data.get('min_stock_level', 0),
                product_data.get('max_stock_level', 100), product_data.get('shelf_life_days', 3),
                product_data.get('requires_temperature_control', False),
                product_data.get('storage_temperature_min'), product_data.get('storage_temperature_max'),
                product_data['created_by']
            )
            
            self.execute_query(query, params, "none")
            return True, "Producto creado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error creando producto: {e}")
            return False, str(e)
    
    def get_products_low_stock(self) -> List[Dict[str, Any]]:
        """Obtiene productos con stock bajo"""
        try:
            # Verificar si la tabla products existe y tiene las columnas necesarias
            return self.execute_query("""
                SELECT p.name, p.current_stock, p.min_stock_level, uom.symbol as unit_symbol
                FROM products p
                LEFT JOIN units_of_measure uom ON p.unit_id = uom.id
                WHERE p.current_stock <= p.min_stock_level
                ORDER BY p.current_stock ASC
            """)
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos con stock bajo: {e}")
            return []
    
    def get_products_expiring_soon(self) -> List[Dict[str, Any]]:
        """Obtiene productos próximos a vencer"""
        try:
            # Verificar si la tabla products existe y tiene las columnas necesarias
            return self.execute_query("""
                SELECT p.name, p.expiry_date, p.batch_number
                FROM products p
                WHERE p.expiry_date IS NOT NULL 
                AND p.expiry_date <= date('now', '+3 days')
                ORDER BY p.expiry_date ASC
            """)
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos próximos a vencer: {e}")
            return []
    
    def get_sales_by_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Obtiene ventas por período"""
        try:
            return self.execute_query("""
                SELECT DATE(created_at) as date, SUM(total_amount) as total_revenue
                FROM sales
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (start_date, end_date))
        except Exception as e:
            logger.error(f"❌ Error obteniendo ventas por período: {e}")
            return []
    
    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtiene los productos más vendidos"""
        try:
            return self.execute_query("""
                SELECT p.name, SUM(si.quantity) as total_quantity
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                GROUP BY p.id, p.name
                ORDER BY total_quantity DESC
                LIMIT ?
            """, (limit,))
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos más vendidos: {e}")
            return []
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario"""
        try:
            user = self.execute_query(
                "SELECT * FROM users WHERE username = ?", (username,), "one"
            )
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # Obtener información del rol
                role = self.execute_query(
                    "SELECT * FROM user_roles WHERE id = ?", (user['role_id'],), "one"
                )
                
                if role:
                    user['role_name'] = role['name']
                    user['permissions'] = role['permissions'].split(',') if role['permissions'] else []
                
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error autenticando usuario: {e}")
            return None
    
    def log_activity(self, user_id: int, action: str, details: str, ip_address: str = None):
        """Registra una actividad del usuario"""
        try:
            self.execute_query("""
                INSERT INTO activity_log (user_id, action, details, ip_address, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, action, details, ip_address), "none")
            
        except Exception as e:
            logger.error(f"❌ Error registrando actividad: {e}")

# Instancia global del gestor de base de datos
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtiene la instancia global del gestor de base de datos"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

if __name__ == "__main__":
    # Test del gestor de base de datos
    print("🧪 Test Gestor Base de Datos Carnicería")
    
    try:
        db_manager = DatabaseManager()
        print("✅ Gestor de base de datos creado")
        
        # Test estadísticas
        stats = db_manager.get_dashboard_stats()
        print(f"✅ Estadísticas obtenidas: {len(stats)} métricas")
        
        # Test categorías
        categories = db_manager.get_product_categories()
        print(f"✅ Categorías obtenidas: {len(categories)} categorías")
        
        # Test unidades
        units = db_manager.get_units_of_measure()
        print(f"✅ Unidades obtenidas: {len(units)} unidades")
        
        print("✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
