// 实验报告1 · 题3：队列的链式存储结构（入队、出队、遍历、翻转）
//
// ★ 编译/调试：建议复制到 C:\cppbuild\ 下再调试（中文路径 gdb 读不到源码）
//   复制：Ctrl+Shift+P → Run Task → "复制到英文目录（调试用）"
//
// 题目要求：
//   (1) 用随机函数生成 10 个 3 位整数（100~999），入队
//   (2) 用遍历操作输出队列内容
//   (3) 把队列的内容翻转，应用出队操作输出队列内容

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

// ==================== 队列 ====================

typedef struct qnode
{
    ElemType data;
    struct qnode *next;
} QNode;

// ★ 链队列：需要一个【队头指针】和一个【队尾指针】
//   为什么两个都要：入队在队尾（O(1)），出队在队头（O(1)）。只有一个指针的话必有一端要 O(n)
//   课本用【带头结点】的写法：front 指向头结点，真正的队头元素是 front->next
typedef struct
{
    QNode *front;    // 队头（指向头结点）
    QNode *rear;     // 队尾（指向最后一个元素）
} LinkQueue;


// ==================== 栈（翻转队列要用，你题2已经写过）====================

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


// ==================== 你写的函数 ====================

// ① 初始化：建一个空队列（带头结点）
//
//   1. Q.front = Q.rear = (QNode *)malloc(sizeof(QNode));   ← 头结点，不存数据
//   2. Q.front->next = NULL;
//
// ★ 空队列的判定是 front == rear（不是 front == NULL）
void InitQueue(LinkQueue &Q)
{
    // TODO
}

// ② 入队：把 e 放到队尾
//
//   1. 造新结点 q，q->data = e，q->next = NULL
//   2. Q.rear->next = q;      ← 挂到队尾后面
//   3. Q.rear = q;            ← 队尾指针后移
//
// ★ 入队只动 rear，不动 front —— 这是 O(1) 的关键
void EnQueue(LinkQueue &Q, ElemType e)
{
    // TODO
}

// ③ 出队：把队头元素取出来，通过引用 e 带出去
//
//   1. 判空：if (Q.front == Q.rear) return false;        ← ★ 空队列的判定
//   2. QNode *p = Q.front->next;      ← 真正的队头元素（跳过表头）
//   3. e = p->data;
//   4. Q.front->next = p->next;       ← 队头后移
//   5. ★★ 特殊情况：如果 p 就是队尾（队列里只剩一个元素），
//          Q.rear 现在指向一块马上要 free 的内存 —— 必须退回头结点：
//          if (Q.rear == p) Q.rear = Q.front;
//   6. free(p);  return true;
bool DeQueue(LinkQueue &Q, ElemType &e)
{
    // TODO
    return false;
}

// ④ 翻转队列：把队列里的元素顺序倒过来
//
// ★ 思路：队列是先进先出，栈是后进先出 —— 用栈做中转，顺序就反了
//
//   1. SNode *S = NULL;                       ← 空栈
//   2. while (Q.front != Q.rear) {            ← 队列非空
//          DeQueue(Q, e);  Push(S, e);        ← 全部搬进栈
//      }
//   3. while (S != NULL) {                    ← 栈非空
//          Pop(S, e);  EnQueue(Q, e);         ← 再全部搬回队列
//      }
//
// ★ 为什么这样能翻转：出队顺序 = a,b,c；入栈后栈顶是 c；
//   出栈顺序 = c,b,a；再入队 → 队列变成 c,b,a。反了 ✅
void ReverseQueue(LinkQueue &Q)
{
    // TODO
}


// ==================== 下面不用改 ====================

void DispQueue(LinkQueue Q)
{
    printf("队头 → ");
    for (QNode *p = Q.front->next; p != NULL; p = p->next)
        printf("%d ", p->data);
    printf("← 队尾\n");
}

int main()
{
    srand((unsigned)time(NULL));

    LinkQueue Q;
    InitQueue(Q);

    // ---------- (1) 入队 10 个 ----------
    printf("--- 入队 ---\n");
    for (int i = 0; i < 10; i++)
    {
        ElemType e = rand() % 900 + 100;
        EnQueue(Q, e);
        printf("入队 %d\n", e);
    }

    // ---------- (2) 遍历输出 ----------
    printf("\n--- 遍历（先进先出，顺序和入队一致）---\n");
    DispQueue(Q);

    // ---------- (3) 翻转 ----------
    printf("\n--- 翻转 ---\n");
    printf("翻转前："); DispQueue(Q);
    ReverseQueue(Q);
    printf("翻转后："); DispQueue(Q);

    printf("\n--- 出队（顺序应该和入队【相反】）---\n");
    ElemType e;
    while (Q.front != Q.rear)
        if (DeQueue(Q, e)) printf("出队 %d\n", e);
    printf("队列已空\n");

    // ---------- 空队列再出队 ----------
    printf("\n--- 空队列出队（应该失败）---\n");
    if (DeQueue(Q, e)) printf("居然成功了？不对\n");
    else printf("出队失败 ✅ 对了，空队列不能出队\n");

    return 0;
}

// ==================== 期望输出 ====================
// --- 入队 ---
// 入队 834
// 入队 217
// ...（10 行）
//
// --- 遍历（先进先出，顺序和入队一致）---
// 队头 → 834 217 596 143 782 405 961 328 674 509 ← 队尾
//
// --- 翻转 ---
// 翻转前：队头 → 834 217 596 143 782 405 961 328 674 509 ← 队尾
// 翻转后：队头 → 509 674 328 961 405 782 143 596 217 834 ← 队尾
//
// --- 出队（顺序应该和入队【相反】）---
// 出队 509
// 出队 674
// ...（和入队顺序正好反过来）
// 队列已空
//
// --- 空队列出队（应该失败）---
// 出队失败 ✅ 对了，空队列不能出队
