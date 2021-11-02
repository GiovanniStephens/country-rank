# Overview

This repository contains a quick hack-together of a data collection to identfy which countries would be good condidates for retirement. 

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

Based on the above factors, I cluster countries based on their characteristics. From what information I know, (e.g. I loved Spain for its culture, cost, stability, and climate) I can pick the cluster of like countries that is most attractive. From that subset of countries, I can estimate the required savings to retire in said countries. This estimate is calculated as the present value of a growing annuity that is of the duration of the remainder of our life expectancy plus moving costs and a buffer. The payment is a 99th percentile lifestyle cost of living for Hanna and me. The expected return r would be around 5% plus the forecast long-term change in purchasing power between NZ and said country (assuming investments are denominated in NZD). 

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
| PPP conversion factors | [data.Worldbank.org](https://data.worldbank.org/indicator/PA.NUS.PPP) |


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
- Percieved quality of the people in these countries.