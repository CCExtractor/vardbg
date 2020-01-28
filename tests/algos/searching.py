"""
Searching algorithms specified by the GCI task.
Minor edits were made to improve readability.
"""


# Implementation from https://www.geeksforgeeks.org/python-program-for-binary-search/
# Returns index of x in arr if present, else -1
def binary_search(arr, left, right, x):
    # Check base case
    if right >= left:
        mid = left + (right - left) // 2

        # If element is present at the middle itself
        if arr[mid] == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid] > x:
            return binary_search(arr, left, mid - 1, x)

        # Else the element can only be present in right subarray
        else:
            return binary_search(arr, mid + 1, right, x)
    else:
        # Element is not present in the array
        return -1


# Implementation from https://www.educative.io/edpresso/how-to-implement-depth-first-search-in-python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = []
        first_call = True
    else:
        first_call = False

    if node not in visited:
        visited.append(node)
        for neighbor in graph[node]:
            dfs(graph, neighbor, visited=visited)

    if first_call:
        print("Visited nodes: " + " ".join(visited))


# Implementation from https://www.educative.io/edpresso/how-to-implement-a-breadth-first-search-in-python
def bfs(graph, node):
    visited = []  # List to keep track of visited nodes.
    queue = []  # Initialize a queue
    vs_queue = []  # Output

    visited.append(node)
    queue.append(node)

    while queue:
        s = queue.pop(0)
        vs_queue.append(s)

        for neighbor in graph[s]:
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)

    print("Visited nodes: " + " ".join(vs_queue))
