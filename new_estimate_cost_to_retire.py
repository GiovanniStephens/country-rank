# Import Yahoo finance data using yfinance
import numpy as np
import yfinance as yf

# Download historical s&p 500 data
data = yf.download('SPY', interval='1mo', start='1993-02-01')
# drop nan values
data = data.dropna()

# Calculate monthly returns
data['Returns'] = data['Adj Close'].pct_change()
data = data.dropna()

weekly_cost_of_living = 320
monthly_cost_of_living = weekly_cost_of_living * 4.33
annual_cost_of_living = monthly_cost_of_living * 12

n_years_liquid = 2
n_years_remaining = 64
long_term_investments_term = n_years_remaining - n_years_liquid
inflation = 0.015
short_term_interest_rate = 0.05
long_term_interest_rate = 0.09

pv_n_years_liquid_growing_annuity = annual_cost_of_living / (short_term_interest_rate - inflation) * (1 - ((1 + inflation) / (1 + short_term_interest_rate)) ** (n_years_liquid))
print(f'PV of {n_years_liquid} years of expenses growing at {inflation} inflation with {short_term_interest_rate} interest: {pv_n_years_liquid_growing_annuity}')
pv_fv_n_years_illiquid_growing_annuity = annual_cost_of_living * (1 + inflation)**n_years_liquid / (long_term_interest_rate - inflation) * (1 - ((1 + inflation) / (1 + long_term_interest_rate)) ** (long_term_investments_term))
pv_n_years_illiquid_growing_annuity = pv_fv_n_years_illiquid_growing_annuity / (1 + long_term_interest_rate)**n_years_liquid
print(f'PV of {long_term_investments_term} years of expenses growing at {inflation} inflation with {long_term_interest_rate} returns: {pv_n_years_illiquid_growing_annuity}')
total_required = pv_n_years_liquid_growing_annuity + pv_n_years_illiquid_growing_annuity
print(f'Total required: {total_required}')

# Simulate the ending value of a portfolio with the historical returns of the S&P 500
n_simulations = 100
# Calculate the ending value of the portfolio
months_survived = []
buffer = 50000 #total_required - total_required
for i in range(n_simulations):
    illiquid_balance = pv_n_years_illiquid_growing_annuity + buffer
    liquid_balance = pv_n_years_liquid_growing_annuity
    new_cost_of_living = monthly_cost_of_living
    # Simulate the ending value of a portfolio with the historical returns of the S&P 500
    for j in range(n_years_remaining * 12):
        new_cost_of_living = new_cost_of_living * (1 + inflation)**(1/12)
        rand_return = data['Returns'].sample().iloc[0]
        
        if liquid_balance - new_cost_of_living > 0:
            liquid_balance = liquid_balance * (1 + short_term_interest_rate)**(1/12) - new_cost_of_living
        elif illiquid_balance - new_cost_of_living > 0:
            illiquid_balance = max(0, illiquid_balance * (1 + rand_return))
        else:
            # print(f'Failed to retire after {j+1} months')
            months_survived.append(j+1)
            break
        top_up_amount = (new_cost_of_living * 12 / (short_term_interest_rate - inflation) * (1 - ((1 + inflation) / (1 + short_term_interest_rate)) ** (n_years_liquid)) - liquid_balance)
        top_up_amount = min(illiquid_balance * rand_return, top_up_amount)
        if top_up_amount > 0 and rand_return > 0 and illiquid_balance > 0:
            liquid_balance = liquid_balance + min(top_up_amount, illiquid_balance * (1 + rand_return) - top_up_amount)
            illiquid_balance = max(0, illiquid_balance * (1 + rand_return) - top_up_amount)
        else:
            illiquid_balance = illiquid_balance * (1 + rand_return)
        # print(f'Month {j+1} liquid_balance: {liquid_balance}, illiquid_balance: {illiquid_balance}, rand_return: {rand_return}, top_up_amount: {top_up_amount}, monthly_cost_of_living: {new_cost_of_living}')
        if (liquid_balance + illiquid_balance) <= 0:
            # print(f'Failed to retire after {j+1} months')
            months_survived.append(j+1)
            break
        if j == n_years_remaining * 12 - 1:
            # print(f'Successfully retired after {j+1} months')
            months_survived.append(j+1)
            break

print(f'Average months survived: {np.mean(months_survived)}')
print(f'Median months survived: {np.median(months_survived)}')
print(f'95th percentile months survived: {np.percentile(months_survived, 95)}')
print(f'99th percentile months survived: {np.percentile(months_survived, 99)}')
print(f'Percent of simulations that failed: {len([x for x in months_survived if x < n_years_remaining * 12]) / n_simulations * 100}')
