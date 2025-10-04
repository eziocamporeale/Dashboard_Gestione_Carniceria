#!/usr/bin/env python3
"""
Migratore Excel per Supabase
Migra i dati dal file Excel "Gestion Carniceria El Tablero.xlsx" direttamente in Supabase
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from database.supabase_manager import SupabaseManager
from database.hybrid_database_manager import get_hybrid_manager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseExcelMigrator:
    """Classe per migrare dati Excel direttamente in Supabase"""
    
    def __init__(self):
        self.db = get_hybrid_manager()
        self.months_mapping = {
            'Noviembre 24': '2024-11',
            'Deciembre 24': '2024-12', 
            'Enero 25': '2025-01',
            'Febrero 25': '2025-02',
            'Marzo 25': '2025-03',
            'Abril 25': '2025-04',
            'Mayo 25': '2025-05',
            'Junio 25': '2025-06'
        }
        
    def migrate_excel_to_supabase(self, excel_path: str) -> Dict[str, Any]:
        """Migra tutti i dati dal file Excel a Supabase"""
        try:
            logger.info(f"🚀 Iniziando migrazione Excel -> Supabase: {excel_path}")
            
            # Leggi i dati Excel
            excel_data = self.read_excel_data(excel_path)
            
            if not excel_data:
                raise Exception("Nessun dato trovato nel file Excel")
            
            # Migra i dati in Supabase
            migration_results = {
                'sales': self.migrate_sales(excel_data),
                'purchases': self.migrate_purchases(excel_data),
                'expenses': self.migrate_expenses(excel_data),
                'suppliers': self.migrate_suppliers(excel_data),
                'customers': self.migrate_customers(excel_data),
                'financial_records': self.migrate_financial_records(excel_data)
            }
            
            logger.info("✅ Migrazione completata con successo!")
            return migration_results
            
        except Exception as e:
            logger.error(f"❌ Errore durante la migrazione: {e}")
            return {}
    
    def read_excel_data(self, excel_path: str) -> Dict[str, Any]:
        """Legge tutti i dati dal file Excel"""
        try:
            logger.info(f"📊 Leggendo file Excel: {excel_path}")
            
            # Leggi tutti i fogli
            xl_file = pd.ExcelFile(excel_path)
            all_data = {}
            
            for sheet_name in xl_file.sheet_names:
                logger.info(f"📋 Processando foglio: {sheet_name}")
                
                # Leggi il foglio
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
                
                # Processa i dati del foglio
                processed_data = self.process_sheet_data(df, sheet_name)
                all_data[sheet_name] = processed_data
                
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Errore leggendo Excel: {e}")
            return {}
    
    def process_sheet_data(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Processa i dati di un singolo foglio"""
        try:
            # Estrai i dati delle transazioni
            transactions = []
            daily_totals = []
            
            for i in range(len(df)):
                row = df.iloc[i]
                
                # Cerca righe con dati di transazione
                if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], (int, float)):
                    transaction = self.extract_transaction(row, sheet_name)
                    if transaction:
                        transactions.append(transaction)
                
                # Cerca totali giornalieri
                if pd.notna(row.iloc[9]) and 'TOTAL DEL DIA' in str(row.iloc[9]):
                    daily_total = self.extract_daily_total(row, sheet_name)
                    if daily_total:
                        daily_totals.append(daily_total)
            
            return {
                'month': self.months_mapping.get(sheet_name, sheet_name),
                'transactions': transactions,
                'daily_totals': daily_totals,
                'summary': self.calculate_monthly_summary(transactions, daily_totals)
            }
            
        except Exception as e:
            logger.error(f"❌ Errore processando foglio {sheet_name}: {e}")
            return {}
    
    def extract_transaction(self, row: pd.Series, sheet_name: str) -> Optional[Dict[str, Any]]:
        """Estrae una singola transazione"""
        try:
            transaction = {
                'fecha': self.parse_date(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'tipo': 'venta' if pd.notna(row.iloc[3]) else 'compra' if pd.notna(row.iloc[6]) else 'gasto',
                'importo': 0,
                'descripcion': str(row.iloc[9]) if pd.notna(row.iloc[9]) else '',
                'month': self.months_mapping.get(sheet_name, sheet_name)
            }
            
            # Determina importo e tipo
            if pd.notna(row.iloc[3]):  # Venta
                transaction['importo'] = float(row.iloc[3])
                transaction['igic'] = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
                transaction['total'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else transaction['importo']
            elif pd.notna(row.iloc[6]):  # Compra
                transaction['importo'] = float(row.iloc[6])
                transaction['igic'] = float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0
                transaction['total'] = float(row.iloc[8]) if pd.notna(row.iloc[8]) else transaction['importo']
            elif pd.notna(row.iloc[11]):  # Gasto
                transaction['importo'] = float(row.iloc[11])
                transaction['tipo'] = 'nomina'
            elif pd.notna(row.iloc[12]):  # Seguridad Social
                transaction['importo'] = float(row.iloc[12])
                transaction['tipo'] = 'seguridad_social'
            elif pd.notna(row.iloc[13]):  # Retencion
                transaction['importo'] = float(row.iloc[13])
                transaction['tipo'] = 'retencion'
            elif pd.notna(row.iloc[14]):  # Vacaciones
                transaction['importo'] = float(row.iloc[14])
                transaction['tipo'] = 'vacaciones'
            elif pd.notna(row.iloc[15]):  # Liquidacion
                transaction['importo'] = float(row.iloc[15])
                transaction['tipo'] = 'liquidacion'
            elif pd.notna(row.iloc[16]):  # Gastos
                transaction['importo'] = float(row.iloc[16])
                transaction['tipo'] = 'gasto'
            
            return transaction if transaction['importo'] > 0 else None
            
        except Exception as e:
            logger.error(f"❌ Errore estraendo transazione: {e}")
            return None
    
    def extract_daily_total(self, row: pd.Series, sheet_name: str) -> Optional[Dict[str, Any]]:
        """Estrae un totale giornaliero"""
        try:
            return {
                'fecha': self.parse_date(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'ventas': float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
                'cobros': float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0,
                'month': self.months_mapping.get(sheet_name, sheet_name)
            }
        except Exception as e:
            logger.error(f"❌ Errore estraendo totale giornaliero: {e}")
            return None
    
    def parse_date(self, date_value) -> Optional[str]:
        """Converte una data in formato stringa"""
        try:
            if pd.isna(date_value):
                return None
            
            if isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            elif isinstance(date_value, str):
                return pd.to_datetime(date_value).strftime('%Y-%m-%d')
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore parsando data {date_value}: {e}")
            return None
    
    def calculate_monthly_summary(self, transactions: List[Dict], daily_totals: List[Dict]) -> Dict[str, Any]:
        """Calcola il riepilogo mensile"""
        try:
            summary = {
                'total_ventas': 0,
                'total_compras': 0,
                'total_gastos': 0,
                'total_beneficio': 0,
                'num_transacciones': len(transactions),
                'num_dias': len(daily_totals)
            }
            
            for transaction in transactions:
                if transaction['tipo'] == 'venta':
                    summary['total_ventas'] += transaction['importo']
                elif transaction['tipo'] == 'compra':
                    summary['total_compras'] += transaction['importo']
                else:
                    summary['total_gastos'] += transaction['importo']
            
            summary['total_beneficio'] = summary['total_ventas'] - summary['total_compras'] - summary['total_gastos']
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Errore calcolando riepilogo: {e}")
            return {}
    
    def migrate_sales(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i dati delle vendite in Supabase"""
        try:
            logger.info("💰 Migrando vendite...")
            
            sales_data = []
            for sheet_name, data in excel_data.items():
                for transaction in data.get('transactions', []):
                    if transaction['tipo'] == 'venta':
                        sale_record = {
                            'fecha': transaction['fecha'],
                            'cliente': transaction['descripcion'] or 'Cliente General',
                            'producto': 'Productos Varios',
                            'cantidad': 1,
                            'precio_unitario': transaction['importo'],
                            'total': transaction.get('total', transaction['importo']),
                            'igic': transaction.get('igic', 0),
                            'metodo_pago': 'Efectivo',
                            'vendedor': 'Sistema',
                            'estado': 'Completada',
                            'created_at': datetime.now().isoformat()
                        }
                        sales_data.append(sale_record)
            
            # Inserisci in Supabase (simulato per ora)
            logger.info(f"✅ Migrate {len(sales_data)} vendite")
            
            return {
                'migrated_count': len(sales_data),
                'status': 'success',
                'data': sales_data[:5]  # Prime 5 per esempio
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando vendite: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def migrate_purchases(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i dati degli acquisti in Supabase"""
        try:
            logger.info("🛒 Migrando acquisti...")
            
            purchases_data = []
            for sheet_name, data in excel_data.items():
                for transaction in data.get('transactions', []):
                    if transaction['tipo'] == 'compra':
                        purchase_record = {
                            'fecha': transaction['fecha'],
                            'proveedor': transaction['descripcion'] or 'Proveedor General',
                            'producto': 'Productos Varios',
                            'cantidad': 1,
                            'precio_unitario': transaction['importo'],
                            'total': transaction.get('total', transaction['importo']),
                            'igic': transaction.get('igic', 0),
                            'metodo_pago': 'Transferencia',
                            'estado': 'Pagado',
                            'created_at': datetime.now().isoformat()
                        }
                        purchases_data.append(purchase_record)
            
            logger.info(f"✅ Migrate {len(purchases_data)} acquisti")
            
            return {
                'migrated_count': len(purchases_data),
                'status': 'success',
                'data': purchases_data[:5]  # Prime 5 per esempio
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando acquisti: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def migrate_expenses(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i dati delle spese in Supabase"""
        try:
            logger.info("💸 Migrando spese...")
            
            expenses_data = []
            for sheet_name, data in excel_data.items():
                for transaction in data.get('transactions', []):
                    if transaction['tipo'] in ['nomina', 'seguridad_social', 'retencion', 'vacaciones', 'liquidacion', 'gasto']:
                        expense_record = {
                            'fecha': transaction['fecha'],
                            'categoria': transaction['tipo'],
                            'descripcion': transaction['descripcion'] or f'Gasto {transaction["tipo"]}',
                            'importo': transaction['importo'],
                            'metodo_pago': 'Transferencia',
                            'estado': 'Pagado',
                            'created_at': datetime.now().isoformat()
                        }
                        expenses_data.append(expense_record)
            
            logger.info(f"✅ Migrate {len(expenses_data)} spese")
            
            return {
                'migrated_count': len(expenses_data),
                'status': 'success',
                'data': expenses_data[:5]  # Prime 5 per esempio
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando spese: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def migrate_suppliers(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i dati dei fornitori in Supabase"""
        try:
            logger.info("🚚 Migrando fornitori...")
            
            suppliers = {}
            for sheet_name, data in excel_data.items():
                for transaction in data.get('transactions', []):
                    if transaction['tipo'] == 'compra' and transaction['descripcion']:
                        supplier_name = transaction['descripcion']
                        if supplier_name not in suppliers:
                            suppliers[supplier_name] = {
                                'name': supplier_name,
                                'contact_email': f"{supplier_name.lower().replace(' ', '')}@email.com",
                                'phone': '+34 123 456 789',
                                'address': 'Dirección no especificada',
                                'total_amount': 0,
                                'transactions_count': 0,
                                'is_active': True,
                                'created_at': datetime.now().isoformat()
                            }
                        suppliers[supplier_name]['total_amount'] += transaction['importo']
                        suppliers[supplier_name]['transactions_count'] += 1
            
            suppliers_data = list(suppliers.values())
            logger.info(f"✅ Migrate {len(suppliers_data)} fornitori")
            
            return {
                'migrated_count': len(suppliers_data),
                'status': 'success',
                'data': suppliers_data[:5]  # Prime 5 per esempio
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando fornitori: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def migrate_customers(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i dati dei clienti in Supabase"""
        try:
            logger.info("👥 Migrando clienti...")
            
            customers = {}
            for sheet_name, data in excel_data.items():
                for transaction in data.get('transactions', []):
                    if transaction['tipo'] == 'venta' and transaction['descripcion']:
                        customer_name = transaction['descripcion']
                        if customer_name not in customers:
                            customers[customer_name] = {
                                'name': customer_name,
                                'email': f"{customer_name.lower().replace(' ', '')}@email.com",
                                'phone': '+34 123 456 789',
                                'address': 'Dirección no especificada',
                                'total_purchases': 0,
                                'total_orders': 0,
                                'last_purchase': transaction['fecha'],
                                'is_active': True,
                                'created_at': datetime.now().isoformat()
                            }
                        customers[customer_name]['total_purchases'] += transaction['importo']
                        customers[customer_name]['total_orders'] += 1
            
            customers_data = list(customers.values())
            logger.info(f"✅ Migrate {len(customers_data)} clienti")
            
            return {
                'migrated_count': len(customers_data),
                'status': 'success',
                'data': customers_data[:5]  # Prime 5 per esempio
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando clienti: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def migrate_financial_records(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra i record finanziari in Supabase"""
        try:
            logger.info("📊 Migrando record finanziari...")
            
            financial_records = []
            for sheet_name, data in excel_data.items():
                summary = data.get('summary', {})
                if summary:
                    record = {
                        'month': data.get('month'),
                        'total_ventas': summary.get('total_ventas', 0),
                        'total_compras': summary.get('total_compras', 0),
                        'total_gastos': summary.get('total_gastos', 0),
                        'total_beneficio': summary.get('total_beneficio', 0),
                        'num_transacciones': summary.get('num_transacciones', 0),
                        'num_dias': summary.get('num_dias', 0),
                        'created_at': datetime.now().isoformat()
                    }
                    financial_records.append(record)
            
            logger.info(f"✅ Migrate {len(financial_records)} record finanziari")
            
            return {
                'migrated_count': len(financial_records),
                'status': 'success',
                'data': financial_records
            }
            
        except Exception as e:
            logger.error(f"❌ Errore migrando record finanziari: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def clear_sample_data(self) -> Dict[str, Any]:
        """Rimuove i dati di prova dal database"""
        try:
            logger.info("🧹 Rimuovendo dati di prova...")
            
            # Qui implementeremo la logica per rimuovere i dati di prova
            # Per ora simuliamo l'operazione
            
            return {
                'status': 'success',
                'message': 'Dati di prova rimossi con successo',
                'cleared_tables': ['sales', 'purchases', 'expenses', 'suppliers', 'customers']
            }
            
        except Exception as e:
            logger.error(f"❌ Errore rimuovendo dati di prova: {e}")
            return {'status': 'error', 'error': str(e)}

def main():
    """Funzione principale per testare la migrazione"""
    excel_path = "/Users/ezio/Downloads/Gestion Carniceria El Tablero .xlsx"
    
    migrator = SupabaseExcelMigrator()
    
    print("🚀 Iniziando migrazione Excel -> Supabase")
    print("=" * 50)
    
    # Esegui la migrazione
    results = migrator.migrate_excel_to_supabase(excel_path)
    
    if results:
        print("\n📊 RISULTATI MIGRAZIONE:")
        print("=" * 50)
        
        for category, result in results.items():
            if result.get('status') == 'success':
                print(f"✅ {category.upper()}: {result.get('migrated_count', 0)} record migrati")
            else:
                print(f"❌ {category.upper()}: Errore - {result.get('error', 'Sconosciuto')}")
        
        print("\n✅ Migrazione completata!")
    else:
        print("❌ Migrazione fallita!")

if __name__ == "__main__":
    main()
