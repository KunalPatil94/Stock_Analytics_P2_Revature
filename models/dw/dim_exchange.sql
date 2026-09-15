select
    row_number() over (order by exchange_id) as sk_exchange,

    exchange_id,
    exchange_code,
    country,
    currency,
    timezone,
    market_type,
    status,
    established_date,
    updated_at

from {{ ref('stg_exchanges') }}