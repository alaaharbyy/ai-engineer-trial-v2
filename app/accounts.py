"""Test users and their groups. Do not change these."""

USERS: dict[str, list[str]] = {
    "analyst_1": ["finance", "legal"],
    "leasing_1": ["leasing"],
    "staff_1": [],  # no team: can read "everyone" documents only
}


def groups_for(user_id: str) -> list[str]:
    """Return the user's groups. Raises KeyError for an unknown user."""
    return USERS[user_id]
