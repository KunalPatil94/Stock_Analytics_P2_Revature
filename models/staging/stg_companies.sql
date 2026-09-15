select
    trim(company_id) as company_id,
    upper(trim(ticker)) as ticker,
    trim(company_name) as company_name,
    trim(sector) as sector,
    trim(industry) as industry,
    trim(market_cap_band) as market_cap_band,
    trim(country) as country,
    trim(primary_exchange_id) as primary_exchange_id,
    trim(status) as status,

    try_to_date(listed_since) as listed_since,
    try_to_timestamp_ntz(updated_at) as updated_at

from {{ source('raw', 'RAW_COMPANIES') }}