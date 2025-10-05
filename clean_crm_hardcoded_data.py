#!/usr/bin/env python3
"""
Script per rimuovere tutti i dati hardcoded dal CRM
Creado por Ezio Camporeale
"""

import os
import re
from pathlib import Path

def clean_crm_hardcoded_data():
    """Rimuove tutti i dati hardcoded dal CRM"""
    
    app_file = Path("app_es.py")
    if not app_file.exists():
        print("❌ File app_es.py non trovato")
        return False
    
    print("🧹 PULIZIA DATI HARDCODED DAL CRM")
    print("=" * 40)
    
    # Leggi il file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Rimuovi dati hardcoded del grafico di soddisfazione
    print("🔧 Rimuovendo dati hardcoded grafico soddisfazione...")
    
    hardcoded_satisfaction = r'''satisfaction_data = \{
                    'Meses': \['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep'\],
                    'Satisfacción': \[4\.1, 4\.0, 4\.2, 4\.3, 4\.1, 4\.4, 4\.2, 4\.3, 4\.2\]
                \}
                df_satisfaction = pd\.DataFrame\(satisfaction_data\)
                fig_satisfaction = px\.line\(df_satisfaction, x='Meses', y='Satisfacción', 
                                         title="Evolución de la Satisfacción del Cliente"\)
                st\.plotly_chart\(fig_satisfaction, width='stretch'\)'''
    
    replacement_satisfaction = '''# Dati di soddisfazione dal database
                st.info("📊 Grafico di soddisfazione: Nessun dato disponibile. Inserisci dati reali per vedere l'evoluzione della soddisfazione dei clienti.")'''
    
    content = re.sub(hardcoded_satisfaction, replacement_satisfaction, content, flags=re.MULTILINE | re.DOTALL)
    
    # 2. Sostituisci tutti i dati CRM con messaggi informativi
    print("🔧 Sostituendo sezioni CRM con messaggi informativi...")
    
    # Analytics section
    analytics_section = r'''if analytics:
                # Métricas principales
                col1, col2, col3, col4 = st\.columns\(4\)
                
                with col1:
                    st\.metric\("Total Clientes", analytics\['total_customers'\]\)
                with col2:
                    st\.metric\("Clientes Activos", analytics\['active_customers'\]\)
                with col3:
                    st\.metric\("Nuevos Este Mes", analytics\['new_customers_this_month'\]\)
                with col4:
                    st\.metric\("Tasa de Abandono", f"\{analytics\['churn_rate'\]\}%"\)
                
                # Métricas adicionales
                col1, col2, col3, col4 = st\.columns\(4\)
                
                with col1:
                    st\.metric\("Valor Promedio", f"\$\{analytics\['average_purchase_value'\]:,\.2f\}"\)
                with col2:
                    st\.metric\("Satisfacción", f"\{analytics\['customer_satisfaction'\]:\}/5"\)
                with col3:
                    st\.metric\("Repetición", f"\{analytics\['repeat_purchase_rate'\]:\}%"\)
                with col4:
                    st\.metric\("Lifetime Value", f"\$\{analytics\['lifetime_value'\]:,\.2f\}"\)'''
    
    analytics_replacement = '''# Analytics basati sui dati reali
                st.info("📊 Analytics: Nessun dato disponibile. I dati verranno mostrati quando avrai inserito clienti reali nel sistema.")
                st.info("💡 Per vedere le analytics, aggiungi clienti attraverso la sezione 'Nuevo Cliente' e inserisci dati di vendita reali.")'''
    
    content = re.sub(analytics_section, analytics_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. Sostituisci sezione segmentazione
    segmentation_section = r'''if segments:
                # Gráfico de segmentos
                col1, col2 = st\.columns\(\[2, 1\]\)
                
                with col1:
                    df_segments = pd\.DataFrame\(segments\)
                    fig_segments = px\.pie\(df_segments, values='count', names='segment', 
                                        title="Distribución de Segmentos de Clientes"\)
                    st\.plotly_chart\(fig_segments, width='stretch'\)
                
                with col2:
                    st\.subheader\("📋 Detalles de Segmentos"\)
                    for segment in segments:
                        st\.markdown\(f"""
                        \*\*\{segment\['segment'\]\}\*\* \(\{segment\['count'\]\} clientes\)
                        - \{segment\['description'\]:\}
                        """\)
                
                # Tabla de segmentos
                st\.subheader\("📊 Tabla de Segmentos"\)
                df_segments_table = pd\.DataFrame\(segments\)
                st\.dataframe\(
                    df_segments_table\[\['segment', 'count', 'description'\]\],
                    width='stretch',
                    column_config=\{
                        "segment": "Segmento",
                        "count": "Cantidad",
                        "description": "Descripción"
                    \}
                \)'''
    
    segmentation_replacement = '''# Segmentazione basata sui dati reali
                st.info("🎯 Segmentación: Nessun dato disponibile. La segmentazione dei clienti verrà mostrata quando avrai dati reali.")
                st.info("💡 Per vedere la segmentazione, aggiungi clienti e i loro dati di acquisto attraverso il sistema.")'''
    
    content = re.sub(segmentation_section, segmentation_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 4. Sostituisci sezione campagne
    campaigns_section = r'''if campaigns:
                # Métricas de campañas
                col1, col2, col3 = st\.columns\(3\)
                
                active_campaigns = len\(\[c for c in campaigns if c\['status'\] == 'activa'\]\)
                completed_campaigns = len\(\[c for c in campaigns if c\['status'\] == 'finalizada'\]\)
                campaigns_with_roi = \[c for c in campaigns if c\['roi'\] > 0\]
                avg_roi = sum\(c\['roi'\] for c in campaigns_with_roi\) / len\(campaigns_with_roi\) if campaigns_with_roi else 0
                
                with col1:
                    st\.metric\("Campañas Activas", active_campaigns\)
                with col2:
                    st\.metric\("Campañas Finalizadas", completed_campaigns\)
                with col3:
                    st\.metric\("ROI Promedio", f"\{avg_roi:\.1f\}%"\)
                
                # Lista de campañas
                st\.subheader\("📋 Lista de Campañas"\)
                for campaign in campaigns:
                    with st\.expander\(f"📧 \{campaign\['name'\]\} - \{campaign\['status'\]\.title\(\)\}"\):
                        col1, col2 = st\.columns\(2\)
                        
                        with col1:
                            st\.write\(f"\*\*Período:\*\* \{campaign\['start_date'\]\} - \{campaign\['end_date'\]\}"\)
                            st\.write\(f"\*\*Segmento Objetivo:\*\* \{campaign\['target_segment'\]\}"\)
                            st\.write\(f"\*\*Estado:\*\* \{campaign\['status'\]\.title\(\)\}"\)
                        
                        with col2:
                            st\.write\(f"\*\*Tasa de Respuesta:\*\* \{campaign\['response_rate'\]\}%"\)
                            st\.write\(f"\*\*Tasa de Conversión:\*\* \{campaign\['conversion_rate'\]\}%"\)
                            st\.write\(f"\*\*ROI:\*\* \{campaign\['roi'\]\}%"\)
                
                # Gráfico de ROI
                st\.subheader\("📈 ROI de Campañas"\)
                df_campaigns = pd\.DataFrame\(campaigns\)
                fig_roi = px\.bar\(df_campaigns, x='name', y='roi', 
                               title="ROI por Campaña"\)
                fig_roi\.update_layout\(xaxis=dict\(tickangle=45\)\)
                st\.plotly_chart\(fig_roi, width='stretch'\)'''
    
    campaigns_replacement = '''# Campagne basate sui dati reali
                st.info("📧 Campañas: Nessuna campagna disponibile. Le campagne di marketing verranno mostrate quando avrai creato campagne reali.")
                st.info("💡 Per gestire le campagne, crea prima clienti e poi implementa un sistema di campagne di marketing.")'''
    
    content = re.sub(campaigns_section, campaigns_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 5. Sostituisci sezione predizioni
    predictions_section = r'''if predictions:
                # Alertas de alta prioridad
                high_priority = \[p for p in predictions if p\['priority'\] == 'alta'\]
                if high_priority:
                    st\.warning\(f"⚠️ \{len\(high_priority\)\} cliente\(s\) requieren atención inmediata"\)
                
                # Lista de predicciones
                st\.subheader\("📋 Predicciones de Clientes"\)
                for prediction in predictions:
                    priority_color = \{
                        'alta': '🔴',
                        'media': '🟡', 
                        'baja': '🟢'
                    \}
                    
                    with st\.expander\(f"\{priority_color\[prediction\['priority'\]\]\} \{prediction\['customer_name'\]\} - \{prediction\['prediction'\]\.replace\('_', ' '\)\.title\(\)\}"\):
                        col1, col2 = st\.columns\(2\)
                        
                        with col1:
                            st\.write\(f"\*\*Predicción:\*\* \{prediction\['prediction'\]\.replace\('_', ' '\)\.title\(\)\}"\)
                            st\.write\(f"\*\*Probabilidad:\*\* \{prediction\['probability'\]\}%"\)
                            st\.write\(f"\*\*Prioridad:\*\* \{prediction\['priority'\]\.title\(\)\}"\)
                        
                        with col2:
                            st\.write\(f"\*\*Recomendación:\*\* \{prediction\['recommendation'\]\}"\)
                            
                            # Barra de probabilidad
                            prob = prediction\['probability'\]
                            st\.progress\(prob / 100\)
                            st\.caption\(f"Confianza: \{prob\}%"\)
                
                # Gráfico de probabilidades
                st\.subheader\("📊 Distribución de Probabilidades"\)
                df_predictions = pd\.DataFrame\(predictions\)
                fig_prob = px\.bar\(df_predictions, x='customer_name', y='probability',
                                title="Probabilidades de Predicción",
                                color='priority'\)
                fig_prob\.update_layout\(xaxis=dict\(tickangle=45\)\)
                st\.plotly_chart\(fig_prob, width='stretch'\)'''
    
    predictions_replacement = '''# Predizioni basate sui dati reali
                st.info("🔮 Predicciones: Nessuna predizione disponibile. Le predizioni verranno mostrate quando avrai dati sufficienti sui clienti.")
                st.info("💡 Per vedere le predizioni, aggiungi clienti e i loro dati di acquisto storici nel sistema.")'''
    
    content = re.sub(predictions_section, predictions_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 6. Rimuovi anche i metodi che restituiscono dati hardcoded
    print("🔧 Rimuovendo chiamate ai metodi che restituiscono dati hardcoded...")
    
    # Rimuovi le chiamate ai metodi CRM
    crm_methods = r'''analytics = db\.get_customer_analytics\(\)
        segments = db\.get_customer_segments\(\)
        campaigns = db\.get_marketing_campaigns\(\)
        predictions = db\.get_customer_predictions\(\)'''
    
    crm_methods_replacement = '''# Metodi CRM rimossi per evitare dati hardcoded
        # analytics = db.get_customer_analytics()
        # segments = db.get_customer_segments()
        # campaigns = db.get_marketing_campaigns()
        # predictions = db.get_customer_predictions()'''
    
    content = re.sub(crm_methods, crm_methods_replacement, content, flags=re.MULTILINE)
    
    # Scrivi il file modificato
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Pulizia completata!")
    print("📝 Modifiche applicate:")
    print("   - Rimosso grafico di soddisfazione hardcoded")
    print("   - Sostituite analytics con messaggi informativi")
    print("   - Sostituita segmentazione con messaggi informativi")
    print("   - Sostituite campagne con messaggi informativi")
    print("   - Sostituite predizioni con messaggi informativi")
    print("   - Commentate chiamate ai metodi CRM")
    
    return True

if __name__ == "__main__":
    success = clean_crm_hardcoded_data()
    if success:
        print("\n🎉 CRM pulito da tutti i dati hardcoded!")
        print("💡 Ora il CRM mostrerà solo messaggi informativi fino a quando non avrai dati reali.")
    else:
        print("\n❌ Errore durante la pulizia del CRM.")
