import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import locale

# Configuration initiale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# CSS personnalisé
st.markdown("""
    <style>
    .card-container {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    .title {
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 20px;
        color: #333;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        flex: 1;
    }
    .metric {
        font-size: 2rem;
        font-weight: bold;
    }
    .delta {
        font-size: 1.2rem;
        margin-top: 5px;
    }
    .label {
        font-size: 1rem;
        color: #555;
    }
    .positive {
        color: green;
    }
    .negative {
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour déterminer la classe CSS de la flèche
def get_delta_class(delta):
    return "positive" if delta >= 0 else "negative"

# Fonction pour charger et traiter les données de formation
def load_and_process_formation_data(fichier):
    if not fichier:
        st.info("Veuillez importer un fichier Excel contenant la feuille 'Formations 2025'.")
        return None, 0

    try:
        df_formations = pd.read_excel(fichier, sheet_name="Formations 2025", header=2)
        
        # Vérification des colonnes requises
        required_columns = ["Date de début", "Nombre de jour"]
        if not all(col in df_formations.columns for col in required_columns):
            st.error("❌ Le fichier ne contient pas les colonnes requises : 'Date de début' et 'Nombre de jour'")
            return None, 0

        # Nettoyage et calculs
        df_formations = df_formations.dropna(subset=required_columns)
        df_formations["Nombre de jour"] = pd.to_numeric(df_formations["Nombre de jour"], errors="coerce")
        jours_formation = df_formations["Nombre de jour"].sum()

        st.sidebar.success(f"✅ Total des jours de formation planifiés : **{jours_formation:.1f} jours**")
        return df_formations, jours_formation

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
        return None, 0
    

# Fonction pour préparer les données Float
def prepare_float_data(data_float, rates):
    # Conversion et nettoyage des données
    data_float["Date"] = pd.to_datetime(data_float["Date"], errors="coerce")
    
    # Normalisation des noms de colonnes
    column_mapping = {
        'Heures facturées': 'Logged Billable hours',
        'Heures non facturées': 'Logged Non-billable hours',
        'Coût total': 'Coût'
    }
    data_float = data_float.rename(columns=column_mapping)
    
    # Ajout des colonnes manquantes avec des valeurs par défaut
    for col in ['Logged Billable hours', 'Logged Non-billable hours', 'Coût']:
        if col not in data_float.columns:
            data_float[col] = 0
    
    # Ajout des colonnes calculées
    data_float['Mois'] = data_float['Date'].dt.strftime('%Y-%m')
    data_float['Jours Réalisés'] = data_float['Logged Billable hours'] / 8
    
    # Fusion avec les taux
    if 'PV' not in data_float.columns and rates is not None:
        data_float = data_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
        data_float['PV'] = data_float['PV'].fillna(0)
        data_float['CA Engagé'] = data_float['Jours Réalisés'] * data_float['PV']
    
    return data_float

# Fonction pour afficher les informations de la mission
def display_mission_info(final_plan_prod, final_float, mission_code, date_debut, date_fin):
    # Récupération des informations de la mission
    mission_client = final_float['Client'].iloc[0] if 'Client' in final_float.columns and not final_float.empty else "N/A"
    mission_full_name = final_plan_prod['Nom de la mission'].iloc[0] if not final_plan_prod.empty else "N/A"
    mission_name = re.sub(r"^\[[^\]]+\]\s*[-_]?\s*", "", mission_full_name).strip()
    mission_budget = final_plan_prod['Budget (PV)'].sum()
    
    # Formatage des dates
    mois_debut = date_debut.strftime("%B %Y").capitalize()
    mois_fin = date_fin.strftime("%B %Y").capitalize()
    
    # Affichage
    col1, col2, col3 = st.columns(3)
    
    with col1: 
        st.markdown(f"""
            <div class="mission-info-container">
                <table class="mission-info-table">
                    <tr><td>Client</td><td>{mission_client}</td></tr>
                    <tr><td>Mission</td><td>{mission_name}</td></tr>
                    <tr><td>Code Mission</td><td>{mission_code}</td></tr>
                    <tr><td>Budget Mission</td><td>{format(mission_budget, ",.0f").replace(",", " ")} €</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
    
    with col3: 
        st.markdown(f"""
            <div class="periode-container">
                <div class="periode-text">📅 Période sélectionnée :</div>
                <div class="periode-date">{mois_debut} - {mois_fin}</div>
            </div>
        """, unsafe_allow_html=True)

# Fonction pour afficher les cartes de métriques
def display_metrics_cards(mission_budget, ca_engage_total, budget_remaining, 
                          percentage_budget_used, percentage_budget_remaining,
                          mission_logged_days, jours_formation, jours_consulting):
    
    # Calcul des pourcentages
    pourcentage_formation = (jours_formation / mission_logged_days) * 100 if mission_logged_days else 0
    pourcentage_consulting = (jours_consulting / mission_logged_days) * 100 if mission_logged_days else 0
    
    # Section Budget
    st.subheader("Budget")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{mission_budget:,.0f} €</div>
                <div class="label">CA Budget</div>
                <div class="delta positive">100%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    
    with col2: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{ca_engage_total:,.0f} €</div>
                <div class="label">CA Engagé</div>
                <div class="delta {get_delta_class(percentage_budget_used)}">{percentage_budget_used:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    
    with col3: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{budget_remaining:,.0f} €</div>
                <div class="label">Solde Restant</div>
                <div class="delta {get_delta_class(percentage_budget_remaining)}">{percentage_budget_remaining:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section Jours
    st.subheader("Jours")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{mission_logged_days:.1f} jours</div>
                <div class="label">Jours Réalisés</div>
                <div class="delta positive">100%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_formation:.1f} jours</div>
                <div class="label">Jours de Formation</div>
                <div class="delta positive">{pourcentage_formation:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_consulting:.1f} jours</div>
                <div class="label">Jours de Consulting</div>
                <div class="delta positive">{pourcentage_consulting:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# Fonction pour afficher les tableaux de données
def display_data_tables(final_float, final_plan_prod):
    col1, col2 = st.columns(2)
    
    with col1:
        # Tableau des jours réalisés
        tableau_cumul_jours = final_float.pivot_table(
            index=['Code Mission', 'Acteur'],
            columns='Mois',
            values='Jours Réalisés',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        tableau_cumul_jours["Total"] = tableau_cumul_jours.iloc[:, 2:].sum(axis=1)
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours.columns[2:-1]) + ['Total']
        tableau_cumul_jours = tableau_cumul_jours[colonnes_ordre]
        
        # Ajout du total général
        total_general_jours = tableau_cumul_jours.iloc[:, 2:].sum(axis=0)
        total_general_jours["Code Mission"] = "Total Général"
        total_general_jours["Acteur"] = ""
        tableau_cumul_jours = pd.concat([tableau_cumul_jours, pd.DataFrame([total_general_jours])], ignore_index=True)
        tableau_cumul_jours.iloc[:, 2:] = tableau_cumul_jours.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")
        
        st.subheader("Cumul Jours de production réalisés")
        st.table(tableau_cumul_jours)
    
    with col2:
        # Tableau du CA engagé
        tableau_cumul_ca = final_float.pivot_table(
            index=['Code Mission', 'Acteur'],
            columns='Mois',
            values='CA Engagé',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        tableau_cumul_ca["Total"] = tableau_cumul_ca.iloc[:, 2:].sum(axis=1)
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_ca.columns[2:-1]) + ['Total']
        tableau_cumul_ca = tableau_cumul_ca[colonnes_ordre]
        
        # Ajout du total général
        total_general_ca = tableau_cumul_ca.iloc[:, 2:].sum(axis=0)
        total_general_ca["Code Mission"] = "Total Général"
        total_general_ca["Acteur"] = ""
        tableau_cumul_ca = pd.concat([tableau_cumul_ca, pd.DataFrame([total_general_ca])], ignore_index=True)
        tableau_cumul_ca.iloc[:, 2:] = tableau_cumul_ca.iloc[:, 2:].applymap(lambda x: f"{float(x):,.0f}".replace(",", " "))
        
        st.subheader("Cumul du CA Engagé")
        st.table(tableau_cumul_ca)

# Fonction pour afficher les détails des intervenants
def display_intervenants_details(final_float, rates):
    st.subheader("Détails générales des intervenants")
    
    intervenants = final_float.groupby('Acteur').agg({
        'Logged Billable hours': 'sum'
    }).reset_index()
    
    intervenants['Jours Réalisés'] = intervenants['Logged Billable hours'] / 8
    intervenants = intervenants.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
    intervenants['PV'] = intervenants['PV'].fillna(0)
    intervenants['CA Engagé'] = intervenants['Jours Réalisés'] * intervenants['PV']
    
    # Formatage des données
    intervenants["Jours Réalisés"] = intervenants["Jours Réalisés"].round(1)
    intervenants["CA Engagé"] = intervenants["CA Engagé"].round(0).astype(int)
    intervenants["PV"] = intervenants["PV"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
    intervenants = intervenants.rename(columns={"Logged Billable hours": "Heures facturables enregistrées"})
    
    st.write(intervenants)

# Fonction pour afficher les visualisations
def display_visualizations(jours_formation, jours_consulting, final_float, final_plan_prod, mission_code):
    st.subheader("Visualisations")
    col6, col7 = st.columns(2)
    
    with col6:
        # Graphique de répartition Formation vs Consulting
        data = pd.DataFrame({
            "Type": ["Formation", "Consulting"],
            "Jours": [jours_formation, jours_consulting]
        })
        
        fig = px.pie(data, names="Type", values="Jours", 
                     title="Part des jours consacrés aux Formations vs Consulting",
                     color_discrete_sequence=["#2a9df4", "#9b59b6"])
        st.plotly_chart(fig)
    
    with col7:
        # Graphique d'évolution du CA Engagé cumulé vs Budget
        cumul_ca = final_float.groupby("Mois")["CA Engagé"].sum().reset_index()
        cumul_ca = cumul_ca.sort_values(by="Mois")
        cumul_ca["CA Engagé Cumulé"] = cumul_ca["CA Engagé"].cumsum()
        budget_mission = final_plan_prod["Budget (PV)"].sum()
        cumul_ca["Budget Mission"] = budget_mission
        
        if not cumul_ca.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"], marker='o', 
                   label="CA Engagé Cumulé", linestyle='-', color='darkblue')
            ax.plot(cumul_ca["Mois"], cumul_ca["Budget Mission"], marker='o', 
                   label="Budget Mission", linestyle='-', color='lightblue')
            
            for x, y in zip(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"]):
                ax.text(x, y, f'{y:,.0f}', ha='right', va='bottom', fontsize=8)
            for x, y in zip(cumul_ca["Mois"], cumul_ca["Budget Mission"]):
                ax.text(x, y, f'{y:,.0f}', ha='left', va='bottom', fontsize=8)
            
            ax.set_xlabel("Mois")
            ax.set_ylabel("Montant (€)")
            ax.set_title(f"Évolution du CA Engagé cumulé vs Budget ({mission_code})")
            ax.legend(title="Type")
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.6)
            
            st.pyplot(fig)

# Fonction principale pour afficher le rapport client
def display_customer_report(data_plan_prod, data_float, rates):
    # 1. Upload fichier Excel (Formations)
    fichier = st.sidebar.file_uploader("📤 Importer le fichier contenant les formations (ex: Formations 2025)", type=["xlsx"])
    
    # 2. Chargement et traitement des données de formation
    df_formations, jours_formation = load_and_process_formation_data(fichier)
    
    # 3. Préparation des données Float
    data_float = prepare_float_data(data_float, rates)
    
    # 4. Vérification des données requises
    required_columns_plan = ['Code Mission', 'Nom de la mission', 'Budget (PV)']
    for col in required_columns_plan:
        if col not in data_plan_prod.columns:
            st.error(f"Colonne manquante dans data_plan_prod : {col}")
            return
    
    # 5. Filtres interactifs
    st.sidebar.header("Filtres")
    
   # Filtre de Mission
    mission_code = st.sidebar.selectbox(
        "🎯 Sélectionnez la mission (uniquement 238010 - Sales Academy)",
        options=data_plan_prod['Code Mission'].unique(),
        index=data_plan_prod['Code Mission'].tolist().index("238010") if "238010" in data_plan_prod['Code Mission'].values else 0
    )
    
    if mission_code != "238010":
        st.error("❌ Cette page est uniquement pour la mission 238010 - Sales Academy.")
        st.stop()
    
    # Application du filtre de mission
    filtered_plan_prod = data_plan_prod[data_plan_prod['Code Mission'] == mission_code]
    filtered_float = data_float[data_float['Code Mission'] == mission_code]
    
    if filtered_plan_prod.empty or filtered_float.empty:
        st.warning("Aucune donnée disponible pour la mission sélectionnée.")
        st.stop()
    
    # Filtre de période
    date_min = filtered_float["Date"].min()
    date_max = filtered_float["Date"].max()
    
    date_debut = st.sidebar.date_input("📅 Date Début", value=date_min)
    date_fin = st.sidebar.date_input("📅 Date Fin", value=date_max)
    
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)
    
    # Application du filtre de période
    if date_debut and date_fin:
        filtered_float = filtered_float[(filtered_float["Date"] >= date_debut) & (filtered_float["Date"] <= date_fin)]
    
    if filtered_float.empty:
        st.warning("⚠️ Aucune donnée disponible pour la période sélectionnée.")
        st.stop()
    
    # Données finales filtrées
    final_plan_prod = filtered_plan_prod.copy()
    final_float = filtered_float.copy()
    
    # 6. Calculs principaux
    # 6. Calculs principaux - MODIFICATION CLÉ
    # Calcul direct des jours réalisés
    mission_logged_hours = filtered_float['Logged Billable hours'].sum()
    mission_logged_days = mission_logged_hours / 8  # Conversion en jours
    
    # Stockage silencieux dans session_state
    if 'mission_logged_days' not in st.session_state:
        st.session_state.mission_logged_days = mission_logged_days
    else:
        st.session_state.mission_logged_days = mission_logged_days
    
    # Calcul des jours consulting
    
    jours_consulting = mission_logged_days - jours_formation
    jours_consulting = max(jours_consulting, 0)  # éviter négatif
    
    pv_moyen = rates["PV"].mean() if not rates.empty else 0
    ca_engage_total = jours_consulting * pv_moyen 
    
    mission_budget = final_plan_prod['Budget (PV)'].sum()
    budget_remaining = mission_budget - ca_engage_total
    percentage_budget_used = (ca_engage_total / mission_budget) * 100 if mission_budget != 0 else 0
    percentage_budget_remaining = (budget_remaining / mission_budget) * 100 if mission_budget != 0 else 0
    
    # Stocker les jours réalisés pour Sales Academy
    if str(mission_code) == "238010":
        st.session_state["mission_logged_days"] = mission_logged_days
    st.write("🔍 Jours consulting :", jours_consulting)
    st.write("🔍 PV moyen :", pv_moyen)
    st.write("🔍 CA Engagé :", ca_engage_total)

    # 7. Affichage des informations
    st.markdown("<div class='title'><b>📊 Tableau de bord - Customer Report</b></div>", unsafe_allow_html=True)
    st.image("Logo_Advent.jpg", width=300)
    st.subheader("📘 Formation vs Consulting - Sales Academy (238010)")
    
    display_mission_info(final_plan_prod, final_float, mission_code, date_debut, date_fin)
    display_metrics_cards(mission_budget, ca_engage_total, budget_remaining,
                         percentage_budget_used, percentage_budget_remaining,
                         mission_logged_days, jours_formation, jours_consulting)
    
    display_data_tables(final_float, final_plan_prod)
    display_intervenants_details(final_float, rates)
    display_visualizations(jours_formation, jours_consulting, final_float, final_plan_prod, mission_code)

# Point d'entrée principal
if __name__ == "__main__":
    # Vérification des données en session
    if "data_plan_prod" in st.session_state and "data_float" in st.session_state:
        data_plan_prod = st.session_state["data_plan_prod"]
        data_float = st.session_state["data_float"]
        rates = st.session_state.get("rates", pd.DataFrame())
        
        # Affichage du rapport
        display_customer_report(data_plan_prod, data_float, rates)
        
    else:
        st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")