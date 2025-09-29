#!/usr/bin/env python3
"""
Funzioni Helper per Dashboard Gestione Macelleria
Utility e funzioni di supporto
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
import json
import re

def format_currency(amount: float, currency: str = "EUR") -> str:
    """
    Formatta un importo come valuta
    
    Args:
        amount: Importo da formattare
        currency: Codice valuta (default: EUR)
        
    Returns:
        String formattata
    """
    if currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_date(date_obj: Union[date, datetime, str], format_str: str = "%d/%m/%Y") -> str:
    """
    Formatta una data
    
    Args:
        date_obj: Oggetto data da formattare
        format_str: Formato di output
        
    Returns:
        String formattata
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except:
            return date_obj
    
    if isinstance(date_obj, (date, datetime)):
        return date_obj.strftime(format_str)
    
    return str(date_obj)

def format_datetime(datetime_obj: Union[datetime, str], format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formatta una data e ora
    
    Args:
        datetime_obj: Oggetto datetime da formattare
        format_str: Formato di output
        
    Returns:
        String formattata
    """
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj)
        except:
            return datetime_obj
    
    if isinstance(datetime_obj, datetime):
        return datetime_obj.strftime(format_str)
    
    return str(datetime_obj)

def calculate_age(birth_date: Union[date, str]) -> Optional[int]:
    """
    Calcola l'età da una data di nascita
    
    Args:
        birth_date: Data di nascita
        
    Returns:
        Età in anni o None se errore
    """
    try:
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date).date()
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def validate_email(email: str) -> bool:
    """
    Valida un indirizzo email
    
    Args:
        email: Indirizzo email da validare
        
    Returns:
        True se valido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Valida un numero di telefono
    
    Args:
        phone: Numero di telefono da validare
        
    Returns:
        True se valido
    """
    # Rimuovi spazi e caratteri speciali
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Pattern per numeri italiani e internazionali
    patterns = [
        r'^\+39\d{10}$',  # +39 + 10 cifre
        r'^39\d{10}$',    # 39 + 10 cifre
        r'^0\d{9,10}$',   # 0 + 9-10 cifre
        r'^\d{10}$'       # 10 cifre
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_vat_number(vat_number: str) -> bool:
    """
    Valida una partita IVA italiana
    
    Args:
        vat_number: Partita IVA da validare
        
    Returns:
        True se valida
    """
    # Rimuovi spazi
    vat_number = vat_number.replace(' ', '')
    
    # Deve essere lunga 11 cifre
    if len(vat_number) != 11 or not vat_number.isdigit():
        return False
    
    # Algoritmo di controllo partita IVA italiana
    multipliers = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    
    for i in range(10):
        product = int(vat_number[i]) * multipliers[i]
        if product > 9:
            product = product // 10 + product % 10
        total += product
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(vat_number[10])

def generate_code(prefix: str, length: int = 6) -> str:
    """
    Genera un codice univoco
    
    Args:
        prefix: Prefisso del codice
        length: Lunghezza della parte numerica
        
    Returns:
        Codice generato
    """
    import random
    import string
    
    # Genera parte numerica casuale
    numeric_part = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}{numeric_part}"

def clean_text(text: str) -> str:
    """
    Pulisce un testo rimuovendo caratteri speciali
    
    Args:
        text: Testo da pulire
        
    Returns:
        Testo pulito
    """
    if not text:
        return ""
    
    # Rimuovi caratteri di controllo e spazi extra
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Rimuovi caratteri non stampabili
    text = ''.join(char for char in text if char.isprintable())
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Tronca un testo alla lunghezza specificata
    
    Args:
        text: Testo da troncare
        max_length: Lunghezza massima
        suffix: Suffisso da aggiungere
        
    Returns:
        Testo troncato
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_json_safe(json_str: str, default: Any = None) -> Any:
    """
    Parsa una stringa JSON in modo sicuro
    
    Args:
        json_str: Stringa JSON da parsare
        default: Valore di default se errore
        
    Returns:
        Oggetto parsato o default
    """
    try:
        return json.loads(json_str) if json_str else default
    except:
        return default

def to_json_safe(obj: Any, default: str = "{}") -> str:
    """
    Converte un oggetto in JSON in modo sicuro
    
    Args:
        obj: Oggetto da convertire
        default: Valore di default se errore
        
    Returns:
        Stringa JSON o default
    """
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except:
        return default

def get_date_range_options() -> Dict[str, Dict[str, date]]:
    """
    Ottiene le opzioni di range di date predefinite
    
    Returns:
        Dict con opzioni di date
    """
    today = date.today()
    
    return {
        "Oggi": {"start": today, "end": today},
        "Ieri": {"start": today - timedelta(days=1), "end": today - timedelta(days=1)},
        "Ultimi 7 giorni": {"start": today - timedelta(days=7), "end": today},
        "Ultimi 30 giorni": {"start": today - timedelta(days=30), "end": today},
        "Questo mese": {"start": today.replace(day=1), "end": today},
        "Mese scorso": {
            "start": (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            "end": today.replace(day=1) - timedelta(days=1)
        },
        "Questo anno": {"start": today.replace(month=1, day=1), "end": today},
        "Anno scorso": {
            "start": today.replace(year=today.year-1, month=1, day=1),
            "end": today.replace(year=today.year-1, month=12, day=31)
        }
    }

def render_date_range_selector(key: str = "date_range") -> Dict[str, date]:
    """
    Renderizza un selettore di range di date
    
    Args:
        key: Chiave per Streamlit
        
    Returns:
        Dict con start_date e end_date
    """
    options = get_date_range_options()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_option = st.selectbox(
            "Periodo",
            list(options.keys()),
            key=f"{key}_option"
        )
    
    with col2:
        custom_range = st.checkbox("Range personalizzato", key=f"{key}_custom")
    
    if custom_range:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data inizio", key=f"{key}_start")
        with col2:
            end_date = st.date_input("Data fine", key=f"{key}_end")
        
        return {"start": start_date, "end": end_date}
    else:
        return options[selected_option]

def render_status_badge(status: str, status_config: Dict[str, Dict[str, str]] = None) -> str:
    """
    Renderizza un badge di stato
    
    Args:
        status: Stato da visualizzare
        status_config: Configurazione stati
        
    Returns:
        HTML del badge
    """
    if not status_config:
        status_config = {
            "attivo": {"color": "#28a745", "icon": "✅"},
            "inattivo": {"color": "#dc3545", "icon": "❌"},
            "nuovo": {"color": "#007bff", "icon": "🆕"},
            "in_preparazione": {"color": "#ffc107", "icon": "⏳"},
            "pronto": {"color": "#28a745", "icon": "✅"},
            "consegnato": {"color": "#6c757d", "icon": "📦"},
            "annullato": {"color": "#dc3545", "icon": "❌"},
            "pending": {"color": "#ffc107", "icon": "⏳"},
            "paid": {"color": "#28a745", "icon": "💰"},
            "overdue": {"color": "#dc3545", "icon": "⚠️"}
        }
    
    config = status_config.get(status.lower(), {"color": "#6c757d", "icon": "❓"})
    
    return f"""
    <span style="
        background-color: {config['color']};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    ">
        {config['icon']} {status.title()}
    </span>
    """

def render_metric_card(title: str, value: Any, delta: str = None, icon: str = "📊") -> str:
    """
    Renderizza una card metrica
    
    Args:
        title: Titolo della metrica
        value: Valore della metrica
        delta: Valore delta (opzionale)
        icon: Icona (opzionale)
        
    Returns:
        HTML della card
    """
    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size: 0.875rem; color: #6c757d; margin-top: 0.25rem;">{delta}</div>'
    
    return f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B35;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <h3 style="margin: 0; color: #333; font-size: 0.875rem; font-weight: 500;">{title}</h3>
        </div>
        <div style="font-size: 2rem; font-weight: bold; color: #FF6B35; margin-bottom: 0.25rem;">{value}</div>
        {delta_html}
    </div>
    """

def export_dataframe_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Esporta un DataFrame in Excel
    
    Args:
        df: DataFrame da esportare
        filename: Nome file (opzionale)
        
    Returns:
        Bytes del file Excel
    """
    import io
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.xlsx"
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Dati"
    
    # Aggiungi dati
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    
    # Salva in bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output.getvalue()

def export_dataframe_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    """
    Esporta un DataFrame in CSV
    
    Args:
        df: DataFrame da esportare
        filename: Nome file (opzionale)
        
    Returns:
        Stringa CSV
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.csv"
    
    return df.to_csv(index=False, encoding='utf-8')

def render_download_buttons(df: pd.DataFrame, filename_prefix: str = "export"):
    """
    Renderizza i pulsanti di download per un DataFrame
    
    Args:
        df: DataFrame da esportare
        filename_prefix: Prefisso del nome file
    """
    if df.empty:
        st.warning("Nessun dato da esportare")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download Excel
        excel_data = export_dataframe_to_excel(df, f"{filename_prefix}.xlsx")
        st.download_button(
            label="📊 Scarica Excel",
            data=excel_data,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Download CSV
        csv_data = export_dataframe_to_csv(df, f"{filename_prefix}.csv")
        st.download_button(
            label="📄 Scarica CSV",
            data=csv_data,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True
        )

def show_success_message(message: str, icon: str = "✅"):
    """
    Mostra un messaggio di successo
    
    Args:
        message: Messaggio da mostrare
        icon: Icona (opzionale)
    """
    st.success(f"{icon} {message}")

def show_error_message(message: str, icon: str = "❌"):
    """
    Mostra un messaggio di errore
    
    Args:
        message: Messaggio da mostrare
        icon: Icona (opzionale)
    """
    st.error(f"{icon} {message}")

def show_warning_message(message: str, icon: str = "⚠️"):
    """
    Mostra un messaggio di avviso
    
    Args:
        message: Messaggio da mostrare
        icon: Icona (opzionale)
    """
    st.warning(f"{icon} {message}")

def show_info_message(message: str, icon: str = "ℹ️"):
    """
    Mostra un messaggio informativo
    
    Args:
        message: Messaggio da mostrare
        icon: Icona (opzionale)
    """
    st.info(f"{icon} {message}")

def render_loading_spinner(message: str = "Caricamento..."):
    """
    Renderizza uno spinner di caricamento
    
    Args:
        message: Messaggio da mostrare
    """
    return st.spinner(message)

def clear_cache():
    """
    Pulisce la cache di Streamlit
    """
    st.cache_data.clear()
    st.cache_resource.clear()

def get_client_info() -> Dict[str, str]:
    """
    Ottiene informazioni sul client (limitato in Streamlit)
    
    Returns:
        Dict con informazioni client
    """
    return {
        "user_agent": "Streamlit App",
        "ip_address": "127.0.0.1",  # Localhost per sviluppo
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test delle funzioni helper
    print("🧪 Test Funzioni Helper")
    
    # Test formattazione
    print(f"💰 Valuta: {format_currency(1234.56)}")
    print(f"📅 Data: {format_date(date.today())}")
    print(f"📅 Data/Ora: {format_datetime(datetime.now())}")
    
    # Test validazione
    print(f"📧 Email valida: {validate_email('test@example.com')}")
    print(f"📞 Telefono valido: {validate_phone('+39 333 1234567')}")
    print(f"🏢 P.IVA valida: {validate_vat_number('12345678901')}")
    
    # Test generazione codice
    print(f"🔢 Codice generato: {generate_code('PROD', 4)}")
    
    # Test pulizia testo
    print(f"🧹 Testo pulito: '{clean_text('  Testo   con   spazi  ')}'")
    
    print("✅ Test completato")

