
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="청년 첫 취업 지연 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data" / "processed"

# -----------------------------------------------------------------------------
# Design: dark premium analytics dashboard
# -----------------------------------------------------------------------------
INDIGO = "#6366F1"
TEAL = "#10B981"
AMBER = "#F59E0B"
ROSE = "#F43F5E"
SKY = "#38BDF8"
VIOLET = "#A78BFA"
LIME = "#84CC16"
SLATE = "#94A3B8"
BLUE = INDIGO
GREEN = TEAL
ORANGE = AMBER
RED = ROSE
PURPLE = VIOLET
GRAY = SLATE
COLORWAY = [INDIGO, TEAL, AMBER, ROSE, SKY, VIOLET, LIME, SLATE]
TEMPLATE = "plotly_dark"

st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Pretendard', 'Noto Sans KR', system-ui, sans-serif; }
.stApp { background: #080E1C; color: #E2E8F0; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1320px; }
section[data-testid="stSidebar"] { background: #050A14; border-right: 1px solid rgba(99,132,255,.15); }
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(99,132,255,.08); border: 1px solid rgba(99,132,255,.15);
    border-radius: 10px; padding: 7px 10px; margin-bottom: 5px; transition: background .18s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(99,132,255,.18); }
.sidebar-source { background: rgba(99,132,255,.07); border: 1px solid rgba(99,132,255,.18); border-radius: 14px; padding: 14px; margin-top: 12px; }
.sidebar-source .source-title { font-size: .76rem; font-weight: 700; color: #818CF8 !important; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 8px; }
.sidebar-source .source-line { font-size: .85rem; line-height: 1.7; color: #94A3B8 !important; }
.sidebar-note { font-size: .75rem; color: #64748B !important; margin-top: 10px; line-height: 1.6; }
.hero {
    background: radial-gradient(ellipse at 0% 0%, rgba(99,102,241,.28) 0%, transparent 55%),
                radial-gradient(ellipse at 100% 100%, rgba(16,185,129,.16) 0%, transparent 50%),
                linear-gradient(160deg, #0D1528 0%, #0A1020 60%, #080E1C 100%);
    border: 1px solid rgba(99,102,241,.22); border-radius: 24px; padding: 38px 42px;
    margin-bottom: 24px; position: relative; overflow: hidden;
}
.hero::before { content: ''; position: absolute; top: -1px; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #6366F1, #10B981, transparent); }
.hero .eyebrow { font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #818CF8; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.hero .eyebrow::before { content: ''; display: inline-block; width: 22px; height: 2px; background: #6366F1; border-radius: 2px; }
.hero h1 { font-size: 2.35rem; line-height: 1.15; margin: 0 0 14px; letter-spacing: -0.04em; font-weight: 800; color: #F1F5F9; }
.hero h1 span { color: #818CF8; }
.hero p { font-size: 1rem; color: rgba(226,232,240,.72); line-height: 1.78; margin: 0; max-width: 920px; }
.section-title { font-size: 1.22rem; font-weight: 800; letter-spacing: -0.02em; color: #F1F5F9; margin: 28px 0 6px; padding-left: 14px; border-left: 3px solid #6366F1; }
.section-sub { font-size: .92rem; color: #64748B; line-height: 1.65; margin-bottom: 14px; padding-left: 17px; }
.kpi { background: linear-gradient(145deg, #0E1629, #0A1020); border: 1px solid rgba(99,102,241,.2); border-radius: 18px; padding: 20px 20px 18px; min-height: 120px; position: relative; overflow: hidden; }
.kpi::after { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,.5), transparent); }
.kpi .label { font-size: .76rem; color: #64748B; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 10px; }
.kpi .value { font-family: 'DM Mono', 'Pretendard', monospace; font-size: 1.9rem; font-weight: 500; letter-spacing: -0.03em; color: #E2E8F0; text-shadow: 0 0 24px rgba(99,102,241,.35); }
.kpi .note { font-size: .78rem; color: #475569; margin-top: 8px; line-height: 1.5; }
.card { background: #0E1629; border: 1px solid rgba(99,102,241,.18); border-radius: 20px; padding: 20px 22px; margin-bottom: 16px; }
.story-card { background: linear-gradient(145deg, #0E1629, #0A1020); border: 1px solid rgba(99,102,241,.16); border-radius: 18px; padding: 20px; height: 100%; }
.story-card .num { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; border-radius: 8px; background: rgba(99,102,241,.18); color: #818CF8; font-weight: 800; font-size: .85rem; margin-bottom: 12px; border: 1px solid rgba(99,102,241,.25); }
.story-card h4 { margin: 0 0 8px; font-size: .98rem; color: #E2E8F0; font-weight: 700; }
.story-card p { margin: 0; font-size: .87rem; line-height: 1.65; color: #64748B; }
.callout { background: rgba(99,102,241,.08); color: #A5B4FC; border: 1px solid rgba(99,102,241,.22); border-left: 4px solid #6366F1; padding: 14px 16px; border-radius: 12px; line-height: 1.7; margin: 12px 0 18px; font-size: .92rem; }
.caution { background: rgba(249,115,22,.07); color: #FDBA74; border: 1px solid rgba(249,115,22,.2); border-left: 4px solid #F97316; padding: 14px 16px; border-radius: 12px; line-height: 1.7; margin: 12px 0 18px; font-size: .92rem; }
.good { background: rgba(16,185,129,.07); color: #6EE7B7; border: 1px solid rgba(16,185,129,.2); border-left: 4px solid #10B981; padding: 14px 16px; border-radius: 12px; line-height: 1.7; margin: 12px 0 18px; font-size: .92rem; }
.badge { display: inline-block; background: rgba(99,102,241,.15); color: #818CF8; border: 1px solid rgba(99,102,241,.25); border-radius: 999px; padding: 4px 10px; font-weight: 700; font-size: .75rem; margin: 3px 4px 3px 0; }
div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
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
        "exam_field": pd.read_csv(DATA_DIR / "exam_prep_field.csv"),
        "resting": pd.read_csv(DATA_DIR / "resting.csv"),
        "nonregular": pd.read_csv(DATA_DIR / "nonregular.csv"),
        "first_job_industry": pd.read_csv(DATA_DIR / "first_job_industry.csv"),
        "region": pd.read_csv(DATA_DIR / "region.csv"),
    }

data = load_data()
emp = data["employment"]
first = data["first_job"]
exam = data["exam"]
exam_field = data["exam_field"]
rest = data["resting"]
nr = data["nonregular"]
fj_ind = data["first_job_industry"]
region = data["region"]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
COLUMN_LABELS = {
    "year": "연도",
    "employment_rate": "고용률(%)",
    "unemployment_rate": "실업률(%)",
    "unemployed_thousand": "실업자 수(천 명)",
    "employed_thousand": "취업자 수(천 명)",
    "inactive_thousand": "비경제활동인구(천 명)",
    "youth_population_proxy_thousand": "청년 인구 추정치(천 명)",
    "avg_first_job_months": "첫 취업 평균소요기간(개월)",
    "first_job_over_1y_share": "첫 취업 1년 이상 소요 비중(%)",
    "first_job_total_thousand": "첫 취업 유경험자(천 명)",
    "exam_prep_thousand": "취업시험 준비자 수(천 명)",
    "exam_prep_ratio": "취업시험 준비자 비율(%)",
    "youth_inactive_thousand": "청년층 비경제활동인구(천 명)",
    "category": "준비 분야",
    "value_thousand": "인원(천 명)",
    "share_percent": "비중(%)",
    "resting_thousand": "쉬었음 청년 수(천 명)",
    "resting_share_in_inactive": "비경제활동인구 중 쉬었음 비중(%)",
    "wage_workers_thousand": "임금근로자 수(천 명)",
    "regular_thousand": "정규직 수(천 명)",
    "nonregular_thousand": "비정규직 수(천 명)",
    "regular_ratio": "정규직 비율(%)",
    "nonregular_ratio": "비정규직 비율(%)",
    "industry": "산업",
    "first_job_industry_thousand": "첫 일자리 인원(천 명)",
    "region_short": "시도",
    "regional_employment_rate": "지역별 청년 고용률(%)",
    "regional_unemployment_rate": "지역별 청년 실업률(%)",
}

def kr_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: COLUMN_LABELS.get(c, c) for c in df.columns})

def latest(df: pd.DataFrame) -> pd.Series:
    return df.sort_values("year").iloc[-1]

def hero(title: str, subtitle: str, eyebrow: str = "YOUTH FIRST JOB DASHBOARD") -> None:
    st.markdown(f"""
    <div class="hero">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="kpi">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

def story_card(num: int, title: str, text: str) -> None:
    st.markdown(f"""
    <div class="story-card">
        <div class="num">{num}</div>
        <h4>{title}</h4>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)

def style_fig(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        template=TEMPLATE,
        colorway=COLORWAY,
        height=height,
        margin=dict(l=35, r=25, t=70, b=40),
        paper_bgcolor="#0A1020",
        plot_bgcolor="#0A1020",
        font=dict(color="#94A3B8", family="Pretendard"),
        title=dict(font=dict(color="#E2E8F0", size=18), x=0.02),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
    )
    fig.update_xaxes(gridcolor="rgba(99,102,241,.10)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(99,102,241,.10)", zeroline=False)
    return fig

def add_period_markers(fig: go.Figure) -> go.Figure:
    fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor="rgba(239,68,68,0.07)", line_width=0, layer="below")
    fig.add_vline(x=2022, line_width=1, line_dash="dot", line_color="rgba(148,163,184,.55)")
    fig.add_annotation(x=2020.5, y=1.05, yref="paper", text="2020~2021", showarrow=False, font=dict(size=11, color="#FCA5A5"))
    fig.add_annotation(x=2022, y=1.12, yref="paper", text="2022 이후", showarrow=False, font=dict(size=11, color="#94A3B8"))
    return fig

def line_chart(df: pd.DataFrame, y_cols: list[str], title: str, y_title: str, names: dict[str, str] | None = None, height: int = 430) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[col], mode="lines+markers", name=(names or {}).get(col, col),
            line=dict(width=3, color=COLORWAY[i % len(COLORWAY)]), marker=dict(size=7)
        ))
    fig.update_layout(title=title, xaxis_title="연도", yaxis_title=y_title)
    fig = style_fig(fig, height=height)
    return add_period_markers(fig)

def dual_axis_line_chart(df: pd.DataFrame, left_col: str, right_col: str, title: str, left_title: str, right_title: str, left_name: str, right_name: str, left_color: str = BLUE, right_color: str = ORANGE, height: int = 430) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["year"], y=df[left_col], mode="lines+markers", name=left_name, line=dict(color=left_color, width=3)))
    fig.add_trace(go.Scatter(x=df["year"], y=df[right_col], mode="lines+markers", name=right_name, yaxis="y2", line=dict(color=right_color, width=3)))
    fig.update_layout(title=title, xaxis_title="연도", yaxis_title=left_title, yaxis2=dict(title=right_title, overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"))
    fig = style_fig(fig, height=height)
    return add_period_markers(fig)

def make_base100(df: pd.DataFrame, cols: list[str], base_year: int | None = None) -> pd.DataFrame:
    base_year = int(base_year or df["year"].min())
    base_row = df.loc[df["year"] == base_year].iloc[0]
    out = pd.DataFrame({"year": df["year"]})
    for col in cols:
        base_value = float(base_row[col])
        out[col] = df[col] / base_value * 100 if base_value != 0 else np.nan
    return out

def horizontal_bar(df: pd.DataFrame, x: str, y: str, title: str, x_label: str, y_label: str = "", color: str = BLUE, height: int = 460) -> go.Figure:
    fig = px.bar(df, x=x, y=y, orientation="h", title=title, labels={x: x_label, y: y_label}, template=TEMPLATE)
    fig.update_traces(marker_color=color)
    fig = style_fig(fig, height=height)
    return fig

latest_emp = latest(emp)
latest_first = latest(first)
latest_exam = latest(exam)
latest_rest = latest(rest)
latest_nr = latest(nr)
latest_field_year = int(exam_field["year"].max())
latest_exam_field = exam_field[exam_field["year"] == latest_field_year].copy()
latest_ind_year = int(fj_ind["year"].max())
latest_fj_ind = fj_ind[(fj_ind["year"] == latest_ind_year) & fj_ind["first_job_industry_thousand"].notna()].copy()
latest_region_year = int(region["year"].max())
latest_region = region[region["year"] == latest_region_year].copy()

# -----------------------------------------------------------------------------
# Navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📊 청년 첫 취업 지연 분석")
st.sidebar.caption("공공데이터 기반 탐색형 대시보드")
page = st.sidebar.radio(
    "페이지",
    [
        "프로젝트 개요",
        "1. 첫 취업까지 얼마나 걸리는가",
        "2. 취업 준비는 어디로 향하는가",
        "3. 실업률 밖 쉬었음 청년",
        "4. 첫 취업 이후 일자리는 안정적인가",
        "5. 첫 취업은 어느 산업으로 연결되는가",
        "6. 지역별 진입 여건은 다른가",
        "종합 결론과 대책",
    ],
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="sidebar-source">
        <div class="source-title">DATA & TOOL</div>
        <div class="source-line">KOSIS 경제활동인구조사</div>
        <div class="source-line">KOSIS 청년층 부가조사</div>
        <div class="source-line">KOSIS 지역별고용조사</div>
        <div class="source-line">Streamlit Dashboard</div>
    </div>
    <div class="sidebar-note">※ 원인을 단정하기보다, 공개 통계로 확인되는 첫 취업 진입 흐름을 정리했습니다.</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "프로젝트 개요":
    hero(
        "청년의 <span>첫 취업</span>은 왜 늦어질까?",
        "청년 취업난 전체를 모두 설명하기보다, 청년들이 노동시장에 처음 들어가는 과정에서 어떤 지연과 구조가 나타나는지 살펴본다.",
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi("청년 고용률", f"{latest_emp['employment_rate']:.1f}%", "청년 인구·취업자 수와 함께 해석")
    with c2:
        kpi("첫 취업 소요", f"{latest_first['avg_first_job_months']:.1f}개월", "졸업·중퇴 뒤 첫 일자리 기준")
    with c3:
        kpi("1년 이상 소요", f"{latest_first['first_job_over_1y_share']:.1f}%", "첫 취업 장기 지연")
    with c4:
        kpi("취업시험 준비", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동 청년 중")
    with c5:
        kpi("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%", "비경제활동 청년 중")

    section("문제 정의와 분석 범위", "첫 취업 지연을 개인의 준비 문제로만 보지 않고, 진입 전·진입 과정·진입 후·지역 여건으로 나누어 본다.")
    callout(
        "이 대시보드는 ‘청년이 취업하기 힘들다’는 큰 질문을 그대로 다루기보다, 그중에서도 <b>첫 취업 지연</b>에 초점을 맞췄다. "
        "첫 취업까지 걸리는 시간, 취업시험 준비 상태, 쉬었음 청년, 비정규직 비율, 첫 일자리 산업 분포, 지역별 고용률을 통해 청년의 노동시장 진입 흐름을 확인한다."
    )

    section("데이터 출처와 분석 기간", "임금 자료는 제외하고, 첫 취업 진입과 직접 연결되는 자료 중심으로 재구성했다.")
    sources = pd.DataFrame({
        "데이터": [
            "청년 고용률·실업률·취업자 수",
            "첫 취업 소요기간",
            "취업시험 준비자 수·비율",
            "취업시험 준비 분야",
            "쉬었음 청년",
            "정규직·비정규직",
            "첫 일자리 산업 분포",
            "시도별 청년 고용률·실업률",
        ],
        "출처": [
            "KOSIS 경제활동인구조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 경제활동인구조사",
            "KOSIS 경제활동인구조사 근로형태별 부가조사",
            "KOSIS 경제활동인구조사 청년층 부가조사",
            "KOSIS 지역별고용조사",
        ],
        "분석 기간": ["2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025", "2015~2025"],
        "분석 역할": [
            "고용시장 배경",
            "첫 취업 지연 직접 지표",
            "취업 전 대기 상태",
            "준비 방향 확인",
            "실업률 밖 청년",
            "진입 후 고용 안정성",
            "첫 일자리 진입 산업",
            "지역별 진입 여건",
        ],
    })
    st.dataframe(sources, use_container_width=True, hide_index=True)

    section("고용률만 보면 놓치는 것", "고용률은 비율이다. 청년 인구와 취업자 수가 같이 움직였는지도 확인해야 한다.")
    base100 = make_base100(emp, ["employment_rate", "employed_thousand", "youth_population_proxy_thousand"])
    fig = line_chart(
        base100,
        ["employment_rate", "employed_thousand", "youth_population_proxy_thousand"],
        "청년 고용률·취업자 수·청년 인구 비교: 2015년=100",
        "2015년=100",
        {"employment_rate": "고용률 지수", "employed_thousand": "취업자 수 지수", "youth_population_proxy_thousand": "청년 인구 지수"},
        height=430,
    )
    st.plotly_chart(fig, use_container_width=True)
    callout(
        f"청년 고용률은 {emp.iloc[0]['employment_rate']:.1f}%에서 {latest_emp['employment_rate']:.1f}%로 높아졌지만, "
        f"같은 기간 취업자 수는 {emp.iloc[0]['employed_thousand']:,.0f}천 명에서 {latest_emp['employed_thousand']:,.0f}천 명으로, "
        f"청년 인구 추정치는 {emp.iloc[0]['youth_population_proxy_thousand']:,.0f}천 명에서 {latest_emp['youth_population_proxy_thousand']:,.0f}천 명으로 줄었다. "
        "그래서 고용률 하나로 첫 취업 상황이 개선됐다고 단정하기 어렵다."
    )

    section("대시보드 흐름", "각 페이지는 첫 취업 지연을 서로 다른 각도에서 확인한다.")
    items = [
        (1, "첫 취업까지 얼마나 걸리는가", "첫 취업 평균소요기간과 1년 이상 소요 비중을 확인한다."),
        (2, "취업 준비는 어디로 향하는가", "취업시험 준비자 규모와 준비 분야 변화를 본다."),
        (3, "실업률 밖 청년이 있는가", "쉬었음 청년을 통해 공식 실업률 밖 흐름을 확인한다."),
        (4, "첫 취업 이후 일자리는 안정적인가", "비정규직 비율과 규모로 고용 안정성을 본다."),
        (5, "첫 취업은 어느 산업으로 연결되는가", "실제 첫 일자리 산업 분포와 집중도를 확인한다."),
        (6, "지역별 진입 여건은 다른가", "시도별 고용률과 실업률로 지역 차이를 본다."),
    ]
    for start in range(0, len(items), 3):
        cols = st.columns(3)
        for col, item in zip(cols, items[start:start+3]):
            with col:
                story_card(*item)

elif page == "1. 첫 취업까지 얼마나 걸리는가":
    hero(
        "1. 첫 취업까지 얼마나 걸리는가?",
        "첫 직장까지 걸리는 시간은 청년들이 체감하는 취업 지연과 직접 연결된다. 평균소요기간과 1년 이상 소요 비중을 함께 본다.",
        eyebrow="PART 1 · ENTRY DELAY",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("첫 취업 평균소요기간", f"{latest_first['avg_first_job_months']:.1f}개월", "최근값")
    with c2:
        kpi("1년 이상 소요 비중", f"{latest_first['first_job_over_1y_share']:.1f}%", "장기 지연 집단")
    with c3:
        kpi("첫 취업 유경험자", f"{latest_first['first_job_total_thousand']:,.0f}천 명", "최근값")

    callout("평균소요기간은 전체 흐름을 보여주고, 1년 이상 소요 비중은 장기 지연 집단의 규모를 보여준다. 두 지표를 함께 봐야 첫 취업 지연을 더 안정적으로 설명할 수 있다.")
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

    latest_year = int(latest_first["year"])
    dist = pd.DataFrame({
        "소요기간": ["3개월 미만", "3~6개월", "6개월~1년", "1~2년", "2~3년", "3년 이상"],
        "인원(천 명)": [
            latest_first["under_3m_thousand"], latest_first["m3_6_thousand"], latest_first["m6_12_thousand"],
            latest_first["y1_2_thousand"], latest_first["y2_3_thousand"], latest_first["over_3y_thousand"],
        ],
    })
    fig = px.bar(dist, x="소요기간", y="인원(천 명)", title=f"{latest_year}년 첫 취업 소요기간 분포", template=TEMPLATE)
    fig.update_traces(marker_color=BLUE)
    fig = style_fig(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    good("첫 취업까지 시간이 길어진다면, 취업 문제는 실업률에 잡히기 전부터 시작된다고 볼 수 있다.")

elif page == "2. 취업 준비는 어디로 향하는가":
    hero(
        "2. 취업 준비는 어디로 향하는가?",
        "취업시험 준비자는 아직 일자리로 이동하지 못하고 준비 단계에 머무는 청년을 보여준다. 준비 분야를 보면 그 대기 상태가 어디로 향하는지도 확인할 수 있다.",
        eyebrow="PART 2 · PREPARATION DIRECTION",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("취업시험 준비자", f"{latest_exam['exam_prep_thousand']:,.0f}천 명", "최근값")
    with c2:
        kpi("준비자 비율", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동인구 중")
    with c3:
        top_field = latest_exam_field.sort_values("share_percent", ascending=False).iloc[0]
        kpi("가장 큰 준비 분야", f"{top_field['category']}", f"{top_field['share_percent']:.1f}%")

    callout("취업시험 준비자는 ‘취업하지 않는 청년’이 아니라, 특정 분야를 목표로 준비 상태에 머무는 청년층을 보여준다. 그래서 준비자 수와 준비 분야를 함께 본다.")
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

    section("취업시험 준비 분야", "일반기업체·공무원·전문직 등 어떤 방향의 준비가 큰지 확인한다.")
    field_pivot = exam_field.pivot(index="year", columns="category", values="share_percent").reset_index()
    field_cols = [c for c in field_pivot.columns if c != "year"]
    fig = line_chart(field_pivot, field_cols, "취업시험 준비 분야별 비중 추이", "%", {c: c for c in field_cols}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    latest_field_bar = latest_exam_field.sort_values("share_percent", ascending=True)
    fig = horizontal_bar(latest_field_bar, "share_percent", "category", f"{latest_field_year}년 취업시험 준비 분야 비중", "비중(%)", "준비 분야", color=GREEN, height=420)
    st.plotly_chart(fig, use_container_width=True)
    caution("준비 분야 비중은 취업시험 준비자 전체를 분모로 계산했다. 준비자를 취업 실패자로 단정하지 않고, 취업 전 대기 상태와 준비 방향을 보여주는 지표로 해석한다.")

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

    callout("실업률이 낮다고 해서 취업 어려움이 사라졌다고 보기 어렵다. 쉬었음 청년은 통계상 실업자 밖에 있는 청년층을 살펴보는 보조 지표다.")
    m = emp[["year", "unemployment_rate"]].merge(rest, on="year")
    st.plotly_chart(line_chart(m, ["unemployment_rate", "resting_share_in_inactive"], "실업률과 쉬었음 비중 비교", "%", {"unemployment_rate": "실업률", "resting_share_in_inactive": "쉬었음 비중"}), use_container_width=True)
    count_compare = emp[["year", "unemployed_thousand"]].merge(rest[["year", "resting_thousand"]], on="year")
    st.plotly_chart(line_chart(count_compare, ["unemployed_thousand", "resting_thousand"], "공식 실업자 수와 쉬었음 청년 수 비교", "천 명", {"unemployed_thousand": "실업자 수", "resting_thousand": "쉬었음 청년 수"}), use_container_width=True)
    caution("쉬었음 청년을 모두 구직 포기자로 볼 수는 없다. 건강, 휴식, 개인 사정도 포함된다. 다만 실업자 수와 나란히 보면 실업률 밖 청년 규모를 이해하는 데 도움이 된다.")

elif page == "4. 첫 취업 이후 일자리는 안정적인가":
    hero(
        "4. 첫 취업 이후 일자리는 안정적인가?",
        "첫 취업에 성공하더라도 일자리 안정성이 낮다면 청년의 노동시장 안착은 늦어질 수 있다. 비정규직 비율과 규모를 함께 본다.",
        eyebrow="PART 4 · JOB STABILITY",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", "임금근로 청년 기준")
    with c2:
        kpi("정규직 비율", f"{latest_nr['regular_ratio']:.1f}%", "임금근로 청년 기준")
    with c3:
        kpi("비정규직 규모", f"{latest_nr['nonregular_thousand']:,.0f}천 명", "최근값")

    callout("고용률은 취업 여부를 보여준다. 하지만 첫 취업 이후의 체감은 일자리 안정성과도 연결된다. 그래서 비정규직 비율을 함께 본다.")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(line_chart(nr, ["nonregular_ratio"], "청년 비정규직 비율 추이", "%", {"nonregular_ratio": "비정규직 비율"}), use_container_width=True)
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=nr["year"], y=nr["regular_thousand"], name="정규직", marker_color=BLUE))
        fig.add_trace(go.Bar(x=nr["year"], y=nr["nonregular_thousand"], name="비정규직", marker_color=ORANGE))
        fig.update_layout(title="청년 정규직·비정규직 규모", xaxis_title="연도", yaxis_title="천 명", barmode="stack")
        fig = style_fig(fig, 430)
        st.plotly_chart(fig, use_container_width=True)
    caution("비정규직이 항상 나쁜 일자리라는 뜻은 아니다. 여기서는 고용 안정성을 보는 참고 지표로 활용했다.")
    caution("정규직·비정규직 수는 천 명 단위 반올림 자료라 세부 합계와 전체 값에 작은 차이가 날 수 있다.")

elif page == "5. 첫 취업은 어느 산업으로 연결되는가":
    hero(
        "5. 첫 취업은 어느 산업으로 연결되는가?",
        "임금 파트는 제외하고, 청년들이 실제 첫 일자리로 어느 산업에 진입하는지 확인했다. 첫 취업 지연을 진입 산업 구조와 함께 보기 위한 페이지다.",
        eyebrow="PART 5 · FIRST JOB INDUSTRY",
    )
    ind_valid = latest_fj_ind.dropna(subset=["first_job_industry_thousand"]).copy()
    ind_valid = ind_valid.sort_values("share_percent", ascending=False)
    top3_share = ind_valid.head(3)["share_percent"].sum()
    top_ind = ind_valid.iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("분석 연도", f"{latest_ind_year}년", "첫 일자리 산업 기준")
    with c2:
        kpi("상위 산업", f"{top_ind['industry']}", f"{top_ind['share_percent']:.1f}%")
    with c3:
        kpi("상위 3개 집중도", f"{top3_share:.1f}%", "파생 지표")

    callout("첫 일자리 산업 분포는 청년들이 실제로 노동시장에 처음 들어갈 때 어느 산업으로 연결되는지 보여준다. 이는 청년의 희망 산업을 직접 측정한 자료는 아니며, 실제 첫 취업 진입 구조를 확인하는 자료로 해석한다.")
    fig = horizontal_bar(ind_valid.sort_values("share_percent", ascending=True), "share_percent", "industry", f"{latest_ind_year}년 첫 일자리 산업 분포", "비중(%)", "산업", color=BLUE, height=560)
    st.plotly_chart(fig, use_container_width=True)

    section("파생 지표: 첫 일자리 산업 집중도", "상위 산업에 첫 일자리가 얼마나 몰려 있는지 보기 위해 상위 3개 산업 비중을 더했다.")
    top_table = ind_valid.head(5)[["industry", "first_job_industry_thousand", "share_percent"]].copy()
    top_table["rank"] = range(1, len(top_table) + 1)
    top_table = top_table[["rank", "industry", "first_job_industry_thousand", "share_percent"]]
    st.dataframe(kr_df(top_table), use_container_width=True, hide_index=True)
    good(
        f"{latest_ind_year}년 기준 첫 일자리 상위 3개 산업 비중은 {top3_share:.1f}%다. "
        "첫 취업이 일부 산업에 집중되어 있다면, 첫 취업 지연은 개인의 준비 기간뿐 아니라 실제 진입 가능한 산업 구조와도 함께 봐야 한다."
    )
    caution("이 자료는 첫 일자리 산업 분포다. ‘기업이 청년을 얼마나 채용했는가’가 아니라, 청년 취업 유경험자의 첫 일자리가 어느 산업에 분포했는지를 보여준다.")

elif page == "6. 지역별 진입 여건은 다른가":
    hero(
        "6. 지역별 진입 여건은 다른가?",
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
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("전국 청년 고용률", f"{national_emp:.1f}%" if national_emp is not None else "-", f"{selected_year}년 기준")
    with c2:
        best = reg.iloc[0]
        kpi("고용률 최고 지역", f"{best['region_short']}", f"{best['regional_employment_rate']:.1f}%")
    with c3:
        low = reg.iloc[-1]
        kpi("고용률 최저 지역", f"{low['region_short']}", f"{low['regional_employment_rate']:.1f}%")
    callout("전체 지역을 모두 사용하되, 해석에서는 상위 5개와 하위 5개를 강조한다. 전국 평균 뒤에 가려지는 지역별 차이를 보기 위한 보조 분석이다.")
    fig = px.bar(reg.sort_values("regional_employment_rate"), x="regional_employment_rate", y="region_short", orientation="h", title=f"{selected_year}년 시도별 청년 고용률", labels={"regional_employment_rate": "청년 고용률(%)", "region_short": "시도"}, template=TEMPLATE)
    fig.update_traces(marker_color=BLUE)
    if national_emp is not None:
        fig.add_vline(x=national_emp, line_dash="dash", line_color=ORANGE, annotation_text="전국", annotation_position="top")
    fig = style_fig(fig, 560)
    st.plotly_chart(fig, use_container_width=True)

    top_emp = reg.head(5)[["region_short", "regional_employment_rate"]].reset_index(drop=True)
    low_emp = reg.tail(5).sort_values("regional_employment_rate")[["region_short", "regional_employment_rate"]].reset_index(drop=True)
    both = pd.concat([
        top_emp.rename(columns={"region_short": "고용률 상위 지역", "regional_employment_rate": "상위 고용률(%)"}),
        low_emp.rename(columns={"region_short": "고용률 하위 지역", "regional_employment_rate": "하위 고용률(%)"}),
    ], axis=1)
    st.dataframe(both, use_container_width=True, hide_index=True)

    reg_unemp = region[region["year"] == selected_year].dropna(subset=["regional_unemployment_rate"]).sort_values("regional_unemployment_rate", ascending=False)
    fig = px.bar(reg_unemp.sort_values("regional_unemployment_rate"), x="regional_unemployment_rate", y="region_short", orientation="h", title=f"{selected_year}년 시도별 청년 실업률", labels={"regional_unemployment_rate": "청년 실업률(%)", "region_short": "시도"}, template=TEMPLATE)
    fig.update_traces(marker_color=ROSE)
    if national_unemp is not None:
        fig.add_vline(x=national_unemp, line_dash="dash", line_color=ORANGE, annotation_text="전국", annotation_position="top")
    fig = style_fig(fig, 560)
    st.plotly_chart(fig, use_container_width=True)

    pivot = region.pivot(index="region_short", columns="year", values="regional_employment_rate")
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Viridis", title="시도별 청년 고용률 heatmap", labels=dict(color="고용률(%)"))
    fig = style_fig(fig, 650)
    st.plotly_chart(fig, use_container_width=True)
    caution("세종특별자치시는 일부 초기 연도 자료가 제공되지 않아 공백으로 표시될 수 있다. 지역별 고용률만으로 특정 지역의 취업난을 단정하지 않고, 산업 구조와 인구 이동을 함께 고려해야 한다.")

elif page == "종합 결론과 대책":
    hero(
        "결론: 첫 취업 지연은 여러 단계에서 나타난다",
        "분석 결과를 청년 개인의 어려움으로만 보지 않고, 정부·기업·대학·지역이 왜 이 문제를 봐야 하는지까지 연결했다.",
        eyebrow="CONCLUSION · ACTION PLAN",
    )
    good(
        "이 대시보드는 청년 취업난 전체의 모든 원인을 입증한 연구가 아니다. 대신 공개 통계로 확인 가능한 범위에서, "
        "첫 취업 지연이 <b>진입 속도·준비 방향·실업률 밖 청년·고용 안정성·첫 일자리 산업 구조·지역 여건</b>에서 어떻게 나타나는지 정리했다."
    )
    section("핵심 결론", "데이터에서 확인한 흐름을 무리하게 원인으로 단정하지 않고, 첫 취업 지연의 징후로 정리했다.")
    conclusions = pd.DataFrame({
        "확인한 흐름": [
            "고용률만으로 청년 고용 상황을 단정하기 어렵다",
            "첫 취업까지 1년 이상 걸리는 집단이 존재한다",
            "취업시험 준비자는 특정 분야를 목표로 준비 상태에 머문다",
            "공식 실업률 밖에 쉬었음 청년 규모가 존재한다",
            "첫 취업 이후에도 비정규직 비율이 높게 나타난다",
            "첫 일자리는 일부 산업에 집중되는 경향이 있다",
            "지역별 청년 고용률 차이가 존재한다",
        ],
        "해석": [
            "청년 인구와 취업자 수 변화를 함께 봐야 한다",
            "첫 취업 지연은 단순 체감이 아니라 통계로 확인되는 흐름이다",
            "취업 전 대기 상태의 방향까지 같이 봐야 한다",
            "실업률만으로 노동시장 밖 청년을 설명하기 어렵다",
            "취업 성공 이후의 안착 문제도 함께 고려해야 한다",
            "첫 취업은 실제 진입 가능한 산업 구조와 연결된다",
            "전국 평균만으로 지역별 진입 여건을 설명하기 어렵다",
        ],
    })
    st.dataframe(conclusions, use_container_width=True, hide_index=True)

    section("데이터 결과와 대응 방향", "대책은 ‘청년을 도와야 한다’가 아니라, 노동시장 진입 경로를 개선하는 방향으로 정리했다.")
    policy = pd.DataFrame({
        "분석에서 확인한 문제": [
            "첫 취업까지 시간이 오래 걸림",
            "취업시험 준비 상태에 머무는 청년 존재",
            "쉬었음 청년 규모 존재",
            "비정규직 비율 상승",
            "첫 일자리 산업 집중",
            "지역별 고용률 차이",
        ],
        "제3자 관점의 의미": [
            "노동시장 진입이 늦어져 기업의 초기 인재 확보와 정부 고용정책 부담으로 연결될 수 있음",
            "청년의 준비 방향이 특정 분야에 쏠리면 민간 일자리 진입이 늦어질 수 있음",
            "인적자원이 경제활동으로 연결되지 못하는 비활용 문제가 생길 수 있음",
            "기업 입장에서는 숙련 축적과 장기 인력 확보가 어려워질 수 있음",
            "청년 첫 진입 경로가 일부 산업에 몰리면 산업별 미스매치가 커질 수 있음",
            "지역 청년 유출과 지역 기업 인력 확보 문제로 이어질 수 있음",
        ],
        "대응 방향": [
            "첫 일자리 매칭 강화, 직무 연계형 인턴십 확대",
            "준비 분야별 진로 전환 지원, 민간 채용 연계 프로그램 강화",
            "노동시장 재진입 상담, 직업훈련, 심리·진로 복합 지원",
            "청년 비정규직 장기근속 유도, 정규직 전환 인센티브",
            "첫 일자리 산업 다변화, 성장 산업 직무교육 확대",
            "지역 산업 구조에 맞는 일자리 매칭과 지방 정착 지원",
        ],
    })
    st.dataframe(policy, use_container_width=True, hide_index=True)
    callout("최종 정리: 청년 첫 취업 지연은 개인의 노력 부족으로만 설명하기 어렵다. 공개 통계로 확인되는 흐름만 보더라도, 준비 상태의 장기화, 실업률 밖 청년, 고용 안정성, 첫 일자리 산업 구조, 지역별 여건 차이가 함께 나타난다.")
    caution("본 프로젝트는 탐색적 데이터 분석이다. 경기 상황, AI, 기업 채용 방식, 정치·제도 변화 같은 외부 요인은 직접 검증하지 않았으며, 후속 분석에서 보완할 수 있다.")
