// 实验报告1 · 题4：线性表、栈和队列的应用
//
// (1) 链表按基准值分割   ← 用你题1 写过的遍历 + 摘链
// (2) 括号匹配（三种括号）← 用你题2 写过的栈
// (3) 迷宫最短路径（选做）← 用你题3 写过的队列
//
// ★ 编译/调试：建议复制到 C:\cppbuild\ 下（中文路径 gdb 读不到源码）

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int ElemType;

// ==================== 单链表（和题1 一样）====================

typedef struct LNode
{
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;

// 尾插建表（这个我写好了，直接用）
void CreateList(LinkList &L, int n)
{
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL;
    LNode *tail = L;
    for (int i = 0; i < n; i++)
    {
        LNode *q = (LinkList)malloc(sizeof(LNode));
        q->data = rand() % 900 + 100;
        q->next = NULL;
        tail->next = q;
        tail = q;
    }
}

void DispList(LinkList L)
{
    for (LNode *p = L->next; p != NULL; p = p->next)
        printf("%d ", p->data);
    printf("\n");
}

// 栈（括号匹配要用，字符存进 int 里）
typedef struct snode
{
    ElemType data;
    struct snode *next;
} SNode;

void Push(SNode *&S, ElemType e)
{
    SNode *q = (SNode *)malloc(sizeof(SNode));
    q->data = e;
    q->next = S;
    S = q;
}

bool Pop(SNode *&S, ElemType &e)
{
    if (S == NULL) return false;
    e = S->data;
    SNode *p = S;
    S = S->next;
    free(p);
    return true;
}


// ==================== 你写的两个函数 ====================

// ① 按基准值分割：所有 < pivot 的结点排在 >= pivot 的结点【之前】
//
// ★ 题目要求：不占用新的存储空间 + 注意时间复杂度
//
// 【思路】建两路链表（小 / 大），遍历原表把结点分别挂上去，最后接起来。
//        全程只改 next 指针，不 malloc 任何结点。
//
// 【怎么写】用两个"假头结点"（在栈上开，不是 malloc，所以不算占空间）：
//
//   LNode bigHead;                    ← 大表用这个假头
//   bigHead.next = NULL;
//   LNode *tailSmall = L;             ← ★ 小表直接用 L 这个头结点
//   LNode *tailBig   = &bigHead;      ← 大表的尾巴，一开始指向假头
//
//   for (LNode *p = L->next; p != NULL; )      ← ★ 注意循环里自己推进 p
//   {
//       LNode *next = p->next;                 ← ① 先存下一个（马上要改 p->next）
//       if (p->data < pivot) { tailSmall->next = p; tailSmall = p; }
//       else                 { tailBig->next   = p; tailBig   = p; }
//       p = next;                              ← ② 再往前走
//   }
//   tailSmall->next = bigHead.next;            ← ③ 小表尾巴接上大表
//   tailBig->next = NULL;                      ← ④ 大表尾巴收尾（否则可能接到旧链）
//
// 时间复杂度：一遍遍历 O(n)。空间：只用了两个指针，O(1)。
void PartitionList(LinkList &L, ElemType pivot)
{
    // TODO
}

// ② 括号匹配：判断字符串里的 () [] {} 是否【正确配对】
//
// 规则：
//   遇到左括号 ( [ {  → 入栈
//   遇到右括号 ) ] }  → 栈顶必须是【与之配对】的左括号，否则 return false；
//                        然后把它弹出
//   其它字符          → ★ 跳过（题目要求"增加对非括号字符的判断"）
//   扫完整串          → ★ 栈必须为空，否则 return false（比如 "(((" ）
//
// 两个必查的失败情况：
//   ")( "   ← 栈空时遇到右括号 → 失败
//   "((("   ← 扫完了栈不空    → 失败
//
// 判配对可以写个小函数：左括号和右括号是不是一对
bool IsMatch(char left, char right)
{
    return (left == '(' && right == ')') ||
           (left == '[' && right == ']') ||
           (left == '{' && right == '}');
}

bool BracketMatch(const char *s)
{
    // TODO
    return false;
}


// ==================== 下面不用改 ====================

int main()
{
    srand((unsigned)time(NULL));

    // ---------- (1) 链表分割 ----------
    printf("=== (1) 按基准值分割单链表 ===\n");
    LinkList L = NULL;
    CreateList(L, 10);
    printf("原链表：");
    DispList(L);

    ElemType pivot = L->next->data;        // 拿第一个元素当基准
    printf("基准值：%d\n", pivot);

    PartitionList(L, pivot);
    printf("分割后（左边全 < %d，右边全 >= %d）：\n        ", pivot, pivot);
    DispList(L);

    // ---------- (2) 括号匹配 ----------
    printf("\n=== (2) 括号匹配 ===\n");
    const char *tests[] = {
        "(a[b]{c})",          // 合法
        "{[()]}",             // 合法
        "([)]",               // 不合法（交叉）
        "(((",                // 不合法（没闭合）
        ")( ",                // 不合法（右括号在左）
        "x=1+(2*[3-4])",      // 合法（含非括号字符）
        "hello world",        // 合法（完全没有括号）
        NULL
    };
    for (int i = 0; tests[i] != NULL; i++)
        printf("  %-16s → %s\n", tests[i],
               BracketMatch(tests[i]) ? "合法 ✅" : "不合法 ❌");

    return 0;
}

// ==================== 期望输出 ====================
// === (1) 按基准值分割单链表 ===
// 原链表：834 217 596 143 782 405 961 328 674 509
// 基准值：834
// 分割后（左边全 < 834，右边全 >= 834）：
//         217 596 143 782 405 328 674 509 834
//
// === (2) 括号匹配 ===
//   (a[b]{c})        → 合法 ✅
//   {[()]}           → 合法 ✅
//   ([)]             → 不合法 ❌
//   (((              → 不合法 ❌
//   )(               → 不合法 ❌
//   x=1+(2*[3-4])    → 合法 ✅
//   hello world      → 合法 ✅
