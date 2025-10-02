#!/usr/bin/env python3
"""
Sistema di Autenticazione per Dashboard Gestione Macelleria
Gestisce login, logout, sessioni e permessi utente
Creato da Ezio Camporeale
"""

import streamlit as st
import bcrypt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from database.hybrid_database_manager import get_hybrid_manager

# Configura logging
logger = logging.getLogger(__name__)

class AuthManager:
    """Manager per l'autenticazione e autorizzazione"""
    
    def __init__(self):
        self.db = get_hybrid_manager()
        self.session_key = "macelleria_auth_session"
        self.user_key = "macelleria_user"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Autentica un utente
        
        Args:
            username: Nome utente
            password: Password
            
        Returns:
            Tuple[success, message, user_data]
        """
        try:
            # Autentica l'utente
            user = self.db.authenticate_user(username, password)
            
            if user:
                # Salva la sessione
                self._save_session(user)
                
                # Log dell'attività
                self.db.log_activity(
                    user_id=user['id'],
                    action='login',
                    details=f'Login effettuato da {username}',
                    ip_address=self._get_client_ip()
                )
                
                logger.info(f"✅ Login effettuato: {username}")
                return True, "Login effettuato con successo", user
            else:
                logger.warning(f"❌ Tentativo login fallito: {username}")
                return False, "Credenziali non valide", None
                
        except Exception as e:
            logger.error(f"❌ Errore durante login: {e}")
            return False, f"Errore durante l'autenticazione: {str(e)}", None
    
    def logout(self) -> bool:
        """
        Disconnette l'utente corrente
        
        Returns:
            bool: True se logout riuscito
        """
        try:
            user = self.get_current_user()
            if user:
                # Log dell'attività
                self.db.log_activity(
                    user_id=user['id'],
                    action='logout',
                    details=f'Logout effettuato da {user["username"]}',
                    ip_address=self._get_client_ip()
                )
            
            # Rimuovi la sessione
            self._clear_session()
            
            logger.info("✅ Logout effettuato")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore durante logout: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Ottiene l'utente corrente dalla sessione
        
        Returns:
            Dict con i dati dell'utente o None se non autenticato
        """
        try:
            if self.user_key in st.session_state:
                user_data = st.session_state[self.user_key]
                
                # Verifica se la sessione è ancora valida
                if self._is_session_valid():
                    return user_data
                else:
                    # Sessione scaduta
                    self._clear_session()
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento utente corrente: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Verifica se l'utente è autenticato
        
        Returns:
            bool: True se autenticato
        """
        user = self.get_current_user()
        return user is not None
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica se l'utente corrente ha un permesso specifico
        
        Args:
            permission: Nome del permesso da verificare
            
        Returns:
            bool: True se ha il permesso
        """
        try:
            user = self.get_current_user()
            if not user:
                return False
            
            # Admin ha tutti i permessi
            if user.get('is_admin', False):
                return True
            
            # Verifica permessi specifici
            user_permissions = user.get('permissions', [])
            return permission in user_permissions or 'all' in user_permissions
            
        except Exception as e:
            logger.error(f"❌ Errore verifica permesso {permission}: {e}")
            return False
    
    def has_role(self, role_name: str) -> bool:
        """
        Verifica se l'utente corrente ha un ruolo specifico
        
        Args:
            role_name: Nome del ruolo da verificare
            
        Returns:
            bool: True se ha il ruolo
        """
        try:
            user = self.get_current_user()
            if not user:
                return False
            
            return user.get('role_name') == role_name
            
        except Exception as e:
            logger.error(f"❌ Errore verifica ruolo {role_name}: {e}")
            return False
    
    def require_auth(self, redirect_to_login: bool = True):
        """
        Decorator per richiedere autenticazione
        
        Args:
            redirect_to_login: Se True, reindirizza al login se non autenticato
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
                st.stop()
            return False
        return True
    
    def require_permission(self, permission: str, redirect_to_login: bool = True):
        """
        Decorator per richiedere un permesso specifico
        
        Args:
            permission: Permesso richiesto
            redirect_to_login: Se True, reindirizza al login se non autenticato
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
                st.stop()
            return False
        
        if not self.has_permission(permission):
            st.error(f"🚫 Permesso negato. Non hai i privilegi per accedere a questa sezione.")
            st.stop()
        
        return True
    
    def require_role(self, role_name: str, redirect_to_login: bool = True):
        """
        Decorator per richiedere un ruolo specifico
        
        Args:
            role_name: Ruolo richiesto
            redirect_to_login: Se True, reindirizza al login se non autenticato
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
                st.stop()
            return False
        
        if not self.has_role(role_name):
            st.error(f"🚫 Ruolo richiesto: {role_name}. Non hai i privilegi per accedere a questa sezione.")
            st.stop()
        
        return True
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Ottiene informazioni complete dell'utente corrente
        
        Returns:
            Dict con informazioni utente
        """
        user = self.get_current_user()
        if not user:
            return {}
        
        # Gestisci sia username che email per compatibilità
        username = user.get('username', user.get('email', 'unknown'))
        
        return {
            'id': user['id'],
            'username': username,
            'email': user.get('email', ''),
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'full_name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
            'role_name': user.get('role_name', ''),
            'is_admin': user.get('is_admin', False),
            'permissions': user.get('permissions', []),
            'login_time': self._get_session_login_time()
        }
    
    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambia la password dell'utente corrente
        
        Args:
            current_password: Password attuale
            new_password: Nuova password
            
        Returns:
            Tuple[success, message]
        """
        try:
            user = self.get_current_user()
            if not user:
                return False, "Utente non autenticato"
            
            # Verifica password attuale
            if not self.db.authenticate_user(user['username'], current_password):
                return False, "Password attuale non corretta"
            
            # Hash della nuova password
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Aggiorna password nel database
            query = "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.db.execute_query(query, (new_password_hash, user['id']), "none")
            
            # Log dell'attività
            self.db.log_activity(
                user_id=user['id'],
                action='password_change',
                details='Password modificata',
                ip_address=self._get_client_ip()
            )
            
            logger.info(f"✅ Password modificata per utente: {user['username']}")
            return True, "Password modificata con successo"
            
        except Exception as e:
            logger.error(f"❌ Errore cambio password: {e}")
            return False, f"Errore durante il cambio password: {str(e)}"
    
    def _save_session(self, user_data: Dict[str, Any]):
        """Salva i dati della sessione"""
        try:
            # Gestisci sia username che email per compatibilità
            username = user_data.get('username', user_data.get('email', 'unknown'))
            
            session_data = {
                'user_id': user_data['id'],
                'username': username,
                'login_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=8)).isoformat()
            }
            
            st.session_state[self.session_key] = session_data
            st.session_state[self.user_key] = user_data
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio sessione: {e}")
    
    def _clear_session(self):
        """Cancella i dati della sessione"""
        try:
            if self.session_key in st.session_state:
                del st.session_state[self.session_key]
            if self.user_key in st.session_state:
                del st.session_state[self.user_key]
                
        except Exception as e:
            logger.error(f"❌ Errore cancellazione sessione: {e}")
    
    def _is_session_valid(self) -> bool:
        """Verifica se la sessione è ancora valida"""
        try:
            if self.session_key not in st.session_state:
                return False
            
            session_data = st.session_state[self.session_key]
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            
            return datetime.now() < expires_at
            
        except Exception as e:
            logger.error(f"❌ Errore verifica validità sessione: {e}")
            return False
    
    def _get_session_login_time(self) -> Optional[datetime]:
        """Ottiene l'orario di login dalla sessione"""
        try:
            if self.session_key in st.session_state:
                session_data = st.session_state[self.session_key]
                return datetime.fromisoformat(session_data['login_time'])
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento orario login: {e}")
            return None
    
    def _get_client_ip(self) -> str:
        """Ottiene l'IP del client (approssimativo per Streamlit)"""
        try:
            # Streamlit non fornisce direttamente l'IP del client
            # Possiamo usare una stringa generica o implementare una soluzione più sofisticata
            return "127.0.0.1"  # Localhost per sviluppo
            
        except Exception as e:
            logger.error(f"❌ Errore ottenimento IP client: {e}")
            return "unknown"

# ===== FUNZIONI DI CONVENIENZA =====

def get_auth_manager() -> AuthManager:
    """Ottiene l'istanza globale dell'AuthManager"""
    if 'auth_manager' not in st.session_state:
        st.session_state['auth_manager'] = AuthManager()
    return st.session_state['auth_manager']

def require_auth():
    """Decorator per richiedere autenticazione"""
    auth_manager = get_auth_manager()
    return auth_manager.require_auth()

def require_permission(permission: str):
    """Decorator per richiedere un permesso specifico"""
    auth_manager = get_auth_manager()
    return auth_manager.require_permission(permission)

def require_role(role_name: str):
    """Decorator per richiedere un ruolo specifico"""
    auth_manager = get_auth_manager()
    return auth_manager.require_role(role_name)

def is_authenticated() -> bool:
    """Verifica se l'utente è autenticato"""
    auth_manager = get_auth_manager()
    return auth_manager.is_authenticated()

def has_permission(permission: str) -> bool:
    """Verifica se l'utente ha un permesso specifico"""
    auth_manager = get_auth_manager()
    return auth_manager.has_permission(permission)

def has_role(role_name: str) -> bool:
    """Verifica se l'utente ha un ruolo specifico"""
    auth_manager = get_auth_manager()
    return auth_manager.has_role(role_name)

def get_current_user() -> Optional[Dict[str, Any]]:
    """Ottiene l'utente corrente"""
    auth_manager = get_auth_manager()
    return auth_manager.get_current_user()

def get_user_info() -> Dict[str, Any]:
    """Ottiene informazioni complete dell'utente corrente"""
    auth_manager = get_auth_manager()
    return auth_manager.get_user_info()

def login(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Effettua il login"""
    auth_manager = get_auth_manager()
    return auth_manager.login(username, password)

def logout() -> bool:
    """Effettua il logout"""
    auth_manager = get_auth_manager()
    return auth_manager.logout()

def change_password(current_password: str, new_password: str) -> Tuple[bool, str]:
    """Cambia la password dell'utente corrente"""
    auth_manager = get_auth_manager()
    return auth_manager.change_password(current_password, new_password)

# ===== COMPONENTI UI =====

def render_login_form():
    """Renderizza il form di login"""
    st.title("🔐 Login - Dashboard Gestione Macelleria")
    st.markdown("---")
    
    with st.form("login_form"):
        st.subheader("Accedi al Sistema")
        
        username = st.text_input(
            "👤 Nome Utente",
            placeholder="Inserisci il tuo username",
            help="Username per l'accesso al sistema"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Inserisci la tua password",
            help="Password per l'accesso al sistema"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_button = st.form_submit_button("🚀 Accedi", use_container_width=True)
        
        with col2:
            if st.form_submit_button("❓ Aiuto", use_container_width=True):
                st.info("""
                **Credenziali di Default:**
                - Username: `admin`
                - Password: `admin123`
                
                **Nota:** Cambia la password dopo il primo accesso!
                """)
        
        if login_button:
            if not username or not password:
                st.error("⚠️ Inserisci username e password")
            else:
                with st.spinner("🔍 Autenticazione in corso..."):
                    success, message, user = login(username, password)
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>Dashboard Gestione Macelleria v1.0.0 - Creato da Ezio Camporeale</small>
    </div>
    """, unsafe_allow_html=True)

def render_user_info():
    """Renderizza le informazioni dell'utente corrente"""
    user_info = get_user_info()
    
    if not user_info:
        return
    
    with st.sidebar:
        st.markdown("### 👤 Utente Corrente")
        
        # Avatar e nome
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("👨‍💼")
        with col2:
            st.markdown(f"**{user_info['full_name']}**")
            st.caption(f"@{user_info['username']}")
        
        # Ruolo e permessi
        st.markdown(f"**Ruolo:** {user_info['role_name']}")
        
        if user_info['is_admin']:
            st.markdown("🔑 **Amministratore**")
        else:
            permissions = user_info['permissions']
            if permissions:
                st.markdown(f"**Permessi:** {', '.join(permissions)}")
        
        # Login time
        login_time = user_info.get('login_time')
        if login_time:
            st.caption(f"Login: {login_time.strftime('%H:%M')}")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            if logout():
                st.success("Logout effettuato")
                st.rerun()

def render_permission_denied():
    """Renderizza il messaggio di permesso negato"""
    st.error("🚫 **Accesso Negato**")
    st.warning("Non hai i privilegi necessari per accedere a questa sezione.")
    
    user_info = get_user_info()
    if user_info:
        st.info(f"**Ruolo attuale:** {user_info['role_name']}")
        st.info(f"**Permessi:** {', '.join(user_info['permissions'])}")
    
    if st.button("🔙 Torna alla Dashboard"):
        st.rerun()

if __name__ == "__main__":
    # Test del sistema di autenticazione
    print("🧪 Test Sistema di Autenticazione")
    
    # Test login con credenziali di default
    auth_manager = AuthManager()
    success, message, user = auth_manager.login("admin", "admin123")
    
    if success:
        print(f"✅ Login test riuscito: {user['username']}")
        print(f"   Ruolo: {user['role_name']}")
        print(f"   Permessi: {user['permissions']}")
    else:
        print(f"❌ Login test fallito: {message}")
    
    print("✅ Test completato")
