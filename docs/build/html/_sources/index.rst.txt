.. Country Rank documentation master file, created by
   sphinx-quickstart on Sat May 20 17:15:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Country Rank's documentation!
========================================

**Country Rank** is a Python project performing an exploratory data analysis (EDA)
to cluster countries based on their characteristics. This was an exercise to try to find 
like countries to New Zealand (where I live) and other nice places that are cheaper to retire. 

This project includes clustering, time series forecasting, and simulation. 

I chose to include data for several deciding factors that were important to me in a country for retirement.

**Deciding Factors**

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

**Approach**

I cluster the countries based on their characteristics to find groups of countries that are similar. 

From what I know, I loved Spain. With that knowledge, I can pick the cluster of similar countries like Spain. These represent a set of candidate countries with attractive attributes.

From that subset of countries, I can estimate the required savings to retire in said countries. This estimate is calculated as the present value of a growing annuity. 

The growing annuity has the following input parameters:

1. Duration (i.e. the length of the annuity);
2. The starting cash flow (i.e. the cost of living at this current time.);
3. The long-term investment returns rate after expenses;
4. The growth rate of the cash flow.


*Duration*

The duration is is calculated as the duration of the remainder of our 
life expectancy. For example, if I am 30 years old and my life 
expectancy is 95, I have 65 years left to live. 
This is the duration of the annuity.

*Cash Flow*

The starting cash flow is the estimated cost of living in the country. 
It is calculated as the 90th percentitle of the cost of living in the 
country. There is also a cost of living buffer added into the cost of 
living to account for unexpected lifestyle creap.

*Return on Investment*

The expected return on investments is assumed to be around 5% 
(this is conversative to ensure we are not underestimating the cost to retire).  

*Growth Rate*

The growth rate is the forecast long-term change in purchasing power (PPP) 
between NZ and said country (assuming investments are denominated in NZD). 
This is an estimate that includes both inflation and FX changes for 
both NZ and the country. (A good explanation of PPP can be found `here`_).

.. _here: https://ourworldindata.org/what-are-ppps

**Data Sources**

* Cost of living by country | https://www.numbeo.com 
* Climate | https://www.weatherbase.com
* Population density | https://www.infoplease.com/world/population/population-density-square-mile-countries
* Safety | https://www.numbeo.com
* Corruption | https://www.transparency.org/en/cpi/2020
* Healthcare | https://www.numbeo.com
* Air purity | https://www.numbeo.com
* Country freedom | https://www.freedomhouse.org
* PPP conversion factors | https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Contents
--------

.. toctree::

   usage
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
