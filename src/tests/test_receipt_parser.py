from src.extraction.receipt_parser import SupermarketReceiptParser


class TestSupermarketReceiptParser:
    """Test cases for supermarket receipt parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SupermarketReceiptParser()

    def test_detect_market(self):
        """Test market detection from receipt text."""
        text_with_pingo_doce = "PD PRELADA\nTel.: 226198120\nPingo Doce - Distribuição Alimentar, S.A."
        market = self.parser._detect_market(text_with_pingo_doce)
        assert market == "Pingo Doce"

        text_with_continente = "MCH Matosinhos\nMODELO CONTINENTE HIPERMERCADOS S.A."
        market = self.parser._detect_market(text_with_continente)
        assert market == "Continente"

        text_without_market = "Some other receipt\nTel.: 123456789\nOther Store"
        market = self.parser._detect_market(text_without_market)
        assert market is None

    def test_extract_branch(self):
        """Test branch extraction from receipt text."""
        # Test old format
        text_old = "PD PRELADA\nTel.: 226198120\nPingo Doce - Distribuição Alimentar, S.A."
        branch_old = self.parser._extract_branch(text_old)
        assert branch_old == "PD PRELADA"

        # Test new format like "go Doce Canidelo 2"
        text_new = "go Doce Canidelo 2\nTel.: 227728010\nPingo Doce - Distribuição Alimentar, S.A."
        branch_new = self.parser._extract_branch(text_new)
        assert branch_new == "go Doce Canidelo 2"

    def test_parse_product_line_pattern1(self):
        """Test parsing product line with quantity and total."""
        self.parser.market = "Pingo Doce"
        line = "C TRANCHE SALMÃO UN150 2,000 X 3,69 7,38"
        product = self.parser._parse_product_line(
            line, "PEIXARIA", "PD PRELADA")

        assert product is not None
        assert product.product == "TRANCHE SALMÃO UN150"
        assert product.price == 3.69
        assert product.quantity == 2.0
        assert product.product_type == "PEIXARIA"

    def test_parse_product_line_pattern2(self):
        """Test parsing simple product line with just price."""
        line = "E PÃO DE LEITE 1,99"
        product = self.parser._parse_product_line(
            line, "PADARIA/PASTELARIA", "PD PRELADA")

        assert product is not None
        assert product.product == "PÃO DE LEITE"
        assert product.price == 1.99
        assert product.quantity == 1.0

    def test_parse_product_line_pattern3(self):
        """Test parsing product line with weight quantity."""
        line = "C BANANA IMPORTADA 0,645 X 1,25 0,81"
        product = self.parser._parse_product_line(
            line, "FRUTAS E VEGETAIS", "PD PRELADA")

        assert product is not None
        assert product.product == "BANANA IMPORTADA"
        assert product.price == 1.25
        assert product.quantity == 0.645

    def test_parse_discount_line(self):
        """Test parsing discount lines."""
        line = "Poupança Imediata (0,40)"
        discount = self.parser._parse_discount_line(line)
        assert discount == 0.40

        line = "Poupança Imediata (3,40)"
        discount = self.parser._parse_discount_line(line)
        assert discount == 3.40

        line = "Some other line"
        discount = self.parser._parse_discount_line(line)
        assert discount is None

    def test_parse_product_line_invalid(self):
        """Test parsing invalid product line."""
        line = "Invalid product line"
        product = self.parser._parse_product_line(line, "TEST", "PD TEST")

        assert product is None

    def test_is_product_type_header(self):
        """Test product type header detection."""
        assert self.parser._is_product_type_header("PEIXARIA") is True
        assert self.parser._is_product_type_header(
            "PADARIA/PASTELARIA") is True
        assert self.parser._is_product_type_header("FRUTAS E VEGETAIS") is True
        assert self.parser._is_product_type_header(
            "BEBIDAS") is True  # New type
        assert self.parser._is_product_type_header("Regular text") is False

    def test_parse_receipt_pdf1(self):
        """Test parsing PDF 1 example from user."""
        pdf1_text = """PD PRELADA
Tel.: 226198120
Pingo Doce - Distribuição Alimentar, S.A.
Sede: R Actor António Silva,N7,1649-033 Lisboa
Registo C.R.C. Lisboa-Matrícula/NIPC: 500829993
C. Social: 33.808.115 EUR / Registo Produtor:
PT001730, PT01101095, PT03000085,
PT06000383, PT04000029
Artigos
PEIXARIA
C TRANCHE SALMÃO UN150 2,000 X 3,69 7,38
Poupança Imediata (3,40)
Exclusivo POUPA Shaker (0,40)
PADARIA/PASTELARIA
E PÃO DE LEITE 1,99
E BOLA BERLIM KIT KAT 1,000 X 0,99 0,99
E BOLA BERLIM SIMPLES 1,000 X 0,79 0,79
E MERENDA MISTA 95 G 2,000 X 0,79 1,58
FRUTAS E VEGETAIS
C BANANA IMPORTADA 0,645 X 1,25 0,81
Poupança Imediata (0,04)
CONGELADOS
C ALM TOMA S/GL PD420G 4,29
C BROCOLOS PD 400G 2 X 0,89 1,78
Resumo"""

        result = self.parser.parse_receipt(pdf1_text)

        assert result.success is True
        assert result.receipt is not None
        assert result.receipt.market == "Pingo Doce"
        assert result.receipt.branch == "PD PRELADA"
        assert result.receipt.invoice is None  # No invoice in this test data
        assert result.receipt.total is None   # No total in this test data
        assert result.receipt.date is None    # No date in this test data
        assert len(result.receipt.products) == 8  # Should have 8 products

        # Check specific products
        products = result.receipt.products
        salmao = next((p for p in products if "SALMÃO" in p.product), None)
        assert salmao is not None
        assert salmao.price == 3.69
        assert salmao.quantity == 2.0
        assert salmao.discount == 3.40  # Should have discount

        banana = next((p for p in products if "BANANA" in p.product), None)
        assert banana is not None
        assert banana.price == 1.25
        assert banana.quantity == 0.645
        assert banana.discount == 0.04  # Should have discount

    def test_parse_receipt_pdf2(self):
        """Test parsing PDF 2 example from user."""
        pdf2_text = """PD PRELADA
Tel.: 226198120
Pingo Doce - Distribuição Alimentar, S.A.
Sede: R Actor António Silva,N7,1649-033 Lisboa
Registo C.R.C. Lisboa-Matrícula/NIPC: 500829993
C. Social: 33.808.115 EUR / Registo Produtor:
PT001730, PT01101095, PT03000085,
PT06000383, PT04000029
Artigos
MERCEARIA + PET FOOD
E DIGES MAÇA 171G 2,49
Poupança Imediata (0,50)
PRONTO A COMER
E PIZZA FRES PD CA415G 2,89"""

        result = self.parser.parse_receipt(pdf2_text)

        assert result.success is True
        assert result.receipt is not None
        assert result.receipt.invoice is None
        assert result.receipt.total is None
        assert result.receipt.date is None
        assert len(result.receipt.products) == 2

        # Check products
        diges = next(
            (p for p in result.receipt.products if "DIGES" in p.product), None)
        pizza = next(
            (p for p in result.receipt.products if "PIZZA" in p.product), None)

        assert diges is not None
        assert diges.price == 2.49
        assert diges.product_type == "MERCEARIA + PET FOOD"

        assert pizza is not None
        assert pizza.price == 2.89
        assert pizza.product_type == "PRONTO A COMER"

    def test_extract_invoice(self):
        """Test invoice extraction."""
        text = "Fatura Simplificada FS 04890942308181520/067139"
        invoice = self.parser._extract_invoice(text)
        assert invoice == "FS 04890942308181520/067139"

        text_no_invoice = "Some other text"
        invoice = self.parser._extract_invoice(text_no_invoice)
        assert invoice is None

    def test_extract_total(self):
        """Test total extraction."""
        text = "COMPRA 10,55€"
        total = self.parser._extract_total(text)
        assert total == 10.55

        text_no_total = "Some other text"
        total = self.parser._extract_total(text_no_total)
        assert total is None

    def test_extract_date(self):
        """Test date extraction."""
        # Test DD/MM/YYYY format (should remain as is)
        text_slash = "Data de emissão: 25/08/2025"
        date_slash = self.parser._extract_date(text_slash)
        assert date_slash == "25/08/2025"

        # Test DD-MM-YYYY format (should be converted to DD/MM/YYYY)
        text_dash = "Data de emissão: 16-08-2025"
        date_dash = self.parser._extract_date(text_dash)
        assert date_dash == "16/08/2025"

        # Test no date
        text_no_date = "Some other text"
        date = self.parser._extract_date(text_no_date)
        assert date is None

    def test_extract_continente_date(self):
        """Test Continente date extraction."""
        # Test DD/MM/YYYY format after invoice number
        text_slash = "Nro: FS 04890942308181520/067139 25/08/2025"
        date_slash = self.parser._extract_continente_date(text_slash)
        assert date_slash == "25/08/2025"

        # Test DD-MM-YYYY format (should be converted to DD/MM/YYYY)
        text_dash = "Nro: FS 04890942308181520/067139 16-08-2025"
        date_dash = self.parser._extract_continente_date(text_dash)
        assert date_dash == "16/08/2025"

        # Test no date
        text_no_date = "Some other text"
        date = self.parser._extract_continente_date(text_no_date)
        assert date is None
