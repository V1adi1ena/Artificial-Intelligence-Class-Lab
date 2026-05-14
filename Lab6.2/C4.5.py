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
        pass
    # 递归建树
    def _grow_tree(self, X, y, depth):
        pass


    # =========================
    # 寻找最佳划分
    # =========================
    def _best_split(self, X, y):
        pass


    # =========================
    # 信息熵
    # =========================
    def _entropy(self, y):
        pass


    # =========================
    # 信息增益
    # =========================
    def _information_gain(
        self,
        y,
        left_indices,
        right_indices
    ):
        pass


    # =========================
    # Split Information
    # =========================
    def _split_info(
        self,
        left_indices,
        right_indices,
        total_samples
    ):
        pass


    # =========================
    # Gain Ratio
    # =========================
    def _gain_ratio(
        self,
        y,
        left_indices,
        right_indices
    ):
        pass


    # =========================
    # 连续值划分
    # =========================
    def _split(
        self,
        feature_column,
        threshold
    ):
        pass


    # =========================
    # 生成候选阈值
    # =========================
    def _candidate_thresholds(
        self,
        feature_column
    ):
        pass


    # =========================
    # 叶子节点类别
    # =========================
    def _leaf_value(self, y):
        pass


    # =========================
    # 单样本预测
    # =========================
    def _predict_one(self, x, node):
        pass


    # =========================
    # 批量预测
    # =========================
    def predict(self, X):
        pass


    # =========================
    # 悲观剪枝
    # =========================
    def prune(self):
        pass


    # =========================
    # 递归剪枝
    # =========================
    def _prune_tree(self, node):
        pass


    # =========================
    # 子树误差率
    # =========================
    def _subtree_error(self, node):
        pass


    # =========================
    # 叶节点误差率
    # =========================
    def _leaf_error(self, node):
        pass


    # =========================
    # 打印树
    # =========================
    def print_tree(self):
        pass


    # =========================
    # 递归打印
    # =========================
    def _print_tree(self, node, indent=""):
        pass