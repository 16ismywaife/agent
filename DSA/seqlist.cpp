// 顺序表（跟《数据结构教程 第7版》第 2 章 p.28~31 对齐）
//
// ★ 规则：类型定义和 main 我已经写好（就是课本上的写法），
//   三个标着 TODO 的函数体**你自己填**，照着书上抄一遍再理解。
//
// 编译：Ctrl+Shift+B
// 运行：& "$env:TEMP\seqlist.exe"
//
// 课本的约定（★ 这三条最容易错）：
//   1. 静态数组 MaxSize，没有扩容
//   2. 逻辑序号从 1 开始（i=1 是第一个元素），数组下标从 0 开始 → 用 data[i-1]
//   3. SqList *&L 里的 & 是 C++ 引用：函数里改了 L，外面也会变

#include <stdio.h>
#include <stdlib.h>

#define MaxSize 50
typedef int ElemType;          // 课本 p.29：为了简单，元素类型先当 int

typedef struct
{
    ElemType data[MaxSize];    // 存元素
    int length;                // 实际长度（用了几个）
} SqList;


// ==================== 你写的三个函数 ====================

// ① 初始化：课本 p.30
//    要给 L 分配空间（malloc），并把 length 设成 0
void InitList(SqList *&L)
{
    L = (SqList *)malloc(sizeof(SqList));
    L->length = 0;
}

// ② 输出全部元素：课本 p.31
//    循环 n 次，每次 printf("%d ", L->data[i])
//    循环范围是 length（不是 MaxSize！）
void DispList(SqList *L)
{
    for (int i = 0; i < L->length; i++)
        printf("%d ", L->data[i]);
    printf("\n");
}

// ③ 按逻辑序号取值：课本 p.31
//    i 是从 1 开始的逻辑序号
//    先判 i 合不合法（1 <= i <= length），不合法 return false
//    合法就 e = L->data[i-1]，return true
bool GetElem(SqList *L, int i, ElemType &e)
{
    if (i < 1 || i > L->length)
        return false;

    e = L->data[i - 1];
    return true;
}


// ==================== 下面不用改 ====================

int main()
{
    SqList *L;
    InitList(L);                    // 初始化

    // 手动塞 4 个元素，模拟"已经存了数据"
    L->data[0] = 3;
    L->data[1] = 7;
    L->data[2] = 1;
    L->data[3] = 9;
    L->length = 4;

    printf("顺序表现有元素：");
    DispList(L);

    ElemType e;
    if (GetElem(L, 3, e))
        printf("第 3 个元素 = %d\n", e);
    else
        printf("第 3 个元素取不到（越界）\n");

    if (!GetElem(L, 9, e))
        printf("第 9 个元素取不到（越界）—— 对了，说明你判断写对了\n");

    free(L);                        // 用完释放，和 malloc 配对
    return 0;
}

// ==================== 期望输出 ====================
// 顺序表现有元素：3 7 1 9
// 第 3 个元素 = 1
// 第 9 个元素取不到（越界）—— 对了，说明你判断写对了
