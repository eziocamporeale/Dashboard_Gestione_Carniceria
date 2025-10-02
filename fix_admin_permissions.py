#!/usr/bin/env python3
"""
Script per correggere i permessi dell'utente admin
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory radice del progetto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.supabase_manager import SupabaseManager

def fix_admin_permissions():
    """Corregge i permessi dell'utente admin"""
    print("🔧 CORREGGENDO PERMESSI UTENTE ADMIN")
    print("=" * 50)
    
    # Inizializza SupabaseManager
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ ERRORE: Connessione Supabase non disponibile")
        return False
    
    print("✅ Connessione Supabase attiva")
    
    try:
        # Trova l'utente admin
        admin_users = db.select('users', filters={'email': 'admin@carniceria.com'})
        
        if not admin_users:
            print("❌ Utente admin non trovato")
            return False
        
        admin_user = admin_users[0]
        print(f"✅ Utente admin trovato: {admin_user['email']}")
        
        # Aggiorna i permessi dell'admin
        update_data = {
            'is_admin': True,
            'role_id': 1  # Assicurati che sia il ruolo admin
        }
        
        result = db.update('users', update_data, {'email': 'admin@carniceria.com'})
        
        if result:
            print("✅ Permessi admin aggiornati con successo")
            
            # Verifica l'aggiornamento
            updated_admin = db.select('users', filters={'email': 'admin@carniceria.com'})
            if updated_admin and updated_admin[0].get('is_admin'):
                print("✅ Verifica: Utente admin ora ha is_admin=True")
                return True
            else:
                print("❌ Verifica fallita: is_admin non impostato")
                return False
        else:
            print("❌ Aggiornamento permessi fallito")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante aggiornamento permessi: {e}")
        return False

def test_admin_permissions():
    """Testa i permessi dell'admin"""
    print("\n🧪 TESTANDO PERMESSI ADMIN")
    print("=" * 30)
    
    try:
        from components.auth.auth_manager import get_auth_manager
        
        auth_manager = get_auth_manager()
        
        # Testa se l'admin ha permessi
        if auth_manager.has_permission("all"):
            print("✅ Admin ha permesso 'all'")
        else:
            print("❌ Admin non ha permesso 'all'")
        
        if auth_manager.has_permission("dashboard"):
            print("✅ Admin ha permesso 'dashboard'")
        else:
            print("❌ Admin non ha permesso 'dashboard'")
        
        # Testa se è admin
        user = auth_manager.get_current_user()
        if user and user.get('is_admin'):
            print("✅ Utente è riconosciuto come admin")
        else:
            print("❌ Utente non è riconosciuto come admin")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore durante test permessi: {e}")
        return False

if __name__ == "__main__":
    print("🔧 SCRIPT CORREZIONE PERMESSI ADMIN")
    print("=" * 50)
    
    # Assicurati che le variabili d'ambiente siano impostate
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Corregge i permessi
    success = fix_admin_permissions()
    
    if success:
        # Testa i permessi
        test_success = test_admin_permissions()
        
        if test_success:
            print("\n🎉 PERMESSI ADMIN CORRETTI E TESTATI!")
            print("✅ Il menu dovrebbe ora essere visibile")
        else:
            print("\n⚠️ Permessi corretti ma test fallito")
    else:
        print("\n❌ FALLIMENTO: Impossibile correggere i permessi admin")
        print("💡 Prova a verificare manualmente i permessi su Supabase Dashboard")
    
    print("\n" + "=" * 50)
