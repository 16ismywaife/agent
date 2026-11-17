// 第 5 步：哈夫曼树 + 编码 + 译码（实验2 题4）
//
// 三步走：
//   1. 统计每个字符出现多少次
//   2. 每次挑出两个权值最小的结点合并，合成的新结点放回池子里，重复到只剩一个
//   3. 从叶子往根走，走左边记 0、走右边记 1，倒过来就是编码
//
// 译码是反着来：从根出发，读 0 就往左、读 1 就往右，走到叶子就输出一个字符。

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 200          // 叶子结点数上限

typedef struct {
    char data;         // 这个结点代表的字符（只有叶子才有）
    int weight;        // 权值：出现次数
    int parent;
    int lchild;
    int rchild;
} HTNode;

typedef struct {
    char cd[N + 2];    // 编码字符串（cd[n0+1] 放结束符）
    int start;         // 编码在 cd 里从第几位开始
} HCode;

// ==================== 1. 建哈夫曼树 ====================

void CreateHT(HTNode ht[], int n0)
{
    int i, k, lnode, rnode;
    int min1, min2;

    // 先把 2*n0-1 个结点全初始化成"孤立"
    for (i = 0; i < 2 * n0 - 1; i++) {
        ht[i].parent = -1;
        ht[i].lchild = -1;
        ht[i].rchild = -1;
    }

    // 一共要合并 n0-1 次
    for (i = n0; i < 2 * n0 - 1; i++) {
        min1 = min2 = 2147483647;   // 分别记最小和次小
        lnode = rnode = -1;

        for (k = 0; k <= i - 1; k++) {
            if (ht[k].parent == -1) {        // 只看还没被合并过的
                if (ht[k].weight < min1) {
                    min2 = min1;
                    rnode = lnode;
                    min1 = ht[k].weight;
                    lnode = k;
                } else if (ht[k].weight < min2) {
                    min2 = ht[k].weight;
                    rnode = k;
                }
            }
        }

        // 把这两个最小的挂到新结点 i 下面
        ht[lnode].parent = i;
        ht[rnode].parent = i;
        ht[i].weight = ht[lnode].weight + ht[rnode].weight;
        ht[i].lchild = lnode;
        ht[i].rchild = rnode;
    }
}

// ==================== 2. 求每个叶子的编码 ====================

void CreateHCode(HTNode ht[], HCode hcd[], int n0)
{
    int i, c, f;

    for (i = 0; i < n0; i++) {
        hcd[i].start = n0;          // 从后往前填
        c = i;                      // 从叶子出发
        f = ht[i].parent;

        while (f != -1) {           // 一直往上爬到根
            if (ht[f].lchild == c) {
                hcd[i].cd[hcd[i].start--] = '0';   // 我是左孩子 → 0
            } else {
                hcd[i].cd[hcd[i].start--] = '1';   // 我是右孩子 → 1
            }
            c = f;
            f = ht[f].parent;
        }
        hcd[i].start++;             // start 停在编码第一位
        hcd[i].cd[n0 + 1] = '\0';   // 补上字符串结束符，才能用 %s 打印
    }
}

// ==================== 3. 译码 ====================

void DeCode(HTNode ht[], int n0, char *code, char *out)
{
    int i, p, m = 0;
    int root = 2 * n0 - 2;          // 根是最后一个结点

    p = root;
    for (i = 0; code[i] != '\0'; i++) {
        if (code[i] == '0') p = ht[p].lchild;
        else                p = ht[p].rchild;

        if (ht[p].lchild == -1 && ht[p].rchild == -1) {   // 走到叶子了
            out[m++] = ht[p].data;
            p = root;                                     // 回到根，接着读
        }
    }
    out[m] = '\0';
}

// ==================== main ====================

int main()
{
    system("chcp 65001 > nul");

    // 题目里那段英文（原文里有一个弯引号 ’，这里换成普通 ' ，否则会占 3 个字节）
    char text[] =
        "The Chinese official said he viewed the Trump Presidency not as an aberration but as "
        "the product of a failing political system. This jibes with other accounts. The Chinese "
        "leadership believes that the United States, and Western democracies in general, haven't "
        "risen to the challenge of a globalized economy, which necessitates big changes in "
        "production patterns, as well as major upgrades in education and public infrastructure. "
        "In Trump and Trumpism, the Chinese see an inevitable backlash to this failure.";

    // ---- 统计频率 ----
    int cnt[256] = {0};
    int i, n0 = 0;
    for (i = 0; text[i] != '\0'; i++) {
        cnt[(unsigned char)text[i]]++;
    }

    HTNode ht[2 * N];
    int k = 0;

    for (i = 0; i < 256; i++) {
        if (cnt[i] > 0) {
            ht[k].data = (char)i;
            ht[k].weight = cnt[i];
            k++;
        }
    }
    n0 = k;

    printf("总字符数: %d\n", (int)strlen(text));
    printf("不同字符数: %d\n\n", n0);

    printf("字符  次数  频率\n");
    for (i = 0; i < n0; i++) {
        char show = ht[i].data;
        if (show == ' ') printf("[空格]  %3d  %5.2f%%\n", ht[i].weight, 100.0 * ht[i].weight / strlen(text));
        else             printf("  %c    %3d  %5.2f%%\n", show, ht[i].weight, 100.0 * ht[i].weight / strlen(text));
    }

    // ---- 建树 ----
    CreateHT(ht, n0);

    // ---- 编码 ----
    HCode hcd[N];
    CreateHCode(ht, hcd, n0);

    printf("\n哈夫曼编码:\n");
    for (i = 0; i < n0; i++) {
        char show = ht[i].data;
        if (show == ' ') printf("  [空格]  ->  %s\n", &hcd[i].cd[hcd[i].start]);
        else             printf("    %c     ->  %s\n", show, &hcd[i].cd[hcd[i].start]);
    }

    // ---- 把整段文本编码成 0-1 串 ----
    int codeLen = 0;
    for (i = 0; i < n0; i++) codeLen += ht[i].weight * (n0 - hcd[i].start + 1);
    char *code = (char *)malloc(codeLen + 1);

    // 建一个"字符 -> 编码"的索引表
    char *table[256];
    for (i = 0; i < 256; i++) table[i] = NULL;
    for (i = 0; i < n0; i++) table[(unsigned char)ht[i].data] = &hcd[i].cd[hcd[i].start];

    int pos = 0;
    for (i = 0; text[i] != '\0'; i++) {
        char *c = table[(unsigned char)text[i]];
        while (*c != '\0') code[pos++] = *c++;
    }
    code[pos] = '\0';

    printf("\n编码后长度: %d 位（原文 %d 个字符，压缩到 %.1f%%）\n",
           codeLen, (int)strlen(text), 100.0 * codeLen / (8.0 * strlen(text)));

    printf("0-1 序列前 120 位:\n");
    for (i = 0; i < 120 && code[i] != '\0'; i++) printf("%c", code[i]);
    printf("...\n");

    // ---- 译码 ----
    char *decoded = (char *)malloc(strlen(text) + 1);
    DeCode(ht, n0, code, decoded);

    printf("\n译码结果:\n%s\n", decoded);

    printf("\n译码结果与原文本一致: %s\n", strcmp(text, decoded) == 0 ? "是" : "否");

    free(code);
    free(decoded);
    return 0;
}
