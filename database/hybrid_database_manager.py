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
    
    def __init__(self):
        """Inizializza il gestore ibrido"""
        if SUPABASE_AVAILABLE and SupabaseManager:
            self.supabase_manager = SupabaseManager()
            self.use_supabase = self.supabase_manager.is_connected()
        else:
            self.supabase_manager = None
            self.use_supabase = False
            
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
        """Crea un nuovo cliente"""
        try:
            manager = self._get_manager()
            return manager.create_customer(customer_data)
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
            manager = self._get_manager()
            return manager.create_supplier(supplier_data)
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

# Istanza globale

_hybrid_manager = None

def get_hybrid_manager() -> HybridDatabaseManager:
    """Ottiene l'istanza globale del gestore ibrido"""
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridDatabaseManager()
    return _hybrid_manager
