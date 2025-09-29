#!/usr/bin/env python3
"""
Sistema de Autenticación para Dashboard Gestión Carnicería
Gestiona login, logout, sesiones y permisos de usuario
Creado por Ezio Camporeale
Traducido al español para Argentina
"""

import streamlit as st
import bcrypt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from database.database_manager import get_db_manager

# Configurar logging
logger = logging.getLogger(__name__)

class AuthManager:
    """Manager para autenticación y autorización"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.session_key = "carniceria_auth_session"
        self.user_key = "carniceria_user"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Autentica un usuario
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Tuple[success, message, user_data]
        """
        try:
            # Autenticar usuario
            user = self.db.authenticate_user(username, password)
            
            if user:
                # Guardar sesión
                self._save_session(user)
                
                # Log de la actividad
                self.db.log_activity(
                    user_id=user['id'],
                    action='login',
                    details=f'Login realizado por {username}',
                    ip_address=self._get_client_ip()
                )
                
                logger.info(f"✅ Login realizado: {username}")
                return True, "Login realizado con éxito", user
            else:
                logger.warning(f"❌ Intento de login fallido: {username}")
                return False, "Credenciales no válidas", None
                
        except Exception as e:
            logger.error(f"❌ Error durante login: {e}")
            return False, f"Error durante la autenticación: {str(e)}", None
    
    def logout(self) -> bool:
        """
        Desconecta al usuario actual
        
        Returns:
            bool: True si logout exitoso
        """
        try:
            user = self.get_current_user()
            if user:
                # Log de la actividad
                self.db.log_activity(
                    user_id=user['id'],
                    action='logout',
                    details=f'Logout realizado por {user["username"]}',
                    ip_address=self._get_client_ip()
                )
            
            # Remover sesión
            self._clear_session()
            
            logger.info("✅ Logout realizado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante logout: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario actual de la sesión
        
        Returns:
            Dict con datos del usuario o None si no autenticado
        """
        try:
            if self.user_key in st.session_state:
                user_data = st.session_state[self.user_key]
                
                # Verificar si la sesión sigue siendo válida
                if self._is_session_valid():
                    return user_data
                else:
                    # Sesión expirada
                    self._clear_session()
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario actual: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Verifica si el usuario está autenticado
        
        Returns:
            bool: True si autenticado
        """
        user = self.get_current_user()
        return user is not None
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico
        
        Args:
            permission: Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso
        """
        try:
            user = self.get_current_user()
            if not user:
                return False
            
            # Admin tiene todos los permisos
            if user.get('is_admin', False):
                return True
            
            # Verificar permisos específicos
            user_permissions = user.get('permissions', [])
            return permission in user_permissions or 'all' in user_permissions
            
        except Exception as e:
            logger.error(f"❌ Error verificando permiso {permission}: {e}")
            return False
    
    def has_role(self, role_name: str) -> bool:
        """
        Verifica si el usuario actual tiene un rol específico
        
        Args:
            role_name: Nombre del rol a verificar
            
        Returns:
            bool: True si tiene el rol
        """
        try:
            user = self.get_current_user()
            if not user:
                return False
            
            return user.get('role_name') == role_name
            
        except Exception as e:
            logger.error(f"❌ Error verificando rol {role_name}: {e}")
            return False
    
    def require_auth(self, redirect_to_login: bool = True):
        """
        Decorator para requerir autenticación
        
        Args:
            redirect_to_login: Si True, redirige al login si no autenticado
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Acceso requerido. Inicia sesión para continuar.")
                st.stop()
            return False
        return True
    
    def require_permission(self, permission: str, redirect_to_login: bool = True):
        """
        Decorator para requerir un permiso específico
        
        Args:
            permission: Permiso requerido
            redirect_to_login: Si True, redirige al login si no autenticado
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Acceso requerido. Inicia sesión para continuar.")
                st.stop()
            return False
        
        if not self.has_permission(permission):
            st.error(f"🚫 Permiso denegado. No tienes privilegios para acceder a esta sección.")
            st.stop()
        
        return True
    
    def require_role(self, role_name: str, redirect_to_login: bool = True):
        """
        Decorator para requerir un rol específico
        
        Args:
            role_name: Rol requerido
            redirect_to_login: Si True, redirige al login si no autenticado
        """
        if not self.is_authenticated():
            if redirect_to_login:
                st.error("🔒 Acceso requerido. Inicia sesión para continuar.")
                st.stop()
            return False
        
        if not self.has_role(role_name):
            st.error(f"🚫 Rol requerido: {role_name}. No tienes privilegios para acceder a esta sección.")
            st.stop()
        
        return True
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Obtiene información completa del usuario actual
        
        Returns:
            Dict con información del usuario
        """
        user = self.get_current_user()
        if not user:
            return {}
        
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'full_name': f"{user['first_name']} {user['last_name']}",
            'role_name': user['role_name'],
            'is_admin': user.get('is_admin', False),
            'permissions': user.get('permissions', []),
            'login_time': self._get_session_login_time()
        }
    
    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambia la contraseña del usuario actual
        
        Args:
            current_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            Tuple[success, message]
        """
        try:
            user = self.get_current_user()
            if not user:
                return False, "Usuario no autenticado"
            
            # Verificar contraseña actual
            if not self.db.authenticate_user(user['username'], current_password):
                return False, "Contraseña actual incorrecta"
            
            # Hash de la nueva contraseña
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Actualizar contraseña en base de datos
            query = "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.db.execute_query(query, (new_password_hash, user['id']), "none")
            
            # Log de la actividad
            self.db.log_activity(
                user_id=user['id'],
                action='password_change',
                details='Contraseña modificada',
                ip_address=self._get_client_ip()
            )
            
            logger.info(f"✅ Contraseña modificada para usuario: {user['username']}")
            return True, "Contraseña modificada con éxito"
            
        except Exception as e:
            logger.error(f"❌ Error cambio contraseña: {e}")
            return False, f"Error durante el cambio de contraseña: {str(e)}"
    
    def _save_session(self, user_data: Dict[str, Any]):
        """Guarda los datos de la sesión"""
        try:
            session_data = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'login_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=8)).isoformat()
            }
            
            st.session_state[self.session_key] = session_data
            st.session_state[self.user_key] = user_data
            
        except Exception as e:
            logger.error(f"❌ Error guardando sesión: {e}")
    
    def _clear_session(self):
        """Borra los datos de la sesión"""
        try:
            if self.session_key in st.session_state:
                del st.session_state[self.session_key]
            if self.user_key in st.session_state:
                del st.session_state[self.user_key]
                
        except Exception as e:
            logger.error(f"❌ Error borrando sesión: {e}")
    
    def _is_session_valid(self) -> bool:
        """Verifica si la sesión sigue siendo válida"""
        try:
            if self.session_key not in st.session_state:
                return False
            
            session_data = st.session_state[self.session_key]
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            
            return datetime.now() < expires_at
            
        except Exception as e:
            logger.error(f"❌ Error verificando validez sesión: {e}")
            return False
    
    def _get_session_login_time(self) -> Optional[datetime]:
        """Obtiene la hora de login de la sesión"""
        try:
            if self.session_key in st.session_state:
                session_data = st.session_state[self.session_key]
                return datetime.fromisoformat(session_data['login_time'])
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo hora login: {e}")
            return None
    
    def _get_client_ip(self) -> str:
        """Obtiene la IP del cliente (aproximativo para Streamlit)"""
        try:
            # Streamlit no proporciona directamente la IP del cliente
            # Podemos usar una cadena genérica o implementar una solución más sofisticada
            return "127.0.0.1"  # Localhost para desarrollo
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo IP cliente: {e}")
            return "unknown"

# ===== FUNCIONES DE CONVENIENCIA =====

def get_auth_manager() -> AuthManager:
    """Obtiene la instancia global del AuthManager"""
    if 'auth_manager' not in st.session_state:
        st.session_state['auth_manager'] = AuthManager()
    return st.session_state['auth_manager']

def require_auth():
    """Decorator para requerir autenticación"""
    auth_manager = get_auth_manager()
    return auth_manager.require_auth()

def require_permission(permission: str):
    """Decorator para requerir un permiso específico"""
    auth_manager = get_auth_manager()
    return auth_manager.require_permission(permission)

def require_role(role_name: str):
    """Decorator para requerir un rol específico"""
    auth_manager = get_auth_manager()
    return auth_manager.require_role(role_name)

def is_authenticated() -> bool:
    """Verifica si el usuario está autenticado"""
    auth_manager = get_auth_manager()
    return auth_manager.is_authenticated()

def has_permission(permission: str) -> bool:
    """Verifica si el usuario tiene un permiso específico"""
    auth_manager = get_auth_manager()
    return auth_manager.has_permission(permission)

def has_role(role_name: str) -> bool:
    """Verifica si el usuario tiene un rol específico"""
    auth_manager = get_auth_manager()
    return auth_manager.has_role(role_name)

def get_current_user() -> Optional[Dict[str, Any]]:
    """Obtiene el usuario actual"""
    auth_manager = get_auth_manager()
    return auth_manager.get_current_user()

def get_user_info() -> Dict[str, Any]:
    """Obtiene información completa del usuario actual"""
    auth_manager = get_auth_manager()
    return auth_manager.get_user_info()

def login(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Realiza el login"""
    auth_manager = get_auth_manager()
    return auth_manager.login(username, password)

def logout() -> bool:
    """Realiza el logout"""
    auth_manager = get_auth_manager()
    return auth_manager.logout()

def change_password(current_password: str, new_password: str) -> Tuple[bool, str]:
    """Cambia la contraseña del usuario actual"""
    auth_manager = get_auth_manager()
    return auth_manager.change_password(current_password, new_password)

# ===== COMPONENTES UI =====

def render_login_form():
    """Renderiza el formulario de login"""
    st.title("🔐 Login - Dashboard Gestión Carnicería")
    st.markdown("---")
    
    with st.form("login_form"):
        st.subheader("Acceder al Sistema")
        
        username = st.text_input(
            "👤 Nombre de Usuario",
            placeholder="Ingresa tu nombre de usuario",
            help="Nombre de usuario para acceder al sistema"
        )
        
        password = st.text_input(
            "🔑 Contraseña",
            type="password",
            placeholder="Ingresa tu contraseña",
            help="Contraseña para acceder al sistema"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_button = st.form_submit_button("🚀 Acceder", use_container_width=True)
        
        with col2:
            if st.form_submit_button("❓ Ayuda", use_container_width=True):
                st.info("""
                **Credenciales por Defecto:**
                - Usuario: `admin`
                - Contraseña: `admin123`
                
                **Nota:** ¡Cambia la contraseña después del primer acceso!
                """)
        
        if login_button:
            if not username or not password:
                st.error("⚠️ Ingresa usuario y contraseña")
            else:
                with st.spinner("🔍 Autenticando..."):
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
        <small>Dashboard Gestión Carnicería v1.0.0 - Creado por Ezio Camporeale</small>
    </div>
    """, unsafe_allow_html=True)

def render_user_info():
    """Renderiza la información del usuario actual"""
    user_info = get_user_info()
    
    if not user_info:
        return
    
    with st.sidebar:
        st.markdown("### 👤 Usuario Actual")
        
        # Avatar y nombre
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("👨‍💼")
        with col2:
            st.markdown(f"**{user_info['full_name']}**")
            st.caption(f"@{user_info['username']}")
        
        # Rol y permisos
        st.markdown(f"**Rol:** {user_info['role_name']}")
        
        if user_info['is_admin']:
            st.markdown("🔑 **Administrador**")
        else:
            permissions = user_info['permissions']
            if permissions:
                st.markdown(f"**Permisos:** {', '.join(permissions)}")
        
        # Hora de login
        login_time = user_info.get('login_time')
        if login_time:
            st.caption(f"Login: {login_time.strftime('%H:%M')}")
        
        # Botón logout
        if st.button("🚪 Logout", use_container_width=True):
            if logout():
                st.success("Logout realizado")
                st.rerun()

def render_permission_denied():
    """Renderiza el mensaje de permiso denegado"""
    st.error("🚫 **Acceso Denegado**")
    st.warning("No tienes los privilegios necesarios para acceder a esta sección.")
    
    user_info = get_user_info()
    if user_info:
        st.info(f"**Rol actual:** {user_info['role_name']}")
        st.info(f"**Permisos:** {', '.join(user_info['permissions'])}")
    
    if st.button("🔙 Volver al Dashboard"):
        st.rerun()

if __name__ == "__main__":
    # Test del sistema de autenticación
    print("🧪 Test Sistema de Autenticación")
    
    # Test login con credenciales por defecto
    auth_manager = AuthManager()
    success, message, user = auth_manager.login("admin", "admin123")
    
    if success:
        print(f"✅ Test login exitoso: {user['username']}")
        print(f"   Rol: {user['role_name']}")
        print(f"   Permisos: {user['permissions']}")
    else:
        print(f"❌ Test login fallido: {message}")
    
    print("✅ Test completado")
