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
// ────────────────────────────────────────────────────────────
// 【一、什么叫"假头"】
//   假头（头结点）= 一个不存数据、只用来"占位"的结点。
//   你其实一直在用它：题1 的 CreateListTail 里那句
//       L = malloc(...);  L->next = NULL;
//   建出来的 L 就是假头 —— 第一个数据结点挂在它后面。
//
//   假头有什么用？让"挂第一个结点"和"挂第 2、3 个结点"用同一句代码：
//       tail->next = p;  tail = p;
//   没有假头的话，每次都要先判断"现在表是不是空的"。
//
// 【二、什么叫"小表 / 大表"】
//   不是新造两条链表！是把【原来的结点】分成两组，分别用两根尾巴串起来。
//   一个结点都不 malloc，只改 next 指针。
//
// ────────────────────────────────────────────────────────────
// 【三、怎么写：两个假头，左右对称，最好理解】
//
//   LNode smallHead, bigHead;                        ← 两个假头，开在栈上（不是 malloc）
//   LNode *tailSmall = &smallHead;                   ← 尾巴指针：一开始指向假头
//   LNode *tailBig   = &bigHead;
//   smallHead.next = NULL;
//   bigHead.next = NULL;
//
//   for (LNode *p = L->next; p != NULL; )            ← ★ 注意 for 第三段是空的
//   {
//       LNode *pnext = p->next;                      ← ① 先存下一个（马上要改 p->next）
//       if (p->data < pivot) { tailSmall->next = p; tailSmall = p; }   ← 挂到小表尾巴
//       else                 { tailBig->next   = p; tailBig   = p; }   ← 挂到大表尾巴
//       p = pnext;                                   ← ② 再往前走
//   }
//   tailSmall->next = bigHead.next;                  ← ③ 小表的尾巴接上大表的第一个
//   tailBig->next = NULL;                            ← ④ 大表收尾（否则可能接到旧链）
//   L->next = smallHead.next;                        ← ⑤ 把结果接回 L 这个头结点后面
//
// ★ 命名建议：变量别叫 next —— 会和结构体字段 p->next 看混。
//   pnext / tailSmall / tailBig 这种名字，三天后回来看还认得出。
//
// 【四、为什么循环里必须自己推进 p】
//   因为你把 p 挂到新表上时执行了 tailSmall->next = p，之后 p 的 next 会被覆盖成
//   下一个挂进来的结点 —— 如果不先存 pnext，后面的元素全丢。
//
// 时间复杂度：一遍遍历 O(n)。空间：两个假头 + 几个指针，O(1)。
void PartitionList(LinkList &L, ElemType pivot)
{
    LNode smallhead,bighead;
    LNode *tailsmall=&smallhead,*tailbig=&bighead;
    smallhead.next=NULL;
    bighead.next=NULL;
    for(LNode *p=L->next;p!=NULL;){
        LNode *pnext=p->next;
        if(p->data<pivot){
            tailsmall->next=p;
            tailsmall=p;
        }else{
            tailbig->next=p;
            tailbig=p;
        }
        p=pnext;
    }
    tailsmall->next=bighead.next;
    tailbig->next=NULL;
    L->next=smallhead.next;
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
    SNode *S=NULL;
    for(int i=0;s[i]!='\0';i++){
        char c=s[i];
        if(c=='('||c=='['||c=='{'){
            Push(S,c);
        }else if(c==')'||c==']'||c=='}'){
            ElemType top;
            if(!Pop(S,top)) return false;
            if(!IsMatch(top,c)) return false;
        }

    }
    return S==NULL;
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
