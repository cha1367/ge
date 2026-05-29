# app.py (전체 수정본)
import re
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

    df_age = load_age()
    if df_age is None or df_age.empty:
        st.error("연령별 데이터가 없습니다. df_age를 로드하거나 파일을 확인하세요.")
    else:
        # --- 1. 직종 컬럼(행 레이블) 찾기 ---
        job_col = None
        for c in df_age.columns[:3]:
            if '직종' in str(c) or '직업' in str(c) or '직종별' in str(c):
                job_col = c
                break
        if job_col is None:
            job_col = df_age.columns[1] if len(df_age.columns) > 1 else df_age.columns[0]
        st.write("직종 컬럼:", job_col)

        # --- 2. 연령 컬럼 자동 탐색 ---
        age_cols = []
        for c in df_age.columns:
            s = str(c)
            if (re.search(r'\d{2}대', s)
                or re.search(r'\b(10|20|30|40|50|60|70)대\b', s)
                or re.search(r'\d{4}\.\d+/\d+', s)
                or re.search(r'^\d{2}$', s)):
                age_cols.append(c)
        if not age_cols:
            age_cols = list(df_age.columns[2:]) if len(df_age.columns) > 2 else []
        if not age_cols:
            st.error("연령 컬럼을 자동으로 찾지 못했습니다. 컬럼명을 확인하거나 수동으로 age_cols를 지정하세요.")
        else:
            st.write("탐지된 연령 컬럼:", age_cols)

            # --- 3. 정규화: 숫자형으로 변환 ---
            def to_num(s):
                s = str(s)
                s = s.replace(',', '').replace(' ', '').replace('명','').replace('명수','')
                s = s.replace('\u200b','')
                return pd.to_numeric(s, errors='coerce')

            df_age_norm = df_age.copy()
            for c in age_cols:
                df_age_norm[c] = to_num(df_age_norm[c])

            # --- 4. 요약 테이블: 직종별 총합 및 연령별 비율 ---
            df_age_norm['총계'] = df_age_norm[age_cols].sum(axis=1, skipna=True)
            top_n = st.slider("상위 직종 개수", min_value=5, max_value=20, value=10)
            top_jobs = df_age_norm.sort_values('총계', ascending=False).head(top_n)

            st.markdown("#### 상위 직종 표 (총계 기준)")
            # 안전 출력: 숫자형 보장 후 스타일 적용
            display_df = top_jobs[[job_col, '총계'] + age_cols].copy()
            for c in age_cols + ['총계']:
                display_df[c] = pd.to_numeric(display_df[c], errors='coerce').fillna(0)
            st.dataframe(display_df.reset_index(drop=True).style.format("{:,.0f}"))

            # --- 5. 누적 막대: 직종별 연령 분포 (절대값) ---
            st.markdown("#### 직종별 연령 분포 (절대값, 상위 직종)")
            plot_df = top_jobs[[job_col] + age_cols].melt(id_vars=[job_col], value_vars=age_cols, var_name='연령', value_name='취업자수')
            order = top_jobs[job_col].tolist()
            fig = px.bar(plot_df, x=job_col, y='취업자수', color='연령', category_orders={job_col: order},
                         labels={job_col:'직종', '취업자수':'취업자 수 (명)'})
            fig.update_layout(barmode='stack', xaxis={'categoryorder':'array', 'categoryarray':order}, height=520, **LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

            # --- 6. 비율 누적 막대: 직종별 연령 비율 ---
            st.markdown("#### 직종별 연령 비율 (정규화, 상위 직종)")
            pct_df = top_jobs[[job_col] + age_cols].copy()
            for c in age_cols:
                pct_df[c] = pct_df[c] / pct_df['총계'] * 100
            plot_pct = pct_df.melt(id_vars=[job_col], value_vars=age_cols, var_name='연령', value_name='비율')
            fig2 = px.bar(plot_pct, x=job_col, y='비율', color='연령', category_orders={job_col: order}, labels={'비율':'비율 (%)'})
            fig2.update_layout(barmode='stack', height=520, **LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

            # --- 7. 연령별 상위 직종 ---
            st.markdown("#### 연령별 상위 직종")
            top_k = st.slider("연령별 상위 직종 개수", min_value=3, max_value=10, value=5, key='topk_age')
            for c in age_cols:
                tmp = df_age_norm[[job_col, c]].dropna().sort_values(c, ascending=False).head(top_k)
                st.markdown(f"**{c} 상위 {top_k} 직종**")
                st.table(tmp.set_index(job_col).style.format("{:,.0f}"))

            # --- 8. 특정 직종 연령 분포 ---
            st.markdown("#### 특정 직종의 연령 분포 보기")
            selected_job = st.selectbox("직종 선택", df_age_norm[job_col].astype(str).unique().tolist(), index=0)
            sel_row = df_age_norm[df_age_norm[job_col].astype(str) == str(selected_job)]
            if not sel_row.empty:
                sel_vals = sel_row[age_cols].iloc[0].to_dict()
                sel_df = pd.DataFrame({'연령': list(sel_vals.keys()), '취업자수': list(sel_vals.values())})
                fig3 = px.bar(sel_df, x='취업자수', y='연령', orientation='h', labels={'취업자수':'취업자 수 (명)'}, color='연령', height=360)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("선택한 직종의 데이터가 없습니다.")

            # --- 9. 발표자 노트 및 체크리스트 ---
            st.markdown("---")
            st.markdown("**발표자 노트**")
            st.write("- 슬라이드에는 한 줄 요약과 핵심 연령대 수치만 크게 표시하세요.")
            st.write("- 상위 5~8개 직종만 슬라이드에 노출하면 가독성이 좋아집니다.")
            st.markdown("**체크리스트**")
            st.write("- 데이터 단위 확인 완료")
            st.write("- 상위 직종 개수 조정(슬라이더로 테스트)")

            # --- 10. 디버그 출력 ---
            if st.checkbox("디버그 출력 보기"):
                st.write("원본 컬럼:", list(df_age.columns))
                st.write("탐지된 연령 컬럼:", age_cols)
                st.write("직종 샘플:", df_age[job_col].astype(str).unique()[:30])
                st.dataframe(df_age_norm[[job_col] + age_cols].head(8))

# -------------------------
# 6. 임금 (업로드된 CSV 구조용 완전 대체 블록)
# -------------------------
elif page == "💰 임금":
    st.title("💰 직종별 평균 임금 비교 (2020–2025)")

    df_mgr = load_wage(include_manager=True)
    df_nomgr = load_wage(include_manager=False)

    if (df_mgr is None or df_mgr.empty) and (df_nomgr is None or df_nomgr.empty):
        st.error("임금 관련 CSV 파일을 불러올 수 없습니다. data/ 폴더에 관리자 포함/미포함 CSV를 확인하세요.")
    else:
        year_labels = ['2020','2021','2022','2023','2024','2025']
        def find_col(df, y):
            for c in df.columns:
                if str(c).strip() == str(y) or re.search(r'\b' + str(y) + r'\b', str(c)):
                    return c
            return None

        sample_df = df_mgr if (df_mgr is not None and not df_mgr.empty) else df_nomgr
        year_cols = [find_col(sample_df, y) for y in year_labels]
        year_cols = [c for c in year_cols if c is not None]

        if not year_cols:
            st.error("연도 컬럼(2020~2025)을 찾지 못했습니다. CSV 헤더를 확인하세요.")
        else:
            st.write("사용 연도 컬럼:", year_cols)

            def normalize_col(df, col):
                s = df[col].astype(str).fillna('')
                s = s.str.replace(',', '')
                s = s.str.replace(' ', '')
                s = s.str.replace('천원', '')
                s = s.str.replace('원', '')
                s = s.str.replace('\u200b','')
                s = s.replace({'-':'', '—':'', '–':'', '…':'', 'N/A':'', 'na':'', '': np.nan})
                return pd.to_numeric(s, errors='coerce')

            for c in year_cols:
                if df_mgr is not None and c in df_mgr.columns:
                    df_mgr[c] = normalize_col(df_mgr, c)
                if df_nomgr is not None and c in df_nomgr.columns:
                    df_nomgr[c] = normalize_col(df_nomgr, c)

            # 직종 컬럼 찾기
            job_col = None
            if df_mgr is not None and not df_mgr.empty:
                for c in df_mgr.columns[:3]:
                    if '직종' in str(c) or '직업' in str(c):
                        job_col = c
                        break
                if job_col is None:
                    job_col = df_mgr.columns[1] if len(df_mgr.columns)>1 else df_mgr.columns[0]
            elif df_nomgr is not None and not df_nomgr.empty:
                for c in df_nomgr.columns[:3]:
                    if '직종' in str(c) or '직업' in str(c):
                        job_col = c
                        break

            if job_col is None:
                st.error("직종 컬럼을 찾을 수 없습니다.")
            else:
                st.write("직종 컬럼:", job_col)

                white_pattern = r'관리자|전문가|전문직|사무'
                blue_pattern  = r'기능원|기능|기계|기계조작|장치|조작|단순|노무|조립'

                def mask(df, pattern):
                    try:
                        return df[job_col].astype(str).str.contains(pattern, na=False)
                    except Exception:
                        return pd.Series([False]*len(df), index=df.index)

                trend = []
                for c in year_cols:
                    w_sum = df_mgr.loc[mask(df_mgr, white_pattern), c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    b_sum = df_mgr.loc[mask(df_mgr, blue_pattern), c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    total = df_mgr[c].sum(skipna=True) if (df_mgr is not None and c in df_mgr.columns) else 0
                    trend.append({'연도': str(int(re.search(r'\d{4}', str(c)).group(0))) if re.search(r'\d{4}', str(c)) else str(c),
                                  '화이트합계': float(w_sum or 0),
                                  '블루합계': float(b_sum or 0),
                                  '총합계': float(total or 0)})

                trend_df = pd.DataFrame(trend)

                latest_col = year_cols[-1]
                white_mask_mgr = mask(df_mgr, white_pattern) if (df_mgr is not None and latest_col in df_mgr.columns) else pd.Series([False])
                white_mask_nom = mask(df_nomgr, white_pattern) if (df_nomgr is not None and latest_col in df_nomgr.columns) else pd.Series([False])
                blue_mask_mgr = mask(df_mgr, blue_pattern) if (df_mgr is not None and latest_col in df_mgr.columns) else pd.Series([False])

                white_all = df_mgr.loc[white_mask_mgr, latest_col].mean() if (df_mgr is not None and latest_col in df_mgr.columns) else np.nan
                white_no_mgr = df_nomgr.loc[white_mask_nom, latest_col].mean() if (df_nomgr is not None and latest_col in df_nomgr.columns) else np.nan
                blue_avg = df_mgr.loc[blue_mask_mgr, latest_col].mean() if (df_mgr is not None and latest_col in df_mgr.columns) else np.nan

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("화이트칼라 평균(관리자 포함)", f"{white_all:,.0f}천원/월" if not np.isnan(white_all) else "데이터 없음")
                c2.metric("화이트칼라 평균(관리자 제외)", f"{white_no_mgr:,.0f}천원/월" if not np.isnan(white_no_mgr) else "데이터 없음")
                c3.metric("블루칼라 평균", f"{blue_avg:,.0f}천원/월" if not np.isnan(blue_avg) else "데이터 없음")
                if not np.isnan(white_no_mgr) and not np.isnan(blue_avg):
                    gap = white_no_mgr - blue_avg
                    c4.metric("임금 격차(관리자 제외)", f"{gap:,.0f}천원", f"{(gap/blue_avg*100):.1f}%")
                else:
                    c4.metric("임금 격차(관리자 제외)", "데이터 없음")

                st.markdown("---")
                st.markdown(f"**요약 (한 문장)**: {int(latest_col) if re.search(r'\\d{4}', str(latest_col)) else latest_col}년 기준, 화이트칼라 평균은 **{'' if np.isnan(white_all) else f'{white_all:,.0f}천원/월'}**이며, 블루칼라 평균은 **{'' if np.isnan(blue_avg) else f'{blue_avg:,.0f}천원/월'}**입니다.")
                st.caption("데이터 단위: 천원/월 · 출처: 업로드된 CSV · 전처리: 쉼표·단위 제거")

                st.markdown("#### 연도별 합계 추이 (화이트 vs 블루)")
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=trend_df['연도'], y=trend_df['화이트합계'], mode='lines+markers', name='화이트칼라', line=dict(color=CW)))
                fig_line.add_trace(go.Scatter(x=trend_df['연도'], y=trend_df['블루합계'], mode='lines+markers', name='블루칼라', line=dict(color=CB)))
                fig_line.update_layout(**LAYOUT, xaxis_title='연도', yaxis_title='월임금 합계 (단위: 천원)', height=420)
                st.plotly_chart(fig_line, use_container_width=True)

                st.markdown("#### 연도별 비교 (그룹형 막대)")
                bar_df = trend_df.melt(id_vars=['연도'], value_vars=['화이트합계','블루합계'], var_name='직군', value_name='값')
                bar_df['직군'] = bar_df['직군'].map({'화이트합계':'화이트칼라','블루합계':'블루칼라'})
                fig_bar = px.bar(bar_df, x='연도', y='값', color='직군', barmode='group', color_discrete_map={'화이트칼라':CW,'블루칼라':CB})
                fig_bar.update_layout(**LAYOUT, yaxis_title='월임금 합계 (천원)', height=420)
                st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown(f"#### 직종별 임금 분포 — {str(latest_col)}")
                if df_mgr is not None and latest_col in df_mgr.columns:
                    tmp = df_mgr[[job_col, latest_col]].copy()
                    tmp.columns = ['직종','월임금']
                    tmp['월임금'] = pd.to_numeric(tmp['월임금'], errors='coerce')
                    tmp = tmp.dropna(subset=['월임금'])
                    if not tmp.empty:
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

                st.markdown("#### 연도별 요약 표 (단위: 천원)")
                avg_rows = []
                for c in year_cols:
                    w = df_mgr.loc[mask(df_mgr, white_pattern), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                    b = df_mgr.loc[mask(df_mgr, blue_pattern), c].mean() if (df_mgr is not None and c in df_mgr.columns) else np.nan
                    avg_rows.append({'연도': str(int(re.search(r'\d{4}', str(c)).group(0))) if re.search(r'\d{4}', str(c)) else str(c),
                                     '화이트평균(천원)': w, '블루평균(천원)': b})
                avg_df = pd.DataFrame(avg_rows).set_index('연도')
                st.dataframe(avg_df.style.format("{:,.0f}"))

                insight("발표용: 슬라이드에는 '한 줄 요약'과 '핵심 수치'만 크게 보여주고, 세부 차트는 보조로 사용하세요.", 'green')

# -------------------------
# 7. 결론
# -------------------------
elif page == "📝 결론":
    st.title("📝 결론 및 시사점")
    st.markdown("#### 요약")
    st.write("- 화이트칼라와 블루칼라의 분포와 임금 차이를 연령·성별·지역 관점에서 분석했습니다.")
    st.write("- 관리자 포함 여부가 평균 임금에 큰 영향을 미칩니다.")
    st.markdown("#### 시사점")
    st.write("- 중간임금층 강화 정책 필요성; 지역별·성별 맞춤형 일자리 정책 고려.")
    insight("데이터 출처와 전처리(단위, 결측치)를 발표자료에 명확히 표기하세요.", 'green')

else:
    st.info("사이드바에서 페이지를 선택하세요.")
