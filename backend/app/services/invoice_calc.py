from decimal import Decimal, ROUND_HALF_UP


def quantize_jpy(value: Decimal) -> Decimal:
    return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def tax_rate_for(tax_code: str) -> Decimal:
    if tax_code == 'reduced':
        return Decimal('0.08')
    return Decimal('0.10')


def calc_line(subtotal: Decimal, discount: Decimal, tax_code: str) -> tuple[Decimal, Decimal, Decimal]:
    after_discount = subtotal - discount
    if after_discount < 0:
        raise ValueError('Negative line total after discount')
    tax = quantize_jpy(after_discount * tax_rate_for(tax_code))
    total = after_discount + tax
    return quantize_jpy(subtotal), tax, quantize_jpy(total)
