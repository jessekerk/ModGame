"""Utilities for sampling valid duplicate-card configurations without enumeration."""
import random
from collections import Counter


def sample_remaining_hand(played_history, m, extra_cards):
    """Sample a compatible hand uniformly over valid duplicate-card sets."""
    played = Counter(played_history)
    if any(count > 2 for count in played.values()):
        raise ValueError("Observed plays are inconsistent with the game rules.")

    forced = {card for card, count in played.items() if count == 2}
    slots_left = extra_cards - len(forced)
    eligible = [card for card in range(1, m + 1) if card not in forced]
    if slots_left < 0 or slots_left > len(eligible):
        raise ValueError("No possible hand matches the observed plays.")

    duplicates = forced | set(random.sample(eligible, slots_left))
    return {card: 1 + (card in duplicates) - played[card] for card in range(1, m + 1)}


def estimate_remaining_cards(played_history, m, extra_cards):
    """Exact expected remaining counts, computed analytically rather than by enumeration."""
    played = Counter(played_history)
    if any(count > 2 for count in played.values()):
        raise ValueError("Observed plays are inconsistent with the game rules.")

    forced = {card for card, count in played.items() if count == 2}
    slots_left = extra_cards - len(forced)
    eligible = [card for card in range(1, m + 1) if card not in forced]
    if slots_left < 0 or slots_left > len(eligible):
        raise ValueError("No possible hand matches the observed plays.")

    p_duplicate = slots_left / len(eligible) if eligible else 0.0
    return {
        card: 1 + (1.0 if card in forced else p_duplicate) - played[card]
        for card in range(1, m + 1)
    }
