import numpy as np
np.random.seed(42)      # 固定随机种子，保证每次结果一样（这行很重要）

# 1. 造 5 个学生 × 3 个科目 的成绩矩阵（0~100 随机整数）
scores = np.random.randint(0,100,(5,3))
print(scores)

# 2. 打印 shape
print(scores.shape)
# 3. 全体平均分
print(scores.mean())
# 4. 每个科目的平均分（用 axis=0）
print(scores.mean(axis=0))
# 5. 每个学生的平均分（用 axis=1）
print(scores.mean(axis=1))
# 6. 每个学生的最高分（用 axis=1）
print(scores.max(axis=1))
# 7. 取出所有 > 90 的分数
print(scores[scores>90])
# 8. 把所有 < 60 的分数改成 60（提示：布尔索引赋值）
scores[scores<60]=60
print(scores)