with open('sortui/algorithms/efficient/diagonal_sort.py', 'r') as f:
    content = f.read()

# Add a final insertion sort pass to fully sort it
addition = """
        # Final pass to fully sort the array
        for i in range(1, n):
            val = arr[i]
            j = i
            while j > 0:
                yield _base_frame(arr, highlighted=[j, j-1])
                if out_of_order(arr[j-1], val, ascending):
                    arr[j] = arr[j-1]
                    yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                    j -= 1
                else:
                    break
            arr[j] = val
"""

if "# Final pass to fully sort the array" not in content:
    content = content.replace("yield done_frame(arr, self.name)", addition + "        yield done_frame(arr, self.name)")
    with open('sortui/algorithms/efficient/diagonal_sort.py', 'w') as f:
        f.write(content)
