#!/usr/bin/env python3
"""
Script per aggiornare la password dell'utente admin
Dashboard Gestión Carnicería
Creato da Ezio Camporeale
"""

import os
import sys
import logging
import bcrypt
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.supabase_manager import SupabaseManager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_admin_password():
    """Aggiorna la password dell'utente admin"""
    
    print("🔧 AGGIORNANDO PASSWORD UTENTE ADMIN")
    print("=" * 50)
    
    # Configura le variabili d'ambiente
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Inizializza il manager Supabase
    print("\n🔍 Inizializzando SupabaseManager...")
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ FALLO: Connessione a Supabase fallita.")
        return False
    
    print("✅ Connessione a Supabase stabilita.")
    
    # 1. Genera nuovo hash per admin123
    print("\n➡️ Generando nuovo hash per password 'admin123'...")
    password = "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    new_password_hash = bcrypt.hashpw(password_bytes, salt)
    print(f"Nuovo hash: {new_password_hash.decode('utf-8')}")
    
    # 2. Cerca l'utente admin
    print("\n➡️ Cercando utente admin...")
    users = db.select("users", filters={"email": "admin@carniceria.com"})
    
    if not users:
        print("❌ Utente admin non trovato")
        return False
    
    user = users[0]
    print(f"✅ Utente admin trovato: {user.get('email')}")
    print(f"Hash attuale: {user.get('password_hash')}")
    
    # 3. Aggiorna la password
    print("\n➡️ Aggiornando password...")
    update_data = {
        "password_hash": new_password_hash.decode('utf-8')
    }
    
    success = db.update("users", update_data, {"email": "admin@carniceria.com"})
    
    if success:
        print("✅ Password aggiornata con successo!")
        
        # 4. Testa la nuova password
        print("\n➡️ Testando nuova password...")
        auth_result = db.authenticate_user("admin@carniceria.com", "admin123")
        
        if auth_result:
            print("✅ Autenticazione riuscita con nuova password!")
            print(f"   Utente: {auth_result.get('email')}")
        else:
            print("❌ Autenticazione ancora fallita!")
    else:
        print("❌ Errore aggiornando password")
        return False
    
    print("\n" + "=" * 50)
    print("✅ PASSWORD AGGIORNATA CON SUCCESSO!")
    print("🔑 Credenziali:")
    print("   Email: admin@carniceria.com")
    print("   Password: admin123")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = update_admin_password()
    if success:
        print("\n🎉 Password aggiornata con successo!")
        print("🚀 Ora puoi testare il login su Streamlit Cloud")
    else:
        print("\n❌ Errore aggiornando password")
        sys.exit(1)
