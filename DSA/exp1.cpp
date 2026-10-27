// 实验报告1 · 题1：单链表的 7 小问
//
// ★ 规则：结构定义和 main 我写好了（课本写法），标 TODO 的函数体你自己填。
//
// 编译：Ctrl+Shift+B      运行：& "$env:TEMP\exp1.exe"
//
// ────────────────────────────────────────────────────────────
// 第 1 步（今天从这里开始）：建表 + 输出
//   (1) 用随机函数生成 10 个【不同】的 3 位整数（100~999），存进链表
//   (2) 输出链表内容
// ────────────────────────────────────────────────────────────

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

typedef struct LNode
{
    ElemType data;       // 存数据
    struct LNode *next;  // 指向下一个结点
} LNode, *LinkList;      // LinkList 就是 LNode*（指向结点的指针）


// ==================== 第 1 步：你写的两个函数 ====================

// ① 建表（尾插法）：生成 n 个【不同的】3 位整数
//
// 要做的事：
//   1. 先建一个【头结点】（它不存数据，只是让后面的操作不用特判空表）
//        L = (LinkList)malloc(sizeof(LNode));
//        L->next = NULL;
//   2. 用一个变量 tail 指向当前的表尾，一开始 tail = L
//   3. 循环 n 次：
//        a. 生成一个 100~999 的数：rand() % 900 + 100
//           ★ "不同"要去重 —— 最简单：用 bool used[1000] 标记，重复就重新生成
//        b. 新结点 q = (LinkList)malloc(sizeof(LNode));  q->data = 数;  q->next = NULL;
//        c. 挂到表尾：tail->next = q;  tail = q;
//   4. 循环结束
//
// ★ 为什么用尾插：输出顺序 = 生成顺序，后面第 (3) 问输出"位置"也符合直觉。
void CreateListTail(LinkList &L, int n)
{
    L=(LinkList)malloc(sizeof(LNode));
    L->next=NULL;
    LNode *tail=L;
    bool used[1000]={false};
    for(int i=0;i<n;i++){
        int num;
        do{
            num=rand()%900+100;
        }while(used[num]);
        used[num]=true;
        LinkList q=(LinkList)malloc(sizeof(LNode));
        q->data=num;
        q->next=NULL;
        tail->next=q;
        tail=q;
    }
}

// ② 输出链表
//
// 要从【头结点的下一个】开始走（头结点不存数据）：
//   LNode *p = L->next;
//   while (p != NULL) {
//       printf("%d ", p->data);
//       p = p->next;
//   }
void DispList(LinkList L)
{
    LNode *p=L->next;
    while(p!=NULL){
        printf("%d ",p->data);
        p=p->next;
    }
}


// ==================== 第 2 步：查找 和 插入 ====================

// ③ 查找：读入一个整数，若在表中，返回它的【位置】（首位置为 1）；不在返回 0
//
// 做法：
//   LNode *p = L->next;
//   int pos = 1;                      ← ★ 位置从 1 开始，不是 0
//   while (p != NULL && p->data != e) { p = p->next; pos++; }
//   if (p != NULL) return pos;
//   return 0;                         ← 找不到返回 0（课本约定）
int LocateElem(LinkList L, ElemType e)
{
    LinkList p=L->next;
    int pos=1;
    while(p!=NULL&&p->data!=e){
        p=p->next;
        pos++;
    }
    if(p!=NULL) return pos;
    return 0;
}

// ④ 插入：把 e 插到第 i 个位置（i 是逻辑序号，合法范围 1 ~ n+1）
//
// ★ 三个要点：
//   1. 合法范围是 1 ~ n+1（插到末尾 = 第 n+1 个位置，这是合法的）
//   2. 单链表插不进去"自己前面"，所以必须先找到【第 i-1 个结点】
//   3. 先连后断：q->next = p->next;  p->next = q;   （顺序反了就丢链）
//
// 做法：
//   if (i < 1) return false;
//   LNode *p = L;                     ← 从头结点开始（i=1 时正好指向头结点）
//   int j = 0;                        ← j 表示 p 现在是第几个结点（头结点算第 0 个）
//   while (p != NULL && j < i - 1) { p = p->next; j++; }
//   if (p == NULL) return false;      ← i 太大，超出了 n+1
//   然后造结点、挂上去
bool ListInsert(LinkList &L, int i, ElemType e)
{
    
    if(i<1)return false;
    LinkList p=L;
    int j=0;
    while(p!=NULL&&j<i-1){
        p=p->next;
        j++;
    }
    if(p==NULL)return false;
    LinkList q=(LinkList)malloc(sizeof(LNode));
    q->data=e;
    q->next=p->next;
    p->next=q;
    return true;
}


// ==================== 第 3 步：删除 和 翻转 ====================

// ⑤ 删除：读入一个整数，若在链表里，删掉那个结点
//
// ★ 单链表删不了"自己" —— 必须找到【前一个结点】。
//
// 做法：
//   LNode *pre = L;              ← pre 是"前一个"，一开始是头结点
//   LNode *p = L->next;          ← p 是"当前"，从第一个数据结点开始
//   while (p != NULL && p->data != e) { pre = p; p = p->next; }
//   // 循环停下时：要么 p 找到了（p->data == e），要么 p 走到 NULL
//   if (p == NULL) return false;         ← 没找到
//   pre->next = p->next;                 ← ★ 前一个直接指向当前的后一个，跳过 p
//   free(p);                             ← ★ 一定要 free，否则内存泄漏
//   return true;
bool ListDeleteByValue(LinkList &L, ElemType e)
{
    LinkList pre=L;
    LinkList p=L->next;
    while(p!=NULL&&p->data!=e){
        pre=p;
        p=p->next;
    }
    if(p==NULL)return false;
    pre->next=p->next;
    free(p);
    return true;
}

// ⑥ 翻转：把整个链表倒过来，★ 不占用新的存储空间
//
// 三指针法（pre / p / next），核心就三行，但顺序不能错：
//
//   LNode *pre = NULL;
//   LNode *p = L->next;          ← 从第一个数据结点开始
//   while (p != NULL) {
//       LNode *next = p->next;   ← ★① 先把"下一个"存住
//        p->next = pre;          ← ★② 再让 p 反过来指
//        pre = p;                ← ★③ pre 往前挪
//        p = next;               ← ★④ p 往前挪
//   }
//   L->next = pre;               ← ★ 最后别忘：头结点指向新的第一个
//
// ★ 为什么必须先存 next：② 一旦执行，p->next 就被覆盖了，原来的下一个就找不到了
// ★ 为什么最后要 L->next = pre：循环结束时 pre 指向原表的最后一个结点，也就是新的第一个
void ReverseList(LinkList &L)
{
    LinkList p=L->next;
    L->next=NULL;
    while(p!=NULL){
        LinkList q=p->next;
        p->next=L->next;
        L->next=p;
        p=q;
    }
}


// ==================== 第 4 步：合并两个有序链表 ====================

// ⑦ 把两个【非递减】链表合并成一个【非递增】链表
//    ★ 要求：仍使用原来两个链表的存储空间，不占用其他空间；允许有重复数据
//
// 【推导一遍再写代码】：
//   从两个表里每次取【较小】的那个 → 取出来的顺序是 小 → 大
//   再把每个取出来的结点【头插】到结果表 → 后插的排前面 → 结果 大 → 小 = 非递增 ✅
//
// 做法：
//   1. 用 LA 的头结点当结果表的头：  LA->next = NULL;
//   2. 两个指针 pa = LA->next, pb = LB->next 各走各的表
//   3. while (pa != NULL && pb != NULL) 挑较小的那个 r 摘下来，头插进结果表
//   4. 剩下没走完的那条，继续一个个头插
//   5. 最后把 LB 的头结点 free 掉（它的结点都搬到 LA 那边了，只剩个空壳）
//
// ★ 注意：这里是"取较小的"，不是"取较大的" —— 因为后面还有一次头插，会把顺序倒过来
// ★ 允许重复：pa->data <= pb->data 时取 pa（相等也照取，不要跳过）
void MergeDesc(LinkList &LA, LinkList &LB)
{
    LinkList pa=LA->next;
    LinkList pb=LB->next;
    LA->next=NULL;
    LB->next=NULL;
    while(pa!=NULL&&pb!=NULL){
        LinkList p;
        if(pa->data<=pb->data){
            p=pa;
            pa=pa->next;
        }else{
            p=pb;
            pb=pb->next;
        }
        p->next=LA->next;
        LA->next=p;
    }
    while(pa!=NULL){
        LinkList p=pa;
        pa=pa->next;
        p->next=LA->next;
        LA->next=p;
    }
    while(pb!=NULL){
        LinkList p=pb;
        pb=pb->next;
        p->next=LA->next;
        LA->next=p; 
    }
    free(LB);
}


// ==================== 造有序表（这个我写好了，你不用改）====================

// 随机生成 n 个数，边生成边按【非递减】插进去
void CreateSorted(LinkList &L, int n)
{
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL;
    for (int i = 0; i < n; i++)
    {
        int x = rand() % 900 + 100;
        LNode *pre = L, *p = L->next;
        while (p != NULL && p->data < x) { pre = p; p = p->next; }
        LNode *q = (LinkList)malloc(sizeof(LNode));
        q->data = x;
        q->next = p;
        pre->next = q;
    }
}


// ==================== 下面不用改 ====================

int main()
{
    srand((unsigned)time(NULL));     // 随机种子：每跑一次数不一样

    LinkList L = NULL;
    CreateListTail(L, 10);

    printf("链表内容：");
    DispList(L);
    printf("\n");

    // ---------- 第 2 步的测试 ----------
    printf("\n--- 查找 ---\n");
    ElemType target = L->next->data;          // 第一个元素，肯定存在
    printf("查找 %d（存在）：位置 %d\n", target, LocateElem(L, target));
    printf("查找 1000（不存在）：位置 %d（0 = 没找到）\n", LocateElem(L, 1000));

    printf("\n--- 插入 ---\n");
    printf("在第 3 个位置插入 777：");
    if (ListInsert(L, 3, 777)) { DispList(L); printf("\n"); }
    else printf("位置不合理\n");

    printf("在第 1 个位置插入 111：");
    if (ListInsert(L, 1, 111)) { DispList(L); printf("\n"); }
    else printf("位置不合理\n");

    printf("在第 13 个位置插入 999（合法：n=12 时上限是 13）：");
    if (ListInsert(L, 13, 999)) { DispList(L); printf("\n"); }
    else printf("位置不合理 —— 这里其实应该成功，检查你的范围判断\n");

    printf("在第 15 个位置插入 888（越界）：");
    if (ListInsert(L, 15, 888)) printf("居然成功了？不对\n");
    else printf("位置不合理 ✅ 对了，上限是 n+1 = 14\n");

    // ---------- 第 3 步的测试 ----------
    printf("\n--- 删除 ---\n");
    printf("删除 777（存在）：");
    if (ListDeleteByValue(L, 777)) { DispList(L); printf("\n"); }
    else printf("没找到这个数\n");

    printf("删除 1000（不存在）：");
    if (ListDeleteByValue(L, 1000)) printf("居然删掉了？不对\n");
    else printf("没找到这个数 ✅ 对了（应该返回 false）\n");

    printf("\n--- 翻转 ---\n");
    printf("翻转前："); DispList(L); printf("\n");
    ReverseList(L);
    printf("翻转后："); DispList(L); printf("\n");

    // ---------- 第 4 步：合并两个有序链表 ----------
    printf("\n--- 合并（非递减 → 非递增）---\n");
    LinkList LA = NULL, LB = NULL;
    CreateSorted(LA, 4);            // 造 4 个【非递减】的数
    CreateSorted(LB, 3);            // 再造 3 个
    printf("LA（非递减）："); DispList(LA); printf("\n");
    printf("LB（非递减）："); DispList(LB); printf("\n");
    MergeDesc(LA, LB);
    printf("合并后（非递增）："); DispList(LA); printf("\n");

    return 0;
}

// ==================== 期望输出 ====================
// 链表内容：834 217 596 143 782 405 961 328 674 509
// （10 个互不相同的三位数，每次跑都不一样）
//
// --- 查找 ---
// 查找 834（存在）：位置 1
// 查找 1000（不存在）：位置 0（0 = 没找到）
//
// --- 插入 ---
// 在第 3 个位置插入 777：834 217 777 596 143 782 405 961 328 674 509
// 在第 1 个位置插入 111：111 834 217 777 596 143 782 405 961 328 674 509
// 在第 13 个位置插入 999（合法：n=12 时上限是 13）：111 834 217 777 596 143 782 405 961 328 674 509 999
// 在第 15 个位置插入 888（越界）：位置不合理 ✅ 对了，上限是 n+1 = 14


