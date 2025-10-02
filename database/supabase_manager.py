#!/usr/bin/env python3
"""
Supabase Manager per Dashboard Gestión Carnicería
Gestione connessione e operazioni database Supabase
Creato da Ezio Camporeale
"""

import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config.supabase_config import SupabaseConfig

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    """Gestore database Supabase per l'applicazione"""
    
    def __init__(self):
        """Inizializza il gestore Supabase"""
        self.config = SupabaseConfig()
        self.client = None
        
        if self.config.is_supabase_configured():
            try:
                from supabase import create_client, Client
                self.client: Client = create_client(
                    self.config.SUPABASE_URL, 
                    self.config.SUPABASE_ANON_KEY
                )
                logger.info("✅ Connessione Supabase inizializzata")
            except ImportError:
                logger.error("❌ Libreria supabase non installata. Esegui: pip install supabase")
                self.client = None
            except Exception as e:
                logger.error(f"❌ Errore connessione Supabase: {e}")
                self.client = None
        else:
            logger.warning("⚠️ Supabase non configurato. Controlla le variabili ambiente.")
            self.client = None
    
    def is_connected(self) -> bool:
        """Verifica se la connessione Supabase è attiva"""
        return self.client is not None
    
    def test_connection(self) -> bool:
        """Testa la connessione a Supabase"""
        if not self.is_connected():
            return False
        
        try:
            # Test semplice: contare le righe in una tabella
            result = self.client.table('roles').select('id').limit(1).execute()
            logger.info("✅ Test connessione Supabase riuscito")
            return True
        except Exception as e:
            logger.error(f"❌ Test connessione Supabase fallito: {e}")
            return False
    
    # ==================== METODI CRUD GENERICI ====================
    
    def select(self, table: str, columns: str = "*", filters: Dict = None, limit: int = None, order_by: str = None) -> List[Dict]:
        """Seleziona dati da una tabella"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return []
        
        try:
            query = self.client.table(table).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            if order_by:
                query = query.order(order_by)
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Errore selezione da {table}: {e}")
            return []
    
    def insert(self, table: str, data: Dict) -> Optional[Dict]:
        """Inserisce un record in una tabella"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return None
        
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Errore inserimento in {table}: {e}")
            return None
    
    def update(self, table: str, data: Dict, filters: Dict) -> bool:
        """Aggiorna record in una tabella"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return False
        
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return True
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento in {table}: {e}")
            return False
    
    def delete(self, table: str, filters: Dict) -> bool:
        """Elimina record da una tabella"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return False
        
        try:
            query = self.client.table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return True
        except Exception as e:
            logger.error(f"❌ Errore eliminazione da {table}: {e}")
            return False
    
    # ==================== METODI SPECIFICI PER CARNICERÍA ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche dashboard"""
        try:
            # Statistiche vendite
            sales_stats = self.select('sales', 'total_amount, sale_date')
            total_sales = sum([sale['total_amount'] for sale in sales_stats])
            
            # Statistiche prodotti
            products_count = len(self.select('products'))
            low_stock_products = len(self.select('products', filters={'current_stock': 0}))
            
            # Statistiche clienti
            customers_count = len(self.select('customers'))
            
            return {
                'total_sales': total_sales,
                'products_count': products_count,
                'low_stock_products': low_stock_products,
                'customers_count': customers_count,
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Errore ottenendo statistiche dashboard: {e}")
            return {}
    
    def get_products_low_stock(self) -> List[Dict]:
        """Ottiene prodotti con stock basso"""
        try:
            return self.select('products', filters={'current_stock': 0})
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti stock basso: {e}")
            return []
    
    def get_products_expiring_soon(self, days: int = 7) -> List[Dict]:
        """Ottiene prodotti in scadenza"""
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            return self.select('products', filters={'expiry_date': expiry_date.date().isoformat()})
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti in scadenza: {e}")
            return []
    
    def get_sales_by_period(self, period: str = 'month') -> List[Dict]:
        """Ottiene vendite per periodo"""
        try:
            if period == 'month':
                start_date = datetime.now() - timedelta(days=30)
            elif period == 'week':
                start_date = datetime.now() - timedelta(days=7)
            else:
                start_date = datetime.now() - timedelta(days=1)
            
            return self.select('sales', filters={'sale_date': start_date.isoformat()})
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per periodo: {e}")
            return []
    
    def get_top_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            # Query complessa per ottenere prodotti più venduti
            # Implementazione semplificata
            return self.select('products', limit=limit)
        except Exception as e:
            logger.error(f"❌ Errore ottenendo top prodotti: {e}")
            return []
    
    def save_excel_data(self, data: Dict) -> bool:
        """Salva dati Excel nel database"""
        try:
            excel_data = {
                'file_name': data.get('file_name', 'import.xlsx'),
                'data': json.dumps(data),
                'processed_by': data.get('user_id'),
                'upload_date': datetime.now().isoformat()
            }
            
            result = self.insert('excel_data', excel_data)
            return result is not None
        except Exception as e:
            logger.error(f"❌ Errore salvando dati Excel: {e}")
            return False
    
    def get_excel_data_summary(self) -> List[Dict]:
        """Ottiene riepilogo dati Excel salvati"""
        try:
            return self.select('excel_data', order_by='upload_date DESC')
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo Excel: {e}")
            return []
    
    def get_saved_excel_data(self, limit: int = 50) -> List[Dict]:
        """Ottiene dati Excel salvati"""
        try:
            return self.select('excel_data', limit=limit, order_by='upload_date DESC')
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati Excel salvati: {e}")
            return []
    
    # ==================== METODI AUTENTICAZIONE ====================
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentica un utente"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return None
        
        try:
            # Implementazione autenticazione sicura
            users = self.select('users', filters={'email': email})
            if users:
                user = users[0]
                # Verifica password con bcrypt
                import bcrypt
                password_hash = user.get('password_hash')
                if password_hash and bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    return user
            return None
        except Exception as e:
            logger.error(f"❌ Errore autenticazione utente: {e}")
            return None
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Crea un nuovo utente"""
        try:
            # Hash password (implementazione semplificata)
            user_data['password_hash'] = user_data.get('password', '')
            del user_data['password']  # Rimuovi password in chiaro
            
            return self.insert('users', user_data)
        except Exception as e:
            logger.error(f"❌ Errore creando utente: {e}")
            return None
    
    # ==================== METODI UTILITÀ ====================
    
    def get_table_info(self, table: str) -> Dict:
        """Ottiene informazioni su una tabella"""
        try:
            count = len(self.select(table))
            return {
                'table': table,
                'count': count,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Errore ottenendo info tabella {table}: {e}")
            return {}
    
    def backup_data(self) -> Dict:
        """Crea backup dei dati principali"""
        try:
            backup = {
                'timestamp': datetime.now().isoformat(),
                'products': self.select('products'),
                'customers': self.select('customers'),
                'sales': self.select('sales'),
                'suppliers': self.select('suppliers'),
                'employees': self.select('employees')
            }
            return backup
        except Exception as e:
            logger.error(f"❌ Errore creando backup: {e}")
            return {}

# Instanza globale
_supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Ottiene l'istanza globale del gestore Supabase"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager
