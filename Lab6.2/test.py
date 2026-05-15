import numpy as np
from C45 import C45Classifier  # 如果文件名不含点号，改成 from C45 import

# ============ 1. 加载数据 ============
data = np.loadtxt(r"d:\Code\AI\Lab6.2\german.data-numeric")
X = data[:, :-1].astype(np.float64)
y = data[:, -1].astype(np.int64)

print(f"数据集: {X.shape[0]} 样本, {X.shape[1]} 特征")
print(f"类别分布: {dict(zip(*np.unique(y, return_counts=True)))}")

# ============ 2. 划分训练/测试集 ============
np.random.seed(42)
indices = np.random.permutation(len(X))
split = int(0.8 * len(X))
train_idx, test_idx = indices[:split], indices[split:]

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

print(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")

# ============ 3. 训练 ============
clf = C45Classifier(max_depth=5, min_samples_split=5)
clf.fit(X_train, y_train)

# ============ 4. 查看树结构 ============
clf.print_tree()

# ============ 5. 测试准确率 ============
y_pred = clf.predict(X_test)
accuracy = np.mean(y_pred == y_test)
print(f"\n测试准确率: {accuracy:.4f} ({accuracy*100:.2f}%)")

# 训练集准确率
y_train_pred = clf.predict(X_train)
train_acc = np.mean(y_train_pred == y_train)
print(f"训练准确率: {train_acc:.4f} ({train_acc*100:.2f}%)")