import pandas as pd
import streamlit as st
import plotly.express as px


def display_dashboard(data_plan_prod, data_float, merged_data):
    # Injecter le style CSS
    st.markdown("""
        <style>
            .title {
                font-family: 'Arial', sans-serif;
                font-size: 2.5rem;
                text-align: center;
                margin-bottom: 20px;
                color: #333;
            }
        
            .card {
                background-color: #f9f9f9;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                margin: 10px;
            }
            .card h2 {
                font-size: 2rem;
                margin: 0;
                color: #007BFF;
            }
            .card p {
                margin: 5px 0;
                font-size: 1.2rem;
                color: #555;
            }
        
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<div class='title'>📊 Tableau de bord - Misssion View</div>", unsafe_allow_html=True)
    #st.title("Dashboard : Comparaison Budget vs Réel")

    # Ajout de filtres dynamiques
    with st.sidebar.expander("Filtres", expanded= True):

        # Conversion de la colonne "Période" en datetime
        data_plan_prod['Période'] = pd.to_datetime(data_plan_prod['Période'], format='%b-%y', errors='coerce')

        # Ajout du filtre de plage de dates
        min_date = data_plan_prod['Période'].min()
        max_date = data_plan_prod['Période'].max()

        start_date, end_date = st.date_input(
            "Filtrer par Période (plage de dates)",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Filtre : Code Cadran
        code_cadran_filter = st.multiselect(
            "Filtrer par Code Cadran",
            options=data_plan_prod['Code Cadran'].unique(),
            default=data_plan_prod['Code Cadran'].unique()
        )

        # Filtre : Cadran Mission Desc
        cadran_desc_filter = st.multiselect(
            "Filtrer par Cadran Mission Desc",
            options=data_plan_prod['Cadran Mission Desc'].unique(),
            default=data_plan_prod['Cadran Mission Desc'].unique()
        )

        # Filtre : Leader
        leader_filter = st.multiselect(
            "Filtrer par Leader",
            options=data_plan_prod['Leader'].unique(),
            default=data_plan_prod['Leader'].unique()
        )

        # Filtre : Topic
        topic_filter = st.multiselect(
            "Filtrer par Topic",
            options=data_plan_prod['Topic'].unique(),
            default=data_plan_prod['Topic'].unique()
        )

    # Application des filtres
    data_plan_prod_filtered = data_plan_prod[
        (data_plan_prod['Période'] >= pd.Timestamp(start_date)) &
        (data_plan_prod['Période'] <= pd.Timestamp(end_date)) & 
        (data_plan_prod['Code Cadran'].isin(code_cadran_filter)) &
        (data_plan_prod['Cadran Mission Desc'].isin(cadran_desc_filter)) &
        (data_plan_prod['Leader'].isin(leader_filter)) &
        (data_plan_prod['Topic'].isin(topic_filter)) 
    ]
    # Application des filtres sur data_float
    data_float_filtered = data_float[
        (data_float['Code Mission'].isin(data_plan_prod_filtered['Code Mission'])) &
        (data_float['Date'] >= pd.Timestamp(start_date)) &
        (data_float['Date'] <= pd.Timestamp(end_date))
    ]

    # Supprimer les doublons pour créer une liste unique des noms de mission
    unique_missions = merged_data[['Code Mission', 'Nom de la mission']].drop_duplicates(subset='Nom de la mission')
    # Créer un filtre multisélection basé sur les codes de mission uniques
    mission_filter = st.multiselect(
        "Sélectionnez une ou plusieurs missions",
        options=unique_missions['Code Mission'].unique(),
        format_func=lambda x: unique_missions.loc[unique_missions['Code Mission'] == x, 'Nom de la mission'].iloc[0]
    )

    # Appliquer le filtre sur les données fusionnées pour les missions
    if mission_filter:
        data_plan_prod_filtered = data_plan_prod_filtered[data_plan_prod_filtered['Code Mission'].isin(mission_filter)]
        data_float_filtered = data_float_filtered[data_float_filtered['Code Mission'].isin(mission_filter)]

        # Fusionner les deux tables pour inclure tous les acteurs
        merged_actors = pd.concat([
            data_plan_prod_filtered[['Code Mission', 'Acteur']].drop_duplicates(),
            data_float_filtered[['Code Mission', 'Acteur']].drop_duplicates()
        ], ignore_index=True).drop_duplicates()


        # Filtrer les acteurs pour les missions sélectionnées
        filtered_actors = merged_actors['Acteur'].drop_duplicates().tolist()
        actor_filter = st.multiselect(
            "Sélectionnez un ou plusieurs acteurs",
            options=filtered_actors,
            default=filtered_actors
        )

        # Appliquer le filtre des acteurs sur les données
        if actor_filter:
            # Filtrer les missions basées sur les acteurs sélectionnés
            filtered_actors_missions = merged_actors[merged_actors['Acteur'].isin(actor_filter)]['Code Mission'].unique()

            # Appliquer le filtre des missions associées aux acteurs sélectionnés
            data_plan_prod_filtered = data_plan_prod_filtered[data_plan_prod_filtered['Code Mission'].isin(filtered_actors_missions)]
            data_float_filtered = data_float_filtered[data_float_filtered['Code Mission'].isin(filtered_actors_missions)]

            # Appliquer un filtre supplémentaire sur les lignes spécifiques des acteurs dans data_float_filtered
            data_float_filtered = data_float_filtered[data_float_filtered['Acteur'].isin(actor_filter)]
            data_plan_prod_filtered = data_plan_prod_filtered[data_plan_prod_filtered['Acteur'].isin(actor_filter)]

    else:
        # Si aucune mission sélectionnée, ne rien afficher pour les acteurs
        st.info("Veuillez sélectionner une mission pour voir les acteurs associés.")
        data_plan_prod_filtered = data_plan_prod
        data_float_filtered = data_float
            
    # Initialiser totals_by_mission pour éviter des erreurs si aucune mission n'est sélectionnée
    totals_by_mission = pd.DataFrame(columns=['Nom de la mission', 'Budget (PV)', 'Nbre de jour mission', 'Real Days Worked', 'Gap'])
    
    # Appliquer le filtre sur les données fusionnées
    if mission_filter:
        filtered_data = merged_data[merged_data['Code Mission'].isin(mission_filter)]
        if not filtered_data.empty:
            totals_by_mission = filtered_data.groupby('Nom de la mission').agg({
                'Budget (PV)': 'sum',
                'Nbre de jour mission': 'sum',
                'Real Days Worked': 'first'
            }).reset_index()
            # Calculer les écarts
            totals_by_mission['Gap'] = totals_by_mission['Nbre de jour mission'] - totals_by_mission['Real Days Worked']

    # Ajouter le style pour les cartes
    # Filtrer par mission si un filtre est appliqué
    # Supprimer les doublons et créer une liste unique des codes de mission avec leur nom
    unique_missions = merged_data[['Code Mission', 'Nom de la mission']].drop_duplicates()

    # Appliquer le filtre sur les totaux par mission
    if mission_filter:
        # Filtrer les données consolidées (totals_by_mission) par les codes sélectionnés
        totals_by_mission = totals_by_mission[totals_by_mission['Nom de la mission'].str.contains('|'.join(mission_filter), case=False, na=False)]

    st.markdown("""
        <style>
        .card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px;
        }
        .card h2 {
            font-size: 2rem;
            margin: 0;
        }
        .card p {
            margin: 5px 0;
            font-size: 1.2rem;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    # Comparaison globale dans la première colonne
    st.subheader("Comparaison globale")
    budget_total = data_plan_prod_filtered['Budget (PV)'].sum(skipna=True)
    heures_facturees = data_float_filtered['Heures facturées'].sum(skipna=True)
    marge_total = budget_total - data_float_filtered['Coût'].sum(skipna=True)
    jours_prevus_total = totals_by_mission['Nbre de jour mission'].sum()
    jours_realises_total = totals_by_mission['Real Days Worked'].sum()
    with st.container ( border = True):
        col1,col2,col3 = st.columns(3)
        with col1:
            # Afficher les KPIs en cartes personnalisées
            st.markdown(f"""
                <div class="card">
                    <h2>{budget_total:.2f} €</h2>
                    <p>Budget Total (PV)</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card">
                    <h2>{jours_prevus_total:.2f} jours</h2>
                    <p>Total Jours Prévus</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="card">
                    <h2>{heures_facturees:.2f} h</h2>
                    <p>Total Heures Facturées</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card">
                    <h2>{jours_realises_total:.2f} jours</h2>
                    <p>Total Jours Réalisés</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="card">
                    <h2>{marge_total:.2f} €</h2>
                    <p>Marge Totale</p>
                </div>
            """, unsafe_allow_html=True)
            # Vérification si une mission est sélectionnée
            if mission_filter:
                client_list = ", ".join(data_plan_prod_filtered['Client'].unique())
                st.markdown(f"""
                    <div class="card">
                        <h2>{client_list}</h2>
                        <p>Clients</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="card">
                        <h4>"Aucune mission sélectionné"</h4>
                        <p>Clients</p>
                    </div>
                """, unsafe_allow_html=True)

    # Calcul des totaux consolidés par mission
    st.subheader("Totaux consolidés par Mission")

    if mission_filter:
        if not data_float_filtered.empty:
            # Vérification de la colonne 'Code Mission'
            if 'Code Mission' not in data_float_filtered.columns or 'Code Mission' not in data_plan_prod_filtered.columns:
                st.error("La colonne 'Code Mission' est manquante dans les données filtrées.")
            else:
                # Agréger les données par Code Mission
                totals_by_mission = data_float_filtered.groupby('Code Mission').agg({
                    'Heures facturées': 'sum',
                    'Total Hours': 'sum',
                    'Coût': 'sum'
                }).reset_index()

                # Ajouter les colonnes supplémentaires depuis data_plan_prod_filtered
                totals_by_mission = pd.merge(
                    totals_by_mission,
                    data_plan_prod_filtered[['Code Mission', 'Nom de la mission', 'Budget (PV)', 'Nbre de jour mission', 'Client']],
                    on='Code Mission',
                    how='left'
                )

                # Ajouter la colonne calculée pour "Real Days Worked"
                if 'Total Hours' in totals_by_mission.columns:
                    totals_by_mission['Real Days Worked'] = totals_by_mission['Total Hours'] / 8
                else:
                    totals_by_mission['Real Days Worked'] = 0  # Valeur par défaut si Total Hours est manquant

                # Ajouter la colonne calculée pour l'écart (Gap)
                if 'Nbre de jour mission' in totals_by_mission.columns and 'Real Days Worked' in totals_by_mission.columns:
                    totals_by_mission['Gap'] = totals_by_mission['Nbre de jour mission'] - totals_by_mission['Real Days Worked']
                else:
                    totals_by_mission['Gap'] = 0  # Valeur par défaut si les colonnes nécessaires sont manquantes
                # Regrouper les résultats par mission pour obtenir les totaux

                grouped_totals = totals_by_mission.groupby('Nom de la mission').agg({
                    'Budget (PV)': 'sum',
                    'Nbre de jour mission': 'sum',
                    'Real Days Worked': 'first',
                    'Gap': 'sum'
                }).reset_index()

                # Afficher les données consolidées par mission
                for _, row in grouped_totals.iterrows():
                    st.markdown(f"""
                        **Mission**: {row['Nom de la mission']}  
                        - **Budget Total (PV)**: {row.get('Budget (PV)', 'N/A')} €  
                        - **Jours Prévus**: {row.get('Nbre de jour mission', 'N/A')} jours  
                        - **Réalisé (jours travaillés)**: {row.get('Real Days Worked', 0):.2f} jours  
                        - **Écart (Gap)**: {row.get('Gap', 0):.2f} jours  
                    """)

        else:
            st.info("Aucune donnée disponible pour les missions sélectionnées.")
    else:
        st.info("Aucune mission sélectionnée.")

    # Afficher les données filtrées
    st.write("### Résumé des Missions")
    if not {'Nom de la mission', 'Budget (PV)', 'Nbre de jour mission', 'Real Days Worked'}.issubset(merged_data.columns):
        st.error("Certaines colonnes nécessaires sont manquantes dans les données fusionnées.")
    else:
        st.write(merged_data[['Nom de la mission', 'Budget (PV)', 'Nbre de jour mission', 'Real Days Worked']])

    # Calcul des écarts
    if 'Nbre de jour mission' in merged_data.columns and 'Real Days Worked' in merged_data.columns:
        merged_data['Gap'] = merged_data['Nbre de jour mission'] - merged_data['Real Days Worked']

    # Graphique : Évolution temporelle Budget vs Réel
    st.subheader("Évolution temporelle")
    evolution = data_float.groupby('Date')['Heures facturées'].sum().reset_index()
    budget_evolution = data_plan_prod.groupby('Période')['Budget (PV)'].sum().reset_index()
    fig_line = px.line(
        evolution,
        x='Date',
        y='Heures facturées',
        title="Évolution des Heures Facturées",
        labels={'Heures facturées': 'Heures', 'Date': 'Temps'}
    )
    fig_line.add_scatter(
        x=budget_evolution['Période'],
        y=budget_evolution['Budget (PV)'],
        mode='lines',
        name='Budget (PV)'
    )
    st.plotly_chart(fig_line)
    
    # Détails des missions
    st.subheader("Détails des missions")
    mission = st.selectbox("Sélectionnez une mission", data_float['Nom de la mission'].unique())
    details_mission = data_float[data_float['Nom de la mission'] == mission]
    st.write(details_mission)

    # Division en colonnes
    col1, col2 = st.columns(2)

    # Comparaison globale dans la première colonne
    with col1:
        # Graphique : Répartition du budget par client
        st.subheader("Répartition du budget par client")
        budget_client = data_plan_prod.groupby('Client')['Budget (PV)'].sum().reset_index()
        fig_pie = px.pie(
            budget_client,
            values='Budget (PV)',
            names='Client',
            title="Répartition du Budget par Client"
        )
        st.plotly_chart(fig_pie)
    # Comparaison par territoire dans la deuxième colonne
    with col2:
        st.subheader("Comparaison par territoire")
        comparaison = data_plan_prod.groupby('Code Territoire')['Budget (PV)'].sum().reset_index()
        comparaison = comparaison.merge(
            data_float.groupby('Code Territoire')['Heures facturées'].sum().reset_index(),
            on='Code Territoire',
            how='left'
        )
        fig = px.bar(
            comparaison,
            x='Code Territoire',
            y=['Budget (PV)', 'Heures facturées'],
            title="Budget vs Réel par Territoire",
            labels={'value': 'Montant (€)', 'Code Territoire': 'Territoire'}
        )
        st.plotly_chart(fig)


# Vérifiez si les données sont disponibles dans la session
if "data_plan_prod" in st.session_state and "data_float" in st.session_state and "merged_data" in st.session_state:
    data_plan_prod = st.session_state["data_plan_prod"]
    data_float = st.session_state["data_float"]
    merged_data = st.session_state["merged_data"]

    # Afficher le tableau de bord avec les données existantes
    display_dashboard(data_plan_prod, data_float, merged_data)
else:
    st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")

