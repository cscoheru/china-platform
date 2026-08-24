# Stage 0 Gate 0 — E-1 中文扫描 PDF 候选报告（研究 Agent 回报）

> 文档日期：2026-08-24
> 适用：E-1 研究 Agent 回报（2026-08-24 后台任务 `a96659e291b77b5e2`）结构化整理
> 编写角色：CC（Claude Code）
> 状态：**草稿；未下载任何候选；等 Cursor 预审裁定（07 §5.2）+ §7 U-1 / U-2 用户裁定**
> 范围：仅整理研究 Agent 报告；不动 spike 04 任何文件；不下发 PDF；不改 gate_thresholds.json。

---

## §0. TL;DR

| 维度 | 结论 |
|---|---|
| 合法免费中文扫描 PDF 来源 | **仅 1 个已确认**：全国人大法规数据库陕西省财政预算管理条例（4 页） |
| 其他 10+ 个备选（born-digital） | 政府公开 / 学术机构开放 / 国际组织 CC-BY；非扫描 PDF，可作文本对照 |
| 用户政策 U-3 影响 | 即使该 PDF ACCEPT，**spike 04 不再是 Stage 0 验收项**（per docs/15 §4a）；该 PDF 仅作研究追踪 / OCR 管线充实 |
| CC 当前动作 | **不下载**；等 Cursor 预审 + U-1 / U-2 裁定 |
| Stage 0 Gate 0 | 仍 BLOCKED（口径未实质改动） |

---

## §1. 候选源结构化清单（研究 Agent 报告整理）

### 1.1 Tier 1 — 唯一已确认扫描 PDF（供 OCR 真值对照）

#### 候选 1：陕西省财政预算管理条例

| 字段 | 值 |
|---|---|
| URL | `https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf` |
| 来源机构 | 全国人大常委会法律法规数据库（`wb.flk.npc.gov.cn`） |
| 许可依据 | 政府公开文件，无版权声明；默认公共领域 |
| 文件类型证据 | **Canon SC1011 + MP Navigator EX** 扫描生成；嵌入 JPEG 图像层；1259×1669 px/页（4 页一致） |
| 文件大小 | 984 KB |
| 真值对照 | 嵌入文本层（pdftotext 提取 11,387 字符，含 3,230 中文字）可与图像层 OCR 比对 |
| 代表性 | 地方性法规（陕西财政预算管理），符合中国治理研究 PRD；规模小（4 页） |
| 风险 | 无绕墙、无批量、无商业库、无合成；URL 单条下载 |
| 备注 | 同站点（`wb.flk.npc.gov.cn/dfxfg/PDF/`）批量地方性法规多为扫描生成，可持续挖掘 |

#### 候选 2（同站更多资源）

| 字段 | 值 |
|---|---|
| 范围 | 全国人大法律法规数据库 `dfxfg/PDF/` 子目录 |
| 状态 | 浏览器可访问清单；逐条 URL 未一一验证 |
| 风险 | 逐条单下载可接受；不批量；不爬取列表外内容 |

### 1.2 Tier 2 — born-digital PDF（可作文本对照但非扫描）

| # | 来源 | URL | 标题 | 授权 | 备注 |
|---|---|---|---|---|---|
| 3 | 中国社科院法学所 | `http://iolaw.cssn.cn/zzwx/201905/P020190522362649620152.pdf` | 刑法中"国家工作人员"概念立法演变 | 社科院开放获取 | ~10 页 |
| 4 | 国家知识产权局 | `https://www.cnipa.gov.cn/module/download/downfile.jsp?...` | 知识产权强国建设发展报告 2025 | 政府公开 | 多页 |
| 5 | 国新办 | `http://www.scio.gov.cn/live/2026/38633/qwxz/202605/P020260601622910390503.pdf` | 常住地提供基本公共服务吹风会 | 政府公开 | 多页 |
| 6 | 国家统计局 | `https://www.stats.gov.cn/zt_18555/ztsj/jzgj/jz2015/202302/P020230218542075734622.pdf` | 中国统计体系简介 2015 | 政府公开 | 多页 |
| 7 | 发改委 | `https://www.ndrc.gov.cn/fggz/fzzlgh/gjfzgh/202603/U020260317369114704096.pdf` | 十四五规划纲要 | 政府公开 | ~100+ 页 |

**性质**：born-digital（非扫描），文本可机器直接提取；如需 OCR 真值对照，必须配扫描 PDF；可作"基线对照"验证文本提取管线（非 OCR 能力验证）。

### 1.3 Tier 3 — 国际组织中国报告（英文/双语）

| # | 来源 | URL | 标题 | 授权 |
|---|---|---|---|---|
| 8 | UNDP | `https://www.undp.org/sites/g/files/zskgke326/files/migration/cn/UNDP-CH--NHDR-2016-CH.pdf` | 中国人类发展报告 2016（中文版） | UNDP open access |
| 9 | ADB | `https://www.adb.org/sites/default/files/publication/236661/transforming-high-income-prc.pdf` | 向高收入中国转型 | CC BY 3.0 IGO |
| 10 | World Bank | `https://documents1.worldbank.org/curated/en/781101468239669951/pdf/China-2030-building-a-modern-harmonious-and-creative-society.pdf` | China 2030 | World Bank CC BY |
| 11 | CRS（**唯一国际来源扫描 PDF**） | `https://digital.library.unt.edu/ark:/67531/metadc821120/m2/1/high_res_d/RS20655_2000Aug17.pdf` | China: The National People's Congress | **Public Domain**；仅 6 页英文 |

### 1.4 已排查无果

| 来源 | 否决原因 |
|---|---|
| 国家统计局统计年鉴 | HTML 格式，非 PDF |
| macrodatas.cn | 需登录，版权不明 |
| CNKI / 知网 | 付费墙 |
| 万方数据 | 需订阅 |
| NSSD 国家哲学社会科学文献中心 | 无结果 |
| 国家档案馆 sag.gov.cn | 无大尺寸扫描 PDF 开放 |
| 中国国家图书馆 nlc.cn | 需注册/借阅 |

---

## §2. 红线复核（07 §4 逐条）

| # | 约束 | 候选 1 陕西条例 | 候选 3-10 born-digital | 候选 11 CRS |
|---|---|---|---|---|
| R-1 | 不爬取 / 不绕墙 / 不批量 | ✅ 单条 curl | ✅ 单条 curl | ✅ 单条 curl |
| R-2 | 不商业 OCR / 付费库 | ✅ 政府公开 | ✅ 政府公开 / UNDP / ADB / WB | ✅ Public Domain |
| R-3 | 不合成 PDF | ✅ 真扫描 PDF | N/A（born-digital） | ✅ 真扫描 PDF |
| R-4 | 不降 `gate_thresholds.json` 门槛 | ✅ 不动 | ✅ 不动 | ✅ 不动 |
| R-5 | 真实中文 + 授权明确 + 真值可对照 | ✅ 中文 + 公共领域 + 嵌入文本层 | ⚠ 中文 + 政府公开但非扫描 | ⚠ 英文 + 公共领域 + 真扫描 |

**首选**：候选 1 陕西省财政预算管理条例（唯一同时满足 R-1..R-5 的候选）。

---

## §3. 用户 U-3 落地后的实际意义

per docs/15 §4a：

- spike 04 **不再是 Stage 0 验收项**
- 即使候选 1 ACCEPT + 集成成功，Stage 0 不因此从 BLOCKED 转为 PASS
- 该 PDF 的实际价值：**研究追踪 + OCR 管线充实 + 未来 Stage 1+ 使用**
- 当前最可行的作用：替换或并列 1909 美国样本，作为 OCR 管线**中文压力测试**真实样本

**结论**：候选 1 仍值得集成（低风险高收益），但**不阻塞 Gate 0 也不解开 Gate 0**。

---

## §4. 等裁定项（停等，CC 不动手）

| 编号 | 事项 | 预审方 | CC 等待动作 |
|---|---|---|---|
| §5.2 | 候选 1 ACCEPT / REJECT / NEEDS-INFO | Cursor | 见裁定后执行 |
| U-1 | 候选 PDF 是否满足 PRD「代表性」 | 用户 | 即使 Cursor ACCEPT，CC 不下载 |
| U-2 | 是否接受人工标注 ground truth（候选 1 是 4 页小样本，可能需要） | 用户 | 即使接受，CC 不下载 |

---

## §5. Cursor 预审裁定记录

来源：`reviews/09-stage0-cursor-e1-precheck-20260824.md`（2026-08-24）

### 5.1 总表（已填）

| 候选 | 标识 | 裁定 | CC 动作 |
|---|---|---|---|
| **1** | 陕西省财政预算管理条例（4 页） | **ACCEPT（有条件 C-1..C-4）** | U-1/U-2 用户裁定后 → `07` §5.3 |
| 2 | 同站 `dfxfg/PDF/` 目录 | **NEEDS-INFO** | 须逐条补 §5.1 字段后再预审；禁止目录批量下载 |
| 3–7 | Tier 2 born-digital | **REJECT（E-1 用途）** | 不作 spike 04 OCR 主样本；可作未来文本提取基线另立项 |
| 8–10 | Tier 3 国际组织 | **REJECT（E-1）** | 非中文扫描表；不符合 R-5 |
| 11 | CRS 英文 6 页扫描 | **REJECT（E-1）** | 英文；与 1909 美国样本同类风险 |

### 5.2 候选 1 ACCEPT 条件（09 §1.2）

```
C-1. HTTP 200 且 magic=%PDF
C-2. pdfinfo 显示图像层 / Producer 含扫描设备痕迹
C-3. pdftotext 提取中文 ≥3000 字（与报告 3,230 量级一致）
C-4. provenance.json 写明 source_url + license 依据（法规库公开属性）
```

不达标 → 改 NEEDS-INFO。

### 5.3 用户裁定（2026-08-24）

- **U-1**：法规扫描件作"中文 OCR 压力样本"接受（不强求 PRD 原"代表性"；U-3 已将 spike 04 转为非验收项）
- **U-2**：同意用嵌入文本层作真值（不需人工全表标注）

**闸门**：09 §4 要求 U-1 + U-2 用户确认前禁止下载——已解除。

### 5.4 09 §5 任务清单（CC 后续执行）

- 任务 A：U-3 文档落地（docs/11/12/13 + 独立 commit + pack rebuild）
- 任务 B：更新本文件 §5（已完成 — 见上）
- 任务 C：U-1/U-2 确认后执行 `07` §5.3 九步（探针 curl → 验证 C-1..C-4 → provenance.json → pdftotext 真值 → extract → evaluate → pytest → 文档 → pack rebuild → commit）
- 任务 D：禁止清单（批量爬取、绕门槛、宣布 PASS）

### 5.5 Stage 0 口径

per 09 §3 + docs/15 §4a：

- spike 04 非 Stage 0 验收项
- 候选 1 集成成功**不得**自动宣布 Stage 0 PASS
- P-1 / P-2 不变
- U-4 待 eval 后用户裁定

---

## §5a. CC 任务 C 第 1 步探针结果（2026-08-24）

### 5a.1 探针命令与结果

```
$ curl -sLI -w "HTTP %{http_code} / size=%{size_download} / time=%{time_total}s\n" \
    --max-time 30 \
    "https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf"
HTTP 000 / size=0 / time=2.534929s
exit 35 (SSL connect error)
```

详细日志摘录：

```
* Uses proxy env variable https_proxy == 'http://127.0.0.1:7890'
* CONNECT tunnel established, response 200
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to wb.flk.npc.gov.cn:443
* Closing connection
```

### 5a.2 诊断

| 测试站点 | HTTP | 结论 |
|---|---|---|
| `anthropic.com` | 200 | 国际可达 |
| `github.com` | 200 | 国际可达 |
| `undp.org` | 403 | 国际可达（HEAD 被拒但非 SSL 问题） |
| `wb.flk.npc.gov.cn` | 000 / exit 35 | **国内政府站点 TLS 失败** |
| `stats.gov.cn` | 000 / exit 35 | 同上 |

**根因**：Clash 代理 CONNECT 隧道成功，但 TLS 握手在 `wb.flk.npc.gov.cn:443` 阶段 `SSL_ERROR_SYSCALL`。LibreSSL `/etc/ssl/cert.pem` 不含国内政府 CA 根证书（国内站点常用 CFCA / 国密 / 政务 CA）。

**这与全局记忆 `python-urllib-ssl-clash-proxy.md` 同类（certifi CA 包可解 Python urllib，但 curl 用系统 trust store；本机未安装国内 CA 包）。**

### 5a.3 09 §1.3 警告完全应验

Cursor 在 09 §1.3 已记录："本环境 SSL 失败，未得 PDF 字节"——CC 当前环境复现一致。

### 5a.4 CC 当前动作

按 09 §1.3 指示"**不因此否决候选 1；下载验证责任在 §5.3 第一步，失败则停报**"：

- ❌ **不下载**：候选 1 资格有效但当前本机环境无法完成 C-1
- ❌ **不使用 `--insecure`**：违反 R-1 绕墙红线
- ❌ **不修改 trust store**：属于环境级配置变更，未经用户授权
- ⏸ **停报**：等待用户处置

### 5a.5 候选处置路径（待用户裁定）

| 路径 | 操作 | 触发条件 |
|---|---|---|
| 用户本地下载 | 用户在能访问国内政府站的机器下载后传给 CC | 用户主动提供 PDF 文件 |
| 切换 CC 工作环境 | ssh 到国内服务器（如 puer-hk）后下载 | 用户授权 + CC 验证网络可达性 |
| 接受 E-1 实质失败 | 走 `06` §6 失败路径（U-3 已选） | 用户明确指令；不影响 Gate 0（U-3） |
| 候选源替换 | 改用 Tier 3 国际组织中文 PDF（如 UNDP 中国人类发展报告） | 需重新 §5.1 → §5.2 预审 |

**CC 不替用户选路径。**

---

## §6. 失败路径（07 §6 模板）

若 §4 中所有候选全部 REJECT：

```
E-1 中文扫描 PDF 检索 — 负面结果
- 日期：2026-08-24
- 方法：研究 Agent 4 子 Agent 并行（耗时 31m40s）
- 候选扫描：50+ 来源（中国官方 + 学术 + 国际）
- 唯一已确认合法免费中文扫描 PDF：候选 1 陕西省条例（4 页）
- 但 per U-3，spike 04 不再是 Stage 0 验收项

替代路径（需用户裁定 §7 U-3 已选 = 完整移除 spike 04 验收）：
1. 用户上传 PDF（用户此前声明"没有 PDF"）
2. 授权库接入（需书面许可）
3. PRD 缩小范围（U-3 已选此项实质内容）

按 U-3：spike 04 不再作为 Stage 0 验收项；E-1 实质失败不影响 Stage 0 总体判定。
但 spike 04 仍作为研究追踪项保留，未来 Stage 1+ 可重新启用。
```

**CC 当前不撰写此负面报告；候选 1 仍在预审中。**

---

## §7. 待 CC 执行的下一步（停等）

1. 若 Cursor ACCEPT + U-1 / U-2 裁定 → 按 07 §5.3 九步流程执行
2. 若 Cursor REJECT 或 NEEDS-INFO → 回 §1.1 候选 2 或升级到 §6 失败路径
3. 若 §7 用户裁定补充新条款 → 更新 docs/15 §4a

---

## §8. 红线（重申）

- ❌ CC 不得在未经 Cursor ACCEPT 的情况下下载 PDF
- ❌ CC 不得在未经用户 §7 U-1 / U-2 裁定的情况下入库
- ❌ CC 不得修改 `gate_thresholds.json` 换取 PASS
- ❌ CC 不得将 1909 美国样本标为中国代表性
- ❌ CC 不得批量爬取 / 绕墙 / 商业库

---

## §9. 阅读路径

| 优先级 | 文件 | 用途 |
|---|---|---|
| P0 | `reviews/07-stage0-cc-handoff-e1-waiting-20260824.md` | 上游 E-1 等待指令 |
| P0 | `docs/15-stage0-p0p1-handoff-20260824.md §4a` | U-3 / U-5 已裁定条款 |
| P0 | 本文件 | 候选源结构化清单（不下载） |
| P1 | `spikes/04-scanned-pdf/README.md` | spike 04 管线现状 |
| P1 | `spikes/04-scanned-pdf/gate_thresholds.json` | 门槛（勿改） |

---

— End of E-1 candidate report draft (CC, 2026-08-24) —