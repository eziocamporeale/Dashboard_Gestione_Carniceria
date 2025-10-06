#!/usr/bin/env python3
"""
Hybrid Database Manager per Dashboard Gestión Carnicería
Supporta sia Supabase che SQLite come fallback
Creato da Ezio Camporeale
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import sys
from pathlib import Path
import atexit
import weakref

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

# Import condizionali per evitare errori
try:
    from database.supabase_manager import SupabaseManager
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Supabase non disponibile: {e}")
    SUPABASE_AVAILABLE = False
    SupabaseManager = None

try:
    from database.database_manager_simple import SimpleDatabaseManager
    SQLITE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ SimpleDatabaseManager non disponibile: {e}")
    SQLITE_AVAILABLE = False
    SimpleDatabaseManager = None

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridDatabaseManager:
    """Gestore database ibrido: Supabase principale, SQLite fallback"""
    
    # Singleton pattern per evitare multiple istanze
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HybridDatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inizializza il gestore ibrido"""
        if self._initialized:
            return
            
        if SUPABASE_AVAILABLE and SupabaseManager:
            self.supabase_manager = SupabaseManager()
            self.use_supabase = self.supabase_manager.is_connected()
        else:
            self.supabase_manager = None
            self.use_supabase = False
            
        # Registra cleanup automatico
        atexit.register(self.cleanup)
        weakref.finalize(self, self.cleanup)
        
        self._initialized = True
            
        if SQLITE_AVAILABLE and SimpleDatabaseManager:
            self.sqlite_manager = SimpleDatabaseManager()
        else:
            self.sqlite_manager = None
            logger.error("❌ Nessun gestore di database disponibile!")
            raise Exception("Impossibile inizializzare alcun gestore di database")
        
        if self.use_supabase:
            logger.info("✅ Usando Supabase come database principale")
        else:
            logger.info("⚠️ Supabase non disponibile, usando SQLite come fallback")
    
    def _get_manager(self):
        """Ottiene il manager attivo (Supabase o SQLite)"""
        if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
            return self.supabase_manager
        else:
            return self.sqlite_manager
    
    def is_supabase_active(self) -> bool:
        """Verifica se Supabase è attivo"""
        return self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected()
    
    def switch_to_sqlite(self):
        """Forza l'uso di SQLite"""
        self.use_supabase = False
        logger.info("🔄 Switched to SQLite fallback")
    
    def switch_to_supabase(self):
        """Forza l'uso di Supabase"""
        if self.supabase_manager.is_connected():
            self.use_supabase = True
            logger.info("🔄 Switched to Supabase")
        else:
            logger.warning("⚠️ Supabase non disponibile, rimanendo su SQLite")
    
    # ==================== METODI DASHBOARD ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche dashboard"""
        try:
            manager = self._get_manager()
            return manager.get_dashboard_stats()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo statistiche dashboard: {e}")
            return {}
    
    def get_products_low_stock(self) -> List[Dict]:
        """Ottiene prodotti con stock basso"""
        try:
            manager = self._get_manager()
            return manager.get_products_low_stock()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti stock basso: {e}")
            return []
    
    def get_products_expiring_soon(self) -> List[Dict]:
        """Ottiene prodotti in scadenza"""
        try:
            manager = self._get_manager()
            return manager.get_products_expiring_soon()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti in scadenza: {e}")
            return []
    
    def get_product_categories(self) -> List[Dict]:
        """Ottiene categorie prodotti"""
        try:
            manager = self._get_manager()
            return manager.get_product_categories()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo categorie: {e}")
            return []
    
    def get_units_of_measure(self) -> List[Dict]:
        """Ottiene unità di misura"""
        try:
            manager = self._get_manager()
            return manager.get_units_of_measure()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo unità di misura: {e}")
            return []
    
    def get_sales_by_period(self, start_date=None, end_date=None, period: str = 'month') -> List[Dict]:
        """Ottiene vendite per periodo - compatibile con entrambe le firme"""
        try:
            manager = self._get_manager()
            
            # Se sono stati passati start_date e end_date, usa quella firma
            if start_date is not None and end_date is not None:
                if hasattr(manager, 'get_sales_by_period') and manager.get_sales_by_period.__code__.co_argcount >= 3:
                    return manager.get_sales_by_period(start_date, end_date)
                else:
                    # Fallback: usa il periodo
                    return manager.get_sales_by_period(period)
            else:
                # Usa la firma con periodo
                return manager.get_sales_by_period(period)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per periodo: {e}")
            return []
    
    def get_customers(self) -> List[Dict]:
        """Ottiene clienti"""
        try:
            manager = self._get_manager()
            return manager.get_customers()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo clienti: {e}")
            return []
    
    def get_products(self) -> List[Dict]:
        """Ottiene prodotti"""
        try:
            manager = self._get_manager()
            return manager.get_products()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti: {e}")
            return []
    
    def get_recent_orders(self) -> List[Dict]:
        """Ottiene ordini recenti"""
        try:
            manager = self._get_manager()
            return manager.get_recent_orders()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo ordini recenti: {e}")
            return []
    
    def get_top_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            manager = self._get_manager()
            return manager.get_top_products(limit=limit)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo top prodotti: {e}")
            return []
    
    def get_top_customers(self, limit: int = 5) -> List[Dict]:
        """Ottiene clienti migliori"""
        try:
            manager = self._get_manager()
            return manager.get_top_customers(limit=limit)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo top clienti: {e}")
            return []
    
    def get_monthly_revenue(self, months: int = 6) -> List[Dict]:
        """Ottiene ricavi mensili"""
        try:
            manager = self._get_manager()
            return manager.get_monthly_revenue(months=months)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo ricavi mensili: {e}")
            return []
    
    def get_daily_sales(self, days: int = 7) -> List[Dict]:
        """Ottiene vendite giornaliere"""
        try:
            manager = self._get_manager()
            return manager.get_daily_sales(days=days)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite giornaliere: {e}")
            return []
    
    def get_suppliers(self) -> List[Dict]:
        """Ottiene fornitori"""
        try:
            manager = self._get_manager()
            return manager.get_suppliers()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo fornitori: {e}")
            return []
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Ottiene riepilogo inventario"""
        try:
            manager = self._get_manager()
            return manager.get_inventory_summary()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo inventario: {e}")
            return {}
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Ottiene riepilogo finanziario"""
        try:
            manager = self._get_manager()
            return manager.get_financial_summary()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo finanziario: {e}")
            return {}
    
    # ==================== METODI EXCEL ====================
    
    def save_excel_data(self, data: Dict) -> bool:
        """Salva dati Excel"""
        try:
            manager = self._get_manager()
            return manager.save_excel_data(data)
        except Exception as e:
            logger.error(f"❌ Errore salvando dati Excel: {e}")
            return False
    
    def get_excel_data_summary(self) -> List[Dict]:
        """Ottiene riepilogo dati Excel"""
        try:
            manager = self._get_manager()
            return manager.get_excel_data_summary()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo Excel: {e}")
            return []
    
    def get_saved_excel_data(self) -> List[Dict]:
        """Ottiene dati Excel salvati"""
        try:
            manager = self._get_manager()
            return manager.get_saved_excel_data()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati Excel salvati: {e}")
            return []
    
    # ==================== METODI VENDITE ====================
    
    def get_sales_summary(self) -> Dict[str, Any]:
        """Ottiene riepilogo vendite"""
        try:
            manager = self._get_manager()
            return manager.get_sales_summary()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo vendite: {e}")
            return {}
    
    def get_daily_sales_data(self, days: int = 30) -> List[Dict]:
        """Ottiene dati vendite giornaliere"""
        try:
            manager = self._get_manager()
            return manager.get_daily_sales_data(days)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati vendite giornaliere: {e}")
            return []
    
    def get_sales_by_category(self) -> List[Dict]:
        """Ottiene vendite per categoria"""
        try:
            manager = self._get_manager()
            return manager.get_sales_by_category()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per categoria: {e}")
            return []
    
    def get_top_selling_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            manager = self._get_manager()
            return manager.get_top_selling_products(limit)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti più venduti: {e}")
            return []
    
    def get_sales_forecast(self, months: int = 6) -> List[Dict]:
        """Ottiene proiezione vendite"""
        try:
            manager = self._get_manager()
            return manager.get_sales_forecast(months)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo proiezione vendite: {e}")
            return []
    
    def get_sales_team_performance(self) -> List[Dict]:
        """Ottiene performance team vendite"""
        try:
            manager = self._get_manager()
            return manager.get_sales_team_performance()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo performance team: {e}")
            return []
    
    # ==================== METODI PRODOTTI ====================
    
    def get_all_products(self) -> List[Dict]:
        """Ottiene tutti i prodotti"""
        try:
            manager = self._get_manager()
            return manager.get_all_products()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo tutti i prodotti: {e}")
            return []
    
    def get_all_suppliers(self) -> List[Dict]:
        """Ottiene tutti i fornitori"""
        try:
            manager = self._get_manager()
            return manager.get_all_suppliers()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo tutti i fornitori: {e}")
            return []
    
    def get_all_customers(self) -> List[Dict]:
        """Ottiene tutti i clienti"""
        try:
            manager = self._get_manager()
            return manager.get_all_customers()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo tutti i clienti: {e}")
            return []
    
    def create_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Crea un nuevo cliente"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                return self.supabase_manager.create_customer(customer_data)
            else:
                if hasattr(self.sqlite_manager, 'create_customer'):
                    return self.sqlite_manager.create_customer(customer_data)
                else:
                    logger.error("❌ Metodo create_customer non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore creando cliente: {e}")
            return False
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Actualiza un cliente existente"""
        try:
            manager = self._get_manager()
            return manager.update_customer(customer_id, customer_data)
        except Exception as e:
            logger.error(f"❌ Errore actualizando cliente {customer_id}: {e}")
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Elimina un cliente"""
        try:
            manager = self._get_manager()
            return manager.delete_customer(customer_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando cliente {customer_id}: {e}")
            return False
    
    # ==================== METODOS CRM ====================
    
    def get_customer_interactions(self, customer_id: int) -> List[Dict]:
        """Obtiene el historial de interacciones de un cliente"""
        try:
            manager = self._get_manager()
            return manager.get_customer_interactions(customer_id)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo interacciones del cliente {customer_id}: {e}")
            return []
    
    def add_customer_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Añade una nueva interacción con el cliente"""
        try:
            manager = self._get_manager()
            return manager.add_customer_interaction(interaction_data)
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo interazione: {e}")
            return False
    
    def get_customer_segments(self) -> List[Dict]:
        """Obtiene segmentos de clientes"""
        try:
            manager = self._get_manager()
            return manager.get_customer_segments()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo segmenti: {e}")
            return []
    
    def get_customer_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de clientes"""
        try:
            manager = self._get_manager()
            return manager.get_customer_analytics()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo analytics: {e}")
            return {}
    
    def get_marketing_campaigns(self) -> List[Dict]:
        """Obtiene campañas de marketing"""
        try:
            manager = self._get_manager()
            return manager.get_marketing_campaigns()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo campagne: {e}")
            return []
    
    def get_customer_predictions(self) -> List[Dict]:
        """Obtiene predicciones de clientes"""
        try:
            manager = self._get_manager()
            return manager.get_customer_predictions()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo predizioni: {e}")
            return []
    
    # ==================== METODOS PROVEEDORES CRUD ====================
    
    def create_supplier(self, supplier_data: Dict[str, Any]) -> bool:
        """Crea un nuevo proveedor"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                return self.supabase_manager.create_supplier(supplier_data)
            else:
                if hasattr(self.sqlite_manager, 'create_supplier'):
                    return self.sqlite_manager.create_supplier(supplier_data)
                else:
                    logger.error("❌ Metodo create_supplier non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore creando proveedor: {e}")
            return False
    
    def update_supplier(self, supplier_id: int, supplier_data: Dict[str, Any]) -> bool:
        """Actualiza un proveedor existente"""
        try:
            manager = self._get_manager()
            return manager.update_supplier(supplier_id, supplier_data)
        except Exception as e:
            logger.error(f"❌ Errore actualizando proveedor {supplier_id}: {e}")
            return False
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Elimina un proveedor"""
        try:
            manager = self._get_manager()
            return manager.delete_supplier(supplier_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando proveedor {supplier_id}: {e}")
            return False
    
    # ==================== METODOS ORDERS CRUD ====================
    
    def create_order(self, order_data: Dict[str, Any]) -> bool:
        """Crea un nuevo pedido"""
        try:
            manager = self._get_manager()
            return manager.create_order(order_data)
        except Exception as e:
            logger.error(f"❌ Errore creando pedido: {e}")
            return False
    
    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> bool:
        """Actualiza un pedido existente"""
        try:
            manager = self._get_manager()
            return manager.update_order(order_id, order_data)
        except Exception as e:
            logger.error(f"❌ Errore actualizando pedido {order_id}: {e}")
            return False
    
    def delete_order(self, order_id: int) -> bool:
        """Elimina un pedido"""
        try:
            manager = self._get_manager()
            return manager.delete_order(order_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando pedido {order_id}: {e}")
            return False
    
    def get_supplier_orders(self) -> List[Dict]:
        """Obtiene todos los pedidos de proveedores"""
        try:
            manager = self._get_manager()
            return manager.get_supplier_orders()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo pedidos de proveedores: {e}")
            return []
    
    # ==================== METODOS INVENTARIO CRUD ====================
    
    def create_product(self, product_data: Dict[str, Any]) -> bool:
        """Crea un nuevo producto"""
        try:
            manager = self._get_manager()
            return manager.create_product(product_data)
        except Exception as e:
            logger.error(f"❌ Errore creando producto: {e}")
            return False
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Actualiza un producto existente"""
        try:
            manager = self._get_manager()
            return manager.update_product(product_id, product_data)
        except Exception as e:
            logger.error(f"❌ Errore actualizando producto {product_id}: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto"""
        try:
            manager = self._get_manager()
            return manager.delete_product(product_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando producto {product_id}: {e}")
            return False
    
    # ==================== METODOS VENTAS CRUD ====================
    
    def create_sale(self, sale_data: Dict[str, Any]) -> bool:
        """Crea una nueva venta"""
        try:
            manager = self._get_manager()
            return manager.create_sale(sale_data)
        except Exception as e:
            logger.error(f"❌ Errore creando venta: {e}")
            return False
    
    def update_sale(self, sale_id: int, sale_data: Dict[str, Any]) -> bool:
        """Actualiza una venta existente"""
        try:
            manager = self._get_manager()
            return manager.update_sale(sale_id, sale_data)
        except Exception as e:
            logger.error(f"❌ Errore actualizando venta {sale_id}: {e}")
            return False
    
    def delete_sale(self, sale_id: int) -> bool:
        """Elimina una venta"""
        try:
            manager = self._get_manager()
            return manager.delete_sale(sale_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando venta {sale_id}: {e}")
            return False
    
    def get_all_sales(self) -> List[Dict]:
        """Obtiene todas las ventas individuales"""
        try:
            manager = self._get_manager()
            return manager.get_all_sales()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo tutte le vendite: {e}")
            return []
    
    # ==================== CRUD USUARIOS ====================
    
    def get_all_users(self) -> List[Dict]:
        """Ottiene tutti gli utenti"""
        try:
            manager = self._get_manager()
            return manager.get_all_users()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo utenti: {e}")
            return []
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Crea un nuovo utente"""
        try:
            manager = self._get_manager()
            return manager.create_user(user_data)
        except Exception as e:
            logger.error(f"❌ Errore creando utente: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Aggiorna un utente esistente"""
        try:
            manager = self._get_manager()
            return manager.update_user(user_id, user_data)
        except Exception as e:
            logger.error(f"❌ Errore aggiornando utente: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Elimina un utente (soft delete)"""
        try:
            manager = self._get_manager()
            return manager.delete_user(user_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando utente: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Ottiene un utente per ID"""
        try:
            manager = self._get_manager()
            return manager.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo utente {user_id}: {e}")
            return None
    
    def get_all_roles(self) -> List[Dict]:
        """Ottiene tutti i ruoli"""
        try:
            manager = self._get_manager()
            return manager.get_all_roles()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo ruoli: {e}")
            return []
    
    # ==================== GESTORE CONTABILITÀ GIORNALIERA ====================
    
    def add_daily_income(self, amount: float, category: str, description: str = "", payment_method: str = "Efectivo", date: str = None) -> Optional[Dict]:
        """Aggiunge un'entrata giornaliera"""
        try:
            manager = self._get_manager()
            return manager.add_daily_income(amount, category, description, payment_method, date)
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo entrata: {e}")
            return None
    
    def add_daily_expense(self, amount: float, category: str, description: str = "", supplier: str = "", payment_method: str = "Efectivo", date: str = None) -> Optional[Dict]:
        """Aggiunge un'uscita giornaliera"""
        try:
            manager = self._get_manager()
            return manager.add_daily_expense(amount, category, description, supplier, payment_method, date)
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo uscita: {e}")
            return None
    
    def get_daily_entries(self, date: str = None) -> Dict:
        """Ottiene tutte le entrate e uscite di un giorno"""
        try:
            manager = self._get_manager()
            return manager.get_daily_entries(date)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo entrate giornaliere: {e}")
            return {'date': date, 'income': [], 'expenses': [], 'total_income': 0, 'total_expenses': 0}
    
    def get_daily_report(self, date: str = None) -> Dict:
        """Ottiene il report giornaliero calcolato"""
        try:
            manager = self._get_manager()
            return manager.get_daily_report(date)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo report giornaliero: {e}")
            return {}
    
    def get_accounting_categories(self, category_type: str = None) -> List[Dict]:
        """Ottiene le categorie di contabilità"""
        try:
            manager = self._get_manager()
            return manager.get_accounting_categories(category_type)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo categorie: {e}")
            return []
    
    def add_accounting_category(self, name: str, category_type: str, color: str = "#636EFA", icon: str = "💰") -> Optional[Dict]:
        """Aggiunge una nuova categoria"""
        try:
            manager = self._get_manager()
            return manager.add_accounting_category(name, category_type, color, icon)
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo categoria: {e}")
            return None
    
    def get_weekly_summary(self, start_date: str = None) -> List[Dict]:
        """Ottiene riepilogo settimanale"""
        try:
            manager = self._get_manager()
            return manager.get_weekly_summary(start_date)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo settimanale: {e}")
            return []
    
    def get_monthly_summary(self, year: int = None, month: int = None) -> Dict:
        """Ottiene riepilogo mensile"""
        try:
            manager = self._get_manager()
            return manager.get_monthly_summary(year, month)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo mensile: {e}")
            return {}
    
    def delete_daily_entry(self, entry_type: str, entry_id: str) -> bool:
        """Elimina un'entrata o uscita giornaliera"""
        try:
            manager = self._get_manager()
            return manager.delete_daily_entry(entry_type, entry_id)
        except Exception as e:
            logger.error(f"❌ Errore eliminando {entry_type}: {e}")
            return False
    
    # ==================== GESTORE CONTABILITÀ (LEGACY) ====================
    
    def get_financial_summary(self, start_date=None, end_date=None) -> Dict:
        """Ottiene riepilogo finanziario (entrate e uscite)"""
        try:
            manager = self._get_manager()
            return manager.get_financial_summary(start_date, end_date)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo finanziario: {e}")
            return {}
    
    def get_monthly_financial_data(self, months: int = 12) -> List[Dict]:
        """Ottiene dati finanziari mensili"""
        try:
            manager = self._get_manager()
            return manager.get_monthly_financial_data(months)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati finanziari mensili: {e}")
            return []
    
    def get_expense_categories(self) -> List[Dict]:
        """Ottiene categorie di spese"""
        try:
            manager = self._get_manager()
            return manager.get_expense_categories()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo categorie spese: {e}")
            return []
    
    def get_income_trends(self, days: int = 30) -> List[Dict]:
        """Ottiene tendenze delle entrate"""
        try:
            manager = self._get_manager()
            return manager.get_income_trends(days)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo tendenze entrate: {e}")
            return []
    
    def get_financial_forecast(self, months: int = 6) -> List[Dict]:
        """Ottiene previsioni finanziarie"""
        try:
            manager = self._get_manager()
            return manager.get_financial_forecast(months)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo previsioni finanziarie: {e}")
            return []
    
    def get_daily_sales_data(self, days: int = 30) -> List[Dict]:
        """Ottiene dati vendite giornaliere"""
        try:
            manager = self._get_manager()
            return manager.get_daily_sales_data(days)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati vendite giornaliere: {e}")
            return []
    
    def get_sales_by_category(self) -> List[Dict]:
        """Ottiene vendite per categoria"""
        try:
            manager = self._get_manager()
            return manager.get_sales_by_category()
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per categoria: {e}")
            return []
    
    def get_top_selling_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            manager = self._get_manager()
            return manager.get_top_selling_products(limit)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti più venduti: {e}")
            return []
    
    # ==================== METODI UTILITÀ ====================
    
    def get_database_info(self) -> Dict[str, Any]:
        """Ottiene informazioni database"""
        return {
            'active_database': 'Supabase' if self.is_supabase_active() else 'SQLite',
            'supabase_connected': self.supabase_manager.is_connected(),
            'sqlite_available': True,
            'last_check': datetime.now().isoformat()
        }
    
    def test_connection(self) -> bool:
        """Testa la connessione database"""
        try:
            manager = self._get_manager()
            if hasattr(manager, 'test_connection'):
                return manager.test_connection()
            else:
                # Per SQLite, test semplice
                stats = manager.get_dashboard_stats()
                return bool(stats)
        except Exception as e:
            logger.error(f"❌ Errore test connessione: {e}")
            return False

    def authenticate_user(self, username: str, password: str):
        """Autentica un utente"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Per Supabase, usa email invece di username
                # Se username è "admin", convertilo in email
                if username == "admin":
                    email = "admin@carniceria.com"
                else:
                    email = username  # Assume che sia già un email
                return self.supabase_manager.authenticate_user(email, password)
            else:
                return self.sqlite_manager.authenticate_user(username, password)
        except Exception as e:
            logger.error(f"❌ Errore durante autenticazione: {e}")
            return None
    
    def log_activity(self, user_id: str, action: str, details: str, ip_address: str = None):
        """Log dell'attività utente"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Per Supabase, usa il metodo log_activity se disponibile
                if hasattr(self.supabase_manager, 'log_activity'):
                    return self.supabase_manager.log_activity(user_id, action, details, ip_address)
                else:
                    # Implementazione semplificata per Supabase
                    activity_data = {
                        'user_id': user_id,
                        'activity_type': action,
                        'description': details,
                        'ip_address': ip_address
                    }
                    return self.supabase_manager.insert('activity_log', activity_data)
            else:
                # Per SQLite, usa il metodo del SimpleDatabaseManager
                return self.sqlite_manager.log_activity(user_id, action, details, ip_address)
        except Exception as e:
            logger.error(f"❌ Errore durante log attività: {e}")
            return None

    def add_employee(self, employee_data: Dict[str, Any]) -> bool:
        """Aggiunge un nuovo impiegato"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Per Supabase
                response = self.supabase_manager.client.table('employees').insert(employee_data).execute()
                return response.data is not None
            else:
                # Per SQLite
                if hasattr(self.sqlite_manager, 'add_employee'):
                    return self.sqlite_manager.add_employee(employee_data)
                else:
                    logger.error("❌ Metodo add_employee non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo impiegato: {e}")
            return False

    def select(self, table_name: str, filters: dict = None) -> List[Dict[str, Any]]:
        """Seleziona record da una tabella"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Per Supabase
                query = self.supabase_manager.client.table(table_name).select('*')
                
                # Applica filtri se specificati
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                
                response = query.execute()
                return response.data or []
            else:
                # Per SQLite
                if hasattr(self.sqlite_manager, 'select'):
                    return self.sqlite_manager.select(table_name, filters) or []
                else:
                    logger.error(f"❌ Metodo select non disponibile per SQLite")
                    return []
        except Exception as e:
            logger.error(f"❌ Errore durante selezione da {table_name}: {e}")
            return []

    def execute_sql(self, sql: str) -> bool:
        """Esegue uno script SQL"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Per Supabase, usa l'endpoint SQL
                response = self.supabase_manager.client.post('/rest/v1/rpc/exec', {
                    'sql': sql
                }).execute()
                return True
            else:
                logger.error("❌ Esecuzione SQL non disponibile per SQLite")
                return False
        except Exception as e:
            logger.error(f"❌ Errore esecuzione SQL: {e}")
            return False
    
    # ==================== METODOS EMPLEADOS CRUD ====================
    
    def add_employee(self, employee_data: Dict[str, Any]) -> bool:
        """Aggiunge un nuovo impiegato"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                response = self.supabase_manager.client.table('employees').insert(employee_data).execute()
                return response.data is not None
            else:
                if hasattr(self.sqlite_manager, 'add_employee'):
                    return self.sqlite_manager.add_employee(employee_data)
                else:
                    logger.error("❌ Metodo add_employee non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore aggiungendo impiegato: {e}")
            return False
    
    def update_employee(self, employee_id: str, employee_data: Dict[str, Any]) -> bool:
        """Aggiorna un impiegato esistente"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                response = self.supabase_manager.client.table('employees').update(employee_data).eq('id', employee_id).execute()
                return response.data is not None
            else:
                if hasattr(self.sqlite_manager, 'update_employee'):
                    return self.sqlite_manager.update_employee(employee_id, employee_data)
                else:
                    logger.error("❌ Metodo update_employee non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore aggiornando impiegato: {e}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """Elimina un impiegato"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                response = self.supabase_manager.client.table('employees').delete().eq('id', employee_id).execute()
                return True  # Supabase restituisce sempre successo anche se non trova il record
            else:
                if hasattr(self.sqlite_manager, 'delete_employee'):
                    return self.sqlite_manager.delete_employee(employee_id)
                else:
                    logger.error("❌ Metodo delete_employee non disponibile per SQLite")
                    return False
        except Exception as e:
            logger.error(f"❌ Errore eliminando impiegato: {e}")
            return False
    
    def get_employee(self, employee_id: str) -> Dict[str, Any]:
        """Ottiene un impiegato specifico"""
        try:
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                response = self.supabase_manager.client.table('employees').select('*').eq('id', employee_id).execute()
                return response.data[0] if response.data else {}
            else:
                if hasattr(self.sqlite_manager, 'get_employee'):
                    return self.sqlite_manager.get_employee(employee_id)
                else:
                    logger.error("❌ Metodo get_employee non disponibile per SQLite")
                    return {}
        except Exception as e:
            logger.error(f"❌ Errore ottenendo impiegato: {e}")
            return {}

    def get_monthly_transactions(self, year: int, month: int) -> Dict[str, List[Dict[str, Any]]]:
        """Ottiene tutte le transazioni di un mese specifico"""
        try:
            # Formatta le date per il mese
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            monthly_income = []
            monthly_expenses = []
            
            if self.use_supabase and self.supabase_manager and self.supabase_manager.is_connected():
                # Query Supabase per entrate del mese
                try:
                    income_response = self.supabase_manager.client.table('daily_income').select('*').gte('date', start_date).lt('date', end_date).execute()
                    monthly_income = income_response.data or []
                except Exception as e:
                    logger.error(f"❌ Errore ottenendo entrate mensili: {e}")
                
                # Query Supabase per uscite del mese
                try:
                    expense_response = self.supabase_manager.client.table('daily_expenses').select('*').gte('date', start_date).lt('date', end_date).execute()
                    monthly_expenses = expense_response.data or []
                except Exception as e:
                    logger.error(f"❌ Errore ottenendo uscite mensili: {e}")
            else:
                # Fallback SQLite
                if hasattr(self.sqlite_manager, 'get_monthly_transactions'):
                    result = self.sqlite_manager.get_monthly_transactions(year, month)
                    monthly_income = result.get('income', [])
                    monthly_expenses = result.get('expenses', [])
                else:
                    logger.error("❌ Metodo get_monthly_transactions non disponibile per SQLite")
            
            return {
                'income': monthly_income,
                'expenses': monthly_expenses
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ottenendo transazioni mensili: {e}")
            return {'income': [], 'expenses': []}

    def get_weekly_summary(self, week_start_date: str) -> List[Dict[str, Any]]:
        """Ottiene il riepilogo settimanale per una settimana specifica"""
        try:
            from datetime import datetime, timedelta
            
            # Converte la data di inizio settimana
            start_date = datetime.fromisoformat(week_start_date).date()
            end_date = start_date + timedelta(days=6)
            
            weekly_data = []
            
            # Itera attraverso ogni giorno della settimana
            for i in range(7):
                current_date = start_date + timedelta(days=i)
                date_str = current_date.isoformat()
                
                # Ottieni le transazioni del giorno
                if hasattr(self, 'get_monthly_transactions'):
                    monthly_data = self.get_monthly_transactions(current_date.year, current_date.month)
                    
                    # Filtra per il giorno specifico
                    day_income = [t for t in monthly_data.get('income', []) if t.get('date', '').startswith(date_str)]
                    day_expenses = [t for t in monthly_data.get('expenses', []) if t.get('date', '').startswith(date_str)]
                    
                    # Calcola totali del giorno
                    total_income = sum([float(t.get('amount', 0)) for t in day_income])
                    total_expenses = sum([float(t.get('amount', 0)) for t in day_expenses])
                    net_profit = total_income - total_expenses
                    transactions_count = len(day_income) + len(day_expenses)
                    
                    # Calcola margine di profitto
                    profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
                    
                    daily_summary = {
                        'date': date_str,
                        'total_income': total_income,
                        'total_expenses': total_expenses,
                        'net_profit': net_profit,
                        'profit_margin': profit_margin,
                        'transactions_count': transactions_count
                    }
                    
                    weekly_data.append(daily_summary)
                else:
                    # Fallback se il metodo non esiste
                    daily_summary = {
                        'date': date_str,
                        'total_income': 0,
                        'total_expenses': 0,
                        'net_profit': 0,
                        'profit_margin': 0,
                        'transactions_count': 0
                    }
                    weekly_data.append(daily_summary)
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo settimanale: {e}")
            return []

    def cleanup(self):
        """Pulizia risorse e chiusura connessioni"""
        try:
            # Cleanup Supabase
            if hasattr(self, 'supabase_manager') and self.supabase_manager:
                if hasattr(self.supabase_manager, 'cleanup'):
                    self.supabase_manager.cleanup()
            
            # Cleanup SQLite
            if hasattr(self, 'sqlite_manager') and self.sqlite_manager:
                if hasattr(self.sqlite_manager, 'close'):
                    self.sqlite_manager.close()
                    
            logger.info("✅ Cleanup HybridDatabaseManager completato")
            
        except Exception as e:
            logger.error(f"❌ Errore durante cleanup HybridDatabaseManager: {e}")

    def get_connection_info(self) -> Dict[str, Any]:
        """Ottiene informazioni sulle connessioni"""
        info = {
            'use_supabase': self.use_supabase,
            'supabase_available': SUPABASE_AVAILABLE,
            'sqlite_available': SQLITE_AVAILABLE
        }
        
        if self.supabase_manager and hasattr(self.supabase_manager, 'get_connection_info'):
            info['supabase'] = self.supabase_manager.get_connection_info()
            
        return info

# Istanza globale

_hybrid_manager = None

def get_hybrid_manager() -> HybridDatabaseManager:
    """Ottiene l'istanza globale del gestore ibrido"""
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridDatabaseManager()
    return _hybrid_manager
