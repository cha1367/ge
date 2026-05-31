# ============================================================
# 대한민국 노동시장의 직군 분포와 인력 수급 특성 분석
# 화이트칼라와 블루칼라를 중심으로
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="직군 분포 및 인력 수급 분석",
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
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="metric-container"] * { color: #e6edf3 !important; }
h1 { color: #58a6ff !important; }
h2, h3 { color: #e6edf3 !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
hr { border-color: #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────
CW = '#58a6ff'
CB = '#f85149'
CO = '#6e7681'

WHITE_JOBS = ['1 관리자', '2 전문가 및 관련 종사자', '3 사무 종사자']
BLUE_JOBS  = ['7 기능원 및 관련 기능종사자', '8 장치,기계조작 및 조립종사자', '9 단순노무 종사자']
WHITE_REGION = ['관리자', '전문가 및 관련 종사자', '사무 종사자']
BLUE_REGION  = ['기능원 및 관련 기능 종사자', '장치‧기계 조작 및 조립 종사자', '단순 노무 종사자']
WHITE_SUPPLY = ['0 경영ㆍ사무ㆍ금융ㆍ보험직', '1 연구직 및 공학기술직',
                '2 교육ㆍ법률ㆍ사회복지ㆍ경찰ㆍ소방직 및 군인', '3 보건ㆍ의료직']
BLUE_SUPPLY  = ['5 미용ㆍ여행ㆍ숙박ㆍ음식ㆍ경비ㆍ청소직', '6 영업ㆍ판매ㆍ운전ㆍ운송직',
                '7 건설ㆍ채굴직', '8 설치ㆍ정비ㆍ생산직', '9 농림어업직']

LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#8b949e'), margin=dict(t=40,b=30,l=20,r=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3')),
    xaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#8b949e'),
    yaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#8b949e'),
)

def insight(text, color='blue'):
    c = {'blue':'#58a6ff','red':'#f85149','green':'#3fb950','yellow':'#e3b341'}.get(color,'#58a6ff')
    st.markdown(
        f'<div style="background:#161b22;border-left:4px solid {c};border-radius:0 8px 8px 0;'
        f'padding:12px 16px;margin:8px 0;color:#8b949e;font-size:14px;">💡 {text}</div>',
        unsafe_allow_html=True
    )

def card(title, content, color='#58a6ff'):
    st.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-top:3px solid {color};'
        f'border-radius:8px;padding:20px;margin:6px 0;">'
        f'<h4 style="color:{color};margin:0 0 10px 0;">{title}</h4>'
        f'<p style="color:#8b949e;font-size:13px;line-height:1.7;margin:0;">{content}</p></div>',
        unsafe_allow_html=True
    )

# ── 데이터 로딩 ───────────────────────────────────────────────
@st.cache_data
def load_yearly():
    df = pd.read_csv("data/직업별_취업자_연도별.csv", encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    return df, year_cols, df.columns[0]

@st.cache_data
def load_gender():
    df = pd.read_csv("data/성별_직업별.csv", encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    return df, year_cols

@st.cache_data
def load_region():
    df = pd.read_csv("data/시도별_직업별.csv", encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '행정구역'
    df.columns.values[1] = '직업별'
    val_cols = [c for c in df.columns if '/' in str(c)]
    return df, val_cols

@st.cache_data
def load_wage():
    # 관리자 포함/미포함 두 파일 로드
    df_inc = pd.read_csv("data/관리자_포함.csv", encoding='utf-8-sig')
    df_inc = df_inc.iloc[1:].reset_index(drop=True)
    df_exc = pd.read_csv("data/관리자_미_포함.csv", encoding='utf-8-sig')
    df_exc = df_exc.iloc[1:].reset_index(drop=True)
    # 헤더행 제거
    df_inc = df_inc.iloc[1:].reset_index(drop=True)
    df_exc = df_exc.iloc[1:].reset_index(drop=True)
    year_cols = [c for c in df_inc.columns if c.isdigit() and len(c)==4]
    return df_inc, df_exc, year_cols

@st.cache_data
def load_edu():
    df = pd.read_csv("data/직업별_학력별.csv", encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '직업별'
    # 최신 반기 컬럼 (2024.1/2 기준: 취업자, 15~29, 30~39, 40~49, 50~59, 60이상, 중졸이하, 고졸, 대졸이상)
    latest = '2024.1/2'
    cols_2024 = [c for c in df.columns if latest in str(c)]
    return df, cols_2024

@st.cache_data
def load_supply():
    df = pd.read_csv("data/직종별·규모별.csv", encoding='utf-8-sig')
    df = df.iloc[1:].reset_index(drop=True)
    df.columns.values[0] = '시도별'
    df.columns.values[1] = '규모별'
    df.columns.values[2] = '직종별'
    df = df.iloc[1:].reset_index(drop=True)
    national = df[(df['시도별']=='전국') & (df['규모별']=='전규모(1인이상)')].copy()
    val_cols = [c for c in df.columns if '/' in str(c)]
    return national, val_cols

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 직군 분포 분석")
    st.markdown("**화이트칼라 · 블루칼라**")
    st.markdown("---")
    page = st.radio("", [
        "🏠  프로젝트 소개",
        "📊  직군 분포 분석",
        "🗺   지역별 분포 분석",
        "💰  임금 분석",
        "🏭  노동시장 수요 및 인력 수급",
        "📋  결론 및 시사점"
    ])
    st.markdown("---")
    st.markdown("**🔵 화이트칼라**\n관리자 · 전문가 · 사무")
    st.markdown("**🔴 블루칼라**\n기능원 · 기계조작 · 단순노무")
    st.markdown("---")
    st.caption("출처: 통계청 KOSIS · 고용노동부")

# ══════════════════════════════════════════════════════════════
# 페이지 1. 프로젝트 소개
# ══════════════════════════════════════════════════════════════
if page == "🏠  프로젝트 소개":
    st.title("대한민국 노동시장의 직군 분포와\n인력 수급 특성 분석")
    st.markdown("#### — 화이트칼라와 블루칼라를 중심으로 —")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        card("🎯 주제 선정 이유",
             "과거에는 화이트칼라 직종이 선호되는 경향이 강했지만, 최근 반도체·정유·생산기술직 등 "
             "고임금 기술직이 주목받으면서 블루칼라 직군에 대한 인식도 변화하고 있다. "
             "일부 산업에서는 지속적인 인력 부족 현상이 발생하고 있어 객관적인 데이터 분석이 필요하다.",
             '#58a6ff')
    with col2:
        card("❓ 문제 제기",
             "사회적 인식과 달리 실제 노동시장에서는 화이트칼라와 블루칼라가 어떻게 분포되어 있는가? "
             "각 직군은 지역, 성별, 임금 수준 측면에서 어떠한 차이를 보이며, "
             "어떤 직군에서 인력 부족 현상이 나타나고 있는가?",
             '#e3b341')
    with col3:
        card("🎯 분석 목표",
             "① 직군별 분포 분석<br>"
             "② 지역별 분포 차이 분석<br>"
             "③ 성별 직군 특성 분석<br>"
             "④ 직군별 임금 수준 비교<br>"
             "⑤ 노동시장 인력 수요 분석<br>"
             "⑥ 미충원율 기반 인력 부족 분석",
             '#3fb950')

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        card("🔵 화이트칼라 분류 (KSCO 기준)",
             "• 관리자<br>• 전문가 및 관련 종사자<br>• 사무 종사자", '#58a6ff')
    with col2:
        card("🔴 블루칼라 분류 (KSCO 기준)",
             "• 기능원 및 관련 기능 종사자<br>• 장치·기계조작 및 조립 종사자<br>• 단순노무 종사자", '#f85149')

    st.markdown("---")
    st.markdown("### 📋 분석 흐름")
    items = [
        ("📊", "직군 분포", "전국 비율 및 추이"),
        ("🗺", "지역별 분포", "시도별 차이"),
        ("💰", "임금 분석", "직종별 임금 비교"),
        ("🏭", "인력 수급", "구인·미충원 분석"),
        ("📋", "결론", "종합 시사점"),
    ]
    cols = st.columns(len(items))
    for i, (icon, title, desc) in enumerate(items):
        with cols[i]:
            st.markdown(
                f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
                f'padding:14px;text-align:center;">'
                f'<div style="font-size:28px;">{icon}</div>'
                f'<div style="color:#e6edf3;font-size:12px;font-weight:bold;margin:6px 0;">{title}</div>'
                f'<div style="color:#6e7681;font-size:11px;">{desc}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### 🗂 사용 데이터")
    data_rows = [
        ("직업별 취업자 수 (연도별)", "통계청 경제활동인구조사", "2016~2025"),
        ("성별 직업별 취업자 수", "통계청 경제활동인구조사", "2016~2025"),
        ("시도별 직업별 취업자 수", "통계청 지역별고용조사", "2015~2025"),
        ("직종별 월임금총액", "고용노동부 고용형태별근로실태조사", "2020~2025"),
        ("직업별 연령·학력별 취업자", "통계청 지역별고용조사", "2014~2024"),
        ("직종별 구인인원 및 미충원율", "고용노동부 직종별사업체노동력조사", "2021~2025"),
    ]
    for name, src, period in data_rows:
        st.markdown(
            f'<div style="background:#161b22;border:1px solid #30363d;border-radius:6px;'
            f'padding:10px 16px;margin:4px 0;">'
            f'<span style="color:#e6edf3;font-size:13px;">📁 {name}</span>'
            f'<span style="color:#8b949e;font-size:12px;float:right;">{src} | {period}</span></div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════
# 페이지 2. 직군 분포 분석
# ══════════════════════════════════════════════════════════════
elif page == "📊  직군 분포 분석":
    st.title("📊 직군 분포 분석")
    st.markdown("**대한민국 노동자는 화이트칼라와 블루칼라 중 어디에 더 많이 분포하는가?**")
    st.markdown("---")

    df, year_cols, job_col = load_yearly()
    df_g, year_cols_g = load_gender()

    wr = df[df[job_col].isin(WHITE_JOBS)]
    br = df[df[job_col].isin(BLUE_JOBS)]
    tr = df[df[job_col]=='계']

    # 연도 슬라이더
    selected = st.select_slider("📅 기준 연도 선택", options=year_cols, value=year_cols[-1])

    wv = wr[selected].astype(float).sum()
    bv = br[selected].astype(float).sum()
    tv = float(tr[selected].values[0])
    ov = tv - wv - bv

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("전체 취업자", f"{tv/10000:.1f}만명", f"{selected}년")
    c2.metric("🔵 화이트칼라", f"{wv/tv*100:.1f}%", f"{wv:.0f}천명")
    c3.metric("🔴 블루칼라", f"{bv/tv*100:.1f}%", f"{bv:.0f}천명")
    c4.metric("기타 직종", f"{ov/tv*100:.1f}%", f"{ov:.0f}천명")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### 직군별 비율 ({selected}년) — 도넛 차트")
        pie = pd.DataFrame({'직군':['화이트칼라','블루칼라','기타'], '취업자':[wv,bv,ov]})
        fig = px.pie(pie, values='취업자', names='직군', hole=0.52,
                     color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO})
        fig.update_traces(textposition='outside', textinfo='percent+label',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight(f"블루칼라 {bv/tv*100:.1f}% ({bv:.0f}천명) — 전체 취업자의 약 {bv/tv*100:.0f}% 차지")

    with col2:
        st.markdown("#### 연도별 취업자 추이 — Line Chart")
        trend = [{'연도':y,'화이트칼라':wr[y].astype(float).sum(),'블루칼라':br[y].astype(float).sum()} for y in year_cols]
        tdf = pd.DataFrame(trend)
        fig2 = go.Figure()
        fig2.add_vline(x='2022', line_dash='dash', line_color='#e3b341', line_width=1.5)
        fig2.add_annotation(x='2022', y=1, yref='paper', text='2022 ChatGPT',
                           font=dict(color='#e3b341'), showarrow=False,
                           xanchor='left', yanchor='bottom')
        fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라',
                                  line=dict(color=CW,width=3), mode='lines+markers',
                                  fill='tozeroy', fillcolor='rgba(88,166,255,0.1)'))
        fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라',
                                  line=dict(color=CB,width=3), mode='lines+markers',
                                  fill='tozeroy', fillcolor='rgba(248,81,73,0.1)'))
        fig2.update_layout(**LAYOUT, height=360, xaxis_title='연도', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig2, use_container_width=True)
        insight("화이트칼라는 꾸준히 증가, 블루칼라는 완만하게 감소 추세")

    st.markdown("---")
    st.markdown("#### 성별 화이트·블루칼라 비율 — 100% 누적 막대")
    col1, col2 = st.columns(2)
    for gender, col, label in [('남자',col1,'남성'),('여자',col2,'여성')]:
        gender_trend = []
        for y in year_cols_g:
            sub = df_g[df_g['성별']==gender]
            w = sub[sub['직업별'].isin(WHITE_JOBS)][y].apply(pd.to_numeric,errors='coerce').sum()
            b = sub[sub['직업별'].isin(BLUE_JOBS)][y].apply(pd.to_numeric,errors='coerce').sum()
            t = w+b
            if t>0:
                gender_trend.append({'연도':y,'화이트칼라':w/t*100,'블루칼라':b/t*100})
        gdf = pd.DataFrame(gender_trend)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name='화이트칼라', x=gdf['연도'], y=gdf['화이트칼라'],
                              marker_color=CW, text=gdf['화이트칼라'],
                              texttemplate='%{text:.0f}%', textposition='inside'))
        fig3.add_trace(go.Bar(name='블루칼라', x=gdf['연도'], y=gdf['블루칼라'],
                              marker_color=CB, text=gdf['블루칼라'],
                              texttemplate='%{text:.0f}%', textposition='inside'))
        fig3.update_layout(**LAYOUT, height=320, barmode='stack',
                           title=label, title_font_color='#e6edf3',
                           yaxis_title='비율 (%)', xaxis_title='')
        with col:
            st.plotly_chart(fig3, use_container_width=True)
    insight("남성은 블루칼라 비율이 높고, 여성은 화이트칼라(사무·전문직) 비중이 더 높음", 'red')

# ══════════════════════════════════════════════════════════════
# 페이지 3. 지역별 분포 분석
# ══════════════════════════════════════════════════════════════
elif page == "🗺   지역별 분포 분석":
    st.title("🗺 지역별 분포 분석")
    st.markdown("**지역에 따라 화이트칼라와 블루칼라 비중은 어떻게 다른가?**")
    st.markdown("---")

    df, val_cols = load_region()

    # 연도 슬라이더 (반기 선택)
    period_options = sorted(list(set([c.split('.')[0] for c in val_cols])))
    selected_period = st.select_slider(
        "📅 기준 시점 선택",
        options=val_cols,
        value=val_cols[-1]
    )
    latest_col = selected_period

    regions = [r for r in df['행정구역'].unique() if r not in ['행정구역별','계','전국']]
    result = []
    for reg in regions:
        sub = df[df['행정구역']==reg].copy()
        sub[latest_col] = pd.to_numeric(sub[latest_col], errors='coerce')
        total_row = sub[sub['직업별']=='계']
        if total_row.empty: continue
        total = float(total_row[latest_col].values[0])
        white = sub[sub['직업별'].isin(WHITE_REGION)][latest_col].sum()
        blue  = sub[sub['직업별'].isin(BLUE_REGION)][latest_col].sum()
        if total>0:
            result.append({'지역':reg,'화이트칼라비율':white/total*100,
                           '블루칼라비율':blue/total*100,'총취업자':total})
    rdf = pd.DataFrame(result)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 시도별 블루칼라 비율")
        fig = px.bar(rdf.sort_values('블루칼라비율',ascending=True),
                     x='블루칼라비율', y='지역', orientation='h',
                     color='블루칼라비율',
                     color_continuous_scale=[[0,'#21262d'],[1,CB]],
                     text='블루칼라비율')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=520, showlegend=False,
                          coloraxis_showscale=False,
                          xaxis_title='블루칼라 비율 (%)', yaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 시도별 화이트칼라 비율")
        fig2 = px.bar(rdf.sort_values('화이트칼라비율',ascending=True),
                      x='화이트칼라비율', y='지역', orientation='h',
                      color='화이트칼라비율',
                      color_continuous_scale=[[0,'#21262d'],[1,CW]],
                      text='화이트칼라비율')
        fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                           textfont=dict(color='#e6edf3'))
        fig2.update_layout(**LAYOUT, height=520, showlegend=False,
                           coloraxis_showscale=False,
                           xaxis_title='화이트칼라 비율 (%)', yaxis_title='')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 시도별 화이트 vs 블루칼라 비교 — 로리팝 차트")
    rdf_s = rdf.sort_values('블루칼라비율', ascending=True)
    fig3 = go.Figure()
    for _, row in rdf_s.iterrows():
        fig3.add_trace(go.Scatter(x=[row['화이트칼라비율'],row['블루칼라비율']],
                                  y=[row['지역'],row['지역']], mode='lines',
                                  line=dict(color='#30363d',width=2), showlegend=False))
    fig3.add_trace(go.Scatter(x=rdf_s['화이트칼라비율'], y=rdf_s['지역'],
                              mode='markers', name='화이트칼라',
                              marker=dict(color=CW,size=14,line=dict(color='white',width=1))))
    fig3.add_trace(go.Scatter(x=rdf_s['블루칼라비율'], y=rdf_s['지역'],
                              mode='markers', name='블루칼라',
                              marker=dict(color=CB,size=14,line=dict(color='white',width=1))))
    fig3.update_layout(**LAYOUT, height=520, xaxis_title='비율 (%)', yaxis_title='')
    st.plotly_chart(fig3, use_container_width=True)
    insight("서울·세종은 화이트칼라 집중, 울산·경남·충남은 블루칼라 집중 — 지역 산업 구조 반영", 'red')

# ══════════════════════════════════════════════════════════════
# 페이지 4. 임금 분석
# ══════════════════════════════════════════════════════════════
elif page == "💰  임금 분석":
    st.title("💰 임금 분석")
    st.markdown("**화이트칼라와 블루칼라의 임금 수준은 어떤 차이가 있는가?**")
    st.markdown("---")

    df_inc, df_exc, year_cols = load_wage()

    WAGE_LABEL_INC = {
        '전직종':'전직종','관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가',
        '사무 종사자(3)':'사무종사자','서비스 종사자(4)':'서비스','판매 종사자(5)':'판매',
        '농림·어업 숙련 종사자(6)':'농림어업','기능원 및 관련기능종사자(7)':'기능원',
        '장치·기계 조작 및 조립종사자(8)':'기계조작','단순노무 종사자(9)':'단순노무',
    }
    WAGE_LABEL_EXC = {
        '전직종':'전직종','전문가 및 관련종사자(2)':'전문가','사무 종사자(3)':'사무종사자',
        '서비스 종사자(4)':'서비스','판매 종사자(5)':'판매',
        '농림·어업 숙련 종사자(6)':'농림어업','기능원 및 관련기능종사자(7)':'기능원',
        '장치·기계 조작 및 조립종사자(8)':'기계조작','단순노무 종사자(9)':'단순노무',
    }

    latest_yr = year_cols[-1]
    target = ['관리자','전문가','사무종사자','기능원','기계조작','단순노무']

    # 관리자 포함 기준
    inc = df_inc[df_inc['고용형태']=='전체근로자'].copy()
    inc['직종'] = inc['직종별'].map(WAGE_LABEL_INC).fillna(inc['직종별'])
    inc[latest_yr] = pd.to_numeric(inc[latest_yr], errors='coerce')
    wdf = inc[inc['직종'].isin(target)][['직종',latest_yr]].dropna()
    wdf.columns = ['직종','월임금']
    wdf['직군'] = wdf['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')

    w_avg = wdf[wdf['직군']=='화이트칼라']['월임금'].mean()
    b_avg = wdf[wdf['직군']=='블루칼라']['월임금'].mean()

    c1,c2,c3 = st.columns(3)
    c1.metric("🔵 화이트칼라 평균", f"{w_avg:,.0f}천원/월", f"{latest_yr}년")
    c2.metric("🔴 블루칼라 평균", f"{b_avg:,.0f}천원/월", f"{latest_yr}년")
    c3.metric("월 임금 격차", f"{w_avg-b_avg:,.0f}천원", "화이트 - 블루")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### 직종별 월평균 임금 (관리자 포함, {latest_yr}년)")
        fig = px.bar(wdf.sort_values('월임금',ascending=True),
                     x='월임금', y='직종', orientation='h', color='직군',
                     color_discrete_map={'화이트칼라':CW,'블루칼라':CB},
                     text='월임금')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=380,
                          xaxis_title='월임금 (천원)',
                          yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 연도별 직군 평균 임금 추이 — Line Chart")
        line_data = []
        for yr in year_cols:
            sub = inc[inc['직종'].isin(target)].copy()
            sub[yr] = pd.to_numeric(sub[yr], errors='coerce')
            sub['직군'] = sub['직종'].apply(lambda x:'화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
            for g in ['화이트칼라','블루칼라']:
                avg = sub[sub['직군']==g][yr].mean()
                line_data.append({'연도':yr,'직군':g,'평균임금':avg})
        ldf = pd.DataFrame(line_data).dropna()
        fig2 = px.line(ldf, x='연도', y='평균임금', color='직군',
                       color_discrete_map={'화이트칼라':CW,'블루칼라':CB},
                       markers=True, text='평균임금')
        fig2.update_traces(texttemplate='%{text:,.0f}', textposition='top center',
                           textfont=dict(color='#e6edf3',size=10))
        fig2.update_layout(**LAYOUT, height=380, yaxis_title='월평균 임금 (천원)')
        st.plotly_chart(fig2, use_container_width=True)

    insight(f"월 평균 격차 {w_avg-b_avg:,.0f}천원 — 단, 대기업 생산직은 중소기업 사무직보다 높을 수 있어 주의 필요")

    # 관리자 제외 비교
    st.markdown("---")
    st.markdown("#### 관리자 제외 시 임금 비교 (현실적 비교)")
    exc = df_exc[df_exc['고용형태']=='전체근로자'].copy()
    exc['직종'] = exc['직종별'].map(WAGE_LABEL_EXC).fillna(exc['직종별'])
    exc[latest_yr] = pd.to_numeric(exc[latest_yr], errors='coerce')
    target_exc = ['전문가','사무종사자','기능원','기계조작','단순노무']
    wdf2 = exc[exc['직종'].isin(target_exc)][['직종',latest_yr]].dropna()
    wdf2.columns = ['직종','월임금']
    wdf2['직군'] = wdf2['직종'].apply(lambda x:'화이트칼라' if x in ['전문가','사무종사자'] else '블루칼라')

    w_avg2 = wdf2[wdf2['직군']=='화이트칼라']['월임금'].mean()
    b_avg2 = wdf2[wdf2['직군']=='블루칼라']['월임금'].mean()

    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(wdf2.sort_values('월임금',ascending=True),
                      x='월임금', y='직종', orientation='h', color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB},
                      text='월임금')
        fig3.update_traces(texttemplate='%{text:,.0f}', textposition='outside',
                           textfont=dict(color='#e6edf3'))
        fig3.update_layout(**LAYOUT, height=320,
                           xaxis_title='월임금 (천원)',
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        avg_comp = pd.DataFrame({
            '직군': ['화이트칼라\n(관리자 제외)', '블루칼라'],
            '평균임금': [w_avg2, b_avg2]
        })
        fig4 = px.bar(avg_comp, x='직군', y='평균임금',
                      color='직군', color_discrete_map={
                          '화이트칼라\n(관리자 제외)': CW, '블루칼라': CB},
                      text='평균임금')
        fig4.update_traces(texttemplate='%{text:,.0f}천원', textposition='outside',
                           textfont=dict(color='#e6edf3'))
        fig4.update_layout(**LAYOUT, height=320,
                           yaxis_title='월평균 임금 (천원)', showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    insight(f"관리자 제외 시 화이트칼라 {w_avg2:,.0f}천원 vs 블루칼라 {b_avg2:,.0f}천원 — 격차 {w_avg2-b_avg2:,.0f}천원", 'yellow')

# ══════════════════════════════════════════════════════════════
# 페이지 5. 노동시장 수요 및 인력 수급
# ══════════════════════════════════════════════════════════════
elif page == "🏭  노동시장 수요 및 인력 수급":
    st.title("🏭 노동시장 수요 및 인력 수급")
    st.markdown("**기업은 어떤 직군을 필요로 하며, 실제로 부족한 직군은 무엇인가?**")
    st.markdown("---")

    national, val_cols = load_supply()
    periods = sorted(list(set([c.split('.')[0] for c in val_cols if c.count('/')==1])))
    latest_p = periods[-1]
    gu_col = latest_p
    mi_col = f"{latest_p}.1"
    bu_col = f"{latest_p}.2"

    sdf = national[national['직종별']!='전직종'].copy()
    for c in [gu_col, mi_col, bu_col]:
        sdf[c] = pd.to_numeric(sdf[c], errors='coerce')
    sdf = sdf.dropna(subset=[gu_col])
    sdf['직군'] = sdf['직종별'].apply(
        lambda x: '화이트칼라' if x in WHITE_SUPPLY else '블루칼라'
    )

    w_gu = sdf[sdf['직군']=='화이트칼라'][gu_col].sum()
    b_gu = sdf[sdf['직군']=='블루칼라'][gu_col].sum()
    w_mi = sdf[sdf['직군']=='화이트칼라'][mi_col].sum()
    b_mi = sdf[sdf['직군']=='블루칼라'][mi_col].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🔵 화이트칼라 구인", f"{w_gu:,.0f}명")
    c2.metric("🔴 블루칼라 구인", f"{b_gu:,.0f}명")
    c3.metric("🔵 화이트칼라 미충원", f"{w_mi:,.0f}명")
    c4.metric("🔴 블루칼라 미충원", f"{b_mi:,.0f}명")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 직종별 구인인원")
        fig = px.bar(sdf.sort_values(gu_col,ascending=True),
                     x=gu_col, y='직종별', orientation='h', color='직군',
                     color_discrete_map={'화이트칼라':CW,'블루칼라':CB},
                     text=gu_col)
        fig.update_traces(texttemplate='%{text:,.0f}명', textposition='outside',
                          textfont=dict(color='#e6edf3'))
        fig.update_layout(**LAYOUT, height=400, xaxis_title='구인인원 (명)', yaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 직종별 미충원인원")
        sdf_mi = sdf.dropna(subset=[mi_col]).sort_values(mi_col,ascending=True)
        fig2 = px.bar(sdf_mi, x=mi_col, y='직종별', orientation='h', color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB}, text=mi_col)
        fig2.update_traces(texttemplate='%{text:,.0f}명', textposition='outside',
                           textfont=dict(color='#e6edf3'))
        fig2.update_layout(**LAYOUT, height=400, xaxis_title='미충원인원 (명)', yaxis_title='')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 직종별 부족률 (%)")
    sdf_bu = sdf.dropna(subset=[bu_col]).sort_values(bu_col,ascending=False)
    fig3 = px.bar(sdf_bu, x='직종별', y=bu_col,
                  color=bu_col,
                  color_continuous_scale=[[0,'#21262d'],[0.5,'#e3b341'],[1,CB]],
                  text=bu_col)
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                       textfont=dict(color='#e6edf3'))
    fig3.update_layout(**LAYOUT, height=360, xaxis_title='', yaxis_title='부족률 (%)',
                       coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)
    insight("설치·정비·생산직 및 건설직은 높은 구인 수요와 미충원이 동시에 발생 — 블루칼라 인력 수급 불균형 심화", 'red')

# ══════════════════════════════════════════════════════════════
# 페이지 6. 결론 및 시사점
# ══════════════════════════════════════════════════════════════
elif page == "📋  결론 및 시사점":
    st.title("📋 결론 및 시사점")
    st.markdown("---")

    st.markdown("### 📌 핵심 발견사항")
    findings = [
        ("📊", "직군 분포", "#58a6ff",
         "화이트칼라는 전문가·사무직 중심으로 높은 비중을 차지하고 있으며, "
         "블루칼라도 제조업 및 생산직을 중심으로 상당한 규모를 유지하고 있다."),
        ("👥", "성별 특성", "#f778ba",
         "남성은 블루칼라 직군에 상대적으로 많이 종사하며, "
         "여성은 사무직 및 전문직 비중이 높게 나타난다."),
        ("🗺", "지역별 분포", "#3fb950",
         "서울·경기 등 수도권에서 화이트칼라 비중이 높고, "
         "제조업 중심 지역(울산·경남·충남)에서는 블루칼라 비중이 높게 나타난다."),
        ("💰", "임금 수준", "#e3b341",
         "전문가 직군과 관리자 직군에서 높은 임금 수준을 보이며 직군 간 임금 격차가 존재한다. "
         "단, 대기업 생산직의 경우 중소기업 사무직보다 높은 경우도 있다."),
        ("🏭", "노동시장 수요", "#f85149",
         "설치·정비·생산직과 영업·판매·운송직에서 높은 구인 수요를 보이며, "
         "특정 기술직에서 인력 부족 현상이 지속되고 있다."),
        ("⚠️", "인력 수급 불균형", "#bc8cff",
         "일부 생산직·설비직·기술직은 높은 부족률을 보여 "
         "노동시장 내 수요와 공급 간 불균형이 존재하는 것으로 확인된다."),
    ]
    for i in range(0, len(findings), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(findings):
                icon, title, color, desc = findings[i+j]
                with col:
                    card(f"{icon} {title}", desc, color)

    st.markdown("---")
    st.markdown("### 🔍 최종 결론")
    st.markdown("""
    <div style='background:linear-gradient(135deg,#161b22,#0d1117);
    border:1px solid #30363d;border-top:3px solid #58a6ff;
    border-radius:8px;padding:24px;'>
    <p style='color:#e6edf3;font-size:14px;line-height:1.9;margin:0;'>
    대한민국 노동시장은 직군별로 서로 다른 특성을 보이며 지역, 성별, 임금 수준에서 뚜렷한 차이가 나타난다.<br><br>
    또한 일부 기술직과 생산직에서는 높은 구인 수요와 부족률이 동시에 나타나
    노동시장 내 수요와 공급 간 불균형이 존재하는 것으로 확인된다.<br><br>
    본 분석을 통해 화이트칼라와 블루칼라의 실제 분포와 노동시장 구조를 객관적으로 파악할 수 있으며,
    직군별 인력 수급 특성을 이해하는 데 활용할 수 있다.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 시사점")
    suggestions = [
        "기술직 및 생산직 인력 양성 확대 필요",
        "지역 산업 구조를 고려한 인재 육성 필요",
        "노동시장 수요를 반영한 직업 교육 강화 필요",
        "직군별 인력 수급 불균형 완화를 위한 정책 검토 필요",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        with cols[i%2]:
            st.markdown(
                f'<div style="background:#161b22;border:1px solid #3fb950;'
                f'border-radius:8px;padding:14px 18px;margin:6px 0;">'
                f'<p style="color:#3fb950;margin:0;font-size:13px;">✅ {s}</p></div>',
                unsafe_allow_html=True
            )
