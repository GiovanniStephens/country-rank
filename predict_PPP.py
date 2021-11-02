import pmdarima as pmd
import pandas as pd
import pycountry

# Import the data
conversion_rates = pd.read_csv('data/Purchasing Power Parity Conversion Rates.csv')

# Clean up the data
std_country_names = []
for country in conversion_rates['Country Name']:
    try:
        std_country_names.append(pycountry.countries.search_fuzzy(country)[0].name)
    except:
        std_country_names.append(country)
conversion_rates['std country names'] = std_country_names
conversion_rates = conversion_rates.set_index('std country names')
conversion_rates = conversion_rates.drop('Country Name', axis=1)

# Drop countries that do not have enough conversion rates
filtered_conversion_rates = conversion_rates[conversion_rates.count(1)>=20]


def estimate_PPP_conversion_rate_long_term_change(country):
    # Take an input country
    try:
        std_country = pycountry.countries.search_fuzzy(country)[0].name
    except:
        std_country = country

    ts = filtered_conversion_rates[filtered_conversion_rates.index == std_country]

    if ts.shape[0]>0:
        # Fit a model
        ts = ts.iloc[-1].dropna()
        autoarima_model = pmd.auto_arima(ts.transpose(),start_p=0,start_q=0,test="adf",trace=False)

        n_periods = 10

        # forecast the PPP conversion rate
        prediction = autoarima_model.predict(n_periods)

        # Return the long-term average
        return (prediction[0]/prediction[-1])**(1/n_periods) - 1
    else:
        return 0 # No result.

if __name__ == '__main__':
    print(estimate_PPP_conversion_rate_long_term_change('South Korea'))