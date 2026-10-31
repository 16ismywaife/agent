// 实验3 队列的链式存储结构的实现

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

typedef struct qnode
{
    ElemType data;
    struct qnode *next;
} QNode;

typedef struct
{
    QNode *front;
    QNode *rear;
} LinkQueue;

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

void InitQueue(LinkQueue &Q)
{
    Q.front=Q.rear=(QNode*)malloc(sizeof(QNode));
    Q.front->next=NULL;
}

void EnQueue(LinkQueue &Q, ElemType e)
{
    QNode *q=(QNode*)malloc(sizeof(QNode));
    q->data=e;
    q->next=NULL;
    Q.rear->next=q;
    Q.rear=q;
}

bool DeQueue(LinkQueue &Q, ElemType &e)
{
    if(Q.front==Q.rear) return false;
    QNode *p=Q.front->next;
    e=p->data;
    Q.front->next=p->next;
    if(Q.rear==p) Q.rear=Q.front;
    free(p);
    return true;
}

void ReverseQueue(LinkQueue &Q)
{
    SNode *S=NULL;
    ElemType e;
    while(Q.front!=Q.rear){
        DeQueue(Q,e);
        Push(S,e);
    }
    while(S!=NULL){
        Pop(S,e);
        EnQueue(Q,e);
    }
}

void DispQueue(LinkQueue Q)
{
    printf("队头 → ");
    for (QNode *p = Q.front->next; p != NULL; p = p->next)
        printf("%d ", p->data);
    printf("← 队尾\n");
}

int main()
{
    system("chcp 65001 > nul");
    srand((unsigned)time(NULL));

    LinkQueue Q;
    InitQueue(Q);

    printf("--- 入队 ---\n");
    for (int i = 0; i < 10; i++)
    {
        ElemType e = rand() % 900 + 100;
        EnQueue(Q, e);
        printf("入队 %d\n", e);
    }

    printf("\n--- 遍历（先进先出，顺序和入队一致）---\n");
    DispQueue(Q);

    printf("\n--- 翻转 ---\n");
    printf("翻转前："); DispQueue(Q);
    ReverseQueue(Q);
    printf("翻转后："); DispQueue(Q);

    printf("\n--- 出队（顺序应该和入队【相反】）---\n");
    ElemType e;
    while (Q.front != Q.rear)
        if (DeQueue(Q, e)) printf("出队 %d\n", e);
    printf("队列已空\n");

    printf("\n--- 空队列出队（应该失败）---\n");
    if (DeQueue(Q, e)) printf("插入成功（位置越界，不应成功）\n");
    else printf("出队失败：队列为空\n");

    return 0;
}
