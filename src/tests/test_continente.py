from src.extraction.receipt_parser import SupermarketReceiptParser

parser = SupermarketReceiptParser()
sample_text = """MCH Matosinhos
MODELO CONTINENTE HIPERMERCADOS S.A.
Nro:FS AAA218/024041 11/08/2025 18:05
IVA DESCRICAO VALOR
Soft Drinks:
(B) AGUA S/GAS LUSO 50CL
3 X 0,50 1,50
Higiene:
(A) RESGUARDO CONT BEBE 15UN 5,99
Laticinios/Beb. Veg.:
(A) LEITE M/GORDO CNT 6*1L (R) 5,16
Beleza:
(C) LAM. DESC. BLUE II SLALOM 10UN 6,99
Padaria:
(C) FOLHADO SALSICHA C/QUEIJO UN
2 X 1,09 2,18
TOTAL A PAGAR 61,20"""

result = parser.parse_receipt(sample_text)
print('Success:', result.success)
if result.success:
    print('Market:', result.receipt.market)
    print('Branch:', result.receipt.branch)
    print('Invoice:', result.receipt.invoice)
    print('Total:', result.receipt.total)
    print('Date:', result.receipt.date)
    print('Products:', len(result.receipt.products))
    for i, product in enumerate(result.receipt.products, 1):
        print(
            f"  {i}. {product.product_type}: {product.product} - {product.price}€ (x{product.quantity})")
else:
    print('Error:', result.error_message)
