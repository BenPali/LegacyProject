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
