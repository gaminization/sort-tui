import os
import textwrap

ALGO_DEFINITIONS = [
    {
        "key": "two_way_bubble",
        "class": "TwoWayBubbleSort",
        "category": "simple",
        "name": "Two-Way Bubble Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": True,
        "invariant": "Both ends of the unsorted region shrink each pass — forward pass bubbles largest right, backward pass bubbles smallest left.",
        "desc": "Bidirectional bubble sort variant.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        left, right = 0, n - 1
        sorted_idx = []
        while left < right:
            swapped_any = False
            for i in range(left, right):
                yield base_frame(arr, highlighted=[i, i+1], sorted_indices=sorted_idx, explanation="Forward sweep")
                if out_of_order(arr[i], arr[i+1], ascending):
                    arr[i], arr[i+1] = arr[i+1], arr[i]
                    swapped_any = True
                    yield base_frame(arr, swapped=[i, i+1], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.append(right)
            right -= 1
            if not swapped_any:
                break
            swapped_any = False
            for i in range(right, left, -1):
                yield base_frame(arr, highlighted=[i-1, i], sorted_indices=sorted_idx, explanation="Backward sweep")
                if out_of_order(arr[i-1], arr[i], ascending):
                    arr[i-1], arr[i] = arr[i], arr[i-1]
                    swapped_any = True
                    yield base_frame(arr, swapped=[i-1, i], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.append(left)
            left += 1
            if not swapped_any:
                break
        sorted_idx.extend(range(left, right+1))
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "optimized_bubble",
        "class": "OptimizedBubbleSort",
        "category": "simple",
        "name": "Optimized Bubble Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": True,
        "invariant": "last_swap tracks the rightmost swap position; elements beyond last_swap are confirmed sorted and never re-examined.",
        "desc": "Bubble sort that tracks the last swap index.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        end = n
        sorted_idx = []
        while end > 1:
            new_end = 0
            for i in range(1, end):
                yield base_frame(arr, highlighted=[i-1, i], sorted_indices=sorted_idx, partition_bounds=(0, end), explanation="Scanning unsorted region")
                if out_of_order(arr[i-1], arr[i], ascending):
                    arr[i-1], arr[i] = arr[i], arr[i-1]
                    new_end = i
                    yield base_frame(arr, swapped=[i-1, i], sorted_indices=sorted_idx, partition_bounds=(0, end), operation="swap")
            for j in range(new_end, end):
                if j not in sorted_idx:
                    sorted_idx.append(j)
            end = new_end
        sorted_idx.extend(range(0, end))
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "flag",
        "class": "DutchNationalFlagSort",
        "category": "simple",
        "name": "Dutch National Flag Sort",
        "time": "O(n)",
        "space": "O(1)",
        "stable": False,
        "invariant": "arr[0..lo-1] are all small, arr[lo..mid-1] are all medium, arr[hi+1..n-1] are all large — three strict regions at every step.",
        "desc": "Sorts an array of 3 distinct value ranges in linear time.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        # Find split points roughly based on values
        min_v, max_v = value_of(min(arr, key=value_of)), value_of(max(arr, key=value_of))
        range_v = max_v - min_v
        if range_v == 0:
            yield done_frame(arr, self.name)
            return
        p1 = min_v + range_v / 3
        p2 = min_v + 2 * range_v / 3
        lo, mid, hi = 0, 0, n - 1
        sorted_idx = []
        while mid <= hi:
            yield base_frame(arr, highlighted=[mid], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), explanation="Classifying current element")
            val = value_of(arr[mid])
            if (val < p1 if ascending else val > p2):
                if lo != mid:
                    arr[lo], arr[mid] = arr[mid], arr[lo]
                    yield base_frame(arr, swapped=[lo, mid], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), operation="swap")
                sorted_idx.append(lo)
                lo += 1
                mid += 1
            elif (val >= p2 if ascending else val <= p1):
                if mid != hi:
                    arr[mid], arr[hi] = arr[hi], arr[mid]
                    yield base_frame(arr, swapped=[mid, hi], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), operation="swap")
                sorted_idx.append(hi)
                hi -= 1
            else:
                mid += 1
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "gravity",
        "class": "GravitySortSimulation",
        "category": "simple",
        "name": "Gravity Sort",
        "time": "O(n·max)",
        "space": "O(n·max)",
        "stable": True,
        "invariant": "Each column's bead count equals the number of elements whose value is >= that column's row index after each gravity pass.",
        "desc": "Simulates falling beads.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        if not ascending:
            arr.reverse()
        max_val = max(arr)
        if max_val == 0:
            yield done_frame(arr, self.name)
            return
        beads = [[0]*max_val for _ in range(n)]
        for i in range(n):
            for j in range(arr[i]):
                beads[i][j] = 1
        for j in range(max_val):
            yield base_frame(arr, highlighted=[j], explanation=f"Gravity pass for column {j}", aux_array=[sum(row) for row in beads])
            sum_col = sum(beads[i][j] for i in range(n))
            for i in range(n):
                beads[i][j] = 1 if i >= n - sum_col else 0
            for i in range(n):
                arr[i] = sum(beads[i])
            yield base_frame(arr, operation="write", explanation="Beads settled")
        if not ascending:
            arr.reverse()
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "circle",
        "class": "CircleSort",
        "category": "simple",
        "name": "Circle Sort",
        "time": "O(n log n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Mirrored index pairs (lo, hi) are compared and swapped if out of order; the circle recursively halves until pairs meet.",
        "desc": "Compare mirrored pairs recursively.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        def _inner(lo: int, hi: int, depth: int) -> Generator[SortFrame, None, bool]:
            if lo == hi: return False
            swapped = False
            high = hi
            low = lo
            mid = (hi - lo) // 2
            while lo < hi:
                yield base_frame(arr, highlighted=[lo, hi], recursion_depth=depth, explanation="Comparing mirror pair")
                if out_of_order(arr[lo], arr[hi], ascending):
                    arr[lo], arr[hi] = arr[hi], arr[lo]
                    swapped = True
                    yield base_frame(arr, swapped=[lo, hi], recursion_depth=depth, operation="swap")
                lo += 1
                hi -= 1
            if lo == hi:
                yield base_frame(arr, highlighted=[lo, high], recursion_depth=depth)
                if out_of_order(arr[lo], arr[high], ascending):
                    arr[lo], arr[high] = arr[high], arr[lo]
                    swapped = True
                    yield base_frame(arr, swapped=[lo, high], recursion_depth=depth, operation="swap")
            left_swapped = yield from _inner(low, low + mid, depth+1)
            right_swapped = yield from _inner(low + mid + 1, high, depth+1)
            return swapped or left_swapped or right_swapped
        
        while True:
            did_swap = yield from _inner(0, n-1, 0)
            if not did_swap:
                break
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "swap_sort",
        "class": "SwapSort",
        "category": "simple",
        "name": "Swap Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": False,
        "invariant": "For each index i, element arr[i] is placed into its correct final position by counting elements smaller than it.",
        "desc": "Counts smaller elements to find the exact sorted position.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        for i in range(n - 1):
            while True:
                count = 0
                for j in range(n):
                    if j == i: continue
                    yield base_frame(arr, highlighted=[i, j], explanation=f"Counting elements smaller than arr[{i}]")
                    if (arr[j] < arr[i]) if ascending else (arr[j] > arr[i]):
                        count += 1
                    elif arr[j] == arr[i] and j < i:
                        count += 1
                if count == i:
                    break
                target = count
                yield base_frame(arr, highlighted=[i, target], explanation=f"Swapping to target position {target}")
                arr[i], arr[target] = arr[target], arr[i]
                yield base_frame(arr, swapped=[i, target], operation="swap")
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "max_sort",
        "class": "MaxSort",
        "category": "simple",
        "name": "Max Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": False,
        "invariant": "The suffix arr[boundary..n-1] contains the boundary largest elements in their final sorted positions.",
        "desc": "Selection sort variant finding the maximum.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        sorted_idx = []
        for i in range(n - 1, 0, -1):
            max_idx = i
            for j in range(i - 1, -1, -1):
                yield base_frame(arr, highlighted=[max_idx, j], sorted_indices=sorted_idx)
                if out_of_order(arr[j], arr[max_idx], ascending):
                    max_idx = j
            if max_idx != i:
                arr[i], arr[max_idx] = arr[max_idx], arr[i]
                yield base_frame(arr, swapped=[i, max_idx], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.append(i)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "bidirectional_selection",
        "class": "BidirectionalSelectionSort",
        "category": "simple",
        "name": "Bidirectional Selection Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": False,
        "invariant": "Each pass simultaneously finds both the minimum and maximum of the unsorted region, placing both into final positions.",
        "desc": "Finds min and max simultaneously.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        left, right = 0, n - 1
        sorted_idx = []
        while left < right:
            min_idx, max_idx = left, left
            for i in range(left + 1, right + 1):
                yield base_frame(arr, highlighted=[i, min_idx, max_idx], sorted_indices=sorted_idx)
                if out_of_order(arr[min_idx], arr[i], ascending):
                    min_idx = i
                elif out_of_order(arr[i], arr[max_idx], ascending):
                    max_idx = i
            if min_idx != left:
                arr[left], arr[min_idx] = arr[min_idx], arr[left]
                yield base_frame(arr, swapped=[left, min_idx], sorted_indices=sorted_idx, operation="swap")
                if max_idx == left:
                    max_idx = min_idx
            if max_idx != right:
                arr[right], arr[max_idx] = arr[max_idx], arr[right]
                yield base_frame(arr, swapped=[right, max_idx], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.extend([left, right])
            left += 1
            right -= 1
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "spaghetti_real",
        "class": "SpaghettiSort",
        "category": "simple",
        "name": "Spaghetti Sort (Simulation)",
        "time": "O(n²)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Rods of length proportional to each value are held vertically; the tallest rod found in each pass goes next.",
        "desc": "Simulates finding the tallest rod in a bundle.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        bundle = [(val, idx) for idx, val in enumerate(arr)]
        output = []
        target_idx = n - 1 if ascending else 0
        step = -1 if ascending else 1
        while bundle:
            max_idx = 0
            for i in range(1, len(bundle)):
                yield base_frame(arr, highlighted=[bundle[max_idx][1], bundle[i][1]], aux_array=[b[0] for b in bundle], explanation="Scanning bundle for longest rod")
                if bundle[i][0] > bundle[max_idx][0]:
                    max_idx = i
            val, orig_idx = bundle.pop(max_idx)
            yield base_frame(arr, highlighted=[orig_idx], operation="read", aux_array=[b[0] for b in bundle], explanation="Extracting tallest rod")
            arr[target_idx] = val
            yield base_frame(arr, swapped=[target_idx], operation="write", aux_array=[b[0] for b in bundle], explanation="Writing to output")
            target_idx += step
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "shell_ciura",
        "class": "ShellCiuraSort",
        "category": "efficient",
        "name": "Shellsort (Ciura Gaps)",
        "time": "O(n^(4/3))",
        "space": "O(1)",
        "stable": False,
        "invariant": "The array is h-sorted for all gap values used so far in Ciura's sequence [701,301,132,57,23,10,4,1].",
        "desc": "Shellsort using the optimal Ciura gap sequence.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        gaps = [701, 301, 132, 57, 23, 10, 4, 1]
        for gap in gaps:
            if gap >= n and gap != 1: continue
            for i in range(gap, n):
                temp = arr[i]
                j = i
                while j >= gap:
                    yield base_frame(arr, highlighted=[j, j-gap], metadata={"gap": gap}, explanation="Ciura gap compare")
                    if out_of_order(arr[j-gap], temp, ascending):
                        arr[j] = arr[j-gap]
                        yield base_frame(arr, swapped=[j, j-gap], metadata={"gap": gap}, operation="swap")
                        j -= gap
                    else:
                        break
                arr[j] = temp
                if j != i:
                    yield base_frame(arr, swapped=[j], metadata={"gap": gap}, operation="write")
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "shell_knuth",
        "class": "ShellKnuthSort",
        "category": "efficient",
        "name": "Shellsort (Knuth Gaps)",
        "time": "O(n^(3/2))",
        "space": "O(1)",
        "stable": False,
        "invariant": "The array is h-sorted for all gaps in the Knuth sequence 1,4,13,40,121,... (3k+1) used so far.",
        "desc": "Shellsort using the Knuth gap sequence.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        h = 1
        while h < n // 3:
            h = 3 * h + 1
        while h > 0:
            for i in range(h, n):
                temp = arr[i]
                j = i
                while j >= h:
                    yield base_frame(arr, highlighted=[j, j-h], metadata={"gap": h, "formula": "3k+1"})
                    if out_of_order(arr[j-h], temp, ascending):
                        arr[j] = arr[j-h]
                        yield base_frame(arr, swapped=[j, j-h], metadata={"gap": h, "formula": "3k+1"}, operation="swap")
                        j -= h
                    else:
                        break
                arr[j] = temp
                if j != i:
                    yield base_frame(arr, swapped=[j], metadata={"gap": h, "formula": "3k+1"}, operation="write")
            h //= 3
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "tree_insertion",
        "class": "TreeInsertionSort",
        "category": "efficient",
        "name": "Tree Insertion Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "The BST contains all elements seen so far; its inorder traversal yields them in sorted order at every step.",
        "desc": "Builds a BST and traverses it.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        
        class Node:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                
        root = None
        for i in range(n):
            val = arr[i]
            if root is None:
                root = Node(val)
                yield base_frame(arr, highlighted=[i], metadata={"phase": "insert", "tree_size": i+1}, explanation="Insert root")
            else:
                curr = root
                while True:
                    yield base_frame(arr, highlighted=[i], metadata={"phase": "insert", "tree_size": i+1}, operation="compare")
                    if (val < curr.val) if ascending else (val > curr.val):
                        if curr.left is None:
                            curr.left = Node(val)
                            break
                        curr = curr.left
                    elif val == curr.val:
                        curr.count += 1
                        break
                    else:
                        if curr.right is None:
                            curr.right = Node(val)
                            break
                        curr = curr.right
        
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield base_frame(arr, highlighted=[idx], metadata={"phase": "extract", "tree_size": n}, operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "list_insertion",
        "class": "LinkedListInsertionSort",
        "category": "simple",
        "name": "Linked List Insertion Sort",
        "time": "O(n²)",
        "space": "O(n)",
        "stable": True,
        "invariant": "The virtual linked list contains all processed elements in sorted order; each new element is spliced into its correct position.",
        "desc": "Simulates a linked list insertion sort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        sorted_list = []
        for i in range(n):
            val = arr[i]
            insert_pos = len(sorted_list)
            for j in range(len(sorted_list)):
                yield base_frame(arr, highlighted=[i], aux_array=sorted_list, operation="compare")
                if (val < sorted_list[j]) if ascending else (val > sorted_list[j]):
                    insert_pos = j
                    break
            sorted_list.insert(insert_pos, val)
            yield base_frame(arr, highlighted=[i], aux_array=sorted_list, operation="write")
        for i in range(n):
            arr[i] = sorted_list[i]
            yield base_frame(arr, swapped=[i], aux_array=sorted_list, operation="write")
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "patience_optimized",
        "class": "OptimizedPatienceSort",
        "category": "adaptive",
        "name": "Patience Sort (Optimized)",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Each pile's top is the smallest in that pile; binary search finds the leftmost pile whose top >= current card.",
        "desc": "Patience sort using binary search for pile placement.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        piles = []
        for i in range(n):
            val = arr[i]
            left, right = 0, len(piles)
            while left < right:
                mid = (left + right) // 2
                yield base_frame(arr, highlighted=[i], metadata={"pile_count": len(piles), "search": "binary", "mid": mid})
                if (piles[mid][-1] > val) if ascending else (piles[mid][-1] < val):
                    right = mid
                else:
                    left = mid + 1
            if left == len(piles):
                piles.append([val])
            else:
                piles[left].append(val)
        
        # Merge piles
        import heapq
        heap = []
        for i, p in enumerate(piles):
            heapq.heappush(heap, (p[-1] if ascending else -p[-1], i))
        
        for i in range(n):
            _, p_idx = heapq.heappop(heap)
            val = piles[p_idx].pop()
            if piles[p_idx]:
                heapq.heappush(heap, (piles[p_idx][-1] if ascending else -piles[p_idx][-1], p_idx))
            arr[i] = val
            yield base_frame(arr, swapped=[i], operation="write")
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "spliced_insertion",
        "class": "SplicedInsertionSort",
        "category": "simple",
        "name": "Spliced Insertion Sort",
        "time": "O(n²)",
        "space": "O(1)",
        "stable": True,
        "invariant": "arr[0..i] are sorted; element at i was spliced out of position j and spliced back in at its correct sorted position.",
        "desc": "Explicit splice-out and splice-in insertion sort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        for i in range(1, n):
            yield base_frame(arr, highlighted=[i], explanation="Splice-out selected")
            val = arr[i]
            yield base_frame(arr, highlighted=[i], operation="read", explanation="Element removed")
            j = i
            while j > 0:
                yield base_frame(arr, highlighted=[j-1, j], explanation="Compare")
                if out_of_order(arr[j-1], val, ascending):
                    arr[j] = arr[j-1]
                    yield base_frame(arr, swapped=[j, j-1], operation="write")
                    j -= 1
                else:
                    break
            arr[j] = val
            yield base_frame(arr, swapped=[j], operation="write", explanation="Element spliced in")
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "diagonal_sort",
        "class": "DiagonalSort",
        "category": "efficient",
        "name": "Diagonal Sort",
        "time": "O(n log n)",
        "space": "O(1)",
        "stable": False,
        "invariant": "All elements in each completed diagonal strip are sorted relative to their diagonal neighbors.",
        "desc": "Sorts elements conceptually arranged in a matrix by diagonals.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        w = int(math.ceil(math.sqrt(n)))
        diagonals = {}
        for i in range(n):
            d = (i % w) - (i // w)
            diagonals.setdefault(d, []).append(i)
            
        for d, indices in diagonals.items():
            for i in range(1, len(indices)):
                val = arr[indices[i]]
                j = i
                while j > 0:
                    yield base_frame(arr, highlighted=indices, metadata={"diagonal": d, "width": w})
                    if out_of_order(arr[indices[j-1]], val, ascending):
                        arr[indices[j]] = arr[indices[j-1]]
                        yield base_frame(arr, swapped=[indices[j], indices[j-1]], metadata={"diagonal": d, "width": w}, operation="swap")
                        j -= 1
                    else:
                        break
                arr[indices[j]] = val
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "randomized_quicksort",
        "class": "RandomizedQuicksort",
        "category": "hybrid",
        "name": "Randomized Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Pivot is chosen uniformly at random; all elements left of pivot are <= pivot, all right are >= pivot after partition.",
        "desc": "Quicksort with random pivot selection.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import random
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            rand_idx = random.randint(lo, hi)
            yield base_frame(arr, highlighted=[rand_idx], partition_bounds=(lo, hi), explanation="Selecting random pivot")
            arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]
            pivot = arr[hi]
            
            i = lo
            for j in range(lo, hi):
                yield base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth, metadata={"pivot_value": pivot, "selection": "random"})
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    if i != j:
                        yield base_frame(arr, swapped=[i, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield base_frame(arr, swapped=[i, hi], pivot_index=i, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            yield from _quick(lo, i - 1, depth + 1)
            yield from _quick(i + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "median_of_3_quicksort",
        "class": "MedianOf3Quicksort",
        "category": "hybrid",
        "name": "Median-of-3 Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Pivot is the median of first, middle, and last elements; all elements left are <= pivot, all right are >= pivot.",
        "desc": "Quicksort with median-of-3 pivot.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            mid = (lo + hi) // 2
            yield base_frame(arr, highlighted=[lo, mid, hi], partition_bounds=(lo, hi), explanation="Comparing 3 candidates", metadata={"candidates": [arr[lo], arr[mid], arr[hi]]})
            cands = [(arr[lo], lo), (arr[mid], mid), (arr[hi], hi)]
            cands.sort(key=lambda x: value_of(x[0]), reverse=not ascending)
            med_idx = cands[1][1]
            yield base_frame(arr, highlighted=[med_idx], partition_bounds=(lo, hi), explanation="Median selected as pivot")
            
            arr[med_idx], arr[hi] = arr[hi], arr[med_idx]
            pivot = arr[hi]
            
            i = lo
            for j in range(lo, hi):
                yield base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth)
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    if i != j:
                        yield base_frame(arr, swapped=[i, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield base_frame(arr, swapped=[i, hi], pivot_index=i, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            yield from _quick(lo, i - 1, depth + 1)
            yield from _quick(i + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "median_of_5_quicksort",
        "class": "MedianOf5Quicksort",
        "category": "hybrid",
        "name": "Median-of-5 Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Pivot is the median of 5 evenly-spaced elements; provides better pivot quality at cost of 6 comparisons per call.",
        "desc": "Quicksort with median-of-5 pivot.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            if hi - lo < 4:
                # Fallback to simple selection for small subarrays
                for i in range(lo, hi):
                    min_idx = i
                    for j in range(i+1, hi+1):
                        yield base_frame(arr, highlighted=[min_idx, j], partition_bounds=(lo, hi))
                        if (arr[j] < arr[min_idx]) if ascending else (arr[j] > arr[min_idx]):
                            min_idx = j
                    if min_idx != i:
                        arr[i], arr[min_idx] = arr[min_idx], arr[i]
                        yield base_frame(arr, swapped=[i, min_idx], partition_bounds=(lo, hi), operation="swap")
                return
                
            step = (hi - lo) // 4
            c_idx = [lo, lo+step, lo+2*step, lo+3*step, hi]
            yield base_frame(arr, highlighted=c_idx, partition_bounds=(lo, hi), explanation="5 candidates selected", metadata={"candidates": 5, "pivot_quality": "high"})
            
            cands = [(arr[i], i) for i in c_idx]
            # Selection sort the 5 candidates
            for i in range(5):
                for j in range(i+1, 5):
                    yield base_frame(arr, highlighted=[cands[i][1], cands[j][1]], partition_bounds=(lo, hi))
                    if (cands[j][0] < cands[i][0]) if ascending else (cands[j][0] > cands[i][0]):
                        cands[i], cands[j] = cands[j], cands[i]
            
            med_idx = cands[2][1]
            yield base_frame(arr, highlighted=[med_idx], partition_bounds=(lo, hi), explanation="Median of 5 selected", metadata={"candidates": 5, "pivot_quality": "high"})
            
            arr[med_idx], arr[hi] = arr[hi], arr[med_idx]
            pivot = arr[hi]
            
            i_ptr = lo
            for j in range(lo, hi):
                yield base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth)
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i_ptr], arr[j] = arr[j], arr[i_ptr]
                    if i_ptr != j:
                        yield base_frame(arr, swapped=[i_ptr, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i_ptr += 1
            arr[i_ptr], arr[hi] = arr[hi], arr[i_ptr]
            yield base_frame(arr, swapped=[i_ptr, hi], pivot_index=i_ptr, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            yield from _quick(lo, i_ptr - 1, depth + 1)
            yield from _quick(i_ptr + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "fat_partition_quicksort",
        "class": "FatPartitionQuicksort",
        "category": "hybrid",
        "name": "Fat Partition Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Three regions: arr[lo..p1-1] < pivot, arr[p1..p2] == pivot, arr[p2+1..hi] > pivot after each partition.",
        "desc": "Dutch national flag partition quicksort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[hi]
            i, j, k = lo, lo, hi
            while j <= k:
                yield base_frame(arr, highlighted=[j], partition_bounds=(i, k), recursion_depth=depth, metadata={"equal_count": k-i+1, "regions": 3})
                if (arr[j] < pivot) if ascending else (arr[j] > pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(arr, swapped=[i, j], partition_bounds=(i, k), operation="swap", recursion_depth=depth)
                    i += 1
                    j += 1
                elif (arr[j] > pivot) if ascending else (arr[j] < pivot):
                    arr[j], arr[k] = arr[k], arr[j]
                    yield base_frame(arr, swapped=[j, k], partition_bounds=(i, k), operation="swap", recursion_depth=depth)
                    k -= 1
                else:
                    j += 1
                    
            yield from _quick(lo, i - 1, depth + 1)
            yield from _quick(k + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "three_way_quicksort",
        "class": "ThreeWayQuicksort",
        "category": "hybrid",
        "name": "Three-Way Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Bentley-McIlroy: lt and gt pointers partition into <pivot, ==pivot, >pivot; equal elements are never moved again.",
        "desc": "Bentley-McIlroy 3-way quicksort.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[lo]
            lt, i, gt = lo, lo + 1, hi
            while i <= gt:
                yield base_frame(arr, highlighted=[i], partition_bounds=(lt, gt), recursion_depth=depth, metadata={"lt": lt, "gt": gt, "i": i})
                if (arr[i] < pivot) if ascending else (arr[i] > pivot):
                    arr[lt], arr[i] = arr[i], arr[lt]
                    yield base_frame(arr, swapped=[lt, i], partition_bounds=(lt, gt), operation="swap", recursion_depth=depth)
                    lt += 1
                    i += 1
                elif (arr[i] > pivot) if ascending else (arr[i] < pivot):
                    arr[i], arr[gt] = arr[gt], arr[i]
                    yield base_frame(arr, swapped=[i, gt], partition_bounds=(lt, gt), operation="swap", recursion_depth=depth)
                    gt -= 1
                else:
                    i += 1
                    
            yield from _quick(lo, lt - 1, depth + 1)
            yield from _quick(gt + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "hoare_quicksort",
        "class": "HoareQuicksort",
        "category": "hybrid",
        "name": "Hoare Partition Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Two pointers i and j move inward from opposite ends; all elements left of i are <= pivot, right of j are >= pivot.",
        "desc": "Quicksort with Hoare partition scheme.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[lo + (hi - lo) // 2]
            i, j = lo - 1, hi + 1
            while True:
                i += 1
                while (arr[i] < pivot) if ascending else (arr[i] > pivot):
                    yield base_frame(arr, highlighted=[i, j], recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                    i += 1
                j -= 1
                while (arr[j] > pivot) if ascending else (arr[j] < pivot):
                    yield base_frame(arr, highlighted=[i, j], recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                    j -= 1
                    
                if i >= j:
                    p_idx = j
                    break
                arr[i], arr[j] = arr[j], arr[i]
                yield base_frame(arr, swapped=[i, j], operation="swap", recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                
            yield from _quick(lo, p_idx, depth + 1)
            yield from _quick(p_idx + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "ninther_quicksort",
        "class": "NintherQuicksort",
        "category": "hybrid",
        "name": "Ninther Quicksort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "Pivot is Tukey's ninther: median of three medians of three triples — 9 elements examined, extremely robust pivot.",
        "desc": "Quicksort using Tukey's ninther pivot selection.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _median3(i, j, k):
            a, b, c = arr[i], arr[j], arr[k]
            yield base_frame(arr, highlighted=[i, j, k], explanation="Median of triple")
            if (a < b) if ascending else (a > b):
                if (b < c) if ascending else (b > c): return j
                elif (a < c) if ascending else (a > c): return k
                else: return i
            else:
                if (a < c) if ascending else (a > c): return i
                elif (b < c) if ascending else (b > c): return k
                else: return j
                
        def _quick(lo, hi, depth):
            if lo >= hi: return
            if hi - lo < 8:
                # insertion fallback
                for i in range(lo+1, hi+1):
                    val = arr[i]
                    j = i
                    while j > lo:
                        yield base_frame(arr, highlighted=[j, j-1])
                        if out_of_order(arr[j-1], val, ascending):
                            arr[j] = arr[j-1]
                            yield base_frame(arr, swapped=[j, j-1], operation="swap")
                            j -= 1
                        else: break
                    arr[j] = val
                return
                
            step = (hi - lo) // 8
            yield base_frame(arr, highlighted=[lo, lo+step, lo+2*step, lo+3*step, lo+4*step, lo+5*step, lo+6*step, lo+7*step, hi], metadata={"candidates": 9, "method": "tukey_ninther"})
            
            m1 = yield from _median3(lo, lo+step, lo+2*step)
            m2 = yield from _median3(lo+3*step, lo+4*step, lo+5*step)
            m3 = yield from _median3(lo+6*step, lo+7*step, hi)
            med_idx = yield from _median3(m1, m2, m3)
            
            yield base_frame(arr, highlighted=[med_idx], explanation="Median of medians selected")
            arr[med_idx], arr[hi] = arr[hi], arr[med_idx]
            pivot = arr[hi]
            
            i_ptr = lo
            for j in range(lo, hi):
                yield base_frame(arr, highlighted=[j, hi], pivot_index=hi)
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i_ptr], arr[j] = arr[j], arr[i_ptr]
                    if i_ptr != j:
                        yield base_frame(arr, swapped=[i_ptr, j], pivot_index=hi, operation="swap")
                    i_ptr += 1
            arr[i_ptr], arr[hi] = arr[hi], arr[i_ptr]
            yield base_frame(arr, swapped=[i_ptr, hi], pivot_index=i_ptr, operation="swap")
            
            yield from _quick(lo, i_ptr - 1, depth + 1)
            yield from _quick(i_ptr + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "iterative_quicksort",
        "class": "IterativeQuicksort",
        "category": "hybrid",
        "name": "Iterative Quicksort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "An explicit stack holds (lo, hi) subarray bounds; the stack depth never exceeds log2(n) with tail-call optimization.",
        "desc": "Iterative quicksort using an explicit stack.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        stack = [(0, n - 1)]
        while stack:
            lo, hi = stack.pop()
            depth = len(stack)
            if lo >= hi: continue
            
            pivot = arr[hi]
            i = lo
            for j in range(lo, hi):
                yield base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth, metadata={"stack_depth": depth, "stack": stack})
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    if i != j:
                        yield base_frame(arr, swapped=[i, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield base_frame(arr, swapped=[i, hi], pivot_index=i, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            if i - 1 - lo > hi - i - 1:
                stack.append((lo, i - 1))
                stack.append((i + 1, hi))
            else:
                stack.append((i + 1, hi))
                stack.append((lo, i - 1))
                
        yield done_frame(arr, self.name)
"""
    }
]

import collections

base_imports = """from __future__ import annotations
import math
from typing import Generator, List, Any
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms._helpers import base_frame, done_frame
from sortui.algorithms._helpers import out_of_order, value_of, is_sorted, in_order

"""

for algo in ALGO_DEFINITIONS:
    content = base_imports + f"""
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
    
    file_path = f"sortui/algorithms/{algo['category']}/{algo['key']}.py"
    with open(file_path, "w") as f:
        f.write(content)

# Update __init__.py files
for cat in ['simple', 'efficient', 'adaptive', 'hybrid']:
    init_file = f"sortui/algorithms/{cat}/__init__.py"
    if os.path.exists(init_file):
        with open(init_file, "r") as f:
            content = f.read()
        
        # Add new imports and to _ITEMS
        my_algos = [a for a in ALGO_DEFINITIONS if a['category'] == cat]
        
        imports_to_add = "\n".join(f"from .{a['key']} import {a['class']}" for a in my_algos)
        items_to_add = "\n".join(f"    (\"{a['key']}\", {a['class']})," for a in my_algos)
        
        # very hacky text replacement:
        # inject imports at top after other imports
        lines = content.split('\n')
        idx = 0
        for i, line in enumerate(lines):
            if "from sortui.algorithms.common import" in line or "from sortui.algorithms.base import" in line:
                idx = i + 1
        lines.insert(idx, imports_to_add)
        
        content = "\n".join(lines)
        
        # inject into _ITEMS
        content = content.replace("_ITEMS = [", "_ITEMS = [\n" + items_to_add)
        
        with open(init_file, "w") as f:
            f.write(content)
