class TreeNode:
    def __init__(self, val, children=None):
        self.val = val
        self.children = children if children else []

class Solution:

    def max_depth(self, root):
        if not root:
            return 0

        if not root.children:
            return 1

        return 1 + max(self.max_depth(child) for child in root.children)

    def min_deletions(self, root, k):
        if not root:
            return 0

        self.deletions = 0

        def dfs(node, depth):
            if depth > k:
                # count this node + entire subtree
                self.deletions += self.count_subtree(node)
                return

            for child in node.children:
                dfs(child, depth + 1)

        def count_subtree(node):
            count = 1
            for child in node.children:
                count += count_subtree(child)
            return count

        # make count_subtree accessible inside dfs
        self.count_subtree = count_subtree
        dfs(root, 1)

        return self.deletions

def build_tree(val, children=None):
    return TreeNode(val, children)

def test_tree():
    sol = Solution()

    # Test 1: max depth — linear chain
    #     1
    #     |
    #     2
    #     |
    #     3
    root = build_tree(1, [build_tree(2, [build_tree(3)])])
    assert sol.max_depth(root) == 3, "Test 1 failed"
    print("Test 1 passed: max_depth =", sol.max_depth(root))

    # Test 2: max depth — wide tree
    #       1
    #     / | \
    #    2  3  4
    #   /
    #  5
    root = build_tree(1, [
        build_tree(2, [build_tree(5)]),
        build_tree(3),
        build_tree(4)
    ])
    assert sol.max_depth(root) == 3, "Test 2 failed"
    print("Test 2 passed: max_depth =", sol.max_depth(root))

    # Test 3: min deletions k=1 — only root survives
    #     1
    #     |
    #     2
    #     |
    #     3
    root = build_tree(1, [build_tree(2, [build_tree(3)])])
    assert sol.min_deletions(root, 1) == 2, "Test 3 failed"
    print("Test 3 passed: min_deletions(k=1) =", sol.min_deletions(root, 1))

    # Test 4: min deletions k=2
    #       1
    #     / | \
    #    2  3  4
    #   /
    #  5
    root = build_tree(1, [
        build_tree(2, [build_tree(5)]),
        build_tree(3),
        build_tree(4)
    ])
    assert sol.min_deletions(root, 2) == 1, "Test 4 failed"
    print("Test 4 passed: min_deletions(k=2) =", sol.min_deletions(root, 2))

    # Test 5: k >= max depth — no deletions needed
    root = build_tree(1, [build_tree(2, [build_tree(3)])])
    assert sol.min_deletions(root, 5) == 0, "Test 5 failed"
    print("Test 5 passed: min_deletions(k=5) =", sol.min_deletions(root, 5))

    # Test 6: single node
    root = build_tree(1)
    assert sol.max_depth(root) == 1, "Test 6 failed"
    assert sol.min_deletions(root, 1) == 0, "Test 6 failed"
    print("Test 6 passed: single node")

test_tree()     