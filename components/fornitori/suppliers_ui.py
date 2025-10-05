#!/usr/bin/env python3
"""
Interfaccia Utente per la Gestione Fornitori
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Aggiungi il percorso del progetto al Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.fornitori.suppliers_manager import SuppliersManager

class SuppliersUI:
    """Interfaccia utente per la gestione fornitori"""
    
    def __init__(self):
        self.manager = SuppliersManager()
    
    def render_suppliers_page(self):
        """Renderizza la pagina principale dei fornitori"""
        st.header("🚚 Gestione Fornitori")
        
        # Tabs per le diverse operazioni
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Fornitori", "➕ Nuovo Fornitore", "✏️ Modifica Fornitore", "📊 Statistiche"])
        
        with tab1:
            self._render_suppliers_list()
        
        with tab2:
            self._render_create_supplier()
        
        with tab3:
            self._render_edit_supplier()
        
        with tab4:
            self._render_suppliers_stats()
    
    def _render_suppliers_list(self):
        """Renderizza la lista dei fornitori"""
        st.subheader("📋 Lista Fornitori")
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_active_only = st.checkbox("Mostra solo fornitori attivi", value=True)
        
        with col2:
            search_term = st.text_input("🔍 Cerca fornitore", placeholder="Nome, contatto o email...")
        
        with col3:
            if st.button("🔄 Aggiorna Lista"):
                st.rerun()
        
        # Recupera fornitori
        success, message, suppliers = self.manager.get_suppliers(
            active_only=show_active_only,
            search_term=search_term
        )
        
        if not success:
            st.error(message)
            return
        
        if not suppliers:
            st.info("ℹ️ Nessun fornitore trovato")
            return
        
        # Mostra fornitori in una tabella
        st.success(f"✅ {message}")
        
        # Prepara dati per la tabella
        df_data = []
        for supplier in suppliers:
            df_data.append({
                'ID': supplier.get('id', 'N/A'),
                'Nome': supplier.get('name', 'N/A'),
                'Contatto': supplier.get('contact_person', 'N/A'),
                'Email': supplier.get('contact_email', 'N/A'),
                'Telefono': supplier.get('phone', 'N/A'),
                'Indirizzo': supplier.get('address', 'N/A'),
                'Stato': '🟢 Attivo' if supplier.get('is_active', True) else '🔴 Inattivo',
                'Creato': supplier.get('created_at', 'N/A')[:10] if supplier.get('created_at') else 'N/A'
            })
        
        df = pd.DataFrame(df_data)
        
        # Mostra tabella
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'ID': st.column_config.NumberColumn('ID', width='small'),
                'Nome': st.column_config.TextColumn('Nome', width='medium'),
                'Contatto': st.column_config.TextColumn('Contatto', width='medium'),
                'Email': st.column_config.TextColumn('Email', width='large'),
                'Telefono': st.column_config.TextColumn('Telefono', width='medium'),
                'Indirizzo': st.column_config.TextColumn('Indirizzo', width='large'),
                'Stato': st.column_config.TextColumn('Stato', width='small'),
                'Creato': st.column_config.TextColumn('Creato', width='small')
            }
        )
        
        # Azioni rapide
        st.subheader("🔧 Azioni Rapide")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Esporta Lista"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica CSV",
                    data=csv,
                    file_name=f"fornitori_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🔄 Aggiorna Database"):
                st.rerun()
        
        with col3:
            if st.button("📊 Visualizza Statistiche"):
                st.session_state.show_stats = True
                st.rerun()
    
    def _render_create_supplier(self):
        """Renderizza il form per creare un nuovo fornitore"""
        st.subheader("➕ Nuovo Fornitore")
        
        with st.form("create_supplier_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome del Fornitore *", placeholder="Es. Toledo Import")
                contact_email = st.text_input("Email di Contatto", placeholder="esempio@fornitore.com")
                phone = st.text_input("Telefono", placeholder="+34 600 123 456")
            
            with col2:
                address = st.text_area("Indirizzo", placeholder="Via, Città, CAP...")
                contact_person = st.text_input("Persona di Contatto", placeholder="Nome Cognome")
                notes = st.text_area("Note", placeholder="Informazioni aggiuntive...")
            
            # Stato attivo
            is_active = st.checkbox("Fornitore attivo", value=True)
            
            # Pulsante submit
            submitted = st.form_submit_button("💾 Salva Fornitore", type="primary")
            
            if submitted:
                # Validazione
                if not name or not name.strip():
                    st.error("❌ Il nome del fornitore è obbligatorio")
                    return
                
                # Prepara dati
                supplier_data = {
                    'name': name,
                    'contact_email': contact_email,
                    'phone': phone,
                    'address': address,
                    'contact_person': contact_person,
                    'notes': notes,
                    'is_active': is_active
                }
                
                # Crea fornitore
                with st.spinner("Creando fornitore..."):
                    success, message, created_supplier = self.manager.create_supplier(supplier_data)
                
                if success:
                    st.success(message)
                    
                    # Mostra riepilogo
                    st.subheader("📋 Riepilogo Fornitore Creato")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nome:** {created_supplier.get('name', 'N/A')}")
                        st.write(f"**Email:** {created_supplier.get('contact_email', 'N/A')}")
                        st.write(f"**Telefono:** {created_supplier.get('phone', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Contatto:** {created_supplier.get('contact_person', 'N/A')}")
                        st.write(f"**Indirizzo:** {created_supplier.get('address', 'N/A')}")
                        st.write(f"**Stato:** {'🟢 Attivo' if created_supplier.get('is_active', True) else '🔴 Inattivo'}")
                    
                    if created_supplier.get('notes'):
                        st.write(f"**Note:** {created_supplier.get('notes')}")
                    
                    # Pulisci form
                    st.session_state.create_supplier_form_cleared = True
                    st.rerun()
                else:
                    st.error(message)
    
    def _render_edit_supplier(self):
        """Renderizza il form per modificare un fornitore"""
        st.subheader("✏️ Modifica Fornitore")
        
        # Selezione fornitore
        success, message, suppliers = self.manager.get_suppliers()
        
        if not success:
            st.error(message)
            return
        
        if not suppliers:
            st.info("ℹ️ Nessun fornitore disponibile per la modifica")
            return
        
        # Dropdown per selezione fornitore
        supplier_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in suppliers}
        selected_supplier_name = st.selectbox(
            "Seleziona fornitore da modificare:",
            options=list(supplier_options.keys()),
            key="edit_supplier_select"
        )
        
        if selected_supplier_name:
            supplier_id = supplier_options[selected_supplier_name]
            
            # Recupera dati fornitore
            success, message, supplier = self.manager.get_supplier_by_id(supplier_id)
            
            if not success:
                st.error(message)
                return
            
            # Form di modifica
            with st.form("edit_supplier_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input(
                        "Nome del Fornitore *", 
                        value=supplier.get('name', ''),
                        key="edit_name"
                    )
                    contact_email = st.text_input(
                        "Email di Contatto", 
                        value=supplier.get('contact_email', ''),
                        key="edit_email"
                    )
                    phone = st.text_input(
                        "Telefono", 
                        value=supplier.get('phone', ''),
                        key="edit_phone"
                    )
                
                with col2:
                    address = st.text_area(
                        "Indirizzo", 
                        value=supplier.get('address', ''),
                        key="edit_address"
                    )
                    contact_person = st.text_input(
                        "Persona di Contatto", 
                        value=supplier.get('contact_person', ''),
                        key="edit_contact_person"
                    )
                    notes = st.text_area(
                        "Note", 
                        value=supplier.get('notes', ''),
                        key="edit_notes"
                    )
                
                # Stato attivo
                is_active = st.checkbox(
                    "Fornitore attivo", 
                    value=supplier.get('is_active', True),
                    key="edit_is_active"
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    submitted = st.form_submit_button("💾 Salva Modifiche", type="primary")
                
                with col2:
                    if st.form_submit_button("🗑️ Disattiva Fornitore", type="secondary"):
                        # Soft delete
                        with st.spinner("Disattivando fornitore..."):
                            success, message = self.manager.delete_supplier(supplier_id, soft_delete=True)
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                with col3:
                    if st.form_submit_button("❌ Elimina Definitivamente", type="secondary"):
                        # Hard delete con conferma
                        if st.session_state.get('confirm_delete', False):
                            with st.spinner("Eliminando fornitore..."):
                                success, message = self.manager.delete_supplier(supplier_id, soft_delete=False)
                            
                            if success:
                                st.success(message)
                                st.session_state.confirm_delete = False
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.session_state.confirm_delete = True
                            st.warning("⚠️ Clicca di nuovo per confermare l'eliminazione definitiva")
                
                if submitted:
                    # Validazione
                    if not name or not name.strip():
                        st.error("❌ Il nome del fornitore è obbligatorio")
                        return
                    
                    # Prepara dati
                    supplier_data = {
                        'name': name,
                        'contact_email': contact_email,
                        'phone': phone,
                        'address': address,
                        'contact_person': contact_person,
                        'notes': notes,
                        'is_active': is_active
                    }
                    
                    # Aggiorna fornitore
                    with st.spinner("Aggiornando fornitore..."):
                        success, message, updated_supplier = self.manager.update_supplier(supplier_id, supplier_data)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    def _render_suppliers_stats(self):
        """Renderizza le statistiche sui fornitori"""
        st.subheader("📊 Statistiche Fornitori")
        
        # Recupera statistiche
        stats = self.manager.get_suppliers_stats()
        
        if not stats.get('success', False):
            st.error(f"❌ Errore nel recupero delle statistiche: {stats.get('error', 'Errore sconosciuto')}")
            return
        
        # Mostra metriche
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Totale Fornitori",
                value=stats['total'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="🟢 Fornitori Attivi",
                value=stats['active'],
                delta=None
            )
        
        with col3:
            st.metric(
                label="🔴 Fornitori Inattivi",
                value=stats['inactive'],
                delta=None
            )
        
        with col4:
            if stats['total'] > 0:
                active_percentage = (stats['active'] / stats['total']) * 100
                st.metric(
                    label="📈 % Attivi",
                    value=f"{active_percentage:.1f}%",
                    delta=None
                )
            else:
                st.metric(
                    label="📈 % Attivi",
                    value="0%",
                    delta=None
                )
        
        # Grafico a torta
        if stats['total'] > 0:
            st.subheader("📊 Distribuzione Fornitori")
            
            import plotly.express as px
            
            fig_data = {
                'Tipo': ['Attivi', 'Inattivi'],
                'Quantità': [stats['active'], stats['inactive']],
                'Colore': ['#28a745', '#dc3545']
            }
            
            fig = px.pie(
                values=fig_data['Quantità'],
                names=fig_data['Tipo'],
                title="Distribuzione Fornitori",
                color_discrete_sequence=['#28a745', '#dc3545']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Nessun fornitore disponibile per le statistiche")

def render_suppliers_page():
    """Funzione principale per renderizzare la pagina fornitori"""
    ui = SuppliersUI()
    ui.render_suppliers_page()

