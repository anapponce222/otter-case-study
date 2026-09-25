# Market Deal Intelligence

A lightweight market intelligence prototype built for the Otter case study.

The project extracts and normalizes active deals from Amazon Mexico's Today's
Deals marketplace and transforms the data into an interactive Streamlit
dashboard for promotional benchmarking and deal exploration.

## Project Overview

The prototype explores three main questions:

1. How aggressive are promotions across different product categories?
2. How does promotional value change across price points?
3. Which deals stand out relative to the typical promotion in their category?

The goal is not to recommend specific promotions, but to demonstrate how
external marketplace data can be transformed into actionable competitive
intelligence.

## Data Extraction

Data was collected from Amazon Mexico's structured Today's Deals endpoint.

The extraction process:

- Requests deal data in batches of 30 products
- Paginates through the available results
- Retries transient server errors using bounded exponential backoff
- Deduplicates products using ASIN
- Normalizes nested API responses into a tabular dataset

The final snapshot contains 330 unique active deals.

## Data Processing

Each product is normalized into one row containing relevant fields such as:

- Product and brand
- Category
- Deal price
- Reference price
- Displayed discount
- Calculated discount
- Absolute monetary savings
- Rating and review count
- Deal metadata
- Product URL

Additional analytical features include price bands, category-level discount
benchmarks, and discount uplift relative to the category median.

## Dashboard

The Streamlit dashboard contains:

### Market Overview

High-level metrics describing the current promotional landscape.

### Promotional Landscape

Compares median discount levels across categories with at least 10 active deals.

### Deal Positioning

Shows how discount levels vary across product price points.

### Discount Value by Price Band

Compares percentage discounts with absolute monetary savings across price
segments.

### Standout Deals

Identifies promotions whose discounts are unusually high relative to their
category benchmark and provides review volume as additional context.

### Deal Explorer

Allows users to filter individual deals by category, brand, discount level,
and price.

## Key Assumptions

- Products returned as available `BEST_DEAL` promotions are treated as active
  deals.
- Category benchmarks require at least 10 active deals.
- Median discount is used for benchmarking to reduce sensitivity to outliers.
- Review count is interpreted as accumulated social proof, not sales or
  current deal performance.

## Limitations

The dataset represents a point-in-time marketplace snapshot.

It does not contain historical promotion performance, sales, conversion,
profitability, product margins, or customer-level behavior. The analysis
therefore provides market intelligence rather than promotion-performance
recommendations.

## Product Opportunity

This approach could be extended into a promotion intelligence product for
restaurants by combining first-party restaurant performance data, anonymized
market benchmarks, and external market signals.

Such a product could help restaurant operators understand how their
promotional strategy compares with the broader market and identify unusual
competitive activity worth investigating.

## Run Locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate