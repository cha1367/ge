import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="쉬었음 청년 사회 확산 대시보드",
    page_icon="📊",
    layout="wide"
)

# ── 스타일 ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .main { background-color: #0e1117; }

    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 100%);
        border-left: 4px solid #ff4b4b;
        padding: 2rem 2.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
    }
    .hero p {
        font-size: 1rem;
        color: #9ca3af;
        margin: 0;
        line-height: 1.7;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 2.5rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2d3748;
    }
    .section-badge {
        background: #ff4b4b;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }

    .connector {
        background: #1a1f2e;
        border-left: 3px solid #4a6fa5;
        padding: 0.8rem 1.2rem;
        border-radius: 0 6px 6px 0;
        margin: 1rem 0;
        color: #9ca3af;
        font-size: 0.9rem;
        font-style: italic;
    }

    .metric-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #ff4b4b;
    }
    .metric-card .sub {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }

    .note {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.5rem;
        font-style: italic;
    }

    .stPlotlyChart { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 ───────────────────────────────────────────────
years = list(range(2015, 2026))

resting_youth = [273, 245, 270, 283, 332, 415, 393, 362, 371, 389, 408]  # 천명
inactive_total = [2277, 2234, 2297, 2303, 2328, 2503, 2443, 2245, 2163, 2085, 2048]  # 천명
youth_population = [6699, 6758, 6811, 6824, 6810, 6806, 6656, 6417, 6197, 5956, 5682]  # 천명

AVG_INCOME = 271     # 만원 (20대 평균, 2024 통계청)
CONSUMPTION = 0.69   # 평균소비성향 (가계동향조사)
PENSION_RATE = 0.09  # 국민연금 보험료율

df = pd.DataFrame({
    "연도": years,
    "쉬었음_청년": resting_youth,
    "전체_비경활": inactive_total,
    "청년_인구": youth_population,
})

df["쉬었음_비율"] = (df["쉬었음_청년"] / df["전체_비경활"] * 100).round(1)
df["쉬었음_증가율"] = df["쉬었음_청년"].pct_change() * 100
df["비경활_증가율"] = df["전체_비경활"].pct_change() * 100
df["소비공백_억원"] = (df["쉬었음_청년"] * 1000 * AVG_INCOME * 10000 * CONSUMPTION / 1e8).round(0)
df["연금손실_억원"] = (df["쉬었음_청년"] * 1000 * AVG_INCOME * 10000 * PENSION_RATE / 1e8).round(0)
df["내수공백률"] = (df["쉬었음_청년"] / df["청년_인구"] * 100).round(2)
df["누적_연금손실"] = df["연금손실_억원"].cumsum()

PLOT_BG = "#0e1117"
PAPER_BG = "#0e1117"
GRID = "#1f2937"
TEXT = "#e0e0e0"
RED = "#ff4b4b"
BLUE = "#4a9eff"

def base_layout(title="", yaxis_title="", xaxis_title="연도"):
    return dict(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT, family="Noto Sans KR"),
        title=dict(text=title, font=dict(size=14, color=TEXT)),
        xaxis=dict(
            title=xaxis_title,
            gridcolor=GRID,
            color=TEXT,
            tickvals=years,
            ticktext=[str(y) for y in years],
        ),
        yaxis=dict(title=yaxis_title, gridcolor=GRID, color=TEXT),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        hovermode="x unified",
    )


# ══════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>쉬었음 청년, 어디까지 퍼지나?</h1>
    <p>단순히 쉬고 있는 청년의 수가 늘었다는 사실을 넘어,<br>
    그 증가가 <strong>노동시장 이탈 → 소비 공백 → 재정 기반 약화</strong>로
    어떻게 확산되는지 파생지표로 보여줍니다.</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 1단계. 문제 규모
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-badge">STEP 1</span>
    <span class="section-title">문제 규모 확인</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">2025년 쉬었음 청년</div>
        <div class="value">{resting_youth[-1]}천명</div>
        <div class="sub">20~29세 기준</div>
    </div>""", unsafe_allow_html=True)
with col2:
    diff = resting_youth[-1] - resting_youth[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">2015년 대비 증가</div>
        <div class="value">+{diff}천명</div>
        <div class="sub">2015년 {resting_youth[0]}천명 → 2025년 {resting_youth[-1]}천명</div>
    </div>""", unsafe_allow_html=True)
with col3:
    peak = max(resting_youth)
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">역대 최고 (2020년)</div>
        <div class="value">{peak}천명</div>
        <div class="sub">코로나19 영향</div>
    </div>""", unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=years, y=resting_youth,
    marker_color=[RED if y >= 2020 else "#4a6fa5" for y in years],
    name="쉬었음 청년 수",
    hovertemplate="%{x}년: %{y}천명<extra></extra>"
))
fig1.add_trace(go.Scatter(
    x=years, y=resting_youth,
    mode="lines+markers",
    line=dict(color=RED, width=2, dash="dot"),
    marker=dict(size=6),
    name="추이",
    hovertemplate="%{x}년: %{y}천명<extra></extra>"
))
fig1.update_layout(**base_layout("20~29세 쉬었음 청년 수 추이 (2015~2025)", "천명"))
st.plotly_chart(fig1, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 2단계. 노동시장
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="connector">
    ▼ 규모가 확인됐다면, 이 증가가 노동시장 전체에서 어떤 의미인지 살펴봅니다.
</div>
<div class="section-header">
    <span class="section-badge">STEP 2</span>
    <span class="section-title">노동시장 관점 — 청년 이탈이 가속되고 있는가?</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 청년 이탈 가속도 지수", "📊 청년 비경활 중 쉬었음 비율"])

with tab1:
    st.caption("가설: 쉬었음 청년 증가 속도가 전체 비경제활동인구 증가 속도보다 빠르다")
    df_rate = df.dropna(subset=["쉬었음_증가율"])
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_rate["연도"], y=df_rate["쉬었음_증가율"],
        mode="lines+markers", name="쉬었음 청년 증가율",
        line=dict(color=RED, width=2.5),
        marker=dict(size=7),
        hovertemplate="%{x}년: %{y:.1f}%<extra></extra>"
    ))
    fig2.add_trace(go.Scatter(
        x=df_rate["연도"], y=df_rate["비경활_증가율"],
        mode="lines+markers", name="전체 비경활 증가율",
        line=dict(color=BLUE, width=2.5, dash="dash"),
        marker=dict(size=7),
        hovertemplate="%{x}년: %{y:.1f}%<extra></extra>"
    ))
    fig2.add_hline(y=0, line_dash="dot", line_color=GRID)
    fig2.update_layout(**base_layout("쉬었음 청년 vs 전체 비경활 증가율 비교", "증가율 (%)"))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('<p class="note">※ 전년 대비 증가율 기준 / 출처: KOSIS 경제활동인구조사</p>', unsafe_allow_html=True)

with tab2:
    st.caption("가설: 비경제활동인구 중 쉬었음 청년 비중이 증가하고 있다")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["연도"], y=df["쉬었음_비율"],
        mode="lines+markers+text",
        line=dict(color=RED, width=2.5),
        marker=dict(size=8),
        text=[f"{v}%" for v in df["쉬었음_비율"]],
        textposition="top center",
        textfont=dict(size=9, color=TEXT),
        hovertemplate="%{x}년: %{y}%<extra></extra>"
    ))
    fig3.update_layout(**base_layout("비경활 청년 중 '쉬었음' 비율 추이", "비율 (%)"))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('<p class="note">※ 쉬었음 청년 수 ÷ 전체 비경제활동인구(20~29세) × 100 / 출처: KOSIS</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 3단계. 경제
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="connector">
    ▼ 노동시장을 이탈한 청년들은 소득이 없습니다. 그 공백이 경제에 어떻게 나타날까요?
</div>
<div class="section-header">
    <span class="section-badge">STEP 3</span>
    <span class="section-title">경제 관점 — 내수 기반이 약화되고 있는가?</span>
</div>
""", unsafe_allow_html=True)

st.caption("가설: 쉬었음 청년 증가는 내수 기반을 약화시킨다")

latest_consumption = int(df["소비공백_억원"].iloc[-1])
st.markdown(f"""
<div class="metric-card" style="max-width:400px; margin-bottom:1rem;">
    <div class="label">2025년 청년 소비 공백 추정액</div>
    <div class="value">{latest_consumption:,}억원</div>
    <div class="sub">약 {latest_consumption/10000:.1f}조원 규모</div>
</div>""", unsafe_allow_html=True)

fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=df["연도"], y=df["소비공백_억원"],
    marker_color=[RED if y >= 2020 else "#4a6fa5" for y in years],
    name="소비 공백 추정액",
    hovertemplate="%{x}년: %{y:,}억원<extra></extra>"
))
fig4.update_layout(**base_layout("청년 소비 공백 추정액 (2015~2025)", "억원"))
st.plotly_chart(fig4, use_container_width=True)
st.markdown("""
<p class="note">
※ 추정값 · 실제 소비 감소액이 아닌 잠재 소비 미실현 추정치<br>
※ 수식: 쉬었음 청년 수 × 271만원(20대 평균소득, 통계청 2024) × 0.69(평균소비성향, 가계동향조사)<br>
※ 청년 전용 소비성향 통계 부재로 전체 평균 대리변수 사용
</p>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("보조지표: 청년 내수 기여 공백률 (20~29세 인구 대비 쉬었음 청년 비율)")
fig4b = go.Figure()
fig4b.add_trace(go.Scatter(
    x=df["연도"], y=df["내수공백률"],
    mode="lines+markers+text",
    line=dict(color="#f59e0b", width=2.5),
    marker=dict(size=8),
    text=[f"{v}%" for v in df["내수공백률"]],
    textposition="top center",
    textfont=dict(size=9, color=TEXT),
    hovertemplate="%{x}년: %{y}%<extra></extra>"
))
fig4b.update_layout(**base_layout("청년 내수 기여 공백률 (2015~2025)", "비율 (%)"))
st.plotly_chart(fig4b, use_container_width=True)
st.markdown("""
<p class="note">
※ 수식: 쉬었음 청년 수 ÷ 20~29세 전체 인구 × 100<br>
※ 출처: KOSIS 경제활동인구조사, 주민등록인구통계<br>
※ 20~29세 청년 인구 중 소비에 기여하지 못하는 비율을 나타내는 추정 지표
</p>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 4단계. 재정
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="connector">
    ▼ 소비 공백은 지금의 문제입니다. 재정 관점에서는 미래까지 영향이 이어집니다.
</div>
<div class="section-header">
    <span class="section-badge">STEP 4</span>
    <span class="section-title">재정 관점 — 국민연금 납부 기반이 약화되고 있는가?</span>
</div>
""", unsafe_allow_html=True)

st.caption("가설: 쉬었음 청년 증가는 국민연금 납부 기반을 약화시킨다")

latest_pension = int(df["연금손실_억원"].iloc[-1])
cumulative = int(df["연금손실_억원"].sum())
st.markdown(f"""
<div style="display:flex; gap:1rem; margin-bottom:1rem;">
    <div class="metric-card" style="flex:1;">
        <div class="label">2025년 잠재 연금 납부 손실</div>
        <div class="value">{latest_pension:,}억원</div>
        <div class="sub">연간 기준</div>
    </div>
    <div class="metric-card" style="flex:1;">
        <div class="label">2015~2025 누적 손실 추정</div>
        <div class="value">{cumulative:,}억원</div>
        <div class="sub">약 {cumulative/10000:.1f}조원</div>
    </div>
</div>""", unsafe_allow_html=True)

fig5 = go.Figure()
fig5.add_trace(go.Scatter(
    x=df["연도"], y=df["연금손실_억원"],
    mode="lines+markers",
    fill="tozeroy",
    fillcolor="rgba(255,75,75,0.15)",
    line=dict(color=RED, width=2.5),
    marker=dict(size=7),
    name="잠재 연금 납부 손실",
    hovertemplate="%{x}년: %{y:,}억원<extra></extra>"
))
fig5.update_layout(**base_layout("잠재 국민연금 납부 손실 추정액 (2015~2025)", "억원"))
st.plotly_chart(fig5, use_container_width=True)
st.markdown("""
<p class="note">
※ 추정값 · 실제 세입 감소액이 아닌 잠재 미유입 추정치<br>
※ 수식: 쉬었음 청년 수 × 271만원 × 9%(국민연금법 보험료율, 고정값)<br>
※ 국민연금 보험료는 실제 가입 여부 미반영 단순 역산치<br>
※ 2024년 기준 평균소득 고정값 적용 보수적 추정치
</p>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("보조지표: 2015~2025 누적 잠재 연금 납부 손실 (추정)")
fig5b = go.Figure()
fig5b.add_trace(go.Bar(
    x=df["연도"], y=df["연금손실_억원"],
    name="당해 손실",
    marker_color="rgba(255,75,75,0.5)",
    hovertemplate="%{x}년 당해: %{y:,}억원<extra></extra>"
))
fig5b.add_trace(go.Scatter(
    x=df["연도"], y=df["누적_연금손실"],
    mode="lines+markers",
    name="누적 손실",
    line=dict(color=RED, width=2.5),
    marker=dict(size=8),
    yaxis="y2",
    hovertemplate="%{x}년 누적: %{y:,}억원<extra></extra>"
))
fig5b.update_layout(
    **base_layout("누적 잠재 국민연금 납부 손실 (2015~2025)", "당해 손실 (억원)"),
    yaxis2=dict(
        title="누적 손실 (억원)",
        overlaying="y",
        side="right",
        gridcolor=GRID,
        color=TEXT,
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
)
st.plotly_chart(fig5b, use_container_width=True)
st.markdown(f"""
<p class="note">
※ 2015~2025년 누적 잠재 손실 합계: <strong style="color:#ff4b4b;">{int(df["누적_연금손실"].iloc[-1]):,}억원 (약 {int(df["누적_연금손실"].iloc[-1])/10000:.1f}조원)</strong><br>
※ 추정값 · 2024년 기준 평균소득 271만원 고정 적용
</p>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 5단계. 정책적 시사점 & 대책방안
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="connector">
    ▼ 데이터가 보여주는 확산 구조를 바탕으로, 어떤 개입이 필요한지 살펴봅니다.
</div>
<div class="section-header">
    <span class="section-badge">STEP 5</span>
    <span class="section-title">정책적 시사점 — 무엇을 해야 하는가?</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card" style="text-align:left; height:100%;">
        <div class="label">🔧 노동시장 관점</div>
        <div style="font-size:1rem; font-weight:600; color:#ffffff; margin:0.8rem 0 0.5rem 0;">
            원인별 맞춤 조기 개입
        </div>
        <div style="font-size:0.85rem; color:#9ca3af; line-height:1.8;">
            쉬었음 청년이 장기 비경활 상태로 고착되기 전<br>
            조기 개입이 핵심입니다.<br><br>
            • 구직 포기 청년 → 취업동기 회복 프로그램<br>
            • 미스매치 청년 → 직업훈련 + 중소기업 인턴 연계<br>
            • 목표: 노동시장 재진입 가속화
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="text-align:left; height:100%;">
        <div class="label">💰 경제 관점</div>
        <div style="font-size:1rem; font-weight:600; color:#ffffff; margin:0.8rem 0 0.5rem 0;">
            소비 공백 완화 지원
        </div>
        <div style="font-size:0.85rem; color:#9ca3af; line-height:1.8;">
            연간 추정 소비 공백 <span style="color:#ff4b4b; font-weight:600;">{int(df['소비공백_억원'].iloc[-1]):,}억원</span> 규모.<br>
            취업 청년의 소비 여력을 높이는 방향으로<br>
            내수 기반을 보완할 수 있습니다.<br><br>
            • 청년 일경험 확대 → 소득 창출 기회 제공<br>
            • 취업 연계형 지원금 → 소비로 이어지는 구조<br>
            • 목표: 내수 기반 회복
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="text-align:left; height:100%;">
        <div class="label">🏛️ 재정 관점</div>
        <div style="font-size:1rem; font-weight:600; color:#ffffff; margin:0.8rem 0 0.5rem 0;">
            사회보험 진입 기반 강화
        </div>
        <div style="font-size:0.85rem; color:#9ca3af; line-height:1.8;">
            연간 추정 연금 납부 손실 <span style="color:#ff4b4b; font-weight:600;">{int(df['연금손실_억원'].iloc[-1]):,}억원</span>.<br>
            취업 연계로 사회보험 가입을 늘리는 것이<br>
            재정 기반 회복의 핵심입니다.<br><br>
            • 국민연금 지역가입자 보험료 지원 확대<br>
            • 취업 시 사회보험 자동 연계 간소화<br>
            • 목표: 재정 기반 약화 방지
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 핵심 메시지
# ══════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="background:#1a1f2e; border-radius:10px; padding:2rem; text-align:center; margin-top:1rem;">
    <p style="color:#9ca3af; font-size:0.85rem; margin-bottom:0.5rem;">핵심 메시지</p>
    <p style="color:#ffffff; font-size:1.15rem; font-weight:600; line-height:1.8; margin:0;">
        쉬었음 청년 증가는 단순한 개인의 비활동 상태가 아닙니다.<br>
        <span style="color:#ff4b4b;">노동시장 이탈 → 소비 공백 → 재정 기반 약화</span>로<br>
        사회 전체에 확산될 수 있는 구조적 문제입니다.
    </p>
    <p style="color:#6b7280; font-size:0.85rem; margin-top:1rem;">
        쉬었음 청년 1명의 노동시장 재진입은<br>
        연간 소비 약 187만원, 연금 납부 약 24만원을 사회로 되돌립니다.
    </p>
</div>
""", unsafe_allow_html=True)

# ── 분석 한계 ─────────────────────────────────────────────
with st.expander("📋 분석 한계 및 주의사항"):
    st.markdown("""
    **[한계 1] 경제·재정 지표는 추정치**
    - 청년 소비 공백 추정액, 잠재 국민연금 납부 손실은 실측값이 아닌 가정 기반 추정치입니다.
    - 실제 손실액과 차이가 있을 수 있으며, 잠재 공백 규모의 근사치로 해석해야 합니다.

    **[한계 2] 고정값 사용으로 인한 단조로운 추이**
    - 평균소득(271만원), 소비성향(0.69), 연금보험료율(9%)이 고정값이므로
      경제·재정 그래프가 쉬었음 청년 수 추이와 유사한 형태를 보입니다.
    - 향후 연령대 세분화 또는 시나리오 분석으로 보완이 필요합니다.

    **[한계 3] 확산 구조는 인과관계가 아닌 가능성**
    - 본 대시보드의 노동시장 → 경제 → 재정 흐름은 직접적 인과관계가 아니라
      확산 가능성을 보여주는 구조적 분석입니다.
    - 모든 지표는 "영향을 줄 수 있음", "확산 가능성" 수준으로 해석해야 합니다.

    **출처**
    - 쉬었음 청년 수, 비경제활동인구: KOSIS 경제활동인구조사
    - 20대 평균소득(271만원): 통계청 2024년 임금근로일자리 소득결과
    - 평균소비성향(69%): 통계청 가계동향조사
    - 국민연금 보험료율(9%): 국민연금법 제88조
    """)

