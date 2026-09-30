from graph import Graph, Edge
from mst import kruskal, prim


def make_graph():
    g = Graph(directed=False)
    for u, v, w in [("A","B",1),("B","C",2),("A","C",3),("C","D",4),("B","D",5)]:
        g.add_edge(Edge(u, v, w, w, 0))
    return g


def test_kruskal_prim_same_weight():
    g = make_graph()
    _, tk = kruskal(g)
    _, tp = prim(g)
    assert abs(tk - tp) < 1e-9
    assert abs(tk - 7) < 1e-9   # 1 + 2 + 4


def test_mst_edge_count():
    g = make_graph()
    m, _ = kruskal(g)
    assert len(m) == g.nb_vertices() - 1