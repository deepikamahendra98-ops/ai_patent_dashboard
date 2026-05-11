import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Patent NIS Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .metric-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #1D9E75;
        margin-bottom: 8px;
    }
    .india-highlight { color: #1D9E75; font-weight: 600; }
    .stMetric label { font-size: 13px !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; }
    .insight-box {
        background: #e8f5f0;
        border-left: 4px solid #1D9E75;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 14px;
        line-height: 1.6;
        margin: 12px 0;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "nis_results")

@st.cache_data
def load_data():
    files = {
        "counts":  "nis_patent_counts.csv",
        "hhi":     "nis_hhi.csv",
        "div":     "nis_diversification.csv",
        "orig":    "nis_originality.csv",
        "loc":     "nis_localization.csv",
        "ctt":     "nis_ctt.csv",
        "pend":    "nis_pendency.csv",
    }
    data = {}
    for key, fname in files.items():
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            data[key] = pd.read_csv(path)
        else:
            st.error(f"Missing file: {path}")
            st.stop()
    return data

data = load_data()

COUNTRY_LABELS = {
    "US": "USA", "JP": "Japan", "CN": "China", "KR": "S. Korea",
    "DE": "Germany", "TW": "Taiwan", "IN": "India", "GB": "UK",
    "FR": "France", "RU": "Russia", "BR": "Brazil", "ZA": "S. Africa"
}
COUNTRY_COLORS = {
    "IN": "#1D9E75", "CN": "#E24B4A", "US": "#378ADD", "KR": "#BA7517",
    "JP": "#7F77DD", "DE": "#D4537E", "TW": "#639922", "GB": "#1D9E75",
    "FR": "#D85A30", "RU": "#888780", "BR": "#5DCAA5", "ZA": "#B4B2A9"
}
ALL_COUNTRIES = list(COUNTRY_LABELS.keys())
YEARS = list(range(2015, 2024))

def add_labels(df):
    df = df.copy()
    df["country_name"] = df["country"].map(COUNTRY_LABELS).fillna(df["country"])
    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 AI Patent NIS")
    st.markdown("**India vs Global Peers**")
    st.markdown("*2015 – 2023 · USPTO Data*")
    st.divider()

    page = st.radio("Navigate to", [
        "📊 Overview",
        "📈 Patent Counts",
        "🏢 HHI — Concentration",
        "🌐 Diversification",
        "💡 Originality",
        "📍 Localization",
        "⏱ Cycle Time (CTT)",
        "🕐 Pendency",
        "🕸 NIS Radar",
    ])

    st.divider()
    st.markdown("**Country filter**")
    selected_countries = st.multiselect(
        "Compare with India",
        [c for c in ALL_COUNTRIES if c != "IN"],
        default=["CN", "US", "KR", "JP", "DE"]
    )
    if "IN" not in selected_countries:
        selected_countries = ["IN"] + selected_countries

    selected_year = st.slider("Reference year", 2015, 2023, 2023)
    st.divider()
    st.caption("Data: USPTO pvgpatdis + AIPD 2023")
    st.caption("NIS framework: Lee et al. (2025)")

# ── HELPER: COLOUR LIST ───────────────────────────────────────────────────────
def get_colors(countries):
    return [COUNTRY_COLORS.get(c, "#B4B2A9") for c in countries]

# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    font_family="sans-serif",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font_size=11),
    xaxis=dict(showgrid=False, linecolor="#e0e0e0"),
    yaxis=dict(gridcolor="#f0f0f0", linecolor="#e0e0e0"),
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("🔬 AI Patent NIS Dashboard")
    st.markdown("**India's AI innovation performance benchmarked globally · 2015–2023**")

    counts = add_labels(data["counts"])
    yr_data = counts[counts["year"] == selected_year]
    india_row = yr_data[yr_data["country"] == "IN"]
    india_count = int(india_row["patent_count"].values[0]) if len(india_row) > 0 else 0
    india_share = float(india_row["global_share_pct"].values[0]) if len(india_row) > 0 else 0
    india_rank  = int(yr_data.sort_values("patent_count", ascending=False).reset_index(drop=True).query("country=='IN'").index[0]) + 1 if len(india_row) > 0 else "-"

    cn_count = int(yr_data[yr_data["country"]=="CN"]["patent_count"].values[0]) if len(yr_data[yr_data["country"]=="CN"]) > 0 else 1
    ratio = round(cn_count / india_count, 1) if india_count > 0 else "-"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("India AI patents", f"{india_count:,}", f"{selected_year}")
    c2.metric("Global rank", f"#{india_rank}", "of 12 countries")
    c3.metric("Global share", f"{india_share:.2f}%", "↑ from 1.26% in 2015")
    c4.metric("vs China", f"{ratio}×", "China has more")
    india_orig = data["orig"][data["orig"]["country"]=="IN"]
    orig_2023 = india_orig[india_orig["year"]==selected_year]["originality"].values
    c5.metric("Originality", f"{orig_2023[0]:.3f}" if len(orig_2023)>0 else "—", "#2 globally")
    india_loc = data["loc"][data["loc"]["country"]=="IN"]
    loc_2023 = india_loc[india_loc["year"]==selected_year]["localization"].values
    c6.metric("Localization", f"{loc_2023[0]:.4f}" if len(loc_2023)>0 else "—", "Last globally ⚠")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Patent count ranking — {selected_year}")
        rank_df = yr_data.sort_values("patent_count", ascending=True)
        rank_df["color"] = rank_df["country"].apply(lambda c: "#1D9E75" if c=="IN" else "#B4B2A9")
        fig = go.Figure(go.Bar(
            x=rank_df["patent_count"], y=rank_df["country_name"],
            orientation="h", marker_color=rank_df["color"].tolist(),
            text=rank_df["patent_count"].apply(lambda v: f"{v:,}"),
            textposition="outside"
        ))
        fig.update_layout(**PLOT_LAYOUT, height=380, title=f"AI patents granted {selected_year}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("India's global share trend")
        india_trend = counts[counts["country"]=="IN"].sort_values("year")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=india_trend["year"], y=india_trend["global_share_pct"],
            mode="lines+markers", line=dict(color="#1D9E75", width=2.5),
            fill="tozeroy", fillcolor="rgba(29,158,117,0.1)",
            name="India share %",
            text=[f"{v:.2f}%" for v in india_trend["global_share_pct"]],
            hovertemplate="%{x}: %{y:.2f}%"
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=380,
            yaxis_title="Global share (%)",
            title="India % of world AI patents")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("India vs China — growth trajectory")
    in_cn = counts[counts["country"].isin(["IN","CN"])].sort_values("year")
    fig3 = px.line(in_cn, x="year", y="patent_count", color="country",
        color_discrete_map={"IN":"#1D9E75","CN":"#E24B4A"},
        markers=True, labels={"patent_count":"Patents","country":"Country","year":"Year"})
    fig3.update_layout(**PLOT_LAYOUT, height=300)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>Key finding:</b> India ranks 7th globally with 45,218 AI patents (2015–2023).
    India's global share doubled from 1.26% to 2.37%, but China tripled from 3.3% to 8.5% in the same period.
    India's strongest NIS variable is <b>originality</b> (ranked #2 globally), while <b>localization</b> is its
    critical weakness — ranked last, indicating India has not yet built a self-reinforcing domestic AI knowledge ecosystem.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PATENT COUNTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Patent Counts":
    st.title("📈 AI Patent Counts")
    st.markdown("Annual AI-classified granted patents by inventor country · USPTO data")

    counts = add_labels(data["counts"])
    filt = counts[counts["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="patent_count", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"patent_count":"Patent count","country":"Country","year":"Year"},
            title="Annual AI patent counts")
        fig.update_layout(**PLOT_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(filt, x="year", y="global_share_pct", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"global_share_pct":"Global share (%)","country":"Country","year":"Year"},
            title="Global share % over time")
        fig2.update_layout(**PLOT_LAYOUT, height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader(f"Country ranking — {selected_year}")
    yr_df = add_labels(data["counts"][data["counts"]["year"]==selected_year]).sort_values("patent_count", ascending=False)
    yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
    fig3 = px.bar(yr_df, x="country_name", y="patent_count",
        color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
        text="patent_count",
        labels={"patent_count":"Patents","country_name":"Country"},
        title=f"All 12 countries — {selected_year}")
    fig3.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig3.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Full data table")
    show_df = data["counts"][data["counts"]["country"].isin(selected_countries)].copy()
    show_df["country_name"] = show_df["country"].map(COUNTRY_LABELS)
    show_df = show_df[["country_name","year","patent_count","global_share_pct"]].sort_values(["year","patent_count"], ascending=[True,False])
    show_df.columns = ["Country","Year","Patent count","Global share (%)"]
    st.dataframe(show_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HHI
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏢 HHI — Concentration":
    st.title("🏢 HHI — Assignee Concentration")
    st.markdown("Herfindahl-Hirschman Index measures how concentrated AI patents are among assignees. **Higher = fewer organisations dominate.**")

    hhi = add_labels(data["hhi"])
    filt = hhi[hhi["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="hhi", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"hhi":"HHI","country":"Country","year":"Year"},
            title="HHI trend over time")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["hhi"][data["hhi"]["year"]==selected_year]).sort_values("hhi", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="hhi",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["hhi"].round(4),
            title=f"HHI ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India HHI (0.017 in 2023):</b> Moderate concentration — a handful of large IT firms (TCS, Infosys, Wipro)
    and IITs dominate India's AI patents. South Korea (0.171) is the most concentrated globally, dominated by
    Samsung and LG — yet Korea dramatically outperforms India in output. This supports Lee (2013)'s argument
    that during catch-up, concentrated large players can be an advantage. India's HHI is slowly declining,
    suggesting more organisations are entering the AI patent space.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DIVERSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Diversification":
    st.title("🌐 Technological Diversification")
    st.markdown("Proportion of CPC subclasses (out of 1339) covered by each country's AI patents. **Higher = broader technology coverage.**")

    div = add_labels(data["div"])
    filt = div[div["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="diversification", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"diversification":"Diversification index","country":"Country","year":"Year"},
            title="Diversification trend")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["div"][data["div"]["year"]==selected_year]).sort_values("diversification", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="diversification",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["diversification"].round(3),
            title=f"Diversification ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Unique CPC subclasses covered")
    sub_df = div[div["country"].isin(selected_countries) & (div["year"]==selected_year)][["country","unique_cpc_subclasses","diversification"]].copy()
    sub_df["country"] = sub_df["country"].map(COUNTRY_LABELS)
    sub_df.columns = ["Country","Unique subclasses","Diversification index"]
    sub_df = sub_df.sort_values("Unique subclasses", ascending=False)
    st.dataframe(sub_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India covers 374 of 1339 CPC subclasses (28%) in 2023</b> — significantly lower than the US (47%), China (43%)
    and Japan (43%). India's AI patents cluster in software and ICT-adjacent domains rather than spanning hardware,
    biotech, robotics and other AI application areas. Diversification has grown from 22% to 28% — positive momentum,
    but the gap with leading nations is structural and reflects India's service-sector-dominated innovation base.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ORIGINALITY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Originality":
    st.title("💡 Originality")
    st.markdown("Measures how broadly a patent draws on diverse technology fields when citing prior work (1 − HHI of cited patent classes). **Higher = more cross-field innovation.**")

    orig = add_labels(data["orig"])
    filt = orig[orig["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="originality", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"originality":"Originality","country":"Country","year":"Year"},
            title="Originality trend")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["orig"][data["orig"]["year"]==selected_year]).sort_values("originality", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="originality",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["originality"].round(3),
            title=f"Originality ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India's strongest NIS metric — ranked #2 globally in 2023 (0.235).</b>
    India's originality surpasses China (0.176) and Japan (0.174), approaching the US level (0.291).
    This means Indian AI patents draw on a wide variety of technological fields — a sign of maturing, integrative
    innovation capability. The rapid rise from near-zero in 2015 reflects India's growing research maturity,
    particularly from IITs and global R&D centres of US tech companies operating in India.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOCALIZATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📍 Localization":
    st.title("📍 Localization")
    st.markdown("Self-citation rate minus external citation rate. Measures whether a country's AI innovation builds on its own prior domestic work. **Higher = stronger domestic knowledge ecosystem.**")

    loc = add_labels(data["loc"])
    filt = loc[loc["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="localization", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"localization":"Localization","country":"Country","year":"Year"},
            title="Localization trend")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["loc"][data["loc"]["year"]==selected_year]).sort_values("localization", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="localization",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["localization"].round(4),
            title=f"Localization ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Self-cite rate vs External cite rate")
    loc_detail = data["loc"][data["loc"]["country"].isin(selected_countries) & (data["loc"]["year"]==selected_year)].copy()
    loc_detail["country_name"] = loc_detail["country"].map(COUNTRY_LABELS)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Self-cite rate", x=loc_detail["country_name"], y=loc_detail["self_cite_rate"],
        marker_color="#1D9E75"))
    fig3.add_trace(go.Bar(name="External cite rate", x=loc_detail["country_name"], y=loc_detail["external_cite_rate"],
        marker_color="#E24B4A"))
    fig3.update_layout(**PLOT_LAYOUT, barmode="group", height=320,
        title=f"Self-citation vs external citation rate — {selected_year}")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India ranks last in localization (0.046 in 2023)</b> — the most critical structural weakness identified.
    Japan (0.181) and South Korea (0.164) have built deep domestic knowledge ecosystems where researchers
    heavily cite prior domestic AI work. India's near-zero localization means AI innovation here still depends
    almost entirely on foreign knowledge bases. This suggests India's IT services model — implementing foreign
    technology rather than building foundational IP — has not yet transitioned to genuine knowledge creation.
    Policy implication: India needs stronger domestic R&D investment, university-industry linkages,
    and incentives for researchers to build on Indian prior art.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CTT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⏱ Cycle Time (CTT)":
    st.title("⏱ Cycle Time of Technology")
    st.markdown("Average age (in years) of patents cited by each country's AI patents. **Shorter CTT = building on newer, faster-moving knowledge.** Per Lee (2013), short CTT is favourable for catching-up economies.")

    ctt = add_labels(data["ctt"])
    filt = ctt[ctt["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="avg_citation_age", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"avg_citation_age":"Avg citation age (years)","country":"Country","year":"Year"},
            title="CTT trend — average citation age")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["ctt"][data["ctt"]["year"]==selected_year]).sort_values("avg_citation_age", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="avg_citation_age",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["avg_citation_age"].round(1),
            title=f"CTT ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India's CTT (~11.5 years) sits in the middle of the global range.</b>
    Fast-cycle countries: Taiwan (10.2y), China (10.8y), South Korea (10.9y).
    Slow-cycle countries: Germany (14.2y), USA (13.5y).
    India is positioned reasonably — building on moderately recent knowledge, which is
    appropriate for a catching-up economy. However India's CTT has crept upward since 2020,
    suggesting a mild shift toward older knowledge bases, which warrants monitoring.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PENDENCY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🕐 Pendency":
    st.title("🕐 Patent Pendency")
    st.markdown("Average years between patent filing date and grant date. Reflects patent office efficiency and processing capacity.")

    pend = add_labels(data["pend"])
    filt = pend[pend["country"].isin(selected_countries)].sort_values("year")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(filt, x="year", y="avg_pendency_years", color="country",
            color_discrete_map=COUNTRY_COLORS, markers=True,
            labels={"avg_pendency_years":"Avg pendency (years)","country":"Country","year":"Year"},
            title="Patent pendency trend")
        fig.update_layout(**PLOT_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yr_df = add_labels(data["pend"][data["pend"]["year"]==selected_year]).sort_values("avg_pendency_years", ascending=False)
        yr_df["highlight"] = yr_df["country"].apply(lambda c: "India" if c=="IN" else "Other")
        fig2 = px.bar(yr_df, x="country_name", y="avg_pendency_years",
            color="highlight", color_discrete_map={"India":"#1D9E75","Other":"#B4B2A9"},
            text=yr_df["avg_pendency_years"].round(2),
            title=f"Pendency ranking — {selected_year}")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India's pendency (2.46 years in 2023) is among the shortest</b> — better than France (3.40y),
    Germany (3.24y) and Japan (2.77y). This is a surprising positive finding: India's patent office
    processes AI patents relatively quickly compared to peers. However, this may partly reflect the
    smaller volume of applications making processing easier. As India's patent filing volume grows,
    pendency will be a key metric to monitor.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: NIS RADAR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🕸 NIS Radar":
    st.title("🕸 NIS Radar — All Variables")
    st.markdown(f"Normalised comparison of all 5 NIS variables across selected countries · {selected_year}")

    def get_val(df, country, year, col):
        row = df[(df["country"]==country) & (df["year"]==year)]
        return float(row[col].values[0]) if len(row) > 0 else 0.0

    radar_countries = [c for c in selected_countries if c in ALL_COUNTRIES]

    raw = {}
    for c in radar_countries:
        raw[c] = {
            "Originality":      get_val(data["orig"], c, selected_year, "originality"),
            "Localization":     get_val(data["loc"],  c, selected_year, "localization"),
            "Diversification":  get_val(data["div"],  c, selected_year, "diversification"),
            "1/HHI (distrib.)": 1 - get_val(data["hhi"], c, selected_year, "hhi"),
            "Short CTT":        1 / max(get_val(data["ctt"], c, selected_year, "avg_citation_age"), 0.1),
        }

    dims = ["Originality","Localization","Diversification","1/HHI (distrib.)","Short CTT"]
    for dim in dims:
        vals = [raw[c][dim] for c in radar_countries]
        mn, mx = min(vals), max(vals)
        for c in radar_countries:
            raw[c][dim] = (raw[c][dim] - mn) / (mx - mn) if mx > mn else 0.5

    fig = go.Figure()
    for c in radar_countries:
        vals = [raw[c][d] for d in dims] + [raw[c][dims[0]]]
        trace_kwargs = dict(
            r=vals,
            theta=dims + [dims[0]],
            fill="toself" if c == "IN" else "none",
            name=COUNTRY_LABELS.get(c, c),
            line=dict(
                color=COUNTRY_COLORS.get(c, "#B4B2A9"),
                width=3 if c == "IN" else 1.5
            ),
            opacity=0.85 if c == "IN" else 1.0,
        )
        if c == "IN":
            trace_kwargs["fillcolor"] = "rgba(29,158,117,0.15)"
        fig.add_trace(go.Scatterpolar(**trace_kwargs))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], tickfont_size=10, gridcolor="#e0e0e0"),
            angularaxis=dict(tickfont_size=12)
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=520, margin=dict(l=60,r=60,t=40,b=80),
        paper_bgcolor="white", plot_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"NIS variable summary table — {selected_year}")
    rows = []
    for c in radar_countries:
        rows.append({
            "Country":         COUNTRY_LABELS.get(c, c),
            "Patents":         int(get_val(data["counts"], c, selected_year, "patent_count")),
            "Originality":     round(get_val(data["orig"], c, selected_year, "originality"), 3),
            "Localization":    round(get_val(data["loc"],  c, selected_year, "localization"), 4),
            "Diversification": round(get_val(data["div"],  c, selected_year, "diversification"), 3),
            "HHI":             round(get_val(data["hhi"],  c, selected_year, "hhi"), 4),
            "CTT (yrs)":       round(get_val(data["ctt"],  c, selected_year, "avg_citation_age"), 2),
            "Pendency (yrs)":  round(get_val(data["pend"], c, selected_year, "avg_pendency_years"), 2),
        })
    summary_df = pd.DataFrame(rows).sort_values("Patents", ascending=False)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='insight-box'>
    <b>India's NIS profile (green shape):</b> Strong on originality, weak on localization and diversification.
    The shape reflects a country with creative cross-disciplinary innovation but limited domestic
    knowledge accumulation and technology breadth — characteristic of a service-led economy
    transitioning toward product innovation.
    </div>
    """, unsafe_allow_html=True)
