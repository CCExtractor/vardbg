"""
Miscellaneous tests specified by the GCI task.
Minor edits were made to improve readability.
"""


# Implementation from https://dev.to/downey/solving-the-knapsack-problem-with-dynamic-programming-4hce
def knapsack(item_weights, item_values):
    n = len(item_weights)
    W = 15  # total weight capacity
    K = [0] * (W + 1)

    # Base case redundant, but added for clarity
    K[0] = 0

    # Recurrence
    for w in range(1, W + 1):
        max_sub_result = 0
        for i in range(1, n):
            wi = item_weights[i]
            vi = item_values[i]
            if wi <= w:
                subproblem_value = K[w - wi] + vi
                if subproblem_value > max_sub_result:
                    max_sub_result = subproblem_value
        K[w] = max_sub_result

    # Results
    print("Result: ", K[W])
    print("K array: ", K)
