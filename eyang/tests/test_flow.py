"""Flot maximum et coupe minimale."""

def test_flot_a_vers_f(petit):
    from src.flow import ford_fulkerson

    resultat = ford_fulkerson(petit, "A", "F")
    assert resultat["valeur"] == 13
    assert resultat["capacite_coupe"] == 13
    assert {(a, b) for a, b, _c in resultat["coupe"]} == {("B", "D"), ("C", "E")}
    chemins = [(tuple(chemin), debit) for chemin, debit in resultat["chaines"]]
    assert chemins == [
        (("A", "B", "D", "F"), 7),
        (("A", "C", "E", "F"), 5),
        (("A", "C", "E", "D", "F"), 1),
    ]
