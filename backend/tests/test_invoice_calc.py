from decimal import Decimal

from app.services.invoice_calc import calc_line


def test_calc_line_standard_tax():
    subtotal, tax, total = calc_line(Decimal('1000'), Decimal('100'), 'standard')
    assert subtotal == Decimal('1000')
    assert tax == Decimal('90')
    assert total == Decimal('990')


def test_calc_line_reduced_tax():
    subtotal, tax, total = calc_line(Decimal('1000'), Decimal('0'), 'reduced')
    assert subtotal == Decimal('1000')
    assert tax == Decimal('80')
    assert total == Decimal('1080')
