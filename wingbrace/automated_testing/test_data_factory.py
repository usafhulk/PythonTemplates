"""
test_data_factory.py
====================
Factory helpers for generating synthetic, reproducible test data.

Produces realistic-looking data for names, emails, phone numbers, addresses,
dates, UUIDs, and arbitrary structured records — all with no external
dependencies beyond the standard library.

Usage::

    from wingbrace.automated_testing import DataFactory

    factory = DataFactory(seed=42)
    user = factory.user()
    print(user)
    # {'id': 'a1b2c3...', 'first_name': 'Alice', 'last_name': 'Smith',
    #  'email': 'alice.smith@example.com', 'phone': '555-123-4567', ...}

    records = factory.bulk(factory.user, count=100)
"""

import random
import string
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Callable


class DataFactory:
    """
    Generate synthetic test data with an optional random seed for
    reproducible test runs.

    Parameters
    ----------
    seed:
        Seed for the internal ``random.Random`` instance.  Pass ``None``
        for non-deterministic output.
    """

    _FIRST_NAMES = [
        "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Heidi",
        "Ivan", "Judy", "Karl", "Laura", "Mallory", "Nathan", "Olivia",
        "Peggy", "Quentin", "Rachel", "Sam", "Tina", "Ursula", "Victor",
        "Wendy", "Xander", "Yvonne", "Zach",
    ]
    _LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson",
        "White", "Harris", "Martin", "Thompson", "Young", "Robinson",
    ]
    _DOMAINS = [
        "example.com", "test.org", "sample.net", "dummy.io", "fake.co",
    ]
    _STREETS = [
        "Main St", "Oak Ave", "Elm St", "Maple Dr", "Cedar Ln",
        "Birch Blvd", "Walnut Way", "Pine Rd", "Spruce Ct",
    ]
    _CITIES = [
        "Springfield", "Shelbyville", "Ogdenville", "North Haverbrook",
        "Brockway", "Centerburg", "Riverdale", "Lakewood",
    ]
    _STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    ]

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Primitive generators
    # ------------------------------------------------------------------

    def uuid(self) -> str:
        """Return a random UUID4 string."""
        return str(uuid.UUID(int=self._rng.getrandbits(128), version=4))

    def integer(self, low: int = 0, high: int = 1_000) -> int:
        """Return a random integer in [*low*, *high*]."""
        return self._rng.randint(low, high)

    def floating(self, low: float = 0.0, high: float = 1.0, decimals: int = 2) -> float:
        """Return a random float in [*low*, *high*] rounded to *decimals*."""
        return round(self._rng.uniform(low, high), decimals)

    def boolean(self) -> bool:
        """Return ``True`` or ``False`` with equal probability."""
        return self._rng.choice([True, False])

    def string(self, length: int = 8, charset: str = string.ascii_lowercase) -> str:
        """Return a random string of *length* characters."""
        return "".join(self._rng.choices(charset, k=length))

    def choice(self, options: list[Any]) -> Any:
        """Pick a random element from *options*."""
        return self._rng.choice(options)

    def choices(self, options: list[Any], k: int = 1) -> list[Any]:
        """Pick *k* random elements (with replacement) from *options*."""
        return self._rng.choices(options, k=k)

    # ------------------------------------------------------------------
    # Domain-specific generators
    # ------------------------------------------------------------------

    def first_name(self) -> str:
        return self._rng.choice(self._FIRST_NAMES)

    def last_name(self) -> str:
        return self._rng.choice(self._LAST_NAMES)

    def full_name(self) -> str:
        return f"{self.first_name()} {self.last_name()}"

    def email(self, first: str | None = None, last: str | None = None) -> str:
        first = first or self.first_name().lower()
        last = last or self.last_name().lower()
        domain = self._rng.choice(self._DOMAINS)
        return f"{first}.{last}@{domain}"

    def phone(self) -> str:
        area = self._rng.randint(200, 999)
        prefix = self._rng.randint(100, 999)
        line = self._rng.randint(1000, 9999)
        return f"{area}-{prefix}-{line}"

    def address(self) -> dict[str, str]:
        return {
            "street": f"{self._rng.randint(1, 9999)} {self._rng.choice(self._STREETS)}",
            "city": self._rng.choice(self._CITIES),
            "state": self._rng.choice(self._STATES),
            "zip_code": str(self._rng.randint(10000, 99999)),
        }

    def date_between(
        self,
        start: date | None = None,
        end: date | None = None,
    ) -> date:
        """Return a random date between *start* and *end* (inclusive)."""
        start = start or date(2000, 1, 1)
        end = end or date.today()
        delta = (end - start).days
        return start + timedelta(days=self._rng.randint(0, delta))

    def datetime_between(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> datetime:
        """Return a random datetime between *start* and *end*."""
        start = start or datetime(2000, 1, 1)
        end = end or datetime.now()
        delta_seconds = int((end - start).total_seconds())
        return start + timedelta(seconds=self._rng.randint(0, delta_seconds))

    def password(self, length: int = 12) -> str:
        """Generate a random password containing mixed characters."""
        charset = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(self._rng.choices(charset, k=length))

    # ------------------------------------------------------------------
    # Compound record generators
    # ------------------------------------------------------------------

    def user(self) -> dict[str, Any]:
        """Return a synthetic user record."""
        first = self.first_name()
        last = self.last_name()
        return {
            "id": self.uuid(),
            "first_name": first,
            "last_name": last,
            "email": self.email(first.lower(), last.lower()),
            "phone": self.phone(),
            "address": self.address(),
            "date_of_birth": self.date_between(
                date(1950, 1, 1), date(2005, 12, 31)
            ).isoformat(),
            "is_active": self.boolean(),
            "created_at": self.datetime_between().isoformat(),
        }

    def product(self) -> dict[str, Any]:
        """Return a synthetic product record."""
        categories = ["Electronics", "Clothing", "Food", "Furniture", "Books", "Toys"]
        return {
            "id": self.uuid(),
            "name": f"Product-{self.string(6, string.ascii_uppercase)}",
            "sku": self.string(8, string.ascii_uppercase + string.digits),
            "category": self._rng.choice(categories),
            "price": self.floating(0.99, 999.99),
            "quantity_in_stock": self.integer(0, 500),
            "is_available": self.boolean(),
        }

    def transaction(self) -> dict[str, Any]:
        """Return a synthetic financial transaction record."""
        statuses = ["completed", "pending", "failed", "refunded"]
        return {
            "transaction_id": self.uuid(),
            "user_id": self.uuid(),
            "amount": self.floating(1.00, 5000.00),
            "currency": self._rng.choice(["USD", "EUR", "GBP", "CAD"]),
            "status": self._rng.choice(statuses),
            "timestamp": self.datetime_between().isoformat(),
        }

    def api_error(
        self,
        status_code: int | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Return a synthetic API error payload."""
        codes = [400, 401, 403, 404, 409, 422, 500, 503]
        messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            503: "Service Unavailable",
        }
        code = status_code or self._rng.choice(codes)
        return {
            "error": {
                "code": code,
                "message": message or messages.get(code, "Unknown Error"),
                "request_id": self.uuid(),
            }
        }

    # ------------------------------------------------------------------
    # Bulk generation
    # ------------------------------------------------------------------

    def bulk(self, factory_method: Callable[[], Any], count: int = 10) -> list[Any]:
        """
        Generate *count* records using *factory_method*.

        Parameters
        ----------
        factory_method:
            A zero-argument callable (e.g. ``factory.user``) to call
            *count* times.
        count:
            Number of records to produce.

        Returns
        -------
        list
            A list of *count* records.

        Example
        -------
        ::

            users = factory.bulk(factory.user, count=50)
        """
        return [factory_method() for _ in range(count)]
