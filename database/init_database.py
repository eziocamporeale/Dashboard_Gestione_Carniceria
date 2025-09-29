#!/usr/bin/env python3
"""
Script di inizializzazione database per Dashboard Gestione Macelleria
Creato da Ezio Camporeale
"""

import sys
import os
from pathlib import Path

# Aggiungi il percorso del progetto al Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database_manager import MacelleriaDatabaseManager, init_database, test_database_connection
from config import DATABASE_PATH, ensure_directories
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Funzione principale di inizializzazione"""
    print("🚀 Inizializzazione Database Dashboard Gestione Macelleria")
    print("=" * 60)
    
    try:
        # Crea le directory necessarie
        print("📁 Creazione directory necessarie...")
        ensure_directories()
        print("✅ Directory create correttamente")
        
        # Inizializza il database
        print("🗄️ Inizializzazione database...")
        init_database()
        print("✅ Database inizializzato correttamente")
        
        # Test connessione
        print("🔍 Test connessione database...")
        if test_database_connection():
            print("✅ Connessione database OK")
        else:
            print("❌ Errore connessione database")
            return False
        
        # Crea istanza database manager
        db = MacelleriaDatabaseManager()
        
        # Verifica tabelle create
        print("📋 Verifica tabelle create...")
        tables_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        tables = db.execute_query(tables_query)
        print(f"✅ {len(tables)} tabelle create:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verifica dati iniziali
        print("📊 Verifica dati iniziali...")
        
        # Conta ruoli utente
        roles_count = db.execute_query("SELECT COUNT(*) FROM user_roles", fetch="one")[0]
        print(f"✅ {roles_count} ruoli utente inseriti")
        
        # Conta unità di misura
        units_count = db.execute_query("SELECT COUNT(*) FROM units_of_measure", fetch="one")[0]
        print(f"✅ {units_count} unità di misura inserite")
        
        # Conta categorie prodotti
        categories_count = db.execute_query("SELECT COUNT(*) FROM product_categories", fetch="one")[0]
        print(f"✅ {categories_count} categorie prodotti inserite")
        
        # Conta impostazioni sistema
        settings_count = db.execute_query("SELECT COUNT(*) FROM system_settings", fetch="one")[0]
        print(f"✅ {settings_count} impostazioni sistema inserite")
        
        # Conta utenti
        users_count = db.execute_query("SELECT COUNT(*) FROM users", fetch="one")[0]
        print(f"✅ {users_count} utenti inseriti")
        
        # Test funzionalità base
        print("🧪 Test funzionalità base...")
        
        # Test statistiche dashboard
        stats = db.get_dashboard_stats()
        print(f"✅ Statistiche dashboard: {len(stats)} metriche disponibili")
        
        # Test categorie prodotti
        categories = db.get_product_categories()
        print(f"✅ Categorie prodotti: {len(categories)} disponibili")
        
        # Test unità di misura
        units = db.get_units_of_measure()
        print(f"✅ Unità di misura: {len(units)} disponibili")
        
        # Test ruoli utente
        roles = db.get_user_roles()
        print(f"✅ Ruoli utente: {len(roles)} disponibili")
        
        # Informazioni database
        print("\n📋 Informazioni Database:")
        print(f"   📍 Percorso: {DATABASE_PATH}")
        print(f"   📏 Dimensione: {Path(DATABASE_PATH).stat().st_size / 1024:.1f} KB")
        print(f"   🗓️ Creato: {Path(DATABASE_PATH).stat().st_mtime}")
        
        # Credenziali di default
        print("\n🔐 Credenziali di Default:")
        print("   👤 Username: admin")
        print("   🔑 Password: admin123")
        print("   ⚠️  IMPORTANTE: Cambia la password dopo il primo accesso!")
        
        print("\n🎉 Inizializzazione completata con successo!")
        print("🚀 Puoi ora avviare l'applicazione con: streamlit run app.py")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore durante l'inizializzazione: {e}")
        print(f"❌ Errore: {e}")
        return False

def create_sample_data():
    """Crea dati di esempio per test"""
    print("\n📝 Creazione dati di esempio...")
    
    try:
        db = MacelleriaDatabaseManager()
        
        # Crea alcuni prodotti di esempio
        sample_products = [
            {
                'name': 'Tagliata di Manzo',
                'code': 'MAN001',
                'category_id': 1,  # Carne Bovina
                'unit_id': 1,      # kg
                'selling_price': 25.00,
                'cost_price': 18.00,
                'min_stock_level': 5,
                'max_stock_level': 50,
                'shelf_life_days': 3,
                'requires_temperature_control': True,
                'storage_temperature_min': 2,
                'storage_temperature_max': 4,
                'created_by': 1
            },
            {
                'name': 'Petto di Pollo',
                'code': 'POL001',
                'category_id': 3,  # Pollame
                'unit_id': 1,      # kg
                'selling_price': 12.00,
                'cost_price': 8.50,
                'min_stock_level': 10,
                'max_stock_level': 100,
                'shelf_life_days': 2,
                'requires_temperature_control': True,
                'storage_temperature_min': 2,
                'storage_temperature_max': 4,
                'created_by': 1
            },
            {
                'name': 'Prosciutto San Daniele',
                'code': 'SAL001',
                'category_id': 4,  # Salumi
                'unit_id': 1,      # kg
                'selling_price': 35.00,
                'cost_price': 28.00,
                'min_stock_level': 3,
                'max_stock_level': 20,
                'shelf_life_days': 30,
                'requires_temperature_control': True,
                'storage_temperature_min': 4,
                'storage_temperature_max': 8,
                'created_by': 1
            }
        ]
        
        for product_data in sample_products:
            success, product_id = db.create_product(product_data)
            if success:
                print(f"✅ Prodotto creato: {product_data['name']} (ID: {product_id})")
            else:
                print(f"❌ Errore creazione prodotto: {product_data['name']}")
        
        # Crea alcuni clienti di esempio
        sample_customers = [
            {
                'first_name': 'Mario',
                'last_name': 'Rossi',
                'email': 'mario.rossi@email.com',
                'phone': '+39 333 1234567',
                'address': 'Via Roma 123',
                'city': 'Roma',
                'postal_code': '00100',
                'customer_type': 'individual',
                'preferences': {'preferred_cuts': ['tagliata', 'filetto'], 'delivery_day': 'sabato'},
                'created_by': 1
            },
            {
                'first_name': 'Giulia',
                'last_name': 'Bianchi',
                'email': 'giulia.bianchi@email.com',
                'phone': '+39 333 7654321',
                'address': 'Via Milano 456',
                'city': 'Milano',
                'postal_code': '20100',
                'customer_type': 'individual',
                'allergies': 'glutine',
                'preferences': {'preferred_cuts': ['pollo', 'tacchino'], 'delivery_day': 'venerdì'},
                'created_by': 1
            }
        ]
        
        for customer_data in sample_customers:
            success, customer_id = db.create_customer(customer_data)
            if success:
                print(f"✅ Cliente creato: {customer_data['first_name']} {customer_data['last_name']} (ID: {customer_id})")
            else:
                print(f"❌ Errore creazione cliente: {customer_data['first_name']} {customer_data['last_name']}")
        
        print("✅ Dati di esempio creati correttamente")
        
    except Exception as e:
        logger.error(f"❌ Errore creazione dati di esempio: {e}")
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    print("🥩 Dashboard Gestione Macelleria - Inizializzazione Database")
    print("Creato da Ezio Camporeale")
    print()
    
    # Esegui inizializzazione
    if main():
        # Chiedi se creare dati di esempio
        response = input("\n❓ Vuoi creare dati di esempio per test? (s/n): ").lower().strip()
        if response in ['s', 'si', 'y', 'yes']:
            create_sample_data()
        
        print("\n🎯 Prossimi passi:")
        print("1. Avvia l'applicazione: streamlit run app.py")
        print("2. Accedi con le credenziali di default")
        print("3. Cambia la password admin")
        print("4. Configura le impostazioni aziendali")
        print("5. Inizia a utilizzare il sistema!")
        
    else:
        print("\n❌ Inizializzazione fallita. Controlla i log per dettagli.")
        sys.exit(1)

