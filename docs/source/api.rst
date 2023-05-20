API
===

Scraping Cost of Living
-----------------------

.. autofunction:: scrape_cost_of_living.get_cost_of_living_table
.. autofunction:: scrape_cost_of_living.clean_numbeo_table
.. autofunction:: scrape_cost_of_living.check_enough_data
.. autofunction:: scrape_cost_of_living.get_country_cost_of_living
.. autofunction:: scrape_cost_of_living.get_city_cost_of_living
.. autofunction:: scrape_cost_of_living.get_cost_of_living
.. autofunction:: scrape_cost_of_living.get_numbeo_countries
.. autofunction:: scrape_cost_of_living.main


Scraping Indices
----------------

.. autofunction:: scrape_numbeo_indices.scrape_index
.. autofunction:: scrape_numbeo_indices.to_pandas_df


Scraping Climate Data
---------------------

.. autofunction:: scrape_temperatures.f_to_c
.. autofunction:: scrape_temperatures.in_to_mm
.. autofunction:: scrape_temperatures.check_float
.. autofunction:: scrape_temperatures.get_stats
.. autofunction:: scrape_temperatures.get_country_stats
.. autofunction:: scrape_temperatures.main


Main Scraper Module
-------------------

.. autofunction:: scrape_urls.get_table
.. autofunction:: scrape_urls.find_html_class
.. autofunction:: scrape_urls.find_in_html
.. autofunction:: scrape_urls.find_id_in_html
.. autofunction:: scrape_urls.proxy_generator
.. autofunction:: scrape_urls.scrape_page
.. autofunction:: scrape_urls.multi_thread_func


Clustering
----------

.. autofunction:: clustering.reduce_dimensions_pca
.. autofunction:: clustering.reduce_dimensions_umap
.. autofunction:: clustering.shuffle
.. autofunction:: clustering.single_sample_t_test
.. autofunction:: clustering.calc_perm_variance
.. autofunction:: clustering.get_optimal_n_components
.. autofunction:: clustering.kmeans_clustering
.. autofunction:: clustering.hdbscan_clustering

Estimate Cost to Retire
-----------------------

.. autofunction:: estimate_cost_to_retire.estimate_cost_to_retire

.. autofunction:: new_estimate_cost_to_retire.main


Purchasing Power Parity (PPP) Conversion Rates
----------------------------------------------

.. autofunction:: predict_PPP.estimate_PPP_conversion_rate_long_term_change