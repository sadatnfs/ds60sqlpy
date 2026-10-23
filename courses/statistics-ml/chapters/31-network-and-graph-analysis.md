# 31. Network and Graph Analysis

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-031`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A graph represents entities and their relationships. The scientific question determines what counts as a node, an edge and an observation window. A payment graph, a friendship graph and a server-dependency graph can share the same mathematical representation while supporting very different interpretations. Missing edges may mean no relationship, unobserved relationship or relationship outside the collection system.

### Begin with the representation contract

For n nodes, an adjacency matrix A has entry A_ij describing an edge from i to j. An undirected graph uses a symmetric matrix; a directed graph distinguishes incoming and outgoing relations. Edge weights may represent counts, distances, probabilities or signed relationships, and algorithms do not interpret those interchangeably. Self-loops, duplicate edges and changes over time must be handled explicitly. Sparse matrices are often essential because most possible node pairs have no observed edge.

### Centrality is a question, not one number

Degree measures immediate connections. Betweenness measures participation in chosen shortest paths. Eigenvector-style scores reward connection to influential neighbors. Each answers a different operational question. A node can be a low-degree bridge between communities and therefore important for connectivity while having modest popularity. Before ranking, state the assumed flow, direction and edge meaning that make the selected centrality useful.

PageRank illustrates a probabilistic interpretation. With row-stochastic transition matrix P, damping alpha and teleportation distribution v, the stationary score satisfies \(r=\alpha P^{\mathsf T}r+(1-\alpha)v\). Teleportation avoids trapping all mass in isolated closed components under standard positive-support choices. A dangling node with no outgoing links requires an explicit transition rule. The score is a stationary visitation probability under this constructed walk, not an intrinsic moral or causal importance measure.

### Prediction requires a time boundary

Link prediction should construct features from the graph as it existed at the decision time. Computing embeddings or common-neighbor counts on a later complete graph can reveal the test links. Negative examples also require care: an unobserved pair may become positive later, and sampling easy distant pairs can inflate performance. Evaluate on the candidate population actually served, with a temporal holdout when links evolve.

### Association, diffusion and interference

Neighbors often resemble one another because people choose similar neighbors, share environments or influence one another. Observational clustering cannot identify which explanation dominates. An intervention assigned to one node may affect neighboring outcomes, violating an independent-unit treatment model. Exposure mappings, randomization design and network measurement therefore become part of causal identification. The numerical examples below explain graph mechanics, while the method discussions distinguish those mechanics from claims about social or operational influence.

## Methods, mechanisms, and limits

### stat-31-01

**Graph representations**

A graph representation chooses nodes, directed or undirected edges, weights and time support. An adjacency list is efficient for sparse traversal, while a matrix supports linear algebra. Multiple interactions can be stored as separate edges or aggregated counts, producing different models. A projection from a bipartite graph can create dense apparent relationships that reflect shared membership rather than direct interaction.

### stat-31-02

**Degree distributions**

A degree distribution summarizes how many connections nodes have, with in-degree and out-degree separate for directed graphs. A heavy-tailed histogram does not by itself establish a power law. Sampling high-activity nodes or missing low-degree nodes can distort the distribution. Degree also depends on the observation window, so compare like-for-like exposure periods before claiming a structural network change.

### stat-31-03

**Centrality measures**

Centrality measures encode different notions of importance: degree counts local links, closeness summarizes distances, betweenness counts shortest-path mediation, and eigenvector scores propagate neighbor importance. Disconnected graphs and weighted-edge semantics require specific conventions. Choose the measure from a plausible mechanism of communication, failure or influence, and test whether its ranking remains stable under reasonable missing-edge or time-window changes.

### stat-31-04

**PageRank**

PageRank is the stationary distribution of a random walk with teleportation. A damping factor controls the balance between following links and restarting from a chosen distribution. Dangling nodes need a valid transition row so mass is conserved. Convergence and normalization can be checked numerically, but the ranking remains conditional on edge direction, weight construction and teleportation assumptions.

### stat-31-05

**Community detection**

Community detection groups nodes with a specified pattern of connectivity, often dense within-group and sparse between-group links. Different algorithms optimize different objectives and can find overlapping or hierarchical structure. A detected partition is not automatically a real social category. Compare stability across seeds, resolutions and perturbed edges, and use domain evidence before assigning substantive labels.

### stat-31-06

**Modularity**

Modularity compares observed within-community edge weight with a degree-based null expectation. Optimizing it can find useful partitions but has resolution limits and many near-optimal solutions. High modularity is not proof that one partition is uniquely correct. The null model, directed/weighted treatment and resolution parameter change what counts as an unexpectedly dense group.

### stat-31-07

**Stochastic block models**

A stochastic block model assigns nodes to latent groups and specifies edge probabilities by group pair. It can represent assortative communities, disassortative patterns or core-periphery structure. Basic versions assume conditional edge independence given groups and parameters. Model selection for group count and uncertainty in assignments matter; a crisp displayed partition can hide substantial ambiguity.

### stat-31-08

**Degree-corrected block models**

Degree-corrected block models add node-specific propensity parameters so high-degree nodes need not be placed in separate groups solely because they are active. This separates degree heterogeneity from block interaction patterns. Identifiability constraints and sparse data affect estimation. The correction improves flexibility but does not eliminate dependence among edges or solve missing-network sampling bias.

### stat-31-09

**Latent-space network models**

Latent-space models place nodes in an unobserved geometric space where distance or inner products govern edge probabilities. Nearby latent positions can summarize similarity or affinity. The geometry is identifiable only up to transformations such as rotation under common models, so individual coordinates lack unique meaning. A low-dimensional visualization can omit important structure and should not be treated as an observed map.

### stat-31-10

**Exponential random graph models**

Exponential random graph models assign probabilities proportional to \(\exp\bigl(\theta^{\mathsf T}g(\mathrm{graph})\bigr)\), where statistics g can count edges, triangles or other configurations. They model dependence between edges through global graph features. Some specifications exhibit degeneracy, concentrating probability on nearly empty or complete graphs. Simulation-based fit checks and a substantively justified statistic set are essential.

### stat-31-11

**Link prediction**

Link prediction estimates which candidate pairs will form or reveal an edge. Common neighbors, node attributes and embeddings provide different signals. Build all features from the graph available before the outcome period, and define negatives from the actual candidate set. A random split of existing edges can test reconstruction rather than the future-link problem intended for deployment.

### stat-31-12

**Graph embeddings**

Graph embeddings map nodes or subgraphs to vectors that preserve selected structural relationships. Random-walk, matrix-factorization and learned approaches optimize different notions of similarity. Transductive embeddings may not naturally handle new nodes, and training on the full graph can leak held-out links. Evaluate downstream utility and stability, not just an appealing two-dimensional visualization.

### stat-31-13

**Graph neural networks**

Graph neural networks update node representations by aggregating messages from neighbors and transforming them through learned functions. Multiple layers increase the neighborhood receptive field but can oversmooth representations or compress too much distant information. Neighbor sampling, edge features and graph direction affect the model. A learned message-passing architecture does not automatically distinguish causal influence from homophily.

### stat-31-14

**Network diffusion models**

Network diffusion models describe how information, behavior or failure spreads through edges, using mechanisms such as independent cascades or threshold activation. Edge influence probabilities and timing assumptions determine the simulated cascade. Fitting observed spread requires separating exposure opportunity from adoption and shared causes. A simulator calibrated to aggregate cascade size may still misrepresent who is affected and when.

### stat-31-15

**Hawkes processes**

A Hawkes process models event intensity as a baseline plus contributions from prior events, often with decaying kernels. In a multivariate form, cross-excitation can describe event sequences across nodes or categories. Stability conditions constrain total excitation. Self-excitation is a statistical temporal mechanism; unmodeled common shocks can mimic it, so inferred triggering should not automatically be interpreted causally.

### stat-31-16

**Network interference models**

Network interference models allow a unit's outcome to depend on treatments assigned to neighbors. An exposure mapping summarizes which aspects of others' assignments matter, and the estimand can separate direct from spillover effects. Identification depends on the randomization or observational design and network measurement. Ignoring interference can change both the target effect and the valid uncertainty calculation.

### stat-31-17

**Graph sampling bias**

Graph sampling bias arises when observed nodes or edges are selected through crawls, referrals, activity thresholds or incomplete instrumentation. High-degree nodes are often more likely to be seen, and missing edges alter centrality and communities. Document the sampling process and use design-aware methods when possible. A larger observed graph does not automatically become representative of the intended network.

## Worked Python demonstrations

Complete offline program: [chapter_31.py](../examples/chapter_31.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_31.py
```

### Verify the graph before ranking it

The undirected example has a triangle plus one leaf. Degrees [2,2,3,1] sum to eight, twice the four undirected edges. Symmetry and the degree-sum identity catch common direction or duplicate-count mistakes. Node two is highly connected, but a different operational importance question could require a different centrality.

### Preserve probability mass at a dangling node

The directed example gives its dangling node a uniform transition row. Every row of P sums to one, and the iterated PageRank sums to one with a fixed-point residual below numerical tolerance. The test checks the actual stationary equation rather than only whether a vector was returned.

### Keep the future edge out of its features

At prediction time, nodes zero and two are not connected but share node one as a neighbor. Their common-neighbor feature is one. Adding their later edge to a separate matrix leaves the past graph unchanged. Real evaluations need the same temporal isolation for embeddings and all derived structural features.

### Complete executable example

```python
import numpy as np

def graph_bookkeeping():
    a=np.array([[0.,1.,1.,0.],[1.,0.,1.,0.],[1.,1.,0.,1.],[0.,0.,1.,0.]])
    degree=a.sum(axis=1)
    assert np.array_equal(a,a.T) and degree.tolist()==[2.,2.,3.,1.]
    assert degree.sum()==2*4
    print("Undirected degrees:",degree,"edges:",degree.sum()/2)

def pagerank():
    a=np.array([[0.,1.,0.,0.],[0.,0.,1.,0.],[1.,0.,0.,1.],[0.,0.,0.,0.]])
    p=np.zeros_like(a)
    for i,row in enumerate(a):p[i]=row/row.sum() if row.sum() else np.full(4,.25)
    r=np.full(4,.25);alpha=.85
    for _ in range(200):r=alpha*p.T@r+(1-alpha)*np.full(4,.25)
    residual=np.max(np.abs(r-(alpha*p.T@r+(1-alpha)*np.full(4,.25))))
    assert np.allclose(p.sum(axis=1),1.) and np.isclose(r.sum(),1.) and residual<1e-12
    assert r[2]>r[0]
    print("PageRank:",r,"fixed-point residual:",residual)

def past_only_link_feature():
    past=np.array([[0,1,0],[1,0,1],[0,1,0]])
    common=int(past[0]@past[2])
    assert common==1 and past[0,2]==0
    future=past.copy();future[0,2]=future[2,0]=1
    assert future[0,2]==1 and past[0,2]==0
    print("Past common neighbors for future pair (0,2):",common)

def main():
    graph_bookkeeping();pagerank();past_only_link_feature()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Which centrality should identify critical infrastructure?** Start with the failure or flow mechanism. Degree may describe local load, betweenness possible routing bottlenecks, and reachability impact consequences of removal. Validate against the operational objective rather than declaring one centrality universally best.

**Interview: Why can graph evaluation leak without using the label column?** Structural features or embeddings computed on a later graph can encode the held-out edge or its downstream consequences. The complete graph construction and feature pipeline must respect the prediction timestamp.

**Interview: Does neighbor similarity prove influence?** No. Homophily, shared environments and sampling can create the same association. Influence requires a design or identifying assumptions that separate these mechanisms, often while accounting for interference.

## Primary sources and official APIs

- [NetworkX PageRank reference and original-paper citations](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html)

- [Kipf and Welling, Semi-Supervised Classification with Graph Convolutional Networks](https://arxiv.org/abs/1609.02907)

## Reading connections

[Previous chapter](30-spatial-and-spatiotemporal-statistics.md) | [Book contents](../README.md) | [Next chapter](32-recommendation-information-retrieval-and-ranking.md)
