# Sales Orders Domain Specification

## Purpose
The sales orders pipeline processes raw order data into curated, business-ready datasets for analytics and reporting.

## Data Sources
- **raw.sales_orders**: Raw order data from e-commerce platform
- **raw.customers**: Customer master data
- **raw.products**: Product catalog

## Business Rules

### Data Quality Requirements
- Order amounts must be positive
- Customer IDs must exist in customer master
- Product IDs must exist in product catalog
- Timestamps must be valid and recent

### Transformation Logic
1. **Clean**: Remove invalid records
2. **Enrich**: Add customer and product details
3. **Calculate**: Compute derived fields
4. **Validate**: Apply business rules

## SLA Commitments
- **Availability**: 99.9% uptime
- **Freshness**: Data available within 2 hours of source update
- **Accuracy**: <0.1% error rate

## Downstream Dependencies
- **curated.revenue_summary**: Daily revenue reporting
- **bi.daily_sales**: Executive dashboard
- **analytics.customer_behavior**: Customer analytics

## Ownership
- **Primary**: data-sales team
- **Secondary**: data-platform team
- **Stakeholders**: Finance, Marketing, Product
