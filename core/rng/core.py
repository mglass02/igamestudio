import os, time, hashlib, struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class GLI19RNG:
    """
    GLI-19 §3 compliant CSPRNG.
    Uses AES-CTR-DRBG with multi-source seeding.
    Source code must be submitted to GLI with certification request.
    """
    RESEED_INTERVAL = 10_000  # §3.3.2c: periodic re-seeding

    def __init__(self):
        self._draws = 0
        self._seed()

    def _seed(self):
        # §3.3.2b: must NOT seed from time alone — combine sources
        entropy = (
            os.urandom(32)           # OS CSPRNG (primary entropy)
            + struct.pack('>Q', time.time_ns())  # timestamp
            + struct.pack('>Q', id(self))        # process memory addr
        )
        self._key = hashlib.sha256(entropy).digest()
        self._counter = int.from_bytes(os.urandom(16), 'big')

    def _reseed_if_needed(self):
        # §3.3.2c: periodic state modification via fresh entropy
        if self._draws % self.RESEED_INTERVAL == 0:
            new_entropy = os.urandom(16)
            self._key = hashlib.sha256(self._key + new_entropy).digest()

    def random_bytes(self, n: int) -> bytes:
        self._reseed_if_needed()
        self._draws += 1
        self._counter += 1
        ctr = self._counter.to_bytes(16, 'big')
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(ctr))
        enc = cipher.encryptor()
        return enc.update(bytes(n)) + enc.finalize()[:n]

    def randbelow(self, n: int) -> int:
        """
        §3.2.3: Unbiased uniform int in [0, n).
        Rejection sampling eliminates modulo bias.
        """
        if n <= 0:
            raise ValueError("n must be positive")
        bit_len = n.bit_length()
        byte_len = (bit_len + 7) // 8
        mask = (1 << bit_len) - 1
        while True:
            candidate = int.from_bytes(self.random_bytes(byte_len), 'big') & mask
            if candidate < n:   # reject if >= n (§3.2.3a: discard is permitted)
                return candidate

    def shuffle(self, lst: list) -> list:
        """Fisher-Yates — provably unbiased shuffle for deck-style games."""
        a = list(lst)
        for i in range(len(a) - 1, 0, -1):
            j = self.randbelow(i + 1)
            a[i], a[j] = a[j], a[i]
        return a

# Singleton — one RNG instance per process
_rng = GLI19RNG()

def randbelow(n):  return _rng.randbelow(n)
def shuffle(lst):  return _rng.shuffle(lst)
def random_bytes(n): return _rng.random_bytes(n)