def swap_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        while True:
            count = 0
            for j in range(n):
                if j == i: continue
                if arr[j] < arr[i]:
                    count += 1
            if count == i:
                break
            target = count
            while target < n and arr[target] == arr[i]:
                target += 1
            if target == i:
                break
            arr[i], arr[target] = arr[target], arr[i]
    return arr
print(swap_sort([3, 3, 2, 2, 1]))
print(swap_sort([4, 1, 2, 3, 2, 4, 1]))
print(swap_sort([2, 1, 2, 3, 3]))
