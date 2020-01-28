#!/usr/bin/env python3


def bubble_sort(lst):
    # Swap the elements to arrange in order
    for iter_num in range(len(lst) - 1, 0, -1):
        for i in range(iter_num):  # vardbg: ref lst[i]
            if lst[i] > lst[i + 1]:
                tmp_i = lst[i]  # vardbg: ref lst[tmp_i]
                lst[i] = lst[i + 1]
                lst[i + 1] = tmp_i

        print(f"Iteration {iter_num}:", lst)

    return lst


def main():
    lst = [8, 17, 3, 9]
    print("Unsorted:", lst)
    bubble_sort(lst)
    print("After:", lst)


if __name__ == "__main__":
    main()
