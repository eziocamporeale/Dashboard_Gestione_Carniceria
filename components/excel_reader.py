#!/usr/bin/env python3
"""
Lector de Excel Específico para Carnicería
Lee y procesa el Excel real de la carnicería
Creado por Ezio Camporeale
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging
import streamlit as st

# Configurar logging
logger = logging.getLogger(__name__)

class ExcelReader:
    """Lector específico para el Excel de la carnicería"""
    
    def __init__(self):
        self.data = {}
        self.processed_data = {}
        
    def load_excel(self, file_path: str) -> bool:
        """Carga el Excel y procesa todas las hojas"""
        try:
            # Cargar todas las hojas
            self.data = pd.read_excel(file_path, sheet_name=None)
            
            # Procesar cada hoja
            for sheet_name, sheet_data in self.data.items():
                logger.info(f"📊 Procesando hoja: {sheet_name}")
                processed = self._process_sheet(sheet_name, sheet_data)
                if processed:
                    self.processed_data[sheet_name] = processed
            
            logger.info(f"✅ Excel cargado: {len(self.processed_data)} hojas procesadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando Excel: {e}")
            return False
    
    def _process_sheet(self, sheet_name: str, data: pd.DataFrame) -> Dict:
        """Procesa una hoja específica"""
        try:
            # Limpiar datos
            cleaned_data = self._clean_data(data)
            
            if cleaned_data.empty:
                return None
            
            # Extraer información
            sheet_info = {
                'sheet_name': sheet_name,
                'total_rows': len(cleaned_data),
                'sales_data': self._extract_sales_data(cleaned_data),
                'supplier_data': self._extract_supplier_data(cleaned_data),
                'summary': self._create_summary(cleaned_data)
            }
            
            return sheet_info
            
        except Exception as e:
            logger.error(f"❌ Error procesando hoja {sheet_name}: {e}")
            return None
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpia los datos de la hoja"""
        try:
            # Remover filas completamente vacías
            cleaned = data.dropna(how='all')
            
            # Remover columnas completamente vacías
            cleaned = cleaned.dropna(axis=1, how='all')
            
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos: {e}")
            return data
    
    def _extract_sales_data(self, data: pd.DataFrame) -> Dict:
        """Extrae datos de ventas"""
        try:
            sales_info = {
                'total_sales': 0,
                'daily_sales': [],
                'total_transactions': 0
            }
            
            # Buscar específicamente las columnas de ventas del Excel real
            sales_columns = []
            for col in data.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ['base', 'igic', 'cobro', 'total']):
                    sales_columns.append(col)
            
            # Calcular total de ventas solo de las columnas correctas
            for col in sales_columns:
                try:
                    values = pd.to_numeric(data[col], errors='coerce')
                    # Filtrar valores extremos (probablemente errores de lectura)
                    values = values[(values >= 0) & (values <= 1000000)]  # Máximo 1 millón
                    sales_info['total_sales'] += values.sum()
                except:
                    pass
            
            # Buscar ventas diarias
            daily_sales = self._find_daily_sales(data)
            sales_info['daily_sales'] = daily_sales
            
            # Contar transacciones válidas
            sales_info['total_transactions'] = len(data)
            
            return sales_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de ventas: {e}")
            return {}
    
    def _find_daily_sales(self, data: pd.DataFrame) -> List[Dict]:
        """Encuentra las ventas diarias"""
        try:
            daily_sales = []
            
            # Buscar en todas las filas
            for index, row in data.iterrows():
                try:
                    # Convertir fila a string para buscar "TOTAL DIA"
                    row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                    
                    if 'TOTAL DIA' in row_str:
                        # Buscar valores numéricos en la fila
                        numeric_values = []
                        for cell in row:
                            if pd.notna(cell):
                                try:
                                    numeric_values.append(float(cell))
                                except:
                                    pass
                        
                        if numeric_values:
                            # Filtrar valores extremos
                            valid_values = [v for v in numeric_values if 0 <= v <= 1000000]
                            
                            if valid_values:
                                daily_sale = {
                                    'date': row.iloc[1] if len(row) > 1 else None,
                                    'amount': max(valid_values),  # Tomar el valor más alto válido
                                    'type': 'daily_total'
                                }
                                daily_sales.append(daily_sale)
                            
                except Exception as row_error:
                    continue
            
            return daily_sales
            
        except Exception as e:
            logger.error(f"❌ Error encontrando ventas diarias: {e}")
            return []
    
    def _extract_supplier_data(self, data: pd.DataFrame) -> Dict:
        """Extrae datos de proveedores"""
        try:
            supplier_info = {
                'total_payments': 0,
                'suppliers': [],
                'supplier_count': 0
            }
            
            # Buscar proveedores
            suppliers = self._find_suppliers(data)
            supplier_info['suppliers'] = suppliers
            supplier_info['supplier_count'] = len(suppliers)
            
            # Calcular total de pagos
            for supplier in suppliers:
                supplier_info['total_payments'] += supplier.get('amount', 0)
            
            return supplier_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de proveedores: {e}")
            return {}
    
    def _find_suppliers(self, data: pd.DataFrame) -> List[Dict]:
        """Encuentra los proveedores"""
        try:
            suppliers = []
            
            # Buscar en todas las filas
            for index, row in data.iterrows():
                try:
                    # Convertir fila a string para buscar nombres de proveedores
                    row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                    
                    # Si no es "TOTAL DIA" y tiene texto, podría ser un proveedor
                    if 'TOTAL DIA' not in row_str and len(row_str.strip()) > 0:
                        # Buscar valores numéricos en la fila
                        numeric_values = []
                        for cell in row:
                            if pd.notna(cell):
                                try:
                                    numeric_values.append(float(cell))
                                except:
                                    pass
                        
                        if numeric_values:
                            # Filtrar valores extremos
                            valid_values = [v for v in numeric_values if 0 <= v <= 1000000]
                            
                            if valid_values:
                                # Buscar el nombre del proveedor (último texto no numérico)
                                supplier_name = None
                                for cell in row:
                                    if pd.notna(cell) and not str(cell).replace('.', '').replace(',', '').isdigit():
                                        supplier_name = str(cell).strip()
                                
                                if supplier_name and supplier_name != 'nan' and supplier_name != 'TOTAL DIA':
                                    supplier = {
                                        'name': supplier_name,
                                        'amount': max(valid_values),
                                        'date': row.iloc[1] if len(row) > 1 else None,
                                        'invoice': row.iloc[0] if len(row) > 0 else None
                                    }
                                    suppliers.append(supplier)
                            
                except Exception as row_error:
                    continue
            
            return suppliers
            
        except Exception as e:
            logger.error(f"❌ Error encontrando proveedores: {e}")
            return []
    
    def _create_summary(self, data: pd.DataFrame) -> Dict:
        """Crea un resumen de los datos"""
        try:
            summary = {
                'total_rows': len(data),
                'total_columns': len(data.columns),
                'data_quality': 'good',
                'columns_info': {}
            }
            
            # Información de columnas
            for col in data.columns:
                summary['columns_info'][str(col)] = {
                    'type': str(data[col].dtype),
                    'non_null_count': data[col].count(),
                    'null_count': data[col].isnull().sum(),
                    'unique_values': data[col].nunique()
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error creando resumen: {e}")
            return {}
    
    def get_comprehensive_analysis(self) -> Dict:
        """Obtiene un análisis completo"""
        try:
            analysis = {
                'overview': self._get_overview(),
                'monthly_breakdown': self._get_monthly_breakdown(),
                'trends': self._calculate_trends(),
                'suppliers_analysis': self._analyze_suppliers(),
                'forecasts': self._generate_forecasts()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis completo: {e}")
            return {}
    
    def _get_overview(self) -> Dict:
        """Obtiene una visión general"""
        try:
            overview = {
                'total_months': len(self.processed_data),
                'total_sales': 0,
                'total_expenses': 0,
                'total_profit': 0,
                'total_transactions': 0
            }
            
            # Calcular totales
            for month_data in self.processed_data.values():
                sales = month_data.get('sales_data', {}).get('total_sales', 0)
                expenses = month_data.get('supplier_data', {}).get('total_payments', 0)
                transactions = month_data.get('sales_data', {}).get('total_transactions', 0)
                
                overview['total_sales'] += sales
                overview['total_expenses'] += expenses
                overview['total_profit'] += (sales - expenses)
                overview['total_transactions'] += transactions
            
            return overview
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visión general: {e}")
            return {}
    
    def _get_monthly_breakdown(self) -> Dict:
        """Obtiene el desglose mensual"""
        try:
            breakdown = {}
            
            for month, data in self.processed_data.items():
                sales = data.get('sales_data', {}).get('total_sales', 0)
                expenses = data.get('supplier_data', {}).get('total_payments', 0)
                profit = sales - expenses
                transactions = data.get('sales_data', {}).get('total_transactions', 0)
                
                breakdown[month] = {
                    'sales': sales,
                    'expenses': expenses,
                    'profit': profit,
                    'transactions': transactions,
                    'profit_margin': (profit / sales * 100) if sales > 0 else 0
                }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo desglose mensual: {e}")
            return {}
    
    def _calculate_trends(self) -> Dict:
        """Calcula las tendencias"""
        try:
            trends = {
                'sales_trend': 'stable',
                'expense_trend': 'stable',
                'profit_trend': 'stable',
                'growth_rate': 0
            }
            
            if len(self.processed_data) < 2:
                return trends
            
            # Obtener datos para análisis
            monthly_breakdown = self._get_monthly_breakdown()
            
            sales_values = []
            expense_values = []
            profit_values = []
            
            for month_data in monthly_breakdown.values():
                sales_values.append(month_data['sales'])
                expense_values.append(month_data['expenses'])
                profit_values.append(month_data['profit'])
            
            # Calcular tendencias
            if len(sales_values) > 1:
                trends['sales_trend'] = self._determine_trend(sales_values)
                trends['expense_trend'] = self._determine_trend(expense_values)
                trends['profit_trend'] = self._determine_trend(profit_values)
                
                # Calcular tasa de crecimiento
                if sales_values[0] > 0:
                    trends['growth_rate'] = ((sales_values[-1] - sales_values[0]) / sales_values[0]) * 100
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Error calculando tendencias: {e}")
            return {}
    
    def _determine_trend(self, values: List[float]) -> str:
        """Determina la tendencia de una serie de valores"""
        try:
            if len(values) < 2:
                return 'stable'
            
            # Calcular pendiente
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            if slope > 0.1:
                return 'increasing'
            elif slope < -0.1:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"❌ Error determinando tendencia: {e}")
            return 'stable'
    
    def _analyze_suppliers(self) -> Dict:
        """Analiza los proveedores"""
        try:
            suppliers_analysis = {
                'total_suppliers': 0,
                'top_suppliers': [],
                'total_payments': 0,
                'average_payment': 0
            }
            
            supplier_totals = {}
            total_payments = 0
            
            # Analizar proveedores
            for month_data in self.processed_data.values():
                suppliers = month_data.get('supplier_data', {}).get('suppliers', [])
                
                for supplier in suppliers:
                    supplier_name = supplier.get('name', 'Desconocido')
                    amount = supplier.get('amount', 0)
                    
                    if supplier_name not in supplier_totals:
                        supplier_totals[supplier_name] = 0
                    
                    supplier_totals[supplier_name] += amount
                    total_payments += amount
            
            # Crear ranking
            suppliers_analysis['total_suppliers'] = len(supplier_totals)
            suppliers_analysis['total_payments'] = total_payments
            
            if len(supplier_totals) > 0:
                suppliers_analysis['average_payment'] = total_payments / len(supplier_totals)
                
                # Top 5 proveedores
                sorted_suppliers = sorted(supplier_totals.items(), key=lambda x: x[1], reverse=True)
                suppliers_analysis['top_suppliers'] = sorted_suppliers[:5]
            
            return suppliers_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analizando proveedores: {e}")
            return {}
    
    def _generate_forecasts(self) -> Dict:
        """Genera previsiones"""
        try:
            forecasts = {
                'next_month_sales': 0,
                'next_month_expenses': 0,
                'next_month_profit': 0,
                'confidence_level': 'medium',
                'assumptions': []
            }
            
            if len(self.processed_data) < 2:
                return forecasts
            
            # Obtener datos históricos
            monthly_breakdown = self._get_monthly_breakdown()
            
            sales_values = []
            expense_values = []
            
            for month_data in monthly_breakdown.values():
                sales_values.append(month_data['sales'])
                expense_values.append(month_data['expenses'])
            
            # Previsión simple (promedio móvil)
            if len(sales_values) >= 3:
                forecasts['next_month_sales'] = np.mean(sales_values[-3:])
                forecasts['next_month_expenses'] = np.mean(expense_values[-3:])
                forecasts['next_month_profit'] = forecasts['next_month_sales'] - forecasts['next_month_expenses']
                
                forecasts['confidence_level'] = 'high'
                forecasts['assumptions'] = [
                    'Basado en promedio de últimos 3 meses',
                    'Sin cambios estacionales significativos',
                    'Manteniendo tendencia actual de la carnicería'
                ]
            
            return forecasts
            
        except Exception as e:
            logger.error(f"❌ Error generando previsiones: {e}")
            return {}

# Función de conveniencia
def analyze_carniceria_excel(file_path: str) -> ExcelReader:
    """Analiza el Excel de la carnicería"""
    reader = ExcelReader()
    if reader.load_excel(file_path):
        return reader
    else:
        raise Exception("Error analizando Excel de carnicería")

if __name__ == "__main__":
    # Test del lector
    print("🧪 Test Lector Excel Carnicería")
    
    reader = ExcelReader()
    print("✅ Lector creado")
    
    # Test de tendencias
    test_values = [1000, 1200, 1100, 1300, 1400]
    trend = reader._determine_trend(test_values)
    print(f"📈 Tendencia test: {trend}")
    
    print("✅ Test completado")
