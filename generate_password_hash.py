#!/usr/bin/env python3
"""
Script per generare hash bcrypt corretto per la password admin123
"""

import bcrypt

def generate_admin_hash():
    """Genera hash bcrypt per password 'admin123'"""
    password = "admin123"
    
    # Genera salt e hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    print("=" * 60)
    print("GENERAZIONE HASH PASSWORD ADMIN")
    print("=" * 60)
    print(f"Password: {password}")
    print(f"Hash generato: {password_hash.decode('utf-8')}")
    print("=" * 60)
    
    # Verifica che l'hash funzioni
    if bcrypt.checkpw(password.encode('utf-8'), password_hash):
        print("✅ Hash verificato con successo!")
    else:
        print("❌ Errore nella verifica dell'hash!")
    
    return password_hash.decode('utf-8')

def test_existing_hash():
    """Testa l'hash esistente nel database"""
    existing_hash = '$0.00b$0.00$N7ODldIPrnAg078f8VOOb.XRd.cEHJZ6YYhrDTSAE5BF9r52Km1Qm'
    password = "admin123"
    
    print("\n" + "=" * 60)
    print("TEST HASH ESISTENTE NEL DATABASE")
    print("=" * 60)
    print(f"Password: {password}")
    print(f"Hash esistente: {existing_hash}")
    
    try:
        if bcrypt.checkpw(password.encode('utf-8'), existing_hash.encode('utf-8')):
            print("✅ Hash esistente FUNZIONA correttamente!")
            return True
        else:
            print("❌ Hash esistente NON FUNZIONA!")
            return False
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        return False

if __name__ == "__main__":
    print("🔐 GENERATORE HASH PASSWORD PER DASHBOARD MACELLERIA")
    
    # Testa hash esistente
    if test_existing_hash():
        print("\n✅ L'hash esistente dovrebbe funzionare!")
        print("Prova a fare il login con:")
        print("   Email: admin@carniceria.com")
        print("   Password: admin123")
    else:
        print("\n🔄 Generando nuovo hash...")
        new_hash = generate_admin_hash()
        print(f"\nSQL da eseguire:")
        print(f"UPDATE users SET password_hash = '{new_hash}' WHERE email = 'admin@carniceria.com';")
