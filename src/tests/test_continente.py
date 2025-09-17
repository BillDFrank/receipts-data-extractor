from src.extraction.receipt_parser import SupermarketReceiptParser


def test_continente_totals_layout1():
    parser = SupermarketReceiptParser()
    text = """MCH Matosinhos
MODELO CONTINENTE HIPERMERCADOS S.A.
Nro:FS AAA218/024041 11/08/2025 18:05
IVA DESCRICAO VALOR
Soft Drinks:
(B) AGUA S/GAS LUSO 50CL
3 X 0,50 1,50
TOTAL A PAGAR 61,20
Cartao Credito 61,20
Total de descontos e poupancas 5,31
%IVA Total Liq. IVA Total
(A) 6,00% 15,21 0,91 16,12
(B) 13,00% 1,33 0,17 1,50
(C) 23,00% 35,43 8,15 43,58
"""
    result = parser.parse_receipt(text)
    assert result.success
    assert result.receipt.market == "Continente"
    # total should be inferred: paid + discount
    assert result.receipt.total_paid == 61.20
    assert result.receipt.total_discount == 5.31
    assert result.receipt.total == 66.51


def test_continente_totals_layout2():
    parser = SupermarketReceiptParser()
    text = """MCH Matosinhos
MODELO CONTINENTE HIPERMERCADOS S.A.
Nro:FS AAA218/024041 11/08/2025 18:05
IVA DESCRICAO VALOR
Soft Drinks:
(B) AGUA S/GAS LUSO 50CL
3 X 0,50 1,50
SUBTOTAL 24,53
Desconto Cartao Utilizado 5,00
TOTAL A PAGAR 19,53
Cartao Credito 19,53
Total de descontos e poupancas 1,55
"""
    result = parser.parse_receipt(text)
    assert result.success
    assert result.receipt.market == "Continente"
    # prefer SUBTOTAL for total and compute discount as SUBTOTAL - TOTAL A PAGAR
    assert result.receipt.total == 24.53
    assert result.receipt.total_paid == 19.53
    assert result.receipt.total_discount == 5.00
