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
TOTAL A PAGAR 61,20"""

result = parser.parse_receipt(sample_text)
if result.success:
    print("Products extracted:")
    for i, product in enumerate(result.receipt.products, 1):
        print(f"{i}. {product.product}: {product.price}€ (x{product.quantity})")
else:
    print("Failed to parse receipt")
