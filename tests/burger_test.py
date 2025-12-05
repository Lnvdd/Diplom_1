import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers import (
    create_mock_ingredient,
    create_mock_bun,
    setup_burger_with_bun_and_ingredients,
    add_multiple_ingredients_to_burger,
    calculate_burger_price,
    verify_ingredients_in_receipt
)
from praktikum.ingredient_types import INGREDIENT_TYPE_SAUCE, INGREDIENT_TYPE_FILLING


class TestBurger:

    # Проверка булочек

    def test_set_bun_success(self, burger, white_bun):
        """Проверка установки булки"""
        burger.set_buns(white_bun)
        assert burger.bun == white_bun

    def test_set_bun_replace_existing(self, burger, white_bun, black_bun):
        """Проверка замены булки на другую"""
        burger.set_buns(white_bun)
        burger.set_buns(black_bun)
        assert burger.bun == black_bun

    # Проверка добавления ингредиентов

    def test_add_ingredient_one(self, burger, sauce_ingredient):
        """Проверка добавления одного ингредиента"""
        burger.add_ingredient(sauce_ingredient)
        assert len(burger.ingredients) == 1

    def test_add_ingredient_first_element(self, burger, sauce_ingredient):
        """Проверка, что добавленный ингредиент находится в начале списка"""
        burger.add_ingredient(sauce_ingredient)
        assert burger.ingredients[0] == sauce_ingredient

    def test_add_ingredient_multiple(self, burger, ingredient_count):
        """Проверка добавления нескольких ингредиентов"""
        ingredients = [
            create_mock_ingredient(f"Ingredient_{i}", INGREDIENT_TYPE_SAUCE, 50.0)
            for i in range(ingredient_count)
        ]
        burger = add_multiple_ingredients_to_burger(burger, ingredients)
        assert len(burger.ingredients) == ingredient_count

    def test_add_ingredient_keeps_order_first(self, burger, sauce_ingredient, filling_ingredient):
        """Проверка сохранения порядка: первый элемент"""
        burger.add_ingredient(sauce_ingredient)
        burger.add_ingredient(filling_ingredient)
        assert burger.ingredients[0] == sauce_ingredient

    def test_add_ingredient_keeps_order_second(self, burger, sauce_ingredient, filling_ingredient):
        """Проверка сохранения порядка: второй элемент"""
        burger.add_ingredient(sauce_ingredient)
        burger.add_ingredient(filling_ingredient)
        assert burger.ingredients[1] == filling_ingredient

    # Проверка удаления ингредиентов

    def test_remove_ingredient_decreases_count(self, burger):
        """Проверка уменьшения количества при удалении"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Second", INGREDIENT_TYPE_FILLING, 100.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2])
        burger.remove_ingredient(0)
        assert len(burger.ingredients) == 1

    def test_remove_ingredient_first_leaves_second(self, burger):
        """Проверка удаления первого ингредиента оставляет второй"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Second", INGREDIENT_TYPE_FILLING, 100.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2])
        burger.remove_ingredient(0)
        assert burger.ingredients[0] == ing2

    def test_remove_ingredient_middle(self, burger):
        """Проверка удаления среднего ингредиента"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Middle", INGREDIENT_TYPE_FILLING, 100.0)
        ing3 = create_mock_ingredient("Last", INGREDIENT_TYPE_SAUCE, 75.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2, ing3])
        burger.remove_ingredient(1)
        assert burger.ingredients[1] == ing3

    def test_remove_ingredient_at_index(self, burger, move_positions):
        """Проверка удаления ингредиента по индексу"""
        from_pos, to_pos = move_positions
        ingredients = [
            create_mock_ingredient(f"Ing_{i}", INGREDIENT_TYPE_SAUCE, 50.0)
            for i in range(3)
        ]
        burger = add_multiple_ingredients_to_burger(burger, ingredients)
        burger.remove_ingredient(from_pos)
        assert len(burger.ingredients) == 2

    # Проверка перемещения ингредиентов

    def test_move_ingredient_forward(self, burger):
        """Проверка перемещения ингредиента вперёд"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Second", INGREDIENT_TYPE_FILLING, 100.0)
        ing3 = create_mock_ingredient("Third", INGREDIENT_TYPE_SAUCE, 75.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2, ing3])
        burger.move_ingredient(0, 2)
        assert burger.ingredients[2] == ing1

    def test_move_ingredient_changes_first_position(self, burger):
        """Проверка изменения первой позиции при перемещении"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Second", INGREDIENT_TYPE_FILLING, 100.0)
        ing3 = create_mock_ingredient("Third", INGREDIENT_TYPE_SAUCE, 75.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2, ing3])
        burger.move_ingredient(0, 2)
        assert burger.ingredients[0] == ing2

    def test_move_ingredient_backward(self, burger):
        """Проверка перемещения ингредиента назад"""
        ing1 = create_mock_ingredient("First", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Second", INGREDIENT_TYPE_FILLING, 100.0)
        ing3 = create_mock_ingredient("Third", INGREDIENT_TYPE_SAUCE, 75.0)
        burger = add_multiple_ingredients_to_burger(burger, [ing1, ing2, ing3])
        burger.move_ingredient(2, 0)
        assert burger.ingredients[0] == ing3

    def test_move_ingredient_preserves_count(self, burger, move_positions):
        """Проверка сохранения количества при перемещении"""
        from_pos, to_pos = move_positions
        ingredients = [
            create_mock_ingredient(f"Ing_{i}", INGREDIENT_TYPE_SAUCE, 50.0)
            for i in range(3)
        ]
        burger = add_multiple_ingredients_to_burger(burger, ingredients)
        burger.move_ingredient(from_pos, to_pos)
        assert len(burger.ingredients) == 3

    # Проверка расчёта цены

    def test_price_only_bun(self, burger, white_bun):
        """Проверка цены только булки"""
        burger.set_buns(white_bun)
        expected_price = calculate_burger_price(100.0, [])
        assert burger.get_price() == expected_price

    def test_price_bun_and_one_ingredient(self, burger, white_bun, sauce_ingredient):
        """Проверка цены булки и одного ингредиента"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        expected_price = calculate_burger_price(100.0, [90.0])
        assert burger.get_price() == expected_price

    def test_price_bun_and_two_ingredients(self, burger, white_bun, sauce_ingredient, filling_ingredient):
        """Проверка цены булки и двух ингредиентов"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient, filling_ingredient)
        expected_price = calculate_burger_price(100.0, [90.0, 100.0])
        assert burger.get_price() == expected_price

    def test_price_various_combinations(self, burger, price_combinations):
        """Проверка цены различных комбинаций"""
        bun_price, ing_prices, expected_price = price_combinations
        bun = create_mock_bun("Test Bun", bun_price)
        burger.set_buns(bun)
        for price in ing_prices:
            ing = create_mock_ingredient("Test Ing", INGREDIENT_TYPE_SAUCE, price)
            burger.add_ingredient(ing)
        
        calculated_price = calculate_burger_price(bun_price, ing_prices)
        assert burger.get_price() == calculated_price
        assert burger.get_price() == expected_price

    def test_remove_ingredient_decreases_price(self, burger, white_bun):
        """Проверка уменьшения цены при удалении ингредиента"""
        ing1 = create_mock_ingredient("Item1", INGREDIENT_TYPE_SAUCE, 100.0)
        ing2 = create_mock_ingredient("Item2", INGREDIENT_TYPE_FILLING, 150.0)
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, ing1, ing2)
        
        price_before = burger.get_price()
        burger.remove_ingredient(0)
        price_after = burger.get_price()
        
        assert price_after == price_before - 100.0

    def test_burger_move_and_get_price(self, burger, white_bun):
        """Проверка цены после перемещения ингредиента"""
        ing1 = create_mock_ingredient("Item1", INGREDIENT_TYPE_SAUCE, 100.0)
        ing2 = create_mock_ingredient("Item2", INGREDIENT_TYPE_FILLING, 150.0)
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, ing1, ing2)
        burger.move_ingredient(0, 1)
        
        expected_price = calculate_burger_price(100.0, [100.0, 150.0])
        assert burger.get_price() == expected_price

    # Проверка чека

    def test_receipt_contains_bun(self, burger, white_bun, sauce_ingredient):
        """Проверка наличия булки в чеке"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        receipt = burger.get_receipt()
        assert "(==== White Bun ====)" in receipt

    def test_receipt_contains_ingredient(self, burger, white_bun, sauce_ingredient):
        """Проверка наличия ингредиента в чеке"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        receipt = burger.get_receipt()
        assert "spicy sauce" in receipt

    def test_receipt_contains_price(self, burger, white_bun, sauce_ingredient):
        """Проверка наличия цены в чеке"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        receipt = burger.get_receipt()
        assert "Price:" in receipt

    def test_receipt_shows_all_ingredients(self, burger, white_bun):
        """Проверка отображения всех ингредиентов в чеке"""
        ing1 = create_mock_ingredient("Item_0", INGREDIENT_TYPE_SAUCE, 50.0)
        ing2 = create_mock_ingredient("Item_1", INGREDIENT_TYPE_SAUCE, 50.0)
        ing3 = create_mock_ingredient("Item_2", INGREDIENT_TYPE_SAUCE, 50.0)
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, ing1, ing2, ing3)
        receipt = burger.get_receipt()
        
        assert verify_ingredients_in_receipt(receipt, ["Item_0", "Item_1", "Item_2"])

    def test_receipt_price_matches_get_price(self, burger, white_bun, sauce_ingredient):
        """Проверка соответствия цены в чеке и методе get_price"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        receipt = burger.get_receipt()
        expected_price = burger.get_price()
        
        assert f"Price: {expected_price}" in receipt

    def test_receipt_zero_ingredients(self, burger, white_bun):
        """Проверка чека без ингредиентов"""
        burger.set_buns(white_bun)
        receipt = burger.get_receipt()
        assert "(==== White Bun ====)" in receipt

    def test_receipt_one_ingredient(self, burger, white_bun):
        """Проверка чека с одним ингредиентом"""
        ing = create_mock_ingredient("Ing_0", INGREDIENT_TYPE_SAUCE, 25.0)
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, ing)
        receipt = burger.get_receipt()
        assert "Price:" in receipt

    def test_receipt_three_ingredients(self, burger, white_bun):
        """Проверка чека с тремя ингредиентами"""
        ingredients = [
            create_mock_ingredient(f"Ing_{i}", INGREDIENT_TYPE_SAUCE, 25.0)
            for i in range(3)
        ]
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, *ingredients)
        receipt = burger.get_receipt()
        assert "Price:" in receipt

    def test_receipt_five_ingredients(self, burger, white_bun):
        """Проверка чека с пятью ингредиентами"""
        ingredients = [
            create_mock_ingredient(f"Ing_{i}", INGREDIENT_TYPE_SAUCE, 25.0)
            for i in range(5)
        ]
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, *ingredients)
        receipt = burger.get_receipt()
        assert "Price:" in receipt

    # Комбинированные тесты

    def test_burger_add_and_remove_ingredient(self, burger, white_bun, sauce_ingredient):
        """Проверка добавления и удаления ингредиента"""
        burger = setup_burger_with_bun_and_ingredients(burger, white_bun, sauce_ingredient)
        burger.remove_ingredient(0)
        assert len(burger.ingredients) == 0