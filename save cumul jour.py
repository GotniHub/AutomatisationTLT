#         # Nettoyage des noms
#         def clean_nom(nom):
#             if pd.isna(nom):
#                 return ""
#             nom = str(nom).strip().lower()
#             return unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('utf-8')

#         # Nettoyer les noms dans les deux fichiers
#         final_float['Acteur_clean'] = final_float['Acteur'].apply(clean_nom)
#         df_formations['Formateur_clean'] = df_formations['Formateur 1'].apply(clean_nom)

#         # Préparation des dates
#         final_float['Date'] = pd.to_datetime(final_float['Date'], errors='coerce')
#         df_formations['Date de début'] = pd.to_datetime(df_formations['Date de début'], errors='coerce')

#         # Grouper les jours de formation par formateur ET date
#         jours_formation_par_jour = df_formations.groupby(['Formateur_clean', 'Date de début'])['Nombre de jour'].sum().reset_index()

#         # Fusionner avec le fichier float pour soustraire les jours de formation jour par jour
#         final_float = final_float.merge(
#             jours_formation_par_jour,
#             how='left',
#             left_on=['Acteur_clean', 'Date'],
#             right_on=['Formateur_clean', 'Date de début']
#         )

#         # Remplacer NaN par 0 pour les jours non formateurs
#         final_float['Nombre de jour'] = final_float['Nombre de jour'].fillna(0)

#         # Calcul des jours réalisés et jours d'ingénierie
#         final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8
#         final_float['Jours Ingénierie'] = final_float['Jours Réalisés'] - final_float['Nombre de jour']
#         final_float['Jours Ingénierie'] = final_float['Jours Ingénierie'].apply(lambda x: max(x, 0))

#         # Ajouter colonne Mois pour le pivot
#         final_float['Mois'] = final_float['Date'].dt.strftime('%Y-%m')

#         # Créer le tableau croisé dynamique
#         tableau_cumul_jours_ingenierie = final_float.pivot_table(
#             index=['Code Mission', 'Acteur'],
#             columns='Mois',
#             values='Jours Ingénierie',
#             aggfunc='sum',
#             fill_value=0
#         ).reset_index()

#         # Ajouter la colonne Total
#         tableau_cumul_jours_ingenierie['Total'] = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum(axis=1)

#         # Réorganiser
#         colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours_ingenierie.columns[2:-1]) + ['Total']
#         tableau_cumul_jours_ingenierie = tableau_cumul_jours_ingenierie[colonnes_ordre]

#         # Total général
#         total_general = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum()
#         total_general['Code Mission'] = 'Total Général'
#         total_general['Acteur'] = ''
#         tableau_cumul_jours_ingenierie = pd.concat([tableau_cumul_jours_ingenierie, pd.DataFrame([total_general])], ignore_index=True)

#         # Format
#         tableau_cumul_jours_ingenierie.iloc[:, 2:] = tableau_cumul_jours_ingenierie.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")

#         # Affichage
#         st.subheader("Cumul Jours d'Ingénierie réalisés")
#         st.table(tableau_cumul_jours_ingenierie)



# #TEST FINAL

# # Nettoyer les noms
# final_float['Acteur_clean'] = final_float['Acteur'].apply(clean_nom)
# df_formations['Formateur_clean'] = df_formations['Formateur 1'].apply(clean_nom)

# # Convertir les dates
# final_float['Date'] = pd.to_datetime(final_float['Date'], errors='coerce')
# df_formations['Date de début'] = pd.to_datetime(df_formations['Date de début'], errors='coerce')

# # Ajouter le mois dans chaque fichier
# final_float['Mois'] = final_float['Date'].dt.strftime('%Y-%m')
# df_formations['Mois'] = df_formations['Date de début'].dt.strftime('%Y-%m')

# # Calculer les jours réalisés (Jours Réalisés = heures facturées / 8)
# final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

# # Grouper les jours réalisés par intervenant et mois
# jours_realises_par_mois = final_float.groupby(['Code Mission', 'Acteur', 'Acteur_clean', 'Mois'])['Jours Réalisés'].sum().reset_index()

# # Grouper les jours de formation par formateur et mois
# jours_formations_par_mois = df_formations.groupby(['Formateur_clean', 'Mois'])['Nombre de jour'].sum().reset_index()

# # Fusionner les deux tables par Acteur_clean et Mois
# df_merged = jours_realises_par_mois.merge(
#     jours_formations_par_mois,
#     how='left',
#     left_on=['Acteur_clean', 'Mois'],
#     right_on=['Formateur_clean', 'Mois']
# )

# # Remplacer NaN par 0 pour les formateurs sans formation ce mois-là
# df_merged['Nombre de jour'] = df_merged['Nombre de jour'].fillna(0)

# # Calculer les jours d'ingénierie
# df_merged['Jours Ingénierie'] = df_merged['Jours Réalisés'] - df_merged['Nombre de jour']
# df_merged['Jours Ingénierie'] = df_merged['Jours Ingénierie'].apply(lambda x: max(x, 0))

# # Créer le pivot final
# tableau_cumul_jours_ingenierie = df_merged.pivot_table(
#     index=['Code Mission', 'Acteur'],
#     columns='Mois',
#     values='Jours Ingénierie',
#     aggfunc='sum',
#     fill_value=0
# ).reset_index()

# # Ajouter la colonne Total
# tableau_cumul_jours_ingenierie['Total'] = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum(axis=1)

# # Réorganiser les colonnes
# colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours_ingenierie.columns[2:-1]) + ['Total']
# tableau_cumul_jours_ingenierie = tableau_cumul_jours_ingenierie[colonnes_ordre]

# # Ligne total général
# total_general = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum()
# total_general['Code Mission'] = 'Total Général'
# total_general['Acteur'] = ''
# tableau_cumul_jours_ingenierie = pd.concat([tableau_cumul_jours_ingenierie, pd.DataFrame([total_general])], ignore_index=True)

# # Formatage
# tableau_cumul_jours_ingenierie.iloc[:, 2:] = tableau_cumul_jours_ingenierie.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")

# # Affichage
# st.subheader("Cumul Jours d'Ingénierie réalisés")
# st.table(tableau_cumul_jours_ingenierie)
