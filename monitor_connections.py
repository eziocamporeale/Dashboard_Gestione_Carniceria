#!/usr/bin/env python3
"""
Script per monitorare le connessioni e risorse
Creado por Ezio Camporeale
"""

import os
import sys
import psutil
import gc
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from database.hybrid_database_manager import get_hybrid_manager
    print("✅ Importato HybridDatabaseManager")
except ImportError as e:
    print(f"❌ Errore import HybridDatabaseManager: {e}")
    sys.exit(1)

def get_system_info():
    """Ottiene informazioni sul sistema"""
    
    print("🖥️  INFORMAZIONI SISTEMA")
    print("=" * 30)
    
    # Processo corrente
    process = psutil.Process()
    
    print(f"📊 Process ID: {process.pid}")
    print(f"💾 Memoria utilizzata: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"🔗 File aperti: {process.num_fds()}")
    print(f"🧵 Thread attivi: {process.num_threads()}")
    print(f"⏱️  Tempo CPU: {process.cpu_percent()}%")
    
    # Memoria sistema
    memory = psutil.virtual_memory()
    print(f"\n💾 Memoria Sistema:")
    print(f"  - Totale: {memory.total / 1024 / 1024 / 1024:.2f} GB")
    print(f"  - Disponibile: {memory.available / 1024 / 1024 / 1024:.2f} GB")
    print(f"  - Utilizzata: {memory.percent}%")
    
    # Limiti sistema
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        print(f"\n📁 Limiti File Descriptors:")
        print(f"  - Soft limit: {soft}")
        print(f"  - Hard limit: {hard}")
    except Exception as e:
        print(f"❌ Errore ottenendo limiti: {e}")

def get_database_info():
    """Ottiene informazioni sulle connessioni database"""
    
    print("\n🗄️  INFORMAZIONI DATABASE")
    print("=" * 30)
    
    try:
        db = get_hybrid_manager()
        info = db.get_connection_info()
        
        print(f"🔗 Usa Supabase: {info.get('use_supabase', False)}")
        print(f"✅ Supabase disponibile: {info.get('supabase_available', False)}")
        print(f"✅ SQLite disponibile: {info.get('sqlite_available', False)}")
        
        if 'supabase' in info:
            supabase_info = info['supabase']
            print(f"\n📡 Supabase:")
            print(f"  - Connessioni attive: {supabase_info.get('connection_count', 0)}")
            print(f"  - Max connessioni: {supabase_info.get('max_connections', 0)}")
            print(f"  - Connesso: {supabase_info.get('is_connected', False)}")
            
            cache_size = supabase_info.get('cache_size', {})
            print(f"  - Cache size:")
            for table, size in cache_size.items():
                print(f"    * {table}: {size}")
                
    except Exception as e:
        print(f"❌ Errore ottenendo info database: {e}")

def cleanup_resources():
    """Pulisce le risorse"""
    
    print("\n🧹 PULIZIA RISORSE")
    print("=" * 20)
    
    try:
        # Cleanup database
        db = get_hybrid_manager()
        db.cleanup()
        print("✅ Database cleanup completato")
        
        # Garbage collection
        collected = gc.collect()
        print(f"✅ Garbage collection: {collected} oggetti rimossi")
        
        # Info dopo cleanup
        process = psutil.Process()
        print(f"🔗 File aperti dopo cleanup: {process.num_fds()}")
        print(f"💾 Memoria dopo cleanup: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"❌ Errore durante cleanup: {e}")

def check_file_descriptors():
    """Verifica i file descriptors aperti"""
    
    print("\n📁 FILE DESCRIPTORS APERTI")
    print("=" * 30)
    
    try:
        process = psutil.Process()
        open_files = process.open_files()
        
        print(f"📊 Totale file aperti: {len(open_files)}")
        
        if len(open_files) > 0:
            print("\n📋 Lista file aperti:")
            for i, file_info in enumerate(open_files[:20]):  # Mostra solo i primi 20
                print(f"  {i+1}. {file_info.path} (fd: {file_info.fd})")
            
            if len(open_files) > 20:
                print(f"  ... e altri {len(open_files) - 20} file")
        
        # Raggruppa per tipo
        file_types = {}
        for file_info in open_files:
            ext = Path(file_info.path).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_types:
            print(f"\n📊 File per tipo:")
            for ext, count in sorted(file_types.items()):
                print(f"  - {ext or 'no extension'}: {count}")
                
    except Exception as e:
        print(f"❌ Errore verificando file descriptors: {e}")

def monitor_connections():
    """Monitora le connessioni in tempo reale"""
    
    print("\n🔍 MONITORAGGIO CONNESSIONI")
    print("=" * 30)
    
    try:
        db = get_hybrid_manager()
        
        print("📊 Stato connessioni:")
        info = db.get_connection_info()
        
        if 'supabase' in info:
            supabase_info = info['supabase']
            connection_count = supabase_info.get('connection_count', 0)
            max_connections = supabase_info.get('max_connections', 10)
            
            print(f"  - Connessioni attive: {connection_count}/{max_connections}")
            
            if connection_count >= max_connections * 0.8:
                print("⚠️  ATTENZIONE: Connessioni vicine al limite!")
            elif connection_count >= max_connections:
                print("❌ ERRORE: Limite connessioni superato!")
            else:
                print("✅ Connessioni OK")
        
        # Verifica memoria
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > 500:  # Più di 500MB
            print(f"⚠️  ATTENZIONE: Uso memoria alto: {memory_mb:.2f} MB")
        else:
            print(f"✅ Memoria OK: {memory_mb:.2f} MB")
            
    except Exception as e:
        print(f"❌ Errore monitorando connessioni: {e}")

if __name__ == "__main__":
    print("🔍 MONITOR CONNESSIONI E RISORSE")
    print("=" * 40)
    
    # 1. Info sistema
    get_system_info()
    
    # 2. Info database
    get_database_info()
    
    # 3. Verifica file descriptors
    check_file_descriptors()
    
    # 4. Monitora connessioni
    monitor_connections()
    
    # 5. Cleanup (opzionale)
    print("\n" + "=" * 40)
    response = input("🧹 Eseguire cleanup risorse? (y/N): ").strip().lower()
    if response == 'y':
        cleanup_resources()
    
    print("\n🎯 Monitor completato!")
