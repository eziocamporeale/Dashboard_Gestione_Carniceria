#!/usr/bin/env python3
"""
Analizador Específico para Datos de Carnicería
Analiza los datos del Excel de gestión de la carnicería
Basado en la estructura real del Excel proporcionado
Creado por Ezio Camporeale
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Configurar logging
logger = logging.getLogger(__name__)

class CarniceriaAnalyzer:
    """Analizador específico para datos de carnicería"""
    
    def __init__(self):
        self.raw_data = None
        self.processed_data = None
        self.monthly_data = {}
        self.daily_data = {}
        self.suppliers_data = {}
        
    def load_carniceria_data(self, file_path: str) -> bool:
        """
        Carga los datos específicos del Excel de la carnicería
        
        Args:
            file_path: Ruta del archivo Excel
            
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            # Cargar el Excel con todas las hojas
            self.raw_data = pd.read_excel(file_path, sheet_name=None)
            
            # Procesar cada hoja según su estructura
            self._process_carniceria_sheets()
            
            logger.info(f"✅ Datos de carnicería cargados: {len(self.raw_data)} hojas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos de carnicería: {e}")
            return False
    
    def _process_carniceria_sheets(self):
        """Procesa las hojas específicas del Excel de carnicería"""
        try:
            for sheet_name, sheet_data in self.raw_data.items():
                logger.info(f"📊 Procesando hoja de carnicería: {sheet_name}")
                
                # Procesar según el tipo de hoja
                if 'noviembre' in sheet_name.lower() or 'diciembre' in sheet_name.lower():
                    processed = self._process_monthly_sheet(sheet_name, sheet_data)
                elif 'resumen' in sheet_name.lower() or 'total' in sheet_name.lower():
                    processed = self._process_summary_sheet(sheet_name, sheet_data)
                else:
                    processed = self._process_general_sheet(sheet_name, sheet_data)
                
                if processed:
                    self.monthly_data[sheet_name] = processed
                    
        except Exception as e:
            logger.error(f"❌ Error procesando hojas de carnicería: {e}")
    
    def _process_monthly_sheet(self, sheet_name: str, data: pd.DataFrame) -> Dict:
        """Procesa una hoja mensual específica"""
        try:
            # Limpiar datos
            cleaned_data = self._clean_carniceria_data(data)
            
            # Extraer información específica
            monthly_info = {
                'month': sheet_name,
                'total_sales': self._extract_total_sales(cleaned_data),
                'daily_sales': self._extract_daily_sales(cleaned_data),
                'supplier_payments': self._extract_supplier_payments(cleaned_data),
                'expenses': self._extract_expenses(cleaned_data),
                'profit_analysis': self._calculate_profit_analysis(cleaned_data),
                'transactions_count': len(cleaned_data),
                'date_range': self._get_monthly_date_range(cleaned_data)
            }
            
            return monthly_info
            
        except Exception as e:
            logger.error(f"❌ Error procesando hoja mensual {sheet_name}: {e}")
            return {}
    
    def _clean_carniceria_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpia los datos específicos de la carnicería"""
        try:
            # Remover filas completamente vacías
            cleaned = data.dropna(how='all')
            
            # Remover columnas completamente vacías
            cleaned = cleaned.dropna(axis=1, how='all')
            
            # Convertir tipos de datos específicos
            cleaned = self._convert_carniceria_types(cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos de carnicería: {e}")
            return data
    
    def _convert_carniceria_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convierte tipos de datos específicos de la carnicería"""
        try:
            # Identificar columnas de fechas
            date_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['fecha', 'date', 'venta']):
                    date_columns.append(col)
            
            # Convertir fechas
            for col in date_columns:
                try:
                    data[col] = pd.to_datetime(data[col], errors='coerce')
                except:
                    pass
            
            # Identificar columnas monetarias
            money_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['base', 'igic', 'cobro', 'pago', 'total', 'beneficio']):
                    money_columns.append(col)
            
            # Convertir a numérico
            for col in money_columns:
                try:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                except:
                    pass
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo tipos de carnicería: {e}")
            return data
    
    def _extract_total_sales(self, data: pd.DataFrame) -> Dict:
        """Extrae el total de ventas de los datos"""
        try:
            sales_info = {
                'total_amount': 0,
                'base_amount': 0,
                'igic_amount': 0,
                'net_amount': 0,
                'transaction_count': 0
            }
            
            # Buscar columnas de ventas
            sales_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['base', 'igic', 'cobro', 'total']):
                    sales_columns.append(col)
            
            if sales_columns:
                # Calcular totales
                for col in sales_columns:
                    try:
                        values = pd.to_numeric(data[col], errors='coerce')
                        sales_info['total_amount'] += values.sum()
                        
                        if 'base' in col.lower():
                            sales_info['base_amount'] += values.sum()
                        elif 'igic' in col.lower():
                            sales_info['igic_amount'] += values.sum()
                        elif 'total' in col.lower():
                            sales_info['net_amount'] += values.sum()
                            
                    except:
                        pass
                
                # Contar transacciones
                sales_info['transaction_count'] = len(data)
            
            return sales_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo total de ventas: {e}")
            return {}
    
    def _extract_daily_sales(self, data: pd.DataFrame) -> List[Dict]:
        """Extrae las ventas diarias"""
        try:
            daily_sales = []
            
            # Buscar filas con ventas diarias
            for index, row in data.iterrows():
                try:
                    # Verificar si es una venta diaria - buscar en la columna Nombre
                    if pd.notna(row.iloc[0]) and len(row) > 9:
                        nombre_value = str(row.iloc[9]) if pd.notna(row.iloc[9]) else ""
                        
                        if 'TOTAL DIA' in nombre_value:
                            daily_sale = {
                                'date': row.iloc[1] if len(row) > 1 else None,
                                'amount': row.iloc[2] if len(row) > 2 else 0,
                                'type': 'daily_total'
                            }
                            daily_sales.append(daily_sale)
                            
                except Exception as row_error:
                    continue
            
            return daily_sales
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo ventas diarias: {e}")
            return []
    
    def _extract_supplier_payments(self, data: pd.DataFrame) -> List[Dict]:
        """Extrae los pagos a proveedores"""
        try:
            supplier_payments = []
            
            # Buscar filas con pagos a proveedores
            for index, row in data.iterrows():
                try:
                    # Verificar si es un pago a proveedor - buscar en la columna Nombre
                    if pd.notna(row.iloc[0]) and len(row) > 9:
                        nombre_value = str(row.iloc[9]) if pd.notna(row.iloc[9]) else ""
                        
                        # Si no es "TOTAL DIA" y tiene un nombre de proveedor
                        if 'TOTAL DIA' not in nombre_value and nombre_value.strip() != "":
                            supplier_payment = {
                                'supplier_name': nombre_value,
                                'amount': row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else 0,
                                'date': row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None,
                                'invoice_number': row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else None
                            }
                            supplier_payments.append(supplier_payment)
                            
                except Exception as row_error:
                    continue
            
            return supplier_payments
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo pagos a proveedores: {e}")
            return []
    
    def _extract_expenses(self, data: pd.DataFrame) -> Dict:
        """Extrae los gastos"""
        try:
            expenses_info = {
                'total_expenses': 0,
                'supplier_payments': 0,
                'operational_expenses': 0,
                'other_expenses': 0
            }
            
            # Calcular gastos totales
            supplier_payments = self._extract_supplier_payments(data)
            for payment in supplier_payments:
                expenses_info['supplier_payments'] += payment['amount']
            
            expenses_info['total_expenses'] = expenses_info['supplier_payments']
            
            return expenses_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo gastos: {e}")
            return {}
    
    def _calculate_profit_analysis(self, data: pd.DataFrame) -> Dict:
        """Calcula el análisis de ganancias"""
        try:
            sales_info = self._extract_total_sales(data)
            expenses_info = self._extract_expenses(data)
            
            profit_analysis = {
                'gross_profit': sales_info['total_amount'] - expenses_info['total_expenses'],
                'profit_margin': 0,
                'expense_ratio': 0,
                'net_profit': 0
            }
            
            # Calcular márgenes
            if sales_info['total_amount'] > 0:
                profit_analysis['profit_margin'] = (profit_analysis['gross_profit'] / sales_info['total_amount']) * 100
                profit_analysis['expense_ratio'] = (expenses_info['total_expenses'] / sales_info['total_amount']) * 100
            
            profit_analysis['net_profit'] = profit_analysis['gross_profit']
            
            return profit_analysis
            
        except Exception as e:
            logger.error(f"❌ Error calculando análisis de ganancias: {e}")
            return {}
    
    def _get_monthly_date_range(self, data: pd.DataFrame) -> Dict:
        """Obtiene el rango de fechas del mes"""
        try:
            date_columns = []
            for col in data.columns:
                if 'fecha' in col.lower() or 'date' in col.lower():
                    date_columns.append(col)
            
            if not date_columns:
                return {'start': None, 'end': None, 'days': 0}
            
            # Encontrar fechas válidas
            valid_dates = []
            for col in date_columns:
                dates = pd.to_datetime(data[col], errors='coerce')
                valid_dates.extend(dates.dropna().tolist())
            
            if not valid_dates:
                return {'start': None, 'end': None, 'days': 0}
            
            start_date = min(valid_dates)
            end_date = max(valid_dates)
            days = (end_date - start_date).days
            
            return {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'days': days
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo rango de fechas mensual: {e}")
            return {'start': None, 'end': None, 'days': 0}
    
    def get_comprehensive_analysis(self) -> Dict:
        """Obtiene un análisis completo de todos los datos"""
        try:
            analysis = {
                'overview': self._get_overview(),
                'monthly_breakdown': self._get_monthly_breakdown(),
                'trends': self._calculate_trends(),
                'suppliers_analysis': self._analyze_suppliers(),
                'profitability': self._analyze_profitability(),
                'forecasts': self._generate_forecasts()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis completo: {e}")
            return {}
    
    def _get_overview(self) -> Dict:
        """Obtiene una visión general de los datos"""
        try:
            overview = {
                'total_months': len(self.monthly_data),
                'total_sales': 0,
                'total_expenses': 0,
                'total_profit': 0,
                'total_transactions': 0,
                'date_range': {'start': None, 'end': None}
            }
            
            # Calcular totales
            for month_data in self.monthly_data.values():
                sales = month_data.get('total_sales', {}).get('total_amount', 0)
                expenses = month_data.get('expenses', {}).get('total_expenses', 0)
                transactions = month_data.get('transactions_count', 0)
                
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
            
            for month, data in self.monthly_data.items():
                breakdown[month] = {
                    'sales': data.get('total_sales', {}).get('total_amount', 0),
                    'expenses': data.get('expenses', {}).get('total_expenses', 0),
                    'profit': data.get('profit_analysis', {}).get('gross_profit', 0),
                    'transactions': data.get('transactions_count', 0),
                    'profit_margin': data.get('profit_analysis', {}).get('profit_margin', 0)
                }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo desglose mensual: {e}")
            return {}
    
    def _calculate_trends(self) -> Dict:
        """Calcula las tendencias de los datos"""
        try:
            trends = {
                'sales_trend': 'stable',
                'expense_trend': 'stable',
                'profit_trend': 'stable',
                'growth_rate': 0
            }
            
            if len(self.monthly_data) < 2:
                return trends
            
            # Obtener datos para análisis de tendencias
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
            
            # Analizar pagos por proveedor
            for month_data in self.monthly_data.values():
                supplier_payments = month_data.get('supplier_payments', [])
                
                for payment in supplier_payments:
                    supplier_name = payment.get('supplier_name', 'Desconocido')
                    amount = payment.get('amount', 0)
                    
                    if supplier_name not in supplier_totals:
                        supplier_totals[supplier_name] = 0
                    
                    supplier_totals[supplier_name] += amount
                    total_payments += amount
            
            # Crear ranking de proveedores
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
    
    def _analyze_profitability(self) -> Dict:
        """Analiza la rentabilidad"""
        try:
            profitability = {
                'overall_profit_margin': 0,
                'monthly_profit_margins': {},
                'profit_consistency': 'stable',
                'break_even_point': 0
            }
            
            total_sales = 0
            total_profit = 0
            monthly_margins = []
            
            # Calcular márgenes mensuales
            for month, data in self.monthly_data.items():
                sales = data.get('total_sales', {}).get('total_amount', 0)
                profit = data.get('profit_analysis', {}).get('gross_profit', 0)
                
                if sales > 0:
                    margin = (profit / sales) * 100
                    profitability['monthly_profit_margins'][month] = margin
                    monthly_margins.append(margin)
                
                total_sales += sales
                total_profit += profit
            
            # Calcular margen general
            if total_sales > 0:
                profitability['overall_profit_margin'] = (total_profit / total_sales) * 100
            
            # Analizar consistencia
            if len(monthly_margins) > 1:
                std_dev = np.std(monthly_margins)
                if std_dev < 5:
                    profitability['profit_consistency'] = 'stable'
                elif std_dev < 10:
                    profitability['profit_consistency'] = 'moderate'
                else:
                    profitability['profit_consistency'] = 'variable'
            
            return profitability
            
        except Exception as e:
            logger.error(f"❌ Error analizando rentabilidad: {e}")
            return {}
    
    def _generate_forecasts(self) -> Dict:
        """Genera previsiones basadas en datos históricos"""
        try:
            forecasts = {
                'next_month_sales': 0,
                'next_month_expenses': 0,
                'next_month_profit': 0,
                'confidence_level': 'medium',
                'assumptions': []
            }
            
            if len(self.monthly_data) < 2:
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
    
    def create_visualizations(self) -> Dict:
        """Crea visualizaciones de los datos"""
        try:
            visualizations = {
                'sales_trend_chart': None,
                'profit_margin_chart': None,
                'suppliers_chart': None,
                'monthly_comparison_chart': None
            }
            
            # Crear gráfico de tendencia de ventas
            monthly_breakdown = self._get_monthly_breakdown()
            if monthly_breakdown:
                df = pd.DataFrame(monthly_breakdown).T
                
                # Gráfico de tendencia de ventas
                fig_sales = px.line(
                    df, 
                    x=df.index, 
                    y='sales',
                    title='Tendencia de Ventas Mensuales',
                    labels={'sales': 'Ventas ($)', 'index': 'Mes'}
                )
                visualizations['sales_trend_chart'] = fig_sales
                
                # Gráfico de margen de ganancia
                fig_profit = px.bar(
                    df,
                    x=df.index,
                    y='profit_margin',
                    title='Margen de Ganancia Mensual (%)',
                    labels={'profit_margin': 'Margen (%)', 'index': 'Mes'}
                )
                visualizations['profit_margin_chart'] = fig_profit
            
            # Crear gráfico de proveedores
            suppliers_analysis = self._analyze_suppliers()
            if suppliers_analysis['top_suppliers']:
                suppliers_df = pd.DataFrame(
                    suppliers_analysis['top_suppliers'], 
                    columns=['Proveedor', 'Monto']
                )
                
                fig_suppliers = px.pie(
                    suppliers_df,
                    values='Monto',
                    names='Proveedor',
                    title='Distribución de Pagos a Proveedores'
                )
                visualizations['suppliers_chart'] = fig_suppliers
            
            return visualizations
            
        except Exception as e:
            logger.error(f"❌ Error creando visualizaciones: {e}")
            return {}

# ===== FUNCIONES DE CONVENIENCIA =====

def analyze_carniceria_excel(file_path: str) -> CarniceriaAnalyzer:
    """Analiza el Excel de la carnicería y retorna el analizador"""
    analyzer = CarniceriaAnalyzer()
    if analyzer.load_carniceria_data(file_path):
        return analyzer
    else:
        raise Exception("Error analizando Excel de carnicería")

def get_carniceria_summary(file_path: str) -> Dict:
    """Obtiene un resumen rápido del Excel de la carnicería"""
    try:
        analyzer = analyze_carniceria_excel(file_path)
        return analyzer.get_comprehensive_analysis()
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen de carnicería: {e}")
        return {}

if __name__ == "__main__":
    # Test del analizador
    print("🧪 Test Analizador Carnicería")
    
    # Test con datos de ejemplo
    analyzer = CarniceriaAnalyzer()
    print("✅ Analizador creado")
    
    # Test de tendencias
    test_values = [1000, 1200, 1100, 1300, 1400]
    trend = analyzer._determine_trend(test_values)
    print(f"📈 Tendencia test: {trend}")
    
    print("✅ Test completado")
