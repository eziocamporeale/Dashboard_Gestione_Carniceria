#!/usr/bin/env python3
"""
Dashboard Gestione Macelleria - Applicazione Principale Streamlit
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# Aggiungi il percorso del progetto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importa i moduli del progetto
from config import APP_NAME, APP_VERSION, APP_AUTHOR, STREAMLIT_CONFIG
from database.database_manager import get_db_manager
from components.auth.auth_manager import (
    get_auth_manager, require_auth, require_permission, 
    render_login_form, render_user_info, render_permission_denied,
    get_current_user, get_user_info, is_authenticated, has_permission
)

# Configurazione Streamlit
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B35;
    }
    
    .alert-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #FF6B35, #F7931E);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #E55A2B, #E0841A);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNZIONI PRINCIPALI =====

def render_header():
    """Renderizza l'header dell'applicazione"""
    st.markdown(f"""
    <div class="main-header">
        <h1>🥩 {APP_NAME}</h1>
        <p>Versione {APP_VERSION} - Creato da {APP_AUTHOR}</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderizza la sidebar con navigazione"""
    with st.sidebar:
        st.title("🧭 Navigazione")
        
        # Informazioni utente
        render_user_info()
        
        st.markdown("---")
        
        # Menu di navigazione
        if is_authenticated():
            user_info = get_user_info()
            
            # Menu principale
            menu_items = [
                ("🏠 Dashboard", "dashboard"),
                ("📦 Inventario", "inventario"),
                ("🛒 Vendite", "vendite"),
                ("👥 Clienti", "clienti"),
                ("🚚 Fornitori", "fornitori"),
                ("👨‍💼 Personale", "personale"),
                ("📊 Analytics", "analytics"),
                ("⚙️ Impostazioni", "settings")
            ]
            
            # Filtra menu in base ai permessi
            available_menu = []
            for item_name, item_key in menu_items:
                if has_permission(item_key) or has_permission("all"):
                    available_menu.append((item_name, item_key))
            
            # Selezione pagina
            selected_page = st.selectbox(
                "Seleziona Sezione",
                [item[0] for item in available_menu],
                key="page_selector"
            )
            
            # Trova la chiave della pagina selezionata
            page_key = None
            for item_name, item_key in available_menu:
                if item_name == selected_page:
                    page_key = item_key
                    break
            
            # Salva la pagina selezionata
            if page_key:
                st.session_state['current_page'] = page_key
            
            st.markdown("---")
            
            # Quick Actions
            st.subheader("⚡ Azioni Rapide")
            
            if has_permission("vendite"):
                if st.button("💰 Nuova Vendita", use_container_width=True):
                    st.session_state['current_page'] = 'vendite'
                    st.rerun()
            
            if has_permission("inventario"):
                if st.button("📦 Aggiungi Prodotto", use_container_width=True):
                    st.session_state['current_page'] = 'inventario'
                    st.rerun()
            
            if has_permission("clienti"):
                if st.button("👥 Nuovo Cliente", use_container_width=True):
                    st.session_state['current_page'] = 'clienti'
                    st.rerun()
            
            st.markdown("---")
            
            # Informazioni sistema
            st.subheader("ℹ️ Sistema")
            st.caption(f"Versione: {APP_VERSION}")
            st.caption(f"Database: Connesso")
            st.caption(f"Utenti attivi: 1")

def render_dashboard():
    """Renderizza la dashboard principale"""
    st.header("🏠 Dashboard Principale")
    
    # Ottieni statistiche
    db = get_db_manager()
    stats = db.get_dashboard_stats()
    
    # KPI principali
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Vendite Oggi",
            value=f"€{stats.get('sales_today', {}).get('total', 0):.2f}",
            delta=f"{stats.get('sales_today', {}).get('count', 0)} transazioni"
        )
    
    with col2:
        st.metric(
            label="📋 Ordini Oggi",
            value=f"{stats.get('orders_today', {}).get('count', 0)}",
            delta=f"€{stats.get('orders_today', {}).get('total', 0):.2f}"
        )
    
    with col3:
        st.metric(
            label="👥 Clienti Totali",
            value=f"{stats.get('total_customers', 0)}",
            delta="Attivi"
        )
    
    with col4:
        st.metric(
            label="📦 Prodotti Totali",
            value=f"{stats.get('total_products', 0)}",
            delta="In catalogo"
        )
    
    st.markdown("---")
    
    # Alert e notifiche
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Alert Scorte")
        
        # Prodotti con scorte basse
        low_stock_products = db.get_products_low_stock()
        if low_stock_products:
            for product in low_stock_products[:5]:  # Mostra solo i primi 5
                st.markdown(f"""
                <div class="alert-card">
                    <strong>📉 {product['name']}</strong><br>
                    Scorte: {product['current_stock']} {product.get('unit_symbol', '')} 
                    (Min: {product['min_stock_level']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Tutte le scorte sono sufficienti")
    
    with col2:
        st.subheader("📅 Scadenze Prossime")
        
        # Prodotti in scadenza
        expiring_products = db.get_products_expiring_soon()
        if expiring_products:
            for product in expiring_products[:5]:  # Mostra solo i primi 5
                st.markdown(f"""
                <div class="alert-card">
                    <strong>⏰ {product['name']}</strong><br>
                    Scade: {product['expiry_date']}<br>
                    Lotto: {product['batch_number']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Nessun prodotto in scadenza")
    
    st.markdown("---")
    
    # Grafici
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vendite Ultimi 7 Giorni")
        
        # Ottieni vendite degli ultimi 7 giorni
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        sales_data = db.get_sales_by_period(start_date, end_date)
        
        if sales_data:
            df_sales = pd.DataFrame(sales_data)
            fig = px.line(
                df_sales, 
                x='date', 
                y='total_revenue',
                title="Andamento Vendite",
                labels={'total_revenue': 'Ricavi (€)', 'date': 'Data'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun dato di vendita disponibile per il periodo selezionato")
    
    with col2:
        st.subheader("🏆 Prodotti Più Venduti")
        
        # Ottieni prodotti più venduti
        top_products = db.get_top_products(limit=5)
        
        if top_products:
            df_products = pd.DataFrame(top_products)
            fig = px.bar(
                df_products,
                x='total_quantity',
                y='name',
                orientation='h',
                title="Top 5 Prodotti",
                labels={'total_quantity': 'Quantità Venduta', 'name': 'Prodotto'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun dato di vendita disponibile")

def render_inventario():
    """Renderizza la sezione inventario"""
    require_permission("inventario")
    
    st.header("📦 Gestione Inventario")
    
    # Tabs per diverse funzionalità
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Panoramica", "➕ Nuovo Prodotto", "📊 Scorte", "⚠️ Alert"])
    
    with tab1:
        st.subheader("📋 Panoramica Prodotti")
        
        # Ottieni tutti i prodotti
        db = get_db_manager()
        products = db.get_all_products()
        
        if products:
            # Crea DataFrame
            df_products = pd.DataFrame(products)
            
            # Filtri
            col1, col2 = st.columns(2)
            with col1:
                category_filter = st.selectbox(
                    "Filtra per Categoria",
                    ["Tutte"] + list(df_products['category_name'].unique())
                )
            
            with col2:
                search_term = st.text_input("🔍 Cerca Prodotto", placeholder="Nome o codice prodotto")
            
            # Applica filtri
            filtered_df = df_products.copy()
            
            if category_filter != "Tutte":
                filtered_df = filtered_df[filtered_df['category_name'] == category_filter]
            
            if search_term:
                mask = filtered_df['name'].str.contains(search_term, case=False, na=False) | \
                       filtered_df['code'].str.contains(search_term, case=False, na=False)
                filtered_df = filtered_df[mask]
            
            # Mostra tabella
            st.dataframe(
                filtered_df[['name', 'code', 'category_name', 'selling_price', 'current_stock', 'min_stock_level']],
                use_container_width=True,
                column_config={
                    "name": "Nome Prodotto",
                    "code": "Codice",
                    "category_name": "Categoria",
                    "selling_price": st.column_config.NumberColumn("Prezzo (€)", format="€%.2f"),
                    "current_stock": "Scorte Attuali",
                    "min_stock_level": "Scorte Minime"
                }
            )
        else:
            st.info("Nessun prodotto trovato. Aggiungi il primo prodotto!")
    
    with tab2:
        st.subheader("➕ Aggiungi Nuovo Prodotto")
        
        with st.form("new_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome Prodotto *", placeholder="es. Tagliata di Manzo")
                code = st.text_input("Codice Prodotto", placeholder="es. MAN001")
                barcode = st.text_input("Codice a Barre", placeholder="es. 1234567890123")
                
                # Categorie
                categories = db.get_product_categories()
                category_options = {cat['name']: cat['id'] for cat in categories}
                selected_category = st.selectbox("Categoria *", list(category_options.keys()))
                category_id = category_options[selected_category]
                
                # Unità di misura
                units = db.get_units_of_measure()
                unit_options = {f"{unit['name']} ({unit['symbol']})": unit['id'] for unit in units}
                selected_unit = st.selectbox("Unità di Misura *", list(unit_options.keys()))
                unit_id = unit_options[selected_unit]
            
            with col2:
                description = st.text_area("Descrizione", placeholder="Descrizione del prodotto")
                brand = st.text_input("Marca", placeholder="es. Brand Name")
                origin = st.text_input("Provenienza", placeholder="es. Italia, Piemonte")
                
                cost_price = st.number_input("Prezzo di Costo (€)", min_value=0.0, step=0.01)
                selling_price = st.number_input("Prezzo di Vendita (€) *", min_value=0.0, step=0.01)
                
                min_stock = st.number_input("Scorte Minime", min_value=0, value=5)
                max_stock = st.number_input("Scorte Massime", min_value=0, value=100)
            
            # Opzioni avanzate
            with st.expander("⚙️ Opzioni Avanzate"):
                shelf_life = st.number_input("Giorni di Conservazione", min_value=0, value=3)
                temp_control = st.checkbox("Richiede Controllo Temperatura")
                
                if temp_control:
                    col_temp1, col_temp2 = st.columns(2)
                    with col_temp1:
                        temp_min = st.number_input("Temperatura Min (°C)", value=2.0)
                    with col_temp2:
                        temp_max = st.number_input("Temperatura Max (°C)", value=4.0)
                else:
                    temp_min = temp_max = None
            
            # Pulsante submit
            if st.form_submit_button("➕ Aggiungi Prodotto", use_container_width=True):
                if not name or not selling_price:
                    st.error("⚠️ Compila tutti i campi obbligatori")
                else:
                    product_data = {
                        'name': name,
                        'code': code,
                        'barcode': barcode,
                        'category_id': category_id,
                        'unit_id': unit_id,
                        'description': description,
                        'brand': brand,
                        'origin': origin,
                        'cost_price': cost_price,
                        'selling_price': selling_price,
                        'min_stock_level': min_stock,
                        'max_stock_level': max_stock,
                        'shelf_life_days': shelf_life,
                        'requires_temperature_control': temp_control,
                        'storage_temperature_min': temp_min,
                        'storage_temperature_max': temp_max,
                        'created_by': get_current_user()['id']
                    }
                    
                    success, result = db.create_product(product_data)
                    
                    if success:
                        st.success(f"✅ Prodotto '{name}' aggiunto con successo!")
                        st.balloons()
                    else:
                        st.error(f"❌ Errore: {result}")
    
    with tab3:
        st.subheader("📊 Gestione Scorte")
        st.info("🚧 Funzionalità in sviluppo - Gestione scorte e inventario")
    
    with tab4:
        st.subheader("⚠️ Alert e Notifiche")
        
        # Prodotti con scorte basse
        low_stock = db.get_products_low_stock()
        if low_stock:
            st.warning(f"⚠️ {len(low_stock)} prodotti con scorte basse")
            for product in low_stock:
                st.write(f"• {product['name']}: {product['current_stock']} (min: {product['min_stock_level']})")
        else:
            st.success("✅ Tutte le scorte sono sufficienti")
        
        # Prodotti in scadenza
        expiring = db.get_products_expiring_soon()
        if expiring:
            st.warning(f"⏰ {len(expiring)} prodotti in scadenza")
            for product in expiring:
                st.write(f"• {product['name']}: scade il {product['expiry_date']}")
        else:
            st.success("✅ Nessun prodotto in scadenza")

def render_vendite():
    """Renderizza la sezione vendite"""
    require_permission("vendite")
    
    st.header("🛒 Gestione Vendite")
    st.info("🚧 Funzionalità in sviluppo - Sistema vendite e POS")

def render_clienti():
    """Renderizza la sezione clienti"""
    require_permission("clienti")
    
    st.header("👥 Gestione Clienti")
    st.info("🚧 Funzionalità in sviluppo - Database clienti e CRM")

def render_fornitori():
    """Renderizza la sezione fornitori"""
    require_permission("fornitori")
    
    try:
        from components.fornitori.suppliers_ui import render_suppliers_page
        render_suppliers_page()
    except ImportError as e:
        st.error(f"❌ Errore nel caricamento del componente fornitori: {e}")
        st.info("🚧 Funzionalità fornitori non disponibile - Contatta l'amministratore")

def render_personale():
    """Renderizza la sezione personale"""
    require_permission("personale")
    
    st.header("👨‍💼 Gestione Personale")
    st.info("🚧 Funzionalità in sviluppo - Gestione dipendenti e turni")

def render_analytics():
    """Renderizza la sezione analytics"""
    require_permission("analytics")
    
    st.header("📊 Analytics e Report")
    st.info("🚧 Funzionalità in sviluppo - Reportistica avanzata e BI")

def render_settings():
    """Renderizza la sezione impostazioni"""
    require_permission("settings")
    
    st.header("⚙️ Impostazioni Sistema")
    st.info("🚧 Funzionalità in sviluppo - Configurazioni e amministrazione")

# ===== FUNZIONE PRINCIPALE =====

def main():
    """Funzione principale dell'applicazione"""
    
    # Renderizza header
    render_header()
    
    # Verifica autenticazione
    if not is_authenticated():
        render_login_form()
        return
    
    # Renderizza sidebar
    render_sidebar()
    
    # Ottieni pagina corrente
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # Renderizza contenuto principale
    try:
        if current_page == 'dashboard':
            render_dashboard()
        elif current_page == 'inventario':
            render_inventario()
        elif current_page == 'vendite':
            render_vendite()
        elif current_page == 'clienti':
            render_clienti()
        elif current_page == 'fornitori':
            render_fornitori()
        elif current_page == 'personale':
            render_personale()
        elif current_page == 'analytics':
            render_analytics()
        elif current_page == 'settings':
            render_settings()
        else:
            render_dashboard()
            
    except Exception as e:
        st.error(f"❌ Errore durante il rendering della pagina: {str(e)}")
        st.exception(e)

# ===== AVVIO APPLICAZIONE =====

if __name__ == "__main__":
    main()

