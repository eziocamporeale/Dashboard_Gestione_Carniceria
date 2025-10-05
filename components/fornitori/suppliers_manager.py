#!/usr/bin/env python3
"""
Gestione Fornitori - Componente CRUD Completo
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

# Aggiungi il percorso del progetto al Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from database.database_manager import get_db_manager
except ImportError:
    # Fallback per test
    from database.hybrid_database_manager import get_hybrid_manager as get_db_manager

class SuppliersManager:
    """Gestore completo per le operazioni CRUD sui fornitori"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.table_name = 'suppliers'
    
    def create_supplier(self, supplier_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Crea un nuovo fornitore
        
        Args:
            supplier_data: Dizionario con i dati del fornitore
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, created_supplier)
        """
        try:
            # Validazione dati
            validation_result = self._validate_supplier_data(supplier_data)
            if not validation_result[0]:
                return False, validation_result[1], None
            
            # Preparazione dati per l'inserimento
            insert_data = {
                'name': supplier_data['name'].strip(),
                'contact_email': supplier_data.get('contact_email', '').strip(),
                'phone': supplier_data.get('phone', '').strip(),
                'address': supplier_data.get('address', '').strip(),
                'contact_person': supplier_data.get('contact_person', '').strip(),
                'notes': supplier_data.get('notes', '').strip(),
                'is_active': supplier_data.get('is_active', True),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Rimuovi campi vuoti per evitare errori
            insert_data = {k: v for k, v in insert_data.items() if v is not None and v != ''}
            
            # Inserimento nel database
            if self.db.use_supabase and self.db.supabase_manager:
                response = self.db.supabase_manager.client.table(self.table_name).insert(insert_data).execute()
                
                if response.data:
                    created_supplier = response.data[0]
                    return True, f"✅ Fornitore '{supplier_data['name']}' creato con successo!", created_supplier
                else:
                    return False, "❌ Errore durante la creazione del fornitore", None
            else:
                return False, "❌ Database non disponibile", None
                
        except Exception as e:
            error_msg = f"❌ Errore durante la creazione del fornitore: {str(e)}"
            return False, error_msg, None
    
    def get_suppliers(self, active_only: bool = False, search_term: str = "") -> Tuple[bool, str, List[Dict]]:
        """
        Recupera la lista dei fornitori
        
        Args:
            active_only: Se True, recupera solo fornitori attivi
            search_term: Termine di ricerca per filtrare i risultati
            
        Returns:
            Tuple[bool, str, List[Dict]]: (success, message, suppliers_list)
        """
        try:
            if self.db.use_supabase and self.db.supabase_manager:
                query = self.db.supabase_manager.client.table(self.table_name).select('*')
                
                # Filtro per fornitori attivi
                if active_only:
                    query = query.eq('is_active', True)
                
                # Ordinamento per nome
                query = query.order('name')
                
                response = query.execute()
                
                if response.data:
                    suppliers = response.data
                    
                    # Filtro per termine di ricerca
                    if search_term:
                        search_lower = search_term.lower()
                        suppliers = [
                            s for s in suppliers 
                            if search_lower in s.get('name', '').lower() or
                               search_lower in s.get('contact_person', '').lower() or
                               search_lower in s.get('contact_email', '').lower()
                        ]
                    
                    return True, f"✅ Trovati {len(suppliers)} fornitori", suppliers
                else:
                    return True, "ℹ️ Nessun fornitore trovato", []
            else:
                return False, "❌ Database non disponibile", []
                
        except Exception as e:
            error_msg = f"❌ Errore durante il recupero dei fornitori: {str(e)}"
            return False, error_msg, []
    
    def get_supplier_by_id(self, supplier_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Recupera un fornitore per ID
        
        Args:
            supplier_id: ID del fornitore
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, supplier_data)
        """
        try:
            if self.db.use_supabase and self.db.supabase_manager:
                response = self.db.supabase_manager.client.table(self.table_name).select('*').eq('id', supplier_id).execute()
                
                if response.data:
                    return True, "✅ Fornitore trovato", response.data[0]
                else:
                    return False, "❌ Fornitore non trovato", None
            else:
                return False, "❌ Database non disponibile", None
                
        except Exception as e:
            error_msg = f"❌ Errore durante il recupero del fornitore: {str(e)}"
            return False, error_msg, None
    
    def update_supplier(self, supplier_id: int, supplier_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Aggiorna un fornitore esistente
        
        Args:
            supplier_id: ID del fornitore da aggiornare
            supplier_data: Dati aggiornati del fornitore
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, updated_supplier)
        """
        try:
            # Validazione dati
            validation_result = self._validate_supplier_data(supplier_data)
            if not validation_result[0]:
                return False, validation_result[1], None
            
            # Preparazione dati per l'aggiornamento
            update_data = {
                'name': supplier_data['name'].strip(),
                'contact_email': supplier_data.get('contact_email', '').strip(),
                'phone': supplier_data.get('phone', '').strip(),
                'address': supplier_data.get('address', '').strip(),
                'contact_person': supplier_data.get('contact_person', '').strip(),
                'notes': supplier_data.get('notes', '').strip(),
                'is_active': supplier_data.get('is_active', True),
                'updated_at': datetime.now().isoformat()
            }
            
            # Rimuovi campi vuoti per evitare errori
            update_data = {k: v for k, v in update_data.items() if v is not None and v != ''}
            
            # Aggiornamento nel database
            if self.db.use_supabase and self.db.supabase_manager:
                response = self.db.supabase_manager.client.table(self.table_name).update(update_data).eq('id', supplier_id).execute()
                
                if response.data:
                    updated_supplier = response.data[0]
                    return True, f"✅ Fornitore '{supplier_data['name']}' aggiornato con successo!", updated_supplier
                else:
                    return False, "❌ Fornitore non trovato o errore durante l'aggiornamento", None
            else:
                return False, "❌ Database non disponibile", None
                
        except Exception as e:
            error_msg = f"❌ Errore durante l'aggiornamento del fornitore: {str(e)}"
            return False, error_msg, None
    
    def delete_supplier(self, supplier_id: int, soft_delete: bool = True) -> Tuple[bool, str]:
        """
        Elimina un fornitore
        
        Args:
            supplier_id: ID del fornitore da eliminare
            soft_delete: Se True, imposta is_active=False invece di eliminare fisicamente
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if self.db.use_supabase and self.db.supabase_manager:
                if soft_delete:
                    # Soft delete: imposta is_active=False
                    response = self.db.supabase_manager.client.table(self.table_name).update({
                        'is_active': False,
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', supplier_id).execute()
                    
                    if response.data:
                        return True, "✅ Fornitore disattivato con successo!"
                    else:
                        return False, "❌ Fornitore non trovato"
                else:
                    # Hard delete: elimina fisicamente il record
                    response = self.db.supabase_manager.client.table(self.table_name).delete().eq('id', supplier_id).execute()
                    
                    if response.data:
                        return True, "✅ Fornitore eliminato definitivamente!"
                    else:
                        return False, "❌ Fornitore non trovato"
            else:
                return False, "❌ Database non disponibile"
                
        except Exception as e:
            error_msg = f"❌ Errore durante l'eliminazione del fornitore: {str(e)}"
            return False, error_msg
    
    def _validate_supplier_data(self, supplier_data: Dict) -> Tuple[bool, str]:
        """
        Valida i dati del fornitore
        
        Args:
            supplier_data: Dati del fornitore da validare
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Nome obbligatorio
        if not supplier_data.get('name') or not supplier_data['name'].strip():
            return False, "❌ Il nome del fornitore è obbligatorio"
        
        # Email valida (se fornita)
        email = supplier_data.get('contact_email', '').strip()
        if email:
            if '@' not in email or '.' not in email:
                return False, "❌ Email non valida"
        
        # Telefono (se fornito) - validazione base
        phone = supplier_data.get('phone', '').strip()
        if phone:
            # Rimuovi spazi e caratteri speciali per la validazione
            clean_phone = ''.join(c for c in phone if c.isdigit() or c in '+()-')
            if len(clean_phone) < 7:
                return False, "❌ Numero di telefono troppo corto"
        
        return True, "✅ Dati validi"
    
    def get_suppliers_stats(self) -> Dict:
        """
        Recupera statistiche sui fornitori
        
        Returns:
            Dict: Statistiche sui fornitori
        """
        try:
            success, message, suppliers = self.get_suppliers()
            
            if success and suppliers:
                total_suppliers = len(suppliers)
                active_suppliers = len([s for s in suppliers if s.get('is_active', True)])
                inactive_suppliers = total_suppliers - active_suppliers
                
                return {
                    'total': total_suppliers,
                    'active': active_suppliers,
                    'inactive': inactive_suppliers,
                    'success': True
                }
            else:
                return {
                    'total': 0,
                    'active': 0,
                    'inactive': 0,
                    'success': False,
                    'error': message
                }
                
        except Exception as e:
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'success': False,
                'error': f"Errore durante il calcolo delle statistiche: {str(e)}"
            }
