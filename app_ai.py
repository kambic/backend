# app.py — MODULAR, CLEAN, EXCEL-SAFE, PRODUCTION READY
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime
import requests
import io

# ========================= CONFIG =========================
st.set_page_config(
    page_title="STAG vs PROD – Expired URLs Monitor",
    page_icon="Magnifying glass",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


st.markdown(f"""
<style>
    .big-font {{font-size: 28px !important; font-weight: bold;}}
    .metric-good {{color: #00aa00; background: #e6ffe6; padding: 10px; border-radius: 10px;}}
    .metric-bad  {{color: #aa0000; background: #ffe6e6; padding: 10px; border-radius: 10px;}}
    .footer {{text-align: center; color: #888; margin-top: 4rem;}}
    .help-text {{font-size: 14px; color: #666;}}
    {"body {background: #1e1e1e; color: white;}" if st.session_state.theme == "dark" else ""}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])
with col2:
    st.button("Dark Mode" if st.session_state.theme == "light" else "Light Mode", on_click=toggle_theme)


# ========================= UTILS =========================
def to_excel_safe(df: pd.DataFrame, title: str = "Report") -> bytes:
    """Export DataFrame to Excel with timezone-naive datetimes"""
    df_export = df.copy()

    # FIX: Ensure all datetime columns are timezone-naive for Excel compatibility
    for col in df_export.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        # Check if the column is timezone-aware and convert to naive if it is
        if df_export[col].dt.tz is not None:
            # Convert to naive (removes tz info)
            df_export[col] = df_export[col].dt.tz_localize(None)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name=title[:31])
        worksheet = writer.sheets[title[:31]]
        for i, col in enumerate(df_export.columns, 1):
            max_len = max(df_export[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(64 + i)].width = min(max_len, 50)
    return output.getvalue()


# ========================= DATA MODULE =========================
@st.cache_data(ttl=1800, show_spinner=False)
def load_environment(file_path: str, env_name: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        st.warning(f"{file_path} missing → using mock data")
        mock = [
            {"mappedOfferId": f"{env_name[0]}{i:05d}",
             "videoURLs": [{"videoURL": f"https://{env_name.lower()}.cdn.example.com/v{i}.mp4"}],
             "expired": f"2024-{'%02d' % ((i % 12) + 1)}-{'%02d' % ((i % 30) + 1)}T00:00:00Z"}
            for i in range(1, 450 if env_name == "Staging" else 380)
        ]
        path.write_text(json.dumps(mock))

    df = pd.DataFrame(json.load(open(path)))
    df["videoURL"] = df["videoURLs"].apply(lambda x: x[0]["videoURL"] if x else None)
    # Convert to datetime, ensuring it's interpreted as UTC, then make it timezone-naive
    df["expired"] = pd.to_datetime(df["expired"], utc=True).dt.tz_localize(None)
    df["year"] = df["expired"].dt.year
    df["month_year"] = df["expired"].dt.strftime("%Y-%m")
    df["date"] = df["expired"].dt.date  # Still useful for simpler display/filtering
    df["env"] = env_name
    return df.drop(columns=["videoURLs"], errors="ignore")


# ========================= MAIN APP =========================
def main():
    st.title("STAG vs PROD Expired URLs Monitor")
    st.markdown("### Real-time comparison of expired video URLs across environments")

    # Load data
    with st.spinner("Loading Staging & Production..."):
        stag = load_environment("mtcms-stag-response.json", "Staging")
        prod = load_environment("mtcms-prod-response.json", "Production")
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
        st.markdown(f"<div class='{'metric-bad' if diff > 0 else 'metric-good'} big-font'>{pct:+.1f}%</div>",
                    unsafe_allow_html=True)
    with c4:
        st.caption(f"Updated: {datetime.now():%b %d, %Y %H:%M}")

    st.markdown("---")

    # Global Year Selector
    years = sorted(combined["year"].unique(), reverse=True)
    selected_year = st.selectbox("Focus Year", years, index=0, help="All tabs use this year")

    # Tabs
    tab_overview, tab_drill, tab_diff, tab_health = st.tabs([
        "Overview", "Drilldown + Filters", "Deep Diff", "URL Health"
    ])

    # === TAB 1: Overview ===
    with tab_overview:
        col1, col2 = st.columns([3, 2])
        with col1:
            fig = px.bar(
                combined.groupby(["year", "env"], as_index=False).size(),
                x="year", y="size", color="env", barmode="group",
                title="Expired URLs by Year"
            )
            st.plotly_chart(fig, width='stretch')
        with col2:
            monthly = combined[combined["year"] == selected_year].groupby(["month_year", "env"], as_index=False).size()
            fig2 = px.line(monthly, x="month_year", y="size", color="env", markers=True,
                           title=f"Monthly Trend – {selected_year}")
            st.plotly_chart(fig2, width='stretch')

    # === TAB 2: Drilldown + Filters + Excel + Modal ===
    with tab_drill:
        st.subheader(f"Drilldown: Expired URLs in {selected_year}")

        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            envs = st.multiselect("Environment", ["Staging", "Production"], default=["Staging", "Production"])
        with colf2:
            offer = st.text_input("Offer ID contains")
        with colf3:
            url_part = st.text_input("URL contains")

        # SUGAR: Use date objects for cleaner date_input defaults
        start_default = datetime(selected_year, 1, 1).date()
        end_default = datetime(selected_year, 12, 31).date()

        date_range = st.date_input(
            "Expired Date Range",
            value=(start_default, end_default),
            key="drill_date"
        )

        # Filter logic
        df = combined[combined["year"] == selected_year].copy()
        if envs: df = df[df["env"].isin(envs)]
        if offer: df = df[df["mappedOfferId"].astype(str).str.contains(offer, case=False, na=False)]
        if url_part: df = df[df["videoURL"].str.contains(url_part, case=False, na=False)]

        # SUGAR: Robust date range filtering against the datetime column
        if len(date_range) == 2:
            # Convert start date to 00:00:00 Timestamp
            start_ts = pd.to_datetime(date_range[0])
            # Convert end date to 23:59:59 Timestamp to include the entire last day
            end_ts = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

            # Filter against the original 'expired' datetime column
            df = df[(df["expired"] >= start_ts) & (df["expired"] <= end_ts)]

        if df.empty:
            st.info("No data matches your filters")
        else:
            display = df[["env", "mappedOfferId", "videoURL", "expired"]].sort_values(["env", "expired"])
            st.dataframe(display, use_container_width=True, height=700, hide_index=True)

            # Excel Export
            excel = to_excel_safe(display, f"URLs_{selected_year}")
            st.download_button(
                "Download as Excel",
                excel,
                f"expired_urls_{selected_year}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Click to view all URLs for offer
            sel = st.dataframe(
                display.head(50),
                use_container_width=True,
                height=200,
                on_select="rerun",
                selection_mode="single-row",
                key="offer_click"
            )
            if sel.selection.rows:
                offer_id = display.iloc[sel.selection.rows[0]]["mappedOfferId"]
                with st.expander(f"All URLs for {offer_id}", expanded=True):
                    full = combined[
                        (combined["mappedOfferId"] == offer_id) &
                        (combined["year"] == selected_year)
                        ][["env", "videoURL", "expired"]]
                    st.dataframe(full, use_container_width=True)
                    st.caption(f"{len(full)} entries")

    # === TAB 3: Deep Diff ===
    with tab_diff:
        stag_y = stag[stag["year"] == selected_year]
        prod_y = prod[prod["year"] == selected_year]
        only_stag = stag_y[~stag_y["videoURL"].isin(prod_y["videoURL"])]
        only_prod = prod_y[~prod_y["videoURL"].isin(stag_y["videoURL"])]

        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"Only in Staging ({selected_year})")
            st.metric("Count", len(only_stag))
            if len(only_stag):
                st.dataframe(only_stag[["mappedOfferId", "videoURL"]], height=600)
                st.download_button("Export", to_excel_safe(only_stag), f"only_staging_{selected_year}.xlsx")
            else:
                st.success("Clean")

        with c2:
            st.subheader(f"Only in Production ({selected_year})")
            st.metric("Count", len(only_prod))
            if len(only_prod):
                st.dataframe(only_prod[["mappedOfferId", "videoURL"]], height=600)
                st.download_button("Export", to_excel_safe(only_prod), f"only_prod_{selected_year}.xlsx")
            else:
                st.success("Synced")

    # === TAB 4: Health Check ===
    with tab_health:
        if st.button("Run Health Check", type="primary", use_container_width=True):
            urls = combined["videoURL"].dropna().unique()
            results = []
            for url in st.progress(urls):
                try:
                    r = requests.head(url, timeout=8)
                    results.append({"URL": url, "Status": r.status_code, "Alive": r.status_code < 400})
                except:
                    results.append({"URL": url, "Status": "Error", "Alive": False})
            st.session_state.health = pd.DataFrame(results)
            st.success("Done!")

        if "health" in st.session_state:
            h = st.session_state.health
            st.write(f"**{len(h)} URLs** → **{h['Alive'].sum()} alive**")
            # SUGAR: Ensure styling column exists before applying style (needed if using mock data)
            if 'Alive' in h.columns:
                st.dataframe(h.style.apply(
                    lambda r: ["background-color:#d4edda" if r.Alive else "background-color:#f8d7da"] * len(r), axis=1))
            else:
                st.dataframe(h)
            st.download_button("Export Health", to_excel_safe(h), "url_health.xlsx")

    st.markdown("<div class='footer'>Modular • Excel-safe • Dark mode • Filters • Click modal • GitLab CI ready</div>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
