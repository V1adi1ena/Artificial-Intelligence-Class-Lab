import re
from itertools import combinations
KB1 = {('A(tony)',),('A(mike)',),('A(john)',),('L(tony,rain)',),('L(tony,snow)',),('~A(x)','S(x)','C(x)'),('~C(y)','~L(y,rain)'),('L(z,snow)','~S(z)'),('~L(tony,u)','~L(mike,u)'),('L(tony,v)','L(mike,v)'),('~A(w)','~C(w)','S(w)')}
KB2 = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',), ('~On(xx,yy)','~Green(xx)','Green(yy)')}
#1
#任务目标：编写函数 ResolutionProp 实现命题逻辑的归结推理过程。
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
                    merged = simplify(merged)

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

def simplify(clause):
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

def replace(it, res):
    if not res:
        return it
    # 先处理~符号
    if it.startswith('~'):
        return '~' + replace(it[1:], res)
    
    if is_var(it):
        if it in res:
          return replace(res[it], res)
        return it
    if is_const(it):
        return it
    if is_func(it):
        func_name, func_args = split_func(it)
        new_args = [replace(x, res) for x in func_args]

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
        s = replace(s, res)
        t = replace(t, res)
        if s == t:
            continue
        if is_var(s):
            if is_occurred(s, t):
                return None
            new_binding = {s: t}
            res = {k: replace(v, new_binding) for k, v in res.items()}
            res[s] = t
            S = [(replace(a, new_binding), replace(b, new_binding)) for a, b in S]
            continue

        elif is_var(t):
            if is_occurred(t, s):
                print(f"occurs check 失败: {t} 出现在 {s} 中")
                return None
            new_binding = {t: s}
            res = {k: replace(v, new_binding) for k, v in res.items()}
            res[t] = s
            S = [(replace(a, new_binding), replace(b, new_binding)) for a, b in S]
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

'from MGU import *'
def Index(literal_idx,clause_idx,len):
    if len==1:
        return str(clause_idx+1)
    else:
        return str(clause_idx+1)+chr(ord('a')+literal_idx)
def iscomplementary(x,y):
    if not x or not y:  
        return False
    endx=x.find('(')
    endy=y.find('(')
    if x[0]=='~' and x[1:endx]==y[:endy]:
        return True
    if y[0]=='~' and y[1:endy]==x[:endx]:
        return True
    return False
def resolve(clause1,clause2,idx1,idx2):   #归结得到新子句
    newclause=list(clause1)+list(clause2)
    newclause.remove(clause1[idx1])
    newclause.remove(clause2[idx2])
    newclause=list(dict.fromkeys(newclause))
    return tuple(newclause)
def sequence(newclause,idx1,idx2,dictionary):
    if not dictionary:
        ans='R['+idx1+','+idx2+']='
    else:
        ans='R['+idx1+','+idx2+']'
        for key,value in dictionary.items():
            ans+='{'+str(key)+'='+str(value)+'}'
        ans+='='
    ans+=str(newclause)
    return ans
def sub(clause,dictionary):
    newclause=[]
    for x in clause:
        newclause.append(replace(x,dictionary))
    return tuple(newclause)
def resolution(KB):
    ALL=list(KB)
    support_list=[ALL[-1]]
    result=[]
    vis=set()
    while True:
        newclauset=[]
        for clause1_idx in range(len(ALL)):
            for clause2_idx in range(clause1_idx+1,len(ALL)):
                if clause1_idx==clause2_idx :
                    continue
                clause1,clause2=ALL[clause1_idx],ALL[clause2_idx]
                if (clause1,clause2) in vis:
                    continue
                if clause2 not in support_list and clause1 not in support_list:
                    continue
                for literal_idx1 in range(len(clause1)):
                    for literal_idx2 in range(len(clause2)):
                        literal1,literal2=clause1[literal_idx1],clause2[literal_idx2]
                        if not iscomplementary(literal1,literal2):
                            continue
                        '''处理互补对'''
                        literal1=literal1.replace('~','')
                        literal2=literal2.replace('~','')
                        literal1,literal2=[literal1],[literal2]
                        mgu_dict=MGU(literal1,literal2)
                        if mgu_dict==None:
                            continue
                        mgu_clause1=sub(clause1,mgu_dict)
                        mgu_clause2=sub(clause2,mgu_dict)
                        newclause=resolve(mgu_clause1,mgu_clause2,literal_idx1,literal_idx2)
                        if newclause in ALL or newclause in newclauset:
                            continue
                        vis.add((clause1,clause2))
                        idx1=Index(literal_idx1,clause1_idx,len(clause1))
                        idx2=Index(literal_idx2,clause2_idx,len(clause2))
                        seq=sequence(newclause,idx1,idx2,mgu_dict)
                        result.append(seq)
                        newclauset.append(newclause)
                        if newclause==():
                            return result
        ALL.extend(newclauset)
        support_list.extend(newclauset)
def newnum(num,res,usefulres,size):
    if num<=size:
        return num
    fa_seq=res[num-1]
    start=fa_seq.find('(')
    for i in range(size,len(usefulres)):
        begin=usefulres[i].find('(')
        if usefulres[i][begin:]==fa_seq[start:]:
            return i+1

def getfa(clause):
    start=clause.find('[')
    end=clause.find(']')
    num=clause[start+1:end].split(',')
    fa1=int(''.join(x for x in num[0] if not x.isalpha()))
    fa2=int(''.join(x for x in num[1] if not x.isalpha()))
    return fa1,fa2

def Resequence(seq,num1,num2,newnum1,newnum2):
    num1_pos=seq.find(num1)
    end=num1_pos+len(num1)
    seq=seq[:num1_pos]+newnum1+seq[end:]
    findnum2=num1_pos+len(newnum1)
    num2_pos=seq.find(num2, findnum2)
    end=num2_pos+len(num2)
    seq=seq[:num2_pos]+newnum2+seq[end:]
    return seq
def simplify(res,size):   #size是初始子句集大小
    useful=[]
    que=[len(res)]
    vis=set()
    while que!=[]:
        front=que.pop(0)
        if front in vis:
            continue
        vis.add(front)

        useful.append(res[front-1])
        fa1,fa2=getfa(res[front-1])
        if fa1>size:
            que.append(fa1)
        if fa2>size:
            que.append(fa2)
    useful.reverse()
    usefulres=res[0:size]+useful
    for i in range(size,len(usefulres)):
        fa1,fa2=getfa(usefulres[i])
        newnum1=str(newnum(fa1,res,usefulres,size))
        newnum2=str(newnum(fa2,res,usefulres,size))
        #print(fa1,newnum1,fa2,newnum2)
        usefulres[i]=Resequence(usefulres[i],str(fa1),str(fa2),newnum1,newnum2)
    return usefulres
def solve(KB: set):
    res=list(KB.copy())+resolution(KB)
    res=simplify(res,len(KB))
    return res