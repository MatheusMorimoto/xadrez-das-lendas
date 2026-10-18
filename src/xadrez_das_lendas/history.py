"""Persistencia local e classificacao das partidas tradicionais."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MatchRecord:
    played_at: str
    white_player: str
    black_player: str
    result: str
    winner: str | None
    moves: tuple[str, ...]

    @classmethod
    def create(
        cls,
        white_player: str,
        black_player: str,
        result: str,
        winner: str | None,
        moves: list[str],
    ) -> MatchRecord:
        return cls(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            white_player,
            black_player,
            result,
            winner,
            tuple(moves),
        )


def default_history_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / "XadrezDasLendas" / "historico_partidas.json"


class HistoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_history_path()

    def load(self) -> list[MatchRecord]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return [MatchRecord(**{**item, "moves": tuple(item["moves"])}) for item in data]
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            return []

    def append(self, record: MatchRecord) -> None:
        records = self.load()
        records.append(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(item) for item in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def leaderboard(records: list[MatchRecord]) -> list[tuple[str, int, int]]:
    scores: dict[str, list[int]] = {}
    for record in records:
        for player in (record.white_player, record.black_player):
            scores.setdefault(player, [0, 0])[1] += 1
        if record.winner is not None:
            scores.setdefault(record.winner, [0, 0])[0] += 1
    return sorted(
        ((name, values[0], values[1]) for name, values in scores.items()),
        key=lambda item: (-item[1], -item[2], item[0]),
    )
