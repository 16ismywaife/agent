// 第 1 步：二叉链表 + 三种递归遍历
//
// 要建的树（用块注释画，因为 // 注释里行尾不能是反斜杠）：
/*
          A
        /   \
       B     C
      / \     \
     D   E     F
*/
// 先序：A B D E C F
// 中序：D B E A C F
// 后序：D E B F C A

#include <stdio.h>
#include <stdlib.h>

typedef char ElemType;

typedef struct BTNode
{
    ElemType data;
    struct BTNode *lchild;
    struct BTNode *rchild;
} BTNode;

// 造一个孤立的结点：左右孩子都是空的
BTNode *NewNode(char ch)
{
    BTNode *p = (BTNode *)malloc(sizeof(BTNode));
    p->data = ch;
    p->lchild = NULL;
    p->rchild = NULL;
    return p;
}

// 先序：自己 → 左 → 右
void PreOrder(BTNode *b)
{
    if (b != NULL) {
        printf("%c ", b->data);
        PreOrder(b->lchild);
        PreOrder(b->rchild);
    }
}

// 中序：左 → 自己 → 右
void InOrder(BTNode *b)
{
    if (b != NULL) {
        InOrder(b->lchild);
        printf("%c ", b->data);
        InOrder(b->rchild);
    }
}

// 后序：左 → 右 → 自己
void PostOrder(BTNode *b)
{
    if (b != NULL) {
        PostOrder(b->lchild);
        PostOrder(b->rchild);
        printf("%c ", b->data);
    }
}

int main()
{
    system("chcp 65001 > nul");

    BTNode *A = NewNode('A');
    BTNode *B = NewNode('B');
    BTNode *C = NewNode('C');
    BTNode *D = NewNode('D');
    BTNode *E = NewNode('E');
    BTNode *F = NewNode('F');

    A->lchild = B;  A->rchild = C;
    B->lchild = D;  B->rchild = E;
    C->lchild = NULL;  C->rchild = F;

    printf("先序遍历: ");
    PreOrder(A);
    printf("\n");

    printf("中序遍历: ");
    InOrder(A);
    printf("\n");

    printf("后序遍历: ");
    PostOrder(A);
    printf("\n");

    return 0;
}
