select
    trim(action_id) as action_id,
    trim(company_id) as company_id,
    upper(trim(ticker)) as ticker,
    upper(trim(action_type)) as action_type,

    try_to_date(ex_date) as ex_date,
    try_to_date(record_date) as record_date,
    try_to_date(pay_date) as pay_date,

    try_to_decimal(action_value, 18, 4) as action_value,

    trim(ratio) as ratio,
    upper(trim(currency)) as currency,
    upper(trim(status)) as status,

    try_to_timestamp_ntz(updated_at) as updated_at

from {{ source('raw', 'RAW_CORPORATE_ACTIONS') }}