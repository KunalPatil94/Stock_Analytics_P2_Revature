{% snapshot dim_company_snapshot %}

{{
    config(
        target_schema='DW',
        unique_key='company_id',
        strategy='check',
        check_cols=[
            'ticker',
            'company_name',
            'sector',
            'industry',
            'market_cap_band',
            'country',
            'primary_exchange_id',
            'status',
            'listed_since'
        ]
    )
}}

select
    company_id,
    ticker,
    company_name,
    sector,
    industry,
    market_cap_band,
    country,
    primary_exchange_id,
    status,
    listed_since,
    updated_at

from {{ ref('stg_companies') }}

{% endsnapshot %}