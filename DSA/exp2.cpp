// 实验报告1 · 题2：栈的链式存储结构（入栈、出栈）
//
// ★ 老师要求：在【入栈】和【出栈】接口处各设一个断点，
//   按 F5 启动调试，F10 逐句执行，观察栈顶数据和栈顶位置，各截一张图。
//
// 调试步骤见 dsa/实验报告1_指导.md 第三节，或直接：
//   1. 在第 41 行（入栈函数第一行）行号左边点一下 → 红点（断点①）
//   2. 按 F5 → 自动复制到 C:\cppbuild\current.cpp 并编译启动
//   3. 按 F10 单步，左侧"变量"里看 S（栈顶指针）和 S->data（栈顶元素）
//   4. Win + Shift + S 截图

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

// ★ 链栈：栈顶就是链表的【第一个结点】（头插法入栈）
typedef struct linknode
{
    ElemType data;
    struct linknode *next;
} LiNode, *LiStack;


// ==================== 你写的两个函数 ====================

// ① 入栈：把 e 压到栈顶
//
// 链栈的入栈 = 单链表的【头插】：
//   1. 造一个新结点 q
//   2. q->data = e
//   3. q->next = S      ← 新结点指向原来的栈顶
//   4. S = q            ← 栈顶指针移到新结点
//
// ★ 为什么不用头结点：栈只需要"栈顶在哪"，不需要遍历，所以 S 直接指向第一个数据结点
void Push(LiStack &S, ElemType e)
{
    // TODO
}

// ② 出栈：把栈顶元素取出来，通过引用 e 带出去
//
//   1. 判空：if (S == NULL) return false;
//   2. e = S->data;        ← 先取值
//   3. LiNode *p = S;      ← 记住要删的结点
//   4. S = S->next;        ← 栈顶下移
//   5. free(p);            ← 释放
//   6. return true;
bool Pop(LiStack &S, ElemType &e)
{
    // TODO
    return false;
}


// ==================== 下面不用改 ====================

// 从栈顶往下打印（顺序和出栈顺序一样）
void DispStack(LiStack S)
{
    printf("栈顶 → ");
    for (LiNode *p = S; p != NULL; p = p->next)
        printf("%d ", p->data);
    printf("← 栈底\n");
}

int main()
{
    srand((unsigned)time(NULL));

    LiStack S = NULL;      // 空栈

    // ---------- 入栈：10 个三位整数 ----------
    printf("--- 入栈 ---\n");
    for (int i = 0; i < 10; i++)
    {
        ElemType e = rand() % 900 + 100;
        Push(S, e);                       // ← 断点①设在这个函数的【第一行】
        printf("入栈 %d，当前栈顶 = %d\n", e, S->data);
    }
    printf("\n");
    DispStack(S);

    // ---------- 出栈：全部弹出 ----------
    printf("\n--- 出栈 ---\n");
    ElemType e;
    while (S != NULL)
    {
        if (Pop(S, e))                    // ← 断点②设在这个函数的【第一行】
            printf("出栈 %d，", e);
        if (S != NULL) printf("当前栈顶 = %d\n", S->data);
        else           printf("栈已空\n");
    }

    // ---------- 空栈再弹一次 ----------
    printf("\n--- 空栈出栈（应该失败）---\n");
    if (Pop(S, e)) printf("居然成功了？不对\n");
    else printf("出栈失败 ✅ 对了，空栈不能弹\n");

    return 0;
}

// ==================== 期望输出 ====================
// --- 入栈 ---
// 入栈 834，当前栈顶 = 834
// 入栈 217，当前栈顶 = 217
// ...（10 行，栈顶每次都是最后入栈的那个）
// 栈顶 → 509 674 328 961 405 782 143 596 217 834 ← 栈底
//
// --- 出栈 ---
// 出栈 509，当前栈顶 = 674
// 出栈 674，当前栈顶 = 328
// ...（顺序和入栈【完全相反】—— 这就是"后进先出"）
// 出栈 834，栈已空
//
// --- 空栈出栈（应该失败）---
// 出栈失败 ✅ 对了，空栈不能弹
