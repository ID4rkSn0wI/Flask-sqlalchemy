import pytest
from yandex_testing_lesson import Rectangle


def test_is_under_attack_true():
    a, b = 3, 4
    r = Rectangle(a, b)
    assert r.get_area() == 12
    assert r.get_perimeter() == a * 2 + b * 2


def test_is_under_attack_false():
    a, b = 3, '4'
    with pytest.raises(TypeError):
        r = Rectangle(a, b)


def test_is_under_attack_falseh():
    a, b = '3', 4
    with pytest.raises(TypeError):
        r = Rectangle(a, b)


def test_is_under_attack_faglse():
    a, b = 3, [2]
    with pytest.raises(TypeError):
        r = Rectangle(a, b)


def test_is_under_attack_falfse():
    a, b = [2], 3
    with pytest.raises(TypeError):
        r = Rectangle(a, b)


def test_is_under_attack_rfalse():
    a, b = -1, 2
    with pytest.raises(ValueError):
        r = Rectangle(a, b)


def test_is_under_attack_faldse():
    a, b = 1, -2
    with pytest.raises(ValueError):
        r = Rectangle(a, b)
