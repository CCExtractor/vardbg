"""
Miscellaneous tests specified by the GCI task.
Minor edits were made to improve readability.
"""


# Implementation from https://dev.to/downey/solving-the-knapsack-problem-with-dynamic-programming-4hce
def knapsack(item_weights, item_values, total_weight):
    n = len(item_weights)
    max_values = [0] * (total_weight + 1)

    # Base case redundant, but added for clarity
    max_values[0] = 0

    # Recurrence
    for weight in range(1, total_weight + 1):
        max_sub_result = 0
        for i in range(1, n):
            wi = item_weights[i]
            vi = item_values[i]
            if wi <= weight:
                subproblem_value = max_values[weight - wi] + vi
                if subproblem_value > max_sub_result:
                    max_sub_result = subproblem_value
        max_values[weight] = max_sub_result

    # Results
    print("Maximum value possible: ", max_values[total_weight])
