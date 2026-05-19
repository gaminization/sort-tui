import os

with open('sortui/algorithms/__init__.py', 'r') as f:
    content = f.read()

new_simples = [
    'TwoWayBubbleSort', 'OptimizedBubbleSort', 'DutchNationalFlagSort',
    'GravitySortSimulation', 'CircleSort', 'SwapSort', 'MaxSort',
    'BidirectionalSelectionSort', 'SpaghettiSort', 'LinkedListInsertionSort',
    'SplicedInsertionSort'
]

new_keys = [
    'two_way_bubble', 'optimized_bubble', 'flag', 'gravity', 'circle',
    'swap_sort', 'max_sort', 'bidirectional_selection', 'spaghetti_real',
    'list_insertion', 'spliced_insertion'
]

# Update imports
import_statement = "from sortui.algorithms.simple import (\n    " + ",\n    ".join([
    "BubbleSort", "CocktailShakerSort", "CycleSort", "ExchangeSort",
    "GnomeSort", "InsertionSort", "OddEvenSort", "SelectionSort", "StrandSort"
] + new_simples) + ",\n)"

import re
content = re.sub(r'from sortui\.algorithms\.simple import \([\s\S]*?\)', import_statement, content)

# Update ALGORITHMS dict
algo_updates = ""
for k, cls in zip(new_keys, new_simples):
    algo_updates += f'    "{k}": {cls},\n'

content = content.replace('"strand": StrandSort,\n}', f'"strand": StrandSort,\n{algo_updates}}}')

# Update CATEGORIES dict
cat_updates = ""
for k in new_keys:
    cat_updates += f'        "{k}",\n'

content = content.replace('"strand",\n    ],', f'"strand",\n{cat_updates}    ],')

with open('sortui/algorithms/__init__.py', 'w') as f:
    f.write(content)
