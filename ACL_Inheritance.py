# You have a graph where:
# Nodes can have explicit allow or deny permissions
# Permissions propagate through edges (inheritance)
# You need to determine the effective permission of every node

from collections import deque

def compute_acl(nodes, edges, allow_acl, deny_acl):

    adj = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    parents = {node: [] for node in nodes}
    explicit = {}
    effective = {}

    for parent, child in edges:
        adj[parent].append(child)
        indegree[child] += 1
        parents[child].append(parent)

    #explicit permissions
    for node in allow_acl:
        explicit[node] = 'allow'

    for node in deny_acl:
        explicit[node] = 'deny'  # deny overrides allow if both set

    queue = deque()

    for node in nodes:
        if indegree[node] == 0:
            queue.append(node)

    while queue:
        node = queue.popleft()

        if node in explicit:
            effective[node] = explicit[node]

        elif not parents[node]:
            effective[node] = 'deny'    # root with no explicit → deny

        else:
            effective[node] = 'allow'

        for child in adj[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    return effective

def test_acl():
    nodes = ['A', 'B', 'C']
    edges = [('A', 'B'), ('B', 'C')]
    allow_acl = ['A']
    deny_acl = []

    result = compute_acl(nodes, edges, allow_acl, deny_acl)
    print(result)


if __name__ == "__main__":
    test_acl()





