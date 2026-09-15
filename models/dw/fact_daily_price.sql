{{ config(
    materialized = 'table'
) }}

select
    p.price_id,

    d.sk_date,
    c.sk_company,
    e.sk_exchange,

    p.trade_date,
    p.company_id,
    p.exchange_id,

    p.open,
    p.high,
    p.low,
    p.close,
    p.adj_close,
    p.volume,
    p.vwap,

    p.updated_at

from {{ ref('stg_prices_daily') }} p

left join {{ ref('dim_date') }} d
    on p.trade_date = d.full_date

left join {{ ref('dim_company') }} c
    on p.company_id = c.company_id
    and p.trade_date >= c.eff_start
    and (
        p.trade_date < c.eff_end
        or c.eff_end is null
    )

left join {{ ref('dim_exchange') }} e
    on p.exchange_id = e.exchange_id