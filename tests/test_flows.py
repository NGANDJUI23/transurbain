from graph import Graph, Edge
from flows import ford_fulkerson, min_cut


def make_graph():
    g = Graph(directed=True)
    for u, v, c in [("S","A",10),("S","B",10),("A","B",2),("A","T",8),("B","T",9)]:
        g.add_edge(Edge(u, v, 1, 1, c))
    return g


def test_max_flow_value():
    g = make_graph()
    val, *_ = ford_fulkerson(g, "S", "T")
    assert val == 17


def test_min_cut_value_equals_flow():
    g = make_graph()
    val, _, _, _ = min_cut(g, "S", "T")
    assert val == 17


def test_min_cut_partition():
    g = make_graph()
    val, S, T, cut = min_cut(g, "S", "T")
    assert "S" in S and "T" in T
    assert sum(c for _, _, c in cut) == val