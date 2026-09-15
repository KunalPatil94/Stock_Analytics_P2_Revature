with date_range as (

    select
        min(trade_date) as min_date,
        max(trade_date) as max_date
    from {{ ref('stg_prices_daily') }}

),

dates as (

    select
        dateadd(
            day,
            row_number() over (order by seq4()) - 1,
            min_date
        ) as full_date

    from date_range,
         table(generator(rowcount => 1000))

    qualify full_date <= max_date

)

select
    to_number(to_char(full_date, 'YYYYMMDD')) as sk_date,
    full_date,

    year(full_date) as year,
    quarter(full_date) as quarter,
    month(full_date) as month,
    monthname(full_date) as month_name,

    weekiso(full_date) as week,
    day(full_date) as day,
    dayofweekiso(full_date) as day_of_week,
    dayname(full_date) as day_name

from dates