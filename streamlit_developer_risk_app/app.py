import os
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="AI 시대 개발자 고용 생존성 분석",
    page_icon="📊",
    layout="wide",
)

DATA_FILE = "stackoverflow_2021_2025_exactname_combined_tables_v2.xlsx"

GROUP_COLORS = {
    "위험군": "#D62728",
    "전환유력군": "#FF7F0E",
    "안정군": "#2CA02C",
    "정체군": "#7F7F7F",
}

st.markdown(
    """
    <style>
    .main {background-color: #FAFAFA;}
    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #E6E8EF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .small-note {color:#6B7280; font-size: 0.9rem;}
    .section-title {font-size: 1.35rem; font-weight: 700; margin-top: 0.4rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def read_sheet(sheet_name: str) -> pd.DataFrame:
    """The workbook has two title/description rows and one blank row; real headers start after skiprows=3."""
    return pd.read_excel(DATA_FILE, sheet_name=sheet_name, skiprows=3)

@st.cache_data
def load_data():
    table1 = read_sheet("01_Table1_Top10_2021_2025")
    vol = read_sheet("02_Table2_Volatility")
    salary = read_sheet("03_Table3_Salary_Regular")
    quad = read_sheet("04_Table4_Quadrant_Input")
    top5 = read_sheet("05_Volatility_Top5")
    tech21 = read_sheet("06_TechCount_2021")
    tech25 = read_sheet("07_TechCount_2025")

    # Numeric cleanup
    for df in [vol, salary, quad, top5, tech21, tech25]:
        for col in df.columns:
            if any(key in col for key in ["Count", "Ratio", "Score", "Salary", "Volatility", "Viability", "Rank", "Median"]):
                df[col] = pd.to_numeric(df[col], errors="ignore")

    return table1, vol, salary, quad, top5, tech21, tech25


def fmt_num(value: Optional[float], digits: int = 3, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}{suffix}"


def fmt_money(value: Optional[float]) -> str:
    if pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def filter_name_status(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if "Name_Status" not in df.columns:
        return df
    if mode == "양쪽 연도 모두 있는 직무만":
        return df[df["Name_Status"].eq("Both exact-name match")].copy()
    return df.copy()


table1, vol, salary, quad, top5, tech21, tech25 = load_data()

st.sidebar.title("📌 메뉴")
page = st.sidebar.radio(
    "화면 선택",
    [
        "개요",
        "표1 기술 Top10",
        "표2 변동성 분석",
        "표3 고용 지표",
        "표4 4사분면",
        "변동성 Top5",
        "데이터 표",
    ],
)

status_mode = st.sidebar.selectbox(
    "직무명 기준",
    ["양쪽 연도 모두 있는 직무만", "전체 직무 보기"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption("데이터: Stack Overflow Developer Survey 2021·2025 정리표")
st.sidebar.caption("DevType 명칭이 다르면 강제 매핑하지 않고 별도 직무로 유지")

both_quad = filter_name_status(quad, status_mode)
both_vol = filter_name_status(vol, status_mode)
both_salary = filter_name_status(salary, status_mode)
both_table1 = filter_name_status(table1, status_mode)

# ------------------------- Overview -------------------------
if page == "개요":
    st.title("생성형 AI 전후 개발자 직종별 고용 생존성 분석")
    st.caption("2021 vs 2025 Stack Overflow Developer Survey 기반")

    calc_quad = quad[quad["Calculation_Status"].eq("Calculated")].copy()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 직무 수", f"{len(calc_quad):,}개")
    c2.metric("평균 변동성", fmt_num(calc_quad["Volatility"].mean(), 3))
    c3.metric("2025 평균 생존성", fmt_num(calc_quad["Employment_Viability_2025"].mean(), 3))
    c4.metric("2025 연봉 중앙값 평균", fmt_money(salary["Median_Salary_USD_2025"].mean()))

    st.markdown("### 분석 흐름")
    flow = pd.DataFrame(
        {
            "단계": ["표1", "표2", "표3", "표4"],
            "내용": [
                "2021년·2025년 직무별 사용 기술 Top10 추출",
                "Top10 기술의 교집합/합집합으로 Volatility 계산",
                "직무별 연봉 중앙값과 정규직/고용 비율 산출",
                "Volatility와 Employment Viability를 결합해 4사분면 분류",
            ],
            "핵심 컬럼": [
                "Tech_2021_Top10_List, Tech_2025_Top10_List",
                "Intersection_Count, Union_Count, Volatility",
                "Median_Salary_USD, Regular_Ratio",
                "Employment_Viability, Quadrant_Group",
            ],
        }
    )
    st.dataframe(flow, use_container_width=True, hide_index=True)

    st.markdown("### 핵심 해석")
    st.info(
        "기술 변동성이 높고 고용 생존성이 낮은 직무는 '위험군', "
        "기술 변동성이 높지만 고용 생존성이 높은 직무는 '전환유력군'으로 해석합니다."
    )

# ------------------------- Table 1 -------------------------
elif page == "표1 기술 Top10":
    st.title("표1. 2021년 vs 2025년 사용 기술 Top10")
    st.caption("LanguageHaveWorkedWith 기준. 향후 희망 기술은 제외했습니다.")

    options = both_table1["DevType"].dropna().tolist()
    selected = st.selectbox("직무 선택", options)
    row = both_table1[both_table1["DevType"].eq(selected)].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("2021 Top10")
        st.write(row.get("Tech_2021_Top10_List", "-"))
        st.metric("2021 응답자 수", int(row["Respondent_Count_2021"]) if pd.notna(row.get("Respondent_Count_2021")) else "-")
    with c2:
        st.subheader("2025 Top10")
        st.write(row.get("Tech_2025_Top10_List", "-"))
        st.metric("2025 응답자 수", int(row["Respondent_Count_2025"]) if pd.notna(row.get("Respondent_Count_2025")) else "-")

    display_cols = ["DevType", "Name_Status", "Respondent_Count_2021", "Tech_2021_Top10_List", "Respondent_Count_2025", "Tech_2025_Top10_List"]
    st.dataframe(both_table1[display_cols], use_container_width=True, hide_index=True)

# ------------------------- Table 2 -------------------------
elif page == "표2 변동성 분석":
    st.title("표2. 기술 스택 변동성 분석")
    st.caption("Volatility = 1 - (Intersection_Count / Union_Count)")

    calc = both_vol.dropna(subset=["Volatility"]).copy().sort_values("Volatility", ascending=False)
    fig = px.bar(
        calc.head(15),
        x="Volatility",
        y="DevType",
        orientation="h",
        hover_data=["Intersection_Count", "Union_Count"],
        title="기술 변동성 상위 직무",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=560)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        calc[["DevType", "Intersection_List", "Intersection_Count", "Union_Count", "Volatility", "Volatility_Rank"]],
        use_container_width=True,
        hide_index=True,
    )

# ------------------------- Table 3 -------------------------
elif page == "표3 고용 지표":
    st.title("표3. 연봉 및 정규직·고용 비율")
    st.caption("2021년과 2025년 값을 분리해 표시합니다.")

    year = st.radio("연도", ["2021", "2025"], horizontal=True)
    df = both_salary.copy()
    if year == "2021":
        plot_df = df.dropna(subset=["Median_Salary_USD_2021", "Regular_Ratio_2021"]).copy()
        x, y, size = "Median_Salary_USD_2021", "Regular_Ratio_2021", "Respondent_Count_2021"
    else:
        plot_df = df.dropna(subset=["Median_Salary_USD_2025", "Regular_Ratio_2025"]).copy()
        x, y, size = "Median_Salary_USD_2025", "Regular_Ratio_2025", "Respondent_Count_2025"

    fig = px.scatter(
        plot_df,
        x=x,
        y=y,
        size=size,
        hover_name="DevType",
        title=f"{year} 직무별 연봉 중앙값 vs 정규직/고용 비율",
        labels={x: "연봉 중앙값(USD)", y: "정규직/고용 비율"},
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    cols = ["DevType", "Name_Status"] + [c for c in df.columns if c.endswith(f"_{year}")]
    st.dataframe(df[cols], use_container_width=True, hide_index=True)

# ------------------------- Table 4 -------------------------
elif page == "표4 4사분면":
    st.title("표4. 기술 변동성 × 고용 생존성 4사분면")
    st.caption("X축=Employment Viability, Y축=Volatility")

    year = st.radio("생존성 기준 연도", ["2021", "2025"], horizontal=True)
    q = both_quad.dropna(subset=["Volatility", f"Employment_Viability_{year}", f"Quadrant_Group_{year}"]).copy()
    q["Group"] = q[f"Quadrant_Group_{year}"]
    x_col = f"Employment_Viability_{year}"

    fig = px.scatter(
        q,
        x=x_col,
        y="Volatility",
        color="Group",
        color_discrete_map=GROUP_COLORS,
        hover_name="DevType",
        hover_data=["Name_Status", "Volatility", x_col],
        title=f"{year} 기준 개발자 직무 4사분면",
    )
    fig.add_vline(x=q[x_col].median(), line_dash="dash", line_color="gray")
    fig.add_hline(y=q["Volatility"].median(), line_dash="dash", line_color="gray")
    fig.update_layout(height=650)
    st.plotly_chart(fig, use_container_width=True)

    counts = q["Group"].value_counts().reset_index()
    counts.columns = ["Quadrant_Group", "Count"]
    st.dataframe(counts, use_container_width=True, hide_index=True)
    st.dataframe(q[["DevType", "Volatility", x_col, "Group", "Calculation_Status"]], use_container_width=True, hide_index=True)

# ------------------------- Top5 -------------------------
elif page == "변동성 Top5":
    st.title("변동성이 높은 직업군 Top5")
    st.caption("2021년과 2025년 모두 exact DevType 명칭이 존재하는 직무 중 산출")

    st.dataframe(top5, use_container_width=True, hide_index=True)
    fig = px.bar(top5, x="Volatility", y="DevType", orientation="h", title="Volatility Top5")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Data -------------------------
else:
    st.title("원자료 표 확인")
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
    }
    st.dataframe(df_map[sheet], use_container_width=True, hide_index=True)

