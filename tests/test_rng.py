"""
Run these tests BEFORE submitting. GLI §3.2.2 runs equivalent tests
at 99% confidence. If your RNG fails here, it fails certification.
"""
import scipy.stats as stats
from core.rng.core import randbelow
from collections import Counter

N = 100_000   # sample size
RANGE = 100   # uniform over [0, 99]

def test_chi_square():
    """§3.2.2a: Total Distribution / Chi-square test."""
    counts = Counter(randbelow(RANGE) for _ in range(N))
    expected = N / RANGE
    chi2, p = stats.chisquare([counts.get(i, 0) for i in range(RANGE)])
    assert p > 0.01, f"Chi-square FAIL: p={p:.4f} (bias detected)"
    print(f"Chi-square PASS: p={p:.4f}")

def test_runs():
    """§3.2.2d: Corrected Runs test for independence."""
    seq = [randbelow(2) for _ in range(N)]
    
    # Count n1 (zeros) and n2 (ones)
    n1 = seq.count(0)
    n2 = seq.count(1)
    n = n1 + n2
    
    # Count observed runs
    runs = 1
    for i in range(1, n):
        if seq[i] != seq[i-1]:
            runs += 1
            
    # Calculate Expected Runs and Standard Deviation
    # E[R] = (2 * n1 * n2) / n + 1
    expected_runs = (2 * n1 * n2) / n + 1
    
    # Variance = (2*n1*n2 * (2*n1*n2 - n)) / (n^2 * (n-1))
    variance = (2 * n1 * n2 * (2 * n1 * n2 - n)) / ((n**2) * (n - 1))
    std = variance ** 0.5
    
    z = abs(runs - expected_runs) / std
    
    assert z < 3.0, f"Runs test FAIL: z={z:.2f} (not independent)"
    print(f"Runs test PASS: z={z:.2f}")

def test_serial_correlation():
    """§3.2.2f: Serial correlation — draw N+1 should not depend on draw N."""
    seq = [randbelow(RANGE) for _ in range(N)]
    corr = sum(seq[i]*seq[i+1] for i in range(N-1)) / (N-1)
    mean = (RANGE - 1) / 2
    expected_corr = mean * mean
    deviation = abs(corr - expected_corr) / (RANGE * RANGE)
    assert deviation < 0.01, f"Serial correlation FAIL: dev={deviation:.4f}"
    print(f"Serial correlation PASS: deviation={deviation:.5f}")

if __name__ == "__main__":
    test_chi_square()
    test_runs()
    test_serial_correlation()
    print("All RNG tests passed ✓")