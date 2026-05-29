import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="화이트칼라 · 블루칼라 분석", page_icon="📊", layout="wide")

# 기본 스타일 (간단한 다크 테마)
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #c9d1d9; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="metric-container"] {
    background:#0f1720; border:1px solid #30363d; border-radius:12px; padding:12px;
}
.insight-box { background:#0f1720; border-left:4px solid #58a6ff; border-radius:0 8px 8px 0; padding:12px 16px; margin:8px 0; color:#9aa5b1; font-size:14px; }
.insight-red { border-left-color:#f85149; }
.insight-green { border-left-color:#3fb950; }
h1 { color:#58a6ff !important; }
h2,h3 { color:#e6edf3 !important; }
hr { border-color:#30363d !important; }
</style>
""", unsafe_allow_html=True)

# 색상/레이아웃
CW, CB, CO = '#58a6ff', '#f85149', '#6e7681'
LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#9aa5b1', family='sans-serif'),
    margin=dict(t=40,b=30,l=20,r=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3')),
    xaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#9aa5b1'),
    yaxis=dict(gridcolor='#21262d', zerolinecolor='#21262d', color='#9aa5b1'),
)

def insight(text, color='blue'):
    cls = 'insight-box' + (' insight-red' if color=='red' else ' insight-green' if color=='green' else '')
    st.markdown(f'<div class="{cls}">💡 {text}</div>', unsafe_allow_html=True)

# 데이터 로드 함수 (CSV 파일명은 data/ 폴더에 있다고 가정)
@st.cache_data
def load_yearly():
    df = pd.read_csv("data/직업별_취업자_연도별.csv", encoding='utf-8-sig')
    return df

@st.cache_data
def load_region():
    df = pd.read_csv("data/시도별_직업별.csv", encoding='utf-8-sig')
    return df

@st.cache_data
def load_gender():
    df = pd.read_csv("data/성별_직업별.csv", encoding='utf-8-sig')
    return df

@st.cache_data
def load_age():
    df = pd.read_csv("data/직업별_학력별.csv", encoding='utf-8-sig')
    return df

@st.cache_data
def load_wage(include_manager=True):
    fname = "data/관리자 포함.csv" if include_manager else "data/관리자 미 포함.csv"
    df = pd.read_csv(fname, encoding='utf-8-sig')
    return df

# 사이드바 메뉴
with st.sidebar:
    st.markdown("## 📊 직종 분포 분석")
    page = st.radio("", [
        "🏠 소개",
        "📊 전국 현황",
        "🗺 지역별",
        "👥 성별",
        "🎂 연령별",
        "💰 임금",
        "📝 결론"
    ])
    st.markdown("---")
    st.markdown("🔵 **화이트칼라**: 관리자 · 전문가 · 사무")
    st.markdown("🔴 **블루칼라**: 기능원 · 기계조작 · 단순노무")
    st.caption("데이터 출처: 통계청 KOSIS · 고용노동부 (예시)")

# -------------------------
# 1. 소개
# -------------------------
if page == "🏠 소개":
    st.title("대한민국 화이트칼라 · 블루칼라 분포 분석")
    st.markdown("#### 졸업 후 우리가 진출할 노동시장의 구조를 데이터로 확인합니다.")
    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("**분석 목적**")
        st.write("- 화이트칼라·블루칼라 직종 분포 파악")
        st.write("- 지역·성별·연령별 구조 비교")
        st.write("- 직종별 임금 차이 분석 (관리자 포함/제외)")
    with col2:
        st.markdown("**데이터 파일**")
        st.write("- 관리자 포함.csv")
        st.write("- 관리자 미 포함.csv")
        st.write("- 성별_직업별.csv")
        st.write("- 시도별_직업별.csv")
        st.write("- 직업별_취업자_연도별.csv")
        st.write("- 직업별_학력별.csv")
    st.markdown("---")
    insight("앱을 실행하기 전에 data/ 폴더에 위 CSV 파일들이 있는지 확인하세요.", 'green')

# -------------------------
# 2. 전국 현황
# -------------------------
elif page == "📊 전국 현황":
    st.title("📊 전국 화이트칼라 · 블루칼라 현황")
    df = load_yearly()

    # 연도 컬럼 자동 탐색 (숫자 4자리)
    year_cols = [c for c in df.columns if str(c).isdigit() and len(str(c)) == 4]
    if not year_cols:
        # fallback: 숫자 포함 컬럼
        year_cols = [c for c in df.columns if any(ch.isdigit() for ch in str(c))]
    if not year_cols:
        st.error("연도 컬럼을 찾지 못했습니다. CSV 헤더를 확인해주세요.")
    else:
        latest = year_cols[-1]
        # 직업별 컬럼명 가정: '직업별' 또는 첫 컬럼
        job_col = df.columns[0]

        # 화이트/블루 정의 (문자열 포함 검사)
        white_mask = df[job_col].str.contains('관리자|전문가|사무', na=False)
        blue_mask = df[job_col].str.contains('기능원|기계조작|단순', na=False)
        total_row = df[df[job_col].str.contains('계', na=False)]
        try:
            total = float(total_row[latest].values[0])
        except Exception:
            total = df[latest].astype(float).sum()

        white = df[white_mask][latest].astype(float).sum()
        blue = df[blue_mask][latest].astype(float).sum()
        other = max(total - white - blue, 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("전체 취업자", f"{total/10000:.1f}만명", f"{latest}년")
        c2.metric("화이트칼라 비율", f"{white/total*100:.1f}%")
        c3.metric("블루칼라 비율", f"{blue/total*100:.1f}%")
        c4.metric("기타", f"{other:.0f}명")

        st.markdown("---")
        col1, col2 = st.columns([1,1.6])
        with col1:
            st.markdown("#### 직군별 비율 (도넛)")
            pie = pd.DataFrame({'직군':['화이트칼라','블루칼라','기타'], '취업자':[white,blue,other]})
            fig = px.pie(pie, values='취업자', names='직군', hole=0.55,
                         color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO})
            fig.update_traces(textposition='outside', textinfo='percent+label', textfont=dict(color='#e6edf3'))
            fig.update_layout(**LAYOUT, height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            insight("전국적으로 화이트칼라 비중이 높은 직군과 블루칼라 비중이 높은 직군이 공존합니다.")
        with col2:
            st.markdown("#### 연도별 취업자 추이 (화이트 vs 블루)")
            # 연도별 합계 계산
            trend = []
            for y in year_cols:
                try:
                    w = df[white_mask][y].astype(float).sum()
                    b = df[blue_mask][y].astype(float).sum()
                except Exception:
                    w = 0; b = 0
                trend.append({'연도':str(y),'화이트칼라':w,'블루칼라':b})
            tdf = pd.DataFrame(trend)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라',
                                      line=dict(color=CW, width=3), fill='tozeroy'))
            fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라',
                                      line=dict(color=CB, width=3), fill='tozeroy'))
            fig2.update_layout(**LAYOUT, height=380, xaxis_title='연도', yaxis_title='취업자 수 (천명)')
            st.plotly_chart(fig2, use_container_width=True)
            insight("최근 몇 년간 화이트칼라의 상대적 증가가 관찰됩니다.", 'green')

# -------------------------
# 3. 지역별
# -------------------------
elif page == "🗺 지역별":
    st.title("🗺 시도별 화이트칼라 · 블루칼라 분포")
    df = load_region()
    # 컬럼명 정리: 행정구역, 직업별, 연도별 값들
    cols_2024 = [c for c in df.columns if '2024' in str(c)]
    if not cols_2024:
        # fallback: 숫자 포함 컬럼
        cols_2024 = [c for c in df.columns if any(ch.isdigit() for ch in str(c))]
    latest_col = cols_2024[0] if cols_2024 else df.columns[-1]

    # 행정구역 컬럼 찾기
    possible_region_cols = [c for c in df.columns if '행정' in str(c) or '시도' in str(c) or '행정구역' in str(c)]
    region_col = possible_region_cols[0] if possible_region_cols else df.columns[0]
    job_col = [c for c in df.columns if '직업' in str(c)][0] if any('직업' in str(c) for c in df.columns) else df.columns[1]

    regions = df[region_col].unique()
    result = []
    for reg in regions:
        sub = df[df[region_col] == reg]
        if sub.empty: continue
        # 총계 행 찾기
        total_row = sub[sub[job_col].str.contains('계', na=False)]
        try:
            total = float(total_row[latest_col].values[0])
        except Exception:
            total = sub[latest_col].astype(float).sum()
        white = sub[sub[job_col].str.contains('관리자|전문가|사무', na=False)][latest_col].astype(float).sum()
        blue = sub[sub[job_col].str.contains('기능원|기계조작|단순', na=False)][latest_col].astype(float).sum()
        result.append({'지역':reg, '화이트':white, '블루':blue, '총':total})
    rdf = pd.DataFrame(result).dropna()

    st.markdown("#### 시도별 블루칼라 규모 (트리맵)")
    fig = px.treemap(rdf, path=['지역'], values='블루', color='블루',
                     color_continuous_scale=[[0,'#21262d'],[0.5,'#f85149'],[1,'#ff6b6b']])
    fig.update_layout(**LAYOUT, height=420)
    st.plotly_chart(fig, use_container_width=True)
    insight("제조업 중심 지역에서 블루칼라 비중이 높게 나타납니다.", 'red')

    st.markdown("---")
    st.markdown("#### 시도별 화이트 vs 블루 비율 (로리팝 스타일)")
    rdf['화이트비율'] = rdf['화이트'] / rdf['총'] * 100
    rdf['블루비율'] = rdf['블루'] / rdf['총'] * 100
    rdf_s = rdf.sort_values('블루비율', ascending=True)

    fig2 = go.Figure()
    for _, row in rdf_s.iterrows():
        fig2.add_trace(go.Scatter(x=[row['화이트비율'], row['블루비율']],
                                  y=[row['지역'], row['지역']],
                                  mode='lines', line=dict(color='#30363d', width=2), showlegend=False))
    fig2.add_trace(go.Scatter(x=rdf_s['화이트비율'], y=rdf_s['지역'], mode='markers', name='화이트칼라',
                              marker=dict(color=CW, size=12, line=dict(color='white', width=1))))
    fig2.add_trace(go.Scatter(x=rdf_s['블루비율'], y=rdf_s['지역'], mode='markers', name='블루칼라',
                              marker=dict(color=CB, size=12, line=dict(color='white', width=1))))
    fig2.update_layout(**LAYOUT, height=520, xaxis_title='비율 (%)', yaxis_title='')
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# 4. 성별
# -------------------------
elif page == "👥 성별":
    st.title("👥 성별 직종 분포")
    df = load_gender()
    # 연도 컬럼 자동 탐색
    year_cols = [c for c in df.columns if str(c).isdigit() and len(str(c))==4]
    if not year_cols:
        year_cols = [c for c in df.columns if any(ch.isdigit() for ch in str(c))]
    latest = year_cols[-1] if year_cols else df.columns[-1]

    # 남/여 도넛
    def calc_gender_counts(g):
        sub = df[df['성별'] == g]
        w = sub[sub['직업별'].str.contains('관리자|전문가|사무', na=False)][latest].astype(float).sum()
        b = sub[sub['직업별'].str.contains('기능원|기계조작|단순', na=False)][latest].astype(float).sum()
        return w, b

    wm, bm = calc_gender_counts('남자')
    wf, bf = calc_gender_counts('여자')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 남성 직군 비율")
        pie_m = pd.DataFrame({'직군':['화이트칼라','블루칼라'], '취업자':[wm, bm]})
        figm = px.pie(pie_m, values='취업자', names='직군', hole=0.55, color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB})
        figm.update_layout(**LAYOUT, height=340, showlegend=False)
        st.plotly_chart(figm, use_container_width=True)
    with col2:
        st.markdown("#### 여성 직군 비율")
        pie_f = pd.DataFrame({'직군':['화이트칼라','블루칼라'], '취업자':[wf, bf]})
        figf = px.pie(pie_f, values='취업자', names='직군', hole=0.55, color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB})
        figf.update_layout(**LAYOUT, height=340, showlegend=False)
        st.plotly_chart(figf, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 직종별 남/여 구성 (스택형 막대)")
    # 직종 라벨 매핑 (간단)
    LABEL_G = {
        '1 관리자':'관리자','2 전문가 및 관련 종사자':'전문가','3 사무 종사자':'사무종사자',
        '7 기능원 및 관련 기능종사자':'기능원','8 장치,기계조작 및 조립종사자':'기계조작','9 단순노무 종사자':'단순노무'
    }
    stack_list = []
    for gender in ['남자','여자']:
        sub = df[(df['성별']==gender) & (df['직업별'].isin(LABEL_G.keys()))][['직업별', latest]].copy()
        sub[latest] = pd.to_numeric(sub[latest], errors='coerce')
        sub['직업별'] = sub['직업별'].map(LABEL_G)
        sub['성별'] = '남성' if gender=='남자' else '여성'
        stack_list.append(sub)
    if stack_list:
        sdf = pd.concat(stack_list)
        sdf.columns = ['직종','취업자','성별']
        fig = px.bar(sdf, x='직종', y='취업자', color='성별', barmode='stack',
                     color_discrete_map={'남성':CW,'여성':'#f778ba'})
        fig.update_layout(**LAYOUT, height=380, xaxis_title='', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig, use_container_width=True)
        insight("남성은 블루칼라 비중이 높고, 여성은 화이트칼라 비중이 상대적으로 높습니다.", 'red')

# -------------------------
# 5. 연령별
# -------------------------
elif page == "🎂 연령별":
    st.title("🎂 연령별 직종 분포")
    df = load_age()
    # 연령 관련 컬럼 탐색 (예: 2024.1/2 같은 표기)
    age_cols = [c for c in df.columns if '2024' in str(c) or '연령' in str(c) or '세' in str(c)]
    if not age_cols:
        # fallback: 숫자 포함 컬럼 (사용자 데이터에 따라 조정 필요)
        age_cols = [c for c in df.columns if any(ch.isdigit() for ch in str(c))]
    # 직업 필터
    df_sub = df[df['직업별'].str.contains('관리자|전문가|사무|기능원|기계조작|단순', na=False)].copy()
    if age_cols:
        melt = df_sub.melt(id_vars=['직업별'], value_vars=age_cols, var_name='연령대', value_name='취업자')
        melt['취업자'] = pd.to_numeric(melt['취업자'], errors='coerce')
        fig = px.bar(melt, x='직업별', y='취업자', color='연령대', barmode='stack')
        fig.update_layout(**LAYOUT, height=420, xaxis_title='', yaxis_title='취업자 수 (천명)')
        st.plotly_chart(fig, use_container_width=True)
        insight("연령대별로 직종 선호가 다르게 나타납니다. (예: 고령층 블루칼라 비중 증가)", 'green')
    else:
        st.warning("연령대 컬럼을 찾지 못했습니다. CSV 구조를 확인해주세요.")

# -------------------------
# 6. 임금
# -------------------------
elif page == "💰 임금":
    st.title("💰 직종별 평균 임금 비교")
    # 두 파일(관리자 포함 / 미포함) 불러오기
    df_mgr = load_wage(include_manager=True)
    df_nomgr = load_wage(include_manager=False)

    # 최신 연도 컬럼 자동 탐색 (예: '2025 월임금총액 (천원)' 또는 '2025')
    def find_wage_col(df):
        # 우선적으로 '월임금' 텍스트 포함 컬럼 찾기
        candidates = [c for c in df.columns if '월임금' in str(c)]
        if candidates:
            return candidates[-1]
        # 다음으로 4자리 연도 포함 컬럼
        for c in df.columns[::-1]:
            import re
            m = re.search(r'(\d{4})', str(c))
            if m:
                return c
        # fallback: 마지막 수치형 컬럼
        num_cols = [c for c in df.columns if df[c].dtype != object]
        return num_cols[-1] if num_cols else df.columns[-1]

    latest_col = find_wage_col(df_mgr)

    WLABEL = {
        '전직종':'전직종','관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가',
        '사무 종사자(3)':'사무종사자','서비스 종사자(4)':'서비스',
        '판매 종사자(5)':'판매','농림·어업 숙련 종사자(6)':'농림어업',
        '기능원 및 관련 기능 종사자(7)':'기능원','장치·기계 조작 및 조립 종사자(8)':'기계조작',
        '단순노무 종사자(9)':'단순노무'
    }

    def process_wage(df, wage_col):
        # 첫 컬럼을 직종명으로 가정
        job_col = df.columns[0]
        tmp = df[[job_col, wage_col]].copy()
        tmp.columns = ['직종', '월임금']
        tmp['월임금'] = tmp['월임금'].astype(str).str.replace(',', '').str.replace(' ', '')
        tmp['월임금'] = pd.to_numeric(tmp['월임금'], errors='coerce')
        tmp['직종'] = tmp['직종'].map(WLABEL).fillna(tmp['직종'])
        tmp['직군'] = tmp['직종'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
        return tmp.dropna(subset=['월임금'])

    w_mgr = process_wage(df_mgr, latest_col)
    w_nomgr = process_wage(df_nomgr, latest_col)

    # 요약 통계
    white_all = w_mgr[w_mgr['직군']=='화이트칼라']['월임금'].mean()
    white_no_mgr = w_nomgr[w_nomgr['직군']=='화이트칼라']['월임금'].mean()
    blue_avg = w_mgr[w_mgr['직군']=='블루칼라']['월임금'].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("화이트칼라 평균(관리자 포함)", f"{white_all:,.0f}천원/월")
    c2.metric("화이트칼라 평균(관리자 제외)", f"{white_no_mgr:,.0f}천원/월")
    c3.metric("블루칼라 평균", f"{blue_avg:,.0f}천원/월")
    c4.metric("임금 격차(관리자 제외)", f"{(white_no_mgr - blue_avg):,.0f}천원")

    st.markdown("---")
    # 왼쪽: 연도별(파일에 여러 연도 있을 경우) 추이 — 여기서는 단일 연도만 가정
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("#### 직종별 평균 임금 (관리자 포함)")
        order = w_mgr.groupby('직종')['월임금'].median().sort_values(ascending=False).index.tolist()
        fig = px.bar(w_mgr.sort_values('월임금', ascending=False), x='직종', y='월임금', color='직군',
                     category_orders={'직종': order},
                     color_discrete_map={'화이트칼라':CW,'블루칼라':CB}, text='월임금')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(**LAYOUT, height=420, xaxis_title='', yaxis_title='월임금 (천원)')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### 직종별 임금 분포 (박스플롯, 최근 연도)")
        fig2 = px.box(w_mgr, x='월임금', y='직종', color='직군',
                      color_discrete_map={'화이트칼라':CW,'블루칼라':CB}, points='outliers', orientation='h')
        shapes = []
        if not np.isnan(white_all):
            shapes.append(dict(type='line', x0=white_all, x1=white_all, y0=-0.5, y1=len(w_mgr['직종'].unique())-0.5,
                               line=dict(color=CW, dash='dash', width=1.5)))
        if not np.isnan(blue_avg):
            shapes.append(dict(type='line', x0=blue_avg, x1=blue_avg, y0=-0.5, y1=len(w_mgr['직종'].unique())-0.5,
                               line=dict(color=CB, dash='dash', width=1.5)))
        fig2.update_layout(**LAYOUT, height=420, shapes=shapes, xaxis_title='월임금 (천원)')
        st.plotly_chart(fig2, use_container_width=True)

    insight("관리자 직종은 평균을 크게 끌어올립니다. 관리자 제외 평균을 함께 제시하면 현실적 비교가 가능합니다.", 'green')

# -------------------------
# 7. 결론
# -------------------------
elif page == "📝 결론":
    st.title("📝 결론 및 시사점")
    st.markdown("#### 요약")
    # 간단한 요약 카드 (데이터가 로드 가능한 경우에만 수치 표시)
    try:
        df_yearly = load_yearly()
        year_cols = [c for c in df_yearly.columns if str(c).isdigit() and len(str(c))==4]
        latest = year_cols[-1] if year_cols else df_yearly.columns[-1]
        total = df_yearly[df_yearly[df_yearly.columns[0]].str.contains('계', na=False)][latest].astype(float).values[0]
        st.metric("전체 취업자 (최근)", f"{total/10000:.1f}만명")
    except Exception:
        st.write("- 데이터가 완전히 로드되지 않았습니다. 일부 수치가 비어있을 수 있습니다.")

    st.markdown("---")
    st.markdown("#### 핵심 인사이트")
    st.write("- 화이트칼라 비중이 꾸준히 증가하는 추세가 관찰됩니다.")
    st.write("- 지역별로 산업구조 차이가 뚜렷하여 정책·교육·직업훈련의 지역 맞춤화가 필요합니다.")
    st.write("- 임금은 관리자 직종이 평균을 끌어올리므로 관리자 제외 평균을 함께 제시해야 현실적 비교가 가능합니다.")

    st.markdown("---")
    st.markdown("#### 시각적 비교 (관리자 제외 평균 vs 블루칼라 평균)")
    # 간단한 슬로프 그래프: 관리자 제외 화이트 평균 vs 블루 평균
    try:
        df_mgr = load_wage(True)
        df_nomgr = load_wage(False)
        latest_col = [c for c in df_mgr.columns if any(ch.isdigit() for ch in str(c))][-1]
        w_mgr = df_mgr[[df_mgr.columns[0], latest_col]].copy()
        w_mgr.columns = ['직종','월임금']
        w_mgr['월임금'] = pd.to_numeric(w_mgr['월임금'].astype(str).str.replace(',',''), errors='coerce')
        w_mgr['직종'] = w_mgr['직종'].map({
            '관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가','사무 종사자(3)':'사무종사자',
            '기능원 및 관련 기능 종사자(7)':'기능원','장치·기계 조작 및 조립 종사자(8)':'기계조작','단순노무 종사자(9)':'단순노무'
        }).fillna(w_mgr['직종'])
        # 화이트(관리자 제외) 평균
        w_nom = df_nomgr[[df_nomgr.columns[0], latest_col]].copy()
        w_nom.columns = ['직종','월임금']
        w_nom['월임금'] = pd.to_numeric(w_nom['월임금'].astype(str).str.replace(',',''), errors='coerce')
        white_no_mgr = w_nom[w_nom['직종'].str.contains('관리자|전문가|사무', na=False)]['월임금'].mean()
        blue_avg = w_mgr[w_mgr['직종'].str.contains('기능원|기계조작|단순', na=False)]['월임금'].mean()

        slope_df = pd.DataFrame({
            '그룹':['화이트칼라(관리자 제외)','블루칼라'],
            '평균':[white_no_mgr, blue_avg]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[slope_df.loc[0,'평균'], slope_df.loc[1,'평균']],
                                 mode='lines+markers', marker=dict(size=12, color=[CW,CB]),
                                 line=dict(color='#9aa5b1')))
        fig.update_layout(**LAYOUT, height=320, xaxis=dict(showticklabels=False), yaxis_title='월임금 (천원)')
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.info("결론용 비교 그래프를 만들기 위한 충분한 임금 데이터가 없습니다.")

    insight("정책·교육·진로 설계 시 관리자 효과(평균을 끌어올리는 영향)를 고려하세요.", 'green')

# -------------------------
# 예외 처리: 페이지 없음
# -------------------------
else:
    st.write("선택된 페이지가 없습니다. 사이드바에서 페이지를 선택하세요.")
