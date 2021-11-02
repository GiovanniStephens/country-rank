import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import hdbscan
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
import estimate_cost_to_retire as retire

df = pd.read_csv('data/All Data by Country.csv')

# Head of the data
# print(df.head())

# Counts by column
df.count()


# Cleaned data to keep just the countries with enough data.
df = df[df.count(1)>=9]
countries = df['Country']
df = df.drop(['pop2019', 'Crime Index', 'Country'], axis=1)

# Impute missing datapoints using KNN.
imputer = KNNImputer(n_neighbors=2)
no_nulls = imputer.fit_transform(df)
no_nulls = pd.DataFrame(no_nulls, columns=df.columns)

# Basic data description
print(no_nulls.describe())

# Histograms for all the variables
no_nulls.hist(figsize=(16, 20), bins=20, xlabelsize=7, ylabelsize=7)
plt.savefig("visualisations/variable_distributions.png")
plt.clf()

# Correlation heatmap
corr = no_nulls.corr()
sns.heatmap(no_nulls.corr()[(corr >= 0.4) | (corr <= -0.4)], 
            cmap='viridis', vmax=1.0, vmin=-1.0, linewidths=0.1,
            annot=True, annot_kws={"size": 8}, square=True)
plt.savefig("visualisations/correlations_heatmap.png")
plt.clf()

# Regression plots for some of the stronger correlations.
sns.regplot(x=no_nulls['avg temp'],y='Pollution Index', data=no_nulls)
plt.savefig("visualisations/avg_temp_vs_pollution.png")
plt.clf()
sns.regplot(x=no_nulls['Cost of Living pw'],y='Pollution Index', data=no_nulls)
plt.savefig("visualisations/cost_vs_pollution.png")
plt.clf()
sns.regplot(x=no_nulls['Health Care Index'],y='Pollution Index', data=no_nulls)
plt.savefig("visualisations/health_care_vs_pollution.png")
plt.clf()
sns.regplot(x=no_nulls['Safety Index'],y='Pollution Index', data=no_nulls)
plt.savefig("visualisations/safety_vs_pollution.png")
plt.clf()
sns.regplot(x=no_nulls['min temp'],y='avg rainfall', data=no_nulls)
plt.savefig("visualisations/min_temp_vs_rainfall.png")
plt.clf()
sns.regplot(x=no_nulls['Cost of Living pw'],y='Health Care Index', data=no_nulls)
plt.savefig("visualisations/cost_vs_health_care.png")
plt.clf()

# Normalise the data
std_values = StandardScaler().fit_transform(no_nulls)

# Reduce the dimensionality to 2 dimensions
import clustering
# tsne = TSNE(n_components=2, perplexity=10, n_iter=4000)
# tsne_results = tsne.fit_transform(std_values)
tsne_results = clustering.reduce_dimensions_umap(std_values,5)

# Cluster the data

clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
clusterer.fit(tsne_results)
labels = clusterer.labels_
# labels = clustering.kmeans_clustering(tsne_results, num_clusters=10)
# color_palette = sns.color_palette('bright', labels.max()+1)
# cluster_colors = [color_palette[x] if x >= 0
#                   else (0.5, 0.5, 0.5)
#                   for x in labels]
# plt.scatter(*tsne_results.T, linewidth=0, c=cluster_colors, alpha=1, s=100)
# plt.savefig("visualisations/clusters.png")

# Outliers
threshold = pd.Series(clusterer.outlier_scores_).quantile(0.9)
print(countries[clusterer.outlier_scores_>threshold])

# NZ Cluster (you may need to change the cluster number to work out which one you like)
for i in range(labels.max()):
    print(f'Cluster {i}:')
    print(pd.merge(no_nulls[labels==i], countries.reset_index(), left_index=True, right_index=True))

no_nulls['Country'] = countries.reset_index()['Country']
no_nulls['Cluster'] = labels

potential_retirement_countries = ['Colombia', 'Spain', 'Portugal', 'Greece', 'South Korea', 'New Zealand', 'Georgia', 'Uruguay']
preferred_clusters = set(no_nulls[no_nulls['Country'].isin(potential_retirement_countries)]['Cluster'].values)
for preferred_cluster in preferred_clusters:
    for country in no_nulls[no_nulls['Cluster']==preferred_cluster].values:
        retirement_cost = retire.estimate_cost_to_retire(country[16],country[4],buffer_pa=0)
        country_name = country[16]
        print(f'The cost to retire in {country_name} is: {round(retirement_cost,2)}')
