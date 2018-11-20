# *- coding: utf-8 -*

import pytest

from peregrine.resources.graph import AdjacencyListGraph


def test_monotonic_paths():
    g = AdjacencyListGraph()
    g.add(1, {2, 4})
    g.add(2, {1, 3})
    g.add(3, {2, 4, 6})
    g.add(4, {1, 3, 5})
    g.add(5, {4, 6})
    g.add(6, {3, 5})
    levels = lambda n: 0 if n <= 2 else 1 if n <= 5 else 2
    #                 ━┓
    #         1        ┃
    #        / \       ┃ level 0
    #       2   \      ┃
    #      /     \    ━┫
    #     3 ----- 4    ┃
    #      \     /     ┃ level 1
    #       \   5      ┃
    #        \ /      ━┫
    #         6        ┃ level 2
    #                 ━┛
    def check(src, dst, result):
        assert sorted(g.monotonic_paths(src, dst, levels)) == sorted(result)
    check(1, 2, [[1, 2]])
    check(1, 3, [[1, 2, 3], [1, 4, 3]])
    check(1, 4, [[1, 2, 3, 4], [1, 4]])
    check(1, 5, [[1, 2, 3, 4, 5], [1, 4, 5]])
    check(1, 6, [[1, 2, 3, 6], [1, 2, 3, 4, 5, 6], [1, 4, 3, 6], [1, 4, 5, 6]])
    print()
