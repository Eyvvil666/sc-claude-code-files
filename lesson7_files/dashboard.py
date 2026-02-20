"""
E-Commerce Sales Performance Dashboard
"""

import calendar

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from business_metrics import (
    calculate_avg_order_value,
    calculate_category_revenue,
    calculate_delivery_satisfaction,
    calculate_mom_growth,
    calculate_order_count,
    calculate_revenue,
    calculate_state_revenue,
)
from data_loader import (
    add_temporal_features,
    calculate_delivery_speed,
    filter_by_period,
    load_datasets,
    prepare_sales_data,
)

st.set_page_config(
    page_title="E-Commerce Sales Performance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
.kpi-card {
    background: white;
    padding: 1rem 1.2rem;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
    height: 128px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.bottom-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
    height: 168px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.kpi-label, .bottom-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    color: #6b7280;
    letter-spacing: 0.05em;
    margin: 0;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
    line-height: 1.1;
}
.bottom-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
    line-height: 1.1;
}
.kpi-trend, .bottom-trend {
    font-size: 0.82rem;
    margin: 0;
}
.stars {
    font-size: 1.35rem;
    color: #f59e0b;
    margin: 0.25rem 0;
}
/* Remove the default Streamlit card border/shadow around each chart */
[data-testid="stPlotlyChart"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
}
[data-testid="stPlotlyChart"] > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt_compact(v: float) -> str:
    """Format a dollar value as $2M, $1.5M, $300K, $45."""
    if abs(v) >= 1_000_000:
        m = v / 1_000_000
        return f"${m:.1f}M" if m % 1 != 0 else f"${m:.0f}M"
    elif abs(v) >= 1_000:
        k = v / 1_000
        return f"${k:.0f}K"
    else:
        return f"${v:.0f}"


def trend_badge(current, previous, lower_is_better: bool = False) -> str:
    """Return an HTML span with a colored directional trend indicator."""
    if previous is None or pd.isna(previous) or previous == 0:
        return '<span style="color:#6b7280">—</span>'
    if current is None or pd.isna(current):
        return '<span style="color:#6b7280">—</span>'
    pct = (current - previous) / abs(previous) * 100
    positive_outcome = pct < 0 if lower_is_better else pct > 0
    color = "#16a34a" if positive_outcome else "#dc2626"
    arrow = "↑" if pct > 0 else "↓"
    return f'<span style="color:{color}">{arrow} {abs(pct):.2f}%</span>'


def make_y_ticks(max_val: float, n: int = 5) -> tuple:
    """Compute nicely-spaced tick values and compact string labels."""
    import math

    if max_val <= 0:
        return [0], ["$0"]
    raw_step = max_val / (n - 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    nice_step = math.ceil(raw_step / magnitude) * magnitude
    ticks = [i * nice_step for i in range(n)]
    labels = [fmt_compact(t) for t in ticks]
    return ticks, labels


# ── Data Loading (cached) ────────────────────────────────────────────────────

@st.cache_data
def get_base_data():
    datasets = load_datasets("ecommerce_data")
    sales_df = prepare_sales_data(datasets["order_items"], datasets["orders"])
    sales_df = add_temporal_features(sales_df, "order_purchase_timestamp")
    return datasets, sales_df


# ── Month abbreviations ──────────────────────────────────────────────────────
MONTH_ABBRS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ── App entry point ──────────────────────────────────────────────────────────
datasets, sales_df = get_base_data()

delivered = sales_df[sales_df["order_status"] == "delivered"].copy()
available_years = sorted(
    delivered["year"].dropna().astype(int).unique(), reverse=True
)

# ── Header ───────────────────────────────────────────────────────────────────
hdr, _, yr_col, mo_col = st.columns([3, 1, 1, 1])

with hdr:
    st.markdown("## E-Commerce Sales Performance")

with yr_col:
    default_yr_idx = available_years.index(2023) if 2023 in available_years else 0
    analysis_year = st.selectbox("Year", available_years, index=default_yr_idx)

with mo_col:
    month_options = ["All Months"] + MONTH_ABBRS
    selected_month_label = st.selectbox("Month", month_options)
    analysis_month = (
        None
        if selected_month_label == "All Months"
        else MONTH_ABBRS.index(selected_month_label) + 1
    )

comparison_year = analysis_year - 1

# ── Filtering ────────────────────────────────────────────────────────────────
current_df = calculate_delivery_speed(
    filter_by_period(delivered, analysis_year, analysis_month)
)
comparison_df = calculate_delivery_speed(
    filter_by_period(delivered, comparison_year, analysis_month)
)
has_comparison = not comparison_df.empty

# ── KPI Calculations ──────────────────────────────────────────────────────────
revenue = calculate_revenue(current_df)
prev_rev = calculate_revenue(comparison_df) if has_comparison else None

aov = calculate_avg_order_value(current_df)
prev_aov = calculate_avg_order_value(comparison_df) if has_comparison else None

orders = calculate_order_count(current_df)
prev_orders = calculate_order_count(comparison_df) if has_comparison else None

mom_series = calculate_mom_growth(current_df)
avg_mom = mom_series.mean() if not mom_series.dropna().empty else 0.0
mom_color = "#16a34a" if avg_mom > 0 else "#dc2626"
mom_arrow = "↑" if avg_mom > 0 else "↓"

# ── KPI Row ───────────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
    <div class="kpi-card">
        <p class="kpi-label">Total Revenue</p>
        <p class="kpi-value">{fmt_compact(revenue)}</p>
        <p class="kpi-trend">{trend_badge(revenue, prev_rev)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
    <div class="kpi-card">
        <p class="kpi-label">Avg Monthly Growth</p>
        <p class="kpi-value">{avg_mom:+.2f}%</p>
        <p class="kpi-trend"><span style="color:{mom_color}">{mom_arrow}</span></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi3:
    aov_display = fmt_compact(aov) if not pd.isna(aov) else "—"
    st.markdown(
        f"""
    <div class="kpi-card">
        <p class="kpi-label">Avg Order Value</p>
        <p class="kpi-value">{aov_display}</p>
        <p class="kpi-trend">{trend_badge(aov, prev_aov)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
    <div class="kpi-card">
        <p class="kpi-label">Total Orders</p>
        <p class="kpi-value">{orders:,}</p>
        <p class="kpi-trend">{trend_badge(orders, prev_orders)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Chart Row 1 ───────────────────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    cur_monthly = (
        current_df.groupby("month")["price"]
        .sum()
        .reindex(range(1, 13))
        .dropna()
    )
    comp_monthly = (
        comparison_df.groupby("month")["price"]
        .sum()
        .reindex(range(1, 13))
        .dropna()
        if has_comparison
        else pd.Series(dtype=float)
    )

    max_rev = max(
        cur_monthly.max() if not cur_monthly.empty else 0,
        comp_monthly.max() if not comp_monthly.empty else 0,
    )
    yticks, ytick_labels = make_y_ticks(max_rev)

    fig_trend = go.Figure()
    if not cur_monthly.empty:
        fig_trend.add_trace(
            go.Scatter(
                x=[calendar.month_abbr[m] for m in cur_monthly.index],
                y=cur_monthly.values,
                mode="lines+markers",
                name=str(analysis_year),
                line=dict(color="#2C5F8A", width=2.5),
                marker=dict(size=7),
                hovertemplate="%{x}: %{customdata}<extra></extra>",
                customdata=[fmt_compact(v) for v in cur_monthly.values],
            )
        )
    if not comp_monthly.empty:
        fig_trend.add_trace(
            go.Scatter(
                x=[calendar.month_abbr[m] for m in comp_monthly.index],
                y=comp_monthly.values,
                mode="lines+markers",
                name=str(comparison_year),
                line=dict(color="#9CA3AF", width=2, dash="dash"),
                marker=dict(size=6),
                hovertemplate="%{x}: %{customdata}<extra></extra>",
                customdata=[fmt_compact(v) for v in comp_monthly.values],
            )
        )
    fig_trend.update_layout(
        title="Revenue Trend",
        hovermode="x unified",
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0f2f5"),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f0f2f5",
            tickvals=yticks,
            ticktext=ytick_labels,
        ),
        height=350,
        margin=dict(t=50, b=40, l=60, r=20),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

with chart2:
    cat_rev = calculate_category_revenue(current_df, datasets["products"]).head(10)
    cat_rev = cat_rev.iloc[::-1]  # Reverse so highest bar is at the top
    n = len(cat_rev)
    colors = [
        f"rgba(44,95,138,{0.35 + 0.65 * i / max(n - 1, 1):.2f})"
        for i in range(n)
    ]

    x_max = cat_rev.max() if not cat_rev.empty else 1
    xticks, xtick_labels = make_y_ticks(x_max, n=5)

    fig_cat = go.Figure(
        go.Bar(
            y=cat_rev.index,
            x=cat_rev.values,
            orientation="h",
            marker_color=colors,
            text=[fmt_compact(v) for v in cat_rev.values],
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
            textfont=dict(size=11),
        )
    )
    fig_cat.update_layout(
        title="Top 10 Categories",
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="#f0f2f5",
            tickvals=xticks,
            ticktext=xtick_labels,
        ),
        yaxis=dict(showgrid=False),
        height=350,
        margin=dict(t=50, b=40, l=160, r=80),
    )
    st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

# ── Chart Row 2 ───────────────────────────────────────────────────────────────
chart3, chart4 = st.columns(2)

with chart3:
    state_rev = calculate_state_revenue(
        current_df, datasets["orders"], datasets["customers"]
    )

    fig_map = go.Figure(
        go.Choropleth(
            locations=state_rev["customer_state"],
            z=state_rev["revenue"],
            locationmode="USA-states",
            colorscale="Blues",
            showscale=True,
            colorbar=dict(title="Revenue", tickformat="$~s"),
        )
    )
    fig_map.update_layout(
        title="Revenue by State",
        geo_scope="usa",
        height=350,
        margin=dict(t=50, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

with chart4:
    sat_df = calculate_delivery_satisfaction(current_df, datasets["reviews"])
    buckets = ["1-3 days", "4-7 days", "8+ days"]
    bucket_means = (
        sat_df[sat_df["delivery_bucket"] != "Unknown"]
        .groupby("delivery_bucket")["review_score"]
        .mean()
        .reindex(buckets)
    )

    fig_sat = go.Figure(
        go.Bar(
            x=bucket_means.index,
            y=bucket_means.values,
            marker_color="#2C5F8A",
            text=[f"{v:.2f}" if not pd.isna(v) else "" for v in bucket_means.values],
            textposition="outside",
        )
    )
    fig_sat.update_layout(
        title="Review Score vs Delivery Time",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f2f5", range=[0, 5.4]),
        height=350,
        margin=dict(t=50, b=40, l=50, r=20),
    )
    st.plotly_chart(fig_sat, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ── Bottom Row ────────────────────────────────────────────────────────────────
bot1, bot2 = st.columns(2)

avg_delivery = (
    current_df["delivery_speed"].mean()
    if "delivery_speed" in current_df.columns
    else float("nan")
)
prev_delivery = (
    comparison_df["delivery_speed"].mean()
    if (has_comparison and "delivery_speed" in comparison_df.columns)
    else None
)

with bot1:
    del_val = f"{avg_delivery:.2f} days" if not pd.isna(avg_delivery) else "—"
    st.markdown(
        f"""
    <div class="bottom-card">
        <p class="bottom-label">Average Delivery Time</p>
        <p class="bottom-value">{del_val}</p>
        <p class="bottom-trend">{trend_badge(avg_delivery, prev_delivery, lower_is_better=True)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

rev_df = calculate_delivery_satisfaction(current_df, datasets["reviews"])
avg_review = (
    rev_df["review_score"].mean()
    if "review_score" in rev_df.columns
    else float("nan")
)

with bot2:
    if not pd.isna(avg_review):
        filled = round(avg_review)
        stars = "★" * filled + "☆" * (5 - filled)
        review_val = f"{avg_review:.2f}"
    else:
        stars = "☆☆☆☆☆"
        review_val = "—"
    st.markdown(
        f"""
    <div class="bottom-card">
        <p class="bottom-value">{review_val}</p>
        <p class="stars">{stars}</p>
        <p class="bottom-label">Average Review Score</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
