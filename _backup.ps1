# 把手册和工作日志备份到 E 盘「05_文档与书」
#
# 为什么要这个脚本：2026-10-16 移动硬盘摔坏，项目文档差点全丢。
#   代码有 GitHub 兜底，但 HANDBOOK / 日志只在仓库里 —— 仓库所在的盘没了就是真没了。
#
# 用法：
#   cd "E:\04_脚本与代码\agent"
#   .\_backup.ps1                    # 备份到默认位置
#   .\_backup.ps1 -Dest "D:\某处"    # 换目标
#
# 脚本会：复制 → 算 SHA256 → 逐个比对 → 重新生成「说明.md」→ 打印结果
#
# ★ 两条踩过的坑（2026-10-20）：
#   1. 这个文件必须存成【带 BOM 的 UTF-8】。Windows PowerShell 5.1 读 .ps1 时，
#      没有 BOM 就按系统 ANSI（这里是 GBK）解 —— 中文注释变乱码，整个脚本语法解析失败。
#   2. here-string 里反引号是转义符，三反引号会被吃成一个 —— 所以说明.md 用 @' '@
#      单引号版本 + 占位符 {0}，不用 @" "@ 双引号版本。

param(
    [string]$Dest = "E:\05_文档与书\agent-6周计划手册备份"
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path

# 要备份的文件：源路径 → 备份里的名字 → 说明
$Items = @(
    @{ Src = Join-Path $Repo "HANDBOOK.md";  Name = "HANDBOOK.md";           Desc = "自学手册，9 章约 3300 行，以仓库里那份为准" },
    @{ Src = Join-Path $Repo "notes\log.md"; Name = "工作日志_notes_log.md"; Desc = "每日工作日志，第 6 周汇报第 3~4 页直接从这里抄" }
)

Write-Host ""
Write-Host "备份 -> $Dest" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

$rows = @()
$allOk = $true

foreach ($it in $Items) {
    if (-not (Test-Path $it.Src)) {
        Write-Host ("  [X] 源文件不存在: " + $it.Src) -ForegroundColor Red
        $allOk = $false
        continue
    }

    $dstPath = Join-Path $Dest $it.Name
    Copy-Item $it.Src $dstPath -Force

    $hSrc = (Get-FileHash $it.Src  -Algorithm SHA256).Hash
    $hDst = (Get-FileHash $dstPath -Algorithm SHA256).Hash
    $ok = ($hSrc -eq $hDst)
    if (-not $ok) { $allOk = $false }

    $flag = "OK "
    if (-not $ok) { $flag = "BAD" }

    $kb = [math]::Round((Get-Item $it.Src).Length / 1KB, 1)
    Write-Host ("  [{0}] {1,-24} {2,7} KB  {3}..." -f $flag, $it.Name, $kb, $hSrc.Substring(0, 16))

    $rel = $it.Src.Replace($Repo + "\", "")
    $rows += ('| `' + $it.Name + '` | `' + $rel + '` | ' + $it.Desc + ' | `' + $hSrc + '` |')
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$tableRows = $rows -join "`r`n"

# ★ 单引号 here-string：里面的 $ 和反引号都不解释，只有 {0} {1} {2} {3} 由 -f 填
$doc = @'
# 这是备份（不是原件）

> 备份时间：{0}
> 备份原因：2026-10-16 用过一年多的移动硬盘摔坏，教训是**文档要有一份不跟着仓库走的副本**。

## 这里面是什么

| 文件 | 原件位置 | 说明 | SHA256 |
|---|---|---|---|
{1}

**原件永远在仓库里**（{2}），仓库还有一份在 GitHub（github.com/16ismywaife/agent）。
这份备份的作用是：**仓库所在的那块盘要是也没了，这里还能捞回来**。

## 完整性校验

```powershell
Get-FileHash "{3}\HANDBOOK.md" -Algorithm SHA256
```

和上表的值一样 = 这份备份是新的；不一样 = 这份备份旧了，重跑一次 _backup.ps1。

## 怎么更新这份备份

```powershell
cd "{2}"
.\_backup.ps1
```

## 什么时候该更新

- HANDBOOK 或日志改过之后
- **每周日收尾跑一次就够** —— 别指望"想起来再备份"，上次就是这么丢的
'@ -f $stamp, $tableRows, $Repo, $Dest

Set-Content -Path (Join-Path $Dest "说明.md") -Value $doc -Encoding UTF8

Write-Host ""
if ($allOk) {
    Write-Host "[OK] 备份完成，两份文件的 SHA256 与源文件逐一比对一致" -ForegroundColor Green
} else {
    Write-Host "[BAD] 有文件校验不一致，看上面哪一行是 BAD" -ForegroundColor Red
    exit 1
}
