#!/usr/bin/env python3
"""Deterministic layout and character metrics for the Shaanxi OCR research track."""
from __future__ import annotations

import statistics
import unicodedata
from dataclasses import dataclass

CONTENT_BOUND_TRIM_RATIO = 0.05


@dataclass(frozen=True)
class Word:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    text: str
    confidence: float | None = None

    @property
    def x_center(self) -> float:
        return (self.x_min + self.x_max) / 2

    @property
    def y_center(self) -> float:
        return (self.y_min + self.y_max) / 2

    @property
    def height(self) -> float:
        return self.y_max - self.y_min


def visible_words(words: list[Word]) -> list[Word]:
    return [
        word
        for word in words
        if word.text.strip() and word.height > 0 and word.x_max > word.x_min
    ]


def cluster_physical_lines(words: list[Word]) -> list[str]:
    """Group words by baseline and order each physical line left-to-right."""
    visible = visible_words(words)
    if not visible:
        return []
    tolerance = max(3.0, statistics.median(word.height for word in visible) * 0.45)
    lines: list[list[object]] = []
    for word in sorted(visible, key=lambda item: (item.y_center, item.x_min)):
        candidates = [line for line in lines if abs(word.y_center - float(line[0])) <= tolerance]
        if not candidates:
            lines.append([word.y_center, [word]])
            continue
        line = min(candidates, key=lambda item: abs(word.y_center - float(item[0])))
        line_words = line[1]
        assert isinstance(line_words, list)
        line_words.append(word)
        line[0] = sum(item.y_center for item in line_words) / len(line_words)
    ordered = sorted(lines, key=lambda item: float(item[0]))
    return [
        "".join(word.text for word in sorted(line[1], key=lambda item: item.x_min))
        for line in ordered
    ]


def calculate_region_divider(words: list[Word], page_width: float) -> float:
    """Estimate the column divider from robust visible-content bounds."""
    visible = visible_words(words)
    if not visible:
        return page_width / 2
    trim_count = int(len(visible) * CONTENT_BOUND_TRIM_RATIO)
    left_edges = sorted(word.x_min for word in visible)
    right_edges = sorted(word.x_max for word in visible)
    left_bound = left_edges[trim_count]
    right_bound = right_edges[-trim_count - 1] if trim_count else right_edges[-1]
    if right_bound <= left_bound:
        return page_width / 2
    return (left_bound + right_bound) / 2


def crossing_word_count(words: list[Word], divider: float) -> int:
    return sum(
        word.x_min < divider < word.x_max for word in visible_words(words)
    )


def split_page_regions(words: list[Word], page_width: float) -> dict[str, list[str]]:
    """Canonicalize columns using the page's robust visible-content midpoint."""
    divider = calculate_region_divider(words, page_width)
    return {
        "left": cluster_physical_lines([word for word in words if word.x_center < divider]),
        "right": cluster_physical_lines([word for word in words if word.x_center >= divider]),
    }


def is_han(character: str) -> bool:
    return "㐀" <= character <= "鿿"


def normalize_characters(text: str, *, han_only: bool = False) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    if han_only:
        return "".join(character for character in normalized if is_han(character))
    return "".join(
        character
        for character in normalized
        if not character.isspace() and unicodedata.category(character)[0] != "C"
    )


def levenshtein_distance(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for row, left_character in enumerate(left, 1):
        current = [row]
        for column, right_character in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column] + 1,
                    previous[column - 1] + (left_character != right_character),
                )
            )
        previous = current
    return previous[-1]


def score_region_pairs(
    truth_regions: list[str], observed_regions: list[str], *, han_only: bool = False
) -> dict[str, int | float]:
    if len(truth_regions) != len(observed_regions):
        raise ValueError("truth and observed region counts differ")
    pairs = [
        (
            normalize_characters(truth, han_only=han_only),
            normalize_characters(observed, han_only=han_only),
        )
        for truth, observed in zip(truth_regions, observed_regions, strict=True)
    ]
    edit_distance = sum(levenshtein_distance(truth, observed) for truth, observed in pairs)
    denominator = sum(max(len(truth), len(observed)) for truth, observed in pairs)
    accuracy = 100.0 if denominator == 0 else 100.0 * (1 - edit_distance / denominator)
    return {
        "accuracy_pct": round(accuracy, 2),
        "edit_distance": edit_distance,
        "truth_chars": sum(len(truth) for truth, _ in pairs),
        "ocr_chars": sum(len(observed) for _, observed in pairs),
        "compared_chars": denominator,
    }
