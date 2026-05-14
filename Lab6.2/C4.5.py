from dataclasses import dataclass
from typing import Optional, Any
import numpy as np

@dataclass
class Node:
    # 当前划分使用的特征索引
    feature: Optional[int] = None
    # 当前划分阈值
    threshold: Optional[float] = None
    # 当前节点信息增益 / gain ratio / gini下降
    score: Optional[float] = None
    # 左右子树
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    # 叶子节点类别
    value: Optional[Any] = None
    # 当前节点样本数
    samples: int = 0
    # 当前节点类别统计
    class_counts: Optional[dict] = None
    # 当前节点深度
    depth: int = 0

class C45Classifier:
    def __init__(
        self,
        max_depth=None,
        min_samples_split=2,
        min_gain_ratio=0.0
    ):
        # 最大深度
        self.max_depth = max_depth
        # 最小划分样本数
        self.min_samples_split = min_samples_split
        # 最小信息增益率
        self.min_gain_ratio = min_gain_ratio
        # 根节点
        self.root = None
        # 特征数
        self.n_features = None
        # 类别数
        self.n_classes = None
    # 训练
    def fit(self, X, y):
        self.root = self._grow_tree(X, y, 0)
    # 递归建树
    def _grow_tree(self, X, y, depth):
        decision_feature, decision_threshold = self._best_split(X, y)
        if decision_feature is None:
            return Node(value = self._leaf_value(y))
        left_indices, right_indices = self._split(X[:, decision_feature], decision_threshold)
        if len(y)<self.min_samples_split or depth >= self.max_depth or self._gain_ratio(y, left_indices, right_indices) < self.min_gain_ratio:
            return Node(value = self._leaf_value(y))
        node = Node(
            feature=decision_feature,
            threshold=decision_threshold,
            score=self._gain_ratio(y, left_indices, right_indices),
            left=self._grow_tree(X[left_indices], y[left_indices], depth+1),
            right=self._grow_tree(X[right_indices], y[right_indices], depth+1),
            samples=len(X),
            class_counts=np.bincount(y),
            depth=depth
        )
        return node
    """寻找最佳划分,如果找到使得该节点会被判定为叶子节点的划分也不会在此处进行判定 只负责寻找最佳划分"""
    def _best_split(self, X, y):
        best_gain_ratio = 0.0
        best_feature = None
        best_threshold = None
        for i in range(len(X[0])):
            thresholds = self._candidate_thresholds(X[:, i])
            for threshold in thresholds:
                left_indices, right_indices = self._split(X[:, i], threshold)
                score = self._gain_ratio(y, left_indices, right_indices)
                if score > best_gain_ratio:
                    best_gain_ratio = score
                    best_feature = i
                    best_threshold = threshold
        return best_feature, best_threshold
    """计算信息熵 y:节点的target序列"""
    def _entropy(self, y):
        if(len(y) == 0):
            return 0
        class_counts = np.bincount(y)
        coefs = class_counts[class_counts>0] / len(y)
        entropy = -np.sum(coefs * np.log2(coefs))
        return entropy
    """计算信息增益 y:节点的target序列 left_indices:左子树索引 right_indices:右子树索引"""
    def _information_gain(self, y, left_indices, right_indices):
        left_entropy = self._entropy(y[left_indices])
        right_entropy = self._entropy(y[right_indices])
        return self._entropy(y) - (len(left_indices) / len(y) * left_entropy + len(right_indices) / len(y) * right_entropy)
    """计算分裂信息"""
    def _split_info(self, left_indices, right_indices, total_samples):
        D1 = len(left_indices)
        D2 = len(right_indices)
        D = total_samples
        return -D1/D * np.log2(D1/D) - D2/D * np.log2(D2/D)
    """计算信息增益率 y:节点的target序列 left_indices:左子树索引 right_indices:右子树索引"""
    def _gain_ratio(self, y, left_indices, right_indices):
        return self._information_gain(y, left_indices, right_indices) / self._split_info(left_indices, right_indices, len(y))
    """连续值划分"""
    def _split(self, feature_column, threshold):
        left_indices = np.where(feature_column <= threshold)[0]
        right_indices = np.where(feature_column > threshold)[0]
        return left_indices, right_indices
    """候选阈值,把特征值排序,取每个值的中间值作为候选阈值"""
    def _candidate_thresholds(self, feature_column):
      values = np.unique(feature_column)
      thresholds = []
      for i in range(len(values) - 1):
          midpoint = (values[i] + values[i + 1]) / 2
          thresholds.append(midpoint)
      return thresholds
    """根据当前y的各个类别返回一个出现最多的类作为该叶子节点的类别"""
    def _leaf_value(self, y):
        class_counts = np.bincount(y)
        return np.argmax(class_counts)
    """单个样本预测"""
    def _predict_one(self, x, node):
        if node.value is not None:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        else:
            return self._predict_one(x, node.right)
    """批量预测"""
    def predict(self, X):
        return np.array([self._predict_one(x, self.root) for x in X])
    """剪枝"""
    def prune(self):
        pass
    """递归剪枝"""
    def _prune_tree(self, node):
        pass
    """子树误差率"""
    def _subtree_error(self, node):
        pass
    """叶子节点误差率"""
    def _leaf_error(self, node):
        pass
    def print_tree(self):
        if self.root is None:
            print("请先建立决策树喵~")
            return
        self._print_tree(self.root)

    def _print_tree(self, node, indent=""):
        if node.value is not None:
            print(f"{indent}[Leaf] depth={node.depth} | class={node.value} | samples={node.samples} | class_counts={node.class_counts}")
            return
        print(f"{indent}[Node] depth={node.depth} | feature={node.feature} <= {node.threshold:.4f} | gain_ratio={node.score:.4f} | samples={node.samples} | class_counts={node.class_counts}")
        if node.left is not None:
            print(f"{indent}  Left:")
            self._print_tree(node.left, indent + "    ")
        if node.right is not None:
            print(f"{indent}  Right:")
            self._print_tree(node.right, indent + "    ")