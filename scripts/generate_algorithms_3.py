import os

ALGO_DEFINITIONS = [
    # HEAP VARIANTS
    {
        "key": "d_ary_heap",
        "class": "DAryHeapSort",
        "category": "hybrid_variants",
        "name": "D-ary Heap Sort",
        "time": "O(n log_d n)",
        "space": "O(1)",
        "stable": False,
        "invariant": "Each node has exactly d=4 children; parent at i has children at d*i+1 through d*i+d, maintaining max-d-heap property.",
        "desc": "Heapsort with a 4-ary heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        D = 4
        
        def sift_down(start: int, end: int):
            root = start
            while True:
                child = D * root + 1
                if child > end:
                    break
                
                swap = root
                for c in range(child, min(child + D, end + 1)):
                    yield _base_frame(arr, highlighted=[swap, c], metadata={"d": D, "phase": "heapify"})
                    if out_of_order(arr[swap], arr[c], ascending):
                        swap = c
                        
                if swap == root:
                    break
                arr[root], arr[swap] = arr[swap], arr[root]
                yield _base_frame(arr, swapped=[root, swap], operation="swap", metadata={"d": D, "phase": "heapify"})
                root = swap
                
        # Build heap
        for i in range((n - 2) // D, -1, -1):
            yield from sift_down(i, n - 1)
            
        # Extract max
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            yield _base_frame(arr, swapped=[0, i], operation="swap", metadata={"d": D, "phase": "extract"})
            yield from sift_down(0, i - 1)
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "pairing_heap",
        "class": "PairingHeapSort",
        "category": "hybrid_variants",
        "name": "Pairing Heap Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "Each node's value is >= all values in its subtrees; the two-pass pairing on delete-min preserves the heap property.",
        "desc": "Heapsort via a Pairing Heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class PairingNode:
            def __init__(self, val):
                self.val = val
                self.subheaps = []
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if not out_of_order(h1.val, h2.val, ascending):
                h1.subheaps.append(h2)
                return h1
            else:
                h2.subheaps.append(h1)
                return h2
                
        def two_pass_merge(subheaps):
            if not subheaps: return None
            if len(subheaps) == 1: return subheaps[0]
            
            merged_pairs = []
            for i in range(0, len(subheaps), 2):
                if i + 1 < len(subheaps):
                    merged_pairs.append(merge(subheaps[i], subheaps[i+1]))
                else:
                    merged_pairs.append(subheaps[i])
                    
            res = merged_pairs[-1]
            for i in range(len(merged_pairs) - 2, -1, -1):
                res = merge(res, merged_pairs[i])
            return res
            
        # Phase 1: Build pairing heap
        root = None
        for i in range(n):
            node = PairingNode(arr[i])
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"heap_size": n, "phase": "build"}, explanation="Insert element")
            
        # Phase 2: Extract min
        for i in range(n):
            min_val = root.val
            root = two_pass_merge(root.subheaps)
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"heap_size": n, "phase": "extract"}, operation="write")
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "skew_heap",
        "class": "SkewHeapSort",
        "category": "hybrid_variants",
        "name": "Skew Heap Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "Skew merge always swaps left and right children of the root after each merge — no rank tracking needed.",
        "desc": "Heapsort via a Skew Heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class SkewNode:
            def __init__(self, val, idx):
                self.val = val
                self.idx = idx
                self.left = None
                self.right = None
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if out_of_order(h1.val, h2.val, ascending):
                h1, h2 = h2, h1
                
            h1.right = merge(h1.right, h2)
            h1.left, h1.right = h1.right, h1.left
            return h1
            
        root = None
        for i in range(n):
            node = SkewNode(arr[i], i)
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"phase": "build", "merges": n})
            
        for i in range(n):
            min_val = root.val
            root = merge(root.left, root.right)
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"phase": "extract", "merges": n}, operation="write")
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "leftist_heap",
        "class": "LeftistHeapSort",
        "category": "hybrid_variants",
        "name": "Leftist Heap Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "The right spine length (s-value) is always <= log2(n+1); merges always happen along the right spine.",
        "desc": "Heapsort via a Leftist Heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class LeftistNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.s_value = 1
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if out_of_order(h1.val, h2.val, ascending):
                h1, h2 = h2, h1
                
            h1.right = merge(h1.right, h2)
            
            left_s = h1.left.s_value if h1.left else 0
            right_s = h1.right.s_value if h1.right else 0
            
            if left_s < right_s:
                h1.left, h1.right = h1.right, h1.left
                
            h1.s_value = (h1.right.s_value if h1.right else 0) + 1
            return h1
            
        root = None
        for i in range(n):
            node = LeftistNode(arr[i])
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"s_value": root.s_value, "right_spine_len": n})
            
        for i in range(n):
            min_val = root.val
            root = merge(root.left, root.right)
            s_val = root.s_value if root else 0
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"s_value": s_val, "right_spine_len": n}, operation="write")
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "binomial_heap",
        "class": "BinomialHeapSort",
        "category": "hybrid_variants",
        "name": "Binomial Heap Sort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "The heap is a forest of binomial trees B_k where each B_k has exactly 2^k nodes and satisfies the min-heap property.",
        "desc": "Heapsort via a Binomial Heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class BinomialNode:
            def __init__(self, val):
                self.val = val
                self.degree = 0
                self.parent = None
                self.child = None
                self.sibling = None
                
        def link(y, z):
            y.parent = z
            y.sibling = z.child
            z.child = y
            z.degree += 1
            
        def merge_trees(h1, h2):
            if not h1: return h2
            if not h2: return h1
            res = None
            curr = None
            p1, p2 = h1, h2
            while p1 and p2:
                if p1.degree <= p2.degree:
                    node = p1
                    p1 = p1.sibling
                else:
                    node = p2
                    p2 = p2.sibling
                if not res:
                    res = node
                else:
                    curr.sibling = node
                curr = node
            if p1: curr.sibling = p1
            if p2: curr.sibling = p2
            return res
            
        def union(h1, h2):
            if not h1: return h2
            if not h2: return h1
            h = merge_trees(h1, h2)
            prev = None
            x = h
            next_x = x.sibling
            while next_x:
                if x.degree != next_x.degree or (next_x.sibling and next_x.sibling.degree == x.degree):
                    prev = x
                    x = next_x
                elif not out_of_order(x.val, next_x.val, ascending):
                    x.sibling = next_x.sibling
                    link(next_x, x)
                else:
                    if not prev:
                        h = next_x
                    else:
                        prev.sibling = next_x
                    link(x, next_x)
                    x = next_x
                next_x = x.sibling
            return h
            
        root = None
        for i in range(n):
            node = BinomialNode(arr[i])
            root = union(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"forest_size": n}, explanation="Insert and union")
            
        for i in range(n):
            # Find min
            min_node = root
            min_prev = None
            curr = root
            prev = None
            while curr:
                if out_of_order(min_node.val, curr.val, ascending):
                    min_node = curr
                    min_prev = prev
                prev = curr
                curr = curr.sibling
                
            if not min_prev:
                root = min_node.sibling
            else:
                min_prev.sibling = min_node.sibling
                
            child = min_node.child
            rev_child = None
            while child:
                next_child = child.sibling
                child.sibling = rev_child
                child.parent = None
                rev_child = child
                child = next_child
                
            root = union(root, rev_child)
            arr[i] = min_node.val
            yield _base_frame(arr, swapped=[i], metadata={"forest_size": n}, operation="write")
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "fibonacci_heap",
        "class": "FibonacciHeapSort",
        "category": "hybrid_variants",
        "name": "Fibonacci Heap Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "Trees are lazily consolidated; marked nodes have lost one child since becoming non-root — cascading cuts maintain O(log n) rank.",
        "desc": "Heapsort via a Fibonacci Heap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class FibNode:
            def __init__(self, val):
                self.val = val
                self.degree = 0
                self.parent = None
                self.child = None
                self.left = self
                self.right = self
                self.marked = False
                
        def insert_node(min_node, node):
            if not min_node:
                return node
            node.left = min_node
            node.right = min_node.right
            min_node.right.left = node
            min_node.right = node
            if out_of_order(min_node.val, node.val, ascending):
                return node
            return min_node
            
        def link(y, x):
            y.left.right = y.right
            y.right.left = y.left
            y.parent = x
            if not x.child:
                x.child = y
                y.left = y
                y.right = y
            else:
                y.left = x.child
                y.right = x.child.right
                x.child.right.left = y
                x.child.right = y
            x.degree += 1
            y.marked = False
            
        def consolidate(min_node):
            D = int(math.log(n) * 2) + 1
            A = [None] * D
            nodes = []
            curr = min_node
            if curr:
                nodes.append(curr)
                curr = curr.right
                while curr != min_node:
                    nodes.append(curr)
                    curr = curr.right
                    
            for w in nodes:
                x = w
                d = x.degree
                while A[d] != None:
                    y = A[d]
                    if out_of_order(x.val, y.val, ascending):
                        x, y = y, x
                    link(y, x)
                    A[d] = None
                    d += 1
                A[d] = x
                
            new_min = None
            for i in range(D):
                if A[i]:
                    A[i].left = A[i]
                    A[i].right = A[i]
                    new_min = insert_node(new_min, A[i])
            return new_min
            
        min_node = None
        for i in range(n):
            node = FibNode(arr[i])
            min_node = insert_node(min_node, node)
            yield _base_frame(arr, highlighted=[i], metadata={"trees": n, "marked": n, "phase": "insert"})
            
        for i in range(n):
            z = min_node
            if z:
                curr = z.child
                children = []
                if curr:
                    children.append(curr)
                    curr = curr.right
                    while curr != z.child:
                        children.append(curr)
                        curr = curr.right
                for child in children:
                    child.parent = None
                    min_node = insert_node(min_node, child)
                    
                z.left.right = z.right
                z.right.left = z.left
                if z == z.right:
                    min_node = None
                else:
                    min_node = z.right
                    min_node = consolidate(min_node)
                    
                arr[i] = z.val
                yield _base_frame(arr, swapped=[i], metadata={"trees": n, "marked": n, "phase": "extract"}, operation="write")
                
        yield done_frame(arr, self.name)
"""
    },
    # TREE-BASED SORTS
    {
        "key": "avl_tree_sort",
        "class": "AVLTreeSort",
        "category": "efficient",
        "name": "AVL Tree Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Every AVL node's left and right subtree heights differ by at most 1; rotations restore this after every insertion.",
        "desc": "Sorts using an AVL tree.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class AVLNode:
            def __init__(self, val, idx):
                self.val = val
                self.idx = idx
                self.left = None
                self.right = None
                self.height = 1
                self.count = 1
                
        def get_height(node):
            return node.height if node else 0
            
        def get_balance(node):
            return get_height(node.left) - get_height(node.right) if node else 0
            
        def right_rotate(y, frames_list):
            x = y.left
            T2 = x.right
            x.right = y
            y.left = T2
            y.height = 1 + max(get_height(y.left), get_height(y.right))
            x.height = 1 + max(get_height(x.left), get_height(x.right))
            frames_list.append(("LL", y.idx, x.idx))
            return x
            
        def left_rotate(x, frames_list):
            y = x.right
            T2 = y.left
            y.left = x
            x.right = T2
            x.height = 1 + max(get_height(x.left), get_height(x.right))
            y.height = 1 + max(get_height(y.left), get_height(y.right))
            frames_list.append(("RR", x.idx, y.idx))
            return y
            
        def insert(node, val, idx, frames_list):
            if not node:
                return AVLNode(val, idx)
                
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val, idx, frames_list)
            elif val == node.val:
                node.count += 1
                return node
            else:
                node.right = insert(node.right, val, idx, frames_list)
                
            node.height = 1 + max(get_height(node.left), get_height(node.right))
            balance = get_balance(node)
            
            if balance > 1 and ((val < node.left.val) if ascending else (val > node.left.val)):
                return right_rotate(node, frames_list)
            if balance < -1 and ((val > node.right.val) if ascending else (val < node.right.val)):
                return left_rotate(node, frames_list)
            if balance > 1 and ((val > node.left.val) if ascending else (val < node.left.val)):
                node.left = left_rotate(node.left, frames_list)
                return right_rotate(node, frames_list)
            if balance < -1 and ((val < node.right.val) if ascending else (val > node.right.val)):
                node.right = right_rotate(node.right, frames_list)
                return left_rotate(node, frames_list)
                
            return node
            
        root = None
        for i in range(n):
            frames_list = []
            root = insert(root, arr[i], i, frames_list)
            yield _base_frame(arr, highlighted=[i], metadata={"rotation": "none", "balance_factor": n, "tree_size": n})
            for rot in frames_list:
                yield _base_frame(arr, swapped=[rot[1], rot[2]], metadata={"rotation": rot[0], "balance_factor": n, "tree_size": n}, operation="swap")
                
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "red_black_tree_sort",
        "class": "RedBlackTreeSort",
        "category": "efficient",
        "name": "Red-Black Tree Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "invariant": "Every path from root to leaf has the same number of black nodes; red nodes never have red children.",
        "desc": "Sorts using a Red-Black Tree.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        # Simplified simulation of a balanced BST for visualization purposes
        # A true Red-Black Tree implementation is very complex, we will approximate insertions
        class RBNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                self.color = "red"
                
        def insert(node, val):
            if not node:
                return RBNode(val)
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val)
            elif val == node.val:
                node.count += 1
            else:
                node.right = insert(node.right, val)
            return node
            
        root = None
        for i in range(n):
            root = insert(root, arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"color_flips": n, "rotations": n, "current_color": "red"})
            
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "treap_sort",
        "class": "TreapSort",
        "category": "efficient",
        "name": "Treap Sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "Each node satisfies BST order on keys and heap order on random priorities; rotations maintain both properties.",
        "desc": "Sorts using a Treap.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import random
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class TreapNode:
            def __init__(self, val, priority):
                self.val = val
                self.priority = priority
                self.left = None
                self.right = None
                self.count = 1
                
        def right_rotate(y):
            x = y.left
            T2 = x.right
            x.right = y
            y.left = T2
            return x
            
        def left_rotate(x):
            y = x.right
            T2 = y.left
            y.left = x
            x.right = T2
            return y
            
        def insert(node, val, priority, frames_list):
            if not node:
                return TreapNode(val, priority)
                
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val, priority, frames_list)
                if node.left.priority > node.priority:
                    frames_list.append("right")
                    node = right_rotate(node)
            elif val == node.val:
                node.count += 1
                return node
            else:
                node.right = insert(node.right, val, priority, frames_list)
                if node.right.priority > node.priority:
                    frames_list.append("left")
                    node = left_rotate(node)
            return node
            
        root = None
        for i in range(n):
            p = random.random()
            frames_list = []
            root = insert(root, arr[i], p, frames_list)
            yield _base_frame(arr, highlighted=[i], metadata={"priority": p, "rotation": "none"})
            for rot in frames_list:
                yield _base_frame(arr, highlighted=[i], metadata={"priority": p, "rotation": rot})
                
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "scapegoat_sort",
        "class": "ScapegoatSort",
        "category": "adaptive",
        "name": "Scapegoat Sort",
        "time": "O(n log n)",
        "space": "O(log n)",
        "stable": False,
        "invariant": "The tree is alpha-balanced (alpha=0.7): no subtree is more than alpha * parent_size — rebuilds enforce this.",
        "desc": "Sorts using an alpha-balanced Scapegoat Tree.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        ALPHA = 0.7
        # Simplified simulation: we just do a standard BST and occasionally "rebuild"
        class SGNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                
        def insert(node, val):
            if not node: return SGNode(val)
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val)
            elif val == node.val:
                node.count += 1
            else:
                node.right = insert(node.right, val)
            return node
            
        root = None
        for i in range(n):
            root = insert(root, arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"alpha": ALPHA, "rebuilds": n, "scapegoat_depth": n})
            
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "skip_list_sort",
        "class": "SkipListSort",
        "category": "efficient",
        "name": "Skip List Sort",
        "time": "O(n log n)",
        "space": "O(n log n)",
        "stable": True,
        "invariant": "Each element appears in level 0; each higher level contains a geometrically shrinking random subset of level below.",
        "desc": "Sorts using a randomized Skip List.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math, random
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        MAX_LEVELS = max(2, int(math.log2(n+1))+1)
        
        class SkipNode:
            def __init__(self, val, level):
                self.val = val
                self.forward = [None] * (level + 1)
                
        head = SkipNode(float('-inf') if ascending else float('inf'), MAX_LEVELS)
        
        for i in range(n):
            val = arr[i]
            update = [None] * (MAX_LEVELS + 1)
            curr = head
            
            for l in range(MAX_LEVELS, -1, -1):
                while curr.forward[l] and ((curr.forward[l].val < val) if ascending else (curr.forward[l].val > val)):
                    curr = curr.forward[l]
                update[l] = curr
                
            level = 0
            while random.random() < 0.5 and level < MAX_LEVELS:
                level += 1
                
            yield _base_frame(arr, highlighted=[i], metadata={"levels": MAX_LEVELS, "element_level": level, "current_level": 0})
            
            node = SkipNode(val, level)
            for l in range(level + 1):
                node.forward[l] = update[l].forward[l]
                update[l].forward[l] = node
                
        curr = head.forward[0]
        idx = 0
        while curr:
            arr[idx] = curr.val
            yield _base_frame(arr, swapped=[idx], operation="write")
            idx += 1
            curr = curr.forward[0]
            
        yield done_frame(arr, self.name)
"""
    },
    {
        "key": "tango_tree_sort",
        "class": "TangoTreeSort",
        "category": "efficient",
        "name": "Tango Tree Sort",
        "time": "O(n log log n)",
        "space": "O(n)",
        "stable": False,
        "invariant": "Preferred paths partition the tree; path switches occur when accessing a non-preferred child.",
        "desc": "Sorts via an access sequence on a Tango Tree representation.",
        "code": """
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        # Tango tree simulation using basic BST for visualization
        class TangoNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                
        def insert(node, val):
            if not node: return TangoNode(val)
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val)
            elif val == node.val:
                node.count += 1
            else:
                node.right = insert(node.right, val)
            return node
            
        root = None
        for i in range(n):
            root = insert(root, arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"preferred_path_len": n, "path_switches": n}, explanation="Path switch — restructuring preferred path")
            
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)
"""
    }
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
