import numpy as np
from Cart import CARTClassifier


def count_leaves(node):
    if node is None:
        return 0
    if node.value is not None:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)


def count_nodes(node):
    if node is None:
        return 0
    if node.value is not None:
        return 1
    return 1 + count_nodes(node.left) + count_nodes(node.right)


# ============ 1. 加载数据 ============
data = np.loadtxt(r"d:\Code\AI\Lab6.2\german.data-numeric")
X = data[:, :-1].astype(np.float64)
y = data[:, -1].astype(np.int64)

print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
print(f"Class distribution: {dict(zip(*np.unique(y, return_counts=True)))}")

# ============ 2. 划分训练/测试集 ============
np.random.seed(42)
indices = np.random.permutation(len(X))
split = int(0.8 * len(X))
train_idx, test_idx = indices[:split], indices[split:]

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# ============ 3. 基准 CART（无剪枝，有限深度） ============
print("\n=== CART (max_depth=5, no pruning) ===")
cart1 = CARTClassifier(max_depth=5, min_samples_split=5)
cart1.fit(X_train, y_train)

y_pred = cart1.predict(X_test)
acc = np.mean(y_pred == y_test)
print(f"Test accuracy:  {acc:.4f} ({acc*100:.2f}%)")

y_train_pred = cart1.predict(X_train)
train_acc = np.mean(y_train_pred == y_train)
print(f"Train accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
print(f"Tree: {count_nodes(cart1.root)} nodes, {count_leaves(cart1.root)} leaves")

# ============ 4. CART + CCP 剪枝 ============
print("\n=== CART (max_depth=5, ccp_alpha=0.5) ===")
cart2 = CARTClassifier(max_depth=5, min_samples_split=5, ccp_alpha=0.5)
cart2.fit(X_train, y_train)

y_pred2 = cart2.predict(X_test)
acc2 = np.mean(y_pred2 == y_test)
print(f"Test accuracy:  {acc2:.4f} ({acc2*100:.2f}%)")

y_train_pred2 = cart2.predict(X_train)
train_acc2 = np.mean(y_train_pred2 == y_train)
print(f"Train accuracy: {train_acc2:.4f} ({train_acc2*100:.2f}%)")
print(f"Tree: {count_nodes(cart2.root)} nodes, {count_leaves(cart2.root)} leaves")

# ============ 5. 更深树 + 剪枝 ============
print("\n=== CART (max_depth=8, ccp_alpha=0.3) ===")
cart3 = CARTClassifier(max_depth=8, min_samples_split=5, ccp_alpha=0.3)
cart3.fit(X_train, y_train)

y_pred3 = cart3.predict(X_test)
acc3 = np.mean(y_pred3 == y_test)
print(f"Test accuracy:  {acc3:.4f} ({acc3*100:.2f}%)")

y_train_pred3 = cart3.predict(X_train)
train_acc3 = np.mean(y_train_pred3 == y_train)
print(f"Train accuracy: {train_acc3:.4f} ({train_acc3*100:.2f}%)")
print(f"Tree: {count_nodes(cart3.root)} nodes, {count_leaves(cart3.root)} leaves")

# ============ 6. 不同 ccp_alpha 对比 ============
print("\n=== CCP alpha sweep ===")
for alpha in [0.0, 0.1, 0.3, 0.5, 1.0, 2.0]:
    cart = CARTClassifier(max_depth=6, min_samples_split=5, ccp_alpha=alpha)
    cart.fit(X_train, y_train)
    yp = cart.predict(X_test)
    acc_val = np.mean(yp == y_test)
    n_leaves = count_leaves(cart.root)
    print(f"  alpha={alpha:.1f}: accuracy={acc_val:.4f}, leaves={n_leaves}")

# ============ 7. 打印一棵树结构 ============
print("\n=== Tree structure (max_depth=3, ccp_alpha=0.3) ===")
cart4 = CARTClassifier(max_depth=3, min_samples_split=10, ccp_alpha=0.3)
cart4.fit(X_train, y_train)
cart4.print_tree()
