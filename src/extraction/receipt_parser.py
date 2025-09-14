import re
from typing import List, Optional
from .models import Product, Receipt, ExtractionResult


class SupermarketReceiptParser:
    """Parser for supermarket receipts (Pingo Doce, Continente, etc.)."""

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

            if not self.market:
                return ExtractionResult(
                    success=False,
                    error_message="Could not detect market from receipt"
                )

            # Route to appropriate parsing method based on market
            if self.market == "Pingo Doce":
                return self._parse_pingo_doce_receipt(text)
            elif self.market == "Continente":
                return self._parse_continente_receipt(text)
            else:
                return ExtractionResult(
                    success=False,
                    error_message=f"Unsupported market: {self.market}"
                )

        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=f"Error parsing receipt: {str(e)}"
            )

    def _detect_market(self, text: str) -> Optional[str]:
        """Detect market name from receipt text."""
        lines = text.split('\n')[:2]  # Check first 2 lines
        first_two_lines = ' '.join(lines).upper()

        if "CONTINENTE" in first_two_lines:
            return "Continente"
        elif "PINGO DOCE" in text.upper():
            return "Pingo Doce"
        return None

    def _parse_pingo_doce_receipt(self, text: str) -> ExtractionResult:
        """Parse Pingo Doce receipt text."""
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

    def _parse_continente_receipt(self, text: str) -> ExtractionResult:
        """Parse Continente receipt text."""
        # Extract branch name (first line)
        branch = self._extract_continente_branch(text)
        if not branch:
            return ExtractionResult(
                success=False,
                error_message="Could not extract branch information"
            )

        # Extract invoice, total, date
        invoice = self._extract_continente_invoice(text)
        total = self._extract_continente_total(text)
        date = self._extract_continente_date(text)

        # Extract products
        products = self._extract_continente_products(text)

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

    def _extract_branch(self, text: str) -> Optional[str]:
        """Extract branch name from receipt text."""
        lines = text.split('\n')

        # Look for the first line before "Tel.:"
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Tel.:'):
                if line:
                    return line
            elif line.startswith('Tel.:'):
                # If we reach Tel.: without finding a branch, break
                break

        # Fallback to old method if new method doesn't work
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
        # Try multiple patterns in order of preference

        # Pattern 1: TOTAL A PAGAR (most reliable)
        match = re.search(r'TOTAL A PAGAR\s+([\d,]+)', text)
        if match:
            return float(match.group(1).replace(',', '.'))

        # Pattern 2: TOTAL PAGO
        match = re.search(r'TOTAL PAGO\s+([\d,]+)', text)
        if match:
            return float(match.group(1).replace(',', '.'))

        # Pattern 3: COMPRA (handle space in decimal)
        match = re.search(r'COMPRA\s+([\d]+),\s*([\d]+)€', text)
        if match:
            whole, decimal = match.groups()
            return float(f"{whole}.{decimal}")

        # Pattern 4: COMPRA (fallback for other formats)
        match = re.search(r'COMPRA\s+([\d,\s]+)€', text)
        if match:
            amount = match.group(1).replace(',', '.').replace(' ', '')
            return float(amount)

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        # Look for "Data de emissão:" followed by date
        match = re.search(r'Data de emissão:\s*([^\s]+)', text)
        if match:
            date_str = match.group(1)
            # Handle different date formats
            # Format 1: DD-MM-YYYY (e.g., 16-08-2025) - convert to DD/MM/YYYY
            if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
                return date_str.replace('-', '/')
            # Format 2: DD/MM/YYYY (e.g., 16/08/2025) - keep as is
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                return date_str
            # Format 3: Other formats - return as is
            else:
                return date_str
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
                product = self._parse_product_line(
                    line, current_section, branch)
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

        match = re.match(pattern1, line) or re.match(pattern3, line) or re.match(
            pattern2, line) or re.match(pattern4, line)

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
                    quantity = float(quantity_match.group(
                        1)) if quantity_match else 1.0
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

    def _extract_continente_branch(self, text: str) -> Optional[str]:
        """Extract branch name from Continente receipt (first line)."""
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line:
                return first_line
        return None

    def _extract_continente_invoice(self, text: str) -> Optional[str]:
        """Extract invoice number from Continente receipt."""
        # Look for "Nro:FS " followed by the invoice number
        match = re.search(r'Nro:\s*FS\s+([^\s]+)', text)
        if match:
            return f"FS {match.group(1)}"
        return None

    def _extract_continente_total(self, text: str) -> Optional[float]:
        """Extract total amount from Continente receipt."""
        # Look for "TOTAL A PAGAR " followed by amount
        match = re.search(r'TOTAL A PAGAR\s+([\d,]+)', text)
        if match:
            return float(match.group(1).replace(',', '.'))
        return None

    def _extract_continente_date(self, text: str) -> Optional[str]:
        """Extract date from Continente receipt."""
        # Look for date after invoice number in format DD/MM/YYYY or DD-MM-YYYY
        match = re.search(
            r'Nro:\s*FS\s+[^\s]+\s+(\d{2}[/-]\d{2}[/-]\d{4})', text)
        if match:
            date_str = match.group(1)
            # Convert DD-MM-YYYY to DD/MM/YYYY if needed
            if '-' in date_str:
                date_str = date_str.replace('-', '/')
            return date_str  # Return DD/MM/YYYY format
        return None

    def _extract_continente_products(self, text: str) -> List[Product]:
        """Extract all products from Continente receipt text."""
        products = []
        lines = text.split('\n')

        current_section = None
        parsing_products = False
        pending_product = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a product type header (ends with :)
            if line.endswith(':') and not line.startswith('('):
                current_section = line.rstrip(':')
                parsing_products = True
                continue

            # Stop parsing when we reach certain sections
            if any(phrase in line.upper() for phrase in ['TOTAL A PAGAR', 'CARTAO CREDITO', 'IVA INCLUIDO']):
                break

            # Only parse products after we've found "IVA DESCRICAO VALOR"
            if 'IVA DESCRICAO VALOR' in line.upper():
                parsing_products = True
                continue

            if parsing_products and current_section:
                # Check if this is a product line (starts with letter in parentheses)
                if re.match(r'^\([A-Z]\)', line):
                    # If we have a pending product, save it first
                    if pending_product:
                        products.append(pending_product)
                        pending_product = None

                    # Parse the product line
                    product = self._parse_continente_product_line(
                        line, current_section)
                    if product:
                        # Check if price is in the same line
                        if product.price > 0:
                            products.append(product)
                        else:
                            # Price might be in next line, keep as pending
                            pending_product = product
                elif pending_product and re.search(r'[\d,]+', line):
                    # This might be the price/quantity line for the pending product
                    updated_product = self._parse_continente_price_line(
                        line, pending_product)
                    if updated_product:
                        products.append(updated_product)
                        pending_product = None

        # Add any remaining pending product
        if pending_product:
            products.append(pending_product)

        return products

    def _parse_continente_product_line(self, line: str, section_type: str) -> Optional[Product]:
        """Parse a single product line from Continente receipt."""
        # Skip lines that don't start with a letter in parentheses
        if not re.match(r'^\([A-Z]\)', line):
            return None

        # Extract product name: everything after the letter in parentheses
        product_match = re.match(r'^\([A-Z]\)\s*(.+?)\s*$', line)
        if not product_match:
            return None

        product_name = product_match.group(1).strip()

        # Check if there's a price in the same line
        price_match = re.search(r'([\d,]+)$', product_name)
        if price_match:
            price_str = price_match.group(1)
            # Remove price from product name
            product_name = re.sub(r'\s*[\d,]+$', '', product_name).strip()
            try:
                price = float(price_str.replace(',', '.'))
            except ValueError:
                price = 0.0
        else:
            price = 0.0  # Price might be in next line

        # Extract quantity if present in the same line
        quantity = 1.0
        if price > 0:  # Only check for quantity if price is in same line
            quantity_match = re.search(r'(\d+)\s*X\s*[\d,]+', line)
            if quantity_match:
                quantity = float(quantity_match.group(1))

        return Product(
            product_type=section_type,
            product=product_name.strip(),
            price=price,
            quantity=quantity
        )

    def _parse_continente_price_line(self, line: str, product: Product) -> Optional[Product]:
        """Parse a price/quantity line that follows a product line."""
        # Look for patterns like "3 X 0,50 1,50" or just "1,50"
        quantity_price_match = re.search(
            r'(\d+)\s*X\s*([\d,]+)\s*([\d,]+)', line)
        if quantity_price_match:
            quantity = float(quantity_price_match.group(1))
            unit_price = float(quantity_price_match.group(2).replace(',', '.'))
            total_price = float(
                quantity_price_match.group(3).replace(',', '.'))
            return Product(
                product_type=product.product_type,
                product=product.product,
                price=unit_price,  # Use unit price instead of total price
                quantity=quantity
            )

        # Look for just a price
        price_match = re.search(r'^([\d,]+)$', line.strip())
        if price_match:
            price = float(price_match.group(1).replace(',', '.'))
            return Product(
                product_type=product.product_type,
                product=product.product,
                price=price,
                quantity=product.quantity
            )

        return None
