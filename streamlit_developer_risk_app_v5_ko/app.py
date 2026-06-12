from pathlib import Path
from typing import Optional, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="AI 전후 개발자 고용 생존성 대시보드",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "stackoverflow_2021_2025_exactname_combined_tables_v2.xlsx"

GROUP_COLORS = {
    "위험군": "#EF4444",        # red
    "전환유력군": "#F59E0B",    # amber
    "안정군": "#10B981",        # green
    "정체군": "#6B7280",        # gray
}

PLOT_TEMPLATE = "plotly_white"

# =========================================================
# Korean display mapping
# =========================================================
DEVTYPE_KO = {
    "Developer, back-end": "백엔드 개발자",
    "Developer, front-end": "프론트엔드 개발자",
    "Developer, full-stack": "풀스택 개발자",
    "Developer, mobile": "모바일 개발자",
    "Developer, desktop or enterprise applications": "데스크톱/기업용 앱 개발자",
    "Developer, embedded applications or devices": "임베디드 개발자",
    "Developer, QA or test": "QA/테스트 개발자",
    "Developer, game or graphics": "게임/그래픽 개발자",
    "Developer, AI apps or physical AI": "AI 앱/피지컬 AI 개발자",
    "Data scientist or machine learning specialist": "데이터 과학자/머신러닝 전문가",
    "Data scientist": "데이터 과학자",
    "Data or business analyst": "데이터/비즈니스 분석가",
    "Data engineer": "데이터 엔지니어",
    "Engineer, data": "데이터 엔지니어",
    "DevOps specialist": "DevOps 전문가",
    "DevOps engineer or professional": "DevOps 엔지니어/전문가",
    "Cloud infrastructure engineer": "클라우드 인프라 엔지니어",
    "Engineer, site reliability": "사이트 신뢰성 엔지니어(SRE)",
    "System administrator": "시스템 관리자",
    "Support engineer or analyst": "지원 엔지니어/분석가",
    "Database administrator": "데이터베이스 관리자",
    "Database administrator or engineer": "데이터베이스 관리자/엔지니어",
    "Cybersecurity or InfoSec professional": "사이버보안/정보보호 전문가",
    "Security professional": "보안 전문가",
    "Engineering manager": "개발 관리자",
    "Project manager": "프로젝트 관리자",
    "Product manager": "프로덕트 매니저",
    "Senior Executive (C-Suite, VP, etc.)": "임원급 관리자",
    "Senior executive (C-suite, VP, etc.)": "임원급 관리자",
    "Architect, software or solutions": "소프트웨어/솔루션 아키텍트",
    "AI/ML engineer": "AI/ML 엔지니어",
    "Applied scientist": "응용 과학자",
    "Academic researcher": "학술 연구자",
    "Scientist": "과학자/연구원",
    "Designer": "디자이너",
    "Educator": "교육자",
    "Student": "학생/학습자",
    "Founder, technology or otherwise": "창업자",
    "Marketing or sales professional": "마케팅/영업 전문가",
    "Retired": "은퇴자",
    "Other (please specify):": "기타",
}

COLUMN_KO = {
    "DevType_Display": "개발자 직무",
    "DevType": "원문 직무명",
    "Name_Status": "직무명 매칭 상태",
    "Respondent_Count_2021": "2021년 응답자 수",
    "Respondent_Count_2025": "2025년 응답자 수",
    "Tech_2021_Top10_List": "2021년 사용 기술 Top10",
    "Tech_2025_Top10_List": "2025년 사용 기술 Top10",
    "Intersection_List": "공통 기술 목록",
    "Intersection_Count": "겹치는 기술 수",
    "Union_Count": "전체 기술 수",
    "Volatility": "기술 변동성",
    "Volatility_Rank": "변동성 순위",
    "Calculation_Status": "계산 상태",
    "Rank": "순위",
    "Median_Salary_USD_2021": "2021년 연봉 중앙값(USD)",
    "Median_Salary_USD_2025": "2025년 연봉 중앙값(USD)",
    "Regular_Ratio_2021": "2021년 정규직/고용 비율",
    "Regular_Ratio_2025": "2025년 정규직/고용 비율",
    "Salary_N_2021": "2021년 연봉 응답 수",
    "Salary_N_2025": "2025년 연봉 응답 수",
    "Salary_Score_2021": "2021년 연봉 점수",
    "Salary_Score_2025": "2025년 연봉 점수",
    "Regular_Score_2021": "2021년 고용 안정성 점수",
    "Regular_Score_2025": "2025년 고용 안정성 점수",
    "Economic_Stability_Score_2021": "2021년 경제 안정성 점수",
    "Economic_Stability_Score_2025": "2025년 경제 안정성 점수",
    "Regular_Definition_2021": "2021년 고용 기준",
    "Regular_Definition_2025": "2025년 고용 기준",
    "Volatility_Median": "변동성 중앙값",
    "Employment_Viability_2021": "2021년 고용 생존성",
    "Employment_Viability_2025": "2025년 고용 생존성",
    "Viability_2021_Median": "2021년 생존성 중앙값",
    "Viability_2025_Median": "2025년 생존성 중앙값",
    "Quadrant_Group_2021": "2021년 4사분면 분류",
    "Quadrant_Group_2025": "2025년 4사분면 분류",
    "Year": "연도",
    "Technology": "기술",
    "Count": "빈도",
}

STATUS_KO = {
    "Both exact-name match": "양쪽 연도 동일 직무명",
    "Only 2021": "2021년에만 존재",
    "Only 2025": "2025년에만 존재",
    "Calculated": "계산 완료",
    "Missing data": "데이터 부족",
}


def ko_devtype(value) -> str:
    if pd.isna(value):
        return "-"
    value = str(value)
    ko = DEVTYPE_KO.get(value, value)
    return f"{ko} ({value})" if ko != value else value


def add_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "DevType" in df.columns and "DevType_Display" not in df.columns:
        df.insert(0, "DevType_Display", df["DevType"].apply(ko_devtype))
    if "Name_Status" in df.columns:
        df["Name_Status_KO"] = df["Name_Status"].map(STATUS_KO).fillna(df["Name_Status"])
    if "Calculation_Status" in df.columns:
        df["Calculation_Status_KO"] = df["Calculation_Status"].map(STATUS_KO).fillna(df["Calculation_Status"])
    return df


def pretty_df(df: pd.DataFrame, columns: Optional[List[str]] = None, drop_original_devtype: bool = False) -> pd.DataFrame:
    out = df.copy()
    if columns is not None:
        out = out[[c for c in columns if c in out.columns]].copy()
    if drop_original_devtype and "DevType" in out.columns and "DevType_Display" in out.columns:
        out = out.drop(columns=["DevType"])
    return out.rename(columns={c: COLUMN_KO.get(c, c) for c in out.columns})

# =========================================================
# CSS: dashboard style
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
    }

    [data-testid="stSidebar"] {
        background: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.25rem 0;
    }

    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #0891B2 100%);
        padding: 2.0rem 2.2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 40px rgba(15,23,42,0.20);
    }
    .hero h1 {
        font-size: 2.0rem;
        line-height: 1.25;
        margin: 0 0 0.65rem 0;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    .hero p {
        font-size: 1.02rem;
        opacity: 0.92;
        margin: 0;
        max-width: 980px;
    }

    .page-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #0F172A;
        margin: 0.2rem 0 0.3rem 0;
    }
    .page-subtitle {
        color: #64748B;
        font-size: 0.98rem;
        margin-bottom: 1.2rem;
    }

    .kpi-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 1.05rem 1.1rem;
        box-shadow: 0 10px 28px rgba(15,23,42,0.06);
        min-height: 118px;
    }
    .kpi-label {
        color: #64748B;
        font-size: 0.86rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .kpi-note {
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }

    .info-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 8px 22px rgba(15,23,42,0.05);
        height: 100%;
    }
    .info-card h3 {
        color: #0F172A;
        font-size: 1.05rem;
        margin: 0 0 0.6rem 0;
        font-weight: 800;
    }
    .info-card p, .info-card li {
        color: #334155;
        font-size: 0.94rem;
        line-height: 1.62;
    }

    .badge {
        display: inline-block;
        background: #E0F2FE;
        color: #075985;
        border: 1px solid #BAE6FD;
        border-radius: 999px;
        padding: 0.33rem 0.62rem;
        margin: 0.18rem 0.15rem;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .badge-old {
        background: #EEF2FF;
        color: #3730A3;
        border-color: #C7D2FE;
    }
    .badge-new {
        background: #ECFDF5;
        color: #047857;
        border-color: #A7F3D0;
    }
    .warn-box {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        color: #9A3412;
        padding: 1rem 1.1rem;
        border-radius: 16px;
        line-height: 1.6;
    }
    .good-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 1rem 1.1rem;
        border-radius: 16px;
        line-height: 1.6;
    }
    .danger-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        color: #991B1B;
        padding: 1rem 1.1rem;
        border-radius: 16px;
        line-height: 1.6;
    }
    .muted {
        color: #64748B;
        font-size: 0.92rem;
    }
    hr {
        margin-top: 1.25rem;
        margin-bottom: 1.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Data utilities
# =========================================================
@st.cache_data(show_spinner="분석 데이터를 불러오는 중...")
def read_sheet(sheet_name: str) -> pd.DataFrame:
    if not DATA_FILE.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_FILE.name}")
        st.info("GitHub 저장소에서 app.py와 엑셀 파일이 같은 폴더에 있는지 확인하세요.")
        st.stop()
    return pd.read_excel(DATA_FILE, sheet_name=sheet_name, skiprows=3)


def numeric_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    keys = ["Count", "Ratio", "Score", "Salary", "Volatility", "Viability", "Rank", "Median", "N_"]
    for col in df.columns:
        if any(key in str(col) for key in keys):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner="대시보드 데이터 준비 중...")
def load_data():
    readme = read_sheet("00_README")
    table1 = read_sheet("01_Table1_Top10_2021_2025")
    vol = numeric_cleanup(read_sheet("02_Table2_Volatility"))
    salary = numeric_cleanup(read_sheet("03_Table3_Salary_Regular"))
    quad = numeric_cleanup(read_sheet("04_Table4_Quadrant_Input"))
    top5 = numeric_cleanup(read_sheet("05_Volatility_Top5"))
    tech21 = numeric_cleanup(read_sheet("06_TechCount_2021"))
    tech25 = numeric_cleanup(read_sheet("07_TechCount_2025"))
    table1 = add_display_columns(table1)
    vol = add_display_columns(vol)
    salary = add_display_columns(salary)
    quad = add_display_columns(quad)
    top5 = add_display_columns(top5)
    tech21 = add_display_columns(tech21)
    tech25 = add_display_columns(tech25)
    return readme, table1, vol, salary, quad, top5, tech21, tech25


def fmt_num(value: Optional[float], digits: int = 3, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}{suffix}"


def fmt_int(value: Optional[float]) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}"


def fmt_money(value: Optional[float]) -> str:
    if pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def fmt_pct(value: Optional[float]) -> str:
    if pd.isna(value):
        return "-"
    return f"{value*100:,.1f}%"


def filter_name_status(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if "Name_Status" not in df.columns:
        return df.copy()
    if mode == "양쪽 연도 모두 있는 직무만":
        return df[df["Name_Status"].eq("Both exact-name match")].copy()
    return df.copy()


def parse_tech_list(value) -> List[str]:
    if pd.isna(value):
        return []
    items = []
    seen = set()
    for raw in str(value).split(";"):
        t = raw.strip()
        if not t:
            continue
        # Normalize obvious accidental concatenation from Excel generation
        if t not in seen:
            seen.add(t)
            items.append(t)
    return items[:10]


def badges(items: List[str], klass: str = "") -> str:
    return "".join([f'<span class="badge {klass}">{x}</span>' for x in items]) or "<span class='muted'>데이터 없음</span>"


def kpi_card(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def make_quadrant_fig(q: pd.DataFrame, year: str):
    x_col = f"Employment_Viability_{year}"
    group_col = f"Quadrant_Group_{year}"
    plot_df = q.dropna(subset=["Volatility", x_col, group_col]).copy()
    plot_df["Group"] = plot_df[group_col]

    x_med = plot_df[x_col].median()
    y_med = plot_df["Volatility"].median()

    fig = px.scatter(
        plot_df,
        x=x_col,
        y="Volatility",
        color="Group",
        color_discrete_map=GROUP_COLORS,
        size=plot_df.get("Volatility", pd.Series([1]*len(plot_df))).abs() + 0.08,
        hover_name="DevType_Display" if "DevType_Display" in plot_df.columns else "DevType",
        hover_data={"Name_Status": True, "Volatility": ":.3f", x_col: ":.3f", "Group": True},
        template=PLOT_TEMPLATE,
        labels={x_col: "고용 생존성", "Volatility": "기술 스택 변동성"},
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.88), selector=dict(mode="markers"))
    fig.add_vline(x=x_med, line_dash="dash", line_color="#64748B", line_width=1.5)
    fig.add_hline(y=y_med, line_dash="dash", line_color="#64748B", line_width=1.5)

    # Quadrant labels
    x_max, x_min = plot_df[x_col].max(), plot_df[x_col].min()
    y_max, y_min = plot_df["Volatility"].max(), plot_df["Volatility"].min()
    x_pad = (x_max - x_min) * 0.06 if x_max != x_min else 0.05
    y_pad = (y_max - y_min) * 0.06 if y_max != y_min else 0.05

    labels = [
        (x_min + x_pad, y_max - y_pad, "위험군<br><span style='font-size:11px'>고변동·저생존성</span>", "#EF4444"),
        (x_max - x_pad, y_max - y_pad, "전환유력군<br><span style='font-size:11px'>고변동·고생존성</span>", "#F59E0B"),
        (x_max - x_pad, y_min + y_pad, "안정군<br><span style='font-size:11px'>저변동·고생존성</span>", "#10B981"),
        (x_min + x_pad, y_min + y_pad, "정체군<br><span style='font-size:11px'>저변동·저생존성</span>", "#6B7280"),
    ]
    for x, y, text, color in labels:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False, font=dict(size=13, color=color), align="center")

    fig.update_layout(
        height=660,
        margin=dict(l=20, r=20, t=35, b=20),
        legend_title_text="최종 그룹",
        plot_bgcolor="white",
    )
    return fig, plot_df


# =========================================================
# Load data
# =========================================================
readme, table1, vol, salary, quad, top5, tech21, tech25 = load_data()

# =========================================================
# Sidebar
# =========================================================
st.sidebar.markdown("### 🧭 AI 개발자 생존성")
st.sidebar.caption("2021 vs 2025 Stack Overflow 기반")

page = st.sidebar.radio(
    "화면 선택",
    [
        "🏠 개요",
        "⚡ 간단 요약",
        "🧩 표1 기술 Top10",
        "📈 표2 변동성 분석",
        "💼 표3 고용 지표",
        "🎯 표4 4사분면",
        "🏁 결론",
        "📋 원자료",
    ],
)

status_mode = st.sidebar.selectbox(
    "직무명 기준",
    ["양쪽 연도 모두 있는 직무만", "전체 직무 보기"],
    index=0,
    help="DevType 명칭이 2021년과 2025년에 정확히 일치하는 직무만 볼지 선택합니다.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**데이터 기준**")
st.sidebar.caption("• Stack Overflow Developer Survey 2021·2025")
st.sidebar.caption("• LanguageHaveWorkedWith 기준 Top10")
st.sidebar.caption("• 향후 희망 기술은 제외")
st.sidebar.caption("• DevType 명칭이 다르면 별도 직무로 유지")

both_quad = filter_name_status(quad, status_mode)
both_vol = filter_name_status(vol, status_mode)
both_salary = filter_name_status(salary, status_mode)
both_table1 = filter_name_status(table1, status_mode)

calc_quad = both_quad[both_quad["Calculation_Status"].eq("Calculated")].copy()
calc_vol = both_vol.dropna(subset=["Volatility"]).copy()

# =========================================================
# Page: Overview
# =========================================================
if page == "🏠 개요":
    st.markdown(
        """
        <div class="hero">
            <h1>생성형 AI 전후 개발자 직종별<br/>고용 생존성 분석</h1>
            <p>2021년과 2025년 Stack Overflow Developer Survey를 비교해, 개발자 직무별 기술 스택 변동성과 경제적 생존성을 정량화한 대시보드입니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("분석 가능 직무 수", f"{len(calc_quad):,}개", "2021·2025 exact DevType 기준")
    with c2:
        kpi_card("평균 변동성", fmt_num(calc_quad["Volatility"].mean(), 3), "Jaccard distance")
    with c3:
        kpi_card("2025 평균 생존성", fmt_num(calc_quad["Employment_Viability_2025"].mean(), 3), "연봉·고용비율/변동성")
    with c4:
        kpi_card("2025 평균 연봉", fmt_money(both_salary["Median_Salary_USD_2025"].mean()), "직무별 중앙값 평균")

    st.markdown("---")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(
            """
            <div class="info-card">
                <h3>분석 주제</h3>
                <p><b>생성형 AI 패러다임(2022년) 전후 데이터의 스택 변동성을 기반으로 한 개발자 직종별 고용 생존성 판별</b></p>
                <p>기술 스택이 급격히 바뀌는 직무가 실제로 고용 생존성 측면에서도 취약한지 확인하기 위해, 기술 변동성·연봉·정규직/고용 비율을 하나의 분석 흐름으로 연결했습니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="info-card">
                <h3>핵심 질문</h3>
                <ul>
                    <li>2021년과 2025년 사이 직무별 사용 기술은 얼마나 바뀌었는가?</li>
                    <li>기술 변동성이 높은 직무는 고용 생존성이 낮은가?</li>
                    <li>어떤 직무가 위험군·전환유력군·안정군·정체군으로 나뉘는가?</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 분석 흐름")
    flow = pd.DataFrame(
        {
            "단계": ["표1", "표2", "표3", "표4"],
            "역할": ["기술 스택 추출", "변동성 정량화", "고용 지표 산출", "4사분면 판별"],
            "설명": [
                "2021년·2025년 DevType별 사용 기술 Top10 추출",
                "Top10 기술의 교집합과 합집합으로 Volatility 계산",
                "연봉 중앙값과 정규직/고용 비율을 0~1 점수화",
                "Volatility와 Employment Viability를 결합해 직무 그룹 분류",
            ],
            "결과": ["직무별 Top10 비교표", "기술 변동성", "경제적 안정성", "위험군/전환유력군/안정군/정체군"],
        }
    )
    st.dataframe(flow, use_container_width=True, hide_index=True)

# =========================================================
# Page: Quick summary
# =========================================================
elif page == "⚡ 간단 요약":
    page_header("간단 요약", "발표 첫 화면에서 바로 보여줄 수 있는 핵심 수치와 결과입니다.")

    q2025 = calc_quad.dropna(subset=["Employment_Viability_2025", "Quadrant_Group_2025"]).copy()
    group_counts = q2025["Quadrant_Group_2025"].value_counts().reindex(["위험군", "전환유력군", "안정군", "정체군"]).fillna(0).astype(int)

    c1, c2, c3, c4 = st.columns(4)
    for group, col in zip(["위험군", "전환유력군", "안정군", "정체군"], [c1, c2, c3, c4]):
        with col:
            kpi_card(group, f"{group_counts[group]}개", "2025 생존성 기준")

    st.markdown("---")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("#### 변동성 높은 직무 Top5")
        st.dataframe(pretty_df(top5, ["Rank", "DevType_Display", "Volatility", "Intersection_Count", "Union_Count"], drop_original_devtype=True), use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("#### 2025 기준 4사분면 분포")
        counts = group_counts.reset_index()
        counts.columns = ["Group", "Count"]
        fig = px.pie(counts, values="Count", names="Group", hole=0.48, color="Group", color_discrete_map=GROUP_COLORS, template=PLOT_TEMPLATE)
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20), legend_title_text="그룹")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 한 줄 결론")
    st.markdown(
        """
        <div class="good-box">
        2021년과 2025년의 기술 Top10을 비교하면 직무별 기술 변화 폭이 다르게 나타나며, 이를 연봉·정규직/고용 비율과 결합하면 개발자 직무를 위험군·전환유력군·안정군·정체군으로 나눌 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# Page: Table 1
# =========================================================
elif page == "🧩 표1 기술 Top10":
    page_header("표1. 2021년 vs 2025년 사용 기술 Top10", "DevType별 LanguageHaveWorkedWith 기준. 향후 희망 기술은 제외했습니다.")

    options = both_table1["DevType_Display"].dropna().tolist() if "DevType_Display" in both_table1.columns else both_table1["DevType"].dropna().tolist()
    selected = st.selectbox("직무 선택", options)
    key_col = "DevType_Display" if "DevType_Display" in both_table1.columns else "DevType"
    row = both_table1[both_table1[key_col].eq(selected)].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="info-card"><h3>2021 사용 기술 Top10</h3>', unsafe_allow_html=True)
        st.markdown(badges(parse_tech_list(row.get("Tech_2021_Top10_List")), "badge-old"), unsafe_allow_html=True)
        st.metric("2021 응답자 수", fmt_int(row.get("Respondent_Count_2021")))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-card"><h3>2025 사용 기술 Top10</h3>', unsafe_allow_html=True)
        st.markdown(badges(parse_tech_list(row.get("Tech_2025_Top10_List")), "badge-new"), unsafe_allow_html=True)
        st.metric("2025 응답자 수", fmt_int(row.get("Respondent_Count_2025")))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 전체 비교표")
    display_cols = ["DevType_Display", "Name_Status_KO", "Respondent_Count_2021", "Tech_2021_Top10_List", "Respondent_Count_2025", "Tech_2025_Top10_List"]
    st.dataframe(pretty_df(both_table1, display_cols, drop_original_devtype=True), use_container_width=True, hide_index=True)

# =========================================================
# Page: Table 2
# =========================================================
elif page == "📈 표2 변동성 분석":
    page_header("표2. 기술 스택 변동성 분석", "Volatility = 1 - (Intersection_Count / Union_Count)")

    calc = calc_vol.sort_values("Volatility", ascending=False)
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("최고 변동성", fmt_num(calc["Volatility"].max(), 3), calc.iloc[0].get("DevType_Display", calc.iloc[0]["DevType"]) if len(calc) else "-")
    with c2:
        kpi_card("중앙값", fmt_num(calc["Volatility"].median(), 3), "4사분면 기준선")
    with c3:
        kpi_card("평균", fmt_num(calc["Volatility"].mean(), 3), "분석 직무 기준")

    fig = px.bar(
        calc.head(15),
        x="Volatility",
        y="DevType_Display",
        orientation="h",
        hover_data={"DevType": True, "Intersection_Count": True, "Union_Count": True, "Volatility_Rank": True},
        template=PLOT_TEMPLATE,
        title="기술 변동성 상위 15개 직무",
        color="Volatility",
        color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=620, coloraxis_showscale=False, margin=dict(l=10, r=10, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        pretty_df(calc, ["DevType_Display", "Name_Status_KO", "Intersection_List", "Intersection_Count", "Union_Count", "Volatility", "Volatility_Rank"], drop_original_devtype=True),
        use_container_width=True,
        hide_index=True,
    )

# =========================================================
# Page: Table 3
# =========================================================
elif page == "💼 표3 고용 지표":
    page_header("표3. 연봉 및 정규직·고용 비율", "연도별로 연봉 중앙값과 고용 안정성 지표를 분리해 확인합니다.")

    year = st.radio("연도 선택", ["2021", "2025"], horizontal=True)
    df = both_salary.copy()
    if year == "2021":
        plot_df = df.dropna(subset=["Median_Salary_USD_2021", "Regular_Ratio_2021"]).copy()
        x, y, size = "Median_Salary_USD_2021", "Regular_Ratio_2021", "Respondent_Count_2021"
        score1, score2 = "Salary_Score_2021", "Regular_Score_2021"
    else:
        plot_df = df.dropna(subset=["Median_Salary_USD_2025", "Regular_Ratio_2025"]).copy()
        x, y, size = "Median_Salary_USD_2025", "Regular_Ratio_2025", "Respondent_Count_2025"
        score1, score2 = "Salary_Score_2025", "Regular_Score_2025"

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("연봉 중앙값 평균", fmt_money(plot_df[x].mean()), f"{year} 기준")
    with c2:
        kpi_card("정규직/고용 비율 평균", fmt_pct(plot_df[y].mean()), f"{year} 기준")
    with c3:
        kpi_card("표시 직무 수", f"{len(plot_df):,}개", "결측 제외")

    fig = px.scatter(
        plot_df,
        x=x,
        y=y,
        size=size,
        color=score2,
        color_continuous_scale="Teal",
        hover_name="DevType_Display" if "DevType_Display" in plot_df.columns else "DevType",
        hover_data={"DevType": True, "Name_Status_KO": True, score1: ":.3f", score2: ":.3f"},
        template=PLOT_TEMPLATE,
        labels={x: "연봉 중앙값(USD)", y: "정규직/고용 비율", score2: "고용 점수"},
        title=f"{year} 직무별 연봉 중앙값 vs 정규직/고용 비율",
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(height=590, margin=dict(l=10, r=10, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

    cols = ["DevType_Display", "Name_Status_KO"] + [c for c in df.columns if c.endswith(f"_{year}")]
    st.dataframe(pretty_df(df, cols, drop_original_devtype=True), use_container_width=True, hide_index=True)

# =========================================================
# Page: Table 4
# =========================================================
elif page == "🎯 표4 4사분면":
    page_header("표4. 기술 변동성 × 고용 생존성 4사분면", "X축은 고용 생존성, Y축은 기술 스택 변동성입니다.")

    year = st.radio("생존성 기준 연도", ["2021", "2025"], horizontal=True)
    fig, plot_df = make_quadrant_fig(both_quad, year)
    st.plotly_chart(fig, use_container_width=True)

    x_col = f"Employment_Viability_{year}"
    group_col = f"Quadrant_Group_{year}"
    counts = plot_df["Group"].value_counts().reset_index()
    counts.columns = ["Quadrant_Group", "Count"]
    c1, c2 = st.columns([0.75, 1.25])
    with c1:
        st.markdown("#### 그룹별 직무 수")
        st.dataframe(counts, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### 4사분면 결과표")
        show_cols = ["DevType_Display", "Volatility", x_col, group_col, "Calculation_Status_KO"]
        st.dataframe(pretty_df(plot_df[show_cols].sort_values([group_col, "Volatility"], ascending=[True, False]), drop_original_devtype=True), use_container_width=True, hide_index=True)

# =========================================================
# Page: Conclusion
# =========================================================
elif page == "🏁 결론":
    page_header("결론 및 해석", "대시보드 결과를 발표용 문장으로 정리한 페이지입니다.")

    q2025 = calc_quad.dropna(subset=["Employment_Viability_2025", "Quadrant_Group_2025"]).copy()
    top_risk = q2025[q2025["Quadrant_Group_2025"].eq("위험군")].sort_values("Volatility", ascending=False).head(5)
    top_stable = q2025[q2025["Quadrant_Group_2025"].eq("안정군")].sort_values("Employment_Viability_2025", ascending=False).head(5)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="danger-box">
            <b>위험군 해석</b><br>
            기술 스택 변동성이 높지만 고용 생존성이 낮은 직무입니다. 새로운 기술 전환 압력이 큰 반면, 연봉·고용 안정성 지표가 상대적으로 낮아 AI 패러다임 변화에 취약할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(pretty_df(top_risk, ["DevType_Display", "Volatility", "Employment_Viability_2025", "Quadrant_Group_2025"], drop_original_devtype=True), use_container_width=True, hide_index=True)
    with c2:
        st.markdown(
            """
            <div class="good-box">
            <b>안정군 해석</b><br>
            기술 변동성이 낮고 고용 생존성이 높은 직무입니다. 기존 기술 스택이 비교적 유지되면서도 연봉·고용 안정성 지표가 높아 상대적으로 방어력이 강한 직무로 해석할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(pretty_df(top_stable, ["DevType_Display", "Volatility", "Employment_Viability_2025", "Quadrant_Group_2025"], drop_original_devtype=True), use_container_width=True, hide_index=True)

    st.markdown("### 최종 결론")
    st.markdown(
        """
        <div class="info-card">
        <h3>분석 결론</h3>
        <ul>
            <li>생성형 AI 이후 모든 개발자 직무가 동일하게 위험해지는 것이 아니라, <b>직무별 기술 스택 변동성과 고용 지표에 따라 위험도가 다르게 나타난다</b>.</li>
            <li>기술 변동성이 높은 직무는 재교육·스택 전환 압력이 크므로, 단순히 현재 기술 보유 여부보다 <b>전환 가능성</b>이 중요하다.</li>
            <li>연봉과 고용 비율이 높은 직무는 변동성이 있더라도 시장에서 방어력이 있을 수 있어 <b>전환유력군</b>으로 해석할 수 있다.</li>
            <li>따라서 개발자 생존 전략은 “AI에 대체되는가”보다, <b>변화하는 기술 스택에 얼마나 빨리 적응하는가</b>에 초점을 맞춰야 한다.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 발표용 한 문장")
    st.markdown(
        """
        <div class="warn-box">
        본 프로젝트는 2021년과 2025년 Stack Overflow 데이터를 비교해, 생성형 AI 전후 개발자 직무별 기술 스택 변동성을 수치화하고 이를 연봉·고용 안정성과 결합해 직무별 고용 생존성을 판별했다.
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# Page: Raw data
# =========================================================
else:
    page_header("원자료 표 확인", "엑셀에 들어 있는 원자료 시트를 웹에서 직접 확인합니다.")
    sheet = st.selectbox(
        "시트 선택",
        [
            "01_Table1_Top10_2021_2025",
            "02_Table2_Volatility",
            "03_Table3_Salary_Regular",
            "04_Table4_Quadrant_Input",
            "05_Volatility_Top5",
            "06_TechCount_2021",
            "07_TechCount_2025",
            "00_README",
        ],
    )
    df_map = {
        "01_Table1_Top10_2021_2025": table1,
        "02_Table2_Volatility": vol,
        "03_Table3_Salary_Regular": salary,
        "04_Table4_Quadrant_Input": quad,
        "05_Volatility_Top5": top5,
        "06_TechCount_2021": tech21,
        "07_TechCount_2025": tech25,
        "00_README": readme,
    }
    st.dataframe(pretty_df(df_map[sheet], drop_original_devtype=False), use_container_width=True, hide_index=True)
