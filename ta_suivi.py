        with st.expander("📊 Formations & Formateurs", expanded=True):
            st.subheader("Formations & Formateurs")

            # Harmonisation BU
            def normalize_bu(bu):
                if isinstance(bu, str):
                    return bu.strip().upper().replace("É", "E")
                return bu

            df_form["BU_clean"] = df_form["BU"].apply(normalize_bu)
            df_ta["BU_clean"] = df_ta["BU"].apply(normalize_bu)

            # Regroupement par BU
            form_counts = df_form.groupby("BU_clean").size()
            formateurs = df_form.groupby("BU_clean")["Formateur 1"].nunique()

            ta_obs = df_ta[df_ta["Type de TA"].str.lower().str.contains("observation", na=False)]
            ta_suivi = df_ta[df_ta["Type de TA"].str.lower().str.contains("suivi", na=False)]

            ta_obs_counts = ta_obs.groupby("BU_clean").size()
            ta_suivi_counts = ta_suivi.groupby("BU_clean").size()

            # Liste finale des BU à afficher
            bu_list = ["EUROPE", "RETAIL", "USA CANADA", "JAPON", "APAC CHINE"]

            data_summary = {
                "WSA 2024": [
                    "Nbre de formations",
                    "Nombre de formateurs",
                    "Nbre de TA Observation",
                    "Nbre de TA Suivi"
                ]
            }

            for bu in bu_list:
                data_summary[bu] = [
                    form_counts.get(bu, 0),
                    formateurs.get(bu, 0),
                    ta_obs_counts.get(bu, 0),
                    ta_suivi_counts.get(bu, 0)
                ]

            # Ajouter colonne TOTAL
            data_summary["TOTAL"] = [
                sum(form_counts),
                df_form["Formateur 1"].nunique(),
                len(ta_obs),
                len(ta_suivi)
            ]

            df_summary = pd.DataFrame(data_summary)

            # Mise en forme
            def highlight_blue(val):
                return "color: #1E88E5; font-weight: bold;" if isinstance(val, int) and val > 0 else ""

            styled_summary = df_summary.style.applymap(highlight_blue, subset=pd.IndexSlice[:, ["TOTAL"]])

            st.dataframe(styled_summary, height=300)