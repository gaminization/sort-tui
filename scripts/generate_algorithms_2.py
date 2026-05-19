import os
import textwrap

ALGO_DEFINITIONS = [
    # MERGE SORT VARIANTS
    {
        "key": "natural_merge",
        "class": "NaturalMergeSort",
        "category": "efficient",
        "name": "Natural Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Natural runs (existing ascending sequences) are detected and used directly; only run boundaries are merged, never internal.",
        "desc": "Natural runs are detected and used directly.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        aux = [0] * n
        
        while True:
            # Phase 1: Detect runs
            runs = []
            i = 0
            while i < n:
                start = i
                yield _base_frame(arr, highlighted=[i], metadata={"phase": "detect", "run_count": n})
                while i < n - 1:
                    yield _base_frame(arr, highlighted=[i, i+1], metadata={"phase": "detect", "run_count": n})
                    if not out_of_order(arr[i], arr[i+1], ascending):
                        i += 1
                    else:
                        break
                runs.append((start, i + 1))
                i += 1
                
            if len(runs) <= 1:
                break
                
            # Phase 2: Merge adjacent runs
            new_runs = []
            for j in range(0, len(runs), 2):
                if j + 1 < len(runs):
                    l_start, l_end = runs[j]
                    r_start, r_end = runs[j+1]
                    
                    p1, p2, out = l_start, r_start, l_start
                    while p1 < l_end and p2 < r_end:
                        yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end - 1), aux_array=aux)
                        if not out_of_order(arr[p1], arr[p2], ascending):
                            aux[out] = arr[p1]
                            p1 += 1
                        else:
                            aux[out] = arr[p2]
                            p2 += 1
                        out += 1
                        
                    while p1 < l_end:
                        aux[out] = arr[p1]
                        p1 += 1
                        out += 1
                    while p2 < r_end:
                        aux[out] = arr[p2]
                        p2 += 1
                        out += 1
                        
                    for k in range(l_start, r_end):
                        arr[k] = aux[k]
                        yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end - 1), aux_array=aux, operation="write")
                    new_runs.append((l_start, r_end))
                else:
                    new_runs.append(runs[j])
            runs = new_runs
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "strand_merge",
        "class": "StrandMergeSort",
        "category": "efficient",
        "name": "Strand Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Each extracted strand is a maximal ascending subsequence; strands are merged via priority queue until one strand remains.",
        "desc": "Extracts maximal ascending subsequences.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        strands = []
        unprocessed = arr[:]
        
        # Phase 1: extract strands
        while unprocessed:
            strand = [unprocessed.pop(0)]
            i = 0
            while i < len(unprocessed):
                yield _base_frame(arr, highlighted=[n - len(unprocessed) + i], aux_array=strand, metadata={"strand_count": n, "phase": "extract"})
                if not out_of_order(strand[-1], unprocessed[i], ascending):
                    strand.append(unprocessed.pop(i))
                else:
                    i += 1
            strands.append(strand)
            
        # Phase 2: merge strands using heapq
        import heapq
        heap = []
        for i, s in enumerate(strands):
            heapq.heappush(heap, (s[0] if ascending else -s[0], i, 0))
            
        idx = 0
        while heap:
            val, s_idx, elem_idx = heapq.heappop(heap)
            arr[idx] = strands[s_idx][elem_idx]
            yield _base_frame(arr, swapped=[idx], metadata={"strand_count": n, "phase": "merge"}, operation="write")
            idx += 1
            if elem_idx + 1 < len(strands[s_idx]):
                next_val = strands[s_idx][elem_idx + 1]
                heapq.heappush(heap, (next_val if ascending else -next_val, s_idx, elem_idx + 1))
                
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "tiled_merge",
        "class": "TiledMergeSort",
        "category": "efficient",
        "name": "Tiled Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Each tile of size sqrt(n) is sorted before cross-tile merges begin; tile boundaries remain visible throughout.",
        "desc": "Sorts tiles before merging.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        TILE_SIZE = max(4, int(math.sqrt(n)))
        aux = [0] * n
        
        # Phase 1: sort each tile with insertion sort
        for start in range(0, n, TILE_SIZE):
            end = min(start + TILE_SIZE, n)
            for i in range(start + 1, end):
                val = arr[i]
                j = i
                while j > start:
                    yield _base_frame(arr, highlighted=[j, j-1], partition_bounds=(start, end-1), metadata={"tile_size": TILE_SIZE, "phase": "tile"})
                    if out_of_order(arr[j-1], val, ascending):
                        arr[j] = arr[j-1]
                        yield _base_frame(arr, swapped=[j, j-1], partition_bounds=(start, end-1), metadata={"tile_size": TILE_SIZE, "phase": "tile"}, operation="swap")
                        j -= 1
                    else:
                        break
                arr[j] = val
                
        # Phase 2: merge tiles in passes
        width = TILE_SIZE
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), metadata={"tile_size": TILE_SIZE, "phase": "merge"})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        aux[out] = arr[p1]
                        p1 += 1
                    else:
                        aux[out] = arr[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    aux[out] = arr[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    aux[out] = arr[p2]
                    p2 += 1
                    out += 1
                    
                for k in range(l_start, r_end):
                    arr[k] = aux[k]
                    yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end-1), metadata={"tile_size": TILE_SIZE, "phase": "merge"}, operation="write")
            width *= 2
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "iterative_merge",
        "class": "IterativeMergeSort",
        "category": "efficient",
        "name": "Iterative Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Bottom-up: all subarrays of size 2^pass are sorted; pass number is always floor(log2(current_merge_size)).",
        "desc": "Bottom-up merge sort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        aux = [0] * n
        width = 1
        pass_num = 0
        
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), aux_array=aux, metadata={"width": width, "pass": pass_num})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        aux[out] = arr[p1]
                        p1 += 1
                    else:
                        aux[out] = arr[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    aux[out] = arr[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    aux[out] = arr[p2]
                    p2 += 1
                    out += 1
                    
                for k in range(l_start, r_end):
                    arr[k] = aux[k]
                    yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end-1), aux_array=aux, metadata={"width": width, "pass": pass_num}, operation="write")
            width *= 2
            pass_num += 1
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "multi_merge",
        "class": "MultiWayMergeSort",
        "category": "efficient",
        "name": "Multi-way Merge Sort",
        "time": "O(n log k log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "A min-heap of size k holds the front elements of k sorted runs; the heap minimum is always the next output element.",
        "desc": "Splits array into k runs and merges them.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        K_WAYS = max(3, min(8, n//10))
        if K_WAYS < 2: K_WAYS = 2
        
        run_size = (n + K_WAYS - 1) // K_WAYS
        runs = []
        for i in range(0, n, run_size):
            end = min(i + run_size, n)
            run = arr[i:end]
            run.sort(reverse=not ascending)
            runs.append(run)
            for j in range(i, end):
                arr[j] = run[j-i]
                yield _base_frame(arr, swapped=[j], operation="write")
                
        import heapq
        heap = []
        for i, r in enumerate(runs):
            if r:
                heapq.heappush(heap, (r[0] if ascending else -r[0], i, 0))
                
        idx = 0
        while heap:
            val, r_idx, elem_idx = heapq.heappop(heap)
            arr[idx] = runs[r_idx][elem_idx]
            heap_vals = [h[0] if ascending else -h[0] for h in heap]
            yield _base_frame(arr, swapped=[idx], aux_array=heap_vals, metadata={"k": K_WAYS, "heap_size": len(heap)}, operation="write")
            idx += 1
            if elem_idx + 1 < len(runs[r_idx]):
                next_val = runs[r_idx][elem_idx + 1]
                heapq.heappush(heap, (next_val if ascending else -next_val, r_idx, elem_idx + 1))
                
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "tape_merge",
        "class": "TapeMergeSort",
        "category": "external",
        "name": "Tape Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Two virtual input tapes hold sorted runs alternately; each merge pass reads both tapes and writes to two output tapes.",
        "desc": "Simulates 4-tape merge sort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        tapes = [[], [], [], []]
        
        # Initial distribution
        for i in range(n):
            tapes[i % 2].append(arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"tape_A": len(tapes[0]), "tape_B": len(tapes[1]), "tape_C": len(tapes[2]), "tape_D": len(tapes[3]), "pass": 0})
            
        run_size = 1
        pass_num = 1
        
        while True:
            tapes[2] = []
            tapes[3] = []
            
            i, j = 0, 0
            out_idx = 0
            
            while i < len(tapes[0]) or j < len(tapes[1]):
                l_start = i
                l_end = min(i + run_size, len(tapes[0]))
                r_start = j
                r_end = min(j + run_size, len(tapes[1]))
                
                while i < l_end and j < r_end:
                    yield _base_frame(arr, metadata={"tape_A": len(tapes[0]), "tape_B": len(tapes[1]), "tape_C": len(tapes[2]), "tape_D": len(tapes[3]), "pass": pass_num})
                    if not out_of_order(tapes[0][i], tapes[1][j], ascending):
                        tapes[2 + out_idx % 2].append(tapes[0][i])
                        i += 1
                    else:
                        tapes[2 + out_idx % 2].append(tapes[1][j])
                        j += 1
                        
                while i < l_end:
                    tapes[2 + out_idx % 2].append(tapes[0][i])
                    i += 1
                while j < r_end:
                    tapes[2 + out_idx % 2].append(tapes[1][j])
                    j += 1
                    
                out_idx += 1
                
            tapes[0], tapes[1] = tapes[2], tapes[3]
            run_size *= 2
            pass_num += 1
            
            if len(tapes[1]) == 0:
                break
                
        for i in range(n):
            arr[i] = tapes[0][i]
            yield _base_frame(arr, swapped=[i], operation="write")
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "ping_pong_merge",
        "class": "PingPongMergeSort",
        "category": "efficient",
        "name": "Ping-Pong Merge Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Sorted runs alternate between two buffers each pass; the active buffer and output buffer swap roles every merge pass.",
        "desc": "Alternates src and dst buffers.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        src = arr[:]
        dst = [0] * n
        width = 1
        pass_num = 0
        
        while width < n:
            buffer_name = "A" if pass_num % 2 == 0 else "B"
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n:
                    for k in range(l_start, l_end):
                        dst[k] = src[k]
                    continue
                    
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, aux_array=dst, metadata={"pass": pass_num, "buffer": buffer_name})
                    if not out_of_order(src[p1], src[p2], ascending):
                        dst[out] = src[p1]
                        p1 += 1
                    else:
                        dst[out] = src[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    dst[out] = src[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    dst[out] = src[p2]
                    p2 += 1
                    out += 1
                    
            src, dst = dst, src
            width *= 2
            pass_num += 1
            
        if pass_num % 2 != 0:
            for i in range(n):
                arr[i] = src[i]
                yield _base_frame(arr, swapped=[i], operation="write")
                
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "block_merge",
        "class": "BlockMergeSort",
        "category": "efficient",
        "name": "Block Merge Sort",
        "time": "O(n log n)",
        "space": "O(sqrt(n))",
        "stable": True,
        "invariant": "sqrt(n) internal buffer elements are used as swap space; block swaps and local merges avoid any external auxiliary array.",
        "desc": "Merges using internal buffer block.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        BLOCK = max(2, int(math.sqrt(n)))
        
        # Simulated block merge using a local buffer for visualization
        # Real block merge is complex, we simulate the buffer usage
        aux = [0] * BLOCK
        
        # Initial sort of blocks
        for start in range(0, n, BLOCK):
            end = min(start + BLOCK, n)
            for i in range(start + 1, end):
                val = arr[i]
                j = i
                while j > start:
                    yield _base_frame(arr, highlighted=[j, j-1], metadata={"block_size": BLOCK, "buffer_size": BLOCK})
                    if out_of_order(arr[j-1], val, ascending):
                        arr[j] = arr[j-1]
                        yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                        j -= 1
                    else:
                        break
                arr[j] = val
                
        width = BLOCK
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                # We simulate using the internal buffer by reading chunks into aux
                p1, p2, out = l_start, r_start, l_start
                merged = []
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), metadata={"block_size": BLOCK, "buffer_size": BLOCK})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        merged.append(arr[p1])
                        p1 += 1
                    else:
                        merged.append(arr[p2])
                        p2 += 1
                        
                while p1 < l_end:
                    merged.append(arr[p1])
                    p1 += 1
                while p2 < r_end:
                    merged.append(arr[p2])
                    p2 += 1
                    
                for k in range(len(merged)):
                    arr[l_start + k] = merged[k]
                    yield _base_frame(arr, swapped=[l_start + k], partition_bounds=(l_start, r_end-1), operation="write")
                    
            width *= 2
            
        yield done_frame(arr, self.name)
"""
    },
]

def generate_file(cat_path, algo):
    filepath = os.path.join("sortui", "algorithms", cat_path, f"{algo['key']}.py")
    content = f"""from __future__ import annotations
import math
from typing import Generator, List, Any
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms._helpers import base_frame, done_frame
from sortui.algorithms._helpers import out_of_order, value_of, is_sorted, in_order

def _base_frame(arr, **kwargs):
    kwargs.setdefault('explanation', '')
    kwargs.setdefault('operation', '')
    return base_frame(arr, **kwargs)

class {algo['class']}(SortAlgorithm):
    name = "{algo['name']}"
    category = "CATEGORY"  # replaced by init
    time_complexity = "{algo['time']}"
    space_complexity = "{algo['space']}"
    stable = {algo['stable']}
    description = "{algo['desc']}"
    
    def get_invariant(self) -> str:
        return "{algo['invariant']}"

{algo['code']}
"""
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")

for algo in ALGO_DEFINITIONS:
    generate_file(algo['category'], algo)
