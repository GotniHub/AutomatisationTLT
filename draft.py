    # # Création du graphique avec Matplotlib
    # evofig, ax = plt.subplots(figsize=(8, 4))  # Ajuster la taille
    
    # # Tracer les courbes
    # ax.plot(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"], marker='o', label="CA Engagé Cumulé", linestyle='-', color='darkblue')
    # ax.plot(cumul_ca["Mois"], cumul_ca["Budget Mission"], marker='o', label="Budget Mission", linestyle='-', color='lightblue')
    #     # Ajouter les valeurs au-dessus des points
    # for x, y in zip(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"]):
    #     ax.text(x, y, f'{y:,.0f}', ha='right', va='bottom', fontsize=8)
    # for x, y in zip(cumul_ca["Mois"], cumul_ca["Budget Mission"]):
    #     ax.text(x, y, f'{y:,.0f}', ha='left', va='bottom', fontsize=8)
    # # Ajouter les labels et le titre
    # ax.set_xlabel("Mois")
    # ax.set_ylabel("Montant (€)")
    # ax.set_title(f"Évolution du CA Engagé cumulé vs Budget ({mission_filter})")
    
    # # Ajouter une légende
    # ax.legend(title="Type")
    
    # # Personnaliser l'affichage
    # plt.xticks(rotation=45)  # Rotation des labels de l'axe X si nécessaire
    # plt.grid(True, linestyle='--', alpha=0.6)
    
    # # Afficher le graphique dans Streamlit
    # st.subheader("Évolution du CA Engagé cumulé vs Budget")
    # evo_chart_path = os.path.abspath("evo_chart.png")  # Absolute path
    # plt.savefig(evo_chart_path, bbox_inches='tight', dpi=300)
    # st.pyplot(evofig)

    #     # 📌 Création du graphique avec Plotly
    # fig = px.line(
    #     cumul_ca,
    #     x="Mois",
    #     y=["CA Engagé Cumulé", "Budget Mission"],
    #     markers=True,
    #     title=f"Évolution du CA Engagé cumulé vs Budget ({mission_filter})",
    #     labels={"value": "Montant (€)", "Mois": "Mois", "variable": "Type"},
    # )

    # # 📌 Personnaliser le style du graphique
    # fig.update_layout(
    #     title={"x": 0.5, "xanchor": "center"},
    #     xaxis_title="Mois",
    #     yaxis_title="Montant (€)",
    #     legend_title="Type",
    #     template="plotly_white",
    # )

    # # 📌 Affichage du graphique dans Streamlit
    # st.subheader("Évolution du CA Engagé cumulé vs Budget ( Dynamique ) 📈")
    # st.plotly_chart(fig)


    # # 📌 Préparer les données : contribution de chaque mois au CA total
    # waterfall_data = final_float.groupby("Mois")["CA Engagé"].sum().reset_index()

    # # 📌 Calcul du total correct (somme de toutes les contributions par mois)
    # total_ca_engage = waterfall_data["CA Engagé"].sum()

    # # 📌 Définition des mesures (toutes en "relative" sauf le total qui est "total")
    # measures = ["relative"] * len(waterfall_data) + ["total"]

    # # 📌 Création du graphique Waterfall
    # waterfall_fig = go.Figure(go.Waterfall(
    #     name="CA Engagé",
    #     orientation="v",
    #     measure=measures,  # Appliquer les mesures correctes
    #     x=waterfall_data["Mois"].tolist() + ["Total"],  # Ajouter le total dans l'axe X
    #     y=waterfall_data["CA Engagé"].tolist() + [total_ca_engage],  # Ajouter le vrai total dans Y
    #     connector={"line": {"color": "rgb(63, 63, 63)"}},  # Ligne de connexion entre les barres
    # ))

    # # 📌 Personnalisation du visuel
    # waterfall_fig.update_layout(
    #     title="Contribution du CA Engagé par Mois 💰",
    #     xaxis_title="Mois",
    #     yaxis_title="CA Engagé (€)",
    #     template="plotly_white",
    # )

    # # 📌 Affichage du graphique dans Streamlit
    # st.subheader("Contribution du CA Engagé par Mois 💰")
    # st.plotly_chart(waterfall_fig)


    # def generate_pdf(report_html):
    #     pdf_file_path = "customer_report.pdf"

    #     options = {
    #         "enable-local-file-access": "",  # Allow local images to be embedded
    #         "page-size": "A4",
    #         "margin-top": "10mm",
    #         "margin-bottom": "10mm",
    #         "margin-left": "10mm",
    #         "margin-right": "10mm"
    #     }

    #     # 🔹 Ensure the Pie Chart Image Path is Passed Correctly
    #     pie_chart_path = os.path.abspath("pie_chart.png")  # Absolute path
    #     report_html = report_html.replace("pie_chart.png", pie_chart_path)
    #     # 🔹 Ensure the Pie Chart Image Path is Passed Correctly
    #     bar_chart_path = os.path.abspath("bar_chart.png")  # Absolute path
    #     report_html = report_html.replace("bar_chart.png", bar_chart_path)
    #     # 🔹 Ensure the Pie Chart Image Path is Passed Correctly
    #     evo_chart_path = os.path.abspath("evo_chart.png")  # Absolute path
    #     report_html = report_html.replace("evo_chart.png", evo_chart_path)

    #     # Generate the PDF
    #     try:
    #         pdfkit.from_string(report_html, pdf_file_path, options=options)
    #         return pdf_file_path
    #     except Exception as e:
    #         st.error(f"Erreur lors de la génération du PDF : {e}")
    #         return None

        
    # #     # 📌 Générer le contenu HTML du rapport
    # # st.subheader("Télécharger le rapport en PDF 📄")

    # # 📌 Utiliser Jinja2 pour générer le HTML proprement
    # template = Template("""
    # <!DOCTYPE html>
    # <html lang="fr">
    # <head>
    #     <meta charset="UTF-8">
    #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #     <title>Customer Report</title>
    #     <style>
    #         body { font-family: Arial, sans-serif; margin: 20px; }
    #         h1, h2, h3 { color: #333; }
    #         table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    #         th, td { border: 1px solid black; padding: 8px; text-align: left; }
    #         th { background-color: #f2f2f2; }
    #         .header {
    #             display: flex;
    #             align-items: center;
    #             justify-content: space-between;
    #             margin-bottom: 20px;
    #         }
    #         .section {
    #             page-break-inside: avoid;
    #             margin-bottom: 20px;
    #         }
    #         .header img {
    #             width: 200px;  /* 🔹 Ajuste la taille du logo */
    #             height: auto;
    #         }
    #     </style>
    # </head>
    # <body>
    #     <!-- 🔹 EN-TÊTE AVEC LOGO -->
    #     <div class="header">
    #         <img src="{{ logo_path }}" alt="Logo">
    #         <h1>Customer Report</h1>
    #     </div>
            
    #     <h2>Informations Générales</h2>
    #     <table>
    #         <tr><th>Client</th><td>{{ mission_client }}</td></tr>
    #         <tr><th>Mission</th><td>{{ mission_name }}</td></tr>
    #         <tr><th>Code Mission</th><td>{{ mission_code }}</td></tr>
    #         <tr><th>Budget Mission</th><td>{{ mission_budget }} €</td></tr>
    #     </table>

    #     <h2>Budget et Consommation </h2>
    #     <table>
    #         <tr><th>CA Budget</th><td>{{ mission_budget }} €</td></tr>
    #         <tr><th>CA Engagé</th><td>{{ ca_engage_total }} €</td></tr>
    #         <tr><th>Solde Restant</th><td>{{ budget_remaining }} €</td></tr>
    #     </table>

    #     <h2>Jours Consommés </h2>
    #     <table>
    #         <tr><th>Jours Budget</th><td>{{ mission_days_budget }} jours</td></tr>
    #         <tr><th>Jours Réalisés</th><td>{{ mission_logged_days }} jours</td></tr>
    #         <tr><th>Solde Jours Restant</th><td>{{ mission_days_remaining }} jours</td></tr>
    #     </table>

    #     <div class="section page-break">
    #         <h2>Détails des Intervenants</h2>
    #         {{ intervenants.to_html(index=False) }}
    #     </div>

    #     <div class="section page-break">
    #         <h2>Cumul Jours Réalisés </h2>
    #         {{ tableau_cumul_jours.to_html(index=False) }}
    #     </div>

    #     <div class="section page-break">
    #         <h2>Cumul CA Engagé </h2>
    #         {{ tableau_cumul_ca.to_html(index=False) }}
    #     </div>
    #     <div class="section" style="page-break-inside: avoid;">
    #         <h2>Visualisations</h2>
                        
    #         <div style="page-break-inside: avoid;">                
    #             <h3>Répartition des coûts par intervenant</h3>
    #             <img src="pie_chart.png" alt="Pie Chart" width="600">
    #         </div>
                            
    #         <div style="page-break-inside: avoid;">                                
    #             <h3>Jours Réalisés par Intervenant</h3>
    #             <img src="bar_chart.png" alt="Bar Chart" width="600">
    #         </div>
            
    #         <div style="page-break-inside: avoid;">                                
    #             <h3>Évolution du CA Engagé cumulé vs Budget</h3>
    #             <img src="evo_chart.png" alt="Evo Chart" width="600">
    #         </div>   
    #     </div>           
    # </body>
    # </html>
    # """)
    # logo_path = os.path.abspath("Logo_Advent.jpg")
    # # 📌 Générer le HTML avec les données de la mission sélectionnée
    # report_html = template.render(
    #     mission_client=mission_client,
    #     mission_name=mission_name,
    #     mission_code=mission_code,
    #     mission_budget=f"{mission_budget:,.0f}",
    #     ca_engage_total=f"{ca_engage_total:,.0f}",
    #     budget_remaining=f"{budget_remaining:,.0f}",
    #     #mission_days_budget=mission_days_budget,
    #     mission_logged_days=mission_logged_days,
    #     #mission_days_remaining=mission_days_remaining,
    #     intervenants=intervenants,
    #     tableau_cumul_jours=tableau_cumul_jours,
    #     tableau_cumul_ca=tableau_cumul_ca,
    #     logo_path=logo_path 
    # )

    # # Générer le fichier PDF avec les images en mémoire
    # pdf_path = generate_pdf(report_html)

    # # 📌 Ajouter un bouton pour télécharger le PDF
    # # if pdf_path:
    # #     st.write(f"Le fichier PDF a été généré ici : {pdf_path}")
    # #     with open(pdf_path, "rb") as pdf_file:
    # #         st.download_button(
    # #             label="📥 Télécharger le rapport PDF",
    # #             data=pdf_file,
    # #             file_name="Customer_Report.pdf",
    # #             mime="application/pdf"
    # #         )




    # col6, col7 = st.columns(2)

    # # Répartition des coûts
    # with col6:
    #     st.subheader("Répartition des coûts par intervenant")
    #     if not final_float.empty:
    #         # Filtrer les intervenants ayant un CA Engagé > 0
    #         intervenants = intervenants[intervenants['CA Engagé'] > 0]
    #         # Calculer les pourcentages
    #         intervenants['Pourcentage'] = (intervenants['CA Engagé'] / intervenants['CA Engagé'].sum()) * 100

    #         # Générer une palette de bleu dégradé
    #         num_parts = len(intervenants)
    #         colors = [plt.cm.Blues(i / num_parts) for i in range(1, num_parts + 1)]
            
    #         def autopct_format(pct):
    #             return f'{pct:.1f}%' if pct > 1 else ''  # Cache les % trop petits
    #         # Création du pie chart
    #         piefig, ax = plt.subplots(figsize=(3, 3))
    #         wedges, texts, autotexts = ax.pie(
    #             intervenants['CA Engagé'], 
    #             labels=None, 
    #             autopct=autopct_format, 
    #             startangle=140, 
    #             colors=colors, 
    #             wedgeprops={'edgecolor': 'white'},
    #             pctdistance=0.75
    #         )
    #             # Ajuster la taille du texte des pourcentages
    #         for autotext in autotexts:
    #             autotext.set_fontsize(5)  # Réduction de la taille du texte des pourcentages
    #             # Construire les labels de légende avec les données
    #         legend_labels = [
    #             f"{row['Acteur']}\nCA: {int(round(row['CA Engagé'], 0)):,} €\nJours: {row['Jours Réalisés']}\nPart: {row['Pourcentage']:.1f}%"
    #             for _, row in intervenants.iterrows()
    #         ]
    #         # Remplacer les virgules par des espaces
    #         legend_labels = [label.replace(",", " ") for label in legend_labels]



    #         # Ajouter la légende en associant chaque wedge à son label
    #         ax.legend(
    #             handles=wedges, 
    #             labels=legend_labels, 
    #             title="Intervenants", 
    #             loc="center left", 
    #             bbox_to_anchor=(1, 0.5), 
    #             fontsize=5, 
    #             title_fontsize=5, 
    #             frameon=True, 
    #             markerscale=0.5
    #         )

    #         # Ajouter une légende associée aux couleurs
    #         #ax.legend(wedges, legend_labels, intervenants['Acteur'], title="Intervenants", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=5, title_fontsize=5, frameon=True, markerscale=0.5)
            
    #         # Ajouter un titre
    #         #ax.set_title("Répartition des coûts par intervenant")


    #         # Title and formatting
    #         #ax.set_title("Répartition des coûts par intervenant", fontsize=14, fontweight='bold')

    #         # Save the pie chart
    #         pie_chart_path = os.path.abspath("pie_chart.png")  # Absolute path
    #         plt.savefig(pie_chart_path, bbox_inches='tight', dpi=300)

    #         # Display in Streamlit
    #         st.pyplot(piefig)

    #     else:
    #         st.warning("Aucune donnée disponible pour afficher la répartition des coûts.")

    # # Répartition des heures réalisées
    # with col7:
    #     st.subheader("Jours Réalisés par Intervenant")
    #     if not intervenants.empty:
    #         # Création du bar chart
    #         barfig, ax = plt.subplots(figsize=(6, 4))  # Ajuster la taille
    #         bars = ax.bar(
    #             intervenants['Acteur'], 
    #             intervenants['Jours Réalisés'], 
    #             color=plt.cm.Blues(np.linspace(0.3, 1, len(intervenants)))  # Dégradé de bleu
    #         )
            
    #         # Ajouter les valeurs au-dessus des barres
    #         for bar, jours in zip(bars, intervenants['Jours Réalisés']):
    #             ax.text(
    #                 bar.get_x() + bar.get_width() / 2, 
    #                 bar.get_height(), 
    #                 f'{jours}', 
    #                 ha='center', va='bottom', fontsize=8
    #             )
            
    #         # Ajouter les labels et le titre
    #         ax.set_xlabel("Intervenants")
    #         ax.set_ylabel("Jours Réalisés")
                        
    #         # Afficher le graphique
    #         plt.xticks(rotation=45)  # Rotation des labels si nécessaire
    #         bar_chart_path = os.path.abspath("bar_chart.png")  # Absolute path
    #         plt.savefig(bar_chart_path, bbox_inches='tight', dpi=300)
    #         st.pyplot(barfig)
    #     else:
    #         print("Aucune donnée disponible pour afficher le graphique.")