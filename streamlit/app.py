import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Stock Analytics Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM
# ============================================================
UP = "#35D6A0"
DOWN = "#FF6259"
AMBER = "#E8A63D"
BLUE = "#6C8EF5"
MUTED = "#8996A6"

SECTOR_COLORS = {
    "Tech": "#6C8EF5",
    "Financials": "#E8A63D",
    "Energy": "#FF6259",
    "IT": "#35D6A0",
    "Consumer": "#C792EA",
    "Industrials": "#8996A6",
}

ACTION_COLORS = {
    "SPLIT": "#6C8EF5",
    "BONUS": "#35D6A0",
    "BUYBACK": "#E8A63D",
    "DIVIDEND": "#C792EA",
}

SEM = "STOCK_ANALYTICS.SEM"
DW = "STOCK_ANALYTICS.DW"

# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,.18);
        background: linear-gradient(180deg, rgba(128,128,128,.035), rgba(128,128,128,.015));
    }
    [data-testid="stSidebar"] .nav-caption {
        font-size: .74rem;
        color: #8996A6;
        line-height: 1.45;
        margin-top: 8px;
    }
    [data-testid="stSidebar"] .nav-brand {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -.02em;
    }
    [data-testid="stSidebar"] .nav-version {
        display: inline-block;
        margin-top: 6px;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: .65rem;
        font-weight: 700;
        color: #A8B0BC;
        background: rgba(128,128,128,.08);
        border: 1px solid rgba(128,128,128,.12);
    }

    /* Clean left navigation: text list + subtle active state */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 3px;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        border-radius: 7px;
        padding: 8px 10px !important;
        margin: 0 !important;
        min-height: 34px;
        cursor: pointer;
        transition: background .15s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(128,128,128,.08);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(128,128,128,.18);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        font-size: .88rem;
        font-weight: 500;
        margin: 0;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background: rgba(128,128,128,.055);
        border: 1px solid rgba(128,128,128,.14);
        padding: 14px 16px;
        border-radius: 12px;
    }
    [data-testid="stMetricLabel"] { font-size: .78rem; }
    [data-testid="stMetricValue"] { font-size: 1.45rem; }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .hero {
        padding: 4px 0 12px 0;
    }
    .eyebrow {
        text-transform: uppercase;
        letter-spacing: .12em;
        font-size: .72rem;
        color: #8996A6;
        font-weight: 700;
        margin-bottom: .25rem;
    }
    .hero-title {
        font-size: 2.45rem;
        line-height: 1.05;
        font-weight: 800;
        margin: 0;
    }
    .hero-subtitle {
        color: #9AA4B2;
        margin-top: .55rem;
        font-size: .98rem;
    }
    .section-label {
        font-size: .74rem;
        text-transform: uppercase;
        letter-spacing: .1em;
        color: #8996A6;
        font-weight: 700;
        margin: 12px 0 6px 0;
    }
    .insight {
        border: 1px solid rgba(128,128,128,.14);
        background: rgba(128,128,128,.045);
        border-radius: 12px;
        padding: 13px 15px;
        min-height: 78px;
    }
    .insight-title { font-size: .76rem; color: #8996A6; margin-bottom: 3px; }
    .insight-value { font-size: 1.05rem; font-weight: 700; }
    .insight-note { font-size: .76rem; color: #8996A6; margin-top: 2px; }

    .platform-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:18px 0 24px 0; }
    .platform-card { border:1px solid rgba(128,128,128,.14); background:rgba(128,128,128,.045); border-radius:14px; padding:15px 16px; min-height:104px; }
    .platform-card .num { font-size:.70rem; font-weight:800; letter-spacing:.10em; color:#8996A6; text-transform:uppercase; }
    .platform-card .title { margin-top:7px; font-size:1rem; font-weight:750; }
    .platform-card .desc { margin-top:4px; color:#8996A6; font-size:.77rem; line-height:1.35; }
    .arch-wrap { border:1px solid rgba(128,128,128,.14); background:rgba(128,128,128,.035); border-radius:16px; padding:18px; margin:10px 0 22px 0; }
    .arch-row { display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap; }
    .arch-node { border:1px solid rgba(128,128,128,.18); background:rgba(128,128,128,.06); border-radius:11px; padding:10px 13px; min-width:118px; text-align:center; }
    .arch-node strong { display:block; font-size:.82rem; }
    .arch-node span { display:block; margin-top:3px; font-size:.66rem; color:#8996A6; }
    .arch-arrow { color:#8996A6; font-size:1rem; }
    .layer-pill { display:inline-block; margin:2px 4px 2px 0; padding:4px 8px; border-radius:999px; font-size:.66rem; font-weight:700; border:1px solid rgba(128,128,128,.15); background:rgba(128,128,128,.05); color:#C7CDD5; }
    .principle { border-left:3px solid #6C8EF5; padding:8px 12px; background:rgba(108,142,245,.055); border-radius:0 9px 9px 0; margin:7px 0; font-size:.83rem; line-height:1.4; }
    @media (max-width:900px) { .platform-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION + DATA ACCESS
# ============================================================
session = get_active_session()


@st.cache_data(ttl=300, show_spinner=False)
def run_query(query: str) -> pd.DataFrame:
    return session.sql(query).to_pandas()


def sql_escape(value) -> str:
    return str(value).replace("'", "''")


def fmt_number(value) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):,.0f}"


def fmt_decimal(value, decimals=2) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):,.{decimals}f}"


def fmt_currency(value) -> str:
    if pd.isna(value):
        return "—"
    return f"${float(value):,.2f}"


def fmt_percent(value) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):,.2f}%"


def sector_scale():
    return alt.Scale(domain=list(SECTOR_COLORS), range=list(SECTOR_COLORS.values()))


def action_scale():
    return alt.Scale(domain=list(ACTION_COLORS), range=list(ACTION_COLORS.values()))


def base_chart(chart):
    return chart.configure_view(strokeOpacity=0).configure_axis(
        labelColor="#A8B0BC",
        titleColor="#D5DAE1",
        gridColor="#303641",
        domainColor="#414852",
        tickColor="#414852",
        labelFontSize=11,
        titleFontSize=12,
    ).configure_legend(
        labelColor="#C7CDD5",
        titleColor="#D5DAE1",
        labelFontSize=11,
    )


def show_chart(chart, height=None):
    if height:
        chart = chart.properties(height=height)
    st.altair_chart(base_chart(chart), use_container_width=True)


def donut_chart(df, category, value, scale=None, height=300):
    color = alt.Color(
        f"{category}:N",
        scale=scale,
        legend=alt.Legend(title=None),
    )
    return (
        alt.Chart(df)
        .mark_arc(innerRadius=62, outerRadius=120)
        .encode(
            theta=alt.Theta(f"{value}:Q"),
            color=color,
            tooltip=[alt.Tooltip(f"{category}:N", title=category), alt.Tooltip(f"{value}:Q", title=value, format=",.2f")],
        )
        .properties(height=height)
    )


def signed_bar(df, value, category, title, height=300):
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{value}:Q", title=title),
            y=alt.Y(f"{category}:N", title=None, sort="-x"),
            color=alt.condition(alt.datum[value] >= 0, alt.value(UP), alt.value(DOWN)),
            tooltip=[category, alt.Tooltip(value, format=".2f")],
        )
        .properties(height=height)
    )


def ranked_bar(df, value, category, title, color=BLUE, height=300):
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4, color=color)
        .encode(
            x=alt.X(f"{value}:Q", title=title),
            y=alt.Y(f"{category}:N", title=None, sort="-x"),
            tooltip=[category, alt.Tooltip(value, format=",.2f")],
        )
        .properties(height=height)
    )


def candlestick(df, height=390):
    base = alt.Chart(df).encode(
        x=alt.X("TRADE_DATE:T", title=None),
        color=alt.condition(
            alt.datum.OPEN <= alt.datum.CLOSE,
            alt.value(UP),
            alt.value(DOWN),
        ),
    )
    wick = base.mark_rule().encode(y=alt.Y("LOW:Q", title="Price"), y2="HIGH:Q")
    body = base.mark_bar(size=12).encode(
        y="OPEN:Q",
        y2="CLOSE:Q",
        tooltip=[
            alt.Tooltip("TRADE_DATE:T", title="Date"),
            alt.Tooltip("OPEN:Q", title="Open", format=",.2f"),
            alt.Tooltip("HIGH:Q", title="High", format=",.2f"),
            alt.Tooltip("LOW:Q", title="Low", format=",.2f"),
            alt.Tooltip("CLOSE:Q", title="Close", format=",.2f"),
        ],
    )
    return (wick + body).properties(height=height)


def volume_chart(df, height=230):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("TRADE_DATE:T", title=None),
            y=alt.Y("VOLUME:Q", title="Shares", axis=alt.Axis(format="~s")),
            color=alt.condition(alt.datum.DAILY_RETURN_PCT >= 0, alt.value(UP), alt.value(DOWN)),
            tooltip=[
                alt.Tooltip("TRADE_DATE:T", title="Date"),
                alt.Tooltip("VOLUME:Q", title="Volume", format=","),
                alt.Tooltip("DAILY_RETURN_PCT:Q", title="Return %", format=".2f"),
            ],
        )
        .properties(height=height)
    )


def insight_card(title, value, note=""):
    st.markdown(
        f'<div class="insight"><div class="insight-title">{title}</div>'
        f'<div class="insight-value">{value}</div><div class="insight-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def page_header(eyebrow, title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{eyebrow}</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown('<div class="nav-brand">Stock Analytics</div>', unsafe_allow_html=True)
st.sidebar.caption("Snowflake • dbt • Streamlit")
st.sidebar.divider()

PAGES = [
    "Platform Overview",
    "Market Overview",
    "Market Movers",
    "Company Detail",
    "Price History",
    "Sector & Exchange",
    "Corporate Actions",
    "Stock Screener",
]

page = st.sidebar.radio(
    "Navigation",
    PAGES,
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown(
    '<div class="nav-caption">Curated analytical views backed by Snowflake semantic models.</div>',
    unsafe_allow_html=True,
)

st.sidebar.divider()
st.sidebar.markdown("**Data interpretation**")
st.sidebar.caption(
    "Returns and volatility are same-session metrics (close vs open). "
    "The seed dataset is intentionally small, so this app avoids presenting sparse data as long-term time-series performance."
)

# ============================================================
# PLATFORM OVERVIEW
# ============================================================
if page == "Platform Overview":
    page_header(
        "DATA ENGINEERING PLATFORM",
        "Multi-Exchange Stock Analytics",
        "A Snowflake-native analytics platform demonstrating ingestion, dimensional modeling, data quality, semantic modeling, and decision-ready analytics.",
    )

    facts = [
        ("01", "Source", "Seed CSV feeds", "Companies, exchanges, prices and corporate actions"),
        ("02", "Platform", "Snowflake", "Warehouse, compute and governed analytics"),
        ("03", "Transformation", "dbt", "Staging → dimensional warehouse → semantic views"),
        ("04", "Experience", "Native Streamlit", "Interactive analytics running directly in Snowflake"),
    ]
    st.markdown(
        '<div class="platform-grid">' +
        "".join(
            f'<div class="platform-card"><div class="num">{n}</div>'
            f'<div class="title">{title}</div><div class="desc">{desc}</div></div>'
            for n, title, desc, _ in facts
        ) +
        '</div>',
        unsafe_allow_html=True,
    )

    footprint = run_query(
        f"SELECT COUNT(DISTINCT TICKER) AS COMPANIES, COUNT(*) AS TRADING_RECORDS, "
        f"COUNT(DISTINCT EXCHANGE_CODE) AS EXCHANGES, SUM(VOLUME) AS TOTAL_VOLUME "
        f"FROM {SEM}.STOCK_DAILY_ANALYTICS"
    ).iloc[0]

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.metric("Tracked Companies", fmt_number(footprint["COMPANIES"]))
    with f2:
        st.metric("Price Records", fmt_number(footprint["TRADING_RECORDS"]))
    with f3:
        st.metric("Exchanges", fmt_number(footprint["EXCHANGES"]))
    with f4:
        st.metric("Shares Traded", fmt_number(footprint["TOTAL_VOLUME"]))

    st.markdown('<div class="section-label">Architecture</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="arch-wrap"><div class="arch-row">'
        '<div class="arch-node"><strong> S3</strong><span>Source files</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong> Snowpipe</strong><span>Ingestion</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong>RAW</strong><span>Landing layer</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong>dbt Staging</strong><span>Clean & standardize</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong>DW</strong><span>Star schema</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong>SEM</strong><span>Business views</span></div><div class="arch-arrow">→</div>'
        '<div class="arch-node"><strong> Streamlit</strong><span>Analytics UX</span></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2)
    with a1:
        st.subheader("Data layers")
        st.markdown(
            '<span class="layer-pill">RAW • source-aligned</span>'
            '<span class="layer-pill">STAGING • dbt views</span>'
            '<span class="layer-pill">DW • dimensional model</span>'
            '<span class="layer-pill">SEM • analytics views</span>',
            unsafe_allow_html=True,
        )
        st.markdown("#### Warehouse model")
        st.markdown(
            "- **DIM_COMPANY** — SCD Type 2 history\n"
            "- **DIM_EXCHANGE** — Type 1 reference dimension\n"
            "- **DIM_DATE** — reusable calendar dimension\n"
            "- **FACT_DAILY_PRICE** — company × date trading grain\n"
            "- **FACT_CORPORATE_ACTIONS** — event-level corporate actions"
        )

    with a2:
        st.subheader("Engineering capabilities")
        st.markdown(
            '<div class="principle"><b>Separation of concerns</b> — ingestion, transformation, warehouse modeling and presentation stay in their appropriate layers.</div>'
            '<div class="principle"><b>Historical correctness</b> — company attributes use SCD Type 2 and relevant event-date joins.</div>'
            '<div class="principle"><b>Explainable analytics</b> — metrics are based on what this seed dataset can actually support.</div>'
            '<div class="principle"><b>Semantic consumption</b> — Streamlit consumes curated SEM views rather than rebuilding business logic in Python.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Dashboard map</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.subheader(" Market intelligence")
        st.caption("Market Overview + Market Movers")
        st.markdown("Gainers • losers • volume leaders • sector mix • intraday activity")
    with d2:
        st.subheader(" Drill-down analytics")
        st.caption("Company Detail + Price History")
        st.markdown("Company KPIs • OHLC • volume • session returns • corporate actions")
    with d3:
        st.subheader(" Cross-sectional analysis")
        st.caption("Sector / Exchange + Screener")
        st.markdown("Sector comparisons • exchange activity • filters • ranking • export")

    st.divider()
    st.subheader("Design decisions that matter")
    decisions = [
        ("No fabricated market calendar", "The source does not provide an authoritative exchange calendar."),
        ("No misleading 20D volatility", "The seed dataset is small and sparse, so long-window statistics would not be defensible."),
        ("Business-defined fact grain", "Daily price data is modeled around the company/date/exchange trading record."),
        ("Corporate actions stay separate", "Splits, bonuses, dividends and buybacks are event data, not daily price observations."),
    ]
    for title, body in decisions:
        st.markdown(
            f'<div class="principle"><b>{title}</b> — {body}</div>',
            unsafe_allow_html=True,
        )

    st.caption(
        "Interview framing: S3/Snowpipe handles ingestion → dbt handles transformation and modeling → "
        "Snowflake DW/SEM provides governed analytics → Native Streamlit provides the consumption layer."
    )

# ============================================================
# MARKET OVERVIEW
# ============================================================
elif page == "Market Overview":
    page_header(
        "MARKET PULSE",
        "Market Overview",
        "A decision-ready view of activity, leaders, sector mix, and the latest trading records.",
    )

    overview = run_query(f"""
        SELECT
            COUNT(*) AS COMPANIES,
            SUM(TRADING_DAYS) AS TRADING_RECORDS,
            MIN(FIRST_TRADE_DATE) AS FIRST_TRADE_DATE,
            MAX(LAST_TRADE_DATE) AS LAST_TRADE_DATE,
            SUM(TOTAL_VOLUME) AS TOTAL_VOLUME,
            SUM(TOTAL_TURNOVER_USD) AS TOTAL_TURNOVER_USD
        FROM {SEM}.COMPANY_PERFORMANCE
    """)

    advdec = run_query(f"""
        SELECT
            SUM(IFF(DAILY_RETURN_PCT > 0, 1, 0)) AS ADV,
            SUM(IFF(DAILY_RETURN_PCT < 0, 1, 0)) AS DEC_
        FROM {SEM}.STOCK_DAILY_ANALYTICS
    """).iloc[0]

    actions_count = run_query(f"""
        SELECT COUNT(*) AS N
        FROM {DW}.FACT_CORPORATE_ACTIONS
        WHERE UPPER(STATUS) = 'ANNOUNCED'
    """).iloc[0]["N"]

    row = overview.iloc[0]
    adv = int(advdec["ADV"] or 0)
    dec = int(advdec["DEC_"] or 0)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Companies", fmt_number(row["COMPANIES"]))
    with k2:
        st.metric("Trading Records", fmt_number(row["TRADING_RECORDS"]))
    with k3:
        st.metric("Total Volume", fmt_number(row["TOTAL_VOLUME"]))
    with k4:
        st.metric("Turnover (USD)", fmt_currency(row["TOTAL_TURNOVER_USD"]))

    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.metric("Coverage Start", str(row["FIRST_TRADE_DATE"]))
    with k6:
        st.metric("Latest Trade", str(row["LAST_TRADE_DATE"]))
    with k7:
        st.metric("Advance / Decline", f"{adv} / {dec}")
    with k8:
        st.metric("Announced Actions", fmt_number(actions_count))

    st.markdown('<div class="section-label">Market leaders</div>', unsafe_allow_html=True)
    leaders = run_query(f"""
        SELECT TICKER, COMPANY_NAME, SECTOR, EXCHANGE_CODE,
               CLOSE, DAILY_RETURN_PCT, VOLUME, TRADE_DATE
        FROM {SEM}.MARKET_MOVERS
    """)

    if not leaders.empty:
        top_gainer = leaders.loc[leaders["DAILY_RETURN_PCT"].idxmax()]
        top_loser = leaders.loc[leaders["DAILY_RETURN_PCT"].idxmin()]
        top_volume = leaders.loc[leaders["VOLUME"].idxmax()]
        widest_range = run_query(f"""
            SELECT TICKER, DAILY_RANGE_PCT
            FROM {SEM}.STOCK_DAILY_ANALYTICS
            ORDER BY DAILY_RANGE_PCT DESC
            LIMIT 1
        """).iloc[0]

        i1, i2, i3, i4 = st.columns(4)
        with i1:
            insight_card("Top gainer", f"{top_gainer['TICKER']}  {fmt_percent(top_gainer['DAILY_RETURN_PCT'])}", "best same-session return")
        with i2:
            insight_card("Top loser", f"{top_loser['TICKER']}  {fmt_percent(top_loser['DAILY_RETURN_PCT'])}", "weakest same-session return")
        with i3:
            insight_card("Most active", str(top_volume["TICKER"]), f"{fmt_number(top_volume['VOLUME'])} shares")
        with i4:
            insight_card("Widest range", str(widest_range["TICKER"]), f"{fmt_percent(widest_range['DAILY_RANGE_PCT'])} intraday range")

    st.markdown('<div class="section-label">Market composition</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        sector_volume = run_query(f"""
            SELECT SECTOR, SUM(TOTAL_VOLUME) AS TOTAL_VOLUME
            FROM {SEM}.SECTOR_EXCHANGE_SUMMARY
            GROUP BY SECTOR
            ORDER BY TOTAL_VOLUME DESC
        """)
        st.subheader("Trading Volume by Sector")
        show_chart(donut_chart(sector_volume, "SECTOR", "TOTAL_VOLUME", sector_scale(), 320))

    with c2:
        sector_return = run_query(f"""
            SELECT SECTOR, AVG(AVG_DAILY_RETURN_PCT) AS AVG_RETURN
            FROM {SEM}.SECTOR_EXCHANGE_SUMMARY
            GROUP BY SECTOR
            ORDER BY AVG_RETURN DESC
        """)
        st.subheader("Average Intraday Return")
        show_chart(signed_bar(sector_return, "AVG_RETURN", "SECTOR", "Return %", 320))

    st.markdown('<div class="section-label">Latest records</div>', unsafe_allow_html=True)
    snapshot = leaders.sort_values("TRADE_DATE", ascending=False).copy()
    snapshot["DAILY_RETURN_PCT"] = snapshot["DAILY_RETURN_PCT"].round(2)
    snapshot["CLOSE"] = snapshot["CLOSE"].round(2)
    st.dataframe(
        snapshot[["TRADE_DATE", "TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "CLOSE", "DAILY_RETURN_PCT", "VOLUME"]].head(12),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# MARKET MOVERS
# ============================================================
elif page == "Market Movers":
    page_header(
        "MARKET ACTIVITY",
        "Market Movers",
        "Ranked gainers, losers, volume leaders, and the intraday risk/activity map.",
    )

    movers = run_query(f"""
        SELECT TRADE_DATE, TICKER, COMPANY_NAME, SECTOR, EXCHANGE_CODE,
               OPEN, CLOSE, DAILY_RETURN_PCT, DAILY_RANGE_PCT, VOLUME, TURNOVER_USD,
               GAIN_RANK, LOSS_RANK, VOLUME_RANK
        FROM {SEM}.MARKET_MOVERS
    """)

    if movers.empty:
        st.info("No market-mover data available.")
        st.stop()

    t1, t2, t3 = st.tabs([" Gainers", " Losers", " Volume"])

    with t1:
        df = movers.sort_values("DAILY_RETURN_PCT", ascending=False).head(10).copy()
        st.subheader("Top 10 Gainers")
        show_chart(ranked_bar(df, "DAILY_RETURN_PCT", "TICKER", "Intraday return %", UP, 310))
        df["DAILY_RETURN_PCT"] = df["DAILY_RETURN_PCT"].round(2)
        st.dataframe(df[["TRADE_DATE", "TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "CLOSE", "DAILY_RETURN_PCT", "VOLUME"]], use_container_width=True, hide_index=True)

    with t2:
        df = movers.sort_values("DAILY_RETURN_PCT", ascending=True).head(10).copy()
        st.subheader("Top 10 Losers")
        show_chart(ranked_bar(df, "DAILY_RETURN_PCT", "TICKER", "Intraday return %", DOWN, 310))
        df["DAILY_RETURN_PCT"] = df["DAILY_RETURN_PCT"].round(2)
        st.dataframe(df[["TRADE_DATE", "TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "CLOSE", "DAILY_RETURN_PCT", "VOLUME"]], use_container_width=True, hide_index=True)

    with t3:
        df = movers.sort_values("VOLUME", ascending=False).head(10).copy()
        st.subheader("Top 10 by Trading Volume")
        show_chart(ranked_bar(df, "VOLUME", "TICKER", "Shares traded", AMBER, 310))
        st.dataframe(df[["TRADE_DATE", "TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "VOLUME", "TURNOVER_USD"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Intraday Activity Map")
    st.caption("Each point is one trading record. X = intraday range, Y = volume, bubble size = USD turnover.")

    activity = run_query(f"""
        SELECT TICKER, COMPANY_NAME, SECTOR, EXCHANGE_CODE,
               DAILY_RANGE_PCT, DAILY_RETURN_PCT, VOLUME, TURNOVER_USD
        FROM {SEM}.STOCK_DAILY_ANALYTICS
    """)

    if not activity.empty:
        bubble = (
            alt.Chart(activity)
            .mark_circle(opacity=0.72)
            .encode(
                x=alt.X("DAILY_RANGE_PCT:Q", title="Intraday range %"),
                y=alt.Y("VOLUME:Q", title="Volume", axis=alt.Axis(format="~s")),
                size=alt.Size("TURNOVER_USD:Q", legend=None, scale=alt.Scale(range=[70, 1600])),
                color=alt.Color("SECTOR:N", scale=sector_scale(), legend=alt.Legend(title=None)),
                tooltip=["TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "DAILY_RANGE_PCT", "DAILY_RETURN_PCT", "VOLUME", "TURNOVER_USD"],
            )
            .properties(height=430)
        )
        show_chart(bubble)

# ============================================================
# COMPANY DETAIL
# ============================================================
elif page == "Company Detail":
    page_header(
        "ENTITY VIEW",
        "Company Detail",
        "A single-company profile combining dimensional attributes, trading metrics, price action, and corporate events.",
    )

    companies = run_query(f"""
        SELECT TICKER, COMPANY_NAME
        FROM {SEM}.COMPANY_PERFORMANCE
        ORDER BY COMPANY_NAME
    """)

    if companies.empty:
        st.warning("No companies available.")
        st.stop()

    labels = (companies["TICKER"].astype(str) + " — " + companies["COMPANY_NAME"].astype(str)).tolist()
    selected = st.selectbox("Company", labels)
    ticker = selected.split(" — ", 1)[0]
    safe = sql_escape(ticker)

    profile = run_query(f"""
        SELECT TICKER, COMPANY_NAME, SECTOR, INDUSTRY, EXCHANGE_CODE,
               TRADING_DAYS, FIRST_TRADE_DATE, LAST_TRADE_DATE,
               PERIOD_LOW, PERIOD_HIGH, AVG_CLOSE, AVG_VOLUME, AVG_VWAP,
               PRICE_RANGE, AVG_DAILY_RETURN_PCT, AVG_INTRADAY_VOLATILITY_PCT,
               TOTAL_VOLUME, TOTAL_TURNOVER_USD
        FROM {SEM}.COMPANY_PERFORMANCE
        WHERE TICKER = '{safe}'
    """)

    history = run_query(f"""
        SELECT FULL_DATE AS TRADE_DATE,
               OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME, VWAP,
               DAILY_RANGE, DAILY_RETURN_PCT, DAILY_RANGE_PCT,
               TURNOVER, USD_RATE, TURNOVER_USD
        FROM {SEM}.STOCK_DAILY_ANALYTICS
        WHERE TICKER = '{safe}'
        ORDER BY FULL_DATE
    """)

    if profile.empty or history.empty:
        st.warning("No company data available.")
        st.stop()

    p = profile.iloc[0]
    if int(p["TRADING_DAYS"]) == 1:
        st.warning("Only one trading session is available for this ticker. Treat the metrics as a snapshot, not a long-term trend.")

    st.subheader(f"{p['COMPANY_NAME']}  ·  {p['TICKER']}")
    a, b, c, d = st.columns(4)
    with a: st.metric("Sector", str(p["SECTOR"]))
    with b: st.metric("Industry", str(p["INDUSTRY"]))
    with c: st.metric("Exchange", str(p["EXCHANGE_CODE"]))
    with d: st.metric("Trading sessions", fmt_number(p["TRADING_DAYS"]))

    a, b, c, d = st.columns(4)
    with a: st.metric("Period low", fmt_decimal(p["PERIOD_LOW"]))
    with b: st.metric("Period high", fmt_decimal(p["PERIOD_HIGH"]))
    with c: st.metric("Average close", fmt_decimal(p["AVG_CLOSE"]))
    with d: st.metric("Average VWAP", fmt_decimal(p["AVG_VWAP"]))

    latest = history.iloc[-1]
    a, b, c, d = st.columns(4)
    with a: st.metric("Latest close", fmt_decimal(latest["CLOSE"]))
    with b: st.metric("Latest return", fmt_percent(latest["DAILY_RETURN_PCT"]))
    with c: st.metric("Latest volume", fmt_number(latest["VOLUME"]))
    with d: st.metric("Latest range", fmt_percent(latest["DAILY_RANGE_PCT"]))

    st.divider()
    c1, c2 = st.columns([1.7, 1])
    with c1:
        st.subheader("Price action")
        chart_data = history.copy()
        chart_data["TRADE_DATE"] = pd.to_datetime(chart_data["TRADE_DATE"])
        show_chart(candlestick(chart_data, 390))
    with c2:
        st.subheader("Session returns")
        ret = history[["TRADE_DATE", "DAILY_RETURN_PCT"]].copy()
        ret["TRADE_DATE"] = pd.to_datetime(ret["TRADE_DATE"])
        return_chart = (
            alt.Chart(ret)
            .mark_bar(cornerRadiusEnd=3)
            .encode(
                x=alt.X("TRADE_DATE:T", title=None),
                y=alt.Y("DAILY_RETURN_PCT:Q", title="Return %"),
                color=alt.condition(alt.datum.DAILY_RETURN_PCT >= 0, alt.value(UP), alt.value(DOWN)),
                tooltip=["TRADE_DATE", "DAILY_RETURN_PCT"],
            )
            .properties(height=390)
        )
        show_chart(return_chart)

    st.subheader("Trading volume")
    show_chart(volume_chart(chart_data, 240))

    st.subheader("Corporate actions")
    actions = run_query(f"""
        SELECT f.TICKER, c.COMPANY_NAME, f.ACTION_TYPE,
               f.EX_DATE, f.RECORD_DATE, f.PAY_DATE,
               f.ACTION_VALUE, f.RATIO, f.CURRENCY, f.STATUS
        FROM {DW}.FACT_CORPORATE_ACTIONS f
        LEFT JOIN {DW}.DIM_COMPANY c
          ON f.SK_COMPANY = c.SK_COMPANY
        WHERE f.TICKER = '{safe}'
        ORDER BY f.EX_DATE
    """)
    if actions.empty:
        st.info("No corporate actions recorded for this company.")
    else:
        st.dataframe(actions, use_container_width=True, hide_index=True)

# ============================================================
# PRICE HISTORY
# ============================================================
elif page == "Price History":
    page_header(
        "MARKET HISTORY",
        "Price History",
        "Interactive OHLC, volume, VWAP, turnover, and same-session performance for a selected company.",
    )

    companies = run_query(f"SELECT TICKER, COMPANY_NAME FROM {SEM}.COMPANY_PERFORMANCE ORDER BY COMPANY_NAME")
    labels = (companies["TICKER"].astype(str) + " — " + companies["COMPANY_NAME"].astype(str)).tolist()
    selected = st.selectbox("Company", labels)
    ticker = selected.split(" — ", 1)[0]
    safe = sql_escape(ticker)

    history = run_query(f"""
        SELECT FULL_DATE AS TRADE_DATE,
               OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME, VWAP,
               DAILY_RANGE, DAILY_RETURN_PCT, DAILY_RANGE_PCT,
               TURNOVER, USD_RATE, TURNOVER_USD
        FROM {SEM}.STOCK_DAILY_ANALYTICS
        WHERE TICKER = '{safe}'
        ORDER BY FULL_DATE
    """)

    if history.empty:
        st.warning("No price history available.")
        st.stop()

    latest = history.iloc[-1]
    a, b, c, d = st.columns(4)
    with a: st.metric("Latest close", fmt_decimal(latest["CLOSE"]))
    with b: st.metric("VWAP", fmt_decimal(latest["VWAP"]))
    with c: st.metric("Daily return", fmt_percent(latest["DAILY_RETURN_PCT"]))
    with d: st.metric("Volume", fmt_number(latest["VOLUME"]))

    chart_data = history.copy()
    chart_data["TRADE_DATE"] = pd.to_datetime(chart_data["TRADE_DATE"])

    st.subheader("OHLC")
    show_chart(candlestick(chart_data, 420))

    st.subheader("Volume")
    show_chart(volume_chart(chart_data, 250))

    st.subheader("Trading records")
    display = history.copy()
    for col in ["OPEN", "HIGH", "LOW", "CLOSE", "ADJ_CLOSE", "VWAP", "DAILY_RANGE", "DAILY_RETURN_PCT", "DAILY_RANGE_PCT", "TURNOVER", "USD_RATE", "TURNOVER_USD"]:
        if col in display.columns:
            display[col] = display[col].round(2)
    st.dataframe(display, use_container_width=True, hide_index=True)

# ============================================================
# SECTOR & EXCHANGE
# ============================================================
elif page == "Sector & Exchange":
    page_header(
        "CROSS-SECTIONAL ANALYTICS",
        "Sector & Exchange",
        "Compare trading activity, returns, volatility, VWAP, and company coverage across market segments.",
    )

    summary = run_query(f"""
        SELECT SECTOR, EXCHANGE_CODE, TOTAL_COMPANIES, TOTAL_TRADING_RECORDS,
               AVG_CLOSE_PRICE, AVG_DAILY_RETURN_PCT, AVG_INTRADAY_VOLATILITY_PCT,
               TOTAL_VOLUME, TOTAL_TURNOVER_USD
        FROM {SEM}.SECTOR_EXCHANGE_SUMMARY
        ORDER BY TOTAL_TURNOVER_USD DESC
    """)

    if summary.empty:
        st.warning("No sector/exchange data available.")
        st.stop()

    # Derive VWAP from the daily semantic view rather than inventing it in the UI.
    vwap = run_query(f"""
        SELECT SECTOR, EXCHANGE_CODE, AVG(VWAP) AS AVG_VWAP
        FROM {SEM}.STOCK_DAILY_ANALYTICS
        GROUP BY SECTOR, EXCHANGE_CODE
        ORDER BY AVG_VWAP DESC
    """)

    c1, c2 = st.columns(2)
    with c1:
        by_sector = summary.groupby("SECTOR", as_index=False)["TOTAL_VOLUME"].sum().sort_values("TOTAL_VOLUME", ascending=False)
        st.subheader("Trading Volume by Sector")
        show_chart(ranked_bar(by_sector, "TOTAL_VOLUME", "SECTOR", "Shares traded", BLUE, 330))
    with c2:
        by_sector = summary.groupby("SECTOR", as_index=False)["AVG_INTRADAY_VOLATILITY_PCT"].mean().sort_values("AVG_INTRADAY_VOLATILITY_PCT", ascending=False)
        st.subheader("Average Intraday Range")
        show_chart(ranked_bar(by_sector, "AVG_INTRADAY_VOLATILITY_PCT", "SECTOR", "Range %", AMBER, 330))

    c3, c4 = st.columns(2)
    with c3:
        by_exchange = summary.groupby("EXCHANGE_CODE", as_index=False)["TOTAL_VOLUME"].sum()
        st.subheader("Exchange Volume Share")
        show_chart(donut_chart(by_exchange, "EXCHANGE_CODE", "TOTAL_VOLUME", None, 330))
    with c4:
        st.subheader("Sector VWAP by Exchange")
        heat = (
            alt.Chart(vwap)
            .mark_rect(cornerRadius=4)
            .encode(
                x=alt.X("EXCHANGE_CODE:N", title=None),
                y=alt.Y("SECTOR:N", title=None, sort="-x"),
                color=alt.Color("AVG_VWAP:Q", title="Avg VWAP"),
                tooltip=["SECTOR", "EXCHANGE_CODE", alt.Tooltip("AVG_VWAP:Q", format=",.2f")],
            )
            .properties(height=330)
        )
        show_chart(heat)

    st.subheader("Sector / Exchange Aggregated Metrics")
    display = summary.copy()
    for col in ["AVG_CLOSE_PRICE", "AVG_DAILY_RETURN_PCT", "AVG_INTRADAY_VOLATILITY_PCT", "TOTAL_TURNOVER_USD"]:
        display[col] = display[col].round(2)
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Companies by Sector")
    sectors = sorted(summary["SECTOR"].dropna().unique().tolist())
    if sectors:
        selected_sector = st.selectbox("Sector", sectors)
        safe_sector = sql_escape(selected_sector)
        companies = run_query(f"""
            SELECT TICKER, COMPANY_NAME, INDUSTRY, EXCHANGE_CODE,
                   TRADING_DAYS, AVG_CLOSE, AVG_DAILY_RETURN_PCT,
                   TOTAL_VOLUME, TOTAL_TURNOVER_USD
            FROM {SEM}.COMPANY_PERFORMANCE
            WHERE SECTOR = '{safe_sector}'
            ORDER BY TOTAL_TURNOVER_USD DESC
        """)
        for col in ["AVG_CLOSE", "AVG_DAILY_RETURN_PCT", "TOTAL_TURNOVER_USD"]:
            if col in companies.columns:
                companies[col] = companies[col].round(2)
        st.dataframe(companies, use_container_width=True, hide_index=True)

# ============================================================
# CORPORATE ACTIONS
# ============================================================
elif page == "Corporate Actions":
    page_header(
        "EVENT CALENDAR",
        "Corporate Actions",
        "Splits, bonuses, buybacks, and dividends linked back to the SCD2 company dimension.",
    )

    actions = run_query(f"""
        SELECT f.ACTION_ID, f.TICKER, c.COMPANY_NAME, c.SECTOR, c.COUNTRY,
               f.ACTION_TYPE, f.EX_DATE, f.RECORD_DATE, f.PAY_DATE,
               f.ACTION_VALUE, f.RATIO, f.CURRENCY, f.STATUS
        FROM {DW}.FACT_CORPORATE_ACTIONS f
        LEFT JOIN {DW}.DIM_COMPANY c
          ON f.SK_COMPANY = c.SK_COMPANY
        ORDER BY f.EX_DATE
    """)

    if actions.empty:
        st.info("No corporate actions recorded.")
        st.stop()

    c1, c2 = st.columns(2)
    with c1:
        by_type = actions.groupby("ACTION_TYPE", as_index=False).size()
        by_type.columns = ["ACTION_TYPE", "COUNT"]
        st.subheader("Actions by Type")
        show_chart(donut_chart(by_type, "ACTION_TYPE", "COUNT", action_scale(), 320))
    with c2:
        by_sector = actions.groupby("SECTOR", as_index=False).size()
        by_sector.columns = ["SECTOR", "COUNT"]
        st.subheader("Actions by Sector")
        show_chart(ranked_bar(by_sector, "COUNT", "SECTOR", "Announcements", BLUE, 320))

    f1, f2, f3 = st.columns(3)
    with f1:
        types = ["All"] + sorted(actions["ACTION_TYPE"].dropna().unique().tolist())
        selected_type = st.selectbox("Action type", types)
    with f2:
        sectors = ["All"] + sorted(actions["SECTOR"].dropna().unique().tolist())
        selected_sector = st.selectbox("Sector", sectors)
    with f3:
        statuses = ["All"] + sorted(actions["STATUS"].dropna().unique().tolist())
        selected_status = st.selectbox("Status", statuses)

    filtered = actions.copy()
    if selected_type != "All":
        filtered = filtered[filtered["ACTION_TYPE"] == selected_type]
    if selected_sector != "All":
        filtered = filtered[filtered["SECTOR"] == selected_sector]
    if selected_status != "All":
        filtered = filtered[filtered["STATUS"] == selected_status]

    st.subheader(f"Events · {len(filtered):,}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ============================================================
# STOCK SCREENER
# ============================================================
elif page == "Stock Screener":
    page_header(
        "DISCOVERY",
        "Stock Screener",
        "Filter the trading feed using transparent daily metrics — no black-box scoring.",
    )

    dimensions = run_query(f"""
        SELECT DISTINCT SECTOR, EXCHANGE_CODE, MARKET_CAP_BAND
        FROM {SEM}.STOCK_DAILY_ANALYTICS
        WHERE SECTOR IS NOT NULL
        ORDER BY SECTOR, EXCHANGE_CODE, MARKET_CAP_BAND
    """)

    c1, c2, c3 = st.columns(3)
    with c1:
        sectors = ["All"] + sorted(dimensions["SECTOR"].dropna().unique().tolist())
        selected_sector = st.selectbox("Sector", sectors)
    with c2:
        exchanges = ["All"] + sorted(dimensions["EXCHANGE_CODE"].dropna().unique().tolist())
        selected_exchange = st.selectbox("Exchange", exchanges)
    with c3:
        caps = ["All"] + sorted(dimensions["MARKET_CAP_BAND"].dropna().unique().tolist())
        selected_cap = st.selectbox("Market-cap band", caps)

    c4, c5 = st.columns(2)
    with c4:
        return_range = st.slider("Intraday return %", -100.0, 100.0, (-100.0, 100.0), 0.5)
    with c5:
        min_volume = st.number_input("Minimum volume", min_value=0, value=0, step=100000)

    conditions = [
        f"DAILY_RETURN_PCT BETWEEN {return_range[0]} AND {return_range[1]}",
        f"VOLUME >= {min_volume}",
    ]
    if selected_sector != "All":
        conditions.append(f"SECTOR = '{sql_escape(selected_sector)}'")
    if selected_exchange != "All":
        conditions.append(f"EXCHANGE_CODE = '{sql_escape(selected_exchange)}'")
    if selected_cap != "All":
        conditions.append(f"MARKET_CAP_BAND = '{sql_escape(selected_cap)}'")

    screened = run_query(f"""
        SELECT FULL_DATE AS TRADE_DATE, TICKER, COMPANY_NAME,
               SECTOR, INDUSTRY, MARKET_CAP_BAND, EXCHANGE_CODE,
               OPEN, HIGH, LOW, CLOSE, VWAP,
               DAILY_RETURN_PCT, DAILY_RANGE_PCT, VOLUME,
               TURNOVER_USD
        FROM {SEM}.STOCK_DAILY_ANALYTICS
        WHERE {' AND '.join(conditions)}
        ORDER BY DAILY_RETURN_PCT DESC
        LIMIT 100
    """)

    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Matching records", f"{len(screened):,}")
    with m2: st.metric("Positive records", f"{int((screened['DAILY_RETURN_PCT'] > 0).sum()):,}" if not screened.empty else "0")
    with m3: st.metric("Negative records", f"{int((screened['DAILY_RETURN_PCT'] < 0).sum()):,}" if not screened.empty else "0")

    if screened.empty:
        st.info("No trading records match the selected filters.")
    else:
        st.subheader("Return distribution")
        hist = (
            alt.Chart(screened)
            .mark_bar(color=AMBER)
            .encode(
                x=alt.X("DAILY_RETURN_PCT:Q", bin=alt.Bin(maxbins=14), title="Intraday return %"),
                y=alt.Y("count():Q", title="Records"),
                tooltip=[alt.Tooltip("count():Q", title="Records")],
            )
            .properties(height=260)
        )
        show_chart(hist)

        display = screened.copy()
        for col in ["OPEN", "HIGH", "LOW", "CLOSE", "VWAP", "DAILY_RETURN_PCT", "DAILY_RANGE_PCT", "TURNOVER_USD"]:
            if col in display.columns:
                display[col] = display[col].round(2)
        st.dataframe(display, use_container_width=True, hide_index=True)

        csv = display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download screened records",
            data=csv,
            file_name="stock_screener_results.csv",
            mime="text/csv",
        )

# ============================================================
# FOOTER
# ============================================================
st.sidebar.divider()
st.sidebar.caption("S3 → Snowpipe → RAW → dbt → DW/SEM → Native Streamlit")
