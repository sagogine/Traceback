# Marketing Attribution Pipeline Specification

## Purpose
Multi-touch attribution modeling for marketing campaign effectiveness and ROI analysis.

## Data Sources
- **raw.marketing_touchpoints**: Customer interactions
- **raw.campaign_performance**: Campaign metrics
- **raw.conversion_events**: Purchase conversions
- **raw.customer_journey**: Complete customer path

## Business Rules
### Attribution Models
- **First Touch**: Credit to first interaction
- **Last Touch**: Credit to final interaction
- **Linear**: Equal credit to all touchpoints
- **Time Decay**: More credit to recent interactions

### ROI Calculations
- **Campaign ROI**: Revenue / Campaign Cost
- **Channel ROI**: Revenue / Channel Investment
- **Customer LTV**: Lifetime value calculations

## SLA Commitments
- **Availability**: 99.0% uptime
- **Freshness**: Weekly updates by Monday 9 AM
- **Accuracy**: <1% error rate

## Downstream Dependencies
- **marketing.campaign_optimization**: Budget allocation
- **sales.lead_scoring**: Lead qualification
- **product.growth_metrics**: Product adoption tracking

## Ownership
- **Primary**: data-marketing team
- **Secondary**: data-growth team
- **Stakeholders**: Marketing, Sales, Product