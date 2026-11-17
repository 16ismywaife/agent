// 第 4 步：广义表字符串建树（实验2 题1 的最后一块）
//
// 思路：字符串里有四种字符，各有一个意思
//   '('  刚才那个结点有孩子了 → 把它记到栈里
//   ','  左孩子处理完了，接下来是右孩子
//   ')'  这个结点的孩子全处理完了 → 从栈里去掉
//  字母  造一个结点，按 k 挂成栈顶结点的左孩子或右孩子
//
// 栈里存的是"还没处理完孩子的结点"，跟上一题非递归遍历里的栈是一样的作用。

#include <stdio.h>
#include <stdlib.h>

#define MaxSize 50
typedef char ElemType;

typedef struct BTNode
{
    ElemType data;
    struct BTNode *lchild;
    struct BTNode *rchild;
} BTNode;

// ==================== 广义表建树 ====================

void CreateBTree(BTNode *&b, char *str)
{
    BTNode *St[MaxSize], *p = NULL;
    int top = -1;
    int k = 0;          // k=1 表示下一个结点做左孩子，k=2 表示做右孩子
    int j = 0;
    char ch;

    b = NULL;           // 一开始是空树
    ch = str[j];

    while (ch != '\0') {
        switch (ch) {
        case '(':                       // 开始处理孩子
            top++;
            St[top] = p;                // 把刚才那个结点压栈
            k = 1;                      // 先做左孩子
            break;

        case ')':                       // 这个结点的孩子处理完了
            top--;                      // 弹栈
            break;

        case ',':                       // 左孩子完了，转右孩子
            k = 2;
            break;

        default:                        // 遇到字母
            p = (BTNode *)malloc(sizeof(BTNode));
            p->data = ch;
            p->lchild = NULL;
            p->rchild = NULL;

            if (b == NULL) {
                b = p;                  // 第一个字母就是根
            } else if (k == 1) {
                St[top]->lchild = p;    // 挂成栈顶结点的左孩子
            } else {
                St[top]->rchild = p;    // 挂成右孩子
            }
        }
        j++;
        ch = str[j];
    }
}

// ==================== 基本的递归算法 ====================

void InOrder(BTNode *b)
{
    if (b != NULL) {
        InOrder(b->lchild);
        printf("%c ", b->data);
        InOrder(b->rchild);
    }
}

int NodeCount(BTNode *b)
{
    if (b == NULL) return 0;
    return NodeCount(b->lchild) + NodeCount(b->rchild) + 1;
}

int LeafCount(BTNode *b)
{
    if (b == NULL) return 0;
    if (b->lchild == NULL && b->rchild == NULL) return 1;
    return LeafCount(b->lchild) + LeafCount(b->rchild);
}

int Height(BTNode *b)
{
    if (b == NULL) return 0;
    int l = Height(b->lchild);
    int r = Height(b->rchild);
    return (l > r ? l : r) + 1;
}

int NodeDegree(BTNode *b)
{
    int d = 0;
    if (b->lchild != NULL) d++;
    if (b->rchild != NULL) d++;
    return d;
}

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

BTNode *FindNode(BTNode *b, char ch)
{
    if (b == NULL) return NULL;
    if (b->data == ch) return b;
    BTNode *p = FindNode(b->lchild, ch);
    if (p != NULL) return p;
    return FindNode(b->rchild, ch);
}

// ==================== main ====================

int main()
{
    system("chcp 65001 > nul");

    BTNode *b;
    char str[] = "A(B(D,E(H(J,K(L,M(,N))))),C(F,G(,I)))";

    CreateBTree(b, str);

    printf("用广义表建树: %s\n\n", str);

    printf("中序遍历: ");
    InOrder(b);
    printf("\n\n");

    printf("结点个数: %d\n", NodeCount(b));
    printf("叶子个数: %d\n", LeafCount(b));
    printf("树的度  : %d\n", TreeDegree(b));
    printf("高度    : %d\n\n", Height(b));

    BTNode *h = FindNode(b, 'H');
    printf("H 的左孩子: %c\n", h->lchild->data);
    printf("H 的右孩子: %c\n", h->rchild->data);

    return 0;
}
