"""Host-side tests for P1GL signed one's-complement coordinate encoding."""
MASK = (1 << 18) - 1

def encode(value):
    if not -(1 << 17) + 1 <= value <= (1 << 17) - 1:
        raise ValueError('outside PDP-1 ones-complement integer range')
    return value if value >= 0 else (~(-value)) & MASK

def decode(word):
    word &= MASK
    if word == MASK:
        return 0
    return word if not word & (1 << 17) else -((~word) & MASK)

def test_round_trip():
    for n in [-131071, -8192, -1, 0, 1, 8192, 131071]:
        assert decode(encode(n)) == n

def test_calibration():
    assert encode(8192) == 0o20000
    assert encode(-8192) == 0o757777
    assert decode(0o777777) == 0

if __name__ == '__main__':
    test_round_trip()
    test_calibration()
    print('PASS: coordinate encoding and calibration constants')
