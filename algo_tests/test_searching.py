from .searching import binary_search, bfs, dfs
from vardbg.debugger import Debugger
from vardbg import ansi

SAMPLE_LIST = [2, 3, 4, 10, 40]
SAMPLE_LIST_ITEM = 10
SAMPLE_GRAPH = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["F"], "F": []}
SAMPLE_GRAPH_ITEM = "A"


def test_searching():
    print(ansi.bold("Binary Search"))
    with Debugger() as dbg:
        bs_list = SAMPLE_LIST.copy()
        dbg.run(binary_search, bs_list, 0, len(bs_list) - 1, SAMPLE_LIST_ITEM)
        print(bs_list)
        print()

    print(ansi.bold("BFS"))
    with Debugger() as dbg:
        bfs_graph = SAMPLE_GRAPH.copy()
        dbg.run(bfs, bfs_graph, SAMPLE_GRAPH_ITEM)
        print()

    print(ansi.bold("DFS"))
    with Debugger() as dbg:
        dfs_graph = SAMPLE_GRAPH.copy()
        dbg.run(dfs, dfs_graph, SAMPLE_GRAPH_ITEM)
        print()
