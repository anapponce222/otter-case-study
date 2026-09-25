import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------
# Visual constants
# -------------------------

CHART_COLORS = [
    "#6366F1",
    "#8B5CF6",
    "#0EA5E9",
    "#14B8A6",
    "#F59E0B",
    "#EC4899",
    "#64748B",
    "#84CC16",
]


# -------------------------
# Page configuration
# -------------------------

st.set_page_config(
    page_title="Market Deal Intelligence",
    page_icon="📊",
    layout="wide"
)


# -------------------------
# Global styling
# -------------------------

st.markdown(
    """
    <style>
        /* App */
        .stApp {
            background-color: #F8FAFC;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        /* Typography */
        html, body, [class*="css"] {
            font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
            color: #172033;
        }

        h1, h2, h3, h4 {
            color: #172033;
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.6rem !important;
            font-weight: 750 !important;
        }

        h2 {
            font-weight: 700 !important;
        }

        /* KPI cards */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E7EAF0;
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }

        [data-testid="stMetricLabel"] {
            color: #667085;
        }

        [data-testid="stMetricValue"] {
            color: #172033;
            font-weight: 700;
        }

        /* Dividers */
        hr {
            border-color: #E7EAF0 !important;
            margin-top: 2.5rem !important;
            margin-bottom: 2.5rem !important;
        }

        /* Info boxes */
        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid #E7EAF0;
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------
# Load data
# -------------------------

@st.cache_data
def load_data():
    return pd.read_csv("data/amazon_deals_normalized.csv")


df = load_data()


# -------------------------
# Category benchmarks
# -------------------------

category_benchmarks = (
    df.groupby("category_clean")
      .agg(
          category_deals=("asin", "count"),
          category_median_discount=(
              "display_discount_pct",
              "median"
          )
      )
      .reset_index()
)

df = df.merge(
    category_benchmarks,
    on="category_clean",
    how="left"
)

df["discount_uplift_pp"] = (
    df["display_discount_pct"]
    - df["category_median_discount"]
)


# -------------------------
# Header
# -------------------------

st.title("Market Deal Intelligence")

st.markdown(
    """
    **Competitive promotion benchmarking from public marketplace data**
    """
)

st.caption(
    f"Amazon Mexico · Today's Deals · {len(df):,} active deals analyzed"
)

st.markdown(
    """
    Understand market-wide promotional behavior, benchmark discount
    strategies, and identify deals that stand out relative to their peers.
    """
)


# -------------------------
# KPI calculations
# -------------------------

total_deals = len(df)
median_discount = df["display_discount_pct"].median()
median_price = df["deal_price_mxn"].median()
median_savings = df["absolute_savings_mxn"].median()


# -------------------------
# KPI cards
# -------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Active Deals",
        value=f"{total_deals:,}"
    )

with col2:
    st.metric(
        label="Median Discount",
        value=f"{median_discount:.0f}%"
    )

with col3:
    st.metric(
        label="Median Deal Price",
        value=f"${median_price:,.0f}"
    )

with col4:
    st.metric(
        label="Median Savings",
        value=f"${median_savings:,.0f}"
    )

st.caption("Prices and savings shown in MXN.")


# -------------------------
# Promotional landscape
# -------------------------

st.divider()

st.subheader("Promotional Landscape")

st.caption(
    "Median discount by category · categories with at least 10 active deals"
)

category_summary = (
    df.groupby("category_clean")
      .agg(
          deals=("asin", "count"),
          median_discount=("display_discount_pct", "median")
      )
      .query("deals >= 10")
      .sort_values("median_discount", ascending=True)
      .reset_index()
)

fig_category = px.bar(
    category_summary,
    x="median_discount",
    y="category_clean",
    orientation="h",
    text="median_discount",
    labels={
        "median_discount": "Median Discount (%)",
        "category_clean": ""
    },
    hover_data={
        "deals": True,
        "median_discount": ":.1f"
    },
    color_discrete_sequence=["#6366F1"]
)

fig_category.update_traces(
    texttemplate="%{text:.0f}%",
    textposition="outside"
)

fig_category.update_layout(
    showlegend=False,
    xaxis_title="Median Discount (%)",
    yaxis_title=None,
    height=550,
    margin=dict(l=10, r=40, t=10, b=10),
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(
        family="Inter, Helvetica Neue, Arial",
        color="#667085"
    )
)

fig_category.update_xaxes(
    gridcolor="#E7EAF0"
)

st.plotly_chart(
    fig_category,
    use_container_width=True
)


# -------------------------
# Deal positioning
# -------------------------

st.divider()

st.subheader("Deal Positioning")

st.caption(
    "How deal prices and discount levels are distributed across the marketplace"
)

fig_scatter = px.scatter(
    df,
    x="deal_price_mxn",
    y="display_discount_pct",
    color="category_clean",
    color_discrete_sequence=CHART_COLORS,
    hover_name="title",
    hover_data={
        "brand": True,
        "category_clean": True,
        "deal_price_mxn": ":,.0f",
        "basis_price_mxn": ":,.0f",
        "display_discount_pct": ":.0f",
        "absolute_savings_mxn": ":,.0f",
        "review_count": ":,.0f"
    },
    labels={
        "deal_price_mxn": "Deal Price (MXN)",
        "display_discount_pct": "Discount (%)",
        "category_clean": "Category",
        "brand": "Brand",
        "basis_price_mxn": "Reference Price",
        "absolute_savings_mxn": "Savings",
        "review_count": "Reviews"
    },
    log_x=True
)

fig_scatter.update_traces(
    marker=dict(
        size=9,
        opacity=0.65
    )
)

fig_scatter.update_layout(
    showlegend=False,
    xaxis_title="Deal Price (MXN, log scale)",
    yaxis_title="Discount (%)",
    height=520,
    margin=dict(l=10, r=20, t=10, b=10),
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(
        family="Inter, Helvetica Neue, Arial",
        color="#667085"
    )
)

fig_scatter.update_xaxes(
    tickvals=[
        100,
        250,
        500,
        1000,
        2500,
        5000,
        10000,
        25000
    ],
    ticktext=[
        "$100",
        "$250",
        "$500",
        "$1K",
        "$2.5K",
        "$5K",
        "$10K",
        "$25K"
    ],
    gridcolor="#E7EAF0"
)

fig_scatter.update_yaxes(
    gridcolor="#E7EAF0"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# -------------------------
# Discount value by price band
# -------------------------

st.divider()

st.subheader("Discount Value by Price Band")

st.caption(
    "Percentage discount and monetary savings provide different views of deal value"
)

price_band_order = [
    "Under $500",
    "$500–999",
    "$1,000–2,499",
    "$2,500–4,999",
    "$5,000+"
]

price_band_summary = (
    df.groupby("price_band", observed=True)
      .agg(
          deals=("asin", "count"),
          median_discount=("display_discount_pct", "median"),
          median_savings=("absolute_savings_mxn", "median")
      )
      .reindex(price_band_order)
      .reset_index()
)

left, right = st.columns(2)


# Median percentage discount
with left:
    st.markdown("#### Median Discount")

    fig_discount_band = px.bar(
        price_band_summary,
        x="price_band",
        y="median_discount",
        text="median_discount",
        labels={
            "price_band": "",
            "median_discount": "Median Discount (%)"
        },
        hover_data={
            "deals": True
        },
        color_discrete_sequence=["#6366F1"]
    )

    fig_discount_band.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside"
    )

    fig_discount_band.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        font=dict(
            family="Inter, Helvetica Neue, Arial",
            color="#667085"
        )
    )

    fig_discount_band.update_xaxes(
        showgrid=False
    )

    fig_discount_band.update_yaxes(
        gridcolor="#E7EAF0"
    )

    st.plotly_chart(
        fig_discount_band,
        use_container_width=True
    )


# Median monetary savings
with right:
    st.markdown("#### Median Savings")

    fig_savings_band = px.bar(
        price_band_summary,
        x="price_band",
        y="median_savings",
        text="median_savings",
        labels={
            "price_band": "",
            "median_savings": "Median Savings (MXN)"
        },
        hover_data={
            "deals": True
        },
        color_discrete_sequence=["#14B8A6"]
    )

    fig_savings_band.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig_savings_band.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        font=dict(
            family="Inter, Helvetica Neue, Arial",
            color="#667085"
        )
    )

    fig_savings_band.update_xaxes(
        showgrid=False
    )

    fig_savings_band.update_yaxes(
        gridcolor="#E7EAF0"
    )

    st.plotly_chart(
        fig_savings_band,
        use_container_width=True
    )

st.info(
    "Lower-priced deals tend to offer stronger percentage discounts, "
    "while higher-priced products generate substantially larger monetary savings."
)


# -------------------------
# Standout deals
# -------------------------

st.divider()

st.subheader("Standout Deals")

st.caption(
    "Identify promotions that stand out relative to their category benchmark"
)

benchmark_df = df[
    (df["category_deals"] >= 10)
    & (df["review_count"].notna())
].copy()

fig_standout = px.scatter(
    benchmark_df,
    x="discount_uplift_pp",
    y="review_count",
    color="category_clean",
    color_discrete_sequence=CHART_COLORS,
    hover_name="title",
    hover_data={
        "brand": True,
        "category_clean": True,
        "display_discount_pct": ":.0f",
        "category_median_discount": ":.1f",
        "discount_uplift_pp": ":+.1f",
        "review_count": ":,.0f",
        "deal_price_mxn": ":,.0f"
    },
    labels={
        "discount_uplift_pp": "Discount vs. Category Benchmark (pp)",
        "review_count": "Reviews",
        "category_clean": "Category",
        "brand": "Brand",
        "display_discount_pct": "Product Discount",
        "category_median_discount": "Category Median",
        "deal_price_mxn": "Deal Price"
    },
    log_y=True
)

fig_standout.update_traces(
    marker=dict(
        size=9,
        opacity=0.65
    )
)

fig_standout.add_vline(
    x=0,
    line_dash="dash",
    line_color="#94A3B8"
)

fig_standout.add_annotation(
    x=1,
    y=0.99,
    xref="x",
    yref="paper",
    text="Above category benchmark →",
    showarrow=False,
    xanchor="left",
    yanchor="top",
    font=dict(
        size=12,
        color="#6366F1"
    )
)

fig_standout.update_layout(
    showlegend=False,
    xaxis_title="Discount vs. Category Benchmark (percentage points)",
    yaxis_title="Review Count (log scale)",
    height=540,
    margin=dict(l=10, r=20, t=10, b=10),
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(
        family="Inter, Helvetica Neue, Arial",
        color="#667085"
    )
)

fig_standout.update_xaxes(
    gridcolor="#E7EAF0"
)

fig_standout.update_yaxes(
    tickvals=[
        1,
        10,
        100,
        1000,
        10000,
        100000
    ],
    ticktext=[
        "1",
        "10",
        "100",
        "1K",
        "10K",
        "100K"
    ],
    gridcolor="#E7EAF0"
)

st.plotly_chart(
    fig_standout,
    use_container_width=True
)

st.info(
    "Deals further to the right offer larger discounts than the typical "
    "promotion in their category. Products higher on the chart have more "
    "accumulated customer reviews, providing a measure of existing social proof."
)


# -------------------------
# Largest category-relative discounts
# -------------------------

top_standouts = (
    benchmark_df[
        benchmark_df["discount_uplift_pp"] > 0
    ]
    .sort_values(
        ["discount_uplift_pp", "review_count"],
        ascending=[False, False]
    )
    .head(5)
)

st.markdown("#### Largest Category-Relative Discounts")

st.dataframe(
    top_standouts[
        [
            "title",
            "category_clean",
            "display_discount_pct",
            "category_median_discount",
            "discount_uplift_pp",
            "review_count",
            "product_url"
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "title": st.column_config.TextColumn(
            "Product",
            width="large"
        ),
        "category_clean": st.column_config.TextColumn(
            "Category"
        ),
        "display_discount_pct": st.column_config.NumberColumn(
            "Discount",
            format="%.0f%%"
        ),
        "category_median_discount": st.column_config.NumberColumn(
            "Category Median",
            format="%.1f%%"
        ),
        "discount_uplift_pp": st.column_config.NumberColumn(
            "Vs. Benchmark",
            format="+%.1f pp"
        ),
        "review_count": st.column_config.NumberColumn(
            "Reviews",
            format="%d"
        ),
        "product_url": st.column_config.LinkColumn(
            "Amazon",
            display_text="View deal"
        )
    }
)


# -------------------------
# Deal explorer
# -------------------------

st.divider()

st.subheader("Deal Explorer")

st.caption(
    "Filter and explore individual deals from the current marketplace snapshot"
)


# -------------------------
# Filters
# -------------------------

filter_col1, filter_col2, filter_col3 = st.columns(3)

categories = sorted(
    df["category_clean"].dropna().unique()
)

brands = sorted(
    df["brand"].dropna().unique()
)

with filter_col1:
    selected_categories = st.multiselect(
        "Category",
        options=categories,
        placeholder="All categories"
    )

with filter_col2:
    selected_brands = st.multiselect(
        "Brand",
        options=brands,
        placeholder="All brands"
    )

with filter_col3:
    min_discount = st.slider(
        "Minimum discount",
        min_value=0,
        max_value=int(df["display_discount_pct"].max()),
        value=0,
        step=5,
        format="%d%%"
    )


# Price filter
min_price = int(df["deal_price_mxn"].min())
max_price = int(df["deal_price_mxn"].max())

selected_price_range = st.slider(
    "Deal price range (MXN)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=100
)


# -------------------------
# Apply filters
# -------------------------

filtered_df = df.copy()

if selected_categories:
    filtered_df = filtered_df[
        filtered_df["category_clean"].isin(selected_categories)
    ]

if selected_brands:
    filtered_df = filtered_df[
        filtered_df["brand"].isin(selected_brands)
    ]

filtered_df = filtered_df[
    filtered_df["display_discount_pct"] >= min_discount
]

filtered_df = filtered_df[
    filtered_df["deal_price_mxn"].between(
        selected_price_range[0],
        selected_price_range[1]
    )
]


# -------------------------
# Results
# -------------------------

st.markdown(
    f"**{len(filtered_df):,} deals found**"
)

display_df = (
    filtered_df[
        [
            "title",
            "brand",
            "category_clean",
            "deal_price_mxn",
            "display_discount_pct",
            "absolute_savings_mxn",
            "rating",
            "review_count",
            "product_url"
        ]
    ]
    .sort_values(
        "display_discount_pct",
        ascending=False
    )
    .copy()
)

display_df["brand"] = display_df["brand"].fillna("—")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "title": st.column_config.TextColumn(
            "Product",
            width="large"
        ),

        "brand": st.column_config.TextColumn(
            "Brand"
        ),

        "category_clean": st.column_config.TextColumn(
            "Category"
        ),

        "deal_price_mxn": st.column_config.NumberColumn(
            "Deal Price",
            format="$%.0f"
        ),

        "display_discount_pct": st.column_config.NumberColumn(
            "Discount",
            format="%.0f%%"
        ),

        "absolute_savings_mxn": st.column_config.NumberColumn(
            "Savings",
            format="$%.0f"
        ),

        "rating": st.column_config.NumberColumn(
            "Rating",
            format="%.1f ★"
        ),

        "review_count": st.column_config.NumberColumn(
            "Reviews",
            format="%d"
        ),

        "product_url": st.column_config.LinkColumn(
            "Amazon",
            display_text="View deal"
        )
    }
)

# -------------------------
# About this prototype
# -------------------------

st.divider()

with st.expander("About this prototype"):
    st.markdown(
        """
        ### Methodology

        This prototype uses a point-in-time snapshot of Amazon Mexico's
        Today's Deals marketplace. The data was extracted from Amazon's
        structured deals endpoint, normalized to one row per product, and
        analyzed across categories, price points, discount levels, and
        customer review volume.

        ### Key assumptions

        - **Deal definition:** Products returned by Amazon's deals feed as
          available `BEST_DEAL` promotions are treated as active deals.
        - **Category benchmarking:** Category-level comparisons are limited
          to categories with at least 10 active deals to reduce noise from
          very small samples.
        - **Discount benchmarking:** Median discount is used instead of the
          mean because promotional distributions can contain large outliers.
        - **Customer reviews:** Review count represents accumulated social
          proof. It is not treated as a measure of sales or current deal
          performance.

        ### Limitations

        This analysis represents a single marketplace snapshot and does not
        include historical deal performance, sales, conversion rates,
        restaurant or product margins, profitability, or customer-level
        behavior. Results should therefore be interpreted as market
        intelligence rather than promotion-performance recommendations.

        ### Product opportunity

        The same approach could be extended into a promotion intelligence
        product for restaurants by combining first-party restaurant
        performance data, anonymized market benchmarks, and external market
        signals. This could help operators understand how their promotional
        strategy compares with the market and identify unusual competitive
        activity worth investigating.
        """
    )