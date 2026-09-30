from graph import Graph, Edge
from exploration import (bfs, dfs, weak_components,
                         strongly_connected_components, is_weakly_connected)


def make_graph():
    g = Graph(directed=True)
    for u, v in [("A","B"),("B","C"),("C","A"),("C","D")]:
        g.add_edge(Edge(u, v, 1, 1, 0))
    return g


def test_bfs_dfs_visit_all():
    g = make_graph()
    assert set(bfs(g, "A")) == set(g.vertices)
    assert set(dfs(g, "A")) == set(g.vertices)


def test_weak_components():
    g = make_graph()
    assert is_weakly_connected(g)


def test_scc():
    g = make_graph()
    comps = strongly_connected_components(g)
    scc_sets = [set(c) for c in comps]
    assert {"A", "B", "C"} in scc_sets
    assert {"D"} in scc_sets