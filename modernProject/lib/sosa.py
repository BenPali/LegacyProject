class Sosa:
    def __init__(self, value):
        self.value = int(value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Sosa({self.value})"

    def __eq__(self, other):
        if isinstance(other, Sosa):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)


def of_int(n):
    return Sosa(n)


def to_int(sosa):
    return sosa.value


def zero():
    return Sosa(0)


def one():
    return Sosa(1)


def eq(sosa1, sosa2):
    return sosa1.value == sosa2.value


def even(sosa):
    return sosa.value % 2 == 0


def half(sosa):
    return Sosa(sosa.value // 2)


def twice(sosa):
    return Sosa(sosa.value * 2)


def inc(sosa, n):
    return Sosa(sosa.value + n)


def branches(sosa):
    if sosa.value == 0:
        return []
    path = []
    n = sosa.value
    while n > 1:
        path.insert(0, 1 if n % 2 == 1 else 0)
        n = n // 2
    return path
