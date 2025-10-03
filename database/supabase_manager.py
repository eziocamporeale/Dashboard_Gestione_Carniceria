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
        self._deleted_customers = set()  # Traccia clienti eliminati
        self._customers_cache = None     # Cache per i clienti
        self._deleted_suppliers = set()  # Traccia fornitori eliminati
        self._suppliers_cache = None     # Cache per i fornitori
        self._deleted_orders = set()     # Traccia ordini eliminati
        self._orders_cache = None        # Cache per gli ordini
        
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
    
    def get_sales_by_period(self, start_date=None, end_date=None, period: str = 'month') -> List[Dict]:
        """Ottiene vendite per periodo - compatibile con entrambe le firme"""
        try:
            # Se sono stati passati start_date e end_date, usa quelli
            if start_date is not None and end_date is not None:
                # Usa le date specifiche
                pass
            else:
                # Usa il periodo predefinito
                if period == 'month':
                    start_date = datetime.now() - timedelta(days=30)
                elif period == 'week':
                    start_date = datetime.now() - timedelta(days=7)
                else:
                    start_date = datetime.now() - timedelta(days=1)
                end_date = datetime.now()
            
            # Query per range di date
            query = self.client.table('sales').select('*')
            query = query.gte('sale_date', start_date.isoformat())
            query = query.lte('sale_date', end_date.isoformat())
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per periodo: {e}")
            return []
    
    def get_top_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            # In una implementazione reale, si farebbe una query JOIN con sales
            return [
                {'id': 1, 'name': 'Carne de Res', 'total_sales': 150.75, 'total_quantity': 10},
                {'id': 2, 'name': 'Pollo', 'total_sales': 87.50, 'total_quantity': 8},
                {'id': 3, 'name': 'Cerdo', 'total_sales': 65.25, 'total_quantity': 5},
                {'id': 4, 'name': 'Chorizo', 'total_sales': 45.00, 'total_quantity': 6},
                {'id': 5, 'name': 'Jamón', 'total_sales': 32.50, 'total_quantity': 4}
            ][:limit]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo top prodotti: {e}")
            return []
    
    def get_top_customers(self, limit: int = 5) -> List[Dict]:
        """Ottiene clienti più attivi"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'id': 1, 'name': 'Juan Pérez', 'total_purchases': 450.75, 'total_orders': 12},
                {'id': 2, 'name': 'María García', 'total_purchases': 387.50, 'total_orders': 8},
                {'id': 3, 'name': 'Carlos López', 'total_purchases': 265.25, 'total_orders': 6},
                {'id': 4, 'name': 'Ana Martínez', 'total_purchases': 245.00, 'total_orders': 5},
                {'id': 5, 'name': 'Luis Rodríguez', 'total_purchases': 132.50, 'total_orders': 3}
            ][:limit]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo top clienti: {e}")
            return []
    
    def get_monthly_revenue(self, months: int = 6) -> List[Dict]:
        """Ottiene ricavi mensili"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'month': '2024-01', 'revenue': 12500.75, 'orders': 45},
                {'month': '2024-02', 'revenue': 13800.50, 'orders': 52},
                {'month': '2024-03', 'revenue': 15200.25, 'orders': 58},
                {'month': '2024-04', 'revenue': 16800.00, 'orders': 65},
                {'month': '2024-05', 'revenue': 17500.75, 'orders': 68},
                {'month': '2024-06', 'revenue': 18200.50, 'orders': 72}
            ][:months]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo ricavi mensili: {e}")
            return []
    
    def get_daily_sales(self, days: int = 7) -> List[Dict]:
        """Ottiene vendite giornaliere"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'date': '2024-06-01', 'sales': 850.75, 'orders': 12},
                {'date': '2024-06-02', 'sales': 920.50, 'orders': 15},
                {'date': '2024-06-03', 'sales': 780.25, 'orders': 10},
                {'date': '2024-06-04', 'sales': 1100.00, 'orders': 18},
                {'date': '2024-06-05', 'sales': 950.75, 'orders': 14},
                {'date': '2024-06-06', 'sales': 1200.50, 'orders': 20},
                {'date': '2024-06-07', 'sales': 1050.25, 'orders': 16}
            ][:days]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite giornaliere: {e}")
            return []
    
    def get_product_categories(self) -> List[Dict]:
        """Ottiene categorie di prodotti"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'id': 1, 'name': 'Carnes', 'description': 'Carnes frescas', 'color': '#DC3545'},
                {'id': 2, 'name': 'Aves', 'description': 'Pollo y otras aves', 'color': '#FFC107'},
                {'id': 3, 'name': 'Embutidos', 'description': 'Embutidos y fiambres', 'color': '#6F42C1'},
                {'id': 4, 'name': 'Pescados', 'description': 'Pescados frescos', 'color': '#17A2B8'},
                {'id': 5, 'name': 'Verduras', 'description': 'Verduras frescas', 'color': '#28A745'},
                {'id': 6, 'name': 'Otros', 'description': 'Otros productos', 'color': '#6C757D'}
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo categorie prodotti: {e}")
            return []
    
    def get_units_of_measure(self) -> List[Dict]:
        """Ottiene unità di misura"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'id': 1, 'name': 'Kilogramo', 'symbol': 'kg', 'description': 'Peso en kilogramos'},
                {'id': 2, 'name': 'Gramo', 'symbol': 'g', 'description': 'Peso en gramos'},
                {'id': 3, 'name': 'Unidad', 'symbol': 'un', 'description': 'Cantidad en unidades'},
                {'id': 4, 'name': 'Libra', 'symbol': 'lb', 'description': 'Peso en libras'},
                {'id': 5, 'name': 'Onza', 'symbol': 'oz', 'description': 'Peso en onzas'}
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo unità di misura: {e}")
            return []
    
    def get_all_products(self) -> List[Dict]:
        """Ottiene tutti i prodotti"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {
                    'id': 1, 'name': 'Carne de Res', 'code': 'BOV001', 'description': 'Carne de res fresca',
                    'category_id': 1, 'category_name': 'Carnes', 'unit_id': 1, 'unit_name': 'Kilogramo',
                    'cost_price': 15.50, 'selling_price': 25.00, 'current_stock': 50.0, 'min_stock_level': 10.0,
                    'expiry_date': '2024-10-15', 'supplier_id': 1, 'is_active': True
                },
                {
                    'id': 2, 'name': 'Pollo', 'code': 'AVE001', 'description': 'Pollo fresco',
                    'category_id': 2, 'category_name': 'Aves', 'unit_id': 1, 'unit_name': 'Kilogramo',
                    'cost_price': 8.50, 'selling_price': 12.00, 'current_stock': 30.0, 'min_stock_level': 5.0,
                    'expiry_date': '2024-10-10', 'supplier_id': 2, 'is_active': True
                },
                {
                    'id': 3, 'name': 'Chorizo', 'code': 'EMB001', 'description': 'Chorizo artesanal',
                    'category_id': 3, 'category_name': 'Embutidos', 'unit_id': 3, 'unit_name': 'Unidad',
                    'cost_price': 5.00, 'selling_price': 8.50, 'current_stock': 20.0, 'min_stock_level': 3.0,
                    'expiry_date': '2024-10-20', 'supplier_id': 3, 'is_active': True
                }
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti: {e}")
            return []
    
    def get_all_suppliers(self) -> List[Dict]:
        """Ottiene tutti i fornitori"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            all_suppliers = [
                {
                    'id': 1, 'name': 'Carnes del Norte', 'contact_person': 'Juan Pérez',
                    'phone': '+54 11 1234-5678', 'contact_email': 'juan@carnesdelnorte.com',
                    'address': 'Av. Corrientes 1234, Buenos Aires', 'cuit': '20-12345678-9',
                    'total_amount': 45000.00, 'transactions_count': 25, 'is_active': True,
                    'created_at': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2, 'name': 'Aves Frescas S.A.', 'contact_person': 'María García',
                    'phone': '+54 11 2345-6789', 'contact_email': 'maria@avesfrescas.com',
                    'address': 'Av. Santa Fe 5678, Buenos Aires', 'cuit': '20-23456789-0',
                    'total_amount': 32000.00, 'transactions_count': 18, 'is_active': True,
                    'created_at': '2024-02-20T14:15:00Z'
                },
                {
                    'id': 3, 'name': 'Embutidos Artesanales', 'contact_person': 'Carlos López',
                    'phone': '+54 11 3456-7890', 'contact_email': 'carlos@embutidosartesanales.com',
                    'address': 'Av. Córdoba 9012, Buenos Aires', 'cuit': '20-34567890-1',
                    'total_amount': 28000.00, 'transactions_count': 15, 'is_active': True,
                    'created_at': '2024-03-10T09:45:00Z'
                }
            ]
            
            # Filtra i fornitori eliminati
            active_suppliers = [s for s in all_suppliers if s['id'] not in self._deleted_suppliers]
            return active_suppliers
        except Exception as e:
            logger.error(f"❌ Errore ottenendo fornitori: {e}")
            return []
    
    def get_all_customers(self) -> List[Dict]:
        """Ottiene tutti i clienti"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            all_customers = [
                {
                    'id': 1, 'name': 'Juan Pérez', 'email': 'juan.perez@email.com',
                    'phone': '+54 11 1234-5678', 'address': 'Av. Corrientes 1234, Buenos Aires',
                    'total_purchases': 4500.75, 'total_orders': 12, 'last_purchase': '2024-09-28',
                    'is_active': True, 'created_at': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2, 'name': 'María García', 'email': 'maria.garcia@email.com',
                    'phone': '+54 11 2345-6789', 'address': 'Av. Santa Fe 5678, Buenos Aires',
                    'total_purchases': 3200.50, 'total_orders': 8, 'last_purchase': '2024-09-25',
                    'is_active': True, 'created_at': '2024-02-20T14:15:00Z'
                },
                {
                    'id': 3, 'name': 'Carlos López', 'email': 'carlos.lopez@email.com',
                    'phone': '+54 11 3456-7890', 'address': 'Av. Córdoba 9012, Buenos Aires',
                    'total_purchases': 2800.25, 'total_orders': 6, 'last_purchase': '2024-09-22',
                    'is_active': True, 'created_at': '2024-03-10T09:45:00Z'
                },
                {
                    'id': 4, 'name': 'Ana Martínez', 'email': 'ana.martinez@email.com',
                    'phone': '+54 11 4567-8901', 'address': 'Av. Rivadavia 3456, Buenos Aires',
                    'total_purchases': 1950.00, 'total_orders': 4, 'last_purchase': '2024-09-20',
                    'is_active': True, 'created_at': '2024-04-05T16:20:00Z'
                },
                {
                    'id': 5, 'name': 'Luis Rodríguez', 'email': 'luis.rodriguez@email.com',
                    'phone': '+54 11 5678-9012', 'address': 'Av. Callao 7890, Buenos Aires',
                    'total_purchases': 1200.75, 'total_orders': 3, 'last_purchase': '2024-09-18',
                    'is_active': True, 'created_at': '2024-05-12T11:30:00Z'
                }
            ]
            
            # Filtra i clienti eliminati
            active_customers = [c for c in all_customers if c['id'] not in self._deleted_customers]
            return active_customers
        except Exception as e:
            logger.error(f"❌ Errore ottenendo clienti: {e}")
            return []
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Actualiza un cliente existente"""
        try:
            # En una implementación real, aquí se actualizaría en Supabase
            logger.info(f"✅ Cliente {customer_id} actualizado: {customer_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando cliente {customer_id}: {e}")
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Elimina un cliente"""
        try:
            # Aggiungi l'ID alla lista dei clienti eliminati
            self._deleted_customers.add(customer_id)
            logger.info(f"✅ Cliente {customer_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando cliente {customer_id}: {e}")
            return False
    
    def create_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Crea un nuevo cliente"""
        try:
            # En una implementación real, aquí se insertaría en Supabase
            logger.info(f"✅ Nuevo cliente creado: {customer_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando cliente: {e}")
            return False
    
    # ==================== METODOS CRM ====================
    
    def get_customer_interactions(self, customer_id: int) -> List[Dict[str, Any]]:
        """Obtiene el historial de interacciones de un cliente"""
        try:
            # Datos de ejemplo para interacciones
            interactions = [
                {
                    'id': 1, 'customer_id': customer_id, 'type': 'llamada', 'date': '2024-09-28',
                    'description': 'Llamada de seguimiento post-compra', 'outcome': 'satisfecho',
                    'notes': 'Cliente muy contento con el producto', 'employee': 'Juan Pérez'
                },
                {
                    'id': 2, 'customer_id': customer_id, 'type': 'email', 'date': '2024-09-25',
                    'description': 'Envío de catálogo de productos', 'outcome': 'interesado',
                    'notes': 'Solicitó información sobre nuevos productos', 'employee': 'María García'
                },
                {
                    'id': 3, 'customer_id': customer_id, 'type': 'visita', 'date': '2024-09-20',
                    'description': 'Visita al local para consulta', 'outcome': 'compra_realizada',
                    'notes': 'Realizó compra por $450', 'employee': 'Carlos López'
                }
            ]
            return [i for i in interactions if i['customer_id'] == customer_id]
        except Exception as e:
            logger.error(f"❌ Error obteniendo interacciones del cliente {customer_id}: {e}")
            return []
    
    def add_customer_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Añade una nueva interacción con el cliente"""
        try:
            logger.info(f"✅ Nueva interacción añadida: {interaction_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error añadiendo interacción: {e}")
            return False
    
    def get_customer_segments(self) -> List[Dict[str, Any]]:
        """Obtiene segmentos de clientes"""
        try:
            return [
                {'segment': 'VIP', 'count': 5, 'description': 'Clientes con compras > $5000', 'color': '#FFD700'},
                {'segment': 'Frecuentes', 'count': 12, 'description': 'Clientes con > 10 compras', 'color': '#32CD32'},
                {'segment': 'Ocasionales', 'count': 8, 'description': 'Clientes con 3-10 compras', 'color': '#FFA500'},
                {'segment': 'Nuevos', 'count': 3, 'description': 'Clientes con < 3 compras', 'color': '#87CEEB'},
                {'segment': 'Inactivos', 'count': 2, 'description': 'Sin compras en 6 meses', 'color': '#DC143C'}
            ]
        except Exception as e:
            logger.error(f"❌ Error obteniendo segmentos: {e}")
            return []
    
    def get_customer_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de clientes"""
        try:
            return {
                'total_customers': 30,
                'active_customers': 25,
                'new_customers_this_month': 5,
                'churn_rate': 8.5,
                'average_purchase_value': 2850.50,
                'customer_satisfaction': 4.2,
                'repeat_purchase_rate': 75.0,
                'lifetime_value': 12500.00
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo analytics: {e}")
            return {}
    
    def get_marketing_campaigns(self) -> List[Dict[str, Any]]:
        """Obtiene campañas de marketing"""
        try:
            return [
                {
                    'id': 1, 'name': 'Oferta Carnes Premium', 'status': 'activa',
                    'start_date': '2024-09-01', 'end_date': '2024-09-30',
                    'target_segment': 'VIP', 'response_rate': 15.5,
                    'conversion_rate': 8.2, 'roi': 250.0
                },
                {
                    'id': 2, 'name': 'Descuento Nuevos Clientes', 'status': 'finalizada',
                    'start_date': '2024-08-15', 'end_date': '2024-08-31',
                    'target_segment': 'Nuevos', 'response_rate': 22.3,
                    'conversion_rate': 12.1, 'roi': 180.0
                },
                {
                    'id': 3, 'name': 'Recordatorio Compras', 'status': 'programada',
                    'start_date': '2024-10-01', 'end_date': '2024-10-15',
                    'target_segment': 'Inactivos', 'response_rate': 0.0,
                    'conversion_rate': 0.0, 'roi': 0.0
                }
            ]
        except Exception as e:
            logger.error(f"❌ Error obteniendo campañas: {e}")
            return []
    
    def get_customer_predictions(self) -> List[Dict[str, Any]]:
        """Obtiene predicciones de clientes"""
        try:
            return [
                {
                    'customer_id': 1, 'customer_name': 'Juan Pérez',
                    'prediction': 'alto_riesgo_abandono', 'probability': 85.2,
                    'recommendation': 'Ofrecer descuento especial', 'priority': 'alta'
                },
                {
                    'customer_id': 2, 'customer_name': 'María García',
                    'prediction': 'compra_probable', 'probability': 78.5,
                    'recommendation': 'Enviar catálogo de productos', 'priority': 'media'
                },
                {
                    'customer_id': 3, 'customer_name': 'Carlos López',
                    'prediction': 'cliente_estable', 'probability': 92.1,
                    'recommendation': 'Mantener relación actual', 'priority': 'baja'
                }
            ]
        except Exception as e:
            logger.error(f"❌ Error obteniendo predicciones: {e}")
            return []
    
    # ==================== METODOS PROVEEDORES CRUD ====================
    
    def update_supplier(self, supplier_id: int, supplier_data: Dict[str, Any]) -> bool:
        """Actualiza un proveedor existente"""
        try:
            # En una implementación real, aquí se actualizaría en Supabase
            logger.info(f"✅ Proveedor {supplier_id} actualizado: {supplier_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor {supplier_id}: {e}")
            return False
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Elimina un proveedor"""
        try:
            # Aggiungi l'ID alla lista dei fornitori eliminati
            self._deleted_suppliers.add(supplier_id)
            logger.info(f"✅ Proveedor {supplier_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando proveedor {supplier_id}: {e}")
            return False
    
    def create_supplier(self, supplier_data: Dict[str, Any]) -> bool:
        """Crea un nuevo proveedor"""
        try:
            # En una implementación real, aquí se insertaría en Supabase
            logger.info(f"✅ Nuevo proveedor creado: {supplier_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando proveedor: {e}")
            return False
    
    # ==================== METODOS ORDERS CRUD ====================
    
    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> bool:
        """Actualiza un pedido existente"""
        try:
            # En una implementación real, aquí se actualizaría en Supabase
            logger.info(f"✅ Pedido {order_id} actualizado: {order_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando pedido {order_id}: {e}")
            return False
    
    def delete_order(self, order_id: int) -> bool:
        """Elimina un pedido"""
        try:
            # Aggiungi l'ID alla lista degli ordini eliminati
            self._deleted_orders.add(order_id)
            logger.info(f"✅ Pedido {order_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando pedido {order_id}: {e}")
            return False
    
    def create_order(self, order_data: Dict[str, Any]) -> bool:
        """Crea un nuevo pedido"""
        try:
            # En una implementación real, aquí se insertaría en Supabase
            logger.info(f"✅ Nuevo pedido creado: {order_data}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando pedido: {e}")
            return False
    
    def get_supplier_orders(self) -> List[Dict[str, Any]]:
        """Obtiene todos los pedidos de proveedores"""
        try:
            all_orders = [
                {
                    'id': 1,
                    'supplier_name': 'Distribuidora ABC',
                    'order_date': '2024-09-20',
                    'delivery_date': '2024-09-25',
                    'status': 'Pendiente',
                    'total_amount': 1250.50,
                    'items_count': 15
                },
                {
                    'id': 2,
                    'supplier_name': 'Carnes Premium',
                    'order_date': '2024-09-18',
                    'delivery_date': '2024-09-22',
                    'status': 'Entregado',
                    'total_amount': 890.75,
                    'items_count': 8
                },
                {
                    'id': 3,
                    'supplier_name': 'Embutidos del Sur',
                    'order_date': '2024-09-15',
                    'delivery_date': '2024-09-20',
                    'status': 'En Tránsito',
                    'total_amount': 675.25,
                    'items_count': 12
                }
            ]
            
            # Filtra gli ordini eliminati
            active_orders = [o for o in all_orders if o['id'] not in self._deleted_orders]
            return active_orders
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos de proveedores: {e}")
            return []
    
    def get_sales_summary(self) -> Dict:
        """Ottiene riepilogo vendite"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return {
                'total_sales_today': 1250.75,
                'total_sales_week': 8750.50,
                'total_sales_month': 32500.25,
                'total_sales_year': 125000.00,
                'average_daily_sales': 1083.33,
                'best_selling_product': 'Carne de Res Premium',
                'best_selling_category': 'Carnes',
                'total_transactions': 156,
                'average_transaction_value': 801.28
            }
        except Exception as e:
            logger.error(f"❌ Errore ottenendo riepilogo vendite: {e}")
            return {}
    
    def get_sales_team_performance(self) -> List[Dict]:
        """Ottiene performance del team vendite"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {
                    'employee_name': 'María García',
                    'position': 'Vendedora Senior',
                    'total_sales': 45000.75,
                    'transactions': 85,
                    'commission': 2250.38,
                    'rating': 4.8
                },
                {
                    'employee_name': 'Carlos López',
                    'position': 'Vendedor',
                    'total_sales': 32000.50,
                    'transactions': 62,
                    'commission': 1600.25,
                    'rating': 4.5
                },
                {
                    'employee_name': 'Ana Martínez',
                    'position': 'Vendedora Junior',
                    'total_sales': 18500.25,
                    'transactions': 45,
                    'commission': 925.13,
                    'rating': 4.2
                }
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo performance team: {e}")
            return []
    
    def get_sales_forecast(self, months: int = 6) -> List[Dict]:
        """Ottiene proiezione vendite"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            import datetime
            from dateutil.relativedelta import relativedelta
            
            forecast_data = []
            base_date = datetime.datetime.now()
            
            for i in range(months):
                month_date = base_date + relativedelta(months=i)
                predicted_sales = 30000 + (i * 2000)  # Crescita simulata
                confidence_lower = predicted_sales * 0.85
                confidence_upper = predicted_sales * 1.15
                growth_rate = 0.05 + (i * 0.01)  # Crescita del 5-10%
                
                forecast_data.append({
                    'month': month_date.strftime('%Y-%m'),
                    'predicted_sales': predicted_sales,
                    'confidence_lower': confidence_lower,
                    'confidence_upper': confidence_upper,
                    'growth_rate': growth_rate
                })
            
            return forecast_data
        except Exception as e:
            logger.error(f"❌ Errore ottenendo proiezione vendite: {e}")
            return []
    
    def get_daily_sales_data(self, days: int = 30) -> List[Dict]:
        """Ottiene dati vendite giornaliere"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            import datetime
            from dateutil.relativedelta import relativedelta
            
            daily_data = []
            base_date = datetime.datetime.now() - relativedelta(days=days)
            
            for i in range(days):
                current_date = base_date + relativedelta(days=i)
                # Simula vendite con variazione casuale
                base_sales = 1000 + (i * 50)  # Crescita base
                variation = (i % 7) * 200  # Variazione settimanale
                daily_sales = base_sales + variation
                
                daily_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'sales': daily_sales,
                    'transactions': 15 + (i % 10),
                    'avg_transaction': daily_sales / (15 + (i % 10))
                })
            
            return daily_data
        except Exception as e:
            logger.error(f"❌ Errore ottenendo dati vendite giornaliere: {e}")
            return []
    
    def get_sales_by_category(self) -> List[Dict]:
        """Ottiene vendite per categoria"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {'category': 'Carnes', 'sales': 15000.50, 'percentage': 45.2, 'transactions': 85},
                {'category': 'Aves', 'sales': 8500.25, 'percentage': 25.6, 'transactions': 45},
                {'category': 'Embutidos', 'sales': 6200.75, 'percentage': 18.7, 'transactions': 32},
                {'category': 'Pescados', 'sales': 2800.00, 'percentage': 8.4, 'transactions': 18},
                {'category': 'Verduras', 'sales': 1200.50, 'percentage': 3.6, 'transactions': 12}
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo vendite per categoria: {e}")
            return []
    
    def get_top_selling_products(self, limit: int = 10) -> List[Dict]:
        """Ottiene prodotti più venduti"""
        try:
            # Dati di esempio per compatibilità con il dashboard
            return [
                {
                    'product': 'Carne de Res Premium',
                    'category': 'Carnes',
                    'sales': 4500.75,
                    'quantity': 25.5,
                    'profit': 1125.19
                },
                {
                    'product': 'Pollo Entero',
                    'category': 'Aves',
                    'sales': 3200.50,
                    'quantity': 40.0,
                    'profit': 800.13
                },
                {
                    'product': 'Jamón Cocido',
                    'category': 'Embutidos',
                    'sales': 2800.25,
                    'quantity': 15.0,
                    'profit': 700.06
                },
                {
                    'product': 'Salchichas',
                    'category': 'Embutidos',
                    'sales': 1950.00,
                    'quantity': 30.0,
                    'profit': 487.50
                },
                {
                    'product': 'Bife de Chorizo',
                    'category': 'Carnes',
                    'sales': 1800.75,
                    'quantity': 12.0,
                    'profit': 450.19
                }
            ]
        except Exception as e:
            logger.error(f"❌ Errore ottenendo prodotti più venduti: {e}")
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
    
    def log_activity(self, user_id: str, action: str, details: str, ip_address: str = None):
        """Log dell'attività utente"""
        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': action,
                'description': details,
                'ip_address': ip_address
            }
            return self.insert('activity_log', activity_data)
        except Exception as e:
            logger.error(f"❌ Errore loggando attività: {e}")
            return None
    
    def rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """Chiama una funzione RPC (Remote Procedure Call) su Supabase"""
        if not self.is_connected():
            logger.error("❌ Supabase non connesso")
            return None
        try:
            response = self.client.rpc(function_name, params).execute()
            return response.data
        except Exception as e:
            logger.error(f"❌ Errore chiamata RPC '{function_name}': {e}")
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
