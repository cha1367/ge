import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="직업 편견 분석 대시보드", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1a1d27; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label { color: white !important; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

COLOR_WHITE = '#4f8ef7'
COLOR_BLUE  = '#e05c5c'
COLOR_OTHER = '#aaaaaa'

WHITE = ['1 관리자', '2 전문가 및 관련 종사자', '3 사무 종사자']
BLUE  = ['7 기능원 및 관련 기능종사자', '8 장치,기계조작 및 조립종사자', '9 단순노무 종사자']

LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
              font_color='white', margin=dict(t=40, b=20, l=20, r=20))

# ── 사이드바 ──────────────────────────────
with st.sidebar:
    st.markdown("## 📊 직업 편견 분석")
    st.markdown('*"공부 안 하면 용접이나 해?"*')
    st.markdown("---")
    page = st.radio("페이지 선택", [
        "🏠 프로젝트 소개",
        "📊 전국 현황",
        "⚧ 성별 분포",
        "💰 임금 비교",
        "🎓 학력 분포",
        "📝 결론"
    ])
    st.markdown("---")
    st.markdown("🔵 **화이트칼라** 관리자 / 전문가 / 사무종사자")
    st.markdown("🔴 **블루칼라** 기능원 / 기계조작 / 단순노무")
    st.markdown("---")
    st.caption("출처: 통계청, 고용노동부")

# ── 데이터 로드 ───────────────────────────
@st.cache_data
def load_yearly():
    df = pd.read_csv("data/직업별_취업자_연도별.csv", encoding='utf-8-sig')
    year_cols = [c for c in df.columns if c.isdigit() and len(c)==4]
    job_col = df.columns[0]
    return df, year_cols, job_col

@st.cache_data
def load_gender():
    df = pd.read_csv("data/성별_직업별.csv", encoding='utf-8-sig')
    df.columns = ['성별','산업별','직업별','취업자_1','RSE_1','취업자_2','RSE_2']
    df = df.iloc[1:].reset_index(drop=True)
    df['취업자_1'] = pd.to_numeric(df['취업자_1'], errors='coerce')
    return df

GENDER_WHITE = ['관리자', '전문가 및 관련 종사자', '사무 종사자']
GENDER_BLUE  = ['기능원 및 관련 기능 종사자', '장치​‧기계 조작 및 조립 종사자', '단순 노무 종사자']
GENDER_LABEL = {
    '관리자': '관리자',
    '전문가 및 관련 종사자': '전문가',
    '사무 종사자': '사무종사자',
    '기능원 및 관련 기능 종사자': '기능원',
    '장치​‧기계 조작 및 조립 종사자': '기계조작',
    '단순 노무 종사자': '단순노무'
}

@st.cache_data
def load_wage():
    df = pd.read_csv("data/직종별_임금.csv", encoding='utf-8-sig')
    items = df.iloc[0].tolist()
    df = df.iloc[1:].reset_index(drop=True)
    return df, items

@st.cache_data
def load_edu():
    df = pd.read_csv("data/직업별_학력별.csv", encoding='euc-kr')
    cols = ['직업별','취업자계','연령15~29','연령30~39','연령40~49','연령50~59','연령60이상','교육중졸이하','교육고졸','교육대졸이상']
    df.columns = cols
    df = df.iloc[1:].reset_index(drop=True)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# ── 공통 직종 라벨 ─────────────────────────
label_map6 = {
    '1 관리자': '관리자',
    '2 전문가 및 관련 종사자': '전문가',
    '3 사무 종사자': '사무종사자',
    '7 기능원 및 관련 기능종사자': '기능원',
    '8 장치,기계조작 및 조립종사자': '기계조작',
    '9 단순노무 종사자': '단순노무'
}

# ══════════════════════════════════════════
# 페이지 1: 소개
# ══════════════════════════════════════════
if page == "🏠 프로젝트 소개":
    st.title('"공부 안 하면 용접이나 해?"')
    st.subheader("데이터로 보는 대한민국 직업 편견의 실태")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 분석 배경")
        st.markdown("""
어릴 때 한 번쯤 들어봤을 말이 있습니다.

> *"공부 안 하면 용접이나 해"*
> *"환경미화원 될래?"*

이 말에는 블루칼라 직업을 낮게 보는
**암묵적인 직업 위계 의식**이 담겨 있습니다.

실제 국가 고용 통계 데이터를 활용해
이 편견이 현실과 얼마나 다른지 검증합니다.
        """)
    with col2:
        st.markdown("### 📋 분석 항목")
        st.markdown("""
| # | 분석 항목 | 핵심 질문 |
|---|---|---|
| 1 | 전국 직군별 비율 | 블루칼라가 정말 소수인가? |
| 2 | 성별 분포 | 성별 쏠림이 있나? |
| 3 | 임금 비교 | 실제 임금 차이는? |
| 4 | 학력 분포 | 학력과 직종의 관계는? |
        """)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🔵 화이트칼라**\n- 관리자\n- 전문가 및 관련 종사자\n- 사무 종사자")
    with col2:
        st.error("**🔴 블루칼라**\n- 기능원 및 관련 기능 종사자\n- 장치·기계조작 및 조립 종사자\n- 단순노무 종사자")

# ══════════════════════════════════════════
# 페이지 2: 전국 현황
# ══════════════════════════════════════════
elif page == "📊 전국 현황":
    st.title("📊 전국 화이트칼라 · 블루칼라 현황")
    st.markdown("---")

    df, year_cols, job_col = load_yearly()
    white_rows = df[df[job_col].isin(WHITE)]
    blue_rows  = df[df[job_col].isin(BLUE)]
    total_row  = df[df[job_col] == '계']
    latest = year_cols[-1]

    white_val = white_rows[latest].astype(float).sum()
    blue_val  = blue_rows[latest].astype(float).sum()
    total_val = float(total_row[latest].values[0])
    other_val = total_val - white_val - blue_val

    # KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 취업자", f"{total_val/10000:.1f}만명")
    c2.metric("🔵 화이트칼라", f"{white_val/total_val*100:.1f}%", f"{white_val:.0f}천명")
    c3.metric("🔴 블루칼라", f"{blue_val/total_val*100:.1f}%", f"{blue_val:.0f}천명")
    c4.metric("기준연도", f"{latest}년")

    st.markdown("---")

    # 파이 + 세로막대 (Column Chart)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"직군별 비율 ({latest}년)")
        pie = pd.DataFrame({
            '직군': ['화이트칼라', '블루칼라', '기타'],
            '취업자': [white_val, blue_val, other_val]
        })
        fig = px.pie(pie, values='취업자', names='직군', hole=0.45,
                     color='직군',
                     color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE, '기타': COLOR_OTHER})
        fig.update_layout(**LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"💡 블루칼라 {blue_val/total_val*100:.1f}% — 생각보다 훨씬 많습니다")

    with col2:
        st.subheader("직종별 취업자 수 (Column Chart)")
        bar_data = df[df[job_col].isin(WHITE+BLUE)][[job_col, latest]].copy()
        bar_data.columns = ['직종', '취업자']
        bar_data['취업자'] = bar_data['취업자'].astype(float)
        bar_data['직군'] = bar_data['직종'].apply(lambda x: '화이트칼라' if x in WHITE else '블루칼라')
        bar_data['직종'] = bar_data['직종'].map(label_map6)
        fig2 = px.bar(bar_data, x='직종', y='취업자', color='직군',
                      color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                      text='취업자', barmode='group')
        fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig2.update_layout(**LAYOUT, height=360, xaxis_title='직종', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Area Chart (꺾은선 + 면적)
    st.subheader("연도별 취업자 추이 (Area Chart)")
    trend = []
    for y in year_cols:
        trend.append({
            '연도': y,
            '화이트칼라': white_rows[y].astype(float).sum(),
            '블루칼라': blue_rows[y].astype(float).sum()
        })
    tdf = pd.DataFrame(trend)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라',
        line=dict(color=COLOR_WHITE, width=3), mode='lines+markers',
        fill='tozeroy', fillcolor='rgba(79,142,247,0.2)'
    ))
    fig3.add_trace(go.Scatter(
        x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라',
        line=dict(color=COLOR_BLUE, width=3), mode='lines+markers',
        fill='tozeroy', fillcolor='rgba(224,92,92,0.2)'
    ))
    fig3.update_layout(**LAYOUT, height=350,
                       xaxis_title='연도', yaxis_title='취업자 수 (천명)')
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("💡 10년간 화이트칼라 꾸준히 증가, 블루칼라는 완만하게 감소")

# ══════════════════════════════════════════
# 페이지 3: 성별 분포
# ══════════════════════════════════════════
elif page == "⚧ 성별 분포":
    st.title("⚧ 성별 직종 분포")
    st.markdown("---")

    df = load_gender()
    all_target = GENDER_WHITE + GENDER_BLUE
    gdf = df[(df['산업별']=='계') & (df['직업별'].isin(all_target))][['성별','직업별','취업자_1']].copy()
    gdf['직업별'] = gdf['직업별'].map(GENDER_LABEL)
    gdf['직군'] = gdf['직업별'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')

    # 서브플롯 (남/여 나란히)
    st.subheader("남성 vs 여성 직종별 취업자 (서브플롯)")
    col1, col2 = st.columns(2)
    with col1:
        male = gdf[gdf['성별']=='남자'].sort_values('취업자_1')
        fig = px.bar(male, x='직업별', y='취업자_1', color='직군',
                     color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                     title='남성', text='취업자_1')
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig.update_layout(**LAYOUT, height=380, xaxis_title='', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        female = gdf[gdf['성별']=='여자'].sort_values('취업자_1')
        fig2 = px.bar(female, x='직업별', y='취업자_1', color='직군',
                      color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                      title='여성', text='취업자_1')
        fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig2.update_layout(**LAYOUT, height=380, xaxis_title='', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # 도넛차트 (남/여 직군 비율)
    st.subheader("성별 직군 비율 비교 (도넛 차트)")
    col1, col2 = st.columns(2)
    for gender, col in [('남자', col1), ('여자', col2)]:
        sub = gdf[gdf['성별']==gender]
        w = sub[sub['직군']=='화이트칼라']['취업자_1'].sum()
        b = sub[sub['직군']=='블루칼라']['취업자_1'].sum()
        donut = pd.DataFrame({'직군': ['화이트칼라', '블루칼라'], '취업자': [w, b]})
        fig = px.pie(donut, values='취업자', names='직군', hole=0.5,
                     title=f'{"남성" if gender=="남자" else "여성"} 직군 비율',
                     color='직군',
                     color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE})
        fig.update_layout(**LAYOUT, height=320)
        with col:
            st.plotly_chart(fig, use_container_width=True)

    st.caption("💡 남성은 블루칼라, 여성은 화이트칼라에 상대적으로 집중")

# ══════════════════════════════════════════
# 페이지 4: 임금 비교
# ══════════════════════════════════════════
elif page == "💰 임금 비교":
    st.title("💰 직종별 평균 임금 비교")
    st.markdown("---")

    df, items = load_wage()
    total_df = df[df.iloc[:,0]=='전체근로자'].copy()
    wage_col = total_df.columns[74] if len(total_df.columns) > 74 else total_df.columns[-7]

    wage_data = total_df[[total_df.columns[1], wage_col]].copy()
    wage_data.columns = ['직종', '월임금(천원)']
    wage_data['월임금(천원)'] = pd.to_numeric(wage_data['월임금(천원)'], errors='coerce')
    wage_data = wage_data.dropna()

    wlabel = {
        '전직종': '전직종',
        '관리자(1)': '관리자',
        '전문가 및 관련종사자(2)': '전문가',
        '사무 종사자(3)': '사무종사자',
        '서비스 종사자(4)': '서비스',
        '판매 종사자(5)': '판매',
        '농림어업 숙련종사자(6)': '농림어업',
        '기능원 및 관련기능종사자(7)': '기능원',
        '장치·기계 조작 및 조립종사자(8)': '기계조작',
        '단순노무 종사자(9)': '단순노무',
    }
    wage_data['직종'] = wage_data['직종'].map(wlabel).fillna(wage_data['직종'])
    target = ['관리자','전문가','사무종사자','기능원','기계조작','단순노무']
    wdf = wage_data[wage_data['직종'].isin(target)].copy()
    wdf['직군'] = wdf['직종'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
    wdf = wdf.sort_values('월임금(천원)')

    w_avg = wdf[wdf['직군']=='화이트칼라']['월임금(천원)'].mean()
    b_avg = wdf[wdf['직군']=='블루칼라']['월임금(천원)'].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("🔵 화이트칼라 평균", f"{w_avg:,.0f}천원")
    c2.metric("🔴 블루칼라 평균", f"{b_avg:,.0f}천원")
    c3.metric("임금 격차", f"{w_avg-b_avg:,.0f}천원", "화이트 - 블루")

    st.markdown("---")

    # 가로 막대 (Bar Chart)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("직종별 월평균 임금 (Bar Chart)")
        fig = px.bar(wdf, x='월임금(천원)', y='직종', orientation='h', color='직군',
                     color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                     text='월임금(천원)')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(**LAYOUT, height=380,
                          xaxis_title='월임금 (천원)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Combo Chart (막대 + 평균선)
        st.subheader("임금 비교 + 평균선 (Combo Chart)")
        fig2 = go.Figure()
        colors = [COLOR_WHITE if x in ['관리자','전문가','사무종사자'] else COLOR_BLUE
                  for x in wdf['직종']]
        fig2.add_trace(go.Bar(
            x=wdf['직종'], y=wdf['월임금(천원)'],
            marker_color=colors, name='월임금',
            text=wdf['월임금(천원)'],
            texttemplate='%{text:,.0f}', textposition='outside'
        ))
        fig2.add_trace(go.Scatter(
            x=wdf['직종'], y=[w_avg]*3 + [b_avg]*3,
            mode='lines', name='직군 평균',
            line=dict(color='yellow', width=2, dash='dash')
        ))
        fig2.update_layout(**LAYOUT, height=380,
                           xaxis_title='직종', yaxis_title='월임금 (천원)')
        st.plotly_chart(fig2, use_container_width=True)

    st.caption(f"💡 화이트칼라 평균 {w_avg:,.0f}천원 vs 블루칼라 평균 {b_avg:,.0f}천원 — 격차 {w_avg-b_avg:,.0f}천원")

# ══════════════════════════════════════════
# 페이지 5: 학력 분포
# ══════════════════════════════════════════
elif page == "🎓 학력 분포":
    st.title("🎓 직종별 학력 분포")
    st.subheader('"공부 안 하면 블루칼라?" — 데이터로 확인')
    st.markdown("---")

    df = load_edu()
    elabel = {
        '관리자': '관리자',
        '전문가 및 관련 종사자': '전문가',
        '사무 종사자': '사무종사자',
        '기능원 및 관련 기능종사자': '기능원',
        '장치·기계 조작 및 조립 종사자': '기계조작',
        '단순노무 종사자': '단순노무',
    }
    edf = df[df['직업별'].isin(elabel.keys())].copy()
    edf['직업별'] = edf['직업별'].map(elabel)
    edf['직군'] = edf['직업별'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
    edf['고졸비율'] = edf['교육고졸'] / edf['취업자계'] * 100
    edf['대졸비율'] = edf['교육대졸이상'] / edf['취업자계'] * 100
    edf['중졸이하비율'] = edf['교육중졸이하'] / edf['취업자계'] * 100

    # 누적 막대 (학력 구성)
    st.subheader("직종별 학력 구성 비율 (누적 Bar Chart)")
    melt = pd.melt(edf[['직업별','직군','고졸비율','대졸비율','중졸이하비율']],
                   id_vars=['직업별','직군'], var_name='학력', value_name='비율')
    melt['학력'] = melt['학력'].map({'고졸비율':'고졸','대졸비율':'대졸이상','중졸이하비율':'중졸이하'})
    fig = px.bar(melt, x='직업별', y='비율', color='학력', barmode='stack',
                 color_discrete_map={'고졸':'#f7c948','대졸이상': COLOR_WHITE,'중졸이하': COLOR_BLUE},
                 text='비율')
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
    fig.update_layout(**LAYOUT, height=380, xaxis_title='직종', yaxis_title='비율 (%)')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 대졸 vs 고졸 비율 비교
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("대졸 이상 비율 (%)")
        fig2 = px.bar(edf.sort_values('대졸비율'), x='직업별', y='대졸비율', color='직군',
                      color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                      text='대졸비율')
        fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig2.update_layout(**LAYOUT, height=350, xaxis_title='', yaxis_title='비율 (%)')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("고졸 비율 (%)")
        fig3 = px.bar(edf.sort_values('고졸비율'), x='직업별', y='고졸비율', color='직군',
                      color_discrete_map={'화이트칼라': COLOR_WHITE, '블루칼라': COLOR_BLUE},
                      text='고졸비율')
        fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig3.update_layout(**LAYOUT, height=350, xaxis_title='', yaxis_title='비율 (%)')
        st.plotly_chart(fig3, use_container_width=True)

    st.caption("💡 블루칼라도 고졸 이상 비율이 높습니다 — '공부 안 하면 블루칼라'는 편견입니다")

# ══════════════════════════════════════════
# 페이지 6: 결론
# ══════════════════════════════════════════
elif page == "📝 결론":
    st.title("📝 결론 — 직업윤리의 관점에서")
    st.markdown("---")
    st.markdown("## ❌ '공부 안 하면 용접이나 해?' — 이 말은 틀렸습니다.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**편견의 시작**\n\n어릴 때부터 주입된 직업 위계 의식. 블루칼라를 기피 직종으로 만드는 사회적 인식이 존재합니다.")
    with col2:
        st.warning("**데이터가 말하는 현실**\n\n블루칼라는 전체 취업자의 30% 이상. 대한민국 경제를 실질적으로 움직이는 핵심 노동력입니다.")
    with col3:
        st.info("**직업윤리의 방향**\n\n직업에 귀천이 없다는 원칙은 선언이 아닌 처우로 증명되어야 합니다.")

    st.markdown("---")

    # KPI
    df, year_cols, job_col = load_yearly()
    latest = year_cols[-1]
    white_rows = df[df[job_col].isin(WHITE)]
    blue_rows  = df[df[job_col].isin(BLUE)]
    total_val  = float(df[df[job_col]=='계'][latest].values[0])
    white_val  = white_rows[latest].astype(float).sum()
    blue_val   = blue_rows[latest].astype(float).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("블루칼라 비율", f"{blue_val/total_val*100:.1f}%")
    c2.metric("화이트칼라 비율", f"{white_val/total_val*100:.1f}%")
    c3.metric("블루칼라 취업자", f"{blue_val:.0f}천명")

    st.markdown("---")

    # Area Chart 요약
    st.subheader("10년간 취업자 추이 요약 (Area Chart)")
    trend = [{'연도': y,
               '화이트칼라': white_rows[y].astype(float).sum(),
               '블루칼라': blue_rows[y].astype(float).sum()} for y in year_cols]
    tdf = pd.DataFrame(trend)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라',
                             line=dict(color=COLOR_WHITE, width=3), mode='lines+markers',
                             fill='tozeroy', fillcolor='rgba(79,142,247,0.2)'))
    fig.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라',
                             line=dict(color=COLOR_BLUE, width=3), mode='lines+markers',
                             fill='tozeroy', fillcolor='rgba(224,92,92,0.2)'))
    fig.update_layout(**LAYOUT, height=300, xaxis_title='연도', yaxis_title='취업자 수 (천명)')
    st.plotly_chart(fig, use_container_width=True)

    st.success("**최종 메시지**\n\n블루칼라 노동자는 낮은 학력·낮은 능력의 사람이 아닙니다. 데이터는 이들이 대한민국 노동시장의 30%를 차지하는 핵심 인력임을 보여줍니다. 편견이 바뀌어야 처우도 바뀝니다.")
