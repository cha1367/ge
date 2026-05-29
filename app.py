# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="화이트칼라 · 블루칼라 분석", page_icon="📊", layout="wide")

# -------------------------
# 스타일 (간단 다크 테마)
# -------------------------
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #c9d1d9; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#161b22 0%,#0d1117 100%); border-right:1px solid #30363d; }
[data-testid="stSidebar"] * { color:#e6edf3 !important; }
[data-testid="metric-container"] { background:#0f1720; border:1px solid #30363d; border-radius:12px; padding:12px; }
.insight-box { background:#0f1720; border-left:4px solid #58a6ff; border-radius:0 8px 8px 0; padding:12px 16px; margin:8px 0; color:#9aa5b1; font-size:14px; }
.insight-red { border-left-color:#f85149; }
.insight-green { border-left-color:#3fb950; }
h1 { color:#58a6ff !important; }
h2,h3 { color:#e6edf3 !important; }
hr { border-color:#30363d !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 공통 설정
# -------------------------
CW, CB, CO = '#58a6ff', '#f85149', '#6e7681'
LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#9aa5b1', family='sans-serif'),
    margin=dict(t=40,b=30,l=20,r=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3')),
)

def insight(text, color='blue'):
    cls = 'insight-box' + (' insight-red' if color=='red' else ' insight-green' if color=='green' else '')
    st.markdown(f'<div class="{cls}">💡 {text}</div>', unsafe_allow_html=True)

# -------------------------
# 안전 로드 / 전처리 유틸
# -------------------------
@st.cache_data
def load_csv_safe(path):
    try:
        return pd.read_csv(path, encoding='utf-8-sig')
    except Exception:
        return pd.read_csv(path, encoding='cp949', errors='ignore')

def to_numeric_safe(series):
    s = series.astype(str).fillna('')
    s = s.str.replace(',', '').str.replace(' ', '').str.replace('\u200b','')
    s = s.replace({'-': np.nan, '—': np.nan, '–': np.nan, '…': np.nan, 'N/A': np.nan, 'na': np.nan, '': np.nan})
    return pd.to_numeric(s, errors='coerce')

def find_year_columns(df):
    years = [c for c in df.columns if str(c).isdigit() and len(str(c))==4]
    return years if years else [c for c in df.columns if any(ch.isdigit() for ch in str(c))]

# -------------------------
# 데이터 로드 (data/ 폴더)
# -------------------------
@st.cache_data
def load_yearly(): return load_csv_safe("data/직업별_취업자_연도별.csv")
@st.cache_data
def load_region(): return load_csv_safe("data/시도별_직업별.csv")
@st.cache_data
def load_gender(): return load_csv_safe("data/성별_직업별.csv")
@st.cache_data
def load_age(): return load_csv_safe("data/직업별_학력별.csv")
@st.cache_data
def load_wage(include_manager=True):
    fname = "data/관리자 포함.csv" if include_manager else "data/관리자 미 포함.csv"
    return load_csv_safe(fname)

# -------------------------
# 사이드바 (필터 + 디버그)
# -------------------------
with st.sidebar:
    st.title("📊 직종 분포 분석")
    page = st.radio("", ["🏠 소개","📊 전국 현황","🗺 지역별","👥 성별","🎂 연령별","💰 임금","📝 결론"])
    st.markdown("---")
    st.checkbox("디버그 모드 (값 출력)", key="debug")
    st.markdown("**데이터 파일 (data/ 폴더)**")
    st.write("- 관리자 포함.csv  - 관리자 미 포함.csv")
    st.write("- 성별_직업별.csv  - 시도별_직업별.csv")
    st.write("- 직업별_취업자_연도별.csv  - 직업별_학력별.csv")
    st.markdown("---")
    st.markdown("🔵 **화이트칼라**: 관리자 · 전문가 · 사무")
    st.markdown("🔴 **블루칼라**: 기능원 · 기계조작 · 단순노무")

# -------------------------
# 1. 소개
# -------------------------
if page == "🏠 소개":
    st.title("대한민국 화이트칼라 · 블루칼라 분석")
    st.markdown("#### 목적: 직종 구조와 임금 차이를 지역·성별·연령 관점에서 시각화")
    st.markdown("---")
    st.markdown("**사용법**: 사이드바에서 페이지 선택 → (전국/지역/성별/연령/임금) 확인 → 필요시 디버그 모드 켜서 값 확인")
    insight("앱 실행 전 data/ 폴더에 CSV 파일들이 있는지 확인하세요.", 'green')

# -------------------------
# 2. 전국 현황
# -------------------------
elif page == "📊 전국 현황":
    st.title("📊 전국 현황")
    df = load_yearly()
    if df is None or df.empty:
        st.error("직업별_취업자_연도별.csv를 불러올 수 없습니다.")
    else:
        year_cols = find_year_columns(df)
        if not year_cols:
            st.error("연도 컬럼을 찾지 못했습니다.")
        else:
            latest = year_cols[-1]
            job_col = df.columns[0]

            white_mask = df[job_col].astype(str).str.contains('관리자|전문가|전문직|사무', na=False)
            blue_mask = df[job_col].astype(str).str.contains('기능원|기계|기계조작|장치|단순|노무', na=False)

            # 안전 합계
            total_row = df[df[job_col].astype(str).str.contains('계', na=False)]
            total = to_numeric_safe(total_row[latest]).sum() if not total_row.empty else to_numeric_safe(df[latest]).sum()
            white = to_numeric_safe(df.loc[white_mask, latest]).sum()
            blue = to_numeric_safe(df.loc[blue_mask, latest]).sum()
            other = max(total - white - blue, 0)

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("전체 취업자", f"{total/10000:.1f}만명", f"{latest}년")
            c2.metric("화이트칼라 비율", f"{white/total*100:.1f}%")
            c3.metric("블루칼라 비율", f"{blue/total*100:.1f}%")
            c4.metric("기타", f"{other:.0f}명")

            st.markdown("---")
            col1, col2 = st.columns([1,1.6])
            with col1:
                st.markdown(f"#### 직군별 비율 (도넛) — {latest}년, 단위: 명")
                pie = pd.DataFrame({'직군':['화이트칼라','블루칼라','기타'], '취업자':[white,blue,other]})
                fig = px.pie(pie, values='취업자', names='직군', hole=0.55,
                             color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO})
                fig.update_traces(textposition='outside', textinfo='percent+label', textfont=dict(color='#e6edf3'))
                fig.update_layout(**LAYOUT, height=380, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("#### 연도별 취업자 추이 (화이트 vs 블루)")
                trend = []
                for y in year_cols:
                    w = to_numeric_safe(df.loc[white_mask, y]).sum() if y in df.columns else 0
                    b = to_numeric_safe(df.loc[blue_mask, y]).sum() if y in df.columns else 0
                    trend.append({'연도':str(y),'화이트칼라':w,'블루칼라':b})
                tdf = pd.DataFrame(trend)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트칼라'], name='화이트칼라', line=dict(color=CW, width=3), fill='tozeroy'))
                fig2.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루칼라'], name='블루칼라', line=dict(color=CB, width=3), fill='tozeroy'))
                fig2.update_layout(**LAYOUT, height=380, xaxis_title='연도', yaxis_title='취업자 수 (명)')
                st.plotly_chart(fig2, use_container_width=True)

            if st.session_state.debug:
                st.markdown("#### (디버그) 직업명 샘플")
                st.write(df[job_col].astype(str).unique()[:60])

# -------------------------
# 3. 지역별 (완전판)
# -------------------------
elif page == "🗺 지역별":
    st.title("🗺 시도별 분포")
    df = load_region()
    if df is None or df.empty:
        st.error("시도별_직업별.csv를 불러올 수 없습니다.")
    else:
        # 최신값 컬럼 자동 탐색
        cols_2024 = [c for c in df.columns if '2024' in str(c)]
        latest_col = cols_2024[0] if cols_2024 else (next((c for c in df.columns[::-1] if any(ch.isdigit() for ch in str(c))), df.columns[-1]))

        region_col = next((c for c in df.columns if '행정' in str(c) or '시도' in str(c) or '행정구역' in str(c)), df.columns[0])
        job_col = next((c for c in df.columns if '직업' in str(c) or '직종' in str(c)), df.columns[1] if len(df.columns)>1 else df.columns[0])

        st.markdown(f"**사용 컬럼**: 행정구역 `{region_col}` · 직업명 `{job_col}` · 값 `{latest_col}`")
        regions = df[region_col].dropna().unique()
        rows = []
        for reg in regions:
            sub = df[df[region_col] == reg]
            if sub.empty: continue

            # 총계 우선 찾기
            total = None
            total_row = sub[sub[job_col].astype(str).str.contains('계', na=False)]
            if not total_row.empty:
                total_val = to_numeric_safe(total_row[latest_col])
                if not total_val.isna().all():
                    total = float(total_val.sum())
            if total is None:
                total = float(to_numeric_safe(sub[latest_col]).sum())

            white_mask = sub[job_col].astype(str).str.contains('관리자|전문가|전문직|사무|사무종사', na=False)
            blue_mask = sub[job_col].astype(str).str.contains('기능원|기계|기계조작|장치|단순|노무', na=False)

            white_sum = float(to_numeric_safe(sub.loc[white_mask, latest_col]).sum() or 0)
            blue_sum  = float(to_numeric_safe(sub.loc[blue_mask, latest_col]).sum() or 0)

            rows.append({'지역': reg, '화이트': white_sum, '블루': blue_sum, '총': total})

        rdf = pd.DataFrame(rows).dropna(subset=['총'])
        if rdf.empty:
            st.warning("지역별 집계 결과가 비어있습니다. CSV 구조를 확인하세요.")
        else:
            rdf['화이트비율'] = (rdf['화이트'] / rdf['총'] * 100).fillna(0)
            rdf['블루비율'] = (rdf['블루'] / rdf['총'] * 100).fillna(0)

            st.markdown(f"#### 시도별 직군 트리맵 — {latest_col} 기준")
            melt = rdf.melt(id_vars=['지역','총'], value_vars=['화이트','블루'], var_name='직군', value_name='취업자')
            fig_tree = px.treemap(melt, path=['지역','직군'], values='취업자',
                                  color='직군', color_discrete_map={'화이트':CW,'블루':CB})
            fig_tree.update_layout(**LAYOUT, height=420)
            st.plotly_chart(fig_tree, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 시도별 화이트 vs 블루 비율 (로리팝)")
            rdf_sorted = rdf.sort_values('블루비율', ascending=True)
            fig_lolli = go.Figure()
            for _, row in rdf_sorted.iterrows():
                w_pct = row['화이트']/row['총']*100 if row['총']>0 else 0
                b_pct = row['블루']/row['총']*100 if row['총']>0 else 0
                fig_lolli.add_trace(go.Scatter(x=[w_pct, b_pct], y=[row['지역'], row['지역']],
                                               mode='lines', line=dict(color='#30363d', width=2), showlegend=False))
            fig_lolli.add_trace(go.Scatter(x=rdf_sorted['화이트비율'], y=rdf_sorted['지역'],
                                           mode='markers', name='화이트칼라',
                                           marker=dict(color=CW, size=12, line=dict(color='white', width=1))))
            fig_lolli.add_trace(go.Scatter(x=rdf_sorted['블루비율'], y=rdf_sorted['지역'],
                                           mode='markers', name='블루칼라',
                                           marker=dict(color=CB, size=12, line=dict(color='white', width=1))))
            fig_lolli.update_layout(**LAYOUT, height=520, xaxis_title='비율 (%)', yaxis_title='')
            st.plotly_chart(fig_lolli, use_container_width=True)

            st.markdown("#### 집계 샘플 (상위 10개)")
            st.dataframe(rdf.sort_values('블루', ascending=False).head(10).reset_index(drop=True))

            if st.session_state.debug:
                st.markdown("#### (디버그) 지역별 원시 샘플")
                st.write(df[[region_col, job_col, latest_col]].head(50))

            insight("지역별 직업 표기 방식이 다양하면 매칭 패턴을 확장하세요.", 'green')

# -------------------------
# 4. 성별
# -------------------------
elif page == "👥 성별":
    st.title("👥 성별 직종 분포")
    df = load_gender()
    if df is None or df.empty:
        st.error("성별_직업별.csv를 불러올 수 없습니다.")
    else:
        year_cols = find_year_columns(df)
        latest = year_cols[-1] if year_cols else df.columns[-1]

        def calc_gender_counts(g):
            sub = df[df['성별'] == g]
            w = to_numeric_safe(sub[sub['직업별'].astype(str).str.contains('관리자|전문가|전문직|사무', na=False)][latest]).sum()
            b = to_numeric_safe(sub[sub['직업별'].astype(str).str.contains('기능원|기계|기계조작|장치|단순|노무', na=False)][latest]).sum()
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
        # LABEL_G은 데이터에 맞게 조정 필요
        LABEL_G = {
            '1 관리자':'관리자','2 전문가 및 관련 종사자':'전문가','3 사무 종사자':'사무종사자',
            '7 기능원 및 관련 기능종사자':'기능원','8 장치,기계조작 및 조립종사자':'기계조작','9 단순노무 종사자':'단순노무'
        }
        stack_list = []
        for gender in ['남자','여자']:
            sub = df[(df['성별']==gender) & (df['직업별'].isin(LABEL_G.keys()))][['직업별', latest]].copy()
            if sub.empty: continue
            sub[latest] = pd.to_numeric(sub[latest], errors='coerce')
            sub['직업별'] = sub['직업별'].map(LABEL_G)
            sub['성별'] = '남성' if gender=='남자' else '여성'
            stack_list.append(sub)
        if stack_list:
            sdf = pd.concat(stack_list)
            sdf.columns = ['직종','취업자','성별']
            fig = px.bar(sdf, x='직종', y='취업자', color='성별', barmode='stack',
                         color_discrete_map={'남성':CW,'여성':'#f778ba'})
            fig.update_layout(**LAYOUT, height=380, xaxis_title='', yaxis_title='취업자 수 (명)')
            st.plotly_chart(fig, use_container_width=True)
            insight("남성은 블루칼라 비중이 높고, 여성은 화이트칼라 비중이 상대적으로 높습니다.", 'red')
        else:
            st.info("직종별 성별 데이터가 충분하지 않습니다. CSV 구조를 확인하세요.")

# -------------------------
# 5. 연령별
# -------------------------
elif page == "🎂 연령별":
    st.title("🎂 연령별 직종 분포")
    df = load_age()
    if df is None or df.empty:
        st.error("직업별_학력별.csv를 불러올 수 없습니다.")
    else:
        age_cols = [c for c in df.columns if '2024' in str(c) or '연령' in str(c) or '세' in str(c)]
        if not age_cols:
            age_cols = [c for c in df.columns if any(ch.isdigit() for ch in str(c))]
        df_sub = df[df['직업별'].astype(str).str.contains('관리자|전문가|사무|기능원|기계|단순|노무', na=False)].copy()
        if age_cols:
            melt = df_sub.melt(id_vars=['직업별'], value_vars=age_cols, var_name='연령대', value_name='취업자')
            melt['취업자'] = to_numeric_safe(melt['취업자'])
            fig = px.bar(melt, x='직업별', y='취업자', color='연령대', barmode='stack')
            fig.update_layout(**LAYOUT, height=420, xaxis_title='', yaxis_title='취업자 수 (명)')
            st.plotly_chart(fig, use_container_width=True)
            insight("연령대별 직종 선호 차이를 확인하세요.", 'green')
        else:
            st.warning("연령대 컬럼을 찾지 못했습니다. CSV 구조를 확인해주세요.")

# -------------------------
# 6. 임금
# -------------------------
elif page == "💰 임금":
    st.title("💰 직종별 평균 임금 비교")
    df_mgr = load_wage(True)
    df_nomgr = load_wage(False)
    if (df_mgr is None or df_mgr.empty) and (df_nomgr is None or df_nomgr.empty):
        st.error("임금 관련 CSV 파일을 불러올 수 없습니다.")
    else:
        def find_wage_col(df):
            candidates = [c for c in df.columns if '월임금' in str(c)]
            if candidates: return candidates[-1]
            for c in df.columns[::-1]:
                import re
                if re.search(r'(\d{4})', str(c)): return c
            num_cols = [c for c in df.columns if df[c].dtype != object]
            return num_cols[-1] if num_cols else df.columns[-1]

        wage_col = find_wage_col(df_mgr if (df_mgr is not None and not df_mgr.empty) else df_nomgr)
        WLABEL = {
            '전직종':'전직종','관리자(1)':'관리자','전문가 및 관련종사자(2)':'전문가',
            '사무 종사자(3)':'사무종사자','서비스 종사자(4)':'서비스','판매 종사자(5)':'판매',
            '농림·어업 숙련 종사자(6)':'농림어업','기능원 및 관련 기능 종사자(7)':'기능원',
            '장치·기계 조작 및 조립 종사자(8)':'기계조작','단순노무 종사자(9)':'단순노무'
        }

        def process_wage(df, wage_col):
            job_col = df.columns[0]
            tmp = df[[job_col, wage_col]].copy()
            tmp.columns = ['직종','월임금']
            tmp['월임금'] = tmp['월임금'].astype(str).str.replace(',', '').str.replace(' ', '')
            tmp['월임금'] = pd.to_numeric(tmp['월임금'], errors='coerce')
            tmp['직종'] = tmp['직종'].map(WLABEL).fillna(tmp['직종'])
            tmp['직군'] = tmp['직종'].apply(lambda x: '화이트칼라' if x in ['관리자','전문가','사무종사자'] else '블루칼라')
            return tmp.dropna(subset=['월임금'])

        w_mgr = process_wage(df_mgr, wage_col) if (df_mgr is not None and not df_mgr.empty) else pd.DataFrame(columns=['직종','월임금','직군'])
        w_nomgr = process_wage(df_nomgr, wage_col) if (df_nomgr is not None and not df_nomgr.empty) else pd.DataFrame(columns=['직종','월임금','직군'])

        white_all = w_mgr[w_mgr['직군']=='화이트칼라']['월임금'].mean() if not w_mgr.empty else np.nan
        white_no_mgr = w_nomgr[w_nomgr['직군']=='화이트칼라']['월임금'].mean() if not w_nomgr.empty else np.nan
        blue_avg = w_mgr[w_mgr['직군']=='블루칼라']['월임금'].mean() if not w_mgr.empty else np.nan

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("화이트칼라 평균(관리자 포함)", f"{white_all:,.0f}천원/월" if not np.isnan(white_all) else "데이터 없음")
        c2.metric("화이트칼라 평균(관리자 제외)", f"{white_no_mgr:,.0f}천원/월" if not np.isnan(white_no_mgr) else "데이터 없음")
        c3.metric("블루칼라 평균", f"{blue_avg:,.0f}천원/월" if not np.isnan(blue_avg) else "데이터 없음")
        c4.metric("임금 격차(관리자 제외)", f"{(white_no_mgr - blue_avg):,.0f}천원" if (not np.isnan(white_no_mgr) and not np.isnan(blue_avg)) else "데이터 없음")

        st.markdown("---")
        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("#### 직종별 평균 임금 (관리자 포함)")
            if not w_mgr.empty:
                order = w_mgr.groupby('직종')['월임금'].median().sort_values(ascending=False).index.tolist()
                fig = px.bar(w_mgr.sort_values('월임금', ascending=False), x='직종', y='월임금', color='직군',
                             category_orders={'직종': order}, color_discrete_map={'화이트칼라':CW,'블루칼라':CB}, text='월임금')
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(**LAYOUT, height=420, xaxis_title='', yaxis_title='월임금 (천원)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("관리자 포함 임금 데이터가 없습니다.")
        with col2:
            st.markdown("#### 직종별 임금 분포 (박스플롯)")
            if not w_mgr.empty:
                fig2 = px.box(w_mgr, x='월임금', y='직종', color='직군', color_discrete_map={'화이트칼라':CW,'블루칼라':CB}, points='outliers', orientation='h')
                shapes = []
                if not np.isnan(white_all):
                    shapes.append(dict(type='line', x0=white_all, x1=white_all, y0=-0.5, y1=len(w_mgr['직종'].unique())-0.5, line=dict(color=CW, dash='dash', width=1.5)))
                if not np.isnan(blue_avg):
                    shapes.append(dict(type='line', x0=blue_avg, x1=blue_avg, y0=-0.5, y1=len(w_mgr['직종'].unique())-0.5, line=dict(color=CB, dash='dash', width=1.5)))
                fig2.update_layout(**LAYOUT, height=420, shapes=shapes, xaxis_title='월임금 (천원)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("임금 분포를 그릴 데이터가 없습니다.")

        insight("관리자 직종은 평균을 끌어올립니다. 관리자 제외 평균을 함께 제시하세요.", 'green')

# -------------------------
# 7. 결론
# -------------------------
elif page == "📝 결론":
    st.title("📝 결론 및 시사점")
    st.markdown("#### 요약")
    try:
        df_yearly = load_yearly()
        year_cols = find_year_columns(df_yearly)
        latest = year_cols[-1] if year_cols else df_yearly.columns[-1]
        total = to_numeric_safe(df_yearly[df_yearly[df_yearly.columns[0]].astype(str).str.contains('계', na=False)][latest]).sum()
        st.metric("전체 취업자 (최근)", f"{total/10000:.1f}만명")
    except Exception:
        st.write("- 일부 수치가 비어있을 수 있습니다.")

    st.markdown("---")
    st.write("- 화이트칼라 비중이 증가하는 추세가 관찰됩니다.")
    st.write("- 지역별 산업구조 차이가 뚜렷합니다.")
    st.write("- 임금은 관리자 효과를 고려해야 합니다.")
    insight("교수님용: 데이터·전처리·단위(천원/월) 명시 권장", 'green')

# -------------------------
# 기본
# -------------------------
else:
    st.write("사이드바에서 페이지를 선택하세요.")

