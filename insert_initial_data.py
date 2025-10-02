#!/usr/bin/env python3
"""
Script per inserire dati iniziali nel database Supabase
Dashboard Gestión Carnicería
Creato da Ezio Camporeale
"""

import os
import sys
import logging
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.supabase_manager import SupabaseManager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_initial_data():
    """Inserisce i dati iniziali nel database Supabase"""
    
    print("🚀 INIZIANDO INSERIMENTO DATI INIZIALI IN SUPABASE")
    print("=" * 60)
    
    # Configura le variabili d'ambiente per il test
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Inizializza il manager Supabase
    print("\n🔍 Inizializzando SupabaseManager...")
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ FALLO: Connessione a Supabase fallita.")
        return False
    
    print("✅ Connessione a Supabase stabilita.")
    
    # 1. Inserisci ruoli
    print("\n➡️ Inserendo ruoli...")
    roles_data = [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "admin",
            "description": "Administrador completo",
            "permissions": {"all": True}
        },
        {
            "id": "00000000-0000-0000-0000-000000000002", 
            "name": "manager",
            "description": "Gerente de tienda",
            "permissions": {"sales": True, "inventory": True, "reports": True}
        },
        {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "employee", 
            "description": "Empleado",
            "permissions": {"sales": True, "inventory": False, "reports": False}
        },
        {
            "id": "00000000-0000-0000-0000-000000000004",
            "name": "viewer",
            "description": "Solo lectura", 
            "permissions": {"reports": True}
        }
    ]
    
    for role in roles_data:
        result = db.insert("roles", role)
        if result:
            print(f"✅ Ruolo '{role['name']}' inserito")
        else:
            print(f"⚠️ Ruolo '{role['name']}' già esistente o errore")
    
    # 2. Inserisci utente admin
    print("\n➡️ Inserendo utente admin...")
    admin_user = {
        "id": "00000000-0000-0000-0000-000000000101",
        "email": "admin@carniceria.com",
        "password_hash": "admin123",  # In produzione dovrebbe essere hashata
        "first_name": "Admin",
        "last_name": "Sistema",
        "role_id": "00000000-0000-0000-0000-000000000001",
        "is_active": True
    }
    
    admin_result = db.insert("users", admin_user)
    if admin_result:
        print("✅ Utente admin inserito")
    else:
        print("⚠️ Utente admin già esistente o errore")
    
    # 3. Inserisci categorie prodotti
    print("\n➡️ Inserendo categorie prodotti...")
    categories_data = [
        {
            "id": "00000000-0000-0000-0000-000000000201",
            "name": "Carnes",
            "description": "Carnes frescas",
            "color": "#DC3545"
        },
        {
            "id": "00000000-0000-0000-0000-000000000202",
            "name": "Aves", 
            "description": "Pollo y otras aves",
            "color": "#FFC107"
        },
        {
            "id": "00000000-0000-0000-0000-000000000203",
            "name": "Embutidos",
            "description": "Embutidos y fiambres", 
            "color": "#6F42C1"
        },
        {
            "id": "00000000-0000-0000-0000-000000000204",
            "name": "Pescados",
            "description": "Pescados frescos",
            "color": "#17A2B8"
        },
        {
            "id": "00000000-0000-0000-0000-000000000205",
            "name": "Verduras",
            "description": "Verduras frescas",
            "color": "#28A745"
        },
        {
            "id": "00000000-0000-0000-0000-000000000206",
            "name": "Otros",
            "description": "Otros productos",
            "color": "#6C757D"
        }
    ]
    
    for category in categories_data:
        result = db.insert("product_categories", category)
        if result:
            print(f"✅ Categoria '{category['name']}' inserita")
        else:
            print(f"⚠️ Categoria '{category['name']}' già esistente o errore")
    
    # 4. Inserisci unità di misura
    print("\n➡️ Inserendo unità di misura...")
    units_data = [
        {
            "id": "00000000-0000-0000-0000-000000000301",
            "name": "Kilogramo",
            "symbol": "kg",
            "description": "Peso en kilogramos"
        },
        {
            "id": "00000000-0000-0000-0000-000000000302",
            "name": "Gramo",
            "symbol": "g", 
            "description": "Peso en gramos"
        },
        {
            "id": "00000000-0000-0000-0000-000000000303",
            "name": "Unidad",
            "symbol": "un",
            "description": "Cantidad en unidades"
        },
        {
            "id": "00000000-0000-0000-0000-000000000304",
            "name": "Libra",
            "symbol": "lb",
            "description": "Peso en libras"
        },
        {
            "id": "00000000-0000-0000-0000-000000000305",
            "name": "Onza",
            "symbol": "oz",
            "description": "Peso en onzas"
        }
    ]
    
    for unit in units_data:
        result = db.insert("units_of_measure", unit)
        if result:
            print(f"✅ Unità '{unit['name']}' inserita")
        else:
            print(f"⚠️ Unità '{unit['name']}' già esistente o errore")
    
    # 5. Testa la connessione
    print("\n➡️ Testando connessione...")
    users = db.select("users", filters={"email": "admin@carniceria.com"})
    if users:
        print(f"✅ Utente admin trovato: {users[0]['email']}")
    else:
        print("❌ Utente admin non trovato")
    
    print("\n" + "=" * 60)
    print("✅ INSERIMENTO DATI INIZIALI COMPLETATO!")
    print("🔑 Credenziali di accesso:")
    print("   Email: admin@carniceria.com")
    print("   Password: admin123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = insert_initial_data()
    if success:
        print("\n🎉 Dati iniziali inseriti con successo!")
        print("🚀 Ora puoi testare il login su Streamlit Cloud")
    else:
        print("\n❌ Errore durante l'inserimento dei dati")
        sys.exit(1)
