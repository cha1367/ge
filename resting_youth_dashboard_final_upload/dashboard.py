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

AVG_INCOME = 271      # 만원, 20대 평균소득 가정값
CONSUMPTION = 0.69    # 평균소비성향 가정값
PENSION_RATE = 0.09   # 국민연금 보험료율

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
    data["고용보험피보험자_증가율"] = (data["고용보험피보험자_명"].pct_change() * 100).round(1)

    data["쉬었음_비율"] = (data["쉬었음_청년"] / data["전체_비경활"] * 100).round(1)
    data["쉬었음_증가율"] = (data["쉬었음_청년"].pct_change() * 100).round(1)
    data["비경활_증가율"] = (data["전체_비경활"].pct_change() * 100).round(1)
    data["인구_증가율"] = (data["청년_인구"].pct_change() * 100).round(1)
    data["소비공백_억원"] = (
        data["쉬었음_청년"] * 1000 * AVG_INCOME * 10000 * CONSUMPTION / 1e8
    ).round(0).astype(int)
    data["연금공백_억원"] = (
        data["쉬었음_청년"] * 1000 * AVG_INCOME * 10000 * 12 * PENSION_RATE / 1e8
    ).round(0).astype(int)
    # 이전 코드 호환용 컬럼. 화면에서는 '손실' 대신 '공백'을 사용한다.
    data["연금손실_억원"] = data["연금공백_억원"]
    data["내수공백률"] = (data["쉬었음_청년"] / data["청년_인구"] * 100).round(2)
    data["누적_연금공백"] = data["연금공백_억원"].cumsum()
    data["누적_연금손실"] = data["누적_연금공백"]
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
        20~29세 쉬었음 청년 증가가 <strong>노동시장 이탈 → 소비 공백 → 재정 기반 약화</strong>로
        어떻게 확산될 수 있는지 단계별 파생지표로 보여줍니다.
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
        20대 인구 대비: <b style="color:#f59e0b;">{latest_value('내수공백률'):.2f}%</b><br>
        소비 공백: <b style="color:#60a5fa;">{int(latest_value('소비공백_억원')):,}억원</b><br>
        고용보험 피보험자: <b style="color:#a78bfa;">{latest_value('고용보험피보험자_만명'):.1f}만명</b>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.caption("자료: KOSIS 경제활동인구조사·주민등록인구통계, EIS 고용행정통계 / 단위: 천명·억원·만명")

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
        metric_card("2025 소비 공백", f"{int(latest_value('소비공백_억원')):,}억원", f"약 {latest_value('소비공백_억원')/10000:.2f}조원", "amber")
    with c4:
        metric_card("20대 고용보험 피보험자", f"{latest_value('고용보험피보험자_만명'):.1f}만명", "2025년 12월 말 기준", "purple")

    section_header("FLOW", "분석 흐름", "이 대시보드는 한 화면에 모든 차트를 몰아넣지 않고, 왼쪽 사이드바에서 단계별로 넘겨보는 구조입니다.")
    f1, f2, f3, f4, f5 = st.columns(5)
    flow_items = [
        ("STEP 1", "문제 규모", "쉬었음 청년 수와 20대 인구 흐름 확인"),
        ("STEP 2", "노동시장", "쉬었음 증가율과 비경활 내 비중 비교"),
        ("STEP 3", "경제", "소득·소비 가정으로 잠재 소비 공백 추정"),
        ("STEP 4", "재정", "고용보험 피보험자와 사회보험 진입률 확인"),
        ("STEP 5", "정책", "조기개입·소비·사회보험 관점의 대책 정리"),
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

    st.markdown('<div class="connector">핵심 논리: 쉬었음 청년의 증가는 단순한 개인 상태가 아니라 노동시장 밖에 머무는 기간이 길어질수록 소비와 사회보험 납부 기반까지 약화시키는 구조로 해석할 수 있습니다.</div>', unsafe_allow_html=True)

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
            y=df["내수공백률"],
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
    section_header("STEP 2", "노동시장 관점 — 청년 이탈이 가속되고 있는가?", "쉬었음 청년 증가율을 전체 비경제활동인구 증가율과 비교하고, 비경활 내부에서 쉬었음이 차지하는 비중을 확인합니다.")

    latest_rate = df["쉬었음_비율"].iloc[-1]
    rate_change = df["쉬었음_비율"].iloc[-1] - df["쉬었음_비율"].iloc[0]
    latest_growth = df["쉬었음_증가율"].iloc[-1]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025 비경활 중 쉬었음 비율", f"{latest_rate:.1f}%", "쉬었음 청년 ÷ 전체 비경활", "red")
    with c2:
        metric_card("2015년 대비 비중 변화", f"+{rate_change:.1f}%p", f"{df['쉬었음_비율'].iloc[0]:.1f}% → {latest_rate:.1f}%", "blue")
    with c3:
        metric_card("2025 전년 대비 증가율", f"{latest_growth:.1f}%", "쉬었음 청년 수 기준", "amber")

    tab1, tab2 = st.tabs(["📈 증가율 비교", "📊 비경활 중 쉬었음 비율"])

    with tab1:
        df_rate = df.dropna(subset=["쉬었음_증가율", "비경활_증가율"])
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=df_rate["연도"],
                y=df_rate["쉬었음_증가율"],
                mode="lines+markers",
                name="쉬었음 청년 증가율",
                line=dict(color=RED, width=2.8),
                marker=dict(size=7),
                hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=df_rate["연도"],
                y=df_rate["비경활_증가율"],
                mode="lines+markers",
                name="전체 비경활 증가율",
                line=dict(color=BLUE, width=2.8, dash="dash"),
                marker=dict(size=7),
                hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
            )
        )
        fig2.add_hline(y=0, line_dash="dot", line_color=GRID)
        add_covid_band(fig2)
        fig2.update_layout(**base_layout("쉬었음 청년 vs 전체 비경제활동인구 증가율", "전년 대비 증가율 (%)"))
        chart_start()
        st.plotly_chart(fig2, use_container_width=True)
        chart_end()
        st.markdown('<p class="note">※ 전년 대비 증가율 기준. 2015년은 전년 자료가 없어 증가율 계산에서 제외됩니다.</p>', unsafe_allow_html=True)

    with tab2:
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
                name="쉬었음 비율",
                hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
            )
        )
        add_covid_band(fig3)
        fig3.update_layout(**base_layout("비경제활동인구 중 '쉬었음' 비율", "비율 (%)"))
        chart_start()
        st.plotly_chart(fig3, use_container_width=True)
        chart_end()
        st.markdown('<p class="note">※ 수식: 쉬었음 청년 수 ÷ 전체 비경제활동인구(20~29세) × 100</p>', unsafe_allow_html=True)


def page_economy() -> None:
    hero()
    section_header("STEP 3", "경제 관점 — 내수 기반이 약화되고 있는가?", "쉬었음 청년이 벌고 쓸 수 있었던 잠재 소비액을 단순 가정으로 추정합니다.")

    latest_consumption = int(df["소비공백_억원"].iloc[-1])
    latest_gap_rate = df["내수공백률"].iloc[-1]
    per_person_consumption = AVG_INCOME * CONSUMPTION

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025 청년 소비 공백", f"{latest_consumption:,}억원", f"약 {latest_consumption/10000:.2f}조원", "red")
    with c2:
        metric_card("1인당 잠재 소비", f"{per_person_consumption:.0f}만원", "271만원 × 0.69", "blue")
    with c3:
        metric_card("20대 인구 대비 쉬었음", f"{latest_gap_rate:.2f}%", "내수 기여 공백률", "amber")

    fig4 = go.Figure()
    fig4.add_trace(
        go.Bar(
            x=df["연도"],
            y=df["소비공백_억원"],
            marker_color=[RED if year >= 2020 else "#4a6fa5" for year in df["연도"]],
            name="소비 공백 추정액",
            hovertemplate="%{x}년: %{y:,}억원<extra></extra>",
        )
    )
    add_covid_band(fig4)
    fig4.update_layout(**base_layout("청년 소비 공백 추정액", "억원"))
    chart_start()
    st.plotly_chart(fig4, use_container_width=True)
    chart_end()

    st.markdown(
        f"""
<div class="connector">
    계산식: 쉬었음 청년 수 × {AVG_INCOME}만원 × {CONSUMPTION}<br>
    이 값은 실제 소비 감소액이 아니라, 쉬었음 상태가 아니었다면 발생할 수 있었던 <b>잠재 소비 미실현 규모</b>입니다.
</div>
""",
        unsafe_allow_html=True,
    )

    fig4b = go.Figure()
    fig4b.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["내수공백률"],
            mode="lines+markers+text",
            line=dict(color=AMBER, width=2.8),
            marker=dict(size=8),
            text=[f"{v:.2f}%" for v in df["내수공백률"]],
            textposition="top center",
            textfont=dict(size=10, color=TEXT),
            name="청년 내수 기여 공백률",
            hovertemplate="%{x}년: %{y:.2f}%<extra></extra>",
        )
    )
    add_covid_band(fig4b)
    fig4b.update_layout(**base_layout("청년 내수 기여 공백률", "비율 (%)"))
    chart_start()
    st.plotly_chart(fig4b, use_container_width=True)
    chart_end()
    st.markdown('<p class="note">※ 수식: 쉬었음 청년 수 ÷ 20~29세 전체 인구 × 100</p>', unsafe_allow_html=True)


def page_fiscal() -> None:
    hero()
    section_header(
        "STEP 4",
        "재정 관점 — 청년은 사회보험 체계에 얼마나 진입하고 있는가?",
        "기존 국민연금 공백 추정치만 보여주면 쉬었음 청년 수와 차트 모양이 거의 같아집니다. 따라서 재정 파트에는 실제 관측자료인 20대 고용보험 피보험자 수를 함께 제시합니다.",
    )

    latest_insured_10k = float(df["고용보험피보험자_만명"].iloc[-1])
    latest_entry_rate = float(df["고용보험피보험자_비율"].iloc[-1])
    latest_pension_gap = int(df["연금공백_억원"].iloc[-1])
    cumulative_gap = int(df["누적_연금공백"].iloc[-1])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("2025 20대 고용보험 피보험자", f"{latest_insured_10k:.1f}만명", "EIS, 2025년 12월 말 기준", "purple")
    with c2:
        metric_card("고용보험 기준 사회보험 진입률", f"{latest_entry_rate:.1f}%", "20대 인구 대비 피보험자 비율", "blue")
    with c3:
        metric_card("잠재 국민연금 납부 공백", f"{latest_pension_gap:,}억원", "연간 추정치, 실제 세입 아님", "red")

    st.markdown(
        """
<div class="connector">
    재정 파트의 핵심은 <b>추정치와 관측자료를 분리</b>하는 것입니다.<br>
    고용보험 피보험자 수는 실제 관측자료이고, 국민연금 납부 공백은 평균소득과 보험료율을 적용한 잠재 추정치입니다.
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

    fig_entry = go.Figure()
    fig_entry.add_trace(
        go.Bar(
            x=df["연도"],
            y=df["고용보험피보험자_비율"],
            marker_color=[PURPLE if y >= 2020 else BLUE for y in df["연도"]],
            name="고용보험 기준 사회보험 진입률",
            hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
        )
    )
    fig_entry.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["고용보험피보험자_비율"],
            mode="lines+markers",
            line=dict(color=TEXT, width=2, dash="dot"),
            marker=dict(size=6),
            name="추이",
            hovertemplate="%{x}년: %{y:.1f}%<extra></extra>",
        )
    )
    add_covid_band(fig_entry)
    fig_entry.update_layout(**base_layout("20대 인구 대비 고용보험 피보험자 비율", "비율 (%)"))
    chart_start()
    st.plotly_chart(fig_entry, use_container_width=True)
    chart_end()
    st.markdown(
        '<p class="note">※ 수식: 20대 고용보험 피보험자 수 ÷ 20~29세 주민등록인구 × 100. 전체 사회보험 가입률이 아니라 고용보험 기준의 노동시장·사회보험 진입 보조지표입니다.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("보조 추정지표: 잠재 국민연금 납부 공백")

    fig_gap = go.Figure()
    fig_gap.add_trace(
        go.Scatter(
            x=df["연도"],
            y=df["연금공백_억원"],
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(255,75,75,0.14)",
            line=dict(color=RED, width=2.6),
            marker=dict(size=7),
            name="잠재 국민연금 납부 공백",
            hovertemplate="%{x}년: %{y:,}억원<extra></extra>",
        )
    )
    add_covid_band(fig_gap)
    fig_gap.update_layout(**base_layout("잠재 국민연금 납부 공백 추정액", "억원"))
    chart_start()
    st.plotly_chart(fig_gap, use_container_width=True)
    chart_end()

    st.markdown(
        f"""
<div class="connector">
    계산식: 쉬었음 청년 수 × {AVG_INCOME}만원 × 12개월 × {PENSION_RATE:.0%}<br>
    이 값은 실제 국민연금 미납액이나 재정 손실액이 아니라, 쉬었음 청년이 노동시장에 진입해 가입 대상이 되었을 경우 발생할 수 있었던 <b>연간 잠재 납부 공백 추정치</b>입니다.<br>
    2015~2025년 누적 잠재 공백 추정액은 <b style="color:#ff4b4b;">{cumulative_gap:,}억원</b>입니다.
</div>
""",
        unsafe_allow_html=True,
    )


def page_policy() -> None:
    hero()
    section_header(
        "STEP 5",
        "정책·결론 — 지원 확대보다 재진입 구조 설계",
        "전체 요약 → 관점별 문제점 → 우수 중소·중견기업 실무경력 인증 우대전형으로 정리합니다.",
    )

    latest_consumption = int(df["소비공백_억원"].iloc[-1])
    latest_pension = int(df["연금공백_억원"].iloc[-1])
    latest_insured = float(df["고용보험피보험자_만명"].iloc[-1])
    latest_gap_rate = float(df["내수공백률"].iloc[-1])

    # ── 1. 전체 요약 ──────────────────────────────────────────
    st.markdown("### 1. 전체 요약")
    st.markdown(
        f"""
<div class="connector">
    본 대시보드는 20~29세 쉬었음 청년 증가를 <strong>노동시장 → 경제 → 재정</strong> 흐름으로 재구성했습니다.
    분석의 핵심은 쉬었음 청년을 단순히 개인의 휴식 상태로 보는 것이 아니라,
    <strong>실무경력 지연 → 첫 소득 부재 → 사회보험 편입 지연</strong>으로 이어질 수 있는 구조로 보는 것입니다.
    소비 공백과 국민연금 납부 공백은 실제 손실액이 아니라 잠재 추정치이므로,
    정책은 특정 금액을 보전하는 방식보다 공백이 발생하는 경로를 줄이는 방향이어야 합니다.
</div>
""",
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        metric_card("2025 쉬었음 청년", f"{int(df['쉬었음_청년'].iloc[-1]):,}천명", "노동시장 밖에 머무는 20대 규모", "red")
    with s2:
        metric_card("2025 소비 공백", f"{latest_consumption:,}억원", "잠재 소비 여력 추정치", "amber")
    with s3:
        metric_card("20대 고용보험 피보험자", f"{latest_insured:.1f}만명", "2025년 12월 말 실제 관측값", "purple")

    # ── 2. 관점별 문제점 ──────────────────────────────────────
    st.markdown("### 2. 관점별 문제점")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(
            """
<div class="policy-grid-card">
    <div class="policy-kicker">🔧 노동시장 관점</div>
    <div class="policy-title">실무경력 부족과<br>대기업 준비 장기화</div>
    <div class="policy-desc">
        쉬었음 청년이 노동시장 밖에 오래 머물수록 실제 현장 경험을 쌓기 어렵습니다.
        특히 대기업·공공기관 준비가 길어지는 동안 실무경력은 누적되지 않고,
        중소·중견기업 취업은 경력 정체로 인식되는 문제가 있습니다.
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
    <div class="policy-title">첫 소득 부재와<br>소비 여력 약화</div>
    <div class="policy-desc">
        쉬었음 청년이 늘어나면 노동소득이 발생하지 않는 청년이 늘고,
        이는 잠재 소비 여력 약화로 이어질 수 있습니다.
        2025년 잠재 소비 공백은 <span class="policy-highlight-amber">{latest_consumption:,}억원</span>으로 추정됩니다.
    </div>
    <ul>
        <li>소득 부재 → 소비 여력 약화</li>
        <li>20대 인구 대비 쉬었음 비율: {latest_gap_rate:.2f}%</li>
        <li>단순 소비지원보다 첫 소득 창출 경로가 중요</li>
        <li>문제 핵심: 소득 발생 전 단계의 장기화</li>
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
    <div class="policy-title">사회보험 편입 지연과<br>고용 유지 문제</div>
    <div class="policy-desc">
        일반적인 취업은 대부분 고용보험 가입으로 이어집니다.
        따라서 중요한 것은 가입 자체보다 <strong>고용보험 피보험 상태가 얼마나 유지되는지</strong>입니다.
        국민연금 납부 공백 <span class="policy-highlight-purple">{latest_pension:,}억원</span>은 잠재 추정치입니다.
    </div>
    <ul>
        <li>취업 지연 → 사회보험 편입 지연</li>
        <li>단순 취업자 수보다 3개월·6개월 유지율 중요</li>
        <li>추정 손실 보전보다 재진입 경로 관리 필요</li>
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
        경제 대책은 소비를 직접 보전하는 것이 아니라, 청년이 다시 소득을 만들 수 있는 경로를 회복하는 방향이어야 합니다.
        실무경력 인증 우대전형은 취업 준비 장기화를 줄이고 첫 소득 발생을 앞당깁니다.
    </div>
    <ul>
        <li>교육 이수보다 실제 과업 수행 중심</li>
        <li>첫 월급과 경력 형성 동시 달성</li>
        <li>기업은 채용 전 직무 적합성 확인</li>
        <li>소득 창출 → 소비 여력 회복</li>
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
        ("STEP 1", "기업 선정", "기술력·근로조건·교육역량을 기준으로 우수 중소·중견기업을 지정합니다."),
        ("STEP 2", "실무 수행", "청년은 지정 기업에서 실제 직무 과업을 수행하며 2~3년간 실무경력을 쌓습니다."),
        ("STEP 3", "경력 인증", "기업·산업단체·정부가 실무성과를 평가해 공식 실무경력으로 인증합니다."),
        ("STEP 4", "우대 연계", "인증 경력을 대기업·상위 중견기업·공공 기술직 채용 우대 요소로 활용합니다."),
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

    # ── 5. 최종 결론 ──────────────────────────────────────────
    st.markdown(
        """
<div class="policy-final-box">
    <h3>최종 결론</h3>
    <p>
        쉬었음 청년 문제의 핵심은 청년 개인의 의지 부족이 아니라,
        노동시장 밖에 머무는 시간이 길어질수록 <strong>실무경력·소득·사회보험 편입이 함께 지연되는 구조</strong>에 있습니다.
        따라서 정책은 지원금을 더 주는 방식보다, 청년이 실제 일자리로 진입하고 유지될 수 있는 경력 사다리를 설계하는 방향이어야 합니다.
        우수 중소·중견기업 실무경력 인증 우대전형은 청년에게는 첫 경력과 상위 커리어 경로를 제공하고,
        기업에는 검증된 기술 인재를 확보하게 하며, 국가는 고용보험과 국민연금 기반을 보완할 수 있는 통합 대책입니다.
    </p>
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
            f"""
<div class="metric-card">
    <div class="label">경제 관점</div>
    <div class="sub">청년 소비 공백 추정액</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">쉬었음 청년 수 × {AVG_INCOME}만원 × {CONSUMPTION}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
<div class="metric-card">
    <div class="label">재정 관점</div>
    <div class="sub">잠재 국민연금 납부 공백</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">쉬었음 청년 수 × {AVG_INCOME}만원 × 12개월 × {PENSION_RATE:.0%}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
<div class="metric-card">
    <div class="label">보조지표</div>
    <div class="sub">고용보험 기준 사회보험 진입률</div>
    <div style="color:#ffffff; line-height:1.7; margin-top:0.6rem;">20대 고용보험 피보험자 수 ÷ 20~29세 전체 인구 × 100</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with st.expander("📋 분석 한계 및 주의사항", expanded=True):
        st.markdown(
            """
**[한계 1] 경제·재정 지표는 추정치**
- 청년 소비 공백 추정액과 잠재 국민연금 납부 공백은 실측값이 아니라 가정 기반 추정치입니다.
- 실제 손실액이 아니라 잠재 공백 규모의 근사치로 해석해야 합니다.

**[한계 2] 고정값 사용**
- 평균소득 271만원, 평균소비성향 0.69, 국민연금 보험료율 9%를 전 기간에 동일 적용했습니다.
- 소비 공백과 국민연금 공백은 쉬었음 청년 수를 금액으로 환산한 추정지표입니다.
- 재정 파트에는 이를 보완하기 위해 EIS 고용보험 피보험자 수라는 실제 관측자료를 함께 사용했습니다.

**[한계 3] 확산 구조는 인과관계가 아닌 가능성**
- 노동시장 → 경제 → 재정 흐름은 직접 인과관계 검증이 아니라 구조적 확산 가능성을 보여주는 분석입니다.

**출처**
- 쉬었음 청년 수, 비경제활동인구: KOSIS 경제활동인구조사
- 20~29세 인구: KOSIS 주민등록인구통계, 1세별 주민등록인구 합산
- 20대 고용보험 피보험자: EIS 고용행정통계 월별 피보험자현황, 연령_10세 20~29세, 각 연도 12월 말 기준
- 평균소득, 소비성향, 국민연금 보험료율: 분석용 고정 가정값
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
