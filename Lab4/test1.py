"""
Task 1 - ResolutionProp 命题逻辑归结推理测试文件
包含多个测试用例，验证ResolutionProp函数的正确性
"""

from hw04 import ResolutionProp


def test_case_1():
    """测试用例1：简单矛盾推理
    KB = {('FirstGrade',), ('~FirstGrade', 'Child'), ('~Child',)}
    推理过程应该得出空子句
    """
    print("=" * 60)
    print("测试用例1：简单矛盾推理")
    print("=" * 60)
    KB = {('FirstGrade',), ('~FirstGrade', 'Child'), ('~Child',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and result[-1].endswith("()"):
        print("✓ 成功推出矛盾（空子句）")
    else:
        print("✗ 未能推出矛盾")
    print()


def test_case_2():
    """测试用例2：另一个简单推理
    KB = {('P',), ('~P', 'Q'), ('~Q',)}
    应该推出空子句
    """
    print("=" * 60)
    print("测试用例2：简单推理（P, Q）")
    print("=" * 60)
    KB = {('P',), ('~P', 'Q'), ('~Q',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and result[-1].endswith("()"):
        print("✓ 成功推出矛盾（空子句）")
    else:
        print("✗ 未能推出矛盾")
    print()


def test_case_3():
    """测试用例3：三层推理链
    KB = {('A',), ('~A', 'B'), ('~B', 'C'), ('~C',)}
    从A推出B，从B推出C，从C推出矛盾
    """
    print("=" * 60)
    print("测试用例3：三层推理链")
    print("=" * 60)
    KB = {('A',), ('~A', 'B'), ('~B', 'C'), ('~C',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and result[-1].endswith("()"):
        print("✓ 成功推出矛盾（空子句）")
    else:
        print("✗ 未能推出矛盾")
    print()


def test_case_4():
    """测试用例4：多分支推理
    KB = {('P',), ('Q',), ('~P', '~Q', 'R'), ('~R',)}
    需要同时使用P和Q才能推出R，再与~R矛盾
    """
    print("=" * 60)
    print("测试用例4：多分支推理")
    print("=" * 60)
    KB = {('P',), ('Q',), ('~P', '~Q', 'R'), ('~R',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and result[-1].endswith("()"):
        print("✓ 成功推出矛盾（空子句）")
    else:
        print("✗ 未能推出矛盾")
    print()


def test_case_5():
    """测试用例5：无矛盾的知识库
    KB = {('A',), ('B',)}
    这个知识库是一致的，不能推出矛盾
    """
    print("=" * 60)
    print("测试用例5：一致的知识库（无矛盾）")
    print("=" * 60)
    KB = {('A',), ('B',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and any("()" in step for step in result):
        print("✗ 推出了矛盾（不应该）")
    else:
        print("✓ 未能推出矛盾（正确，知识库一致）")
    print()


def test_case_6():
    """测试用例6：条件和查询
    KB = {('Student',), ('~Student', 'Study'), ('~Student', '~Study', 'Fail'), ('~Study',), ('~Fail',)}
    复杂的多层推理
    """
    print("=" * 60)
    print("测试用例6：复杂多层推理")
    print("=" * 60)
    KB = {('Student',), ('~Student', 'Study'), ('~Student', '~Study', 'Fail'), ('~Study',), ('~Fail',)}
    
    result = ResolutionProp(KB)
    
    print(f"知识库 KB = {KB}")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()
    
    # 判断是否推出矛盾
    if result and result[-1].endswith("()"):
        print("✓ 成功推出矛盾（空子句）")
    else:
        print("✗ 未能推出矛盾")
    print()


def test_case_7():
    """测试用例7：给定的原始KB1
    验证原始代码中的KB1能否正确处理
    """
    print("=" * 60)
    print("测试用例7：原始KB1")
    print("=" * 60)
    KB1 = {('A(tony)',),('A(mike)',),('A(john)',),('L(tony,rain)',),('L(tony,snow)',),
           ('~A(x)','S(x)','C(x)'),('~C(y)','~L(y,rain)'),('L(z,snow)','~S(z)'),
           ('~L(tony,u)','~L(mike,u)'),('L(tony,v)','L(mike,v)'),('~A(w)','~C(w)','S(w)')}
    
    result = ResolutionProp(KB1)
    
    print("知识库 KB1 (包含一阶逻辑原子)")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()


def test_case_8():
    """测试用例8：给定的原始KB2
    验证原始代码中的KB2能否正确处理
    """
    print("=" * 60)
    print("测试用例8：原始KB2")
    print("=" * 60)
    KB2 = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',), 
           ('~On(xx,yy)','~Green(xx)','Green(yy)')}
    
    result = ResolutionProp(KB2)
    
    print("知识库 KB2 (关于位置和颜色)")
    print("\n推理步骤：")
    for step in result:
        print(step)
    print()


def run_all_tests():
    """运行所有测试用例"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "命题逻辑归结推理 (ResolutionProp) 测试" + " " * 8 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
    test_case_7()
    test_case_8()
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "所有测试完成" + " " * 26 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")


if __name__ == "__main__":
    run_all_tests()
