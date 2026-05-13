#!/usr/bin/env bash

set -e

echo "Running smoke tests..."

echo "1. Checking sortui --version..."
if ! sortui --version | grep -q "sortui"; then
    echo "[FAIL] sortui --version does not contain 'sortui'"
    exit 1
fi
echo "[PASS] sortui --version"

echo "2. Checking sortui --list..."
LIST_OUT=$(sortui --list)
if ! echo "$LIST_OUT" | grep -q "Simple Sorts"; then
    echo "[FAIL] sortui --list missing 'Simple Sorts'"
    exit 1
fi
if ! echo "$LIST_OUT" | grep -q "Efficient Sorts"; then
    echo "[FAIL] sortui --list missing 'Efficient Sorts'"
    exit 1
fi
echo "[PASS] sortui --list"

echo "3. Checking sortui --benchmark..."
if ! sortui --benchmark bubble insertion quicksort --size 30 --seed 42 > /dev/null; then
    echo "[FAIL] sortui --benchmark failed"
    exit 1
fi
echo "[PASS] sortui --benchmark"

echo "4. Checking algorithm correctness (Bubble, Tim, RadixLSD)..."
python3 -c "
from sortui.algorithms.simple import BubbleSort
from sortui.algorithms.hybrid import TimSort
from sortui.algorithms.non_comparison import RadixLSDSort
import random

def test_algo(cls):
    arr = [random.randint(1, 1000) for _ in range(50)]
    engine = cls()
    list(engine.sort(arr))
    if not all(arr[i] <= arr[i+1] for i in range(len(arr)-1)):
        raise Exception(f'{cls.name} failed to sort correctly')

test_algo(BubbleSort)
test_algo(TimSort)
test_algo(RadixLSDSort)
"
echo "[PASS] Algorithms correctly sorted array"

echo "5. Checking TimSort frame efficiency (nearly-sorted vs random)..."
python3 -c "
from sortui.algorithms.hybrid import TimSort
import random

def count_frames(arr):
    return len(list(TimSort().sort(arr)))

arr_random = [random.randint(1, 1000) for _ in range(100)]
arr_nearly_sorted = sorted(arr_random)
arr_nearly_sorted[0], arr_nearly_sorted[-1] = arr_nearly_sorted[-1], arr_nearly_sorted[0]

random_frames = count_frames(arr_random)
nearly_sorted_frames = count_frames(arr_nearly_sorted)

if nearly_sorted_frames >= random_frames:
    raise Exception(f'TimSort not efficient on nearly-sorted: nearly_sorted_frames={nearly_sorted_frames}, random_frames={random_frames}')
"
echo "[PASS] TimSort efficiency check"

echo -e "\nAll smoke tests passed!"
