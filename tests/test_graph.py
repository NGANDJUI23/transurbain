import numpy as np
from graph import Graph, Edge


def test_adjacency_matrix():
    g = Graph(directed=True)
    g.add_edge(Edge("A", "B", 3, 5, 10))
    g.add_edge(Edge("B", "C", 2, 2, 4))
    M, idx = g.adjacency_matrix()
    assert M[idx["A"], idx["B"]] == 3
    assert M[idx["B"], idx["A"]] == np.inf
    assert M[idx["A"], idx["A"]] == 0


def test_reversed():
    g = Graph(directed=True)
    g.add_edge(Edge("A", "B", 1, 1, 0))
    gr = g.reversed()
    assert [e.target for e in gr.neighbors("B")] == ["A"]