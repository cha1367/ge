import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="대한민국 노동시장 직군 분포 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 스타일 ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.metric-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8a 100%);
    border-radius: 12px; padding: 20px 24px; color: white;
    text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.metric-card .label { font-size: 13px; opacity: 0.85; margin-bottom: 8px; }
.metric-card .value { font-size: 32px; font-weight: 700; }
.metric-card .sub   { font-size: 12px; opacity: 0.7; margin-top: 4px; }

.white-card {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
    border-radius: 12px; padding: 20px 24px; color: white;
    text-align: center; box-shadow: 0 4px 15px rgba(37,99,235,0.3);
}
.blue-card {
    background: linear-gradient(135deg, #b45309 0%, #d97706 100%);
    border-radius: 12px; padding: 20px 24px; color: white;
    text-align: center; box-shadow: 0 4px 15px rgba(180,83,9,0.3);
}
.card-label { font-size: 13px; opacity: 0.9; margin-bottom: 6px; }
.card-value { font-size: 28px; font-weight: 700; }
.card-sub   { font-size: 12px; opacity: 0.8; margin-top: 4px; }

.section-title {
    font-size: 20px; font-weight: 700; color: #1e3a5f;
    border-left: 4px solid #2563eb; padding-left: 12px;
    margin: 24px 0 16px 0;
}
</style>
""", unsafe_allow_html=True)


# ── 데이터 경로 ─────────────────────────────────────────
# app.py 위치 기준으로 data 폴더 참조
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data
def load_data():
    # 1. 취업자 연도별
    df_year = pd.read_csv(f"{BASE}/직업별_취업자_연도별.csv")
    df_year.columns = ['직업별'] + [str(c) for c in df_year.columns[1:]]

    # 2. 임금 - 관리자 포함/미포함
    def load_wage(path):
        df = pd.read_csv(path, header=[0, 1])
        df.columns = ['고용형태', '직종별'] + [str(y) for y in range(2020, 2026)]
        return df[df['고용형태'] == '전체근로자'].copy()

    df_wage_incl = load_wage(f"{BASE}/관리자_포함.csv")
    df_wage_excl = load_wage(f"{BASE}/관리자_미_포함.csv")

    # 3. 시도별 (raw 그대로 보존)
    raw_region = pd.read_csv(f"{BASE}/시도별_직업별.csv", header=None)
    r_years = raw_region.iloc[0, 2:].tolist()
    df_region = raw_region.iloc[2:].copy()
    df_region.columns = ['행정구역', '직업별'] + r_years
    df_region = df_region.reset_index(drop=True)
    for c in r_years:
        df_region[c] = pd.to_numeric(df_region[c], errors='coerce')

    # 4. 학력/연령별
    raw_edu = pd.read_csv(f"{BASE}/직업별_학력별.csv", header=None)
    col_labels = raw_edu.iloc[0].tolist()
    sub_labels = raw_edu.iloc[1].tolist()

    # 5. 직종별 구인/미충원
    raw_jd = pd.read_csv(f"{BASE}/직종별_규모별.csv", header=None)
    jd_years = raw_jd.iloc[0, 3:].tolist()
    jd_subs  = raw_jd.iloc[1, 3:].tolist()
    df_jd = raw_jd.iloc[2:].copy()
    df_jd.columns = ['시도별', '규모별', '직종별'] + [f"{y}_{s}" for y, s in zip(jd_years, jd_subs)]
    df_jd = df_jd.reset_index(drop=True)

    return df_year, df_wage_incl, df_wage_excl, df_region, r_years, raw_edu, col_labels, sub_labels, df_jd

df_year, df_wage_incl, df_wage_excl, df_region, r_years, raw_edu, col_labels, sub_labels, df_jd = load_data()

# ── 분류 상수 ─────────────────────────────────────────────
WHITE_COLLAR  = ['2 전문가 및 관련 종사자', '3 사무 종사자']
BLUE_COLLAR   = ['7 기능원 및 관련 기능종사자', '8 장치,기계조작 및 조립종사자', '9 단순노무 종사자']
WHITE_REGION  = ['전문가 및 관련 종사자', '사무 종사자']
BLUE_REGION   = ['기능원 및 관련 기능 종사자', '장치\u200b\u2027기계 조작 및 조립 종사자', '단순 노무 종사자']


# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 분석 메뉴")
    page = st.radio(
        "",
        ["🏠 개요", "👤 직군 분포 분석", "🗺️ 지역별 분포", "💰 임금 분석", "🏭 노동시장 수요", "📋 결론"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**데이터 출처**")
    st.markdown("- 통계청 경제활동인구조사\n- 통계청 지역별고용조사\n- 고용노동부 직종별사업체노동력조사")
    st.markdown("**분석 기준**")
    st.markdown("한국표준직업분류(KSCO) 기준")


# ═══════════════════════════════════════════════════════
# PAGE 1: 개요
# ═══════════════════════════════════════════════════════
if page == "🏠 개요":
    st.title("대한민국 노동시장 직군 분포 분석")
    st.markdown("##### 화이트칼라와 블루칼라를 중심으로 | 통계청·고용노동부 데이터 기반")
    st.markdown("---")

    year_col  = '2025'
    total_val = pd.to_numeric(df_year[df_year['직업별'] == '계'][year_col].values[0], errors='coerce')

    def sum_group(jobs, col):
        s = 0
        for j in jobs:
            v = df_year[df_year['직업별'] == j][col]
            if not v.empty:
                s += pd.to_numeric(v.values[0], errors='coerce') or 0
        return s

    white_sum = sum_group(WHITE_COLLAR, year_col)
    blue_sum  = sum_group(BLUE_COLLAR,  year_col)
    other     = total_val - white_sum - blue_sum

    # KPI 카드
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">전체 취업자 (2025)</div>
            <div class="value">{total_val/1000:.1f}백만명</div>
            <div class="sub">({total_val:,.0f}천명)</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="white-card">
            <div class="card-label">🤍 화이트칼라</div>
            <div class="card-value">{white_sum:,.0f}천명</div>
            <div class="card-sub">{white_sum/total_val*100:.1f}% (관리자 제외)</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="blue-card">
            <div class="card-label">🔧 블루칼라</div>
            <div class="card-value">{blue_sum:,.0f}천명</div>
            <div class="card-sub">{blue_sum/total_val*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">기타 직종</div>
            <div class="value">{other:,.0f}천명</div>
            <div class="sub">{other/total_val*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        st.markdown('<div class="section-title">2025년 직군 비중 (관리자 제외)</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(go.Pie(
            labels=['화이트칼라', '블루칼라', '기타'],
            values=[white_sum, blue_sum, other],
            hole=0.55,
            marker_colors=['#2563eb', '#d97706', '#94a3b8'],
            textinfo='label+percent', textfont_size=13,
        ))
        fig_donut.update_layout(
            height=360, margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            annotations=[dict(text=f'{white_sum/total_val*100:.0f}%<br>화이트',
                              x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#2563eb')]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">연도별 화·블루칼라 취업자 추이</div>', unsafe_allow_html=True)
        years = [str(y) for y in range(2016, 2026)]
        w_vals, b_vals = [], []
        for y in years:
            w_vals.append(sum_group(WHITE_COLLAR, y))
            b_vals.append(sum_group(BLUE_COLLAR,  y))

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=years, y=w_vals, name='화이트칼라',
            line=dict(color='#2563eb', width=3), mode='lines+markers', marker=dict(size=7)))
        fig_trend.add_trace(go.Scatter(x=years, y=b_vals, name='블루칼라',
            line=dict(color='#d97706', width=3), mode='lines+markers', marker=dict(size=7)))
        fig_trend.update_layout(
            height=360, margin=dict(t=20, b=20, l=20, r=40),
            yaxis_title='취업자 수 (천명)',
            legend=dict(orientation='h', y=1.05),
            plot_bgcolor='white', paper_bgcolor='white',
            yaxis=dict(gridcolor='#f0f0f0'), xaxis=dict(gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # 세부 직종별
    st.markdown('<div class="section-title">2025년 세부 직종별 취업자 현황</div>', unsafe_allow_html=True)
    detail_jobs   = ['1 관리자', '2 전문가 및 관련 종사자', '3 사무 종사자',
                     '7 기능원 및 관련 기능종사자', '8 장치,기계조작 및 조립종사자', '9 단순노무 종사자']
    job_labels    = ['관리자', '전문가 및\n관련종사자', '사무 종사자',
                     '기능원 및\n관련기능', '장치·기계\n조작·조립', '단순노무']
    colors        = ['#93c5fd', '#2563eb', '#1d4ed8', '#f59e0b', '#d97706', '#b45309']
    vals = []
    for j in detail_jobs:
        v = df_year[df_year['직업별'] == j]['2025']
        vals.append(pd.to_numeric(v.values[0], errors='coerce') if not v.empty else 0)

    fig_bar = go.Figure(go.Bar(
        x=job_labels, y=vals, marker_color=colors,
        text=[f'{v:,.0f}천명' for v in vals], textposition='outside', textfont_size=12
    ))
    fig_bar.update_layout(
        height=320, margin=dict(t=10, b=10, l=20, r=20),
        yaxis_title='취업자 수 (천명)',
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis=dict(gridcolor='#f0f0f0'), showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 2: 직군 분포 분석 (연령·학력)
# ═══════════════════════════════════════════════════════
elif page == "👤 직군 분포 분석":
    st.title("직군 분포 분석")
    st.markdown("연령과 학력에 따른 화이트칼라·블루칼라 분포 차이를 분석합니다.")
    st.markdown("---")

    target_period = '2024.1/2'
    period_indices = [i for i, c in enumerate(col_labels) if c == target_period]

    if period_indices:
        start_idx = period_indices[0]

        target_rows = {
            '화이트칼라\n(전문가·관련종사자)': '전문가 및 관련 종사자',
            '화이트칼라\n(사무종사자)':        '사무 종사자',
            '블루칼라\n(기능원·관련기능)':     '기능원 및 관련 기능 종사자',
            '블루칼라\n(장치·기계조작)':       '장치·기계 조작 및 조립 종사자',
            '블루칼라\n(단순노무)':            '단순노무 종사자',
        }
        age_cols_name = ['15~29세', '30~39세', '40~49세', '50~59세', '60세 이상']
        edu_cols_name = ['중졸이하', '고졸', '대졸이상']

        age_data, edu_data = [], []
        for label, row_name in target_rows.items():
            row_match = raw_edu[raw_edu.iloc[:, 0] == row_name]
            if row_match.empty:
                continue
            row_vals = row_match.iloc[0, start_idx:start_idx+9].tolist()
            for i, ag in enumerate(age_cols_name):
                v = pd.to_numeric(row_vals[i+1], errors='coerce')
                age_data.append({'직종': label, '연령대': ag, '취업자': v or 0})
            for i, ec in enumerate(edu_cols_name):
                v = pd.to_numeric(row_vals[i+6], errors='coerce')
                edu_data.append({'직종': label, '학력': ec, '취업자': v or 0})

        df_age      = pd.DataFrame(age_data)
        df_edu_chart = pd.DataFrame(edu_data)

        # 연령별 100% 누적 막대
        st.markdown('<div class="section-title">연령대별 직종 분포 (2024년 상반기)</div>', unsafe_allow_html=True)
        age_pivot = df_age.pivot_table(index='연령대', columns='직종', values='취업자', aggfunc='sum').fillna(0)
        age_pct   = age_pivot.div(age_pivot.sum(axis=1), axis=0) * 100
        age_order = ['15~29세', '30~39세', '40~49세', '50~59세', '60세 이상']
        age_pct   = age_pct.reindex([a for a in age_order if a in age_pct.index])

        colors_stack = ['#1d4ed8', '#2563eb', '#f59e0b', '#d97706', '#b45309']
        fig_age = go.Figure()
        for col, color in zip(age_pct.columns, colors_stack):
            fig_age.add_trace(go.Bar(
                name=col, x=age_pct.index, y=age_pct[col],
                marker_color=color,
                text=[f'{v:.1f}%' for v in age_pct[col]],
                textposition='inside', textfont_size=11
            ))
        fig_age.update_layout(
            barmode='stack', height=380,
            yaxis_title='비율 (%)', xaxis_title='연령대',
            legend=dict(orientation='h', y=-0.25, font_size=11),
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(t=10, b=80, l=20, r=20)
        )
        st.plotly_chart(fig_age, use_container_width=True)

        # 학력별 트리맵
        st.markdown('<div class="section-title">학력별 직종 취업자 분포 트리맵 (2024년 상반기)</div>', unsafe_allow_html=True)
        df_edu_chart['구분']    = df_edu_chart['직종'].apply(lambda x: '화이트칼라' if '화이트' in x else '블루칼라')
        df_edu_chart['직종단순'] = df_edu_chart['직종'].str.replace('\n', ' ')

        fig_tree = px.treemap(
            df_edu_chart, path=['구분', '학력', '직종단순'], values='취업자',
            color='구분',
            color_discrete_map={'화이트칼라': '#2563eb', '블루칼라': '#d97706'},
        )
        fig_tree.update_layout(height=420, margin=dict(t=10, b=10))
        fig_tree.update_traces(textfont_size=12)
        st.plotly_chart(fig_tree, use_container_width=True)

    else:
        st.warning("2024.1/2 기간 데이터를 찾을 수 없습니다.")


# ═══════════════════════════════════════════════════════
# PAGE 3: 지역별 분포
# ═══════════════════════════════════════════════════════
elif page == "🗺️ 지역별 분포":
    st.title("지역별 직군 분포 분석")
    st.markdown("17개 시도별 화이트칼라·블루칼라 취업자 비중을 비교합니다.")
    st.markdown("---")

    # 최신 컬럼 자동 선택 (2025.2/2 우선, 없으면 마지막 컬럼)
    avail_year_cols = [c for c in r_years if '2025' in str(c)]
    target_year = avail_year_cols[-1] if avail_year_cols else r_years[-1]

    sido_list = [s for s in df_region['행정구역'].unique() if s not in ['계', '행정구역별']]

    region_stats = []
    for sido in sido_list:
        sub   = df_region[df_region['행정구역'] == sido]
        total = sub[sub['직업별'] == '계'][target_year].values
        if len(total) == 0 or np.isnan(total[0]):
            continue
        total = total[0]

        def safe_sum(jobs):
            s = 0
            for j in jobs:
                r = sub[sub['직업별'] == j][target_year]
                if not r.empty and not np.isnan(r.values[0]):
                    s += r.values[0]
            return s

        white = safe_sum(WHITE_REGION)
        blue  = safe_sum(BLUE_REGION)

        if total > 0:
            region_stats.append({
                '지역': sido, '전체': total,
                '화이트칼라': white, '블루칼라': blue,
                '화이트비율': white / total * 100,
                '블루비율':   blue  / total * 100,
            })

    df_rs = pd.DataFrame(region_stats).sort_values('화이트비율', ascending=False)

    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown('<div class="section-title">지역별 화이트·블루칼라 비율 비교</div>', unsafe_allow_html=True)
        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(
            y=df_rs['지역'], x=df_rs['화이트비율'], orientation='h',
            name='화이트칼라', marker_color='#2563eb',
            text=[f'{v:.1f}%' for v in df_rs['화이트비율']], textposition='outside'
        ))
        fig_region.add_trace(go.Bar(
            y=df_rs['지역'], x=df_rs['블루비율'], orientation='h',
            name='블루칼라', marker_color='#d97706',
            text=[f'{v:.1f}%' for v in df_rs['블루비율']], textposition='outside'
        ))
        fig_region.update_layout(
            barmode='group', height=520,
            xaxis_title='비율 (%)',
            legend=dict(orientation='h', y=1.05),
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(t=10, b=20, l=10, r=60),
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">지역별 취업자 구성 (100% 누적)</div>', unsafe_allow_html=True)
        df_rs2 = df_rs.copy()
        df_rs2['기타비율'] = 100 - df_rs2['화이트비율'] - df_rs2['블루비율']

        fig_stack = go.Figure()
        for col, color, name in [('화이트비율','#2563eb','화이트칼라'),
                                  ('블루비율','#d97706','블루칼라'),
                                  ('기타비율','#94a3b8','기타')]:
            fig_stack.add_trace(go.Bar(
                y=df_rs2['지역'], x=df_rs2[col], orientation='h',
                name=name, marker_color=color
            ))
        fig_stack.update_layout(
            barmode='stack', height=520,
            xaxis_title='비율 (%)',
            legend=dict(orientation='h', y=1.05),
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(t=10, b=20, l=10, r=20),
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    st.markdown('<div class="section-title">시도별 상세 현황</div>', unsafe_allow_html=True)
    disp = df_rs[['지역','전체','화이트칼라','블루칼라','화이트비율','블루비율']].copy()
    disp.columns = ['지역','전체(천명)','화이트칼라(천명)','블루칼라(천명)','화이트비율(%)','블루비율(%)']
    disp['화이트비율(%)'] = disp['화이트비율(%)'].round(1)
    disp['블루비율(%)']   = disp['블루비율(%)'].round(1)
    st.dataframe(disp.set_index('지역'), use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 4: 임금 분석
# ═══════════════════════════════════════════════════════
elif page == "💰 임금 분석":
    st.title("직군별 임금 분석")
    st.markdown("화이트칼라와 블루칼라의 월임금총액을 비교합니다.")
    st.markdown("---")

    mode = st.radio("분석 모드", ["관리자 제외", "관리자 포함"], horizontal=True)
    df_w = df_wage_excl if mode == "관리자 제외" else df_wage_incl

    white_jobs_wage = ['전문가 및 관련종사자(2)', '사무 종사자(3)']
    blue_jobs_wage  = ['기능원 및 관련 기능 종사자(7)', '장치·기계 조작 및 조립 종사자(8)', '단순노무 종사자(9)']
    if mode == "관리자 포함":
        white_jobs_wage = ['관리자(1)'] + white_jobs_wage

    years_wage = ['2020', '2021', '2022', '2023', '2024', '2025']
    all_wage_jobs = white_jobs_wage + blue_jobs_wage

    wage_colors = {
        '관리자(1)':                      '#93c5fd',
        '전문가 및 관련종사자(2)':          '#2563eb',
        '사무 종사자(3)':                  '#1d4ed8',
        '기능원 및 관련 기능 종사자(7)':    '#fbbf24',
        '장치·기계 조작 및 조립 종사자(8)': '#d97706',
        '단순노무 종사자(9)':              '#b45309',
    }
    short_names = {
        '관리자(1)':                      '관리자',
        '전문가 및 관련종사자(2)':          '전문가',
        '사무 종사자(3)':                  '사무',
        '기능원 및 관련 기능 종사자(7)':    '기능원',
        '장치·기계 조작 및 조립 종사자(8)': '장치·기계',
        '단순노무 종사자(9)':              '단순노무',
    }

    st.markdown('<div class="section-title">연도별 월임금총액 추이 (천원)</div>', unsafe_allow_html=True)
    fig_wage = go.Figure()
    for job in all_wage_jobs:
        row = df_w[df_w['직종별'] == job]
        if row.empty:
            continue
        vals_w = [pd.to_numeric(row[y].values[0], errors='coerce') for y in years_wage]
        fig_wage.add_trace(go.Scatter(
            x=years_wage, y=vals_w,
            name=short_names.get(job, job),
            line=dict(color=wage_colors.get(job, '#888'), width=2.5),
            mode='lines+markers', marker=dict(size=7)
        ))
    fig_wage.update_layout(
        height=400, margin=dict(t=10, b=10, l=20, r=20),
        yaxis_title='월임금총액 (천원)',
        legend=dict(orientation='h', y=-0.2),
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis=dict(gridcolor='#f0f0f0'), xaxis=dict(gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig_wage, use_container_width=True)

    st.markdown('<div class="section-title">2025년 직종별 월임금총액 비교</div>', unsafe_allow_html=True)
    wage_2025 = []
    for job in all_wage_jobs:
        row = df_w[df_w['직종별'] == job]
        if row.empty:
            continue
        v = pd.to_numeric(row['2025'].values[0], errors='coerce')
        wage_2025.append({'직종': short_names.get(job, job), '임금': v,
                          '구분': '화이트칼라' if job in white_jobs_wage else '블루칼라'})

    df_w25 = pd.DataFrame(wage_2025).sort_values('임금', ascending=False)
    fig_w25 = go.Figure(go.Bar(
        x=df_w25['직종'], y=df_w25['임금'],
        marker_color=['#2563eb' if g == '화이트칼라' else '#d97706' for g in df_w25['구분']],
        text=[f'{v:,.0f}천원' for v in df_w25['임금']],
        textposition='outside', textfont_size=12
    ))
    fig_w25.update_layout(
        height=380, margin=dict(t=10, b=10, l=20, r=20),
        yaxis_title='월임금총액 (천원)',
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis=dict(gridcolor='#f0f0f0'), showlegend=False
    )
    st.plotly_chart(fig_w25, use_container_width=True)

    st.markdown('<div class="section-title">전직종 평균 대비 임금 비율 (2025년)</div>', unsafe_allow_html=True)
    avg_row = df_w[df_w['직종별'] == '전직종']
    if not avg_row.empty:
        avg_wage = pd.to_numeric(avg_row['2025'].values[0], errors='coerce')
        df_w25['평균대비'] = df_w25['임금'] / avg_wage * 100
        fig_ratio = go.Figure(go.Bar(
            x=df_w25['직종'], y=df_w25['평균대비'],
            marker_color=['#2563eb' if g == '화이트칼라' else '#d97706' for g in df_w25['구분']],
            text=[f'{v:.1f}%' for v in df_w25['평균대비']], textposition='outside'
        ))
        fig_ratio.add_hline(y=100, line_dash='dash', line_color='red', annotation_text='전직종 평균(100%)')
        fig_ratio.update_layout(
            height=320, margin=dict(t=10, b=10, l=20, r=20),
            yaxis_title='전직종 평균 대비 (%)',
            plot_bgcolor='white', paper_bgcolor='white',
            yaxis=dict(gridcolor='#f0f0f0'),
        )
        st.plotly_chart(fig_ratio, use_container_width=True)
        st.caption(f"* 전직종 평균 임금 기준: {avg_wage:,.0f}천원 (2025년)")


# ═══════════════════════════════════════════════════════
# PAGE 5: 노동시장 수요 및 인력 부족
# ═══════════════════════════════════════════════════════
elif page == "🏭 노동시장 수요":
    st.title("노동시장 수요 및 인력 부족 분석")
    st.markdown("직종별 구인인원과 미충원율을 통해 인력 부족 현황을 파악합니다.")
    st.markdown("---")

    df_jd_nation = df_jd[(df_jd['시도별'] == '전국') & (df_jd['규모별'] == '전규모(1인이상)')].copy()
    df_jd_nation['직종명'] = df_jd_nation['직종별'].str.replace(r'^\d+ ', '', regex=True)

    # 최신 기간 컬럼 자동 탐색
    recruit_cols_all = [c for c in df_jd_nation.columns if '구인인원' in c]
    rate_cols_all    = [c for c in df_jd_nation.columns if '부족률'   in c]
    unfill_cols_all  = [c for c in df_jd_nation.columns if '미충원인원' in c]

    recruit_col = recruit_cols_all[-1] if recruit_cols_all else None
    rate_col    = rate_cols_all[-1]    if rate_cols_all    else None
    unfill_col  = unfill_cols_all[-1]  if unfill_cols_all  else None

    if recruit_col:
        for c in [recruit_col, unfill_col, rate_col]:
            if c:
                df_jd_nation[c] = pd.to_numeric(df_jd_nation[c], errors='coerce')

        white_kw = ['경영', '연구', '교육', '보건', '예술']
        def get_color(job):
            return '#2563eb' if any(kw in job for kw in white_kw) else '#d97706'

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="section-title">직종별 구인인원 ({recruit_col.split("_")[0]})</div>', unsafe_allow_html=True)
            df_recruit = df_jd_nation.sort_values(recruit_col, ascending=True)
            fig_recruit = go.Figure(go.Bar(
                x=df_recruit[recruit_col], y=df_recruit['직종명'], orientation='h',
                marker_color=[get_color(j) for j in df_recruit['직종명']],
                text=[f'{v:,.0f}명' for v in df_recruit[recruit_col]], textposition='outside',
            ))
            fig_recruit.update_layout(
                height=380, margin=dict(t=10, b=10, l=10, r=80),
                xaxis_title='구인인원 (명)',
                plot_bgcolor='white', paper_bgcolor='white',
                xaxis=dict(gridcolor='#f0f0f0')
            )
            st.plotly_chart(fig_recruit, use_container_width=True)

        with c2:
            st.markdown(f'<div class="section-title">직종별 미충원율 ({rate_col.split("_")[0]})</div>', unsafe_allow_html=True)
            df_rate = df_jd_nation.sort_values(rate_col, ascending=True)
            fig_rate = go.Figure(go.Bar(
                x=df_rate[rate_col], y=df_rate['직종명'], orientation='h',
                marker_color=[get_color(j) for j in df_rate['직종명']],
                text=[f'{v:.1f}%' for v in df_rate[rate_col]], textposition='outside',
            ))
            fig_rate.update_layout(
                height=380, margin=dict(t=10, b=10, l=10, r=60),
                xaxis_title='미충원율 (%)',
                plot_bgcolor='white', paper_bgcolor='white',
                xaxis=dict(gridcolor='#f0f0f0')
            )
            st.plotly_chart(fig_rate, use_container_width=True)

        # 히트맵
        st.markdown('<div class="section-title">연도별 직종별 미충원율 히트맵</div>', unsafe_allow_html=True)
        period_labels = [c.replace('_부족률 (%)', '') for c in rate_cols_all]
        heat_data = []
        for _, row in df_jd_nation.iterrows():
            vals = [pd.to_numeric(row.get(c, None), errors='coerce') for c in rate_cols_all]
            heat_data.append(vals)

        job_names = df_jd_nation['직종명'].tolist()
        fig_heat = go.Figure(go.Heatmap(
            z=heat_data, x=period_labels, y=job_names,
            colorscale='RdYlGn_r',
            text=[[f'{v:.1f}%' if not np.isnan(v) else '' for v in row] for row in heat_data],
            texttemplate='%{text}', textfont_size=10,
            colorbar_title='미충원율(%)'
        ))
        fig_heat.update_layout(
            height=420, margin=dict(t=10, b=10, l=20, r=20),
            xaxis_title='기간',
            plot_bgcolor='white', paper_bgcolor='white',
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    else:
        st.error("구인인원 컬럼을 찾을 수 없습니다.")
        st.write(df_jd_nation.columns.tolist())


# ═══════════════════════════════════════════════════════
# PAGE 6: 결론
# ═══════════════════════════════════════════════════════
elif page == "📋 결론":
    st.title("분석 결론")
    st.markdown("---")

    items = [
        ("화이트칼라와 블루칼라 분포 현황",
         "2025년 기준 전체 취업자 중 화이트칼라(전문가·사무직)는 약 47%, 블루칼라(기능원·기계조작·단순노무)는 약 30%를 차지한다. "
         "관리자를 포함할 경우 화이트칼라 비중이 더 높아지지만, 관리자는 소수 고임금 직종으로 별도 분석이 필요하다."),
        ("연령 및 학력 특성",
         "화이트칼라는 20~40대 대졸 이상 인력이 중심을 이루는 반면, "
         "블루칼라는 40대 이상 고졸 이하 인력 비중이 높게 나타난다. "
         "이는 고령화에 따른 블루칼라 인력 수급 문제와 연결된다."),
        ("지역별 차이",
         "서울·대전 등 행정·금융 중심 도시는 화이트칼라 비율이 높고, "
         "경남·울산·충남 등 제조업 집중 지역은 블루칼라 비율이 상대적으로 높다."),
        ("임금 수준 비교",
         "화이트칼라의 월임금총액은 전직종 평균 대비 높은 수준이며, "
         "특히 전문가 직종의 임금 상승세가 두드러진다. "
         "고숙련 블루칼라의 임금 경쟁력도 증가하는 추세를 보인다."),
        ("노동시장 수요",
         "구인인원 기준으로는 서비스·판매·운전 관련직의 수요가 높고, "
         "기술·공학직도 지속적으로 높은 구인 수요를 보인다."),
        ("인력 부족 현황",
         "미충원율은 건설·채굴직, 설치·정비·생산직에서 지속적으로 높게 나타나 "
         "블루칼라 일부 직종의 인력 부족 현상이 구조적임을 시사한다."),
    ]

    for i, (title, content) in enumerate(items, 1):
        with st.expander(f"**{i}. {title}**", expanded=True):
            st.markdown(content)

    st.markdown("---")
    st.markdown("""
### 최종 결론
대한민국 노동시장은 직군별로 **뚜렷한 연령·학력·지역·임금 차이**를 보이며,
일부 블루칼라 직종에서는 **지속적인 인력 부족**이 구조적으로 나타나고 있다.
화이트칼라 선호 경향이 사회 전반에 존재하지만,
실제 데이터는 고숙련 블루칼라 직종의 **임금 경쟁력 상승**과 함께
수급 불균형이 심화되고 있음을 보여준다.

> *데이터 출처: 통계청 경제활동인구조사·지역별고용조사, 고용노동부 직종별사업체노동력조사*
    """)
