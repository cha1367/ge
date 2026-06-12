from pathlib import Path
from typing import Optional, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="생성형 AI 전후 개발자 고용 생존성 판별",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "stackoverflow_2021_2025_ai_roles_revised.xlsx"

PALETTE = {
    "navy": "#0B1220",
    "blue": "#2563EB",
    "cyan": "#06B6D4",
    "purple": "#7C3AED",
    "green": "#10B981",
    "amber": "#F59E0B",
    "red": "#EF4444",
    "slate": "#64748B",
    "light": "#F8FAFC",
}

GROUP_COLORS = {
    "위험군": "#EF4444",
    "전환유력군": "#F59E0B",
    "안정군": "#10B981",
    "정체군": "#64748B",
    "계산 제외": "#94A3B8",
}

DEVTYPE_KO = {
    "Developer, back-end": "백엔드 개발자",
    "Developer, front-end": "프론트엔드 개발자",
    "Developer, full-stack": "풀스택 개발자",
    "Developer, mobile": "모바일 개발자",
    "Developer, desktop or enterprise applications": "데스크톱/기업용 앱 개발자",
    "Developer, embedded applications or devices": "임베디드 개발자",
    "Developer, QA or test": "QA/테스트 개발자",
    "Developer, game or graphics": "게임/그래픽 개발자",
    "Data or business analyst": "데이터/비즈니스 분석가",
    "Data scientist": "데이터 사이언티스트",
    "Data engineer": "데이터 엔지니어",
    "AI/ML engineer": "AI/ML 엔지니어",
    "Academic researcher": "학술 연구자",
    "Engineering manager": "개발 관리자",
    "Product manager": "프로덕트 매니저",
    "System administrator": "시스템 관리자",
    "Other (please specify):": "기타",
}

COLUMN_KO = {
    "Standard_DevType_Display": "개발자 직무",
    "Standard_DevType": "표준 직무명",
    "DevType_Display": "개발자 직무",
    "DevType": "원문 직무명",
    "DevType_Source": "원문 직무명",
    "DevType_2021_Source": "2021년 원문 직무명",
    "DevType_2025_Source": "2025년 원문 직무명",
    "AI_Related": "AI 관련 직무",
    "Mapping_Type": "매핑 유형",
    "Mapping_Note": "매핑 설명",
    "Rank": "순위",
    "Year": "연도",
    "Technology": "기술",
    "Count": "빈도",
    "Share_2021": "2021년 응답 비율",
    "Share_2025": "2025년 응답 비율",
    "Tech_2021": "2021년 기술",
    "Count_2021": "2021년 빈도",
    "Tech_2025": "2025년 기술",
    "Count_2025": "2025년 빈도",
    "Tech_Count_2021": "2021년 기술 수",
    "Tech_Count_2025": "2025년 기술 수",
    "Top10_Change_Note": "2025년 변화 메모",
    "Respondent_Count_2021": "2021년 응답자 수",
    "Respondent_Count_2025": "2025년 응답자 수",
    "Tech_2021_Top10_List": "2021년 사용 기술 Top10",
    "Tech_2025_Top10_List": "2025년 사용 기술 Top10",
    "Intersection_List": "공통 기술 목록",
    "Intersection_Count": "겹치는 기술 수",
    "Union_Count": "전체 기술 수",
    "Volatility_Formula": "변동성 공식",
    "Volatility": "기술 변동성",
    "Volatility_Level": "변동성 수준",
    "Volatility_Rank": "변동성 순위",
    "Formula_Explanation": "공식 설명",
    "Calculation_Note": "계산 메모",
    "Respondent_Count": "응답자 수",
    "Salary_N": "연봉 응답 수",
    "Raw_Salary": "연봉 중앙값(USD)",
    "Raw_Regular_Rate": "정규직/고용 비율",
    "Salary_Score": "연봉 점수",
    "Regular_Score": "고용 안정성 점수",
    "Employment_Definition": "고용 기준",
    "Raw_Salary_2021": "2021년 연봉 중앙값(USD)",
    "Raw_Salary_2025": "2025년 연봉 중앙값(USD)",
    "Raw_Regular_Rate_2021": "2021년 정규직/고용 비율",
    "Raw_Regular_Rate_2025": "2025년 정규직/고용 비율",
    "Salary_Score_2021": "2021년 연봉 점수",
    "Salary_Score_2025": "2025년 연봉 점수",
    "Regular_Score_2021": "2021년 고용 점수",
    "Regular_Score_2025": "2025년 고용 점수",
    "Employment_Viability": "고용 생존성",
    "Quadrant_Group": "최종 분류",
    "Employment_Viability_Formula": "고용 생존성 공식",
    "Volatility_Threshold_Median": "변동성 중앙값 기준",
    "Viability_Threshold_Median": "생존성 중앙값 기준",
}

NUMERIC_HINTS = ["Rate", "Score", "Salary", "Volatility", "Viability", "Count", "Rank", "Share", "Year"]


def ko_name(value: object) -> str:
    if pd.isna(value):
        return "-"
    value = str(value)
    ko = DEVTYPE_KO.get(value, value)
    return f"{ko} · {value}" if ko != value else value


def add_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Standard_DevType" in out.columns and "Standard_DevType_Display" not in out.columns:
        out.insert(0, "Standard_DevType_Display", out["Standard_DevType"].apply(ko_name))
    elif "DevType" in out.columns and "DevType_Display" not in out.columns:
        out.insert(0, "DevType_Display", out["DevType"].apply(ko_name))
    return out


def pretty_df(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    out = df.copy()
    if columns is not None:
        out = out[[c for c in columns if c in out.columns]].copy()
    return out.rename(columns={c: COLUMN_KO.get(c, c) for c in out.columns})


def read_sheet(sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE, sheet_name=sheet_name, header=2)
    df = df.dropna(how="all")
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed)
    for col in df.columns:
        if col in COLUMN_KO or any(key in str(col) for key in NUMERIC_HINTS):
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0:
                df[col] = converted
    return df


def split_tech_set(value: object) -> set:
    if pd.isna(value):
        return set()
    return {item.strip() for item in str(value).split(";") if item.strip()}


def prepare_volatility_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    tech21_sets = out.get("Tech_2021_Top10_List", pd.Series(index=out.index, dtype=object)).apply(split_tech_set)
    tech25_sets = out.get("Tech_2025_Top10_List", pd.Series(index=out.index, dtype=object)).apply(split_tech_set)
    out["Tech_Count_2021"] = tech21_sets.apply(len)
    out["Tech_Count_2025"] = tech25_sets.apply(len)
    out["Intersection_Count"] = [len(a & b) for a, b in zip(tech21_sets, tech25_sets)]
    out["Union_Count"] = [len(a | b) for a, b in zip(tech21_sets, tech25_sets)]
    out["Volatility"] = out.apply(
        lambda r: 1 - (r["Intersection_Count"] / r["Union_Count"]) if r["Union_Count"] else pd.NA,
        axis=1,
    )
    return out


@st.cache_data(show_spinner=False)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_FILE.name}")
        st.stop()
    return {
        "table1": read_sheet("01_Table1_OverallTop10"),
        "vol": read_sheet("02_Table2_Volatility"),
        "salary": read_sheet("03_Table3_SalaryRegular"),
        "quad": read_sheet("04_Table4_Quadrant"),
        "tech21": read_sheet("06_TechCount_2021"),
        "tech25": read_sheet("07_TechCount_2025"),
        "overall_count": read_sheet("09_Overall_TechCount"),
    }


def fmt_money(x):
    if pd.isna(x):
        return "-"
    return f"${x:,.0f}"


def fmt_pct(x):
    if pd.isna(x):
        return "-"
    return f"{x:.1%}"


def metric_card(label: str, value: str, note: str = "", accent: str = "blue"):
    st.markdown(
        f"""
        <div class="metric-card accent-{accent}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = ""):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def callout(title: str, body: str, tone: str = "blue"):
    st.markdown(
        f"""
        <div class="callout callout-{tone}">
          <div class="callout-title">{title}</div>
          <div class="callout-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def formula_box(title: str, formula: str, body: str):
    st.markdown(
        f"""
        <div class="formula-box">
          <div class="formula-title">{title}</div>
          <div class="formula-code">{formula}</div>
          <div class="formula-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(fig, height: int = 520, showlegend: bool = True):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=13, color="#0F172A"),
        margin=dict(l=20, r=20, t=70, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) if showlegend else None,
        title=dict(font=dict(size=18, color="#0F172A"), x=0.02, xanchor="left"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    return fig


def page_shell(page_name: str):
    st.markdown(
        f"""
        <div class="topbar">
          <div>
            <div class="eyebrow">AI Developer Risk Analytics</div>
            <div class="topbar-title">{page_name}</div>
          </div>
          <div class="topbar-pill">2021 → 2025 · Stack Overflow 기반</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    :root {
      --bg: #F4F7FB;
      --panel: rgba(255,255,255,0.92);
      --line: #E2E8F0;
      --text: #0F172A;
      --muted: #64748B;
      --blue: #2563EB;
      --cyan: #06B6D4;
      --green: #10B981;
      --amber: #F59E0B;
      --red: #EF4444;
    }
    .stApp {
      background:
        radial-gradient(circle at top left, rgba(37,99,235,0.15), transparent 32rem),
        radial-gradient(circle at top right, rgba(6,182,212,0.12), transparent 30rem),
        linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
    }
    blockquote, p, li, div { word-break: keep-all; }
    [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0B1220 0%, #111827 48%, #0F172A 100%);
      border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #E5E7EB !important; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px;
      padding: 0.45rem 0.65rem;
      margin: 0.23rem 0;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
      background: rgba(37,99,235,0.28);
      border-color: rgba(96,165,250,0.42);
    }
    .sidebar-brand {
      padding: 0.8rem 0.2rem 1.2rem 0.2rem;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      margin-bottom: 1rem;
    }
    .sidebar-logo {
      width: 42px; height: 42px; border-radius: 14px;
      display:flex; align-items:center; justify-content:center;
      background: linear-gradient(135deg, #2563EB, #06B6D4);
      color:white; font-size:1.25rem; font-weight:900; margin-bottom:0.6rem;
      box-shadow: 0 12px 30px rgba(37,99,235,0.35);
    }
    .sidebar-title {font-size:1.05rem; font-weight:850; letter-spacing:-0.02em;}
    .sidebar-caption {color:#94A3B8 !important; font-size:0.78rem; line-height:1.45; margin-top:0.3rem;}
    .topbar {
      display:flex; justify-content:space-between; align-items:center;
      padding: 1.05rem 1.2rem; margin-bottom:1.1rem;
      background: rgba(255,255,255,0.80); border: 1px solid rgba(226,232,240,0.85);
      border-radius: 22px; box-shadow: 0 18px 45px rgba(15,23,42,0.07);
      backdrop-filter: blur(12px);
    }
    .eyebrow {font-size:0.72rem; color:#2563EB; font-weight:850; text-transform:uppercase; letter-spacing:0.08em;}
    .topbar-title {font-size:1.45rem; color:#0F172A; font-weight:900; letter-spacing:-0.04em; margin-top:0.12rem;}
    .topbar-pill {background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; border-radius:999px; padding:0.48rem 0.8rem; font-weight:800; font-size:0.83rem;}
    .hero-card {
      position:relative; overflow:hidden;
      background: linear-gradient(135deg, #08111F 0%, #112B57 55%, #075985 100%);
      color:white; padding: 2.1rem 2.25rem; border-radius: 28px;
      box-shadow: 0 22px 65px rgba(15,23,42,0.24); margin-bottom:1.15rem;
    }
    .hero-card:after {
      content:""; position:absolute; width:360px; height:360px; border-radius:50%;
      right:-110px; top:-160px; background:rgba(34,211,238,0.20); filter:blur(1px);
    }
    .hero-kicker {display:inline-block; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.22); padding:0.35rem 0.62rem; border-radius:999px; font-size:0.8rem; font-weight:800; margin-bottom:0.85rem;}
    .hero-title {font-size:2.35rem; font-weight:950; line-height:1.18; letter-spacing:-0.055em; max-width:900px; margin-bottom:0.8rem;}
    .hero-desc {font-size:1.02rem; line-height:1.65; color:#DDEAFE; max-width:980px;}
    .metric-card {
      min-height: 128px; position:relative; overflow:hidden;
      background: rgba(255,255,255,0.95); border: 1px solid #E2E8F0;
      border-radius: 22px; padding: 1.12rem 1.2rem;
      box-shadow: 0 16px 42px rgba(15,23,42,0.08);
    }
    .metric-card:before {content:""; position:absolute; left:0; top:0; height:100%; width:5px; background:#2563EB;}
    .metric-card.accent-cyan:before {background:#06B6D4;} .metric-card.accent-green:before {background:#10B981;} .metric-card.accent-amber:before {background:#F59E0B;} .metric-card.accent-red:before {background:#EF4444;} .metric-card.accent-purple:before {background:#7C3AED;}
    .metric-label {font-size:0.84rem; color:#64748B; font-weight:850; margin-bottom:0.45rem;}
    .metric-value {font-size:1.75rem; color:#0F172A; font-weight:950; letter-spacing:-0.04em;}
    .metric-note {font-size:0.78rem; color:#94A3B8; margin-top:0.35rem; line-height:1.35;}
    .section-title {font-size:1.55rem; color:#0F172A; font-weight:950; letter-spacing:-0.04em; margin:1.15rem 0 0.2rem 0;}
    .section-subtitle {font-size:0.96rem; color:#64748B; margin-bottom:1rem; line-height:1.6;}
    .panel {
      background: rgba(255,255,255,0.93); border:1px solid #E2E8F0; border-radius:22px; padding:1.25rem 1.35rem;
      box-shadow:0 14px 38px rgba(15,23,42,0.07); height:100%;
    }
    .panel h3 {font-size:1.05rem; font-weight:900; color:#0F172A; margin:0 0 0.55rem 0;}
    .panel p, .panel li {font-size:0.94rem; color:#334155; line-height:1.65;}
    .callout {border-radius:18px; padding:1rem 1.15rem; margin:0.65rem 0 1rem 0; border:1px solid; box-shadow:0 10px 26px rgba(15,23,42,0.04);}
    .callout-title {font-weight:900; margin-bottom:0.35rem;} .callout-body {font-size:0.92rem; line-height:1.6;}
    .callout-blue {background:#EFF6FF; border-color:#BFDBFE; color:#1E3A8A;} .callout-amber {background:#FFFBEB; border-color:#FDE68A; color:#78350F;} .callout-green {background:#ECFDF5; border-color:#BBF7D0; color:#065F46;} .callout-red {background:#FEF2F2; border-color:#FECACA; color:#7F1D1D;}
    .formula-box {background:#0F172A; color:white; border-radius:20px; padding:1.05rem 1.2rem; margin:0.7rem 0 1.1rem 0; box-shadow:0 16px 42px rgba(15,23,42,0.18);}
    .formula-title {font-size:0.82rem; color:#93C5FD; font-weight:900; text-transform:uppercase; letter-spacing:0.07em;}
    .formula-code {font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:1.05rem; font-weight:900; color:#E0F2FE; margin:0.5rem 0;}
    .formula-body {font-size:0.88rem; color:#CBD5E1; line-height:1.55;}
    .badge {display:inline-flex; align-items:center; gap:0.35rem; border-radius:999px; padding:0.28rem 0.62rem; font-size:0.78rem; font-weight:900; background:#EEF2FF; color:#3730A3; border:1px solid #C7D2FE;}
    .dataframe {font-size:0.86rem !important;}
    [data-testid="stMetric"] {background: white; border-radius: 18px; padding: 1rem; border: 1px solid #E2E8F0; box-shadow: 0 12px 30px rgba(15,23,42,0.05);}
    </style>
    """,
    unsafe_allow_html=True,
)

# Load data
data = load_data()
table1 = data["table1"]
vol = data["vol"]
salary = data["salary"]
quad = data["quad"]
tech21 = data["tech21"]
tech25 = data["tech25"]
overall_count = data["overall_count"]
vol_display = prepare_volatility_table(vol)

# Sidebar
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
      <div class="sidebar-logo">AI</div>
      <div class="sidebar-title">개발자 고용 생존성 판별</div>
      <div class="sidebar-caption">생성형 AI 전후 기술 스택 변동성과 고용 지표를 한 화면에서 탐색합니다.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
page = st.sidebar.radio(
    "탐색 메뉴",
    [
        "Executive Summary",
        "표1 기술 변화",
        "표2 기술 변동성",
        "표3 고용 지표",
        "표4 4사분면",
        "원자료 테이블",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("메인 계산: Stack Overflow Developer Survey 2021·2025")

# Derived KPIs
avg_vol = vol["Volatility"].dropna().mean() if "Volatility" in vol else float("nan")
max_vol_row = vol.dropna(subset=["Volatility"]).sort_values("Volatility", ascending=False).head(1)
max_vol_name = max_vol_row["Standard_DevType"].iloc[0] if not max_vol_row.empty else "-"
avg_salary_2025 = quad["Raw_Salary_2025"].dropna().mean() if "Raw_Salary_2025" in quad else float("nan")
avg_regular_2025 = quad["Raw_Regular_Rate_2025"].dropna().mean() if "Raw_Regular_Rate_2025" in quad else float("nan")
num_jobs = len(quad)
ai_job_count = len(quad[quad.get("AI_Related", "No") == "Yes"]) if "AI_Related" in quad else 0

# Pages
if page == "Executive Summary":
    page_shell("Executive Summary")
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-kicker">Generative AI Paradigm Shift · 2022 전후 비교</div>
          <div class="hero-title">생성형 AI 패러다임 전후 데이터의 스택 변동성을 기반으로 한 개발자 직종별 고용 생존성 판별</div>
          <div class="hero-desc">Stack Overflow Developer Survey 2021·2025 데이터를 활용해 직종별 기술 스택 변동성을 수치화하고, 이를 연봉 중앙값 및 고용 비율과 결합해 개발자 직종을 위험군·전환유력군·안정군·정체군으로 분류합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("분석 직무 수", f"{num_jobs}개", "Student 제외", "blue")
    with c2:
        metric_card("AI 관련 직무", f"{ai_job_count}개", "Data scientist / Data engineer / AI·ML", "purple")
    with c3:
        metric_card("평균 기술 변동성", f"{avg_vol:.3f}", "자카드 거리 기준", "amber")
    with c4:
        metric_card("2025 평균 연봉", fmt_money(avg_salary_2025), f"평균 고용비율 {fmt_pct(avg_regular_2025)}", "green")

    section_title("선정 배경과 분석 설계", "생성형 AI 이후 커진 기술 변화의 불확실성을 직종별 수치로 비교합니다.")
    a, b, c = st.columns(3)
    with a:
        st.markdown("""
        <div class="panel"><h3>① 기술 환경의 변화</h3><p>생성형 AI 도입 이후 개발 생태계의 기술 스택은 더 빠르게 변하고 있습니다. 본 프로젝트는 2021년과 2025년의 기술 목록을 비교해 직종별 변화 압력을 측정합니다.</p></div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel"><h3>② 분석의 필요성</h3><p>기술 변화가 곧 고용 불안으로 이어진다는 가설을 데이터로 검증하기 위해, 기술 변동성과 경제적 보상·고용 안정성 지표를 함께 봅니다.</p></div>
        """, unsafe_allow_html=True)
    with c:
        st.markdown("""
        <div class="panel"><h3>③ 연구 목적</h3><p>직종별 기술 변동성을 정량화하고 고용 생존성과 비교해 어떤 직종이 취약하거나 안정적인지 4사분면으로 판별합니다.</p></div>
        """, unsafe_allow_html=True)

    section_title("핵심 결과 미리보기")
    left, right = st.columns([1.1, 1])
    with left:
        qdf = quad.dropna(subset=["Volatility", "Employment_Viability"]).copy()
        fig = px.scatter(
            qdf,
            x="Employment_Viability",
            y="Volatility",
            color="Quadrant_Group",
            size="Raw_Salary_2025",
            hover_name="Standard_DevType",
            color_discrete_map=GROUP_COLORS,
            title="기술 변동성 × 고용 생존성",
        )
        if not qdf.empty:
            fig.add_vline(x=qdf["Employment_Viability"].median(), line_dash="dash", line_color="#94A3B8")
            fig.add_hline(y=qdf["Volatility"].median(), line_dash="dash", line_color="#94A3B8")
        fig.update_layout(xaxis_title="고용 생존성", yaxis_title="기술 변동성")
        st.plotly_chart(style_fig(fig, 540), use_container_width=True)
    with right:
        callout("해석 기준", "Y축이 높을수록 기술 스택 변화 압력이 크고, X축이 높을수록 연봉·고용 지표 기반 생존성이 높습니다. 위험군은 고변동·저생존성 영역입니다.", "blue")
        callout("가장 변동성이 큰 직무", f"현재 데이터 기준 변동성 상위 직무는 <b>{max_vol_name}</b>입니다. 정확한 해석은 표2와 표4 화면에서 확인합니다.", "amber")
        st.dataframe(pd.DataFrame([
            {"표": "표1 기술 변화", "표 설명": "전체 개발자 기준 2021·2025 대표 기술 변화"},
            {"표": "표2 기술 변동성", "표 설명": "직무별 기술 집합의 교집합·합집합 기반 변동성"},
            {"표": "표3 고용 지표", "표 설명": "2025년 연봉 중앙값과 고용 비율 시각화"},
            {"표": "표4 4사분면", "표 설명": "기술 변동성 × 고용 생존성 분류"},
        ]), use_container_width=True, hide_index=True)

elif page == "표1 기술 변화":
    page_shell("표1. 전체 기술 변화 Top10")
    callout("표1 설명", "전체 개발자 응답 기준으로 2021년과 2025년의 대표 기술 변화 흐름을 보여주는 요약표입니다. AI 관련 직무는 별도 표로 빼지 않고 표2·표3·표4 원데이터에 포함했습니다.", "blue")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(table1, x="Count_2021", y="Tech_2021", orientation="h", text="Count_2021", title="2021년 전체 사용 기술 Top10")
        fig.update_traces(marker_color="#2563EB", textposition="outside")
        fig.update_layout(xaxis_title="빈도", yaxis_title="기술", yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_fig(fig, 500, False), use_container_width=True)
    with c2:
        fig = px.bar(table1, x="Count_2025", y="Tech_2025", orientation="h", text="Count_2025", title="2025년 전체 사용 기술 Top10")
        fig.update_traces(marker_color="#06B6D4", textposition="outside")
        fig.update_layout(xaxis_title="빈도", yaxis_title="기술", yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_fig(fig, 500, False), use_container_width=True)
    st.dataframe(pretty_df(table1, ["Rank", "Tech_2021", "Count_2021", "Tech_2025", "Count_2025"]), use_container_width=True, hide_index=True)

elif page == "표2 기술 변동성":
    page_shell("표2. 직무별 기술 변동성")
    formula_box(
        "Volatility formula",
        "Volatility = 1 - (Intersection_Count / Union_Count)",
        "평균 기술 수를 쓰지 않고, 표에 포함된 2021·2025 기술 목록 전체를 집합으로 변환해 교집합·합집합을 계산합니다. 값이 높을수록 기술 스택 변화가 큽니다.",
    )
    plot_df = vol_display.dropna(subset=["Volatility"]).sort_values("Volatility", ascending=True).copy()
    plot_df["직무"] = plot_df["Standard_DevType"].apply(lambda x: DEVTYPE_KO.get(str(x), str(x)))
    fig = px.bar(
        plot_df,
        x="Volatility",
        y="직무",
        orientation="h",
        color="AI_Related",
        color_discrete_map={"Yes": "#7C3AED", "No": "#2563EB"},
        title="직무별 기술 변동성 순위",
    )
    fig.update_layout(xaxis_title="기술 변동성", yaxis_title="직무", height=max(520, len(plot_df) * 28))
    st.plotly_chart(style_fig(fig, max(520, len(plot_df) * 28)), use_container_width=True)
    st.dataframe(pretty_df(add_display_columns(vol_display), ["Standard_DevType_Display", "AI_Related", "Tech_Count_2021", "Tech_Count_2025", "Intersection_Count", "Union_Count", "Volatility", "Volatility_Rank"]), use_container_width=True, hide_index=True)

elif page == "표3 고용 지표":
    page_shell("표3. 연봉 및 고용 지표")
    callout("표3 설명", "직무별 경제적 보상과 고용 안정성의 대리 지표입니다. 연봉은 중앙값을 사용해 극단값 영향을 줄였습니다. Retired 항목은 개발자 직무 비교에서 제외했습니다.", "green")
    salary25 = salary[salary["Year"] == 2025].copy() if "Year" in salary else salary.copy()
    if "Standard_DevType" in salary25:
        salary25 = salary25[~salary25["Standard_DevType"].astype(str).str.contains("Retired", case=False, na=False)].copy()
    salary25["직무"] = salary25["Standard_DevType"].apply(lambda x: DEVTYPE_KO.get(str(x), str(x))) if "Standard_DevType" in salary25 else salary25.get("DevType", "")
    left, right = st.columns([1.1, 1])
    with left:
        fig = px.scatter(
            salary25,
            x="Raw_Regular_Rate",
            y="Raw_Salary",
            size="Respondent_Count",
            color="AI_Related",
            hover_name="직무",
            color_discrete_map={"Yes": "#7C3AED", "No": "#10B981"},
            title="2025년 연봉 중앙값 × 정규직/고용 비율",
        )
        fig.update_layout(xaxis_tickformat=".0%", xaxis_title="정규직/고용 비율", yaxis_title="연봉 중앙값(USD)")
        st.plotly_chart(style_fig(fig, 560), use_container_width=True)
    with right:
        top_salary = salary25.dropna(subset=["Raw_Salary"]).sort_values("Raw_Salary", ascending=False).head(7)
        fig2 = px.bar(top_salary, x="Raw_Salary", y="직무", orientation="h", title="2025년 연봉 중앙값 상위 직무")
        fig2.update_traces(marker_color="#0EA5E9")
        fig2.update_layout(xaxis_title="연봉 중앙값(USD)", yaxis_title="직무", yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_fig(fig2, 560, False), use_container_width=True)


elif page == "표4 4사분면":
    page_shell("표4. 4사분면 분석")
    formula_box(
        "Employment viability formula",
        "Employment_Viability = (Salary_Score_2025 + Regular_Score_2025) / (1 + Volatility)",
        "연봉 점수와 고용 점수를 더한 뒤 기술 변동성으로 보정합니다. 변동성이 높을수록 같은 연봉·고용 점수라도 생존성은 낮아집니다.",
    )
    qdf = quad.dropna(subset=["Volatility", "Employment_Viability"]).copy()
    qdf["직무"] = qdf["Standard_DevType"].apply(lambda x: DEVTYPE_KO.get(str(x), str(x)))
    fig = px.scatter(
        qdf,
        x="Employment_Viability",
        y="Volatility",
        color="Quadrant_Group",
        size="Raw_Salary_2025",
        hover_name="직무",
        hover_data={"AI_Related": True, "Raw_Salary_2025": ":,.0f", "Raw_Regular_Rate_2025": ":.1%", "직무": False},
        color_discrete_map=GROUP_COLORS,
        title="기술 변동성 × 고용 생존성 4사분면",
    )
    if not qdf.empty:
        med_x = qdf["Employment_Viability"].median()
        med_y = qdf["Volatility"].median()
        fig.add_vline(x=med_x, line_dash="dash", line_color="#94A3B8", annotation_text="생존성 중앙값")
        fig.add_hline(y=med_y, line_dash="dash", line_color="#94A3B8", annotation_text="변동성 중앙값")
        fig.add_annotation(x=qdf["Employment_Viability"].min(), y=qdf["Volatility"].max(), text="위험군", showarrow=False, font=dict(color="#EF4444", size=15))
        fig.add_annotation(x=qdf["Employment_Viability"].max(), y=qdf["Volatility"].max(), text="전환유력군", showarrow=False, font=dict(color="#F59E0B", size=15))
        fig.add_annotation(x=qdf["Employment_Viability"].max(), y=qdf["Volatility"].min(), text="안정군", showarrow=False, font=dict(color="#10B981", size=15))
        fig.add_annotation(x=qdf["Employment_Viability"].min(), y=qdf["Volatility"].min(), text="정체군", showarrow=False, font=dict(color="#64748B", size=15))
    fig.update_layout(xaxis_title="고용 생존성", yaxis_title="기술 변동성")
    st.plotly_chart(style_fig(fig, 700), use_container_width=True)

elif page == "원자료 테이블":
    page_shell("원자료 테이블")
    tabs = st.tabs(["2021 기술빈도", "2025 기술빈도", "전체 기술빈도", "표2 계산 입력"])
    with tabs[0]:
        st.dataframe(pretty_df(add_display_columns(tech21)), use_container_width=True, hide_index=True)
    with tabs[1]:
        st.dataframe(pretty_df(add_display_columns(tech25)), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe(pretty_df(overall_count), use_container_width=True, hide_index=True)
    with tabs[3]:
        st.dataframe(pretty_df(add_display_columns(vol_display), ["Standard_DevType_Display", "AI_Related", "Tech_Count_2021", "Tech_Count_2025", "Intersection_Count", "Union_Count", "Volatility", "Volatility_Rank"]), use_container_width=True, hide_index=True)
