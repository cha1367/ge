from pathlib import Path
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================
# Streamlit 기본 설정
# ==========================================================
st.set_page_config(
    page_title="대한민국 노동시장 직군 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
YEARS = [str(y) for y in range(2016, 2026)]
LATEST_YEAR = "2025"
LATEST_HALF = "2025.2/2"
AGE_EDU_PERIOD = "2024.1/2"

WHITE_JOBS = ["관리자", "전문가 및 관련 종사자", "사무 종사자"]
BLUE_JOBS = ["기능원 및 관련 기능 종사자", "장치·기계 조작 및 조립 종사자", "단순노무 종사자"]
OTHER_JOBS = ["서비스 종사자", "판매 종사자", "농림어업 숙련 종사자"]
JOB_ORDER = ["화이트칼라", "블루칼라", "기타"]
COLOR_MAP = {"화이트칼라": "#38BDF8", "블루칼라": "#FB923C", "기타": "#94A3B8"}

FILE_PATTERNS = {
    "employment_yearly": ["직업별_취업자_연도별.csv"],
    "region_job": ["시도별_직업별.csv"],
    "age_edu": ["직업별_학력별.csv"],
    "wage_with_manager": ["관리자 포함.csv"],
    "wage_without_manager": ["관리자 미 포함.csv"],
    "region_industry": ["행정구역_시도__산업별_취업자*.csv"],
    "industry_job": ["전국_성별_산업_직업별_취업자_대분류*.csv"],
}

# ==========================================================
# CSS 디자인 - 다크 테마
# ==========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top left, #1E293B 0, #0B1120 34%, #020617 100%);
        color: #E5E7EB;
    }
    .main .block-container {
        padding-top: 2.0rem;
        padding-bottom: 3rem;
        max-width: 1320px;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0F172A 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.25);
    }
    section[data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }
    .main-title {
        font-size: 2.45rem;
        font-weight: 850;
        color: #F8FAFC;
        line-height: 1.25;
        letter-spacing: -0.035em;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 1.08rem;
        color: #CBD5E1;
        margin-bottom: 1.4rem;
    }
    .page-title {
        font-size: 1.95rem;
        font-weight: 820;
        color: #F8FAFC;
        letter-spacing: -0.03em;
        margin-bottom: 0.45rem;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 760;
        color: #F8FAFC;
        margin-top: 1.2rem;
        margin-bottom: 0.55rem;
    }
    .soft-card, .info-card {
        background: rgba(15, 23, 42, 0.82);
        padding: 1.25rem 1.35rem;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 14px 34px rgba(0,0,0,0.34);
        margin-bottom: 1rem;
        color: #E5E7EB;
    }
    .blue-card {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.18) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 1.25rem 1.35rem;
        border-radius: 18px;
        border: 1px solid rgba(56, 189, 248, 0.32);
        margin-bottom: 1rem;
        color: #E0F2FE;
    }
    .reason-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 24, 39, 0.92) 100%);
        padding: 1.15rem 1.25rem;
        border-radius: 16px;
        border-left: 5px solid #38BDF8;
        border-top: 1px solid rgba(148, 163, 184, 0.18);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        margin: 0.8rem 0 1.2rem 0;
        color: #DDEAFE;
    }
    .insight-card {
        background: linear-gradient(135deg, rgba(22, 101, 52, 0.28) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 1.2rem 1.3rem;
        border-radius: 16px;
        border: 1px solid rgba(34, 197, 94, 0.35);
        margin-top: 1rem;
        color: #DCFCE7;
    }
    .warning-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%);
        padding: 1.15rem 1.25rem;
        border-radius: 16px;
        border: 1px solid rgba(251, 191, 36, 0.34);
        margin: 0.8rem 0 1.1rem 0;
        color: #FEF3C7;
    }
    .kpi-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        padding: 1.15rem 1.1rem;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.26);
        box-shadow: 0 10px 26px rgba(0,0,0,0.28);
        min-height: 118px;
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 0.88rem;
        font-weight: 650;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 1.65rem;
        font-weight: 850;
        letter-spacing: -0.02em;
    }
    
    div[data-testid="stPlotlyChart"] {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 16px;
        padding: 0.35rem 0.35rem 0.15rem 0.35rem;
    }

    .kpi-sub {
        color: #38BDF8;
        font-size: 0.84rem;
        margin-top: 0.45rem;
    }
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #E5E7EB;
        line-height: 1.72;
    }
    h1, h2, h3, h4 { color: #F8FAFC !important; }
    hr { border-color: rgba(148, 163, 184, 0.28); }
    div[data-testid="stPlotlyChart"] {
        background: rgba(15, 23, 42, 0.68);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 0.45rem;
        box-shadow: 0 10px 26px rgba(0,0,0,0.22);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 공통 유틸 함수
# ==========================================================
def html_card(title: str, body: str, kind: str = "soft-card"):
    st.markdown(f"""<div class="{kind}"><b>{title}</b><br>{body}</div>""", unsafe_allow_html=True)


def page_header(title: str, question: str | None = None, reason: str | None = None):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if question:
        st.markdown(f"<div class='blue-card'><b>분석 질문</b><br>{question}</div>", unsafe_allow_html=True)
    if reason:
        st.markdown(f"<div class='reason-card'><b>이 분석을 선택한 이유</b><br>{reason}</div>", unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def find_file(key: str) -> Path | None:
    patterns = FILE_PATTERNS[key]
    for pattern in patterns:
        matches = sorted(DATA_DIR.glob(pattern))
        if matches:
            return matches[0]
    return None


def read_csv_smart(path: Path) -> pd.DataFrame:
    last_error = None
    for enc in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            last_error = e
    raise RuntimeError(f"CSV 파일을 읽을 수 없습니다: {path.name} / {last_error}")


def clean_number(s):
    if pd.isna(s):
        return np.nan
    txt = str(s).strip().replace(",", "")
    if txt in ["-", "", "nan", "NaN", "취업자 (천명)", "월임금총액 (천원)"]:
        return np.nan
    return pd.to_numeric(txt, errors="coerce")


def to_numeric_frame(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = out[c].map(clean_number)
    return out


def normalize_job(job: str) -> str:
    job = str(job).strip()
    job = job.replace("∙", "·").replace("ㆍ", "·")
    job = re.sub(r"^\*\s*", "", job)
    job = re.sub(r"^\d+\s*", "", job)
    job = re.sub(r"\([^)]*\)", "", job).strip()
    job = re.sub(r"\s+", " ", job)
    if "전문가" in job:
        return "전문가 및 관련 종사자"
    if "사무" in job:
        return "사무 종사자"
    if "서비스" in job:
        return "서비스 종사자"
    if "판매" in job:
        return "판매 종사자"
    if "농림어업" in job:
        return "농림어업 숙련 종사자"
    if "기능원" in job:
        return "기능원 및 관련 기능 종사자"
    if "장치" in job or "기계" in job or "조립" in job:
        return "장치·기계 조작 및 조립 종사자"
    if "단순" in job:
        return "단순노무 종사자"
    if "관리자" in job:
        return "관리자"
    return job


def classify_job(job: str, include_manager: bool = True) -> str:
    job_std = normalize_job(job)
    if job_std == "관리자":
        return "화이트칼라" if include_manager else "기타"
    if job_std in ["전문가 및 관련 종사자", "사무 종사자"]:
        return "화이트칼라"
    if job_std in BLUE_JOBS:
        return "블루칼라"
    if job_std in OTHER_JOBS:
        return "기타"
    return "기타"


def is_base_job(job: str) -> bool:
    return normalize_job(job) in WHITE_JOBS + BLUE_JOBS + OTHER_JOBS


def normalize_industry(industry: str) -> str:
    """KOSIS 산업명 정규화.

    원본에는 `C. 제 조 업(10~34)`처럼 코드, 점, 괄호, 불필요한 공백이
    섞여 있다. 그대로 두면 `제조업`, `건설업` 같은 주요 산업 리스트와
    매칭되지 않아 차트가 빈 그래프로 출력된다.
    """
    s = str(industry).strip()
    if s in ["", "nan", "None"]:
        return ""

    # 앞쪽 묶음 표시(*)와 산업 코드(A., B. 등) 제거
    s = re.sub(r"^\*\s*", "", s)
    s = re.sub(r"^[A-Z]\.\s*", "", s)
    s = re.sub(r"^[A-Z]\s+", "", s)

    # 괄호 속 산업코드 제거: (10~34) 등
    s = re.sub(r"\([^)]*\)", "", s).strip()
    s = re.sub(r"\s+", " ", s)

    # 매칭용: 모든 공백 제거
    compact = re.sub(r"\s+", "", s)

    # 주요 산업명 표준화
    if compact == "계":
        return "계"
    if "농업" in compact and "임업" in compact and "어업" in compact:
        return "농업, 임업 및 어업"
    if compact in ["광업", "광업"]:
        return "광업"
    if compact == "제조업":
        return "제조업"
    if "전기" in compact and "가스" in compact:
        return "전기, 가스, 증기 및 공기조절 공급업"
    if "수도" in compact and "폐기물" in compact:
        return "수도, 하수 및 폐기물 처리, 원료 재생업"
    if compact == "건설업":
        return "건설업"
    if "도매" in compact and "소매" in compact:
        return "도매 및 소매업"
    if "운수" in compact and "창고" in compact:
        return "운수 및 창고업"
    if "숙박" in compact and "음식점" in compact:
        return "숙박 및 음식점업"
    if "정보통신" in compact:
        return "정보통신업"
    if "금융" in compact and "보험" in compact:
        return "금융 및 보험업"
    if "부동산" in compact:
        return "부동산업"
    if "전문" in compact and "과학" in compact and "기술" in compact:
        return "전문, 과학 및 기술 서비스업"
    if "사업시설" in compact and "사업지원" in compact:
        return "사업시설 관리, 사업 지원 및 임대 서비스업"
    if "공공행정" in compact or "국방" in compact:
        return "공공행정, 국방 및 사회보장 행정"
    if "교육서비스" in compact:
        return "교육 서비스업"
    if "보건업" in compact or "사회복지" in compact:
        return "보건업 및 사회복지 서비스업"
    if "예술" in compact and "스포츠" in compact:
        return "예술, 스포츠 및 여가관련 서비스업"
    if "협회" in compact and "수리" in compact:
        return "협회 및 단체, 수리 및 기타 개인 서비스업"
    if "가구내고용" in compact:
        return "가구 내 고용활동"
    if "국제" in compact and "외국기관" in compact:
        return "국제 및 외국기관"

    return s


def chart_layout(fig, height=420, showlegend=True):
    """다크 테마에서도 범례, 축, 라벨이 또렷하게 보이도록 통일 레이아웃 적용"""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=20, r=20, t=72, b=54),
        font=dict(family="Noto Sans KR, Arial", size=13, color="#F8FAFC"),
        title=dict(font=dict(size=18, color="#F8FAFC"), x=0.02),
        paper_bgcolor="rgba(15,23,42,0.98)",
        plot_bgcolor="rgba(15,23,42,0.92)",
        showlegend=showlegend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="left",
            x=0,
            bgcolor="rgba(15,23,42,0.96)",
            bordercolor="rgba(148,163,184,0.45)",
            borderwidth=1,
            font=dict(size=13, color="#F8FAFC"),
            traceorder="normal",
            itemclick="toggleothers",
            itemdoubleclick="toggle",
        ),
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.98)",
            bordercolor="#38BDF8",
            font=dict(color="#F8FAFC", size=13),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)",
        tickfont=dict(color="#E2E8F0", size=12),
        title_font=dict(color="#F8FAFC", size=13),
        color="#E2E8F0",
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)",
        tickfont=dict(color="#E2E8F0", size=12),
        title_font=dict(color="#F8FAFC", size=13),
        color="#E2E8F0",
    )
    return fig


def stacked_bar_100(df, x_col, category_col, value_col, title, x_title="", y_title="비중(%)"):
    fig = px.bar(
        df,
        x=x_col,
        y=value_col,
        color=category_col,
        color_discrete_map=COLOR_MAP,
        category_orders={category_col: JOB_ORDER},
        text=df[value_col].map(lambda v: f"{v:.1f}%" if pd.notna(v) and v >= 7 else ""),
        title=title,
    )
    fig.update_traces(textposition="inside", insidetextanchor="middle", textfont=dict(color="#F8FAFC", size=12), marker_line_color="rgba(255,255,255,0.08)", marker_line_width=0.6)
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100], title=y_title)
    fig.update_xaxes(title=x_title)
    return chart_layout(fig, height=430)

# ==========================================================
# 데이터 로드 및 전처리
# ==========================================================
@st.cache_data(show_spinner=False)
def load_all_data():
    missing = []
    paths = {}
    for k in FILE_PATTERNS:
        p = find_file(k)
        if p is None:
            missing.append(k)
        else:
            paths[k] = p
    if missing:
        raise FileNotFoundError(
            "data 폴더에서 필요한 CSV를 찾지 못했습니다: " + ", ".join(missing)
        )

    raw = {k: read_csv_smart(p) for k, p in paths.items()}
    return raw, {k: str(v.name) for k, v in paths.items()}


def prepare_yearly_employment(df: pd.DataFrame) -> pd.DataFrame:
    year_cols = [c for c in df.columns if c in YEARS]
    data = df.copy()
    data = data[data["직업별"].map(is_base_job)].copy()
    data["직업표준"] = data["직업별"].map(normalize_job)
    data["직군"] = data["직업별"].map(lambda x: classify_job(x, include_manager=True))
    data = to_numeric_frame(data, year_cols)
    long = data.melt(id_vars=["직업표준", "직군"], value_vars=year_cols, var_name="연도", value_name="취업자")
    long["취업자"] = pd.to_numeric(long["취업자"], errors="coerce")

    totals = df[df["직업별"].astype(str).str.strip().eq("계")][year_cols].iloc[0].map(clean_number)
    total_df = pd.DataFrame({"연도": year_cols, "전체취업자": [totals[y] for y in year_cols]})
    grouped = long.groupby(["연도", "직군"], as_index=False)["취업자"].sum()
    grouped = grouped.merge(total_df, on="연도", how="left")
    grouped["비중"] = grouped["취업자"] / grouped["전체취업자"] * 100
    grouped["직군"] = pd.Categorical(grouped["직군"], JOB_ORDER, ordered=True)
    return grouped.sort_values(["연도", "직군"])


def prepare_manager_compare(df: pd.DataFrame) -> pd.DataFrame:
    year_cols = [c for c in df.columns if c in YEARS]
    data = df.copy()
    data = data[data["직업별"].map(is_base_job)].copy()
    data["직업표준"] = data["직업별"].map(normalize_job)
    data = to_numeric_frame(data, year_cols)
    long = data.melt(id_vars=["직업표준"], value_vars=year_cols, var_name="연도", value_name="취업자")
    totals = df[df["직업별"].astype(str).str.strip().eq("계")][year_cols].iloc[0].map(clean_number)

    rows = []
    for year in year_cols:
        d = long[long["연도"] == year]
        total = totals[year]
        included = d[d["직업표준"].isin(WHITE_JOBS)]["취업자"].sum()
        excluded = d[d["직업표준"].isin(["전문가 및 관련 종사자", "사무 종사자"])] ["취업자"].sum()
        rows.append({"연도": year, "기준": "관리자 포함", "비중": included / total * 100})
        rows.append({"연도": year, "기준": "관리자 제외", "비중": excluded / total * 100})
    return pd.DataFrame(rows)


def prepare_region_job(df: pd.DataFrame, period: str = LATEST_HALF) -> pd.DataFrame:
    data = df.copy()
    if data.iloc[0].astype(str).str.contains("취업자").any():
        data = data.iloc[1:].copy()
    data[period] = data[period].map(clean_number)
    totals = data[data["직업별"].astype(str).str.strip().eq("계")][["행정구역별", period]].rename(columns={period: "전체취업자"})
    detail = data[data["직업별"].map(is_base_job)].copy()
    detail["직군"] = detail["직업별"].map(lambda x: classify_job(x, True))
    grouped = detail.groupby(["행정구역별", "직군"], as_index=False)[period].sum().rename(columns={period: "취업자"})
    out = grouped.merge(totals, on="행정구역별", how="left")
    out["비중"] = out["취업자"] / out["전체취업자"] * 100
    out = out[out["행정구역별"] != "계"].copy()
    return out


def prepare_region_industry(df: pd.DataFrame, year: str = LATEST_YEAR) -> pd.DataFrame:
    data = df.copy()
    data[year] = data[year].map(clean_number)
    data["산업표준"] = data["산업별"].map(normalize_industry)
    total = data[data["산업별"].astype(str).str.strip().eq("계")][["시도별", year]].rename(columns={year: "전체취업자"})
    out = data.merge(total, on="시도별", how="left")
    out["비중"] = out[year] / out["전체취업자"] * 100
    out = out[out["시도별"] != "계"].copy()
    return out


def prepare_industry_job(df: pd.DataFrame, period: str = LATEST_HALF) -> pd.DataFrame:
    data = df.copy()
    if data.iloc[0].astype(str).str.contains("취업자").any():
        data = data.iloc[1:].copy()
    data = data[(data["성별"].astype(str).str.strip() == "계")].copy()
    data[period] = data[period].map(clean_number)
    data["산업표준"] = data["산업별"].map(normalize_industry)
    detail = data[(data["산업별"].astype(str).str.strip() != "계") & data["직업별"].map(is_base_job)].copy()
    detail["직군"] = detail["직업별"].map(lambda x: classify_job(x, True))
    grouped = detail.groupby(["산업표준", "직군"], as_index=False)[period].sum().rename(columns={period: "취업자"})
    total = grouped.groupby("산업표준", as_index=False)["취업자"].sum().rename(columns={"취업자": "산업취업자"})
    out = grouped.merge(total, on="산업표준", how="left")
    out["비중"] = out["취업자"] / out["산업취업자"] * 100
    out = out[out["산업취업자"] > 0].copy()
    return out


def prepare_wage(df_wage: pd.DataFrame, emp_df: pd.DataFrame):
    year_cols = [c for c in df_wage.columns if c in ["2020", "2021", "2022", "2023", "2024", "2025"]]
    data = df_wage.copy()
    if data.iloc[0].astype(str).str.contains("월임금").any():
        data = data.iloc[1:].copy()
    data = data[data["직종별"].map(is_base_job)].copy()
    data["직업표준"] = data["직종별"].map(normalize_job)
    data = to_numeric_frame(data, year_cols)
    wage_long = data.melt(id_vars=["직업표준"], value_vars=year_cols, var_name="연도", value_name="월임금")

    emp = emp_df.copy()
    emp = emp[emp["직업별"].map(is_base_job)].copy()
    emp["직업표준"] = emp["직업별"].map(normalize_job)
    emp = to_numeric_frame(emp, year_cols)
    emp_long = emp.melt(id_vars=["직업표준"], value_vars=year_cols, var_name="연도", value_name="취업자")

    merged = wage_long.merge(emp_long, on=["직업표준", "연도"], how="left")
    rows = []
    for year, d in merged.groupby("연도"):
        white_inc = d[d["직업표준"].isin(WHITE_JOBS)]
        white_exc = d[d["직업표준"].isin(["전문가 및 관련 종사자", "사무 종사자"])]
        blue = d[d["직업표준"].isin(BLUE_JOBS)]
        for label, sub in [("화이트칼라(관리자 포함)", white_inc), ("화이트칼라(관리자 제외)", white_exc), ("블루칼라", blue)]:
            sub = sub.dropna(subset=["월임금", "취업자"])
            if sub.empty or sub["취업자"].sum() == 0:
                val = np.nan
            else:
                val = (sub["월임금"] * sub["취업자"]).sum() / sub["취업자"].sum()
            rows.append({"연도": year, "구분": label, "월임금": val})
    comparison = pd.DataFrame(rows)
    latest_job = wage_long[wage_long["연도"] == LATEST_YEAR].dropna().sort_values("월임금", ascending=False)
    return wage_long, comparison, latest_job


def prepare_age_edu(df: pd.DataFrame, period: str = AGE_EDU_PERIOD):
    data = df.copy()
    # 첫 행은 계량항목명이다.
    measure_map = data.iloc[0].to_dict()
    data = data.iloc[1:].copy()
    data = data[data["직업별"].map(is_base_job)].copy()
    data["직업표준"] = data["직업별"].map(normalize_job)
    data["직군"] = data["직업별"].map(lambda x: classify_job(x, True))

    period_cols = [c for c in df.columns if c == period or c.startswith(period + ".")]
    rows = []
    for _, r in data.iterrows():
        for c in period_cols:
            measure = str(measure_map.get(c, c)).strip()
            rows.append({
                "직업표준": r["직업표준"],
                "직군": r["직군"],
                "항목": measure,
                "값": clean_number(r[c]),
            })
    long = pd.DataFrame(rows).dropna(subset=["값"])
    grouped = long.groupby(["직군", "항목"], as_index=False)["값"].sum()

    age = grouped[grouped["항목"].str.contains("연령", na=False)].copy()
    age["세부항목"] = age["항목"].str.replace("연령", "", regex=False).str.replace("(", "", regex=False).str.replace(")", "", regex=False)
    age_total = age.groupby("직군", as_index=False)["값"].sum().rename(columns={"값": "직군합계"})
    age = age.merge(age_total, on="직군")
    age["비중"] = age["값"] / age["직군합계"] * 100

    edu = grouped[grouped["항목"].str.contains("교육정도", na=False)].copy()
    edu["세부항목"] = edu["항목"].str.replace("교육정도", "", regex=False).str.replace("(", "", regex=False).str.replace(")", "", regex=False)
    edu_total = edu.groupby("직군", as_index=False)["값"].sum().rename(columns={"값": "직군합계"})
    edu = edu.merge(edu_total, on="직군")
    edu["비중"] = edu["값"] / edu["직군합계"] * 100
    return age, edu

# ==========================================================
# 차트 생성 함수
# ==========================================================
def fig_trend(job_share: pd.DataFrame):
    fig = px.line(
        job_share,
        x="연도", y="비중", color="직군",
        markers=True,
        color_discrete_map=COLOR_MAP,
        category_orders={"직군": JOB_ORDER},
        title="2016~2025 직군별 취업자 비중 변화",
    )
    fig.update_yaxes(title="전체 취업자 대비 비중(%)", ticksuffix="%")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 430)


def fig_pie_latest(job_share: pd.DataFrame):
    latest = job_share[job_share["연도"] == LATEST_YEAR].copy()
    fig = px.pie(
        latest,
        names="직군", values="취업자", hole=0.55,
        color="직군", color_discrete_map=COLOR_MAP,
        title=f"{LATEST_YEAR}년 직군 구성",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return chart_layout(fig, 410)


def fig_count_trend(job_share: pd.DataFrame):
    fig = px.line(
        job_share,
        x="연도", y="취업자", color="직군",
        markers=True,
        color_discrete_map=COLOR_MAP,
        category_orders={"직군": JOB_ORDER},
        title="2016~2025 직군별 취업자 수 추이",
    )
    fig.update_yaxes(title="취업자 수(천명)")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 430)


def fig_manager_own_share(manager_df: pd.DataFrame):
    pivot = manager_df.pivot(index="연도", columns="기준", values="비중").reset_index()
    if {"관리자 포함", "관리자 제외"}.issubset(pivot.columns):
        pivot["관리자 비중"] = pivot["관리자 포함"] - pivot["관리자 제외"]
    else:
        pivot["관리자 비중"] = np.nan
    fig = px.line(
        pivot,
        x="연도", y="관리자 비중",
        markers=True,
        title="전체 취업자 중 관리자 비중 추이",
    )
    fig.update_traces(line_color="#A78BFA")
    fig.update_yaxes(title="비중(%)", ticksuffix="%")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 400, False)


def fig_single_ratio_bar(df: pd.DataFrame, item_name: str, title: str, color: str = "#60A5FA"):
    d = df[df["세부항목"].astype(str).eq(item_name)].copy()
    d = d.sort_values("비중", ascending=True)
    fig = px.bar(
        d,
        x="비중",
        y="직군",
        orientation="h",
        text=d["비중"].map(lambda v: f"{v:.1f}%"),
        title=title,
    )
    fig.update_traces(marker_color=color, textposition="outside")
    fig.update_xaxes(title="비중(%)", ticksuffix="%")
    fig.update_yaxes(title="")
    return chart_layout(fig, 360, False)


def fig_region_industry_scatter(region_job: pd.DataFrame, region_industry: pd.DataFrame):
    blue = region_job[region_job["직군"].eq("블루칼라")][["행정구역별", "비중"]].rename(
        columns={"행정구역별": "지역", "비중": "블루칼라 비중"}
    )
    manu = region_industry[region_industry["산업표준"].eq("제조업")][["시도별", "비중"]].rename(
        columns={"시도별": "지역", "비중": "제조업 비중"}
    )
    d = blue.merge(manu, on="지역", how="inner").dropna()
    if d.empty:
        return None
    fig = px.scatter(
        d,
        x="제조업 비중",
        y="블루칼라 비중",
        text="지역",
        title="제조업 비중과 블루칼라 비중의 관계",
        hover_name="지역",
    )
    fig.update_traces(
        marker=dict(size=12, color="#F97316", line=dict(width=1, color="#FED7AA")),
        textposition="top center",
        textfont=dict(color="#F8FAFC", size=11),
    )
    fig.update_xaxes(title="제조업 취업자 비중(%)", ticksuffix="%")
    fig.update_yaxes(title="블루칼라 비중(%)", ticksuffix="%")
    return chart_layout(fig, 470, False)


def fig_wage_gap(wage_group: pd.DataFrame):
    pivot = wage_group.pivot(index="연도", columns="구분", values="월임금").reset_index()
    if {"화이트칼라(관리자 제외)", "블루칼라"}.issubset(pivot.columns):
        pivot["임금격차"] = pivot["화이트칼라(관리자 제외)"] - pivot["블루칼라"]
    else:
        pivot["임금격차"] = np.nan
    fig = px.line(
        pivot,
        x="연도", y="임금격차",
        markers=True,
        title="화이트칼라(관리자 제외)와 블루칼라 임금 격차 추이",
    )
    fig.update_traces(line_color="#FBBF24")
    fig.update_yaxes(title="월임금 격차(천원)")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 390, False)


def fig_selected_industry(industry_job: pd.DataFrame, selected_industry: str):
    d = industry_job[industry_job["산업표준"].eq(selected_industry)].copy()
    if d.empty:
        return None
    d["직군"] = pd.Categorical(d["직군"], JOB_ORDER, ordered=True)
    d = d.sort_values("직군")
    fig = px.bar(
        d,
        x="직군",
        y="비중",
        color="직군",
        color_discrete_map=COLOR_MAP,
        text=d["비중"].map(lambda v: f"{v:.1f}%"),
        title=f"{selected_industry} 직군 구성",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(title="비중(%)", ticksuffix="%", range=[0, max(100, d["비중"].max() * 1.15)])
    fig.update_xaxes(title="")
    return chart_layout(fig, 390, False)


def fig_manager_bar(manager_df: pd.DataFrame):
    latest = manager_df[manager_df["연도"] == LATEST_YEAR].copy()
    fig = px.bar(latest, x="기준", y="비중", text=latest["비중"].map(lambda v: f"{v:.2f}%"), title="2025년 관리자 포함/제외 화이트칼라 비중")
    fig.update_traces(marker_color=["#38BDF8", "#0EA5E9"], textposition="outside")
    fig.update_yaxes(title="비중(%)", ticksuffix="%")
    fig.update_xaxes(title="")
    return chart_layout(fig, 400, False)


def fig_manager_line(manager_df: pd.DataFrame):
    fig = px.line(manager_df, x="연도", y="비중", color="기준", markers=True, title="관리자 포함/제외 기준별 화이트칼라 비중 추이")
    fig.update_yaxes(title="비중(%)", ticksuffix="%")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 420)


def fig_top_bar(df: pd.DataFrame, label_col: str, value_col: str, title: str, color: str = "#2563EB", suffix="%"):
    d = df.sort_values(value_col, ascending=True).copy()
    fig = px.bar(d, x=value_col, y=label_col, orientation="h", text=d[value_col].map(lambda v: f"{v:.1f}{suffix}"), title=title)
    fig.update_traces(marker_color=color, textposition="outside")
    fig.update_xaxes(title=f"비중({suffix})" if suffix == "%" else "값", ticksuffix=suffix if suffix == "%" else "")
    fig.update_yaxes(title="")
    return chart_layout(fig, 410, False)


def fig_wage_bar(latest_job: pd.DataFrame):
    d = latest_job.copy()
    d = d[d["직업표준"].isin(WHITE_JOBS + BLUE_JOBS)].sort_values("월임금", ascending=True)
    fig = px.bar(
        d,
        x="월임금", y="직업표준", orientation="h",
        text=d["월임금"].map(lambda v: f"{v:,.0f}"),
        title="2025년 직업 대분류별 월임금총액",
    )
    fig.update_traces(marker_color="#94A3B8", textposition="outside")
    fig.update_xaxes(title="월임금총액(천원)")
    fig.update_yaxes(title="")
    return chart_layout(fig, 440, False)


def fig_wage_compare(wage_group: pd.DataFrame):
    d = wage_group[wage_group["연도"] == LATEST_YEAR].copy()
    order = ["화이트칼라(관리자 포함)", "화이트칼라(관리자 제외)", "블루칼라"]
    d["구분"] = pd.Categorical(d["구분"], order, ordered=True)
    d = d.sort_values("구분")
    fig = px.bar(d, x="구분", y="월임금", text=d["월임금"].map(lambda v: f"{v:,.0f}"), title="2025년 직군별 가중평균 월임금 비교")
    fig.update_traces(marker_color=["#38BDF8", "#0EA5E9", "#FB923C"], textposition="outside")
    fig.update_yaxes(title="월임금총액(천원)")
    fig.update_xaxes(title="")
    return chart_layout(fig, 410, False)


def fig_wage_line(wage_group: pd.DataFrame):
    d = wage_group[wage_group["구분"].isin(["화이트칼라(관리자 제외)", "블루칼라"])]
    fig = px.line(d, x="연도", y="월임금", color="구분", markers=True, title="2020~2025 직군별 월임금 추이")
    fig.update_yaxes(title="월임금총액(천원)")
    fig.update_xaxes(title="연도")
    return chart_layout(fig, 430)

# ==========================================================
# 페이지 함수
# ==========================================================
def page_intro(file_names):
    st.markdown("<div class='main-title'>대한민국 노동시장의 직군 분포 변화와 산업구조 특성 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>화이트칼라와 블루칼라를 중심으로 보는 2016~2025년 노동시장 구조 변화</div>", unsafe_allow_html=True)

    html_card(
        "프로젝트 배경",
        "화이트칼라와 블루칼라는 오랫동안 서로 다른 직업군으로 인식되어 왔다. 최근에는 반도체, 정유, 생산기술직 등 고임금 기술직이 주목받으면서 블루칼라 직군에 대한 관심도 다시 커지고 있다. 그러나 이러한 인식 변화가 실제 노동시장 구조와 일치하는지는 데이터로 확인해야 한다. 본 대시보드는 국가 통계 데이터를 활용해 직군 분포 변화, 인적 특성, 지역 차이, 임금 차이, 산업별 직군 구조를 종합적으로 분석한다.",
        "blue-card",
    )

    st.markdown("<div class='section-title'>문제 제기</div>", unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        html_card("질문 1", "대한민국 노동시장에서 화이트칼라와 블루칼라는 실제로 어떻게 분포하고 있는가?")
        html_card("질문 2", "2016년부터 2025년까지 두 직군의 비중은 어떻게 변화했는가?")
    with q2:
        html_card("질문 3", "연령, 학력, 지역, 임금 측면에서 두 직군은 어떤 차이를 보이는가?")
        html_card("질문 4", "산업구조에 따라 화이트칼라와 블루칼라의 구성은 어떻게 달라지는가?")

    st.markdown("<div class='section-title'>분석 목표</div>", unsafe_allow_html=True)
    goals = [
        "화이트칼라와 블루칼라의 분포 변화를 분석한다.",
        "연령별 직군 특성을 분석한다.",
        "학력별 직군 특성을 분석한다.",
        "지역별 직군 분포 차이를 분석한다.",
        "직군별 임금 수준 및 변화 추이를 분석한다.",
        "산업별 직군 구조와 산업구조에 따른 직군 분포 차이를 분석한다.",
    ]
    cols = st.columns(3)
    for i, goal in enumerate(goals):
        with cols[i % 3]:
            html_card(f"목표 {i+1}", goal)

    st.markdown("<div class='section-title'>직군 분류 기준</div>", unsafe_allow_html=True)
    class_df = pd.DataFrame({
        "구분": ["화이트칼라", "화이트칼라", "화이트칼라", "블루칼라", "블루칼라", "블루칼라", "기타", "기타", "기타"],
        "직업 대분류": [
            "관리자", "전문가 및 관련 종사자", "사무 종사자",
            "기능원 및 관련 기능 종사자", "장치·기계 조작 및 조립 종사자", "단순노무 종사자",
            "서비스 종사자", "판매 종사자", "농림어업 숙련 종사자"
        ],
        "설명": [
            "조직의 정책, 사업, 인력, 예산, 업무 방향을 기획·지휘·조정하는 직군",
            "전문지식과 기술을 바탕으로 연구, 교육, 보건, 공학, 법률 등의 업무를 수행하는 직군",
            "행정, 회계, 문서관리, 고객관리, 조직 운영 지원 등 사무 기반 업무를 수행하는 직군",
            "숙련기술을 바탕으로 제조, 건설, 수리, 설치 등의 작업을 수행하는 직군",
            "기계장치 조작, 생산설비 운영, 제품 조립 등의 업무를 수행하는 직군",
            "비교적 단순하고 반복적인 육체노동 또는 현장 보조 업무를 수행하는 직군",
            "대면 서비스, 돌봄, 음식, 미용, 보안 등 서비스 제공 업무",
            "상품 판매, 영업, 매장 운영 등 판매 중심 업무",
            "농업, 임업, 어업 관련 숙련 업무",
        ]
    })
    st.dataframe(class_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-title'>기타 직군은 무엇인가?</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-card'>
    <b>기타 직군</b>은 화이트칼라 또는 블루칼라 중 하나로 단정하기 어려운 직업군을 따로 묶은 것이다.
    서비스 종사자, 판매 종사자, 농림어업 숙련 종사자가 여기에 해당한다.<br><br>
    <ul>
      <li><b>서비스 종사자</b>: 음식, 숙박, 미용, 돌봄, 보안, 경비, 청소 등 대면 서비스 중심 업무</li>
      <li><b>판매 종사자</b>: 상품 판매, 매장 관리, 영업, 고객 응대 등 판매 중심 업무</li>
      <li><b>농림어업 숙련 종사자</b>: 농업, 임업, 어업 분야에서 숙련 기능을 바탕으로 일하는 직군</li>
    </ul>
    이 직군들은 사무·전문직 중심의 화이트칼라와도 다르고, 제조·건설·기계조작 중심의 블루칼라와도 다르다.
    따라서 억지로 한쪽에 포함하지 않고 <b>기타</b>로 분리해 전체 노동시장 구조를 더 정확하게 보여준다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='warn-card'><b>관리자를 화이트칼라에 포함한 이유</b><br>관리자는 직접 생산이나 단순노무를 수행하는 직군이라기보다 조직의 정책, 사업, 인력, 예산, 업무 방향을 기획·조정·지휘하는 직군이다. 따라서 비육체노동, 조직관리, 의사결정 중심 직무라는 점에서 화이트칼라에 포함했다. 다만 관리자는 임금 수준이 높고 평균값에 영향을 줄 수 있으므로, 별도 페이지에서 관리자 포함/제외 기준을 함께 비교한다.</div>", unsafe_allow_html=True)

    manager_detail = pd.DataFrame({
        "관리자 세부 예시": [
            "공공 기관 및 기업 고위직",
            "행정·경영 지원 및 마케팅 관리직",
            "전문 서비스 관리직",
            "건설·전기 및 생산 관련 관리직",
            "판매 및 고객 서비스 관리직",
        ],
        "역할": [
            "조직 전체의 전략, 정책, 방향을 결정",
            "행정, 경영지원, 마케팅 조직의 업무를 관리",
            "전문서비스 분야의 사업과 인력을 관리",
            "건설, 전기, 생산 현장의 운영과 공정을 관리",
            "판매조직과 고객서비스 조직의 운영을 관리",
        ]
    })
    st.markdown("<div class='section-title'>관리자에는 어떤 직무가 포함되는가?</div>", unsafe_allow_html=True)
    st.dataframe(manager_detail, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-title'>사용 데이터</div>", unsafe_allow_html=True)
    data_intro = pd.DataFrame({
        "데이터": [
            "직업별 취업자 연도별 데이터", "시도별 직업별 데이터", "직업별 연령·학력 데이터",
            "직업별 임금 데이터", "시도별 산업별 취업자 데이터", "산업별 직업별 취업자 데이터"
        ],
        "주요 변수": [
            "연도, 직업, 취업자 수", "지역, 직업, 취업자 수", "직업, 연령, 교육정도, 취업자 수",
            "직업, 연도, 월임금총액", "지역, 산업, 취업자 수", "산업, 직업, 취업자 수"
        ],
        "분석 목적": [
            "직군 분포 변화", "지역별 직군 분포", "연령·학력별 특성",
            "임금 분석", "지역별 산업구조", "산업별 직군 구조"
        ],
    })
    st.dataframe(data_intro, use_container_width=True, hide_index=True)

    with st.expander("실제 로드된 파일명 확인"):
        st.json(file_names)

    st.markdown("<div class='section-title'>분석 흐름</div>", unsafe_allow_html=True)
    flow = ["직군 분류 기준 설정", "전체 분포 변화", "관리자 포함/제외 검증", "연령·학력 특성", "지역별 분포", "임금 분석", "산업별 직군 구조", "결론 및 시사점"]
    st.markdown("".join([f"<span class='flow-box'>{x}</span>" for x in flow]), unsafe_allow_html=True)


def page_trend(job_share):
    page_header(
        "직군 분포 변화 분석",
        "화이트칼라와 블루칼라의 비중은 2016년부터 2025년까지 어떻게 변화했는가?",
        "프로젝트의 핵심 질문은 화이트칼라와 블루칼라의 비중이 과거부터 현재까지 어떻게 변화했는지 확인하는 것이다. 따라서 전체 취업자 대비 직군별 비중 변화를 먼저 제시한다.",
    )
    latest = job_share[job_share["연도"] == LATEST_YEAR].set_index("직군")
    first = job_share[job_share["연도"] == "2016"].set_index("직군")
    w_latest = latest.loc["화이트칼라", "비중"]
    b_latest = latest.loc["블루칼라", "비중"]
    w_delta = w_latest - first.loc["화이트칼라", "비중"]
    b_delta = b_latest - first.loc["블루칼라", "비중"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("2025 화이트칼라 비중", f"{w_latest:.2f}%")
    with c2: metric_card("2025 블루칼라 비중", f"{b_latest:.2f}%")
    with c3: metric_card("화이트칼라 변화", f"{w_delta:+.2f}%p", "2016년 대비")
    with c4: metric_card("블루칼라 변화", f"{b_delta:+.2f}%p", "2016년 대비")

    left, right = st.columns([1.6, 1])
    with left:
        st.plotly_chart(fig_trend(job_share), use_container_width=True)
    with right:
        st.plotly_chart(fig_pie_latest(job_share), use_container_width=True)

    st.plotly_chart(fig_count_trend(job_share), use_container_width=True)

    st.markdown("<div class='insight-card'><b>핵심 해석</b><br>2016~2025년 사이 화이트칼라 비중은 증가한 반면, 블루칼라 비중은 감소했다. 추가로 취업자 수 추이를 함께 보면 비중 변화가 실제 규모 변화인지, 전체 취업자 구조 변화에서 비롯된 것인지 더 입체적으로 확인할 수 있다.</div>", unsafe_allow_html=True)


def page_manager(manager_df):
    page_header(
        "관리자 포함/제외 비교",
        "관리자를 화이트칼라에 포함할 때와 제외할 때 결과가 크게 달라지는가?",
        "관리자는 화이트칼라에 포함할 수 있지만, 임금과 비중 해석에 영향을 줄 수 있다. 따라서 관리자 포함 여부가 핵심 결론을 바꾸는지 확인하기 위해 별도 비교 페이지를 구성한다.",
    )
    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.plotly_chart(fig_manager_bar(manager_df), use_container_width=True)
    with c2:
        st.plotly_chart(fig_manager_line(manager_df), use_container_width=True)

    st.plotly_chart(fig_manager_own_share(manager_df), use_container_width=True)

    latest = manager_df[manager_df["연도"] == LATEST_YEAR].set_index("기준")
    diff = latest.loc["관리자 포함", "비중"] - latest.loc["관리자 제외", "비중"]
    st.markdown(f"<div class='insight-card'><b>핵심 해석</b><br>2025년 기준 관리자를 포함하면 화이트칼라 비중은 {latest.loc['관리자 포함','비중']:.2f}%, 제외하면 {latest.loc['관리자 제외','비중']:.2f}%로 차이는 {diff:.2f}%p다. 관리자 자체 비중을 별도로 보면 전체 노동시장 내 비중이 크지 않아, 관리자 포함 여부가 핵심 추세를 바꾸지는 않는다.</div>", unsafe_allow_html=True)

    with st.expander("관리자 직군 설명 자세히 보기"):
        html_card("관리자란?", "조직의 정책, 사업, 인력, 예산, 업무 방향을 기획·지휘·조정하는 직군이다. 공공 기관 및 기업 고위직, 행정·경영 지원 및 마케팅 관리직, 전문 서비스 관리직, 건설·전기 및 생산 관련 관리직, 판매 및 고객 서비스 관리직 등이 포함된다.")


def page_age_edu(age_df, edu_df):
    page_header(
        "연령·학력별 직군 특성",
        "연령과 학력에 따라 화이트칼라와 블루칼라 분포는 어떻게 달라지는가?",
        "직군 차이는 단순한 직업명 차이가 아니라 인적 특성과 연결된다. 연령과 학력은 직군별 노동시장 구조를 설명하는 핵심 변수이므로 분석에 포함한다.",
    )
    st.caption(f"※ 연령·학력 분석은 {AGE_EDU_PERIOD} 기준입니다.")
    age_order = ["15~29세", "30~39세", "40~49세", "50~59세", "60세 이상"]
    edu_order = ["중졸이하", "고졸", "대졸이상"]
    age_df = age_df.copy()
    edu_df = edu_df.copy()
    age_df["세부항목"] = pd.Categorical(age_df["세부항목"], age_order, ordered=True)
    edu_df["세부항목"] = pd.Categorical(edu_df["세부항목"], edu_order, ordered=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            age_df.sort_values(["직군", "세부항목"]),
            x="직군", y="비중", color="세부항목", text=age_df["비중"].map(lambda v: f"{v:.1f}%" if v >= 8 else ""),
            title="직군별 연령 구성",
        )
        fig.update_traces(textfont=dict(color="#F8FAFC", size=11), marker_line_color="rgba(255,255,255,0.10)", marker_line_width=0.5)
        fig.update_layout(barmode="stack")
        fig.update_yaxes(range=[0, 100], title="비중(%)", ticksuffix="%")
        fig.update_xaxes(title="")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with c2:
        fig = px.bar(
            edu_df.sort_values(["직군", "세부항목"]),
            x="직군", y="비중", color="세부항목", text=edu_df["비중"].map(lambda v: f"{v:.1f}%" if v >= 8 else ""),
            title="직군별 학력 구성",
        )
        fig.update_traces(textfont=dict(color="#F8FAFC", size=11), marker_line_color="rgba(255,255,255,0.10)", marker_line_width=0.5)
        fig.update_layout(barmode="stack")
        fig.update_yaxes(range=[0, 100], title="비중(%)", ticksuffix="%")
        fig.update_xaxes(title="")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_single_ratio_bar(edu_df, "대졸이상", "직군별 대졸 이상 비중", "#60A5FA"), use_container_width=True)
    with c4:
        st.plotly_chart(fig_single_ratio_bar(age_df, "60세 이상", "직군별 60세 이상 비중", "#34D399"), use_container_width=True)

    st.markdown("<div class='insight-card'><b>핵심 해석</b><br>화이트칼라는 대졸 이상과 30~40대 중심의 비중이 높고, 블루칼라는 고졸 및 50대 이상 비중이 상대적으로 높다. 보조 차트를 통해 대졸 이상 비중과 60세 이상 비중의 차이를 더 직접적으로 확인할 수 있다.</div>", unsafe_allow_html=True)


def page_region(region_job, region_industry):
    page_header(
        "지역별 직군 분포와 산업구조",
        "지역에 따라 화이트칼라와 블루칼라 비중은 어떻게 다르며, 이 차이는 산업구조와 관련이 있는가?",
        "지역별 직군 차이는 단순한 지역 차이가 아니라 산업구조와 연결될 수 있다. 기존 시도별 직업 데이터와 시도별 산업 데이터를 함께 활용하여 지역별 차이의 배경을 설명한다.",
    )
    white_top = region_job[region_job["직군"] == "화이트칼라"].nlargest(5, "비중")[["행정구역별", "비중"]]
    blue_top = region_job[region_job["직군"] == "블루칼라"].nlargest(5, "비중")[["행정구역별", "비중"]]
    manu = region_industry[region_industry["산업표준"].eq("제조업")].nlargest(5, "비중")[["시도별", "비중"]]

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_top_bar(white_top, "행정구역별", "비중", "화이트칼라 비중 상위 지역", "#60A5FA"), use_container_width=True)
    with c2:
        st.plotly_chart(fig_top_bar(blue_top, "행정구역별", "비중", "블루칼라 비중 상위 지역", "#F97316"), use_container_width=True)

    c3, c4 = st.columns([1, 1.15])
    with c3:
        st.plotly_chart(fig_top_bar(manu, "시도별", "비중", "제조업 취업자 비중 상위 지역", "#94A3B8"), use_container_width=True)
    with c4:
        scatter = fig_region_industry_scatter(region_job, region_industry)
        if scatter is None:
            st.markdown("<div class='warning-card'><b>차트 데이터 없음</b><br>지역별 제조업 비중과 블루칼라 비중을 연결할 수 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.plotly_chart(scatter, use_container_width=True)

    st.markdown("<div class='insight-card'><b>핵심 해석</b><br>지역별 직군 차이는 단순한 직업 선택의 차이라기보다 지역 산업구조와 연결된다. 특히 제조업 비중과 블루칼라 비중을 함께 보면, 제조업 기반 지역에서 블루칼라 비중이 높게 나타나는 경향을 확인할 수 있다. 단, 이는 상관관계이며 직접적인 인과관계로 단정하지 않는다.</div>", unsafe_allow_html=True)


def page_wage(wage_group, latest_job):
    page_header(
        "직군별 임금 분석",
        "화이트칼라와 블루칼라의 임금 수준은 어떻게 다르며, 관리자를 포함하면 결과가 어떻게 달라지는가?",
        "임금은 직군 차이를 설명하는 핵심 지표다. 다만 관리자는 임금 수준이 매우 높아 화이트칼라 평균임금에 큰 영향을 줄 수 있으므로 관리자 포함/제외 기준을 함께 제시한다.",
    )
    st.markdown("<div class='warn-card'><b>주의</b><br>관리자는 임금 수준이 높아 평균값에 영향을 줄 수 있다. 따라서 단순 비교만 하지 않고 관리자 포함 기준과 제외 기준을 함께 확인한다.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.plotly_chart(fig_wage_bar(latest_job), use_container_width=True)
    with c2:
        st.plotly_chart(fig_wage_compare(wage_group), use_container_width=True)

    c3, c4 = st.columns([1.2, 1])
    with c3:
        st.plotly_chart(fig_wage_line(wage_group), use_container_width=True)
    with c4:
        st.plotly_chart(fig_wage_gap(wage_group), use_container_width=True)

    st.markdown("<div class='insight-card'><b>핵심 해석</b><br>화이트칼라의 임금 수준은 블루칼라보다 높게 나타나지만, 관리자는 임금 수준이 매우 높아 평균값에 큰 영향을 준다. 임금 격차 추이를 함께 보면 단순 수준 차이뿐 아니라 격차의 방향성도 확인할 수 있다.</div>", unsafe_allow_html=True)


def page_industry(industry_job):
    page_header(
        "산업별 직군 구조 분석",
        "산업에 따라 화이트칼라와 블루칼라의 구성은 어떻게 달라지는가?",
        "구인·미충원 데이터는 직업분류 체계가 달라 화이트칼라·블루칼라 분석의 메인 자료로 사용하기 어렵다. 대신 산업별 직업분포 데이터를 활용하면 기존 직군 분류 기준과 일관성을 유지하면서 산업구조에 따른 직군 차이를 분석할 수 있다.",
    )
    white_top = industry_job[industry_job["직군"] == "화이트칼라"].nlargest(5, "비중")[["산업표준", "비중"]]
    blue_top = industry_job[industry_job["직군"] == "블루칼라"].nlargest(5, "비중")[["산업표준", "비중"]]

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_top_bar(white_top, "산업표준", "비중", "화이트칼라 비중이 높은 산업 TOP5", "#60A5FA"), use_container_width=True)
    with c2:
        st.plotly_chart(fig_top_bar(blue_top, "산업표준", "비중", "블루칼라 비중이 높은 산업 TOP5", "#F97316"), use_container_width=True)

    major = ["제조업", "건설업", "운수 및 창고업", "정보통신업", "금융 및 보험업", "전문, 과학 및 기술 서비스업", "교육 서비스업"]
    d = industry_job[industry_job["산업표준"].isin(major)].copy()

    if d.empty:
        st.markdown(
            "<div class='warning-card'><b>차트 데이터 없음</b><br>주요 산업명이 원본 CSV와 매칭되지 않았습니다. 산업명 정규화 함수를 확인하세요.</div>",
            unsafe_allow_html=True,
        )
    else:
        order_map = {name: i for i, name in enumerate(major)}
        d["정렬순서"] = d["산업표준"].map(order_map)
        d = d.sort_values(["정렬순서", "직군"]).copy()
        fig = stacked_bar_100(d, "산업표준", "직군", "비중", "주요 산업별 직군 구성", x_title="산업")
        fig.update_xaxes(categoryorder="array", categoryarray=major)
        st.plotly_chart(fig, use_container_width=True)

    industry_options = sorted(industry_job["산업표준"].dropna().unique().tolist())
    default_idx = industry_options.index("제조업") if "제조업" in industry_options else 0
    selected_industry = st.selectbox("상세히 볼 산업 선택", industry_options, index=default_idx)
    detail_fig = fig_selected_industry(industry_job, selected_industry)
    if detail_fig is not None:
        st.plotly_chart(detail_fig, use_container_width=True)

    st.markdown("<div class='insight-card'><b>핵심 해석</b><br>정보통신업과 전문·과학·기술 서비스업은 화이트칼라 비중이 높고, 운수·창고업, 건설업, 제조업은 블루칼라 비중이 높다. 산업 선택 기능을 통해 개별 산업의 직군 구성을 추가로 확인할 수 있다.</div>", unsafe_allow_html=True)


def page_conclusion():
    page_header("결론 및 시사점", "분석 결과를 종합하면 한국 노동시장의 직군 구조는 어떻게 변화하고 있는가?", None)

    conclusions = [
        ("화이트칼라 비중 증가", "2016~2025년 사이 화이트칼라 비중은 증가했다."),
        ("블루칼라 비중 감소", "같은 기간 블루칼라 비중은 감소했다."),
        ("분류 기준 검증", "관리자 포함 여부는 수치에 영향을 주지만 핵심 추세를 바꾸지는 않는다."),
        ("인적 특성 차이", "화이트칼라는 대졸 이상과 30~40대 비중이 높다."),
        ("고령층 차이", "블루칼라는 고졸과 50대 이상 비중이 상대적으로 높다."),
        ("산업구조 차이", "지역별·산업별로 직군 구조가 뚜렷하게 다르게 나타난다."),
    ]
    cols = st.columns(3)
    for i, (t, b) in enumerate(conclusions):
        with cols[i % 3]:
            html_card(t, b, "soft-card")

    st.markdown("<div class='section-title'>시사점</div>", unsafe_allow_html=True)
    implications = [
        "직군 변화는 단순한 직업 선호 변화가 아니라 산업구조 변화와 함께 해석해야 한다.",
        "블루칼라 비중은 감소하고 있지만 제조업, 건설업, 운수업 등 특정 산업에서는 여전히 핵심 직군이다.",
        "지역별 노동시장 정책은 지역의 산업구조와 직군 분포를 함께 고려해야 한다.",
        "기술인력 양성과 직업교육은 산업별 직군 구조를 반영해 설계할 필요가 있다.",
    ]
    for idx, text in enumerate(implications, 1):
        html_card(f"시사점 {idx}", text, "blue-card")

    st.markdown("<div class='warn-card'><b>분석 한계</b><br>본 분석은 직업 대분류와 산업 대분류를 중심으로 한 구조 분석이다. 따라서 개인의 직업 선택 동기, 직무 전환, 실제 구직 선호, 산업 내부의 세부 직무 변화까지 직접 설명하지는 못한다. 향후 분석에서는 산업 중분류, 기업규모, 근로시간, 고용형태 자료를 결합하면 더 정교한 해석이 가능하다.</div>", unsafe_allow_html=True)

# ==========================================================
# 앱 실행부
# ==========================================================
def main():
    st.sidebar.markdown("### 📊 노동시장 직군 분석")
    st.sidebar.caption("화이트칼라·블루칼라 중심 Streamlit 대시보드")
    page = st.sidebar.radio(
        "페이지 선택",
        [
            "1. 프로젝트 개요",
            "2. 직군 분포 변화",
            "3. 관리자 포함/제외 비교",
            "4. 연령·학력별 특성",
            "5. 지역별 분포와 산업구조",
            "6. 임금 분석",
            "7. 산업별 직군 구조",
            "8. 결론 및 시사점",
        ],
    )
    st.sidebar.markdown("---")

    try:
        raw, file_names = load_all_data()
        job_share = prepare_yearly_employment(raw["employment_yearly"])
        manager_df = prepare_manager_compare(raw["employment_yearly"])
        region_job = prepare_region_job(raw["region_job"])
        region_industry = prepare_region_industry(raw["region_industry"])
        industry_job = prepare_industry_job(raw["industry_job"])
        wage_long, wage_group, latest_job = prepare_wage(raw["wage_with_manager"], raw["employment_yearly"])
        age_df, edu_df = prepare_age_edu(raw["age_edu"])
    except Exception as e:
        st.error("데이터 로드 또는 전처리 중 오류가 발생했습니다.")
        st.exception(e)
        st.stop()

    if page == "1. 프로젝트 개요":
        page_intro(file_names)
    elif page == "2. 직군 분포 변화":
        page_trend(job_share)
    elif page == "3. 관리자 포함/제외 비교":
        page_manager(manager_df)
    elif page == "4. 연령·학력별 특성":
        page_age_edu(age_df, edu_df)
    elif page == "5. 지역별 분포와 산업구조":
        page_region(region_job, region_industry)
    elif page == "6. 임금 분석":
        page_wage(wage_group, latest_job)
    elif page == "7. 산업별 직군 구조":
        page_industry(industry_job)
    elif page == "8. 결론 및 시사점":
        page_conclusion()

if __name__ == "__main__":
    main()
