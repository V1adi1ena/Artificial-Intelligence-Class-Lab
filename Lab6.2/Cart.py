from dataclasses import dataclass
from typing import Optional, Any
import numpy as np

@dataclass
class Node:
    feature: Optional[int] = None
    threshold: Optional[float] = None
    score: Optional[float] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    value: Optional[Any] = None
    samples: int = 0
    class_counts: Optional[dict] = None
    depth: int = 0


class CARTClassifier:
    def __init__(
        self,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_impurity_decrease=0.0,
        ccp_alpha=0.0
    ):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_impurity_decrease = min_impurity_decrease
        self.ccp_alpha = ccp_alpha
        self.root = None
        self.n_classes = None
        self.n_features = None

    def fit(self, X, y):
        self.n_features = X.shape[1]
        self.n_classes = len(np.unique(y))
        self.root = self._grow_tree(X, y, 0)
        if self.ccp_alpha > 0:
            self._prune()

    def _grow_tree(self, X, y, depth):
        n_samples = len(y)
        if n_samples < self.min_samples_split:
            return Node(value=self._leaf_value(y), samples=n_samples,
                       class_counts=np.bincount(y), depth=depth)

        if self.max_depth is not None and depth >= self.max_depth:
            return Node(value=self._leaf_value(y), samples=n_samples,
                       class_counts=np.bincount(y), depth=depth)

        if len(np.unique(y)) == 1:
            return Node(value=self._leaf_value(y), samples=n_samples,
                       class_counts=np.bincount(y), depth=depth)

        best_feature, best_threshold, best_gain = self._best_split(X, y)

        if best_feature is None:
            return Node(value=self._leaf_value(y), samples=n_samples,
                       class_counts=np.bincount(y), depth=depth)

        left_idx, right_idx = self._split(X[:, best_feature], best_threshold)

        if len(left_idx) < self.min_samples_leaf or len(right_idx) < self.min_samples_leaf:
            return Node(value=self._leaf_value(y), samples=n_samples,
                       class_counts=np.bincount(y), depth=depth)

        node = Node(
            feature=best_feature,
            threshold=best_threshold,
            score=best_gain,
            left=self._grow_tree(X[left_idx], y[left_idx], depth + 1),
            right=self._grow_tree(X[right_idx], y[right_idx], depth + 1),
            samples=n_samples,
            class_counts=np.bincount(y),
            depth=depth
        )
        return node

    def _best_split(self, X, y):
        best_gain = self.min_impurity_decrease
        best_feature = None
        best_threshold = None

        for i in range(X.shape[1]):
            thresholds = self._candidate_thresholds(X[:, i])
            for threshold in thresholds:
                left_idx, right_idx = self._split(X[:, i], threshold)
                gain = self._gini_gain(y, left_idx, right_idx)
                if gain > best_gain:
                    best_gain = gain
                    best_feature = i
                    best_threshold = threshold

        if best_feature is None:
            return None, None, None
        return best_feature, best_threshold, best_gain

    def _gini(self, y):
        if len(y) == 0:
            return 0.0
        class_counts = np.bincount(y)
        probs = class_counts[class_counts > 0] / len(y)
        return 1.0 - np.sum(probs ** 2)

    def _gini_gain(self, y, left_indices, right_indices):
        n_left = len(left_indices)
        n_right = len(right_indices)
        n = len(y)
        if n_left == 0 or n_right == 0:
            return 0.0
        gini_parent = self._gini(y)
        gini_left = self._gini(y[left_indices])
        gini_right = self._gini(y[right_indices])
        return gini_parent - (n_left / n * gini_left + n_right / n * gini_right)

    def _split(self, feature_column, threshold):
        left_indices = np.where(feature_column <= threshold)[0]
        right_indices = np.where(feature_column > threshold)[0]
        return left_indices, right_indices

    def _candidate_thresholds(self, feature_column):
        values = np.unique(feature_column)
        thresholds = []
        for i in range(len(values) - 1):
            thresholds.append((values[i] + values[i + 1]) / 2)
        return thresholds

    def _leaf_value(self, y):
        class_counts = np.bincount(y)
        return np.argmax(class_counts)

    def _predict_one(self, x, node):
        if node.value is not None:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        else:
            return self._predict_one(x, node.right)

    def predict(self, X):
        return np.array([self._predict_one(x, self.root) for x in X])

    def _prune(self):
        while self._prune_tree(self.root):
            pass

    def _prune_tree(self, node):
        if node is None or node.value is not None:
            return False

        pruned = False
        if node.left is not None:
            pruned |= self._prune_tree(node.left)
        if node.right is not None:
            pruned |= self._prune_tree(node.right)

        left_leaf = node.left is None or node.left.value is not None
        right_leaf = node.right is None or node.right.value is not None

        if left_leaf and right_leaf:
            subtree_cost = self._subtree_cost(node)
            n_leaves = self._num_leaves(node)
            if n_leaves > 1:
                leaf_cost = node.samples - np.max(node.class_counts)
                effective_alpha = (leaf_cost - subtree_cost) / (n_leaves - 1)
                if effective_alpha <= self.ccp_alpha:
                    node.feature = None
                    node.threshold = None
                    node.score = None
                    node.left = None
                    node.right = None
                    node.value = np.argmax(node.class_counts)
                    pruned = True

        return pruned

    def _subtree_cost(self, node):
        if node is None:
            return 0
        if node.value is not None:
            return node.samples - np.max(node.class_counts)
        return self._subtree_cost(node.left) + self._subtree_cost(node.right)

    def _num_leaves(self, node):
        if node is None:
            return 0
        if node.value is not None:
            return 1
        return self._num_leaves(node.left) + self._num_leaves(node.right)

    def print_tree(self):
        if self.root is None:
            print("Tree not built yet.")
            return
        self._print_tree(self.root)

    def _print_tree(self, node, indent=""):
        if node.value is not None:
            majority = np.argmax(node.class_counts) if node.class_counts is not None else "?"
            print(f"{indent}[Leaf] depth={node.depth} | class={node.value} (majority={majority}) | samples={node.samples}")
            return
        print(f"{indent}[Node] depth={node.depth} | feature={node.feature} <= {node.threshold:.4f} | gini_gain={node.score:.4f} | samples={node.samples}")
        if node.left is not None:
            print(f"{indent}  Left:")
            self._print_tree(node.left, indent + "    ")
        if node.right is not None:
            print(f"{indent}  Right:")
            self._print_tree(node.right, indent + "    ")
