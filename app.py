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
# -------------------------
# 6. 임금 (발표용 개선 블록)
# -------------------------
elif page == "💰 임금":
    import re
    st.title("💰 직종별 평균 임금 비교 (발표용)")

    # 데이터 로드
    df_mgr = load_wage(include_manager=True)
    df_nomgr = load_wage(include_manager=False)

    # 파일 체크
    if (df_mgr is None or df_mgr.empty) and (df_nomgr is None or df_nomgr.empty):
        st.error("임금 CSV 파일을 찾을 수 없습니다. data/ 폴더를 확인하세요.")
    else:
        # --- 연도 컬럼 찾기 (2020~2025 우선) ---
        years = ['2020','2021','2022','2023','2024','2025']
        def find_col(df, y):
            for c in df.columns:
                if str(c).strip() == str(y) or re.search(r'\b' + str(y) + r'\b', str(c)):
                    return c
            return None
        sample = df_mgr if (df_mgr is not None and not df_mgr.empty) else df_nomgr
        year_cols = [find_col(sample, y) for y in years]
        year_cols = [c for c in year_cols if c is not None]

        if not year_cols:
            st.error("연도 컬럼을 찾지 못했습니다. CSV 헤더를 확인하세요.")
        else:
            # --- 정규화 유틸 ---
            def norm_col(df, col):
                s = df[col].astype(str).fillna('')
                s = s.str.replace(',', '').str.replace(' ', '').str.replace('천원','').str.replace('원','').str.replace('\u200b','')
                s = s.replace({'-':'', '—':'', '–':'', '…':'', 'N/A':'', 'na':'', '': np.nan})
                return pd.to_numeric(s, errors='coerce')

            for c in year_cols:
                if df_mgr is not None and c in df_mgr.columns:
                    df_mgr[c] = norm_col(df_mgr, c)
                if df_nomgr is not None and c in df_nomgr.columns:
                    df_nomgr[c] = norm_col(df_nomgr, c)

            # --- 직종 컬럼 찾기 ---
            job_col = None
            for c in sample.columns[:3]:
                if '직종' in str(c) or '직업' in str(c):
                    job_col = c
                    break
            if job_col is None:
                job_col = sample.columns[1] if len(sample.columns) > 1 else sample.columns[0]

            # --- 패턴 정의 ---
            white_pat = r'관리자|전문가|전문직|사무'
            blue_pat  = r'기능원|기능|기계|기계조작|장치|조작|단순|노무|조립'

            def mask(df, pat):
                try:
                    return df[job_col].astype(str).str.contains(pat, na=False)
                except Exception:
                    return pd.Series([False]*len(df), index=df.index)

            # --- 최신 연도 메트릭 (큰 숫자, 발표용 강조) ---
            latest = year_cols[-1]
            white_all = df_mgr.loc[mask(df_mgr, white_pat), latest].mean() if (df_mgr is not None and latest in df_mgr.columns) else np.nan
            white_no_mgr = df_nomgr.loc[mask(df_nomgr, white_pat), latest].mean() if (df_nomgr is not None and latest in df_nomgr.columns) else np.nan
            blue_avg = df_mgr.loc[mask(df_mgr, blue_pat), latest].mean() if (df_mgr is not None and latest in df_mgr.columns) else np.nan

            # 큰 메트릭 영역 (발표용 강조)
            st.markdown("### 핵심 메트릭 (단위: 천원/월)")
            m1, m2, m3, m4 = st.columns([1.2,1.2,1.2,1.2])
            m1.metric("화이트칼라 평균 (관리자 포함)", f"{white_all:,.0f}천원/월" if not np.isnan(white_all) else "데이터 없음")
            m2.metric("화이트칼라 평균 (관리자 제외)", f"{white_no_mgr:,.0f}천원/월" if not np.isnan(white_no_mgr) else "데이터 없음")
            m3.metric("블루칼라 평균", f"{blue_avg:,.0f}천원/월" if not np.isnan(blue_avg) else "데이터 없음")
            if not np.isnan(white_no_mgr) and not np.isnan(blue_avg):
                gap = white_no_mgr - blue_avg
                m4.metric("임금 격차 (관리자 제외)", f"{gap:,.0f}천원", f"{(gap/blue_avg*100):.1f}%")
            else:
                m4.metric("임금 격차 (관리자 제외)", "데이터 없음")

            st.markdown("---")

            # --- 발표용 요약 캡션 (크게) ---
            st.markdown(f"**요약 (한 문장)**: {int(latest) if re.search(r'\\d{4}', str(latest)) else latest}년 기준, 화이트칼라 평균은 **{'' if np.isnan(white_all) else f'{white_all:,.0f}천원/월'}**이며, 블루칼라 평균은 **{'' if np.isnan(blue_avg) else f'{blue_avg:,.0f}천원/월'}**입니다.")
            st.caption("데이터 단위: 천원/월 · 출처: 업로드된 CSV · 전처리: 쉼표·단위 제거")

            # --- 연도별 추이 (라인) ---
            st.markdown("#### 연도별 평균 추이 (화이트 vs 블루)")
            trend = []
            for c in year_cols:
                w = df_mgr.loc[mask(df_mgr, white_pat), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                b = df_mgr.loc[mask(df_mgr, blue_pat), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                trend.append({'연도': str(int(re.search(r'\d{4}', str(c)).group(0))) if re.search(r'\d{4}', str(c)) else str(c),
                              '화이트평균': float(w) if not np.isnan(w) else None,
                              '블루평균': float(b) if not np.isnan(b) else None})
            tdf = pd.DataFrame(trend)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tdf['연도'], y=tdf['화이트평균'], mode='lines+markers', name='화이트칼라', line=dict(color=CW, width=3)))
            fig.add_trace(go.Scatter(x=tdf['연도'], y=tdf['블루평균'], mode='lines+markers', name='블루칼라', line=dict(color=CB, width=3)))
            fig.update_layout(**LAYOUT, height=380, xaxis_title='연도', yaxis_title='평균 월임금 (천원)')
            # 발표용 주석: 최근 연도 값 라벨
            if not tdf['화이트평균'].isna().all():
                fig.add_annotation(x=tdf['연도'].iloc[-1], y=tdf['화이트평균'].iloc[-1],
                                   text=f"화이트 {tdf['화이트평균'].iloc[-1]:,.0f}천원", showarrow=True, arrowhead=2, ax=0, ay=-40, font=dict(color=CW))
            if not tdf['블루평균'].isna().all():
                fig.add_annotation(x=tdf['연도'].iloc[-1], y=tdf['블루평균'].iloc[-1],
                                   text=f"블루 {tdf['블루평균'].iloc[-1]:,.0f}천원", showarrow=True, arrowhead=2, ax=0, ay=40, font=dict(color=CB))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # --- 직종별 분포 (최신 연도) + 발표자 노트 ---
            st.markdown(f"#### 직종별 임금 분포 — {str(latest)} (발표용)")
            if df_mgr is not None and latest in df_mgr.columns:
                tmp = df_mgr[[job_col, latest]].copy()
                tmp.columns = ['직종','월임금']
                tmp['월임금'] = pd.to_numeric(tmp['월임금'], errors='coerce')
                tmp = tmp.dropna(subset=['월임금'])
                if not tmp.empty:
                    def classify(s):
                        s = str(s)
                        if re.search(white_pat, s): return '화이트칼라'
                        if re.search(blue_pat, s): return '블루칼라'
                        return '기타'
                    tmp['직군'] = tmp['직종'].apply(classify)
                    fig2 = px.box(tmp, x='월임금', y='직종', color='직군', orientation='h',
                                  color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO}, points='outliers')
                    fig2.update_layout(**LAYOUT, height=420, xaxis_title='월임금 (천원)')
                    st.plotly_chart(fig2, use_container_width=True)

                    # 발표자 노트(접근성: 버튼으로 토글)
                    if st.button("발표자 노트 보기"):
                        st.markdown("**발표자 노트**")
                        st.write("- 핵심: 관리자 포함 시 화이트칼라 평균이 크게 올라감(관리자 영향).")
                        st.write("- 포인트: 블루칼라 평균은 상대적으로 완만한 상승. 정책적 시사점: 중간임금층 강화 필요.")
                        st.write("- 질문 대비: 데이터 출처, 단위(천원), 전처리(쉼표·단위 제거) 설명 준비.")
                else:
                    st.info("임금 분포를 그릴 데이터가 없습니다.")
            else:
                st.info("관리자 포함 임금 데이터가 없습니다.")

            st.markdown("---")
            # --- 연도별 표 (간단) ---
            st.markdown("#### 연도별 요약 표 (단위: 천원)")
            # 평균 기준 표 생성
            avg_rows = []
            for c in year_cols:
                w = df_mgr.loc[mask(df_mgr, white_pat), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                b = df_mgr.loc[mask(df_mgr, blue_pat), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                avg_rows.append({'연도': str(int(re.search(r'\d{4}', str(c)).group(0))) if re.search(r'\d{4}', str(c)) else str(c),
                                 '화이트평균(천원)': w, '블루평균(천원)': b})
            avg_df = pd.DataFrame(avg_rows).set_index('연도')
            st.dataframe(avg_df.style.format("{:,.0f}"))

            insight("발표용: 슬라이드에는 '한 줄 요약'과 '핵심 수치'만 크게 보여주고, 세부 차트는 보조로 사용하세요.", 'green')


# -------------------------
# 6. 임금 (업로드된 CSV 구조용 완전 대체 블록)
# -------------------------
elif page == "💰 임금":
    import re
    st.title("💰 직종별 평균 임금 비교 (2020–2025)")

    # 데이터 로드 (load_wage 함수가 이미 정의되어 있음)
    df_mgr = load_wage(include_manager=True)    # 관리자 포함 파일
    df_nomgr = load_wage(include_manager=False) # 관리자 미포함 파일

    # 파일 존재 확인
    if (df_mgr is None or df_mgr.empty) and (df_nomgr is None or df_nomgr.empty):
        st.error("임금 관련 CSV 파일을 불러올 수 없습니다. data/ 폴더에 관리자 포함/미포함 CSV를 확인하세요.")
    else:
        # --- 1) 연도 컬럼 명시 (업로드된 파일은 2020..2025 컬럼이 있음) ---
        year_labels = ['2020','2021','2022','2023','2024','2025']
        # 실제 컬럼명 매핑: 파일에는 숫자형 컬럼(정수)으로 들어있을 수 있으므로 문자열/정수 모두 처리
        def find_col(df, y):
            for c in df.columns:
                if str(c).strip() == str(y) or re.search(r'\b' + str(y) + r'\b', str(c)):
                    return c
            return None

        year_cols = []
        sample_df = df_mgr if (df_mgr is not None and not df_mgr.empty) else df_nomgr
        for y in year_labels:
            c = find_col(sample_df, y)
            if c is not None:
                year_cols.append(c)

        if not year_cols:
            st.error("연도 컬럼(2020~2025)을 찾지 못했습니다. CSV 헤더를 확인하세요.")
        else:
            st.write("사용 연도 컬럼:", year_cols)

            # --- 2) 정규화 유틸 (숫자형 보장) ---
            def normalize_col(df, col):
                s = df[col].astype(str).fillna('')
                s = s.str.replace(',', '')
                s = s.str.replace(' ', '')
                s = s.str.replace('천원', '')
                s = s.str.replace('원', '')
                s = s.str.replace('\u200b','')
                s = s.replace({'-':'', '—':'', '–':'', '…':'', 'N/A':'', 'na':'', '': np.nan})
                return pd.to_numeric(s, errors='coerce')

            # 정규화 적용 (원본 덮어쓰기 허용)
            for c in year_cols:
                if df_mgr is not None and c in df_mgr.columns:
                    df_mgr[c] = normalize_col(df_mgr, c)
                if df_nomgr is not None and c in df_nomgr.columns:
                    df_nomgr[c] = normalize_col(df_nomgr, c)

            # --- 3) 직종 컬럼 확인 (첫 컬럼이 '직종별' 형태) ---
            job_col = None
            if df_mgr is not None and not df_mgr.empty:
                job_col = df_mgr.columns[1] if df_mgr.columns[0] in ['고용형태','"고용형태"'] else df_mgr.columns[1] if len(df_mgr.columns)>1 else df_mgr.columns[0]
                # uploaded CSV uses columns: "고용형태","직종별",2020...
                # ensure we pick the '직종별' column
                # try to find column name containing '직종' if present
                for c in df_mgr.columns[:3]:
                    if '직종' in str(c):
                        job_col = c
                        break
            elif df_nomgr is not None and not df_nomgr.empty:
                for c in df_nomgr.columns[:3]:
                    if '직종' in str(c):
                        job_col = c
                        break

            if job_col is None:
                st.error("직종 컬럼을 찾을 수 없습니다.")
            else:
                st.write("직종 컬럼:", job_col)

                # --- 4) 화이트/블루 패턴 (업로드된 직종명에 맞춤) ---
                white_pattern = r'관리자|전문가|전문직|사무'
                blue_pattern  = r'기능원|기능|기계|기계조작|장치|조작|단순|노무|조립'

                def mask(df, pattern):
                    try:
                        return df[job_col].astype(str).str.contains(pattern, na=False)
                    except Exception:
                        return pd.Series([False]*len(df), index=df.index)

                # --- 5) 연도별 집계(합계 또는 평균) 생성 ---
                trend = []
                for c in year_cols:
                    w_sum = df_mgr.loc[mask(df_mgr, white_pattern), c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    b_sum = df_mgr.loc[mask(df_mgr, blue_pattern), c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    total = df_mgr[c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    # 단위: 천원(파일 기준)
                    trend.append({'연도': str(int(re.search(r'\d{4}', str(c)).group(0))) if re.search(r'\d{4}', str(c)) else str(c),
                                  '화이트합계': float(w_sum or 0),
                                  '블루합계': float(b_sum or 0),
                                  '총합계': float(total or 0)})

                trend_df = pd.DataFrame(trend)

                # --- 6) 관리자 포함/제외 평균(최신 연도 기준) ---
                latest_col = year_cols[-1]
                # 관리자 포함: df_mgr에서 '관리자(1)' 등 매칭
                mgr_mask = df_mgr[job_col].astype(str).str.contains(r'관리자', na=False) if (df_mgr is not None and latest_col in df_mgr.columns) else pd.Series([False])
                white_mask_mgr = mask(df_mgr, white_pattern) if (df_mgr is not None and latest_col in df_mgr.columns) else pd.Series([False])
                white_mask_nom = mask(df_nomgr, white_pattern) if (df_nomgr is not None and latest_col in df_nomgr.columns) else pd.Series([False])
                blue_mask_mgr = mask(df_mgr, blue_pattern) if (df_mgr is not None and latest_col in df_mgr.columns) else pd.Series([False])

                white_all = df_mgr.loc[white_mask_mgr, latest_col].mean() if (df_mgr is not None and latest_col in df_mgr.columns) else np.nan
                white_no_mgr = df_nomgr.loc[white_mask_nom, latest_col].mean() if (df_nomgr is not None and latest_col in df_nomgr.columns) else np.nan
                blue_avg = df_mgr.loc[blue_mask_mgr, latest_col].mean() if (df_mgr is not None and latest_col in df_mgr.columns) else np.nan

                # 메트릭 (단위: 천원/월)
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("화이트칼라 평균(관리자 포함)", f"{white_all:,.0f}천원/월" if not np.isnan(white_all) else "데이터 없음")
                c2.metric("화이트칼라 평균(관리자 제외)", f"{white_no_mgr:,.0f}천원/월" if not np.isnan(white_no_mgr) else "데이터 없음")
                c3.metric("블루칼라 평균", f"{blue_avg:,.0f}천원/월" if not np.isnan(blue_avg) else "데이터 없음")
                c4.metric("임금 격차(관리자 제외)", f"{(white_no_mgr - blue_avg):,.0f}천원" if (not np.isnan(white_no_mgr) and not np.isnan(blue_avg)) else "데이터 없음")

                st.markdown("---")

                # --- 7) 연도별 추이 (라인 차트) ---
                st.markdown("#### 연도별 합계 추이 (화이트 vs 블루)")
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=trend_df['연도'], y=trend_df['화이트합계'], mode='lines+markers', name='화이트칼라', line=dict(color=CW)))
                fig_line.add_trace(go.Scatter(x=trend_df['연도'], y=trend_df['블루합계'], mode='lines+markers', name='블루칼라', line=dict(color=CB)))
                fig_line.update_layout(**LAYOUT, xaxis_title='연도', yaxis_title='월임금 합계 (단위: 천원)', height=420)
                st.plotly_chart(fig_line, use_container_width=True)

                # --- 8) 연도별 비교 막대 (그룹형) ---
                st.markdown("#### 연도별 비교 (그룹형 막대)")
                bar_df = trend_df.melt(id_vars=['연도'], value_vars=['화이트합계','블루합계'], var_name='직군', value_name='값')
                bar_df['직군'] = bar_df['직군'].map({'화이트합계':'화이트칼라','블루합계':'블루칼라'})
                fig_bar = px.bar(bar_df, x='연도', y='값', color='직군', barmode='group', color_discrete_map={'화이트칼라':CW,'블루칼라':CB})
                fig_bar.update_layout(**LAYOUT, yaxis_title='월임금 합계 (천원)', height=420)
                st.plotly_chart(fig_bar, use_container_width=True)

                # --- 9) 직종별 분포 (박스플롯) for latest year ---
                st.markdown(f"#### 직종별 임금 분포 (박스플롯) — {str(latest_col)}")
                if df_mgr is not None and latest_col in df_mgr.columns:
                    tmp = df_mgr[[job_col, latest_col]].copy()
                    tmp.columns = ['직종','월임금']
                    tmp['월임금'] = pd.to_numeric(tmp['월임금'], errors='coerce')
                    tmp = tmp.dropna(subset=['월임금'])
                    if not tmp.empty:
                        # classify
                        def classify(s):
                            s = str(s)
                            if re.search(white_pattern, s): return '화이트칼라'
                            if re.search(blue_pattern, s): return '블루칼라'
                            return '기타'
                        tmp['직군'] = tmp['직종'].apply(classify)
                        fig_box = px.box(tmp, x='월임금', y='직종', color='직군', orientation='h',
                                         color_discrete_map={'화이트칼라':CW,'블루칼라':CB,'기타':CO}, points='outliers')
                        fig_box.update_layout(**LAYOUT, xaxis_title='월임금 (천원)', height=420)
                        st.plotly_chart(fig_box, use_container_width=True)
                    else:
                        st.info("임금 분포를 그릴 데이터가 없습니다.")
                else:
                    st.info("관리자 포함 임금 데이터가 없습니다.")

                # --- 10) 연도별 집계 표 출력 ---
                st.markdown("#### 연도별 집계 표 (단위: 천원)")
                st.dataframe(trend_df.set_index('연도'))
                insight("데이터 단위는 CSV 기준으로 '천원'입니다. 관리자 포함/제외의 차이를 확인하세요.", 'green')




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

