# ADR-004: Synthetic Data Strategy

## Status
Approved

## Context
We need realistic test datasets containing 100,000+ orders, 10,000 customers, and 1,000 products to test the platform. We evaluated standard testing data vs. generating synthetic records programmatically.

## Decision
We implemented a self-contained, repeatable Python generator script that outputs structured CSV records matching realistic retail data distributions.

## Rationale
1. **Multi-Channel Format Diversity**: To verify the standardization capabilities of our Silver layer, the generator outputs diverse channel formats (e.g. Amazon dates in ISO `YYYY-MM-DDTHH:MM:SSZ`, Flipkart dates in `DD/MM/YYYY HH:MM`, and Shopify standard format).
2. **Deterministic & Self-Contained**: The script relies solely on Python's standard library. It does not require installing external libraries like `Faker`, preventing dependency conflicts during Docker builds or local test runs.
3. **Realistic Distributions**:
   - Order volumes reflect real commerce trends (Shopify is standard, Amazon has high-value tech, Flipkart contains high volume).
   - A 4% refund rate is simulated for Shopify orders to test refund/cancellation aggregation pipelines.
