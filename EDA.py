import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import hdbscan
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler


df = pd.read_csv('data/All Data by Country.csv')

# Head of the data
print(df.head())

# Counts by column
df.count()

# Cleaned data to keep just countries that have all their data.
no_nulls = df.dropna()
countries = no_nulls['Country']
no_nulls = no_nulls.drop(['pop2019', 'Crime Index', 'Country'], axis=1)

# Basic data description
print(no_nulls.describe())

# Histograms for all the variables
no_nulls.hist(figsize=(16, 20), bins=20, xlabelsize=7, ylabelsize=7)
plt.savefig("visualisations/variable_distributions.png")
plt.clf()

# Correlation heatmap
corr = no_nulls.corr()
sns.heatmap(no_nulls.corr()[(corr >= 0.5) | (corr <= -0.4)], 
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
tsne = TSNE(n_components=2, perplexity=10, n_iter=4000)
tsne_results = tsne.fit_transform(std_values)

# Cluster the data
clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
clusterer.fit(std_values)
color_palette = sns.color_palette('deep', clusterer.labels_.max()+1)
cluster_colors = [color_palette[x] if x >= 0
                  else (0.5, 0.5, 0.5)
                  for x in clusterer.labels_]
# cluster_member_colors = [sns.desaturate(x, p) for x, p in
#                          zip(cluster_colors, clusterer.probabilities_)]
plt.scatter(*tsne_results.T, linewidth=0, c=cluster_colors, alpha=0.25)
plt.savefig("visualisations/clusters.png")

# Outliers
threshold = pd.Series(clusterer.outlier_scores_).quantile(0.9)
print(countries[clusterer.outlier_scores_>threshold])

# NZ Cluster (you may need to change the cluster number to work out which one you like)
print(pd.merge(no_nulls[clusterer.labels_==4], countries, left_index=True, right_index=True))
