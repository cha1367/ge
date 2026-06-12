from pathlib import Path
from typing import Optional, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AI 전후 개발자 고용 생존성 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "stackoverflow_2021_2025_ai_roles_revised.xlsx"
REF_DIR = BASE_DIR / "ref_data"

GROUP_COLORS = {
    "위험군": "#EF4444",
    "전환유력군": "#F59E0B",
    "안정군": "#10B981",
    "정체군": "#6B7280",
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

NUMERIC_COLS = [
    "Count", "Rank", "Count_2021", "Count_2025", "Share_2021", "Share_2025",
    "Respondent_Count_2021", "Respondent_Count_2025", "Intersection_Count", "Union_Count",
    "Volatility", "Volatility_Rank", "Respondent_Count", "Salary_N", "Raw_Salary",
    "Raw_Regular_Rate", "Salary_Score", "Regular_Score", "Raw_Salary_2021", "Raw_Salary_2025",
    "Raw_Regular_Rate_2021", "Raw_Regular_Rate_2025", "Salary_Score_2021", "Salary_Score_2025",
    "Regular_Score_2021", "Regular_Score_2025", "Employment_Viability",
    "Volatility_Threshold_Median", "Viability_Threshold_Median", "Year",
]


def ko_name(value: object) -> str:
    if pd.isna(value):
        return "-"
    value = str(value)
    ko = DEVTYPE_KO.get(value, value)
    return f"{ko} ({value})" if ko != value else value


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
        if col in NUMERIC_COLS or any(key in str(col) for key in ["Rate", "Score", "Salary", "Volatility", "Viability", "Count", "Rank", "Share"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def read_ref_csv(name: str) -> pd.DataFrame:
    path = REF_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_data():
    if not DATA_FILE.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_FILE.name}")
        st.stop()
    data = {
        "table1": read_sheet("01_Table1_OverallTop10"),
        "ai_roles": read_sheet("01B_AI_Role_Top10"),
        "vol": read_sheet("02_Table2_Volatility"),
        "salary": read_sheet("03_Table3_SalaryRegular"),
        "quad": read_sheet("04_Table4_Quadrant"),
        "top5": read_sheet("05_Volatility_Top5"),
        "tech21": read_sheet("06_TechCount_2021"),
        "tech25": read_sheet("07_TechCount_2025"),
        "mapping": read_sheet("08_AI_Role_Mapping"),
        "overall_count": read_sheet("09_Overall_TechCount"),
        "onet_summary": read_ref_csv("onet_role_summary.csv"),
        "onet_examples": read_ref_csv("onet_role_examples.csv"),
        "linkedin_role_summary": read_ref_csv("linkedin_role_summary.csv"),
        "linkedin_role_skill": read_ref_csv("linkedin_role_skill_top10.csv"),
        "linkedin_overall": read_ref_csv("linkedin_overall_dev_skill_top30.csv"),
        "linkedin_meta": read_ref_csv("linkedin_metadata.csv"),
        "domestic": read_ref_csv("domestic_sw_manpower.csv"),
    }
    return data


def format_money(x):
    if pd.isna(x):
        return "-"
    return f"${x:,.0f}"


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


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');
    html, body, [class*="css"] {font-family:'Noto Sans KR', sans-serif;}
    .stApp {background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);}    
    [data-testid="stSidebar"] {background: #0F172A;}
    [data-testid="stSidebar"] * {color: #E5E7EB !important;}
    .hero {background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 58%, #0891B2 100%); padding: 2rem 2.2rem; border-radius: 24px; color: white; margin-bottom: 1.1rem; box-shadow: 0 18px 40px rgba(15,23,42,0.18);}    
    .hero h1 {font-size: 2rem; line-height: 1.25; margin: 0 0 0.65rem 0; font-weight: 800; letter-spacing: -0.03em;}
    .hero p {font-size: 1rem; opacity: 0.92; margin: 0; max-width: 980px;}
    .page-title {font-size: 1.75rem; font-weight: 800; color: #0F172A; margin: 0.3rem 0 0.3rem 0;}
    .page-subtitle {color: #64748B; font-size: 0.98rem; margin-bottom: 1.2rem;}
    .kpi-card {background: rgba(255,255,255,0.96); border: 1px solid #E2E8F0; border-radius: 18px; padding: 1.05rem 1.1rem; box-shadow: 0 10px 28px rgba(15,23,42,0.06); min-height: 118px;}
    .kpi-label {color:#64748B; font-size:0.86rem; font-weight:700; margin-bottom:0.35rem;}
    .kpi-value {color:#0F172A; font-size:1.55rem; font-weight:800; letter-spacing:-0.02em;}
    .kpi-note {color:#94A3B8; font-size:0.78rem; margin-top:0.35rem;}
    .info-card {background:white; border:1px solid #E2E8F0; border-radius:18px; padding:1.15rem 1.25rem; box-shadow:0 8px 22px rgba(15,23,42,0.05); height:100%;}
    .info-card h3 {color:#0F172A; font-size:1.05rem; margin:0 0 0.6rem 0; font-weight:800;}
    .info-card p, .info-card li {color:#334155; font-size:0.94rem; line-height:1.62;}
    .formula-card {background:#FFFBEB; border:1px solid #FDE68A; border-radius:16px; padding:1rem 1.2rem; margin:0.5rem 0 1rem 0; color:#78350F;}
    .formula-card code {font-size:1rem; font-weight:800; color:#92400E;}
    .small-note {font-size:0.86rem; color:#64748B;}
    .ai-badge {display:inline-block; background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; border-radius:999px; padding:0.2rem 0.55rem; font-size:0.78rem; font-weight:800;}
    </style>
    """,
    unsafe_allow_html=True,
)


data = load_data()
table1 = data["table1"]
ai_roles = data["ai_roles"]
vol = data["vol"]
salary = data["salary"]
quad = data["quad"]
top5 = data["top5"]
tech21 = data["tech21"]
tech25 = data["tech25"]
mapping = data["mapping"]
overall_count = data["overall_count"]
onet_summary = data["onet_summary"]
onet_examples = data["onet_examples"]
linkedin_role_summary = data["linkedin_role_summary"]
linkedin_role_skill = data["linkedin_role_skill"]
linkedin_overall = data["linkedin_overall"]
linkedin_meta = data["linkedin_meta"]
domestic = data["domestic"]

st.sidebar.markdown("### 📊 AI 개발자 생존성")
st.sidebar.caption("2021 vs 2025 Stack Overflow Survey")
page = st.sidebar.radio(
    "메뉴",
    [
        "개요",
        "표1 전체 기술 Top10",
        "AI 관련 직무",
        "표2 기술 변동성",
        "표3 고용 지표",
        "표4 4사분면",
        "변동성 Top5",
        "참고자료: O*NET",
        "참고자료: LinkedIn",
        "참고자료: 국내 SW 인력",
        "원자료",
    ],
)

st.markdown(
    """
    <div class="hero">
        <h1>생성형 AI 전후 개발자 직종별 고용 생존성 분석</h1>
        <p>Stack Overflow Developer Survey 2021·2025 데이터를 기반으로 기술 스택 변동성과 연봉·고용 지표를 결합해 개발자 직무의 위험도와 생존성을 시각화합니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

avg_vol = vol["Volatility"].dropna().mean() if "Volatility" in vol else float("nan")
avg_salary_2025 = quad["Raw_Salary_2025"].dropna().mean() if "Raw_Salary_2025" in quad else float("nan")
avg_regular_2025 = quad["Raw_Regular_Rate_2025"].dropna().mean() if "Raw_Regular_Rate_2025" in quad else float("nan")
num_jobs = len(quad)
ai_job_count = len(quad[quad.get("AI_Related", "No") == "Yes"]) if "AI_Related" in quad else 0

if page == "개요":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("분석 직무 수", f"{num_jobs}개", "Student 제외")
    with c2:
        kpi_card("AI 관련 직무", f"{ai_job_count}개", "Data/AI 계열 별도 표시")
    with c3:
        kpi_card("평균 기술 변동성", f"{avg_vol:.3f}", "자카드 거리 기준")
    with c4:
        kpi_card("2025 평균 연봉", format_money(avg_salary_2025), f"평균 고용비율 {avg_regular_2025:.1%}" if pd.notna(avg_regular_2025) else "")

    st.markdown('<div class="page-title">프로젝트 개요</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">생성형 AI 등장 전후 개발자 직무별 기술 변화와 고용 생존성을 정량화합니다.</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            """
            <div class="info-card">
            <h3>1. 문제의식</h3>
            <p>생성형 AI 이후 개발 생태계의 기술 스택은 빠르게 재편되고 있습니다. 이 변화는 직무별로 다르게 나타나며, 연봉과 고용 안정성에도 서로 다른 영향을 줄 수 있습니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """
            <div class="info-card">
            <h3>2. 분석 방법</h3>
            <p>2021년과 2025년 사용 기술 Top10을 독립적으로 산출한 뒤, 교집합과 합집합을 이용해 기술 변동성을 계산했습니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            """
            <div class="info-card">
            <h3>3. 결과 해석</h3>
            <p>기술 변동성과 고용 생존성을 결합해 위험군, 전환유력군, 안정군, 정체군으로 분류하고 직무별 대응 방향을 해석합니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("### 데이터 구성")
    st.dataframe(pd.DataFrame([
        {"구분":"메인 데이터", "자료":"Stack Overflow Developer Survey 2021·2025", "역할":"표1~표4 핵심 계산"},
        {"구분":"참고자료", "자료":"O*NET Software Skills", "역할":"직업별 요구 기술 검증"},
        {"구분":"참고자료", "자료":"LinkedIn Jobs & Skills 2024", "역할":"채용공고 기술스택 참고"},
        {"구분":"참고자료", "자료":"국내 직종별 SW 전문인력", "역할":"국내 고용시장 흐름 참고"},
    ]), use_container_width=True, hide_index=True)

elif page == "표1 전체 기술 Top10":
    st.markdown('<div class="page-title">표1. 전체 사용 기술 Top10 변화</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">직무별이 아니라 전체 응답자 기준으로 2021년과 2025년의 기술 스택 변화를 가볍게 보여주는 표입니다.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(table1, x="Rank", y="Count_2021", text="Tech_2021", title="2021년 전체 기술 Top10")
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis_title="빈도", xaxis_title="순위", height=420)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(table1, x="Rank", y="Count_2025", text="Tech_2025", title="2025년 전체 기술 Top10")
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis_title="빈도", xaxis_title="순위", height=420)
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pretty_df(table1), use_container_width=True, hide_index=True)

elif page == "AI 관련 직무":
    st.markdown('<div class="page-title">AI 관련 직무</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Data scientist, Data engineer, AI/ML engineer를 분석용 표준 직무명으로 추가해 모든 표에 반영했습니다.</div>', unsafe_allow_html=True)
    st.markdown('<span class="ai-badge">AI 관련 직무 포함</span>', unsafe_allow_html=True)
    st.markdown("#### AI 관련 직무별 2021/2025 사용 기술 Top10")
    st.dataframe(pretty_df(add_display_columns(ai_roles)), use_container_width=True, hide_index=True)
    st.markdown("#### 매핑 기준")
    st.dataframe(pretty_df(add_display_columns(mapping)), use_container_width=True, hide_index=True)
    ai_quad = quad[quad.get("AI_Related", "No") == "Yes"].copy()
    if not ai_quad.empty:
        fig = px.scatter(
            ai_quad, x="Employment_Viability", y="Volatility", text="Standard_DevType",
            size="Raw_Salary_2025", color="Quadrant_Group", color_discrete_map=GROUP_COLORS,
            title="AI 관련 직무의 4사분면 위치"
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(xaxis_title="고용 생존성", yaxis_title="기술 변동성", height=520)
        st.plotly_chart(fig, use_container_width=True)

elif page == "표2 기술 변동성":
    st.markdown('<div class="page-title">표2. 직무별 기술 변동성</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">각 연도별 순수 Top10 기술 목록을 따로 만든 뒤, 두 집합의 차이를 자카드 거리로 계산했습니다.</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="formula-card">
        <b>기술 변동성 공식</b><br>
        <code>Volatility = 1 - (Intersection_Count / Union_Count)</code><br>
        Intersection_Count는 2021년과 2025년에 모두 포함된 기술 수, Union_Count는 두 연도 기술을 중복 없이 합친 전체 기술 수입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    plot_df = vol.dropna(subset=["Volatility"]).sort_values("Volatility", ascending=True)
    fig = px.bar(plot_df, x="Volatility", y="Standard_DevType", orientation="h", color="AI_Related", title="직무별 기술 변동성")
    fig.update_layout(xaxis_title="기술 변동성", yaxis_title="직무", height=max(500, len(plot_df) * 26))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pretty_df(add_display_columns(vol)), use_container_width=True, hide_index=True)

elif page == "표3 고용 지표":
    st.markdown('<div class="page-title">표3. 연봉 및 정규직/고용 비율</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">직무별 연봉 중앙값과 고용 상태 비율을 연도별로 정리했습니다.</div>', unsafe_allow_html=True)
    salary25 = salary[salary["Year"] == 2025].copy() if "Year" in salary else salary.copy()
    fig = px.scatter(
        salary25, x="Raw_Regular_Rate", y="Raw_Salary", size="Respondent_Count",
        color="AI_Related", hover_name="Standard_DevType",
        title="2025년 직무별 연봉 중앙값과 고용 비율"
    )
    fig.update_layout(xaxis_tickformat=".0%", xaxis_title="정규직/고용 비율", yaxis_title="연봉 중앙값(USD)", height=540)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pretty_df(add_display_columns(salary)), use_container_width=True, hide_index=True)

elif page == "표4 4사분면":
    st.markdown('<div class="page-title">표4. 기술 변동성 × 고용 생존성 4사분면</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">X축은 고용 생존성, Y축은 기술 변동성입니다. 중앙값을 기준으로 네 그룹을 나눕니다.</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="formula-card">
        <b>고용 생존성 공식</b><br>
        <code>Employment_Viability = (Salary_Score_2025 + Regular_Score_2025) / (1 + Volatility)</code><br>
        기술 변동성이 클수록 동일한 연봉·고용 점수라도 생존성 점수가 낮아지도록 설계했습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    qdf = quad.dropna(subset=["Volatility", "Employment_Viability"]).copy()
    fig = px.scatter(
        qdf, x="Employment_Viability", y="Volatility", color="Quadrant_Group",
        size="Raw_Salary_2025", hover_name="Standard_DevType",
        hover_data=["AI_Related", "Raw_Salary_2025", "Raw_Regular_Rate_2025"],
        color_discrete_map=GROUP_COLORS, title="개발자 직무별 4사분면"
    )
    if not qdf.empty:
        fig.add_vline(x=qdf["Employment_Viability"].median(), line_dash="dash", line_color="#64748B")
        fig.add_hline(y=qdf["Volatility"].median(), line_dash="dash", line_color="#64748B")
    fig.update_layout(xaxis_title="고용 생존성", yaxis_title="기술 변동성", height=650)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pretty_df(add_display_columns(quad)), use_container_width=True, hide_index=True)

elif page == "변동성 Top5":
    st.markdown('<div class="page-title">기술 변동성 높은 직무 Top5</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">2021년 대비 2025년 사용 기술 Top10이 가장 많이 바뀐 직무입니다.</div>', unsafe_allow_html=True)
    fig = px.bar(top5.sort_values("Volatility", ascending=True), x="Volatility", y="Standard_DevType", orientation="h", color="AI_Related", title="Volatility Top5")
    fig.update_layout(xaxis_title="기술 변동성", yaxis_title="직무", height=460)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pretty_df(add_display_columns(top5)), use_container_width=True, hide_index=True)

elif page == "참고자료: O*NET":
    st.markdown('<div class="page-title">참고자료: O*NET Software Skills</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">O*NET은 최신 직업별 요구 소프트웨어 기술과 Hot/In Demand 여부를 제공하는 공식 참고자료입니다.</div>', unsafe_allow_html=True)
    st.info("O*NET 자료는 2021/2025 변동성 계산에 직접 넣지 않고, Stack Overflow 주요 기술이 실제 직업별 요구 기술과도 연결되는지 확인하는 참고자료로만 사용합니다.")
    if not onet_summary.empty:
        fig = px.bar(onet_summary.sort_values("In_Demand_수", ascending=True), x="In_Demand_수", y="프로젝트_직무군", orientation="h", title="O*NET 직무군별 In Demand 기술 수")
        fig.update_layout(xaxis_title="In Demand 기술 수", yaxis_title="프로젝트 직무군", height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(onet_summary, use_container_width=True, hide_index=True)
    if not onet_examples.empty:
        st.markdown("#### 세부 기술 예시")
        st.dataframe(onet_examples.head(500), use_container_width=True, hide_index=True)

elif page == "참고자료: LinkedIn":
    st.markdown('<div class="page-title">참고자료: LinkedIn Jobs & Skills 2024</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Kaggle LinkedIn job_skills 자료에서 채용공고 기술스택을 참고용으로 요약했습니다.</div>', unsafe_allow_html=True)
    st.warning("현재 보유한 LinkedIn 파일은 job_link와 job_skills만 포함합니다. 따라서 직무명은 URL 키워드로 추정했으며, 핵심 계산이 아닌 참고자료로만 사용합니다.")
    if not linkedin_role_summary.empty:
        fig = px.bar(linkedin_role_summary.sort_values("URL_키워드_매칭_공고수", ascending=True), x="URL_키워드_매칭_공고수", y="직무_추정", orientation="h", title="URL 키워드 기반 직무 추정 공고 수")
        fig.update_layout(xaxis_title="추정 공고 수", yaxis_title="직무", height=540)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(linkedin_role_summary, use_container_width=True, hide_index=True)
    if not linkedin_role_skill.empty:
        st.markdown("#### 직무별 기술 Top10")
        st.dataframe(linkedin_role_skill, use_container_width=True, hide_index=True)
    if not linkedin_overall.empty:
        st.markdown("#### 개발 관련 URL 추정 공고 전체 기술 Top30")
        st.dataframe(linkedin_overall, use_container_width=True, hide_index=True)
    if not linkedin_meta.empty:
        st.markdown("#### 데이터 한계")
        st.dataframe(linkedin_meta, use_container_width=True, hide_index=True)

elif page == "참고자료: 국내 SW 인력":
    st.markdown('<div class="page-title">참고자료: 국내 직종별 SW 전문인력</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">국내 SW 직무별 인력 흐름을 보조적으로 확인하는 자료입니다. 핵심 계산에는 직접 넣지 않습니다.</div>', unsafe_allow_html=True)
    if not domestic.empty:
        long = domestic.melt(id_vars=["구분"], var_name="연도", value_name="인력_천명")
        fig = px.line(long, x="연도", y="인력_천명", color="구분", markers=True, title="국내 직종별 SW 전문인력 추이")
        fig.update_layout(xaxis_title="연도", yaxis_title="인력(천 명)", height=560)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(domestic, use_container_width=True, hide_index=True)

elif page == "원자료":
    st.markdown('<div class="page-title">원자료 표</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">검증용 상세 테이블입니다.</div>', unsafe_allow_html=True)
    tabs = st.tabs(["2021 기술빈도", "2025 기술빈도", "전체 기술빈도", "O*NET", "LinkedIn", "국내자료"])
    with tabs[0]:
        st.dataframe(pretty_df(add_display_columns(tech21)), use_container_width=True, hide_index=True)
    with tabs[1]:
        st.dataframe(pretty_df(add_display_columns(tech25)), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe(pretty_df(overall_count), use_container_width=True, hide_index=True)
    with tabs[3]:
        st.dataframe(onet_summary, use_container_width=True, hide_index=True)
    with tabs[4]:
        st.dataframe(linkedin_role_summary, use_container_width=True, hide_index=True)
    with tabs[5]:
        st.dataframe(domestic, use_container_width=True, hide_index=True)
