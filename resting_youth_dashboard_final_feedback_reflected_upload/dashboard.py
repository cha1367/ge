import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="쉬었음 청년 사회 확산 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
YEARS = list(range(2015, 2026))


PLOT_BG = "#0b1020"
PAPER_BG = "#0b1020"
CARD_BG = "#111827"
CARD_BG_2 = "#0f172a"
GRID = "#243044"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
DIM = "#64748b"
RED = "#ff4b4b"
BLUE = "#60a5fa"
AMBER = "#f59e0b"
GREEN = "#22c55e"
PURPLE = "#a78bfa"

# ─────────────────────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255,75,75,0.12), transparent 32%),
        linear-gradient(180deg, #0b1020 0%, #0e1117 55%, #0b1020 100%);
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1280px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b16 0%, #0f172a 100%);
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(17, 24, 39, 0.72);
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 0.55rem 0.7rem;
    margin: 0.25rem 0;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    border-color: #ff4b4b;
    background: rgba(255, 75, 75, 0.08);
}

.hero {
    background:
        linear-gradient(135deg, rgba(255,75,75,0.14), rgba(96,165,250,0.08)),
        linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid #263244;
    border-left: 5px solid #ff4b4b;
    padding: 2rem 2.3rem;
    border-radius: 18px;
    margin-bottom: 1.4rem;
    box-shadow: 0 18px 40px rgba(0,0,0,0.22);
}

.hero .eyebrow {
    color: #ff8a8a;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.hero h1 {
    font-size: 2.15rem;
    line-height: 1.22;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.6rem 0;
}

.hero p {
    font-size: 1rem;
    color: #b6c2d1;
    margin: 0;
    line-height: 1.75;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.4rem 0 0.8rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #243044;
}

.section-badge {
    background: linear-gradient(135deg, #ff4b4b, #fb7185);
    color: white;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 5px 11px;
    border-radius: 999px;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
}

.section-subtitle {
    color: #9ca3af;
    margin-top: -0.2rem;
    margin-bottom: 1rem;
    line-height: 1.7;
    font-size: 0.92rem;
}

.metric-card {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border: 1px solid #243044;
    border-radius: 16px;
    padding: 1.2rem 1.25rem;
    height: 100%;
    box-shadow: 0 12px 28px rgba(0,0,0,0.16);
}

.metric-card .label {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.metric-card .value {
    font-size: 1.9rem;
    line-height: 1.1;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.4rem;
}

.metric-card .value.red { color: #ff4b4b; }
.metric-card .value.blue { color: #60a5fa; }
.metric-card .value.amber { color: #f59e0b; }
.metric-card .value.green { color: #22c55e; }
.metric-card .value.purple { color: #a78bfa; }

.metric-card .sub {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.55;
}

.chart-card {
    background: #0b1020;
    border: 1px solid #243044;
    border-radius: 16px;
    padding: 0.85rem 0.9rem 0.35rem 0.9rem;
    margin-top: 0.85rem;
    box-shadow: 0 12px 28px rgba(0,0,0,0.14);
}

.connector {
    background: rgba(96,165,250,0.08);
    border: 1px solid rgba(96,165,250,0.16);
    border-left: 4px solid #60a5fa;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    margin: 1rem 0;
    color: #b6c2d1;
    font-size: 0.9rem;
    line-height: 1.7;
}

.note {
    font-size: 0.78rem;
    color: #7b8794;
    margin-top: 0.55rem;
    line-height: 1.65;
}

.flow-card {
    background: linear-gradient(180deg, rgba(17,24,39,0.94), rgba(15,23,42,0.94));
    border: 1px solid #243044;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    height: 100%;
}

.flow-card .num {
    color: #ff4b4b;
    font-weight: 900;
    font-size: 0.8rem;
    margin-bottom: 0.45rem;
}

.flow-card .title {
    color: #ffffff;
    font-weight: 800;
    font-size: 1rem;
    margin-bottom: 0.45rem;
}

.flow-card .desc {
    color: #94a3b8;
    font-size: 0.83rem;
    line-height: 1.65;
}

.policy-card {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border: 1px solid #243044;
    border-radius: 16px;
    padding: 1.25rem;
    height: 100%;
}

.policy-card h4 {
    color: #ffffff;
    font-size: 1rem;
    margin: 0.4rem 0 0.75rem 0;
}

.policy-card p, .policy-card li {
    color: #aeb8c6;
    font-size: 0.86rem;
    line-height: 1.75;
}



.policy-grid-card {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border: 1px solid #243044;
    border-radius: 22px;
    padding: 1.65rem 1.7rem 1.55rem 1.7rem;
    min-height: 430px;
    height: 100%;
    box-shadow: 0 18px 40px rgba(0,0,0,0.18);
}
.policy-grid-card .policy-kicker {
    color: #d1d5db;
    font-size: 1.02rem;
    font-weight: 800;
    margin-bottom: 1.05rem;
}
.policy-grid-card .policy-title {
    color: #ffffff;
    font-size: 1.22rem;
    font-weight: 900;
    line-height: 1.45;
    margin-bottom: 1.15rem;
}
.policy-grid-card .policy-desc {
    color: #aeb8c6;
    font-size: 0.92rem;
    line-height: 1.85;
    margin-bottom: 1.2rem;
}
.policy-grid-card ul {
    margin: 0;
    padding-left: 1.1rem;
}
.policy-grid-card li {
    color: #b6c2d1;
    font-size: 0.9rem;
    line-height: 1.85;
    margin-bottom: 0.35rem;
}
.policy-highlight-red { color: #ff4b4b; font-weight: 900; }
.policy-highlight-blue { color: #60a5fa; font-weight: 900; }
.policy-highlight-amber { color: #f59e0b; font-weight: 900; }
.policy-highlight-purple { color: #a78bfa; font-weight: 900; }
.policy-final-box {
    background: linear-gradient(135deg, rgba(96,165,250,0.12), rgba(255,75,75,0.10));
    border: 1px solid #243044;
    border-left: 4px solid #60a5fa;
    border-radius: 18px;
    padding: 1.45rem 1.65rem;
    margin-top: 1.25rem;
}
.policy-final-box h3 {
    color: #ffffff;
    margin: 0 0 0.7rem 0;
    font-size: 1.15rem;
}
.policy-final-box p {
    color: #aeb8c6;
    line-height: 1.85;
    margin: 0;
    font-size: 0.95rem;
}
.policy-step {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid #243044;
    border-radius: 16px;
    padding: 1rem 1.05rem;
    height: 100%;
}
.policy-step .step-no {
    color: #60a5fa;
    font-weight: 900;
    font-size: 0.8rem;
    margin-bottom: 0.4rem;
}
.policy-step .step-title {
    color: #ffffff;
    font-weight: 850;
    font-size: 0.98rem;
    margin-bottom: 0.45rem;
}
.policy-step .step-desc {
    color: #9ca3af;
    font-size: 0.84rem;
    line-height: 1.65;
}

.sidebar-card {
    background: rgba(17, 24, 39, 0.72);
    border: 1px solid #243044;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.sidebar-card .side-title {
    font-weight: 800;
    color: #ffffff;
    font-size: 1rem;
    margin-bottom: 0.35rem;
}

.sidebar-card .side-text {
    color: #94a3b8;
    font-size: 0.82rem;
    line-height: 1.55;
}

hr {
    border-color: #243044 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    background: #111827;
    border: 1px solid #243044;
    border-radius: 999px;
    padding: 0.5rem 1rem;
}

.stTabs [aria-selected="true"] {
    border-color: #ff4b4b !important;
    color: #ffffff !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────
def read_csv_safely(path: Path) -> pd.DataFrame:
    """KOSIS CSV는 보통 CP949/EUC-KR이므로 여러 인코딩을 순차 시도."""
    last_error = None
    for enc in ("cp949", "euc-kr", "utf-8-sig", "utf-8"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as exc:  # pragma: no cover - Streamlit 실행용 안전장치
            last_error = exc
    raise last_error


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> pd.DataFrame:
    """CSV가 있으면 CSV를 우선 사용하고, 없으면 기존 수치로 대체."""
    try:
        resting_raw = read_csv_safely(BASE_DIR / "resting_youth_20_29.csv")
        inactive_raw = read_csv_safely(BASE_DIR / "inactive_population_20_29.csv")
        population_raw = read_csv_safely(BASE_DIR / "youth_population_1age.csv")

        year_cols = [c for c in resting_raw.columns if str(c).strip().isdigit()]
        year_cols = [str(c) for c in year_cols]
        years = [int(c) for c in year_cols]

        resting = pd.to_numeric(resting_raw.loc[0, year_cols], errors="coerce").astype(float).to_list()
        inactive = pd.to_numeric(inactive_raw.loc[0, year_cols], errors="coerce").astype(float).to_list()

        # youth_population_1age.csv: 1행은 단위 설명, 이후 전국 20세~29세 행을 합산
        age_col = population_raw.columns[1]
        pop_body = population_raw.iloc[1:].copy()
        pop_body["age_num"] = pop_body[age_col].astype(str).str.extract(r"(\d+)").astype(float)
        pop_20s = pop_body[pop_body["age_num"].between(20, 29)]
        population = (
            pop_20s[year_cols]
            .apply(pd.to_numeric, errors="coerce")
            .sum(axis=0)
            .div(1000)
            .round(0)
            .astype(int)
            .to_list()
        )
    except Exception:
        years = YEARS
        resting = [273, 245, 270, 283, 332, 415, 393, 362, 371, 389, 408]  # 천명
        inactive = [2277, 2234, 2297, 2303, 2328, 2503, 2443, 2245, 2163, 2085, 2048]  # 천명
        population = [6699, 6758, 6811, 6824, 6810, 6806, 6656, 6417, 6197, 5956, 5682]  # 천명

    data = pd.DataFrame(
        {
            "연도": years,
            "쉬었음_청년": resting,
            "전체_비경활": inactive,
            "청년_인구": population,
        }
    )

    # EIS 고용행정통계: 월별 피보험자현황, 연령_10세 20~29세, 각 연도 12월 말 기준
    try:
        insured_raw = read_csv_safely(BASE_DIR / "employment_insured_20_29.csv")
        insured_raw.columns = [str(c).strip().replace("﻿", "") for c in insured_raw.columns]
        insured_raw["year"] = pd.to_numeric(insured_raw["year"], errors="coerce").astype("Int64")
        insured_raw["insured_20_29"] = pd.to_numeric(insured_raw["insured_20_29"], errors="coerce")
        insured_raw = insured_raw.dropna(subset=["year", "insured_20_29"])
        insured_map = dict(zip(insured_raw["year"].astype(int), insured_raw["insured_20_29"].astype(int)))
    except Exception:
        insured_map = {
            2015: 2149763,
            2016: 2184062,
            2017: 2211174,
            2018: 2302667,
            2019: 2340599,
            2020: 2360286,
            2021: 2412702,
            2022: 2382979,
            2023: 2344848,
            2024: 2247167,
            2025: 2157846,
        }

    data["고용보험피보험자_명"] = data["연도"].map(insured_map).astype(float)
    data["고용보험피보험자_만명"] = (data["고용보험피보험자_명"] / 10000).round(1)
    data["고용보험피보험자_비율"] = (
        data["고용보험피보험자_명"] / (data["청년_인구"] * 1000) * 100
    ).round(1)
    base_population_2015 = float(data.loc[data["연도"] == 2015, "청년_인구"].iloc[0])
    data["고용보험피보험자_2015인구기준비율"] = (
        data["고용보험피보험자_명"] / (base_population_2015 * 1000) * 100
    ).round(1)
    data["고용보험피보험자_증가율"] = (data["고용보험피보험자_명"].pct_change() * 100).round(1)

    data["쉬었음_비율"] = (data["쉬었음_청년"] / data["전체_비경활"] * 100).round(1)
    data["쉬었음_증가율"] = (data["쉬었음_청년"].pct_change() * 100).round(1)
    data["비경활_증가율"] = (data["전체_비경활"].pct_change() * 100).round(1)
    data["인구_증가율"] = (data["청년_인구"].pct_change() * 100).round(1)
    data["인구대비_쉬었음비율"] = (data["쉬었음_청년"] / data["청년_인구"] * 100).round(2)

    # 경제 보강 데이터: 음식점 및 주점업 서비스업생산지수(불변지수, 2020=100)
    try:
        food_raw = read_csv_safely(BASE_DIR / "food_service_production_index_clean.csv")
        food_raw.columns = [str(c).strip().replace("﻿", "") for c in food_raw.columns]
        food_raw["year"] = pd.to_numeric(food_raw["year"], errors="coerce").astype("Int64")
        food_raw["food_service_index"] = pd.to_numeric(food_raw["food_service_index"], errors="coerce")
        food_raw = food_raw.dropna(subset=["year", "food_service_index"])
        food_index_map = dict(zip(food_raw["year"].astype(int), food_raw["food_service_index"].astype(float)))
    except Exception:
        food_index_map = {
            2015: 122.9, 2016: 125.5, 2017: 123.4, 2018: 120.7, 2019: 119.4,
            2020: 100.0, 2021: 100.7, 2022: 116.6, 2023: 117.0, 2024: 115.3, 2025: 114.3,
        }

    data["음식점주점업_생산지수"] = data["연도"].map(food_index_map).astype(float)
    data["음식점주점업_전년대비"] = data["음식점주점업_생산지수"].diff().round(1)

    # 경제 파생지표: 청년 비활동-생활서비스 부담지수
    # 2020년을 100으로 둔 상대지표.
    # 쉬었음 청년 규모가 커질수록, 음식점·주점업 생산지수가 낮을수록 부담지수가 상승한다.
    _base_resting = float(data.loc[data["연도"] == 2020, "쉬었음_청년"].iloc[0])
    data["쉬었음_상대지수"] = (data["쉬었음_청년"] / _base_resting * 100).round(1)
    data["청년비활동_생활서비스부담지수"] = (
        data["쉬었음_상대지수"] / (data["음식점주점업_생산지수"] / 100)
    ).round(1)

    # 노동시장 보강 데이터: 청년 취업자 수 + 미충원인원 정제본
    try:
        labor_raw = read_csv_safely(BASE_DIR / "labor_market_derived_clean.csv")
        labor_raw.columns = [str(c).strip().replace("﻿", "") for c in labor_raw.columns]
        labor_raw["year"] = pd.to_numeric(labor_raw["year"], errors="coerce").astype("Int64")
        labor_raw = labor_raw.dropna(subset=["year"])

        employed_map = dict(zip(labor_raw["year"].astype(int), pd.to_numeric(labor_raw["employed_youth_20_29_thousand"], errors="coerce")))
        unfilled_map = dict(zip(labor_raw["year"].astype(int), pd.to_numeric(labor_raw["unfilled_workers"], errors="coerce")))
        basis_map = dict(zip(labor_raw["year"].astype(int), labor_raw.get("business_size_basis", "")))
        note_map = dict(zip(labor_raw["year"].astype(int), labor_raw.get("validity_note", "")))
    except Exception:
        # CSV가 없을 때도 GitHub에서 dashboard.py만 수정해 실행 가능하도록 fallback 내장
        employed_map = {
            2015: 3619, 2016: 3664, 2017: 3660, 2018: 3699, 2019: 3747, 2020: 3601,
            2021: 3706, 2022: 3818, 2023: 3736, 2024: 3612, 2025: 3442,
        }
        unfilled_map = {
            2015: 90580, 2016: 95282, 2017: 85052, 2018: 83911, 2019: 75909, 2020: 67188,
            2021: 111769, 2022: 153262, 2023: 114397, 2024: 102795, 2025: 85752,
        }
        basis_map = {y: "5인이상" for y in YEARS}
        note_map = {y: "전국·전산업·5인 이상 사업체, 각 연도 하반기(2/2) 기준" for y in YEARS}

    data["청년취업자_천명"] = data["연도"].map(employed_map).astype(float)
    data["미충원인원_명"] = data["연도"].map(unfilled_map).astype(float)
    data["미충원_기준"] = data["연도"].map(basis_map)
    data["미충원_주의"] = data["연도"].map(note_map)
    data["취업자대비_쉬었음비율"] = (
        data["쉬었음_청년"] / data["청년취업자_천명"] * 100
    ).round(2)
    data["청년비활동_미충원배수"] = (
        data["쉬었음_청년"] * 1000 / data["미충원인원_명"]
    ).round(2)
    return data


df = load_dashboard_data()
years = df["연도"].astype(int).to_list()

# ─────────────────────────────────────────────────────────────
# Helper components
# ─────────────────────────────────────────────────────────────
def base_layout(title: str = "", yaxis_title: str = "", xaxis_title: str = "연도") -> dict:
    return dict(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT, family="Noto Sans KR"),
        title=dict(text=title, font=dict(size=15, color=TEXT, family="Noto Sans KR"), x=0.01),
        xaxis=dict(
            title=xaxis_title,
            gridcolor=GRID,
            color=TEXT,
            tickmode="array",
            tickvals=years,
            ticktext=[str(y) for y in years],
            zerolinecolor=GRID,
        ),
        yaxis=dict(title=yaxis_title, gridcolor=GRID, color=TEXT, zerolinecolor=GRID),
        margin=dict(l=46, r=28, t=58, b=42),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT), orientation="h", y=1.07),
        hovermode="x unified",
        height=430,
    )


def section_header(step: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
<div class="section-header">
    <span class="section-badge">{step}</span>
    <span class="section-title">{title}</span>
</div>
""",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, sub: str = "", color: str = "red") -> None:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="label">{label}</div>
    <div class="value {color}">{value}</div>
    <div class="sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def chart_start() -> None:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)


def chart_end() -> None:
    st.markdown('</div>', unsafe_allow_html=True)


def hero() -> None:
    st.markdown(
        """
<div class="hero">
    <div class="eyebrow">Youth Inactivity Dashboard · 2015—2025</div>
    <h1>쉬었음 청년, 어디까지 퍼지나?</h1>
    <p>
        20~29세 쉬었음 청년 증가가 <strong>기업 미충원과의 연결 실패 → 생활서비스 업종 흐름 → 고용보험 편입 변화</strong>와
        어떻게 연결될 수 있는지 관측자료와 상대 파생지표로 보여줍니다.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


def add_covid_band(fig: go.Figure) -> None:
    fig.add_vrect(
        x0=2019.5,
        x1=2021.5,
        fillcolor="rgba(255, 75, 75, 0.08)",
        line_width=0,
        annotation_text="코로나19 구간",
        annotation_position="top left",
        annotation_font_color="#fca5a5",
    )


def latest_value(column: str):
    return df[column].iloc[-1]

# ─────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────
st.sidebar.markdown(
    """
<div class="sidebar-card">
    <div class="side-title">📊 쉬었음 청년 대시보드</div>
    <div class="side-text">왼쪽 메뉴를 클릭하면 화면이 단계별로 전환됩니다.</div>
</div>
""",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "페이지 이동",
    [
        "🏠 개요",
        "① 문제 규모",
        "② 노동시장",
        "③ 경제",
        "④ 재정",
        "⑤ 정책·결론",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
<div class="sidebar-card">
    <div class="side-title">2025 핵심 수치</div>
    <div class="side-text">
        쉬었음 청년: <b style="color:#ff4b4b;">{int(latest_value('쉬었음_청년')):,}천명</b><br>
        20대 인구 대비: <b style="color:#f59e0b;">{latest_value('인구대비_쉬었음비율'):.2f}%</b><br>        생활서비스 부담지수: <b style="color:#60a5fa;">{latest_value('청년비활동_생활서비스부담지수'):.1f}</b><br>
        2015 인구 기준 피보험자: <b style="color:#a78bfa;">{latest_value('고용보험피보험자_2015인구기준비율'):.1f}%</b>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.caption("자료: KOSIS 경제활동인구조사·주민등록인구통계·서비스업동향조사, EIS 고용행정통계, 고용노동통계 / 단위: 천명·명·만명·지수")

# ─────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────
def page_overview() -> None:
    hero()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("2025년 쉬었음 청년", f"{int(latest_value('쉬었음_청년')):,}천명", "20~29세 기준", "red")
    with c2:
        diff = int(df["쉬었음_청년"].iloc[-1] - df["쉬었음_청년"].iloc[0])
        metric_card("2015년 대비", f"+{diff:,}천명", f"{int(df['쉬었음_청년'].iloc[0])}천명 → {int(df['쉬었음_청년'].iloc[-1])}천명", "blue")
    with c3:
        metric_card("생활서비스 부담지수", f"{latest_value('청년비활동_생활서비스부담지수'):.1f}", "2020=100 기준", "amber")
    with c4:
        metric_card("2015 인구 기준 피보험자", f"{latest_value('고용보험피보험자_2015인구기준비율'):.1f}%", f"실제 피보험자 {latest_value('고용보험피보험자_만명'):.1f}만명", "purple")

    section_header("FLOW", "분석 흐름", "이 대시보드는 한 화면에 모든 차트를 몰아넣지 않고, 왼쪽 사이드바에서 단계별로 넘겨보는 구조입니다.")
    f1, f2, f3, f4, f5 = st.columns(5)
    flow_items = [
        ("STEP 1", "문제 규모", "쉬었음 청년 수와 20대 인구 흐름 확인"),
        ("STEP 2", "노동시장", "비경활 내 비중과 기업 미충원 배수 확인"),
        ("STEP 3", "경제", "쉬었음 상대규모와 음식점·주점업 생산 흐름 결합"),
        ("STEP 4", "재정", "고용보험 피보험자와 인구 감소 보정 비율 확인"),
        ("STEP 5", "정책", "재진입 경로와 사회보험 유지 관점의 대책 정리"),
    ]
    for col, item in zip([f1, f2, f3, f4, f5], flow_items):
        with col:
            st.markdown(
                f"""
<div class="flow-card">
    <div class="num">{item[0]}</div>
    <div class="title">{item[1]}</div>
    <div class="desc">{item[2]}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="connector">핵심 논리: 본 대시보드는 20~29세 단일 구간을 기준으로, 쉬었음 청년 증가가 기업 미충원·생활서비스 업종 흐름·고용보험 편입 변화와 어떻게 연결될 수 있는지 파생지표로 재구성합니다. 단, 이는 직접 인과 증명이 아니라 구조적 확산 가능성 분석입니다.</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["연도"],
            y=df["쉬었음_청년"],
            name="쉬었음 청년",
            marker_color=[RED if y >= 2020 else "#4a6fa5" for y in df["연도"]],
            hovertemplate="%{x}년: %{y:,}천명<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["인구대비_쉬었음비율"],
            name="20대 인구 대비 비율",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=AMBER, width=2.5),
            marker=dict(size=7),
            hovertemplate="%{x}년: %{y:.2f}%<extra></extra>",
        )
    )
    add_covid_band(fig)
    fig.update_layout(**base_layout("대시보드 요약: 쉬었음 청년 수와 20대 인구 대비 비율", "쉬었음 청년 수 (천명)"))
    fig.update_layout(
        yaxis2=dict(title="20대 인구 대비 (%)", overlaying="y", side="right", gridcolor=GRID, color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT), orientation="h", y=1.08),
    )
    chart_start()
    st.plotly_chart(fig, use_container_width=True)
    chart_end()


def page_scale() -> None:
    hero()
    section_header("STEP 1", "문제 규모 확인", "2015~2025년 20~29세 쉬었음 청년 수가 어느 정도 규모로 변했는지 확인합니다.")

    peak_idx = df["쉬었음_청년"].idxmax()
    peak_year = int(df.loc[peak_idx, "연도"])
    peak_value = int(df.loc[peak_idx, "쉬었음_청년"])
    pop_change = int(df["청년_인구"].iloc[-1] - df["청년_인구"].iloc[0])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025년 쉬었음 청년", f"{int(df['쉬었음_청년'].iloc[-1]):,}천명", "20~29세 기준", "red")
    with c2:
        metric_card("최고점", f"{peak_value:,}천명", f"{peak_year}년", "blue")
    with c3:
        metric_card("20대 인구 변화", f"{pop_change:,}천명", f"2015년 {int(df['청년_인구'].iloc[0]):,}천명 → 2025년 {int(df['청년_인구'].iloc[-1]):,}천명", "amber")

    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=df["연도"],
            y=df["쉬었음_청년"],
            marker_color=[RED if year >= 2020 else "#4a6fa5" for year in df["연도"]],
            name="쉬었음 청년 수",
            hovertemplate="%{x}년: %{y:,}천명<extra></extra>",
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["쉬었음_청년"],
            mode="lines+markers",
            line=dict(color=RED, width=2, dash="dot"),
            marker=dict(size=6),
            name="추이",
            hovertemplate="%{x}년: %{y:,}천명<extra></extra>",
        )
    )
    add_covid_band(fig1)
    fig1.update_layout(**base_layout("20~29세 쉬었음 청년 수 추이", "천명"))
    chart_start()
    st.plotly_chart(fig1, use_container_width=True)
    chart_end()

    st.markdown('<div class="connector">해석: 20대 전체 인구는 감소하고 있는데, 쉬었음 청년 규모는 2015년보다 높은 수준입니다. 그래서 단순 인구수보다 <b>20대 인구 대비 비율</b>을 함께 봐야 합니다.</div>', unsafe_allow_html=True)

    fig1b = go.Figure()
    fig1b.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["청년_인구"],
            mode="lines+markers",
            name="20~29세 인구",
            line=dict(color=BLUE, width=2.8),
            marker=dict(size=7),
            hovertemplate="%{x}년: %{y:,}천명<extra></extra>",
        )
    )
    fig1b.update_layout(**base_layout("20~29세 전체 인구 추이", "천명"))
    chart_start()
    st.plotly_chart(fig1b, use_container_width=True)
    chart_end()


def page_labor() -> None:
    hero()
    section_header(
        "STEP 2",
        "노동시장 관점 — 기업의 인력 공백과 청년 비활동이 함께 나타나는가?",
        "비경제활동 내부의 쉬었음 비중을 확인하고, 청년 취업자 수·미충원인원을 결합해 노동시장 미스매치 가능성을 봅니다.",
    )

    latest_rate = float(df["쉬었음_비율"].iloc[-1])
    latest_rest_to_emp = float(df["취업자대비_쉬었음비율"].iloc[-1])
    latest_mismatch = float(df["청년비활동_미충원배수"].iloc[-1])
    latest_unfilled = int(df["미충원인원_명"].iloc[-1])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025 비경활 중 쉬었음 비율", f"{latest_rate:.1f}%", "쉬었음 청년 ÷ 전체 비경활", "red")
    with c2:
        metric_card("취업자 대비 쉬었음 비율", f"{latest_rest_to_emp:.2f}%", "쉬었음 청년 ÷ 20대 취업자", "blue")
    with c3:
        metric_card("청년 비활동-미충원 배수", f"{latest_mismatch:.2f}배", f"미충원인원 {latest_unfilled:,}명 기준", "amber")

    st.markdown(
        """
<div class="connector">
    노동시장 파트의 핵심은 중소기업 인력난을 직접 증명하는 것이 아니라,
    <b>기업은 인원을 채우지 못하고, 동시에 청년은 노동시장 밖에 머무는 구조가 함께 나타나는지</b>를 확인하는 것입니다.
    미충원인원 대비 쉬었음 청년 규모는 노동시장 미스매치 가능성을 보여주는 보조 파생지표입니다.
</div>
""",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📊 비경활 중 쉬었음", "👥 취업자 대비 쉬었음", "🏭 미충원 배수"])

    with tab1:
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=df["연도"],
                y=df["쉬었음_비율"],
                mode="lines+markers+text",
                line=dict(color=RED, width=2.8),
                marker=dict(size=8),
                text=[f"{v:.1f}%" for v in df["쉬었음_비율"]],
                textposition="top center",
                textfont=dict(size=10, color=TEXT),
                name="비경활 중 쉬었음 비율",
                hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
            )
        )
        add_covid_band(fig3)
        fig3.update_layout(**base_layout("비경제활동인구 중 '쉬었음' 비율", "비율 (%)"))
        chart_start()
        st.plotly_chart(fig3, use_container_width=True)
        chart_end()
        st.markdown('<p class="note">※ 수식: 쉬었음 청년 수 ÷ 전체 비경제활동인구(20~29세) × 100</p>', unsafe_allow_html=True)

    with tab2:
        fig_emp = go.Figure()
        fig_emp.add_trace(
            go.Bar(
                x=df["연도"],
                y=df["청년취업자_천명"],
                marker_color=[BLUE if y < 2020 else "#4a6fa5" for y in df["연도"]],
                name="20~29세 취업자 수",
                hovertemplate="%{x}년: %{y:,}천명<extra></extra>",
            )
        )
        fig_emp.add_trace(
            go.Scatter(
                x=df["연도"],
                y=df["취업자대비_쉬었음비율"],
                name="취업자 대비 쉬었음 비율",
                mode="lines+markers+text",
                yaxis="y2",
                line=dict(color=AMBER, width=2.8),
                marker=dict(size=7),
                text=[f"{v:.1f}%" for v in df["취업자대비_쉬었음비율"]],
                textposition="top center",
                textfont=dict(size=10, color=TEXT),
                hovertemplate="%{x}년: %{y:.2f}%<extra></extra>",
            )
        )
        add_covid_band(fig_emp)
        fig_emp.update_layout(**base_layout("20대 취업자 수와 취업자 대비 쉬었음 비율", "취업자 수 (천명)"))
        fig_emp.update_layout(
            yaxis2=dict(title="취업자 대비 쉬었음 (%)", overlaying="y", side="right", gridcolor=GRID, color=TEXT),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT), orientation="h", y=1.08),
        )
        chart_start()
        st.plotly_chart(fig_emp, use_container_width=True)
        chart_end()
        st.markdown('<p class="note">※ 수식: 쉬었음 청년 수 ÷ 20~29세 취업자 수 × 100. 단위는 모두 천명 기준입니다.</p>', unsafe_allow_html=True)

    with tab3:
        fig_mis = go.Figure()
        fig_mis.add_trace(
            go.Bar(
                x=df["연도"],
                y=df["미충원인원_명"],
                marker_color=[PURPLE if y >= 2021 else "#4a6fa5" for y in df["연도"]],
                name="미충원인원",
                hovertemplate="%{x}년: %{y:,}명<extra></extra>",
            )
        )
        fig_mis.add_trace(
            go.Scatter(
                x=df["연도"],
                y=df["청년비활동_미충원배수"],
                name="청년 비활동-미충원 배수",
                mode="lines+markers+text",
                yaxis="y2",
                line=dict(color=RED, width=2.8),
                marker=dict(size=7),
                text=[f"{v:.2f}배" for v in df["청년비활동_미충원배수"]],
                textposition="top center",
                textfont=dict(size=10, color=TEXT),
                hovertemplate="%{x}년: %{y:.2f}배<extra></extra>",
            )
        )
        add_covid_band(fig_mis)
        fig_mis.update_layout(**base_layout("기업 미충원인원과 청년 비활동-미충원 배수", "미충원인원 (명)"))
        fig_mis.update_layout(
            yaxis2=dict(title="배수", overlaying="y", side="right", gridcolor=GRID, color=TEXT),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT), orientation="h", y=1.08),
        )
        chart_start()
        st.plotly_chart(fig_mis, use_container_width=True)
        chart_end()
        st.markdown(
            '<p class="note">※ 수식: 쉬었음 청년 수(천명) × 1000 ÷ 미충원인원(명). 값은 “미충원인원 1명당 쉬었음 청년이 몇 명 존재하는가”를 뜻합니다. 쉬었음 청년이 해당 일자리를 곧바로 채울 수 있다는 의미는 아닙니다.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="note">※ 미충원인원은 고용노동통계 직종별사업체노동력조사 기준이며, 전국·전산업·5인 이상 사업체의 각 연도 하반기(2/2) 값을 사용했습니다.</p>',
            unsafe_allow_html=True,
        )



def page_economy() -> None:
    hero()
    section_header(
        "STEP 3",
        "경제 관점 — 청년 비활동이 생활서비스 흐름과 어떻게 연결되는가?",
        "금액 추정 대신, 쉬었음 청년 상대규모와 음식점·주점업 생산지수를 결합한 상대지표로 생활서비스 업종의 부담 가능성을 봅니다.",
    )

    latest_resting_index = float(df["쉬었음_상대지수"].iloc[-1])
    latest_food_index = float(df["음식점주점업_생산지수"].iloc[-1])
    latest_service_pressure = float(df["청년비활동_생활서비스부담지수"].iloc[-1])
    pressure_change_2020 = latest_service_pressure - 100

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("쉬었음 청년 상대규모", f"{latest_resting_index:.1f}", "2020=100 기준", "red")
    with c2:
        metric_card("음식점·주점업 생산지수", f"{latest_food_index:.1f}", "불변지수, 2020=100", "blue")
    with c3:
        metric_card("생활서비스 부담지수", f"{latest_service_pressure:.1f}", f"2020=100 대비 {pressure_change_2020:+.1f}p", "amber")

    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["쉬었음_상대지수"],
            mode="lines+markers+text",
            line=dict(color=RED, width=2.8),
            marker=dict(size=8),
            text=[f"{v:.1f}" for v in df["쉬었음_상대지수"]],
            textposition="top center",
            textfont=dict(size=10, color=TEXT),
            name="쉬었음 청년 상대규모",
            hovertemplate="%{x}년: %{y:.1f}<extra></extra>",
        )
    )
    fig4.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["음식점주점업_생산지수"],
            mode="lines+markers",
            line=dict(color=BLUE, width=2.8),
            marker=dict(size=7),
            name="음식점·주점업 생산지수",
            hovertemplate="%{x}년: %{y:.1f}<extra></extra>",
        )
    )
    fig4.add_hline(y=100, line_dash="dot", line_color=GRID, annotation_text="2020=100", annotation_font_color=MUTED)
    add_covid_band(fig4)
    fig4.update_layout(**base_layout("쉬었음 청년 상대규모와 음식점·주점업 생산지수", "지수 (2020=100)"))
    chart_start()
    st.plotly_chart(fig4, use_container_width=True)
    chart_end()

    st.markdown(
        """
<div class="connector">
    경제 파트는 금액 환산 대신 상대지표를 사용합니다.<br>
    2020년을 기준으로 쉬었음 청년 규모가 어떻게 움직였는지, 그리고 음식점·주점업 생산 흐름이 어떻게 변했는지를 함께 봅니다.
</div>
""",
        unsafe_allow_html=True,
    )

    fig4b = go.Figure()
    fig4b.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["청년비활동_생활서비스부담지수"],
            mode="lines+markers+text",
            line=dict(color=AMBER, width=2.8),
            marker=dict(size=8),
            text=[f"{v:.1f}" for v in df["청년비활동_생활서비스부담지수"]],
            textposition="top center",
            textfont=dict(size=10, color=TEXT),
            name="청년 비활동-생활서비스 부담지수",
            hovertemplate="%{x}년: %{y:.1f}<extra></extra>",
        )
    )
    fig4b.add_hline(y=100, line_dash="dot", line_color=GRID, annotation_text="2020=100", annotation_font_color=MUTED)
    add_covid_band(fig4b)
    fig4b.update_layout(**base_layout("청년 비활동-생활서비스 부담지수", "지수 (2020=100)"))
    chart_start()
    st.plotly_chart(fig4b, use_container_width=True)
    chart_end()
    st.markdown(
        '<p class="note">※ 수식: (쉬었음 청년 수 ÷ 2020년 쉬었음 청년 수 × 100) ÷ (음식점·주점업 생산지수 ÷ 100). 쉬었음 청년 상대규모가 커질수록, 음식점·주점업 생산지수가 낮을수록 지수가 상승합니다.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="note">※ 음식점·주점업 생산지수는 KOSIS 서비스업동향조사, 산업별 서비스업생산지수, 음식점 및 주점업, 불변지수(2020=100)를 사용했습니다. 이 지표는 직접 인과관계를 의미하지 않고, 청년 비활동 규모와 생활서비스 업종 흐름을 결합한 보조 파생지표입니다.</p>',
        unsafe_allow_html=True,
    )


def page_fiscal() -> None:
    hero()
    section_header(
        "STEP 4",
        "재정 관점 — 20대의 고용보험 편입 규모는 어떻게 변했는가?",
        "재정 파트는 임금·보험료 가정이 필요한 금액 추정을 제외하고, 실제 관측자료인 20대 고용보험 피보험자 수와 2015년 인구 기준 보정 비율을 중심으로 봅니다.",
    )

    latest_insured_10k = float(df["고용보험피보험자_만명"].iloc[-1])
    latest_entry_rate = float(df["고용보험피보험자_비율"].iloc[-1])
    latest_fixed_rate = float(df["고용보험피보험자_2015인구기준비율"].iloc[-1])
    insured_2021 = float(df.loc[df["연도"] == 2021, "고용보험피보험자_만명"].iloc[0])
    insured_change = latest_insured_10k - insured_2021

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025 20대 고용보험 피보험자", f"{latest_insured_10k:.1f}만명", "EIS, 2025년 12월 말 기준", "purple")
    with c2:
        metric_card("2015 인구 기준 피보험자", f"{latest_fixed_rate:.1f}%", f"해당연도 인구 기준은 {latest_entry_rate:.1f}%", "blue")
    with c3:
        metric_card("2021년 대비 피보험자 변화", f"{insured_change:+.1f}만명", f"2021년 {insured_2021:.1f}만명 → 2025년 {latest_insured_10k:.1f}만명", "red")

    st.markdown(
        """
<div class="connector">
    재정 파트의 핵심은 <b>실제 관측자료</b>를 통해 청년의 고용보험 편입 규모를 보는 것입니다.<br>
    해당 연도 인구를 분모로 쓰면 20대 인구 감소 때문에 비율이 좋아 보일 수 있으므로, 보조적으로 2015년 20대 인구를 고정분모로 둔 비율도 함께 봅니다.
</div>
""",
        unsafe_allow_html=True,
    )

    fig_insured = go.Figure()
    fig_insured.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["고용보험피보험자_만명"],
            mode="lines+markers+text",
            line=dict(color=PURPLE, width=2.8),
            marker=dict(size=8),
            text=[f"{v:.0f}" for v in df["고용보험피보험자_만명"]],
            textposition="top center",
            textfont=dict(size=9, color=TEXT),
            name="20대 고용보험 피보험자",
            hovertemplate="%{x}년: %{y:.1f}만명<extra></extra>",
        )
    )
    add_covid_band(fig_insured)
    fig_insured.update_layout(**base_layout("20대 고용보험 피보험자 수 추이", "만명"))
    chart_start()
    st.plotly_chart(fig_insured, use_container_width=True)
    chart_end()
    st.markdown(
        '<p class="note">※ EIS 고용행정통계 월별 피보험자현황 기준. 연령_10세 20~29세, 지역 전체, 각 연도 12월 말 피보험자수(전체)를 사용했습니다. 월별 값을 합산하지 않았습니다.</p>',
        unsafe_allow_html=True,
    )

    fig_fixed = go.Figure()
    fig_fixed.add_trace(
        go.Bar(
            x=df["연도"],
            y=df["고용보험피보험자_2015인구기준비율"],
            marker_color=[PURPLE if y >= 2020 else BLUE for y in df["연도"]],
            name="2015년 인구 기준 피보험자 비율",
            hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
        )
    )
    fig_fixed.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["고용보험피보험자_2015인구기준비율"],
            mode="lines+markers",
            line=dict(color=TEXT, width=2, dash="dot"),
            marker=dict(size=6),
            name="추이",
            hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
        )
    )
    add_covid_band(fig_fixed)
    fig_fixed.update_layout(**base_layout("2015년 인구 기준 고용보험 피보험자 규모", "비율 (%)"))
    chart_start()
    st.plotly_chart(fig_fixed, use_container_width=True)
    chart_end()
    st.markdown(
        '<p class="note">※ 수식: 20대 고용보험 피보험자 수 ÷ 2015년 20~29세 주민등록인구 × 100. 인구 감소 효과를 줄이고 피보험자 규모 변화를 보기 위한 보조지표입니다.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="note">※ 이 값은 실제 가입률이 아니라 고정분모 기준 비교지표입니다. 해당 연도 인구 대비 비율은 별도 참고값이며, 발표에서는 실제 피보험자 수와 이 고정분모 지표를 함께 해석합니다.</p>',
        unsafe_allow_html=True,
    )

def page_policy() -> None:
    hero()
    section_header(
        "STEP 5",
        "정책·결론 — 지원 확대보다 재진입 구조 설계",
        "전체 요약 → 관점별 문제점 → 정책 방향 순으로 정리합니다.",
    )

    latest_insured = float(df["고용보험피보험자_만명"].iloc[-1])
    latest_service_pressure = float(df["청년비활동_생활서비스부담지수"].iloc[-1])
    latest_mismatch = float(df["청년비활동_미충원배수"].iloc[-1])
    latest_entry_rate = float(df["고용보험피보험자_비율"].iloc[-1])
    latest_fixed_rate = float(df["고용보험피보험자_2015인구기준비율"].iloc[-1])

    # ── 1. 전체 요약 ──────────────────────────────────────────
    st.markdown("### 1. 전체 요약")
    st.markdown(
        f"""
<div class="connector">
    <strong>핵심 메시지:</strong> 본 대시보드는 쉬었음 청년 증가가 기업 미충원, 생활서비스 업종 흐름, 사회보험 편입 변화와 어떻게 연결될 수 있는지 데이터로 재구성한 것입니다.<br>
    다만 노동시장·경제·재정 지표는 직접 인과관계를 증명하는 것이 아니라, 원자료를 결합한 <strong>보조 파생지표</strong>로 해석합니다.
</div>
""",
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("2025 쉬었음 청년", f"{int(df['쉬었음_청년'].iloc[-1]):,}천명", "20~29세 단일 기준", "red")
    with s2:
        metric_card("비활동-미충원 배수", f"{latest_mismatch:.2f}배", "미충원 1명당 쉬었음 청년", "blue")
    with s3:
        metric_card("생활서비스 부담지수", f"{latest_service_pressure:.1f}", "2020=100 기준", "amber")
    with s4:
        metric_card("2015 인구 기준 피보험자", f"{latest_fixed_rate:.1f}%", f"실제 피보험자 {latest_insured:.1f}만명", "purple")

    # ── 2. 관점별 문제점 ──────────────────────────────────────
    st.markdown("### 2. 관점별 문제점")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(
            """
<div class="policy-grid-card">
    <div class="policy-kicker">🔧 노동시장 관점</div>
    <div class="policy-title">실무경력 부족과<br>기업 인력 공백의 동시 존재</div>
    <div class="policy-desc">
        쉬었음 청년이 채용시장과 멀어질수록 실제 현장 경험을 쌓기 어렵습니다.
        동시에 기업의 미충원 상황이 존재한다면, 청년의 경력 공백과 기업의 인력 공백이 함께 나타날 수 있습니다.
    </div>
    <ul>
        <li>구직 준비 장기화 → 실무경험 공백 확대</li>
        <li>중소·중견기업 취업에 대한 낮은 신뢰</li>
        <li>기업은 검증된 신입 기술인재 확보에 어려움</li>
        <li>문제 핵심: 첫 경력 진입 경로의 부재</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            f"""
<div class="policy-grid-card">
    <div class="policy-kicker">💰 경제 관점</div>
    <div class="policy-title">청년 비활동과<br>생활서비스 수요 기반</div>
    <div class="policy-desc">
        경제 파트는 금액 환산 대신 쉬었음 청년 상대규모와 음식점·주점업 생산지수를 결합했습니다.
        2025년 청년 비활동-생활서비스 부담지수는 <span class="policy-highlight-amber">{latest_service_pressure:.1f}</span>입니다. (2020=100)
    </div>
    <ul>
        <li>쉬었음 청년 규모와 생활서비스 업종 흐름 결합</li>
        <li>음식점·주점업 생산지수는 보조 관측자료</li>
        <li>직접 인과관계가 아니라 상대 흐름 확인</li>
        <li>문제 핵심: 청년 비활동과 생활서비스 흐름의 동시 관찰</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            f"""
<div class="policy-grid-card">
    <div class="policy-kicker">🏛️ 재정 관점</div>
    <div class="policy-title">사회보험 편입과<br>고용 유지 문제</div>
    <div class="policy-desc">
        재정 파트는 실제 관측자료인 20대 고용보험 피보험자 수를 중심으로 봤습니다.
        2025년 피보험자는 <span class="policy-highlight-purple">{latest_insured:.1f}만명</span>,
        2015년 인구 기준 피보험자 비율은 <span class="policy-highlight-purple">{latest_fixed_rate:.1f}%</span>입니다.
    </div>
    <ul>
        <li>취업 지연 → 사회보험 편입 지연 가능성</li>
        <li>해당 연도 인구 기준 비율은 인구 감소의 영향을 받음</li>
        <li>단순 가입 여부보다 3개월·6개월 유지율 중요</li>
        <li>문제 핵심: 첫 일자리 유지 구조의 부족</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    # ── 3. 정책 방향 ──────────────────────────────────────────
    st.markdown("### 3. 정책 방향")
    st.markdown(
        """
<div class="policy-final-box">
    <h3>우수 중소·중견기업 실무경력 인증 우대전형</h3>
    <p>
        본 분석의 정책 결론은 새로운 현금성 지원을 추가하자는 것이 아닙니다.
        핵심은 <strong>중소·중견기업에서 쌓은 실무경력을 상위 커리어로 인정하는 공식 사다리</strong>를 만드는 것입니다.
        우수 중소·중견기업에서 2~3년간 검증된 실무성과를 쌓은 청년에게 대기업·상위 중견기업·공공 기술직 채용에서
        서류전형 우대 또는 가산점을 부여하는 협약형 우대전형을 제안합니다.
        이는 대기업 채용을 보장하는 프리패스가 아니라, 검증된 실무경력을 채용시장에서 공식적으로 인정하는 구조입니다.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(
            """
<div class="policy-grid-card">
    <div class="policy-kicker">🔧 노동시장 해법</div>
    <div class="policy-title">중소·중견기업 경력을<br>경력 사다리로 전환</div>
    <div class="policy-desc">
        청년에게 “일단 아무 데나 취업하라”고 말하는 방식은 설득력이 약합니다.
        대신 우수 중소·중견기업 근무가 상위 커리어로 이어지는 공식 경로를 제공해야 합니다.
    </div>
    <ul>
        <li>우수 중소·중견기업 지정</li>
        <li>2~3년 실무성과 공동 평가</li>
        <li>실무경력 인증서 발급</li>
        <li>상위기업·공공 기술직 우대전형 연계</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            """
<div class="policy-grid-card">
    <div class="policy-kicker">💰 경제 해법</div>
    <div class="policy-title">첫 소득과 실무경험을<br>동시에 발생</div>
    <div class="policy-desc">
        경제 대책은 단기적 보전보다, 청년이 다시 소득을 만들 수 있는 경로를 회복하는 방향이어야 합니다.
        실무경력 인증 우대전형은 취업 준비 장기화를 줄이고 첫 소득 발생을 앞당깁니다.
    </div>
    <ul>
        <li>교육 이수보다 실제 과업 수행 중심</li>
        <li>첫 월급과 경력 형성 동시 달성</li>
        <li>기업은 채용 전 직무 적합성 확인</li>
        <li>경제활동 재진입 경로 회복</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )
    with a3:
        st.markdown(
            """
<div class="policy-grid-card">
    <div class="policy-kicker">🏛️ 재정 해법</div>
    <div class="policy-title">취업 여부보다<br>첫 일자리 유지율 관리</div>
    <div class="policy-desc">
        취업하면 고용보험 가입은 대체로 따라옵니다. 그래서 정책 성과는 단순 가입 여부가 아니라
        피보험 상태가 3개월·6개월 이상 유지되는지로 판단해야 합니다.
    </div>
    <ul>
        <li>기존: 참여자 수·수료자 수 중심</li>
        <li>변경: 고용보험 유지율 중심</li>
        <li>3개월·6개월 피보험 유지율 추적</li>
        <li>재이탈률까지 성과관리 지표화</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    # ── 4. 실행 구조 ──────────────────────────────────────────
    st.markdown("### 4. 실행 구조")
    e1, e2, e3, e4 = st.columns(4)
    steps = [
        ("STEP 1", "기업 선정", "고용노동부·중소벤처기업부·산업별 협회가 기술력·근로조건·교육역량을 기준으로 우수 중소·중견기업을 지정합니다."),
        ("STEP 2", "실무 수행", "청년은 지정 기업에서 실제 직무 과업을 수행하며 2~3년간 검증 가능한 실무경력을 쌓습니다."),
        ("STEP 3", "경력 인증", "기업·산업단체·정부가 직무성과를 공동 평가해 공식 실무경력 인증서를 발급합니다."),
        ("STEP 4", "우대 연계", "인증 경력을 대기업·상위 중견기업·공공 기술직 채용의 서류 우대 또는 가산점 요소로 활용합니다."),
    ]
    for col, (no, title, desc) in zip([e1, e2, e3, e4], steps):
        with col:
            st.markdown(
                f"""
<div class="policy-step">
    <div class="step-no">{no}</div>
    <div class="step-title">{title}</div>
    <div class="step-desc">{desc}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    # ── 5. 데이터 출처 ──────────────────────────────────────────
    st.markdown("### 5. 데이터 출처")
    st.markdown(
        """
<div class="policy-final-box">
    <h3>데이터 출처·필터 조건</h3>
    <p>
        <strong>분석 범위</strong>: 20~29세 단일 구간, 2015~2025년<br>
        <strong>쉬었음 청년 수·전체 비경제활동인구</strong>: KOSIS 경제활동인구조사, 연도별, 단위 천명<br>
        <strong>20~29세 취업자 수</strong>: KOSIS 경제활동인구조사, 연령별 경제활동인구 총괄, 연도별, 단위 천명<br>
        <strong>20~29세 주민등록인구</strong>: KOSIS 주민등록인구통계, 1세별 20~29세 합산, 단위 천명<br>
        <strong>미충원인원</strong>: 고용노동통계 직종별사업체노동력조사, 전국·전산업·5인 이상, 각 연도 하반기(2/2), 단위 명<br>
        <strong>음식점 및 주점업 서비스업생산지수</strong>: KOSIS 서비스업동향조사, 음식점 및 주점업, 불변지수, 2020=100<br>
        <strong>20대 고용보험 피보험자 수</strong>: EIS 고용행정통계 월별 피보험자현황, 연령 20~29세, 각 연도 12월 말 기준, 단위 명<br>
        <strong>2015년 인구 기준 피보험자 비율</strong>: 20대 고용보험 피보험자 수 ÷ 2015년 20~29세 주민등록인구 × 100
    </p>
</div>

<div class="connector">
    <strong>해석 주의:</strong> 청년 비활동-미충원 배수는 쉬었음 청년이 곧바로 미충원 일자리를 채운다는 뜻이 아닙니다.
    생활서비스 부담지수도 음식점·주점업 흐름과 청년 비활동 규모를 결합한 보조 파생지표이며, 직접 인과관계를 의미하지 않습니다.
</div>
""",
        unsafe_allow_html=True,
    )


def page_data_limit() -> None:
    hero()
    section_header("DATA", "데이터·수식·분석 한계", "사용한 자료, 계산 방식, 발표 때 방어해야 할 한계를 한 화면에 정리했습니다.")

    st.markdown("### 사용 데이터 미리보기")
    display_df = df.copy()
    display_df["연도"] = display_df["연도"].astype(int)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("### 파생지표 수식")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
<div class="metric-card">
    <div class="label">경제 관점</div>
    <div class="sub">청년 비활동-생활서비스 부담지수</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">(쉬었음 청년 수 ÷ 2020년 쉬었음 청년 수 × 100) ÷ (음식점·주점업 생산지수 ÷ 100)</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="metric-card">
    <div class="label">재정 관점</div>
    <div class="sub">2015년 인구 기준 피보험자 비율</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">20대 고용보험 피보험자 수 ÷ 2015년 20~29세 인구 × 100</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
<div class="metric-card">
    <div class="label">노동시장 관점</div>
    <div class="sub">청년 비활동-미충원 배수</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">쉬었음 청년 수(천명) × 1000 ÷ 미충원인원(명)</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with st.expander("📋 분석 한계 및 주의사항", expanded=True):
        st.markdown(
            """
**[한계 1] 경제 지표는 상대 파생지표**
- 청년 비활동-생활서비스 부담지수는 쉬었음 청년 상대규모와 음식점·주점업 생산지수를 결합한 보조지표입니다.
- 음식점·주점업 생산지수는 청년 소비만을 직접 측정한 자료가 아니므로 직접 인과관계로 해석하면 안 됩니다.

**[한계 2] 재정 지표는 고용보험 중심**
- 재정 파트는 실제 관측 가능한 20대 고용보험 피보험자 수와 2015년 인구 기준 보정 비율을 사용했습니다.
- 해당 연도 인구 대비 비율은 20대 인구 감소의 영향을 받기 때문에, 발표에서는 실제 피보험자 수와 고정분모 보조지표를 함께 해석합니다.

**[한계 3] 확산 구조는 인과관계가 아닌 가능성**
- 노동시장 → 경제 → 재정 흐름은 직접 인과관계 검증이 아니라 구조적 확산 가능성을 보여주는 분석입니다.

**출처**
- 쉬었음 청년 수, 비경제활동인구: KOSIS 경제활동인구조사
- 20~29세 인구: KOSIS 주민등록인구통계, 1세별 주민등록인구 합산
- 20대 고용보험 피보험자: EIS 고용행정통계 월별 피보험자현황, 연령_10세 20~29세, 각 연도 12월 말 기준
- 음식점 및 주점업 서비스업생산지수: KOSIS 서비스업동향조사, 산업별 서비스업생산지수, 불변지수(2020=100)
"""
        )

# ─────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────
if page == "🏠 개요":
    page_overview()
elif page == "① 문제 규모":
    page_scale()
elif page == "② 노동시장":
    page_labor()
elif page == "③ 경제":
    page_economy()
elif page == "④ 재정":
    page_fiscal()
elif page == "⑤ 정책·결론":
    page_policy()

