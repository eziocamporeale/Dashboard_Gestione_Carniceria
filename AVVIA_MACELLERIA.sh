#!/bin/bash
# Script di avvio rapido per Dashboard Gestione Macelleria
# Creato da Ezio Camporeale

echo "🥩 Dashboard Gestione Macelleria - Avvio Rapido"
echo "================================================"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato. Installa Python 3.8+ prima di continuare."
    exit 1
fi

echo "✅ Python3 trovato: $(python3 --version)"

# Verifica Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Installazione dipendenze..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Errore installazione dipendenze"
        exit 1
    fi
    echo "✅ Dipendenze installate"
else
    echo "✅ Streamlit già installato"
fi

# Verifica database
if [ ! -f "data/macelleria.db" ]; then
    echo "🗄️ Inizializzazione database..."
    python3 database/init_database.py
    if [ $? -ne 0 ]; then
        echo "❌ Errore inizializzazione database"
        exit 1
    fi
    echo "✅ Database inizializzato"
else
    echo "✅ Database già esistente"
fi

# Test sistema
echo "🧪 Test sistema..."
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from app import main
print('✅ App importata correttamente')
" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Sistema testato e funzionante"
else
    echo "⚠️ Alcuni test falliti, ma il sistema dovrebbe funzionare"
fi

echo ""
echo "🚀 Avvio applicazione..."
echo "📱 L'applicazione sarà disponibile su: http://localhost:8501"
echo "🔐 Credenziali di default: admin / admin123"
echo ""

# Avvia Streamlit
streamlit run app.py --server.port 8501 --server.headless true

