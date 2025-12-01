# app.py — Production-Ready STAG vs PROD Expired URLs Dashboard
# Deploy instantly: https://share.streamlit.io

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ========================= CONFIG =========================
st.set_page_config(
    page_title="STAG vs PROD – Expired URLs Monitor",
    page_icon="Chart with red and green bars",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/yourname/stag-prod-dashboard",
        "Report a bug": "https://github.com/yourname/stag-prod-dashboard/issues",
        "About": "Real-time comparison of expired video URLs between Staging and Production"
    }
)

# ========================= STYLING =========================
st.markdown("""
<style>
    .big-font {font-size: 28px !important; font-weight: bold;}
    .metric-good {color: #00aa00; background: #e6ffe6; padding: 10px; border-radius: 10px;}
    .metric-bad  {color: #aa0000; background: #ffe6e6; padding: 10px; border-radius: 10px;}
    .stPlotlyChart {margin-bottom: 0;}
    .block-container {padding-top: 2rem;}
    .footer {text-align: center; color: #888; margin-top: 4rem; font-size: 14px;}
    .stButton>button {width: 100%; height: 50px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)


# ========================= DATA LOADER =========================
@st.cache_data(ttl=1800, show_spinner="Loading data...")  # 30 min cache
def load_data(file_path: str, env_name: str) -> pd.DataFrame:
    path = Path(file_path)

    # Auto-create realistic mock data if files don't exist (great for demo/deploy)
    if not path.exists():
        st.warning(f"{path.name} not found → using realistic mock data")
        mock = [
            {"mappedOfferId": f"{env_name[0]}{i:05d}",
             "videoURLs": [{"videoURL": f"https://{env_name.lower()}.cdn.example.com/v{i}.mp4"}],
             "expired": f"2024-{'%02d' % ((i % 12) + 1)}-01T00:00:00Z" if env_name == "Staging" else f"2023-{'%02d' % ((i % 10) + 1)}-15T00:00:00Z"}
            for i in range(1, 350 if env_name == "Staging" else 280)
        ]
        path.write_text(json.dumps(mock))

    data = json.load(open(path))
    df = pd.DataFrame(data)
    df["videoURL"] = df["videoURLs"].apply(lambda x: x[0]["videoURL"] if x else None)
    df["expired"] = pd.to_datetime(df["expired"])
    df["year"] = df["expired"].dt.year
    df["month"] = df["expired"].dt.month
    df["month_year"] = df["expired"].dt.strftime("%Y-%m")  # Clean string for Plotly
    df["env"] = env_name
    return df.drop(columns=["videoURLs"], errors="ignore")


# ========================= URL VALIDATOR =========================
def check_url(url: str) -> dict:
    try:
        start = time.time()
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "HealthCheck"})
        rt = int((time.time() - start) * 1000)
        return {"videoURL": url, "alive": r.status_code < 400, "status": r.status_code, "rt_ms": rt}
    except:
        return {"videoURL": url, "alive": False, "status": "Error", "rt_ms": None}


@st.cache_data(ttl=3600)
def validate_urls(df: pd.DataFrame) -> pd.DataFrame:
    urls = df["videoURL"].dropna().unique().tolist()
    results = []
    with ThreadPoolExecutor(max_workers=30) as pool:
        futures = [pool.submit(check_url, url) for url in urls]
        for f in st.progress(futures, text="Validating URLs..."):
            results.append(f.result())
    return pd.DataFrame(results)


# ========================= MAIN APP =========================
def main():
    st.title("STAG vs PROD Expired URLs Monitor")

    # Load data
    with st.spinner("Loading environments..."):
        stag = load_data("mtcms-stag-response.json", "Staging")
        prod = load_data("mtcms-prod-response.json", "Production")
        combined = pd.concat([stag, prod], ignore_index=True)

    # Header Metrics
    diff = len(stag) - len(prod)
    pct = diff / len(prod) * 100 if len(prod) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Staging", f"{len(stag):,}")
    with c2:
        st.metric("Production", f"{len(prod):,}", delta=f"{diff:+,}")
    with c3:
        if diff > 0:
            st.markdown(f"<div class='metric-bad big-font'>+{pct:.1f}% more</div>", unsafe_allow_html=True)
        elif diff < 0:
            st.markdown(f"<div class='metric-good big-font'>{pct:.1f}% fewer</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='big-font'>Synced!</div>", unsafe_allow_html=True)
    with c4:
        st.caption(f"Last updated: {datetime.now():%b %d, %Y %H:%M}")

    st.markdown("---")

    # Global Year Filter
    years = sorted(combined["year"].unique(), reverse=True)
    selected_year = st.selectbox("Focus Year", years, index=0)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Drilldown", "Deep Diff", "URL Health"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            yearly = combined.groupby(["year", "env"], as_index=False).size()
            fig = px.bar(yearly, x="year", y="size", color="env", barmode="group",
                         color_discrete_map={"Staging": "#ff4444", "Production": "#00aa88"})
            fig.update_traces(texttemplate="%{y}", textposition="outside")
            st.plotly_chart(fig, width='stretch')
        with col2:
            monthly = combined[combined["year"] == selected_year].groupby(["month_year", "env"], as_index=False).size()
            fig2 = px.line(monthly, x="month_year", y="size", color="env", markers=True,
                           color_discrete_map={"Staging": "#ff4444", "Production": "#00aa88"})
            st.plotly_chart(fig2, width='stretch')

    with tab2:
        data = combined[combined["year"] == selected_year][["env", "mappedOfferId", "videoURL", "expired"]]
        st.dataframe(data.sort_values(["env", "expired"]), height=800, hide_index=True)

    with tab3:
        only_stag = stag[~stag["videoURL"].isin(prod["videoURL"])]
        only_prod = prod[~prod["videoURL"].isin(stag["videoURL"])]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Only in Staging")
            st.metric("Count", len(only_stag))
            st.dataframe(only_stag[["mappedOfferId", "videoURL"]], height=600)
        with c2:
            st.subheader("Only in Production")
            st.metric("Count", len(only_prod))
            st.dataframe(only_prod[["mappedOfferId", "videoURL"]], height=600)

    with tab4:
        if st.button("Run URL Health Check", type="primary", use_container_width=True):
            with st.spinner("Checking all unique URLs..."):
                results = validate_urls(combined)
                st.session_state.health = results
            st.success("Done!")

        if "health" in st.session_state:
            df = st.session_state.health
            alive = df["alive"].sum()
            st.write(f"**{len(df)} URLs** → **{alive} alive** | **{len(df) - alive} broken**")
            styled = df.style.apply(lambda row: ["background:#d4edda" if row.alive else "#f8d7da"] * len(row), axis=1)
            st.dataframe(styled, height=700)
            st.download_button("Export CSV", df.to_csv(index=False), "url_health.csv")

    st.markdown("<div class='footer'>Production-Ready • Auto-mock • Zero config • Deploy anywhere</div>",
                unsafe_allow_html=True)


# ========================= RUN =========================
if __name__ == "__main__":
    main()
