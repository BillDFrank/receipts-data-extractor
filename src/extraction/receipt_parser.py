import re
from typing import List, Optional
from .models import Product, Receipt, ExtractionResult


class PingoDoceReceiptParser:
    """Parser for Pingo Doce supermarket receipts."""

    def __init__(self):
        self.market = None  # Will be detected dynamically

    def parse_receipt(self, text: str) -> ExtractionResult:
        """
        Parse receipt text and extract products.

        Args:
            text: Raw text extracted from PDF

        Returns:
            ExtractionResult with parsed receipt or error
        """
        try:
            # Detect market dynamically
            self.market = self._detect_market(text)

            # Extract branch name
            branch = self._extract_branch(text)
            if not branch:
                return ExtractionResult(
                    success=False,
                    error_message="Could not extract branch information"
                )

            # Extract invoice, total, date
            invoice = self._extract_invoice(text)
            total = self._extract_total(text)
            date = self._extract_date(text)

            # Extract products
            products = self._extract_products(text, branch)

            if not products:
                return ExtractionResult(
                    success=False,
                    error_message="No products found in receipt"
                )

            receipt = Receipt(
                market=self.market,
                branch=branch,
                invoice=invoice,
                total=total,
                date=date,
                products=products
            )

            return ExtractionResult(success=True, receipt=receipt)

        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Error parsing receipt: {str(e)}"
            )

    def _detect_market(self, text: str) -> Optional[str]:
        """Detect market name from receipt text."""
        if "Pingo Doce" in text:
            return "Pingo Doce"
        return None

    def _extract_branch(self, text: str) -> Optional[str]:
        """Extract branch name from receipt text."""
        # Look for "PD " followed by branch name
        branch_match = re.search(r'PD\s+([^\n]+)', text)
        if branch_match:
            return f"PD {branch_match.group(1).strip()}"
        return None

    def _extract_invoice(self, text: str) -> Optional[str]:
        """Extract invoice number from receipt text."""
        # Look for "Fatura Simplificada FS " followed by the invoice number
        match = re.search(r'Fatura Simplificada\s+FS\s+([^\s]+)', text)
        if match:
            return f"FS {match.group(1)}"
        return None

    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt text."""
        # Look for "COMPRA " followed by amount with €
        match = re.search(r'COMPRA\s+([\d,]+)€', text)
        if match:
            return float(match.group(1).replace(',', '.'))
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        # Look for "Data de emissão:" followed by date
        match = re.search(r'Data de emissão:\s*([^\s]+)', text)
        if match:
            return match.group(1)
        return None

    def _extract_products(self, text: str, branch: str) -> List[Product]:
        """Extract all products from receipt text."""
        products = []
        lines = text.split('\n')

        current_section = None
        last_product = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Stop parsing when we reach the "Resumo" section
            if line.startswith("Resumo"):
                break

            # Check if this is a product type header
            if self._is_product_type_header(line):
                current_section = line
                continue

            # Try to parse as a discount line
            discount = self._parse_discount_line(line)
            if discount is not None and last_product is not None:
                # Associate discount with the last product
                if last_product.discount is None:
                    last_product.discount = discount
                else:
                    last_product.discount2 = discount
                continue

            # Try to parse as a product line
            if current_section:
                product = self._parse_product_line(line, current_section, branch)
                if product:
                    products.append(product)
                    last_product = product

        return products

    def _is_product_type_header(self, line: str) -> bool:
        """Check if a line is a product type header."""
        return line.isupper() and not re.search(r'\d', line) and not re.match(r'^[A-Z]\s', line)

    def _parse_discount_line(self, line: str) -> Optional[float]:
        """Parse a discount line and return the discount amount."""
        # Pattern: "Poupança Imediata (amount)"
        discount_match = re.search(r'Poupança Imediata\s*\(([\d,]+)\)', line)
        if discount_match:
            discount_str = discount_match.group(1)
            return float(discount_str.replace(',', '.'))
        return None

    def _parse_product_line(self, line: str, section_type: str, branch: str) -> Optional[Product]:
        """Parse a single product line."""
        # Skip discount lines for now (we'll handle them separately)
        if 'Poupança Imediata' in line:
            return None

        # Pattern 1: Type + Product + Quantity + X + Price + Total
        # Example: "C TRANCHE SALMÃO UN150 2,000 X 3,69 7,38"
        pattern1 = r'^([A-Z])\s+(.+?)\s+(\d+(?:,\d+)?)\s+X\s+([\d,]+)\s+([\d,]+)$'

        # Pattern 2: Type + Product + Price (no quantity)
        # Example: "E PÃO DE LEITE 1,99"
        pattern2 = r'^([A-Z])\s+(.+?)\s+([\d,]+)$'

        # Pattern 3: Type + Product + Quantity + X + Price + Total (with weight)
        # Example: "C BANANA IMPORTADA 0,645 X 1,25 0,81"
        pattern3 = r'^([A-Z])\s+(.+?)\s+([\d,]+)\s+X\s+([\d,]+)\s+([\d,]+)$'

        # Pattern 4: Type + Type + Product + Quantity + Price
        # Example: "E C COLA ZERO 2X1,75L 3,69"
        pattern4 = r'^([A-Z])\s+([A-Z])\s+(.+?)\s+(.+?)\s+([\d,]+)$'

        match = re.match(pattern1, line) or re.match(pattern3, line) or re.match(pattern2, line) or re.match(pattern4, line)

        if match:
            groups = match.groups()
            if len(groups) == 5:
                if 'X' in line:  # Pattern 1 or 3
                    product_type_indicator, product_name, quantity, price, total = groups
                    quantity = float(quantity.replace(',', '.'))
                    price = float(price.replace(',', '.'))
                else:  # Pattern 4: "E C COLA ZERO 2X1,75L 3,69"
                    type1, type2, product_name, quantity_info, price = groups
                    product_type_indicator = f"{type1} {type2}"
                    # Extract quantity from format like "2X1,75L"
                    quantity_match = re.search(r'(\d+)', quantity_info)
                    quantity = float(quantity_match.group(1)) if quantity_match else 1.0
                    price = float(price.replace(',', '.'))
                    product_name = f"{type2} {product_name}"
            else:  # Pattern 2
                product_type_indicator, product_name, price = groups
                quantity = 1.0
                price = float(price.replace(',', '.'))

            return Product(
                product_type=section_type,
                product=product_name.strip(),
                price=price,
                quantity=quantity
            )

        return None