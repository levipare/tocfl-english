import gzip
from dataclasses import dataclass
from typing import TextIO


@dataclass(frozen=True)
class Entry:
    traditional: str
    simplified: str
    pinyin: str
    definitions: list[str]


class CcCedict:
    def __init__(self, cccedict_gzip_file: str) -> None:
        self.entries: list[Entry] = []
        self.simplified_to_index: dict[str, int] = {}
        self.traditional_to_index: dict[str, int] = {}

        with gzip.open(cccedict_gzip_file, mode="rt", encoding="utf-8") as file:
            self._parse_file(file)

    def get_definitions(self, chinese: str) -> list[str] | None:
        entry = self.get_entry(chinese)
        return None if entry is None else entry.definitions

    def get_pinyin(self, chinese: str) -> str | None:
        entry = self.get_entry(chinese)
        return None if entry is None else entry.pinyin

    def get_simplified(self, chinese: str) -> str | None:
        entry = self.get_entry(chinese)
        return None if entry is None else entry.simplified

    def get_traditional(self, chinese: str) -> str | None:
        entry = self.get_entry(chinese)
        return None if entry is None else entry.traditional

    def get_entry(self, chinese: str) -> Entry | None:
        idx = self.simplified_to_index.get(chinese)
        if idx is not None:
            return self.entries[idx]

        idx = self.traditional_to_index.get(chinese)
        if idx is not None:
            return self.entries[idx]

        return None

    def get_entries(self) -> list[Entry]:
        return self.entries

    def _parse_file(self, file: TextIO) -> None:
        for _, line in enumerate(file):
            entry = self._parse_line(line)
            if entry is None:
                continue

            self.entries.append(entry)
            self.simplified_to_index[entry.simplified] = len(self.entries) - 1
            self.traditional_to_index[entry.traditional] = len(self.entries) - 1

    def _parse_line(self, line: str) -> Entry | None:
        if line.startswith("#"):
            return None

        line = line.strip().rstrip("/")

        chinese, english = line.split("/", maxsplit=1)
        chinese = chinese.strip()

        traditional_and_simplified, pinyin = chinese.split("[")
        traditional, simplified = traditional_and_simplified.strip().split()

        pinyin = pinyin[:-1]  # remove trailing ']'

        senses = english.split("/")
        glosses = [sense.split(";") for sense in senses]
        definitions = [definition for gloss in glosses for definition in gloss]

        return Entry(
            traditional=traditional,
            simplified=simplified,
            pinyin=pinyin,
            definitions=definitions,
        )
