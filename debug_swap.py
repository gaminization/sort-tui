def swap_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        while True:
            count = 0
            for j in range(n):
                if j == i: continue
                if arr[j] < arr[i]:
                    count += 1
            target = count
            while target < n and arr[target] == arr[i]:
                target += 1
            if target == i or target >= n or arr[i] == arr[target]:
                break
            print(f"i={i}, arr={arr}, count={count}, target={target}")
            arr[i], arr[target] = arr[target], arr[i]
    return arr
print(swap_sort([3, 3, 2, 2, 1]))
