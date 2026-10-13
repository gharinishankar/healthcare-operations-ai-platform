
from decimal import Decimal, ROUND_HALF_UP


def calculate_dna_rate(dna, attended):
    eligible = dna + attended

    if eligible == 0:
        return None

    rate = (
        Decimal(dna)
        / Decimal(eligible)
        * Decimal(100)
    )

    return float(
        rate.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    )


def verify_practice(practice):
    calculated = calculate_dna_rate(
        practice["did_not_attend"],
        practice["attended"]
    )

    return calculated == practice["dna_rate_percent"]
