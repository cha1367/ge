# app.py
# 실행: streamlit run app.py
# 필요 패키지: streamlit pandas plotly

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================
# 0. 기본 설정
# =========================
st.set_page_config(
    page_title="노동시장 직군 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent

FILES = {
    "annual_job": "직업별_취업자_연도별.csv",
    "gender_job": "성별_직업별.csv",
    "region_job": "시도별_직업별.csv",
    "age_edu_job": "직업별_학력별.csv",
    "industry_job": "전국_성별_산업_직업별_취업자_대분류__20260531191932.csv",
    "region_industry": "행정구역_시도__산업별_취업자_20260531191255.csv",
    "wage_include_mgr": "관리자 포함.csv",
    "wage_exclude_mgr": "관리자 미 포함.csv",
}

WHITE = ["관리자", "전문가", "사무"]
BLUE = ["기능원", "장치", "단순"]
OTHER = ["서비스", "판매", "농림"]

COLOR_MAP = {
    "화이트칼라": "#8dd3ff",
    "블루칼라": "#ffb86c",
    "기타": "#b9fbc0",
    "관리자 포함": "#8dd3ff",
    "관리자 제외": "#cdb4db",
}

px.defaults.template = "plotly_dark"

# =========================
# 1. CSS: 검은 계열 디자인
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #080b12 0%, #111827 45%, #0b1020 100%);
        color: #e5e7eb;
    }
    section[data-testid="stSidebar"] {
        background: #050816;
        border-right: 1px solid #1f2937;
    }
    .block-container {
        padding-top: 1.7rem;
        padding-bottom: 2.5rem;
    }
    h1, h2, h3 {
        color: #f9fafb;
        letter-spacing: -0.03em;
    }
    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263244;
        padding: 18px 20px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
    }
    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
    }
    div[data-testid="stMetricValue"] {
        color: #f9fafb;
    }
    .insight-box {
        background: #111827;
        border-left: 5px solid #60a5fa;
        border-radius: 14px;
        padding: 16px 18px;
        margin: 12px 0 18px 0;
        color: #e5e7eb;
        line-height: 1.7;
    }
    .note-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 14px 16px;
        color: #cbd5e1;
        line-height: 1.65;
    }
    .small-caption {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-top: -8px;
    }
    hr {
        border-color: #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 2. 공통 함수
# =========================
@st.cache_data
def read_csv_file(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_error = e
    raise RuntimeError(f"파일을 읽지 못했습니다: {filename} / {last_error}")


def to_num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def is_aggregate_job(name: str) -> bool:
    name = str(name).strip()
    return name == "계" or name.startswith("*") or name in ["직업별", "성별"]


def classify_job(name: str) -> str | None:
    name = str(name).replace(" ", "").strip()
    if name in ["계", "직업별", "성별"] or name.startswith("*"):
        return None
    if any(k.replace(" ", "") in name for k in WHITE):
        return "화이트칼라"
    if any(k.replace(" ", "") in name for k in BLUE):
        return "블루칼라"
    if any(k.replace(" ", "") in name for k in OTHER):
        return "기타"
    return None


def style_fig(fig, title=None, height=460):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb", family="Malgun Gothic, AppleGothic, Arial"),
        margin=dict(l=30, r=30, t=70 if title else 30, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#243041", zerolinecolor="#334155")
    fig.update_yaxes(gridcolor="#243041", zerolinecolor="#334155")
    return fig


def insight(text: str):
    st.markdown(f"<div class='insight-box'><b>핵심 해석</b><br>{text}</div>", unsafe_allow_html=True)


def note(text: str):
    st.markdown(f"<div class='note-box'>{text}</div>", unsafe_allow_html=True)


def get_latest_period(columns, pattern=r"^\d{4}\.\d/2"):
    periods = [c for c in columns if re.match(pattern, str(c))]
    return periods[-1] if periods else None

# =========================
# 3. 데이터 전처리 함수
# =========================
@st.cache_data
def build_annual_job_group() -> pd.DataFrame:
    df = read_csv_file(FILES["annual_job"]).copy()
    years = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    detail = df[~df["직업별"].astype(str).apply(is_aggregate_job)].copy()
    detail["직군"] = detail["직업별"].apply(classify_job)
    for y in years:
        detail[y] = to_num(detail[y])

    total = df[df["직업별"].astype(str).str.strip() == "계"].iloc[0]
    rows = []
    for y in years:
        total_y = pd.to_numeric(str(total[y]).replace(",", ""), errors="coerce")
        for group in ["화이트칼라", "블루칼라", "기타"]:
            value = detail.loc[detail["직군"] == group, y].sum()
            rows.append({"연도": int(y), "직군": group, "취업자수": value, "비중": value / total_y * 100})
    return pd.DataFrame(rows)


@st.cache_data
def build_manager_compare() -> pd.DataFrame:
    df = read_csv_file(FILES["annual_job"]).copy()
    years = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    for y in years:
        df[y] = to_num(df[y])

    def val(keyword, year):
        return df[df["직업별"].astype(str).str.contains(keyword, regex=False)][year].iloc[0]

    total = df[df["직업별"].astype(str).str.strip() == "계"].iloc[0]
    rows = []
    for y in years:
        total_y = total[y]
        mgr = val("관리자", y)
        prof = val("전문가", y)
        office = val("사무", y)
        include = mgr + prof + office
        exclude = prof + office
        rows.append({"연도": int(y), "기준": "관리자 포함", "비중": include / total_y * 100, "취업자수": include})
        rows.append({"연도": int(y), "기준": "관리자 제외", "비중": exclude / total_y * 100, "취업자수": exclude})
    return pd.DataFrame(rows)


@st.cache_data
def build_gender_job() -> pd.DataFrame:
    df = read_csv_file(FILES["gender_job"]).copy()
    years = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    detail = df[~df["직업별"].astype(str).apply(is_aggregate_job)].copy()
    detail["직군"] = detail["직업별"].apply(classify_job)
    for y in years:
        detail[y] = to_num(detail[y])

    total = df[df["직업별"].astype(str).str.strip() == "계"].copy()
    for y in years:
        total[y] = to_num(total[y])

    rows = []
    for gender in ["남자", "여자"]:
        total_row = total[total["성별"] == gender].iloc[0]
        sub = detail[detail["성별"] == gender]
        for y in years:
            total_y = total_row[y]
            for group in ["화이트칼라", "블루칼라", "기타"]:
                value = sub.loc[sub["직군"] == group, y].sum()
                rows.append({"성별": gender, "연도": int(y), "직군": group, "취업자수": value, "비중": value / total_y * 100})
    return pd.DataFrame(rows)


@st.cache_data
def build_region_job(period="2025.2/2") -> pd.DataFrame:
    df = read_csv_file(FILES["region_job"]).copy()
    df = df[df["행정구역별"].astype(str) != "행정구역별"].copy()
    df[period] = to_num(df[period])
    df["직군"] = df["직업별"].apply(classify_job)

    rows = []
    for region, sub in df.groupby("행정구역별"):
        if region == "계":
            continue
        total = sub.loc[sub["직업별"].astype(str).str.strip() == "계", period].sum()
        if total == 0:
            continue
        for group in ["화이트칼라", "블루칼라", "기타"]:
            value = sub.loc[sub["직군"] == group, period].sum()
            rows.append({"지역": region, "직군": group, "취업자수": value, "비중": value / total * 100})
    return pd.DataFrame(rows)


@st.cache_data
def build_industry_job(period="2025.2/2") -> pd.DataFrame:
    df = read_csv_file(FILES["industry_job"]).copy()
    df = df[(df["성별"].astype(str) == "계") & (df["산업별"].astype(str) != "산업별")].copy()
    df[period] = to_num(df[period])
    df["직군"] = df["직업별"].apply(classify_job)

    rows = []
    for industry, sub in df.groupby("산업별"):
        if industry == "계":
            continue
        total = sub.loc[sub["직업별"].astype(str).str.strip() == "계", period].sum()
        if total == 0:
            continue
        for group in ["화이트칼라", "블루칼라", "기타"]:
            value = sub.loc[sub["직군"] == group, period].sum()
            rows.append({"산업": industry, "직군": group, "취업자수": value, "비중": value / total * 100})
    return pd.DataFrame(rows)


@st.cache_data
def build_region_industry(year="2025") -> pd.DataFrame:
    df = read_csv_file(FILES["region_industry"]).copy()
    df = df[df["시도별"].astype(str) != "계"].copy()
    df[year] = to_num(df[year])

    total = df[df["산업별"].astype(str).str.strip() == "계"][["시도별", year]].rename(columns={year: "전체"})
    merged = df.merge(total, on="시도별", how="left")
    merged["비중"] = merged[year] / merged["전체"] * 100
    merged = merged.rename(columns={"시도별": "지역", "산업별": "산업", year: "취업자수"})
    return merged


@st.cache_data
def build_age_edu(period="2024.1/2"):
    df = read_csv_file(FILES["age_edu_job"]).copy()
    # 첫 번째 행은 각 반복 컬럼의 실제 지표명이다.
    header_row = df.iloc[0]
    data = df.iloc[1:].copy()

    period_cols = [c for c in df.columns if str(c).startswith(period)]
    rows = []
    for col in period_cols:
        metric = str(header_row[col]).strip()
        temp = data[["직업별", col]].copy()
        temp["지표"] = metric
        temp["값"] = to_num(temp[col])
        rows.append(temp[["직업별", "지표", "값"]])

    long = pd.concat(rows, ignore_index=True)
    long["직군"] = long["직업별"].apply(classify_job)
    long = long[long["직군"].notna()].copy()

    group = long.groupby(["직군", "지표"], as_index=False)["값"].sum()
    total_by_group = group[group["지표"] == "취업자 (천명)"][["직군", "값"]].rename(columns={"값": "직군전체"})
    group = group.merge(total_by_group, on="직군", how="left")
    group["비중"] = group["값"] / group["직군전체"] * 100

    age_order = ["연령(15~29세)", "연령(30~39세)", "연령(40~49세)", "연령(50~59세)", "연령(60세 이상)"]
    edu_order = ["교육정도(중졸이하)", "교육정도(고졸)", "교육정도(대졸이상)"]
    age = group[group["지표"].isin(age_order)].copy()
    edu = group[group["지표"].isin(edu_order)].copy()
    age["지표"] = pd.Categorical(age["지표"], categories=age_order, ordered=True)
    edu["지표"] = pd.Categorical(edu["지표"], categories=edu_order, ordered=True)
    return age.sort_values(["직군", "지표"]), edu.sort_values(["직군", "지표"])


@st.cache_data
def build_wage(include_manager=True) -> pd.DataFrame:
    filename = FILES["wage_include_mgr"] if include_manager else FILES["wage_exclude_mgr"]
    df = read_csv_file(filename).copy()
    df = df[df["고용형태"].astype(str) != "고용형태"].copy()
    years = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    for y in years:
        df[y] = to_num(df[y])
    df["직군"] = df["직종별"].apply(classify_job)

    rows = []
    for y in years:
        # 직업 대분류별 원자료
        for _, r in df.iterrows():
            if str(r["직종별"]) == "전직종":
                continue
            rows.append({"연도": int(y), "직종": r["직종별"], "직군": r["직군"], "월임금총액": r[y]})
    return pd.DataFrame(rows)


@st.cache_data
def build_wage_group() -> pd.DataFrame:
    inc = build_wage(True)
    exc = build_wage(False)
    rows = []
    for year, sub in inc.groupby("연도"):
        rows.append({"연도": year, "기준": "화이트칼라(관리자 포함)", "월임금총액": sub[sub["직군"] == "화이트칼라"]["월임금총액"].mean()})
        rows.append({"연도": year, "기준": "블루칼라", "월임금총액": sub[sub["직군"] == "블루칼라"]["월임금총액"].mean()})
    for year, sub in exc.groupby("연도"):
        rows.append({"연도": year, "기준": "화이트칼라(관리자 제외)", "월임금총액": sub[sub["직군"] == "화이트칼라"]["월임금총액"].mean()})
    return pd.DataFrame(rows)

# =========================
# 4. 사이드바
# =========================
st.sidebar.title("📊 노동시장 직군 분석")
st.sidebar.caption("화이트칼라·블루칼라 중심")

page = st.sidebar.radio(
    "페이지 선택",
    [
        "프로젝트 개요",
        "직군 분포 변화",
        "관리자 포함/제외 비교",
        "연령·학력별 특성",
        "지역별 직군 분포",
        "지역 산업구조 연결",
        "산업별 직군 구조",
        "임금 분석",
        "성별 보조 분석",
        "결론 및 시사점",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**사용 파일명**")
for f in FILES.values():
    st.sidebar.caption(f)

# =========================
# 5. 페이지별 화면
# =========================
if page == "프로젝트 개요":
    st.title("대한민국 노동시장의 직군 분포 변화와 산업구조 특성 분석")
    st.markdown("### 화이트칼라와 블루칼라를 중심으로")

    note(
        "본 대시보드는 2016~2025년 직업별 취업자 자료를 중심으로 한국 노동시장의 직군 구조 변화를 분석한다. "
        "분석의 초점은 단순한 직업별 취업자 수 비교가 아니라, 화이트칼라·블루칼라의 비중 변화가 연령, 학력, 지역, 산업구조, 임금과 어떻게 연결되는지 확인하는 데 있다."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("분석 기간", "2016~2025")
    c2.metric("핵심 분류", "화이트칼라 / 블루칼라 / 기타")
    c3.metric("대시보드 구성", "10개 페이지")

    st.markdown("## 직군 분류 기준")
    class_df = pd.DataFrame(
        {
            "구분": ["화이트칼라", "블루칼라", "기타"],
            "포함 직업": [
                "관리자, 전문가 및 관련 종사자, 사무 종사자",
                "기능원 및 관련 기능 종사자, 장치·기계 조작 및 조립 종사자, 단순노무 종사자",
                "서비스 종사자, 판매 종사자, 농림어업 숙련 종사자",
            ],
            "분류 이유": [
                "관리·전문지식·사무처리 중심 직무",
                "생산·기능·조립·기계조작·현장노동 중심 직무",
                "화이트칼라/블루칼라 어느 한쪽으로 단순 분류하기 어려운 직무",
            ],
        }
    )
    st.dataframe(class_df, use_container_width=True, hide_index=True)

    st.markdown("## 사용 데이터")
    data_df = pd.DataFrame(
        [
            ["직업별_취업자_연도별.csv", "연도별 직군 비중 변화, 관리자 포함/제외 비교"],
            ["직업별_학력별.csv", "연령·학력별 직군 특성"],
            ["시도별_직업별.csv", "지역별 직군 분포"],
            ["행정구역_시도__산업별_취업자_20260531191255.csv", "지역별 산업구조"],
            ["전국_성별_산업_직업별_취업자_대분류__20260531191932.csv", "산업별 직군 구조"],
            ["관리자 포함.csv / 관리자 미 포함.csv", "직군별 임금 비교 및 관리자 효과 확인"],
            ["성별_직업별.csv", "성별 직군 구조 보조 분석"],
        ],
        columns=["파일명", "활용 목적"],
    )
    st.dataframe(data_df, use_container_width=True, hide_index=True)

elif page == "직군 분포 변화":
    st.title("2016~2025년 직군 분포 변화")
    df = build_annual_job_group()
    wide = df.pivot(index="연도", columns="직군", values="비중").reset_index()
    y2025 = df[df["연도"] == df["연도"].max()]
    y2016 = df[df["연도"] == df["연도"].min()]

    col1, col2, col3, col4 = st.columns(4)
    wc25 = y2025.loc[y2025["직군"] == "화이트칼라", "비중"].iloc[0]
    bc25 = y2025.loc[y2025["직군"] == "블루칼라", "비중"].iloc[0]
    wc16 = y2016.loc[y2016["직군"] == "화이트칼라", "비중"].iloc[0]
    bc16 = y2016.loc[y2016["직군"] == "블루칼라", "비중"].iloc[0]
    col1.metric("2025 화이트칼라 비중", f"{wc25:.2f}%", f"{wc25 - wc16:+.2f}%p")
    col2.metric("2025 블루칼라 비중", f"{bc25:.2f}%", f"{bc25 - bc16:+.2f}%p")
    col3.metric("화이트칼라 변화폭", f"{wc25 - wc16:+.2f}%p")
    col4.metric("블루칼라 변화폭", f"{bc25 - bc16:+.2f}%p")

    fig = px.line(df, x="연도", y="비중", color="직군", markers=True, color_discrete_map=COLOR_MAP)
    st.plotly_chart(style_fig(fig, "2016~2025년 화이트칼라·블루칼라·기타 비중 변화"), use_container_width=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig2 = px.pie(y2025, names="직군", values="취업자수", hole=0.55, color="직군", color_discrete_map=COLOR_MAP)
        st.plotly_chart(style_fig(fig2, "2025년 직군 구성"), use_container_width=True)
    with c2:
        st.dataframe(wide.round(2), use_container_width=True, hide_index=True)

    insight("전체 취업자 기준으로 직군 비중의 장기 변화를 확인한다. 이 페이지가 프로젝트의 핵심 출발점이며, 이후 연령·학력·지역·산업·임금 분석은 이 변화가 어디에서 비롯되는지 설명하는 보조 분석이다.")

elif page == "관리자 포함/제외 비교":
    st.title("관리자 포함/제외 비교")
    df = build_manager_compare()
    latest = df["연도"].max()
    latest_df = df[df["연도"] == latest]

    c1, c2, c3 = st.columns(3)
    inc = latest_df.loc[latest_df["기준"] == "관리자 포함", "비중"].iloc[0]
    exc = latest_df.loc[latest_df["기준"] == "관리자 제외", "비중"].iloc[0]
    c1.metric(f"{latest} 관리자 포함", f"{inc:.2f}%")
    c2.metric(f"{latest} 관리자 제외", f"{exc:.2f}%")
    c3.metric("차이", f"{inc-exc:.2f}%p")

    fig = px.line(df, x="연도", y="비중", color="기준", markers=True, color_discrete_map=COLOR_MAP)
    st.plotly_chart(style_fig(fig, "관리자 포함 여부에 따른 화이트칼라 비중 추이"), use_container_width=True)

    fig2 = px.bar(latest_df, x="기준", y="비중", color="기준", text="비중", color_discrete_map=COLOR_MAP)
    fig2.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(style_fig(fig2, f"{latest}년 관리자 포함/제외 화이트칼라 비중 비교", height=420), use_container_width=True)

    insight("관리자는 화이트칼라에 포함할 수 있지만, 임금과 조직 내 지위가 높아 평균을 왜곡할 수 있다. 따라서 포함 기준과 제외 기준을 함께 제시하면 분류 기준에 대한 방어력이 커진다.")

elif page == "연령·학력별 특성":
    st.title("연령·학력별 직군 특성")
    period = "2024.1/2"
    age, edu = build_age_edu(period)
    note(f"연령·학력별 분석은 자료 제공 범위에 맞춰 **{period} 기준**으로 수행한다.")

    fig = px.bar(age, x="직군", y="비중", color="지표", text="비중", barmode="stack")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    st.plotly_chart(style_fig(fig, "직군별 연령 구성"), use_container_width=True)

    fig2 = px.bar(edu, x="직군", y="비중", color="지표", text="비중", barmode="stack")
    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    st.plotly_chart(style_fig(fig2, "직군별 학력 구성"), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 연령 구성 데이터")
        st.dataframe(age.round(2), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### 학력 구성 데이터")
        st.dataframe(edu.round(2), use_container_width=True, hide_index=True)

    insight("직군 차이는 단순히 직업명 차이가 아니라 인적 구성 차이와 연결된다. 특히 연령과 학력은 노동시장 구조를 설명하는 기본 변수이므로, 전체 추세 분석 뒤에 반드시 확인할 필요가 있다.")

elif page == "지역별 직군 분포":
    st.title("지역별 직군 분포")
    period = "2025.2/2"
    df = build_region_job(period)
    note(f"지역별 직군 분포는 **{period} 기준**으로 분석한다.")

    selected_group = st.selectbox("직군 선택", ["화이트칼라", "블루칼라", "기타"], index=0)
    top = df[df["직군"] == selected_group].sort_values("비중", ascending=False).head(10)
    fig = px.bar(top, x="비중", y="지역", orientation="h", color="비중", text="비중")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig, f"{selected_group} 비중 상위 지역 TOP10"), use_container_width=True)

    compare_regions = ["서울특별시", "세종특별자치시", "울산광역시", "경상남도", "경기도"]
    comp = df[df["지역"].isin(compare_regions)]
    fig2 = px.bar(comp, x="지역", y="비중", color="직군", barmode="group", text="비중", color_discrete_map=COLOR_MAP)
    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(style_fig(fig2, "주요 지역 직군 비중 비교"), use_container_width=True)

    st.dataframe(df.pivot(index="지역", columns="직군", values="비중").reset_index().round(2), use_container_width=True, hide_index=True)
    insight("지역별 직군 분포는 지역 산업 기반과 연결해 해석해야 한다. 예를 들어 제조업 기반 지역은 블루칼라 비중이, 행정·전문서비스 기능이 집중된 지역은 화이트칼라 비중이 높게 나타날 수 있다.")

elif page == "지역 산업구조 연결":
    st.title("지역 산업구조와 직군 분포 연결")
    year = "2025"
    region_job = build_region_job("2025.2/2")
    region_ind = build_region_industry(year)
    note(f"직군 분포는 2025년 하반기, 산업구조는 {year}년 연간 자료를 사용한다. 기준 시점이 완전히 같지 않으므로 인과관계가 아니라 연관성 중심으로 해석한다.")

    industries = {
        "제조업": "C 제조업(10~34)",
        "정보통신업": "J 정보통신업(58~63)",
        "전문·과학·기술서비스업": "M 전문, 과학 및 기술 서비스업(70~73)",
        "공공행정": "O 공공행정, 국방 및 사회보장 행정(84)",
        "건설업": "F 건설업(41~42)",
    }
    choice = st.selectbox("산업 선택", list(industries.keys()))
    ind_name = industries[choice]
    top = region_ind[region_ind["산업"] == ind_name].sort_values("비중", ascending=False).head(10)
    fig = px.bar(top, x="비중", y="지역", orientation="h", color="비중", text="비중")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig, f"{choice} 취업자 비중 상위 지역 TOP10"), use_container_width=True)

    # 핵심 지역 비교표
    target_regions = ["서울특별시", "세종특별자치시", "울산광역시", "경상남도", "경기도"]
    job_pivot = region_job[region_job["지역"].isin(target_regions)].pivot(index="지역", columns="직군", values="비중").reset_index()
    ind_pivot = region_ind[(region_ind["지역"].isin(target_regions)) & (region_ind["산업"].isin(industries.values()))]
    ind_pivot = ind_pivot.pivot(index="지역", columns="산업", values="비중").reset_index()
    merged = job_pivot.merge(ind_pivot, on="지역", how="left")
    st.markdown("#### 주요 지역: 직군 비중과 산업 비중 비교")
    st.dataframe(merged.round(2), use_container_width=True, hide_index=True)

    insight("이 페이지의 목적은 지역별 직군 차이를 산업구조와 연결해 설명하는 것이다. 단순히 어느 지역의 블루칼라 비중이 높다고 말하는 것보다, 해당 지역의 제조업·건설업·정보통신업·전문서비스업 비중을 함께 보면 해석력이 높아진다.")

elif page == "산업별 직군 구조":
    st.title("산업별 직군 구조")
    period = "2025.2/2"
    df = build_industry_job(period)
    note(f"산업별 직군 구조는 성별 '계', **{period} 기준**으로 분석한다.")

    selected_group = st.selectbox("비중 상위 산업을 볼 직군", ["화이트칼라", "블루칼라", "기타"], index=0)
    top = df[df["직군"] == selected_group].sort_values("비중", ascending=False).head(10)
    fig = px.bar(top, x="비중", y="산업", orientation="h", color="비중", text="비중")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig, f"{selected_group} 비중 높은 산업 TOP10"), use_container_width=True)

    major_keywords = ["제 조 업", "건 설 업", "운수", "정보통신", "금융", "전문, 과학", "교육", "보건업"]
    major = df[df["산업"].apply(lambda x: any(k in str(x) for k in major_keywords))].copy()
    fig2 = px.bar(major, x="산업", y="비중", color="직군", barmode="stack", text="비중", color_discrete_map=COLOR_MAP)
    fig2.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
    fig2.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(style_fig(fig2, "주요 산업별 직군 구성"), use_container_width=True)

    insight("산업별 직군 구조는 이 프로젝트의 핵심 분석 중 하나다. 화이트칼라 중심 산업과 블루칼라 중심 산업을 구분하면 전체 노동시장 변화가 산업구조와 연결되어 있다는 점을 보여줄 수 있다.")

elif page == "임금 분석":
    st.title("직군별 임금 분석")
    wage_jobs = build_wage(True)
    wage_group = build_wage_group()
    note("임금 자료는 2020~2025년 직업 대분류별 월임금총액을 사용한다. 직군 평균은 직업 대분류별 임금의 단순 평균이며, 취업자 수 가중평균이 아니라는 한계가 있다.")

    latest = wage_jobs["연도"].max()
    latest_jobs = wage_jobs[wage_jobs["연도"] == latest].dropna(subset=["직군"])
    fig = px.bar(latest_jobs, x="월임금총액", y="직종", orientation="h", color="직군", text="월임금총액", color_discrete_map=COLOR_MAP)
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig, f"{latest}년 직업 대분류별 월임금총액", height=560), use_container_width=True)

    fig2 = px.line(wage_group, x="연도", y="월임금총액", color="기준", markers=True)
    st.plotly_chart(style_fig(fig2, "2020~2025년 직군별 월임금총액 추이"), use_container_width=True)

    st.dataframe(wage_group.round(1), use_container_width=True, hide_index=True)
    insight("관리자는 임금 수준이 높아 화이트칼라 평균임금에 영향을 줄 수 있다. 따라서 관리자 포함 기준과 제외 기준을 함께 제시하면 임금 격차를 더 신중하게 해석할 수 있다.")

elif page == "성별 보조 분석":
    st.title("성별 직군 분포 보조 분석")
    df = build_gender_job()
    latest = df["연도"].max()
    latest_df = df[df["연도"] == latest]

    fig = px.bar(latest_df, x="성별", y="비중", color="직군", barmode="group", text="비중", color_discrete_map=COLOR_MAP)
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(style_fig(fig, f"{latest}년 성별 직군 비중 비교"), use_container_width=True)

    group = st.selectbox("추이 확인 직군", ["화이트칼라", "블루칼라", "기타"])
    trend = df[df["직군"] == group]
    fig2 = px.line(trend, x="연도", y="비중", color="성별", markers=True)
    st.plotly_chart(style_fig(fig2, f"2016~2025년 성별 {group} 비중 추이"), use_container_width=True)

    insight("성별 분석은 본 프로젝트의 핵심 축은 아니지만, 직군 구조 차이를 보조적으로 설명하는 데 활용할 수 있다. 발표 시간이 부족하면 이 페이지는 부록처럼 사용해도 된다.")

elif page == "결론 및 시사점":
    st.title("결론 및 시사점")
    annual = build_annual_job_group()
    mgr = build_manager_compare()
    latest = annual["연도"].max()
    first = annual["연도"].min()

    wc_latest = annual[(annual["연도"] == latest) & (annual["직군"] == "화이트칼라")]["비중"].iloc[0]
    wc_first = annual[(annual["연도"] == first) & (annual["직군"] == "화이트칼라")]["비중"].iloc[0]
    bc_latest = annual[(annual["연도"] == latest) & (annual["직군"] == "블루칼라")]["비중"].iloc[0]
    bc_first = annual[(annual["연도"] == first) & (annual["직군"] == "블루칼라")]["비중"].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("화이트칼라 변화", f"{wc_latest - wc_first:+.2f}%p")
    c2.metric("블루칼라 변화", f"{bc_latest - bc_first:+.2f}%p")
    c3.metric("분석 범위", "직업·지역·산업·임금")

    st.markdown("## 핵심 결론")
    conclusions = [
        "2016~2025년 전체 취업자 기준으로 화이트칼라와 블루칼라의 비중 변화가 확인된다.",
        "관리자 포함 여부는 화이트칼라 수치에 영향을 주지만, 핵심 추세를 검토하는 보조 기준으로 활용할 수 있다.",
        "직군별 연령·학력 구성은 서로 다르게 나타나며, 직군 구조는 인적 특성과 연결된다.",
        "지역별 직군 차이는 제조업, 공공행정, 정보통신업, 전문서비스업 등 지역 산업구조와 함께 해석할 필요가 있다.",
        "산업별로 화이트칼라 중심 산업과 블루칼라 중심 산업이 구분된다.",
        "임금 분석에서는 관리자 효과가 화이트칼라 평균에 미치는 영향을 별도로 고려해야 한다.",
    ]
    for i, txt in enumerate(conclusions, 1):
        st.markdown(f"<div class='note-box'><b>{i}.</b> {txt}</div>", unsafe_allow_html=True)

    st.markdown("## 최종 메시지")
    insight("한국 노동시장의 직군 변화는 단순히 화이트칼라 증가와 블루칼라 감소로만 볼 수 없다. 연령, 학력, 지역, 산업구조, 임금 차이가 함께 작용한 노동시장 구조 변화로 해석해야 한다.")
