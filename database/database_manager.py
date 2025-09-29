#!/usr/bin/env python3
"""
Database Manager per Dashboard Gestione Macelleria
Gestisce tutte le operazioni CRUD e query complesse
Creato da Ezio Camporeale
"""

import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
import bcrypt
from config import DATABASE_PATH, LOGGING_CONFIG

# Configura logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MacelleriaDatabaseManager:
    """Database Manager completo per la gestione della macelleria"""
    
    def __init__(self, db_path: str = None):
        """Inizializza il database manager"""
        self.db_path = db_path or str(DATABASE_PATH)
        self.init_database()
    
    def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        try:
            # Crea la directory se non esiste
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Leggi e esegui lo schema SQL
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                # Esegui lo schema (SQLite non supporta esecuzione multipla)
                cursor.executescript(schema_sql)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database macelleria inizializzato correttamente")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione database: {e}")
            raise
    
    def get_connection(self):
        """Ottiene una connessione al database"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = "all") -> Union[List, Dict, Any]:
        """Esegue una query e restituisce i risultati"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == "all":
                results = cursor.fetchall()
            elif fetch == "one":
                results = cursor.fetchone()
            elif fetch == "none":
                results = None
            
            conn.commit()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Errore esecuzione query: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Esegue una query con parametri multipli"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(query, params_list)
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore esecuzione query multipla: {e}")
            return False
    
    # ===== GESTIONE UTENTI E AUTENTICAZIONE =====
    
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """Crea un nuovo utente"""
        try:
            # Hash della password
            password_hash = bcrypt.hashpw(
                user_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            query = """
                INSERT INTO users (username, email, password_hash, first_name, last_name, 
                                 phone, role_id, is_active, notes, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('phone', ''),
                user_data['role_id'],
                user_data.get('is_active', True),
                user_data.get('notes', ''),
                user_data['created_by']
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Utente creato: {user_data['username']}")
            return True, user_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione utente: {e}")
            return False, str(e)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un utente"""
        try:
            query = """
                SELECT u.id, u.username, u.email, u.password_hash, u.first_name, u.last_name,
                       u.role_id, u.is_active, u.is_admin, ur.name as role_name, ur.permissions
                FROM users u
                JOIN user_roles ur ON u.role_id = ur.id
                WHERE u.username = ? AND u.is_active = 1
            """
            
            result = self.execute_query(query, (username,), "one")
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[3].encode('utf-8')):
                # Aggiorna ultimo login
                self.update_user_last_login(result[0])
                
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'first_name': result[4],
                    'last_name': result[5],
                    'role_id': result[6],
                    'is_active': result[7],
                    'is_admin': result[8],
                    'role_name': result[9],
                    'permissions': json.loads(result[10]) if result[10] else []
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore autenticazione: {e}")
            return None
    
    def update_user_last_login(self, user_id: int):
        """Aggiorna l'ultimo login dell'utente"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute_query(query, (user_id,), "none")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un utente per ID"""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone,
                   u.role_id, u.is_active, u.is_admin, u.notes, u.created_at, u.last_login,
                   ur.name as role_name, ur.display_name as role_display_name
            FROM users u
            JOIN user_roles ur ON u.role_id = ur.id
            WHERE u.id = ?
        """
        
        result = self.execute_query(query, (user_id,), "one")
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'first_name': result[3],
                'last_name': result[4],
                'phone': result[5],
                'role_id': result[6],
                'is_active': result[7],
                'is_admin': result[8],
                'notes': result[9],
                'created_at': result[10],
                'last_login': result[11],
                'role_name': result[12],
                'role_display_name': result[13]
            }
        
        return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Ottiene tutti gli utenti"""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone,
                   u.role_id, u.is_active, u.is_admin, u.created_at, u.last_login,
                   ur.name as role_name, ur.display_name as role_display_name
            FROM users u
            JOIN user_roles ur ON u.role_id = ur.id
            ORDER BY u.first_name, u.last_name
        """
        
        results = self.execute_query(query)
        users = []
        
        for result in results:
            users.append({
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'first_name': result[3],
                'last_name': result[4],
                'phone': result[5],
                'role_id': result[6],
                'is_active': result[7],
                'is_admin': result[8],
                'created_at': result[9],
                'last_login': result[10],
                'role_name': result[11],
                'role_display_name': result[12]
            })
        
        return users
    
    # ===== GESTIONE PRODOTTI E INVENTARIO =====
    
    def create_product(self, product_data: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """Crea un nuovo prodotto"""
        try:
            query = """
                INSERT INTO products (name, code, barcode, category_id, unit_id, description,
                                    brand, origin, weight_per_unit, cost_price, selling_price,
                                    min_stock_level, max_stock_level, shelf_life_days,
                                    requires_temperature_control, storage_temperature_min,
                                    storage_temperature_max, is_active, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                product_data['name'],
                product_data.get('code', ''),
                product_data.get('barcode', ''),
                product_data['category_id'],
                product_data['unit_id'],
                product_data.get('description', ''),
                product_data.get('brand', ''),
                product_data.get('origin', ''),
                product_data.get('weight_per_unit', 1.0),
                product_data.get('cost_price', 0.0),
                product_data['selling_price'],
                product_data.get('min_stock_level', 0),
                product_data.get('max_stock_level', 1000),
                product_data.get('shelf_life_days'),
                product_data.get('requires_temperature_control', False),
                product_data.get('storage_temperature_min'),
                product_data.get('storage_temperature_max'),
                product_data.get('is_active', True),
                product_data['created_by']
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Prodotto creato: {product_data['name']}")
            return True, product_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione prodotto: {e}")
            return False, str(e)
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un prodotto per ID"""
        query = """
            SELECT p.id, p.name, p.code, p.barcode, p.category_id, p.unit_id,
                   p.description, p.brand, p.origin, p.weight_per_unit,
                   p.cost_price, p.selling_price, p.min_stock_level, p.max_stock_level,
                   p.shelf_life_days, p.requires_temperature_control,
                   p.storage_temperature_min, p.storage_temperature_max,
                   p.is_active, p.created_at, p.updated_at,
                   pc.name as category_name, pc.color as category_color,
                   uom.name as unit_name, uom.symbol as unit_symbol
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            LEFT JOIN units_of_measure uom ON p.unit_id = uom.id
            WHERE p.id = ?
        """
        
        result = self.execute_query(query, (product_id,), "one")
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'code': result[2],
                'barcode': result[3],
                'category_id': result[4],
                'unit_id': result[5],
                'description': result[6],
                'brand': result[7],
                'origin': result[8],
                'weight_per_unit': result[9],
                'cost_price': result[10],
                'selling_price': result[11],
                'min_stock_level': result[12],
                'max_stock_level': result[13],
                'shelf_life_days': result[14],
                'requires_temperature_control': result[15],
                'storage_temperature_min': result[16],
                'storage_temperature_max': result[17],
                'is_active': result[18],
                'created_at': result[19],
                'updated_at': result[20],
                'category_name': result[21],
                'category_color': result[22],
                'unit_name': result[23],
                'unit_symbol': result[24]
            }
        
        return None
    
    def get_all_products(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Ottiene tutti i prodotti"""
        where_clause = "WHERE p.is_active = 1" if active_only else ""
        
        query = f"""
            SELECT p.id, p.name, p.code, p.barcode, p.category_id, p.unit_id,
                   p.description, p.brand, p.origin, p.weight_per_unit,
                   p.cost_price, p.selling_price, p.min_stock_level, p.max_stock_level,
                   p.shelf_life_days, p.requires_temperature_control,
                   p.storage_temperature_min, p.storage_temperature_max,
                   p.is_active, p.created_at, p.updated_at,
                   pc.name as category_name, pc.color as category_color,
                   uom.name as unit_name, uom.symbol as unit_symbol,
                   COALESCE(SUM(i.quantity), 0) as current_stock
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            LEFT JOIN units_of_measure uom ON p.unit_id = uom.id
            LEFT JOIN inventory i ON p.id = i.product_id AND i.quality_status = 'good'
            {where_clause}
            GROUP BY p.id
            ORDER BY p.name
        """
        
        results = self.execute_query(query)
        products = []
        
        for result in results:
            products.append({
                'id': result[0],
                'name': result[1],
                'code': result[2],
                'barcode': result[3],
                'category_id': result[4],
                'unit_id': result[5],
                'description': result[6],
                'brand': result[7],
                'origin': result[8],
                'weight_per_unit': result[9],
                'cost_price': result[10],
                'selling_price': result[11],
                'min_stock_level': result[12],
                'max_stock_level': result[13],
                'shelf_life_days': result[14],
                'requires_temperature_control': result[15],
                'storage_temperature_min': result[16],
                'storage_temperature_max': result[17],
                'is_active': result[18],
                'created_at': result[19],
                'updated_at': result[20],
                'category_name': result[21],
                'category_color': result[22],
                'unit_name': result[23],
                'unit_symbol': result[24],
                'current_stock': result[25]
            })
        
        return products
    
    def get_products_low_stock(self) -> List[Dict[str, Any]]:
        """Ottiene prodotti con scorte basse"""
        query = """
            SELECT p.id, p.name, p.code, p.min_stock_level,
                   COALESCE(SUM(i.quantity), 0) as current_stock,
                   pc.name as category_name, pc.color as category_color
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            LEFT JOIN inventory i ON p.id = i.product_id AND i.quality_status = 'good'
            WHERE p.is_active = 1 AND p.min_stock_level > 0
            GROUP BY p.id
            HAVING current_stock <= p.min_stock_level
            ORDER BY (current_stock - p.min_stock_level) ASC
        """
        
        results = self.execute_query(query)
        products = []
        
        for result in results:
            products.append({
                'id': result[0],
                'name': result[1],
                'code': result[2],
                'min_stock_level': result[3],
                'current_stock': result[4],
                'category_name': result[5],
                'category_color': result[6]
            })
        
        return products
    
    def get_products_expiring_soon(self, days: int = 3) -> List[Dict[str, Any]]:
        """Ottiene prodotti in scadenza"""
        query = """
            SELECT p.id, p.name, p.code, i.batch_number, i.expiry_date,
                   i.quantity, uom.symbol as unit_symbol,
                   pc.name as category_name, pc.color as category_color
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN units_of_measure uom ON i.unit_id = uom.id
            WHERE p.is_active = 1 AND i.quality_status = 'good'
            AND i.expiry_date IS NOT NULL
            AND i.expiry_date <= date('now', '+{} days')
            ORDER BY i.expiry_date ASC
        """.format(days)
        
        results = self.execute_query(query)
        products = []
        
        for result in results:
            products.append({
                'id': result[0],
                'name': result[1],
                'code': result[2],
                'batch_number': result[3],
                'expiry_date': result[4],
                'quantity': result[5],
                'unit_symbol': result[6],
                'category_name': result[7],
                'category_color': result[8]
            })
        
        return products
    
    # ===== GESTIONE CLIENTI =====
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """Crea un nuovo cliente"""
        try:
            query = """
                INSERT INTO customers (first_name, last_name, email, phone, address, city,
                                     postal_code, country, birth_date, customer_type,
                                     company_name, vat_number, tax_code, preferences,
                                     allergies, loyalty_points, notes, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                customer_data['first_name'],
                customer_data['last_name'],
                customer_data.get('email', ''),
                customer_data.get('phone', ''),
                customer_data.get('address', ''),
                customer_data.get('city', ''),
                customer_data.get('postal_code', ''),
                customer_data.get('country', 'Italia'),
                customer_data.get('birth_date'),
                customer_data.get('customer_type', 'individual'),
                customer_data.get('company_name', ''),
                customer_data.get('vat_number', ''),
                customer_data.get('tax_code', ''),
                json.dumps(customer_data.get('preferences', {})),
                customer_data.get('allergies', ''),
                customer_data.get('loyalty_points', 0),
                customer_data.get('notes', ''),
                customer_data['created_by']
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            customer_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cliente creato: {customer_data['first_name']} {customer_data['last_name']}")
            return True, customer_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione cliente: {e}")
            return False, str(e)
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Ottiene un cliente per ID"""
        query = """
            SELECT id, first_name, last_name, email, phone, address, city,
                   postal_code, country, birth_date, customer_type, company_name,
                   vat_number, tax_code, preferences, allergies, loyalty_points,
                   total_spent, last_purchase_date, is_active, notes,
                   created_at, updated_at
            FROM customers WHERE id = ?
        """
        
        result = self.execute_query(query, (customer_id,), "one")
        
        if result:
            return {
                'id': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'email': result[3],
                'phone': result[4],
                'address': result[5],
                'city': result[6],
                'postal_code': result[7],
                'country': result[8],
                'birth_date': result[9],
                'customer_type': result[10],
                'company_name': result[11],
                'vat_number': result[12],
                'tax_code': result[13],
                'preferences': json.loads(result[14]) if result[14] else {},
                'allergies': result[15],
                'loyalty_points': result[16],
                'total_spent': result[17],
                'last_purchase_date': result[18],
                'is_active': result[19],
                'notes': result[20],
                'created_at': result[21],
                'updated_at': result[22]
            }
        
        return None
    
    def get_all_customers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Ottiene tutti i clienti"""
        where_clause = "WHERE is_active = 1" if active_only else ""
        
        query = f"""
            SELECT id, first_name, last_name, email, phone, address, city,
                   postal_code, country, birth_date, customer_type, company_name,
                   vat_number, tax_code, preferences, allergies, loyalty_points,
                   total_spent, last_purchase_date, is_active, notes,
                   created_at, updated_at
            FROM customers {where_clause}
            ORDER BY first_name, last_name
        """
        
        results = self.execute_query(query)
        customers = []
        
        for result in results:
            customers.append({
                'id': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'email': result[3],
                'phone': result[4],
                'address': result[5],
                'city': result[6],
                'postal_code': result[7],
                'country': result[8],
                'birth_date': result[9],
                'customer_type': result[10],
                'company_name': result[11],
                'vat_number': result[12],
                'tax_code': result[13],
                'preferences': json.loads(result[14]) if result[14] else {},
                'allergies': result[15],
                'loyalty_points': result[16],
                'total_spent': result[17],
                'last_purchase_date': result[18],
                'is_active': result[19],
                'notes': result[20],
                'created_at': result[21],
                'updated_at': result[22]
            })
        
        return customers
    
    # ===== GESTIONE ORDINI E VENDITE =====
    
    def create_customer_order(self, order_data: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """Crea un nuovo ordine cliente"""
        try:
            # Genera numero ordine unico
            order_number = self._generate_order_number()
            
            query = """
                INSERT INTO customer_orders (order_number, customer_id, delivery_date,
                                           delivery_time, status, total_amount,
                                           discount_amount, tax_amount, final_amount,
                                           payment_method, payment_status, payment_due_date,
                                           delivery_address, delivery_notes,
                                           special_instructions, is_delivery, delivery_fee,
                                           created_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                order_number,
                order_data['customer_id'],
                order_data.get('delivery_date'),
                order_data.get('delivery_time', ''),
                order_data.get('status', 'nuovo'),
                order_data.get('total_amount', 0.0),
                order_data.get('discount_amount', 0.0),
                order_data.get('tax_amount', 0.0),
                order_data.get('final_amount', 0.0),
                order_data.get('payment_method', 'contanti'),
                order_data.get('payment_status', 'pending'),
                order_data.get('payment_due_date'),
                order_data.get('delivery_address', ''),
                order_data.get('delivery_notes', ''),
                order_data.get('special_instructions', ''),
                order_data.get('is_delivery', False),
                order_data.get('delivery_fee', 0.0),
                order_data['created_by'],
                order_data.get('notes', '')
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            order_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Ordine creato: {order_number}")
            return True, order_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione ordine: {e}")
            return False, str(e)
    
    def _generate_order_number(self) -> str:
        """Genera un numero ordine unico"""
        today = date.today()
        prefix = f"ORD{today.strftime('%Y%m%d')}"
        
        query = "SELECT COUNT(*) FROM customer_orders WHERE order_number LIKE ?"
        count = self.execute_query(query, (f"{prefix}%",), "one")[0]
        
        return f"{prefix}{count + 1:04d}"
    
    def create_sale(self, sale_data: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """Crea una nuova vendita"""
        try:
            # Genera numero vendita unico
            sale_number = self._generate_sale_number()
            
            query = """
                INSERT INTO sales (sale_number, order_id, customer_id, total_amount,
                                 discount_amount, tax_amount, final_amount,
                                 payment_method, payment_status, cashier_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                sale_number,
                sale_data.get('order_id'),
                sale_data.get('customer_id'),
                sale_data['total_amount'],
                sale_data.get('discount_amount', 0.0),
                sale_data.get('tax_amount', 0.0),
                sale_data['final_amount'],
                sale_data['payment_method'],
                sale_data.get('payment_status', 'paid'),
                sale_data['cashier_id'],
                sale_data.get('notes', '')
            )
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            sale_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Vendita creata: {sale_number}")
            return True, sale_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione vendita: {e}")
            return False, str(e)
    
    def _generate_sale_number(self) -> str:
        """Genera un numero vendita unico"""
        today = date.today()
        prefix = f"SALE{today.strftime('%Y%m%d')}"
        
        query = "SELECT COUNT(*) FROM sales WHERE sale_number LIKE ?"
        count = self.execute_query(query, (f"{prefix}%",), "one")[0]
        
        return f"{prefix}{count + 1:04d}"
    
    # ===== ANALYTICS E STATISTICHE =====
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ottiene le statistiche per la dashboard"""
        try:
            stats = {}
            
            # Vendite oggi
            query = """
                SELECT COUNT(*) as count, COALESCE(SUM(final_amount), 0) as total
                FROM sales WHERE DATE(sale_date) = DATE('now')
            """
            result = self.execute_query(query, fetch="one")
            stats['sales_today'] = {
                'count': result[0],
                'total': float(result[1])
            }
            
            # Ordini oggi
            query = """
                SELECT COUNT(*) as count, COALESCE(SUM(final_amount), 0) as total
                FROM customer_orders WHERE DATE(order_date) = DATE('now')
            """
            result = self.execute_query(query, fetch="one")
            stats['orders_today'] = {
                'count': result[0],
                'total': float(result[1])
            }
            
            # Clienti totali
            query = "SELECT COUNT(*) FROM customers WHERE is_active = 1"
            result = self.execute_query(query, fetch="one")
            stats['total_customers'] = result[0]
            
            # Prodotti totali
            query = "SELECT COUNT(*) FROM products WHERE is_active = 1"
            result = self.execute_query(query, fetch="one")
            stats['total_products'] = result[0]
            
            # Prodotti con scorte basse
            low_stock_products = self.get_products_low_stock()
            stats['low_stock_count'] = len(low_stock_products)
            
            # Prodotti in scadenza
            expiring_products = self.get_products_expiring_soon()
            stats['expiring_count'] = len(expiring_products)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento statistiche dashboard: {e}")
            return {}
    
    def get_sales_by_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Ottiene le vendite per periodo"""
        query = """
            SELECT DATE(sale_date) as sale_day,
                   COUNT(*) as total_sales,
                   SUM(final_amount) as total_revenue,
                   AVG(final_amount) as average_sale_value,
                   COUNT(DISTINCT customer_id) as unique_customers
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY DATE(sale_date)
            ORDER BY sale_day
        """
        
        results = self.execute_query(query, (start_date, end_date))
        sales = []
        
        for result in results:
            sales.append({
                'date': result[0],
                'total_sales': result[1],
                'total_revenue': float(result[2]),
                'average_sale_value': float(result[3]),
                'unique_customers': result[4]
            })
        
        return sales
    
    def get_top_products(self, limit: int = 10, period_days: int = 30) -> List[Dict[str, Any]]:
        """Ottiene i prodotti più venduti"""
        query = """
            SELECT p.id, p.name, p.code, pc.name as category_name,
                   SUM(si.quantity) as total_quantity,
                   SUM(si.total_price) as total_revenue,
                   COUNT(DISTINCT s.id) as sale_count
            FROM products p
            JOIN sale_items si ON p.id = si.product_id
            JOIN sales s ON si.sale_id = s.id
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            WHERE s.sale_date >= date('now', '-{} days')
            GROUP BY p.id, p.name, p.code, pc.name
            ORDER BY total_quantity DESC
            LIMIT ?
        """.format(period_days)
        
        results = self.execute_query(query, (limit,))
        products = []
        
        for result in results:
            products.append({
                'id': result[0],
                'name': result[1],
                'code': result[2],
                'category_name': result[3],
                'total_quantity': result[4],
                'total_revenue': float(result[5]),
                'sale_count': result[6]
            })
        
        return products
    
    # ===== GESTIONE CATEGORIE E UNITÀ =====
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """Ottiene tutte le categorie prodotti"""
        query = """
            SELECT id, name, parent_id, color, description, sort_order, is_active
            FROM product_categories
            WHERE is_active = 1
            ORDER BY sort_order, name
        """
        
        results = self.execute_query(query)
        categories = []
        
        for result in results:
            categories.append({
                'id': result[0],
                'name': result[1],
                'parent_id': result[2],
                'color': result[3],
                'description': result[4],
                'sort_order': result[5],
                'is_active': result[6]
            })
        
        return categories
    
    def get_units_of_measure(self) -> List[Dict[str, Any]]:
        """Ottiene tutte le unità di misura"""
        query = """
            SELECT id, name, symbol, type, conversion_factor, is_base_unit
            FROM units_of_measure
            ORDER BY type, name
        """
        
        results = self.execute_query(query)
        units = []
        
        for result in results:
            units.append({
                'id': result[0],
                'name': result[1],
                'symbol': result[2],
                'type': result[3],
                'conversion_factor': result[4],
                'is_base_unit': result[5]
            })
        
        return units
    
    def get_user_roles(self) -> List[Dict[str, Any]]:
        """Ottiene tutti i ruoli utente"""
        query = """
            SELECT id, name, display_name, permissions, description
            FROM user_roles
            ORDER BY name
        """
        
        results = self.execute_query(query)
        roles = []
        
        for result in results:
            roles.append({
                'id': result[0],
                'name': result[1],
                'display_name': result[2],
                'permissions': json.loads(result[3]) if result[3] else [],
                'description': result[4]
            })
        
        return roles
    
    # ===== UTILITY E HELPER =====
    
    def test_connection(self) -> bool:
        """Testa la connessione al database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Errore test connessione: {e}")
            return False
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Crea un backup del database"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"macelleria_backup_{timestamp}.db"
            
            # Copia il database
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"✅ Backup creato: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore creazione backup: {e}")
            return False
    
    def log_activity(self, user_id: int, action: str, entity_type: str = None, 
                    entity_id: int = None, details: str = None, ip_address: str = None):
        """Registra un'attività nel log"""
        try:
            query = """
                INSERT INTO activity_log (user_id, action, entity_type, entity_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (user_id, action, entity_type, entity_id, details, ip_address)
            self.execute_query(query, params, "none")
            
        except Exception as e:
            logger.error(f"❌ Errore registrazione attività: {e}")

# ===== ISTANZA GLOBALE =====

# Istanza globale del database manager
db_manager = MacelleriaDatabaseManager()

# Funzioni di convenienza per compatibilità
def get_db_manager() -> MacelleriaDatabaseManager:
    """Ottiene l'istanza globale del database manager"""
    return db_manager

def init_database():
    """Inizializza il database"""
    db_manager.init_database()

def test_database_connection() -> bool:
    """Testa la connessione al database"""
    return db_manager.test_connection()

if __name__ == "__main__":
    # Test del database manager
    print("🧪 Test Database Manager Macelleria")
    
    # Test connessione
    if test_database_connection():
        print("✅ Connessione database OK")
    else:
        print("❌ Errore connessione database")
        exit(1)
    
    # Test statistiche
    stats = db_manager.get_dashboard_stats()
    print(f"📊 Statistiche dashboard: {stats}")
    
    # Test categorie
    categories = db_manager.get_product_categories()
    print(f"🏷️ Categorie prodotti: {len(categories)} trovate")
    
    # Test unità di misura
    units = db_manager.get_units_of_measure()
    print(f"📏 Unità di misura: {len(units)} trovate")
    
    print("✅ Test completato con successo!")
