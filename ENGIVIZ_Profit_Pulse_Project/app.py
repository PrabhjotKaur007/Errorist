import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Profit Pulse | ENGIVIZ 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp {
        background: #070b14;
        color: #eef2ff;
    }
    [data-testid="stSidebar"] {
        background: #0c1220;
        border-right: 1px solid #1f2a44;
    }
    .hero {
        padding: 28px 30px;
        border: 1px solid #273451;
        border-radius: 20px;
        background: linear-gradient(135deg, #111a2d 0%, #0b1220 55%, #10182b 100%);
        margin-bottom: 18px;
    }
    .hero h1 {
        font-size: 42px;
        margin: 0 0 6px 0;
        letter-spacing: -1px;
    }
    .hero p {
        color: #aab7d4;
        font-size: 16px;
        margin: 0;
    }
    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin: 18px 0 4px 0;
    }
    .section-sub {
        color: #8997b5;
        margin-bottom: 12px;
    }
    .insight {
        padding: 16px 18px;
        border-radius: 14px;
        background: #0e1728;
        border: 1px solid #263653;
        margin-bottom: 10px;
    }
    .insight b {
        color: #f1f5ff;
    }
    .small-note {
        color: #8492ad;
        font-size: 13px;
    }
    div[data-testid="stMetric"] {
        background: #0d1525;
        border: 1px solid #25334f;
        padding: 15px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Year"] = df["Order Date"].dt.year
    df["Profit Margin"] = (df["Profit"] / df["Sales"].replace(0, pd.NA)) * 100
    return df


df = load_data()

# ---------- Sidebar ----------
st.sidebar.markdown("## 🎛️ Explore the data")
st.sidebar.caption("Use the filters to make every chart answer a different question.")

years = sorted(df["Year"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
regions = sorted(df["Region"].dropna().unique().tolist())
segments = sorted(df["Segment"].dropna().unique().tolist())
ship_modes = sorted(df["Ship Mode"].dropna().unique().tolist())

selected_years = st.sidebar.multiselect("Year", years, default=years)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_segments = st.sidebar.multiselect("Segment", segments, default=segments)
selected_ship_modes = st.sidebar.multiselect("Ship Mode", ship_modes, default=ship_modes)

filtered = df[
    df["Year"].isin(selected_years)
    & df["Category"].isin(selected_categories)
    & df["Region"].isin(selected_regions)
    & df["Segment"].isin(selected_segments)
    & df["Ship Mode"].isin(selected_ship_modes)
].copy()

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>📊 PROFIT PULSE</h1>
    <p>Where is Superstore creating value — and where is profit quietly disappearing?</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No records match the current filters. Please broaden the filters.")
    st.stop()

# ---------- KPIs ----------
sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
margin = (profit / sales * 100) if sales else 0
orders = filtered["Order ID"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"${sales:,.0f}")
k2.metric("Total Profit", f"${profit:,.0f}")
k3.metric("Profit Margin", f"{margin:.1f}%")
k4.metric("Unique Orders", f"{orders:,}")

st.markdown(
    f'<p class="small-note">Showing {len(filtered):,} order-line records after filters.</p>',
    unsafe_allow_html=True
)

# ---------- Q1 ----------
st.markdown('<div class="section-title">1. Product Profitability</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Which sub-categories create the strongest margins — and which ones destroy value?</div>',
    unsafe_allow_html=True
)

sub = (
    filtered.groupby("Sub-Category", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
)
sub["Profit Margin"] = sub["Profit"] / sub["Sales"] * 100
sub = sub.sort_values("Profit Margin")

fig1 = px.bar(
    sub,
    x="Profit Margin",
    y="Sub-Category",
    orientation="h",
    hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "Quantity": ":,", "Profit Margin": ":.1f"},
    labels={"Profit Margin": "Profit margin (%)", "Sub-Category": ""},
    title="Profit margin by sub-category",
)
fig1.add_vline(x=0, line_width=1)
fig1.update_layout(
    height=470,
    margin=dict(l=10, r=10, t=55, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbe5ff"),
    title_font_size=18,
)
st.plotly_chart(fig1, use_container_width=True)

best = sub.loc[sub["Profit Margin"].idxmax()]
worst = sub.loc[sub["Profit Margin"].idxmin()]

c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f'<div class="insight">🏆 <b>Highest margin:</b> {best["Sub-Category"]} '
        f'({best["Profit Margin"]:.1f}%)</div>',
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f'<div class="insight">⚠️ <b>Lowest margin:</b> {worst["Sub-Category"]} '
        f'({worst["Profit Margin"]:.1f}%)</div>',
        unsafe_allow_html=True
    )

# ---------- Q2 ----------
st.markdown('<div class="section-title">2. Geographic Profit Leaks</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">The broad regions may look healthy. Drill down to states to find where losses actually occur.</div>',
    unsafe_allow_html=True
)

geo = (
    filtered.groupby(["State", "Region"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
)
geo["Profit Margin"] = geo["Profit"] / geo["Sales"] * 100

loss_states = geo[geo["Profit"] < 0].sort_values("Profit").head(12)

fig2 = px.bar(
    loss_states.sort_values("Profit"),
    x="Profit",
    y="State",
    orientation="h",
    hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "Profit Margin": ":.1f"},
    labels={"Profit": "Total profit ($)", "State": ""},
    title="Largest state-level profit losses",
)
fig2.add_vline(x=0, line_width=1)
fig2.update_layout(
    height=430,
    margin=dict(l=10, r=10, t=55, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbe5ff"),
    title_font_size=18,
)
st.plotly_chart(fig2, use_container_width=True)

region_geo = (
    filtered.groupby("Region", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
)
region_geo["Profit Margin"] = region_geo["Profit"] / region_geo["Sales"] * 100

region_col, state_col = st.columns(2)

with region_col:
    fig3 = px.bar(
        region_geo.sort_values("Profit"),
        x="Region",
        y="Profit",
        hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "Profit Margin": ":.1f"},
        labels={"Profit": "Profit ($)", "Region": ""},
        title="Region-level profitability",
    )
    fig3.add_hline(y=0, line_width=1)
    fig3.update_layout(
        height=350, margin=dict(l=10, r=10, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe5ff"), title_font_size=18,
    )
    st.plotly_chart(fig3, use_container_width=True)

with state_col:
    worst_states = geo.sort_values("Profit").head(5)
    st.markdown("**Five biggest state-level profit leaks**")
    display_states = worst_states[["State", "Region", "Sales", "Profit", "Profit Margin"]].copy()
    display_states["Sales"] = display_states["Sales"].map(lambda x: f"${x:,.0f}")
    display_states["Profit"] = display_states["Profit"].map(lambda x: f"${x:,.0f}")
    display_states["Profit Margin"] = display_states["Profit Margin"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_states, use_container_width=True, hide_index=True)

# ---------- Q3 ----------
st.markdown('<div class="section-title">3. Shipping Mode Impact</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Compare sales volume, profit, margin, and delivery time across shipping modes.</div>',
    unsafe_allow_html=True
)

ship = (
    filtered.groupby("Ship Mode", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        AvgShipDays=("Ship Days", "mean"),
    )
)
ship["Profit Margin"] = ship["Profit"] / ship["Sales"] * 100

s1, s2 = st.columns(2)

with s1:
    fig4 = px.bar(
        ship.sort_values("Sales", ascending=False),
        x="Ship Mode",
        y="Sales",
        hover_data={"Profit": ":$,.0f", "Orders": ":,", "Profit Margin": ":.1f"},
        labels={"Sales": "Sales ($)", "Ship Mode": ""},
        title="Sales volume by shipping mode",
    )
    fig4.update_layout(
        height=400, margin=dict(l=10, r=10, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe5ff"), title_font_size=18,
    )
    st.plotly_chart(fig4, use_container_width=True)

with s2:
    fig5 = px.scatter(
        ship,
        x="AvgShipDays",
        y="Profit Margin",
        size="Sales",
        text="Ship Mode",
        hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "Orders": ":,"},
        labels={
            "AvgShipDays": "Average shipping time (days)",
            "Profit Margin": "Profit margin (%)",
        },
        title="Shipping speed vs. profit margin",
    )
    fig5.update_traces(textposition="top center")
    fig5.update_layout(
        height=400, margin=dict(l=10, r=10, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe5ff"), title_font_size=18,
    )
    st.plotly_chart(fig5, use_container_width=True)

# ---------- Supporting insight ----------
st.markdown('<div class="section-title">4. Profit Leak Detector</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">A supporting analysis: how strongly is discounting associated with profit erosion?</div>',
    unsafe_allow_html=True
)

disc = filtered.copy()
disc["Discount Band"] = pd.cut(
    disc["Discount"],
    bins=[-0.001, 0, 0.1, 0.2, 0.3, 0.4, 1.0],
    labels=["0%", "1–10%", "11–20%", "21–30%", "31–40%", "40%+"],
)
discount = (
    disc.groupby("Discount Band", observed=False, as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
)
discount["Profit Margin"] = discount["Profit"] / discount["Sales"] * 100

fig6 = px.bar(
    discount,
    x="Discount Band",
    y="Profit Margin",
    hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "Orders": ":,"},
    labels={"Profit Margin": "Profit margin (%)", "Discount Band": "Discount"},
    title="Profit margin falls as discount depth increases",
)
fig6.add_hline(y=0, line_width=1)
fig6.update_layout(
    height=400,
    margin=dict(l=10, r=10, t=55, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbe5ff"),
    title_font_size=18,
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown(
    '<div class="insight">💡 <b>Story:</b> Strong sales do not automatically mean strong profitability. '
    'The dashboard connects product mix, geographic losses, shipping choices, and discount depth to reveal where value is created and where it leaks away.</div>',
    unsafe_allow_html=True
)

# ---------- Footer ----------
st.markdown(
    '<p class="small-note">ENGIVIZ 2026 • Profit Pulse • Built with Python, Pandas, Plotly and Streamlit</p>',
    unsafe_allow_html=True
)
