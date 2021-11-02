import predict_PPP as ppp
nz_conversion_rate = ppp.estimate_PPP_conversion_rate_long_term_change('New Zealand')

def estimate_cost_to_retire(country, weekly_cost, r=0.06, n=68, moving_cost=8000, buffer_pa=10000):
    conversion_rate_change = ppp.estimate_PPP_conversion_rate_long_term_change(country)
    overall_conversion_rate = min(0,(1+conversion_rate_change) / (1+nz_conversion_rate) - 1)
    g = overall_conversion_rate
    annuity_cost = (weekly_cost*52+buffer_pa)/(r-g)*(1-((1+g)/(1+r))**n)
    return annuity_cost + moving_cost

if __name__ == '__main__':
    buffer = 0
    rate = 0.06
    print(estimate_cost_to_retire('Spain',951,r=rate,n=32, buffer_pa=buffer))
    print(estimate_cost_to_retire('Portugal',853,r=rate,n=32, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Germany',1150,r=rate,n=66, buffer_pa=buffer))
    print(estimate_cost_to_retire('Georgia',445,r=rate,n=32, buffer_pa=buffer))
    print(estimate_cost_to_retire('Colombia',442,r=rate,n=32, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Uruguay',762,r=rate,n=32, buffer_pa=buffer))
    # print(estimate_cost_to_retire('Croatia',874,r=rate,n=66, buffer_pa=buffer))
    # print(estimate_cost_to_retire('New Zealand',1050,r=rate,n=66, moving_cost=0, buffer_pa=buffer))