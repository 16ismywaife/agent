// 第 6 步：中序线索二叉树（实验2 题3）
//
// 一句话：把每个结点【空着的】左指针改指"中序前驱"、空着的右指针改指"中序后继"，
//         这样不用栈、不用递归也能顺着线索走完一遍。
//
// 为了区分"这个指针是真的孩子，还是被我改成线索了"，每个结点加两个标记：
//   ltag = 0 → lchild 是左孩子   ltag = 1 → lchild 是前驱线索
//   rtag = 0 → rchild 是右孩子   rtag = 1 → rchild 是后继线索

#include <stdio.h>
#include <stdlib.h>

typedef char ElemType;

typedef struct TBTNode
{
    ElemType data;
    int ltag, rtag;
    struct TBTNode *lchild;
    struct TBTNode *rchild;
} TBTNode;

TBTNode *pre = NULL;    // 全局：指向"刚访问过的那个结点"

TBTNode *NewNode(char ch)
{
    TBTNode *p = (TBTNode *)malloc(sizeof(TBTNode));
    p->data = ch;
    p->ltag = 0;
    p->rtag = 0;
    p->lchild = NULL;
    p->rchild = NULL;
    return p;
}

// ==================== 中序线索化（递归）====================

void Thread(TBTNode *&p)
{
    if (p != NULL) {
        Thread(p->lchild);              // ① 先处理左子树

        if (p->lchild == NULL) {        // ② 左空 → 改指前驱
            p->lchild = pre;
            p->ltag = 1;
        } else {
            p->ltag = 0;
        }

        if (pre->rchild == NULL) {      // ③ 上一个结点右空 → 改指后继（我）
            pre->rchild = p;
            pre->rtag = 1;
        } else {
            pre->rtag = 0;
        }

        pre = p;                        // ④ 我变成"上一个"
        Thread(p->rchild);              // ⑤ 再处理右子树
    }
}

// 建头结点，把线索串成一个环
TBTNode *CreateThread(TBTNode *b)
{
    TBTNode *root = (TBTNode *)malloc(sizeof(TBTNode));
    root->data = '#';                   // 头结点不是真结点，data 没意义，给个标记方便辨认
    root->ltag = 0;
    root->rtag = 1;
    root->rchild = b;

    if (b == NULL) {
        root->lchild = root;
    } else {
        root->lchild = b;
        pre = root;                     // 第一个结点的前驱指向头结点
        Thread(b);
        pre->rchild = root;             // 最后一个结点的后继指向头结点
        pre->rtag = 1;
        root->rchild = pre;             // 头结点的右指针指向最后一个结点
    }
    return root;
}

// ==================== 靠线索遍历（不用栈不用递归）====================

void ThInOrder(TBTNode *tb)
{
    TBTNode *p = tb->lchild;            // 从头结点的左孩子（即根）开始

    while (p != tb) {
        while (p->ltag == 0) p = p->lchild;     // 一路向左，找到中序第一个

        printf("%c ", p->data);

        while (p->rtag == 1 && p->rchild != tb) {   // 顺着后继线索一路走
            p = p->rchild;
            printf("%c ", p->data);
        }
        p = p->rchild;                          // 有右孩子，转进去
    }
}

// ==================== 求前驱 / 后继 ====================

TBTNode *PreNode(TBTNode *p)
{
    TBTNode *q = p->lchild;

    if (p->ltag == 1) return q;         // 直接就是线索，前驱就是它

    // 有左孩子：前驱 = 左子树里"最右下"的那个
    while (q->rtag == 0) q = q->rchild;
    return q;
}

TBTNode *PostNode(TBTNode *p)
{
    TBTNode *q = p->rchild;

    if (p->rtag == 1) return q;         // 直接就是线索，后继就是它

    // 有右孩子：后继 = 右子树里"最左下"的那个
    while (q->ltag == 0) q = q->lchild;
    return q;
}

// ==================== main ====================

int main()
{
    system("chcp 65001 > nul");

    TBTNode *A = NewNode('A');
    TBTNode *B = NewNode('B');
    TBTNode *C = NewNode('C');
    TBTNode *D = NewNode('D');
    TBTNode *E = NewNode('E');
    TBTNode *F = NewNode('F');
    TBTNode *G = NewNode('G');
    TBTNode *H = NewNode('H');
    TBTNode *I = NewNode('I');
    TBTNode *J = NewNode('J');
    TBTNode *K = NewNode('K');
    TBTNode *L = NewNode('L');
    TBTNode *M = NewNode('M');
    TBTNode *N = NewNode('N');

    A->lchild = B;   A->rchild = C;
    B->lchild = D;   B->rchild = E;
    C->lchild = F;   C->rchild = G;
    E->lchild = H;
    G->rchild = I;
    H->lchild = J;   H->rchild = K;
    K->lchild = L;   K->rchild = M;
    M->rchild = N;

    // 线索化
    TBTNode *tb = CreateThread(A);

    // 靠线索遍历一遍（结果应该跟中序完全一样）
    printf("中序线索遍历: ");
    ThInOrder(tb);
    printf("\n\n");

    // 题目要求：找【根结点】的前驱和后继
    TBTNode *root = A;
    TBTNode *p1 = PreNode(root);
    TBTNode *p2 = PostNode(root);

    printf("根结点 %c 的前驱: %c\n", root->data, p1->data);
    printf("根结点 %c 的后继: %c\n", root->data, p2->data);
    printf("\n");

    // 再看看几个叶子（它们的左右都是线索，最容易验证）
    printf("几个叶子的线索:\n");
    printf("  %c 的前驱是 %c，后继是 %c\n", D->data, PreNode(D)->data, PostNode(D)->data);
    printf("  %c 的前驱是 %c，后继是 %c\n", N->data, PreNode(N)->data, PostNode(N)->data);
    printf("  %c 的前驱是 %c，后继是 %c\n", I->data, PreNode(I)->data, PostNode(I)->data);

    return 0;
}
