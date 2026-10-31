// 实验1 线性表的链表实现

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int ElemType;

typedef struct LNode
{
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;

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

void DispList(LinkList L)
{
    LNode *p=L->next;
    while(p!=NULL){
        printf("%d ",p->data);
        p=p->next;
    }
}

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

int main()
{
    system("chcp 65001 > nul");
    srand((unsigned)time(NULL));

    LinkList L = NULL;
    CreateListTail(L, 10);

    printf("链表内容：");
    DispList(L);
    printf("\n");

    printf("\n--- 查找 ---\n");
    ElemType target = L->next->data;
    printf("查找 %d（存在）：位置 %d\n", target, LocateElem(L, target));
    printf("查找 1000（不存在）：位置 %d（0 = 没找到）\n", LocateElem(L, 1000));

    printf("\n--- 插入 ---\n");
    printf("在第 3 个位置插入 777：");
    if (ListInsert(L, 3, 777)) { DispList(L); printf("\n"); }
    else printf("插入失败：位置越界\n");

    printf("在第 1 个位置插入 111：");
    if (ListInsert(L, 1, 111)) { DispList(L); printf("\n"); }
    else printf("插入失败：位置越界\n");

    printf("在第 13 个位置插入 999（合法：n=12 时上限是 13）：");
    if (ListInsert(L, 13, 999)) { DispList(L); printf("\n"); }
    else printf("位置不合理 —— 这里其实应该成功，检查你的范围判断\n");

    printf("在第 15 个位置插入 888（越界）：");
    if (ListInsert(L, 15, 888)) printf("插入成功（位置越界，不应成功）\n");
    else printf("插入失败：位置越界\n");

    printf("\n--- 删除 ---\n");
    printf("删除 777（存在）：");
    if (ListDeleteByValue(L, 777)) { DispList(L); printf("\n"); }
    else printf("没找到这个数\n");

    printf("删除 1000（不存在）：");
    if (ListDeleteByValue(L, 1000)) printf("删除成功（值不存在，不应成功）\n");
    else printf("删除失败：未找到\n");

    printf("\n--- 翻转 ---\n");
    printf("翻转前："); DispList(L); printf("\n");
    ReverseList(L);
    printf("翻转后："); DispList(L); printf("\n");

    printf("\n--- 合并（非递减 → 非递增）---\n");
    LinkList LA = NULL, LB = NULL;
    CreateSorted(LA, 4);
    CreateSorted(LB, 3);
    printf("LA（非递减）："); DispList(LA); printf("\n");
    printf("LB（非递减）："); DispList(LB); printf("\n");
    MergeDesc(LA, LB);
    printf("合并后（非递增）："); DispList(LA); printf("\n");

    return 0;
}
