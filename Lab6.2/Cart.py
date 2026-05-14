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
  
class CARTClassifier:
    def __init__(
        self,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_impurity_decrease=0.0,
        ccp_alpha=0.0
    ):
        # 最大深度
        self.max_depth = max_depth
        # 最小划分样本数
        self.min_samples_split = min_samples_split
        # 最小叶子节点样本数
        self.min_samples_leaf = min_samples_leaf
        # 最小基尼下降
        self.min_impurity_decrease = min_impurity_decrease
        # CCP剪枝参数
        self.ccp_alpha = ccp_alpha
        # 根节点
        self.root = None
        # 类别数
        self.n_classes = None
        # 特征数
        self.n_features = None

    # 训练入口
    def fit(self, X, y):
        pass

    # 递归建树
    def _grow_tree(self, X, y, depth):
        pass

    # 寻找最佳划分
    def _best_split(self, X, y):
        pass

    # 计算Gini
    def _gini(self, y):
        pass

    # 计算划分后的Gini
    def _gini_gain(
        self,
        y,
        left_indices,
        right_indices
    ):
        pass

    # 划分数据
    def _split(
        self,
        feature_column,
        threshold
    ):
        pass

    # 生成叶子节点类别
    def _leaf_value(self, y):
        pass

    # 单样本预测
    def _predict_one(self, x, node):
        pass

    # 批量预测
    def predict(self, X):
        pass

    # 后剪枝
    def prune(self):
        pass

    # CCP递归剪枝
    def _prune_tree(self, node):
        pass

    # 子树误差
    def _subtree_cost(self, node):
        pass

    # 叶节点数
    def _num_leaves(self, node):
        pass

    # 打印树
    def print_tree(self):
        pass

    # 递归打印
    def _print_tree(self, node, indent=""):
        pass