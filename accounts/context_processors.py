from __future__ import annotations

from typing import Dict

from .models import Message


def unread_message_count(request) -> Dict[str, int]:
    """Provide unread message count for the authenticated user's profile.

    Adds `unread_message_count` to template context (int).
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"unread_message_count": 0}

    profile = getattr(user, "profile", None)
    if not profile:
        return {"unread_message_count": 0}

    count = Message.objects.filter(recipient=profile, is_read=False).count()
    return {"unread_message_count": count}
