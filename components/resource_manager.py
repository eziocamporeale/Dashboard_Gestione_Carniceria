#!/usr/bin/env python3
"""
Resource Manager per Dashboard Gestión Carnicería
Gestisce automaticamente la pulizia delle risorse per evitare "Too many open files"
Creado por Ezio Camporeale
"""

import streamlit as st
import gc
import psutil
import atexit
from typing import Dict, Any
import logging

# Configurazione logging
logger = logging.getLogger(__name__)

class ResourceManager:
    """Gestore risorse per evitare memory leaks e troppi file aperti"""
    
    def __init__(self):
        """Inizializza il gestore risorse"""
        self._cleanup_registered = False
        self._session_id = id(st.session_state)
        self._register_cleanup()
    
    def _register_cleanup(self):
        """Registra il cleanup automatico"""
        if not self._cleanup_registered:
            atexit.register(self.cleanup_all)
            self._cleanup_registered = True
    
    def cleanup_all(self):
        """Pulizia completa delle risorse"""
        try:
            # Cleanup database
            if 'db' in st.session_state:
                db = st.session_state.db
                if hasattr(db, 'cleanup'):
                    db.cleanup()
                    logger.info("✅ Database cleanup completato")
            
            # Garbage collection
            collected = gc.collect()
            if collected > 0:
                logger.info(f"✅ Garbage collection: {collected} oggetti rimossi")
            
            # Log info sistema
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                open_files = process.num_fds()
                logger.info(f"📊 Risorsse dopo cleanup - Memoria: {memory_mb:.2f} MB, File aperti: {open_files}")
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"❌ Errore durante cleanup: {e}")
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Ottiene informazioni sulle risorse"""
        try:
            process = psutil.Process()
            
            info = {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'open_files': process.num_fds(),
                'threads': process.num_threads(),
                'cpu_percent': process.cpu_percent(),
                'session_id': self._session_id
            }
            
            # Info database se disponibile
            if 'db' in st.session_state:
                db = st.session_state.db
                if hasattr(db, 'get_connection_info'):
                    info['database'] = db.get_connection_info()
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Errore ottenendo info risorse: {e}")
            return {}
    
    def check_limits(self) -> Dict[str, bool]:
        """Verifica se siamo vicini ai limiti"""
        try:
            info = self.get_resource_info()
            
            limits = {
                'memory_ok': info.get('memory_mb', 0) < 500,  # Meno di 500MB
                'files_ok': info.get('open_files', 0) < 100,  # Meno di 100 file aperti
                'cpu_ok': info.get('cpu_percent', 0) < 80    # Meno di 80% CPU
            }
            
            return limits
            
        except Exception as e:
            logger.error(f"❌ Errore verificando limiti: {e}")
            return {'memory_ok': True, 'files_ok': True, 'cpu_ok': True}
    
    def auto_cleanup_if_needed(self):
        """Esegue cleanup automatico se necessario"""
        try:
            limits = self.check_limits()
            
            if not limits['memory_ok'] or not limits['files_ok']:
                logger.warning("⚠️  Limiti risorse superati, eseguo cleanup automatico")
                self.cleanup_all()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ Errore durante auto cleanup: {e}")
            return False

def init_resource_manager():
    """Inizializza il gestore risorse nella sessione"""
    if 'resource_manager' not in st.session_state:
        st.session_state.resource_manager = ResourceManager()
    
    return st.session_state.resource_manager

def cleanup_on_page_change():
    """Esegue cleanup quando cambia pagina"""
    try:
        if 'resource_manager' in st.session_state:
            st.session_state.resource_manager.auto_cleanup_if_needed()
    except Exception as e:
        logger.error(f"❌ Errore durante cleanup cambio pagina: {e}")

def show_resource_status():
    """Mostra lo stato delle risorse nella sidebar"""
    try:
        if 'resource_manager' in st.session_state:
            resource_manager = st.session_state.resource_manager
            
            with st.sidebar.expander("📊 Stato Risorse", expanded=False):
                info = resource_manager.get_resource_info()
                limits = resource_manager.check_limits()
                
                # Memoria
                memory_mb = info.get('memory_mb', 0)
                memory_color = "🟢" if limits['memory_ok'] else "🔴"
                st.metric("💾 Memoria", f"{memory_mb:.1f} MB", delta=None)
                
                # File aperti
                open_files = info.get('open_files', 0)
                files_color = "🟢" if limits['files_ok'] else "🔴"
                st.metric("📁 File Aperti", open_files, delta=None)
                
                # CPU
                cpu_percent = info.get('cpu_percent', 0)
                cpu_color = "🟢" if limits['cpu_ok'] else "🔴"
                st.metric("⚡ CPU", f"{cpu_percent:.1f}%", delta=None)
                
                # Stato generale
                all_ok = all(limits.values())
                status_color = "🟢" if all_ok else "🔴"
                status_text = "OK" if all_ok else "ATTENZIONE"
                st.write(f"{status_color} **Stato:** {status_text}")
                
                # Pulsante cleanup manuale
                if st.button("🧹 Cleanup Manuale", use_container_width=True):
                    resource_manager.cleanup_all()
                    st.success("✅ Cleanup completato!")
                    st.rerun()
                    
    except Exception as e:
        logger.error(f"❌ Errore mostrando stato risorse: {e}")

# Decoratore per cleanup automatico
def with_resource_cleanup(func):
    """Decoratore che esegue cleanup dopo ogni funzione"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Cleanup automatico se necessario
            if 'resource_manager' in st.session_state:
                st.session_state.resource_manager.auto_cleanup_if_needed()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Errore in funzione {func.__name__}: {e}")
            raise
    
    return wrapper
