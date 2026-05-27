import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="대한민국 인구 대시보드",
    page_icon="🏙️",
    layout="wide"
)

# ── 스타일 ──────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
    }
    .metric-label { color: #a6adc8; font-size: 0.8rem; margin-bottom: 4px; }
    .metric-value { color: #cdd6f4; font-size: 2rem; font-weight: 700; }
    .metric-delta { font-size: 0.85rem; margin-top: 4px; }
    .delta-down { color: #f38ba8; }
    .delta-up   { color: #a6e3a1; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_csv(
        "행정구역_시군구_별__성별_인구수_20260518155224.csv",
        encoding="euc-kr",
        header=None
    )

    # 헤더 정리
    months = ["2026.02", "2026.03", "2026.04"]
    cols = ["지역"]
    for m in months:
        cols += [f"{m}_총인구", f"{m}_남자", f"{m}_여자"]
    df_raw.columns = cols
    df_raw = df_raw.iloc[2:].reset_index(drop=True)  # 헤더 행 제거

    # 숫자 변환
    for c in cols[1:]:
        df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")

    return df_raw

df = load_data()

# 전국 행 분리
전국 = df[df["지역"] == "전국"].iloc[0]
지역df = df[df["지역"] != "전국"].copy()

# ── 사이드바 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✏️ 설정")
    월_선택 = st.selectbox("📅 월 선택", ["2026.02", "2026.03", "2026.04"])
    성별_선택 = st.radio("👤 성별 선택", ["전체", "남자", "여자"])

    st.markdown("---")
    지역_선택 = st.selectbox(
        "📍 행정구역 선택 (꺾은선 그래프)",
        ["전국"] + list(지역df["지역"].unique())
    )

# ── 컬럼명 결정 ──────────────────────────────────────────
성별_col = {
    "전체": f"{월_선택}_총인구",
    "남자":  f"{월_선택}_남자",
    "여자":  f"{월_선택}_여자",
}[성별_선택]

# 이전 월 계산
prev_월 = {"2026.02": None, "2026.03": "2026.02", "2026.04": "2026.03"}[월_선택]

# ── 타이틀 ──────────────────────────────────────────────
st.title("🏙️ 대한민국 인구 대시보드")

# ── 요약 지표 ────────────────────────────────────────────
st.markdown("### 📌 인구 요약 지표")
col1, col2 = st.columns(2)

총인구 = int(전국[성별_col])
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{월_선택} 총 인구수</div>
        <div class="metric-value">{총인구/1e6:.2f} M</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if prev_월:
        prev_col = 성별_col.replace(월_선택, prev_월)
        prev_인구 = int(전국[prev_col])
        차이 = 총인구 - prev_인구
        방향 = "↓" if 차이 < 0 else "↑"
        cls = "delta-down" if 차이 < 0 else "delta-up"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">전월 대비 증감</div>
            <div class="metric-value">
                <span class="{cls}">{방향} {abs(차이)/1e3:.1f} K</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">전월 대비 증감</div>
            <div class="metric-value" style="color:#585b70;">데이터 없음</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 차트 영역 ────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

# 지역별 막대그래프
with chart_col1:
    st.markdown(f"#### 📊 {월_선택} 지역별 인구수")
    bar_df = 지역df[["지역", 성별_col]].sort_values(성별_col, ascending=True)
    fig_bar = px.bar(
        bar_df, x=성별_col, y="지역",
        orientation="h",
        color=성별_col,
        color_continuous_scale="Blues",
        labels={성별_col: "인구수", "지역": ""},
    )
    fig_bar.update_layout(
        plot_bgcolor="#1e1e2e",
        paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        coloraxis_showscale=True,
        margin=dict(l=10, r=10, t=10, b=30),
        height=480,
    )
    fig_bar.update_xaxes(gridcolor="#313244")
    fig_bar.update_yaxes(gridcolor="#313244")
    st.plotly_chart(fig_bar, use_container_width=True)

# 월별 꺾은선 그래프
with chart_col2:
    st.markdown(f"#### 📈 {지역_선택} 월별 인구 변화")
    if 지역_선택 == "전국":
        row = 전국
    else:
        row = 지역df[지역df["지역"] == 지역_선택].iloc[0]

    months = ["2026.02", "2026.03", "2026.04"]
    col_suffix = {"전체": "_총인구", "남자": "_남자", "여자": "_여자"}[성별_선택]
    values = [int(row[f"{m}{col_suffix}"]) for m in months]

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=months, y=values,
        mode="lines+markers",
        line=dict(color="#89b4fa", width=2),
        marker=dict(size=7, color="#89b4fa"),
    ))
    fig_line.update_layout(
        plot_bgcolor="#1e1e2e",
        paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        margin=dict(l=10, r=10, t=10, b=30),
        height=480,
        xaxis=dict(gridcolor="#313244", title="월"),
        yaxis=dict(gridcolor="#313244", title="인구수"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ── 데이터 테이블 ─────────────────────────────────────────
st.markdown("#### 📋 선택 조건 데이터 테이블")
table_df = 지역df[["지역", 성별_col]].copy()
table_df.columns = ["행정구역", "인구수"]
table_df["월"] = 월_선택
table_df["성별"] = 성별_선택
table_df = table_df.reset_index(drop=True)
st.dataframe(table_df, use_container_width=True, height=300)


