

# def solv(paths):
#     dic = {A : B for A,B in paths}
#     for city in dic.values():
#         if city in dic.keys():
#             continue
#         return city
    
# input = [["A", "B"], ["B", "C"], ["C", "D"]]
# print(solv(input))

def f1(mat):
    dim = len(mat)
    matt = []
    for i, row in enumerate(mat):
        if dim in row:
            col = []
            continue
        return False
    return True
input = [[1,2,3], [3,1,2], [2,3,1]]
print(f1(input))