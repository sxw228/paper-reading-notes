# DISC: Exploiting Data Parallelism of Non-Stencil Computations on CGRAs via Dynamic Iteration Scheduling

**作者**：Yue Liang、Di Mou、Dajiang Liu。[pdf:E01]（PDF 物理页 1，标题与作者栏）

**出处**：ICCAD ’24，October 27–31, 2024，New Jersey, USA。[pdf:E02]（PDF 物理页 1，页脚出版信息）

**年份**：2024。[pdf:E02]（PDF 物理页 1，页脚出版信息）

**DOI**：10.1145/3676536.3676734。[pdf:E02]（PDF 物理页 1，页脚 DOI）

**Zotero key**：JHNTKSKD

**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“CGRA 能否执行循环”，而是一个更窄也更硬的瓶颈：**当 non-stencil loop（非模板循环）的访存地址随 iteration variable 改变，无法像 stencil loop 那样在编译期找到稳定的 memory partitioning 时，怎样仍让多 bank SPM 并行供数，而不把每个 PE 都改造成昂贵的动态数据流处理器。**论文用 `A[i][j]`、`A[j][i]` 与 `A[i][j-1]` 说明，同一组 reference 的相对距离会随 `(i,j)` 改变，静态分 bank 很难保证无冲突。[pdf:E03]（PDF 物理页 1，Fig. 1 与 Introduction）

这个问题重要，是因为 modulo scheduling 的吞吐由 initiation interval（II，启动间隔）直接约束；PE 数量再多，如果同一周期的 load 都落到受冲突的 bank，上游供数会把并行计算压回串行。论文指出，SISO-CGRA 的保守做法是把 irregular references 分散到不同 control step，使一个 control step 只保留一个 load；代价是 II 增大。SIDO-CGRA 虽可在 PE 内推迟单个 operator，却因各 PE 的 scheduler 看不到全局 memory-reference 状态，仍会错过许多可规避冲突，同时付出分布式 scheduler 的面积与功耗。[pdf:E04]（PDF 物理页 1，Introduction 下半部）

因此，论文真正追求的是：在**不放弃 PE 内静态 operator schedule** 的前提下，把运行时自由度集中到 iteration 的发射次序上。其价值不是把整个系统改成通用乱序机，而是用一个中央窗口把 non-stencil loop 中原本被 bank conflict 吃掉的 data parallelism 找回来。

## § 2 — 前人工作与不足

论文先把设计空间拆成两个正交维度：iteration order 是静态还是动态，iteration 内 operator timing 是静态还是动态；据此形成 SISO、SIDO、DISO、DIDO 四象限。作者提出的目标象限是 DISO，即 Dynamic-Iteration and Static-Operator scheduling（动态 iteration、静态 operator），并把它概括为“中央动态调度 + PE 内静态执行”。[pdf:E05]（PDF 物理页 2，Introduction 的设计动机与贡献）

SISO 依靠 middle-end loop transformation 决定 iteration order，再由 back-end modulo scheduling 决定每个 operator 的 time step；PE 只需 FU、register file、configuration buffer 和选择网络，硬件最简单。SIDO 保留静态 iteration order，但每个 PE 增加 input queue、multi-port configuration buffer 和 operator/configuration scheduler，按运行时 operand availability 选择 operator；论文把这类分布式 scheduler 的面积概括为约为 SISO 的 2 倍。[pdf:E06]（PDF 物理页 2，Fig. 2）[pdf:E07]（PDF 物理页 2，Section 2.1）

DISO 的差异不只是“少放几个 scheduler”。作者明确写道：中央 iteration scheduler 在运行时决定 loop iteration order，而 compiler 仍静态决定 iteration 内 operator 的 time step；因此它获得跨多个 iteration、多个 memory reference 的全局视野，同时避免每个 PE 的动态调度器。论文给出的概念面积是约为 SISO 的 1.1 倍，并声称这是首次把 DISO 引入 CGRA；由于本任务只使用论文材料，这个 novelty 只能按作者原文记录，不能视为外部文献核验后的结论。[pdf:E08]（PDF 物理页 3，Section 2.1）

在 memory partitioning 一侧，论文相关工作总结了 hyperplane、lattice 和 graph-based 方法：它们依赖规则、常量 offset 的访问模式；graph folding 和 Graph-Morphing 虽面向 non-stencil，但论文认为前者随问题规模需要更多 bank，后者依赖专用 graph-processing architecture，编译与硬件成本都高。对 out-of-order execution，已有工作多在 instruction 或 task 粒度，或者属于每 PE 动态 operator 的 SIDO；本文选择同构 loop iterations、单个 PEA、静态 data path 这一更受约束的对象。[pdf:E09]（PDF 物理页 8，Section 5）

## § 3 — 重建作者的思考路径

下面是**基于论文证据的逆向重建**，不是作者逐句陈述的历史过程。

第一步，先承认静态 memory partitioning 在 variable-distance references 上没有稳定解。继续沿 SISO 路线，只能把 load 串行化，保证正确但牺牲 II；转向 SIDO，又会把动态调度逻辑复制到每个 PE，而且局部 scheduler 仍不知道别的 PE、别的 iteration 正在占用哪个 bank。

第二步，把调度对象从 operator 提升为 iteration。Cholesky 的示例很关键：5 个 iteration 进入一个 in-order-in、out-of-order-out 的 iteration buffer；在 CS3，较早的第 3 个 iteration 会与流水线中的第 2 个 iteration 冲突，因此运行时先发第 4 个；CS4 没有合法候选便发 bubble；CS5、CS6 再发第 5 与第 3 个。这里已经说明 iteration issue order 不是编译期逐周期表，而是由当时窗口内容和冲突状态决定。[pdf:E10]（PDF 物理页 3，Fig. 4）[pdf:E11]（PDF 物理页 3，Section 2.2）

第三步，为了让“选整个 iteration”仍有足够候选，先在编译期把同一 iteration 内的 memory references 顺序化。这样，一个 iteration 内不再制造同周期多 load 冲突，剩下的 bank competition 主要发生在不同 iteration 的软件流水重叠段。论文把这一点作为实现 conflict detection 的前提，而不是运行时再在 PE 内改 operator timing。[pdf:E12]（PDF 物理页 4，Section 2.3）

第四步，把系统拆成 IGE、ISE、RCE。IGE 生成 iteration variable 与地址；ISE 用 IB、RARDM、RAWDM、ISU 和 ROB 做窗口级判断；RCE 保持 conventional static-operator CGRA。这个拆法让“全局动态”只存在于发射端，而“局部静态”保留在 PEA 及其 configuration schedule 中。[pdf:E13]（PDF 物理页 4，Fig. 5）

第五步，先封住 correctness，再追求 conflict freedom。ROB 按原 iteration order fetch 和 commit；作者据此处理 WAW 与 WAR。RAW 不能只靠顺序 commit，因为 younger load 可能在 older store 尚未落入 SPM 时执行，所以 RAWDM 必须比较 IB 中候选 load 与 ROB 中较早 store，并按 ready bit 决定阻塞或 forwarding。[pdf:E14]（PDF 物理页 4，Section 3.1）流水线也因此被分成 fetch、issue、fixed-latency execution、in-order write back 四段。[pdf:E15]（PDF 物理页 4，Table 1 与相邻正文）

第六步，把 address equality 从“麻烦”变成“复用机会”。RARDM 保存最近已发射 iteration 的 references，并与 IB 候选逐项比较；相同地址的 RAR 不再访问 SPM，而是复用已在 load register 中的数据。[pdf:E16]（PDF 物理页 4，Fig. 6）论文进一步说明，重复 reference 在嵌套 non-stencil loop 中常由外层变量固定、内层变量推进产生，动态比较可避免这些重复 reference 持续占据冲突窗口。[pdf:E17]（PDF 物理页 5，Section 3.2）

第七步，对 RAW 做同样的“hazard 或 reuse”二分：候选 load 等于较早 ROB store address 且 ready=0，则该候选不能发；ready=1，则从 ROB 直接 forward，而不是等待写入再重读 SPM。[pdf:E18]（PDF 物理页 5，Fig. 7 与 Section 3.2）最后，ISU 用 pattern registers 保存已发射、未完成 iteration 在流水线 epilogue 中的规则 load-address 轨迹；候选地址与对应 control step 的在途地址比较，RAR/RAW reuse 可屏蔽本来会出现的 conflict，RAW hazard 则直接取消候选资格，arbiter 从剩余候选中选一个，否则发 bubble。[pdf:E19]（PDF 物理页 5，Section 3.3）

## § 4 — 核心 Intuition

把每个 loop iteration 看成一条**编译期已经排好时间的 memory-bank 访问轨迹**，运行时不改轨迹内部的 operator timing，只从窗口中挑一条不会与在途轨迹相撞的 iteration。中央 scheduler 因为同时看见多个候选和已发射 iteration，能做 PE-local scheduler 做不到的跨 iteration 冲突规避；相同地址则通过 RAR/RAW reuse 从轨迹中删掉。Fig. 8 的 sequential scheduling、software pipelining、pattern registers 与 arbiter 正是“局部静态、全局动态”的硬件化表达。[pdf:E20]（PDF 物理页 6，Fig. 8）

## § 5 — 具体方法与完整 Pipeline

先把边界钉死：**PE 内 operator schedule 是编译期静态形成的；iteration 的逐周期发射次序是运行时动态选择的。不存在一张由 compiler 预先写死“第 t 周期发第 k 个 iteration”的全局表。**compiler 固定的是 DFG mapping、每个 operator 的 control step、load 的顺序以及软件流水结构；运行时 ISU 才依据 candidate readiness、RAW hazard、reuse 与 bank conflict 决定发哪个 iteration，或者发 bubble。

### 编译期：形成局部静态执行模板

C loop 经 Clang 转成 LLVM IR，编译器把 memory-access analysis 与 data-path analysis 分开：address patterns 配置到 IGE，DFG 映射到 RCE；原 DFG 中作为数据源的 load 被 LR register 替代。由于 bank-to-LR 的 load 仍占一个周期，scheduler 必须把同一 iteration 的 load serially scheduled，然后做 software pipelining；memory references 在 PE 外部执行，因此 mapping 阶段不再把地址计算映射进 PE。[pdf:E21]（PDF 物理页 6，Fig. 9 与 Section 3.4）

### 运行时：从 in-order 输入窗口做 out-of-order issue

1. **Fetch。**IVG 产生 iteration variables，最多 `N` 个 AG 产生该 iteration 的 memory addresses。IB 与 ROB 都未满时，iteration 按程序顺序同时进入两者；ROB 记录其 store address。IB 因而保留 original order，但允许后续 out-of-order issue。[pdf:E13][pdf:E15]
2. **RAR comparison。**RARDM 将每个候选的 load addresses 与最近已发射 iteration 的 reference addresses 做完整地址相等比较。相等表示读同一数据，候选可通过 LR 保持/复用而取消这次 SPM read；RAR 是 reuse，不是数据 hazard。[pdf:E16][pdf:E17]
3. **RAW comparison。**RAWDM 将候选所有 load addresses 与 ROB 中更早 iteration 的 store addresses 比较。相等且 producer result 未 ready 是 RAW hazard，候选不能发；相等且 ready 则从 ROB forward，既维持依赖又消除一次 SPM read。[pdf:E18]
4. **Bank-conflict comparison。**ISU 将候选在各静态 control step 的 load 访问，与 pattern registers 中“已发射但尚未完成”的 load 轨迹对齐比较。论文正文统称比较 load addresses；从目标语义看，这里必须使用能判定同一 bank 同周期占用的地址/映射信息，而 RAR/RAW 的 equality 则是数据对象的完整地址相等。论文没有给出 byte address 到 bank index 的具体 bit slicing、真实 BRAM port mode 或逐 bank 端口真值表，因此不能把这一步自动解释成对真实双端口 BRAM 的完整合法性证明。[pdf:E19][pdf:E20]
5. **Select。**reuse 信号屏蔽可被复用的冲突，RAW hazard 排除不 ready 候选；arbiter 在剩余候选中运行时选一个，若为空则选 bubble。选中 iteration 的 load 随后按既定 sequential timing 对齐后送入 RCE。[pdf:E20]
6. **Execute。**RCE 是 static-operator CGRA；iteration 一旦发射，其执行 latency 固定，PE 内没有按 operand readiness 临时改 operator 时刻的 scheduler。[pdf:E14][pdf:E15]
7. **Write back。**结果可以 out-of-order 到达 ROB，但只按 fetch/program order 写回 SPM。[pdf:E14][pdf:E15][pdf:E18]

### RAW、WAR、WAW 分别怎样处理

- **RAW**：由 RAWDM 比较“候选 load ↔ 较早 ROB store”。producer 未 ready 时，ISU 不发该 iteration；ready 时从 ROB forwarding。[pdf:E18]
- **WAR**：younger store 即使先算完也只能留在 ROB，不能越过尚未完成的 older iteration 写 SPM；因此 older read 仍看到写前值。[pdf:E14][pdf:E15]
- **WAW**：两个同地址 store 按 ROB program order commit，最终写入次序与原程序一致。[pdf:E14][pdf:E15]

这里的 WAR/WAW 结论依赖论文的 ROB 模型与被评测 loop 形态；它不是对任意 atomics、I/O side effect、conditional store 或多 store iteration 的泛化证明。

### Cholesky 例子

在 2-bank、3-LSU 的 Fig. 4 中，SISO 因每 control step 只安排一个 load，以固定 II=3 完成 5 个 iteration 共需 15 cycles；SIDO 在 PE 内动态推迟冲突 load，需要 10 cycles；DISO 的 IB 在 CS3 越过第 3 个 iteration 先发第 4 个，CS4 发 bubble，随后发第 5 与第 3 个，9 cycles 完成。[pdf:E10]（PDF 物理页 3，Fig. 4）[pdf:E11]（PDF 物理页 3，Section 2.2）这段时序是“iteration 次序由运行时 conflict 选择”最直接的证据。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有定理、最优性证明或概率模型；核心只有一个与硬件容量相关的 software-pipelining 约束。设单个 application iteration 的 memory-reference 数为 `R`，IGE/硬件最多跟踪的 reference 数为 `N`。当 `R ≤ N` 时，minimal II（MII）与普通 CGRA 一样，由 data dependence 和 resource constraints 决定；当 `R > N` 时，论文把 MII 提高到

`MII = R - N + 1`

以缩短同时留在 pipeline epilogue 中、需要 pattern registers 保存的 reference 轨迹。[pdf:E22]（PDF 物理页 6，Section 3.4，“The II for software pipelining”）

直觉是：II 越大，相邻 iteration 的静态 load 轨迹重叠越少，中央 conflict detector 同时要记住的在途 reference 就越少；代价是基础流水吞吐下降。论文没有推导该式在任意 DFG、任意 bank-port model 下的必要性或充分性，也没有证明 arbiter 能得到全局最优 issue sequence。它证明的是一个可实现的 bounded-window heuristic：固定 iteration 内 timing，用有限 pattern state 做运行时选择。

## § 7 — 实验设计与结论

**问题 1：在统一硬件规模下，DISO 是否比 SISO、SIDO 更快？→ 实验：**三种架构都配置 4×4 PEA、8 LSUs、8-bank、总计 4 KB data memory；DISC 取 `N=8`，IB 与 ROB 同尺寸。性能用 cycle-accurate SystemC simulator，面积/功耗用 Chisel RTL、45 nm FreePDK、Design Compiler 与 PrimeTime。[pdf:E23]（PDF 物理页 6，Section 4.1）7 个 benchmark 来自线性代数与信号处理，包括 Cholesky、GE、LU、QR、Solver、Strsm、Unique。[pdf:E24]（PDF 物理页 7，Table 2）**答案：**DISC w/o reuse 相对 SISO、SIDO 的平均 speedup 分别为 2.54×、1.01×；完整 DISC 分别为 3.57×、1.41×。[pdf:E25]（PDF 物理页 7，Fig. 12 与 Section 4.4）

**问题 2：动态 data reuse 是否是实质贡献，而不是装饰？→ 实验：**加入 DISC w/o reuse 作为 ablation。**答案：**完整 DISC 相对 w/o reuse 仍有平均 1.39× speedup，说明 RAR/RAW reuse 不只减少 memory transaction，也扩大了可发 iteration 集合。[pdf:E26]（PDF 物理页 8，Section 4.4 延续段与 Fig. 13/14）

**问题 3：有限 IB 要多大？→ 实验：**IB size 从 2 扫到 32，并以 size=2 归一化。**答案：**多数 kernel 在 size=8 附近趋于收敛，QR 对更大窗口仍敏感；从性能与资源折中，作者选择 IB=8，ROB 同为 8。[pdf:E24]（PDF 物理页 7，Fig. 10 与 Section 4.2）

**问题 4：中央 scheduler 是否真的比每 PE 动态 scheduler 便宜？→ 实验：**同一 45 nm flow 比较 timing、area、power，并给出 breakdown。**答案：**三者均报告 153.85 MHz；SISO、SIDO、DISC 的面积分别为 0.97、1.51、1.05 mm²，功耗分别为 59.41、128.74、65.95 mW。[pdf:E27]（PDF 物理页 7，Table 3）DISC 相对 SISO 的总面积与总功耗增幅分别为 8.25% 与 11.01%；IB、ROB、IGE、RARDM/RAWDM、ISU 是主要新增项，而 SIDO 的 per-PE configuration scheduler 使其显著更大。[pdf:E28]（PDF 物理页 7，Fig. 11 与 Section 4.3）

**问题 5：性能是否对应更少的 bank conflict？→ 实验：**比较 SPM bandwidth utilization，并给出由 performance speedup 除以 power 得到的 normalized energy efficiency。**答案：**论文报告理想平均带宽利用率 46.4%，SISO 为 12.5%，SIDO 为 31.5%，DISC w/o reuse 为 31.8%，完整 DISC 为 44.6%；完整 DISC 相对 SISO、SIDO 的 energy efficiency 分别为 3.19×、2.75×，w/o reuse 相对 SIDO 仍为 1.97×。[pdf:E29]（PDF 物理页 8，Sections 4.5–4.6）

不得外推的范围也很明确：这些结果来自 simulator 与 45 nm synthesis/power analysis，不是 FPGA board 或 silicon measurement；benchmark 只有 7 个、且 Table 2 都呈现为规则嵌套 loop 中的单个 innermost assignment。论文没有展示真实双端口 BRAM 的 per-bank read/write legality、不同 read-during-write mode、multiple/conditional stores、cache/DRAM miss 或 variable-latency PE operator 下的结果。

## § 8 — Take-aways

### 5 句话

1. non-stencil loop 的核心障碍不是缺 PE，而是静态 partitioning 无法稳定消除随 iteration 改变的 bank conflict。[pdf:E03]
2. DISC 把动态性放在中央 iteration scheduler，把 operator timing 留给编译器和静态 RCE，这就是“全局动态、局部静态”。[pdf:E05]
3. iteration 按原顺序进入 IB/ROB，但由 ISU 根据 bank conflict、RAW readiness 和 reuse 状态 out-of-order issue；没有固定的编译期逐周期 iteration 表。[pdf:E20]
4. RAW 由 RAWDM 的 stall/forwarding 处理，WAR 与 WAW 由 ROB in-order commit 处理，RAR 只是减少 reference 的 reuse。[pdf:E14][pdf:E18]
5. 在论文的 7 个 kernel 与综合模型中，DISC 以接近 SISO 的面积功耗获得高于 SIDO 的平均性能和能效，但这仍不是对任意 non-stencil 程序或真实 BRAM 端口行为的证明。[pdf:E28][pdf:E25]

### 3 句话

1. compiler 决定 iteration 内每个 operator 何时执行，runtime scheduler 决定下一次发哪个 iteration。
2. 地址相等既可能是 RAW hazard，也可能变成 RAR/RAW forwarding；地址映射到同 bank 但数据不同则只能靠窗口选序或 bubble。
3. 论文最有说服力的部分是把 correctness ordering、address reuse 与 bank-conflict arbitration 放在同一个中央窗口里；最缺的是更一般 memory semantics 和物理 memory-port 验证。

### 1 句话

DISC 不是“整机离线静态排程”，而是**静态 operator trajectory 上的运行时 iteration out-of-order issue**。[pdf:E30]（PDF 物理页 8，Conclusion）

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标 non-stencil kernel 能被规约为同构、固定 latency、静态 operator schedule 的 iterations，而且跨 iteration 的全部相关 memory semantics 可以由“候选 loads + ROB 中按序登记的 store address/ready/data”完整表示。**论文的 RCE 固定 latency、ROB entry 结构和 RAWDM 比较逻辑都建立在这一模型上。[pdf:E15][pdf:E18][pdf:E21]

这个假设一旦不成立，后果不是“少一点 speedup”，而可能是错误。multiple stores、conditional store、may-alias pointer、atomic/read-modify-write、I/O side effect、exception、variable-latency operator，都会使“一个 iteration 的完成”和“一个可按序 commit 的 store”不再等价；仅比较 candidate load 与较早 store 也未必覆盖所有 RAW/WAR/WAW。论文给出的 7 个 benchmark 都以单个 innermost assignment 展示，能说明模型适合这些 kernel，却不能证明它覆盖作者标题所指的整个 non-stencil computation 类。[pdf:E24]

另一个与该假设绑定的边界是 memory-port model。论文展示的是 multi-bank SPM、crossbar、load-address pattern comparison 和 ROB-delayed stores；它没有给出真实双端口 BRAM 的端口数、读写同址语义或逐 bank 形式化检查。因此，“ISU 判为 conflict-free”应理解为**在论文抽象 memory model 下合法**，不能自动升级为具体 FPGA BRAM primitive 的完整合法性证明。

## § 10 — 最小复现实验

一周内最值得做的是一个小型 cycle-level simulator，而不是重写整套 CGRA RTL。

数据先用 Fig. 4 的 5 个 Cholesky iterations、2 banks、3 LSUs，随后从 Table 2 再选 Cholesky 与 Unique 的小尺寸实例。实现四个部件：按原序生成 address trace 的 IGE、容量可设为 2/4/8 的 IB、保存 pattern registers 并运行 candidate comparator/arbiter 的 ISU、带 store address/ready/data 与 in-order commit 的 ROB；再分别打开/关闭 RAR、RAW reuse。PE 计算可用固定 latency 的函数模型，最终数组结果与串行软件 reference 比对。

测量四项：每周期 issue 的 iteration ID、bubble 数、每 bank 每周期访问、总 cycles；同时记录 RAW stall、ROB forwarding、RAR reuse 次数。最初的 sanity check 应复现论文示例的 SISO 15 cycles、SIDO 10 cycles、DISO 9 cycles。[pdf:E11]之后在不同 cyclic bank mapping、IB size 和 problem size 下比较固定 iteration order、operator-local greedy、DISC 三种策略。

支持 claim 的最低标准是：所有结果与串行 reference 一致，DISO 的 issue trace 确实随 runtime address/conflict 改变，并在多数配置下降低 cycles 或提高 bank utilization。反驳标准是：出现任何 dependency mismatch，或者在消除 RAR/RAW reuse 后，iteration-wise scheduler 对合理映射普遍不能超过 operator-local baseline，说明论文收益主要来自特定 reuse pattern，而非 DISO 本身。

## § 11 — 最强反例设计

构造一个“**同 bank、不同地址、合法候选总在窗口之外**”的 loop family。设 IB size 为 `M`，让连续 `M` 个 ready iterations 的下一条静态 load 在相同 control step 都映射到同一 hot bank，但 row address 全部不同，因此 RAR/RAW equality reuse 完全无效；第 `M+1` 个 iteration 才映射到空闲 bank。再加入一条跨越多个 iteration 的 RAW chain，使部分候选即使 bank 不冲突也因 producer 未 ready 被 RAWDM 排除。

这会同时攻击 DISC 的两个机制：有限 IB 看不到真正无冲突的 iteration，而“相同地址复用”无法缓解“同 bank 不同数据”的冲突。由于 DISC 以 whole iteration 为发射单位，只要该 iteration 的某个静态 load 与 epilogue 冲突，整个 iteration 就不能发；SIDO 则可能只推迟冲突 operator、继续推进其余 operator。论文自己也承认 IB size 决定动态检测空间，且性能随 IB 增大后才趋于收敛。[pdf:E24]

实验应 sweep `M`、bank 数、每 iteration reference 数、hot-bank 周期和 RAW distance，并分别采用 single-port、simple dual-port、不同 read/write mode 的显式 bank model。若在保持相同 PEA 和总 memory ports 时，SIDO 稳定胜过 DISC，且 DISC 的带宽利用率随 `M` 呈阶跃式崩溃，就说明论文 1.41× 平均优势更可能来自所选 benchmark 中“窗口内候选密度 + 地址复用率”，而不是 iteration granularity 对 non-stencil 的普适优势。[pdf:E25][pdf:E29]

## § 12 — Follow-up Research Bet

### 主押注：运行时 value-sharing hypergraph 驱动的跨-iteration 融合

**新研究问题。**能否不再把 RARDM/RAWDM 发现的地址相等关系只当成一个 `reuse/hazard` bit，而把整个 IB window 表示成动态 value-sharing hypergraph：vertex 是 iteration 的 load/store value，RAR equality 形成一对多共享 hyperedge，RAW producer-consumer 形成有向 edge，然后以“value-sharing cluster”而不是单个 iteration 作为调度和映射对象？

**首次可能实现的能力。**一个值从 SPM 或 ROB 取出一次后，可同时 multicast 给多个 iteration consumer；多个静态 DFG 片段被组成一个 fused super-iteration，在同一个 PEA 的不同区域/时段执行。系统不只是在既定 iteration 之间换顺序，而是动态改变 execution unit 的边界，把运行时发现的跨 iteration value locality 转化为 compute-level fusion。

**因果链。**DISC 已能比较候选与最近已发射 references，并能从 ROB forward ready RAW data；论文的 reuse ablation 带来平均 1.39× speedup，说明 address equality 不是边缘现象。[pdf:E16][pdf:E17][pdf:E18][pdf:E26]将这些局部 equality 扩展为 window-wide hypergraph，可把“删掉一条 memory reference”升级为“一个 producer 驱动多个 consumer”，进一步减少 SPM transaction、register reload 和重复 compute，并为多 iteration 的联合 mapping 提供新并行度。

**改变的基本设计变量。**调度对象从 iteration 变为 value-sharing cluster；状态表示从 address list/pattern registers 变为时间化 dependence hypergraph；hardware mapping 从单个固定 DFG 的重复发射变为多个 DFG fragment 的联合映射；评价对象也从 bank utilization 扩展为 value multicast fanout、cluster occupancy 与 fused-PEA utilization。至少同时改变了状态表示、硬件映射、系统边界和评价对象。

**论文特异依据。**方法侧，RARDM、RAWDM、ROB forwarding 和 IB 已经提供形成动态 edge 的原始信息；实验侧，完整 DISC 的平均 SPM bandwidth utilization 为 44.6%，接近论文给出的 46.4% ideal，而 reuse 仍显著提升 performance，这暗示下一步收益未必来自继续逼近 memory bandwidth，而可能来自把 reuse 关系提升为新的 compute organization。[pdf:E26][pdf:E29]

**最大收益与最大风险。**收益是让 irregular loop 的运行时 data reuse 直接改变 PEA 上的计算拓扑，可能突破“一周期最多 issue 一个完整 iteration”的上限；风险是 online cluster formation、multicast routing、register pressure 与联合 mapping latency 可能吞掉收益，而且 reuse graph 稀疏时 fused packet 会浪费 PE。ordered commit 还必须从单 iteration ROB entry 扩展到 cluster 内多个 store 的精确版本顺序。

**首个证伪实验。**先不做 RTL，只从 7 个 benchmark 的动态 address trace 构造 `M=8` 的滑动窗口 hypergraph。比较三组 cycle model：原 DISC；只减少相同数量 SPM reads、但仍逐 iteration issue 的 control；真正以 cluster 共同 multicast 并联合占用 PEA 的模型。若 cluster 模型在 SPM transaction 数与 control 相同的条件下仍提高 PEA utilization 和总吞吐，才能把收益归因于 hypergraph execution，而非单纯 memory-traffic reduction；若不能，主机制被证伪。

**与最近工作的实质区别。**按本文第 5 节的描述，SIDO 在 PE 内动态选 operator，DISC 在 window 内选 iteration，Graph-Morphing 则依赖专用 graph-processing execution model；本押注的对象是单个静态 PEA 上由运行时地址相等关系生成的跨-iteration value hypergraph。由于没有使用外部全文检索，这只是 evidence-constrained candidate，不声称已完成 novelty 排查。[pdf:E09]

**Wild-card alternative：**把 data placement 本身变为运行时状态，利用 IB 暴露的未来 address window 联合求解 iteration order 与 versioned bank remapping，使 non-stencil array 在执行过程中改变 bank topology；这条路线改变的是物理数据布局与地址翻译，而不是 value-sharing graph。
