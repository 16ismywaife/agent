# 1. 给定一个分数列表，输出及格（>=60）的人数
scores = [88, 45, 92, 60, 73, 39, 95]
nums=[]
for num in scores:
    if num>=60:
        nums.append(num)
print(len(nums))

# 2. 用字典统计每个分数段的人数（<60, 60-79, 80-100）
counts = {}
for s in scores:
    if s < 60:
        bucket = "<60"
    elif s < 80:
        bucket = "60-79"
    else:
        bucket = "80-100"
    counts[bucket] = counts.get(bucket, 0) + 1
print(counts)
# 3. 用列表推导式取出所有及格分数
numss=[x for x in scores if x >= 60]
print(numss)