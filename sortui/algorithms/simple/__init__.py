from .two_way_bubble import TwoWayBubbleSort
from .optimized_bubble import OptimizedBubbleSort
from .flag import DutchNationalFlagSort
from .gravity import GravitySortSimulation
from .circle import CircleSort
from .swap_sort import SwapSort
from .max_sort import MaxSort
from .bidirectional_selection import BidirectionalSelectionSort
from .spaghetti_real import SpaghettiSort
from .list_insertion import LinkedListInsertionSort
from .spliced_insertion import SplicedInsertionSort
from .two_way_bubble import TwoWayBubbleSort
from .optimized_bubble import OptimizedBubbleSort
from .flag import DutchNationalFlagSort
from .gravity import GravitySortSimulation
from .circle import CircleSort
from .swap_sort import SwapSort
from .max_sort import MaxSort
from .bidirectional_selection import BidirectionalSelectionSort
from .spaghetti_real import SpaghettiSort
from .list_insertion import LinkedListInsertionSort
from .spliced_insertion import SplicedInsertionSort
from sortui.algorithms.simple.cycle import CycleSort
from sortui.algorithms.simple.gnome import GnomeSort
from sortui.algorithms.simple.odd_even import OddEvenSort
from sortui.algorithms.simple.strand import StrandSort

from sortui.algorithms.simple.bubble import BubbleSort
from sortui.algorithms.simple.cocktail_shaker import CocktailShakerSort
from sortui.algorithms.simple.exchange import ExchangeSort
from sortui.algorithms.simple.insertion import InsertionSort
from sortui.algorithms.simple.selection import SelectionSort

__all__ = [
    "BubbleSort",
    "InsertionSort",
    "SelectionSort",
    "CocktailShakerSort",
    "GnomeSort",
    "OddEvenSort",
    "ExchangeSort",
    "CycleSort",
    "StrandSort",
    "TwoWayBubbleSort",
    "OptimizedBubbleSort",
    "DutchNationalFlagSort",
    "GravitySortSimulation",
    "CircleSort",
    "SwapSort",
    "MaxSort",
    "BidirectionalSelectionSort",
    "SpaghettiSort",
    "LinkedListInsertionSort",
    "SplicedInsertionSort",
]

for cls_name in __all__:
    cls = locals().get(cls_name)
    if cls and getattr(cls, 'category', None) == "CATEGORY":
        cls.category = "Simple Sorts"
