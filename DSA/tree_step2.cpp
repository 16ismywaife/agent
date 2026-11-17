// 第 2 步：用一个递归模板，算出结点的四种统计量
//
// 用的是实验2 题目里那棵树：A(B(D,E(H(J,K(L,M(,N))))),C(F,G(,I)))
/*
            A
          /   \
         B     C
        / \   / \
       D   E F   G
          /       \
         H         I
        / \
       J   K
          / \
         L   M
              \
               N
*/
// 正确答案：结点 14，叶子 6，度 2，高度 7，H 的左右孩子是 J 和 K

#include <stdio.h>
#include <stdlib.h>

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

// ---------- 递归统计 ----------

// 结点个数 = 左子树 + 右子树 + 自己这 1 个
int NodeCount(BTNode *b)
{
    if (b == NULL) return 0;
    return NodeCount(b->lchild) + NodeCount(b->rchild) + 1;
}

// 叶子个数：自己是叶子就算 1，否则看左右子树
int LeafCount(BTNode *b)
{
    if (b == NULL) return 0;
    if (b->lchild == NULL && b->rchild == NULL) return 1;
    return LeafCount(b->lchild) + LeafCount(b->rchild);
}

// 高度 = 左右里高的那个 + 1
int Height(BTNode *b)
{
    if (b == NULL) return 0;
    int l = Height(b->lchild);
    int r = Height(b->rchild);
    return (l > r ? l : r) + 1;
}

// 单个结点自己的度（有几个孩子）
int NodeDegree(BTNode *b)
{
    int d = 0;
    if (b->lchild != NULL) d++;
    if (b->rchild != NULL) d++;
    return d;
}

// 整棵树的度 = 所有结点度里的最大值
int TreeDegree(BTNode *b)
{
    if (b == NULL) return 0;
    int m = NodeDegree(b);
    int l = TreeDegree(b->lchild);
    int r = TreeDegree(b->rchild);
    if (l > m) m = l;
    if (r > m) m = r;
    return m;
}

// 按值找结点
BTNode *FindNode(BTNode *b, char ch)
{
    if (b == NULL) return NULL;
    if (b->data == ch) return b;
    BTNode *p = FindNode(b->lchild, ch);
    if (p != NULL) return p;
    return FindNode(b->rchild, ch);
}

// ---------- 遍历（第 1 步已经写过）----------

void PreOrder(BTNode *b)
{
    if (b != NULL) {
        printf("%c ", b->data);
        PreOrder(b->lchild);
        PreOrder(b->rchild);
    }
}

void InOrder(BTNode *b)
{
    if (b != NULL) {
        InOrder(b->lchild);
        printf("%c ", b->data);
        InOrder(b->rchild);
    }
}

int main()
{
    system("chcp 65001 > nul");

    // 14 个结点，一个个造
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

    printf("先序遍历: ");
    PreOrder(A);
    printf("\n");

    printf("中序遍历: ");
    InOrder(A);
    printf("\n\n");

    printf("结点个数: %d\n", NodeCount(A));
    printf("叶子个数: %d\n", LeafCount(A));
    printf("树的度  : %d\n", TreeDegree(A));
    printf("高度    : %d\n", Height(A));
    printf("\n");

    BTNode *h = FindNode(A, 'H');
    if (h != NULL) {
        printf("H 的左孩子: %c\n", h->lchild->data);
        printf("H 的右孩子: %c\n", h->rchild->data);
    }

    return 0;
}
