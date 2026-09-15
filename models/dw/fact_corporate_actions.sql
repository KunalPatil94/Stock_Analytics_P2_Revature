{{ config(
    materialized = 'table'
) }}

select
    ca.action_id,
    c.sk_company,
    ca.company_id,
    ca.ticker,
    upper(ca.action_type) as action_type,

    ca.ex_date,
    ca.record_date,
    ca.pay_date,

    ca.action_value,
    ca.ratio,
    ca.currency,
    ca.status,
    ca.updated_at

from {{ ref('stg_corporate_actions') }} ca

left join {{ ref('dim_company') }} c
    on ca.company_id = c.company_id
    and ca.ex_date >= c.eff_start
    and (
        ca.ex_date < c.eff_end
        or c.eff_end is null
    )