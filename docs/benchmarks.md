# Performance Benchmarks

The `sort-tui` engine includes an internal benchmarking utility that bypasses the graphical rendering (`curses`) entirely. This allows for raw profiling of the algorithm generators to track comparisons, swaps, array writes, and overall execution time.

## Machine Specifications

> [!NOTE]
> The benchmarks below were executed on an **x86_64** architecture running **Python 3.10.12**.

**Execution Command:**
```bash
sortui --benchmark bubble insertion selection cocktail_shaker shellsort comb merge quicksort heapsort timsort introsort dual_pivot_quicksort counting radix_lsd radix_msd bucket pdqsort adaptive_merge --size 500 --seed 42
```

## Benchmark Leaderboard 

*(Array Size: `500`, Distribution: `Random`)*

| Algorithm | Time (ms) | Comparisons | Swaps | Writes | Frames |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **counting** | 9.001 | 0 | 0 | 500 | 1,501 |
| **radix_msd** | 25.467 | 0 | 0 | 1,498 | 2,997 |
| **radix_lsd** | 25.501 | 0 | 0 | 1,500 | 3,001 |
| **quicksort** | 93.055 | 4,575 | 2,019 | 0 | 6,925 |
| **bucket** | 97.112 | 3,231 | 0 | 3,787 | 7,997 |
| **introsort** | 105.486 | 4,430 | 1,480 | 1,579 | 7,901 |
| **merge** | 114.212 | 3,849 | 0 | 4,492 | 8,342 |
| **dual_pivot_quicksort** | 131.000 | 4,808 | 0 | 4,852 | 10,140 |
| **comb** | 141.879 | 9,370 | 1,848 | 0 | 11,219 |
| **pdqsort** | 143.260 | 6,624 | 3,200 | 197 | 10,065 |
| **shellsort** | 158.952 | 5,633 | 0 | 5,876 | 14,482 |
| **heapsort** | 167.553 | 7,462 | 4,070 | 0 | 11,533 |
| **timsort** | 272.860 | 10,077 | 0 | 10,095 | 20,665 |
| **adaptive_merge**| 642.940 | 21,502 | 0 | 25,401 | 46,905 |
| **selection** | 1382.751 | 124,750 | 500 | 0 | 125,251 |
| **insertion** | 1665.994 | 61,682 | 0 | 61,687 | 123,869 |
| **cocktail_shaker**| 2300.964 | 92,365 | 61,188 | 0 | 153,554 |
| **bubble** | 2656.198 | 124,659 | 61,188 | 0 | 185,848 |

## Frame Count Distinctiveness

In an educational visualization tool, the number of `yield` statements ("Frames") directly correlates to how much work the algorithm does. Measuring frame counts gives us a direct proxy for computational complexity that is entirely immune to system background load, cache misses, or Python VM overhead.

### Top Performers (Size = 100)

| Algorithm | Frames | Category |
| :--- | :--- | :--- |
| **Quantum Sort** | 102 | Specialized / Joke Sorts |
| **Parallel Bubble Sort** | 169 | Parallel Sorts |
| **Twin Heapsort** | 201 | Hybrid Variants |
| **Binomial Heap Sort** | 202 | CATEGORY |
| **Parallel Merge Sort** | 203 | Parallel Sorts |
| **Fibonacci Heap Sort** | 204 | CATEGORY |

*(Note: Joke sorts intentionally circumvent complexity laws. Real-world winners here leverage heavy parallelism or highly optimized tree structures).*

## TimSort Adaptation Ratio

Adaptive sorting algorithms recognize pre-existing structure in the array. Since `sort-tui` frame count tracks algorithmic operations flawlessly, we can directly measure an algorithm's capability to adapt. 

Here is the frame count measurement for **TimSort** across two topological inputs (`size=500`):

- **TimSort Frames (Random Array)**: 19,266 frames 
- **TimSort Frames (Nearly Sorted)**: 2,246 frames
- **Adaptation Ratio:** 🚀 **8.58x more efficient**

> [!TIP]
> Try running this yourself! `sortui --benchmark timsort --distribution nearly_sorted --size 500`
