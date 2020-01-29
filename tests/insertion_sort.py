#!/usr/bin/env python3


def insertion_sort(lst):
    for i in range(1, len(lst)):  # vardbg: ref lst[i]
        j = i - 1  # vardbg: ref lst[j]
        nxt_element = lst[i]

        # Compare the current element with next one
        while lst[j] > nxt_element and j >= 0:
            lst[j + 1] = lst[j]
            j = j - 1

        lst[j + 1] = nxt_element
        print(f"Iteration {i}:", lst)

    return lst


def main():
    lst = [8, 17, 3, 9]
    print("Unsorted:", lst)
    insertion_sort(lst)
    print("After:", lst)


if __name__ == "__main__":
    main()
