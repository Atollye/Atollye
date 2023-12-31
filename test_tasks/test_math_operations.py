import pytest


# Классы эквивалентности для функции sum():
# -50 (отрицательное число), 2 (целое положительное число), 3.45 (рациональное число).
# Заранее предполагаем, что "от перемены мест слагаемых сумма не меняется"

def sum(a, b):
    return a + b

@pytest.mark.parametrize("a, b, result", [
    (2, 2, 4), (-50, -50, -100), (-50, 2, -48),
    (-50, 3.45, -46.55), (2, 3.45, 5.45), (3.45, 3.45, 6.9)
])
def test_sum(a, b, result):
    assert sum(a, b) == result


    
    

# Для функции sub классы эквивалентности аналогичны функции sum
# -30, 13.7, 48

def sub(a, b):
    return a - b

@pytest.mark.parametrize("a, b, result", [
    (48, 48, 0), 
    (-30, -30, 0),
    (-30, 48, -78),
    (-30, 13.7, -43.7),
    (48, 13.7, 34.3),
    (13.7, 13.7, 0)
])
def test_sub(a, b, result):
    assert sub(a, b) == result

    
    

# Для mul кроме отрицательного, положительного и рационального числа берем еще 0, 
# поскольку он при умножении ведет себя иначе, чем -30, 13.7 и 48
# Опять же исходим из коммутативности умножения
# Итого значения: -30, 0, 13.7, 48


def mul(a, b):
    return a * b

@pytest.mark.parametrize("a, b, result", [
    (-30, 0, 0), 
    (-30, 13.7, -411),
    (-30, 48, -1440),
    (0, 13.7, 0),
    (0, 48, 0),
    (13.7, 48, 657.6)
])
def test_mul(a, b, result):
    assert round(mul(a, b), 1) == result

    
    
# Для функции div классы эквивалентности тоже будут -30, 0, 13.7, 48, 
# но для b = 0 пишем отдельный тест, потому что эта операция выбросит исключение
# и нам нужен assert именно на исключение


def div(a, b):
    return a / b

@pytest.mark.parametrize("a, b, result", [
    (-30, 13.7, -2.2),
    (48, -30, -1.6),
    (13.7, 48, 0.3)
])
def test_div(a, b, result):
    assert round(div(a, b), 1) == result

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        div(13.7, 0)