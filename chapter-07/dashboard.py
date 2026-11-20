import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lab_hub import show_lab_hub
import json
import html
import time
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="CyberShield | Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "results"


# =========================================================
# NAVY BLUE DESIGN SYSTEM
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #06101f;
        --panel: #0b1b30;
        --card: #102640;
        --border: #234463;
        --text: #eff6ff;
        --muted: #9bb2d0;
        --blue: #60a5fa;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 70% 0%, #102a4a 0%, transparent 42%),
            #06101f;
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(6,16,31,0.92);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #09172a, #0b1d33);
        border-right: 1px solid #24415e;
    }

    [data-testid="stSidebar"] * {
        color: #e8f1ff;
    }

    [data-testid="stSidebar"] label {
        color: #c2d5ef !important;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1600px;
    }

    h1, h2, h3, h4 {
        color: #f3f7ff !important;
        letter-spacing: -0.5px;
    }

    p, li, label {
        color: #b7cae4;
    }

    .brand {
        padding: 12px 0 26px;
        border-bottom: 1px solid #29415e;
        margin-bottom: 24px;
    }

    .brand-title {
        color: white;
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .brand-subtitle {
        color: #8daed7;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 8px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 36px 38px;
        border-radius: 20px;
        background: linear-gradient(120deg, #102d50, #173c68 65%, #10243e);
        border: 1px solid #31577e;
        margin-bottom: 22px;
        box-shadow: 0 18px 55px rgba(0,0,0,0.22);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: -65px;
        top: -90px;
        border: 1px solid rgba(147,197,253,0.18);
        border-radius: 50%;
        box-shadow: 0 0 0 25px rgba(147,197,253,0.035),
                    0 0 0 55px rgba(147,197,253,0.025);
    }

    .hero-eyebrow {
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #7dc4ff;
        margin-bottom: 13px;
    }

    .hero h1 {
        font-size: clamp(32px, 4vw, 48px);
        margin: 0;
        font-weight: 800;
    }

    .hero p {
        color: #c6ddfa;
        font-size: 14px;
        margin-top: 12px;
        margin-bottom: 0;
    }

    .section-eyebrow {
        font-size: 10px;
        letter-spacing: 2px;
        color: #72b7ff;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .animated-metric {
        min-height: 210px;
        position: relative;
        overflow: hidden;
        padding: 22px;
        border-radius: 17px;
        background: linear-gradient(145deg, #132c49, #0b1b30);
        border: 1px solid #294765;
        box-shadow: 0 8px 25px rgba(0,0,0,0.13);
        transition: transform .25s ease,
                    border-color .25s ease,
                    box-shadow .25s ease;
        animation: appear .65s ease both;
    }

    .animated-metric:hover {
        transform: translateY(-7px);
        border-color: var(--accent);
        box-shadow: 0 14px 35px var(--glow);
    }

    .metric-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        z-index: 2;
    }

    .metric-icon {
        width: 43px;
        height: 43px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        color: var(--accent);
        background: var(--glow);
        border: 1px solid var(--accent);
        font-size: 23px;
        font-weight: 700;
    }

    .metric-tag {
        font-size: 9px;
        letter-spacing: 1px;
        font-weight: 800;
        color: var(--accent);
        background: var(--glow);
        border: 1px solid var(--accent);
        border-radius: 30px;
        padding: 7px 10px;
    }

    .metric-label {
        margin-top: 23px;
        color: #a6bfdc;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        position: relative;
        z-index: 2;
    }

    .metric-value {
        color: #f5f9ff;
        font-size: clamp(27px, 2.6vw, 37px);
        font-weight: 800;
        margin: 5px 0 14px;
        position: relative;
        z-index: 2;
        font-variant-numeric: tabular-nums;
    }

    .metric-track {
        height: 5px;
        width: 100%;
        background: #243b55;
        border-radius: 20px;
        overflow: hidden;
        position: relative;
        z-index: 2;
    }

    .metric-progress {
        height: 100%;
        width: var(--progress);
        background: var(--accent);
        border-radius: 20px;
        animation: grow 1.2s ease both;
        box-shadow: 0 0 12px var(--glow);
    }

    .metric-note {
        color: #9bb2d0;
        font-size: 10px;
        margin-top: 13px;
        position: relative;
        z-index: 2;
    }

    .metric-orb {
        position: absolute;
        width: 120px;
        height: 120px;
        right: -60px;
        bottom: -70px;
        border-radius: 50%;
        background: var(--glow);
        filter: blur(16px);
        transition: transform .4s ease;
    }

    .animated-metric:hover .metric-orb {
        transform: scale(1.8);
    }

    @keyframes grow {
        from { width: 0; }
        to { width: var(--progress); }
    }

    @keyframes appear {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .panel {
        background: #0b1b30;
        border: 1px solid #233f5d;
        border-radius: 16px;
        padding: 22px;
        margin-top: 8px;
        margin-bottom: 16px;
    }

    .status-pill {
        display: inline-block;
        border: 1px solid #1b8b79;
        background: #0b302f;
        color: #6ee7cf;
        padding: 12px 16px;
        border-radius: 10px;
        width: 100%;
        font-size: 13px;
        margin: 4px 0 20px;
    }

    .small-muted {
        color: #8fa9c8;
        font-size: 12px;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #3978b9;
        background: linear-gradient(110deg, #174d91, #2563eb);
        color: white;
        font-weight: 700;
        transition: all .2s ease;
    }

    .stButton > button:hover {
        border-color: #8ac7ff;
        background: linear-gradient(110deg, #1d5cab, #3478f6);
        transform: translateY(-1px);
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #102640;
        color: white;
        border-color: #31506e;
        border-radius: 9px;
    }

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid #294765;
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stMetric"] {
        background: #102640;
        border: 1px solid #294765;
        border-radius: 12px;
        padding: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #a6bfdc;
    }

    [data-testid="stMetricValue"] {
        color: #f5f9ff;
    }

    hr {
        border-color: #29415e;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR AND DATABASE SETTINGS
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">🛡️ CyberShield</div>
            <div class="brand-subtitle">THREAT INTELLIGENCE PLATFORM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### NAVIGATION")

    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Search Threats",
            "Threat Intelligence",
            "Experiment 7 Results",
            "About Project",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### Database Connection")

    mongo_uri = st.text_input(
        "MongoDB URI",
        value="mongodb://localhost:27017",
    )

    db_name = st.text_input("Database", value="experiment7")
    collection_name = st.text_input(
        "Threat collection",
        value="threat_reports",
    )

    connect_clicked = st.button(
        "Test MongoDB Connection",
        use_container_width=True,
    )

    st.markdown("---")
    st.caption("Python · Streamlit · MongoDB")
    st.caption("Educational cybersecurity project")


# =========================================================
# DATABASE CONNECTION
# =========================================================
@st.cache_resource
def get_client(uri):
    return MongoClient(uri, serverSelectionTimeoutMS=3000)


client = None
collection = None
connection_error = None

try:
    client = get_client(mongo_uri)
    client.admin.command("ping")
    db = client[db_name]
    collection = db[collection_name]

    if connect_clicked:
        st.sidebar.success("MongoDB connection successful!")

except (PyMongoError, ValueError) as exc:
    connection_error = str(exc)
    if connect_clicked:
        st.sidebar.error(f"Connection failed: {connection_error}")


# =========================================================
# DATA LOADING AND FIELD DETECTION
# =========================================================
def load_reports(limit=5000):
    if collection is None:
        return pd.DataFrame()

    try:
        documents = list(collection.find({}, {"_id": 0}).limit(limit))
        return pd.DataFrame(documents)
    except PyMongoError as exc:
        st.error(f"Unable to load reports: {exc}")
        return pd.DataFrame()


def find_column(df, candidates):
    for col in df.columns:
        normalized = str(col).lower().replace("_", "").replace(" ", "")
        for candidate in candidates:
            if candidate in normalized:
                return col
    return None


def text_column(df, candidates):
    col = find_column(df, candidates)
    if col is None:
        return None
    return col


def classify_severity(row):
    text = " ".join(str(value) for value in row.values).lower()

    high_words = [
        "critical", "remote code execution", "rce",
        "privilege escalation", "authentication bypass",
        "sql injection", "actively exploited",
    ]

    medium_words = [
        "medium", "moderate", "cross-site scripting",
        "information disclosure", "denial of service",
    ]

    if any(word in text for word in high_words):
        return "High"

    if any(word in text for word in medium_words):
        return "Medium"

    return "Unclassified"


def prepare_reports(df):
    if df.empty:
        return df

    result = df.copy()

    severity_col = find_column(
        result,
        ["severity", "risklevel", "classification", "priority"],
    )

    if severity_col:
        result["_severity"] = (
            result[severity_col].fillna("").astype(str).str.title()
        )
        result["_severity"] = result["_severity"].apply(
            lambda value: value
            if value.lower() in [
                "critical", "high", "medium", "low",
                "unclassified", "unknown"
            ]
            else "Unclassified"
        )
    else:
        result["_severity"] = result.apply(classify_severity, axis=1)

    return result


reports = prepare_reports(load_reports())


# =========================================================
# REUSABLE COMPONENTS
# =========================================================
def metric_card(label, value, note, icon, accent, tag, percent):
    safe_label = html.escape(str(label))
    safe_value = html.escape(f"{int(value):,}")
    safe_note = html.escape(str(note))
    safe_tag = html.escape(str(tag))
    safe_icon = html.escape(str(icon))

    glow = {
        "#60A5FA": "rgba(96,165,250,.22)",
        "#FB7185": "rgba(251,113,133,.22)",
        "#2DD4BF": "rgba(45,212,191,.22)",
        "#A78BFA": "rgba(167,139,250,.22)",
    }.get(accent, "rgba(96,165,250,.22)")

    card_html = f"""
    <div class="animated-metric"
         style="--accent:{accent};
                --glow:{glow};
                --progress:{percent}%;">
        <div class="metric-top">
            <div class="metric-icon">{safe_icon}</div>
            <span class="metric-tag">{safe_tag}</span>
        </div>
        <div class="metric-label">{safe_label}</div>
        <div class="metric-value">{safe_value}</div>
        <div class="metric-track">
            <div class="metric-progress"></div>
        </div>
        <div class="metric-note">{safe_note}</div>
        <div class="metric-orb"></div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def section_heading(eyebrow, title, subtitle=None):
    st.markdown(
        f"""
        <div class="section-eyebrow">{html.escape(eyebrow.upper())}</div>
        <h2 style="margin-top:0;">{html.escape(title)}</h2>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def show_dataframe(df):
    if df.empty:
        st.info("No matching records were found.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def load_json_results():
    files = sorted(RESULT_DIR.glob("*.json"))
    results = {}

    for file in files:
        try:
            results[file.name] = json.loads(
                file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            results[file.name] = {
                "error": "Could not read this result file."
            }

    return results


# =========================================================
# COMMON HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">CYBERSECURITY ANALYTICS</div>
        <h1>CyberShield</h1>
        <p>Explore, search, and analyze cyber threat reports stored in MongoDB.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if connection_error:
    st.error(
        "MongoDB is unavailable. Start Docker and the MongoDB container, "
        "then click Test MongoDB Connection."
    )
else:
    st.markdown(
        f"""
        <div class="status-pill">
            ● MongoDB connected · {html.escape(db_name)}.
            {html.escape(collection_name)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":
    total = len(reports)

    if total:
        high_count = int(
            reports["_severity"].isin(["High", "Critical"]).sum()
        )
        medium_count = int(
            (reports["_severity"] == "Medium").sum()
        )
        unclassified_count = int(
            reports["_severity"].isin(
                ["Unclassified", "Unknown", "Low"]
            ).sum()
        )
    else:
        high_count = medium_count = unclassified_count = 0

    section_heading(
        "Overview",
        "Threat Analytics",
        "A live overview of the reports currently loaded from MongoDB.",
    )

    cols = st.columns(4, gap="medium")

    metrics = [
        (
            "TOTAL REPORTS", total, "Records in selected collection",
            "▤", "#60A5FA", "DATABASE",
            100,
        ),
        (
            "HIGH", high_count, "High and critical keyword labels",
            "⚠", "#FB7185", "REVIEW",
            round(high_count / max(total, 1) * 100),
        ),
        (
            "MEDIUM", medium_count, "Medium-risk keyword labels",
            "◈", "#2DD4BF", "MONITOR",
            round(medium_count / max(total, 1) * 100),
        ),
        (
            "UNCLASSIFIED", unclassified_count,
            "Records needing further review",
            "⌕", "#A78BFA", "ANALYZE",
            round(unclassified_count / max(total, 1) * 100),
        ),
    ]

    for col, metric in zip(cols, metrics):
        with col:
            metric_card(*metric)

    st.write("")
    section_heading(
        "Visual Insights",
        "Threat Overview",
        "Explore the distribution of records in your database.",
    )

    left, right = st.columns([0.85, 1.6], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Classification Distribution")

        if total:
            chart_data = (
                reports["_severity"]
                .value_counts()
                .rename_axis("Classification")
                .to_frame("Reports")
            )
            st.bar_chart(chart_data, color="#3B82F6")
        else:
            st.info("Insert or import threat reports to view this chart.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Recent Threat Reports")

        if total:
            id_col = text_column(
                reports, ["cveid", "cve", "identifier", "id"]
            )
            name_col = text_column(
                reports, ["threatname", "title", "description", "name"]
            )
            vendor_col = text_column(
                reports, ["vendor", "publisher", "source"]
            )

            display = pd.DataFrame()
            display["Classification"] = reports["_severity"]

            if id_col:
                display["CVE / ID"] = reports[id_col].astype(str)
            if name_col:
                display["Threat"] = reports[name_col].astype(str)
            if vendor_col:
                display["Vendor / Source"] = reports[vendor_col].astype(str)

            if len(display.columns) == 1:
                display = reports.drop(
                    columns=["_severity"], errors="ignore"
                )

            show_dataframe(display.head(10))
        else:
            st.info("No threat reports are currently available.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "Classification is a basic keyword-based estimate, not a verified "
        "security severity assessment."
    )


# =========================================================
# SEARCH THREATS
# =========================================================
elif page == "Search Threats":
    section_heading(
        "Threat Explorer",
        "Search Threat Reports",
        "Search loaded MongoDB records by CVE, threat name, vendor, or keyword.",
    )

    keyword = st.text_input(
        "Search keyword",
        placeholder="Example: Apache, CVE, injection, Microsoft...",
    )

    if not reports.empty:
        filtered = reports.copy()

        if keyword.strip():
            mask = filtered.astype(str).apply(
                lambda col: col.str.contains(
                    keyword.strip(), case=False, na=False, regex=False
                )
            ).any(axis=1)

            filtered = filtered[mask]

        st.write(f"**{len(filtered):,} matching records**")

        show_dataframe(
            filtered.drop(columns=["_severity"], errors="ignore")
        )

        if not filtered.empty:
            st.download_button(
                "Download search results as CSV",
                data=filtered.drop(
                    columns=["_severity"], errors="ignore"
                ).to_csv(index=False).encode("utf-8"),
                file_name="cybershield_search_results.csv",
                mime="text/csv",
            )
    else:
        st.warning("Connect to MongoDB and ensure the collection contains records.")


# =========================================================
# THREAT INTELLIGENCE
# =========================================================
elif page == "Threat Intelligence":
    section_heading(
        "Investigation Workspace",
        "Threat Intelligence",
        "Filter and inspect reports using the available classification labels.",
    )

    if not reports.empty:
        severities = sorted(
            reports["_severity"].dropna().unique().tolist()
        )

        selected_severities = st.multiselect(
            "Filter by classification",
            options=severities,
            default=severities,
        )

        filtered = reports[
            reports["_severity"].isin(selected_severities)
        ]

        a, b, c = st.columns(3)
        a.metric("Filtered Reports", f"{len(filtered):,}")
        b.metric(
            "High / Critical",
            int(filtered["_severity"].isin(["High", "Critical"]).sum()),
        )
        c.metric(
            "Medium",
            int((filtered["_severity"] == "Medium").sum()),
        )

        st.subheader("Investigation Results")
        show_dataframe(
            filtered.drop(columns=["_severity"], errors="ignore")
        )

        st.download_button(
            "Export filtered intelligence",
            data=filtered.drop(
                columns=["_severity"], errors="ignore"
            ).to_csv(index=False).encode("utf-8"),
            file_name="cybershield_threat_intelligence.csv",
            mime="text/csv",
        )
    else:
        st.info("Threat intelligence will appear here when records are available.")


# =========================================================
# EXPERIMENT 7 RESULTS
# =========================================================
elif page == "Experiment 7 Results":
    section_heading(
        "MongoDB Laboratory",
        "Experiment 7 Results",
        "View saved outputs from schema analysis, workload testing, and cache monitoring.",
    )

    result_files = load_json_results()

    if not result_files:
        st.warning(
            "No JSON results found. Run your Experiment 7 Python scripts first."
        )
    else:
        st.success(f"{len(result_files)} saved result file(s) found.")

        selected_file = st.selectbox(
            "Select a result file",
            options=list(result_files.keys()),
        )

        selected_data = result_files[selected_file]

        st.subheader(selected_file)

        if isinstance(selected_data, list):
            show_dataframe(pd.DataFrame(selected_data))
        elif isinstance(selected_data, dict):
            st.json(selected_data)
        else:
            st.write(selected_data)

        st.download_button(
            "Download selected JSON",
            data=json.dumps(
                selected_data, indent=2, ensure_ascii=False
            ),
            file_name=selected_file,
            mime="application/json",
        )

        st.divider()
        st.subheader("All Experiment Result Files")

        for filename, data in result_files.items():
            with st.expander(filename):
                if isinstance(data, list):
                    show_dataframe(pd.DataFrame(data))
                else:
                    st.json(data)


# =========================================================
# ABOUT PROJECT
# =========================================================
      # --- LAB 8 & 9 LIVE + LAB 10-18 AUTO INSIDE LAB 7 (NO BUTTON, AUTO SHOW) ---
    st.markdown("---")
    st.subheader("📌 Continued Experiments - Inside Lab 7 Website")
    st.write("Lab 8 and 9 run automatically on your live MongoDB. Lab 10-18 will auto-join here.")

    tab8, tab9, tab_rest = st.tabs(["Experiment 8", "Experiment 9", "Experiment 10 - 18"])

    # ===== EXPERIMENT 8 - AUTO =====
    with tab8:
        st.markdown("### 📊 Experiment 8 - Indexing & Query Performance")
        st.write("**Objective:** Create index on `threat_type` and compare query performance with/without index.")
        st.code('db.threats.createIndex({ threat_type: 1 })\ndb.threats.find({ threat_type: "Phishing" }).explain("executionStats")', language="javascript")
        st.markdown("**Live Output from your MongoDB:**")
        try:
            from pymongo import MongoClient
            import time
            client8 = MongoClient(mongo_uri)
            col8 = client8[db_name][collection_name]
            col8.create_index("threat_type")
            start = time.time()
            res8 = list(col8.find({"threat_type": "Phishing"}).limit(10))
            t1 = round((time.time() - start) * 1000, 2)
            exp8 = col8.find({"threat_type": "Phishing"}).explain()
            stats8 = exp8.get('executionStats', {})
            st.success("✅ Index created on threat_type")
            c1, c2, c3 = st.columns(3)
            c1.metric("Docs Found", len(res8))
            c2.metric("Query Time", f"{t1} ms")
            c3.metric("Docs Examined", stats8.get('totalDocsExamined', 'N/A'))
            st.write(f"**Execution Time (MongoDB):** {stats8.get('executionTimeMillis', 'N/A')} ms")
            st.write("**Sample Output (First 2 Docs):**")
            st.json(res8[:2])
        except Exception as e:
            st.error(f"Error in Lab 8: {e}")
            st.info("Make sure MongoDB is running and Lab 7 is connected.")

    # ===== EXPERIMENT 9 - AUTO =====
    with tab9:
        st.markdown("### 📊 Experiment 9 - Aggregation Pipeline")
        st.write("**Objective:** Use aggregation pipeline to group threats by type and count them.")
        st.code('db.threats.aggregate([\n  { $group: { _id: "$threat_type", count: { $sum: 1 } } },\n  { $sort: { count: -1 } }\n])', language="javascript")
        st.markdown("**Live Output from your MongoDB:**")
        try:
            from pymongo import MongoClient
            import pandas as pd
            client9 = MongoClient(mongo_uri)
            col9 = client9[db_name][collection_name]
            pipeline9 = [
                {"$group": {"_id": "$threat_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            data9 = list(col9.aggregate(pipeline9))
            if len(data9) > 0:
                st.success(f"✅ Aggregation successful - {len(data9)} threat types found")
                df9 = pd.DataFrame(data9)
                st.dataframe(df9, use_container_width=True)
                st.markdown("**Chart - Threats by Type:**")
                st.bar_chart(df9.set_index("_id")["count"])
                st.write("**Raw Output:**")
                st.json(data9)
            else:
                st.warning("No data found. Add data in Lab 7 first, then Lab 9 will show output.")
        except Exception as e:
            st.error(f"Error in Lab 9: {e}")
            st.info("Make sure MongoDB is running and Lab 7 is connected.")

   


elif page == "About Project":
    section_heading(
        "Project Information",
        "About CyberShield",
        "A MongoDB-based educational threat intelligence dashboard.",
    )

    st.markdown(
        """
        <div class="panel">
            <h3>🛡️ Project Overview</h3>
            <p>
                CyberShield provides an interface to explore and analyze
                cybersecurity threat reports stored in MongoDB. It includes
                searchable records, classification summaries, data exports,
                and saved outputs from MongoDB Experiment 7.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Technology Stack")
        st.markdown(
            """
            - **Python** — application logic
            - **Streamlit** — interactive user interface
            - **MongoDB** — document database
            - **PyMongo** — database connection
            - **Pandas** — data processing and tables
            - **Docker** — local database environment
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Key Features")
        st.markdown(
            """
            - Live MongoDB connection check
            - Animated navy-blue metric cards
            - Threat search and filtering
            - Classification distribution chart
            - CSV export of filtered records
            - Experiment 7 JSON result viewer
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "This dashboard is intended for educational use. "
        "Keyword-based classifications are illustrative and should not "
        "replace validated vulnerability scoring."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#7792b2; font-size:11px; padding:8px;">
        CYBERSHIELD · MONGODB EXPERIMENT 7 · EDUCATIONAL PROJECT
    </div>
    """,
    unsafe_allow_html=True,
)
show_lab_hub()