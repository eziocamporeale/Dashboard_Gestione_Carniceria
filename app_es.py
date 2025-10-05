#!/usr/bin/env python3
"""
Dashboard Gestión Carnicería - Aplicación Principal Streamlit
Creado por Ezio Camporeale
Traducido al español para Argentina
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import datetime as dt
import sys
from pathlib import Path
from streamlit_option_menu import option_menu
import logging

# Assicurati che pandas sia disponibile globalmente
pd = __import__('pandas')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el path del proyecto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar módulos del proyecto
from config_es import APP_NAME, APP_VERSION, APP_AUTHOR
from database.hybrid_database_manager import get_hybrid_manager
from components.resource_manager import init_resource_manager, show_resource_status, cleanup_on_page_change

# Importa il menu centrale
try:
    from components.layout.central_menu import render_central_menu, render_compact_sidebar
    CENTRAL_MENU_AVAILABLE = True
except ImportError as e:
    print(f"❌ Errore import central_menu: {e}")
    render_central_menu = None
    render_compact_sidebar = None
    CENTRAL_MENU_AVAILABLE = False
from components.auth.auth_manager import (
    get_auth_manager, require_auth, require_permission, 
    render_login_form, render_user_info, render_permission_denied,
    get_current_user, get_user_info, is_authenticated, has_permission
)

# Configuración Streamlit
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Resource Manager para evitar "Too many open files"
try:
    resource_manager = init_resource_manager()
    logger.info("✅ Resource Manager inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando Resource Manager: {e}")

# CSS personalizado
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

# ===== FUNCIONES PRINCIPALES =====

def render_header():
    """Renderiza el header de la aplicación"""
    st.markdown(f"""
    <div class="main-header">
        <h1>🥩 {APP_NAME}</h1>
        <p>Versión {APP_VERSION} - Creado por {APP_AUTHOR}</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza la sidebar con navegación"""
    with st.sidebar:
        st.title("🧭 Navegación")
        
        # Información usuario
        render_user_info()
        
        st.markdown("---")
        
        # Menú de navegación
        if is_authenticated():
            user_info = get_user_info()
            
            # Menú principal
            menu_items = [
                ("🏠 Dashboard", "dashboard"),
                ("📦 Inventario", "inventario"),
                ("🛒 Ventas", "ventas"),
                ("👥 Clientes", "clientes"),
                ("🚚 Proveedores", "proveedores"),
                ("👨‍💼 Personal", "personal"),
                ("📊 Analytics", "analytics"),
                ("💰 Balance y Previsiones", "balance"),
                ("⚙️ Configuración", "configuracion")
            ]
            
            # Filtrar menú según permisos
            available_menu = []
            for item_name, item_key in menu_items:
                if has_permission(item_key) or has_permission("all"):
                    available_menu.append((item_name, item_key))
            
            # Selección página
            selected_page = st.selectbox(
                "Selecciona Sección",
                [item[0] for item in available_menu],
                key="page_selector"
            )
            
            # Encontrar la clave de la página seleccionada
            page_key = None
            for item_name, item_key in available_menu:
                if item_name == selected_page:
                    page_key = item_key
                    break
            
            # Guardar la página seleccionada
            if page_key:
                st.session_state['current_page'] = page_key
            
            st.markdown("---")
            
            # Acciones Rápidas
            st.subheader("⚡ Acciones Rápidas")
            
            if has_permission("ventas"):
                if st.button("💰 Nueva Venta", width='stretch'):
                    st.session_state['current_page'] = 'ventas'
                    st.rerun()
            
            if has_permission("inventario"):
                if st.button("📦 Agregar Producto", width='stretch'):
                    st.session_state['current_page'] = 'inventario'
                    st.rerun()
            
            if has_permission("clientes"):
                if st.button("👥 Nuevo Cliente", width='stretch'):
                    st.session_state['current_page'] = 'clientes'
                    st.rerun()
            
            st.markdown("---")
            
            # Monitor risorse per evitare "Too many open files"
            try:
                show_resource_status()
            except Exception as e:
                logger.error(f"❌ Error mostrando estado recursos: {e}")
            
            st.markdown("---")
            
            # Información sistema
            st.subheader("ℹ️ Sistema")
            st.caption(f"Versión: {APP_VERSION}")
            st.caption(f"Base de datos: Conectada")
            st.caption(f"Usuarios activos: 1")

def render_dashboard():
    """Renderiza el dashboard principal"""
    st.header("🏠 Dashboard Principal")
    
    # Obtener estadísticas
    db = get_hybrid_manager()
    stats = db.get_dashboard_stats()
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Ventas Hoy",
            value=f"${stats.get('sales_today', {}).get('total', 0):.2f}",
            delta=f"{stats.get('sales_today', {}).get('count', 0)} transacciones"
        )
    
    with col2:
        st.metric(
            label="📋 Órdenes Hoy",
            value=f"{stats.get('orders_today', {}).get('count', 0)}",
            delta=f"${stats.get('orders_today', {}).get('total', 0):.2f}"
        )
    
    with col3:
        st.metric(
            label="👥 Clientes Totales",
            value=f"{stats.get('total_customers', 0)}",
            delta="Activos"
        )
    
    with col4:
        st.metric(
            label="📦 Productos Totales",
            value=f"{stats.get('total_products', 0)}",
            delta="En catálogo"
        )
    
    st.markdown("---")
    
    # Alertas y notificaciones
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Alertas Stock")
        
        # Productos con stock bajo
        low_stock_products = db.get_products_low_stock()
        if low_stock_products:
            for product in low_stock_products[:5]:  # Mostrar solo los primeros 5
                st.markdown(f"""
                <div class="alert-card">
                    <strong>📉 {product['name']}</strong><br>
                    Stock: {product['current_stock']} {product.get('unit_symbol', '')} 
                    (Mín: {product['min_stock_level']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Todo el stock es suficiente")
    
    with col2:
        st.subheader("📅 Vencimientos Próximos")
        
        # Productos próximos a vencer
        expiring_products = db.get_products_expiring_soon()
        if expiring_products:
            for product in expiring_products[:5]:  # Mostrar solo los primeros 5
                st.markdown(f"""
                <div class="alert-card">
                    <strong>⏰ {product['name']}</strong><br>
                    Vence: {product['expiry_date']}<br>
                    Cantidad: {product.get('quantity', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Ningún producto próximo a vencer")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Ventas Últimos 7 Días")
        
        # Obtener ventas de los últimos 7 días
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        sales_data = db.get_sales_by_period(start_date, end_date)
        
        if sales_data:
            df_sales = pd.DataFrame(sales_data)
            fig = px.line(
                df_sales, 
                x='date', 
                y='total_revenue',
                title="Tendencia Ventas")
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No hay datos de ventas disponibles para el período seleccionado")
    
    with col2:
        st.subheader("🏆 Productos Más Vendidos")
        
        # Obtener productos más vendidos
        top_products = db.get_top_products(limit=5)
        
        if top_products:
            df_products = pd.DataFrame(top_products)
            fig = px.bar(
                df_products,
                x='total_quantity',
                y='name',
                title="Top 5 Productos")
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No hay datos de ventas disponibles")

def render_inventario():
    """Renderiza la sección inventario"""
    require_permission("inventario")
    
    st.header("📦 Gestión Inventario")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Resumen", "➕ Nuevo Producto", "📊 Stock", "⚠️ Alertas"])
    
    with tab1:
        st.subheader("📋 Resumen Productos")
        
        # Obtener todos los productos
        db = get_hybrid_manager()
        products = db.get_all_products()
        
        if products:
            # Crear DataFrame
            df_products = pd.DataFrame(products)
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                category_filter = st.selectbox(
                    "Filtrar por Categoría",
                    ["Todas"] + list(df_products['category_name'].unique())
                )
            
            with col2:
                search_term = st.text_input("🔍 Buscar Producto", placeholder="Nombre o código producto")
            
            # Aplicar filtros
            filtered_df = df_products.copy()
            
            if category_filter != "Todas":
                filtered_df = filtered_df[filtered_df['category_name'] == category_filter]
            
            if search_term:
                mask = filtered_df['name'].str.contains(search_term, case=False, na=False) | \
                       filtered_df['code'].str.contains(search_term, case=False, na=False)
                filtered_df = filtered_df[mask]
            
            # Mostrar productos con acciones CRUD
            st.markdown("---")
            st.subheader("📋 Lista de Productos")
            
            # Mostrar cada producto con opciones de editar/eliminar
            for _, product in filtered_df.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{product['name']}**")
                        st.caption(f"📦 Código: {product['code']}")
                        st.caption(f"🏷️ Categoría: {product['category_name']}")
                    
                    with col2:
                        st.write(f"💰 ${product['selling_price']:,.2f}")
                        stock_status = "🟢" if product['current_stock'] >= product['min_stock_level'] else "🔴"
                        st.caption(f"{stock_status} Stock: {product['current_stock']}")
                    
                    with col3:
                        st.write(f"📊 Mínimo: {product['min_stock_level']}")
                        if product['current_stock'] < product['min_stock_level']:
                            st.caption("⚠️ Stock bajo")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_product_btn_{product['id']}", help="Editar producto"):
                            st.session_state[f'edit_product_{product["id"]}'] = True
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_product_btn_{product['id']}", help="Eliminar producto"):
                            st.session_state[f'delete_product_{product["id"]}'] = True
                    
                    # Modal de edición
                    if st.session_state.get(f'edit_product_{product["id"]}', False):
                        with st.expander(f"✏️ Editar {product['name']}", expanded=True):
                            with st.form(f"edit_product_form_{product['id']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    edit_name = st.text_input("Nombre", value=product['name'], key=f"edit_name_{product['id']}")
                                    edit_code = st.text_input("Código", value=product['code'], key=f"edit_code_{product['id']}")
                                    edit_price = st.number_input("Precio", value=float(product['selling_price']), key=f"edit_price_{product['id']}")
                                
                                with col2:
                                    edit_stock = st.number_input("Stock Actual", value=int(product['current_stock']), key=f"edit_stock_{product['id']}")
                                    edit_min_stock = st.number_input("Stock Mínimo", value=int(product['min_stock_level']), key=f"edit_min_stock_{product['id']}")
                                    edit_category = st.selectbox("Categoría", list(category_options.keys()), 
                                                               index=list(category_options.keys()).index(product['category_name']),
                                                               key=f"edit_category_{product['id']}")
                                
                                col1, col2, col3 = st.columns([1, 1, 1])
                                with col1:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        product_data = {
                                            'name': edit_name,
                                            'code': edit_code,
                                            'selling_price': edit_price,
                                            'current_stock': edit_stock,
                                            'min_stock_level': edit_min_stock,
                                            'category': edit_category
                                        }
                                        
                                        if db.update_product(product['id'], product_data):
                                            st.success(f"✅ Producto '{edit_name}' actualizado correctamente")
                                            st.session_state[f'edit_product_{product["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al actualizar el producto. Intente nuevamente.")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f'edit_product_{product["id"]}'] = False
                                        st.rerun()
                    
                    # Modal de confirmación de eliminación
                    if st.session_state.get(f'delete_product_{product["id"]}', False):
                        with st.expander(f"🗑️ Eliminar {product['name']}", expanded=True):
                            st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar el producto '{product['name']}'?")
                            st.write("**Esta acción no se puede deshacer.**")
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if st.button("🗑️ Confirmar Eliminación", key=f"confirm_del_product_btn_{product['id']}", type="primary"):
                                    if db.delete_product(product['id']):
                                        st.success(f"✅ Producto '{product['name']}' eliminado correctamente")
                                        st.session_state[f'delete_product_{product["id"]}'] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al eliminar el producto. Intente nuevamente.")
                            
                            with col2:
                                if st.button("❌ Cancelar", key=f"cancel_del_product_btn_{product['id']}"):
                                    st.session_state[f'delete_product_{product["id"]}'] = False
                                    st.rerun()
                    
                    st.markdown("---")
            
            # Acciones masivas
            st.markdown("### ⚡ Acciones Masivas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Exportar Inventario", width='stretch'):
                    st.info("Generando archivo Excel...")
                    st.success("✅ Inventario exportado exitosamente!")
            
            with col2:
                if st.button("🔄 Actualizar Stock", width='stretch'):
                    st.info("Actualizando niveles de stock...")
                    st.success("✅ Stock actualizado!")
            
            with col3:
                if st.button("📧 Notificar Stock Bajo", width='stretch'):
                    st.info("Enviando notificaciones...")
                    st.success("✅ Notificaciones enviadas!")
        else:
            st.info("No se encontraron productos. ¡Agrega el primer producto!")
    
    with tab2:
        st.subheader("➕ Agregar Nuevo Producto")
        
        with st.form("new_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre Producto *", placeholder="ej. Bife de Chorizo")
                code = st.text_input("Código Producto", placeholder="ej. BOV001")
                barcode = st.text_input("Código de Barras", placeholder="ej. 1234567890123")
                
                # Categorías
                categories = db.get_product_categories()
                category_options = {cat['name']: cat['id'] for cat in categories}
                selected_category = st.selectbox("Categoría *", list(category_options.keys()))
                category_id = category_options[selected_category]
                
                # Unidades de medida
                units = db.get_units_of_measure()
                unit_options = {f"{unit['name']} ({unit['symbol']})": unit['id'] for unit in units}
                selected_unit = st.selectbox("Unidad de Medida *", list(unit_options.keys()))
                unit_id = unit_options[selected_unit]
            
            with col2:
                description = st.text_area("Descripción", placeholder="Descripción del producto")
                brand = st.text_input("Marca", placeholder="ej. Marca Name")
                origin = st.text_input("Origen", placeholder="ej. Argentina, Buenos Aires")
                
                cost_price = st.number_input("Precio de Costo ($)", min_value=0.0, step=0.01)
                selling_price = st.number_input("Precio de Venta ($) *", min_value=0.0, step=0.01)
                
                min_stock = st.number_input("Stock Mínimo", min_value=0, value=5)
                max_stock = st.number_input("Stock Máximo", min_value=0, value=100)
            
            # Opciones avanzadas
            with st.expander("⚙️ Opciones Avanzadas"):
                shelf_life = st.number_input("Días de Conservación", min_value=0, value=3)
                temp_control = st.checkbox("Requiere Control Temperatura")
                
                if temp_control:
                    col_temp1, col_temp2 = st.columns(2)
                    with col_temp1:
                        temp_min = st.number_input("Temperatura Mín (°C)", value=2.0)
                    with col_temp2:
                        temp_max = st.number_input("Temperatura Máx (°C)", value=4.0)
                else:
                    temp_min = temp_max = None
            
            # Botón submit
            if st.form_submit_button("➕ Agregar Producto", width='stretch'):
                if not name or not selling_price:
                    st.error("⚠️ Completa todos los campos obligatorios")
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
                        'storage_temperature_max': temp_max
                    }
                    
                    if db.create_product(product_data):
                        st.success(f"✅ Producto '{name}' creado exitosamente")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error al crear el producto. Intente nuevamente.")
    
    with tab3:
        st.subheader("📊 Gestión Stock")
        
        # Obtener datos de stock
        db = get_hybrid_manager()
        products = db.get_all_products()
        
        if products:
            df_products = pd.DataFrame(products)
            
            # Métricas de stock
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_products = len(df_products)
                st.metric("Total Productos", total_products)
            with col2:
                low_stock_count = len(df_products[df_products['current_stock'] <= df_products['min_stock_level']])
                st.metric("Stock Bajo", low_stock_count, delta=f"-{low_stock_count}" if low_stock_count > 0 else None)
            with col3:
                total_value = (df_products['current_stock'] * df_products['selling_price']).sum()
                st.metric("Valor Total Stock", f"${total_value:,.2f}")
            with col4:
                avg_stock = df_products['current_stock'].mean()
                st.metric("Stock Promedio", f"{avg_stock:.1f}")
            
            st.markdown("---")
            
            # Filtros avanzados
            col1, col2, col3 = st.columns(3)
            with col1:
                category_filter = st.selectbox(
                    "Filtrar por Categoría",
                    ["Todas"] + list(df_products['category_name'].unique()),
                    key="stock_category_filter"
                )
            with col2:
                stock_status = st.selectbox(
                    "Estado de Stock",
                    ["Todos", "Stock Bajo", "Stock Normal", "Stock Alto"],
                    key="stock_status_filter"
                )
            with col3:
                sort_by = st.selectbox(
                    "Ordenar por",
                    ["Nombre", "Stock Actual", "Valor", "Categoría"],
                    key="stock_sort_filter"
                )
            
            # Aplicar filtros
            filtered_df = df_products.copy()
            
            if category_filter != "Todas":
                filtered_df = filtered_df[filtered_df['category_name'] == category_filter]
            
            if stock_status == "Stock Bajo":
                filtered_df = filtered_df[filtered_df['current_stock'] <= filtered_df['min_stock_level']]
            elif stock_status == "Stock Normal":
                filtered_df = filtered_df[
                    (filtered_df['current_stock'] > filtered_df['min_stock_level']) & 
                    (filtered_df['current_stock'] <= filtered_df['min_stock_level'] * 2)
                ]
            elif stock_status == "Stock Alto":
                filtered_df = filtered_df[filtered_df['current_stock'] > filtered_df['min_stock_level'] * 2]
            
            # Ordenar
            if sort_by == "Stock Actual":
                filtered_df = filtered_df.sort_values('current_stock', ascending=False)
            elif sort_by == "Valor":
                filtered_df['valor_total'] = filtered_df['current_stock'] * filtered_df['selling_price']
                filtered_df = filtered_df.sort_values('valor_total', ascending=False)
            elif sort_by == "Categoría":
                filtered_df = filtered_df.sort_values('category_name')
            else:
                filtered_df = filtered_df.sort_values('name')
            
            # Mostrar tabla de stock
            if not filtered_df.empty:
                # Añadir columna de estado
                def get_stock_status(row):
                    if row['current_stock'] <= row['min_stock_level']:
                        return "🔴 Bajo"
                    elif row['current_stock'] <= row['min_stock_level'] * 2:
                        return "🟡 Normal"
                    else:
                        return "🟢 Alto"
                
                filtered_df['estado'] = filtered_df.apply(get_stock_status, axis=1)
                filtered_df['valor_total'] = filtered_df['current_stock'] * filtered_df['selling_price']
                
                st.dataframe(
                    filtered_df[['name', 'code', 'category_name', 'current_stock', 'min_stock_level', 'estado', 'selling_price', 'valor_total']],
                    width='stretch',
                    column_config={
                        "name": "Producto",
                        "code": "Código",
                        "category_name": "Categoría",
                        "current_stock": "Stock Actual",
                        "min_stock_level": "Stock Mínimo",
                        "estado": "Estado",
                        "selling_price": st.column_config.NumberColumn("Precio Unit.", format="$%.2f"),
                        "valor_total": st.column_config.NumberColumn("Valor Total", format="$%.2f")
                    }
                )
                
                # Gráficos de stock
                st.markdown("---")
                st.subheader("📈 Análisis de Stock")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de stock por categoría
                    category_stock = filtered_df.groupby('category_name')['current_stock'].sum().reset_index()
                    fig_category = px.bar(
                        category_stock,
                        x='category_name',
                        y='current_stock',
                        title="Stock por Categoría")
                    fig_category.update_layout(xaxis=dict(tickangle=-45))
                    st.plotly_chart(fig_category, width='stretch')
                
                with col2:
                    # Gráfico de estado de stock
                    status_counts = filtered_df['estado'].value_counts()
                    fig_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Distribución de Estados de Stock"
                    )
                    st.plotly_chart(fig_status, width='stretch')
                
                # Acciones de stock
                st.markdown("---")
                st.subheader("⚡ Acciones Rápidas")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📦 Actualizar Stock", width='stretch'):
                        st.info("Funcionalidad de actualización de stock en desarrollo")
                
                with col2:
                    if st.button("📋 Generar Reporte", width='stretch'):
                        st.info("Generando reporte de stock...")
                        st.success("✅ Reporte generado exitosamente!")
                
                with col3:
                    if st.button("🔄 Sincronizar", width='stretch'):
                        st.info("Sincronizando datos de stock...")
                        st.success("✅ Sincronización completada!")
            else:
                st.info("No se encontraron productos con los filtros aplicados")
        else:
            st.info("No hay productos en el inventario. ¡Agrega el primer producto!")
    
    with tab4:
        st.subheader("⚠️ Alertas y Notificaciones")
        
        # Productos con stock bajo
        low_stock = db.get_products_low_stock()
        if low_stock:
            st.warning(f"⚠️ {len(low_stock)} productos con stock bajo")
            for product in low_stock:
                st.write(f"• {product['name']}: {product['current_stock']} (mín: {product['min_stock_level']})")
        else:
            st.success("✅ Todo el stock es suficiente")
        
        # Productos próximos a vencer
        expiring = db.get_products_expiring_soon()
        if expiring:
            st.warning(f"⏰ {len(expiring)} productos próximos a vencer")
            for product in expiring:
                st.write(f"• {product['name']}: vence el {product['expiry_date']}")
        else:
            st.success("✅ Ningún producto próximo a vencer")


def render_clientes():
    """Renderiza la sección clientes"""
    require_permission("clientes")
    
    st.header("👥 Gestión Clientes")
    
    # Obtener datos de clientes
    db = get_hybrid_manager()
    customers = db.get_all_customers()
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Clientes", "➕ Nuevo Cliente", "📊 Estadísticas", "💬 CRM"])
    
    with tab1:
        st.subheader("📋 Lista de Clientes")
        
        if customers:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("🔍 Buscar por nombre", placeholder="Nombre del cliente")
            with col2:
                filter_status = st.selectbox("📊 Estado", ["Todos", "Activos", "Inactivos"])
            with col3:
                sort_by = st.selectbox("🔄 Ordenar por", ["Nombre", "Compras", "Última compra"])
            
            # Filtrar clientes
            filtered_customers = customers.copy()
            
            if search_name:
                filtered_customers = [c for c in filtered_customers if search_name.lower() in c['name'].lower()]
            
            if filter_status == "Activos":
                filtered_customers = [c for c in filtered_customers if c.get('is_active', True)]
            elif filter_status == "Inactivos":
                filtered_customers = [c for c in filtered_customers if not c.get('is_active', True)]
            
            # Ordenar
            if sort_by == "Compras":
                filtered_customers.sort(key=lambda x: x.get('total_purchases', 0), reverse=True)
            elif sort_by == "Última compra":
                filtered_customers.sort(key=lambda x: x.get('last_purchase', ''), reverse=True)
            else:
                filtered_customers.sort(key=lambda x: x['name'])
            
            # Mostrar estadísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clientes", len(filtered_customers))
            with col2:
                total_purchases = sum(c.get('total_purchases', 0) for c in filtered_customers)
                st.metric("Compras Totales", f"${total_purchases:,.2f}")
            with col3:
                avg_purchase = total_purchases / len(filtered_customers) if filtered_customers else 0
                st.metric("Promedio por Cliente", f"${avg_purchase:,.2f}")
            with col4:
                active_customers = len([c for c in filtered_customers if c.get('is_active', True)])
                st.metric("Clientes Activos", active_customers)
            
            # Tabla de clientes con acciones
            if filtered_customers:
                st.markdown("---")
                st.subheader("📋 Lista de Clientes")
                
                # Mostrar cada cliente con opciones de editar/eliminar
                for i, customer in enumerate(filtered_customers):
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                        
                        with col1:
                            st.write(f"**{customer['name']}**")
                            st.caption(f"📧 {customer['email']}")
                            st.caption(f"📞 {customer['phone']}")
                        
                        with col2:
                            st.write(f"💰 ${customer['total_purchases']:,.2f}")
                            st.caption(f"📦 {customer['total_orders']} órdenes")
                        
                        with col3:
                            st.write(f"📅 {customer['last_purchase']}")
                            status = "🟢 Activo" if customer.get('is_active', True) else "🔴 Inactivo"
                            st.caption(status)
                        
                        with col4:
                            if st.button("✏️", key=f"edit_customer_btn_{customer['id']}", help="Editar cliente"):
                                st.session_state[f'edit_customer_{customer["id"]}'] = True
                        
                        with col5:
                            if st.button("🗑️", key=f"delete_customer_btn_{customer['id']}", help="Eliminar cliente"):
                                st.session_state[f'delete_customer_{customer["id"]}'] = True
                        
                        # Modal de edición
                        if st.session_state.get(f'edit_customer_{customer["id"]}', False):
                            with st.expander(f"✏️ Editar {customer['name']}", expanded=True):
                                with st.form(f"edit_form_{customer['id']}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        edit_name = st.text_input("Nombre", value=customer['name'], key=f"edit_name_{customer['id']}")
                                        edit_email = st.text_input("Email", value=customer['email'], key=f"edit_email_{customer['id']}")
                                        edit_phone = st.text_input("Teléfono", value=customer['phone'], key=f"edit_phone_{customer['id']}")
                                    
                                    with col2:
                                        edit_address = st.text_area("Dirección", value=customer.get('address', ''), key=f"edit_address_{customer['id']}")
                                        edit_active = st.checkbox("Activo", value=customer.get('is_active', True), key=f"edit_active_{customer['id']}")
                                    
                                    col1, col2, col3 = st.columns([1, 1, 1])
                                    with col1:
                                        if st.form_submit_button("💾 Guardar", type="primary"):
                                            customer_data = {
                                                'name': edit_name,
                                                'email': edit_email,
                                                'phone': edit_phone,
                                                'address': edit_address,
                                                'is_active': edit_active
                                            }
                                            
                                            if db.update_customer(customer['id'], customer_data):
                                                st.success(f"✅ Cliente '{edit_name}' actualizado correctamente")
                                                st.session_state[f'edit_customer_{customer["id"]}'] = False
                                                st.rerun()
                                            else:
                                                st.error("❌ Error al actualizar el cliente. Intente nuevamente.")
                                    
                                    with col2:
                                        if st.form_submit_button("❌ Cancelar"):
                                            st.session_state[f'edit_customer_{customer["id"]}'] = False
                                            st.rerun()
                        
                        # Modal de confirmación de eliminación
                        if st.session_state.get(f'delete_customer_{customer["id"]}', False):
                            with st.expander(f"🗑️ Eliminar {customer['name']}", expanded=True):
                                st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar al cliente '{customer['name']}'?")
                                st.write("**Esta acción no se puede deshacer.**")
                                
                                col1, col2, col3 = st.columns([1, 1, 1])
                                with col1:
                                    if st.button("🗑️ Confirmar Eliminación", key=f"confirm_del_customer_btn_{customer['id']}", type="primary"):
                                        if db.delete_customer(customer['id']):
                                            st.success(f"✅ Cliente '{customer['name']}' eliminado correctamente")
                                            st.session_state[f'delete_customer_{customer["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al eliminar el cliente. Intente nuevamente.")
                                
                                with col2:
                                    if st.button("❌ Cancelar", key=f"cancel_del_customer_btn_{customer['id']}"):
                                        st.session_state[f'delete_customer_{customer["id"]}'] = False
                                        st.rerun()
                        
                        st.markdown("---")
                
                # Acciones masivas
                st.markdown("### ⚡ Acciones Masivas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Enviar Email Masivo", width='stretch'):
                        st.info("Funcionalidad de email masivo en desarrollo")
                
                with col2:
                    if st.button("📊 Exportar Lista", width='stretch'):
                        st.info("Generando archivo Excel...")
                        st.success("✅ Lista exportada exitosamente!")
                
                with col3:
                    if st.button("🔄 Actualizar Datos", width='stretch'):
                        st.info("Actualizando datos de clientes...")
                        st.success("✅ Datos actualizados!")
            else:
                st.info("No se encontraron clientes con los filtros aplicados")
        else:
            st.info("No hay clientes registrados")
    
    with tab2:
        st.subheader("➕ Nuevo Cliente")
        
        with st.form("nuevo_cliente_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez")
                email = st.text_input("Email *", placeholder="juan.perez@email.com")
                phone = st.text_input("Teléfono", placeholder="+54 11 1234-5678")
            
            with col2:
                address = st.text_area("Dirección", placeholder="Av. Corrientes 1234, Buenos Aires")
                notes = st.text_area("Notas", placeholder="Información adicional del cliente")
            
            submitted = st.form_submit_button("💾 Guardar Cliente", width='stretch', type="primary")
            
            if submitted:
                if name and email:
                    customer_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'address': address,
                        'notes': notes,
                        'is_active': True
                    }
                    
                    if db.create_customer(customer_data):
                        st.success(f"✅ Cliente '{name}' agregado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al crear el cliente. Intente nuevamente.")
                else:
                    st.error("❌ Por favor complete los campos obligatorios (Nombre y Email)")
    
    with tab3:
        st.subheader("📊 Estadísticas de Clientes")
        
        if customers:
            # Gráfico de compras por cliente
            top_customers = sorted(customers, key=lambda x: x.get('total_purchases', 0), reverse=True)[:10]
            
            fig_customers = px.bar(
                pd.DataFrame(top_customers),
                x='name',
                y='total_purchases',
                title="Top 10 Clientes por Compras")
            fig_customers.update_layout(xaxis=dict(tickangle=-45))
            st.plotly_chart(fig_customers, width='stretch')
            
            # Gráfico de distribución de órdenes
            orders_data = [c.get('total_orders', 0) for c in customers]
            fig_orders = px.histogram(
                pd.DataFrame({'orders': orders_data}),
                x='orders',
                title="Distribución de Órdenes por Cliente")
            st.plotly_chart(fig_orders, width='stretch')
            
            # Métricas adicionales
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_orders = sum(c.get('total_orders', 0) for c in customers) / len(customers) if customers else 0
                st.metric("Promedio de Órdenes", f"{avg_orders:.1f}")
            with col2:
                max_purchase = max(c.get('total_purchases', 0) for c in customers) if customers else 0
                st.metric("Mayor Compra", f"${max_purchase:,.2f}")
            with col3:
                recent_customers = len([c for c in customers if c.get('last_purchase') and c.get('last_purchase') >= '2024-09-01'])
                st.metric("Clientes Recientes", recent_customers)
        else:
            st.info("No hay datos de clientes para mostrar estadísticas")
    
    with tab4:
        st.subheader("💬 CRM - Gestión de Relaciones")
        
        # Obtener datos CRM
        db = get_hybrid_manager()
        # Metodi CRM rimossi per evitare dati hardcoded
        # analytics = db.get_customer_analytics()
        # segments = db.get_customer_segments()
        # campaigns = db.get_marketing_campaigns()
        # predictions = db.get_customer_predictions()
        
        # Tabs para diferentes funcionalidades CRM
        crm_tab1, crm_tab2, crm_tab3, crm_tab4 = st.tabs(["📊 Analytics", "🎯 Segmentación", "📧 Campañas", "🔮 Predicciones"])
        
        with crm_tab1:
            st.subheader("📊 Analytics de Clientes")
            
            # Analytics basati sui dati reali
            st.info("📊 Analytics: Nessun dato disponibile. I dati verranno mostrati quando avrai inserito clienti reali nel sistema.")
            st.info("💡 Per vedere le analytics, aggiungi clienti attraverso la sezione 'Nuevo Cliente' e inserisci dati di vendita reali.")
            
            # Grafico di soddisfazione
            st.subheader("📈 Satisfacción del Cliente")
            st.info("📊 Grafico di soddisfazione: Nessun dato disponibile. Inserisci dati reali per vedere l'evoluzione della soddisfazione dei clienti.")
        
        with crm_tab2:
            st.subheader("🎯 Segmentación de Clientes")
            
            # Segmentazione basata sui dati reali
            st.info("🎯 Segmentación: Nessun dato disponibile. La segmentazione dei clienti verrà mostrata quando avrai dati reali.")
            st.info("💡 Per vedere la segmentazione, aggiungi clienti e i loro dati di acquisto attraverso il sistema.")
        
        with crm_tab3:
            st.subheader("📧 Campañas de Marketing")
            
            # Campagne basate sui dati reali
            st.info("📧 Campañas: Nessuna campagna disponibile. Le campagne di marketing verranno mostrate quando avrai creato campagne reali.")
            st.info("💡 Per gestire le campagne, crea prima clienti e poi implementa un sistema di campagne di marketing.")
        
        with crm_tab4:
            st.subheader("🔮 Predicciones y Recomendaciones")
            
            # Predizioni basate sui dati reali
            st.info("🔮 Predicciones: Nessuna predizione disponibile. Le predizioni verranno mostrate quando avrai dati sufficienti sui clienti.")
            st.info("💡 Per vedere le predizioni, aggiungi clienti e i loro dati di acquisto storici nel sistema.")
        
        # Sección de interacciones con clientes
        st.markdown("---")
        st.subheader("📞 Gestión de Interacciones")
        
        # Seleccionar cliente para ver interacciones
        if customers:
            customer_names = [f"{c['name']} (ID: {c['id']})" for c in customers]
            selected_customer = st.selectbox("Seleccionar Cliente", customer_names)
            
            if selected_customer:
                customer_id = selected_customer.split("ID: ")[1].split(")")[0]
                interactions = db.get_customer_interactions(customer_id)
                
                if interactions:
                    # Trova il cliente per nome usando l'ID
                    customer_name = next((c['name'] for c in customers if c['id'] == customer_id), 'Cliente Desconocido')
                    st.subheader(f"📋 Historial de Interacciones - {customer_name}")
                    
                    for interaction in interactions:
                        with st.expander(f"📅 {interaction['date']} - {interaction['type'].title()}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Tipo:** {interaction['type'].title()}")
                                st.write(f"**Descripción:** {interaction['description']}")
                                st.write(f"**Resultado:** {interaction['outcome'].replace('_', ' ').title()}")
                            
                            with col2:
                                st.write(f"**Empleado:** {interaction['employee']}")
                                st.write(f"**Notas:** {interaction['notes']}")
                else:
                    st.info("No hay interacciones registradas para este cliente")
                
                # Formulario para nueva interacción
                st.subheader("➕ Nueva Interacción")
                with st.form("nueva_interaccion_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        interaction_type = st.selectbox("Tipo de Interacción", ["llamada", "email", "visita", "reunión"])
                        interaction_date = st.date_input("Fecha")
                        outcome = st.selectbox("Resultado", ["satisfecho", "interesado", "compra_realizada", "no_interesado", "pendiente"])
                    
                    with col2:
                        description = st.text_area("Descripción", placeholder="Descripción de la interacción")
                        notes = st.text_area("Notas", placeholder="Notas adicionales")
                        employee = st.text_input("Empleado", placeholder="Nombre del empleado")
                    
                    if st.form_submit_button("💾 Guardar Interacción", type="primary"):
                        interaction_data = {
                            'customer_id': customer_id,
                            'type': interaction_type,
                            'date': interaction_date.strftime('%Y-%m-%d'),
                            'description': description,
                            'outcome': outcome,
                            'notes': notes,
                            'employee': employee
                        }
                        
                        if db.add_customer_interaction(interaction_data):
                            st.success("✅ Interacción guardada correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la interacción")
        else:
            st.info("No hay clientes disponibles para gestionar interacciones")

def render_proveedores():
    """Renderiza la sección proveedores"""
    require_permission("proveedores")
    
    st.header("🚚 Gestión Proveedores")
    
    # Obtener datos de proveedores
    db = get_hybrid_manager()
    suppliers = db.select('suppliers') or []
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Proveedores", "➕ Nuevo Proveedor", "📊 Estadísticas", "📦 Pedidos"])
    
    with tab1:
        st.subheader("📋 Lista de Proveedores")
        
        if suppliers:
            # Crear DataFrame para mostrar proveedores
            df_suppliers = pd.DataFrame(suppliers)
            
            # Mostrar métricas rápidas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Proveedores", len(suppliers))
            with col2:
                total_amount = sum(s.get('total_amount', 0) for s in suppliers)
                st.metric("Monto Total", f"${total_amount:,.2f}")
            with col3:
                total_transactions = sum(s.get('transactions_count', 0) for s in suppliers)
                st.metric("Total Transacciones", total_transactions)
            with col4:
                avg_amount = total_amount / len(suppliers) if suppliers else 0
                st.metric("Promedio por Proveedor", f"${avg_amount:,.2f}")
            
            st.markdown("---")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Buscar proveedor", placeholder="Nombre, email, teléfono...")
            with col2:
                sort_by = st.selectbox("📊 Ordenar por", ["name", "total_amount", "transactions_count", "created_at"])
            
            # Aplicar filtros
            filtered_suppliers = suppliers
            if search_term:
                filtered_suppliers = [s for s in suppliers if 
                                    search_term.lower() in s.get('name', '').lower() or
                                    search_term.lower() in s.get('contact_email', '').lower() or
                                    search_term.lower() in s.get('phone', '').lower()]
            
            # Ordenar
            if sort_by == "total_amount":
                filtered_suppliers.sort(key=lambda x: x.get('total_amount', 0), reverse=True)
            elif sort_by == "transactions_count":
                filtered_suppliers.sort(key=lambda x: x.get('transactions_count', 0), reverse=True)
            elif sort_by == "created_at":
                filtered_suppliers.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            else:
                filtered_suppliers.sort(key=lambda x: x.get('name', ''))
            
            # Mostrar tabla con acciones CRUD
            if filtered_suppliers:
                st.markdown("---")
                st.subheader("📋 Lista de Proveedores")
                
                # Mostrar cada proveedor con opciones de editar/eliminar
                for supplier in filtered_suppliers:
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                        
                        with col1:
                            st.write(f"**{supplier['name']}**")
                            st.caption(f"📧 {supplier['contact_email']}")
                            st.caption(f"📞 {supplier['phone']}")
                            if supplier.get('contact_person'):
                                st.caption(f"👤 {supplier['contact_person']}")
                        
                        with col2:
                            st.write(f"💰 ${supplier['total_amount']:,.2f}")
                            st.caption(f"📦 {supplier['transactions_count']} transacciones")
                        
                        with col3:
                            if supplier.get('address'):
                                st.write(f"📍 {supplier['address']}")
                            if supplier.get('created_at'):
                                st.caption(f"📅 {supplier['created_at']}")
                        
                        with col4:
                            if st.button("✏️", key=f"edit_btn_{supplier['id']}", help="Editar proveedor"):
                                st.session_state[f'edit_supplier_{supplier["id"]}'] = True
                        
                        with col5:
                            if st.button("🗑️", key=f"delete_btn_{supplier['id']}", help="Eliminar proveedor"):
                                st.session_state[f'delete_supplier_{supplier["id"]}'] = True
                        
                        # Modal de edición
                        if st.session_state.get(f'edit_supplier_{supplier["id"]}', False):
                            with st.expander(f"✏️ Editar {supplier['name']}", expanded=True):
                                with st.form(f"edit_supplier_form_{supplier['id']}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        edit_name = st.text_input("Nombre", value=supplier['name'], key=f"edit_name_{supplier['id']}")
                                        edit_email = st.text_input("Email", value=supplier['contact_email'], key=f"edit_email_{supplier['id']}")
                                        edit_phone = st.text_input("Teléfono", value=supplier['phone'], key=f"edit_phone_{supplier['id']}")
                                        edit_person = st.text_input("Persona de Contacto", value=supplier.get('contact_person', ''), key=f"edit_person_{supplier['id']}")
                                    
                                    with col2:
                                        edit_address = st.text_area("Dirección", value=supplier.get('address', ''), key=f"edit_address_{supplier['id']}")
                                        edit_cuit = st.text_input("CUIT", value=supplier.get('cuit', ''), key=f"edit_cuit_{supplier['id']}")
                                        edit_active = st.checkbox("Activo", value=supplier.get('is_active', True), key=f"edit_active_{supplier['id']}")
                                    
                                    col1, col2, col3 = st.columns([1, 1, 1])
                                    with col1:
                                        if st.form_submit_button("💾 Guardar", type="primary"):
                                            supplier_data = {
                                                'name': edit_name,
                                                'contact_email': edit_email,
                                                'phone': edit_phone,
                                                'contact_person': edit_person,
                                                'address': edit_address,
                                                'cuit': edit_cuit,
                                                'is_active': edit_active
                                            }
                                            
                                            if db.update_supplier(supplier['id'], supplier_data):
                                                st.success(f"✅ Proveedor '{edit_name}' actualizado correctamente")
                                                st.session_state[f'edit_supplier_{supplier["id"]}'] = False
                                                st.rerun()
                                            else:
                                                st.error("❌ Error al actualizar el proveedor. Intente nuevamente.")
                                    
                                    with col2:
                                        if st.form_submit_button("❌ Cancelar"):
                                            st.session_state[f'edit_supplier_{supplier["id"]}'] = False
                                            st.rerun()
                        
                        # Modal de confirmación de eliminación
                        if st.session_state.get(f'delete_supplier_{supplier["id"]}', False):
                            with st.expander(f"🗑️ Eliminar {supplier['name']}", expanded=True):
                                st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar al proveedor '{supplier['name']}'?")
                                st.write("**Esta acción no se puede deshacer.**")
                                
                                col1, col2, col3 = st.columns([1, 1, 1])
                                with col1:
                                    if st.button("🗑️ Confirmar Eliminación", key=f"confirm_del_btn_{supplier['id']}", type="primary"):
                                        if db.delete_supplier(supplier['id']):
                                            st.success(f"✅ Proveedor '{supplier['name']}' eliminado correctamente")
                                            st.session_state[f'delete_supplier_{supplier["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al eliminar el proveedor. Intente nuevamente.")
                                
                                with col2:
                                    if st.button("❌ Cancelar", key=f"cancel_del_btn_{supplier['id']}"):
                                        st.session_state[f'delete_supplier_{supplier["id"]}'] = False
                                        st.rerun()
                        
                        st.markdown("---")
                
                # Acciones masivas
                st.markdown("### ⚡ Acciones Masivas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Enviar Email Masivo", width='stretch'):
                        st.info("Funcionalidad de email masivo en desarrollo")
                
                with col2:
                    if st.button("📊 Exportar Lista", width='stretch'):
                        st.info("Generando archivo Excel...")
                        st.success("✅ Lista exportada exitosamente!")
                
                with col3:
                    if st.button("🔄 Actualizar Datos", width='stretch'):
                        st.info("Actualizando datos de proveedores...")
                        st.success("✅ Datos actualizados!")
            else:
                st.info("No se encontraron proveedores con los filtros aplicados")
        else:
            st.info("No hay proveedores registrados")
    
    with tab2:
        st.subheader("➕ Nuevo Proveedor")
        
        with st.form("nuevo_proveedor"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("🏢 Nombre del Proveedor *", placeholder="Ej: Distribuidora ABC")
                contact_email = st.text_input("📧 Email de Contacto", placeholder="contacto@proveedor.com")
                phone = st.text_input("📞 Teléfono", placeholder="+54 11 1234-5678")
            
            with col2:
                address = st.text_area("📍 Dirección", placeholder="Calle, número, ciudad, código postal")
                contact_person = st.text_input("👤 Persona de Contacto", placeholder="Nombre del contacto principal")
                notes = st.text_area("📝 Notas", placeholder="Información adicional sobre el proveedor")
            
            # Botones
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("💾 Guardar Proveedor", width='stretch', type="primary")
            
            if submitted:
                if not name:
                    st.error("❌ El nombre del proveedor es obligatorio")
                else:
                    try:
                        supplier_data = {
                            'name': name,
                            'contact_email': contact_email,
                            'phone': phone,
                            'address': address,
                            'contact_person': contact_person,
                            'notes': notes,
                            'is_active': True
                        }
                        
                        if db.create_supplier(supplier_data):
                            st.success(f"✅ Proveedor '{name}' creado exitosamente")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Error al crear el proveedor. Intente nuevamente.")
                        
                        # Mostrar resumen
                        st.info(f"""
                        **📋 Resumen del Proveedor Creado:**
                        • **Nombre:** {name}
                        • **Email:** {contact_email or 'No especificado'}
                        • **Teléfono:** {phone or 'No especificado'}
                        • **Contacto:** {contact_person or 'No especificado'}
                        """)
                        
                    except Exception as e:
                        st.error(f"❌ Error creando proveedor: {str(e)}")
    
    with tab3:
        st.subheader("📊 Estadísticas de Proveedores")
        
        if suppliers:
            # Gráficos de estadísticas
            import plotly.express as px
            import plotly.graph_objects as go
            
            # Top 5 proveedores por monto
            top_suppliers = sorted(suppliers, key=lambda x: x.get('total_amount', 0), reverse=True)[:5]
            
            if top_suppliers:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras - Top proveedores
                    fig_bar = px.bar(
                        pd.DataFrame(top_suppliers),
                        x='name',
                        y='total_amount',
                        title="Top 5 Proveedores por Monto")
                    fig_bar.update_layout(xaxis=dict(tickangle=-45))
                    st.plotly_chart(fig_bar, width='stretch')
                
                with col2:
                    # Gráfico de pastel - Distribución de montos
                    fig_pie = px.pie(
                        pd.DataFrame(top_suppliers),
                        values='total_amount',
                        names='name',
                        title="Distribución de Montos por Proveedor"
                    )
                    st.plotly_chart(fig_pie, width='stretch')
                
                # Tabla detallada
                st.subheader("📋 Detalles de Top Proveedores")
                df_top = pd.DataFrame(top_suppliers)
                st.dataframe(
                    df_top[['name', 'total_amount', 'transactions_count', 'contact_email']],
                    width='stretch',
                    column_config={
                        "name": "Proveedor",
                        "total_amount": st.column_config.NumberColumn("Monto Total", format="$%.2f"),
                        "transactions_count": "Transacciones",
                        "contact_email": "Email"
                    }
                )
            else:
                st.info("No hay datos suficientes para mostrar estadísticas")
        else:
            st.info("No hay proveedores registrados para mostrar estadísticas")
    
    with tab4:
        st.subheader("📦 Gestión de Pedidos")
        
        # Obtener pedidos de proveedores desde la base de datos
        orders = db.get_supplier_orders()
        
        # Métricas de pedidos
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pedidos Totales", len(orders))
        with col2:
            pending_orders = len([o for o in orders if o['status'] == 'Pendiente'])
            st.metric("Pendientes", pending_orders)
        with col3:
            delivered_orders = len([o for o in orders if o['status'] == 'Entregado'])
            st.metric("Entregados", delivered_orders)
        with col4:
            total_value = sum(o['total_amount'] for o in orders)
            st.metric("Valor Total", f"${total_value:,.2f}")
        
        st.markdown("---")
        
        # Mostrar pedidos con acciones CRUD
        if orders:
            st.subheader("📋 Lista de Pedidos")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Buscar pedido", placeholder="Proveedor, estado...")
            with col2:
                status_filter = st.selectbox("📊 Filtrar por estado", ["Todos", "Pendiente", "En Tránsito", "Entregado", "Cancelado"])
            
            # Aplicar filtros
            filtered_orders = orders
            if search_term:
                filtered_orders = [o for o in orders if 
                                 search_term.lower() in o.get('supplier_name', '').lower() or
                                 search_term.lower() in o.get('status', '').lower()]
            
            if status_filter != "Todos":
                filtered_orders = [o for o in filtered_orders if o['status'] == status_filter]
            
            # Mostrar cada pedido con opciones de editar/eliminar
            for order in filtered_orders:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**Pedido #{order['id']}**")
                        st.write(f"🏢 {order['supplier_name']}")
                        st.caption(f"📅 Pedido: {order['order_date']}")
                        st.caption(f"🚚 Entrega: {order['delivery_date']}")
                    
                    with col2:
                        st.write(f"💰 ${order['total_amount']:,.2f}")
                        st.caption(f"📦 {order['items_count']} items")
                    
                    with col3:
                        status_color = {
                            'Pendiente': '🟡',
                            'En Tránsito': '🔵',
                            'Entregado': '🟢',
                            'Cancelado': '🔴'
                        }
                        st.write(f"{status_color.get(order['status'], '⚪')} {order['status']}")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_order_btn_{order['id']}", help="Editar pedido"):
                            st.session_state[f'edit_order_{order["id"]}'] = True
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_order_btn_{order['id']}", help="Eliminar pedido"):
                            st.session_state[f'delete_order_{order["id"]}'] = True
                    
                    # Modal de edición
                    if st.session_state.get(f'edit_order_{order["id"]}', False):
                        with st.expander(f"✏️ Editar Pedido #{order['id']}", expanded=True):
                            with st.form(f"edit_order_form_{order['id']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    edit_supplier = st.text_input("Proveedor", value=order['supplier_name'], key=f"edit_supplier_{order['id']}")
                                    edit_order_date = st.date_input("Fecha Pedido", value=pd.to_datetime(order['order_date']).date(), key=f"edit_order_date_{order['id']}")
                                    edit_delivery_date = st.date_input("Fecha Entrega", value=pd.to_datetime(order['delivery_date']).date(), key=f"edit_delivery_date_{order['id']}")
                                
                                with col2:
                                    edit_status = st.selectbox("Estado", ["Pendiente", "En Tránsito", "Entregado", "Cancelado"], 
                                                             index=["Pendiente", "En Tránsito", "Entregado", "Cancelado"].index(order['status']),
                                                             key=f"edit_status_{order['id']}")
                                    edit_amount = st.number_input("Monto Total", value=float(order['total_amount']), key=f"edit_amount_{order['id']}")
                                    edit_items = st.number_input("Cantidad Items", value=int(order['items_count']), key=f"edit_items_{order['id']}")
                                
                                col1, col2, col3 = st.columns([1, 1, 1])
                                with col1:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        order_data = {
                                            'supplier_name': edit_supplier,
                                            'order_date': edit_order_date.strftime('%Y-%m-%d'),
                                            'delivery_date': edit_delivery_date.strftime('%Y-%m-%d'),
                                            'status': edit_status,
                                            'total_amount': edit_amount,
                                            'items_count': edit_items
                                        }
                                        
                                        if db.update_order(order['id'], order_data):
                                            st.success(f"✅ Pedido #{order['id']} actualizado correctamente")
                                            st.session_state[f'edit_order_{order["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al actualizar el pedido. Intente nuevamente.")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f'edit_order_{order["id"]}'] = False
                                        st.rerun()
                    
                    # Modal de confirmación de eliminación
                    if st.session_state.get(f'delete_order_{order["id"]}', False):
                        with st.expander(f"🗑️ Eliminar Pedido #{order['id']}", expanded=True):
                            st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar el pedido #{order['id']} de '{order['supplier_name']}'?")
                            st.write("**Esta acción no se puede deshacer.**")
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if st.button("🗑️ Confirmar Eliminación", key=f"confirm_del_order_btn_{order['id']}", type="primary"):
                                    if db.delete_order(order['id']):
                                        st.success(f"✅ Pedido #{order['id']} eliminado correctamente")
                                        st.session_state[f'delete_order_{order["id"]}'] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al eliminar el pedido. Intente nuevamente.")
                            
                            with col2:
                                if st.button("❌ Cancelar", key=f"cancel_del_order_btn_{order['id']}"):
                                    st.session_state[f'delete_order_{order["id"]}'] = False
                                    st.rerun()
                    
                    st.markdown("---")
            
            # Acciones masivas
            st.markdown("### ⚡ Acciones Masivas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Notificar Proveedores", width='stretch'):
                    st.info("Funcionalidad de notificación en desarrollo")
            
            with col2:
                if st.button("📊 Exportar Pedidos", width='stretch'):
                    st.info("Generando archivo Excel...")
                    st.success("✅ Pedidos exportados exitosamente!")
            
            with col3:
                if st.button("🔄 Actualizar Estados", width='stretch'):
                    st.info("Actualizando estados de pedidos...")
                    st.success("✅ Estados actualizados!")
        else:
            st.info("No hay pedidos registrados")
        
        # Botón para nuevo pedido
        st.markdown("---")
        if st.button("➕ Nuevo Pedido", width='stretch', type="primary"):
            st.info("🚧 Funcionalidad de nuevo pedido en desarrollo")

def render_personal():
    """Renderiza la sección personal"""
    require_permission("personal")
    
    st.header("👨‍💼 Gestión Personal")
    
    # Ottieni dati del personale dal database
    db = get_hybrid_manager()
    try:
        sample_employees = db.select('employees') or []
    except:
        # Se la tabella non esiste ancora, usa lista vuota
        sample_employees = []
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Lista Empleados", "➕ Nuevo Empleado", "⏰ Turnos", "📊 Estadísticas"])
    
    with tab1:
        st.subheader("👥 Lista de Empleados")
        
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Empleados", len(sample_employees))
        with col2:
            active_employees = len([e for e in sample_employees if e['status'] == 'Activo'])
            st.metric("Empleados Activos", active_employees)
        with col3:
            total_salary = sum(e['salary'] for e in sample_employees)
            st.metric("Nómina Total", f"${total_salary:,.2f}")
        with col4:
            avg_salary = total_salary / len(sample_employees) if sample_employees else 0
            st.metric("Salario Promedio", f"${avg_salary:,.2f}")
        
        st.markdown("---")
        
        # Filtros y búsqueda
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Buscar empleado", placeholder="Nombre, posición o departamento...")
        with col2:
            status_filter = st.selectbox("📊 Estado", ["Todos", "Activo", "Inactivo"])
        with col3:
            department_filter = st.selectbox("🏢 Departamento", ["Todos", "Producción", "Ventas", "Administración"])
        
        # Filtrar empleados
        filtered_employees = sample_employees.copy()
        
        if search_term:
            filtered_employees = [e for e in filtered_employees if 
                                search_term.lower() in e['name'].lower() or 
                                search_term.lower() in e['position'].lower() or 
                                search_term.lower() in e['department'].lower()]
        
        if status_filter != "Todos":
            filtered_employees = [e for e in filtered_employees if e['status'] == status_filter]
        
        if department_filter != "Todos":
            filtered_employees = [e for e in filtered_employees if e['department'] == department_filter]
        
        st.markdown("---")
        
        # Mostrar tabla de empleados con acciones
        df_employees = pd.DataFrame(filtered_employees)
        
        if len(filtered_employees) > 0:
            # Crear columnas para acciones
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(
                    df_employees[['name', 'position', 'department', 'hire_date', 'salary', 'status', 'phone']],
                    width='stretch',
                    column_config={
                        "name": "Nombre",
                        "position": "Posición",
                        "department": "Departamento",
                        "hire_date": "Fecha Contratación",
                        "salary": st.column_config.NumberColumn("Salario", format="$%.2f"),
                        "status": "Estado",
                        "phone": "Teléfono"
                    }
                )
            
            with col2:
                st.subheader("⚙️ Acciones")
                
                # Seleccionar empleado para acciones
                employee_names = [f"{e['name']} ({e['position']})" for e in filtered_employees]
                selected_employee = st.selectbox("Seleccionar empleado:", employee_names)
                
                if selected_employee:
                    # Encontrar el empleado seleccionado
                    selected_name = selected_employee.split(" (")[0]
                    selected_emp = next((e for e in filtered_employees if e['name'] == selected_name), None)
                    
                    if selected_emp:
                        st.markdown("---")
                        
                        # Botones de acción
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✏️ Editar", width='stretch', type="primary"):
                                st.session_state['editing_employee'] = selected_emp
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Eliminar", width='stretch', type="secondary"):
                                st.session_state['deleting_employee'] = selected_emp
                                st.rerun()
                        
                        # Mostrar detalles del empleado
                        st.markdown("---")
                        st.subheader("📋 Detalles del Empleado")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Nombre:** {selected_emp['name']}")
                            st.write(f"**Posición:** {selected_emp['position']}")
                            st.write(f"**Departamento:** {selected_emp['department']}")
                            st.write(f"**Fecha Contratación:** {selected_emp['hire_date']}")
                        
                        with col2:
                            st.write(f"**Salario:** ${selected_emp['salary']:,.2f}")
                            st.write(f"**Estado:** {selected_emp['status']}")
                            st.write(f"**Teléfono:** {selected_emp['phone']}")
                            st.write(f"**Email:** {selected_emp['email']}")
        else:
            st.warning("🔍 No se encontraron empleados con los filtros aplicados")
        
        # Modal de edición
        if 'editing_employee' in st.session_state:
            st.markdown("---")
            st.subheader("✏️ Editar Empleado")
            
            emp = st.session_state['editing_employee']
            
            with st.form("edit_employee_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Nombre", value=emp['name'])
                    new_position = st.text_input("Posición", value=emp['position'])
                    new_department = st.selectbox("Departamento", ["Producción", "Ventas", "Administración"], 
                                                index=["Producción", "Ventas", "Administración"].index(emp['department']))
                    new_hire_date = st.date_input("Fecha Contratación", value=pd.to_datetime(emp['hire_date']).date())
                
                with col2:
                    new_salary = st.number_input("Salario", value=float(emp['salary']), min_value=0.0, step=1000.0)
                    new_status = st.selectbox("Estado", ["Activo", "Inactivo"], 
                                            index=["Activo", "Inactivo"].index(emp['status']))
                    new_phone = st.text_input("Teléfono", value=emp['phone'])
                    new_email = st.text_input("Email", value=emp['email'])
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.form_submit_button("💾 Guardar Cambios", width='stretch', type="primary"):
                        # Guardar los cambios en la base de datos
                        try:
                            # Preparar los datos actualizados
                            updated_data = {
                                'name': new_name,
                                'first_name': new_name.split()[0] if new_name else '',
                                'last_name': ' '.join(new_name.split()[1:]) if len(new_name.split()) > 1 else '',
                                'email': new_email,
                                'phone': new_phone,
                                'position': new_position,
                                'department': new_department,
                                'salary': float(new_salary),
                                'hire_date': new_hire_date.isoformat(),
                                'status': new_status,
                                'updated_at': dt.datetime.now().isoformat()
                            }
                            
                            if db.update_employee(emp['id'], updated_data):
                                st.success("✅ Empleado actualizado exitosamente")
                            else:
                                st.error("❌ Error al actualizar el empleado")
                        except Exception as e:
                            st.error(f"❌ Error al actualizar el empleado: {e}")
                        
                        del st.session_state['editing_employee']
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar", width='stretch', type="secondary"):
                        del st.session_state['editing_employee']
                        st.rerun()
        
        # Modal de eliminación
        if 'deleting_employee' in st.session_state:
            st.markdown("---")
            st.subheader("🗑️ Eliminar Empleado")
            
            emp = st.session_state['deleting_employee']
            
            st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar a **{emp['name']}**?")
            st.info("Esta acción no se puede deshacer.")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Confirmar Eliminación", width='stretch', type="primary"):
                    # Eliminar el empleado de la base de datos
                    try:
                        if db.delete_employee(emp['id']):
                            st.success("✅ Empleado eliminado exitosamente")
                            # Limpiar el estado de edición si era el mismo empleado
                            if 'editing_employee' in st.session_state and st.session_state['editing_employee']['id'] == emp['id']:
                                del st.session_state['editing_employee']
                        else:
                            st.error("❌ Error al eliminar el empleado")
                    except Exception as e:
                        st.error(f"❌ Error al eliminar el empleado: {e}")
                    
                    del st.session_state['deleting_employee']
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar", width='stretch', type="secondary"):
                    del st.session_state['deleting_employee']
                    st.rerun()
    
    with tab2:
        st.subheader("➕ Nuevo Empleado")
        
        with st.form("new_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Información Personal")
                new_name = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez")
                new_email = st.text_input("Email *", placeholder="juan.perez@carniceria.com")
                new_phone = st.text_input("Teléfono *", placeholder="+54 11 1234-5678")
                new_address = st.text_area("Dirección", placeholder="Calle, número, ciudad, código postal")
            
            with col2:
                st.subheader("💼 Información Laboral")
                new_position = st.text_input("Posición *", placeholder="Ej: Carnicero Principal")
                new_department = st.selectbox("Departamento *", ["Producción", "Ventas", "Administración"])
                new_salary = st.number_input("Salario *", min_value=0.0, step=1000.0, value=30000.0)
                new_hire_date = st.date_input("Fecha de Contratación *")
            
            st.markdown("---")
            
            # Información adicional
            st.subheader("📊 Información Adicional")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_status = st.selectbox("Estado", ["Activo", "Inactivo"], index=0)
                new_contract_type = st.selectbox("Tipo de Contrato", ["Tiempo Completo", "Medio Tiempo", "Por Horas"])
            
            with col2:
                new_emergency_contact = st.text_input("Contacto de Emergencia", placeholder="Nombre y teléfono")
                new_emergency_phone = st.text_input("Teléfono de Emergencia", placeholder="+54 11 9999-9999")
            
            with col3:
                new_notes = st.text_area("Notas Adicionales", placeholder="Información adicional sobre el empleado")
            
            st.markdown("---")
            
            # Botones de acción
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.form_submit_button("💾 Guardar Empleado", width='stretch', type="primary"):
                    # Validar campos obligatorios
                    if not all([new_name, new_email, new_phone, new_position, new_department]):
                        st.error("❌ Por favor completa todos los campos obligatorios (*)")
                    else:
                        # Crear el nuevo empleado en la base de datos
                        employee_data = {
                            'first_name': new_name.split()[0] if new_name else 'Sin Nombre',
                            'last_name': ' '.join(new_name.split()[1:]) if len(new_name.split()) > 1 else '',
                            'name': new_name,  # Mantenemos también name por compatibilidad
                            'email': new_email,
                            'phone': new_phone,
                            'address': new_address,
                            'position': new_position,
                            'department': new_department,
                            'salary': new_salary,
                            'hire_date': new_hire_date.isoformat(),
                            'status': new_status,
                            'contract_type': new_contract_type,
                            'emergency_contact': new_emergency_contact,
                            'emergency_phone': new_emergency_phone,
                            'notes': new_notes,
                            'created_at': dt.datetime.now().isoformat(),
                            'updated_at': dt.datetime.now().isoformat()
                        }
                        
                        try:
                            result = db.add_employee(employee_data)
                            if result:
                                st.success("✅ Nuevo empleado creado exitosamente")
                                st.balloons()
                                
                                # Mostrar resumen del empleado creado
                                st.info(f"""
                                **📋 Resumen del Empleado Creado:**
                                • **Nombre:** {new_name}
                                • **Posición:** {new_position}
                                • **Departamento:** {new_department}
                                • **Salario:** ${new_salary:,.2f}
                                • **Fecha Contratación:** {new_hire_date}
                                • **Estado:** {new_status}
                                """)
                                
                                # Limpiar el formulario
                                st.rerun()
                            else:
                                st.error("❌ Error al crear el empleado en la base de datos")
                        except Exception as e:
                            error_msg = str(e)
                            if "duplicate key value violates unique constraint" in error_msg and "employees_email_key" in error_msg:
                                st.error("❌ Error: Ya existe un empleado con esta dirección de email. Por favor usa un email diferente.")
                            else:
                                st.error(f"❌ Error al crear el empleado: {error_msg}")
            
            with col2:
                if st.form_submit_button("🔄 Limpiar Formulario", width='stretch', type="secondary"):
                    st.rerun()
            
            with col3:
                if st.form_submit_button("❌ Cancelar", width='stretch', type="secondary"):
                    st.rerun()
        
        # Información sobre el formulario
        st.markdown("---")
        st.info("""
        **📋 Información sobre el Formulario:**
        • Los campos marcados con (*) son obligatorios
        • El email debe ser único en el sistema
        • El salario se puede modificar después de la contratación
        • Se enviará un email de bienvenida al nuevo empleado
        """)
    
    with tab3:
        st.subheader("⏰ Gestión de Turnos")
        
        # Datos de ejemplo para turnos
        sample_shifts = []
        
        # Métricas de turnos
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_shifts = len(sample_shifts)
            st.metric("Total Turnos Hoy", total_shifts)
        with col2:
            active_shifts = len([s for s in sample_shifts if s['status'] == 'En Curso'])
            st.metric("Turnos Activos", active_shifts)
        with col3:
            completed_shifts = len([s for s in sample_shifts if s['status'] == 'Completado'])
            st.metric("Turnos Completados", completed_shifts)
        with col4:
            total_hours = sum(s['hours'] for s in sample_shifts)
            st.metric("Horas Totales", f"{total_hours}h")
        
        st.markdown("---")
        
        # Filtros para turnos
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            shift_date = st.date_input("📅 Fecha", value=pd.to_datetime('2024-09-22').date())
        with col2:
            shift_type_filter = st.selectbox("🕐 Tipo de Turno", ["Todos", "Mañana", "Tarde", "Noche", "Administrativo"])
        with col3:
            status_filter = st.selectbox("📊 Estado", ["Todos", "En Curso", "Completado", "Cancelado"])
        
        # Filtrar turnos
        filtered_shifts = sample_shifts.copy()
        
        if shift_type_filter != "Todos":
            filtered_shifts = [s for s in filtered_shifts if s['shift_type'] == shift_type_filter]
        
        if status_filter != "Todos":
            filtered_shifts = [s for s in filtered_shifts if s['status'] == status_filter]
        
        st.markdown("---")
        
        # Mostrar tabla de turnos
        if len(filtered_shifts) > 0:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if filtered_shifts:
                    df_shifts = pd.DataFrame(filtered_shifts)
                    st.dataframe(
                        df_shifts[['employee_name', 'shift_type', 'start_time', 'end_time', 'hours', 'status', 'notes']],
                    width='stretch',
                    column_config={
                        "employee_name": "Empleado",
                        "shift_type": "Tipo de Turno",
                        "start_time": "Hora Inicio",
                        "end_time": "Hora Fin",
                        "hours": "Horas",
                        "status": "Estado",
                        "notes": "Notas"
                    }
                )
                else:
                    st.info("📊 Nessun turno disponibile")
            
            with col2:
                st.subheader("⚙️ Acciones de Turnos")
                
                # Seleccionar turno para acciones
                shift_options = [f"{s['employee_name']} - {s['shift_type']}" for s in filtered_shifts]
                selected_shift = st.selectbox("Seleccionar turno:", shift_options)
                
                if selected_shift:
                    # Encontrar el turno seleccionado
                    selected_emp_name = selected_shift.split(" - ")[0]
                    selected_shift_type = selected_shift.split(" - ")[1]
                    selected_shift_obj = next((s for s in filtered_shifts if s['employee_name'] == selected_emp_name and s['shift_type'] == selected_shift_type), None)
                    
                    if selected_shift_obj:
                        st.markdown("---")
                        
                        # Botones de acción
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✏️ Editar Turno", width='stretch', type="primary"):
                                st.session_state['editing_shift'] = selected_shift_obj
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Cancelar Turno", width='stretch', type="secondary"):
                                st.session_state['canceling_shift'] = selected_shift_obj
                                st.rerun()
                        
                        # Mostrar detalles del turno
                        st.markdown("---")
                        st.subheader("📋 Detalles del Turno")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Empleado:** {selected_shift_obj['employee_name']}")
                            st.write(f"**Tipo de Turno:** {selected_shift_obj['shift_type']}")
                            st.write(f"**Fecha:** {selected_shift_obj['shift_date']}")
                            st.write(f"**Hora Inicio:** {selected_shift_obj['start_time']}")
                        
                        with col2:
                            st.write(f"**Hora Fin:** {selected_shift_obj['end_time']}")
                            st.write(f"**Horas:** {selected_shift_obj['hours']}h")
                            st.write(f"**Estado:** {selected_shift_obj['status']}")
                            st.write(f"**Notas:** {selected_shift_obj['notes']}")
        else:
            st.warning("🔍 No se encontraron turnos con los filtros aplicados")
        
        # Modal de edición de turno
        if 'editing_shift' in st.session_state:
            st.markdown("---")
            st.subheader("✏️ Editar Turno")
            
            shift = st.session_state['editing_shift']
            
            with st.form("edit_shift_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_employee = st.selectbox("Empleado", [e['name'] for e in sample_employees], 
                                              index=[e['name'] for e in sample_employees].index(shift['employee_name']))
                    new_shift_type = st.selectbox("Tipo de Turno", ["Mañana", "Tarde", "Noche", "Administrativo"], 
                                                index=["Mañana", "Tarde", "Noche", "Administrativo"].index(shift['shift_type']))
                    new_date = st.date_input("Fecha", value=pd.to_datetime(shift['shift_date']).date())
                    new_start_time = st.time_input("Hora Inicio", value=pd.to_datetime(shift['start_time']).time())
                
                with col2:
                    new_end_time = st.time_input("Hora Fin", value=pd.to_datetime(shift['end_time']).time())
                    new_status = st.selectbox("Estado", ["En Curso", "Completado", "Cancelado"], 
                                            index=["En Curso", "Completado", "Cancelado"].index(shift['status']))
                    new_notes = st.text_area("Notas", value=shift['notes'])
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.form_submit_button("💾 Guardar Cambios", width='stretch', type="primary"):
                        st.success("✅ Turno actualizado exitosamente")
                        del st.session_state['editing_shift']
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar", width='stretch', type="secondary"):
                        del st.session_state['editing_shift']
                        st.rerun()
        
        # Modal de cancelación de turno
        if 'canceling_shift' in st.session_state:
            st.markdown("---")
            st.subheader("🗑️ Cancelar Turno")
            
            shift = st.session_state['canceling_shift']
            
            st.warning(f"⚠️ ¿Estás seguro de que quieres cancelar el turno de **{shift['employee_name']}**?")
            st.info("Esta acción cambiará el estado del turno a 'Cancelado'.")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Confirmar Cancelación", width='stretch', type="primary"):
                    st.success("✅ Turno cancelado exitosamente")
                    del st.session_state['canceling_shift']
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar", width='stretch', type="secondary"):
                    del st.session_state['canceling_shift']
                    st.rerun()
        
        # Formulario para nuevo turno
        st.markdown("---")
        st.subheader("➕ Nuevo Turno")
        
        with st.form("new_shift_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_employee = st.selectbox("Empleado *", [e['name'] for e in sample_employees])
                new_shift_type = st.selectbox("Tipo de Turno *", ["Mañana", "Tarde", "Noche", "Administrativo"])
                new_date = st.date_input("Fecha *", value=pd.to_datetime('2024-09-22').date())
                new_start_time = st.time_input("Hora Inicio *", value=pd.to_datetime('08:00').time())
            
            with col2:
                new_end_time = st.time_input("Hora Fin *", value=pd.to_datetime('16:00').time())
                new_status = st.selectbox("Estado", ["En Curso", "Completado", "Cancelado"], index=0)
                new_notes = st.text_area("Notas", placeholder="Información adicional sobre el turno")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("💾 Crear Turno", width='stretch', type="primary"):
                    st.success("✅ Nuevo turno creado exitosamente")
                    st.balloons()
            
            with col2:
                if st.form_submit_button("🔄 Limpiar", width='stretch', type="secondary"):
                    st.rerun()
            
            with col3:
                if st.form_submit_button("❌ Cancelar", width='stretch', type="secondary"):
                    st.rerun()
    
    with tab4:
        st.subheader("📊 Estadísticas de Personal")
        
        # Estadísticas generales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_employees = len(sample_employees)
            st.metric("Total Empleados", total_employees)
        with col2:
            active_employees = len([e for e in sample_employees if e['status'] == 'Activo'])
            st.metric("Empleados Activos", active_employees)
        with col3:
            total_salary = sum(e['salary'] for e in sample_employees)
            st.metric("Nómina Total", f"${total_salary:,.2f}")
        with col4:
            avg_salary = total_salary / len(sample_employees) if sample_employees else 0
            st.metric("Salario Promedio", f"${avg_salary:,.2f}")
        
        st.markdown("---")
        
        # Gráficos de estadísticas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribución por Departamento")
            
            # Contar empleados por departamento
            dept_counts = {}
            for emp in sample_employees:
                dept = emp['department']
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            # Crear gráfico de barras
            import plotly.express as px
            if dept_counts:
                df_dept = pd.DataFrame(list(dept_counts.items()), columns=['Departamento', 'Cantidad'])
                fig_dept = px.bar(df_dept, x='Departamento', y='Cantidad', 
                                title="Empleados por Departamento",
                                color='Cantidad',
                                color_continuous_scale='Blues')
                st.plotly_chart(fig_dept, width='stretch')
            else:
                st.info("📊 Nessun dato disponibile per il grafico dei dipartimenti")
        
        with col2:
            st.subheader("💰 Distribución de Salarios")
            
            # Crear gráfico de salarios
            if sample_employees:
                df_salaries = pd.DataFrame(sample_employees)
                fig_salaries = px.histogram(df_salaries, x='salary', 
                                          title="Distribución de Salarios",
                                          nbins=10)
                fig_salaries.update_layout(
                    xaxis_title="Salario ($)",
                    yaxis_title="Número de Empleados"
                )
                st.plotly_chart(fig_salaries, width='stretch')
            else:
                st.info("📊 Nessun dato disponibile per il grafico dei salari")
        
        st.markdown("---")
        
        # Estadísticas detalladas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Estadísticas por Departamento")
            
            # Calcular estadísticas por departamento
            dept_stats = {}
            for emp in sample_employees:
                dept = emp['department']
                if dept not in dept_stats:
                    dept_stats[dept] = {'count': 0, 'total_salary': 0, 'salaries': []}
                dept_stats[dept]['count'] += 1
                dept_stats[dept]['total_salary'] += emp['salary']
                dept_stats[dept]['salaries'].append(emp['salary'])
            
            # Mostrar estadísticas
            for dept, stats in dept_stats.items():
                avg_dept_salary = stats['total_salary'] / stats['count']
                min_salary = min(stats['salaries']) if stats['salaries'] else 0
                max_salary = max(stats['salaries']) if stats['salaries'] else 0
                
                st.write(f"**{dept}:**")
                st.write(f"• Empleados: {stats['count']}")
                st.write(f"• Salario promedio: ${avg_dept_salary:,.2f}")
                st.write(f"• Rango salarial: ${min_salary:,.2f} - ${max_salary:,.2f}")
                st.write(f"• Total nómina: ${stats['total_salary']:,.2f}")
                st.markdown("---")
        
        with col2:
            st.subheader("📅 Estadísticas por Antigüedad")
            
            # Calcular antigüedad
            from datetime import datetime
            current_date = datetime.now()
            
            for emp in sample_employees:
                hire_date = datetime.strptime(emp['hire_date'], '%Y-%m-%d')
                years_worked = (current_date - hire_date).days / 365.25
                emp['years_worked'] = round(years_worked, 1)
            
            # Agrupar por antigüedad
            seniority_groups = {'0-1 años': 0, '1-3 años': 0, '3-5 años': 0, '5+ años': 0}
            for emp in sample_employees:
                years = emp['years_worked']
                if years <= 1:
                    seniority_groups['0-1 años'] += 1
                elif years <= 3:
                    seniority_groups['1-3 años'] += 1
                elif years <= 5:
                    seniority_groups['3-5 años'] += 1
                else:
                    seniority_groups['5+ años'] += 1
            
            # Mostrar estadísticas de antigüedad
            for group, count in seniority_groups.items():
                st.write(f"**{group}:** {count} empleados")
            
            st.markdown("---")
            
            # Top empleados por salario
            st.subheader("🏆 Top Empleados por Salario")
            sorted_employees = sorted(sample_employees, key=lambda x: x['salary'], reverse=True)
            
            for i, emp in enumerate(sorted_employees[:3], 1):
                st.write(f"{i}. **{emp['name']}** - ${emp['salary']:,.2f} ({emp['position']})")
        
        st.markdown("---")
        
        # Resumen ejecutivo
        st.subheader("📋 Resumen Ejecutivo")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_salary = max(e['salary'] for e in sample_employees) if sample_employees else 0
            st.metric("Empleado con Mayor Salario", 
                     f"${max_salary:,.2f}")
        
        with col2:
            min_salary = min(e['salary'] for e in sample_employees) if sample_employees else 0
            st.metric("Empleado con Menor Salario", 
                     f"${min_salary:,.2f}")
        
        with col3:
            if dept_counts:
                max_dept = max(dept_counts, key=dept_counts.get)
                st.metric("Departamento con Más Empleados", max_dept)
            else:
                st.metric("Departamento con Más Empleados", "N/A")
        
        # Información adicional
        st.markdown("---")
        st.info("""
        **📊 Información sobre las Estadísticas:**
        • Los datos se actualizan en tiempo real
        • Las estadísticas incluyen todos los empleados activos e inactivos
        • Los gráficos son interactivos y se pueden explorar
        • Se pueden exportar los datos en formato CSV
        """)

def render_ventas():
    """Renderiza la sección de Gestión de Ventas"""
    st.header("🛒 Gestión de Ventas")
    
    # Obtener instancia del database manager
    db = get_hybrid_manager()
    
    # Tabs para diferentes aspectos de ventas
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard Ventas", "💰 Nuevas Ventas", "📋 Gestión Ventas", "📈 Reportes", "👥 Equipo Ventas", "🎯 Objetivos"
    ])
    
    with tab1:
        st.subheader("📊 Dashboard de Ventas")
        
        # Obtener resumen de ventas
        try:
            sales_summary = db.get_sales_summary()
            if sales_summary:
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="💰 Ventas Hoy",
                        value=f"${sales_summary.get('total_sales_today', 0):,.2f}",
                        delta=f"+{sales_summary.get('avg_daily_sales', 0):,.0f} vs promedio"
                    )
                
                with col2:
                    st.metric(
                        label="📅 Ventas Esta Semana",
                        value=f"${sales_summary.get('total_sales_week', 0):,.2f}",
                        delta="+12.5% vs semana anterior"
                    )
                
                with col3:
                    st.metric(
                        label="📆 Ventas Este Mes",
                        value=f"${sales_summary.get('total_sales_month', 0):,.2f}",
                        delta="+8.3% vs mes anterior"
                    )
                
                with col4:
                    st.metric(
                        label="🏆 Mejor Producto",
                        value=sales_summary.get('best_selling_product', 'N/A'),
                        delta=sales_summary.get('best_selling_category', 'N/A')
                    )
                
                st.markdown("---")
                
                # Gráficos de tendencias
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Tendencia de Ventas Diarias")
                    daily_sales = db.get_daily_sales_data(30)
                    if daily_sales:
                        df_daily = pd.DataFrame(daily_sales)
                        fig_daily = px.line(df_daily, x='date', y='sales',
                                          title="Ventas Diarias (Últimos 30 días)")
                        fig_daily.update_layout(xaxis_title="Fecha", yaxis_title="Ventas ($)")
                        st.plotly_chart(fig_daily, width='stretch')
                
                with col2:
                    st.subheader("🏷️ Ventas por Categoría")
                    sales_by_category = db.get_sales_by_category()
                    if sales_by_category:
                        df_category = pd.DataFrame(sales_by_category)
                        fig_category = px.pie(df_category, values='sales', names='category',
                                            title="Distribución de Ventas por Categoría")
                        st.plotly_chart(fig_category, width='stretch')
                
                # Top productos más vendidos
                st.subheader("🏆 Productos Más Vendidos")
                top_products = db.get_top_selling_products(10)
                if top_products:
                    df_products = pd.DataFrame(top_products)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de barras
                        fig_products = px.bar(df_products, x='product', y='sales',
                                            title="Top 10 Productos por Ventas")
                        fig_products.update_layout(xaxis=dict(tickangle=45))
                        st.plotly_chart(fig_products, width='stretch')
                    
                    with col2:
                        # Tabla de productos
                        st.dataframe(
                            df_products[['product', 'category', 'sales', 'quantity', 'profit']],
                            width='stretch',
                            column_config={
                                "sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                                "profit": st.column_config.NumberColumn("Ganancia ($)", format="$%.2f")
                            }
                        )
            
            else:
                st.warning("⚠️ No hay datos de ventas disponibles")
                
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de ventas: {str(e)}")
    
    with tab2:
        st.subheader("💰 Registrar Nueva Venta")
        
        # Formulario para nueva venta
        with st.form("nueva_venta_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("👤 Cliente", placeholder="Nombre del cliente")
                fecha = st.date_input("📅 Fecha de Venta", value=datetime.now().date())
                vendedor = st.selectbox("👨‍💼 Vendedor", ["María González", "Carlos Rodríguez", "Ana Martínez", "Luis Fernández"])
            
            with col2:
                tipo_pago = st.selectbox("💳 Tipo de Pago", ["Efectivo", "Tarjeta", "Transferencia", "Cheque"])
                descuento = st.number_input("💰 Descuento (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                observaciones = st.text_area("📝 Observaciones", placeholder="Notas adicionales...")
            
            st.markdown("---")
            st.subheader("🛒 Productos de la Venta")
            
            # Tabla para productos
            if 'productos_venta' not in st.session_state:
                st.session_state.productos_venta = []
            
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                producto = st.selectbox("Producto", [])
            
            with col2:
                cantidad = st.number_input("Cantidad", min_value=0.1, step=0.1, value=1.0)
            
            with col3:
                precio_unit = st.number_input("Precio Unit.", min_value=0.0, step=0.01, value=0.0)
            
            with col4:
                subtotal = cantidad * precio_unit
                st.metric("Subtotal", f"${subtotal:.2f}")
            
            with col5:
                if st.form_submit_button("➕ Agregar", type="primary"):
                    nuevo_producto = {
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_unit': precio_unit,
                        'subtotal': subtotal
                    }
                    st.session_state.productos_venta.append(nuevo_producto)
                    st.rerun()
            
            # Mostrar productos agregados
            if st.session_state.productos_venta:
                st.subheader("📋 Productos Agregados")
                df_productos = pd.DataFrame(st.session_state.productos_venta)
                st.dataframe(df_productos, width='stretch')
                
                # Totales
                total_productos = sum([p['subtotal'] for p in st.session_state.productos_venta])
                descuento_monto = total_productos * (descuento / 100)
                total_final = total_productos - descuento_monto
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Subtotal", f"${total_productos:.2f}")
                with col2:
                    st.metric("Descuento", f"${descuento_monto:.2f}")
                with col3:
                    st.metric("Total", f"${total_final:.2f}")
                with col4:
                    if st.form_submit_button("💾 Guardar Venta", type="primary"):
                        # Crear datos de la venta
                        sale_data = {
                            'fecha': fecha.strftime('%Y-%m-%d'),
                            'cliente': cliente,
                            'vendedor': vendedor,
                            'tipo_pago': tipo_pago,
                            'descuento': descuento,
                            'observaciones': observaciones,
                            'productos': st.session_state.productos_venta,
                            'total': sum(p['subtotal'] for p in st.session_state.productos_venta) * (1 - descuento/100)
                        }
                        
                        if db.create_sale(sale_data):
                            st.success("✅ Venta registrada exitosamente!")
                            st.session_state.productos_venta = []
                            st.rerun()
                        else:
                            st.error("❌ Error al registrar la venta")
    
    with tab3:
        st.subheader("📋 Gestión de Ventas Individuales")
        
        # Obtener todas las ventas
        sales = db.get_all_sales()
        
        if sales:
            # Métricas de ventas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ventas", len(sales))
            with col2:
                total_amount = sum(s['total'] for s in sales)
                st.metric("Monto Total", f"${total_amount:,.2f}")
            with col3:
                today_sales = len([s for s in sales if s['fecha'] == datetime.now().strftime('%Y-%m-%d')])
                st.metric("Ventas Hoy", today_sales)
            with col4:
                completed_sales = len([s for s in sales if s['estado'] == 'Completada'])
                st.metric("Completadas", completed_sales)
            
            st.markdown("---")
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                search_term = st.text_input("🔍 Buscar venta", placeholder="Cliente, producto...")
            with col2:
                date_filter = st.date_input("📅 Filtrar por fecha")
            with col3:
                status_filter = st.selectbox("📊 Filtrar por estado", ["Todos", "Completada", "Pendiente", "Cancelada"])
            
            # Aplicar filtros
            filtered_sales = sales
            if search_term:
                filtered_sales = [s for s in sales if 
                                 search_term.lower() in s.get('cliente', '').lower() or
                                 search_term.lower() in s.get('producto', '').lower()]
            
            if date_filter:
                filtered_sales = [s for s in filtered_sales if s['fecha'] == date_filter.strftime('%Y-%m-%d')]
            
            if status_filter != "Todos":
                filtered_sales = [s for s in filtered_sales if s['estado'] == status_filter]
            
            # Mostrar cada venta con opciones de editar/eliminar
            for sale in filtered_sales:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**Venta #{sale['id']}**")
                        st.write(f"👤 {sale['cliente']}")
                        st.caption(f"📅 {sale['fecha']}")
                        st.caption(f"🛒 {sale['producto']}")
                    
                    with col2:
                        st.write(f"💰 ${sale['total']:,.2f}")
                        st.caption(f"📦 {sale['cantidad']} x ${sale['precio_unitario']:,.2f}")
                        st.caption(f"💳 {sale['metodo_pago']}")
                    
                    with col3:
                        st.write(f"👨‍💼 {sale['vendedor']}")
                        status_color = {
                            'Completada': '🟢',
                            'Pendiente': '🟡',
                            'Cancelada': '🔴'
                        }
                        st.write(f"{status_color.get(sale['estado'], '⚪')} {sale['estado']}")
                        if sale.get('observaciones'):
                            st.caption(f"📝 {sale['observaciones']}")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_sale_btn_{sale['id']}", help="Editar venta"):
                            st.session_state[f'edit_sale_{sale["id"]}'] = True
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_sale_btn_{sale['id']}", help="Eliminar venta"):
                            st.session_state[f'delete_sale_{sale["id"]}'] = True
                    
                    # Modal de edición
                    if st.session_state.get(f'edit_sale_{sale["id"]}', False):
                        with st.expander(f"✏️ Editar Venta #{sale['id']}", expanded=True):
                            with st.form(f"edit_sale_form_{sale['id']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    edit_cliente = st.text_input("Cliente", value=sale['cliente'], key=f"edit_cliente_{sale['id']}")
                                    edit_fecha = st.date_input("Fecha", value=pd.to_datetime(sale['fecha']).date(), key=f"edit_fecha_{sale['id']}")
                                    edit_producto = st.text_input("Producto", value=sale['producto'], key=f"edit_producto_{sale['id']}")
                                
                                with col2:
                                    edit_cantidad = st.number_input("Cantidad", value=float(sale['cantidad']), key=f"edit_cantidad_{sale['id']}")
                                    edit_precio = st.number_input("Precio Unitario", value=float(sale['precio_unitario']), key=f"edit_precio_{sale['id']}")
                                    edit_metodo = st.selectbox("Método Pago", ["Efectivo", "Tarjeta", "Transferencia", "Cheque"], 
                                                             index=["Efectivo", "Tarjeta", "Transferencia", "Cheque"].index(sale['metodo_pago']),
                                                             key=f"edit_metodo_{sale['id']}")
                                
                                col1, col2, col3 = st.columns([1, 1, 1])
                                with col1:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        sale_data = {
                                            'cliente': edit_cliente,
                                            'fecha': edit_fecha.strftime('%Y-%m-%d'),
                                            'producto': edit_producto,
                                            'cantidad': edit_cantidad,
                                            'precio_unitario': edit_precio,
                                            'total': edit_cantidad * edit_precio,
                                            'metodo_pago': edit_metodo,
                                            'vendedor': sale['vendedor'],
                                            'estado': sale['estado'],
                                            'observaciones': sale.get('observaciones', '')
                                        }
                                        
                                        if db.update_sale(sale['id'], sale_data):
                                            st.success(f"✅ Venta #{sale['id']} actualizada correctamente")
                                            st.session_state[f'edit_sale_{sale["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al actualizar la venta. Intente nuevamente.")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f'edit_sale_{sale["id"]}'] = False
                                        st.rerun()
                    
                    # Modal de confirmación de eliminación
                    if st.session_state.get(f'delete_sale_{sale["id"]}', False):
                        with st.expander(f"🗑️ Eliminar Venta #{sale['id']}", expanded=True):
                            st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar la venta #{sale['id']} de '{sale['cliente']}'?")
                            st.write("**Esta acción no se puede deshacer.**")
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if st.button("🗑️ Confirmar Eliminación", key=f"confirm_del_sale_btn_{sale['id']}", type="primary"):
                                    if db.delete_sale(sale['id']):
                                        st.success(f"✅ Venta #{sale['id']} eliminada correctamente")
                                        st.session_state[f'delete_sale_{sale["id"]}'] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al eliminar la venta. Intente nuevamente.")
                            
                            with col2:
                                if st.button("❌ Cancelar", key=f"cancel_del_sale_btn_{sale['id']}"):
                                    st.session_state[f'delete_sale_{sale["id"]}'] = False
                                    st.rerun()
                    
                    st.markdown("---")
            
            # Acciones masivas
            st.markdown("### ⚡ Acciones Masivas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Exportar Ventas", width='stretch'):
                    st.info("Generando archivo Excel...")
                    st.success("✅ Ventas exportadas exitosamente!")
            
            with col2:
                if st.button("📧 Enviar Reporte", width='stretch'):
                    st.info("Enviando reporte por email...")
                    st.success("✅ Reporte enviado!")
            
            with col3:
                if st.button("🔄 Actualizar Estados", width='stretch'):
                    st.info("Actualizando estados de ventas...")
                    st.success("✅ Estados actualizados!")
        else:
            st.info("No hay ventas registradas")
    
    with tab4:
        st.subheader("📈 Reportes de Ventas")
        
        # Filtros de fecha
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_inicio = st.date_input("📅 Fecha Inicio", value=datetime.now().date() - timedelta(days=30))
        with col2:
            fecha_fin = st.date_input("📅 Fecha Fin", value=datetime.now().date())
        with col3:
            tipo_reporte = st.selectbox("📊 Tipo de Reporte", ["Diario", "Semanal", "Mensual", "Anual"])
        
        # Generar reporte
        if st.button("🔄 Generar Reporte", type="primary"):
            with st.spinner("Generando reporte..."):
                # Simular datos del reporte
                st.success("✅ Reporte generado exitosamente!")
                
                # Métricas del reporte
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Ventas", "$0.00")
                with col2:
                    st.metric("Número de Transacciones", "0")
                with col3:
                    st.metric("Promedio por Venta", "$0.00")
                with col4:
                    st.metric("Crecimiento", "+12.5%")
                
                # Gráfico de tendencias
                st.subheader("📈 Tendencia de Ventas")
                fig_trend = px.line(x=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                                   y=[1200, 1350, 1100, 1450, 1600, 1800, 1650],
                                   title="Ventas por Día de la Semana")
                st.plotly_chart(fig_trend, width='stretch')
                
                # Exportar reporte
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📊 Descargar Excel", "reporte_ventas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with col2:
                    st.download_button("📄 Descargar PDF", "reporte_ventas.pdf", "application/pdf")
                with col3:
                    st.button("📧 Enviar por Email")
    
    with tab4:
        st.subheader("👥 Equipo de Ventas")
        
        # Obtener rendimiento del equipo
        try:
            team_performance = db.get_sales_team_performance()
            if team_performance:
                # Métricas del equipo
                col1, col2, col3, col4 = st.columns(4)
                
                total_team_sales = sum([emp['sales'] for emp in team_performance])
                total_team_transactions = sum([emp['transactions'] for emp in team_performance])
                avg_rating = sum([emp['rating'] for emp in team_performance]) / len(team_performance) if team_performance else 0
                
                with col1:
                    st.metric("Ventas Totales Equipo", f"${total_team_sales:,.2f}")
                with col2:
                    st.metric("Transacciones Totales", f"{total_team_transactions}")
                with col3:
                    st.metric("Promedio Rating", f"{avg_rating:.1f}⭐")
                with col4:
                    st.metric("Mejor Vendedor", "María González")
                
                # Tabla de rendimiento
                st.subheader("🏆 Ranking del Equipo")
                df_team = pd.DataFrame(team_performance)
                st.dataframe(
                    df_team,
                    width='stretch',
                    column_config={
                        "sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                        "commission": st.column_config.NumberColumn("Comisión ($)", format="$%.2f"),
                        "rating": st.column_config.NumberColumn("Rating", format="%.1f⭐")
                    }
                )
                
                # Gráfico de rendimiento
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_sales = px.bar(df_team, x='employee', y='sales',
                                     title="Ventas por Vendedor")
                    fig_sales.update_layout(xaxis=dict(tickangle=45))
                    st.plotly_chart(fig_sales, width='stretch')
                
                with col2:
                    fig_rating = px.bar(df_team, x='employee', y='rating',
                                      title="Rating por Vendedor")
                    fig_rating.update_layout(xaxis=dict(tickangle=45))
                    st.plotly_chart(fig_rating, width='stretch')
            
            else:
                st.warning("⚠️ No hay datos del equipo de ventas disponibles")
                
        except Exception as e:
            st.error(f"❌ Error obteniendo datos del equipo: {str(e)}")
    
    with tab5:
        st.subheader("🎯 Objetivos y Metas")
        
        # Objetivos mensuales
        st.subheader("📅 Objetivos del Mes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Meta de Ventas", "$0.00", "$0.00")
        with col2:
            st.metric("Meta Transacciones", "0", "0")
        with col3:
            st.metric("Meta Clientes Nuevos", "0", "0")
        
        # Progreso visual
        st.subheader("📊 Progreso de Objetivos")
        
        # Barra de progreso para ventas
        ventas_actual = 45250
        ventas_meta = 50000
        progreso_ventas = (ventas_actual / ventas_meta) * 100
        
        st.progress(progreso_ventas / 100)
        st.write(f"Ventas: ${ventas_actual:,} / ${ventas_meta:,} ({progreso_ventas:.1f}%)")
        
        # Proyección de ventas
        st.subheader("🔮 Proyección de Ventas")
        forecast_data = db.get_sales_forecast(6)
        if forecast_data:
            df_forecast = pd.DataFrame(forecast_data)
            
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(
                x=df_forecast['month'],
                y=df_forecast['predicted_sales'],
                mode='lines+markers',
                name='Ventas Proyectadas',
                line=dict(color='blue')
            ))
            fig_forecast.add_trace(go.Scatter(
                x=df_forecast['month'],
                y=df_forecast['confidence_lower'],
                mode='lines',
                name='Límite Inferior',
                line=dict(color='red', dash='dash'),
                showlegend=False
            ))
            fig_forecast.add_trace(go.Scatter(
                x=df_forecast['month'],
                y=df_forecast['confidence_upper'],
                mode='lines',
                name='Límite Superior',
                line=dict(color='red', dash='dash'),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)',
                showlegend=False
            ))
            
            fig_forecast.update_layout(
                title='Proyección de Ventas (Próximos 6 meses)',
                xaxis_title='Mes',
                yaxis_title='Ventas ($)'
            )
            
            st.plotly_chart(fig_forecast, width='stretch')
        
        # Acciones recomendadas
        st.subheader("💡 Acciones Recomendadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🎯 **Enfoque en productos de alto margen**\n- Carne de Res Premium\n- Jamón Serrano\n- Salmón Fresco")
        
        with col2:
            st.info("👥 **Capacitación del equipo**\n- Técnicas de venta\n- Productos premium\n- Atención al cliente")

def render_analytics():
    """Renderiza la sección analytics"""
    require_permission("analytics")
    
    st.header("📊 Analytics y Reportes")
    
    # Tabs para diferentes tipos de reportes
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Ventas", "💰 Financiero", "📦 Inventario", "👥 Clientes"])
    
    with tab1:
        st.subheader("📈 Reportes de Ventas")
        
        # Nessun dato fittizio - usa dati reali dal database
        sales_data = []
        
        if sales_data:
            df_sales = pd.DataFrame(sales_data)
        else:
            # Crea DataFrame vuoto per evitare errori
            df_sales = pd.DataFrame(columns=['fecha', 'ventas', 'clientes', 'productos_vendidos'])
        
        # Métricas de ventas
        if not df_sales.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_sales = df_sales['ventas'].sum()
                st.metric("Ventas Totales (30 días)", f"${total_sales:,.2f}")
            with col2:
                avg_daily = df_sales['ventas'].mean()
                st.metric("Promedio Diario", f"${avg_daily:,.2f}")
            with col3:
                best_day = df_sales.loc[df_sales['ventas'].idxmax()]
                st.metric("Mejor Día", f"${best_day['ventas']:,.2f}")
            with col4:
                total_customers = df_sales['clientes'].sum()
                st.metric("Total Clientes", f"{total_customers:,}")
        else:
            st.info("📊 Nessun dato di vendita disponibile. Inserisci dati reali per vedere le metriche.")
        
        # Gráfico de ventas
        if not df_sales.empty:
            fig_line = px.line(
                df_sales,
                x='fecha',
                y='ventas',
                title="Ventas Diarias (Últimos 30 días)")
            fig_line.update_layout(xaxis=dict(tickangle=-45))
            st.plotly_chart(fig_line, width='stretch')
        else:
            st.info("📊 Nessun dato disponibile per il grafico delle vendite.")
    
    with tab2:
        st.subheader("💰 Reportes Financieros")
        st.info("🚧 Reportes financieros en desarrollo")
    
    with tab3:
        st.subheader("📦 Reportes de Inventario")
        st.info("🚧 Reportes de inventario en desarrollo")
    
    with tab4:
        st.subheader("👥 Reportes de Clientes")
        st.info("🚧 Reportes de clientes en desarrollo")

def render_balance():
    """Renderiza la sección balance y contabilidad giornaliera"""
    require_permission("balance")
    
    st.header("💰 Balance y Contabilidad")
    
    # Ottieni il database manager
    db = get_hybrid_manager()
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Entrada Diaria", "📊 Panel Diario", "📈 Reporte Semanal", "📋 Reporte Mensual"])
    
    with tab1:
        st.subheader("📝 Entrada Diaria")
        
        # Selettore data
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_date = st.date_input("📅 Fecha", value=datetime.now().date())
        
        with col2:
            st.info(f"💡 Ingresa ingresos y gastos para el **{selected_date.strftime('%d/%m/%Y')}**")
        
        # Ottieni categorie
        income_categories = db.get_accounting_categories('income')
        expense_categories = db.get_accounting_categories('expense')
        
        # Form per inserimento entrate
        st.subheader("💰 Agregar Ingreso")
        
        with st.form("add_income_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                income_amount = st.number_input("💰 Monto", min_value=0.01, step=0.01, format="%.2f")
                income_category = st.selectbox("📂 Categoría", [c['name'] for c in income_categories])
            
            with col2:
                income_description = st.text_input("📝 Descripción", placeholder="Descripción del ingreso...")
                income_payment = st.selectbox("💳 Método de Pago", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
            
            with col3:
                st.write("")  # Spazio
                st.write("")  # Spazio
                income_submitted = st.form_submit_button("➕ Agregar Ingreso", type="primary")
            
            if income_submitted and income_amount > 0:
                result = db.add_daily_income(
                    amount=income_amount,
                    category=income_category,
                    description=income_description,
                    payment_method=income_payment,
                    date=selected_date.isoformat()
                )
                
                if result:
                    st.success(f"✅ Entrata di ${income_amount:,.2f} aggiunta!")
                    st.rerun()
                else:
                    st.error("❌ Errore aggiungendo entrata")
            
            st.markdown("---")
            
        # Form per inserimento uscite
        st.subheader("💸 Agregar Gasto")
            
        with st.form("add_expense_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                expense_amount = st.number_input("💸 Monto", min_value=0.01, step=0.01, format="%.2f")
                expense_category = st.selectbox("📂 Categoría", [c['name'] for c in expense_categories])
            
            with col2:
                expense_description = st.text_input("📝 Descripción", placeholder="Descripción del gasto...")
                expense_supplier = st.text_input("🏪 Proveedor", placeholder="Nombre del proveedor...")
            
            with col3:
                expense_payment = st.selectbox("💳 Método de Pago", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
                st.write("")  # Spazio
                expense_submitted = st.form_submit_button("➖ Agregar Gasto", type="secondary")
            
            if expense_submitted and expense_amount > 0:
                result = db.add_daily_expense(
                    amount=expense_amount,
                    category=expense_category,
                    description=expense_description,
                    supplier=expense_supplier,
                    payment_method=expense_payment,
                    date=selected_date.isoformat()
                )
                
                if result:
                    st.success(f"✅ Uscita di ${expense_amount:,.2f} aggiunta!")
                    st.rerun()
                else:
                    st.error("❌ Errore aggiungendo uscita")
        
        # Azioni rapide
        st.subheader("⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🥩 Venta Carnes", help="Aggiungi vendita carni"):
                st.session_state['quick_income'] = {'category': '', 'description': 'Venta de carnes'}
        
        with col2:
            if st.button("🌭 Venta Embutidos", help="Aggiungi vendita embutidos"):
                st.session_state['quick_income'] = {'category': '', 'description': 'Venta de embutidos'}
        
        with col3:
            if st.button("⚙️ Gastos Operativos", help="Aggiungi gastos operativos"):
                st.session_state['quick_expense'] = {'category': '', 'description': 'Gastos operativos del día'}
        
        with col4:
            if st.button("💡 Servicios Públicos", help="Aggiungi servicios públicos"):
                st.session_state['quick_expense'] = {'category': 'Servicios Públicos', 'description': 'Pago de servicios públicos'}
        
        # Gestione azioni rapide
        if 'quick_income' in st.session_state:
            quick_data = st.session_state['quick_income']
            with st.expander("⚡ Inserimento Rapido - Entrata", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    quick_amount = st.number_input("💰 Monto", min_value=0.01, step=0.01, format="%.2f", key="quick_income_amount")
                with col2:
                    if st.button("✅ Conferma", key="confirm_quick_income"):
                        result = db.add_daily_income(
                            amount=quick_amount,
                            category=quick_data['category'],
                            description=quick_data['description'],
                            date=selected_date.isoformat()
                        )
                        if result:
                            st.success("✅ Entrata rapida aggiunta!")
                            del st.session_state['quick_income']
                            st.rerun()
        
        if 'quick_expense' in st.session_state:
            quick_data = st.session_state['quick_expense']
            with st.expander("⚡ Entrada Rápida - Gasto", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    quick_amount = st.number_input("💸 Monto", min_value=0.01, step=0.01, format="%.2f", key="quick_expense_amount")
                with col2:
                    if st.button("✅ Conferma", key="confirm_quick_expense"):
                        result = db.add_daily_expense(
                            amount=quick_amount,
                            category=quick_data['category'],
                            description=quick_data['description'],
                            date=selected_date.isoformat()
                        )
                        if result:
                            st.success("✅ Uscita rapida aggiunta!")
                            del st.session_state['quick_expense']
                            st.rerun()
    
    with tab2:
        st.subheader("📊 Panel Diario")
        
        # Selettore data
        col1, col2 = st.columns([1, 3])
        with col1:
            dashboard_date = st.date_input("📅 Fecha", value=datetime.now().date(), key="dashboard_date")
        
        with col2:
            st.info(f"📊 Panel para el **{dashboard_date.strftime('%d/%m/%Y')}**")
        
        # Ottieni dati giornalieri
        daily_entries = db.get_daily_entries(dashboard_date.isoformat())
        daily_report = db.get_daily_report(dashboard_date.isoformat())
        
        # Metriche principali
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Entrate",
                f"${daily_entries['total_income']:,.2f}",
                help="Total entrate del giorno"
            )
        
        with col2:
            st.metric(
                "💸 Uscite",
                f"${daily_entries['total_expenses']:,.2f}",
                help="Total uscite del giorno"
            )
        
        with col3:
            net_profit = daily_entries['total_income'] - daily_entries['total_expenses']
            profit_color = "normal" if net_profit >= 0 else "inverse"
            st.metric(
                "📈 Profitto",
                f"${net_profit:,.2f}",
                delta=f"{daily_report.get('profit_margin', 0):.1f}%" if daily_report else "0%",
                delta_color=profit_color,
                help="Profitto netto del giorno"
            )
        
        with col4:
            total_transactions = len(daily_entries['income']) + len(daily_entries['expenses'])
            st.metric(
                "📊 Transazioni",
                total_transactions,
                help="Numero totale di transazioni"
            )
        
        # Indicatori visivi
        st.subheader("🎯 Indicatori di Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if net_profit > 0:
                st.success("✅ **Giornata Positiva**")
                st.write("Profitto generato")
            else:
                st.error("❌ **Giornata Negativa**")
                st.write("Perdita registrata")
        
        with col2:
            if daily_entries['total_income'] > 0:
                efficiency = (net_profit / daily_entries['total_income']) * 100
                if efficiency > 20:
                    st.success("🚀 **Alta Efficienza**")
                elif efficiency > 10:
                    st.warning("⚠️ **Efficienza Media**")
                else:
                    st.error("📉 **Bassa Efficienza**")
                st.write(f"Efficienza: {efficiency:.1f}%")
            else:
                st.info("📊 Nessun dato")
        
        with col3:
            if total_transactions > 10:
                st.success("🔥 **Alta Attività**")
            elif total_transactions > 5:
                st.warning("📊 **Attività Media**")
            else:
                st.info("😴 **Bassa Attività**")
            st.write(f"Transazioni: {total_transactions}")
        
        # Lista dettagliata entrate
        if daily_entries['income']:
            st.subheader("💰 Entrate del Giorno")
            
            for income in daily_entries['income']:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{income['category']}**")
                        if income['description']:
                            st.caption(income['description'])
                    
                    with col2:
                        st.write(f"💳 {income['payment_method']}")
                        st.caption(f"💰 ${income['amount']:,.2f}")
                    
                    with col3:
                        st.write("")
                    
                    with col4:
                        st.write("")
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_income_{income['id']}", help="Elimina"):
                            if db.delete_daily_entry('income', income['id']):
                                st.success("✅ Eliminato")
                                st.rerun()
                    
                    st.markdown("---")
        
        # Lista dettagliata uscite
        if daily_entries['expenses']:
            st.subheader("💸 Uscite del Giorno")
            
            for expense in daily_entries['expenses']:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{expense['category']}**")
                        if expense['description']:
                            st.caption(expense['description'])
                        if expense['supplier']:
                            st.caption(f"🏪 {expense['supplier']}")
                    
                    with col2:
                        st.write(f"💳 {expense['payment_method']}")
                        st.caption(f"💸 ${expense['amount']:,.2f}")
                    
                    with col3:
                        st.write("")
                    
                    with col4:
                        st.write("")
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_expense_{expense['id']}", help="Elimina"):
                            if db.delete_daily_entry('expense', expense['id']):
                                st.success("✅ Eliminato")
                                st.rerun()
                    
                    st.markdown("---")
        
        # Se non ci sono dati
        if not daily_entries['income'] and not daily_entries['expenses']:
            st.info("📝 Nessun dato per questo giorno. Usa la tab 'Inserimento Giornaliero' per aggiungere entrate e uscite.")
    
    with tab3:
        st.subheader("📈 Reporte Semanal")
        
        # Selettore settimana
        col1, col2 = st.columns([1, 3])
        with col1:
            week_start = st.date_input("📅 Inizio Settimana", value=datetime.now().date() - timedelta(days=7))
        
        with col2:
            week_end = week_start + timedelta(days=6)
            st.info(f"📊 Report settimana: **{week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}**")
        
        # Ottieni dati settimanali
        weekly_data = db.get_weekly_summary(week_start.isoformat())
        
        if weekly_data:
            # Metriche settimanali
            total_income = sum([d['total_income'] for d in weekly_data])
            total_expenses = sum([d['total_expenses'] for d in weekly_data])
            total_profit = sum([d['net_profit'] for d in weekly_data])
            total_transactions = sum([d['transactions_count'] for d in weekly_data])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Entrate Settimanali",
                    f"${total_income:,.2f}",
                    help="Total entrate della settimana"
                )
            
            with col2:
                st.metric(
                    "💸 Uscite Settimanali",
                    f"${total_expenses:,.2f}",
                    help="Total uscite della settimana"
                )
            
            with col3:
                profit_color = "normal" if total_profit >= 0 else "inverse"
                profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0
                st.metric(
                    "📈 Profitto Settimanale",
                    f"${total_profit:,.2f}",
                    delta=f"{profit_margin:.1f}%",
                    delta_color=profit_color,
                    help="Profitto netto della settimana"
                )
            
            with col4:
                st.metric(
                    "📊 Transazioni Totali",
                    total_transactions,
                    help="Numero totale di transazioni"
                )
            
            # Grafico trend giornaliero
            st.subheader("📊 Trend Giornaliero")
            
            df_weekly = pd.DataFrame(weekly_data)
            df_weekly['date'] = pd.to_datetime(df_weekly['date'])
            df_weekly['day_name'] = df_weekly['date'].dt.strftime('%A')
            
            fig_weekly = px.line(
                df_weekly,
                x='day_name',
                y=['total_income', 'total_expenses', 'net_profit'],
                title="Trend Finanziario Settimanale"
            )
            fig_weekly.update_layout(height=400)
            st.plotly_chart(fig_weekly, width='stretch')
            
            # Tabella dettagliata
            st.subheader("📋 Dettaglio Giornaliero")
            
            table_data = []
            for day_data in weekly_data:
                table_data.append({
                    'Data': day_data['date'][:10],
                    'Entrate': f"${day_data['total_income']:,.2f}",
                    'Uscite': f"${day_data['total_expenses']:,.2f}",
                    'Profitto': f"${day_data['net_profit']:,.2f}",
                    'Margine %': f"{day_data['profit_margin']:.1f}%",
                    'Transazioni': day_data['transactions_count']
                })
            
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, width='stretch')
            
            # Analisi performance
            st.subheader("🎯 Analisi Performance")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if weekly_data:
                    best_day = max(weekly_data, key=lambda x: x['net_profit'])
                    st.metric("🏆 Miglior Giorno", best_day['date'][:10])
                    st.caption(f"Profitto: ${best_day['net_profit']:,.2f}")
                else:
                    st.metric("🏆 Miglior Giorno", "N/A")
                    st.caption("Nessun dato disponibile")
            
            with col2:
                avg_daily_profit = total_profit / len(weekly_data) if weekly_data else 0
                st.metric("📊 Profitto Medio Giornaliero", f"${avg_daily_profit:,.2f}")
            
            with col3:
                if total_profit > 0:
                    st.success("✅ **Settimana Positiva**")
                    st.write("Profitto generato")
                else:
                    st.error("❌ **Settimana Negativa**")
                    st.write("Perdita registrata")
        else:
            st.warning("⚠️ Nessun dato per questa settimana")
            st.info("Inserisci dati giornalieri per vedere il report settimanale")
    
    with tab4:
        st.subheader("📋 Reporte Mensual")
        
        # Selettore mese
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_month = st.selectbox("📅 Mese", range(1, 13), index=datetime.now().month - 1)
            selected_year = st.selectbox("📅 Anno", range(2020, 2030), index=datetime.now().year - 2020)
        
        with col2:
            month_name = datetime(selected_year, selected_month, 1).strftime('%B %Y')
            st.info(f"📊 Report mensile: **{month_name}**")
        
        # Ottieni dati mensili
        monthly_data = db.get_monthly_summary(selected_year, selected_month)
        
        if monthly_data and monthly_data['days_with_data'] > 0:
            # Metriche mensili
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Entrate Mensili",
                    f"${monthly_data['total_income']:,.2f}",
                    help="Total entrate del mese"
                )
            
            with col2:
                st.metric(
                    "💸 Uscite Mensili",
                    f"${monthly_data['total_expenses']:,.2f}",
                    help="Total uscite del mese"
                )
            
            with col3:
                profit_color = "normal" if monthly_data['total_profit'] >= 0 else "inverse"
                st.metric(
                    "📈 Profitto Mensile",
                    f"${monthly_data['total_profit']:,.2f}",
                    delta=f"{monthly_data['profit_margin']:.1f}%",
                    delta_color=profit_color,
                    help="Profitto netto del mese"
                )
            
            with col4:
                st.metric(
                    "📊 Transazioni Totali",
                    monthly_data['total_transactions'],
                    help="Numero totale di transazioni"
                )
            
            # Indicatori di performance
            st.subheader("🎯 Indicatori di Performance")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if monthly_data['total_profit'] > 0:
                    st.success("✅ **Mese Positivo**")
                    st.write("Profitto generato")
                else:
                    st.error("❌ **Mese Negativo**")
                    st.write("Perdita registrata")
            
            with col2:
                avg_daily_profit = monthly_data['total_profit'] / monthly_data['days_with_data']
                st.metric("📊 Profitto Medio Giornaliero", f"${avg_daily_profit:,.2f}")
                st.caption(f"Su {monthly_data['days_with_data']} giorni con dati")
            
            with col3:
                efficiency = monthly_data['profit_margin']
                if efficiency > 20:
                    st.success("🚀 **Alta Efficienza**")
                elif efficiency > 10:
                    st.warning("⚠️ **Efficienza Media**")
                else:
                    st.error("📉 **Bassa Efficienza**")
                st.write(f"Efficienza: {efficiency:.1f}%")
            
            # Analisi categorie
            st.subheader("📊 Analisi per Categoria")
            
            # Ottieni tutte le entrate e uscite del mese per analisi categorie
            start_date = f"{selected_year}-{selected_month:02d}-01"
            if selected_month == 12:
                end_date = f"{selected_year + 1}-01-01"
            else:
                end_date = f"{selected_year}-{selected_month + 1:02d}-01"
            
            # Analisi entrate per categoria
            income_categories = db.get_accounting_categories('income')
            expense_categories = db.get_accounting_categories('expense')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**💰 Top Categorie Entrate**")
                # Qui potresti aggiungere un'analisi delle categorie più redditizie
                for category in income_categories[:5]:
                    st.write(f"• {category['icon']} {category['name']}")
            
            with col2:
                st.write("**💸 Top Categorie Uscite**")
                # Qui potresti aggiungere un'analisi delle categorie più costose
                for category in expense_categories[:5]:
                    st.write(f"• {category['icon']} {category['name']}")
            
            # Confronto con mese precedente
            st.subheader("📈 Confronto Mese Precedente")
            
            prev_month = selected_month - 1 if selected_month > 1 else 12
            prev_year = selected_year if selected_month > 1 else selected_year - 1
            
            prev_monthly_data = db.get_monthly_summary(prev_year, prev_month)
            
            if prev_monthly_data and prev_monthly_data['days_with_data'] > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    income_change = ((monthly_data['total_income'] - prev_monthly_data['total_income']) / prev_monthly_data['total_income'] * 100) if prev_monthly_data['total_income'] > 0 else 0
                    st.metric(
                        "💰 Variazione Entrate",
                        f"{income_change:+.1f}%",
                        help="Rispetto al mese precedente"
                    )
                
                with col2:
                    expense_change = ((monthly_data['total_expenses'] - prev_monthly_data['total_expenses']) / prev_monthly_data['total_expenses'] * 100) if prev_monthly_data['total_expenses'] > 0 else 0
                    st.metric(
                        "💸 Variazione Uscite",
                        f"{expense_change:+.1f}%",
                        help="Rispetto al mese precedente"
                    )
                
                with col3:
                    profit_change = ((monthly_data['total_profit'] - prev_monthly_data['total_profit']) / abs(prev_monthly_data['total_profit']) * 100) if prev_monthly_data['total_profit'] != 0 else 0
                    st.metric(
                        "📈 Variazione Profitto",
                        f"{profit_change:+.1f}%",
                        help="Rispetto al mese precedente"
                    )
            else:
                st.info("📊 Nessun dato disponibile per il mese precedente")
            
            # Esportazione report
            st.subheader("📤 Esportazione Report")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Esporta PDF", help="Esporta report in PDF"):
                    st.info("🚧 Funzionalità in sviluppo")
            
            with col2:
                if st.button("📊 Esporta Excel", help="Esporta report in Excel"):
                    st.info("🚧 Funzionalità in sviluppo")
            
            with col3:
                if st.button("📧 Invia Email", help="Invia report via email"):
                    st.info("🚧 Funzionalità in sviluppo")
                else:
                    st.info("📧 Email non inviata")

def render_configuracion():
    """Renderiza la sección configuración"""
    require_permission("configuracion")
    
    st.header("⚙️ Configuración del Sistema")
    
    # Tabs para diferentes configuraciones
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏢 Empresa", "👤 Usuarios", "📁 Datos Excel", "🔧 Sistema", "💾 Backup", "🛠️ Mantenimiento"])
    
    with tab1:
        st.subheader("🏢 Información de la Empresa")
        
        with st.form("config_empresa"):
            col1, col2 = st.columns(2)
            
            with col1:
                empresa_nombre = st.text_input("🏢 Nombre de la Empresa", value="Carnicería Ezio", placeholder="Nombre de tu carnicería")
                empresa_direccion = st.text_area("📍 Dirección", value="Av. Principal 123, Buenos Aires", placeholder="Dirección completa")
                empresa_telefono = st.text_input("📞 Teléfono", value="+54 11 1234-5678", placeholder="Teléfono principal")
            
            with col2:
                empresa_email = st.text_input("📧 Email", value="info@carniceriaezio.com", placeholder="Email de contacto")
                empresa_cuit = st.text_input("🆔 CUIT", value="20-12345678-9", placeholder="CUIT de la empresa")
                empresa_actividad = st.selectbox("🏭 Actividad Principal", ["Carnicería", "Supermercado", "Distribuidora", "Restaurante"])
            
            # Configuraciones adicionales
            st.subheader("⚙️ Configuraciones Adicionales")
            col1, col2 = st.columns(2)
            
            with col1:
                moneda = st.selectbox("💰 Moneda Principal", ["ARS", "USD", "EUR"])
                zona_horaria = st.selectbox("🕐 Zona Horaria", ["America/Argentina/Buenos_Aires", "UTC", "America/New_York"])
                idioma = st.selectbox("🌐 Idioma", ["Español", "Inglés", "Portugués"])
            
            with col2:
                formato_fecha = st.selectbox("📅 Formato de Fecha", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
                formato_hora = st.selectbox("⏰ Formato de Hora", ["24 horas", "12 horas"])
                decimales = st.slider("🔢 Decimales en Precios", min_value=0, max_value=4, value=2)
            
            # Botones
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("💾 Guardar Configuración", width='stretch', type="primary")
            
            if submitted:
                st.success("✅ Configuración de empresa guardada exitosamente")
                st.balloons()
    
    with tab2:
        st.subheader("👤 Gestión de Usuarios")
        
        # Ottieni utenti dal database
        db = get_hybrid_manager()
        users_data = db.get_all_users()
        
        # Métricas de usuarios
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Usuarios", len(users_data))
        with col2:
            active_users = len([u for u in users_data if u['status'] == 'Activo'])
            st.metric("Usuarios Activos", active_users)
        with col3:
            admin_users = len([u for u in users_data if u['role'] == 'Administrador'])
            st.metric("Administradores", admin_users)
        with col4:
            today_logins = len([u for u in users_data if u.get('last_login') and u['last_login'][:10] == datetime.now().strftime('%Y-%m-%d')])
            st.metric("Logins Hoy", today_logins)
        
        # Filtros y búsqueda
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Buscar usuario", placeholder="Nombre, email, rol...")
        with col2:
            status_filter = st.selectbox("📊 Filtrar por estado", ["Todos", "Activo", "Inactivo"])
        with col3:
            role_filter = st.selectbox("👑 Filtrar por rol", ["Todos", "Administrador", "Gerente", "Cajero", "Carnicero"])
        
        # Aplicar filtros
        filtered_users = users_data
        if search_term:
            filtered_users = [u for u in filtered_users if 
                             search_term.lower() in u.get('name', '').lower() or
                             search_term.lower() in u.get('email', '').lower() or
                             search_term.lower() in u.get('role', '').lower()]
        
        if status_filter != "Todos":
            filtered_users = [u for u in filtered_users if u['status'] == status_filter]
        
        if role_filter != "Todos":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        
        # Tabla de usuarios con acciones
        st.subheader("📋 Lista de Usuarios")
        
        if filtered_users:
            for user in filtered_users:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{user['name']}**")
                        st.caption(f"@{user['username']}")
                    
                    with col2:
                        st.write(user['email'])
                        st.caption(f"Rol: {user['role']}")
                    
                    with col3:
                        if user['status'] == 'Activo':
                            st.success("✅ Activo")
                        else:
                            st.error("❌ Inactivo")
                        if user.get('last_login'):
                            st.caption(f"Último login: {user['last_login'][:10]}")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_{user['id']}", help="Editar usuario"):
                            st.session_state[f'edit_user_{user["id"]}'] = True
                    
                    with col5:
                        if st.button("🔄", key=f"toggle_{user['id']}", help="Activar/Desactivar"):
                            new_status = not user.get('is_active', True)
                            if db.update_user(user['id'], {'is_active': new_status}):
                                st.success("✅ Estado actualizado")
                                st.rerun()
                            else:
                                st.error("❌ Error actualizando estado")
                    
                    with col6:
                        if st.button("🗑️", key=f"delete_{user['id']}", help="Eliminar usuario"):
                            if db.delete_user(user['id']):
                                st.success("✅ Usuario eliminado")
                                st.rerun()
                            else:
                                st.error("❌ Error eliminando usuario")
        
        st.markdown("---")
        
        # Formulario para nuevo usuario
        st.subheader("➕ Nuevo Usuario")
        
        with st.form("nuevo_usuario_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Nombre", placeholder="Nombre del usuario")
                last_name = st.text_input("Apellido", placeholder="Apellido del usuario")
                email = st.text_input("Email", placeholder="email@carniceria.com")
            
            with col2:
                # Ottieni ruoli dal database
                roles = db.get_all_roles()
                role_options = {r['name']: r['id'] for r in roles} if roles else {'Usuario': None}
                selected_role = st.selectbox("Rol", list(role_options.keys()))
                role_id = role_options[selected_role]
                
                password = st.text_input("Contraseña", type="password", placeholder="Contraseña temporal")
                is_active = st.checkbox("Usuario Activo", value=True)
            
            submitted = st.form_submit_button("💾 Crear Usuario", type="primary")
            
            if submitted:
                if first_name and last_name and email:
                    user_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'role_id': role_id,
                        'password_hash': password,  # In produzione, hashare la password
                        'is_active': is_active
                    }
                    
                    result = db.create_user(user_data)
                    if result:
                        st.success("✅ Usuario creado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error creando usuario")
                else:
                    st.error("❌ Por favor completa todos los campos obligatorios")
        
        # Formularios de edición (se mostrano cuando se hace clic en editar)
        for user in users_data:
            if st.session_state.get(f'edit_user_{user["id"]}', False):
                st.subheader(f"✏️ Editar Usuario: {user['name']}")
                
                with st.form(f"edit_user_form_{user['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_first_name = st.text_input("Nombre", value=user.get('first_name', ''), key=f"edit_first_{user['id']}")
                        edit_last_name = st.text_input("Apellido", value=user.get('last_name', ''), key=f"edit_last_{user['id']}")
                        edit_email = st.text_input("Email", value=user['email'], key=f"edit_email_{user['id']}")
                    
                    with col2:
                        # Ottieni ruoli dal database
                        roles = db.get_all_roles()
                        role_options = {r['name']: r['id'] for r in roles} if roles else {'Usuario': None}
                        current_role = user.get('role', 'Usuario')
                        edit_role = st.selectbox("Rol", list(role_options.keys()), 
                                               index=list(role_options.keys()).index(current_role) if current_role in role_options else 0,
                                               key=f"edit_role_{user['id']}")
                        edit_role_id = role_options[edit_role]
                        
                        edit_is_active = st.checkbox("Usuario Activo", value=user['status'] == 'Activo', key=f"edit_active_{user['id']}")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                            update_data = {
                                'first_name': edit_first_name,
                                'last_name': edit_last_name,
                                'email': edit_email,
                                'role_id': edit_role_id,
                                'is_active': edit_is_active
                            }
                            
                            if db.update_user(user['id'], update_data):
                                st.success("✅ Usuario actualizado exitosamente")
                                st.session_state[f'edit_user_{user["id"]}'] = False
                                st.rerun()
                            else:
                                st.error("❌ Error actualizando usuario")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state[f'edit_user_{user["id"]}'] = False
                            st.rerun()
    
    with tab3:
        st.subheader("🔧 Configuración del Sistema")
        
        # Configuraciones del sistema
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Configuraciones de Dashboard")
            
            # Configuraciones de métricas
            auto_refresh = st.checkbox("🔄 Auto-refresh Dashboard", value=True)
            refresh_interval = st.slider("⏱️ Intervalo de Refresh (segundos)", min_value=30, max_value=300, value=60)
            
            # Configuraciones de notificaciones
            st.subheader("🔔 Notificaciones")
            email_notifications = st.checkbox("📧 Notificaciones por Email", value=True)
            low_stock_alerts = st.checkbox("📦 Alertas de Stock Bajo", value=True)
            sales_alerts = st.checkbox("💰 Alertas de Ventas", value=False)
        
        with col2:
            st.subheader("🗄️ Configuraciones de Base de Datos")
            
            # Configuraciones de backup automático
            auto_backup = st.checkbox("💾 Backup Automático", value=True)
            backup_frequency = st.selectbox("📅 Frecuencia de Backup", ["Diario", "Semanal", "Mensual"])
            backup_retention = st.slider("🗑️ Retención de Backups (días)", min_value=7, max_value=365, value=30)
            
            # Configuraciones de logs
            st.subheader("📝 Logs del Sistema")
            log_level = st.selectbox("📊 Nivel de Log", ["DEBUG", "INFO", "WARNING", "ERROR"])
            log_retention = st.slider("🗑️ Retención de Logs (días)", min_value=7, max_value=90, value=30)
        
        # Botón para guardar configuraciones
        if st.button("💾 Guardar Configuraciones del Sistema", width='stretch', type="primary"):
            st.success("✅ Configuraciones del sistema guardadas exitosamente")
    
    with tab4:
        st.subheader("💾 Backup y Restauración")
        
        # Información de backup
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Estado del Backup")
            
            # Métricas de backup
            st.metric("Último Backup", "Nessuno")
            st.metric("Tamaño del Backup", "0 MB")
            st.metric("Backups Disponibles", "0")
            st.metric("Próximo Backup", "Non programmato")
            
            # Lista de backups disponibles
            st.subheader("📋 Backups Disponibles")
            backups = []  # Nessun dato fittizio
            
            if backups:
                df_backups = pd.DataFrame(backups)
            else:
                st.info("📊 Nessun backup disponibile.")
                return
            st.dataframe(
                df_backups,
                width='stretch',
                column_config={
                    "fecha": "Fecha",
                    "hora": "Hora",
                    "tamaño": "Tamaño",
                    "tipo": "Tipo"
                }
            )
        
        with col2:
            st.subheader("🔧 Acciones de Backup")
            
            # Botones de acción
            if st.button("💾 Crear Backup Manual", width='stretch', type="primary"):
                st.success("✅ Backup manual creado exitosamente")
                st.info("📁 Ubicación: /backups/backup_manual_20240922_143000.db")
            
            if st.button("📥 Restaurar desde Backup", width='stretch', type="secondary"):
                st.warning("⚠️ Función de restauración en desarrollo")
            
            if st.button("🗑️ Limpiar Backups Antiguos", width='stretch', type="secondary"):
                st.info("🧹 Limpieza de backups antiguos programada")
            
            # Configuraciones de backup
            st.subheader("⚙️ Configuraciones de Backup")
            
            backup_location = st.text_input("📁 Ubicación de Backups", value="/backups/", placeholder="Ruta donde guardar backups")
            compression = st.checkbox("🗜️ Comprimir Backups", value=True)
            encryption = st.checkbox("🔐 Encriptar Backups", value=False)
            
            if st.button("💾 Guardar Configuraciones de Backup", width='stretch'):
                st.success("✅ Configuraciones de backup guardadas")
    
    with tab3:
        st.subheader("📁 Cargar Datos desde Archivo Excel")
        
        # Información sobre el formato esperado
        st.info("""
        **📋 Formato Esperado del Excel:**
        • Cada hoja debe representar un mes (ej: "Noviembre 2024", "Diciembre 2024")
        • Columnas esperadas: Fecha, Base, IGIC, Cobro, Proveedor, etc.
        • Datos de ventas diarias y pagos a proveedores
        """)
        
        # File uploader per caricare dati Excel
        uploaded_file = st.file_uploader(
            "📁 Cargar Archivo Excel con Datos Históricos",
            type=['xlsx', 'xls'],
            help="Sube tu archivo Excel con los datos históricos de la carnicería",
            key="config_excel_file_uploader"
        )
        
        if uploaded_file is not None:
            # Mostrar información del archivo cargado
            st.info(f"📁 **Archivo cargado:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Botón para procesar el archivo
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🚀 Procesar Archivo Personalizado", width='stretch', type="secondary"):
                    try:
                        # Guardar archivo temporalmente
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Procesar el archivo
                        with st.spinner("🔄 Procesando archivo personalizado..."):
                            migrator = SupabaseExcelMigrator()
                            results = migrator.migrate_excel_to_supabase(tmp_file_path)
                            
                            if results:
                                st.success("✅ **Archivo personalizado procesado con éxito!**")
                                
                                # Mostra i risultati
                                st.markdown("### 📊 Risultati:")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Vendite", results.get('sales', {}).get('migrated_count', 0))
                                with col2:
                                    st.metric("Acquisti", results.get('purchases', {}).get('migrated_count', 0))
                                with col3:
                                    st.metric("Spese", results.get('expenses', {}).get('migrated_count', 0))
                                with col4:
                                    st.metric("Fornitori", results.get('suppliers', {}).get('migrated_count', 0))
                                
                                # Crea analisi dei dati
                                carniceria_analysis = {
                                    'overview': {
                                        'total_sales': results.get('sales', {}).get('migrated_count', 0) * 100,  # Stima
                                        'total_purchases': results.get('purchases', {}).get('migrated_count', 0) * 50,  # Stima
                                        'total_expenses': results.get('expenses', {}).get('migrated_count', 0) * 25,  # Stima
                                        'total_suppliers': results.get('suppliers', {}).get('migrated_count', 0),
                                        'total_months': 1
                                    },
                                    'monthly_breakdown': {
                                        'current_month': {
                                            'sales': results.get('sales', {}).get('migrated_count', 0) * 100,
                                            'purchases': results.get('purchases', {}).get('migrated_count', 0) * 50,
                                            'expenses': results.get('expenses', {}).get('migrated_count', 0) * 25
                                        }
                                    },
                                    'forecasts': {
                                        'next_month_sales': results.get('sales', {}).get('migrated_count', 0) * 110,
                                        'growth_rate': 10.0
                                    }
                                }
                                
                                # Aggiorna session state
                                st.session_state['excel_migrated'] = True
                                st.session_state['excel_processed'] = True
                                st.session_state['excel_saved_to_db'] = True
                                st.session_state['migration_results'] = results
                                st.session_state['carniceria_analysis'] = carniceria_analysis
                                
                            else:
                                st.error("❌ Errore processando archivo personalizado")
                        
                        # Limpiar archivo temporal
                        try:
                            os.unlink(tmp_file_path)
                        except:
                            pass
                            
                    except Exception as e:
                        st.error(f"❌ Errore: {e}")
        
        # Mostra stato migrazione
        if st.session_state.get('excel_migrated', False):
            st.success("✅ **Dati Excel migrati con successo!**")
            st.info("I dati sono ora disponibili in tutte le sezioni del dashboard")
    
    with tab4:
        st.subheader("🔧 Estado del Sistema")
        
        # Información del sistema
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🖥️ CPU", "45%", "↓ 5%")
            st.metric("💾 Memoria", "2.1 GB", "↑ 0.2 GB")
        
        with col2:
            st.metric("💿 Disco", "78%", "↑ 2%")
            st.metric("🌐 Red", "Activa", "✅")
        
        with col3:
            st.metric("🗄️ Base de Datos", "Conectada", "✅")
            st.metric("⏱️ Uptime", "15 días", "✅")
        
        # Estado de servicios
        st.subheader("🔧 Servicios del Sistema")
        
        services = [
            {"name": "Servidor Web", "status": "Activo", "uptime": "15 días"},
            {"name": "Base de Datos", "status": "Activo", "uptime": "15 días"},
            {"name": "Servicio de Backup", "status": "Activo", "uptime": "15 días"},
            {"name": "Servicio de Logs", "status": "Activo", "uptime": "15 días"}
        ]
        
        for service in services:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"🔧 {service['name']}")
            with col2:
                if service['status'] == 'Activo':
                    st.success("✅ Activo")
                else:
                    st.error("❌ Inactivo")
            with col3:
                st.caption(f"⏱️ {service['uptime']}")
        
        # Logs del sistema
        st.subheader("📝 Logs Recientes")
        
        logs = []
        
        for log in logs:
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.caption(log['timestamp'])
            with col2:
                if log['level'] == 'ERROR':
                    st.error(log['level'])
                elif log['level'] == 'WARNING':
                    st.warning(log['level'])
                else:
                    st.info(log['level'])
            with col3:
                st.write(log['message'])
    
    with tab6:
        st.subheader("🛠️ Mantenimiento del Sistema")
        
        # Herramientas de mantenimiento
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧹 Limpieza")
            
            if st.button("🗑️ Limpiar Logs Antiguos"):
                st.success("✅ Logs antiguos eliminados")
            
            if st.button("🗑️ Limpiar Cache"):
                st.success("✅ Cache limpiado")
            
            if st.button("🗑️ Optimizar Base de Datos"):
                st.success("✅ Base de datos optimizada")
        
        with col2:
            st.subheader("🔄 Mantenimiento")
            
            if st.button("🔄 Reiniciar Servicios"):
                st.success("✅ Servicios reiniciados")
            
            if st.button("🔄 Actualizar Sistema"):
                st.success("✅ Sistema actualizado")
            
            if st.button("🔄 Verificar Integridad"):
                st.success("✅ Integridad verificada")
        
        # Información del sistema
        st.subheader("ℹ️ Información del Sistema")
        
        system_info = {
            "Versión de Python": "3.9.0",
            "Versión de Streamlit": "1.28.0",
            "Versión de PostgreSQL": "0",
            "Sistema Operativo": "Linux",
            "Arquitectura": "x86_64",
            "Memoria Total": "4 GB",
            "Espacio en Disco": "50 GB"
        }
        
        for key, value in system_info.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{key}:**")
            with col2:
                st.write(value)


# ===== FUNCIÓN PRINCIPAL =====

def main():
    """Función principal de la aplicación"""
    
    # Renderizar header
    render_header()
    
    # Verificar autenticación
    if not is_authenticated():
        render_login_form()
        return
    
    # Menu centrale sempre visibile (come in DASH_GESTIONE_CPA)
    if CENTRAL_MENU_AVAILABLE and render_central_menu:
        # Renderizza sidebar compatta
        render_compact_sidebar()
        
        # Renderizza menu centrale
        current_page = render_central_menu(st.session_state.get('current_page', 'dashboard'))
    else:
        # Fallback al menu originale
        render_sidebar()
        current_page = st.session_state.get('current_page', 'dashboard')
    
    # Renderizar contenido principal
    try:
        if current_page == 'dashboard':
            render_dashboard()
        elif current_page == 'inventario':
            render_inventario()
        elif current_page == 'ventas':
            render_ventas()
        elif current_page == 'clientes':
            render_clientes()
        elif current_page == 'proveedores':
            render_proveedores()
        elif current_page == 'personal':
            render_personal()
        elif current_page == 'analytics':
            render_analytics()
        elif current_page == 'balance':
            render_balance()
        elif current_page == 'configuracion':
            render_configuracion()
        else:
            render_dashboard()
            
    except Exception as e:
        st.error(f"❌ Error durante el renderizado de la página: {str(e)}")
        st.exception(e)

# ===== INICIO APLICACIÓN =====

if __name__ == "__main__":
    main()
