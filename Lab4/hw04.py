import re
from itertools import combinations
KB1 = {('A(tony)',),('A(mike)',),('A(john)',),('L(tony,rain)',),('L(tony,snow)',),('~A(x)','S(x)','C(x)'),('~C(y)','~L(y,rain)'),('L(z,snow)','~S(z)'),('~L(tony,u)','~L(mike,u)'),('L(tony,v)','L(mike,v)'),('~A(w)','~C(w)','S(w)')}
KB2 = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',), ('~On(xx,yy)','~Green(xx)','Green(yy)')}
"""1
任务目标：编写函数 ResolutionProp 实现命题逻辑的归结推理过程。"""
def ResolutionProp(kb:set):
  clauses = list(kb)
  res = []
  idx = 1
  for clause in clauses:
    #print(f"{clause}\n")
    res.append(f"{idx} {clause}")
    idx += 1
  
  found = True
  visited_clauses = []
  while found:
      found = False
      n = len(clauses)
      for i in range(n):
          for j in range(i+1, n):
              if i in visited_clauses or j in visited_clauses:
                 continue
              ci = clauses[i]
              cj = clauses[j]
              src_idx = 0
              for src in ci:
                obj_idx = 0
                for obj in cj:
                  if obj=='~'+src or src=='~'+obj:
                    merged = sorted(tuple(x for x in ci if x != src) + tuple(x for x in cj if x != obj))
                    merged = simp(merged)

                    suffix_i = ""
                    if len(ci) > 1:
                        suffix_i = chr(ord('a') + src_idx)
                    suffix_j = ""
                    if len(cj) > 1:
                        suffix_j = chr(ord('a') + obj_idx)

                    res.append(f"{idx} R[{i+1}{suffix_i}, {j+1}{suffix_j}] = {merged}")
                    idx += 1

                    if not merged: return res
                    
                    found = True
                    visited_clauses.append(i)
                    clauses[j] = merged
                    break;
                  obj_idx += 1
                src_idx += 1
                if found:
                  break
              if found:
                break
          if found:
            break
  return res

def simp(clause):
    """删除互补文字对"""
    clause = list(clause)  # 转为列表
    changed = True
    while changed:
        changed = False
        # 检查任意两个文字是否互补
        n = len(clause)
        for i in range(n):
            for j in range(i+1, n):
                a, b = clause[i], clause[j]
                if a == '~' + b or b == '~' + a:
                    # 删除这两个互补文字
                    del clause[j]
                    del clause[i]
                    changed = True
                    break
            if changed:
                break
    # 去重并排序，返回元组
    return tuple(sorted(set(clause)))

"""2最一般合一算法 (MGU)
任务目标：编写函数 MGU 实现最一般合一算法。

实现要点：

输入：两个原子公式（字符串 str 类型），它们的谓词相同。
输出：最一般合一的结果。
数据类型为字典 dict。
格式形如：{变量: 项, 变量: 项}，其中的变量和项均为字符串。
异常处理：若不存在合一（即合一失败），则返回空字典 {}。
示例：

示例 1
调用：MGU('P(xx,a)', 'P(b,yy)')
返回：{'xx': 'b', 'yy': 'a'}
示例 2：
调用：MGU('P(a,xx,f(g(yy)))', 'P(zz,f(zz),f(uu))')
返回：{'zz': 'a', 'xx': 'f(a)', 'uu': 'g(yy)'}"""
def is_var(it):
    return it in {'x', 'xx', 'y', 'yy', 'z', 'zz', 'w', 'ww', 'u', 'uu', 'v', 'vv', 'p', 'q', 'r', 's', 't'}
def is_const(it):
    if(is_var(it)):
       return False
    if('(' in it):
       return False
    return True
def is_func(it):
   return isinstance(it, str) and '(' in it

def split_func(func):
    args = []
    start = func.find('(')
    func_name = func[:start]
    
    inner = func[start + 1 : func.rfind(')')]
    depth = 0
    current = ''
    for ch in inner:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            args.append(current.strip())
            current = ''
        else:
            current += ch
    if current.strip():
        args.append(current.strip())
    
    return func_name, args

def replace_literal(it, res):
    if not res:
        return it
    # 先处理~符号
    if it.startswith('~'):
        return '~' + replace_literal(it[1:], res)
    
    if is_var(it):
        if it in res:
          return replace_literal(res[it], res)
        return it
    if is_const(it):
        return it
    if is_func(it):
        func_name, func_args = split_func(it)
        new_args = [replace_literal(x, res) for x in func_args]

        return f"{func_name}({', '.join(new_args)})"

def is_occurred(var, term):
    """检查var是否出现在term中（防止循环替换"""
    if var == term:
        return True
    if is_var(term) or is_const(term):
        return False
    elif is_func(term):
        _, args = split_func(term)
        return any(is_occurred(var, arg) for arg in args)

def MGU(f1, f2):
    if len(f1) != len(f2):
        return None
    res = {}
    S = list(zip(f1, f2))
    while S:
        s, t = S.pop(0)
        s = replace_literal(s, res)
        t = replace_literal(t, res)
        if s == t:
            continue
        if is_var(s):
            if is_occurred(s, t):
                return None
            new_binding = {s: t}
            res = {k: replace_literal(v, new_binding) for k, v in res.items()}
            res[s] = t
            S = [(replace_literal(a, new_binding), replace_literal(b, new_binding)) for a, b in S]
            continue
        elif is_var(t):
            if is_occurred(t, s):
                print(f"occurs check 失败: {t} 出现在 {s} 中")
                return None
            new_binding = {t: s}
            res = {k: replace_literal(v, new_binding) for k, v in res.items()}
            res[t] = s
            S = [(replace_literal(a, new_binding), replace_literal(b, new_binding)) for a, b in S]
            continue
        elif is_func(s) and is_func(t):
            fname_s, args_s = split_func(s)
            fname_t, args_t = split_func(t)
            if fname_s != fname_t or len(args_s) != len(args_t):
                print(f"函数不匹配: {fname_s} vs {fname_t}, 参数数 {len(args_s)} vs {len(args_t)}")
                return None
            S = list(zip(args_s, args_t)) + S
            continue
        else:
            return None
    return res


"""3Resolution Principle 推导
输入 KB = {(A(tony),),(A(mike),),(A(john),),(L(tony,rain),),(L(tony,snow),),(~A(x),S(x),C(x)),(~C(y),~L(y,rain)),(L(z,snow),~S(z)),(~L(tony,u),~L(mike,u)),(L(tony,v),L(mike,v)),(~A(w),~C(w),S(w))}

输出

(A(tony),)
(A(mike),)
(A(john),)
(L(tony,rain),)
(L(tony,snow),)
(~A(x),S(x),C(x))
(~C(y),~L(y,rain))
(L(z,snow),~S(z))
(~L(tony,u),~L(mike,u))
(L(tony,v),L(mike,v))
(~A(w),~C(w),S(w))
R[2,11a]{w=mike} = (S(mike),~C(mike))
R[5,9a]{u=snow} = (~L(mike,snow),)
R[6c,12b]{x=mike} = (S(mike),~A(mike),S(mike))
R[2,14b] = (S(mike),)
R[8b,15]{z=mike} = (L(mike,snow),)
R[13,16] = []"""

"""编号，对序列进行索引"""
def Index(literal_idx,clause_idx,clause_len):
    if clause_len==1:
        return str(clause_idx+1)
    else:
        return str(clause_idx+1)+chr(ord('a')+literal_idx)
"""判断谓词是否互补"""
def iscomplementary(x,y):
    endx=x.find('(')
    endy=y.find('(')
    x = x[:endx]
    y = y[:endy]
    return x=='~'+y or y=='~'+x
"""对两个clause归结生成子clause"""
def resolve(clause1,clause2,idx1,idx2):   #归结得到新子句
    newclause=list(clause1)+list(clause2)
    newclause.remove(clause1[idx1])
    newclause.remove(clause2[idx2])
    """去重"""
    newclause=list(dict.fromkeys(newclause))
    return tuple(newclause)
"""生成result序列"""
def generate_sequence(newclause,idx1,idx2,dictionary):
    if not dictionary:
        res='R['+idx1+','+idx2+']='
    else:
        res='R['+idx1+','+idx2+']'
        """添加绑定关系"""
        res += '{'
        for key,value in dictionary.items():
            res += str(key) + '=' + str(value) + ', '
        res += '} = '
    res+=str(newclause)
    return res
"""调用replace_literal函数，对clause进行文字替换"""
def replace_clause(clause,dic):
    newclause=[replace_literal(literal, dic) for literal in clause]
    return tuple(newclause)
def resolution(KB):
    U=list(KB)
    support_list=[U[-1]]
    result=[]
    """记录已经处理的子句对"""
    visited=set()
    while True:
        newclauset=[]
        '''遍历所有子句对'''
        for clause1_idx in range(len(U)):
            for clause2_idx in range(clause1_idx+1,len(U)):
                '''同一个字句'''
                if clause1_idx==clause2_idx :
                    continue
                clause1,clause2=U[clause1_idx],U[clause2_idx]
                '''已经处理的子句对'''
                if (clause1,clause2) in visited:
                    continue
                """必须有一个子句在支持集里"""
                if clause2 not in support_list and clause1 not in support_list:
                    continue
                """遍历子句的所有文字"""
                for literal_idx1 in range(len(clause1)):
                    for literal_idx2 in range(len(clause2)):
                        literal1,literal2=clause1[literal_idx1],clause2[literal_idx2]
                        """判断谓词是否互补"""
                        if not iscomplementary(literal1,literal2):
                            continue
                        '''如果互补就忽略否定进行合一'''
                        literal1=literal1.replace('~','')
                        literal2=literal2.replace('~','')
                        literal1,literal2=[literal1],[literal2]
                        mgu_dict=MGU(literal1,literal2)
                        """合一失败"""
                        if mgu_dict==None:
                            continue
                        """如果合一成功，就对两个文字所在的子句进行替换"""
                        new_clause1=replace_clause(clause1,mgu_dict)
                        new_clause2=replace_clause(clause2,mgu_dict)
                        """归结得到新子句"""
                        newclause=resolve(new_clause1,new_clause2,literal_idx1,literal_idx2)
                        """新子句在所有子句集里或新子句集里"""
                        if newclause in U or newclause in newclauset:
                            continue
                        visited.add((clause1,clause2))  
                        """编号，对序列进行索引"""
                        idx1=Index(literal_idx1,clause1_idx,len(clause1))
                        idx2=Index(literal_idx2,clause2_idx,len(clause2))
                        """生成序列"""
                        seq=generate_sequence(newclause,idx1,idx2,mgu_dict)
                        result.append(seq)
                        newclauset.append(newclause)
                        if newclause==():
                            return result
        if newclauset==[]:
            return result
        U.extend(newclauset)
        support_list.extend(newclauset)
"""重新寻找简化后的序列中子句的来源所在位置"""
def renum(p,res,simplified_res,size):
    if p<=size: return p
    fa_seq=res[p-1]
    start=fa_seq.find('(')
    for i in range(size,len(simplified_res)):
        begin=simplified_res[i].find('(')
        if simplified_res[i][begin:]==fa_seq[start:]:
            return i+1
"""获取clause的前辈"""
def parent(clause):
    start=clause.find('[')
    end=clause.find(']')
    num=clause[start+1:end].split(',')
    p1=int(''.join(x for x in num[0] if not x.isalpha()))
    p2=int(''.join(x for x in num[1] if not x.isalpha()))
    return p1,p2

def regen_sequence(chld,p1,p2,newp1,newp2):
    p1_pos=chld.find(p1)
    end=p1_pos+len(p1)
    chld=chld[:p1_pos]+newp1+chld[end:]
    findp2=p1_pos+len(newp1)
    p2_pos=chld.find(p2, findp2)
    end=p2_pos+len(p2)
    chld=chld[:p2_pos]+newp2+chld[end:]
    return chld
def simplify(res,size):   #size是初始子句集大小
    simplified_path=[]
    """将最后一个clause的idx加入队列，从后往前遍历"""
    que=[len(res)]
    visited=set()
    """循环遍历队列，直到里面的所有子句的前辈都直接来源于初始子句集"""
    while que!=[]:
        front=que.pop(0)
        if front in visited:
            continue
        """将当前子句加入路径"""
        visited.add(front)
        simplified_path.append(res[front-1])
        """获取当前的子句的前辈"""
        p1,p2=parent(res[front-1])
        """如果前辈在初始子句集里，就不能加入队列，因为其不能再往前找了"""
        if p1>size:
            que.append(p1)
        if p2>size:
            que.append(p2)
    simplified_path.reverse()
    simplified_res=res[0:size]+simplified_path
    """重新建立索引，以及子句的前辈子句的位置"""
    for i in range(size,len(simplified_res)):
        """找到简化前前辈子句的位置"""
        i_p1,i_p2=parent(simplified_res[i])
        """找到简化后前辈子句的位置"""
        newnum1=str(renum(i_p1,res,simplified_res,size))
        newnum2=str(renum(i_p2,res,simplified_res,size))
        simplified_res[i]=regen_sequence(simplified_res[i],str(i_p1),str(i_p2),newnum1,newnum2)
    for i in range(len(simplified_res)):
        simplified_res[i] = str(i+1) + " " + str(simplified_res[i])
    return simplified_res
def solve(KB: set):
    """归结推理"""
    res=list(KB.copy())+resolution(KB)
    """去除不需要的路径上的子句"""
    res=simplify(res,len(KB))
    return res