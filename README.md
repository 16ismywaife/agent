# Agent 方向 · 本科生观察期 6 周

培养方案 6 周观察期的代码与日志仓库。

## 目录说明

```
agent/
├── notes/          工作日志（★ 必须提交，第 6 周汇报要用）
├── week1/          第 1 周：Python 与开发环境
├── week2/          第 2 周：Git、Linux 与深度学习基础
├── week3/          第 3 周：现代 AI 模型体验（大模型分支）
├── week4/          第 4 周：三个方向体验（Agent 为重点）
├── week5/          第 5 周：选方向 + 完成小模块
├── week6/          第 6 周：正式考核材料
├── common/         共用工具（日志器、计时器等）
├── data/           数据集（已忽略，不提交）
├── logs/           程序运行日志（已忽略，不提交）
└── checkpoints/    模型权重（已忽略，不提交）
```

## 环境

```bash
conda create -n agent python=3.11 -y
conda activate agent
pip install -r requirements.txt
```

> 固定 Python 3.11：AI 生态对 3.11 支持最完整，3.12/3.13 有些库还没跟上。

## 每周进度

| 周 | 主题 | 交付物 | 状态 |
|---|---|---|---|
| 1 | Python 与开发环境 | CSV 分析脚本（读→统计→绘图→保存） | [ ] |
| 2 | Git、Linux、深度学习基础 | MNIST 训练 + 保存/加载模型 + Accuracy | [ ] |
| 3 | 现代 AI 模型体验 | Prompt / 多轮对话 / 结构化输出 / 参数实验 | [ ] |
| 4 | 三个方向体验 | Agent（LLM + 1 Tool）/ LLM 部署 / 视频 Edge | [ ] |
| 5 | 选方向 + 小模块 | 一个可复现的独立模块 | [ ] |
| 6 | 正式考核 | Demo + 仓库 + 5 页汇报 + 1 页总结 | [ ] |

## 三条纪律

1. **每天 commit** —— 第 6 周要交仓库，有历史的仓库和空仓库是两个东西
2. **每天写日志**（`notes/`）—— 汇报第 3 页直接从这里取，不记就写不实
3. **每个产出都必须能跑起来** —— 方案原文："不以 PPT 包装代替实际工作"、"必须现场运行"

## 每天怎么用

```bash
git status
git add .
git commit -m "week1: csv analysis done"
```
