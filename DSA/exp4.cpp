// 实验4 线性表、栈和队列的应用实现

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int ElemType;

typedef struct LNode
{
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;

void CreateList(LinkList &L, int n)
{
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL;
    LNode *tail = L;
    for (int i = 0; i < n; i++)
    {
        LNode *q = (LinkList)malloc(sizeof(LNode));
        q->data = rand() % 900 + 100;
        q->next = NULL;
        tail->next = q;
        tail = q;
    }
}

void DispList(LinkList L)
{
    for (LNode *p = L->next; p != NULL; p = p->next)
        printf("%d ", p->data);
    printf("\n");
}

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

void PartitionList(LinkList &L, ElemType pivot)
{
    LNode smallhead,bighead;
    LNode *tailsmall=&smallhead,*tailbig=&bighead;
    smallhead.next=NULL;
    bighead.next=NULL;
    for(LNode *p=L->next;p!=NULL;){
        LNode *pnext=p->next;
        if(p->data<pivot){
            tailsmall->next=p;
            tailsmall=p;
        }else{
            tailbig->next=p;
            tailbig=p;
        }
        p=pnext;
    }
    tailsmall->next=bighead.next;
    tailbig->next=NULL;
    L->next=smallhead.next;
}

bool IsMatch(char left, char right)
{
    return (left == '(' && right == ')') ||
           (left == '[' && right == ']') ||
           (left == '{' && right == '}');
}

bool BracketMatch(const char *s)
{
    SNode *S=NULL;
    for(int i=0;s[i]!='\0';i++){
        char c=s[i];
        if(c=='('||c=='['||c=='{'){
            Push(S,c);
        }else if(c==')'||c==']'||c=='}'){
            ElemType top;
            if(!Pop(S,top)) return false;
            if(!IsMatch(top,c)) return false;
        }

    }
    return S==NULL;
}

int main()
{
    system("chcp 65001 > nul");
    srand((unsigned)time(NULL));

    printf("=== (1) 按基准值分割单链表 ===\n");
    LinkList L = NULL;
    CreateList(L, 10);
    printf("原链表：");
    DispList(L);

    ElemType pivot = L->next->data;
    printf("基准值：%d\n", pivot);

    PartitionList(L, pivot);
    printf("分割后（左边全 < %d，右边全 >= %d）：\n        ", pivot, pivot);
    DispList(L);

    printf("\n=== (2) 括号匹配 ===\n");
    const char *tests[] = {
        "(a[b]{c})",
        "{[()]}",
        "([)]",
        "(((",
        ")( ",
        "x=1+(2*[3-4])",
        "hello world",
        NULL
    };
    for (int i = 0; tests[i] != NULL; i++)
        printf("  %-16s → %s\n", tests[i],
               BracketMatch(tests[i]) ? "合法" : "不合法");

    return 0;
}
