# Overview

This is a quick hack-together project to identfy which countries would be good condidates for retirement. I collect data from various sources and then use it to build a model to predict which countries would be good candidates for retirement.

This project includes clustering, time series forecasting, and simulation. <b>Full documentation found [here](https://country-rank.readthedocs.io/en/latest/index.html)</b>.

I chose to include data for several deciding factors that were important to me in a country for retirement.

# Deciding Factors

1. Cost of living by country
2. Climate
3. Population density
4. Safety
5. Corruption
6. Healthcare
7. Air purity
8. Country freedom
9. Forecast change in puchasing power parity (PPP)
10. Estimated amount required to retire comfortably. 

# Approach

I cluster the countries based on their characteristics to find groups of countries that are similar. 

From what I know, I loved Spain. With that knowledge, I can pick the cluster of similar countries like Spain. These represent a set of candidate countries with attractive attributes.

From that subset of countries, I can estimate the required savings to retire in said countries. This estimate is calculated as the present value of a growing annuity. 

The growing annuity has the following input parameters:
1. Duration (i.e. the length of the annuity);
2. The starting cash flow (i.e. the cost of living at this current time.);
3. The long-term investment returns rate after expenses;
4. The growth rate of the cash flow.


### Duration
The duration is is calculated as the duration of the remainder of our life expectancy. For example, if I am 30 years old and my life expectancy is 95, I have 65 years left to live. This is the duration of the annuity.

### Cash Flow
The starting cash flow is the estimated cost of living in the country. It is calculated as the 90th percentitle of the cost of living in the country. There is also a cost of living buffer added into the cost of living to account for unexpected lifestyle creap.

### Return on Investment
The expected return on investments is assumed to be around 5% (this is conversative to ensure we are not underestimating the cost to retire).  

### Growth Rate
The growth rate is the forecast long-term change in purchasing power (PPP) between NZ and said country (assuming investments are denominated in NZD). This is an estimate that includes both inflation and FX changes for both NZ and the country. (A good explanation of PPP can be found [here](https://ourworldindata.org/what-are-ppps)).

# Data Sources:

| Factor | Data Source |
| --- | --- |
| Cost of living by country | [www.numbeo.com](numbeo.com)| 
| Climate | [www.weatherbase.com](www.weatherbase.com) |
| Population density | [www.infoplease.com](https://www.infoplease.com/world/population/population-density-square-mile-countries) |
| Safety | [www.numbeo.com](numbeo.com) |
| Corruption | [www.transparency.org/en/cpi/2020](https://www.transparency.org/en/cpi/2020) |
| Healthcare | [www.numbeo.com](numbeo.com) |
| Air purity | [www.numbeo.com](numbeo.com) |
| Country freedom | [freedomhouse.org](https://freedomhouse.org/) |
| PPP conversion factors | [data.Worldbank.org](https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm) |

# Articles

I wrote a couple of articles with findings from the project. You can find there posted below: 

https://www.linkedin.com/pulse/planning-retirement-shortcut-giovanni-stephens/
https://www.linkedin.com/pulse/where-retire-exploratory-analysis-giovanni-stephens/

# Brief Findings

- Spain and Portugal are two really nice countries for retirement for the following reasons:
    - Their climate is not too hot nor too cold. 
    - They are both relatively safe. 
    - (Though not included in this repo) they are not very corrupt.
    - They are cheaper than New Zealand. 
- Georgia is another country that came up for the following reasons:
    - Not too hot nor too cold. 
    - Not too populated.
    - Very good cost of living.
    - Quite safe.
    - A little politically unstable?
    - Not so many freedoms as first world countries.
- There are quite a few options in South America if one is willing to put up with a little more danger and corruption. 
- South American countries are quite cheap relative to the rest of the world. 
- With how purchasing power is changing as well as the cost of living, Uruguay seems like a great place. 
    - Nice climate. 
    - Common language. 
    - Safe.
    - Free.
    - Pretty good health care and education.
    - Really nice people I think. 

# Future work

There are quite a few other datasets out there that could help inform the decisions. I, currently, do not know what other data I would to include, but some options are below: 
- Ratings of the country by people online;
- Percieved risks by country;
- Percieved 'quality' of the people in these countries.

# Todos
- I need to update the purchasing power conversion rates. Perhaps this could be automated.
- It would be cool to track retirement cost over time in a dashboard. 
