# Benchmarks

The `sort-tui` engine includes an internal benchmarking utility that bypasses the graphical rendering (`curses`) entirely. This allows for raw profiling of the algorithm generators to test comparisons, swaps, arrays writes, and execution time.

## Machine Specifications

- **Architecture:** x86_64
- **Runtime:** Python 3.10.12
- **Command:** `sortui --benchmark bubble insertion selection cocktail_shaker shellsort comb merge quicksort heapsort timsort introsort dual_pivot_quicksort counting radix_lsd radix_msd bucket pdqsort adaptive_merge --size 500 --seed 42`

## Benchmark Leaderboard (Size=500, Random Distribution)

| Algorithm | Time(ms) | Comparisons | Swaps | Writes | Frames |
| --- | --- | --- | --- | --- | --- |
| counting | 9.001 | 0 | 0 | 500 | 1,501 |
| radix_msd | 25.467 | 0 | 0 | 1,498 | 2,997 |
| radix_lsd | 25.501 | 0 | 0 | 1,500 | 3,001 |
| quicksort | 93.055 | 4,575 | 2,019 | 0 | 6,925 |
| bucket | 97.112 | 3,231 | 0 | 3,787 | 7,997 |
| introsort | 105.486 | 4,430 | 1,480 | 1,579 | 7,901 |
| merge | 114.212 | 3,849 | 0 | 4,492 | 8,342 |
| dual_pivot_quicksort | 131.000 | 4,808 | 0 | 4,852 | 10,140 |
| comb | 141.879 | 9,370 | 1,848 | 0 | 11,219 |
| pdqsort | 143.260 | 6,624 | 3,200 | 197 | 10,065 |
| shellsort | 158.952 | 5,633 | 0 | 5,876 | 14,482 |
| heapsort | 167.553 | 7,462 | 4,070 | 0 | 11,533 |
| timsort | 272.860 | 10,077 | 0 | 10,095 | 20,665 |
| adaptive_merge | 642.940 | 21,502 | 0 | 25,401 | 46,905 |
| selection | 1382.751 | 124,750 | 500 | 0 | 125,251 |
| insertion | 1665.994 | 61,682 | 0 | 61,687 | 123,869 |
| cocktail_shaker | 2300.964 | 92,365 | 61,188 | 0 | 153,554 |
| bubble | 2656.198 | 124,659 | 61,188 | 0 | 185,848 |

## Frame Count Distinctiveness

In an educational visualization tool, the number of `yield` statements ("Frames") directly correlates to how much work the algorithm does. Measuring frame counts gives us a direct proxy for work complexity that is immune to system background load, cache misses, or Python overhead. 

Below is the absolute frame count for each non-joke algorithm sorting the same `size=100` random array:

| Algorithm | Frames | Category |
|---|---|---|
| Quantum Sort | 102 | Specialized / Joke Sorts |
| Parallel Bubble Sort | 169 | Parallel Sorts |
| Twin Heapsort | 201 | Hybrid Variants |
| Parallel Merge Sort | 203 | Parallel Sorts |
| Proxmap Sort | 227 | Numerical Sorts |
| Shear Sort | 241 | Parallel Sorts |
| AKS Network Sort | 262 | Parallel Sorts |
| Cartesian Tree Sort | 293 | Adaptive Sorts |
| External Merge Sort | 297 | External Sorts |
| Sample Sort | 302 | Parallel Sorts |
| Ternary Search Tree Sort | 401 | String-Specific Sorts |
| Replacement Selection | 404 | External Sorts |
| Burstsort | 418 | Non-Comparison Sorts |
| Three-Way Merge Sort | 431 | Specialized / Joke Sorts |
| Polyphase Merge Sort | 441 | External Sorts |
| Radix MSD Sort | 517 | Non-Comparison Sorts |
| Cascade Merge Sort | 533 | External Sorts |
| Radix LSD Sort | 601 | Non-Comparison Sorts |
| Parallel Radix Sort | 604 | Parallel Sorts |
| MSD String Sort | 624 | String-Specific Sorts |
| Postman Sort | 635 | Non-Comparison Sorts |
| Library Sort | 725 | Efficient Sorts |
| Kirkpatrick-Reisch Sort | 753 | Numerical Sorts |
| Flashsort | 756 | Non-Comparison Sorts |
| Tree Sort | 797 | Efficient Sorts |
| Columnsort | 801 | Parallel Sorts |
| Quick-Heapsort | 823 | Hybrid Variants |
| Bucket Sort | 885 | Non-Comparison Sorts |
| Spreadsort | 886 | Non-Comparison Sorts |
| American Flag Sort | 887 | String-Specific Sorts |
| Block Quicksort | 895 | Adaptive Sorts |
| In-place Radix Sort | 914 | Numerical Sorts |
| External Distribution Sort | 922 | External Sorts |
| Patience Sort | 944 | Efficient Sorts |
| Quicksort | 960 | Efficient Sorts |
| Tournament Sort | 1,028 | Efficient Sorts |
| Three-Way String Quicksort | 1,038 | String-Specific Sorts |
| Recombinant Sort | 1,056 | Non-Comparison Sorts |
| Cube Sort | 1,135 | Efficient Sorts |
| Counting Sort | 1,186 | Non-Comparison Sorts |
| Dual-Pivot Quicksort | 1,214 | Hybrid Sorts |
| Merge Sort | 1,240 | Efficient Sorts |
| Grailsort | 1,261 | Adaptive Sorts |
| Pigeonhole Sort | 1,286 | Non-Comparison Sorts |
| Bead Sort | 1,292 | Specialized / Joke Sorts |
| Introsort | 1,317 | Hybrid Sorts |
| Quick-Merge Sort | 1,327 | Hybrid Variants |
| Pattern-Defeating Quicksort | 1,330 | Adaptive Sorts |
| Crumsort | 1,348 | Hybrid Sorts |
| Oscillating Sort | 1,377 | External Sorts |
| Ternary Heapsort | 1,404 | Hybrid Variants |
| Splaysort | 1,437 | Adaptive Sorts |
| Block Sort | 1,439 | Efficient Sorts |
| Binary Quicksort | 1,541 | Numerical Sorts |
| Fluxsort | 1,561 | Hybrid Sorts |
| Comb Sort | 1,578 | Efficient Sorts |
| van Emde Boas Sort | 1,599 | Other Sorts |
| Heapsort | 1,616 | Efficient Sorts |
| Adaptive Heapsort | 1,617 | Adaptive Sorts |
| Bottom-Up Heapsort | 1,644 | Hybrid Variants |
| Smoothsort | 1,716 | Efficient Sorts |
| Weak Heapsort | 1,782 | Hybrid Variants |
| Timsort | 1,851 | Hybrid Sorts |
| Shell Sort | 1,890 | Efficient Sorts |
| Strand Sort | 1,969 | Simple Sorts |
| Odd-Even Sort | 2,083 | Simple Sorts |
| Batcher's Sort | 2,084 | Parallel Sorts |
| Bitonic Sort | 2,560 | Specialized / Joke Sorts |
| Multistep Bitonic Sort | 2,564 | Parallel Sorts |
| X + Y Sort | 2,603 | Other Sorts |
| Adaptive Bitonic Sort | 2,659 | Adaptive Sorts |
| In-place Merge Sort | 2,780 | Efficient Sorts |
| Franceschini's Sort | 2,785 | Specialized / Joke Sorts |
| Binary Insertion Sort | 2,857 | Hybrid Variants |
| Adaptive Merge Sort | 3,854 | Adaptive Sorts |
| Pairwise Network Sort | 4,420 | Parallel Sorts |
| Insertion Sort | 4,761 | Simple Sorts |
| Merge-Insertion Sort | 4,791 | Specialized / Joke Sorts |
| Wiggle Sort | 4,902 | Adaptive Sorts |
| Selection Sort | 5,051 | Simple Sorts |
| Linear Sort | 5,362 | Specialized / Joke Sorts |
| Cocktail Shaker Sort | 6,056 | Simple Sorts |
| Cube Network Sort | 6,328 | Sorting Networks |
| Brick Sort | 6,392 | Other Sorts |
| Gnome Sort | 6,796 | Simple Sorts |
| Bubble Sort | 6,908 | Simple Sorts |
| Exchange Sort | 7,184 | Simple Sorts |
| Sorting Network | 7,185 | Specialized / Joke Sorts |
| Pancake Sort | 7,356 | Other Sorts |
| Shuffle-Exchange Network | 8,391 | Sorting Networks |
| Merge-Exchange Sort | 11,606 | Other Sorts |
| Bitonic Merge Network | 11,695 | Sorting Networks |
| Cycle Sort | 14,307 | Simple Sorts |
| Topological Sort | 15,150 | Other Sorts |

## TimSort Adaptation Ratio

Adaptive sorting algorithms recognize pre-existing structure in the array. Since `sort-tui` frame count tracks algorithmic operations flawlessly, we can directly measure an algorithm's capability to adapt. 

Here is the frame count measurement for **TimSort** across two topological inputs (`size=500`):

- **TimSort Frames (Random Array)**: 19,266 frames 
- **TimSort Frames (Nearly Sorted)**: 2,246 frames
- **TimSort Adaptation Ratio:** 8.58x more efficient
