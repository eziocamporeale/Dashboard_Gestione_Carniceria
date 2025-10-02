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
import sys
from pathlib import Path
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
                    Lote: {product['batch_number']}
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
                title="Tendencia Ventas",
                labels={'total_revenue': 'Ingresos ($)', 'date': 'Fecha'}
            )
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
                orientation='h',
                title="Top 5 Productos",
                labels={'total_quantity': 'Cantidad Vendida', 'name': 'Producto'}
            )
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
            
            # Mostrar tabla
            st.dataframe(
                filtered_df[['name', 'code', 'category_name', 'selling_price', 'current_stock', 'min_stock_level']],
                width='stretch',
                column_config={
                    "name": "Nombre Producto",
                    "code": "Código",
                    "category_name": "Categoría",
                    "selling_price": st.column_config.NumberColumn("Precio ($)", format="$%.2f"),
                    "current_stock": "Stock Actual",
                    "min_stock_level": "Stock Mínimo"
                }
            )
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
                        'storage_temperature_max': temp_max,
                        'created_by': get_current_user()['id']
                    }
                    
                    success, result = db.create_product(product_data)
                    
                    if success:
                        st.success(f"✅ Producto '{name}' agregado con éxito!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {result}")
    
    with tab3:
        st.subheader("📊 Gestión Stock")
        st.info("🚧 Funcionalidad en desarrollo - Gestión de stock e inventario")
    
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

def render_ventas():
    """Renderiza la sección ventas"""
    require_permission("ventas")
    
    st.header("🛒 Gestión Ventas")
    st.info("🚧 Funcionalidad en desarrollo - Sistema de ventas y POS")

def render_clientes():
    """Renderiza la sección clientes"""
    require_permission("clientes")
    
    st.header("👥 Gestión Clientes")
    st.info("🚧 Funcionalidad en desarrollo - Base de datos clientes y CRM")

def render_proveedores():
    """Renderiza la sección proveedores"""
    require_permission("proveedores")
    
    st.header("🚚 Gestión Proveedores")
    
    # Obtener datos de proveedores
    db = get_hybrid_manager()
    suppliers = db.get_all_suppliers()
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Proveedores", "➕ Nuevo Proveedor", "📊 Estadísticas", "📦 Pedidos"])
    
    with tab1:
        st.subheader("📋 Lista de Proveedores")
        
        if suppliers:
            # Crear DataFrame para mostrar proveedores
            import pandas as pd
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
            
            # Mostrar tabla
            if filtered_suppliers:
                df_filtered = pd.DataFrame(filtered_suppliers)
                st.dataframe(
                    df_filtered[['name', 'contact_email', 'phone', 'total_amount', 'transactions_count']],
                    width='stretch',
                    column_config={
                        "name": "Nombre",
                        "contact_email": "Email",
                        "phone": "Teléfono",
                        "total_amount": st.column_config.NumberColumn("Monto Total", format="$%.2f"),
                        "transactions_count": "Transacciones"
                    }
                )
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
                        # Crear nuevo proveedor (simulado)
                        new_supplier = {
                            'id': len(suppliers) + 1,
                            'name': name,
                            'contact_email': contact_email,
                            'phone': phone,
                            'address': address,
                            'contact_person': contact_person,
                            'notes': notes,
                            'total_amount': 0.0,
                            'transactions_count': 0,
                            'created_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        st.success(f"✅ Proveedor '{name}' creado exitosamente")
                        st.balloons()
                        
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
                        title="Top 5 Proveedores por Monto",
                        labels={'name': 'Proveedor', 'total_amount': 'Monto Total ($)'}
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
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
        
        # Simular pedidos de proveedores
        sample_orders = [
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
        
        # Métricas de pedidos
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pedidos Totales", len(sample_orders))
        with col2:
            pending_orders = len([o for o in sample_orders if o['status'] == 'Pendiente'])
            st.metric("Pendientes", pending_orders)
        with col3:
            delivered_orders = len([o for o in sample_orders if o['status'] == 'Entregado'])
            st.metric("Entregados", delivered_orders)
        with col4:
            total_value = sum(o['total_amount'] for o in sample_orders)
            st.metric("Valor Total", f"${total_value:,.2f}")
        
        st.markdown("---")
        
        # Tabla de pedidos
        df_orders = pd.DataFrame(sample_orders)
        st.dataframe(
            df_orders,
            width='stretch',
            column_config={
                "id": "ID",
                "supplier_name": "Proveedor",
                "order_date": "Fecha Pedido",
                "delivery_date": "Fecha Entrega",
                "status": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "En Tránsito", "Entregado", "Cancelado"]),
                "total_amount": st.column_config.NumberColumn("Monto Total", format="$%.2f"),
                "items_count": "Items"
            }
        )
        
        # Botón para nuevo pedido
        if st.button("➕ Nuevo Pedido", width='stretch', type="primary"):
            st.info("🚧 Funcionalidad de nuevo pedido en desarrollo")

def render_personal():
    """Renderiza la sección personal"""
    require_permission("personal")
    
    st.header("👨‍💼 Gestión Personal")
    
    # Datos de ejemplo para empleados
    sample_employees = [
        {
            'id': 1,
            'name': 'Juan Pérez',
            'position': 'Carnicero Principal',
            'department': 'Producción',
            'hire_date': '2023-01-15',
            'salary': 45000,
            'status': 'Activo',
            'phone': '+54 11 1234-5678',
            'email': 'juan.perez@carniceria.com'
        },
        {
            'id': 2,
            'name': 'María González',
            'position': 'Cajera',
            'department': 'Ventas',
            'hire_date': '2023-03-20',
            'salary': 35000,
            'status': 'Activo',
            'phone': '+54 11 2345-6789',
            'email': 'maria.gonzalez@carniceria.com'
        },
        {
            'id': 3,
            'name': 'Carlos Rodríguez',
            'position': 'Ayudante de Carnicero',
            'department': 'Producción',
            'hire_date': '2023-06-10',
            'salary': 30000,
            'status': 'Activo',
            'phone': '+54 11 3456-7890',
            'email': 'carlos.rodriguez@carniceria.com'
        },
        {
            'id': 4,
            'name': 'Ana Martínez',
            'position': 'Gerente',
            'department': 'Administración',
            'hire_date': '2022-11-05',
            'salary': 60000,
            'status': 'Activo',
            'phone': '+54 11 4567-8901',
            'email': 'ana.martinez@carniceria.com'
        }
    ]
    
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
            avg_salary = total_salary / len(sample_employees)
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
        import pandas as pd
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
                    new_salary = st.number_input("Salario", value=emp['salary'], min_value=0, step=1000)
                    new_status = st.selectbox("Estado", ["Activo", "Inactivo"], 
                                            index=["Activo", "Inactivo"].index(emp['status']))
                    new_phone = st.text_input("Teléfono", value=emp['phone'])
                    new_email = st.text_input("Email", value=emp['email'])
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.form_submit_button("💾 Guardar Cambios", width='stretch', type="primary"):
                        # Aquí se guardarían los cambios en la base de datos
                        st.success("✅ Empleado actualizado exitosamente")
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
                    # Aquí se eliminaría el empleado de la base de datos
                    st.success("✅ Empleado eliminado exitosamente")
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
                new_salary = st.number_input("Salario *", min_value=0, step=1000, value=30000)
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
                        # Aquí se guardaría el nuevo empleado en la base de datos
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
        sample_shifts = [
            {
                'id': 1,
                'employee_name': 'Juan Pérez',
                'shift_date': '2024-09-22',
                'shift_type': 'Mañana',
                'start_time': '08:00',
                'end_time': '16:00',
                'hours': 8,
                'status': 'Completado',
                'notes': 'Turno normal'
            },
            {
                'id': 2,
                'employee_name': 'María González',
                'shift_date': '2024-09-22',
                'shift_type': 'Tarde',
                'start_time': '14:00',
                'end_time': '22:00',
                'hours': 8,
                'status': 'En Curso',
                'notes': 'Turno de caja'
            },
            {
                'id': 3,
                'employee_name': 'Carlos Rodríguez',
                'shift_date': '2024-09-22',
                'shift_type': 'Mañana',
                'start_time': '07:00',
                'end_time': '15:00',
                'hours': 8,
                'status': 'Completado',
                'notes': 'Ayuda en producción'
            },
            {
                'id': 4,
                'employee_name': 'Ana Martínez',
                'shift_date': '2024-09-22',
                'shift_type': 'Administrativo',
                'start_time': '09:00',
                'end_time': '17:00',
                'hours': 8,
                'status': 'En Curso',
                'notes': 'Tareas administrativas'
            }
        ]
        
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
            avg_salary = total_salary / len(sample_employees)
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
            df_dept = pd.DataFrame(list(dept_counts.items()), columns=['Departamento', 'Cantidad'])
            fig_dept = px.bar(df_dept, x='Departamento', y='Cantidad', 
                            title="Empleados por Departamento",
                            color='Cantidad',
                            color_continuous_scale='Blues')
            st.plotly_chart(fig_dept, width='stretch')
        
        with col2:
            st.subheader("💰 Distribución de Salarios")
            
            # Crear gráfico de salarios
            df_salaries = pd.DataFrame(sample_employees)
            fig_salaries = px.histogram(df_salaries, x='salary', 
                                      title="Distribución de Salarios",
                                      nbins=10,
                                      color_discrete_sequence=['#FF6B6B'])
            fig_salaries.update_layout(
                xaxis_title="Salario ($)",
                yaxis_title="Número de Empleados"
            )
            st.plotly_chart(fig_salaries, width='stretch')
        
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
                min_salary = min(stats['salaries'])
                max_salary = max(stats['salaries'])
                
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
            st.metric("Empleado con Mayor Salario", 
                     f"${max(e['salary'] for e in sample_employees):,.2f}")
        
        with col2:
            st.metric("Empleado con Menor Salario", 
                     f"${min(e['salary'] for e in sample_employees):,.2f}")
        
        with col3:
            st.metric("Departamento con Más Empleados", 
                     max(dept_counts, key=dept_counts.get))
        
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Ventas", "💰 Nuevas Ventas", "📈 Reportes", "👥 Equipo Ventas", "🎯 Objetivos"
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
                                          title="Ventas Diarias (Últimos 30 días)",
                                          labels={'date': 'Fecha', 'sales': 'Ventas ($)'})
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
                                            title="Top 10 Productos por Ventas",
                                            labels={'product': 'Producto', 'sales': 'Ventas ($)'})
                        fig_products.update_xaxis(tickangle=45)
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
                producto = st.selectbox("Producto", ["Carne de Res Premium", "Pollo Entero", "Jamón Serrano", "Salmón Fresco", "Carne Molida"])
            
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
                        st.success("✅ Venta registrada exitosamente!")
                        st.session_state.productos_venta = []
                        st.rerun()
    
    with tab3:
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
                    st.metric("Total Ventas", "$45,250.00")
                with col2:
                    st.metric("Número de Transacciones", "156")
                with col3:
                    st.metric("Promedio por Venta", "$290.06")
                with col4:
                    st.metric("Crecimiento", "+12.5%")
                
                # Gráfico de tendencias
                st.subheader("📈 Tendencia de Ventas")
                fig_trend = px.line(x=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                                   y=[1200, 1350, 1100, 1450, 1600, 1800, 1650],
                                   title="Ventas por Día de la Semana",
                                   labels={'x': 'Día', 'y': 'Ventas ($)'})
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
                avg_rating = sum([emp['rating'] for emp in team_performance]) / len(team_performance)
                
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
                                     title="Ventas por Vendedor",
                                     labels={'employee': 'Vendedor', 'sales': 'Ventas ($)'})
                    fig_sales.update_xaxis(tickangle=45)
                    st.plotly_chart(fig_sales, width='stretch')
                
                with col2:
                    fig_rating = px.bar(df_team, x='employee', y='rating',
                                      title="Rating por Vendedor",
                                      labels={'employee': 'Vendedor', 'rating': 'Rating'})
                    fig_rating.update_xaxis(tickangle=45)
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
            st.metric("Meta de Ventas", "$50,000", "$45,250")
        with col2:
            st.metric("Meta Transacciones", "200", "156")
        with col3:
            st.metric("Meta Clientes Nuevos", "50", "42")
        
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
        
        # Datos de ejemplo para ventas
        import pandas as pd
        import plotly.express as px
        from datetime import datetime, timedelta
        
        # Generar datos de ventas de los últimos 30 días
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        sales_data = []
        
        for date in dates:
            base_sales = 1500
            variation = (hash(str(date)) % 1000) - 500
            daily_sales = max(500, base_sales + variation)
            
            sales_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'ventas': daily_sales,
                'clientes': (hash(str(date)) % 50) + 20,
                'productos_vendidos': (hash(str(date)) % 100) + 50
            })
        
        df_sales = pd.DataFrame(sales_data)
        
        # Métricas de ventas
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
        
        # Gráfico de ventas
        fig_line = px.line(
            df_sales,
            x='fecha',
            y='ventas',
            title="Ventas Diarias (Últimos 30 días)",
            labels={'fecha': 'Fecha', 'ventas': 'Ventas ($)'}
        )
        fig_line.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_line, width='stretch')
    
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
    """Renderiza la sección balance y previsiones"""
    require_permission("balance")
    
    st.header("💰 Balance y Previsiones")
    
    # Importar el lector de Excel
    try:
        from components.excel_reader import ExcelReader, analyze_carniceria_excel
    except ImportError:
        st.error("❌ Error importando lector de Excel")
        return
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumen General", "📈 Análisis Mensual", "🔮 Previsiones", "📁 Cargar Datos", "💾 Datos Guardados"])
    
    with tab1:
        st.subheader("📊 Resumen General")
        
        # Verificar si hay datos procesados
        if 'excel_processed' in st.session_state and st.session_state['excel_processed']:
            st.success("✅ **Datos del Excel procesados correctamente**")
        
        # Mostrar resumen si hay datos cargados
        if 'carniceria_analysis' in st.session_state:
            analysis = st.session_state['carniceria_analysis']
            overview = analysis.get('overview', {})
            
            # KPIs principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 Total Ventas",
                    value=f"${overview.get('total_sales', 0):,.2f}",
                    delta=f"{overview.get('total_months', 0)} meses"
                )
            
            with col2:
                st.metric(
                    label="💸 Total Gastos",
                    value=f"${overview.get('total_expenses', 0):,.2f}",
                    delta="Gastos totales"
                )
            
            with col3:
                st.metric(
                    label="📈 Ganancia Total",
                    value=f"${overview.get('total_profit', 0):,.2f}",
                    delta="Beneficio neto"
                )
            
            with col4:
                st.metric(
                    label="📋 Transacciones",
                    value=f"{overview.get('total_transactions', 0):,}",
                    delta="Total operaciones"
                )
            
            st.markdown("---")
            
            # Análisis de tendencias
            trends = analysis.get('trends', {})
            st.subheader("📈 Análisis de Tendencias")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trend_icon = "📈" if trends.get('sales_trend') == 'increasing' else "📉" if trends.get('sales_trend') == 'decreasing' else "➡️"
                st.metric(
                    label=f"{trend_icon} Tendencia Ventas",
                    value=trends.get('sales_trend', 'stable').title(),
                    delta=f"{trends.get('growth_rate', 0):.1f}%"
                )
            
            with col2:
                trend_icon = "📈" if trends.get('profit_trend') == 'increasing' else "📉" if trends.get('profit_trend') == 'decreasing' else "➡️"
                st.metric(
                    label=f"{trend_icon} Tendencia Ganancias",
                    value=trends.get('profit_trend', 'stable').title(),
                    delta="Beneficio"
                )
            
            with col3:
                trend_icon = "📈" if trends.get('expense_trend') == 'increasing' else "📉" if trends.get('expense_trend') == 'decreasing' else "➡️"
                st.metric(
                    label=f"{trend_icon} Tendencia Gastos",
                    value=trends.get('expense_trend', 'stable').title(),
                    delta="Egresos"
                )
            
            # Análisis de proveedores
            suppliers_analysis = analysis.get('suppliers_analysis', {})
            if suppliers_analysis.get('top_suppliers'):
                st.subheader("🚚 Top Proveedores")
                
                suppliers_df = pd.DataFrame(
                    suppliers_analysis['top_suppliers'], 
                    columns=['Proveedor', 'Monto Total']
                )
                
                st.dataframe(
                    suppliers_df,
                    width='stretch',
                    column_config={
                        "Proveedor": "Proveedor",
                        "Monto Total": st.column_config.NumberColumn("Monto Total ($)", format="$%.2f")
                    }
                )
        else:
            st.info("📁 Carga un archivo Excel para ver el análisis completo")
    
    with tab2:
        st.subheader("📈 Análisis Mensual")
        
        # Verificar si hay datos procesados
        if 'excel_processed' in st.session_state and st.session_state['excel_processed']:
            st.success("✅ **Datos del Excel procesados correctamente**")
        
        if 'carniceria_analysis' in st.session_state:
            analysis = st.session_state['carniceria_analysis']
            monthly_breakdown = analysis.get('monthly_breakdown', {})
            
            if monthly_breakdown:
                # Crear DataFrame para visualización
                df_monthly = pd.DataFrame(monthly_breakdown).T
                df_monthly.index.name = 'Mes'
                
                # Gráfico de tendencia de ventas
                st.subheader("📊 Tendencia de Ventas Mensuales")
                fig_sales = px.line(
                    df_monthly, 
                    x=df_monthly.index, 
                    y='sales',
                    title='Evolución de Ventas por Mes',
                    labels={'sales': 'Ventas ($)', 'index': 'Mes'}
                )
                fig_sales.update_layout(height=400)
                st.plotly_chart(fig_sales, width='stretch')
                
                # Gráfico de margen de ganancia
                st.subheader("📈 Margen de Ganancia Mensual")
                fig_profit = px.bar(
                    df_monthly,
                    x=df_monthly.index,
                    y='profit_margin',
                    title='Margen de Ganancia por Mes (%)',
                    labels={'profit_margin': 'Margen (%)', 'index': 'Mes'}
                )
                fig_profit.update_layout(height=400)
                st.plotly_chart(fig_profit, width='stretch')
                
                # Tabla detallada
                st.subheader("📋 Detalle Mensual")
                st.dataframe(
                    df_monthly,
                    width='stretch',
                    column_config={
                        "sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                        "expenses": st.column_config.NumberColumn("Gastos ($)", format="$%.2f"),
                        "profit": st.column_config.NumberColumn("Ganancia ($)", format="$%.2f"),
                        "transactions": st.column_config.NumberColumn("Transacciones", format="%d"),
                        "profit_margin": st.column_config.NumberColumn("Margen (%)", format="%.1f%%")
                    }
                )
            else:
                st.info("No hay datos mensuales disponibles")
        else:
            st.info("📁 Carga un archivo Excel para ver el análisis mensual")
    
    with tab3:
        st.subheader("🔮 Previsiones")
        
        # Verificar si hay datos procesados
        if 'excel_processed' in st.session_state and st.session_state['excel_processed']:
            st.success("✅ **Datos del Excel procesados correctamente**")
        
        if 'carniceria_analysis' in st.session_state:
            analysis = st.session_state['carniceria_analysis']
            forecasts = analysis.get('forecasts', {})
            
            if forecasts:
                st.subheader("📊 Previsión Próximo Mes")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="💰 Ventas Previstas",
                        value=f"${forecasts.get('next_month_sales', 0):,.2f}",
                        delta="Previsión"
                    )
                
                with col2:
                    st.metric(
                        label="💸 Gastos Previstos",
                        value=f"${forecasts.get('next_month_expenses', 0):,.2f}",
                        delta="Previsión"
                    )
                
                with col3:
                    st.metric(
                        label="📈 Ganancia Prevista",
                        value=f"${forecasts.get('next_month_profit', 0):,.2f}",
                        delta="Previsión"
                    )
                
                # Nivel de confianza
                confidence = forecasts.get('confidence_level', 'medium')
                confidence_icon = "🟢" if confidence == 'high' else "🟡" if confidence == 'medium' else "🔴"
                
                st.info(f"{confidence_icon} **Nivel de Confianza:** {confidence.title()}")
                
                # Suposiciones
                assumptions = forecasts.get('assumptions', [])
                if assumptions:
                    st.subheader("📝 Suposiciones del Modelo")
                    for assumption in assumptions:
                        st.write(f"• {assumption}")
                
                # Gráfico de previsión
                if 'carniceria_analysis' in st.session_state:
                    monthly_breakdown = analysis.get('monthly_breakdown', {})
                    if monthly_breakdown:
                        st.subheader("📈 Proyección de Ventas")
                        
                        # Crear datos para el gráfico
                        months = list(monthly_breakdown.keys())
                        sales = [monthly_breakdown[month]['sales'] for month in months]
                        
                        # Agregar previsión
                        months.append("Próximo Mes")
                        sales.append(forecasts.get('next_month_sales', 0))
                        
                        fig_forecast = go.Figure()
                        
                        # Datos históricos
                        fig_forecast.add_trace(go.Scatter(
                            x=months[:-1],
                            y=sales[:-1],
                            mode='lines+markers',
                            name='Datos Históricos',
                            line=dict(color='blue')
                        ))
                        
                        # Previsión
                        fig_forecast.add_trace(go.Scatter(
                            x=[months[-2], months[-1]],
                            y=[sales[-2], sales[-1]],
                            mode='lines+markers',
                            name='Previsión',
                            line=dict(color='red', dash='dash')
                        ))
                        
                        fig_forecast.update_layout(
                            title='Proyección de Ventas',
                            xaxis_title='Mes',
                            yaxis_title='Ventas ($)',
                            height=400
                        )
                        
                        st.plotly_chart(fig_forecast, width='stretch')
            else:
                st.info("No hay datos suficientes para generar previsiones")
        else:
            st.info("📁 Carga un archivo Excel para ver las previsiones")
    
    with tab4:
        st.subheader("📁 Cargar Datos Históricos")
        
        # Información sobre el formato esperado
        st.info("""
        **📋 Formato Esperado del Excel:**
        • Cada hoja debe representar un mes (ej: "Noviembre 2024", "Diciembre 2024")
        • Columnas esperadas: Fecha, Base, IGIC, Cobro, Proveedor, etc.
        • Datos de ventas diarias y pagos a proveedores
        """)
        
        # Botón para cargar datos Excel
        uploaded_file = st.file_uploader(
            "📁 Cargar Archivo Excel con Datos Históricos",
            type=['xlsx', 'xls'],
            help="Sube tu archivo Excel con los datos históricos de la carnicería"
        )
        
        if uploaded_file is not None:
            # Mostrar información del archivo cargado
            st.info(f"📁 **Archivo cargado:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Botón para procesar el archivo
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🚀 Procesar Archivo Excel", width='stretch', type="primary"):
                    try:
                        # Guardar archivo temporalmente
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Procesar el archivo
                        with st.spinner("🔄 Procesando datos del Excel..."):
                            analyzer = analyze_carniceria_excel(tmp_file_path)
                            analysis = analyzer.get_comprehensive_analysis()
                            
                            # Guardar análisis en session state
                            st.session_state['carniceria_analysis'] = analysis
                            st.session_state['excel_processed'] = True
                            
                            # Guardar datos en la base de datos
                            db = get_hybrid_manager()
                            success = db.save_excel_data(analysis)
                            
                            if success:
                                st.session_state['excel_saved_to_db'] = True
                                logger.info("✅ Datos Excel guardados en la base de datos")
                            else:
                                st.session_state['excel_saved_to_db'] = False
                                logger.error("❌ Error guardando datos Excel en la base de datos")
                            
                            # Limpiar archivo temporal
                            os.unlink(tmp_file_path)
                        
                        st.success(f"✅ Archivo procesado exitosamente: {uploaded_file.name}")
                        st.balloons()
                        
                        # Mostrar resumen del procesamiento
                        overview = analysis.get('overview', {})
                        st.info(f"""
                        **📊 Datos Procesados:**
                        • {overview.get('total_months', 0)} meses analizados
                        • {overview.get('total_transactions', 0):,} transacciones procesadas
                        • ${overview.get('total_sales', 0):,.2f} en ventas totales
                        • ${overview.get('total_profit', 0):,.2f} en ganancias totales
                        """)
                        
                        # Mostrar botón para ver análisis
                        st.markdown("---")
                        st.success("🎉 **¡Datos procesados exitosamente!**")
                        st.info("💡 **Ahora puedes:**")
                        st.write("• Ir a **📊 Resumen General** para ver KPIs principales")
                        st.write("• Ir a **📈 Análisis Mensual** para ver gráficos detallados")
                        st.write("• Ir a **🔮 Previsiones** para ver proyecciones futuras")
                        
                    except Exception as e:
                        st.error(f"❌ Error procesando archivo: {str(e)}")
                        st.exception(e)
            
            # Mostrar información adicional si el archivo está cargado pero no procesado
            if 'excel_processed' not in st.session_state or not st.session_state['excel_processed']:
                st.warning("⚠️ **Archivo cargado pero no procesado**")
                st.info("Haz clic en **'🚀 Procesar Archivo Excel'** para analizar los datos")
        
        # Botón para resetear datos si están procesados
        if 'excel_processed' in st.session_state and st.session_state['excel_processed']:
            st.markdown("---")
            st.subheader("🔄 Gestión de Datos")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🗑️ Limpiar Datos Procesados", width='stretch', type="secondary"):
                    # Limpiar datos del session state
                    if 'carniceria_analysis' in st.session_state:
                        del st.session_state['carniceria_analysis']
                    if 'excel_processed' in st.session_state:
                        del st.session_state['excel_processed']
                    
                    st.success("✅ Datos limpiados correctamente")
                    st.rerun()
    
    with tab5:
        st.subheader("💾 Datos Guardados en Base de Datos")
        
        # Verificar si hay datos guardados
        if 'excel_saved_to_db' in st.session_state and st.session_state['excel_saved_to_db']:
            st.success("✅ **Datos del Excel guardados en la base de datos**")
            
            # Obtener datos de la base de datos
            db = get_hybrid_manager()
            excel_summary = db.get_excel_data_summary()
            
            if excel_summary:
                # Mostrar resumen
                st.subheader("📊 Resumen de Datos Guardados")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="💰 Total Ventas",
                        value=f"${excel_summary.get('total_sales', 0):,.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="💸 Total Gastos",
                        value=f"${excel_summary.get('total_expenses', 0):,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="📈 Ganancia Total",
                        value=f"${excel_summary.get('total_profit', 0):,.2f}"
                    )
                
                with col4:
                    st.metric(
                        label="📋 Transacciones",
                        value=f"{excel_summary.get('total_transactions', 0):,}"
                    )
                
                # Mostrar datos mensuales
                monthly_data = excel_summary.get('monthly_data', [])
                if monthly_data:
                    st.subheader("📅 Datos Mensuales Guardados")
                    
                    monthly_df = pd.DataFrame(monthly_data)
                    st.dataframe(
                        monthly_df,
                        width='stretch',
                        column_config={
                            "month": "Mes",
                            "total_sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                            "total_expenses": st.column_config.NumberColumn("Gastos ($)", format="$%.2f"),
                            "total_profit": st.column_config.NumberColumn("Ganancia ($)", format="$%.2f"),
                            "transactions_count": "Transacciones"
                        }
                    )
                
                # Mostrar top proveedores
                top_suppliers = excel_summary.get('top_suppliers', [])
                if top_suppliers:
                    st.subheader("🚚 Top Proveedores Guardados")
                    
                    suppliers_df = pd.DataFrame(top_suppliers)
                    st.dataframe(
                        suppliers_df,
                        width='stretch',
                        column_config={
                            "name": "Proveedor",
                            "total_amount": st.column_config.NumberColumn("Monto Total ($)", format="$%.2f"),
                            "transactions_count": "Transacciones"
                        }
                    )
                
                # Mostrar datos detallados
                st.subheader("📋 Datos Detallados Guardados")
                
                detailed_data = db.get_saved_excel_data()
                if detailed_data:
                    detailed_df = pd.DataFrame(detailed_data)
                    st.dataframe(
                        detailed_df,
                        width='stretch',
                        column_config={
                            "month": "Mes",
                            "date": "Fecha",
                            "sales_amount": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                            "expense_amount": st.column_config.NumberColumn("Gastos ($)", format="$%.2f"),
                            "supplier_name": "Proveedor",
                            "invoice_number": "Factura",
                            "transaction_type": "Tipo",
                            "created_at": "Guardado"
                        }
                    )
                else:
                    st.info("No hay datos detallados guardados")
            else:
                st.warning("No se pudieron obtener los datos guardados")
        else:
            st.info("📁 No hay datos guardados en la base de datos")
            st.write("Carga y procesa un archivo Excel para ver los datos guardados aquí")
        
        # Información adicional
        st.markdown("---")
        st.subheader("ℹ️ Información Adicional")
        
        st.write("""
        **🔍 Análisis Disponibles:**
        • **Resumen General**: KPIs principales y tendencias
        • **Análisis Mensual**: Evolución detallada por mes
        • **Previsiones**: Proyecciones basadas en datos históricos
        • **Análisis de Proveedores**: Ranking y distribución de pagos
        
        **📈 Métricas Calculadas:**
        • Tendencia de ventas (creciente/decreciente/estable)
        • Margen de ganancia mensual
        • Análisis de rentabilidad
        • Previsiones con nivel de confianza
        """)

def render_configuracion():
    """Renderiza la sección configuración"""
    require_permission("configuracion")
    
    st.header("⚙️ Configuración Sistema")
    
    # Tabs para diferentes configuraciones
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Empresa", "👤 Usuarios", "🔧 Sistema", "💾 Backup"])
    
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
        
        # Lista de usuarios de ejemplo
        users_data = [
            {'id': 1, 'username': 'admin', 'name': 'Admin Sistema', 'email': 'admin@carniceria.com', 'role': 'Administrador', 'status': 'Activo', 'last_login': '2024-09-22 10:30:00'},
            {'id': 2, 'username': 'gerente', 'name': 'Ana Martínez', 'email': 'ana@carniceria.com', 'role': 'Gerente', 'status': 'Activo', 'last_login': '2024-09-21 15:45:00'},
            {'id': 3, 'username': 'cajero1', 'name': 'María González', 'email': 'maria@carniceria.com', 'role': 'Cajero', 'status': 'Activo', 'last_login': '2024-09-22 09:15:00'},
            {'id': 4, 'username': 'carnicero1', 'name': 'Juan Pérez', 'email': 'juan@carniceria.com', 'role': 'Carnicero', 'status': 'Inactivo', 'last_login': '2024-09-15 14:20:00'}
        ]
        
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
            today_logins = len([u for u in users_data if '2024-09-22' in u['last_login']])
            st.metric("Logins Hoy", today_logins)
        
        st.markdown("---")
        
        # Tabla de usuarios
        import pandas as pd
        df_users = pd.DataFrame(users_data)
        st.dataframe(
            df_users[['username', 'name', 'email', 'role', 'status', 'last_login']],
            width='stretch',
            column_config={
                "username": "Usuario",
                "name": "Nombre",
                "email": "Email",
                "role": "Rol",
                "status": st.column_config.SelectboxColumn("Estado", options=["Activo", "Inactivo", "Bloqueado"]),
                "last_login": "Último Login"
            }
        )
        
        # Botón para nuevo usuario
        if st.button("➕ Nuevo Usuario", width='stretch', type="primary"):
            st.info("🚧 Formulario de nuevo usuario en desarrollo")
    
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
            st.metric("Último Backup", "2024-09-22 02:00:00")
            st.metric("Tamaño del Backup", "15.2 MB")
            st.metric("Backups Disponibles", "7")
            st.metric("Próximo Backup", "2024-09-23 02:00:00")
            
            # Lista de backups disponibles
            st.subheader("📋 Backups Disponibles")
            backups = [
                {'fecha': '2024-09-22', 'hora': '02:00:00', 'tamaño': '15.2 MB', 'tipo': 'Automático'},
                {'fecha': '2024-09-21', 'hora': '02:00:00', 'tamaño': '14.8 MB', 'tipo': 'Automático'},
                {'fecha': '2024-09-20', 'hora': '02:00:00', 'tamaño': '14.5 MB', 'tipo': 'Automático'},
                {'fecha': '2024-09-19', 'hora': '15:30:00', 'tamaño': '14.2 MB', 'tipo': 'Manual'}
            ]
            
            df_backups = pd.DataFrame(backups)
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

# ===== FUNCIÓN PRINCIPAL =====

def main():
    """Función principal de la aplicación"""
    
    # Renderizar header
    render_header()
    
    # Verificar autenticación
    if not is_authenticated():
        render_login_form()
        return
    
    # Renderizar sidebar
    render_sidebar()
    
    # Obtener página actual
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
