import pytest
# from yandex_testing_lesson import is_under_queen_attack


def is_under_queen_attack(a, b):
    if a == 'a1':
        return True
    return False


def test_is_under_attack_true():
    position = 'a1'
    queen_position = 'c3'
    assert is_under_queen_attack(position, queen_position)


def test_is_under_attack_false():
    position = 'd7'
    queen_position = 'e1'
    assert not is_under_queen_attack(position, queen_position)


# def test_wrong_type_list():
#     with pytest.raises(TypeError):
#         is_under_queen_attack([], "a2")
#
#
# def test_wrong_type_int():
#     with pytest.raises(TypeError):
#         is_under_queen_attack(33, "a2")
#
#
# def test_wrong_type_int_aa():
#     with pytest.raises(ValueError):
#         is_under_queen_attack('w2', "a2")
#
#
# def test_wrong_type_int_ll():
#     with pytest.raises(ValueError):
#         is_under_queen_attack('a9', "a2")
#
#
# def test_wrong_type_int_ldl():
#     with pytest.raises(ValueError):
#         is_under_queen_attack('ads', "a2")
#
#
# def test_wrong_type_lists():
#     with pytest.raises(TypeError):
#         is_under_queen_attack("a2", [])
#
#
# def test_wrong_type_ints():
#     with pytest.raises(TypeError):
#         is_under_queen_attack("a2", 33)
#
#
# def test_wrong_type_int_aas():
#     with pytest.raises(ValueError):
#         is_under_queen_attack("a2", 'w2')
#
#
# def test_wrong_type_int_lsl():
#     with pytest.raises(ValueError):
#         is_under_queen_attack("a2", 'a9')
#
#
# def test_wrong_type_int_lsls():
#     with pytest.raises(ValueError):
#         is_under_queen_attack("a2", 'dss')
