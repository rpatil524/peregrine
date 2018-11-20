from collections import OrderedDict


def sign(n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


class AdjacencyListGraph(object):

    def __init__(self):
        self.adjacency = dict()

    def add(self, node, neighbors=None):
        neighbors = neighbors or set()
        if node in self.adjacency:
            self.adjacency[node].update(set(neighbors))
        else:
            self.adjacency[node] = set(neighbors)
        for neighbor in neighbors:
            if neighbor in self.adjacency:
                self.adjacency[neighbor].add(node)
            else:
                self.adjacency[neighbor] = {node}

    def monotonic_paths(self, node_src, node_dst, f_node_level):
        """
        Return the simple paths starting at ``node_src`` and ending at ``node_dst``,
        which are monotonic in level according to ``f_node_level`` returning an integer
        for the level of a given node.

        This implementation is based on code from the networkx library. See
        ``ATTRIBUTIONS`` in the root directory.
        """
        level = f_node_level(node_src)
        level_dst = f_node_level(node_dst)
        direction = sign(level_dst - level)
        to_visit = [[node_src]]
        visited = OrderedDict()
        paths = []
        while to_visit:
            next_layer = to_visit[-1]
            if not next_layer:
                to_visit.pop()
                if visited:
                    visited.popitem()
                continue
            node = next_layer.pop()
            level = f_node_level(node)
            if node == node_dst:
                paths.append(list(visited) + [node])
            elif node not in visited:
                visited[node] = None
                adjacent_nodes = [
                    (adjacent, f_node_level(adjacent))
                    for adjacent in self.adjacency[node]
                ]
                to_visit.append([
                    adjacent
                    for adjacent, next_level in adjacent_nodes
                    if (
                        (direction > 0 and next_level >= level)
                        or (direction < 0 and next_level <= level)
                        or (next_level == level)
                    )
                ])
        return paths

    def naive_monotonic_traversals(self, f_node_level):
        traversals = {}
        for node_src in self.adjacency.keys():
            traversals[node_src] = {}
            for node_dst in self.adjacency.keys():
                if node_src == node_dst:
                    continue
                paths = self.monotonic_paths(node_src, node_dst, f_node_level)
                if paths:
                    traversals[node_src][node_dst] = paths
        return traversals
