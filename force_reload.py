#!/usr/bin/env python3
"""
Script per forzare il ricaricamento dell'app su Streamlit Cloud
Creado por Ezio Camporeale
"""

import streamlit as st
import time
from datetime import datetime

# Forza il ricaricamento dell'app
st.set_page_config(
    page_title="Dashboard Gestión Carnicería - RELOAD",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 FORZANDO RICARICAMENTO APP")
st.markdown("---")

# Mostra timestamp per verificare il ricaricamento
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.info(f"⏰ Timestamp: {current_time}")

# Verifica che le modifiche siano state applicate
st.subheader("🔍 VERIFICA MODIFICHE APPLICATE")

try:
    from database.hybrid_database_manager import get_hybrid_manager
    db = get_hybrid_manager()
    
    # Verifica se il metodo get_weekly_summary esiste
    if hasattr(db, 'get_weekly_summary'):
        st.success("✅ Metodo get_weekly_summary() trovato!")
        
        # Test del metodo
        from datetime import datetime, timedelta
        week_start = datetime.now().date() - timedelta(days=7)
        
        try:
            weekly_data = db.get_weekly_summary(week_start.isoformat())
            if weekly_data:
                total_expenses = sum([d.get('total_expenses', 0) for d in weekly_data])
                st.success(f"✅ Metodo funziona! Uscite settimanali: ${total_expenses:,.2f}")
                
                if abs(total_expenses - 8498.42) < 0.01:
                    st.error("❌ La transazione di $8,498.42 è ancora presente!")
                else:
                    st.success("✅ La transazione di $8,498.42 è stata rimossa!")
            else:
                st.warning("⚠️ Nessun dato settimanale restituito")
        except Exception as e:
            st.error(f"❌ Errore testando metodo: {e}")
    else:
        st.error("❌ Metodo get_weekly_summary() NON trovato!")
        
except Exception as e:
    st.error(f"❌ Errore importando database manager: {e}")

# Pulsante per forzare ricaricamento
if st.button("🔄 FORZA RICARICAMENTO COMPLETO", type="primary"):
    st.rerun()

st.markdown("---")
st.info("💡 Se la transazione di $8,498.42 è ancora presente, significa che Streamlit Cloud non ha ancora caricato le modifiche più recenti.")
