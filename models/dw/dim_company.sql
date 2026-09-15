{{ config(
    materialized = 'table'
) }}

with snapshot_data as (

    select
        *,
        row_number() over (
            partition by company_id
            order by dbt_valid_from
        ) as version_number
    from {{ ref('dim_company_snapshot') }}

)

select
    dbt_scd_id as sk_company,

    company_id,
    ticker,
    company_name,
    sector,
    industry,
    market_cap_band,
    country,
    primary_exchange_id,
    status,

    md5(
        concat_ws(
            '||',
            coalesce(ticker, ''),
            coalesce(company_name, ''),
            coalesce(sector, ''),
            coalesce(industry, ''),
            coalesce(market_cap_band, ''),
            coalesce(country, ''),
            coalesce(primary_exchange_id, ''),
            coalesce(status, ''),
            coalesce(to_varchar(listed_since), '')
        )
    ) as hash_diff,

    case
        when version_number = 1
            then listed_since::timestamp_ntz
        else dbt_valid_from
    end as eff_start,

    dbt_valid_to as eff_end,

    case
        when dbt_valid_to is null then true
        else false
    end as is_current

from snapshot_data