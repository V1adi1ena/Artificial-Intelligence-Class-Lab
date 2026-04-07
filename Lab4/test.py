import hw04

def run_test(f1, f2, label):
    print(f"--- 测试 {label} ---")
    print(f"f1: {f1}")
    print(f"f2: {f2}")
    try:
        result = hw04.MGU(f1, f2)
        if result is None:
            print("结果: 合一失败 (None)")
        else:
            print(f"结果: {result}")
    except Exception as e:
        print(f"发生错误: {e}")
    print("-" * 30)

if __name__ == "__main__":
    # 1. 基础合一：变量与常量
    run_test(['P(xx, a)'], ['P(b, yy)'], "基础合一")
    
    # 2. 嵌套合一：函数嵌套
    # 对应你之前问的样例：f(xx, yy) 与 f(g(yy), b)
    run_test(['f(xx, yy)'], ['f(g(yy), b)'], "嵌套合一 (你的样例)")
    
    # 3. 复杂函数嵌套与多变量
    # P(a, xx, f(g(yy))) 与 P(zz, f(zz), f(uu))
    run_test(['P(a, xx, f(g(yy)))'], ['P(zz, f(zz), f(uu))'], "复杂函数嵌套")
    
    # 4. 冲突失败：同一个变量绑定到不同常量
    run_test(['f(x, x)'], ['f(a, b)'], "冲突失败 (x=a vs x=b)")
    
    # 5. Occurs Check 失败：变量出现在包含它的项中
    # f(x) 与 f(g(x)) -> x 不能等于 g(x)
    run_test(['f(x)'], ['f(g(x))'], "Occurs Check 失败")
    
    # 6. 变量与变量合一
    run_test(['P(x, y)'], ['P(y, z)'], "变量与变量")
    
    # 7. 长度不匹配（Arity 错误）
    run_test(['P(x)'], ['P(x, y)'], "参数数量不匹配")

    # 8. KB1 中的变量 'v' 测试 (检查 is_var 是否包含 v)
    run_test(['L(tony, v)'], ['L(tony, rain)'], "KB1 变量 v 测试")