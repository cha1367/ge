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

st.markdown("""
<style>
    .main {background-color:#F8FAFC;}
    .block-container {padding-top:1.4rem; padding-bottom:3rem; max-width:1280px;}
    .hero {background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 56%,#2563EB 100%); color:white; padding:28px 32px; border-radius:22px; box-shadow:0 14px 34px rgba(15,23,42,.18); margin-bottom:18px;}
    .hero h1 {font-size:2.05rem; font-weight:800; margin:0 0 8px 0;}
    .hero p {font-size:1rem; line-height:1.65; color:rgba(255,255,255,.9); margin:0;}
    .card {background:white; border:1px solid #E5E7EB; border-radius:18px; padding:18px 20px; box-shadow:0 8px 22px rgba(15,23,42,.06); margin-bottom:16px;}
    .insight {background:#EFF6FF; color:#1E3A8A; border-left:5px solid #2563EB; padding:14px 16px; border-radius:12px; line-height:1.65; margin:10px 0 16px 0;}
    .warn {background:#FFF7ED; color:#9A3412; border-left:5px solid #F97316; padding:14px 16px; border-radius:12px; line-height:1.65; margin:10px 0 16px 0;}
    .muted {color:#64748B; font-size:.92rem; line-height:1.6;}
    div[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px; padding:14px 16px; box-shadow:0 8px 22px rgba(15,23,42,.05);}
    h2, h3 {color:#0F172A;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return {
        "employment": pd.read_csv(DATA_DIR / "employment.csv"),
        "nonregular": pd.read_csv(DATA_DIR / "nonregular.csv"),
        "resting": pd.read_csv(DATA_DIR / "resting.csv"),
        "wage": pd.read_csv(DATA_DIR / "wage.csv"),
        "industry": pd.read_csv(DATA_DIR / "industry.csv"),
        "first_job": pd.read_csv(DATA_DIR / "first_job.csv"),
        "exam_prep": pd.read_csv(DATA_DIR / "exam_prep.csv"),
        "vulnerability": pd.read_csv(DATA_DIR / "vulnerability.csv"),
    }

data = load_data()
emp = data["employment"]
nr = data["nonregular"]
rest = data["resting"]
wage = data["wage"]
industry = data["industry"]
first = data["first_job"]
exam = data["exam_prep"]
vuln = data["vulnerability"]


DATASET_LABELS = {
    "employment": "공식 고용지표",
    "nonregular": "정규직·비정규직",
    "resting": "쉬었음 청년",
    "wage": "청년 임금",
    "industry": "산업별 일자리 구조",
    "first_job": "첫 취업 소요기간",
    "exam_prep": "취업시험 준비자",
    "vulnerability": "청년 고용 취약성 지수",
}

COLUMN_LABELS = {
    "year": "연도",
    "labor_force_participation_rate": "경제활동참가율(%)",
    "employment_rate": "고용률(%)",
    "inactive_thousand": "비경제활동인구(천 명)",
    "unemployment_rate": "실업률(%)",
    "unemployed_thousand": "실업자 수(천 명)",
    "employed_thousand": "취업자 수(천 명)",
    "youth_population_proxy_thousand": "청년 인구 추정치(천 명)",
    "wage_workers_thousand": "임금근로자 수(천 명)",
    "regular_thousand": "정규직 수(천 명)",
    "nonregular_thousand": "비정규직 수(천 명)",
    "regular_ratio": "정규직 비율(%)",
    "nonregular_ratio": "비정규직 비율(%)",
    "resting_thousand": "쉬었음 청년 수(천 명)",
    "resting_share_in_inactive": "비경제활동인구 중 쉬었음 비중(%)",
    "hourly_wage_total_won": "시간당임금총액(원)",
    "monthly_salary_thousand": "월급여액(천 원)",
    "monthly_wage_total_thousand": "월임금총액(천 원)",
    "y1_2_thousand": "첫 취업 소요 1~2년 미만(천 명)",
    "y2_3_thousand": "첫 취업 소요 2~3년 미만(천 명)",
    "m3_6_thousand": "첫 취업 소요 3~6개월 미만(천 명)",
    "under_3m_thousand": "첫 취업 소요 3개월 미만(천 명)",
    "over_3y_thousand": "첫 취업 소요 3년 이상(천 명)",
    "m6_12_thousand": "첫 취업 소요 6개월~1년 미만(천 명)",
    "avg_first_job_months": "첫 취업 평균소요기간(개월)",
    "first_job_total_thousand": "졸업·중퇴 취업유경험자 전체(천 명)",
    "first_job_over_1y_share": "첫 취업 1년 이상 소요 비중(%)",
    "youth_inactive_thousand": "청년층 비경제활동인구 전체(천 명)",
    "exam_prep_thousand": "취업시험 준비자 수(천 명)",
    "not_exam_prep_thousand": "취업시험 미준비자 수(천 명)",
    "exam_prep_ratio": "취업시험 준비자 비율(%)",
    "industry": "산업",
    "workers": "청년 근로자 수(명)",
    "v_employment": "고용률 취약도",
    "v_nonregular": "비정규직 취약도",
    "v_resting": "쉬었음 취약도",
    "v_exam_prep": "취업시험 준비 취약도",
    "v_first_job": "첫 취업 소요 취약도",
    "v_wage": "임금 취약도",
    "youth_employment_vulnerability_index": "청년 고용 취약성 지수(0~100)",
}

def display_df(df: pd.DataFrame) -> pd.DataFrame:
    """사용자 화면에는 내부 영문 컬럼 대신 한국어 컬럼명을 표시한다."""
    out = df.copy()
    out = out.rename(columns={c: COLUMN_LABELS.get(c, c) for c in out.columns})
    return out


# Common chart layout
plotly_template = "plotly_white"
BLUE = "#2563EB"
NAVY = "#0F172A"
ORANGE = "#F97316"
RED = "#DC2626"
GREEN = "#16A34A"
PURPLE = "#7C3AED"
GRAY = "#64748B"


def hero(title: str, subtitle: str):
    st.markdown(f"""
    <div class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def insight(text: str):
    st.markdown(f"<div class='insight'>{text}</div>", unsafe_allow_html=True)


def warn(text: str):
    st.markdown(f"<div class='warn'>{text}</div>", unsafe_allow_html=True)


def card_start():
    st.markdown("<div class='card'>", unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def line_fig(df, x, ys, title, labels=None, y_title=""):
    fig = go.Figure()
    colors = [BLUE, ORANGE, GREEN, PURPLE, RED, GRAY]
    for i, y in enumerate(ys):
        fig.add_trace(go.Scatter(x=df[x], y=df[y], mode="lines+markers", name=(labels or {}).get(y, y), line=dict(width=3, color=colors[i % len(colors)])))
    fig.update_layout(template=plotly_template, title=title, height=430, margin=dict(l=30,r=20,t=60,b=30), yaxis_title=y_title, xaxis_title="연도", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def weighted_index(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """취약성 구성요소별 가중치를 적용해 0~100 지수를 계산한다."""
    total = sum(weights.values())
    if total == 0:
        return pd.Series(np.nan, index=df.index)
    score = sum(df[col] * w for col, w in weights.items()) / total * 100
    return score.round(2)


def latest_policy_priority(vdf: pd.DataFrame) -> pd.DataFrame:
    """최근 연도 취약도 구성요소를 정책 우선순위 표로 변환한다."""
    row = vdf.loc[vdf["year"] == vdf["year"].max()].iloc[0]
    mapping = [
        ("첫 취업 소요", "v_first_job", "첫 일자리 매칭·직무 연계형 인턴십 강화"),
        ("취업시험 준비", "v_exam_prep", "장기 취업준비 청년의 진로 전환·민간 채용 연계 지원"),
        ("쉬었음 청년", "v_resting", "노동시장 재진입 상담·직업훈련·심리/진로 복합 지원"),
        ("비정규직", "v_nonregular", "청년 비정규직 장기근속 유도 및 정규직 전환 인센티브"),
        ("고용률", "v_employment", "청년 채용 연계형 직무교육과 첫 일자리 매칭 강화"),
        ("임금", "v_wage", "저임금 산업 근로조건 개선 및 실질임금·주거비 후속 분석"),
    ]
    out = []
    for name, col, policy in mapping:
        out.append({"취약 영역": name, "최근 취약도(0~1)": float(row[col]), "우선 대응 방향": policy})
    df = pd.DataFrame(out).sort_values("최근 취약도(0~1)", ascending=False).reset_index(drop=True)
    df.insert(0, "우선순위", range(1, len(df)+1))
    df["최근 취약도(0~1)"] = df["최근 취약도(0~1)"].round(3)
    return df

# Sidebar
st.sidebar.title("📊 청년 취업난 구조 분석")
st.sidebar.caption("KOSIS·고용노동부 공공데이터 기반")
page = st.sidebar.radio(
    "페이지 선택",
    [
        "프로젝트 개요",
        "발표용 핵심 요약",
        "공식 고용지표",
        "노동시장 진입 지연",
        "실업률 밖 청년",
        "고용 안정성",
        "임금과 보상",
        "산업별 일자리 구조",
        "청년 고용 취약성 지수",
        "결론 및 대책",
        "수치·논리 검토",
        "데이터 확인",
    ],
)

# Metrics
latest_year = int(emp["year"].max())
latest_emp = emp.loc[emp["year"] == latest_year].iloc[0]
latest_nr = nr.loc[nr["year"] == nr["year"].max()].iloc[0]
latest_rest = rest.loc[rest["year"] == rest["year"].max()].iloc[0]
latest_wage = wage.loc[wage["year"] == wage["year"].max()].iloc[0]
latest_first = first.loc[first["year"] == first["year"].max()].iloc[0]
latest_exam = exam.loc[exam["year"] == exam["year"].max()].iloc[0]
latest_vuln = vuln.loc[vuln["year"] == vuln["year"].max()].iloc[0]

if page == "프로젝트 개요":
    hero("청년 취업난의 구조적 요인 분석", "노동시장 진입 지연·실업률 밖 청년·고용 안정성·임금·산업 구조를 종합적으로 진단하는 공공데이터 기반 프로젝트")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("최근 청년 고용률", f"{latest_emp['employment_rate']:.1f}%", help="15~29세 기준")
    c2.metric("최근 비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%", help="15~19세+20~29세 임금근로자 기준")
    c3.metric("첫 취업 평균소요기간", f"{latest_first['avg_first_job_months']:.1f}개월", help="졸업/중퇴 취업유경험자 기준")
    c4.metric("청년 고용 취약성 지수", f"{latest_vuln['youth_employment_vulnerability_index']:.1f}", help="공식 지표가 아닌 탐색적 요약 지표")

    st.markdown("### 1. 프로젝트 목적")
    insight("본 프로젝트는 청년 취업난을 단순한 실업률 문제가 아니라, <b>노동시장 진입 지연 → 실업률 밖 청년 → 고용 안정성 → 취업 후 보상 → 산업별 일자리 구조</b>의 문제로 분해해 분석한다. 최종적으로 여러 지표를 표준화한 <b>청년 고용 취약성 지수</b>를 산출해 정책 우선 대응 영역을 제안한다.")

    st.markdown("### 2. 핵심 가설")
    st.markdown("""
    - **핵심 가설**: 청년 취업난은 단순한 일자리 수 부족보다, 노동시장 진입 지연·불안정 고용·실업률 밖 청년 증가·산업별 보상 격차에서 더 뚜렷하게 나타날 것이다.
    - **보조 가설 1**: 실업률이 낮아도 쉬었음 청년과 취업시험 준비자가 많으면 실제 취업난은 지속될 수 있다.
    - **보조 가설 2**: 청년층 비정규직 비율이 높을수록 고용 안정성은 낮게 나타날 수 있다.
    - **보조 가설 3**: 청년 근로자가 많이 분포한 산업이 반드시 높은 임금을 제공하는 것은 아닐 것이다.
    """)

    st.markdown("### 3. 문제 정의와 데이터 근거")
    problem_df = pd.DataFrame({
        "문제 정의": ["노동시장 진입 지연", "공식 실업률의 한계", "안정적 일자리 부족", "취업 후 보상 격차", "산업별 일자리 불균형"],
        "핵심 질문": ["첫 직장까지 얼마나 오래 걸리는가?", "실업률에 잡히지 않는 청년이 있는가?", "취업해도 안정적인 일자리인가?", "취업 이후 보상은 충분한가?", "청년 일자리는 어떤 산업에 몰려 있는가?"],
        "사용 데이터": ["첫 취업 소요기간, 취업시험 준비자", "쉬었음 청년, 비경제활동인구", "정규직·비정규직 비율", "월임금총액, 시간당임금", "산업별 근로자 수·임금"],
    })
    st.dataframe(problem_df, use_container_width=True, hide_index=True)

    warn("주의: 본 분석은 인과관계를 확정하는 분석이 아니라, 청년 취업난과 관련된 여러 지표의 흐름을 함께 확인하는 탐색적 데이터 분석이다.")

elif page == "발표용 핵심 요약":
    hero("발표용 핵심 요약", "발표에서는 모든 그래프를 설명하지 않고, 청년 취업난을 설명하는 핵심 4개 근거와 정책 우선순위만 전달한다.")

    st.markdown("### 발표 핵심 질문")
    insight("청년 취업난은 단순히 일자리 수 부족인가, 아니면 <b>노동시장 진입 지연·실업률 밖 청년·고용 안정성 부족·산업별 보상 격차</b>가 결합된 구조적 문제인가?")

    st.markdown("### 발표에서 강조할 4개 근거")
    summary = pd.DataFrame({
        "순서": [1, 2, 3, 4],
        "핵심 근거": ["노동시장 진입 지연", "실업률 밖 청년", "고용 안정성 부족", "산업별 일자리 구조"],
        "사용 데이터": ["첫 취업 소요기간, 취업시험 준비자", "쉬었음 청년, 쉬었음 비중", "정규직·비정규직 규모와 비율", "산업별 청년 근로자 수, 산업별 월임금"],
        "한 문장 해석": [
            "청년 취업난은 첫 직장에 진입하기까지의 시간이 길어지는 문제와 연결된다.",
            "실업률에 잡히지 않는 쉬었음 청년을 함께 봐야 현실을 더 넓게 설명할 수 있다.",
            "취업 여부뿐 아니라 안정적인 일자리인지가 청년 체감 고용상황을 좌우한다.",
            "청년이 많이 일하는 산업이 반드시 높은 보상을 제공하는 것은 아니다.",
        ],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("### 발표에서는 짧게 처리할 보조 분석")
    support = pd.DataFrame({
        "보조 분석": ["공식 고용지표", "임금과 보상", "청년 고용 취약성 지수"],
        "발표 처리 방식": [
            "배경 지표로 1분 이내 설명. 취업자 수는 청년 인구 감소 영향과 함께 해석한다.",
            "명목임금은 상승했으므로 임금 하락 주장 금지. 고용형태·산업별 보상 차이를 보는 자료로 설명한다.",
            "공식 지표가 아니라 탐색적 요약 지표라고 먼저 밝히고, 정책 우선순위 도출 보조도구로만 사용한다.",
        ]
    })
    st.dataframe(support, use_container_width=True, hide_index=True)

    st.markdown("### 최근 취약 영역 기준 정책 우선순위")
    priority_df = latest_policy_priority(vuln)
    st.dataframe(priority_df, use_container_width=True, hide_index=True)
    warn("발표 결론은 ‘원인을 입증했다’가 아니라 ‘청년 취업난과 관련된 구조적 지표의 흐름을 확인했다’로 표현하는 것이 안전하다.")

elif page == "공식 고용지표":
    hero("공식 고용지표", "청년 고용률·실업률·취업자 수를 통해 고용시장의 기본 흐름을 확인한다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("2025년 고용률", f"{latest_emp['employment_rate']:.1f}%")
    c2.metric("2025년 실업률", f"{latest_emp['unemployment_rate']:.1f}%")
    c3.metric("2025년 취업자 수", f"{latest_emp['employed_thousand']:,.0f}천 명")
    insight("청년 취업자 수는 청년 인구 감소의 영향을 받을 수 있으므로, 단순 규모뿐 아니라 청년 인구 대비 취업 비중인 고용률과 함께 해석해야 한다.")
    fig = line_fig(emp, "year", ["employment_rate", "unemployment_rate", "labor_force_participation_rate"], "청년 고용률·실업률·경제활동참가율 추이", {"employment_rate":"고용률", "unemployment_rate":"실업률", "labor_force_participation_rate":"경제활동참가율"}, "%")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = line_fig(emp, "year", ["employed_thousand", "unemployed_thousand", "inactive_thousand"], "청년 취업자·실업자·비경제활동인구 추이", {"employed_thousand":"취업자", "unemployed_thousand":"실업자", "inactive_thousand":"비경제활동인구"}, "천 명")
    st.plotly_chart(fig2, use_container_width=True)
    warn("해석 주의: 취업자 수 감소를 곧바로 ‘일자리 자체 감소’로 단정하기보다, 청년 인구 변화와 고용률 흐름을 함께 검토해야 한다.")

elif page == "노동시장 진입 지연":
    hero("노동시장 진입 지연", "첫 취업 소요기간과 취업시험 준비자 지표로 청년들이 첫 일자리에 들어가기까지의 지연을 살펴본다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("첫 취업 평균소요기간", f"{latest_first['avg_first_job_months']:.1f}개월")
    c2.metric("1년 이상 소요 비중", f"{latest_first['first_job_over_1y_share']:.1f}%")
    c3.metric("취업시험 준비자 비율", f"{latest_exam['exam_prep_ratio']:.1f}%")
    insight("첫 취업 소요기간은 청년들이 노동시장에 진입하기까지 걸리는 시간을 보여주며, 취업시험 준비자 비율은 취업 전 준비 상태에 머무는 청년의 규모를 보여준다.")
    col_a, col_b = st.columns(2)
    with col_a:
        fig = line_fig(first, "year", ["avg_first_job_months"], "첫 취업 평균소요기간", {"avg_first_job_months":"첫 취업 평균소요기간"}, "개월")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = line_fig(first, "year", ["first_job_over_1y_share"], "첫 취업 1년 이상 소요 비중", {"first_job_over_1y_share":"1년 이상 소요 비중"}, "%")
        st.plotly_chart(fig2, use_container_width=True)
    col_c, col_d = st.columns(2)
    with col_c:
        fig3 = line_fig(exam, "year", ["exam_prep_ratio"], "취업시험 준비자 비율", {"exam_prep_ratio":"취업시험 준비자 비율"}, "%")
        st.plotly_chart(fig3, use_container_width=True)
    with col_d:
        fig4 = line_fig(exam, "year", ["exam_prep_thousand"], "취업시험 준비자 수", {"exam_prep_thousand":"취업시험 준비자"}, "천 명")
        st.plotly_chart(fig4, use_container_width=True)
    warn("취업시험 준비자는 ‘취업 실패자’로 단정할 수 없다. 다만 노동시장 진입 전 준비 상태가 길어지는 현상을 보여주는 보조 지표로 활용할 수 있다.")

elif page == "실업률 밖 청년":
    hero("실업률 밖 청년", "쉬었음 청년과 비경제활동인구 중 쉬었음 비중으로 공식 실업률의 한계를 보완한다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("쉬었음 청년", f"{latest_rest['resting_thousand']:,.0f}천 명")
    c2.metric("쉬었음 비중", f"{latest_rest['resting_share_in_inactive']:.1f}%")
    c3.metric("실업률", f"{latest_emp['unemployment_rate']:.1f}%")
    insight("실업률은 적극적으로 구직활동을 하는 사람만 반영한다. 따라서 쉬었음 청년은 실업률에 드러나지 않는 노동시장 이탈 가능성을 확인하는 보조 지표로 볼 수 있다.")
    merged = emp[["year", "unemployment_rate"]].merge(rest, on="year")
    fig = line_fig(merged, "year", ["unemployment_rate", "resting_share_in_inactive"], "실업률과 쉬었음 비중 비교", {"unemployment_rate":"실업률", "resting_share_in_inactive":"비경제활동인구 중 쉬었음 비중"}, "%")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = line_fig(rest, "year", ["resting_thousand"], "쉬었음 청년 수 추이", {"resting_thousand":"쉬었음 청년"}, "천 명")
    st.plotly_chart(fig2, use_container_width=True)
    warn("쉬었음 청년을 모두 구직 포기자로 볼 수는 없다. 건강, 휴식, 개인 사정 등 다양한 이유가 있을 수 있으므로 ‘노동시장 이탈 가능성’으로 조심스럽게 해석한다.")

elif page == "고용 안정성":
    hero("고용 안정성", "정규직·비정규직 규모와 비율로 청년 고용의 질을 진단한다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("임금근로자", f"{latest_nr['wage_workers_thousand']:,.0f}천 명")
    c2.metric("정규직 비율", f"{latest_nr['regular_ratio']:.1f}%")
    c3.metric("비정규직 비율", f"{latest_nr['nonregular_ratio']:.1f}%")
    insight("고용률은 취업 여부만 보여준다. 따라서 청년들이 안정적인 일자리에 진입하고 있는지 확인하려면 정규직·비정규직 비율을 함께 봐야 한다.")
    fig = line_fig(nr, "year", ["regular_ratio", "nonregular_ratio"], "청년 정규직·비정규직 비율 추이", {"regular_ratio":"정규직 비율", "nonregular_ratio":"비정규직 비율"}, "%")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=nr["year"], y=nr["regular_thousand"], name="정규직", marker_color=BLUE))
    fig2.add_trace(go.Bar(x=nr["year"], y=nr["nonregular_thousand"], name="비정규직", marker_color=ORANGE))
    fig2.update_layout(template=plotly_template, barmode="stack", title="청년 정규직·비정규직 규모", height=430, yaxis_title="천 명", xaxis_title="연도")
    st.plotly_chart(fig2, use_container_width=True)
    warn("비정규직이 항상 나쁜 일자리라고 단정할 수는 없다. 이 분석에서는 비정규직 비율을 고용 안정성을 판단하는 참고 지표로 사용한다.")

elif page == "임금과 보상":
    hero("임금과 보상", "청년층 월임금총액과 시간당임금을 통해 취업 후 보상 수준을 확인한다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("월임금총액", f"{latest_wage['monthly_wage_total_thousand']:,.0f}천 원")
    c2.metric("월급여액", f"{latest_wage['monthly_salary_thousand']:,.0f}천 원")
    c3.metric("시간당임금총액", f"{latest_wage['hourly_wage_total_won']:,.0f}원")
    insight("임금 자료는 청년 취업난의 직접 원인이라기보다, 취업 이후 경제적 안정성과 보상 수준을 확인하는 지표로 사용한다.")
    fig = line_fig(wage, "year", ["monthly_wage_total_thousand", "monthly_salary_thousand"], "29세 이하 청년층 월임금 추이", {"monthly_wage_total_thousand":"월임금총액", "monthly_salary_thousand":"월급여액"}, "천 원")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = line_fig(wage, "year", ["hourly_wage_total_won"], "29세 이하 시간당임금총액 추이", {"hourly_wage_total_won":"시간당임금총액"}, "원")
    st.plotly_chart(fig2, use_container_width=True)
    warn("이 자료는 명목임금 기준이다. 물가, 주거비, 생활비를 반영한 실질 구매력 분석은 후속 연구로 제시하는 것이 안전하다.")

elif page == "산업별 일자리 구조":
    hero("산업별 일자리 구조", "산업별 청년 근로자 수와 월임금을 함께 비교해 청년 일자리의 양과 질을 동시에 본다.")
    years = sorted(industry["year"].dropna().unique())
    selected_year = st.selectbox("분석 연도", years, index=len(years)-1)
    ind_y = industry[industry["year"] == selected_year].copy()
    ind_y = ind_y[ind_y["workers"] > 0]
    top = ind_y.sort_values("workers", ascending=False).head(10)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(top.sort_values("workers"), x="workers", y="industry", orientation="h", title=f"{selected_year}년 산업별 청년 근로자 수 Top 10", labels={"workers":"근로자 수(명)", "industry":"산업"}, template=plotly_template)
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(height=500, margin=dict(l=30,r=20,t=60,b=30))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        top_w = ind_y.sort_values("monthly_wage_total_thousand", ascending=False).head(10)
        fig2 = px.bar(top_w.sort_values("monthly_wage_total_thousand"), x="monthly_wage_total_thousand", y="industry", orientation="h", title=f"{selected_year}년 산업별 청년 월임금 Top 10", labels={"monthly_wage_total_thousand":"월임금총액(천 원)", "industry":"산업"}, template=plotly_template)
        fig2.update_traces(marker_color=GREEN)
        fig2.update_layout(height=500, margin=dict(l=30,r=20,t=60,b=30))
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("### 산업별 근로자 수 × 임금 사분면")
    x_med = ind_y["workers"].median()
    y_med = ind_y["monthly_wage_total_thousand"].median()
    fig3 = px.scatter(ind_y, x="workers", y="monthly_wage_total_thousand", text="industry", size="workers", hover_name="industry", title=f"{selected_year}년 산업별 청년 근로자 수와 월임금", labels={"workers":"청년 근로자 수(명)", "monthly_wage_total_thousand":"월임금총액(천 원)"}, template=plotly_template)
    fig3.add_vline(x=x_med, line_dash="dash", line_color=GRAY)
    fig3.add_hline(y=y_med, line_dash="dash", line_color=GRAY)
    fig3.update_traces(textposition="top center", marker=dict(opacity=.75))
    fig3.update_layout(height=620, margin=dict(l=30,r=20,t=60,b=30))
    st.plotly_chart(fig3, use_container_width=True)
    insight("근로자 수가 많은 산업이 반드시 높은 임금을 제공하는 것은 아니다. 산업별 근로자 수와 월임금을 함께 보면 청년 일자리의 양적 집중과 보상 수준의 차이를 동시에 확인할 수 있다.")

elif page == "청년 고용 취약성 지수":
    hero("청년 고용 취약성 지수", "고용률, 비정규직, 쉬었음, 취업시험 준비, 첫 취업 소요기간, 임금을 표준화해 만든 탐색적 요약 지표")
    c1, c2, c3 = st.columns(3)
    c1.metric("최근 지수", f"{latest_vuln['youth_employment_vulnerability_index']:.1f}")
    c2.metric("최고 지수 연도", f"{int(vuln.loc[vuln['youth_employment_vulnerability_index'].idxmax(), 'year'])}년")
    c3.metric("최저 지수 연도", f"{int(vuln.loc[vuln['youth_employment_vulnerability_index'].idxmin(), 'year'])}년")
    warn("청년 고용 취약성 지수는 공식 통계가 아니다. 여러 지표의 상대적 흐름을 한 화면에서 보기 위해 만든 탐색적 요약 지표이며, 정책 판단의 직접 근거가 아니라 보조 분석으로 사용한다.")
    fig = line_fig(vuln, "year", ["youth_employment_vulnerability_index"], "청년 고용 취약성 지수 추이", {"youth_employment_vulnerability_index":"취약성 지수"}, "0~100")
    st.plotly_chart(fig, use_container_width=True)
    components = vuln[["year","v_employment","v_nonregular","v_resting","v_exam_prep","v_first_job","v_wage"]].copy()
    comp_long = components.melt(id_vars="year", var_name="component", value_name="score")
    names = {"v_employment":"고용률 취약도", "v_nonregular":"비정규직 취약도", "v_resting":"쉬었음 취약도", "v_exam_prep":"취업시험 준비 취약도", "v_first_job":"첫 취업 소요 취약도", "v_wage":"임금 취약도"}
    comp_long["component"] = comp_long["component"].map(names)
    fig2 = px.line(comp_long, x="year", y="score", color="component", markers=True, title="취약성 지수 구성요소 변화", labels={"year":"연도", "score":"표준화 점수", "component":"구성요소"}, template=plotly_template)
    fig2.update_layout(height=520, yaxis_title="표준화 점수(0~1)", xaxis_title="연도", legend_title_text="구성요소")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 가중치 민감도 분석")
    st.caption("동일 가중치 지수만 보여주면 가중치가 임의라는 질문이 나올 수 있다. 아래는 가중치 가정을 바꿨을 때 지수 흐름이 크게 달라지는지 확인하는 보조 분석이다.")
    component_cols = ["v_employment", "v_nonregular", "v_resting", "v_exam_prep", "v_first_job", "v_wage"]
    scenarios = {
        "동일 가중치": {c: 1 for c in component_cols},
        "진입 지연 중시": {"v_employment":1, "v_nonregular":1, "v_resting":1, "v_exam_prep":2, "v_first_job":2, "v_wage":1},
        "고용 안정성 중시": {"v_employment":1, "v_nonregular":2, "v_resting":1, "v_exam_prep":1, "v_first_job":1, "v_wage":2},
    }
    sens = vuln[["year"]].copy()
    for name, weights in scenarios.items():
        sens[name] = weighted_index(vuln, weights)
    sens_long = sens.melt(id_vars="year", var_name="가중치 시나리오", value_name="지수")
    fig_s = px.line(sens_long, x="year", y="지수", color="가중치 시나리오", markers=True, title="청년 고용 취약성 지수 민감도 분석", template=plotly_template)
    fig_s.update_layout(height=460, yaxis_title="0~100", xaxis_title="연도")
    st.plotly_chart(fig_s, use_container_width=True)
    insight("민감도 분석은 지수가 특정 가중치 하나에만 의존하는지 점검하기 위한 보조 장치다. 가중치가 달라져도 주요 정점과 흐름이 크게 비슷하면 지수 해석의 안정성이 높아진다.")

    st.markdown("### 최근 연도 구성요소별 정책 우선순위")
    st.dataframe(latest_policy_priority(vuln), use_container_width=True, hide_index=True)

    st.markdown("""
    **지수 구성 방식**
    - 고용률: 낮을수록 취약 → `1 - 정규화값`
    - 비정규직 비율: 높을수록 취약
    - 쉬었음 비중: 높을수록 취약
    - 취업시험 준비자 비율: 높을수록 취약
    - 첫 취업 평균소요기간: 길수록 취약
    - 명목임금: 낮을수록 취약 → `1 - 정규화값`
    """)

elif page == "결론 및 대책":
    hero("결론 및 대책", "청년 취업난을 취업 전·취업 중·취업 후·산업 구조로 나누어 정책 대응 방향을 제안한다.")
    st.markdown("### 종합 결론")
    insight("분석 결과, 청년 취업난은 실업률 하나만으로 설명하기 어렵다. 청년 고용 문제는 노동시장 진입 지연, 실업률에 드러나지 않는 쉬었음 청년, 비정규직 비율로 나타나는 고용 안정성 문제, 취업 후 보상과 산업별 일자리 구조가 함께 작용하는 복합적 문제로 볼 수 있다.")
    st.markdown("### 정책 우선순위")
    insight("대책은 단순 나열이 아니라, 최근 연도 취약성 구성요소가 높은 영역부터 우선 대응하는 방식으로 제안한다.")
    st.dataframe(latest_policy_priority(vuln), use_container_width=True, hide_index=True)

    st.markdown("### 데이터 기반 정책 제안")
    policy = pd.DataFrame({
        "분석 결과": [
            "첫 취업 소요기간 및 취업시험 준비자 존재",
            "쉬었음 청년과 쉬었음 비중 확인",
            "청년 비정규직 비율이 높은 수준",
            "명목임금은 상승했지만 실질 생활 안정성 판단에는 한계",
            "산업별 청년 근로자 수와 임금 수준 차이 존재",
        ],
        "정책 방향": [
            "직무 연계형 인턴십, 첫 일자리 매칭, 취업준비 장기화 청년 대상 진로 전환 지원",
            "노동시장 재진입 상담, 직업훈련, 심리·진로 복합 지원",
            "청년 비정규직의 정규직 전환 인센티브, 장기근속 가능 일자리 확대",
            "실질임금·주거비를 고려한 청년 생활 안정 정책과 후속 분석 필요",
            "저임금 산업 근로조건 개선, 정보통신·전문서비스 등 성장 산업 직무교육 확대",
        ]
    })
    st.dataframe(policy, use_container_width=True, hide_index=True)
    st.markdown("### 한계점")
    st.markdown("""
    - 자료마다 조사 기준과 시점이 다르므로 직접적인 인과관계로 연결하기 어렵다.
    - 임금 자료는 명목임금 기준이므로 물가와 주거비를 반영하지 못한다.
    - 쉬었음 청년은 모두 구직 포기자로 해석할 수 없다.
    - 청년 고용 취약성 지수는 공식 통계가 아니라 탐색적 요약 지표이다.
    - 산업별 자료는 통계표 기준과 기간 차이가 있어 보조 분석으로 활용하는 것이 적절하다.
    """)
    st.markdown("### 발표 방어 문장")
    warn("본 프로젝트는 청년 취업난의 단일 원인을 확정하는 인과분석이 아니라, 청년 취업난과 관련된 여러 고용지표의 흐름을 함께 살펴보는 탐색적 분석이다.")

elif page == "수치·논리 검토":
    hero("수치·논리 검토", "수치가 비현실적으로 보이는 부분, 해석상 위험한 부분, 발표 방어 포인트를 점검한다.")
    st.markdown("### 1. 수치 이상 여부 점검")
    quality = pd.DataFrame({
        "점검 항목": [
            "청년 고용률·실업률",
            "청년 비정규직 비율",
            "쉬었음 청년 비중",
            "첫 취업 소요기간",
            "취업시험 준비자 비율",
            "청년 임금",
            "산업별 임금·근로자 수",
            "청년 고용 취약성 지수",
        ],
        "관찰된 범위": [
            "고용률 41.2~46.6%, 실업률 5.9~9.8%",
            "비정규직 비율 34.6~45.6%",
            "비경제활동인구 중 쉬었음 비중 5.3~10.3%",
            "평균 10~12개월, 1년 이상 소요 비중 26.0~31.3%",
            "12.2~19.1%",
            "월임금총액 186.9만~269.1만 원, 시간당임금 11,134~18,637원",
            "산업별 월임금 약 135.7만~491.2만 원, 산업별 근로자 수 차이 큼",
            "32.8~56.8점. 2021년 최고, 2025년은 그보다 낮음",
        ],
        "판정": [
            "비현실적 수치 없음. 다만 2015년 대비와 2022년 이후 흐름을 구분해야 함.",
            "수치상 자연스러움. 고용 안정성 지표로 사용 가능.",
            "수치상 자연스러움. 단, 쉬었음=구직 포기자로 단정 금지.",
            "수치상 자연스러움. 취업 진입 지연의 직접 근거로 사용 가능.",
            "수치상 자연스러움. 2021년 정점 후 하락했으므로 ‘계속 증가’ 표현 금지.",
            "명목임금 기준으로 자연스러움. ‘임금이 하락했다’는 결론 금지.",
            "소규모 산업은 근로자 수가 작아 임금 변동이 클 수 있음. 보조 분석으로 사용.",
            "공식 지표가 아니라 탐색적 요약 지표. 결론의 주근거로 과도하게 사용하지 말 것.",
        ]
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

    st.markdown("### 2. 대중·교수님에게 납득 가능한 핵심 메시지")
    credible = pd.DataFrame({
        "말할 수 있는 내용": [
            "청년 고용률은 2015년보다 2025년이 높지만, 2022년 정점 이후 낮아졌다.",
            "청년 비정규직 비율은 2015년보다 2025년에 높아졌다.",
            "비경제활동인구 중 쉬었음 비중은 장기적으로 상승했다.",
            "첫 취업까지 1년 이상 걸린 비중은 2015년보다 2025년에 높아졌다.",
            "취업시험 준비자 비율은 2021년 정점 후 하락했지만, 2025년은 2015년보다 높다.",
            "청년 명목임금은 상승했으므로 임금 하락을 주장하지 않는다.",
            "산업별로 청년 근로자 수와 임금 수준의 차이가 크다.",
        ],
        "주의할 해석": [
            "청년 취업자 수 감소는 청년 인구 감소 영향도 고려해야 함.",
            "비정규직이 모두 나쁜 일자리라고 단정하지 않음.",
            "쉬었음 청년을 모두 구직 포기자로 보지 않음.",
            "평균뿐 아니라 1년 이상 비중도 같이 보여주는 것이 설득력 있음.",
            "취업시험 준비자가 계속 증가했다고 말하면 데이터와 맞지 않음.",
            "명목임금은 물가·주거비를 반영하지 못한다는 한계를 명시.",
            "산업별 자료는 조사 기준 차이가 있어 보조 분석으로 해석.",
        ]
    })
    st.dataframe(credible, use_container_width=True, hide_index=True)

    st.markdown("### 3. 피해야 할 표현과 안전한 표현")
    safe = pd.DataFrame({
        "피해야 할 표현": [
            "청년 고용률은 계속 악화됐다.",
            "청년 취업난의 원인은 비정규직 증가다.",
            "쉬었음 청년은 구직 포기자다.",
            "임금이 낮아져서 청년 취업난이 심해졌다.",
            "청년 고용 취약성 지수가 실제 위험도를 정확히 보여준다.",
        ],
        "대신 사용할 표현": [
            "청년 고용률은 2022년 이후 하락 흐름을 보였다.",
            "비정규직 비율 증가는 고용 안정성 문제와 관련될 가능성이 있다.",
            "쉬었음 청년은 실업률 밖 노동시장 이탈 가능성을 보여주는 보조 지표다.",
            "명목임금은 상승했지만, 실질 생활 안정성은 물가·주거비를 함께 봐야 한다.",
            "청년 고용 취약성 지수는 여러 지표의 상대적 흐름을 보기 위한 탐색적 요약 지표다.",
        ]
    })
    st.dataframe(safe, use_container_width=True, hide_index=True)
    warn("최종 결론은 ‘원인 입증’이 아니라 ‘청년 취업난과 관련된 구조적 지표의 흐름 확인’으로 표현하는 것이 가장 안전하다.")

elif page == "데이터 확인":
    hero("데이터 확인", "처리된 데이터 구조를 확인한다. 화면 표는 한국어 컬럼명으로 번역해 표시한다.")
    reverse_labels = {v: k for k, v in DATASET_LABELS.items()}
    selected_label = st.selectbox("데이터 선택", list(reverse_labels.keys()))
    dataset_name = reverse_labels[selected_label]
    df = data[dataset_name]
    shown = display_df(df)
    st.dataframe(shown, use_container_width=True)
    csv = shown.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("한국어 컬럼명 CSV 다운로드", data=csv, file_name=f"{selected_label}.csv", mime="text/csv")
    st.markdown("### 데이터 설명")
    desc = {
        "employment":"청년 고용률, 실업률, 취업자, 실업자, 비경제활동인구, 경제활동참가율",
        "nonregular":"15~19세와 20~29세를 합산한 임금근로자, 정규직, 비정규직, 비율",
        "resting":"15~29세 쉬었음 청년 수와 비경제활동인구 중 쉬었음 비중",
        "wage":"29세 이하 청년층 월임금총액, 월급여액, 시간당임금총액",
        "industry":"산업대분류별 청년 근로자 수와 월임금총액. 연령구간을 합산하고 근로자수 가중평균 임금을 계산함",
        "first_job":"첫 취업 소요기간 구간별 규모, 평균소요기간, 1년 이상 소요 비중",
        "exam_prep":"청년층 비경제활동인구 중 취업시험 준비자 수와 비율",
        "vulnerability":"청년 고용 취약성 지수와 구성요소 표준화 점수",
    }
    st.info(desc.get(dataset_name, ""))
