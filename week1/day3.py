def get_bucket(s):

   if s<60:
       return "<60"
   elif 60<=s<80:
       return "60-79"
   else:
       return">=80"

# 用起来
scores = [88, 45, 92, 60, 73, 39, 95]
counts = {}
for s in scores:
    b = get_bucket(s)
    counts[b] = counts.get(b, 0) + 1
print(counts)

print(get_bucket(45))   # 应该输出 <60
print(get_bucket(73))   # 应该输出 60-79

def pass_rate(scores, line=60):
    """返回及格率，比如 5/7 -> 0.714"""
    # 提示：先数及格的个数，再除以总数
    l1st=[]
    for s in scores:
        if s>=line:
            l1st.append(s)
    return(len(l1st)/len(scores))

scores = [88, 45, 92, 60, 73, 39, 95]
print(pass_rate(scores))         # 默认按 60 分算
print(pass_rate(scores, 80))     # 按 80 分算

class ScoreAnalyzer:
    """分数分析器"""

    def __init__(self, scores):
        self.scores = scores          # 把传进来的分数存成自己的属性

    def count_pass(self, line):
        """及格人数"""
        l1st = []
        for s in self.scores:
            if s >= line:
                l1st.append(s)
        return (len(l1st))

    def pass_rate(self, line):
        """及格率"""
        l1st = []
        for s in self.scores:
            if s >= line:
                l1st.append(s)
        return (len(l1st) / len(self.scores))

    def buckets(self):
        """返回各分数段人数的字典，用 get_bucket()"""
        counts = {}
        for s in self.scores:
            b = get_bucket(s)
            counts[b] = counts.get(b, 0) + 1
        return counts

    def summary(self,line):

        total = len(self.scores)
        passed = self.count_pass(line)
        rate = self.pass_rate(line)
        print(f"共 {total} 人，及格 {passed} 人，及格率 {rate:.1%}")


if __name__ == "__main__":
    a = ScoreAnalyzer([88, 45, 92, 60, 73, 39, 95])
    print(a.count_pass(60))     # 5
    print(a.pass_rate(60))      # 0.714...
    print(a.buckets())        # {'80-100': 3, '<60': 2, '60-79': 2}
    print(a.summary(line=60))        # 共 7 人，及格 5 人，及格率 71.4%