// 实验2 栈的链式存储结构实现

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

typedef struct linknode
{
    ElemType data;
    struct linknode *next;
} LiNode, *LiStack;

void Push(LiStack &S, ElemType e)
{
    LiStack q=(LiStack)malloc(sizeof(LiNode));
    q->data=e;
    q->next=S;
    S=q;
}

bool Pop(LiStack &S, ElemType &e)
{
    if(S==NULL)return false;
    e=S->data;
    LiStack p=S;
    S=S->next;
    free(p);
    return true;
}

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

    LiStack S = NULL;

    printf("--- 入栈 ---\n");
    for (int i = 0; i < 10; i++)
    {
        ElemType e = rand() % 900 + 100;
        Push(S, e);
        printf("入栈 %d，当前栈顶 = %d\n", e, S->data);
    }
    printf("\n");
    DispStack(S);

    printf("\n--- 出栈 ---\n");
    ElemType e;
    while (S != NULL)
    {
        if (Pop(S, e))
            printf("出栈 %d，", e);
        if (S != NULL) printf("当前栈顶 = %d\n", S->data);
        else           printf("栈已空\n");
    }

    printf("\n--- 空栈出栈（应该失败）---\n");
    if (Pop(S, e)) printf("插入成功（位置越界，不应成功）\n");
    else printf("出栈失败：栈为空\n");

    return 0;
}
