{{ config(
    materialized = 'view'
) }}

-- Feeds the "Top Gainers / Top Losers / Volume Leaders" charts directly.
-- Ranked on daily_return_pct (intraday, same-session change) so Streamlit
-- no longer needs to compute or rank anything itself for this page.

select
    full_date as trade_date,
    ticker,
    company_name,
    sector,
    country,
    exchange_code,

    open,
    close,
    daily_return_pct,
    daily_range_pct,
    volume,
    turnover_usd,

    rank() over (order by daily_return_pct desc) as gain_rank,
    rank() over (order by daily_return_pct asc) as loss_rank,
    rank() over (order by volume desc) as volume_rank

from {{ ref('stock_daily_analytics') }}
