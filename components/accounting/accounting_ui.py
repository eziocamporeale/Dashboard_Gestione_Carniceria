#!/usr/bin/env python3
"""
Interfaccia Utente per la Gestione Accounting
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Aggiungi il percorso del progetto al Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.hybrid_database_manager import get_hybrid_manager

class AccountingUI:
    """Interfaccia utente per la gestione accounting"""
    
    def __init__(self):
        self.db = get_hybrid_manager()
    
    def render_accounting_page(self):
        """Renderizza la pagina principale dell'accounting"""
        st.header("💰 Gestione Contabilità")
        
        # Tabs per le diverse operazioni
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", "💰 Entrate", "💸 Uscite", "📈 Report", "🏷️ Categorie"
        ])
        
        with tab1:
            self._render_accounting_dashboard()
        
        with tab2:
            self._render_income_management()
        
        with tab3:
            self._render_expense_management()
        
        with tab4:
            self._render_reports()
        
        with tab5:
            self._render_categories_management()
    
    def _render_accounting_dashboard(self):
        """Renderizza la dashboard contabilità"""
        st.subheader("📊 Dashboard Contabilità")
        
        # Selezione periodo
        col1, col2 = st.columns(2)
        
        with col1:
            period = st.selectbox(
                "Periodo",
                ["Oggi", "Settimana", "Mese", "Anno"],
                key="accounting_period"
            )
        
        with col2:
            if period == "Oggi":
                selected_date = st.date_input("Data", value=date.today())
            elif period == "Settimana":
                week_start = date.today() - timedelta(days=7)
                selected_date = st.date_input("Data inizio settimana", value=week_start)
            elif period == "Mese":
                month_start = date.today().replace(day=1)
                selected_date = st.date_input("Data inizio mese", value=month_start)
            else:  # Anno
                year_start = date.today().replace(month=1, day=1)
                selected_date = st.date_input("Data inizio anno", value=year_start)
        
        # Recupera statistiche
        if period == "Oggi":
            stats = self._get_daily_stats(selected_date)
        elif period == "Settimana":
            stats = self._get_weekly_stats(selected_date)
        elif period == "Mese":
            stats = self._get_monthly_stats(selected_date.year, selected_date.month)
        else:  # Anno
            stats = self._get_yearly_stats(selected_date.year)
        
        # Mostra metriche
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 Entrate",
                    value=f"${stats.get('total_income', 0):,.2f}",
                    delta=f"+{stats.get('income_count', 0)} transazioni"
                )
            
            with col2:
                st.metric(
                    label="💸 Uscite",
                    value=f"${stats.get('total_expenses', 0):,.2f}",
                    delta=f"+{stats.get('expense_count', 0)} transazioni"
                )
            
            with col3:
                net_profit = stats.get('total_income', 0) - stats.get('total_expenses', 0)
                st.metric(
                    label="📈 Profitto Netto",
                    value=f"${net_profit:,.2f}",
                    delta=f"{stats.get('profit_margin', 0):.1f}% margine"
                )
            
            with col4:
                st.metric(
                    label="📊 Transazioni",
                    value=stats.get('total_transactions', 0),
                    delta=f"{stats.get('transactions_count', 0)} oggi"
                )
        
        # Grafici
        if period == "Settimana" or period == "Mese":
            self._render_period_charts(period, selected_date)
    
    def _render_income_management(self):
        """Renderizza la gestione entrate"""
        st.subheader("💰 Gestione Entrate")
        
        # Form per aggiungere entrata
        with st.expander("➕ Aggiungi Nuova Entrata", expanded=True):
            with st.form("add_income_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    income_date = st.date_input("Data", value=date.today())
                    amount = st.number_input("Importo ($)", min_value=0.01, step=0.01, format="%.2f")
                    category = st.selectbox("Categoria", self._get_income_categories())
                
                with col2:
                    description = st.text_area("Descrizione", placeholder="Descrizione dell'entrata...")
                    payment_method = st.selectbox("Metodo Pagamento", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
                
                submitted = st.form_submit_button("💰 Aggiungi Entrata", type="primary")
                
                if submitted:
                    success, message = self._add_income(
                        income_date, amount, category, description, payment_method
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        # Lista entrate recenti
        st.subheader("📋 Entrate Recenti")
        
        recent_income = self._get_recent_income()
        
        if recent_income:
            df = pd.DataFrame(recent_income)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                df[['date', 'amount', 'category', 'description', 'payment_method']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ℹ️ Nessuna entrata registrata")
    
    def _render_expense_management(self):
        """Renderizza la gestione uscite"""
        st.subheader("💸 Gestione Uscite")
        
        # Form per aggiungere uscita
        with st.expander("➕ Aggiungi Nuova Uscita", expanded=True):
            with st.form("add_expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_date = st.date_input("Data", value=date.today())
                    amount = st.number_input("Importo ($)", min_value=0.01, step=0.01, format="%.2f")
                    category = st.selectbox("Categoria", self._get_expense_categories())
                
                with col2:
                    description = st.text_area("Descrizione", placeholder="Descrizione dell'uscita...")
                    supplier = st.text_input("Fornitore", placeholder="Nome del fornitore...")
                    payment_method = st.selectbox("Metodo Pagamento", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
                
                submitted = st.form_submit_button("💸 Aggiungi Uscita", type="primary")
                
                if submitted:
                    success, message = self._add_expense(
                        expense_date, amount, category, description, supplier, payment_method
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        # Lista uscite recenti
        st.subheader("📋 Uscite Recenti")
        
        recent_expenses = self._get_recent_expenses()
        
        if recent_expenses:
            df = pd.DataFrame(recent_expenses)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                df[['date', 'amount', 'category', 'description', 'supplier', 'payment_method']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ℹ️ Nessuna uscita registrata")
    
    def _render_reports(self):
        """Renderizza i report contabilità"""
        st.subheader("📈 Report Contabilità")
        
        # Filtri periodo
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Data Inizio", value=date.today() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("Data Fine", value=date.today())
        
        # Tipi di report
        report_type = st.selectbox(
            "Tipo Report",
            ["Riepilogo Giornaliero", "Analisi Categorie", "Trend Temporale"]
        )
        
        if st.button("📊 Genera Report"):
            if report_type == "Riepilogo Giornaliero":
                self._render_daily_report(start_date, end_date)
            elif report_type == "Analisi Categorie":
                self._render_category_analysis(start_date, end_date)
            elif report_type == "Trend Temporale":
                self._render_trend_analysis(start_date, end_date)
    
    def _render_categories_management(self):
        """Renderizza la gestione categorie"""
        st.subheader("🏷️ Gestione Categorie")
        
        # Tabs per income/expense
        cat_tab1, cat_tab2 = st.tabs(["💰 Categorie Entrate", "💸 Categorie Uscite"])
        
        with cat_tab1:
            self._render_income_categories()
        
        with cat_tab2:
            self._render_expense_categories()
    
    def _get_income_categories(self) -> List[str]:
        """Recupera categorie entrate"""
        try:
            categories = self.db.get_accounting_categories('income')
            return [cat['name'] for cat in categories] if categories else ['Ventas', 'Servicios']
        except:
            return ['Ventas', 'Servicios', 'Otros Ingresos']
    
    def _get_expense_categories(self) -> List[str]:
        """Recupera categorie uscite"""
        try:
            categories = self.db.get_accounting_categories('expense')
            return [cat['name'] for cat in categories] if categories else ['Compra Carnes', 'Gastos Operativos']
        except:
            return ['Compra Carnes', 'Gastos Operativos', 'Otros Gastos']
    
    def _add_income(self, date_val, amount, category, description, payment_method) -> tuple:
        """Aggiunge una nuova entrata"""
        try:
            income_data = {
                'date': date_val.isoformat(),
                'amount': float(amount),
                'category': category,
                'description': description,
                'payment_method': payment_method
            }
            
            result = self.db.supabase_manager.insert('daily_income', income_data)
            
            if result:
                return True, f"✅ Entrata di ${amount:,.2f} aggiunta con successo!"
            else:
                return False, "❌ Errore durante l'aggiunta dell'entrata"
                
        except Exception as e:
            return False, f"❌ Errore: {str(e)}"
    
    def _add_expense(self, date_val, amount, category, description, supplier, payment_method) -> tuple:
        """Aggiunge una nuova uscita"""
        try:
            expense_data = {
                'date': date_val.isoformat(),
                'amount': float(amount),
                'category': category,
                'description': description,
                'supplier': supplier,
                'payment_method': payment_method
            }
            
            result = self.db.supabase_manager.insert('daily_expenses', expense_data)
            
            if result:
                return True, f"✅ Uscita di ${amount:,.2f} aggiunta con successo!"
            else:
                return False, "❌ Errore durante l'aggiunta dell'uscita"
                
        except Exception as e:
            return False, f"❌ Errore: {str(e)}"
    
    def _get_recent_income(self, limit: int = 10) -> List[Dict]:
        """Recupera entrate recenti"""
        try:
            return self.db.supabase_manager.select(
                'daily_income',
                order_by='date.desc',
                limit=limit
            )
        except:
            return []
    
    def _get_recent_expenses(self, limit: int = 10) -> List[Dict]:
        """Recupera uscite recenti"""
        try:
            return self.db.supabase_manager.select(
                'daily_expenses',
                order_by='date.desc',
                limit=limit
            )
        except:
            return []
    
    def _get_daily_stats(self, date_val) -> Dict:
        """Recupera statistiche giornaliere"""
        try:
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date': date_val.isoformat()}
            )
            
            if reports:
                return reports[0]
            
            # Calcola statistiche manualmente se non ci sono report
            income = self.db.supabase_manager.select(
                'daily_income',
                filters={'date': date_val.isoformat()}
            )
            
            expenses = self.db.supabase_manager.select(
                'daily_expenses',
                filters={'date': date_val.isoformat()}
            )
            
            total_income = sum([i['amount'] for i in income]) if income else 0
            total_expenses = sum([e['amount'] for e in expenses]) if expenses else 0
            
            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'income_count': len(income),
                'expense_count': len(expenses),
                'total_transactions': len(income) + len(expenses)
            }
            
        except:
            return {}
    
    def _get_weekly_stats(self, start_date) -> Dict:
        """Recupera statistiche settimanali"""
        try:
            end_date = (start_date + timedelta(days=7)).isoformat()
            start_date_str = start_date.isoformat()
            
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date__gte': start_date_str, 'date__lte': end_date}
            )
            
            if reports:
                total_income = sum([r['total_income'] for r in reports])
                total_expenses = sum([r['total_expenses'] for r in reports])
                total_transactions = sum([r['transactions_count'] for r in reports])
                
                return {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'total_transactions': total_transactions
                }
            
            return {}
            
        except:
            return {}
    
    def _get_monthly_stats(self, year, month) -> Dict:
        """Recupera statistiche mensili"""
        try:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date__gte': start_date, 'date__lt': end_date}
            )
            
            if reports:
                total_income = sum([r['total_income'] for r in reports])
                total_expenses = sum([r['total_expenses'] for r in reports])
                total_transactions = sum([r['transactions_count'] for r in reports])
                
                return {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'total_transactions': total_transactions
                }
            
            return {}
            
        except:
            return {}
    
    def _get_yearly_stats(self, year) -> Dict:
        """Recupera statistiche annuali"""
        try:
            start_date = f"{year}-01-01"
            end_date = f"{year + 1}-01-01"
            
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date__gte': start_date, 'date__lt': end_date}
            )
            
            if reports:
                total_income = sum([r['total_income'] for r in reports])
                total_expenses = sum([r['total_expenses'] for r in reports])
                total_transactions = sum([r['transactions_count'] for r in reports])
                
                return {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'total_transactions': total_transactions
                }
            
            return {}
            
        except:
            return {}
    
    def _render_period_charts(self, period, selected_date):
        """Renderizza grafici per il periodo"""
        st.subheader("📊 Grafici Periodo")
        
        try:
            if period == "Settimana":
                end_date = selected_date + timedelta(days=7)
                reports = self.db.supabase_manager.select(
                    'daily_reports',
                    filters={'date__gte': selected_date.isoformat(), 'date__lte': end_date.isoformat()},
                    order_by='date'
                )
            else:  # Mese
                start_date = selected_date.replace(day=1)
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1)
                
                reports = self.db.supabase_manager.select(
                    'daily_reports',
                    filters={'date__gte': start_date.isoformat(), 'date__lt': end_date.isoformat()},
                    order_by='date'
                )
            
            if reports:
                df = pd.DataFrame(reports)
                df['date'] = pd.to_datetime(df['date'])
                
                # Grafico entrate/uscite
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['total_income'],
                    mode='lines+markers',
                    name='Entrate',
                    line=dict(color='#00CC96')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['total_expenses'],
                    mode='lines+markers',
                    name='Uscite',
                    line=dict(color='#FF6692')
                ))
                
                fig.update_layout(
                    title=f"Entrate vs Uscite - {period}",
                    xaxis_title="Data",
                    yaxis_title="Importo ($)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Nessun dato disponibile per il periodo selezionato")
                
        except Exception as e:
            st.error(f"❌ Errore generando grafici: {e}")
    
    def _render_daily_report(self, start_date, end_date):
        """Renderizza report giornaliero"""
        st.subheader(f"📋 Report Giornaliero ({start_date} - {end_date})")
        
        try:
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date__gte': start_date.isoformat(), 'date__lte': end_date.isoformat()},
                order_by='date'
            )
            
            if reports:
                df = pd.DataFrame(reports)
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                df['total_income'] = df['total_income'].apply(lambda x: f"${x:,.2f}")
                df['total_expenses'] = df['total_expenses'].apply(lambda x: f"${x:,.2f}")
                df['net_profit'] = df['net_profit'].apply(lambda x: f"${x:,.2f}")
                df['profit_margin'] = df['profit_margin'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(
                    df[['date', 'total_income', 'total_expenses', 'net_profit', 'profit_margin', 'transactions_count']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Nessun dato disponibile per il periodo selezionato")
                
        except Exception as e:
            st.error(f"❌ Errore generando report: {e}")
    
    def _render_category_analysis(self, start_date, end_date):
        """Renderizza analisi categorie"""
        st.subheader(f"📊 Analisi per Categorie ({start_date} - {end_date})")
        
        try:
            # Entrate per categoria
            income = self.db.supabase_manager.select(
                'daily_income',
                filters={'date__gte': start_date.isoformat(), 'date__lte': end_date.isoformat()}
            )
            
            if income:
                income_df = pd.DataFrame(income)
                income_by_category = income_df.groupby('category')['amount'].sum().reset_index()
                
                fig = px.pie(
                    income_by_category,
                    values='amount',
                    names='category',
                    title='Distribuzione Entrate per Categoria'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Uscite per categoria
            expenses = self.db.supabase_manager.select(
                'daily_expenses',
                filters={'date__gte': start_date.isoformat(), 'date__lte': end_date.isoformat()}
            )
            
            if expenses:
                expenses_df = pd.DataFrame(expenses)
                expenses_by_category = expenses_df.groupby('category')['amount'].sum().reset_index()
                
                fig = px.pie(
                    expenses_by_category,
                    values='amount',
                    names='category',
                    title='Distribuzione Uscite per Categoria'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            if not income and not expenses:
                st.info("ℹ️ Nessun dato disponibile per il periodo selezionato")
                
        except Exception as e:
            st.error(f"❌ Errore generando analisi: {e}")
    
    def _render_trend_analysis(self, start_date, end_date):
        """Renderizza analisi trend"""
        st.subheader(f"📈 Analisi Trend ({start_date} - {end_date})")
        
        try:
            reports = self.db.supabase_manager.select(
                'daily_reports',
                filters={'date__gte': start_date.isoformat(), 'date__lte': end_date.isoformat()},
                order_by='date'
            )
            
            if reports:
                df = pd.DataFrame(reports)
                df['date'] = pd.to_datetime(df['date'])
                
                # Grafico trend profitto
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['net_profit'],
                    mode='lines+markers',
                    name='Profitto Netto',
                    line=dict(color='#636EFA')
                ))
                
                fig.update_layout(
                    title="Trend Profitto Netto",
                    xaxis_title="Data",
                    yaxis_title="Profitto ($)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Nessun dato disponibile per il periodo selezionato")
                
        except Exception as e:
            st.error(f"❌ Errore generando trend: {e}")
    
    def _render_income_categories(self):
        """Renderizza gestione categorie entrate"""
        st.write("💰 Categorie Entrate Attive:")
        
        try:
            categories = self.db.get_accounting_categories('income')
            
            if categories:
                for cat in categories:
                    st.write(f"• {cat.get('icon', '💰')} {cat.get('name', 'N/A')}")
            else:
                st.info("ℹ️ Nessuna categoria entrate configurata")
                
        except Exception as e:
            st.error(f"❌ Errore caricando categorie: {e}")
    
    def _render_expense_categories(self):
        """Renderizza gestione categorie uscite"""
        st.write("💸 Categorie Uscite Attive:")
        
        try:
            categories = self.db.get_accounting_categories('expense')
            
            if categories:
                for cat in categories:
                    st.write(f"• {cat.get('icon', '💸')} {cat.get('name', 'N/A')}")
            else:
                st.info("ℹ️ Nessuna categoria uscite configurata")
                
        except Exception as e:
            st.error(f"❌ Errore caricando categorie: {e}")

def render_accounting_page():
    """Funzione principale per renderizzare la pagina accounting"""
    ui = AccountingUI()
    ui.render_accounting_page()
