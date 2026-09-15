select
    trim(price_id) as price_id,
    try_to_date(trade_date) as trade_date,
    trim(company_id) as company_id,
    trim(exchange_id) as exchange_id,

    try_to_decimal(open, 18, 4) as open,
    try_to_decimal(high, 18, 4) as high,
    try_to_decimal(low, 18, 4) as low,
    try_to_decimal(close, 18, 4) as close,
    try_to_decimal(adj_close, 18, 4) as adj_close,

    try_to_number(volume) as volume,
    try_to_decimal(vwap, 18, 4) as vwap,

    try_to_timestamp_ntz(updated_at) as updated_at

from {{ source('raw', 'RAW_PRICES_DAILY') }}