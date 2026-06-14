from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="청년 취업난 구조 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data" / "processed"

# -----------------------------------------------------------------------------
# Design: clean editorial analytics dashboard
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {font-family: 'Inter', 'Noto Sans KR', system-ui, sans-serif;}
.stApp {background: #F5F7FB; color:#111827;}
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px;}
section[data-testid="stSidebar"] {background: #0F172A;}
section[data-testid="stSidebar"] * {color: #E5E7EB !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label {background: rgba(255,255,255,.06); border-radius: 12px; padding: 6px 8px; margin-bottom: 4px;}
.sidebar-source {background: rgba(255,255,255,.08); border:1px solid rgba(148,163,184,.28); border-radius:16px; padding:14px 14px; margin-top: 10px;}
.sidebar-source .source-title {font-size:.78rem; font-weight:800; color:#93C5FD !important; letter-spacing:.04em; margin-bottom:8px;}
.sidebar-source .source-line {font-size:.86rem; line-height:1.65; color:#F8FAFC !important;}
.sidebar-note {font-size:.76rem; line-height:1.55; color:#CBD5E1 !important; margin-top:10px;}

.hero {
    background: radial-gradient(circle at 10% 10%, rgba(37,99,235,.32), transparent 22%),
                linear-gradient(135deg, #0B1120 0%, #16213E 52%, #1E3A8A 100%);
    color: white; border-radius: 28px; padding: 34px 38px; margin-bottom: 22px;
    box-shadow: 0 24px 60px rgba(15,23,42,.18);
}
.hero .eyebrow {font-size: .86rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #93C5FD; margin-bottom: 10px;}
.hero h1 {font-size: 2.35rem; line-height: 1.18; margin: 0 0 12px 0; letter-spacing: -0.035em; font-weight: 850;}
.hero p {font-size: 1.03rem; color: rgba(255,255,255,.86); line-height: 1.72; margin: 0; max-width: 920px;}

.section-title {font-size: 1.45rem; font-weight: 800; letter-spacing: -0.025em; color: #0F172A; margin: 24px 0 10px;}
.section-sub {font-size: .98rem; color:#64748B; line-height:1.65; margin-bottom: 14px;}

.card {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 22px; padding: 20px 22px;
    box-shadow: 0 12px 30px rgba(15,23,42,.06); margin-bottom: 16px;
}
.kpi {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 20px; padding: 18px 18px 16px;
    box-shadow: 0 10px 26px rgba(15,23,42,.055); min-height: 118px;
}
.kpi .label {font-size:.82rem; color:#64748B; font-weight:700; margin-bottom: 8px;}
.kpi .value {font-size:1.9rem; font-weight:850; letter-spacing:-0.04em; color:#0F172A;}
.kpi .note {font-size:.82rem; color:#64748B; margin-top: 8px; line-height:1.45;}

.story-card {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 20px; padding: 18px 18px;
    box-shadow: 0 10px 26px rgba(15,23,42,.045); height: 100%;
}
.story-card .num {display:inline-flex; width:30px; height:30px; align-items:center; justify-content:center; border-radius:10px; background:#DBEAFE; color:#1D4ED8; font-weight:800; margin-bottom:12px;}
.story-card h4 {margin: 0 0 8px; font-size: 1.03rem; color:#111827; font-weight:800;}
.story-card p {margin:0; font-size:.9rem; line-height:1.6; color:#475569;}

.callout {background:#EFF6FF; color:#1E3A8A; border:1px solid #BFDBFE; border-left:6px solid #2563EB; padding:15px 17px; border-radius:15px; line-height:1.65; margin: 12px 0 18px;}
.caution {background:#FFF7ED; color:#9A3412; border:1px solid #FED7AA; border-left:6px solid #F97316; padding:15px 17px; border-radius:15px; line-height:1.65; margin: 12px 0 18px;}
.good {background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; border-left:6px solid #10B981; padding:15px 17px; border-radius:15px; line-height:1.65; margin: 12px 0 18px;}

.badge {display:inline-block; background:#EEF2FF; color:#3730A3; border-radius:999px; padding:6px 10px; font-weight:700; font-size:.78rem; margin:4px 5px 4px 0;}

[data-testid="stDataFrame"] {border-radius: 18px; overflow: hidden;}
h1, h2, h3 {letter-spacing: -0.028em;}
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
        "vuln": pd.read_csv(DATA_DIR / "vulnerability.csv"),
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
vuln = data["vuln"]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
BLUE = "#2563EB"
NAVY = "#0F172A"
SKY = "#38BDF8"
ORANGE = "#F97316"
RED = "#EF4444"
GREEN = "#10B981"
PURPLE = "#7C3AED"
GRAY = "#64748B"
YELLOW = "#EAB308"

COLORWAY = [BLUE, ORANGE, GREEN, PURPLE, RED, SKY, YELLOW, GRAY]
TEMPLATE = "plotly_white"

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
    "youth_employment_vulnerability_index": "청년 고용 취약성 지수(0~100)",
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
        fillcolor="#FDE68A", opacity=0.18,
        layer="below", line_width=0,
        annotation_text="2020~2021 코로나 충격기",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#92400E"),
    )
    fig.add_vline(x=2022, line_dash="dot", line_color="#94A3B8", opacity=0.85)
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
        title=dict(text=title, font=dict(size=19, color=NAVY)),
        height=height,
        margin=dict(l=30, r=25, t=65, b=35),
        xaxis_title="연도",
        yaxis_title=y_title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
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
        title=dict(text=title, font=dict(size=19, color=NAVY)),
        height=height,
        margin=dict(l=30, r=35, t=65, b=35),
        xaxis_title="연도",
        yaxis=dict(title=left_title, showgrid=True, gridcolor="#E5E7EB"),
        yaxis2=dict(title=right_title, overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
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
latest_vuln = latest(vuln)
latest_region_year = int(region["year"].max())
latest_region = region[region["year"] == latest_region_year].copy()

# -----------------------------------------------------------------------------
# Navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📊 청년 취업난 구조 분석")
st.sidebar.caption("스토리형 데이터 대시보드")
page = st.sidebar.radio(
    "페이지",
    [
        "프로젝트 개요",
        "1. 첫 취업까지 오래 걸리는가",
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
    <div class="sidebar-note">※ 본 분석은 인과관계 입증이 아니라 청년 취업난 관련 지표의 흐름을 확인하는 탐색적 분석입니다.</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "프로젝트 개요":
    hero(
        "청년들은 왜 취업이 어렵다고 느낄까?",
        "청년 취업난을 하나의 실업률로 설명하지 않고, 첫 취업 지연·취업 준비 장기화·쉬었음 청년·불안정 고용·임금과 산업 구조로 나누어 분석한다.",
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi("청년 고용률", f"{latest_emp['employment_rate']:.1f}%", "비율 지표: 인구·취업자 수와 함께 해석")
    with c2:
        kpi("첫 취업 소요", f"{latest_first['avg_first_job_months']:.1f}개월", "졸업·중퇴 취업유경험자")
    with c3:
        kpi("취업시험 준비", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동인구 중 비율")
    with c4:
        kpi("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%", "비경제활동인구 중 비율")
    with c5:
        kpi("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", "청년 임금근로자 기준")

    section("데이터 출처와 분석 기간", "각 지표가 어떤 통계에서 왔는지 명확히 구분해 분석 신뢰도를 높였다.")
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
    callout("시계열 그래프에는 2015~2019년을 코로나 이전, 2020~2021년을 코로나 충격기, 2022년 이후를 회복기 이후로 구분하는 기준선을 표시했다. 이 구분은 인과효과를 증명하기 위한 것이 아니라 시기별 흐름을 비교하기 위한 참고 장치다.")

    section("고용률만으로는 충분하지 않은 이유", "고용률은 비율 지표이므로 청년 인구와 취업자 수 흐름을 함께 봐야 한다.")
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
        "따라서 고용률만 보고 청년 고용 상황이 개선되었다고 단정하지 않고, 인구 감소와 취업자 수 변화를 함께 해석한다."
    )

    section("분석 흐름", "청년 취업난을 질문형 흐름으로 나누어 살펴본다.")
    items = [
        (1, "첫 취업까지 오래 걸리는가", "첫 취업 평균소요기간과 1년 이상 소요 비중으로 노동시장 진입 지연을 본다."),
        (2, "취업 준비 상태에 오래 머무르는가", "취업시험 준비자 수와 비율로 취업 전 대기·준비 상태를 확인한다."),
        (3, "실업률 밖 청년이 있는가", "쉬었음 청년과 쉬었음 비중으로 공식 실업률의 한계를 보완한다."),
        (4, "취업해도 안정적인가", "정규직·비정규직 규모와 비정규직 비율로 고용 안정성을 본다."),
        (5, "임금·산업 격차가 있는가", "산업별 청년 근로자 수와 임금을 함께 비교해 일자리 구조를 본다."),
        (6, "지역별 차이가 있는가", "시도별 청년 고용률과 실업률로 전국 평균 뒤의 지역별 차이를 보조적으로 확인한다."),
    ]
    for start in range(0, len(items), 3):
        cols = st.columns(3)
        for col, item in zip(cols, items[start:start+3]):
            with col:
                story_card(*item)

elif page == "1. 첫 취업까지 오래 걸리는가":
    hero(
        "1. 청년들이 첫 취업까지 오래 걸리는가?",
        "취업난의 가장 직접적인 근거는 ‘취업까지 걸리는 시간’이다. 첫 취업 평균소요기간과 1년 이상 소요 비중을 함께 본다.",
        eyebrow="PART 1 · ENTRY DELAY",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("최근 첫 취업 평균소요기간", f"{latest_first['avg_first_job_months']:.1f}개월", "평균 기준")
    with c2:
        kpi("1년 이상 소요 비중", f"{latest_first['first_job_over_1y_share']:.1f}%", "장기 소요 집단")
    with c3:
        base = first.loc[first["year"] == first["year"].min()].iloc[0]
        kpi("1년 이상 비중 변화", f"+{latest_first['first_job_over_1y_share'] - base['first_job_over_1y_share']:.1f}%p", "2015년 대비")

    callout("첫 취업 소요기간은 청년들이 노동시장에 진입하기 전 단계에서 겪는 시간을 보여준다. 평균만 보면 분포를 놓칠 수 있으므로, 1년 이상 소요 비중을 함께 확인한다.")
    caution("취약성 지수의 첫 취업 항목은 평균소요기간만 쓰지 않고, 평균소요기간과 1년 이상 소요 비중을 함께 반영하도록 수정했다.")

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

    good("해석: 이 파트는 ‘취업난’을 가장 직접적으로 설명한다. 청년들이 첫 일자리에 진입하는 데 걸리는 시간이 길다면, 취업난은 단순한 실업률 문제가 아니라 진입 지연 문제로 볼 수 있다.")

elif page == "2. 취업 준비 상태에 머무르는가":
    hero(
        "2. 청년들이 취업 준비 상태에 오래 머무르는가?",
        "취업시험 준비자는 노동시장에 바로 진입하지 못하고 준비 상태에 머무는 청년층을 보여준다.",
        eyebrow="PART 2 · PREPARATION BOTTLENECK",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("취업시험 준비자", f"{latest_exam['exam_prep_thousand']:,.0f}천 명", "최근 연도")
    with c2:
        kpi("준비자 비율", f"{latest_exam['exam_prep_ratio']:.1f}%", "비경제활동인구 중")
    with c3:
        peak = exam.loc[exam["exam_prep_ratio"].idxmax()]
        kpi("비율 최고 연도", f"{int(peak['year'])}년", f"{peak['exam_prep_ratio']:.1f}%")

    callout("취업시험 준비자 지표는 청년층의 ‘취업 전 대기 상태’를 보여준다. 첫 취업 소요기간과 함께 보면 노동시장 진입 지연을 더 직접적으로 설명할 수 있다.")

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

    caution("주의: 취업시험 준비자를 ‘취업 실패자’로 단정하면 안 된다. 다만 취업 전 준비 상태에 머무는 청년층을 보여주는 지표로는 의미가 있다. 준비 여부 도넛 차트는 동일 정보를 반복하므로 제거하고, 수와 비율의 시계열을 함께 보여주는 방식으로 정리했다.")

elif page == "3. 실업률 밖 쉬었음 청년":
    hero(
        "3. 실업률에 안 잡히는 쉬었음 청년이 있는가?",
        "실업률은 구직활동을 하는 사람만 반영한다. 쉬었음 청년은 실업률 밖의 노동시장 이탈 가능성을 보완적으로 보여준다.",
        eyebrow="PART 3 · OUTSIDE OFFICIAL UNEMPLOYMENT",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("쉬었음 청년", f"{latest_rest['resting_thousand']:,.0f}천 명", "최근 연도")
    with c2:
        kpi("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%", "비경제활동인구 중")
    with c3:
        kpi("공식 실업률", f"{latest_emp['unemployment_rate']:.1f}%", "비교 기준")

    callout("이 파트의 핵심은 ‘실업률이 낮아도 현실의 어려움이 사라졌다고 볼 수 있는가?’이다. 쉬었음 청년은 실업률에 포착되지 않는 청년층을 보여주는 보조 지표다.")

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

    caution("쉬었음 청년을 모두 구직 포기자로 볼 수는 없다. 건강, 휴식, 개인 사정 등이 포함될 수 있으므로 ‘노동시장 이탈 가능성’으로 조심스럽게 표현한다. 단독 추이보다 실업자 수와 함께 보면 ‘실업률 밖 청년’이라는 분석 의도가 더 명확해진다.")

elif page == "4. 취업해도 안정적인가":
    hero(
        "4. 취업해도 비정규직 비율이 높은가?",
        "취업률만으로는 일자리의 질을 알 수 없다. 정규직·비정규직 규모와 비율로 청년 고용 안정성을 확인한다.",
        eyebrow="PART 4 · JOB STABILITY",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", "청년 임금근로자 기준")
    with c2:
        kpi("정규직 비율", f"{latest_nr['regular_ratio']:.1f}%", "청년 임금근로자 기준")
    with c3:
        kpi("비정규직 규모", f"{latest_nr['nonregular_thousand']:,.0f}천 명", "최근 연도")

    callout("고용률은 ‘취업했는가’를 보여주지만, 청년들이 체감하는 취업난은 ‘안정적인 일자리인가’와도 관련된다. 그래서 비정규직 비율을 고용 안정성 지표로 본다.")

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

    caution("비정규직이 항상 나쁜 일자리라고 단정할 수는 없다. 이 분석에서는 비정규직 비율을 고용 안정성의 참고 지표로 사용한다.")
    caution("정규직 수와 비정규직 수는 천 명 단위 반올림 자료이므로, 세부 항목 합계가 임금근로자 전체와 1천 명 안팎으로 차이 날 수 있다.")

elif page == "5. 임금과 산업별 격차":
    hero(
        "5. 취업 후 임금과 산업별 격차가 있는가?",
        "청년이 취업한 산업과 그 산업의 임금 수준을 함께 보면, 일자리의 양과 보상을 동시에 확인할 수 있다.",
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

    callout("임금 자료는 ‘임금이 낮아졌다’는 근거가 아니라 취업 후 보상 수준을 확인하는 자료다. 특히 산업별 근로자 수와 임금을 함께 보면, 청년이 많이 일하는 산업이 반드시 높은 보상을 제공하는지 확인할 수 있다.")

    st.plotly_chart(
        line_chart(wage, ["monthly_wage_total_thousand", "monthly_salary_thousand"], "29세 이하 청년층 월임금 추이", "천 원", {"monthly_wage_total_thousand": "월임금총액", "monthly_salary_thousand": "월급여액"}),
        use_container_width=True,
    )
    caution("2020년 시간당임금총액은 코로나19 시기 근로시간 변화와 조사 구조의 영향을 받을 수 있다. 따라서 이 페이지의 임금 해석은 월임금총액을 중심으로 하고, 시간당임금은 보조 지표로만 본다.")

    section("산업별 청년 근로자 수 × 월임금 사분면", "근로자 수가 많은 산업이 좋은 보상을 제공하는지 한 번에 확인한다.")
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

    caution("임금은 명목임금 기준이다. 물가·주거비를 반영한 실질 구매력 분석은 후속 과제로 남기는 것이 안전하다.")

elif page == "6. 지역별 청년 고용률 격차":
    hero(
        "6. 청년 취업난은 지역마다 다를까?",
        "전국 평균만 보면 지역별 차이가 가려질 수 있다. 시도별 청년 고용률과 실업률을 비교해 지역별 노동시장 여건 차이를 보조적으로 확인한다.",
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

    callout("지역별 자료는 전국 단위 분석을 보완하기 위한 보조 분석이다. 고용률은 지역 청년 인구 중 취업자 비율을 보여주므로, 지역별 청년 고용 상황을 비교하는 데 비교적 직관적인 지표다.")

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
        section("고용률 상위·하위 지역", "전체 지역을 모두 사용하되, 해석에서는 상위 5개와 하위 5개를 강조한다.")
        t1 = top_emp[["region_short", "regional_employment_rate"]].rename(
            columns={"region_short": "고용률 상위 지역", "regional_employment_rate": "상위 고용률(%)"}
        ).reset_index(drop=True)
        t2 = low_emp[["region_short", "regional_employment_rate"]].rename(
            columns={"region_short": "고용률 하위 지역", "regional_employment_rate": "하위 고용률(%)"}
        ).reset_index(drop=True)
        both = pd.concat([t1, t2], axis=1)
        st.dataframe(both, use_container_width=True, hide_index=True)
    with col2:
        section("실업률 보조 확인", "지역별 실업률은 변동성이 클 수 있으므로 고용률을 중심으로 해석하고 실업률은 참고 지표로 사용한다. 세종특별자치시는 2015~2016년 실업률 값이 없어 해당 연도에서는 공백 또는 제외로 표시된다.")
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
    section("지역별 고용률 흐름", "연도별 변화까지 보면 특정 연도만의 우연한 순위보다 지역별 흐름을 더 안정적으로 볼 수 있다.")
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

    caution("지역별 고용률만으로 특정 지역의 취업난을 단정할 수는 없다. 산업 구조, 인구 이동, 대학·기업 분포 등 추가 요인이 존재하므로 이 페이지는 전국 평균의 한계를 보완하는 참고 분석으로 해석한다.")

elif page == "종합 결론과 대책":
    hero(
        "종합 결론과 대책",
        "분석 결과를 한 문장으로 묶고, 각 취약 지표와 대응책을 1:1로 연결한다.",
        eyebrow="CONCLUSION · ACTIONABLE INSIGHTS",
    )

    section("종합 결론")
    good("청년 취업난은 실업률 하나만으로 설명하기 어렵다. 첫 취업 소요기간, 취업시험 준비자, 쉬었음 청년, 비정규직 비율, 산업별 임금 격차와 지역별 고용률 차이를 함께 보면 청년 취업난은 <b>취업 전 진입 지연·실업률 밖 청년·고용 안정성 부족·산업별 보상 격차·지역별 고용 여건 차이</b>가 결합된 구조적 문제로 볼 수 있다.")

    section("청년 고용 취약성 지수", "공식 지표가 아니라 여러 지표의 흐름을 한눈에 보기 위한 탐색적 요약 지표다. 첫 취업 항목은 평균소요기간과 1년 이상 소요 비중을 함께 반영했다.")
    st.markdown(
        """
        <div class="card">
        <b>지수 산출 방식</b><br><br>
        각 지표를 0~1 범위로 <b>min-max 정규화</b>한 뒤 취약성이 커지는 방향으로 맞추고, 동일 가중 평균했다.<br>
        <span style="color:#475569;">정규화값 = (x - 최솟값) / (최댓값 - 최솟값)</span><br><br>
        고용률 취약도 = 1 - 정규화(고용률)<br>
        첫 취업 지연 취약도 = [정규화(첫 취업 평균소요기간) + 정규화(1년 이상 소요 비중)] / 2<br>
        취업시험 준비 취약도 = 정규화(취업시험 준비자 비율)<br>
        쉬었음 취약도 = 정규화(쉬었음 비중)<br>
        비정규직 취약도 = 정규화(비정규직 비율)<br>
        임금 취약도 = 1 - 정규화(월임금총액)<br><br>
        <b>청년 고용 취약성 지수 = 각 취약도 지표의 동일 가중 평균 × 100</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    caution("이 지수는 공식 통계가 아니라 여러 지표의 상대적 흐름을 한눈에 보기 위한 탐색적 지표이다. 가중치는 동일 가중을 사용했으며, 정책 판단의 직접 근거가 아니라 보조 해석 도구로 사용한다.")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = line_chart(vuln, ["youth_employment_vulnerability_index"], "청년 고용 취약성 지수 추이", "0~100", {"youth_employment_vulnerability_index": "취약성 지수"}, height=430)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        kpi("최근 취약성 지수", f"{latest_vuln['youth_employment_vulnerability_index']:.1f}", "공식 통계 아님")
        peak = vuln.loc[vuln["youth_employment_vulnerability_index"].idxmax()]
        kpi("최고점", f"{int(peak['year'])}년", f"{peak['youth_employment_vulnerability_index']:.1f}")

    caution("취약성 지수는 정책 판단의 직접 근거가 아니라 보조 지표다. 지수보다 중요한 것은 각 구성요소가 어떤 문제를 보여주는지다. 특히 첫 취업 항목은 평균소요기간과 1년 이상 장기 소요 비중을 함께 반영해 본문 설명과 계산 방식이 일치하도록 했다.")

    section("지표 간 동행 흐름", "각 지표가 서로 어떤 방향으로 함께 움직였는지 참고용 상관관계로 확인한다.")
    corr_cols = {
        "employment_rate": "고용률",
        "avg_first_job_months": "첫 취업 평균소요기간",
        "first_job_over_1y_share": "1년 이상 소요 비중",
        "exam_prep_ratio": "취업시험 준비자 비율",
        "resting_share_in_inactive": "쉬었음 비중",
        "nonregular_ratio": "비정규직 비율",
        "monthly_wage_total_thousand": "월임금총액",
    }
    corr_df = vuln[["year", *corr_cols.keys()]].dropna().rename(columns=corr_cols).drop(columns=["year"])
    corr = corr_df.corr(numeric_only=True)
    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        zmin=-1, zmax=1,
        color_continuous_scale="RdBu_r",
        title="주요 지표 상관관계 heatmap",
        labels=dict(color="상관계수"),
    )
    fig_corr.update_layout(height=640, margin=dict(l=30, r=25, t=65, b=35))
    st.plotly_chart(fig_corr, use_container_width=True)
    caution("상관관계는 2015~2025년의 제한된 연도 수를 바탕으로 한 보조 분석이다. 통계적 인과관계나 유의성을 입증하는 것이 아니라 지표 간 동행 흐름을 참고하기 위한 시각화로 해석한다.")

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
            "취업난은 취업 이전 단계에서 이미 시작될 수 있습니다.",
            "준비 상태의 장기화는 노동시장 진입 지연을 보여줍니다.",
            "실업률 밖의 청년층도 함께 봐야 현실을 더 넓게 설명할 수 있습니다.",
            "취업 여부보다 안정적인 일자리인지가 중요합니다.",
            "청년이 많이 일하는 산업이 반드시 높은 보상을 제공하지는 않습니다.",
            "전국 평균만으로는 지역별 청년 고용 여건 차이를 설명하기 어렵습니다.",
            "명목임금 상승만으로 청년 생활 안정성을 단정할 수 없습니다.",
        ],
    })
    st.dataframe(policy, use_container_width=True, hide_index=True)

    callout("최종 정리: <b>본 프로젝트는 청년 취업난을 단순한 고용률 문제가 아니라, 청년 인구 감소 맥락 속의 취업자 수 변화·첫 취업 지연·취업 준비 장기화·실업률 밖 청년·불안정 고용·산업별 보상 격차·지역별 고용 여건 차이가 함께 나타나는 구조적 문제로 분석했다.</b>")
