#!/usr/bin/env python3
"""
Procesador de Datos Excel para Dashboard Gestión Carnicería
Procesa y analiza los datos históricos del Excel de gestión
Creado por Ezio Camporeale
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import streamlit as st

# Configurar logging
logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Procesador de datos del Excel de gestión de carnicería"""
    
    def __init__(self):
        self.data = None
        self.processed_data = None
        self.monthly_data = {}
        self.yearly_data = {}
        
    def load_excel_data(self, file_path: str) -> bool:
        """
        Carga los datos del Excel
        
        Args:
            file_path: Ruta del archivo Excel
            
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            # Cargar el Excel
            self.data = pd.read_excel(file_path, sheet_name=None)
            
            # Procesar cada hoja
            self._process_all_sheets()
            
            logger.info(f"✅ Excel cargado correctamente: {len(self.data)} hojas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando Excel: {e}")
            return False
    
    def _process_all_sheets(self):
        """Procesa todas las hojas del Excel"""
        try:
            for sheet_name, sheet_data in self.data.items():
                logger.info(f"📊 Procesando hoja: {sheet_name}")
                
                # Procesar datos de la hoja
                processed_sheet = self._process_sheet(sheet_name, sheet_data)
                
                if processed_sheet:
                    self.monthly_data[sheet_name] = processed_sheet
                    
        except Exception as e:
            logger.error(f"❌ Error procesando hojas: {e}")
    
    def _process_sheet(self, sheet_name: str, sheet_data: pd.DataFrame) -> Optional[Dict]:
        """
        Procesa una hoja específica del Excel
        
        Args:
            sheet_name: Nombre de la hoja
            sheet_data: Datos de la hoja
            
        Returns:
            Dict con datos procesados o None si hay error
        """
        try:
            # Limpiar datos
            cleaned_data = self._clean_sheet_data(sheet_data)
            
            if cleaned_data.empty:
                return None
            
            # Extraer información de la hoja
            sheet_info = self._extract_sheet_info(sheet_name, cleaned_data)
            
            return sheet_info
            
        except Exception as e:
            logger.error(f"❌ Error procesando hoja {sheet_name}: {e}")
            return None
    
    def _clean_sheet_data(self, sheet_data: pd.DataFrame) -> pd.DataFrame:
        """Limpia los datos de una hoja"""
        try:
            # Remover filas vacías
            cleaned = sheet_data.dropna(how='all')
            
            # Remover columnas vacías
            cleaned = cleaned.dropna(axis=1, how='all')
            
            # Convertir tipos de datos
            cleaned = self._convert_data_types(cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos: {e}")
            return sheet_data
    
    def _convert_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convierte tipos de datos"""
        try:
            # Identificar columnas de fechas
            date_columns = []
            for col in data.columns:
                if 'fecha' in col.lower() or 'date' in col.lower():
                    date_columns.append(col)
            
            # Convertir fechas
            for col in date_columns:
                try:
                    data[col] = pd.to_datetime(data[col], errors='coerce')
                except:
                    pass
            
            # Identificar columnas numéricas
            numeric_columns = []
            for col in data.columns:
                if data[col].dtype == 'object':
                    try:
                        # Intentar convertir a numérico
                        pd.to_numeric(data[col], errors='coerce')
                        numeric_columns.append(col)
                    except:
                        pass
            
            # Convertir a numérico
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo tipos: {e}")
            return data
    
    def _extract_sheet_info(self, sheet_name: str, data: pd.DataFrame) -> Dict:
        """Extrae información específica de una hoja"""
        try:
            info = {
                'sheet_name': sheet_name,
                'total_rows': len(data),
                'total_columns': len(data.columns),
                'date_range': self._get_date_range(data),
                'sales_data': self._extract_sales_data(data),
                'expense_data': self._extract_expense_data(data),
                'summary': self._create_summary(data)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo información de {sheet_name}: {e}")
            return {}
    
    def _get_date_range(self, data: pd.DataFrame) -> Dict:
        """Obtiene el rango de fechas de los datos"""
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
            logger.error(f"❌ Error obteniendo rango de fechas: {e}")
            return {'start': None, 'end': None, 'days': 0}
    
    def _extract_sales_data(self, data: pd.DataFrame) -> Dict:
        """Extrae datos de ventas"""
        try:
            sales_info = {
                'total_sales': 0,
                'daily_sales': [],
                'monthly_sales': {},
                'top_products': [],
                'sales_trend': 'stable'
            }
            
            # Buscar columnas de ventas
            sales_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['venta', 'cobro', 'total', 'ingreso']):
                    sales_columns.append(col)
            
            if sales_columns:
                # Calcular total de ventas
                for col in sales_columns:
                    try:
                        sales_values = pd.to_numeric(data[col], errors='coerce')
                        sales_info['total_sales'] += sales_values.sum()
                    except:
                        pass
            
            return sales_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de ventas: {e}")
            return {}
    
    def _extract_expense_data(self, data: pd.DataFrame) -> Dict:
        """Extrae datos de gastos"""
        try:
            expense_info = {
                'total_expenses': 0,
                'expense_categories': {},
                'monthly_expenses': {},
                'expense_trend': 'stable'
            }
            
            # Buscar columnas de gastos
            expense_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['gasto', 'compra', 'pago', 'egreso']):
                    expense_columns.append(col)
            
            if expense_columns:
                # Calcular total de gastos
                for col in expense_columns:
                    try:
                        expense_values = pd.to_numeric(data[col], errors='coerce')
                        expense_info['total_expenses'] += expense_values.sum()
                    except:
                        pass
            
            return expense_info
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de gastos: {e}")
            return {}
    
    def _create_summary(self, data: pd.DataFrame) -> Dict:
        """Crea un resumen de los datos"""
        try:
            summary = {
                'total_transactions': len(data),
                'data_quality': 'good',
                'missing_data': data.isnull().sum().sum(),
                'duplicate_rows': data.duplicated().sum(),
                'columns_info': {}
            }
            
            # Información de columnas
            for col in data.columns:
                summary['columns_info'][col] = {
                    'type': str(data[col].dtype),
                    'non_null_count': data[col].count(),
                    'null_count': data[col].isnull().sum(),
                    'unique_values': data[col].nunique()
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error creando resumen: {e}")
            return {}
    
    def get_monthly_summary(self) -> Dict:
        """Obtiene resumen mensual de todos los datos"""
        try:
            summary = {
                'total_months': len(self.monthly_data),
                'total_sales': 0,
                'total_expenses': 0,
                'net_profit': 0,
                'monthly_breakdown': {},
                'trends': {}
            }
            
            # Procesar cada mes
            for month, data in self.monthly_data.items():
                month_summary = {
                    'month': month,
                    'sales': data.get('sales_data', {}).get('total_sales', 0),
                    'expenses': data.get('expense_data', {}).get('total_expenses', 0),
                    'profit': 0,
                    'transactions': data.get('total_rows', 0)
                }
                
                # Calcular ganancia
                month_summary['profit'] = month_summary['sales'] - month_summary['expenses']
                
                # Agregar al total
                summary['total_sales'] += month_summary['sales']
                summary['total_expenses'] += month_summary['expenses']
                summary['net_profit'] += month_summary['profit']
                
                summary['monthly_breakdown'][month] = month_summary
            
            # Calcular tendencias
            summary['trends'] = self._calculate_trends(summary['monthly_breakdown'])
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen mensual: {e}")
            return {}
    
    def _calculate_trends(self, monthly_data: Dict) -> Dict:
        """Calcula tendencias de los datos mensuales"""
        try:
            trends = {
                'sales_trend': 'stable',
                'expense_trend': 'stable',
                'profit_trend': 'stable',
                'growth_rate': 0
            }
            
            if len(monthly_data) < 2:
                return trends
            
            # Convertir a DataFrame para análisis
            df = pd.DataFrame(monthly_data).T
            
            # Calcular tendencias
            if 'sales' in df.columns:
                sales_values = df['sales'].values
                if len(sales_values) > 1:
                    trends['sales_trend'] = self._determine_trend(sales_values)
            
            if 'expenses' in df.columns:
                expense_values = df['expenses'].values
                if len(expense_values) > 1:
                    trends['expense_trend'] = self._determine_trend(expense_values)
            
            if 'profit' in df.columns:
                profit_values = df['profit'].values
                if len(profit_values) > 1:
                    trends['profit_trend'] = self._determine_trend(profit_values)
            
            # Calcular tasa de crecimiento
            if 'sales' in df.columns and len(df['sales']) > 1:
                first_sales = df['sales'].iloc[0]
                last_sales = df['sales'].iloc[-1]
                if first_sales > 0:
                    trends['growth_rate'] = ((last_sales - first_sales) / first_sales) * 100
            
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
    
    def get_forecast_data(self, months_ahead: int = 3) -> Dict:
        """Genera previsiones basadas en datos históricos"""
        try:
            forecast = {
                'forecast_months': months_ahead,
                'predicted_sales': [],
                'predicted_expenses': [],
                'predicted_profit': [],
                'confidence_level': 'medium',
                'assumptions': []
            }
            
            if not self.monthly_data:
                return forecast
            
            # Obtener datos históricos
            historical_sales = []
            historical_expenses = []
            
            for month_data in self.monthly_data.values():
                sales = month_data.get('sales_data', {}).get('total_sales', 0)
                expenses = month_data.get('expense_data', {}).get('total_expenses', 0)
                
                historical_sales.append(sales)
                historical_expenses.append(expenses)
            
            # Generar previsiones simples (promedio móvil)
            if len(historical_sales) >= 3:
                # Promedio de los últimos 3 meses
                avg_sales = np.mean(historical_sales[-3:])
                avg_expenses = np.mean(historical_expenses[-3:])
                
                for i in range(months_ahead):
                    forecast['predicted_sales'].append(avg_sales)
                    forecast['predicted_expenses'].append(avg_expenses)
                    forecast['predicted_profit'].append(avg_sales - avg_expenses)
                
                forecast['confidence_level'] = 'high'
                forecast['assumptions'] = [
                    'Basado en promedio de últimos 3 meses',
                    'Sin cambios estacionales significativos',
                    'Manteniendo tendencia actual'
                ]
            
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error generando previsiones: {e}")
            return {}
    
    def export_analysis(self, output_path: str) -> bool:
        """Exporta el análisis a un archivo"""
        try:
            # Crear resumen
            summary = self.get_monthly_summary()
            forecast = self.get_forecast_data()
            
            # Crear DataFrame para exportar
            export_data = {
                'Resumen Mensual': summary,
                'Previsiones': forecast,
                'Datos Procesados': self.monthly_data
            }
            
            # Exportar a JSON
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Análisis exportado a: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando análisis: {e}")
            return False

# ===== FUNCIONES DE CONVENIENCIA =====

def process_excel_file(file_path: str) -> ExcelProcessor:
    """Procesa un archivo Excel y retorna el procesador"""
    processor = ExcelProcessor()
    if processor.load_excel_data(file_path):
        return processor
    else:
        raise Exception("Error procesando archivo Excel")

def get_excel_summary(file_path: str) -> Dict:
    """Obtiene un resumen rápido del Excel"""
    try:
        processor = process_excel_file(file_path)
        return processor.get_monthly_summary()
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen: {e}")
        return {}

if __name__ == "__main__":
    # Test del procesador
    print("🧪 Test Procesador Excel")
    
    # Test con datos de ejemplo
    processor = ExcelProcessor()
    print("✅ Procesador creado")
    
    # Test de tendencias
    test_values = [1000, 1200, 1100, 1300, 1400]
    trend = processor._determine_trend(test_values)
    print(f"📈 Tendencia test: {trend}")
    
    print("✅ Test completado")
