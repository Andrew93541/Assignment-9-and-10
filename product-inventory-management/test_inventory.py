"""Pytest unit test suite for the Product Inventory Management System."""

import pytest

from inventory import (
    apply_discount,
    calculate_total_price,
    check_stock,
    process_product_order,
)


def test_calculate_total_price_valid():
    """Test total price calculation with standard valid inputs."""
    assert calculate_total_price(500, 3) == 1500
    assert calculate_total_price(199.50, 2) == 399.0


def test_calculate_total_price_zero_price_boundary():
    """Test boundary condition where product price is zero."""
    assert calculate_total_price(0, 5) == 0


def test_calculate_total_price_negative_price_rejected():
    """Test that negative unit price raises ValueError."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_total_price(-100, 2)


def test_calculate_total_price_invalid_quantity_rejected():
    """Test that zero or negative quantity raises ValueError."""
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        calculate_total_price(250, 0)
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        calculate_total_price(250, -3)


def test_apply_discount_valid():
    """Test normal percentage discount calculation."""
    assert apply_discount(1000, 10) == 900
    assert apply_discount(2000, 25) == 1500


def test_apply_discount_boundary_values():
    """Test 0% and 100% discount boundary conditions."""
    assert apply_discount(750, 0) == 750
    assert apply_discount(750, 100) == 0
    assert apply_discount(0, 15) == 0


def test_apply_discount_invalid_percentage_rejected():
    """Test that discount percentages below 0 or above 100 raise ValueError."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(1000, -10)
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(1000, 125)


def test_apply_discount_negative_total_rejected():
    """Test that negative total amount raises ValueError."""
    with pytest.raises(ValueError, match="Total amount cannot be negative"):
        apply_discount(-500, 10)


def test_check_stock_available_and_exact_boundary():
    """Test sufficient stock and exact-match stock boundary."""
    assert check_stock(20, 5) is True
    assert check_stock(10, 10) is True


def test_check_stock_insufficient_and_zero_stock():
    """Test insufficient stock and zero available stock boundary."""
    assert check_stock(3, 5) is False
    assert check_stock(0, 1) is False


def test_check_stock_invalid_quantities_rejected():
    """Test negative available stock and non-positive requested quantity."""
    with pytest.raises(ValueError, match="Available stock cannot be negative"):
        check_stock(-5, 2)
    with pytest.raises(
        ValueError, match="Requested quantity must be greater than zero"
    ):
        check_stock(10, 0)
    with pytest.raises(
        ValueError, match="Requested quantity must be greater than zero"
    ):
        check_stock(10, -2)


def test_non_numeric_and_boolean_inputs_rejected():
    """Test that boolean and string arguments raise TypeError."""
    with pytest.raises(TypeError):
        calculate_total_price(True, 2)
    with pytest.raises(TypeError):
        check_stock(10, 2.5)
    with pytest.raises(TypeError):
        apply_discount("1000", 10)


def test_process_product_order_workflow():
    """Test integrated order workflow including stock deduction and missing SKU."""
    catalog = {"P1": {"name": "SSD", "price": 4000, "stock": 5}}
    final_price = process_product_order(catalog, "P1", 2, discount_percent=10)
    assert final_price == 7200
    assert catalog["P1"]["stock"] == 3

    with pytest.raises(KeyError):
        process_product_order(catalog, "UNKNOWN", 1)
