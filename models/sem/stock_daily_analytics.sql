select
    f.price_id,

    d.full_date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    c.company_id,
    c.ticker,
    c.company_name,
    c.sector,
    c.industry,
    c.market_cap_band,
    c.country,

    e.exchange_id,
    e.exchange_code,
    e.country as exchange_country,
    e.currency,
    e.market_type,

    f.open,
    f.high,
    f.low,
    f.close,
    f.adj_close,
    f.volume,
    f.vwap,

    -- Intraday metrics only: close vs open and high vs low WITHIN the same
    -- session. Deliberately not a day-over-day / period-over-period
    -- calculation: this fact table has sparse, non-consecutive sessions per
    -- ticker, so comparing one row's close to a DIFFERENT row's close from
    -- days earlier produces meaningless swings. Intraday change is the only
    -- return-like metric that is valid at this grain.
    f.high - f.low as daily_range,

    case
        when f.open <> 0
            then ((f.close - f.open) / f.open) * 100
    end as daily_return_pct,

    case
        when f.open <> 0
            then ((f.high - f.low) / f.open) * 100
    end as daily_range_pct,

    f.close * f.volume as turnover,

    fx.usd_rate,
    (f.close * f.volume) * fx.usd_rate as turnover_usd

from {{ ref('fact_daily_price') }} f

join {{ ref('dim_date') }} d
    on f.sk_date = d.sk_date

join {{ ref('dim_company') }} c
    on f.sk_company = c.sk_company

join {{ ref('dim_exchange') }} e
    on f.sk_exchange = e.sk_exchange

left join {{ ref('fx_rates_usd') }} fx
    on e.currency = fx.currency