from xadrez_das_lendas.history import HistoryStore, MatchRecord, leaderboard


def test_history_is_persisted_and_loaded(tmp_path):
    store = HistoryStore(tmp_path / "history.json")
    record = MatchRecord.create("Você", "Máquina", "Xeque-mate", "Você", ["1. Brancas: e2 -> e4"])

    store.append(record)

    assert store.load() == [record]


def test_leaderboard_orders_players_by_wins_then_games():
    records = [
        MatchRecord.create("Ana", "Bia", "Xeque-mate", "Ana", []),
        MatchRecord.create("Bia", "Ana", "Empate", None, []),
        MatchRecord.create("Ana", "Máquina", "Xeque-mate", "Máquina", []),
    ]

    assert leaderboard(records) == [
        ("Ana", 1, 3),
        ("Máquina", 1, 1),
        ("Bia", 0, 2),
    ]
