from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# Page settings
# ------------------------------------------------------------
st.set_page_config(
    page_title="청년 취업난 데이터 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data" / "processed"

# ------------------------------------------------------------
# Styling: clean BI/dashboard style
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;}
    .main {background-color: #F7F9FC;}
    .block-container {padding-top: 1.6rem; padding-bottom: 3rem;}
    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 58%, #2563EB 100%);
        padding: 28px 34px;
        border-radius: 22px;
        color: white;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.18);
        margin-bottom: 18px;
    }
    .hero h1 {font-size: 2.05rem; font-weight: 800; margin: 0 0 8px 0;}
    .hero p {font-size: 1.02rem; color: rgba(255,255,255,.88); margin: 0; line-height: 1.65;}
    .section-card {
        background-color: white;
        padding: 20px 22px;
        border-radius: 18px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        margin-bottom: 16px;
    }
    .metric-card {
        background: white;
        padding: 16px 18px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }
    .small-muted {color: #64748B; font-size: .92rem; line-height: 1.55;}
    .insight-box {
        background: #EFF6FF;
        color: #1E3A8A;
        border-left: 5px solid #2563EB;
        padding: 14px 16px;
        border-radius: 12px;
        margin: 8px 0 16px 0;
        line-height: 1.65;
    }
    .warning-box {
        background: #FFF7ED;
        color: #9A3412;
        border-left: 5px solid #F97316;
        padding: 14px 16px;
        border-radius: 12px;
        margin: 8px 0 16px 0;
        line-height: 1.65;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 14px 16px;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    files = {
        "employment": "employment.csv",
        "nonregular": "nonregular.csv",
        "resting": "resting.csv",
        "wage": "wage.csv",
        "industry": "industry.csv",
    }
    data: dict[str, pd.DataFrame] = {}
    missing = []
    for key, filename in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            missing.append(str(path))
            continue
        data[key] = pd.read_csv(path)
    if missing:
        st.error("처리된 데이터 파일이 없습니다. data/processed 폴더를 확인하세요.\n" + "\n".join(missing))
        st.stop()
    return data


def fmt_num(x: float | int | None, suffix: str = "", decimals: int = 1) -> str:
    if x is None or pd.isna(x):
        return "-"
    if isinstance(x, (int, np.integer)) or decimals == 0:
        return f"{x:,.0f}{suffix}"
    return f"{x:,.{decimals}f}{suffix}"


def yoy_delta(df: pd.DataFrame, col: str, latest_year: int) -> float | None:
    prev_year = latest_year - 1
    latest = df.loc[df["year"] == latest_year, col]
    prev = df.loc[df["year"] == prev_year, col]
    if latest.empty or prev.empty:
        return None
    return float(latest.iloc[0] - prev.iloc[0])


def plot_line(df: pd.DataFrame, y_cols: list[str], labels: dict[str, str], title: str, y_title: str):
    temp = df[["year"] + y_cols].melt(id_vars="year", var_name="indicator", value_name="value")
    temp["indicator"] = temp["indicator"].map(labels).fillna(temp["indicator"])
    fig = px.line(
        temp,
        x="year",
        y="value",
        color="indicator",
        markers=True,
        title=title,
        labels={"year": "연도", "value": y_title, "indicator": "지표"},
        template="plotly_white",
    )
    fig.update_layout(
        height=440,
        legend_title_text="",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=70, b=20),
        font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"),
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    return fig


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, y_title: str, color: str | None = None):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        labels={x: "", y: y_title},
        template="plotly_white",
    )
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=70, b=90),
        xaxis_tickangle=-35,
        font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"),
    )
    return fig


def metric_row(employment: pd.DataFrame, nonregular: pd.DataFrame, resting: pd.DataFrame, wage: pd.DataFrame):
    latest_year = int(min(employment["year"].max(), nonregular["year"].max(), resting["year"].max(), wage["year"].max()))
    emp_latest = employment.loc[employment["year"] == latest_year].iloc[0]
    nr_latest = nonregular.loc[nonregular["year"] == latest_year].iloc[0]
    rest_latest = resting.loc[resting["year"] == latest_year].iloc[0]
    wage_latest = wage[(wage["year"] == latest_year)].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("청년 고용률", fmt_num(emp_latest["employment_rate"], "%"), fmt_num(yoy_delta(employment, "employment_rate", latest_year), "%p"))
    c2.metric("청년 실업률", fmt_num(emp_latest["unemployment_rate"], "%"), fmt_num(yoy_delta(employment, "unemployment_rate", latest_year), "%p"))
    c3.metric("비정규직 비율", fmt_num(nr_latest["nonregular_ratio"], "%"), fmt_num(yoy_delta(nonregular, "nonregular_ratio", latest_year), "%p"))
    c4.metric("쉬었음 청년", fmt_num(rest_latest["resting_thousand"], "천 명", 0), fmt_num(yoy_delta(resting, "resting_thousand", latest_year), "천 명", 0))
    c5.metric("월임금총액", fmt_num(wage_latest["monthly_total_wage_thousand"], "천 원", 0), fmt_num(yoy_delta(wage, "monthly_total_wage_thousand", latest_year), "천 원", 0))


def minmax(series: pd.Series, reverse: bool = False) -> pd.Series:
    s = series.astype(float)
    if s.max() == s.min():
        out = pd.Series(0.5, index=s.index)
    else:
        out = (s - s.min()) / (s.max() - s.min())
    return 1 - out if reverse else out


# ------------------------------------------------------------
# Load
# ------------------------------------------------------------
data = load_data()
employment = data["employment"]
nonregular = data["nonregular"]
resting = data["resting"]
wage = data["wage"]
industry = data["industry"]

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
st.sidebar.title("📊 분석 메뉴")
st.sidebar.caption("KOSIS 기반 청년 취업난 요인 분석 대시보드")
page = st.sidebar.radio(
    "페이지 선택",
    [
        "프로젝트 개요",
        "1. 고용률·실업률",
        "2. 정규직·비정규직",
        "3. 쉬었음 청년",
        "4. 청년 임금",
        "5. 산업별 일자리",
        "6. 종합 결론·대책",
        "데이터 확인",
    ],
)

st.sidebar.markdown("---")
st.sidebar.write("**분석 기간**")
st.sidebar.write(f"고용지표: {employment['year'].min()}~{employment['year'].max()}")
st.sidebar.write(f"산업자료: {industry['year'].min()}~{industry['year'].max()}")
st.sidebar.markdown("---")
st.sidebar.caption("주의: 본 분석은 지표 간 흐름과 관련성을 확인하는 프로젝트이며, 인과관계를 단정하지 않습니다.")

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>청년 고용지표와 취업난 요인 분석</h1>
        <p>고용률·비정규직·쉬었음·임금·산업별 일자리 데이터를 중심으로 청년 취업난을 설명하는 지표들을 탐색합니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_row(employment, nonregular, resting, wage)
st.write("")

# ------------------------------------------------------------
# Pages
# ------------------------------------------------------------
if page == "프로젝트 개요":
    st.subheader("프로젝트 개요")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(
            """
            <div class="section-card">
            <h3>분석 배경</h3>
            <p>최근 청년 고용 문제는 단순히 실업률 하나만으로 설명하기 어렵습니다. 청년 취업자 수 감소, 쉬었음 청년, 취업 준비 장기화, 비정규직과 임금 문제가 함께 언급됩니다.</p>
            <p>따라서 이 프로젝트는 <b>청년들이 왜 취업을 어렵게 느끼는지</b>를 고용의 양, 고용의 질, 노동시장 이탈, 임금, 산업 구조라는 다섯 축으로 나누어 분석합니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="insight-box">
            <b>핵심 질문</b><br>
            청년 취업난은 단순히 일자리 수 부족의 문제인가, 아니면 안정적 일자리 부족·비경제활동 증가·낮은 임금·산업별 일자리 편중과 함께 나타나는 구조적 문제인가?
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        overview = pd.DataFrame(
            {
                "분석축": ["고용의 양", "고용의 질", "노동시장 밖 청년", "임금", "산업 구조"],
                "사용 데이터": ["고용률·실업률·취업자", "정규직·비정규직", "쉬었음 청년", "월임금총액", "산업별 근로자수·임금"],
                "분석 목적": ["기본 고용 흐름 확인", "안정적 일자리 여부 확인", "실업률 밖 청년 확인", "취업 후 경제적 안정성 확인", "어떤 산업에 일자리가 몰리는지 확인"],
            }
        )
        st.dataframe(overview, use_container_width=True, hide_index=True)

    st.subheader("분석 설계")
    st.markdown(
        """
        <div class="section-card">
        <ol>
            <li><b>공식 지표 확인:</b> 청년 고용률·실업률·취업자 수 추이를 확인합니다.</li>
            <li><b>고용의 질 분석:</b> 정규직과 비정규직 비율을 비교합니다.</li>
            <li><b>실업률 밖 청년 확인:</b> 쉬었음 청년 수를 통해 노동시장 이탈 가능성을 확인합니다.</li>
            <li><b>임금 분석:</b> 청년층 월임금총액과 시간당 임금 추이를 봅니다.</li>
            <li><b>산업 구조 분석:</b> 산업별 청년 근로자 수와 임금 수준을 비교합니다.</li>
        </ol>
        </div>
        <div class="warning-box">
        <b>자료 해석 기준</b><br>
        본 대시보드는 2015~2025년 장기 흐름을 비교하되, 자료별 조사 기준이 완전히 같지는 않습니다. 비정규직은 매년 8월 기준, 임금은 29세 이하 기준, 산업별 자료는 일부 구간이 서로 다른 KOSIS 표에서 결합되었습니다. 따라서 결과는 인과관계가 아니라 지표 간 동반 흐름과 구조적 특징으로 해석합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

elif page == "1. 고용률·실업률":
    st.subheader("1. 공식 고용지표: 고용률·실업률")
    st.markdown(
        """
        <div class="section-card">
        이 페이지는 청년 취업 상황의 기본 흐름을 확인합니다. 고용률은 청년 인구 중 취업자의 비율, 실업률은 경제활동인구 중 실업자의 비율입니다. 다만 실업률은 구직활동을 하지 않는 청년을 충분히 보여주지 못할 수 있으므로, 이후 페이지의 지표와 함께 해석해야 합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.plotly_chart(
            plot_line(
                employment,
                ["employment_rate", "unemployment_rate", "labor_force_participation_rate"],
                {
                    "employment_rate": "고용률",
                    "unemployment_rate": "실업률",
                    "labor_force_participation_rate": "경제활동참가율",
                },
                "청년 고용률·실업률·경제활동참가율 추이",
                "비율(%)",
            ),
            use_container_width=True,
        )
    with c2:
        latest = employment.iloc[-1]
        peak_emp = employment.loc[employment["employment_rate"].idxmax()]
        st.markdown(
            f"""
            <div class="insight-box">
            <b>읽는 법</b><br>
            청년 고용률은 {int(peak_emp['year'])}년에 {peak_emp['employment_rate']:.1f}%로 관측기간 중 가장 높았고, 최근 연도에는 {latest['employment_rate']:.1f}%입니다. 따라서 장기적으로 단순 하락이라고 보기보다, <b>2022년 이후 둔화·하락 흐름</b>을 중심으로 해석하는 편이 안전합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(employment, use_container_width=True, hide_index=True)

    st.plotly_chart(
        plot_line(
            employment,
            ["employed_thousand", "unemployed_thousand", "inactive_thousand"],
            {"employed_thousand": "취업자", "unemployed_thousand": "실업자", "inactive_thousand": "비경제활동인구"},
            "청년 취업자·실업자·비경제활동인구 추이",
            "천 명",
        ),
        use_container_width=True,
    )

elif page == "2. 정규직·비정규직":
    st.subheader("2. 고용의 질: 정규직·비정규직")
    st.markdown(
        """
        <div class="section-card">
        고용률은 취업 여부만 보여주지만, 청년이 안정적인 일자리에 진입했는지는 설명하지 못합니다. 그래서 임금근로자 중 정규직·비정규직 비율을 함께 봅니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(
            plot_line(
                nonregular,
                ["regular_ratio", "nonregular_ratio"],
                {"regular_ratio": "정규직 비율", "nonregular_ratio": "비정규직 비율"},
                "청년 정규직·비정규직 비율 추이",
                "비율(%)",
            ),
            use_container_width=True,
        )
    with c2:
        latest = nonregular.iloc[-1]
        st.markdown(
            f"""
            <div class="insight-box">
            <b>핵심 해석</b><br>
            최근 연도 청년 임금근로자 중 비정규직 비율은 {latest['nonregular_ratio']:.1f}%입니다. 취업자 수만 보는 것보다, 정규직과 비정규직 구성을 함께 봐야 현실 취업난을 더 설득력 있게 설명할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(nonregular, use_container_width=True, hide_index=True)

    temp = nonregular[["year", "regular_thousand", "nonregular_thousand"]].melt("year", var_name="type", value_name="workers")
    temp["type"] = temp["type"].map({"regular_thousand": "정규직", "nonregular_thousand": "비정규직"})
    fig = px.bar(temp, x="year", y="workers", color="type", title="청년 정규직·비정규직 규모", labels={"workers": "천 명", "year": "연도", "type": "고용형태"}, template="plotly_white")
    fig.update_layout(height=460, hovermode="x unified", font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

elif page == "3. 쉬었음 청년":
    st.subheader("3. 실업률 밖 청년: 쉬었음")
    st.markdown(
        """
        <div class="section-card">
        실업률은 적극적으로 구직활동을 하는 사람을 중심으로 계산됩니다. 따라서 취업하지 않고 쉬고 있는 청년은 실업률에 충분히 드러나지 않을 수 있습니다. 이 페이지는 '쉬었음' 청년 수를 통해 실업률 밖의 문제를 확인합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    merged = employment.merge(resting, on="year", how="inner")
    merged["resting_share_in_inactive"] = merged["resting_thousand"] / merged["inactive_thousand"] * 100
    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=merged["year"], y=merged["unemployment_rate"], name="실업률(%)", mode="lines+markers", yaxis="y1"))
        fig.add_trace(go.Scatter(x=merged["year"], y=merged["resting_thousand"], name="쉬었음 청년(천 명)", mode="lines+markers", yaxis="y2"))
        fig.update_layout(
            title="청년 실업률과 쉬었음 청년 추이",
            template="plotly_white",
            height=460,
            yaxis=dict(title="실업률(%)"),
            yaxis2=dict(title="쉬었음 청년(천 명)", overlaying="y", side="right"),
            hovermode="x unified",
            legend_title_text="",
            font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(
            """
            <div class="insight-box">
            <b>읽는 법</b><br>
            실업률과 쉬었음 청년은 같은 지표가 아닙니다. 특히 청년 인구 감소로 비경제활동인구 전체가 줄어도, 그 안에서 <b>쉬었음 비중</b>이 커질 수 있습니다. 그래서 쉬었음 청년 수와 비중을 함께 봐야 합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(merged[["year", "unemployment_rate", "inactive_thousand", "resting_thousand"]], use_container_width=True, hide_index=True)

    st.plotly_chart(
        plot_line(
            merged,
            ["resting_share_in_inactive"],
            {"resting_share_in_inactive": "비경제활동인구 중 쉬었음 비중"},
            "청년 비경제활동인구 중 쉬었음 비중",
            "비율(%)",
        ),
        use_container_width=True,
    )

    fig = px.scatter(merged, x="unemployment_rate", y="resting_thousand", text="year", trendline="ols", title="실업률과 쉬었음 청년의 관계", labels={"unemployment_rate": "실업률(%)", "resting_thousand": "쉬었음 청년(천 명)"}, template="plotly_white")
    fig.update_layout(height=460, font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

elif page == "4. 청년 임금":
    st.subheader("4. 취업 후 삶의 질: 청년 임금")
    st.markdown(
        """
        <div class="section-card">
        취업을 하더라도 임금 수준이 낮거나 생활비 상승을 따라가지 못하면 청년층은 고용 상황을 좋게 체감하기 어렵습니다. 이 페이지는 29세 이하 청년층의 <b>명목 임금</b> 변화를 봅니다. 물가·주거비를 반영한 실질임금 분석은 별도 자료가 필요합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    wage_types = wage["employment_type"].unique().tolist()
    selected_type = st.selectbox("고용형태 선택", wage_types, index=0)
    w = wage[wage["employment_type"] == selected_type]

    st.plotly_chart(
        plot_line(
            w,
            ["monthly_total_wage_thousand", "monthly_salary_thousand"],
            {"monthly_total_wage_thousand": "월임금총액", "monthly_salary_thousand": "월급여액"},
            f"29세 이하 {selected_type} 월임금 추이",
            "천 원",
        ),
        use_container_width=True,
    )
    st.plotly_chart(
        plot_line(
            w,
            ["hourly_total_wage_won"],
            {"hourly_total_wage_won": "시간당임금총액"},
            f"29세 이하 {selected_type} 시간당임금총액 추이",
            "원",
        ),
        use_container_width=True,
    )
    if len(wage_types) < 2:
        st.markdown(
            """
            <div class="warning-box">
            현재 업로드된 임금 자료에는 전체근로자만 포함되어 있습니다. 정규근로자·비정규근로자까지 추가로 내려받으면 고용형태별 임금 격차 그래프도 만들 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.dataframe(wage, use_container_width=True, hide_index=True)

elif page == "5. 산업별 일자리":
    st.subheader("5. 산업별 청년 근로자 수와 임금")
    st.markdown(
        """
        <div class="section-card">
        고용률이나 취업자 수가 같더라도 청년 일자리가 어떤 산업에 몰려 있는지는 다를 수 있습니다. 이 페이지는 청년층 근로자가 많은 산업과 해당 산업의 임금 수준을 함께 봅니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns([1, 1])
    with col_a:
        selected_year = st.slider("분석 연도", int(industry["year"].min()), int(industry["year"].max()), int(industry["year"].max()))
    with col_b:
        top_n = st.slider("상위 산업 개수", 5, 15, 10)

    ind_y = industry[industry["year"] == selected_year].dropna(subset=["workers"]).copy()
    ind_y = ind_y.sort_values("workers", ascending=False).head(top_n)
    st.plotly_chart(
        plot_bar(ind_y, "industry", "workers", f"{selected_year}년 산업별 청년 근로자 수 Top {top_n}", "근로자수(명)"),
        use_container_width=True,
    )

    wage_y = industry[industry["year"] == selected_year].dropna(subset=["monthly_total_wage_thousand"]).sort_values("monthly_total_wage_thousand", ascending=False).head(top_n)
    st.plotly_chart(
        plot_bar(wage_y, "industry", "monthly_total_wage_thousand", f"{selected_year}년 산업별 청년 월임금총액 Top {top_n}", "천 원"),
        use_container_width=True,
    )

    scatter_df = industry[industry["year"] == selected_year].dropna(subset=["workers", "monthly_total_wage_thousand"])
    fig = px.scatter(
        scatter_df,
        x="workers",
        y="monthly_total_wage_thousand",
        text="industry",
        title=f"{selected_year}년 산업별 근로자 수와 임금 수준",
        labels={"workers": "근로자수(명)", "monthly_total_wage_thousand": "월임금총액(천 원)"},
        template="plotly_white",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=560, font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

elif page == "6. 종합 결론·대책":
    st.subheader("6. 종합 결론과 대책")
    st.markdown(
        """
        <div class="section-card">
        이 페이지는 여러 지표를 종합해 청년 취업난을 설명합니다. 결론은 특정 요인의 인과효과를 단정하기보다, 각 지표가 함께 보여주는 구조적 특징을 중심으로 정리합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    merged = employment.merge(nonregular[["year", "nonregular_ratio"]], on="year").merge(resting, on="year").merge(wage[wage["employment_type"] == wage["employment_type"].iloc[0]][["year", "monthly_total_wage_thousand"]], on="year")
    merged["employment_bad"] = minmax(merged["employment_rate"], reverse=True)
    merged["unemployment_bad"] = minmax(merged["unemployment_rate"])
    merged["nonregular_bad"] = minmax(merged["nonregular_ratio"])
    merged["resting_bad"] = minmax(merged["resting_thousand"])
    merged["wage_bad"] = minmax(merged["monthly_total_wage_thousand"], reverse=True)
    merged["job_difficulty_index"] = (
        merged["employment_bad"] * 0.20
        + merged["unemployment_bad"] * 0.20
        + merged["nonregular_bad"] * 0.25
        + merged["resting_bad"] * 0.25
        + merged["wage_bad"] * 0.10
    ) * 100

    summary_rows = pd.DataFrame({
        "지표": ["고용률", "실업률", "비정규직 비율", "쉬었음 청년", "월임금총액"],
        "2015년": [
            f"{merged.loc[merged['year'] == 2015, 'employment_rate'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2015, 'unemployment_rate'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2015, 'nonregular_ratio'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2015, 'resting_thousand'].iloc[0]:.0f}천 명",
            f"{merged.loc[merged['year'] == 2015, 'monthly_total_wage_thousand'].iloc[0]:.0f}천 원",
        ],
        "2025년": [
            f"{merged.loc[merged['year'] == 2025, 'employment_rate'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2025, 'unemployment_rate'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2025, 'nonregular_ratio'].iloc[0]:.1f}%",
            f"{merged.loc[merged['year'] == 2025, 'resting_thousand'].iloc[0]:.0f}천 명",
            f"{merged.loc[merged['year'] == 2025, 'monthly_total_wage_thousand'].iloc[0]:.0f}천 원",
        ],
        "해석 포인트": [
            "2022년 정점 이후 하락",
            "장기적으로 하락했으나 최근 소폭 반등",
            "2019년 이후 높은 수준",
            "2015년 대비 증가",
            "명목임금 상승, 실질임금 판단은 제한",
        ],
    })
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="warning-box">
    아래 종합지수는 공식 통계가 아니라 발표용 요약 지표입니다. 가중치가 임의적이므로 결론의 주근거가 아니라 보조 시각화로만 사용합니다.
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(
        plot_line(
            merged,
            ["job_difficulty_index"],
            {"job_difficulty_index": "청년 취업난 종합지수"},
            "청년 취업난 종합지수 추이: 탐색적 지표",
            "0~100",
        ),
        use_container_width=True,
    )

    corr_df = merged[["employment_rate", "unemployment_rate", "nonregular_ratio", "resting_thousand", "monthly_total_wage_thousand", "job_difficulty_index"]].corr(numeric_only=True)
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="주요 지표 간 상관관계",
        template="plotly_white",
    )
    fig.update_layout(height=540, font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="insight-box">
            <h4>종합 결론</h4>
            <ol>
                <li>청년 취업난은 고용률·실업률 하나만으로 설명하기 어렵다.</li>
                <li>비정규직 비율은 고용의 질을 확인하는 핵심 보조지표다.</li>
                <li>쉬었음 청년은 실업률 밖에 있는 노동시장 이탈 가능성을 보여준다.</li>
                <li>임금 수준은 취업 후 삶의 안정성과 연결된다.</li>
                <li>산업별 근로자 수와 임금을 함께 보면 청년 일자리의 구조적 특성을 볼 수 있다.</li>
            </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="section-card">
            <h4>해결 방향</h4>
            <ol>
                <li><b>좋은 일자리 확대:</b> 단순 채용 규모보다 정규직 전환, 근속 가능성, 임금 수준을 함께 보는 청년 고용정책이 필요하다.</li>
                <li><b>쉬었음 청년 재진입 지원:</b> 상담, 직무훈련, 단기 인턴십, 채용 연계 프로그램을 통해 노동시장 복귀 경로를 만들어야 한다.</li>
                <li><b>산업 맞춤형 직무교육:</b> 청년 근로자가 적지만 임금 수준이 높은 산업에는 직무전환 교육과 진입 지원을 강화할 수 있다.</li>
                <li><b>저임금·불안정 산업 개선:</b> 청년이 많이 종사하는 산업의 임금·근로조건을 개선해야 체감 취업난을 줄일 수 있다.</li>
                <li><b>지표 다층화:</b> 실업률뿐 아니라 비경제활동, 쉬었음, 비정규직, 임금 지표를 함께 공개·해석하는 방식이 필요하다.</li>
            </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="warning-box">
        <b>해석상 주의:</b> 본 대시보드는 지표 간 동반 흐름을 보여주는 분석입니다. 특정 지표가 다른 지표의 원인이라고 단정하려면 추가적인 경제 변수, 정책 변수, 기업 채용 데이터, 인구구조 변수를 포함한 별도 분석이 필요합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

elif page == "데이터 확인":
    st.subheader("데이터 확인 및 다운로드")
    dataset_name = st.selectbox("데이터 선택", list(data.keys()))
    df = data[dataset_name]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        label=f"{dataset_name}.csv 다운로드",
        data=df.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"{dataset_name}.csv",
        mime="text/csv",
    )

