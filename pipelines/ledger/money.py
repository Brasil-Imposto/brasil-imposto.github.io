"""Money helpers: exact decimal values and integer cents, never floating point (spec 4.2)."""
from decimal import ROUND_HALF_EVEN, Decimal

EXACT = Decimal("1e-8")  # reais; finer than anything the sources publish


def _decimal(value):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(repr(value))  # the shortest repr is the number the file holds
    return Decimal(str(value))


def exact(value):
    """A source number in reais (int, float, str or Decimal) as an exact Decimal."""
    return _decimal(value).quantize(EXACT, ROUND_HALF_EVEN)


def from_millions(value):
    """R$ milhões, as the RTN and the SGS publish, to exact reais."""
    return (_decimal(value) * 1_000_000).quantize(EXACT, ROUND_HALF_EVEN)


def to_cents(reais):
    """Exact reais to integer cents, rounding half to even."""
    return int((reais * 100).quantize(Decimal(1), ROUND_HALF_EVEN))
