import streamlit as st
import pandas as pd
import plotly.express as px

# Page config & Styling
st.set_page_config(page_title="ALIGN Prototype", layout="wide")
# Global font and sticky sidebar title styling
st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }
        /* Sticky Sidebar Title */
        [data-testid="stSidebar"] h1 {
            position: sticky;
            top: 0;
            background-color: #f0f2f6;
            z-index: 1000;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #ddd;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("fake_align_dataset.csv")
        df["topic"] = df["topic"].str.lower()
        return df
    except FileNotFoundError:
        st.error("Dataset not found. Ensure 'fake_align_dataset.csv' is in the app folder.")
        st.stop()

# Main DataFrame
df = load_data()

# ---- Sidebar: ALIGN Prototype title & filters ----
with st.sidebar:
    st.title("ALIGN Prototype")
    st.header("Filters & Options")

    # Year range slider
    years = sorted(df["year"].unique())
    if 2017 in years:
        years.remove(2017)
    start_year, end_year = st.select_slider(
        "Year range",
        options=years,
        value=(years[0], years[-1]),
        format_func=lambda x: str(x),
        help="2017 is skipped; data from 2017 is grouped into 2018"
    )
    df_filtered = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    # Chapter-topic mapping
    chapter_map = {
        "democracy_section": [
            "elections", "parliament", "governance",
            "civilian_oversight_of_the_security_services", "civil_societies"
        ],
        "public_administration_reform_section": [
            "strategic_framework_for_public_administration_reform",
            "policy_development_and_coordination",
            "public_financial_management",
            "public_service_and_human_resources_management",
            "accountability_of_administration",
            "service_delivery_to_citizens_and_businesses"
        ],
        "23_Judiciary_and_fundamental_rights": [
            "functioning_of_the_judiciary",
            "domestic_processing_of_war_crimes",
            "fight_against_corruption",
            "fundamental_rights",
            "freedom_of_expression"
        ],
        "24_Justice_freedom_and_security": [
            "fight_against_organised_crime",
            "cooperation_in_the_field_of_drugs",
            "fight_against_terrorism",
            "judicial_cooperation_in_civil_commercial_and_criminal_matters",
            "legal_and_irregular_migration",
            "asylum",
            "visa_policy",
            "schengen_and_external_borders"
        ]
    }
    all_topics = [t for topics in chapter_map.values() for t in topics]

    # Quick-topic groups
    st.markdown("**Quick topic groups**")
    sel_dem = st.checkbox("All Democracy topics")
    sel_par = st.checkbox("All Public Admin Reform topics")
    sel_23 = st.checkbox("All Chapter 23 – Judiciary and fundamental rights")
    sel_24 = st.checkbox("All Chapter 24 – Justice, freedom and security")

    # Manual topic selection
    manual_sel = st.multiselect(
        "Select Topics (manual)",
        options=all_topics,
        default=[]
    )
    topics_sel = set(manual_sel)
    if sel_dem:
        topics_sel.update(chapter_map["democracy_section"])
    if sel_par:
        topics_sel.update(chapter_map["public_administration_reform_section"])
    if sel_23:
        topics_sel.update(chapter_map["23_Judiciary_and_fundamental_rights"])
    if sel_24:
        topics_sel.update(chapter_map["24_Justice_freedom_and_security"])
    topics_sel = list(topics_sel)

    # Chapter selector (disabled if topics selected)
    chap_sel = st.multiselect(
        "Select Chapters",
        options=list(chapter_map.keys()),
        default=list(chapter_map.keys()),
        disabled=bool(topics_sel),
        help="Disabled when topics are selected"
    )

    # Institution & paragraph-topic selectors (only no chapters/topics)
    inst_opts = sorted(df_filtered["institution"].dropna().unique())
    institutions_sel = st.multiselect(
        "Select Institutions",
        options=inst_opts,
        disabled=bool(topics_sel) or bool(chap_sel),
        help="Enabled only when no chapters or topics are selected"
    )
    para_opts = sorted(df_filtered["paragraph_topic"].dropna().unique())
    para_sel = st.multiselect(
        "Select Paragraph Topics",
        options=para_opts,
        disabled=bool(topics_sel) or bool(chap_sel),
        help="Enabled only when no chapters or topics are selected"
    )

    # Future feature placeholders
    st.checkbox("Effort Type (Domestic/International)", disabled=True)
    st.checkbox("Domain (Politics/Economy)", disabled=True)

    # View & zero toggle
    view_mode = st.selectbox(
        "View Mode",
        options=["Year-by-Year", "Aggregated"],
        index=0
    )
    include_zero = st.checkbox(
        "Include neutral (0) sentences",
        value=False
    )

    # Chart type logic: force bar when institutions selected
    span = end_year - start_year + 1
    if institutions_sel:
        chart_types = ["Bar chart"]
    else:
        if view_mode == "Aggregated" or span <= 1:
            chart_types = ["Bar chart"]
        elif span < 5:
            chart_types = ["Bar chart", "Line chart"]
        else:
            chart_types = ["Line chart", "Bar chart"]
    chart_type = st.selectbox(
        "Chart Type",
        options=chart_types,
        index=0,
        disabled=bool(institutions_sel),
        help="Bar chart only when institutions selected"
    )

    # Display mode
    if institutions_sel or para_sel:
        disp_modes = ["Count of Evaluated Sentences"]
    else:
        disp_modes = ["Average Evaluation"]
        if institutions_sel or para_sel:
            disp_modes.append("Count of Evaluated Sentences")
    disp_mode = st.selectbox("Display Mode", disp_modes)

        # Title on export (always enabled)
    include_title = True
    # Show toggle for consistency but disable it
    st.checkbox(
        "Include Title on Export",
        value=True,
        disabled=True,
        help="Title inclusion on download is always on"
    )

# --- Prototype info above graph ---
st.markdown("**ALIGN PROTOTYPE**")
st.markdown(
    "This prototype is powered by demo data — and it needs your support to grow. "
    "With real data, ALIGN could offer powerful insights into democratic backsliding, legal harmonization, and international cooperation."
)
st.markdown("⚠️ Prototype based on FAKE DATA - FOR PRESENTATION PURPOSES ONLY")

# --- Data filtering ---
filtered = df_filtered.copy()
# Priority of filters: topics > paragraph topics > chapters
if topics_sel:
    filtered = filtered[filtered["topic"].isin(topics_sel)]
elif para_sel:
    filtered = filtered[filtered["paragraph_topic"].isin(para_sel)]
elif chap_sel:
    filtered = filtered[filtered["chapter"].isin(chap_sel)]
# Zero-value exclusion for average mode
if not include_zero and disp_mode == "Average Evaluation":
    filtered = filtered[filtered["value"] != 0]
if filtered.empty:
    st.info("Nothing to see here... but some regimes would still call it transparent.")
    st.stop()
    st.info("Nothing to see here... but some regimes would still call it transparent.")
    st.stop()

# --- Plot construction ---
if institutions_sel:
    # Show aggregated count per institution with distinct colors
    df_plot = filtered.groupby("institution").size().reset_index(name="count")
    fig = px.bar(
        df_plot,
        x="institution", y="count",
        color="institution",
        labels={"count":"Sentence Count","institution":"Institution"},
        text_auto=".0f"
    )
else:
    if view_mode == "Year-by-Year":
        if disp_mode == "Average Evaluation":
            axis = "topic" if topics_sel else "chapter"
            df_plot = filtered.groupby(["year", axis])["value"].mean().reset_index()
            if chart_type == "Line chart":
                fig = px.line(
                    df_plot, x="year", y="value", color=axis, markers=True,
                    labels={"value":"Avg Score", axis:axis}
                )
                fig.update_traces(
                    text=df_plot["value"],
                    texttemplate="%{text:.2f}",
                    textposition="top center"
                )
            else:
                fig = px.bar(
                    df_plot, x="year", y="value", color=axis, barmode="group",
                    labels={"value":"Avg Score", axis:axis},
                    text_auto=".2f"
                )
            fig.add_hline(y=0, line_dash="solid", line_color="#888888", line_width=0.5)
        else:
            axis = "institution" if institutions_sel else "paragraph_topic"
            df_plot = filtered.groupby(["year", axis]).size().reset_index(name="count")
            if chart_type == "Line chart":
                fig = px.line(
                    df_plot, x="year", y="count", color=axis, markers=True,
                    labels={"count":"Sentence Count"}
                )
                fig.update_traces(marker=dict(size=4))
            else:
                fig = px.bar(
                    df_plot, x="year", y="count", color=axis, barmode="group",
                    labels={"count":"Sentence Count"}, text_auto=".0f"
                )
    else:
        if disp_mode == "Average Evaluation":
            axis = "topic" if topics_sel else "chapter"
            df_plot = filtered.groupby(axis)["value"].mean().reset_index().sort_values("value", ascending=False)
            fig = px.bar(
                df_plot, x=axis, y="value", color=axis,
                labels={"value":"Avg Score", axis:axis}, text_auto=".2f"
            )
        else:
            df_plot = filtered.groupby("topic").size().reset_index(name="count")
            fig = px.bar(
                df_plot, x="topic", y="count", color="topic",
                labels={"count":"Sentence Count","topic":"Topic"}, text_auto=".0f"
            )

# --- Styling and reference ---
fig.update_layout(
    template="simple_white",
    title="",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    font=dict(color="#111111"),
    title_font=dict(size=18)
)
fig.update_xaxes(tickmode="linear", dtick=1)
if not topics_sel and len(chap_sel) == 1 and view_mode == "Year-by-Year" and disp_mode == "Average Evaluation":
    avg_df = filtered.groupby("year")["value"].mean().reset_index()
    fig.add_scatter(
        x=avg_df["year"],
        y=avg_df["value"],
        mode="lines",
        line=dict(dash="dash", width=1, color="#888888"),
        name=f"{chap_sel[0]} avg"
    )

# --- Render & Download ---
st.plotly_chart(fig, use_container_width=True)
col1, col2 = st.columns(2)
with col1:
    try:
        png = fig.to_image(format="png", engine="kaleido")
        if st.download_button(
            "Download PNG", data=png, file_name="align_chart.png", mime="image/png"
        ):
            st.success("PNG downloaded!")
    except:
        st.error("Install kaleido: pip install -U kaleido")
with col2:
    csv_data = filtered.to_csv(index=False).encode()
    if st.download_button(
        "Download CSV", data=csv_data, file_name="align_data.csv", mime="text/csv"
    ):
        st.success("CSV downloaded!")

# Graph Description
st.markdown("---")
st.markdown("#### Graph Description")
st.markdown(
    f"""
    <div style='max-height:150px; overflow-y:auto; font-size:0.9em; padding:8px; border:1px solid #ddd; border-radius:4px;'>
      <p><strong>Time Range:</strong> {start_year}–{end_year}</p>
      <p><strong>Data Type:</strong> {disp_mode}</p>
      <p><strong>Selected Filters:</strong> {'Topics: ' + ', '.join(topics_sel) if topics_sel else 'Chapters: ' + ', '.join(chap_sel)}</p>
      <p><strong>Zero-Value:</strong> {'Included' if include_zero else 'Excluded'}</p>
      <p><strong>Graph Type:</strong> {chart_type} ({view_mode})</p>
      <p style='color:#D9534F;'><strong>Caution:</strong> Results based on less than 15 sentences may be less reliable.</p>
      <p><em>Source:</em> European Commission country reports for selected country and time span.</p>
      <p><em>Interpretation Note:</em> These results reflect the EC's framing, not an objective measure of progress.</p>
      <p><em>Attribution:</em> ALIGN Prototype (2025), built on fake dataset for presentation purposes.</p>
    </div>
    """,
    unsafe_allow_html=True
)
# --- Footer ---
st.markdown("---")
st.markdown(
    "Learn more by visiting [reformtrack.org](https://reformtrack.org) | Reform Track © 2025. Not for commercial use."
)

# Developer mode
st.sidebar.markdown("---")
if st.sidebar.text_input("Dev password", type="password") == "Alignsova9@":
    if st.sidebar.checkbox("Show debug info"):
        st.sidebar.write(df.head())
