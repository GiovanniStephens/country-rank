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
    return annuity_cost + moving_cost


if __name__ == '__main__':
    buffer = 5000
    rate = 0.07
    import scrape_cost_of_living as sc
    # print(estimate_cost_to_retire('Spain',sc.get_country_cost_of_living('Spain'),r=rate,n=66, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Portugal',sc.get_country_cost_of_living('Portugal'),r=rate,n=66, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Georgia',sc.get_country_cost_of_living('Georgia'),r=rate,n=66, buffer_pa=buffer))
    print(estimate_cost_to_retire('Colombia',sc.get_country_cost_of_living('Colombia'),r=rate,n=66, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Uruguay',sc.get_country_cost_of_living('Uruguay'),r=rate,n=66, buffer_pa=buffer))
    print(estimate_cost_to_retire('New Zealand',sc.get_country_cost_of_living('New Zealand',90),r=rate,n=66, moving_cost=0, buffer_pa=buffer))
    print(estimate_cost_to_retire('New Zealand',sc.get_country_cost_of_living('New Zealand',50),r=rate,n=66, moving_cost=0, buffer_pa=buffer))
    print(estimate_cost_to_retire('New Zealand',sc.get_country_cost_of_living('New Zealand',10),r=rate,n=66, moving_cost=0, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Indonesia', sc.get_country_cost_of_living('Indonesia'), r=rate, n=66, moving_cost=5000, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Argentina', sc.get_country_cost_of_living('Argentina'), r=rate, n=66, moving_cost=5000, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Australia', sc.get_country_cost_of_living('Australia', 50), r=rate, n=66, moving_cost=5000, buffer_pa=buffer))