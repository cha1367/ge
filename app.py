import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="화이트칼라 · 블루칼라 분포 분석",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0d1117; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] .stRadio label { color: #e6edf3 !important; font-size:14px; padding:6px 0; }
[data-testid="metric-container"] { background:#161b22; border:1px solid #30363d; border-radius:12px; padding:16px; }
[data-testid="metric-container"] * { color:#e6edf3 !important; }
h1 { color:#58a6ff !important; }
h2,h3 { color:#e6edf3 !important; }
.insight-box { background:#161b22; border-left:4px solid #58a6ff; border-radius:0 8px 8px 0; padding:12px 16px; margin:8px 0; color:#8b949e; font-size:14px; }
.insight-red { border-left-color:#f85149; }
.insight-green { border-left-color:#3fb950; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
hr { border-color:#30363d !important; }
</style>
""", unsafe_allow_html=True)

CW = '#58a6ff'
CB = '#f85149'
CO = '#6e7681'

WHITE = ['1 관리자', '2 전문가 및 관련 종사자', '3 사무 종사자']
BLUE  = ['7 기능원 및 관련 기능종사자', '8 장치,기계조작 및 조립종사자', '9 단순노무 종사자']
ALL_KOR = {
    '1 관리자':'관리자','2 전문가 및 관련 종사자':'전문가','3 사무 종사자':'사무종사자',
    '7 기능원 및 관련 기능종사자':'기능원','8 장치,기계조작 및 조립종사자':'기계조작','9 단순노무 종사자':'단순노무'
}

LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#8b949e', family='sans-serif'),
    margin=dict(t=40,b=30,l=20,r=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3')),
    xaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#8b949e'),
    yaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#8b949e'),
)

def insight(text, color='blue'):
    cls = 'insight-box' + (' insight-red' if color=='red' else ' insight-green' if color=='green' else '')
    st.markdown(f'<div class="{cls}">💡 {text}</div>', unsafe_allow_html=True)

# ── 데이터 로드 ───────────────────────────
@st.cache_data
def load_yearly():
    df = pd.read_csv("data/직업별_취업자_연도별.csv.csv", encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    return df, year_cols, df.columns[0]

@st.cache_data
def load_region():
    df = pd.read_csv("data/시도별_직업별.csv.csv", encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '행정구역'
    df.columns.values[1] = '직업별'
    return df

@st.cache_data
def load_gender():
    df = pd.read_csv("data/성별_직업별.csv.csv", encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    return df, year_cols

@st.cache_data
def load_age():
    df = pd.read_csv("data/직업별_학력별.csv.csv", encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '직업별'
    cols_2024 = [c for c in df.columns if '2024.1/2' in str(c)]
    return df, cols_2024

@st.cache_data
def load_wage():
    df = pd.read_csv("data/직종별_임금.csv.csv", encoding='utf-8-sig')
    items = df.iloc[0].tolist()
    df = df.iloc[1:].reset_index(drop=True)
    return df, items

# ── 사이드바 ──────────────────────────────
with st.sidebar:
    st.markdown("## 📊 직종 분포 분석")
    st.markdown("**화이트칼라 · 블루칼라**")
    st.markdown("---")
    page = st.radio("", [
        "🏠  프로젝트 소개",
        "📊  전국 현황",
        "🗺   지역별 분포",
        "👥  성별 분포",
        "🎂  연령별 분포",
        "💰  임금 비교",
        "📝  결론"
    ])
    st.markdown("---")
    st.markdown("🔵 **화이트칼라**\n관리자 · 전문가 · 사무")
    st.markdown("🔴 **블루칼라**\n기능원 · 기계조작 · 단순노무")
    st.markdown("---")
    st.caption("출처: 통계청 KOSIS · 고용노동부")

# ══════════════════════════════════════════
# 1. 프로젝트 소개
# ══════════════════════════════════════════
if page == "🏠  프로젝트 소개":
    st.title("대한민국 화이트칼라 · 블루칼라 분포 현황 분석")
    st.markdown("#### 우리는 곧 노동시장으로 진출합니다. 그 시장의 실제 구조를 데이터로 확인합니다.")
    st.markdown("---")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown("### 🎯 분석 목적\n졸업 후 우리가 진출할 노동시장의 실제 구조를 이해하기 위해 화이트칼라와 블루칼라 직종의 분포를 다각도로 분석합니다.")
    with col2:
        st.markdown("### 📋 분석 범위\n- 전국 직종별 취업자 추이\n- 17개 시도별 분포\n- 성별 · 연령별 분포\n- 직종별 평균 임금 비교")
    with col3:
        st.markdown("### 🗂 데이터 출처\n- 통계청 경제활동인구조사\n- 통계청 지역별고용조사\n- 고용노동부 근로실태조사\n- 기준: 2016~2024년")
    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("""<div style='background:#161b22;border:1px solid #30363d;border-top:3px solid #58a6ff;border-radius:8px;padding:20px;'>
        <h4 style='color:#58a6ff;margin:0 0 12px 0;'>🔵 화이트칼라</h4>
        <p style='color:#8b949e;margin:4px 0;'>• 관리자 — 기업 임원, 고위 공무원</p>
        <p style='color:#8b949e;margin:4px 0;'>• 전문가 — 의사, IT개발자, 교수 등</p>
        <p style='color:#8b949e;margin:4px 0;'>• 사무종사자 — 일반 사무직, 행정직</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style='background:#161b22;border:1px solid #30363d;border-top:3px solid #f85149;border-radius:8px;padding:20px;'>
        <h4 style='color:#f85149;margin:0 0 12px 0;'>🔴 블루칼라</h4>
        <p style='color:#8b949e;margin:4px 0;'>• 기능원 — 용접공, 배관공, 전기공</p>
        <p style='color:#8b949e;margin:4px 0;'>• 장치·기계조작 — 공장 기계, 운전직</p>
        <p style='color:#8b949e;margin:4px 0;'>• 단순노무 — 환경미화, 택배, 건설</p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 2. 전국 현황 — 파이 + 라인(Area)
# ══════════════════════════════════════════
elif page == "📊  전국 현황":
    st.title("📊 전국 화이트칼라 · 블루칼라 현황")
    st.markdown("---")

    df, year_cols, job_col = load_yearly()
    wr = df[df[job_col].isin(WHITE)]
    br = df[df[job_col].isin(BLUE)]
    tr = df[df[job_col]=='계']
    latest = year_cols[-1]

    wv = wr[latest].astype(float).sum()
    bv = br[latest].astype(float).sum()
    tv = float(tr[latest].values[0])
    ov = tv - wv - bv

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("전체 취업자", f"{tv/10000:.1f}만명", f"{latest}년")
    c2.metric("🔵 화이트칼라", f"{wv/tv*100:.1f}%", f"{wv:.0f}천명")
    c3.metric("🔴 블루칼라", f"{bv/tv*100:.1f}%", f"{bv:.0f}천명")
    c4.metric("AI 전환점", "2022년", "ChatGPT 등장")

    st.markdown("---")
    col1,col2 = st.columns([1,1.5])

    with col1:
        st.markdown("#### 직군별 비율 (도넛 차트)")
        pie = pd.DataFrame({'직군':['화이트칼라','블루칼라','기타'], '취업자':[wv,bv,ov]})
        fig = px.pie(pie, values='취업자', names='직군', hole=0.55,
                     color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO})
        fig.update_traces(textposition='outside', textinfo='percent+label',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight(f"블루칼라 {bv/tv*100:.1f}% — 전체 취업자 약 {bv/10:.0f}만명")

    with col2:
        st.markdown("#### 연도별 취업자 추이 (Area Chart) — ChatGPT(2022) 전후")
        trend = [{'연도':y,'화이트칼라':wr[y].astype(float).sum(),'블루칼라':br[y].astype(float).sum()} for y in year_cols]
        tdf = pd.DataFrame(trend)
        fig3 = go.Figure()
        fig3.add_vrect(x0='2022', x1=year_cols[-1],
                       fillcolor='rgba(88,166,255,0.05)',
                       annotation_text='ChatGPT 이후',
                       annotation_position='top left',
                       annotation_font_color='#58a6ff', line_width=0)
        fig3.add_vline(x='2022', line_dash='dash', line_color='#58a6ff', line_width=1.5)
        fig3.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라',
                                  line=dict(color=CW,width=3), mode='lines+markers',
                                  fill='tozeroy', fillcolor='rgba(88,166,255,0.15)'))
        fig3.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라',
                                  line=dict(color=CB,width=3), mode='lines+markers',
                                  fill='tozeroy', fillcolor='rgba(248,81,73,0.15)'))
        fig3.update_layout(**LAYOUT, height=360, xaxis_title='연도', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig3, use_container_width=True)
        insight("2022년 이후 화이트칼라 증가세 유지, 블루칼라 소폭 감소 — AI의 간접적 영향")

# ══════════════════════════════════════════
# 3. 지역별 — 트리맵 + 스몰 멀티플 막대
# ══════════════════════════════════════════
elif page == "🗺   지역별 분포":
    st.title("🗺 시도별 화이트칼라 · 블루칼라 분포")
    st.markdown("---")

    df = load_region()
    WHITE_R = ['관리자','전문가 및 관련 종사자','사무 종사자']
    BLUE_R  = ['기능원 및 관련 기능 종사자','장치‧기계 조작 및 조립 종사자','단순 노무 종사자']

    val_cols = [c for c in df.columns if '2024' in str(c) and '1/2' in str(c)]
    latest_col = val_cols[0] if val_cols else df.columns[2]

    regions = [r for r in df['행정구역'].unique() if r not in ['행정구역별','계']]
    result = []
    for reg in regions:
        sub = df[df['행정구역']==reg].copy()
        sub[latest_col] = pd.to_numeric(sub[latest_col], errors='coerce')
        total_row = sub[sub['직업별']=='계']
        if total_row.empty: continue
        total = float(total_row[latest_col].values[0])
        white = sub[sub['직업별'].isin(WHITE_R)][latest_col].sum()
        blue  = sub[sub['직업별'].isin(BLUE_R)][latest_col].sum()
        if total > 0:
            result.append({'지역':reg,'화이트칼라':white,'블루칼라':blue,
                           '화이트비율':white/total*100,'블루비율':blue/total*100,'총취업자':total})
    rdf = pd.DataFrame(result)

    # 트리맵 — 블루칼라 규모
    st.markdown("#### 시도별 블루칼라 취업자 규모 (트리맵)")
    rdf_tree = rdf.copy()
    rdf_tree['라벨'] = rdf_tree.apply(lambda x: f"{x['지역']}\n{x['블루비율']:.1f}%", axis=1)
    fig_tree = px.treemap(rdf_tree, path=['지역'], values='블루칼라',
                          color='블루비율',
                          color_continuous_scale=[[0,'#21262d'],[0.5,'#f85149'],[1,'#ff6b6b']],
                          hover_data={'블루비율':':.1f','블루칼라':':.0f'},
                          custom_data=['블루비율'])
    fig_tree.update_traces(
        texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}%',
        textfont=dict(color='white', size=13)
    )
    fig_tree.update_layout(**LAYOUT, height=400, coloraxis_showscale=False)
    st.plotly_chart(fig_tree, use_container_width=True)
    insight("울산·경남·충남 등 제조업 밀집 지역일수록 블루칼라 비율이 높게 나타납니다", 'red')

    st.markdown("---")
    st.markdown("#### 시도별 화이트 vs 블루칼라 비율 비교 (로리팝 차트)")
    rdf_s = rdf.sort_values('블루비율', ascending=True)

    fig2 = go.Figure()
    for _, row in rdf_s.iterrows():
        fig2.add_trace(go.Scatter(
            x=[row['화이트비율'], row['블루비율']],
            y=[row['지역'], row['지역']],
            mode='lines', line=dict(color='#30363d', width=2),
            showlegend=False
        ))
    fig2.add_trace(go.Scatter(
        x=rdf_s['화이트비율'], y=rdf_s['지역'],
        mode='markers', name='화이트칼라',
        marker=dict(color=CW, size=12, line=dict(color='white',width=1))
    ))
    fig2.add_trace(go.Scatter(
        x=rdf_s['블루비율'], y=rdf_s['지역'],
        mode='markers', name='블루칼라',
        marker=dict(color=CB, size=12, line=dict(color='white',width=1))
    ))
    fig2.update_layout(**LAYOUT, height=500,
                       xaxis_title='비율 (%)', yaxis_title='',
                       yaxis=dict(gridcolor='#21262d', color='#8b949e'))
    st.plotly_chart(fig2, use_container_width=True)
    insight("서울·세종은 화이트칼라, 울산·경남은 블루칼라가 압도적 — 지역별 산업 구조 반영")

# ══════════════════════════════════════════
# 4. 성별 — 도넛 2개 + 스택형 막대 + 라인
# ══════════════════════════════════════════
elif page == "👥  성별 분포":
    st.title("👥 성별 직종 분포")
    st.markdown("---")

    df, year_cols = load_gender()
    latest = year_cols[-1]
    WHITE_G = ['1 관리자','2 전문가 및 관련 종사자','3 사무 종사자']
    BLUE_G  = ['7 기능원 및 관련 기능종사자','8 장치,기계조작 및 조립종사자','9 단순노무 종사자']

    # 도넛 차트 2개 (남/여 직군 비율)
    st.markdown("#### 성별 직군 비율 (도넛 차트)")
    col1, col2 = st.columns(2)
    for gender, col, title in [('남자',col1,'남성'),('여자',col2,'여성')]:
        sub = df[df['성별']==gender]
        w = sub[sub['직업별'].isin(WHITE_G)][latest].apply(pd.to_numeric, errors='coerce').sum()
        b = sub[sub['직업별'].isin(BLUE_G)][latest].apply(pd.to_numeric, errors='coerce').sum()
        donut = pd.DataFrame({'직군':['화이트칼라','블루칼라'], '취업자':[w,b]})
        fig = px.pie(donut, values='취업자', names='직군', hole=0.55,
                     title=f'{title} 직군 비율',
                     color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB})
        fig.update_traces(textposition='outside', textinfo='percent+label',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=320, showlegend=False,
                          title_font=dict(color='#e6edf3'))
        with col:
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 스택형 막대 — 직종별 남/여 구성
    st.markdown("#### 직종별 남성·여성 취업자 구성 (스택형 막대)")
    LABEL_G = {
        '1 관리자':'관리자','2 전문가 및 관련 종사자':'전문가','3 사무 종사자':'사무종사자',
        '7 기능원 및 관련 기능종사자':'기능원','8 장치,기계조작 및 조립종사자':'기계조작','9 단순노무 종사자':'단순노무'
    }
    stack_data = []
    for gender in ['남자','여자']:
        sub = df[(df['성별']==gender) & (df['직업별'].isin(WHITE_G+BLUE_G))][['직업별',latest]].copy()
        sub[latest] = pd.to_numeric(sub[latest], errors='coerce')
        sub['직업별'] = sub['직업별'].map(LABEL_G)
        sub['성별'] = '남성' if gender=='남자' else '여성'
        stack_data.append(sub)
    sdf = pd.concat(stack_data)
    sdf.columns = ['직종','취업자','성별']

    fig2 = px.bar(sdf, x='직종', y='취업자', color='성별', barmode='stack',
                  color_discrete_map={'남성':'#58a6ff','여성':'#f778ba'},
                  text='취업자')
    fig2.update_traces(texttemplate='%{text:.0f}', textposition='inside',
                       textfont=dict(color='white', size=10))
    fig2.update_layout(**LAYOUT, height=360, xaxis_title='', yaxis_title='취업자 수 (천명)')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    # 라인 차트 — 연도별 추이
    st.markdown("#### 성별 블루칼라 비율 추이 (Line Chart)")
    trend = []
    for y in year_cols:
        for gender in ['남자','여자']:
            sub = df[df['성별']==gender]
            w = sub[sub['직업별'].isin(WHITE_G)][y].apply(pd.to_numeric, errors='coerce').sum()
            b = sub[sub['직업별'].isin(BLUE_G)][y].apply(pd.to_numeric, errors='coerce').sum()
            t = w+b
            if t>0:
                trend.append({'연도':y,'성별':'남성' if gender=='남자' else '여성','블루칼라비율':b/t*100})
    tdf = pd.DataFrame(trend)
    fig3 = px.line(tdf, x='연도', y='블루칼라비율', color='성별',
                   color_discrete_map={'남성':'#58a6ff','여성':'#f778ba'},
                   markers=True)
    fig3.update_layout(**LAYOUT, height=300, yaxis_title='블루칼라 비율 (%)')
    st.plotly_chart(fig3, use_container_width=True)
    insight("남성 블루칼라 비율이 여성보다 훨씬 높으며, 이 격차는 연도별로 유지됩니다", 'red')

# ══════════════════════════════════════════
# 5. 연령별 — 인구 피라미드 + 누적막대
# ══════════════════════════════════════════
elif page == "🎂  연령별 분포":
    st.title("🎂 연령별 직종 분포")
    st.markdown("---")

    df, cols_2024 = load_age()
    age_labels = ['15~29세','30~39세','40~49세','50~59세','60세이상']
    target_cols = cols_2024[:6] if len(cols_2024)>=6 else cols_2024
    rename_map = {target_cols[i]: (['취업자']+age_labels)[i] for i in range(min(len(target_cols),6))}

    WHITE_A = ['관리자','전문가 및 관련 종사자','사무 종사자']
    BLUE_A  = ['기능원 및 관련 기능종사자','장치‧기계 조작 및 조립 종사자','단순 노무 종사자']
    LABEL_A = {
        '관리자':'관리자','전문가 및 관련 종사자':'전문가','사무 종사자':'사무종사자',
        '기능원 및 관련 기능종사자':'기능원','장치‧기계 조작 및 조립 종사자':'기계조작','단순 노무 종사자':'단순노무'
    }
    adf = df[df['직업별'].isin(WHITE_A+BLUE_A)].copy()
    adf = adf.rename(columns=rename_map)
    adf['직업별'] = adf['직업별'].map(LABEL_A)
    adf['직군'] = adf['직업별'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
    for c in age_labels:
        if c in adf.columns:
            adf[c] = pd.to_numeric(adf[c], errors='coerce')

    age_avail = [c for c in age_labels if c in adf.columns]

    # 인구 피라미드 스타일
    st.markdown("#### 연령대별 화이트 vs 블루칼라 (인구 피라미드)")
    pyr_data = []
    for age in age_avail:
        w = adf[adf['직군']=='화이트칼라'][age].sum()
        b = adf[adf['직군']=='블루칼라'][age].sum()
        pyr_data.append({'연령대':age, '화이트칼라':w, '블루칼라':-b})
    pdf = pd.DataFrame(pyr_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=pdf['연령대'], x=pdf['화이트칼라'], name='화이트칼라',
                         orientation='h', marker_color=CW,
                         text=pdf['화이트칼라'], texttemplate='%{text:.0f}',
                         textposition='outside', textfont=dict(color='#e6edf3')))
    fig.add_trace(go.Bar(y=pdf['연령대'], x=pdf['블루칼라'], name='블루칼라',
                         orientation='h', marker_color=CB,
                         text=pdf['블루칼라'].abs(), texttemplate='%{text:.0f}',
                         textposition='outside', textfont=dict(color='#e6edf3')))
    fig.update_layout(**LAYOUT, height=380, barmode='overlay',
                      xaxis_title='취업자 수 (천명)', yaxis_title='',
                      xaxis=dict(tickformat=',.0f', gridcolor='#21262d', color='#8b949e'))
    st.plotly_chart(fig, use_container_width=True)
    insight("50대 이상 고령층에서 블루칼라 비중 증가 — 젊은층 블루칼라 기피 현상과 연관")

    st.markdown("---")
    # 누적막대 — 직종별 연령 구성
    st.markdown("#### 직종별 연령대 구성 (누적 막대)")
    melt = pd.melt(adf[['직업별','직군']+age_avail],
                   id_vars=['직업별','직군'], var_name='연령대', value_name='취업자')
    colors_age = ['#58a6ff','#3fb950','#e3b341','#f85149','#bc8cff']
    fig2 = px.bar(melt, x='직업별', y='취업자', color='연령대', barmode='stack',
                  color_discrete_sequence=colors_age, text='취업자')
    fig2.update_traces(texttemplate='%{text:.0f}', textposition='inside',
                       textfont=dict(color='white', size=9))
    fig2.update_layout(**LAYOUT, height=380, xaxis_title='', yaxis_title='취업자 수 (천명)')
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════
# 6. 임금 — 박스플롯 + 산점도
# ══════════════════════════════════════════
elif page == "💰  임금 비교":
    st.title("💰 직종별 평균 임금 비교")
    st.markdown("---")

    df, items = load_wage()
    total = df[df.iloc[:,0]=='전체근로자'].copy()
    wage_col = total.columns[74] if len(total.columns)>74 else total.columns[-7]
    wdata = total[[total.columns[1], wage_col]].copy()
    wdata.columns = ['직종','월임금(천원)']
    wdata['월임금(천원)'] = pd.to_numeric(wdata['월임금(천원)'], errors='coerce')
    wdata = wdata.dropna()

    WLABEL = {
        '전직종':'전직종','관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가',
        '사무 종사자(3)':'사무종사자','서비스 종사자(4)':'서비스',
        '판매 종사자(5)':'판매','농림·어업 숙련 종사자(6)':'농림어업',
        '기능원 및 관련기능종사자(7)':'기능원','장치·기계 조작 및 조립종사자(8)':'기계조작',
        '단순노무 종사자(9)':'단순노무',
    }
    wdata['직종'] = wdata['직종'].map(WLABEL).fillna(wdata['직종'])
    target = ['관리자','전문가','사무종사자','기능원','기계조작','단순노무']
    wdf = wdata[wdata['직종'].isin(target)].copy()
    wdf['직군'] = wdf['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')

    # 연도별 임금 데이터 구성 (다중 연도)
    years = ['2020','2021','2022','2023','2024','2025']
    all_wage = []
    for i, yr in enumerate(years):
        base_idx = 2 + i*13
        if base_idx+7 < len(df.columns):
            wc = df.columns[base_idx+7]
            sub = df[df.iloc[:,0]=='전체근로자'][[df.columns[1], wc]].copy()
            sub.columns = ['직종','월임금']
            sub['월임금'] = pd.to_numeric(sub['월임금'], errors='coerce')
            sub['직종'] = sub['직종'].map(WLABEL).fillna(sub['직종'])
            sub = sub[sub['직종'].isin(target)].dropna()
            sub['연도'] = yr
            sub['직군'] = sub['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
            all_wage.append(sub)
    wage_all = pd.concat(all_wage) if all_wage else wdf.rename(columns={'월임금(천원)':'월임금'})

    w_avg = wdf[wdf['직군']=='화이트칼라']['월임금(천원)'].mean()
    b_avg = wdf[wdf['직군']=='블루칼라']['월임금(천원)'].mean()

    c1,c2,c3 = st.columns(3)
    c1.metric("🔵 화이트칼라 평균", f"{w_avg:,.0f}천원/월")
    c2.metric("🔴 블루칼라 평균", f"{b_avg:,.0f}천원/월")
    c3.metric("월 임금 격차", f"{w_avg-b_avg:,.0f}천원")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 연도별 직군 평균 임금 추이 (Line Chart)")
        line_data = wage_all.groupby(['연도','직군'])['월임금'].mean().reset_index()
        fig = px.line(line_data, x='연도', y='월임금', color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB},
                      markers=True, text='월임금')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='top center',
                          textfont=dict(color='#e6edf3', size=10))
        fig.update_layout(**LAYOUT, height=360, yaxis_title='월평균 임금 (천원)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 직종별 임금 + 직군 평균선 (Combo Chart)")
        wdf_s = wdf.sort_values('월임금(천원)')
        fig2 = go.Figure()
        colors = [CW if x in ['관리자','전문가','사무종사자'] else CB for x in wdf_s['직종']]
        fig2.add_trace(go.Bar(x=wdf_s['직종'], y=wdf_s['월임금(천원)'],
                              marker_color=colors, name='월임금',
                              text=wdf_s['월임금(천원)'],
                              texttemplate='%{text:,.0f}', textposition='outside',
                              textfont=dict(color='#e6edf3')))
        fig2.add_hline(y=w_avg, line_dash='dash', line_color=CW, line_width=1.5,
                       annotation_text=f'화이트 평균 {w_avg:,.0f}',
                       annotation_font_color=CW)
        fig2.add_hline(y=b_avg, line_dash='dash', line_color=CB, line_width=1.5,
                       annotation_text=f'블루 평균 {b_avg:,.0f}',
                       annotation_font_color=CB)
        fig2.update_layout(**LAYOUT, height=360, xaxis_title='', yaxis_title='월임금 (천원)')
        st.plotly_chart(fig2, use_container_width=True)

    insight(f"전체 평균 기준 격차 {w_avg-b_avg:,.0f}천원 — 단, 대기업 생산직은 중소기업 사무직보다 높을 수 있습니다")

# ══════════════════════════════════════════
# 7. 결론 — 요약 카드 + 슬로프 그래프
# ══════════════════════════════════════════
elif page == "📝  결론":
    st.title("📝 분석 결론")
    st.markdown("---")

    df, year_cols, job_col = load_yearly()
    latest = year_cols[-1]
    first  = year_cols[0]
    wr = df[df[job_col].isin(WHITE)]
    br = df[df[job_col].isin(BLUE)]
    tv = float(df[df[job_col]=='계'][latest].values[0])
    tv0= float(df[df[job_col]=='계'][first].values[0])
    wv = wr[latest].astype(float).sum()
    bv = br[latest].astype(float).sum()
    wv0= wr[first].astype(float).sum()
    bv0= br[first].astype(float).sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("블루칼라 취업자", f"{bv:.0f}천명", f"{bv-bv0:+.0f}천명 ({first}→{latest})")
    c2.metric("블루칼라 비율", f"{bv/tv*100:.1f}%")
    c3.metric("화이트칼라 취업자", f"{wv:.0f}천명", f"{wv-wv0:+.0f}천명 ({first}→{latest})")
    c4.metric("화이트칼라 비율", f"{wv/tv*100:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        # 슬로프 그래프 (변화 비교)
        st.markdown("#### 직종별 취업자 변화 (슬로프 그래프)")
        slope_data = []
        for job in WHITE+BLUE:
            row = df[df[job_col]==job]
            if row.empty: continue
            v0 = float(row[first].values[0])
            v1 = float(row[latest].values[0])
            label = ALL_KOR.get(job, job)
            grup = '화이트칼라' if job in WHITE else '블루칼라'
            slope_data.append({'직종':label,'시작':v0,'끝':v1,'직군':grup,'변화':v1-v0})
        sdf = pd.DataFrame(slope_data)

        fig = go.Figure()
        for _, row in sdf.iterrows():
            color = CW if row['직군']=='화이트칼라' else CB
            fig.add_trace(go.Scatter(
                x=[first, latest], y=[row['시작'], row['끝']],
                mode='lines+markers+text',
                name=row['직종'],
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                text=[f"{row['직종']} {row['시작']:.0f}", f"{row['끝']:.0f}"],
                textposition=['middle left','middle right'],
                textfont=dict(color='#e6edf3', size=11),
                showlegend=False
            ))
        fig.update_layout(**LAYOUT, height=400,
                          xaxis=dict(tickvals=[first,latest], gridcolor='#21262d', color='#8b949e'),
                          yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 핵심 발견사항")
        st.markdown("""
        <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:8px 0;'>
        <h5 style='color:#58a6ff;margin:0 0 8px 0;'>📊 분포 현황</h5>
        <p style='color:#8b949e;font-size:13px;'>블루칼라 약 30% — 대한민국 산업을 실질적으로 떠받치는 핵심 노동력</p>
        </div>
        <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:8px 0;'>
        <h5 style='color:#3fb950;margin:0 0 8px 0;'>🗺 지역 구조</h5>
        <p style='color:#8b949e;font-size:13px;'>수도권 화이트칼라 집중, 제조업 지역 블루칼라 집중 — 공간적 분리</p>
        </div>
        <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:8px 0;'>
        <h5 style='color:#e3b341;margin:0 0 8px 0;'>👥 성별·연령</h5>
        <p style='color:#8b949e;font-size:13px;'>남성·고령층에 블루칼라 집중, 여성·청년층에 화이트칼라 집중</p>
        </div>
        <div style='background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:8px 0;'>
        <h5 style='color:#f85149;margin:0 0 8px 0;'>💰 임금 구조</h5>
        <p style='color:#8b949e;font-size:13px;'>평균 격차 존재 — 단, 대기업 생산직은 예외적으로 높음</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:linear-gradient(135deg,#161b22,#0d1117);border:1px solid #30363d;
    border-top:3px solid #58a6ff;border-radius:8px;padding:24px;text-align:center;'>
    <h3 style='color:#e6edf3;margin:0 0 12px 0;'>우리 학과 졸업생의 대다수는 블루칼라 직군으로 진출합니다</h3>
    <p style='color:#8b949e;'>데이터가 보여주듯, 블루칼라는 대한민국 노동시장의 30%를 차지하는 핵심 인력입니다.<br>
    지역별·성별·연령별 분포를 이해하는 것이 우리의 진로 설계에 중요한 첫걸음입니다.</p>
    </div>
    """, unsafe_allow_html=True)
