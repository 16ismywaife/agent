// 第 3 步：非递归遍历（用数组栈代替"函数调用栈"）
//
// 思路一句话：递归遍历时，系统偷偷帮你压栈弹栈；
//             非递归就是把那个栈自己写出来，手动压、手动弹。

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MaxSize 50
typedef char ElemType;

typedef struct BTNode
{
    ElemType data;
    struct BTNode *lchild;
    struct BTNode *rchild;
} BTNode;

BTNode *NewNode(char ch)
{
    BTNode *p = (BTNode *)malloc(sizeof(BTNode));
    p->data = ch;
    p->lchild = NULL;
    p->rchild = NULL;
    return p;
}

// ==================== 递归版（对照用）====================

void PreOrderR(BTNode *b, char *buf, int &n)
{
    if (b != NULL) {
        buf[n++] = b->data;
        PreOrderR(b->lchild, buf, n);
        PreOrderR(b->rchild, buf, n);
    }
}

void InOrderR(BTNode *b, char *buf, int &n)
{
    if (b != NULL) {
        InOrderR(b->lchild, buf, n);
        buf[n++] = b->data;
        InOrderR(b->rchild, buf, n);
    }
}

void PostOrderR(BTNode *b, char *buf, int &n)
{
    if (b != NULL) {
        PostOrderR(b->lchild, buf, n);
        PostOrderR(b->rchild, buf, n);
        buf[n++] = b->data;
    }
}

// ==================== 非递归版 ====================

// 先序：根入栈 → 弹一个、打印一个 → 右孩子先入、左孩子后入
// （右先入，左就会先出，于是"左优先"处理，符合先序）
void PreOrderNR(BTNode *b, char *buf, int &n)
{
    BTNode *St[MaxSize], *p;
    int top = -1;
    if (b == NULL) return;

    St[++top] = b;
    while (top > -1) {
        p = St[top--];              // 弹栈
        buf[n++] = p->data;         // 打印
        if (p->rchild != NULL) St[++top] = p->rchild;   // 右先入
        if (p->lchild != NULL) St[++top] = p->lchild;   // 左后入（先出）
    }
}

// 中序：一路向左全部入栈 → 弹一个、打印、转它的右子树 → 重复
void InOrderNR(BTNode *b, char *buf, int &n)
{
    BTNode *St[MaxSize], *p = b;
    int top = -1;

    while (top > -1 || p != NULL) {
        while (p != NULL) {         // 一路向左，全部压栈
            St[++top] = p;
            p = p->lchild;
        }
        if (top > -1) {
            p = St[top--];          // 左边到底了，弹出来
            buf[n++] = p->data;     // 打印
            p = p->rchild;          // 转到右子树
        }
    }
}

// 后序：用两个栈。第一个栈按"根右左"弹出，存进第二个栈，
//       最后第二个栈倒着输出，就成了"左右根"
void PostOrderNR(BTNode *b, char *buf, int &n)
{
    BTNode *S1[MaxSize], *S2[MaxSize], *p;
    int t1 = -1, t2 = -1;
    if (b == NULL) return;

    S1[++t1] = b;
    while (t1 > -1) {
        p = S1[t1--];
        S2[++t2] = p;                                   // 先存进第二个栈
        if (p->lchild != NULL) S1[++t1] = p->lchild;    // 左先入
        if (p->rchild != NULL) S1[++t1] = p->rchild;    // 右后入（先出）
    }
    while (t2 > -1) {
        p = S2[t2--];
        buf[n++] = p->data;
    }
}

// ==================== main ====================

int main()
{
    system("chcp 65001 > nul");

    BTNode *A = NewNode('A');
    BTNode *B = NewNode('B');
    BTNode *C = NewNode('C');
    BTNode *D = NewNode('D');
    BTNode *E = NewNode('E');
    BTNode *F = NewNode('F');
    BTNode *G = NewNode('G');
    BTNode *H = NewNode('H');
    BTNode *I = NewNode('I');
    BTNode *J = NewNode('J');
    BTNode *K = NewNode('K');
    BTNode *L = NewNode('L');
    BTNode *M = NewNode('M');
    BTNode *N = NewNode('N');

    A->lchild = B;   A->rchild = C;
    B->lchild = D;   B->rchild = E;
    C->lchild = F;   C->rchild = G;
    E->lchild = H;
    G->rchild = I;
    H->lchild = J;   H->rchild = K;
    K->lchild = L;   K->rchild = M;
    M->rchild = N;

    char r1[64], r2[64], r3[64];
    char n1[64], n2[64], n3[64];
    int a = 0, b2 = 0, c = 0, d = 0, e = 0, f = 0;

    PreOrderR(A, r1, a);    r1[a] = '\0';
    InOrderR(A, r2, b2);    r2[b2] = '\0';
    PostOrderR(A, r3, c);   r3[c] = '\0';

    PreOrderNR(A, n1, d);   n1[d] = '\0';
    InOrderNR(A, n2, e);    n2[e] = '\0';
    PostOrderNR(A, n3, f);  n3[f] = '\0';

    printf("先序  递归: %s\n", r1);
    printf("先序  非递归: %s   %s\n", n1, strcmp(r1, n1) == 0 ? "一致" : "不一致");
    printf("\n");
    printf("中序  递归: %s\n", r2);
    printf("中序  非递归: %s   %s\n", n2, strcmp(r2, n2) == 0 ? "一致" : "不一致");
    printf("\n");
    printf("后序  递归: %s\n", r3);
    printf("后序  非递归: %s   %s\n", n3, strcmp(r3, n3) == 0 ? "一致" : "不一致");

    return 0;
}
