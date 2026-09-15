{{ config(
    materialized = 'view'
) }}

-- Replaces the Streamlit-side pandas groupby that was computing
-- AVG_DAILY_RETURN_PCT / AVG_VOLATILITY_20D by chaining pct_change() across
-- non-consecutive sessions. Both metrics here are built only from intraday
-- (same-session) values, so they stay sane regardless of how sparse a
-- sector/exchange combination's sessions are.

select
    sector,
    exchange_code,

    count(distinct company_id) as total_companies,
    count(*) as total_trading_records,

    avg(close) as avg_close_price,
    avg(daily_return_pct) as avg_daily_return_pct,
    avg(daily_range_pct) as avg_intraday_volatility_pct,

    sum(volume) as total_volume,
    sum(turnover_usd) as total_turnover_usd

from {{ ref('stock_daily_analytics') }}

group by
    sector,
    exchange_code
