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
    class_counts: Optional[np.ndarray] = None
    depth: int = 0


class DecisionTreeClassifier:
    """Unified decision tree: C4.5 (gain_ratio) / ID3 (entropy) / CART (gini).

    Parameters
    ----------
    criterion : {'gini', 'entropy', 'gain_ratio'}
        Splitting criterion. 'gini' = CART, 'gain_ratio' = C4.5.
    max_depth : int or None
    min_samples_split : int
    min_samples_leaf : int
    min_impurity_decrease : float
        Minimum score improvement to accept a split.
    ccp_alpha : float
        Cost-complexity pruning parameter (CART-style post-pruning).
    """

    def __init__(
        self,
        criterion: str = "gini",
        max_depth=None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
    ):
        if criterion not in ("gini", "entropy", "gain_ratio"):
            raise ValueError(f"criterion must be 'gini', 'entropy', or 'gain_ratio', got '{criterion}'")
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_impurity_decrease = min_impurity_decrease
        self.ccp_alpha = ccp_alpha
        self.root = None
        self.n_features = None
        self.n_classes = None

    # ── impurity / score (the only two methods that depend on criterion) ──

    def _impurity(self, y: np.ndarray) -> float:
        if len(y) == 0:
            return 0.0
        counts = np.bincount(y)
        probs = counts[counts > 0] / len(y)
        if self.criterion == "gini":
            return 1.0 - np.sum(probs ** 2)
        else:
            return -np.sum(probs * np.log2(probs))

    def _score(self, y: np.ndarray, left_idx: np.ndarray, right_idx: np.ndarray) -> float:
        n, nL, nR = len(y), len(left_idx), len(right_idx)
        if nL == 0 or nR == 0:
            return 0.0

        ig = self._impurity(y) - (nL / n * self._impurity(y[left_idx]) + nR / n * self._impurity(y[right_idx]))

        if self.criterion == "gain_ratio":
            si = -(nL / n) * np.log2(nL / n) - (nR / n) * np.log2(nR / n)
            return ig / si if si > 0 else 0.0
        return ig  # gini gain or information gain

    # ── tree building ──

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.n_features = X.shape[1]
        self.n_classes = len(np.unique(y))
        self.root = self._grow_tree(X, y, 0)
        if self.ccp_alpha > 0:
            self._prune()

    def _grow_tree(self, X: np.ndarray, y: np.ndarray, depth: int) -> Node:
        n = len(y)

        if n < self.min_samples_split:
            return self._leaf_node(y, depth)
        if self.max_depth is not None and depth >= self.max_depth:
            return self._leaf_node(y, depth)
        if len(np.unique(y)) == 1:
            return self._leaf_node(y, depth)

        feat, thr, best_score = self._best_split(X, y)
        if feat is None:
            return self._leaf_node(y, depth)

        left_idx, right_idx = self._split(X[:, feat], thr)
        if len(left_idx) < self.min_samples_leaf or len(right_idx) < self.min_samples_leaf:
            return self._leaf_node(y, depth)

        return Node(
            feature=feat,
            threshold=thr,
            score=best_score,
            left=self._grow_tree(X[left_idx], y[left_idx], depth + 1),
            right=self._grow_tree(X[right_idx], y[right_idx], depth + 1),
            samples=n,
            class_counts=np.bincount(y),
            depth=depth,
        )

    def _best_split(self, X: np.ndarray, y: np.ndarray):
        best_score = self.min_impurity_decrease
        best_feat, best_thr = None, None

        for i in range(X.shape[1]):
            for thr in self._thresholds(X[:, i]):
                left_idx, right_idx = self._split(X[:, i], thr)
                s = self._score(y, left_idx, right_idx)
                if s > best_score:
                    best_score = s
                    best_feat = i
                    best_thr = thr

        if best_feat is None:
            return None, None, None
        return best_feat, best_thr, best_score

    # ── helpers (criterion-independent) ──

    def _split(self, col: np.ndarray, thr: float):
        left = np.where(col <= thr)[0]
        right = np.where(col > thr)[0]
        return left, right

    def _thresholds(self, col: np.ndarray):
        vals = np.unique(col)
        return [(vals[i] + vals[i + 1]) / 2 for i in range(len(vals) - 1)]

    def _leaf_value(self, y: np.ndarray):
        return np.argmax(np.bincount(y))

    def _leaf_node(self, y: np.ndarray, depth: int) -> Node:
        return Node(value=self._leaf_value(y), samples=len(y),
                    class_counts=np.bincount(y), depth=depth)

    # ── prediction ──

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict_one(x, self.root) for x in X])

    def _predict_one(self, x: np.ndarray, node: Node):
        if node.value is not None:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        else:
            return self._predict_one(x, node.right)

    # ── CCP pruning ──

    def _prune(self):
        while self._prune_tree(self.root):
            pass

    def _prune_tree(self, node: Node) -> bool:
        if node is None or node.value is not None:
            return False

        changed = False
        if node.left is not None:
            changed |= self._prune_tree(node.left)
        if node.right is not None:
            changed |= self._prune_tree(node.right)

        left_leaf = node.left is None or node.left.value is not None
        right_leaf = node.right is None or node.right.value is not None

        if left_leaf and right_leaf:
            n_leaves = self._num_leaves(node)
            if n_leaves > 1:
                leaf_cost = node.samples - np.max(node.class_counts)
                subtree_cost = self._subtree_cost(node)
                eff_alpha = (leaf_cost - subtree_cost) / (n_leaves - 1)
                if eff_alpha <= self.ccp_alpha:
                    node.feature = None
                    node.threshold = None
                    node.score = None
                    node.left = None
                    node.right = None
                    node.value = np.argmax(node.class_counts)
                    changed = True
        return changed

    def _subtree_cost(self, node: Node) -> int:
        if node is None:
            return 0
        if node.value is not None:
            return node.samples - np.max(node.class_counts)
        return self._subtree_cost(node.left) + self._subtree_cost(node.right)

    def _num_leaves(self, node: Node) -> int:
        if node is None:
            return 0
        if node.value is not None:
            return 1
        return self._num_leaves(node.left) + self._num_leaves(node.right)

    # ── display ──

    def print_tree(self):
        if self.root is None:
            print("Tree not built yet.")
            return
        self._print_tree(self.root)

    def _print_tree(self, node: Node, indent: str = ""):
        if node.value is not None:
            print(f"{indent}[Leaf] depth={node.depth} | class={node.value} | samples={node.samples}")
            return
        crit_label = {"gini": "gini_gain", "entropy": "info_gain", "gain_ratio": "gain_ratio"}[self.criterion]
        print(f"{indent}[Node] depth={node.depth} | feat={node.feature} <= {node.threshold:.4f} | {crit_label}={node.score:.4f} | samples={node.samples}")
        if node.left is not None:
            print(f"{indent}  L:")
            self._print_tree(node.left, indent + "    ")
        if node.right is not None:
            print(f"{indent}  R:")
            self._print_tree(node.right, indent + "    ")
