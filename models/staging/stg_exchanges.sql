select
    trim(exchange_id) as exchange_id,
    upper(trim(exchange_code)) as exchange_code,
    trim(country) as country,
    upper(trim(currency)) as currency,
    trim(timezone) as timezone,
    trim(market_type) as market_type,
    trim(status) as status,

    try_to_date(established_date) as established_date,
    try_to_timestamp_ntz(updated_at) as updated_at

from {{ source('raw', 'RAW_EXCHANGES') }}