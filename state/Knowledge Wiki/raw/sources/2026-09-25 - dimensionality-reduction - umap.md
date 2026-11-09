<!-- source: https://umap-learn.readthedocs.io/ | type: html | hash: c9fc0853a11a3df64f94fabb9a513ca4ab5c3f67ce1ff7921f4c486077b39138 | fetched: 2026-09-25T07:55:06Z -->

- UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction
View page source
# UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction
Uniform Manifold Approximation and Projection (UMAP) is a dimension reduction
technique that can be used for visualisation similarly to t-SNE, but also for
general non-linear dimension reduction. The algorithm is founded on three
assumptions about the data
- The data is uniformly distributed on Riemannian manifold;
- The Riemannian metric is locally constant (or can be approximated as such);
- The manifold is locally connected.
From these assumptions it is possible to model the manifold with a fuzzy
topological structure. The embedding is found by searching for a low dimensional
projection of the data that has the closest possible equivalent fuzzy
topological structure.
The details for the underlying mathematics can be found in
our paper on ArXiv:
McInnes, L, Healy, J, UMAP: Uniform Manifold Approximation and Projection
for Dimension Reduction, ArXiv e-prints 1802.03426, 2018
You can find the software on github.
Installation
Conda install, via the excellent work of the conda-forge team:
conda install -c conda-forge umap-learn
The conda-forge packages are available for linux, OS X, and Windows 64 bit.
PyPI install, presuming you have numba and sklearn and all its requirements
(numpy and scipy) installed:
pip install umap-learn
User Guide / Tutorial:
- How to Use UMAP
- Penguin data
- Digits data
- Basic UMAP Parameters
- n_neighbors
- min_dist
- n_components
- metric
- Plotting UMAP results
- Plotting larger datasets
- Interactive plotting, and hover tools
- Plotting connectivity
- Diagnostic plotting
- UMAP Reproducibility
- Transforming New Data with UMAP
- Inverse transforms
- Parametric (neural network) Embedding
- Defining your own network
- Saving and loading your model
- Plotting loss
- Parametric inverse_transform (reconstruction)
- Autoencoding UMAP
- Early stopping and Keras callbacks
- Additional important parameters
- Extending the model
- Citing our work
- Transforming New Data with Parametric UMAP
- New data with UMAP
- New data with Parametric UMAP
- Re-training Parametric UMAP with landmarks
- UMAP on sparse data
- A mathematical example
- A text analysis example
- UMAP for Supervised Dimension Reduction and Metric Learning
- UMAP on Fashion MNIST
- Using Labels to Separate Classes (Supervised UMAP)
- Using Partial Labelling (Semi-Supervised UMAP)
- Training with Labels and Embedding Unlabelled Test Data (Metric Learning with UMAP)
- Supervised UMAP on the Galaxy10SDSS dataset
- Using UMAP for Clustering
- Traditional clustering
- UMAP enhanced clustering
- Outlier detection using UMAP
- Combining multiple UMAP models
- MNIST digits example
- Diamonds dataset example
- Better Preserving Local Density with DensMAP
- Supervised DensMAP on the Galaxy10SDSS dataset
- Improving the Separation Between Similar Classes Using a Mutual k-NN Graph
- Visualizing the Results
- Citing our work
- Document embedding using UMAP
- Using raw counts
- Using TF-IDF
- Potential applications
- Embedding to non-Euclidean spaces
- Plane embeddings
- Spherical embeddings
- Embedding on a Custom Metric Space
- A Practical Example
- Bonus: Embedding in Hyperbolic space
- How to use AlignedUMAP
- Online updating of aligned embeddings
- Aligning varying parameters
- AlignedUMAP for Time Varying Data
- Processing Congressional Voting Records
- Applying AlignedUMAP
- Visualizing the Results
- Precomputed k-nn
- Practical Uses
- Reproducibility
- Performance Comparison of Dimension Reduction Implementations
- Performance scaling by dataset size
- Release Notes
- What’s new in 0.5
- What’s new in 0.4
- What’s new in 0.3
- What’s new in 0.2
- Frequently Asked Questions
- Should I normalise my features?
- Can I cluster the results of UMAP?
- The clusters are all squashed together and I can’t see internal structure
- I ran out of memory. Help!
- UMAP is eating all my cores. Help!
- Is there GPU or multicore-CPU support?
- Can I add a custom loss function?
- Is there support for the R language?
- Is there a C/C++ implementation?
- I can’t get UMAP to run properly!
- What is the difference between PCA / UMAP / VAEs?
- How UMAP can go wrong
- Successful use-cases
Background on UMAP:
- How UMAP Works
- Topological Data Analysis and Simplicial Complexes
- Adapting to Real World Data
- Finding a Low Dimensional Representation
- The UMAP Algorithm
- Performance Comparison of Dimension Reduction Implementations
- Performance scaling by dataset size
Examples of UMAP usage
- Interactive Visualizations
- UMAP Zoo
- Tensorflow Embedding Projector
- PixPlot
- UMAP Explorer
- Audio Explorer
- Orion Search
- Exploring Fashion MNIST
- ESM Metagenomic Atlas
- Exploratory Analysis of Interesting Datasets
- Prime factorizations of numbers
- Structure of Recent Philosophy
- Language, Context, and Geometry in Neural Networks
- Activation Atlas
- Open Syllabus Galaxy
- Scientific Papers
- The single-cell transcriptional landscape of mammalian organogenesis
- A lineage-resolved molecular atlas of C. elegans embryogenesis at single-cell resolution
- Exploring Neural Networks with Activation Atlases
- TimeCluster: dimension reduction applied to temporal data for visual analytics
- Dimensionality reduction for visualizing single-cell data using UMAP
- Revealing multi-scale population structure in large cohorts
- Understanding Vulnerability of Children in Surrey
API Reference:
- UMAP API Guide
- UMAP
- UMAP
- UMAP.fit()
- UMAP.fit_transform()
- UMAP.inverse_transform()
- UMAP.set_fit_request()
- UMAP.set_transform_request()
- UMAP.transform()
- ParametricUMAP
- Useful Functions
- compute_membership_strengths()
- discrete_metric_simplicial_set_intersection()
- fast_intersection()
- fast_metric_intersection()
- find_ab_params()
- fuzzy_simplicial_set()
- init_graph_transform()
- init_transform()
- make_epochs_per_sample()
- nearest_neighbors()
- raise_disconnected_warning()
- reset_local_connectivity()
- simplicial_set_embedding()
- smooth_knn_dist()
# Indices and tables
- Index
- Module Index
- Search Page
