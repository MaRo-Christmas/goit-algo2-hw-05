import re
import time
import sys
import ipaddress
import hashlib
from math import log2

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def iter_ips_from_log(path):
    """Ітерує валідні IPv4 з лог-файлу. Некоректні рядки ігнорує."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = IP_RE.search(line)
            if not m:
                continue
            ip = m.group(0)
            try:
                ipaddress.ip_address(ip)
                yield ip
            except ValueError:
                continue

# ---------------- HyperLogLog ----------------

class HyperLogLog:
    """
    Простий HLL (64-бітний хеш, оцінка Флак-корекції + лінійна корекція для малих значень).
    error ≈ 1.04/sqrt(m), де m=2^p.
    """
    def __init__(self, p=14):
        if not (4 <= p <= 20):
            raise ValueError("p має бути в діапазоні [4, 20]")
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha_m = self._alpha(self.m)

    @staticmethod
    def _alpha(m):
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / m)

    @staticmethod
    def _rho(w, bits):
        if w == 0:
            return bits + 1
        return (w.bit_length() ^ bits) + 1 

    def _hash64(self, x: str) -> int:
        h = hashlib.sha1(x.encode("utf-8")).digest()
        return int.from_bytes(h[:8], "big", signed=False)

    def add(self, x: str):
        h = self._hash64(x)
        idx = h >> (64 - self.p)
        w = h & ((1 << (64 - self.p)) - 1)
        rho = self._rho(w, 64 - self.p)
        if rho > self.registers[idx]:
            self.registers[idx] = rho

    def count(self) -> float:
        inv_sum = 0.0
        for r in self.registers:
            inv_sum += 2.0 ** (-r)
        E = self.alpha_m * (self.m ** 2) / inv_sum

        V = self.registers.count(0)
        if E <= 5.0 * self.m / 2.0 and V > 0:
            E_lin = self.m * log2(1.0)
            import math
            E_lin = self.m * math.log(self.m / V)
            return E_lin

        return E

# ---------------- Підрахунки та порівняння ----------------

def exact_unique_count(path):
    s = set()
    for ip in iter_ips_from_log(path):
        s.add(ip)
    return len(s)

def hll_unique_count(path, p=14):
    hll = HyperLogLog(p=p)
    for ip in iter_ips_from_log(path):
        hll.add(ip)
    return hll.count()

def main():
    path = "lms-stage-access.log"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # Точний підрахунок
    t0 = time.perf_counter()
    exact = exact_unique_count(path)
    t1 = time.perf_counter()

    # HLL
    t2 = time.perf_counter()
    approx = hll_unique_count(path, p=14)
    t3 = time.perf_counter()

    exact_time = t1 - t0
    hll_time = t3 - t2

    # Вивід таблиці
    print("\nРезультати порівняння:")
    header = f"{'':27s}{'Точний підрахунок':>18s}   {'HyperLogLog':>12s}"
    row1 = f"{'Унікальні елементи':27s}{exact:18.1f}   {approx:12.1f}"
    row2 = f"{'Час виконання (сек.)':27s}{exact_time:18.3f}   {hll_time:12.3f}"
    print(header)
    print(row1)
    print(row2)

if __name__ == "__main__":
    main()
