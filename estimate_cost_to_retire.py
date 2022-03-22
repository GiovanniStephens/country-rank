import predict_PPP as ppp
nz_conversion_rate = ppp.estimate_PPP_conversion_rate_long_term_change('New Zealand')


def estimate_cost_to_retire(country: str,
                            weekly_cost: float,
                            r: float = 0.06,
                            n: int = 68,
                            moving_cost: float = 8000,
                            buffer_pa: float = 10000):
    """
    Estimate the cost to retire in a country.

    :country: The country to estimate the cost to retire in.
    :weekly_cost: The weekly cost of living in the country.
    :r: The rate of return on investments.
    :n: The number of years to retire.
    :moving_cost: The cost of moving to a new country.
    :buffer_pa: The buffer cost in the annual cost of living.
    :return: The cost to retire in the country.
    """
    conversion_rate_change = ppp.estimate_PPP_conversion_rate_long_term_change(country)
    overall_conversion_rate = min(0, (1 + conversion_rate_change) /
                                     (1 + nz_conversion_rate) - 1)
    inverse_conversion_rate = 1 / (1 + overall_conversion_rate) - 1
    g = 1.02/(1+inverse_conversion_rate)-1
    annuity_cost = (weekly_cost * 52 + buffer_pa) / (r - g) * (1 - ((1 + g) / (1 + r))**n)
    return round(annuity_cost + moving_cost,2)


if __name__ == '__main__':
    buffer = 5000
    moving_cost = 8000
    rate = 0.07
    import scrape_cost_of_living as sc
    countries = ['Spain', 'Portugal', 'New Zealand', 'Indonesia', 'Australia', 'Uruguay', 'Argentina', 'Colombia', 'Peru', 'Bolivia', 'Mexico', 'Poland', 'Croatia']
    percentiles = [50]
    # countries = ['Uruguay']
    # percentiles = [90]
    for country in countries:
        for percentile in percentiles:
            cost = sc.get_country_cost_of_living(country,percentile)
            print(estimate_cost_to_retire(country, cost, rate, n=66, moving_cost=moving_cost, buffer_pa=buffer))