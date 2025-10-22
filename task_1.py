import random
import time


class LRUCache:

    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None  # type: LRUCache.Node | None
            self.next = None  # type: LRUCache.Node | None

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = self.Node(0, 0)
        self.tail = self.Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_head(node)
            return node.value
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            new_node = self.Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)

            if len(self.cache) > self.capacity:
                lru = self.tail.prev
                if lru:
                    self._remove(lru)
                    del self.cache[lru.key]

    def get_keys(self):
        return list(self.cache.keys())

    def delete(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            del self.cache[key]


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — Range
            if random.random() < p_hot:  # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:  # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    array[index] = value


def range_sum_with_cache(array, left, right, cache):
    key = (left, right)
    result = cache.get(key)

    if result == -1:
        result = sum(array[left : right + 1])
        cache.put(key, result)

    return result


def update_with_cache(array, index, value, cache):
    array[index] = value

    keys_to_delete = []
    for key in cache.get_keys():
        left, right = key
        if left <= index <= right:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        cache.delete(key)


def run_benchmark():
    N = 100_000
    Q = 50_000
    CACHE_CAPACITY = 1000

    print("LRU-кеш оптимізація доступу до даних")
    print(f"Розмір масиву: {N:,}")
    print(f"Кількість запитів: {Q:,}")
    print(f"Ємність кешу: {CACHE_CAPACITY:,}")

    array_base = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

    update_count = sum(1 for q in queries if q[0] == "Update")
    range_count = Q - update_count

    print("-" * 60)
    print(f"Range запитів: {range_count:,} ({range_count/Q*100:.1f}%)")
    print(f"Update запитів: {update_count:,} ({update_count/Q*100:.1f}%)")
    print("-" * 60)

    print("Тестування БЕЗ кешу...")
    array_no_cache = array_base.copy()
    start_time = time.time()

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_no_cache(array_no_cache, left, right)
        else:
            _, index, value = query
            update_no_cache(array_no_cache, index, value)

    time_no_cache = time.time() - start_time

    print("Тестування з LRU-кешем...")
    array_with_cache = array_base.copy()
    cache = LRUCache(CACHE_CAPACITY)
    start_time = time.time()

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_with_cache(array_with_cache, left, right, cache)
        else:
            _, index, value = query
            update_with_cache(array_with_cache, index, value, cache)

    time_with_cache = time.time() - start_time

    speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 0

    print("=" * 60)
    print("РЕЗУЛЬТАТИ")
    print(f"Без кешу  : {time_no_cache:6.2f} c")
    print(f"LRU-кеш   : {time_with_cache:6.2f} c  (прискорення х{speedup:.1f})")
    print("=" * 60)

    # перевірка
    print("ПЕРЕВІРКА:")
    if array_no_cache == array_with_cache:
        print("ОК: обидва методи дали однакові результати")
    else:
        print("Увага: результати відрізняються!")


if __name__ == "__main__":
    run_benchmark()
