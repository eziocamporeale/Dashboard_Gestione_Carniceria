#!/usr/bin/env python3
"""
Componente Menu Centrale per Dashboard_Gestione_Macelleria
Menu di navigazione posizionato al centro della dashboard, sempre visibile
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.auth.auth_manager import get_user_info

def render_central_menu(current_page: str = "🏠 Dashboard") -> str:
    """
    Renderizza il menu centrale sempre visibile
    
    Args:
        current_page: Pagina corrente selezionata
        
    Returns:
        str: Pagina selezionata
    """
    
    # CSS per il menu centrale sempre visibile
    st.markdown("""
    <style>
    .menu-buttons {
        margin: 1rem 0;
    }
    .menu-buttons {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .menu-btn {
        background: white;
        color: #333;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .menu-btn:hover {
        background: #f5f5f5;
        border-color: #2E86AB;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .menu-btn.active {
        background: #2E86AB;
        color: white;
        border-color: #2E86AB;
        font-weight: bold;
    }
    .menu-btn.active:hover {
        background: white;
        color: #2E86AB;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container del menu
    st.markdown("""
    <div class="menu-buttons">
    """, unsafe_allow_html=True)
    
    # Ottieni le opzioni del menu basate sui permessi utente
    user_info = get_user_info()
    menu_options = [
        ("🏠 Dashboard", "dashboard"),
        ("📦 Inventario", "inventario"),
        ("🛒 Ventas", "ventas"),
        ("👥 Clientes", "clientes"),
        ("🚚 Proveedores", "proveedores"),
        ("👨‍💼 Personal", "personal"),
        ("📊 Analytics", "analytics"),
        ("💰 Balance", "balance"),
        ("⚙️ Configuración", "configuracion")
    ]
    
    # Sistema ora è integrato in Configuración
    # Rimossa tab Sistema separata
    
    # Crea i pulsanti del menu direttamente
    cols = st.columns(len(menu_options))
    selected_page = current_page
    
    for i, (display_name, page_value) in enumerate(menu_options):
        with cols[i]:
            is_active = page_value == current_page
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                display_name, 
                key=f"menu_btn_{page_value}",
                help=f"Vai alla sezione {display_name}",
                width='stretch',
                type=button_type
            ):
                # Imposta la nuova pagina direttamente
                selected_page = page_value
                st.session_state['current_page'] = page_value
                st.rerun()
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return selected_page

def render_compact_sidebar():
    """
    Renderizza una sidebar compatta solo con info utente e logout
    """
    with st.sidebar:
        st.markdown("### 👤 Usuario")
        
        # Informazioni utente
        user_info = get_user_info()
        if user_info:
            st.markdown(f"**👤 {user_info.get('username', 'N/A')}**")
            st.markdown(f"📧 {user_info.get('email', 'N/A')}")
            st.markdown(f"👑 {user_info.get('role_name', 'N/A')}")
            st.markdown(f"🏢 Admin Sistema")
        
        st.markdown("---")
        
        # Pulsante logout
        if st.button("🚪 Logout", width='stretch', type="primary"):
            # Pulisci session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
