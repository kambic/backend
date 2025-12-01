# app.py
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
    page_icon="Chart",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================= STYLING =========================
st.markdown("""
<style>
    .big-font {font-size: 28px !important; font-weight: bold;}
    .metric-good {color: #00aa00; background: #e6ffe6; padding: 10px; border-radius: 10px;}
    .metric-bad  {color: #aa0000; background: #ffe6e6; padding: 10px; border-radius: 10px;}
    .footer {text-align: center; color: #888; margin-top: 4rem;}
</style>
""", unsafe_allow_html=True)

# ========================= DATA LOADER =========================
@st.cache_data(ttl=1800)
def load_data(file_path: str, env_name: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        st.warning(f"{path.name} missing → generating mock data")
        mock = [
            {"mappedOfferId": f"{env_name[0]}{i:05d}",
             "videoURLs": [{"videoURL": f"https://{env_name.lower()}.example.com/v{i}.mp4"}],
             "expired": f"2024-{'%02d' % ((i % 12) + 1)}-01T00:00:00Z" if env_name == "Staging" else f"2023-{'%02d' % ((i % 10) + 1)}-15T00:00:00Z"}
            for i in range(1, 400 if env_name == "Staging" else 320)
        ]
        path.write_text(json.dumps(mock))

    df = pd.DataFrame(json.load(open(path)))
    df["videoURL"] = df["videoURLs"].apply(lambda x: x[0]["videoURL"] if x else None)
    df["expired"] = pd.to_datetime(df["expired"])
    df["year"] = df["expired"].dt.year
    df["month_year"] = df["expired"].dt.strftime("%Y-%m")
    df["env"] = env_name
    return df.drop(columns=["videoURLs"], errors="ignore")

# ========================= URL HEALTH =========================
def check_url(url: str):
    try:
        start = time.time()
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Monitor"})
        return {"videoURL": url, "alive": r.status_code < 400, "status": r.status_code, "rt_ms": int((time.time()-start)*1000)}
    except:
        return {"videoURL": url, "alive": False, "status": "Error", "rt_ms": None}

@st.cache_data(ttl=3600)
def validate_urls(df: pd.DataFrame) -> pd.DataFrame:
    urls = df["videoURL"].dropna().unique()
    results = []
    with ThreadPoolExecutor(max_workers=30) as pool:
        for future in st.progress([pool.submit(check_url, u) for u in urls], text="Checking URLs..."):
            results.append(future.result())
    return pd.DataFrame(results)

# ========================= MAIN =========================
def main():
    st.title("STAG vs PROD – Expired URLs Deep Monitor")

    stag = load_data("mtcms-stag-response.json", "Staging")
    prod = load_data("mtcms-prod-response.json", "Production")
    combined = pd.concat([stag, prod], ignore_index=True)

    # Header
    diff = len(stag) - len(prod)
    pct = diff / len(prod) * 100 if len(prod) > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Staging", f"{len(stag):,}")
    with c2: st.metric("Production", f"{len(prod):,}", delta=f"{diff:+,}")
    with c3:
        cls = "metric-bad" if diff > 0 else "metric-good"
        st.markdown(f"<div class='{cls} big-font'>{pct:+.1f}%</div>", unsafe_allow_html=True)
    with c4: st.caption(f"Updated: {datetime.now():%b %d, %Y %H:%M}")

    st.markdown("---")

    # Global Year Filter
    years = sorted(combined["year"].unique(), reverse=True)
    selected_year = st.selectbox("Focus Year", years, index=0, key="year_filter")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Drilldown", "Deep Diff (by Year)", "URL Health"])

    with tab1:
        col1, col2 = st.columns([3, 2])
        with col1:
            fig = px.bar(combined.groupby(["year", "env"], as_index=False).size(),
                         x="year", y="size", color="env", barmode="group",
                         color_discrete_map={"Staging": "#ff4444", "Production": "#00aa88"})
            fig.update_traces(texttemplate="%{y}", textposition="outside")
            st.plotly_chart(fig, width='stretch')
        with col2:
            monthly = combined[combined["year"] == selected_year].groupby(["month_year", "env"], as_index=False).size()
            fig2 = px.line(monthly, x="month_year", y="size", color="env", markers=True)
            st.plotly_chart(fig2, width='stretch')

    with tab2:
        data = combined[combined["year"] == selected_year][["env", "mappedOfferId", "videoURL", "expired"]]
        st.dataframe(data.sort_values(["env", "expired"]), height=800, hide_index=True)

    with tab3:  # DEEP DIFF — NOW FILTERED BY YEAR
        stag_year = stag[stag["year"] == selected_year]
        prod_year = prod[prod["year"] == selected_year]

        only_stag = stag_year[~stag_year["videoURL"].isin(prod_year["videoURL"])]
        only_prod = prod_year[~prod_year["videoURL"].isin(stag_year["videoURL"])]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Only in Staging ({selected_year})")
            st.metric("Count", len(only_stag))
            if len(only_stag) > 0:
                st.dataframe(only_stag[["mappedOfferId", "videoURL", "expired"]], height=700)
            else:
                st.success("No unique URLs")

        with col2:
            st.subheader(f"Only in Production ({selected_year})")
            st.metric("Count", len(only_prod))
            if len(only_prod) > 0:
                st.dataframe(only_prod[["mappedOfferId", "videoURL", "expired"]], height=700)
            else:
                st.success("Synced")

    with tab4:
        if st.button("Run URL Health Check", type="primary", use_container_width=True):
            with st.spinner("Validating all URLs..."):
                st.session_state.health = validate_urls(combined)
            st.success("Complete!")

        if "health" in st.session_state:
            df = st.session_state.health
            alive = df["alive"].sum()
            st.write(f"**{len(df)} URLs** → **{alive} alive** | **{len(df)-alive} broken**")
            styled = df.style.apply(lambda r: ["background:#d4edda" if r.alive else "#f8d7da"] * len(r), axis=1)
            st.dataframe(styled, height=700)
            st.download_button("Export CSV", df.to_csv(index=False), "url_health.csv")

    st.markdown("<div class='footer'>Auto-deployed by GitLab CI • Year-filtered Deep Diff • Ready for prod</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
