import hashlib

class BloomFilter:
    def __init__(self, size=1000, num_hashes=3):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hashes(self, item):
        hashes = []
        for i in range(self.num_hashes):
            hash_input = f"{item}_{i}".encode("utf-8")
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
            hashes.append(hash_value % self.size)
        return hashes

    def add(self, item):
        if not isinstance(item, str):
            item = str(item)
        for h in self._hashes(item):
            self.bit_array[h] = 1

    def __contains__(self, item):
        if not isinstance(item, str):
            item = str(item)
        return all(self.bit_array[h] == 1 for h in self._hashes(item))


def check_password_uniqueness(bloom_filter, passwords):
    results = {}
    for pwd in passwords:
        if not isinstance(pwd, str) or not pwd.strip():
            results[pwd] = "некоректний пароль"
            continue
        if pwd in bloom_filter:
            results[pwd] = "вже використаний"
        else:
            results[pwd] = "унікальний"
            bloom_filter.add(pwd)
    return results


if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")
