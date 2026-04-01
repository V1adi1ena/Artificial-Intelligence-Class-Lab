def ResolutionProp(kb: set):
    # 子句列表，每个元素是一个子句（元组）
    clauses = list(kb)
    steps = []           # 记录推导步骤
    idx = len(clauses)   # 下一个新子句的序号（从原始子句数量+1开始）

    # 记录原始子句
    for i, clause in enumerate(clauses, 1):
        steps.append(f"{i}  {clause}")

    # 主循环：不断尝试归结，直到产生空子句或无法再生成新子句
    while True:
        found = False
        n = len(clauses)
        # 扫描所有子句对（i < j）
        for i in range(n):
            for j in range(i + 1, n):
                ci = clauses[i]
                cj = clauses[j]
                # 寻找互补文字
                for lit1 in ci:
                    for lit2 in cj:
                        if lit1 == '~' + lit2 or lit2 == '~' + lit1:
                            # 构造新子句：合并两个子句并删除互补文字
                            merged_set = set(ci) | set(cj)
                            merged_set.discard(lit1)
                            merged_set.discard(lit2)
                            new_clause = tuple(sorted(merged_set))   # 排序便于比较

                            # 空子句表示矛盾
                            if not new_clause:
                                steps.append(f"{idx}  空子句（矛盾） 由 {i+1} 和 {j+1} 归结")
                                return steps

                            # 如果新子句不存在于当前子句集中，则加入
                            if new_clause not in clauses:
                                clauses.append(new_clause)
                                steps.append(f"{idx}  {new_clause}  由 {i+1} 和 {j+1} 归结")
                                idx += 1
                                found = True
                                break   # 跳出最内层循环
                    if found:
                        break
                if found:
                    break
            if found:
                break
        # 如果没有产生任何新子句，则无法再归结，结束
        if not found:
            break

    return steps