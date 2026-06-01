# ============================================================
# 대한민국 노동시장의 직군 분포 변화와 산업구조 특성 분석
# 화이트칼라와 블루칼라를 중심으로
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
from pathlib import Path

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="대한민국 노동시장 직군 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0B1120; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #0B1120 100%);
    border-right: 1px solid rgba(148,163,184,0.15);
}
[data-testid="stSidebar"] * { color: #F1F5F9 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 14px; padding: 4px 0; }
[data-testid="metric-container"] {
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 12px;
    padding: 18px;
}
[data-testid="metric-container"] * { color: #F1F5F9 !important; }
div[data-testid="stPlotlyChart"] {
    background: rgba(15,23,42,0.55);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    padding: 0.35rem;
}
h1,h2,h3 { color: #F1F5F9 !important; }
.block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
hr { border-color: rgba(148,163,184,0.2) !important; }
.main-title { font-size:2rem; font-weight:800; color:#60A5FA; margin-bottom:4px; }
.sub-title { font-size:1.1rem; color:#94A3B8; margin-bottom:20px; }
.page-title { font-size:1.6rem; font-weight:700; color:#F1F5F9; margin-bottom:4px; }
.section-title { font-size:1.1rem; font-weight:600; color:#60A5FA; margin:16px 0 8px 0; }
.info-card {
    background:rgba(15,23,42,0.95); border:1px solid rgba(148,163,184,0.2);
    border-radius:10px; padding:18px; margin:6px 0;
}
.reason-card {
    background:rgba(96,165,250,0.08); border:1px solid rgba(96,165,250,0.3);
    border-left:4px solid #60A5FA; border-radius:0 8px 8px 0;
    padding:12px 16px; margin:10px 0;
}
.insight-card {
    background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.3);
    border-left:4px solid #34D399; border-radius:0 8px 8px 0;
    padding:12px 16px; margin:8px 0;
}
.warning-card {
    background:rgba(249,115,22,0.08); border:1px solid rgba(249,115,22,0.3);
    border-left:4px solid #F97316; border-radius:0 8px 8px 0;
    padding:12px 16px; margin:8px 0;
}
.kpi-card {
    background:rgba(15,23,42,0.95); border:1px solid rgba(148,163,184,0.2);
    border-radius:10px; padding:16px; text-align:center; margin:4px 0;
}
.kpi-value { font-size:1.8rem; font-weight:800; color:#60A5FA; }
.kpi-label { font-size:0.85rem; color:#94A3B8; margin-top:4px; }
.kpi-delta { font-size:0.8rem; color:#34D399; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

COLOR_MAP = {
    "화이트칼라": "#60A5FA",
    "블루칼라":   "#F97316",
    "기타":       "#CBD5E1"
}
AGE_COLOR_MAP = {
    "15~29세": "#38BDF8", "30~39세": "#A78BFA",
    "40~49세": "#F43F5E", "50~59세": "#FCA5A5", "60세 이상": "#34D399"
}
EDU_COLOR_MAP = {
    "중졸이하": "#F97316", "고졸": "#60A5FA", "대졸이상": "#34D399"
}

# ── 차트 공통 레이아웃 ────────────────────────────────────────
def chart_layout(fig, height=420, showlegend=True):
    fig.update_layout(
        template="plotly_dark", height=height,
        margin=dict(l=20,r=20,t=78,b=56),
        font=dict(family="Arial", size=13, color="#F8FAFC"),
        title=dict(font=dict(size=16, color="#F8FAFC"), x=0.02, xanchor="left"),
        paper_bgcolor="rgba(15,23,42,0.98)",
        plot_bgcolor="rgba(15,23,42,0.92)",
        showlegend=showlegend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.08,
            xanchor="left", x=0,
            bgcolor="rgba(15,23,42,0.96)",
            bordercolor="rgba(148,163,184,0.45)", borderwidth=1,
            font=dict(size=12, color="#F8FAFC")
        ),
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.98)",
            bordercolor="#38BDF8",
            font=dict(color="#F8FAFC", size=13)
        )
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        linecolor="rgba(148,163,184,0.45)",
        tickfont=dict(color="#E2E8F0", size=12),
        title_font=dict(color="#F8FAFC", size=13), color="#E2E8F0"
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.22)", zeroline=False,
        linecolor="rgba(148,163,184,0.45)",
        tickfont=dict(color="#E2E8F0", size=12),
        title_font=dict(color="#F8FAFC", size=13), color="#E2E8F0"
    )
    return fig

def insight_box(text, color="blue"):
    c = {"blue":"#60A5FA","green":"#34D399","orange":"#F97316","red":"#F43F5E"}.get(color,"#60A5FA")
    st.markdown(
        f'<div style="background:rgba(15,23,42,0.95);border-left:4px solid {c};'
        f'border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;'
        f'color:#CBD5E1;font-size:13px;">💡 {text}</div>',
        unsafe_allow_html=True
    )

def reason_box(text):
    st.markdown(
        f'<div class="reason-card"><span style="color:#60A5FA;font-weight:600;">📌 이 분석을 선택한 이유</span>'
        f'<br><span style="color:#CBD5E1;font-size:13px;">{text}</span></div>',
        unsafe_allow_html=True
    )

# ── 직군 분류 ─────────────────────────────────────────────────
def classify_job(job):
    job = str(job).strip()
    if "관리자" in job: return "화이트칼라"
    if "전문가" in job: return "화이트칼라"
    if "사무" in job: return "화이트칼라"
    if "기능원" in job: return "블루칼라"
    if "장치" in job or "기계" in job or "조립" in job: return "블루칼라"
    if "단순" in job: return "블루칼라"
    if "서비스" in job or "판매" in job or "농림" in job: return "기타"
    return "기타"

# ── 산업명 표준화 ─────────────────────────────────────────────
def normalize_industry(s):
    s = str(s).strip()
    s = re.sub(r"^[A-Z]\.", "", s).strip()
    s = re.sub(r"\([^)]*\)", "", s).strip()
    c = re.sub(r"\s+", "", s)
    if "제조" in c: return "제조업"
    if "건설" in c: return "건설업"
    if "정보통신" in c: return "정보통신업"
    if "전문" in c and "과학" in c and "기술" in c: return "전문·과학기술서비스업"
    if "금융" in c and "보험" in c: return "금융및보험업"
    if "교육" in c: return "교육서비스업"
    if "운수" in c and "창고" in c: return "운수및창고업"
    if "사업시설" in c or "사업지원" in c: return "사업시설관리및지원업"
    if "전기" in c and "가스" in c: return "전기·가스·증기공급업"
    if "보건" in c and "복지" in c: return "보건업및사회복지서비스업"
    if "도매" in c or "소매" in c: return "도소매업"
    if "숙박" in c and "음식" in c: return "숙박및음식점업"
    if "농업" in c or "임업" in c or "어업" in c: return "농림어업"
    if "광공업" in c or "광업" in c: return "광공업"
    return s

# ── 데이터 로딩 함수 ─────────────────────────────────────────

@st.cache_data
def load_yearly():
    path = DATA_DIR / "직업별_취업자_연도별.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')
    return df, year_cols

@st.cache_data
def load_gender():
    path = DATA_DIR / "성별_직업별.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')
    return df, year_cols

@st.cache_data
def load_region():
    path = DATA_DIR / "시도별_직업별.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '행정구역'
    df.columns.values[1] = '직업별'
    val_cols = [c for c in df.columns if '/' in str(c) and '.1' not in str(c) and '.2' not in str(c)]
    for c in val_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df, val_cols

@st.cache_data
def load_wage(with_mgr=True):
    fname = "관리자 포함.csv" if with_mgr else "관리자 미 포함.csv"
    path = DATA_DIR / fname
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')
    return df, year_cols

@st.cache_data
def load_edu():
    path = DATA_DIR / "직업별_학력별.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '직업별'
    # 최신 반기 (2024.1/2) 컬럼 추출
    base_cols = [c for c in df.columns if '2024.1/2' == c[:8] and len(c) <= 9]
    if not base_cols:
        base_cols = [c for c in df.columns if '2024.1/2' in str(c) and '.1' not in str(c) and '.2' not in str(c) and '.3' not in str(c) and '.4' not in str(c) and '.5' not in str(c) and '.6' not in str(c) and '.7' not in str(c) and '.8' not in str(c)]
    # 컬럼 인덱스로 접근
    period = '2024.1/2'
    idx_cols = [i for i, c in enumerate(df.columns) if period in str(c)]
    if len(idx_cols) >= 9:
        total_col = df.columns[idx_cols[0]]
        age_cols = [df.columns[idx_cols[i]] for i in range(1,6)]
        edu_cols = [df.columns[idx_cols[i]] for i in range(6,9)]
        age_names = ['15~29세','30~39세','40~49세','50~59세','60세 이상']
        edu_names = ['중졸이하','고졸','대졸이상']
        rename = {total_col:'취업자'}
        for i, n in enumerate(age_names): rename[age_cols[i]] = n
        for i, n in enumerate(edu_names): rename[edu_cols[i]] = n
        df = df.rename(columns=rename)
        for c in ['취업자']+age_names+edu_names:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        return df, age_names, edu_names
    return df, [], []

@st.cache_data
def load_region_industry():
    path = DATA_DIR / "행정구역_시도__산업별_취업자_20260531191255.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    df.columns.values[0] = '시도별'
    df.columns.values[1] = '산업별'
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')
    df['산업명'] = df['산업별'].apply(normalize_industry)
    return df, year_cols

@st.cache_data
def load_industry_job():
    path = DATA_DIR / "전국_성별_산업_직업별_취업자_대분류__20260531191932.csv"
    if not path.exists():
        return None, []
    df = pd.read_csv(path, encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    val_cols = [c for c in df.columns if '/' in str(c) and '.1' not in str(c) and '.2' not in str(c)]
    for c in val_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['산업명'] = df['산업별'].apply(normalize_industry)
    df['직군'] = df['직업별'].apply(classify_job)
    return df, val_cols

# ── 100% 누적 막대 함수 ───────────────────────────────────────
def stacked_bar_100(df, x_col, category_col, value_col, title, x_title="", y_title="비중(%)"):
    fig = px.bar(
        df, x=x_col, y=value_col, color=category_col,
        color_discrete_map=COLOR_MAP,
        category_orders={category_col: ["화이트칼라","블루칼라","기타"]},
        text=df[value_col].map(lambda v: f"{v:.1f}%" if pd.notna(v) and v >= 7 else ""),
        title=title
    )
    fig.update_traces(
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="#F8FAFC", size=12),
        marker_line_color="rgba(255,255,255,0.12)", marker_line_width=0.6
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0,100], title=y_title)
    fig.update_xaxes(title=x_title)
    return chart_layout(fig, height=430)

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 노동시장 직군 분석")
    st.markdown("**화이트칼라 · 블루칼라**")
    st.markdown("---")
    page = st.radio("페이지 선택", [
        "1. 프로젝트 개요",
        "2. 직군 분포 변화",
        "3. 관리자 포함/제외 비교",
        "4. 연령·학력별 특성",
        "5. 지역별 분포와 산업구조",
        "6. 임금 분석",
        "7. 산업별 직군 구조",
        "8. 결론 및 시사점"
    ])
    st.markdown("---")
    st.markdown("🔵 **화이트칼라** 관리자·전문가·사무")
    st.markdown("🟠 **블루칼라** 기능원·기계조작·단순노무")
    st.markdown("⬜ **기타** 서비스·판매·농림어업")
    st.markdown("---")
    st.caption("출처: 통계청 KOSIS · 고용노동부")

# ══════════════════════════════════════════════════════════════
# 1. 프로젝트 개요
# ══════════════════════════════════════════════════════════════
if page == "1. 프로젝트 개요":
    st.markdown('<div class="main-title">대한민국 노동시장의 직군 분포 변화와 산업구조 특성 분석</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">— 화이트칼라와 블루칼라를 중심으로 —</div>', unsafe_allow_html=True)
    st.markdown("---")

    # 배경·문제제기·목표
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="info-card">
        <div style="color:#60A5FA;font-weight:700;margin-bottom:10px;">🎯 프로젝트 배경</div>
        <div style="color:#CBD5E1;font-size:13px;line-height:1.7;">
        화이트칼라·블루칼라는 오랫동안 서로 다른 직업군으로 인식되어 왔다.
        최근 반도체·정유·생산기술직 등 고임금 기술직이 주목받으며 블루칼라에 대한 인식이 변화하고 있다.
        실제 노동시장 구조가 어떻게 변해왔는지 데이터로 확인할 필요가 있다.
        </div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="info-card">
        <div style="color:#e3b341;font-weight:700;margin-bottom:10px;">❓ 문제 제기</div>
        <div style="color:#CBD5E1;font-size:13px;line-height:1.7;">
        ① 실제 노동시장에서 두 직군은 어떻게 분포하는가?<br>
        ② 2016~2025년 동안 비중은 어떻게 변화했는가?<br>
        ③ 연령·학력·지역·임금에서 어떤 차이를 보이는가?<br>
        ④ 산업구조에 따라 직군 구성은 어떻게 달라지는가?
        </div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="info-card">
        <div style="color:#34D399;font-weight:700;margin-bottom:10px;">🎯 분석 목표</div>
        <div style="color:#CBD5E1;font-size:13px;line-height:1.7;">
        ① 직군별 분포 변화 분석<br>
        ② 관리자 포함·제외 비교 분석<br>
        ③ 연령·학력별 직군 특성 분석<br>
        ④ 지역별 직군 분포 차이 분석<br>
        ⑤ 직군별 임금 수준 분석<br>
        ⑥ 산업별 직군 구조 분석
        </div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📌 직군 분류 기준 (한국표준직업분류 KSCO)</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.3);
        border-top:3px solid #60A5FA;border-radius:8px;padding:18px;">
        <div style="color:#60A5FA;font-weight:700;font-size:15px;margin-bottom:12px;">🔵 화이트칼라</div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>관리자</b><br>
        <span style="color:#94A3B8;">조직의 정책·인력·예산을 기획·지휘하는 직군</span></div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>전문가 및 관련 종사자</b><br>
        <span style="color:#94A3B8;">전문지식 기반 연구·교육·보건·법률·공학 직군</span></div>
        <div style="color:#F1F5F9;font-size:13px;"><b>사무 종사자</b><br>
        <span style="color:#94A3B8;">행정·회계·문서관리·조직운영 지원 직군</span></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.3);
        border-top:3px solid #F97316;border-radius:8px;padding:18px;">
        <div style="color:#F97316;font-weight:700;font-size:15px;margin-bottom:12px;">🟠 블루칼라</div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>기능원 및 관련 기능 종사자</b><br>
        <span style="color:#94A3B8;">숙련 기술 기반 제조·건설·수리·설치 직군</span></div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>장치·기계조작 및 조립 종사자</b><br>
        <span style="color:#94A3B8;">기계장치 조작·생산설비 운영·제품 조립 직군</span></div>
        <div style="color:#F1F5F9;font-size:13px;"><b>단순노무 종사자</b><br>
        <span style="color:#94A3B8;">단순·반복적 육체노동 및 현장 보조 직군</span></div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div style="background:rgba(203,213,225,0.08);border:1px solid rgba(203,213,225,0.2);
        border-top:3px solid #CBD5E1;border-radius:8px;padding:18px;">
        <div style="color:#CBD5E1;font-weight:700;font-size:15px;margin-bottom:12px;">⬜ 기타</div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>서비스 종사자</b><br>
        <span style="color:#94A3B8;">음식·숙박·미용·돌봄·경비·청소 등 대면 서비스</span></div>
        <div style="color:#F1F5F9;font-size:13px;margin-bottom:6px;"><b>판매 종사자</b><br>
        <span style="color:#94A3B8;">상품 판매·매장 관리·영업·고객 응대</span></div>
        <div style="color:#F1F5F9;font-size:13px;"><b>농림어업 숙련 종사자</b><br>
        <span style="color:#94A3B8;">농업·임업·어업 분야 숙련 직군</span></div>
        <div style="color:#94A3B8;font-size:12px;margin-top:10px;border-top:1px solid rgba(148,163,184,0.2);padding-top:8px;">
        ※ 화이트·블루칼라 어느 쪽에도 명확히 속하지 않아 별도 분류</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📋 관리자 포함 기준</div>', unsafe_allow_html=True)
    st.markdown("""<div class="info-card">
    <div style="color:#CBD5E1;font-size:13px;line-height:1.7;">
    관리자는 <b style="color:#60A5FA;">화이트칼라에 포함</b>한다.
    단, 관리자는 임금 수준이 높아 평균을 왜곡할 수 있으므로
    <b style="color:#F97316;">별도 페이지(3번)에서 관리자 포함·제외 비교</b>를 제공한다.<br><br>
    <b>관리자에 포함되는 직무 예시:</b>
    공공기관 및 기업 고위직 / 행정·경영 지원 및 마케팅 관리직 /
    전문 서비스 관리직 / 건설·전기 및 생산 관련 관리직 / 판매 및 고객 서비스 관리직
    </div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🗂 사용 데이터</div>', unsafe_allow_html=True)
    data_rows = [
        ("직업별 취업자 연도별", "연도·직업·취업자 수", "직군 분포 변화 분석", "2·3번"),
        ("시도별 직업별 취업자", "지역·직업·취업자 수", "지역별 직군 분포 분석", "5번"),
        ("직업별 연령·학력별", "연령·학력·직업·취업자 수", "연령·학력별 특성 분석", "4번"),
        ("직종별 월임금총액 (관리자 포함·미포함)", "직업·연도·월임금", "임금 분석", "6번"),
        ("시도별 산업별 취업자", "지역·산업·취업자 수", "지역별 산업구조 분석", "5번"),
        ("산업별 직업별 취업자", "산업·직업·취업자 수", "산업별 직군 구조 분석", "7번"),
    ]
    header_cols = st.columns([3,3,3,1])
    for col, h in zip(header_cols, ["데이터명","주요 변수","분석 목적","페이지"]):
        col.markdown(f"<span style='color:#60A5FA;font-weight:600;font-size:13px;'>{h}</span>", unsafe_allow_html=True)
    for row in data_rows:
        cols = st.columns([3,3,3,1])
        for col, val in zip(cols, row):
            col.markdown(f"<span style='color:#CBD5E1;font-size:13px;'>{val}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:4px 0;border-color:rgba(148,163,184,0.1);'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 2. 직군 분포 변화
# ══════════════════════════════════════════════════════════════
elif page == "2. 직군 분포 변화":
    st.markdown('<div class="page-title">📊 직군 분포 변화</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>2016~2025년 화이트칼라와 블루칼라의 비중은 어떻게 변화했는가?</span>", unsafe_allow_html=True)
    reason_box("프로젝트의 핵심 질문은 두 직군의 비중이 시간에 따라 어떻게 변화했는지 확인하는 것이다. 전체 취업자 대비 직군별 비중 변화를 먼저 제시한다.")
    st.markdown("---")

    df, year_cols = load_yearly()
    if df is None:
        st.error("❌ data/직업별_취업자_연도별.csv 파일을 찾을 수 없습니다.")
        st.stop()

    # 직군 분류
    df['직군'] = df['직업별'].apply(classify_job)
    total_row = df[df['직업별']=='계']
    job_df = df[~df['직업별'].str.contains(r'^\*|^계', na=False)].copy()

    # 연도별 직군 합계
    trend_data = []
    for y in year_cols:
        total = float(total_row[y].values[0]) if not total_row.empty else None
        if total and total > 0:
            for g in ['화이트칼라','블루칼라','기타']:
                val = job_df[job_df['직군']==g][y].sum()
                trend_data.append({'연도':y,'직군':g,'취업자':val,'비중':val/total*100})
    tdf = pd.DataFrame(trend_data)

    if tdf.empty:
        st.warning("데이터가 없습니다.")
        st.stop()

    # KPI
    latest = year_cols[-1]
    first = year_cols[0]
    kpi_cols = st.columns(4)
    for i, (g, label) in enumerate([('화이트칼라','🔵 화이트칼라'),('블루칼라','🟠 블루칼라')]):
        cur = tdf[(tdf['연도']==latest)&(tdf['직군']==g)]['비중'].values
        prev = tdf[(tdf['연도']==first)&(tdf['직군']==g)]['비중'].values
        if len(cur) and len(prev):
            kpi_cols[i*2].metric(f"{label} ({latest}년)", f"{cur[0]:.1f}%")
            delta = cur[0]-prev[0]
            kpi_cols[i*2+1].metric(f"{first}년 대비 변화", f"{delta:+.1f}%p", f"{prev[0]:.1f}% → {cur[0]:.1f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # 선그래프
        fig = px.line(tdf, x='연도', y='비중', color='직군',
                      color_discrete_map=COLOR_MAP,
                      markers=True, title="연도별 직군 비중 변화")
        fig.add_vline(x='2022', line_dash='dash', line_color='#E2E8F0', line_width=1)
        fig.add_annotation(x='2022', y=tdf['비중'].max()*0.95,
                           text='2022', font=dict(color='#E2E8F0',size=11),
                           showarrow=False, xanchor='left')
        fig.update_yaxes(title='비중(%)')
        st.plotly_chart(chart_layout(fig), use_container_width=True)
        insight_box("화이트칼라 비중은 꾸준히 증가, 블루칼라 비중은 완만하게 감소 추세")

    with col2:
        # 도넛 차트
        latest_pie = tdf[tdf['연도']==latest][['직군','취업자']].copy()
        fig2 = px.pie(latest_pie, values='취업자', names='직군', hole=0.52,
                      color='직군', color_discrete_map=COLOR_MAP,
                      title=f"{latest}년 직군 구성")
        fig2.update_traces(
            textfont=dict(color="#F8FAFC", size=13),
            textinfo="label+percent"
        )
        st.plotly_chart(chart_layout(fig2, showlegend=False), use_container_width=True)
        insight_box(f"{latest}년 기준 직군별 취업자 비중 분포")

# ══════════════════════════════════════════════════════════════
# 3. 관리자 포함/제외 비교
# ══════════════════════════════════════════════════════════════
elif page == "3. 관리자 포함/제외 비교":
    st.markdown('<div class="page-title">📊 관리자 포함/제외 비교</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>관리자 포함 여부가 핵심 결론을 바꾸는가?</span>", unsafe_allow_html=True)
    reason_box("관리자는 임금이 높아 평균값을 왜곡할 수 있다. 포함·제외 기준이 핵심 추세를 바꾸는지 확인한다.")
    st.markdown("---")

    df_inc, year_cols_inc = load_wage(with_mgr=True)
    df_exc, year_cols_exc = load_wage(with_mgr=False)

    if df_inc is None or df_exc is None:
        st.error("❌ 임금 데이터 파일을 찾을 수 없습니다. (관리자 포함.csv / 관리자 미 포함.csv)")
        st.stop()

    WAGE_MAP = {
        '관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가','사무 종사자(3)':'사무종사자',
        '기능원 및 관련기능종사자(7)':'기능원','장치·기계 조작 및 조립종사자(8)':'기계조작',
        '단순노무 종사자(9)':'단순노무',
        '전문가 및 관련종사자(2)':'전문가','사무 종사자(3)':'사무종사자',
    }
    TARGET = ['관리자','전문가','사무종사자','기능원','기계조작','단순노무']
    TARGET_EXC = ['전문가','사무종사자','기능원','기계조작','단순노무']

    def get_avg(df, year_cols, targets):
        df_f = df[df['고용형태']=='전체근로자'].copy()
        df_f['직종'] = df_f['직종별'].map(WAGE_MAP).fillna(df_f['직종별'])
        result = []
        for y in year_cols:
            sub = df_f[df_f['직종'].isin(targets)][['직종',y]].dropna()
            sub['직군'] = sub['직종'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
            for g in ['화이트칼라','블루칼라']:
                avg = sub[sub['직군']==g][y].mean()
                result.append({'연도':y,'직군':g,'평균임금':avg})
        return pd.DataFrame(result)

    df_trend_inc = get_avg(df_inc, year_cols_inc, TARGET)
    df_trend_exc = get_avg(df_exc, year_cols_exc, TARGET_EXC)

    latest = year_cols_inc[-1]
    inc_w = df_trend_inc[(df_trend_inc['연도']==latest)&(df_trend_inc['직군']=='화이트칼라')]['평균임금'].values
    inc_b = df_trend_inc[(df_trend_inc['연도']==latest)&(df_trend_inc['직군']=='블루칼라')]['평균임금'].values
    exc_w = df_trend_exc[(df_trend_exc['연도']==latest)&(df_trend_exc['직군']=='화이트칼라')]['평균임금'].values
    exc_b = df_trend_exc[(df_trend_exc['연도']==latest)&(df_trend_exc['직군']=='블루칼라')]['평균임금'].values

    if len(inc_w) and len(inc_b) and len(exc_w) and len(exc_b):
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🔵 화이트칼라 (관리자 포함)", f"{inc_w[0]:,.0f}천원/월")
        c2.metric("🔵 화이트칼라 (관리자 제외)", f"{exc_w[0]:,.0f}천원/월", f"△{inc_w[0]-exc_w[0]:,.0f}천원")
        c3.metric("🟠 블루칼라", f"{inc_b[0]:,.0f}천원/월")
        c4.metric("격차 (관리자 포함 기준)", f"{inc_w[0]-inc_b[0]:,.0f}천원")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        # 관리자 포함 추이
        fig = px.line(df_trend_inc, x='연도', y='평균임금', color='직군',
                      color_discrete_map=COLOR_MAP, markers=True,
                      title="관리자 포함 — 직군별 월평균 임금 추이")
        fig.update_yaxes(title='월평균 임금 (천원)')
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with col2:
        # 관리자 제외 추이
        fig2 = px.line(df_trend_exc, x='연도', y='평균임금', color='직군',
                       color_discrete_map=COLOR_MAP, markers=True,
                       title="관리자 제외 — 직군별 월평균 임금 추이")
        fig2.update_yaxes(title='월평균 임금 (천원)')
        st.plotly_chart(chart_layout(fig2), use_container_width=True)

    insight_box("관리자 포함 여부는 화이트칼라 평균 임금 수치에 영향을 주지만, 화이트칼라 > 블루칼라라는 핵심 추세는 변하지 않는다.", "green")

# ══════════════════════════════════════════════════════════════
# 4. 연령·학력별 특성
# ══════════════════════════════════════════════════════════════
elif page == "4. 연령·학력별 특성":
    st.markdown('<div class="page-title">📊 연령·학력별 특성</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>연령과 학력에 따라 직군 분포는 어떻게 달라지는가? (기준: 2024년 상반기)</span>", unsafe_allow_html=True)
    reason_box("연령과 학력은 직군별 노동시장 구조를 설명하는 핵심 변수다. 인적 특성이 직군 분류와 어떤 상관을 갖는지 분석한다.")
    st.markdown("---")

    result = load_edu()
    if result[0] is None:
        st.error("❌ data/직업별_학력별.csv 파일을 찾을 수 없습니다.")
        st.stop()
    df, age_names, edu_names = result

    if not age_names:
        st.warning("연령·학력 컬럼을 찾을 수 없습니다.")
        st.stop()

    df['직군'] = df['직업별'].apply(classify_job)
    target_jobs = df[~df['직업별'].str.contains(r'^계$|^\*', na=False) & (df['직업별'] != '직업별')].copy()
    target_jobs = target_jobs[target_jobs['직군'].isin(['화이트칼라','블루칼라','기타'])]

    # 연령별 직군 구성
    age_data = []
    for age in age_names:
        if age not in target_jobs.columns: continue
        total_by_age = target_jobs[age].sum()
        if total_by_age == 0: continue
        for g in ['화이트칼라','블루칼라','기타']:
            val = target_jobs[target_jobs['직군']==g][age].sum()
            age_data.append({'연령대':age,'직군':g,'취업자':val,'비중':val/total_by_age*100})
    age_df = pd.DataFrame(age_data)

    # 학력별 직군 구성
    edu_data = []
    for edu in edu_names:
        if edu not in target_jobs.columns: continue
        total_by_edu = target_jobs[edu].sum()
        if total_by_edu == 0: continue
        for g in ['화이트칼라','블루칼라','기타']:
            val = target_jobs[target_jobs['직군']==g][edu].sum()
            edu_data.append({'학력':edu,'직군':g,'취업자':val,'비중':val/total_by_edu*100})
    edu_df = pd.DataFrame(edu_data)

    col1, col2 = st.columns(2)
    with col1:
        if not age_df.empty:
            fig = stacked_bar_100(age_df, '연령대', '직군', '비중', "연령대별 직군 구성 (2024년 상반기)")
            st.plotly_chart(fig, use_container_width=True)
            insight_box("화이트칼라는 30~40대 비중이 높고, 블루칼라는 50대 이상 비중이 상대적으로 높다.")
        else:
            st.warning("연령별 데이터가 없습니다.")

    with col2:
        if not edu_df.empty:
            fig2 = stacked_bar_100(edu_df, '학력', '직군', '비중', "학력별 직군 구성 (2024년 상반기)")
            st.plotly_chart(fig2, use_container_width=True)
            insight_box("대졸 이상에서 화이트칼라 비중이 높고, 고졸·중졸이하에서 블루칼라 비중이 상대적으로 높다.")
        else:
            st.warning("학력별 데이터가 없습니다.")

# ══════════════════════════════════════════════════════════════
# 5. 지역별 분포와 산업구조
# ══════════════════════════════════════════════════════════════
elif page == "5. 지역별 분포와 산업구조":
    st.markdown('<div class="page-title">🗺 지역별 분포와 산업구조</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>지역에 따라 직군 비중과 산업구조는 어떻게 다른가?</span>", unsafe_allow_html=True)
    reason_box("지역별 직군 차이는 단순한 지역 차이가 아니라 산업구조와 연결된다. 직업 데이터와 산업 데이터를 함께 분석해 배경을 설명한다.")
    st.markdown("---")

    df_reg, val_cols = load_region()
    df_ind, ind_year_cols = load_region_industry()

    if df_reg is None:
        st.error("❌ data/시도별_직업별.csv 파일을 찾을 수 없습니다.")
        st.stop()

    latest_col = val_cols[-1] if val_cols else None

    # 시도별 직군 비율 계산
    regions = [r for r in df_reg['행정구역'].unique() if r not in ['행정구역별','계','전국']]
    result = []
    WHITE_R = ['관리자','전문가 및 관련 종사자','사무 종사자']
    BLUE_R  = ['기능원 및 관련 기능 종사자','장치‧기계 조작 및 조립 종사자','단순 노무 종사자']
    for reg in regions:
        sub = df_reg[df_reg['행정구역']==reg]
        total_row = sub[sub['직업별']=='계']
        if total_row.empty or latest_col not in total_row.columns: continue
        total = float(total_row[latest_col].values[0])
        if total == 0: continue
        white = sub[sub['직업별'].isin(WHITE_R)][latest_col].sum()
        blue  = sub[sub['직업별'].isin(BLUE_R)][latest_col].sum()
        result.append({'지역':reg,'화이트칼라비율':white/total*100,'블루칼라비율':blue/total*100})
    rdf = pd.DataFrame(result)

    col1, col2 = st.columns(2)
    with col1:
        if not rdf.empty:
            top5_w = rdf.nlargest(5,'화이트칼라비율').sort_values('화이트칼라비율')
            fig = px.bar(top5_w, x='화이트칼라비율', y='지역', orientation='h',
                         color_discrete_sequence=['#60A5FA'],
                         text='화이트칼라비율', title="화이트칼라 비중 상위 지역 TOP5")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                              textfont=dict(color='#F8FAFC'))
            fig.update_xaxes(title='화이트칼라 비율(%)')
            st.plotly_chart(chart_layout(fig, showlegend=False), use_container_width=True)

    with col2:
        if not rdf.empty:
            top5_b = rdf.nlargest(5,'블루칼라비율').sort_values('블루칼라비율')
            fig2 = px.bar(top5_b, x='블루칼라비율', y='지역', orientation='h',
                          color_discrete_sequence=['#F97316'],
                          text='블루칼라비율', title="블루칼라 비중 상위 지역 TOP5")
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                               textfont=dict(color='#F8FAFC'))
            fig2.update_xaxes(title='블루칼라 비율(%)')
            st.plotly_chart(chart_layout(fig2, showlegend=False), use_container_width=True)

    insight_box("서울·세종 등 수도권은 화이트칼라 집중, 울산·경남·충남 등 제조업 지역은 블루칼라 집중 구조", "orange")

    st.markdown("---")
    if df_ind is not None and ind_year_cols:
        latest_ind = ind_year_cols[-1]
        # 제조업 비중 상위 지역
        total_by_reg = df_ind[(df_ind['시도별']!='계') & (df_ind['산업별'].str.contains('계',na=False))].groupby('시도별')[latest_ind].sum()
        mfg = df_ind[(df_ind['시도별']!='계') & (df_ind['산업명']=='제조업')].groupby('시도별')[latest_ind].sum()
        mfg_ratio = (mfg/total_by_reg*100).dropna().sort_values(ascending=False).head(5).reset_index()
        mfg_ratio.columns = ['지역','제조업비율']
        mfg_ratio = mfg_ratio.sort_values('제조업비율')
        fig3 = px.bar(mfg_ratio, x='제조업비율', y='지역', orientation='h',
                      color_discrete_sequence=['#34D399'],
                      text='제조업비율', title="제조업 취업자 비중 상위 지역 TOP5")
        fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                           textfont=dict(color='#F8FAFC'))
        fig3.update_xaxes(title='제조업 비율(%)')
        st.plotly_chart(chart_layout(fig3, showlegend=False), use_container_width=True)
        insight_box("블루칼라 비중이 높은 지역과 제조업 비중이 높은 지역이 상당 부분 일치한다.", "green")

# ══════════════════════════════════════════════════════════════
# 6. 임금 분석
# ══════════════════════════════════════════════════════════════
elif page == "6. 임금 분석":
    st.markdown('<div class="page-title">💰 임금 분석</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>화이트칼라와 블루칼라의 임금 수준은 어떤 차이가 있는가?</span>", unsafe_allow_html=True)
    reason_box("임금은 직군 차이를 설명하는 핵심 지표다. 관리자 포함·제외 기준을 함께 제시하여 왜곡 없이 비교한다.")
    st.markdown("---")

    df_inc, year_cols = load_wage(with_mgr=True)
    if df_inc is None:
        st.error("❌ 임금 데이터 파일을 찾을 수 없습니다.")
        st.stop()

    WAGE_MAP = {
        '관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가','사무 종사자(3)':'사무종사자',
        '서비스 종사자(4)':'서비스','판매 종사자(5)':'판매',
        '농림·어업 숙련 종사자(6)':'농림어업','기능원 및 관련기능종사자(7)':'기능원',
        '장치·기계 조작 및 조립종사자(8)':'기계조작','단순노무 종사자(9)':'단순노무',
    }
    TARGET = ['관리자','전문가','사무종사자','기능원','기계조작','단순노무']

    df_f = df_inc[df_inc['고용형태']=='전체근로자'].copy()
    df_f['직종'] = df_f['직종별'].map(WAGE_MAP).fillna(df_f['직종별'])
    latest = year_cols[-1]
    wdf = df_f[df_f['직종'].isin(TARGET)][['직종',latest]].dropna()
    wdf.columns = ['직종','월임금']
    wdf['직군'] = wdf['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
    wdf = wdf.sort_values('월임금', ascending=True)

    w_avg = wdf[wdf['직군']=='화이트칼라']['월임금'].mean()
    b_avg = wdf[wdf['직군']=='블루칼라']['월임금'].mean()

    c1,c2,c3 = st.columns(3)
    c1.metric("🔵 화이트칼라 평균", f"{w_avg:,.0f}천원/월", f"{latest}년 기준")
    c2.metric("🟠 블루칼라 평균", f"{b_avg:,.0f}천원/월", f"{latest}년 기준")
    c3.metric("월 임금 격차", f"{w_avg-b_avg:,.0f}천원")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(wdf, x='월임금', y='직종', orientation='h', color='직군',
                     color_discrete_map=COLOR_MAP, text='월임금',
                     title=f"직업 대분류별 월임금총액 ({latest}년)")
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside',
                          textfont=dict(color='#F8FAFC'))
        fig.update_xaxes(title='월임금 (천원)')
        fig.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with col2:
        # 연도별 추이
        line_data = []
        for y in year_cols:
            sub = df_f[df_f['직종'].isin(TARGET)][['직종',y]].dropna()
            sub['직군'] = sub['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
            for g in ['화이트칼라','블루칼라']:
                avg = sub[sub['직군']==g][y].mean()
                line_data.append({'연도':y,'직군':g,'평균임금':avg})
        ldf = pd.DataFrame(line_data).dropna()
        fig2 = px.line(ldf, x='연도', y='평균임금', color='직군',
                       color_discrete_map=COLOR_MAP, markers=True,
                       title="2020~2025 직군별 임금 추이")
        fig2.update_yaxes(title='월평균 임금 (천원)')
        st.plotly_chart(chart_layout(fig2), use_container_width=True)

    insight_box(f"전체 평균 격차 {w_avg-b_avg:,.0f}천원. 단, 대기업 생산직은 중소기업 사무직보다 높을 수 있어 단순 비교에 주의 필요", "orange")

# ══════════════════════════════════════════════════════════════
# 7. 산업별 직군 구조
# ══════════════════════════════════════════════════════════════
elif page == "7. 산업별 직군 구조":
    st.markdown('<div class="page-title">🏭 산업별 직군 구조</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#94A3B8;'>산업에 따라 화이트칼라와 블루칼라 구성은 어떻게 다른가?</span>", unsafe_allow_html=True)
    reason_box("구인·미충원 데이터는 직업분류 체계가 달라 메인 자료로 사용하기 어렵다. 대신 산업별 직업분포 데이터로 산업구조에 따른 직군 차이를 분석한다.")
    st.markdown("---")

    df_ij, val_cols = load_industry_job()
    if df_ij is None:
        st.error("❌ 산업별 직업별 데이터 파일을 찾을 수 없습니다.")
        st.stop()

    # 전국·계·최신 반기
    latest_col = val_cols[-1] if val_cols else None
    if latest_col is None:
        st.warning("데이터 컬럼을 찾을 수 없습니다.")
        st.stop()

    sub = df_ij[(df_ij['성별']=='계')].copy()
    sub = sub[~sub['직업별'].str.contains(r'^계$', na=False)]
    sub = sub[~sub['산업별'].str.contains(r'^계$', na=False)]
    sub[latest_col] = pd.to_numeric(sub[latest_col], errors='coerce')
    sub = sub.dropna(subset=[latest_col])

    # 주요 산업만 필터
    major_industries = ['제조업','건설업','운수및창고업','정보통신업','금융및보험업','전문·과학기술서비스업','교육서비스업']
    sub = sub[sub['산업명'].isin(major_industries)]

    if sub.empty:
        st.warning("주요 산업 데이터가 없습니다.")
        st.stop()

    # 산업별 직군 합계
    grp = sub.groupby(['산업명','직군'])[latest_col].sum().reset_index()
    total_by_ind = grp.groupby('산업명')[latest_col].sum().reset_index()
    total_by_ind.columns = ['산업명','합계']
    grp = grp.merge(total_by_ind, on='산업명')
    grp['비중'] = grp[latest_col]/grp['합계']*100

    # TOP5
    col1, col2 = st.columns(2)
    with col1:
        top5_w = grp[grp['직군']=='화이트칼라'].nlargest(5,'비중').sort_values('비중')
        if not top5_w.empty:
            fig = px.bar(top5_w, x='비중', y='산업명', orientation='h',
                         color_discrete_sequence=['#60A5FA'], text='비중',
                         title="화이트칼라 비중 높은 산업 TOP5")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                              textfont=dict(color='#F8FAFC'))
            fig.update_xaxes(title='화이트칼라 비중(%)')
            st.plotly_chart(chart_layout(fig, showlegend=False), use_container_width=True)

    with col2:
        top5_b = grp[grp['직군']=='블루칼라'].nlargest(5,'비중').sort_values('비중')
        if not top5_b.empty:
            fig2 = px.bar(top5_b, x='비중', y='산업명', orientation='h',
                          color_discrete_sequence=['#F97316'], text='비중',
                          title="블루칼라 비중 높은 산업 TOP5")
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                               textfont=dict(color='#F8FAFC'))
            fig2.update_xaxes(title='블루칼라 비중(%)')
            st.plotly_chart(chart_layout(fig2, showlegend=False), use_container_width=True)

    st.markdown("---")
    # 100% 누적 막대
    # 산업명을 문자열로 유지하고 정렬
    sort_order = grp[grp['직군']=='블루칼라'].sort_values('비중',ascending=False)['산업명'].tolist()
    # 없는 산업 추가
    for ind in major_industries:
        if ind not in sort_order:
            sort_order.append(ind)

    fig3 = px.bar(grp, x='산업명', y='비중', color='직군',
                  color_discrete_map=COLOR_MAP,
                  category_orders={'직군':['화이트칼라','블루칼라','기타'],
                                   '산업명': sort_order},
                  text=grp['비중'].map(lambda v: f"{v:.0f}%" if v>=8 else ""),
                  title="주요 산업별 직군 구성")
    fig3.update_traces(
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="#F8FAFC", size=12),
        marker_line_color="rgba(255,255,255,0.12)", marker_line_width=0.6
    )
    fig3.update_layout(barmode="stack")
    fig3.update_yaxes(range=[0,100], title="비중(%)")
    fig3.update_xaxes(title="")
    st.plotly_chart(chart_layout(fig3, height=430), use_container_width=True)
    insight_box("정보통신업·금융업은 화이트칼라 집중, 제조업·건설업은 블루칼라 집중 구조가 뚜렷하다.", "blue")

# ══════════════════════════════════════════════════════════════
# 8. 결론 및 시사점
# ══════════════════════════════════════════════════════════════
elif page == "8. 결론 및 시사점":
    st.markdown('<div class="page-title">📋 결론 및 시사점</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="section-title">📌 핵심 발견사항</div>', unsafe_allow_html=True)
    conclusions = [
        ("📊", "직군 분포 변화", "#60A5FA",
         "2016~2025년 화이트칼라 비중은 꾸준히 증가하고, 블루칼라 비중은 완만하게 감소했다."),
        ("🔬", "관리자 영향", "#A78BFA",
         "관리자 포함 여부는 화이트칼라 평균 임금 수치에 영향을 주지만, 핵심 추세(화이트 > 블루)는 변하지 않는다."),
        ("👥", "연령·학력 특성", "#34D399",
         "화이트칼라는 대졸 이상·30~40대 비중이 높고, 블루칼라는 고졸·50대 이상 비중이 상대적으로 높다."),
        ("🗺", "지역별 구조", "#38BDF8",
         "수도권·세종은 화이트칼라 집중, 울산·경남·충남 등 제조업 지역은 블루칼라 집중 구조가 뚜렷하다."),
        ("💰", "임금 격차", "#F97316",
         "화이트칼라 평균 임금이 블루칼라보다 높으나, 대기업 생산직 등 고숙련 블루칼라는 예외적으로 높을 수 있다."),
        ("🏭", "산업별 구조", "#FCA5A5",
         "정보통신·금융·전문서비스업은 화이트칼라 집중, 제조·건설·운수업은 블루칼라 집중 구조다."),
    ]
    for i in range(0, len(conclusions), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(conclusions):
                icon, title, color, desc = conclusions[i+j]
                with col:
                    st.markdown(
                        f'<div style="background:rgba(15,23,42,0.95);border:1px solid rgba(148,163,184,0.2);'
                        f'border-top:3px solid {color};border-radius:8px;padding:16px;margin:6px 0;">'
                        f'<div style="color:{color};font-weight:700;margin-bottom:8px;">{icon} {title}</div>'
                        f'<div style="color:#CBD5E1;font-size:13px;line-height:1.7;">{desc}</div></div>',
                        unsafe_allow_html=True
                    )

    st.markdown("---")
    st.markdown('<div class="section-title">💡 시사점</div>', unsafe_allow_html=True)
    suggestions = [
        ("📈", "직군 변화 해석", "블루칼라 비중 감소는 단순 선호 변화가 아닌 산업구조 변화와 함께 해석해야 한다."),
        ("🏗", "블루칼라의 중요성", "제조·건설·운수업에서 블루칼라는 여전히 핵심 직군으로, 해당 산업의 인력 수급이 중요하다."),
        ("🗺", "지역별 정책", "지역 노동시장 정책은 지역의 산업구조와 직군 분포를 함께 고려해야 한다."),
        ("🎓", "직업교육 설계", "기술인력 양성과 직업교육은 산업별 직군 구조를 반영해 설계할 필요가 있다."),
    ]
    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(suggestions):
        with cols[i%2]:
            st.markdown(
                f'<div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.25);'
                f'border-radius:8px;padding:14px 18px;margin:6px 0;">'
                f'<div style="color:#34D399;font-weight:600;margin-bottom:6px;">{icon} {title}</div>'
                f'<div style="color:#CBD5E1;font-size:13px;">{desc}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(15,23,42,0.98),rgba(11,17,32,0.98));
    border:1px solid rgba(148,163,184,0.2);border-top:3px solid #60A5FA;
    border-radius:10px;padding:24px;text-align:center;">
    <div style="color:#F1F5F9;font-size:1.1rem;font-weight:700;margin-bottom:12px;">최종 결론</div>
    <div style="color:#CBD5E1;font-size:13px;line-height:1.9;">
    대한민국 노동시장은 직군별로 뚜렷한 특성을 보이며 지역·학력·연령·임금 수준에서 구조적 차이가 존재한다.<br>
    화이트칼라 비중은 증가 추세이나, 블루칼라는 제조·건설·운수 등 핵심 산업에서 여전히 중요한 역할을 담당하고 있다.<br>
    데이터에 기반한 노동시장 이해가 인력 정책과 직업교육 설계의 출발점이 되어야 한다.
    </div></div>
    """, unsafe_allow_html=True)
