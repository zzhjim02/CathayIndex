<div align="center">

# 🔎 CathayIndex

**本地文件库索引工具 · 把某个文件夹（连同子文件夹、孙文件夹……）里的文件目录做成一个库**

*开箱即用 · 双击即开 · 纯本地 · 不联网 · 不改动任何源文件*

[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2B-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![GitHub release](https://img.shields.io/github/v/release/zzhjim02/CathayIndex)]()

**建好的库名叫「本地文件库」，可以直接被 [CathayFinder](https://github.com/zzhjim02/CathayFinder)
当渠道检索** —— 也就是回答「我现在手头这个盘里到底有哪些书」。

</div>

---

## 🔗 Cathay 人文社科工具链

| 顺序 | 工具 | 干什么 | 状态 |
|:---:|---|---|---|
| ⓪ | [CathayPDG](https://github.com/zzhjim02/CathayPDG) | 读秀/超星 **PDG 批量转 PDF**：解压解密、横竖排分柜 | v0.1.5 |
| ① | **CathayIndex（你在这里）** | 把本地文件夹（含子目录、孙目录）扫成「本地文件库」 | v1.0.0 |
| ② | [**CathayFinder**](https://github.com/zzhjim02/CathayFinder) | 综合性图书检索引擎：11 个渠道，按书名 / 作者 / 出版者 / SSID 精准查 | v1.0.0 |
| ③ | [**CathayOCR**](https://github.com/zzhjim02/CathayOCR) | 多引擎 GPU 加速古籍 PDF 批处理 OCR | v1.2.4 |
| ④ | [**CathayShelf**](https://github.com/zzhjim02/CathayShelf) | 自动著录建夹 / 产物后缀替换 / 繁简转换（已整合 CathaySimplify） | v0.4.5 |
| ⑤ | [**CathayReader**](https://github.com/zzhjim02/CathayReader) | PDF/TXT 双栏同步古籍校勘阅读器 | v1.0.0 |

**备用软件（四个，按需取用）**

| 工具 | 干什么 | 状态 |
|---|---|---|
| [**CathayRepair**](https://github.com/zzhjim02/CathayRepair) | 先把损坏的 PDF 修好（③ OCR 前可选） | v1.0.0 |
| [**CathayRestore**](https://github.com/zzhjim02/CathayRestore) | 把 OCR 文本写回 PDF 文字层（③ OCR 之后可选） | v1.0.0 |
| [**CathayExtract**](https://github.com/zzhjim02/CathayExtract) | 已有双层 PDF → 直接提取文字层成 TXT（③ 的替代入口） | v1.2.3 |
| [**CathaySimplify**](https://github.com/zzhjim02/CathaySimplify) | TXT 繁简体转换 + 编码规范化（功能已并入 ④ CathayShelf） | v1.0.0 |

> 🧭 **主线一句话：** `CathayIndex` 建本地库 → `CathayFinder` 查书（找 SSID / 路径） → `CathayOCR` 识别 → `CathayShelf` 著录归架 → `CathayReader` 双栏校勘

> 📌 **这是本仓库（CathayIndex）** — 主线第 ① 步：**先把自己有的东西变成可检索的库**，再交给 ② CathayFinder 查。

---

## 📦 下载

| 下载方式 | 说明 |
|:-------|:-----|
| 📥 百度网盘（密码 2026） | [CathayIndex 本地文件库索引工具 1.0.0](https://pan.baidu.com/s/1pRtTIOLg2aOm9CRhcxJ_Rg?pwd=2026)（含源码与便携运行库） |
| 🐙 GitHub Releases | [CathayIndex v1.0.0](https://github.com/zzhjim02/CathayIndex/releases/tag/v1.0.0)（Assets 里直接下 `CathayIndex.exe`） |
| 💻 源码 / 便携版 | 本仓库源码：`python gui.py` 直接跑；或用 `runtime\` + `建库.bat`（自带 Python，约 40 MB） |

> ⚠️ **本仓库只放程序，不放任何数据**：索引出来的库（`local_files.db`）、
> `settings.json`、`runtime\`、`dist\` 都不在仓库里 —— 库是**你自己用本工具建**的。

---

## 它做什么

- 选一个（或多个）文件夹 → 递归扫掉里面**所有**层级的文件
- 把「文件名 / 完整路径 / 所属根目录 / 扩展名 / 大小 / 修改时间」写进 SQLite 库
- 库名：**本地文件库**（文件名 `local_files.db`，默认放进 CathayFinder 的 `data\db\`）
- 库里带 FTS 全文索引，检索规则与 CathayFinder 其他渠道**完全一致**（精准匹配、不做模糊召回）
- 两种方式：**全量重建**（默认）／**增量更新**（只加新增和变化的，可选清理已删除的记录）

## 三种用法

**1）图形界面（推荐）**
双击 `建库.bat`（或 `python gui.py`）→ 指一下 **CathayFinder 在哪**（只到它的文件夹这层）
→ 把要收的文件夹拖进窗口 → 「开始建库」。
建完可以就地在窗口下方试搜一下，双击结果直接跳到文件所在位置。

**2）命令行**
```bat
python indexer.py --cli "D:\我的书" "E:\古籍" --mode inc
python indexer.py --cli "Y:\学术信息全文检索数据库" --ext pdf,epub,djvu
python indexer.py --cli "D:\我的书" --cathayfinder "D:\Program Files\CathayFinder 综合性图书检索引擎"
```
参数：`--cathayfinder CathayFinder所在目录`（推荐，库自动写进 `<它>\data\db\local_files.db`）、
`--out 库文件路径`（想让库落在别处时才用）、`--mode full|inc`（默认 full）、
`--ext pdf,epub,...`（只收这些扩展名）、`--keep-hidden`（不跳过隐藏/系统目录）、
`--no-clean`（增量时不清理已删除记录）。

**3）自检**
```bat
python indexer.py --selftest      :: 引擎
python gui.py --selftest          :: 引擎 + 界面
```

## 用 CathayFinder 检索这个库

你只需要在界面上指一下 **CathayFinder 的文件夹**（里面有 `CathayFinder.exe` / `data\db`，例：
`D:\Program Files\CathayFinder 综合性图书检索引擎`），库会自动写成
`<它>\data\db\local_files.db` —— 不用自己去翻 `data\db` 在哪。

选好文件夹建完库、重启 CathayFinder，就能在渠道「**本地文件库**」里搜到。
（也可以先把 CathayFinder 的文件夹直接拖进窗口，再拖要收的文件夹。）

## 界面上的选项说明

| 选项 | 说明 |
|---|---|
| CathayFinder 在哪 | 指到 CathayFinder 的那一层文件夹就行（不用管 `data\db`）；库会自动写成 `<它>\data\db\local_files.db`。「自动」按钮会自己找 |
| 全量重建 | 每次重新扫一遍，生成全新的库（旧库自动留一份 `.bak`） |
| 增量更新 | 已有的记录不动，只加新的、更新变化的；勾了「清理已删除」就会把源里已经没有的文件记录删掉 |
| 只收这些扩展名 | 留空 = 全部文件；填 `pdf,epub,azw3,djvu,txt` 就只收这些 |
| 跳过隐藏/系统目录 | 默认勾选，跳过 `$RECYCLE.BIN`、`System Volume Information`、`.git`、`node_modules` 等 |
| 试搜 | 与 CathayFinder 同一套匹配：输入 `布罗代尔` 只命中完整包含这串的记录 |

## 库结构（想自己接别的工具时看）

```sql
CREATE TABLE items (filename, filepath, account, title, ext, size, mtime, extra);
CREATE VIRTUAL TABLE items_fts USING fts5(title, filename, filepath, account,
                                          content="", contentless_delete=1);
```
- `items_fts` 里的文本是**去掉标点后逐字加空格**存的（`布罗代尔` → `布 罗 代 尔`），
  这样查询会被展开成短语 `"布 罗 代 尔"` 做完整包含匹配 —— 与 CathayFinder 其他库同一套约定。
- 行数 = 文件数；`account` = 你添加的那个根文件夹名。

## 文件说明

```
indexer.py          引擎 + 命令行（扫描 / 建库 / 增量 / 试搜 / 自检）
gui.py              tkinter 图形界面（拖放、进度、建库后试搜）
settings.json       记住上次指的 CathayFinder 位置（不入库）
建库.bat            启动脚本（优先用 runtime\，否则用系统 Python）
fab.py / 发版.bat   一键打包发版（见 发布流程.md）
app.ico             图标
requirements.txt    依赖说明（本工具无需第三方包；tkinterdnd2 可选）
```

## 系统要求

- Windows 10/11 + Python 3.10 以上（自带 tkinter / sqlite3，**无需安装任何第三方包**）
- 可选：`tkinterdnd2` 装上后支持把文件夹直接拖进窗口（不装也能用「添加文件夹」）
- 增量更新会把库里的 (路径,大小,时间) 读进内存，几百万文件的库建议用全量重建或分批

## 常见问题

**扫描很慢？** 机械盘、几百万文件的目录正常要几分钟；进度条会显示总数与进度。

**库会不会把源文件改坏？** 不会。工具只读文件系统，只写库文件本身；库里不保存文件内容，只保存目录信息。

**同名文件怎么办？** 全部照收，靠 `filepath` 区分（同一个文件不会重复收录）。

**CathayFinder 里搜不到？** ① 确认建的库里确实有文件（界面下方试搜一下）；② 确认库落在 CathayFinder 的 `data\db\local_files.db`；③ 重启 CathayFinder；④ 确认「本地文件库」这个渠道前面打了勾。

**仓库里为什么没有 `.db` 文件？** 库是**数据**，只该存在你自己机器上；本仓库只放程序。
（`.gitignore` 已把 `*.db`、`runtime/`、`dist/`、`settings.json` 排除在外。）

## 更新日志

- **v1.0.0**：首个版本。递归建库（全量／增量）、扩展名过滤、隐藏/系统目录跳过、
  清理失效记录、界面内试搜、库结构与 CathayFinder 对齐可直接被检索。

## 许可

GPL-3.0（见 `LICENSE`）。
