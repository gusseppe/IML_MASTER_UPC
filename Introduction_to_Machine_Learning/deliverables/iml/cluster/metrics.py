import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.metrics import adjusted_rand_score 
from sklearn.metrics.cluster import contingency_matrix
from sklearn.metrics import davies_bouldin_score 
from sklearn.metrics import f1_score

from cluster.kmeans import KMeans
from cluster.kmodes import KModes
from cluster.kprototypes import KPrototypes
from cluster.fuzzycmeans import FuzzyCMeans


from sklearn.cluster import AgglomerativeClustering

affinity = ['euclidean', 'cosine']
linkage = ["complete", "average", "single"]


def get_clusterer(n_clusters, cat_features=[], alg='kmeans',
                  agglo_params=None, random_state=10):
    clusterer = None
    metric = ''
    # if len(cat_features) == 0:
    if alg == 'agglo':
        clusterer = AgglomerativeClustering(affinity=agglo_params[0], compute_full_tree='auto',
                                linkage=agglo_params[1], memory=None,
                                            n_clusters=n_clusters,
                                pooling_func='deprecated')
        metric = 'euclidean'
    elif alg == 'kmeans':
        clusterer = KMeans(n_clusters=n_clusters, random_state=random_state)
        metric = 'euclidean'
    elif alg == 'kmodes':
        clusterer = KModes(n_clusters=n_clusters, random_state=random_state)
        metric = 'manhattan'
    elif alg == 'fuzzy':
        clusterer = FuzzyCMeans(n_clusters=n_clusters, random_state=random_state)
        metric = 'euclidean'
# else:
    elif alg == 'kproto':
        clusterer = KPrototypes(n_clusters=n_clusters, cat_features=cat_features, random_state=random_state)
        metric = 'manhattan'

    return clusterer, metric


def silhouette(X, X_pca, cat_features=[],
               alg='kmeans', agglo_params=None,
               range_clusters=range(2, 5), random_state=10):
    """
        Function provided by sklearn with some modifications.
        Reference: https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
    """

    for n_clusters in range_clusters:
        # Create a subplot with 1 row and 2 columns
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        # clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        clusterer, metric = get_clusterer(n_clusters, cat_features,
                                          alg, agglo_params, random_state)
        clusterer.fit(X.values)
        if alg != 'agglo':
            cluster_labels = clusterer.labels
        else:
            cluster_labels = clusterer.labels_

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(X, cluster_labels, metric=metric)
        print("For n_clusters =", n_clusters,
              "The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        # 2nd Plot showing the actual clusters formed
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        ax2.scatter(X_pca.values[:, 0],
                    X_pca.values[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                    c=colors, edgecolor='k')

        if alg != 'agglo':
            # Labeling the clusters
            centers = clusterer.centroids
            # Draw white circles at cluster centers
            ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
                        c="white", alpha=1, s=200, edgecolor='k')

            for i, c in enumerate(centers):
                ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                            s=50, edgecolor='k')

        ax2.set_title("The visualization of the clustered data.")
        ax2.set_xlabel("Feature space for the 1st feature")
        ax2.set_ylabel("Feature space for the 2nd feature")

        plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                      "with n_clusters = %d" % n_clusters),
                     fontsize=14, fontweight='bold')

    plt.show()


def elbow(X, range_clusters=range(2, 6), alg='kmeans',
          cat_features=[], random_state=42):

    inertias = []
    ks = range_clusters
    model = None
    for k in ks:
        if alg == 'kmeans':
            model = KMeans(n_clusters=k, random_state=random_state)
        elif alg == 'kmodes':
            model = KMeans(n_clusters=k, random_state=random_state)
        else:
            model = KPrototypes(n_clusters=k, cat_features=cat_features, random_state=random_state)

        model.fit(X.values)
        # centroids_, clusters_, inertia_ = k_means(X_final.values, k=k)
        inertias.append(model.inertia)

    plt.plot(ks, inertias, '-o', color='black')
    plt.xlabel('number of clusters, k')
    plt.ylabel('inertia')
    plt.title(alg)
    plt.xticks(ks)
    plt.show()


def rename_labels(y_true, y_pred):
    from scipy.stats import mode
    mapping = {}
    for cat in set(y_true):
        predictions = y_pred[y_true == cat]
        predictions = [p for p in predictions if p not in list(mapping.values())]
        mapping[cat] = mode(predictions)[0][0]
    # print(mapping)

    result = y_pred.copy()
    for cat in set(y_true):
        result[y_pred == mapping[cat]] = cat
    return result


def get_metrics(y_true, y_pred, X=None, alg=None):
    def purity_score(y_true, y_pred):
        cm = contingency_matrix(y_true, y_pred)
        return np.sum(np.amax(cm, axis=0)) / np.sum(cm)

    d_metrics = dict()
    d_metrics['ars'] = adjusted_rand_score(y_true, y_pred)
    d_metrics['purity'] = purity_score(y_true, y_pred)
    d_metrics['db'] = davies_bouldin_score(X, y_pred)  # the lower the best
    n_classes = len(set(y_true))
    if n_classes > 2:
        d_metrics['f-measure'] = f1_score(y_true, rename_labels(y_true, y_pred), average='micro')
    elif  n_classes == 2:
        d_metrics['f-measure'] = f1_score(y_true, rename_labels(y_true, y_pred), average='binary')
        # d_metrics['f-measure'] = f1_score(y_true, y_pred, average='binary')
    else:
        print('n_classes must be greater than 1')

    if alg is not None and X is not None:
        if alg == 'kproto' or alg == 'kmodes':
            d_metrics['silhouette'] = silhouette_score(X, y_pred, metric='manhattan')
        else:
            d_metrics['silhouette'] = silhouette_score(X, y_pred, metric='euclidean')

    return d_metrics


