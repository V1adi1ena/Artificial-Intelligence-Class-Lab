def BinarySearch(nums, target):
    """
    :param nums: list[int]
    :param target: int
    :return: int
    """
    length = len(nums)
    if length == 0: return -1

    if nums[length//2] == target: return length//2

    if nums[length//2] < target:
        if BinarySearch(nums[length//2+1:], target) == -1:
            return -1
        return BinarySearch(nums[length//2+1:], target) + length//2
    else:
        return BinarySearch(nums[:length//2], target)

def MatrixAdd(A, B):
    """
    :param A: list[list[int]]
    :param B: list[list[int]]
    :return: list[list[int]]
    """
    res = A
    length = len(A)

    for i in range(length):
        for j in range(length):
            res[i][j] = A[i][j] + B[i][j]
    
    return res

def MatrixMul(A, B):
    """
    :param A: list[list[int]]
    :param B: list[list[int]]
    :return: list[list[int]]
    """
    length = len(A)
    res = [[0]*length for i in range(length)]

    for i in range(length):
        for j in range(length):
            for k in range(length):
              res[i][j] += A[i][k] * B[k][j]
    
    return res

def ReverseKeyValue(dict1):
    """
    :param dict1: dict
    :return: dict
    """
    return {key: val for val, key in dict1.items()}
