# Rewrite Rule Inference Using Equality Saturation

- 作者：Chandrakana Nandi；Max Willsey；Amy Zhu；Yisu Remy Wang；Brett Saiki；Adam Anderson；Adriana Schulz；Dan Grossman；Zachary Tatlock
- 出处：arXiv:2108.10436v1；源 PDF 页眉标注“PL, 2021, USA”
- 年份：2021
- DOI：10.1145/3485496
- Zotero key：P7MZXQQI
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 这篇论文解决的是一个“元重写”问题：给定目标语言的 grammar、interpreter 和候选等式的 validator，能否自动推导出一个小而强的 rewrite ruleset，而不是继续依赖专家通过多年试错手工维护规则。Ruler 把既有的三阶段流程明确化为：枚举项集合 \(T\)、从 \(T\times T\) 产生候选规则集合 \(C\)、从中选择有效且有用的规则集合 \(R\)；它的核心主张是，在 \(R\) 尚处于合成过程时，就用 equality saturation（等式饱和）反过来压缩下一轮的 \(T\) 和 \(C\)。源 PDF 物理页 1–2，Abstract、Fig. 1 与 Introduction 核心段落。[pdf:E01] [pdf:E02]

这个问题重要，不只是因为“写规则很麻烦”，而是规则质量会直接决定编译、合成和证明系统的性能、输出规模与可维护性。论文在引言中转述相关文献：缺少规则化简时，Halide 生成代码可出现 26× slowdown，Herbie 可返回 10× 更大的程序；这些数字属于论文引用的既有工作结论，不是 Ruler 本文的新实验。源 PDF 物理页 1，Introduction。[pdf:E01] 论文进一步指出，小、general、低冗余的 ruleset 会减少反复 pattern matching 的成本，也更容易调试；当语言算子语义变化时，自动重新推导规则还能降低维护成本。源 PDF 物理页 3，Section 2.1。[pdf:E03]

**论文直接陈述的核心结果。** Ruler 报告相对 CVC4 中相近的 rule synthesizer，按 harmonic mean 得到 5.8× 更小的 ruleset、25× 更快的 synthesis，同时没有牺牲整体 deriving power；在 Herbie case study 中，自动规则达到专家规则的端到端效果，并补上了一个长期缺失的化简能力。源 PDF 物理页 1，Abstract。[pdf:E01] 这里真正的价值是把 rewrite-rule engineering 从“一次性人工工艺”变成可重复执行的语义探索过程。

## § 2 — 前人工作与不足

论文最接近的比较对象是 Nötzli et al. 在 CVC4 中的 Syntax-Guided Synthesis（语法引导合成）式 rule enumeration。该方法同样枚举 terms、用 sampling 发现可能等价、再通过 subsumption、canonical variable ordering、semantic equivalence 和 congruence filtering 等阶段减少规则；但这些过滤大多发生在候选已经产生之后，term enumeration 本身没有持续按新学到的等价关系取 quotient。Ruler 的实质差别不是“也用了 sampling”，而是把当前 ruleset 作为反馈信号，同时缩小 enumerated terms 与 candidate rules。源 PDF 物理页 22，Section 8.1。[pdf:E04]

论文还讨论了几类相邻路线。Bansal–Aiken 的 peephole superoptimizer 用 fingerprints 把在少量赋值上表现相同的 terms 分组，和 Ruler 的 cvec 思路相近；TASO 枚举 computation graphs、用 random testing 找等价、再以 Z3 验证并用 subsumption 去除特例；QuickSpec 用测试发现代数等式并排除可由其他等式推出的结果；TheSy 也使用 e-graphs 和 rewriting 过滤冗余 axioms。源 PDF 物理页 22–23，Sections 8.2–8.4。[pdf:E04] [pdf:E05]

**基于证据的判断。** 第一，许多方法压缩的是最终 ruleset 或 candidate list，而不是把已学规则造成的 congruence 立即反馈到后续 term enumeration，因此指数级 term space 和近二次 candidate pairing 仍先发生。第二，若核心搜索强依赖 SMT，则遇到 solver 不支持、语义与 SMT-LIB 不一致、或理论本身不可判定的 domain 时，通用性受限。第三，workload mining 或 machine-learning candidate proposal 可以很有效，但会把覆盖范围绑定到已有 corpus，可能漏掉新 workload 的规则。第四，TheSy 已说明“e-graph 用于等式发现/去冗余”并非完全空白，因此 Ruler 更准确的新意应表述为：在通用 rule-inference loop 内，用 equality saturation 同时闭环压缩 \(T\) 和 \(C\)，而不是笼统声称首次把 e-graph 用于自动等式发现。源 PDF 物理页 22–23，Sections 8.1–8.4。[pdf:E04] [pdf:E05]

## § 3 — 重建作者的思考路径

以下是**基于证据的思考路径重建**，不是作者逐句给出的历史叙述。

1. 先接受已有经验：rewrite system 需要 sound rules，但规则越多不一定越好；更小、更 general、彼此更 orthogonal 的 ruleset 往往匹配成本更低、deriving power 更集中。源 PDF 物理页 3，Section 2.1。[pdf:E03]
2. 抽象各类 rule synthesizer 的共同骨架：先构造 term set \(T\)，再搜索 candidate set \(C\subseteq T\times T\)，最后建立 accepted ruleset \(R\)。源 PDF 物理页 2，Introduction 三阶段列表。[pdf:E02]
3. 识别两个增长瓶颈：语法树数量随深度指数增长；即使只保留 canonical terms，直接配对仍接近 \(O(n^2)\)。因此不能只在最后“删冗余规则”，必须让已知等价关系提前改变搜索空间。源 PDF 物理页 8–9，Sections 3.2–3.3。[pdf:E06] [pdf:E07]
4. 观察 equality saturation 的非破坏性表示：e-graph 能用共享子项和 e-class 紧凑表示大量等价 terms，应用规则时主要通过增加 e-node 与合并 e-class 来累积等价信息。于是把 \(R\) 看成动态增长的 congruence：每学到规则，就合并 \(T\) 中可证明等价的 classes，下一轮只从 quotient space 的代表元继续枚举。源 PDF 物理页 5–8，Figs. 2–4 与 Section 3.2。[pdf:E08] [pdf:E09] [pdf:E06]
5. 为避免在 canonical classes 上仍做全量配对，给每个 e-class 一个 characteristic vector（cvec）作为语义 fingerprint；只有 cvec compatible 的 classes 才进入候选集合，再由 model checking、SMT 或 fuzzing 的 `is_valid` 作最终判定。源 PDF 物理页 9–10，Section 3.3。[pdf:E07] [pdf:E10]
6. 最后再把 equality saturation 用到 candidate minimization：一次选出一批看起来 general 的有效规则，并让它们去证明、删除其余可导出的 candidates。这样 \(R\) 既是输出，也是下一轮 term/candidate compression 的执行器。源 PDF 物理页 10–11，Section 3.4 与 Fig. 5。[pdf:E10] [pdf:E11]

这条路径的关键转折是：不再把“已学规则”视为流程末端的静态产品，而是把它变成搜索过程中不断更新的 quotient operator（商空间算子）。

## § 4 — 核心 Intuition

把当前已学到的 ruleset \(R\) 当作一个在线压缩器：它把已经能证明等价的 terms 合并成同一个 e-class，也把已经能由 \(R\) 推出的 candidate rules 从后续搜索中消去。于是 Ruler 不是在完整语法空间里反复找同一种等价关系，而是在不断收缩的 quotient space 上继续发现新关系。cvec 只负责快速找“可能等价”的 class pair，真正的 soundness 仍交给 domain-specific validator。源 PDF 物理页 2、8–10，Fig. 1 与 Sections 3.2–3.3。[pdf:E02] [pdf:E06] [pdf:E07] [pdf:E10]

## § 5 — 具体方法与完整 Pipeline

**输入与输出。** 输入包括目标语言 grammar、interpreter/evaluator、term enumerator `add_terms`、候选验证器 `is_valid`、最大 iteration/term-size；也可以用 trusted axioms 初始化 \(R\)。输出是可双向理解的等式规则集合，接入只接受单向规则的系统时再做方向展开。Ruler 的整体接口和反馈回路见源 PDF 物理页 2，Fig. 1。[pdf:E02]

完整 pipeline 如下：

1. **初始化。** 建立空 e-graph 作为 \(T\)，令 \(R=\varnothing\)。外层 iteration 控制最多枚举多少 connectives；rational case 使用 expression depth。源 PDF 物理页 6，Fig. 4。[pdf:E09]
2. **枚举并共享。** `add_terms(T,i)` 加入本轮大小的 terms。hash-consing 自动复用相同 subterms，但此时仅有结构共享，还没有语义 quotient。源 PDF 物理页 7–8，Section 3.2。[pdf:E06]
3. **按已知规则压缩 \(T\)。** `run_rewrites(T,R)` 在 e-graph 副本上执行 equality saturation，只把新得到的 e-class merges 复制回原 \(T\)，不把 saturation 中临时生成的 terms 带回去，避免“为了压缩反而继续枚举”。下一轮只从各 equivalence class 的 canonical representative 扩展。源 PDF 物理页 8，Section 3.2。[pdf:E06]
4. **增量计算 cvec。** 常量的 cvec 是常量重复值；复合项对 children cvec 逐点执行 operator；变量 cvec 来自 random values 或 domain-specific interesting values。partial operator 失败用 `null` 表示。源 PDF 物理页 9，Section 3.3。[pdf:E07]
5. **生成候选。** 每个 e-class 只取一个 canonical term；再按 cvec compatibility 分组，仅在组内形成 \(t_i\leftrightarrow t_j\)。这一步把“全体代表元两两配对”改成语义 fingerprint 引导的稀疏配对。源 PDF 物理页 9–10，Section 3.3。[pdf:E07] [pdf:E10]
6. **验证与选择。** `choose_eqs` 先按 syntactic generality heuristic 选一批 candidates，用 `is_valid` 保留有效规则，再调用 `shrink(R\cup K,C)`，通过 equality saturation 删除已经可由 \(R\cup K\) 推导的剩余 candidates。默认 \(n=\infty\) 追求速度；\(n=1\) 更激进地最小化，但需要更多轮。源 PDF 物理页 10–11，Section 3.4 与 Fig. 5。[pdf:E10] [pdf:E11]
7. **闭环。** 新规则并入 \(R\)，返回步骤 3；当没有新 candidates 时才进入更大的 term size。最终返回 \(R\)。源 PDF 物理页 6，Fig. 4。[pdf:E09]

**真实例子：rational rules 接入 Herbie。** 论文用 \(+,-,\times,/,\mathrm{abs},\mathrm{neg}\) 组成 rational grammar，在 depth 2、3 个变量上用 random testing 验证候选，再以 SMT post-pass 检查 soundness。Ruler 在 18 秒内学到 50 条 bidirectional rules；按 Herbie 开发者建议去掉 4 条 expansive rules，并为单向接口展开成 76 条 rules。源 PDF 物理页 15–16，Fig. 7、Sections 5.1–5.2。[pdf:E12] [pdf:E13] 例如 Ruler 找到 \(|a\times b|\leftrightarrow |a|\times|b|\) 与 \(|a\times a|\leftrightarrow a\times a\)，两者组合可完成 Herbie 缺失的 \(|x|\times|x|\leftrightarrow x\times x\) 化简。源 PDF 物理页 16，Section 5.2。[pdf:E13]

**实现与执行平台。** 原型以 Rust 实现，使用 `egg` e-graph library，默认用 Z3 做 SMT validation；核心少于 1,000 行，boolean、bitvector、rational domain adapter 约为 100、400、300 行。源 PDF 物理页 12，Section 3.5。[pdf:E14] CVC4 对比实验为 single-threaded，运行于 AMD 3900X 3.6 GHz、32 GB RAM。源 PDF 物理页 14，Section 4.1.1。[pdf:E15] 论文研究的是 symbolic rule synthesis，不是 EMT/FPGA 仿真器；开关/事件处理、时间推进、多速率、定点表示和 FPGA mapping 均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有以 theorem–proof 为中心的数学推导，但有一套决定算法正确边界与复杂度的形式化定义。

**1. Rule soundness。** 在 domain \(D\) 中，规则 \(\ell\leftrightarrow r\) 的自由变量全称量化，必须满足

\[
\forall \sigma,\qquad \llbracket \sigma(\ell)\rrbracket_D=\llbracket \sigma(r)\rrbracket_D.
\]

直觉是：规则不是对少数测试输入成立，而是对任意 variable substitution 都保持 semantics。源 PDF 物理页 3，Section 2.1 的未编号公式。[pdf:E03]

**2. Naive candidate space。** 若直接在 term set 中寻找所有不同但语义相等的 pair，候选集合为

\[
C_{\text{naive}}=\{\ell\leftrightarrow r\mid \ell,r\in T,\ \ell\neq r\ \land\ \forall\sigma.\ \ell[\sigma]=r[\sigma]\}.
\]

它同时暴露两个成本：term 数量随语法深度指数增长，pairing 又产生二次组合；而且其中很多规则已经可由 \(R\) 推出。源 PDF 物理页 8，Section 3.3 的未编号公式及相邻正文。[pdf:E06]

**3. Characteristic vector。** 对 e-class \(i\) 的 canonical term \(t_i\)，给定 \(m\) 个 variable assignments \(\sigma_j\)，定义

\[
v_i=[\operatorname{eval}(\sigma_j,t_i)\mid j\in[1,m]].
\]

它不是 proof，而是 semantic fingerprint：若两个 total functions 真等价，则在所有采样点上必相同；反过来，在有限采样点相同只说明“值得验证”。源 PDF 物理页 9，Section 3.3 的未编号公式。[pdf:E07]

**4. Partial operator 的 match。** 对可能含 `null` 的 cvec \([a_1,\ldots,a_n]\) 与 \([b_1,\ldots,b_n]\)，论文要求所有位置要么相等、要么至少一侧为 `null`，同时至少有一个位置两侧都非空且相等：

\[
\forall i.\ a_i=b_i\ \lor\ a_i=\mathrm{null}\ \lor\ b_i=\mathrm{null},
\]
\[
\exists i.\ a_i=b_i\ \land\ a_i\neq\mathrm{null}\ \land\ b_i\neq\mathrm{null}.
\]

工程含义是：对某个输入一侧未定义，不立刻把 pair 判为不等；但必须至少存在一个共同定义且相等的观测，防止两个“处处未定义”的项被误配。源 PDF 物理页 9，Section 3.3 的未编号 match 定义。[pdf:E07]

**5. 压缩后的候选集合。** 只从不同 e-classes 的 canonical terms 中，保留 cvec compatible 的 pair：

\[
C=\{t_i\leftrightarrow t_j\mid i,j\in\text{e-classes}(T),\ \operatorname{match}(v_i,v_j)\}.
\]

这里的关键不是这个式子本身，而是 `run_rewrites` 已先把所有可由 \(R\) 证明的等价项放进同一 e-class，所以新生成的 candidate 理论上不应再由当前 \(R\) 直接推出。源 PDF 物理页 10，Section 3.3 的未编号公式。[pdf:E10]

**6. Deriving ratio。** 为比较两个 ruleset 的证明能力，论文定义

\[
p=\frac{|B_A|}{|B|},\qquad B_A=\{b\mid b\in B,\ A\models b\}.
\]

若 \(A\) 和 \(B\) 相互的 deriving ratio 都为 1，它们对彼此规则具有同等覆盖；论文用 egg equality saturation 做有界 derivability test，运行 5 iterations，双向同时重写使单边最多可对应约 10 条 rule applications。源 PDF 物理页 14，Section 4.1.2。[pdf:E15]

**数学边界。** 这些定义支撑的是一个 bounded、heuristic synthesis procedure，而不是对“所有有用规则均可发现”的 completeness theorem。term size、cvec samples、validator、`choose_eqs` heuristic 与 equality-saturation resource limits 都会改变结果。作者在 limitations 中明确承认 complete enumeration、alpha-equivalent terms、候选打分和 conditional rules 仍有限制。源 PDF 物理页 21，Section 7。[pdf:E16]

## § 7 — 实验设计与结论

**问题 1：Ruler 是否比相近的 CVC4 synthesizer 更快、更小，同时保留 proving power？**

实验使用 boolean、4-bit bitvector、32-bit bitvector 三类 grammar，各测最大 2 或 3 个 connectives；两边均从 3 个变量、0 个常量开始，CVC4 启用其 congruence、matching、ordering filters 和 rule checker。Table 1 报告 Ruler/CVC4 的 harmonic-mean time ratio 为 0.04、ruleset-size ratio 为 0.17，即作者概括的 25× faster 与 5.8× smaller。源 PDF 物理页 13–14，Table 1 与 Section 4.1.4。[pdf:E17] [pdf:E15] 在最难的 `bv32, #Conn=3` 行，Ruler 为 630.09 s、188 rules、对 CVC4 rules 的 deriving ratio 0.98；CVC4 为 1199.53 s、1782 rules、对 Ruler rules 的 ratio 0.91。源 PDF 物理页 13，Table 1。[pdf:E17] **答案：** 在这些 bounded grammars 上，Ruler 明显减少规则数和 synthesis time，derivability 大体不降，困难 case 甚至偏向 Ruler。

**问题 2：自动规则能否在真实工具中替换专家规则？**

Herbie 实验从 155 个 benchmarks 中选出 55 个纯 rational 项，再排除 4 个反复 timeout 的 case，最终使用 51 个 benchmarks；四种配置为 None、Herbie、Ruler、Both，每种运行 30 seeds。Fig. 7 的三组 boxplots 分别比较 error improvement、output AST size 和 runtime。源 PDF 物理页 15，Fig. 7 与 Section 5.1。[pdf:E12] 作者观察到：只用 Ruler rules 时，accuracy 与 AST size 效果几乎等同专家 rules；Both 进一步降低 AST size，仍未降低 accuracy；加入 Ruler rules 没有增加 runtime。源 PDF 物理页 16，Section 5.2。[pdf:E13] Ruler 的 50 条双向规则可推出 Herbie 全部 52 条 rational rules；Herbie 只能推出其中 42 条，并漏掉 8 条。两个 absolute-value rules 被 Herbie developers 接纳并解决对应 issue。源 PDF 物理页 16，Section 5.2。[pdf:E13] **答案：** 在该 rational simplification 子系统内，Ruler 达到专家 ruleset 的端到端作用，并发现专家集合缺失的等价关系。

**问题 3：性能来自哪一部分，`choose_eqs` 的学习率如何权衡？**

Fig. 8 显示 SMT domains 中 validation 是主要耗时，其次是 rule minimization；例如 rational profile 中 validation 为 91.95 s，minimization 为 7.47 s，`run_rewrites` 为 2.81 s，rule discovery 为 1.94 s。源 PDF 物理页 17，Fig. 8。[pdf:E18] 调小 \(n\) 到 1 会更激进地压缩 ruleset，但需要更多 outer/inner loops；默认 \(n=\infty\) 通常更快、规则略多，各配置 mutual derivability 整体接近，最低 ratio 为 0.92。源 PDF 物理页 18–19，Fig. 9a 与相邻正文。[pdf:E19] [pdf:E20] **答案：** 快速批量学习与最小 ruleset 之间存在明确 trade-off，论文默认偏向 synthesis throughput。

**问题 4：term-space compaction 是否真是必要机制？**

在 \(n=1\) 的强化对照中，作者移除 `run_rewrites`。Fig. 9b 显示开启它后，time、rules learned 和 e-class 数都下降；rational 的 No-RR 版本 24 小时仍未完成，而 RR 版本约 350 s 完成。源 PDF 物理页 18，Fig. 9b。[pdf:E19] **答案：** 对作者测试的三类 domain，边学边 quotient term space 不是小优化，而是让搜索可完成的核心机制。

**问题 5：不同 validation/cvec 策略如何影响 soundness 与速度？**

Table 2 交叉比较 Cartesian interesting values、random cvec，以及 0/10/100/1000 次 random validation 和 SMT。作者用独立 SMT post-pass 检查结果；大多数 fuzzing 配置得到 sound rules，但 `bitvector-4, C=343, random=10` 出现 2 条 unsound rules，且大量配置因 incompatible cvec merge 被 Ruler 主动终止。源 PDF 物理页 19，Table 2。[pdf:E20] 作者明确强调 fuzzing 不能一般性保证 soundness；对 non-uniform bitvector-32，围绕 0、1、MIN、MAX 等 interesting constants 的 cvec 比 naive random 更有效。源 PDF 物理页 20，Section 6.2。[pdf:E21] **答案：** validation 是可插拔的，但不同 domain 对 sampling distribution 极敏感；“soundiness crash”是实用防线，不是形式保证。

**问题 6：语义变化后能否快速重新推导规则？**

作者把 rational division 从除零未定义改为 \(x/0=0\)。旧语义下，SMT validation 得到 50 rules/约 123 s，100-sample fuzzing 得到 47 equivalent rules/约 21 s；修改 interpreter 一行后，新语义用 fuzzing 得到 47 rules/18 s，再增加约 12 行 SMT support 后得到同一 47-rule set/59 s。比较新旧 ruleset 还识别出 5 条额外 incompatibilities。源 PDF 物理页 20–21，Section 6.3。[pdf:E21] [pdf:E22] **答案：** grammar/interpreter 抽象确实支持低工程成本的语义再探索，且 ruleset difference 可暴露语义变更的连锁后果。

**不可外推的范围。** 主要对比只覆盖 bounded boolean/bitvector/rational grammars；benchmark 为 single-threaded CPU；唯一真实 end-to-end case 是 Herbie 的 rational simplification；论文没有完成 integer、IEEE floating point、conditional rewrite inference、alpha-equivalent term reduction 或大规模 workload-driven enumeration。源 PDF 物理页 12、21，Sections 3.5 与 7。[pdf:E14] [pdf:E16]

## § 8 — Take-aways

**5 句话：**

1. Ruler 的主要贡献是把已学 ruleset 从“最终输出”改造成压缩后续 term/candidate search 的动态 congruence。源 PDF 物理页 2、6，Fig. 1 与 Fig. 4。[pdf:E02] [pdf:E09]
2. e-graph 负责共享和 quotient，cvec 负责把可能等价的 e-classes 聚到一起，validator 才负责最终 soundness。源 PDF 物理页 8–10，Sections 3.2–3.3。[pdf:E06] [pdf:E07] [pdf:E10]
3. 对 CVC4 的 bounded comparison 支持“更快、更小、derivability 不降”的 claim，但它不是跨所有 rewrite domains 的普遍定律。源 PDF 物理页 13–14，Table 1。[pdf:E17] [pdf:E15]
4. Herbie case study 说明自动规则不仅能复现专家 ruleset 的作用，还可能找到多年遗漏、真正影响用户输出的规则。源 PDF 物理页 15–16，Fig. 7 与 Section 5.2。[pdf:E12] [pdf:E13]
5. 该框架最难的工程点最终落在 validator 和 sampling distribution，而不是 e-graph API 本身。源 PDF 物理页 17–20，Figs. 8–9 与 Table 2。[pdf:E18] [pdf:E19] [pdf:E20] [pdf:E21]

**3 句话：**

1. Ruler 用 equality saturation 让 rule inference 在一个不断收缩的 quotient space 上进行。[pdf:E02] [pdf:E09]
2. 实验表明这种反馈能显著降低 synthesis cost，并在 rational case 中达到专家级 end-to-end 效果。[pdf:E12] [pdf:E13] [pdf:E17] [pdf:E19]
3. 但 domain-general 应理解为接口可插拔，而不是每个 domain 都已有廉价、sound、coverage 足够的 validator。[pdf:E10] [pdf:E20] [pdf:E21]

**1 句话：** Ruler 最值得带走的思想是：让正在学习的知识立即改变下一步搜索空间，而不是等搜索结束后再做去重。[pdf:E02] [pdf:E09]

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标 domain 能提供一个既足够 sound、又足够便宜的 `is_valid`，并且 cvec 的取值分布能把危险的 false equivalence 暴露出来。** 这是失败代价最大的假设，因为论文明确规定 Ruler 输出的 soundness 取决于 `is_valid` 的 soundness；cvec match 只产生“likely valid” candidates，不能代替证明。源 PDF 物理页 10，Section 3.3 Validation。[pdf:E10]

若该假设不成立，一条 unsound rule 会被加入 \(R\)，随后 equality saturation 会把它传播到大量 e-classes，导致错误等价关系同时污染 term compaction、candidate generation 和最终 ruleset。论文观察到这种错误常被“amplify”为 incompatible cvec merge 并触发 crash，但作者也明确说 fuzzing alone cannot guarantee soundness；Table 2 还实际出现过未立即 crash 的 unsound configuration。源 PDF 物理页 19–20，Table 2 与 Section 6.2。[pdf:E20] [pdf:E21]

论文给出的正面证据是分层的：boolean 与 bitvector-4 可用 complete cvec/model checking；bitvector-32 可用 SMT；rational 在所测 grammar 上少量 sampling 已很有效。负面信号同样明确：SMT validation 在 profile 中占主要时间，random sampling 对 non-uniform bitvector edge cases 不稳定，partial/conditional semantics 仍未解决。源 PDF 物理页 17、20–21，Fig. 8、Sections 6.2 与 7。[pdf:E18] [pdf:E21] [pdf:E16]

**基于证据的判断。** 论文的 domain-general claim 最稳妥的解释是“核心搜索与 validator 解耦”，而不是“任意 domain 都能同时得到高性能和 soundness”。真正缺少的证据是：IEEE floating point、复杂 undefined behavior、条件等价和稀有边界输入下，是否仍能找到廉价且可信的 semantic oracle。源 PDF 物理页 10、20–21，Section 3.3、Section 6.2 与 Section 7。[pdf:E10] [pdf:E21] [pdf:E16]

## § 10 — 最小复现实验

一周内最有信息量的复现，不是完整重做 CVC4/Herbie，而是验证论文最核心的 causal claim：**`run_rewrites` 是否通过 quotient term space 同时降低 time、ruleset size 和 e-class count，而不损失 derivability。** 源 PDF 物理页 18，Fig. 9b。[pdf:E19]

建议实验如下：

1. 用 Rust + `egg` 实现论文 Fig. 4/5 的最小版本，只支持 boolean grammar：变量 \(x,y,z\)，operators `~`、`&`、`^`、`|`，term size 取 2 和 3。论文原 benchmark grammar 与结果见源 PDF 物理页 13，Fig. 6 与 Table 1。[pdf:E17]
2. 对 3 个 boolean variables 使用全部 \(2^3=8\) 个 assignments 形成 complete cvec，因此所有候选可由 truth table 精确验证，不引入 SMT/fuzzing confound。论文对 small domains 使用 complete cvec/model checking 的做法见源 PDF 物理页 14，Section 4.1.3。[pdf:E15]
3. 固定相同 enumerator、candidate ordering、resource limits 和 `choose_eqs(n=1)`，只比较两版：A 为完整 Ruler；B 删除 `run_rewrites`，其余代码不变。这个 setting 对应论文最强调的 ablation。源 PDF 物理页 18，Fig. 9b。[pdf:E19]
4. 记录 wall-clock time、每轮 canonical e-class 数、candidate count、peak e-nodes、最终 rules 数；再让 A/B rulesets 相互做 equality-saturation derivability test。
5. **支持 claim 的结果：** A 在两个 term sizes 上都显著减少 e-class/candidate peak、总时间和最终规则数，同时 A、B mutual deriving ratio 为 1，所有规则通过 complete truth table。
6. **反驳 claim 的结果：** 删除 `run_rewrites` 后成本没有稳定上升，或 A 为了压缩搜索牺牲了可导出的 equivalences；若只在单一 size 上偶然更快，也不足以支持核心机制。

论文 Table 1 的 0.01/0.06 s 与 20/28 rules 可作为 sanity reference，而不应当作跨机器的硬阈值。源 PDF 物理页 13，Table 1。[pdf:E17]

## § 11 — 最强反例设计

最强反例应绕开 validator 争议，直接攻击“equality saturation 会净压缩搜索”这一机制。我会构造一个**小而可穷举的有限半环/有限域 domain**：例如 \(\mathbb{F}_3\)，grammar 含 \(+\)、\(\times\)、0、1 和 3 个变量，validator 对全部 \(3^3=27\) 个 assignments 穷举，因此 soundness 完全确定。枚举深度逐步增加到 4–5，使系统自然学习 commutativity、associativity、identity、annihilation 和 distributivity，并重点生成交替嵌套的 sum-of-products 与 product-of-sums。

攻击逻辑是：AC 与 distributivity 会让 equality saturation 在副本中产生大量等价 factorization/expansion；即使最终只把 merges 复制回 \(T\)，`run_rewrites` 本身也可能先发生 e-node explosion。论文相关工作已承认 commutativity/associativity rules 可能带来 exponential blowup，并提到限制 rule application 或 inverse transformations 作为缓解方向；limitations 也承认依赖 limits、caps 和 heuristics。源 PDF 物理页 21–22，Sections 7–8.1。[pdf:E16] [pdf:E04]

实验比较完整 Ruler 与 No-RR 版本，保持 exact validator、term budget 和 `choose_eqs` 一致，测量 saturation 副本的 peak e-nodes、peak memory、`run_rewrites` time、总 synthesis time、最终 rule count 与 mutual derivability。**真正推翻核心机制的结果**是：完整 Ruler 先 timeout/OOM，或时间与内存随深度陡增，而 No-RR 仍可完成并产生 deriving power 相当的 ruleset。这样的结果会说明 equality saturation 不是天然的 compression operator；在含强 distributive structure 的 domain，它可能先扩张证明空间，再得到少量 merges，从而使论文在 boolean/bitvector/rational 上的成功无法外推到更强代数理论。

这个反例比“换一组 random seeds 找到 unsound rule”更有力，因为它不依赖弱 validator，而是直接检验 Ruler 的核心计算机制是否在另一类可精确验证的 semantics 下反转。

## § 12 — Follow-up Research Bet

**主 idea：双语义耦合 e-graph 的 semantic-delta synthesis（语义差分合成）。**

**新的研究问题。** 不再问“给一个 interpreter，能学到哪些 rules”，而是问：给同一 grammar 的旧 interpreter \(I_0\) 与新 interpreter \(I_1\)，能否直接合成一个最小的 semantic-delta basis，解释哪些 equivalences 消失、哪些新出现、哪些更深层 terms 会受影响？这首次把 rule synthesis 从单版本 theory discovery 改成可计算的 language-semantics evolution analysis。

**核心机制与因果链。** 共享一次 term enumeration，但维护两个按相同 syntax IDs 对齐的 e-graphs \(T_0,T_1\) 和 paired cvec \((v_i^0,v_i^1)\)。对任意 term pair \((a,b)\)，不只判断“是否等价”，而是记录四态关系：两边都等价、仅旧语义等价、仅新语义等价、两边都不等价。各自的 equality saturation 先生成两套 congruence partitions；partition disagreement 再驱动下一轮 enumeration，优先组合造成 split/merge 的 operators 与 constants；最后合成两个小基 \(D^-\) 与 \(D^+\)，分别解释被移除和新产生的 equivalences。因果链是：paired semantics → partition disagreement → disagreement-guided terms → minimal delta basis → 可解释的迁移影响与高价值 regression witnesses。

这不是“原方法外面套一个 diff wrapper”。它至少改变四个基本设计变量：系统边界从一个 interpreter 变为两个；state representation 从单一 congruence 变为一对 congruences 加差分关系；data generation 从纯 size-bounded enumeration 变为 disagreement-driven enumeration；评价对象从 ruleset size/derivability 变为 held-out semantic-change coverage 和 witness minimality。

**论文特异依据。** Ruler 已把 grammar、interpreter、cvec、validator 与 equality-saturation loop 分离，提供了构造 paired engine 所需的模块边界。源 PDF 物理页 6、9–10，Fig. 4 与 Section 3.3。[pdf:E09] [pdf:E07] [pdf:E10] 更关键的是，论文只改 rational interpreter 一行，把除零从 undefined 改为 \(x/0=0\)，就得到一套不同 rules；比较新旧结果不仅发现预期的 \(x/x\leftrightarrow1\) 与 \(x/0\leftrightarrow0\) 差异，还识别出 5 条额外 incompatible rules。源 PDF 物理页 20–21，Section 6.3。[pdf:E21] [pdf:E22] 这说明“语义变化的影响”本身已经在实验中出现，但论文仍以两次独立 synthesis 后比较 rulesets 的方式处理，没有把差分作为第一类搜索对象。作者提出 workload seeding 与 stochastic enumeration，也为 disagreement-guided term generation 提供了接口依据。源 PDF 物理页 21，Section 7。[pdf:E16]

**最大研究收益与最大科学风险。** 最大收益是把 DSL/compiler semantics 修改后的影响，从人工阅读 changelog 和重跑 test suite，提升为自动生成的、可导出的 semantic-change explanation；它还可能输出最短 witness terms，帮助语言设计者理解一个局部 interpreter 改动为何改变远处的 algebraic laws。最大风险是 semantic delta 不一定存在小基：一次局部变化可能造成 dense、深层、非局部的 partition changes，paired saturation 的成本也可能接近两套 e-graph explosion 之和；若 paired basis 对 held-out depths 没有更好的解释力，独立合成后做 set difference 就足够了。

**首个可证伪实验。** 复用论文的 rational division 场景：旧语义为除零 undefined，新语义为 \(x/0=0\)。在 depth 2 terms 上学习 delta basis，在 depth 3–4 terms 上测试；baseline 是分别运行两次原始 Ruler，再对输出 rulesets 做 syntactic/set derivability difference。主要指标是 delta-basis size、对 held-out equivalence splits/merges 的 derivability coverage、最短 witness size 和总 runtime。只有当 paired method 在相同 term/validation budget 下，用更小 basis 解释更多 held-out changes，且能恢复论文报告的 5 条额外 incompatibilities，才能支持“差分 congruence 是新机制”；若 coverage 与独立 set difference 相同或更差，核心假设被反驳。源 PDF 物理页 20–21，Section 6.3。[pdf:E21] [pdf:E22]

**与论文列出的最近工作的实质区别。** Nötzli/CVC4、TASO、QuickSpec、TheSy 和 Ruler 都在单一 semantics 下寻找 rules/axioms；论文 Related Work 没有把两个 interpreter 的 congruence difference 作为 synthesis object。源 PDF 物理页 22–23，Sections 8.1–8.4。[pdf:E04] [pdf:E05] 由于这里严格不扩展检索范围，这一判断仅是**候选判断，不声称 novelty**。

**Wild-card alternative：** 用 active experimental design 替代固定 random/Cartesian cvec，在每轮选择最大化候选 e-class partition information gain 的 variable assignments，使“测哪些输入”本身成为 rule discovery 的优化变量；它改变的是 measurement/data-generation mechanism，而不是双语义表示。论文已显示 random values 与 interesting constants 在 bitvector-32 上差异显著。源 PDF 物理页 20，Section 6.2。[pdf:E21]
