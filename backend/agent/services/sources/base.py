from abc import ABC, abstractmethod


class EmailSource(ABC):
    """
    Abstract contract for any email ingestion source.

    Every concrete source (mock JSON, Gmail, IMAP, webhook, ...) must return a
    list of normalized email dictionaries. Keeping the shape identical across
    sources is what lets the pipeline worker stay source-agnostic.

    Normalized email shape:
        {
            "email_id":    str,  # globally unique id (used for idempotency)
            "sender":      str,  # raw "From" value
            "subject":     str,
            "body":        str,  # plain-text body
            "received_at": str,  # ISO-8601 timestamp string
        }
    """

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Return a list of normalized email dictionaries for this poll cycle."""
        raise NotImplementedError
