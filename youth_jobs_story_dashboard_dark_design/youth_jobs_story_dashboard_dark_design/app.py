from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="청년 취업 흐름 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data" / "processed"

# -----------------------------------------------------------------------------
# Design: dark premium analytics dashboard
# -----------------------------------------------------------------------------
# 색상 팔레트
INDIGO   = "#6366F1"
TEAL     = "#10B981"
AMBER    = "#F59E0B"
ROSE     = "#F43F5E"
SKY      = "#38BDF8"
VIOLET   = "#A78BFA"
LIME     = "#84CC16"
SLATE    = "#94A3B8"

BLUE     = INDIGO
GREEN    = TEAL
ORANGE   = AMBER
RED      = ROSE
NAVY     = "#0F172A"
PURPLE   = VIOLET
YELLOW   = LIME
GRAY     = SLATE

COLORWAY = [INDIGO, TEAL, AMBER, ROSE, SKY, VIOLET, LIME, SLATE]

# 다크 차트 테마
CHART_BG    = "#0A1020"
CHART_PAPER = "#0A1020"
GRID_COLOR  = "rgba(99,102,241,.1)"
FONT_COLOR  = "#94A3B8"
TITLE_COLOR = "#E2E8F0"

TEMPLATE = "plotly_dark"
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');

/* ── 기본 리셋 ── */
html, body, [class*="css"] {
    font-family: 'Pretendard', 'Noto Sans KR', system-ui, sans-serif;
}
.stApp {
    background: #080E1C;
    color: #E2E8F0;
}
.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1300px;
}

/* ── 사이드바 ── */
section[data-testid="stSidebar"] {
    background: #050A14;
    border-right: 1px solid rgba(99,132,255,.15);
}
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(99,132,255,.08);
    border: 1px solid rgba(99,132,255,.15);
    border-radius: 10px;
    padding: 7px 10px;
    margin-bottom: 5px;
    transition: background .18s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(99,132,255,.18);
}
.sidebar-source {
    background: rgba(99,132,255,.07);
    border: 1px solid rgba(99,132,255,.18);
    border-radius: 14px;
    padding: 14px;
    margin-top: 12px;
}
.sidebar-source .source-title {
    font-size: .76rem; font-weight: 700;
    color: #818CF8 !important;
    letter-spacing: .06em; text-transform: uppercase;
    margin-bottom: 8px;
}
.sidebar-source .source-line { font-size: .85rem; line-height: 1.7; color: #94A3B8 !important; }
.sidebar-note { font-size: .75rem; color: #64748B !important; margin-top: 10px; line-height: 1.6; }

/* ── 히어로 ── */
.hero {
    background:
        radial-gradient(ellipse at 0% 0%, rgba(99,102,241,.28) 0%, transparent 55%),
        radial-gradient(ellipse at 100% 100%, rgba(16,185,129,.16) 0%, transparent 50%),
        linear-gradient(160deg, #0D1528 0%, #0A1020 60%, #080E1C 100%);
    border: 1px solid rgba(99,102,241,.22);
    border-radius: 24px;
    padding: 38px 42px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -1px; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #6366F1, #10B981, transparent);
}
.hero .eyebrow {
    font-size: .78rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase;
    color: #818CF8; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}
.hero .eyebrow::before {
    content: '';
    display: inline-block; width: 22px; height: 2px;
    background: #6366F1; border-radius: 2px;
}
.hero h1 {
    font-size: 2.4rem; line-height: 1.15;
    margin: 0 0 14px; letter-spacing: -0.04em;
    font-weight: 800; color: #F1F5F9;
}
.hero h1 span { color: #818CF8; }
.hero p {
    font-size: 1rem; color: rgba(226,232,240,.72);
    line-height: 1.78; margin: 0; max-width: 860px;
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 1.22rem; font-weight: 800;
    letter-spacing: -0.02em; color: #F1F5F9;
    margin: 28px 0 6px;
    padding-left: 14px;
    border-left: 3px solid #6366F1;
}
.section-sub { font-size: .92rem; color: #64748B; line-height: 1.65; margin-bottom: 14px; padding-left: 17px; }

/* ── KPI 카드 ── */
.kpi {
    background: linear-gradient(145deg, #0E1629, #0A1020);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 18px;
    padding: 20px 20px 18px;
    min-height: 120px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s, box-shadow .2s;
}
.kpi::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.5), transparent);
}
.kpi:hover {
    border-color: rgba(99,102,241,.45);
    box-shadow: 0 0 28px rgba(99,102,241,.12);
}
.kpi .label {
    font-size: .76rem; color: #64748B;
    font-weight: 700; letter-spacing: .05em;
    text-transform: uppercase; margin-bottom: 10px;
}
.kpi .value {
    font-family: 'DM Mono', 'Pretendard', monospace;
    font-size: 2rem; font-weight: 500;
    letter-spacing: -0.03em; color: #E2E8F0;
    text-shadow: 0 0 24px rgba(99,102,241,.35);
}
.kpi .note { font-size: .78rem; color: #475569; margin-top: 8px; line-height: 1.5; }

/* ── 일반 카드 ── */
.card {
    background: #0E1629;
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 20px; padding: 20px 22px;
    margin-bottom: 16px;
}

/* ── 스토리 카드 ── */
.story-card {
    background: linear-gradient(145deg, #0E1629, #0A1020);
    border: 1px solid rgba(99,102,241,.16);
    border-radius: 18px; padding: 20px;
    height: 100%;
    transition: border-color .2s;
}
.story-card:hover { border-color: rgba(99,102,241,.35); }
.story-card .num {
    display: inline-flex; width: 28px; height: 28px;
    align-items: center; justify-content: center;
    border-radius: 8px;
    background: rgba(99,102,241,.18);
    color: #818CF8; font-weight: 800;
    font-size: .85rem; margin-bottom: 12px;
    border: 1px solid rgba(99,102,241,.25);
}
.story-card h4 { margin: 0 0 8px; font-size: .98rem; color: #E2E8F0; font-weight: 700; }
.story-card p { margin: 0; font-size: .87rem; line-height: 1.65; color: #64748B; }

/* ── 알림 박스 ── */
.callout {
    background: rgba(99,102,241,.08);
    color: #A5B4FC;
    border: 1px solid rgba(99,102,241,.22);
    border-left: 4px solid #6366F1;
    padding: 14px 16px; border-radius: 12px;
    line-height: 1.7; margin: 12px 0 18px;
    font-size: .92rem;
}
.caution {
    background: rgba(249,115,22,.07);
    color: #FDBA74;
    border: 1px solid rgba(249,115,22,.2);
    border-left: 4px solid #F97316;
    padding: 14px 16px; border-radius: 12px;
    line-height: 1.7; margin: 12px 0 18px;
    font-size: .92rem;
}
.good {
    background: rgba(16,185,129,.07);
    color: #6EE7B7;
    border: 1px solid rgba(16,185,129,.2);
    border-left: 4px solid #10B981;
    padding: 14px 16px; border-radius: 12px;
    line-height: 1.7; margin: 12px 0 18px;
    font-size: .92rem;
}

/* ── 배지 ── */
.badge {
    display: inline-block;
    background: rgba(99,102,241,.15);
    color: #818CF8;
    border: 1px solid rgba(99,102,241,.25);
    border-radius: 999px;
    padding: 4px 10px;
    font-weight: 700; font-size: .75rem;
    margin: 3px 4px 3px 0;
}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
[data-testid="stDataFrame"] table {
    background: #0E1629 !important;
    color: #CBD5E1 !important;
}

/* ── 셀렉트박스 ── */
[data-testid="stSelectbox"] > div > div {
    background: #0E1629 !important;
    border: 1px solid rgba(99,102,241,.25) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080E1C; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,.3); border-radius: 3px; }

h1, h2, h3 { letter-spacing: -0.025em; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    return {
        "employment": pd.read_csv(DATA_DIR / "employment.csv"),
        "first_job": pd.read_csv(DATA_DIR / "first_job.csv"),
        "exam": pd.read_csv(DATA_DIR / "exam_prep.csv"),
        "resting": pd.read_csv(DATA_DIR / "resting.csv"),
        "nonregular": pd.read_csv(DATA_DIR / "nonregular.csv"),
        "wage": pd.read_csv(DATA_DIR / "wage.csv"),
        "industry": pd.read_csv(DATA_DIR / "industry.csv"),
        "region": pd.read_csv(DATA_DIR / "region.csv"),
    }

data = load_data()
emp = data["employment"]
first = data["first_job"]
exam = data["exam"]
rest = data["resting"]
nr = data["nonregular"]
wage = data["wage"]
industry = data["industry"]
region = data["region"]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
# 색상 변수는 상단에서 정의됨

COLUMN_LABELS = {
    "year": "연도",
    "labor_force_participation_rate": "경제활동참가율(%)",
    "employment_rate": "고용률(%)",
    "inactive_thousand": "비경제활동인구(천 명)",
    "unemployment_rate": "실업률(%)",
    "unemployed_thousand": "실업자 수(천 명)",
    "employed_thousand": "취업자 수(천 명)",
    "youth_population_proxy_thousand": "청년 인구 추정치(천 명)",
    "avg_first_job_months": "첫 취업 평균소요기간(개월)",
    "first_job_over_1y_share": "첫 취업 1년 이상 소요 비중(%)",
    "exam_prep_thousand": "취업시험 준비자 수(천 명)",
    "exam_prep_ratio": "취업시험 준비자 비율(%)",
    "youth_inactive_thousand": "청년층 비경제활동인구(천 명)",
    "resting_thousand": "쉬었음 청년 수(천 명)",
    "resting_share_in_inactive": "비경제활동인구 중 쉬었음 비중(%)",
    "wage_workers_thousand": "임금근로자 수(천 명)",
    "regular_thousand": "정규직 수(천 명)",
    "nonregular_thousand": "비정규직 수(천 명)",
    "regular_ratio": "정규직 비율(%)",
    "nonregular_ratio": "비정규직 비율(%)",
    "monthly_wage_total_thousand": "월임금총액(천 원)",
    "monthly_salary_thousand": "월급여액(천 원)",
    "hourly_wage_total_won": "시간당임금총액(원)",
    "industry": "산업",
    "workers": "청년 근로자 수(명)",
    "region": "시도",
    "region_short": "시도",
    "region_order": "지역 정렬",
    "regional_employment_rate": "지역별 청년 고용률(%)",
    "regional_unemployment_rate": "지역별 청년 실업률(%)",
}


def kr_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: COLUMN_LABELS.get(c, c) for c in df.columns})


def hero(title: str, subtitle: str, eyebrow: str = "YOUTH EMPLOYMENT DASHBOARD") -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, sub: str | None = None) -> None:
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<div class='section-sub'>{sub}</div>", unsafe_allow_html=True)


def callout(text: str) -> None:
    st.markdown(f"<div class='callout'>{text}</div>", unsafe_allow_html=True)


def caution(text: str) -> None:
    st.markdown(f"<div class='caution'>{text}</div>", unsafe_allow_html=True)


def good(text: str) -> None:
    st.markdown(f"<div class='good'>{text}</div>", unsafe_allow_html=True)


def kpi(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def story_card(num: int, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="story-card">
            <div class="num">{num}</div>
            <h4>{title}</h4>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_period_markers(fig: go.Figure) -> go.Figure:
    """Add light period markers for COVID-era comparison.

    The markers are descriptive period guides, not causal proof.
    """
    fig.add_vrect(
        x0=2019.5, x1=2021.5,
        fillcolor="rgba(239,68,68,0.07)",
        layer="below", line_width=0,
        annotation_text="코로나 충격기",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#F87171"),
    )
    fig.add_vline(
        x=2022, line_dash="dot",
        line_color="rgba(99,102,241,0.4)", line_width=1.2,
        annotation_text="회복기",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#818CF8"),
    )
    return fig


def line_chart(df: pd.DataFrame, columns: list[str], title: str, y_title: str, labels: dict[str, str] | None = None, height: int = 430, show_periods: bool = True) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(columns):
        fig.add_trace(
            go.Scatter(
                x=df["year"], y=df[col], mode="lines+markers",
                name=(labels or {}).get(col, col),
                line=dict(width=3.2, color=COLORWAY[i % len(COLORWAY)]),
                marker=dict(size=8),
            )
        )
    fig.update_layout(
        template=TEMPLATE,
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_BG,
        title=dict(text=title, font=dict(size=17, color=TITLE_COLOR, family="Pretendard")),
        height=height,
        margin=dict(l=30, r=25, t=65, b=35),
        xaxis_title="연도",
        yaxis_title=y_title,
        font=dict(color=FONT_COLOR, family="Pretendard"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0E1629", font_color="#E2E8F0", bordercolor=INDIGO),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR, zeroline=False)
    if show_periods:
        add_period_markers(fig)
    return fig


def dual_axis_line_chart(
    df: pd.DataFrame,
    left_col: str,
    right_col: str,
    title: str,
    left_title: str,
    right_title: str,
    left_name: str,
    right_name: str,
    left_color: str = BLUE,
    right_color: str = ORANGE,
    height: int = 450,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df[left_col], mode="lines+markers", name=left_name,
        line=dict(width=3.4, color=left_color), marker=dict(size=8), yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=df["year"], y=df[right_col], mode="lines+markers", name=right_name,
        line=dict(width=3.4, color=right_color), marker=dict(size=8), yaxis="y2"
    ))
    fig.update_layout(
        template=TEMPLATE,
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_BG,
        title=dict(text=title, font=dict(size=17, color=TITLE_COLOR, family="Pretendard")),
        height=height,
        margin=dict(l=30, r=35, t=65, b=35),
        xaxis_title="연도",
        font=dict(color=FONT_COLOR, family="Pretendard"),
        yaxis=dict(title=left_title, showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR, zeroline=False),
        yaxis2=dict(title=right_title, overlaying="y", side="right", showgrid=False, color=FONT_COLOR, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0E1629", font_color="#E2E8F0", bordercolor=INDIGO),
    )
    add_period_markers(fig)
    return fig


def latest(df: pd.DataFrame) -> pd.Series:
    return df.loc[df["year"] == df["year"].max()].iloc[0]


def diff_text(current: float, past: float, unit: str = "") -> str:
    delta = current - past
    arrow = "증가" if delta > 0 else "감소" if delta < 0 else "변화 없음"
    return f"2015년 대비 {abs(delta):.1f}{unit} {arrow}"


def make_base100(df: pd.DataFrame, cols: list[str], base_year: int | None = None) -> pd.DataFrame:
    base_year = int(base_year or df["year"].min())
    base_row = df.loc[df["year"] == base_year].iloc[0]
    out = pd.DataFrame({"year": df["year"]})
    for col in cols:
        base_value = float(base_row[col])
        out[col] = df[col] / base_value * 100 if base_value != 0 else np.nan
    return out


latest_emp = latest(emp)
latest_first = latest(first)
latest_exam = latest(exam)
latest_rest = latest(rest)
latest_nr = latest(nr)
latest_wage = latest(wage)
latest_region_year = int(region["year"].max())
latest_region = region[region["year"] == latest_region_year].copy()

# -----------------------------------------------------------------------------
# Navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📊 청년 취업 흐름 분석")
st.sidebar.caption("청년 고용지표 대시보드")
page = st.sidebar.radio(
    "페이지",
    [
        "프로젝트 개요",
        "1. 첫 취업까지 시간이 오래 걸리는가",
        "2. 취업 준비 상태에 머무르는가",
        "3. 실업률 밖 쉬었음 청년",
        "4. 취업해도 안정적인가",
        "5. 임금과 산업별 격차",
        "6. 지역별 청년 고용률 격차",
        "종합 결론과 대책",
    ],
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="sidebar-source">
        <div class="source-title">DATA & TOOL</div>
        <div class="source-line">KOSIS 국가통계포털</div>
        <div class="source-line">고용노동부 고용형태별근로실태조사</div>
        <div class="source-line">Streamlit Dashboard</div>
    </div>
    <div class="sidebar-note">※ 원인을 단정하기보다, 공개 통계로 확인되는 흐름을 정리했습니다.</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "프로젝트 개요":
    hero(
        "청년 취업, 어디에서 막히고 있을까?",
        "실업률 하나로는 보이지 않는 흐름을 나눠 본다. 첫 취업까지 걸리는 시간, 취업 준비 상태, 쉬었음 청년, 비정규직, 임금과 산업 구조를 함께 확인한다.",
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi("청년 고용률", f"{latest_emp['employment_rate']:.1f}%", "청년 인구·취업자 수와 함께 보기")
    with c2:
        kpi("첫 취업 소요", f"{latest_first['avg_first_job_months']:.1f}개월", "졸업·중퇴 뒤 첫 일자리 기준")
    with c3:
        kpi("취업시험 준비", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동 청년 중")
    with c4:
        kpi("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%", "비경제활동 청년 중")
    with c5:
        kpi("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", "임금근로 청년 기준")

    section("데이터 출처와 분석 기간", "어떤 자료를 어떤 목적으로 썼는지 먼저 정리했다.")
    sources = pd.DataFrame({
        "데이터": [
            "청년 고용률·실업률·취업자 수",
            "첫 취업 소요기간",
            "취업시험 준비자",
            "쉬었음 청년",
            "정규직·비정규직",
            "청년 임금",
            "산업별 청년 근로자 수·임금",
            "시도별 청년 고용률·실업률",
        ],
        "출처": [
            "KOSIS 경제활동인구조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 경제활동인구조사",
            "KOSIS 경제활동인구조사 근로형태별 부가조사",
            "고용노동부 고용형태별근로실태조사",
            "고용노동부 고용형태별근로실태조사",
            "KOSIS 지역별고용조사",
        ],
        "분석 기간": ["2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025", "2020~2025 중심", "2015~2025"],
        "분석 역할": [
            "공식 고용 흐름",
            "노동시장 진입 지연",
            "취업 준비 장기화",
            "실업률 밖 청년",
            "고용 안정성",
            "취업 후 보상",
            "산업별 일자리 구조",
            "지역별 고용 격차",
        ],
    })
    st.dataframe(sources, use_container_width=True, hide_index=True)
    callout("그래프에는 2015~2019년, 2020~2021년, 2022년 이후를 구분해 표시했다. 코로나가 원인이라고 단정하려는 것이 아니라, 시기별 흐름을 보기 위한 기준선이다.")

    section("고용률만 보면 놓치는 것", "고용률은 비율이다. 청년 인구와 취업자 수가 같이 움직였는지도 확인해야 한다.")
    base100 = make_base100(emp, ["employment_rate", "employed_thousand", "youth_population_proxy_thousand"])
    fig = line_chart(
        base100,
        ["employment_rate", "employed_thousand", "youth_population_proxy_thousand"],
        "청년 고용률·취업자 수·청년 인구 비교: 2015년=100",
        "2015년=100",
        {
            "employment_rate": "고용률 지수",
            "employed_thousand": "취업자 수 지수",
            "youth_population_proxy_thousand": "청년 인구 지수",
        },
        height=430,
    )
    st.plotly_chart(fig, use_container_width=True)
    callout(
        f"청년 고용률은 {emp.iloc[0]['employment_rate']:.1f}%에서 {latest_emp['employment_rate']:.1f}%로 높아졌지만, "
        f"같은 기간 취업자 수는 {emp.iloc[0]['employed_thousand']:,.0f}천 명에서 {latest_emp['employed_thousand']:,.0f}천 명으로, "
        f"청년 인구 추정치는 {emp.iloc[0]['youth_population_proxy_thousand']:,.0f}천 명에서 {latest_emp['youth_population_proxy_thousand']:,.0f}천 명으로 감소했다. "
        "그래서 고용률만 보고 상황이 좋아졌다고 보기 어렵다. 청년 인구와 취업자 수가 줄어든 흐름을 함께 봐야 한다."
    )

    section("대시보드 흐름", "한 번에 결론을 내리기보다, 여섯 가지 질문으로 나눠 본다.")
    items = [
        (1, "첫 취업까지 시간이 오래 걸리는가", "첫 취업 평균소요기간과 1년 이상 걸린 비중을 함께 본다."),
        (2, "취업 준비 상태에 오래 머무는가", "취업시험 준비자 수와 비율로 취업 전 대기 상태를 확인한다."),
        (3, "실업률 밖 청년이 있는가", "쉬었음 청년 규모를 통해 실업률 밖의 흐름을 확인한다."),
        (4, "취업해도 안정적인가", "비정규직 비율과 규모로 일자리 안정성을 본다."),
        (5, "임금·산업 격차가 있는가", "산업별 청년 근로자 수와 임금을 함께 비교한다."),
        (6, "지역별 차이가 있는가", "시도별 고용률과 실업률로 지역별 차이를 확인한다."),
    ]
    for start in range(0, len(items), 3):
        cols = st.columns(3)
        for col, item in zip(cols, items[start:start+3]):
            with col:
                story_card(*item)

elif page == "1. 첫 취업까지 시간이 오래 걸리는가":
    hero(
        "1. 청년들이 첫 취업까지 시간이 오래 걸리는가?",
        "첫 직장까지 걸리는 시간은 청년들이 체감하는 취업 어려움과 바로 연결된다. 평균소요기간과 1년 이상 걸린 비중을 함께 본다.",
        eyebrow="PART 1 · ENTRY DELAY",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("첫 취업 평균소요기간", f"{latest_first['avg_first_job_months']:.1f}개월", "평균값")
    with c2:
        kpi("1년 이상 소요 비중", f"{latest_first['first_job_over_1y_share']:.1f}%", "장기 소요 비중")
    with c3:
        base = first.loc[first["year"] == first["year"].min()].iloc[0]
        kpi("1년 이상 비중 변화", f"+{latest_first['first_job_over_1y_share'] - base['first_job_over_1y_share']:.1f}%p", "2015년 대비")

    callout("평균소요기간은 전체 흐름을, 1년 이상 소요 비중은 장기화된 사례를 보여준다. 두 지표를 같이 봐야 첫 취업 지연을 더 정확히 볼 수 있다.")
    st.plotly_chart(
        dual_axis_line_chart(
            first,
            "avg_first_job_months",
            "first_job_over_1y_share",
            "첫 취업 평균소요기간과 1년 이상 소요 비중",
            "평균소요기간(개월)",
            "1년 이상 소요 비중(%)",
            "평균소요기간",
            "1년 이상 소요 비중",
            BLUE,
            ORANGE,
        ),
        use_container_width=True,
    )

    # distribution latest year
    latest_year = int(first["year"].max())
    f_latest = latest_first
    dist = pd.DataFrame({
        "소요기간": ["3개월 미만", "3~6개월", "6개월~1년", "1~2년", "2~3년", "3년 이상"],
        "인원(천 명)": [
            f_latest["under_3m_thousand"], f_latest["m3_6_thousand"], f_latest["m6_12_thousand"],
            f_latest["y1_2_thousand"], f_latest["y2_3_thousand"], f_latest["over_3y_thousand"],
        ],
    })
    fig = px.bar(dist, x="소요기간", y="인원(천 명)", title=f"{latest_year}년 첫 취업 소요기간 분포", template=TEMPLATE)
    fig.update_traces(marker_color=BLUE)
    fig.update_layout(height=430, margin=dict(l=30, r=25, t=65, b=35))
    st.plotly_chart(fig, use_container_width=True)

    good("첫 취업까지 시간이 길어진다면, 취업 문제는 실업률에 잡히기 전부터 시작된다고 볼 수 있다.")

elif page == "2. 취업 준비 상태에 머무르는가":
    hero(
        "2. 청년들이 취업 준비 상태에 오래 머무는가?",
        "취업시험 준비자는 아직 일자리로 이동하지 못하고 준비 단계에 머무는 청년을 보여준다.",
        eyebrow="PART 2 · PREPARATION BOTTLENECK",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("취업시험 준비자", f"{latest_exam['exam_prep_thousand']:,.0f}천 명", "최근값")
    with c2:
        kpi("준비자 비율", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동인구 중")
    with c3:
        peak = exam.loc[exam["exam_prep_ratio"].idxmax()]
        kpi("비율이 가장 높았던 해", f"{int(peak['year'])}년", f"{peak['exam_prep_ratio']:.1f}%")

    callout("취업시험 준비자 수와 비율은 취업 전 단계가 얼마나 길어지는지 보여준다. 첫 취업 소요기간과 같이 보면 진입 지연 흐름이 더 뚜렷하다.")

    st.plotly_chart(
        dual_axis_line_chart(
            exam,
            "exam_prep_thousand",
            "exam_prep_ratio",
            "취업시험 준비자 수와 비율 추이",
            "준비자 수(천 명)",
            "준비자 비율(%)",
            "취업시험 준비자 수",
            "취업시험 준비자 비율",
            BLUE,
            ORANGE,
        ),
        use_container_width=True,
    )

    caution("취업시험 준비자를 곧바로 취업 실패자로 볼 수는 없다. 여기서는 취업 전 준비 상태가 어느 정도 규모인지 보는 지표로 사용했다.")

elif page == "3. 실업률 밖 쉬었음 청년":
    hero(
        "3. 실업률 밖에 쉬었음 청년이 있는가?",
        "실업률은 구직활동을 하는 사람만 반영한다. 쉬었음 청년을 함께 보면 공식 실업률 밖의 흐름을 볼 수 있다.",
        eyebrow="PART 3 · OUTSIDE OFFICIAL UNEMPLOYMENT",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("쉬었음 청년", f"{latest_rest['resting_thousand']:,.0f}천 명", "최근값")
    with c2:
        kpi("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%", "비경제활동인구 중")
    with c3:
        kpi("공식 실업률", f"{latest_emp['unemployment_rate']:.1f}%", "비교 기준")

    callout("실업률이 낮다고 해서 취업 어려움이 사라졌다고 보기는 어렵다. 쉬었음 청년은 통계상 실업자 밖에 있는 청년층을 살펴보는 보조 지표다.")

    m = emp[["year", "unemployment_rate"]].merge(rest, on="year")
    st.plotly_chart(
        line_chart(m, ["unemployment_rate", "resting_share_in_inactive"], "실업률과 쉬었음 비중 비교", "%", {"unemployment_rate": "실업률", "resting_share_in_inactive": "쉬었음 비중"}),
        use_container_width=True,
    )

    count_compare = emp[["year", "unemployed_thousand"]].merge(rest[["year", "resting_thousand"]], on="year")
    st.plotly_chart(
        line_chart(
            count_compare,
            ["unemployed_thousand", "resting_thousand"],
            "공식 실업자 수와 쉬었음 청년 수 비교",
            "천 명",
            {"unemployed_thousand": "실업자 수", "resting_thousand": "쉬었음 청년 수"},
        ),
        use_container_width=True,
    )

    caution("쉬었음 청년을 모두 구직 포기자로 볼 수는 없다. 건강, 휴식, 개인 사정도 포함된다. 다만 실업자 수와 나란히 보면 실업률 밖 청년 규모를 이해하는 데 도움이 된다.")

elif page == "4. 취업해도 안정적인가":
    hero(
        "4. 취업해도 일자리는 안정적인가?",
        "취업 여부만으로는 일자리의 안정성을 알기 어렵다. 비정규직 비율과 규모를 함께 본다.",
        eyebrow="PART 4 · JOB STABILITY",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", "임금근로 청년 기준")
    with c2:
        kpi("정규직 비율", f"{latest_nr['regular_ratio']:.1f}%", "임금근로 청년 기준")
    with c3:
        kpi("비정규직 규모", f"{latest_nr['nonregular_thousand']:,.0f}천 명", "최근값")

    callout("고용률은 취업 여부를 보여준다. 하지만 체감은 일자리 안정성과도 연결된다. 그래서 비정규직 비율을 함께 본다.")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            line_chart(nr, ["nonregular_ratio"], "청년 비정규직 비율 추이", "%", {"nonregular_ratio": "비정규직 비율"}),
            use_container_width=True,
        )
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=nr["year"], y=nr["regular_thousand"], name="정규직", marker_color=BLUE))
        fig.add_trace(go.Bar(x=nr["year"], y=nr["nonregular_thousand"], name="비정규직", marker_color=ORANGE))
        fig.update_layout(template=TEMPLATE, barmode="stack", title="청년 정규직·비정규직 규모", height=430, yaxis_title="천 명", xaxis_title="연도", margin=dict(l=30, r=25, t=65, b=35), legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
        st.plotly_chart(fig, use_container_width=True)

    caution("비정규직이 항상 나쁜 일자리라는 뜻은 아니다. 여기서는 고용 안정성을 보는 참고 지표로 활용했다.")
    caution("정규직·비정규직 수는 천 명 단위 반올림 자료라 세부 합계와 전체 값에 작은 차이가 날 수 있다.")

elif page == "5. 임금과 산업별 격차":
    hero(
        "5. 어떤 산업에 취업하고, 얼마나 받는가?",
        "산업별 청년 근로자 수와 임금을 함께 보면 일자리의 규모와 보상을 같이 볼 수 있다.",
        eyebrow="PART 5 · PAY & INDUSTRY STRUCTURE",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("월임금총액", f"{latest_wage['monthly_wage_total_thousand']:,.0f}천 원", "29세 이하 명목임금")
    with c2:
        kpi("시간당임금총액", f"{latest_wage['hourly_wage_total_won']:,.0f}원", "근로시간 변화 영향 가능")
    with c3:
        years = sorted(industry["year"].dropna().unique())
        default_year = int(max(years))
        kpi("산업 분석 기준", f"{default_year}년", "연도 선택 가능")

    callout("임금 자료는 취업 후 보상 수준을 보기 위한 자료다. 산업별 근로자 수와 임금을 함께 비교하면 청년이 많이 일하는 산업의 보상 수준도 확인할 수 있다.")

    st.plotly_chart(
        line_chart(wage, ["monthly_wage_total_thousand", "monthly_salary_thousand"], "29세 이하 청년층 월임금 추이", "천 원", {"monthly_wage_total_thousand": "월임금총액", "monthly_salary_thousand": "월급여액"}),
        use_container_width=True,
    )
    caution("2020년 시간당임금은 근로시간 변화의 영향을 받을 수 있다. 그래서 임금 흐름은 월임금총액을 중심으로 해석했다.")

    section("산업별 청년 근로자 수 × 월임금 사분면", "청년이 많이 일하는 산업과 임금이 높은 산업이 일치하는지 확인한다.")
    selected_year = st.selectbox("산업 분석 연도", years, index=len(years) - 1)
    ind = industry[industry["year"] == selected_year].copy()
    ind = ind[(ind["workers"] > 0) & ind["monthly_wage_total_thousand"].notna()]
    x_med = ind["workers"].median()
    y_med = ind["monthly_wage_total_thousand"].median()

    def quadrant(row):
        if row["workers"] >= x_med and row["monthly_wage_total_thousand"] >= y_med:
            return "근로자 많음·임금 높음"
        if row["workers"] >= x_med and row["monthly_wage_total_thousand"] < y_med:
            return "근로자 많음·임금 낮음"
        if row["workers"] < x_med and row["monthly_wage_total_thousand"] >= y_med:
            return "근로자 적음·임금 높음"
        return "근로자 적음·임금 낮음"

    ind["구분"] = ind.apply(quadrant, axis=1)
    fig = px.scatter(
        ind,
        x="workers",
        y="monthly_wage_total_thousand",
        size="workers",
        color="구분",
        text="industry",
        hover_name="industry",
        labels={"workers": "청년 근로자 수(명)", "monthly_wage_total_thousand": "월임금총액(천 원)", "구분": "사분면"},
        title=f"{selected_year}년 산업별 청년 근로자 수와 월임금",
        template=TEMPLATE,
        color_discrete_map={
            "근로자 많음·임금 높음": GREEN,
            "근로자 많음·임금 낮음": ORANGE,
            "근로자 적음·임금 높음": BLUE,
            "근로자 적음·임금 낮음": GRAY,
        },
    )
    fig.add_vline(x=x_med, line_dash="dash", line_color="#94A3B8")
    fig.add_hline(y=y_med, line_dash="dash", line_color="#94A3B8")
    fig.update_traces(marker=dict(opacity=.78), textposition="top center")
    fig.update_layout(height=650, margin=dict(l=30, r=25, t=65, b=35), legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        top_workers = ind.sort_values("workers", ascending=False).head(8)
        fig1 = px.bar(top_workers.sort_values("workers"), x="workers", y="industry", orientation="h", title="청년 근로자 수 상위 산업", labels={"workers": "근로자 수(명)", "industry": "산업"}, template=TEMPLATE)
        fig1.update_traces(marker_color=BLUE)
        fig1.update_layout(height=440, margin=dict(l=30, r=20, t=60, b=30))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        top_wage = ind.sort_values("monthly_wage_total_thousand", ascending=False).head(8)
        fig2 = px.bar(top_wage.sort_values("monthly_wage_total_thousand"), x="monthly_wage_total_thousand", y="industry", orientation="h", title="월임금총액 상위 산업", labels={"monthly_wage_total_thousand": "월임금총액(천 원)", "industry": "산업"}, template=TEMPLATE)
        fig2.update_traces(marker_color=GREEN)
        fig2.update_layout(height=440, margin=dict(l=30, r=20, t=60, b=30))
        st.plotly_chart(fig2, use_container_width=True)

    caution("임금은 명목임금 기준이다. 물가와 주거비를 반영한 실질임금 분석은 후속 과제로 남긴다.")

elif page == "6. 지역별 청년 고용률 격차":
    hero(
        "6. 지역마다 청년 고용 상황이 다를까?",
        "전국 평균만 보면 지역 차이가 가려질 수 있다. 시도별 고용률과 실업률로 지역별 차이를 확인한다.",
        eyebrow="PART 6 · REGIONAL GAP",
    )

    years = sorted(region["year"].dropna().unique())
    default_year = int(max(years))
    selected_year = st.selectbox("지역 비교 연도", years, index=len(years) - 1)
    reg = region[region["year"] == selected_year].copy()
    reg = reg.dropna(subset=["regional_employment_rate"]).sort_values("regional_employment_rate", ascending=False)
    national = emp[emp["year"] == selected_year].iloc[0] if selected_year in emp["year"].values else None
    national_emp = float(national["employment_rate"]) if national is not None else None
    national_unemp = float(national["unemployment_rate"]) if national is not None else None

    top_emp = reg.head(5)[["region_short", "regional_employment_rate"]]
    low_emp = reg.tail(5).sort_values("regional_employment_rate")[["region_short", "regional_employment_rate"]]
    high_unemp = reg.dropna(subset=["regional_unemployment_rate"]).sort_values("regional_unemployment_rate", ascending=False).head(5)[["region_short", "regional_unemployment_rate"]]

    c1, c2, c3 = st.columns(3)
    with c1:
        if national_emp is not None:
            kpi("전국 청년 고용률", f"{national_emp:.1f}%", f"{selected_year}년 기준")
        else:
            kpi("비교 연도", f"{selected_year}년", "지역별 자료 기준")
    with c2:
        best = reg.iloc[0]
        kpi("고용률 최고 지역", f"{best['region_short']}", f"{best['regional_employment_rate']:.1f}%")
    with c3:
        worst = reg.iloc[-1]
        kpi("고용률 최저 지역", f"{worst['region_short']}", f"{worst['regional_employment_rate']:.1f}%")

    callout("지역별 고용률은 각 지역 청년 중 취업한 비율을 보여준다. 전국 평균 뒤에 가려진 지역 차이를 확인하는 데 유용하다.")

    fig = px.bar(
        reg.sort_values("regional_employment_rate"),
        x="regional_employment_rate",
        y="region_short",
        orientation="h",
        title=f"{selected_year}년 시도별 청년 고용률",
        labels={"regional_employment_rate": "청년 고용률(%)", "region_short": "시도"},
        template=TEMPLATE,
    )
    fig.update_traces(marker_color=BLUE)
    if national_emp is not None:
        fig.add_vline(x=national_emp, line_dash="dash", line_color=ORANGE, annotation_text=f"전국 {national_emp:.1f}%", annotation_position="top right")
    fig.update_layout(height=650, margin=dict(l=30, r=25, t=65, b=35))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section("고용률 상위·하위 지역", "전체 시도를 모두 포함하고, 표에서는 상위 5개와 하위 5개만 따로 보여준다.")
        t1 = top_emp[["region_short", "regional_employment_rate"]].rename(
            columns={"region_short": "고용률 상위 지역", "regional_employment_rate": "상위 고용률(%)"}
        ).reset_index(drop=True)
        t2 = low_emp[["region_short", "regional_employment_rate"]].rename(
            columns={"region_short": "고용률 하위 지역", "regional_employment_rate": "하위 고용률(%)"}
        ).reset_index(drop=True)
        both = pd.concat([t1, t2], axis=1)
        st.dataframe(both, use_container_width=True, hide_index=True)
    with col2:
        section("실업률 보조 확인", "지역별 실업률은 표본 규모에 따라 변동이 클 수 있어 참고 지표로만 사용했다. 세종특별자치시는 2015~2016년 값이 없어 공백으로 표시된다.")
        fig2 = px.bar(
            reg.dropna(subset=["regional_unemployment_rate"]).sort_values("regional_unemployment_rate", ascending=True),
            x="regional_unemployment_rate",
            y="region_short",
            orientation="h",
            title=f"{selected_year}년 시도별 청년 실업률",
            labels={"regional_unemployment_rate": "청년 실업률(%)", "region_short": "시도"},
            template=TEMPLATE,
        )
        fig2.update_traces(marker_color=ORANGE)
        if national_unemp is not None:
            fig2.add_vline(x=national_unemp, line_dash="dash", line_color=BLUE, annotation_text=f"전국 {national_unemp:.1f}%", annotation_position="top right")
        fig2.update_layout(height=520, margin=dict(l=30, r=25, t=65, b=35))
        st.plotly_chart(fig2, use_container_width=True)

    # Heatmap for regional employment rate trend
    section("지역별 고용률 흐름", "한 해의 순위보다 여러 해의 흐름을 함께 보는 것이 더 안정적이다.")
    heat = region.pivot(index="region_short", columns="year", values="regional_employment_rate")
    order = region.drop_duplicates("region_short").sort_values("region_order")["region_short"].tolist()
    heat = heat.reindex(order)
    fig3 = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(x="연도", y="시도", color="고용률(%)"),
        title="시도별 청년 고용률 heatmap",
    )
    fig3.update_layout(height=560, margin=dict(l=30, r=25, t=65, b=35))
    st.plotly_chart(fig3, use_container_width=True)

    caution("지역별 고용률만으로 특정 지역의 취업난을 단정할 수는 없다. 산업 구조, 인구 이동, 대학과 기업 분포가 함께 영향을 준다.")

elif page == "종합 결론과 대책":
    hero(
        "종합 결론과 대책",
        "분석 결과를 한 문장으로 묶고, 각 문제와 대응책을 1:1로 연결한다.",
        eyebrow="CONCLUSION · ACTIONABLE INSIGHTS",
    )

    section("종합 결론")
    good("실업률 하나만으로는 청년 취업 상황을 충분히 설명하기 어렵다. 첫 취업까지 걸리는 시간, 취업시험 준비자, 쉬었음 청년, 비정규직 비율, 산업별 임금 차이와 지역별 고용률을 함께 봐야 한다. 이 지표들을 종합하면 청년 취업 문제는 <b>취업 전 지연·실업률 밖 청년·일자리 안정성·산업별 보상 차이·지역별 여건 차이</b>가 겹쳐 나타나는 문제로 볼 수 있다.")

    section("데이터 결과와 대책 연결")
    policy = pd.DataFrame({
        "분석에서 확인한 문제": [
            "첫 취업까지 시간이 오래 걸림",
            "취업시험 준비 상태에 머무는 청년 존재",
            "실업률에 잡히지 않는 쉬었음 청년 존재",
            "청년 비정규직 비율이 높음",
            "산업별 근로자 수와 임금 격차 존재",
            "지역별 청년 고용률 차이 존재",
            "명목임금만으로 생활 안정성 판단 어려움",
        ],
        "대응 방향": [
            "첫 일자리 매칭 강화, 직무 연계형 인턴십 확대",
            "장기 취업준비 청년 대상 진로 전환·민간 채용 연계 지원",
            "노동시장 재진입 상담, 직업훈련, 심리·진로 복합 지원",
            "청년 비정규직 장기근속 유도 및 정규직 전환 인센티브",
            "저임금 산업 근로조건 개선, 성장 산업 직무교육 확대",
            "지역별 산업 구조를 고려한 청년 일자리 매칭과 지방 정착 지원",
            "실질임금, 주거비, 생활비를 반영한 후속 분석 필요",
        ],
        "핵심 해석": [
            "취업 어려움은 첫 일자리 전 단계에서 이미 나타난다.",
            "준비 기간이 길어지면 노동시장 진입도 늦어진다.",
            "실업률에 잡히지 않는 청년층도 함께 봐야 한다.",
            "취업 여부만큼 일자리 안정성도 중요하다.",
            "청년이 많은 산업이 반드시 높은 임금을 주는 것은 아니다.",
            "전국 평균만으로는 지역 차이를 보기 어렵다.",
            "명목임금만으로 생활 안정성을 판단하기는 어렵다.",
        ],
    })
    st.dataframe(policy, use_container_width=True, hide_index=True)

    callout("최종 정리: <b>이 대시보드는 청년 취업 문제를 고용률 하나로 보지 않고, 청년 인구 감소 속의 취업자 수 변화·첫 취업 지연·취업 준비 장기화·쉬었음 청년·비정규직·산업별 임금 차이·지역별 고용률 차이로 나누어 정리했다.</b>")
