import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Caricamento dati
st.title("Dashboard Comparativa Fatturato e Quantità")

file_path = "file_comparativo.xlsx"
if not os.path.exists(file_path):
    st.error("Il file dati.xlsx non è stato trovato. Assicurati che sia nella cartella del progetto.")
    st.stop()  # Interrompe l'esecuzione dello script se il file non è presente

# Carica il file Excel
df = pd.read_excel(file_path)

# Dizionario per ordinare i mesi
month_map = {
    'Gennaio': 1, 'Febbraio': 2, 'Marzo': 3, 'Aprile': 4, 'Maggio': 5, 'Giugno': 6,
    'Luglio': 7, 'Agosto': 8, 'Settembre': 9, 'Ottobre': 10, 'Novembre': 11, 'Dicembre': 12
}

# Crea una colonna numerica per ordinare i mesi
df['MESE_NUM'] = df['MESE'].map(month_map)

# Selezione multipla di clienti
clienti = df['CLIENTE'].unique()
clienti_selezionati = st.multiselect("Seleziona uno o più clienti", clienti, default=clienti[:22])


# Selezione multipla di mesi per grafici per cliente
mesi = df['MESE'].unique()
mesi_selezionati = st.multiselect("Seleziona uno o più mesi per i grafici dei clienti", mesi, default=mesi)

# Filtro per clienti e mesi
df_filtrato = df[(df['CLIENTE'].isin(clienti_selezionati)) & (df['MESE'].isin(mesi_selezionati))]

# Ordinare i dati per mese numerico
df_filtrato = df_filtrato.sort_values(by='MESE_NUM')

# Grafico Fatturato con confronto tra anni
df_fatturato_melted = df_filtrato.melt(id_vars=['MESE', 'CLIENTE'],
                                       value_vars=['FATTURATO_2024', 'FATTURATO_2025'],
                                       var_name='Anno', value_name='Fatturato')

fig_fatturato = px.bar(df_fatturato_melted, x='MESE', y='Fatturato', color='Anno',
                       barmode='group', facet_col='CLIENTE', title="Confronto Fatturato per Clienti",
                       category_orders={"MESE": list(month_map.keys())})
st.plotly_chart(fig_fatturato)

# Grafico Quantità con confronto tra anni
df_quantita_melted = df_filtrato.melt(id_vars=['MESE', 'CLIENTE'],
                                      value_vars=['QUANTITA_2024', 'QUANTITA_2025'],
                                      var_name='Anno', value_name='Quantità')

fig_quantita = px.bar(df_quantita_melted, x='MESE', y='Quantità', color='Anno',
                      barmode='group', facet_col='CLIENTE', title="Confronto Quantità per Clienti",
                      category_orders={"MESE": list(month_map.keys())})
st.plotly_chart(fig_quantita)

# Tabella variazioni
st.dataframe(df_filtrato[['MESE', 'CLIENTE', 'VARIAZIONE_%_FATT', 'VARIAZIONE_%_QTA']])

# Sezione andamento complessivo
st.subheader("Andamento Complessivo")

# Aggiungi la selezione dei mesi per i grafici totali
mesi_selezionati_totali = st.multiselect("Seleziona uno o più mesi per i grafici complessivi", mesi, default=mesi)

# Filtra il dataframe per i mesi selezionati nei grafici totali
df_totale = df[df['MESE'].isin(mesi_selezionati_totali)].groupby('MESE')[
    ['FATTURATO_2024', 'FATTURATO_2025', 'QUANTITA_2024', 'QUANTITA_2025']].sum().reset_index()

# Ordinare i dati per mese numerico
df_totale['MESE'] = pd.Categorical(df_totale['MESE'], categories=month_map.keys(), ordered=True)
df_totale = df_totale.sort_values(by='MESE')

# Grafico andamento fatturato totale
df_tot_fatturato_melted = df_totale.melt(id_vars=['MESE'],
                                         value_vars=['FATTURATO_2024', 'FATTURATO_2025'],
                                         var_name='Anno', value_name='Fatturato')

fig_tot_fatturato = px.line(df_tot_fatturato_melted, x='MESE', y='Fatturato', color='Anno',
                            title="Andamento Complessivo del Fatturato",
                            category_orders={"MESE": list(month_map.keys())})
st.plotly_chart(fig_tot_fatturato)

# Grafico andamento quantità totale
df_tot_quantita_melted = df_totale.melt(id_vars=['MESE'],
                                        value_vars=['QUANTITA_2024', 'QUANTITA_2025'],
                                        var_name='Anno', value_name='Quantità')

fig_tot_quantita = px.line(df_tot_quantita_melted, x='MESE', y='Quantità', color='Anno',
                           title="Andamento Complessivo della Quantità",
                           category_orders={"MESE": list(month_map.keys())})
st.plotly_chart(fig_tot_quantita)

# Nuova sezione: Tabella con i 5 clienti con maggiore variazione positiva
st.subheader("Top 5 Clienti con Maggiore Variazione Fatturato 2024-2025")

# Selezione mesi per la variazione
mesi_selezionati_variazione = st.multiselect("Seleziona i mesi per la variazione", mesi, default=mesi)

# Filtro per i mesi selezionati
df_variazione = df[df['MESE'].isin(mesi_selezionati_variazione)].copy()

# Calcolare la variazione di fatturato in percentuale (con controllo per valori nulli o divisione per zero)
df_variazione['Variazione_Fatt'] = ((df_variazione['FATTURATO_2025'] - df_variazione['FATTURATO_2024']) /
                                    df_variazione['FATTURATO_2024'].replace(0, pd.NA)) * 100

# Raggruppare per cliente e calcolare la variazione media per cliente
df_top_clienti = df_variazione.groupby('CLIENTE', as_index=False)['Variazione_Fatt'].mean()

# Ordinare per variazione decrescente e selezionare i top 5
df_top_clienti = df_top_clienti.sort_values(by='Variazione_Fatt', ascending=False).head(5)

# Mostrare la tabella
st.dataframe(df_top_clienti)

# Nuova sezione: Tabella con i 5 clienti con maggiore variazione negativa
st.subheader("Top 5 Clienti con Maggiore Variazione Negativa Fatturato 2024-2025")

# Ordinare per variazione crescente (cambio di segno)
df_clienti_negativi = df_variazione.groupby('CLIENTE', as_index=False)['Variazione_Fatt'].mean()
df_clienti_negativi = df_clienti_negativi.sort_values(by='Variazione_Fatt', ascending=True).head(5)

# Mostrare la tabella
st.dataframe(df_clienti_negativi)
