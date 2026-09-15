{{ config(
    materialized = 'view'
) }}

select
    ticker,
    company_name,
    sector,
    industry,
    exchange_code,

    count(*) as trading_days,

    min(full_date) as first_trade_date,
    max(full_date) as last_trade_date,

    min(low) as period_low,
    max(high) as period_high,

    avg(close) as avg_close,
    avg(volume) as avg_volume,
    avg(vwap) as avg_vwap,

    max(close) - min(close) as price_range,

    -- Average of each session's own intraday return - valid even with
    -- sparse/non-consecutive sessions, since each value is self-contained
    -- to one trading day. Not a period return (first vs last session):
    -- with only 1-5 sessions per ticker here, that metric would be driven
    -- by gaps between sessions, not real price trend - see stock_daily_analytics
    -- for the reasoning.
    avg(daily_return_pct) as avg_daily_return_pct,
    avg(daily_range_pct) as avg_intraday_volatility_pct,

    sum(volume) as total_volume,
    sum(turnover) as total_turnover,
    sum(turnover_usd) as total_turnover_usd

from {{ ref('stock_daily_analytics') }}

group by
    ticker,
    company_name,
    sector,
    industry,
    exchange_code