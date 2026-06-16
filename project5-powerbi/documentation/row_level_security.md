# Row-Level Security (RLS) — Retail Executive Dashboard

## Overview
RLS restricts data access so regional managers only see their own region's data.
Executives and the Finance team see all regions.

## Roles Defined

| Role | Filter | Who Uses It |
|------|--------|-------------|
| `RegionalManager` | `dim_store[region] = USERPRINCIPALNAME()` lookup | Regional managers |
| `Executive` | No filter (all data) | C-suite, Finance |
| `StoreManager` | `dim_store[store_id] = USERPRINCIPALNAME()` lookup | Individual store managers |

## DAX Filter for RegionalManager Role

Apply this filter on `dim_store` table:

```dax
[region] = LOOKUPVALUE(
    security_mapping[region],
    security_mapping[email], USERPRINCIPALNAME()
)
```

## security_mapping Table Structure

| email | region | role |
|-------|--------|------|
| alice@company.com | NORTH | RegionalManager |
| bob@company.com | SOUTH | RegionalManager |
| ceo@company.com | ALL | Executive |

## Testing RLS
1. In Power BI Desktop → Modelling tab → View as Role
2. Select `RegionalManager` and enter a test email
3. Verify only that region's data appears in all visuals

## Deployment Notes
- Assign users to roles in Power BI Service → Dataset → Security
- RLS applies to both Import and DirectQuery tables
- Always test after any schema changes to dim_store
