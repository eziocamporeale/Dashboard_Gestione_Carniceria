#!/usr/bin/env python3
"""
Script per creare le tabelle di contabilità giornaliera in Supabase
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.hybrid_database_manager import get_hybrid_manager

def setup_accounting_tables():
    """Crea las tablas de contabilidad diaria"""
    
    print("🏗️ Configurando tablas de contabilidad diaria...")
    
    db = get_hybrid_manager()
    
    # Categorías predefinidas para ingresos
    income_categories = [
        {'name': 'Ventas Carnes', 'type': 'income', 'color': '#00CC96', 'icon': '🥩'},
        {'name': 'Ventas Embutidos', 'type': 'income', 'color': '#00CC96', 'icon': '🌭'},
        {'name': 'Ventas Pollo', 'type': 'income', 'color': '#00CC96', 'icon': '🐔'},
        {'name': 'Ventas Varios', 'type': 'income', 'color': '#00CC96', 'icon': '🛒'},
        {'name': 'Otros Ingresos', 'type': 'income', 'color': '#00CC96', 'icon': '💰'},
    ]
    
    # Categorías predefinidas para gastos
    expense_categories = [
        {'name': 'Compra Carnes', 'type': 'expense', 'color': '#FF6692', 'icon': '🥩'},
        {'name': 'Compra Embutidos', 'type': 'expense', 'color': '#FF6692', 'icon': '🌭'},
        {'name': 'Compra Pollo', 'type': 'expense', 'color': '#FF6692', 'icon': '🐔'},
        {'name': 'Gastos Operativos', 'type': 'expense', 'color': '#FF6692', 'icon': '⚙️'},
        {'name': 'Servicios Públicos', 'type': 'expense', 'color': '#FF6692', 'icon': '💡'},
        {'name': 'Alquiler', 'type': 'expense', 'color': '#FF6692', 'icon': '🏠'},
        {'name': 'Sueldos', 'type': 'expense', 'color': '#FF6692', 'icon': '👥'},
        {'name': 'Otros Gastos', 'type': 'expense', 'color': '#FF6692', 'icon': '💸'},
    ]
    
    # Intenta crear las categorías
    print("📝 Creando categorías predefinidas...")
    
    all_categories = income_categories + expense_categories
    
    for category in all_categories:
        try:
            result = db.add_accounting_category(
                name=category['name'],
                category_type=category['type'],
                color=category['color'],
                icon=category['icon']
            )
            if result:
                print(f"   ✅ Categoría creada: {category['icon']} {category['name']}")
            else:
                print(f"   ⚠️ Categoría ya existe: {category['icon']} {category['name']}")
        except Exception as e:
            print(f"   ❌ Error creando categoría {category['name']}: {e}")
    
    # Verifica que las categorías hayan sido creadas
    print("🔍 Verificando categorías creadas...")
    
    try:
        income_cats = db.get_accounting_categories('income')
        expense_cats = db.get_accounting_categories('expense')
        
        print(f"   📊 Categorías ingresos: {len(income_cats)}")
        print(f"   📊 Categorías gastos: {len(expense_cats)}")
        
        if income_cats:
            print("   💰 Categorías ingresos:")
            for cat in income_cats:
                print(f"      - {cat['icon']} {cat['name']}")
        
        if expense_cats:
            print("   💸 Categorías gastos:")
            for cat in expense_cats:
                print(f"      - {cat['icon']} {cat['name']}")
        
        print("✅ Configuración completada!")
        
    except Exception as e:
        print(f"❌ Error verificando categorías: {e}")

if __name__ == "__main__":
    setup_accounting_tables()
