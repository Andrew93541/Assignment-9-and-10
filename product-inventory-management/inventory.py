"""Product Inventory Management System with validation, exception handling, and logging."""

import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "application.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 5


def _validate_number(value, name):
    """Validate that value is an int or float (excluding booleans)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        logger.error("Invalid type for %s: %r", name, value)
        raise TypeError(f"{name} must be a numeric value")


def _validate_int(value, name):
    """Validate that value is an integer (excluding booleans)."""
    if isinstance(value, bool) or not isinstance(value, int):
        logger.error("Invalid integer type for %s: %r", name, value)
        raise TypeError(f"{name} must be an integer")


def calculate_total_price(price, quantity):
    """Calculate and return total price based on unit price and quantity."""
    _validate_number(price, "Price")
    _validate_int(quantity, "Quantity")

    if price < 0:
        logger.error("Invalid negative price: %s", price)
        raise ValueError("Price cannot be negative")
    if quantity <= 0:
        logger.error("Invalid non-positive quantity: %s", quantity)
        raise ValueError("Quantity must be greater than zero")

    total = price * quantity
    logger.debug(
        "Calculated total price: price=%s, quantity=%s, total=%s",
        price,
        quantity,
        total,
    )
    return total


def apply_discount(total, discount_percent):
    """Apply discount percentage to total and return the discounted amount."""
    _validate_number(total, "Total amount")
    _validate_number(discount_percent, "Discount percentage")

    if total < 0:
        logger.error("Invalid negative total amount: %s", total)
        raise ValueError("Total amount cannot be negative")
    if not 0 <= discount_percent <= 100:
        logger.error("Invalid discount percentage: %s", discount_percent)
        raise ValueError("Discount percentage must be between 0 and 100")

    discounted_amount = total - (total * discount_percent / 100)
    logger.debug(
        "Applied discount: total=%s, discount_percent=%s, discounted_amount=%s",
        total,
        discount_percent,
        discounted_amount,
    )
    return discounted_amount


def check_stock(available_stock, requested_quantity):
    """Check whether requested quantity can be fulfilled from available stock."""
    _validate_int(available_stock, "Available stock")
    _validate_int(requested_quantity, "Requested quantity")

    if available_stock < 0:
        logger.error("Invalid negative available stock: %s", available_stock)
        raise ValueError("Available stock cannot be negative")
    if requested_quantity <= 0:
        logger.error("Invalid requested quantity: %s", requested_quantity)
        raise ValueError("Requested quantity must be greater than zero")

    logger.debug(
        "Checking stock: available_stock=%s, requested_quantity=%s",
        available_stock,
        requested_quantity,
    )

    if requested_quantity > available_stock:
        logger.warning(
            "Insufficient stock: available=%s, requested=%s",
            available_stock,
            requested_quantity,
        )
        return False

    remaining = available_stock - requested_quantity
    if remaining < LOW_STOCK_THRESHOLD:
        logger.warning(
            "Low stock alert after fulfillment: remaining=%s",
            remaining,
        )

    logger.info(
        "Stock check passed: available=%s, requested=%s",
        available_stock,
        requested_quantity,
    )
    return True


def process_product_order(
    inventory, product_id, requested_quantity, discount_percent=0
):
    """Process a product order with stock verification, pricing, and discount."""
    logger.info(
        "Processing product check for %s (qty=%s)", product_id, requested_quantity
    )

    if product_id not in inventory:
        logger.error("Product ID not found: %s", product_id)
        raise KeyError(f"Product '{product_id}' does not exist in inventory")

    product = inventory[product_id]
    if not check_stock(product["stock"], requested_quantity):
        return None

    gross_total = calculate_total_price(product["price"], requested_quantity)
    final_amount = apply_discount(gross_total, discount_percent)
    product["stock"] -= requested_quantity

    logger.info(
        "Order fulfilled for %s (%s): final_amount=%.2f, remaining_stock=%s",
        product_id,
        product["name"],
        final_amount,
        product["stock"],
    )
    return final_amount


if __name__ == "__main__":
    products = {
        "P101": {"name": "Wireless Keyboard", "price": 1500.0, "stock": 12},
        "P102": {"name": "USB-C Hub", "price": 800.0, "stock": 6},
        "P103": {"name": "Webcam HD", "price": 2500.0, "stock": 2},
    }

    # 1. Valid order with 10% discount
    amount_1 = process_product_order(
        products, "P101", requested_quantity=2, discount_percent=10
    )
    print(f"Order P101 fulfilled — Final payable amount: ₹{amount_1:.2f}")

    # 2. Order triggering low-stock warning (remaining stock < 5)
    amount_2 = process_product_order(
        products, "P102", requested_quantity=3, discount_percent=5
    )
    print(
        f"Order P102 fulfilled (low stock warning logged) — Final amount: ₹{amount_2:.2f}"
    )

    # 3. Order exceeding available stock
    amount_3 = process_product_order(
        products, "P103", requested_quantity=5, discount_percent=0
    )
    print(f"Order P103 stock available for 5 units: {amount_3 is not None}")

    # 4. Graceful exception handling for invalid inputs
    try:
        calculate_total_price(-500, 2)
    except ValueError as exc:
        print(f"Handled expected validation error: {exc}")
