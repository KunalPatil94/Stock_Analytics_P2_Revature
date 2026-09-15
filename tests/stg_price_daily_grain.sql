select
    company_id,
    trade_date,
    exchange_id,
    count(*) as row_count
from {{ ref('stg_prices_daily') }}
group by
    company_id,
    trade_date,
    exchange_id
having count(*) > 1