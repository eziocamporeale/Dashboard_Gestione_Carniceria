#!/bin/bash
# Script de inicio rápido para Dashboard Gestión Carnicería
# Creado por Ezio Camporeale
# Traducido al español para Argentina

echo "🥩 Dashboard Gestión Carnicería - Inicio Rápido"
echo "================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instala Python 3.8+ antes de continuar."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verificar Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Instalando dependencias..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias"
        exit 1
    fi
    echo "✅ Dependencias instaladas"
else
    echo "✅ Streamlit ya instalado"
fi

# Verificar base de datos
if [ ! -f "data/carniceria.db" ]; then
    echo "🗄️ Inicializando base de datos..."
    python3 database/init_database_es.py
    if [ $? -ne 0 ]; then
        echo "❌ Error inicializando base de datos"
        exit 1
    fi
    echo "✅ Base de datos inicializada"
else
    echo "✅ Base de datos ya existe"
fi

# Test sistema
echo "🧪 Probando sistema..."
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from app_es import main
print('✅ App importada correctamente')
" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Sistema probado y funcionando"
else
    echo "⚠️ Algunos tests fallaron, pero el sistema debería funcionar"
fi

echo ""
echo "🚀 Iniciando aplicación..."
echo "📱 La aplicación estará disponible en: http://localhost:8501"
echo "🔐 Credenciales por defecto: admin / admin123"
echo ""

# Iniciar Streamlit
streamlit run app_es.py --server.port 8501 --server.headless true
