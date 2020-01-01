from .searching import binary_search, bfs, dfs
from .run import debug_func
from vardbg import ansi

SAMPLE_LIST = [2, 3, 4, 10, 40]
SAMPLE_LIST_ITEM = 10
SAMPLE_GRAPH = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["F"], "F": []}
SAMPLE_GRAPH_ITEM = "A"


def test_searching():
    print(ansi.bold("Binary Search"))
    bs_list = SAMPLE_LIST.copy()
    debug_func(binary_search, bs_list, 0, len(bs_list) - 1, SAMPLE_LIST_ITEM)
    print(bs_list)
    print()

    print(ansi.bold("BFS"))
    bfs_graph = SAMPLE_GRAPH.copy()
    debug_func(bfs, bfs_graph, SAMPLE_GRAPH_ITEM)
    print()

    print(ansi.bold("DFS"))
    dfs_graph = SAMPLE_GRAPH.copy()
    debug_func(dfs, dfs_graph, SAMPLE_GRAPH_ITEM)
    print()
