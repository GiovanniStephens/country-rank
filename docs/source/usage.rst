Usage
=====

Installation
------------

To use this code, you will need to clone the repository and install the dependencies:

.. code-block:: console
    
        $ git clone https://github.com/GiovanniStephens/country-rank.git
        $ cd country-rank
        $ pip install -r requirements.txt

Exploratory Data analysis (EDA)
-------------------------------

To run a quick exploratory data analysis, you will need to run the following command:

.. code-block:: console

        $ python EDA.py

This will print some basic statistics about the data, and will also generate a few plots in the `visualisations` directory.

Scraping the Data
-----------------

Cost of living data is scraped off Numbeo.com. There are several functions to get 
the data from the website. The data is then cleaned and used to estimate a cost of 
living distribution using a Monte Carlo simulation. This way, one can get a percentile 
for the cost of living.

I also scrape Numbeo.com indices to get pollution, health care, and crime data.
Climate data is scraped from weatherbase.com. 
The main scraper module is used to scrape all the data from the above sources.

To scrape the data, you will need to run the following command:

.. code-block:: console

        $ python get_data.py

It make take a while because it has to scrape data for each country. The data is saved in the `data` directory called `All Data by Country.csv`.

Clustering
----------

The clustering module is used to perform clustering on the country data. There are several utility functions to faciliated
the automated clustering process. You can use principal component analysis (PCA) or 
Uniform Manifold Approximation and Projection (UMAP) to
reduce the dimensionality of the data, and then use k-means or HDBSCAN to perform the clustering.

There are also functions to programmatically determine how many principal components to 
use. This is done by calculating the variance of the data for each number of components, and
then finding the point at which the variance begins to level off.


Estimate Cost to Retire
-----------------------

These two estimate module are used to estimate the cost to retire in a given country. It is calculated using a 
an estimated long-term purchasing power parity (PPP) change and a growing annuity to estimate.

To estimate the cost to retire in a country, you will need to run the following command:

.. code-block:: console

        $ python estimate_cost_to_retire.py

Note that all the parameters are manually defined in the script. You will need to change them to suit your needs.

The new estimate cost to retire is a step-wise simulation assuming a starting 
capital with an assumed cost of living, level of inflation, and time to death.
Using the S&P500 data, it goes month by month simulating a net worth until the end 
of the period. It ultimately prints the probability of success, which is the liklihood 
of not ending destitute. 

To run this simulation, you will need to run the following command:

.. code-block:: console

        $ python new_estimate_cost_to_retire.py

Note that all the parameters are manually defined in the script. You will need to change them to suit your needs.


Purchasing Power Parity (PPP) Conversion Rates
----------------------------------------------

Purchasing power parity conversion rates are taken from the worldbank.org website. 
The conversion rates are forecast to get a long-term view on how relative purchasing
poewr will chanve over time. The changes are relative to New Zealand, where I live. 
In essence, it is implicitly assumed that most of my investments will be denominated
in NZD and converted as needed (if I retire internationally).