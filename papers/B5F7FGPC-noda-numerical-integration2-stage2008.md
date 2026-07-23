# Numerical Integration by the 2-Stage Diagonally Implicit Runge-Kutta Method for Electromagnetic Transient Simulations

- 作者：Taku Noda、Kiyoshi Takenaka、Toshio Inoue
- 出处：*IEEE Transactions on Power Delivery*, Vol. 24, No. 1
- 年份：2009（论文首页注明首次在线发表于 2008 年）
- DOI：10.1109/TPWRD.2008.923397
- Zotero key：B5F7FGPC

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“EMT 仿真会不会发散”这么宽泛的问题，而是一个更具体、更棘手的数值伪影：EMTP 常用的 trapezoidal method 虽然是二阶、A-stable，但当电感电流或电容电压发生突变时，会把不可解析的高频分量变成正负交替、幅值不衰减的数值振荡。对含半导体开关、限幅器、传输线传播和非线性磁化支路的 EMT 仿真，这种振荡很容易被误认成真实过电压或高频暂态。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

当时的工程补救是 critical damping adjustment（CDA）：平时用 trapezoidal method，检测到突变时临时切换到 backward Euler。它在被正确触发时能耗散伪高频，但“先检测事件”本身就是弱点。突变经过 distributed-parameter line 传播后，接收端未必存在一个容易编码识别的本地开关事件；控制器限幅造成的阶跃也可能只表现为仿真计算结果，而不是预先登记的事件。作者因此追求一种不依赖事件检测、在积分公式层面就有 stiff decay 的方法。[pdf:E01]（PDF 物理页 1，Section I）

论文的核心技术 claim 是：把 two-stage diagonally implicit Runge-Kutta（2S-DIRK）用于 EMT，可以保持与 trapezoidal method 接近的二阶精度和 A-stability，同时使无限刚性模态在离散时间中衰减到零，从而不产生持续的伪数值振荡；代价是每个时间步要解两次电路方程。[pdf:E05]（PDF 物理页 5，Eqs. (48)–(52) 与 Section III-B）

## § 2 — 前人工作与不足

Dommel 的 EMTP 路线先把电感、电容离散成 Norton 等效支路，再组装和求解代数电路方程；trapezoidal method 因公式简单、二阶且 A-stable，成为基础积分方法。问题是 A-stable 只保证物理稳定电路不会因步长而发散，并不保证被激发的无限刚性模态会衰减：trapezoidal method 在该极限的放大因子趋于 \(-1\)，因此每步翻转符号而不减幅。[pdf:E05]（PDF 物理页 5，Eqs. (46)–(52)）

Marti 与 Lin 的 CDA 用 backward Euler 覆盖突变附近的步长。它的 stiff decay 能消除振荡，但必须识别 switching event、源值突变或分段线性非线性元件工作点变化；传播到别处的波头、控制系统输出的跳变等并不容易被完整枚举，检测逻辑还增加执行开销。[pdf:E01]（PDF 物理页 1，Section I）

Gear-Shichman 是电子电路分析中使用的两步 implicit/BDF 方法，同样有 stiff decay，但需要多步历史，内存和启动处理不如 one-step 方法直接。一般的 two-stage implicit Runge-Kutta 又会把两个 stage 耦合成 \(2n\) 个联立方程。2S-DIRK 的“diagonally”选择相同的对角系数，把问题拆成顺序求解两次 \(n\) 维电路方程，保留 one-step 属性。[pdf:E02]（PDF 物理页 2，Section II-A）

论文真正新增的是把已有的 2S-DIRK 数值积分结构改写成适用于 EMT companion model 的线性/非线性电感、电容公式，并用频率响应、stability function 和三个 CDA 对比电路说明工程价值；它不是发明 DIRK，也没有建立新的电路求解框架。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Section II）

## § 3 — 重建作者的思考路径

以下是基于论文背景的逆向重建，不是作者逐字陈述。

第一步，工程现象已经表明“物理稳定但波形振铃”与普通发散不同。既然 trapezoidal method 是 A-stable，问题就不应继续只看 absolute stability region，而要看极短时间常数在离散系统中的剩余放大因子。

第二步，backward Euler 能压掉振铃，说明所需性质不是更大的稳定域，而是 stiff decay；但 CDA 把这种性质附着在事件检测器上，检测失败就失效。因此更自然的目标是：让每一步的积分方法本身都具有 stiff decay。

第三步，EMT 的计算成本由“动态元件离散后的矩阵组装、factorization 和 substitution”决定。一个通用 fully implicit 两阶段方法若要求一次求解 \(2n\) 维耦合系统，工程代价太高；一个多步 BDF 又会增加历史状态和切换后的启动复杂性。于是 one-step、二阶、A-stable、stiff-decaying、stage 可顺序解耦成为筛选条件，2S-DIRK 正好满足。[pdf:E02]（PDF 物理页 2，Section II-A）

第四步，要让该方法进入 EMTP 类程序，必须把抽象 ODE stage 变成电感、电容都能 stamp 的 \(G\parallel J\) companion model，并确认两个 stage 是否能共享矩阵结构。线性元件两阶段的 conductance 相同，允许复用 factorization；非线性元件的局部斜率会变，必要时仍要重分解。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Fig. 1 与 Eqs. (10)–(38)）

最后，作者用“解析放大因子 → 简单 RC/RL 电路 → CDA 容易成功的案例 → CDA 检测失败的传输线案例”逐层证明：优势来自积分器的 stiff decay，而不只是某个事件检测规则碰巧更好。

## § 4 — 核心 Intuition

2S-DIRK 可以直观理解为：在一个完整时间步内顺序做两次具有 backward-Euler 形态的隐式更新，再用特定系数组合，恢复二阶精度。这样既让无限快的伪模态每步衰减到零，又让低频、物理相关的波形精度接近 trapezoidal method；代价是每步两次网络求解。[pdf:E02][pdf:E05]（PDF 物理页 2、5）

## § 5 — 具体方法与完整 Pipeline

以含线性 \(R\)、\(L\)、非线性饱和电感和理想开关的 EMT 网络为例，单个时间步的流程是：

1. 设完整步长 \(h=t_n-t_{n-1}\)，取 \(a=1-1/\sqrt 2\)，内部 stage 步长为 \(\tilde h=ah\)，中间时刻为 \(\tilde t_n=t_{n-1}+\tilde h\)。[pdf:E02]（PDF 物理页 2，Eq. (2)）
2. 第一 stage 把所有动态元件 stamp 成 \(G\parallel J\) 等效支路，在 \(\tilde t_n\) 求一次网络方程，得到中间电压、电流和状态。线性电感的 \(G=\tilde h/L\)，线性电容的 \(G=C/\tilde h\)；两者的 history source 由上一步状态给出。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eqs. (7)–(17)）
3. 用 \(\alpha=-\sqrt2\)、\(\beta=1+\sqrt2\) 把旧状态与第一 stage 状态转换成第二 stage 的 history state，即 \(\tilde y_{n-1}=\alpha y_{n-1}+\beta\tilde y_n\)。[pdf:E02]（PDF 物理页 2，Eq. (4)）
4. 在 \(t_n\) 用相同的隐式形态再求一次网络方程，得到 \(y_n\)。对线性 \(L/C\)，两阶段 conductance 相同，因此元件本身不要求重新 factorize 全局 conductance matrix；对非线性电感 \(\phi(i)\) 或非线性电容 \(q(v)\)，两个 stage 的切线斜率可能不同，仍可能触发 refactorization。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eqs. (22)–(38)）
5. 理想开关不能简单地在两个 stage 之间瞬时翻转。作者建议开关动作从一个完整步点开始、到下一个步点结束：开断时，中间 stage 用由旧电流线性插值得到的电流源；闭合时用旧开关电压线性插值得到的电压源。[pdf:E10]（PDF 物理页 10，Appendix B，Eqs. (57)–(58)）

计算依赖上，两个 stage 必须串行，因为第二 stage 的 history state 依赖第一 stage 结果；单个 stage 内仍可沿原 EMT 稀疏网络求解路径执行。论文使用 Sparse Tableau Approach 和基于 \(LU\) decomposition 的求解器；没有报告多核并行、FPGA 映射、固定点位宽、流水线时序或实时硬件平台，因此不能把本文直接解读成 FPGA 实现方案。[pdf:E07][pdf:E09]（PDF 物理页 7、9，Section IV 与计算量讨论）

## § 6 — 核心数学推导（无形式化数学则跳过）

对一般 ODE

\[
\frac{dy}{dt}=f(t,y),
\]

2S-DIRK 的两个隐式 stage 是

\[
\tilde y_n=y_{n-1}+\tilde h f(\tilde t_n,\tilde y_n),
\qquad
y_n=\tilde y_{n-1}+\tilde h f(t_n,y_n),
\]

中间通过

\[
\tilde y_{n-1}=\alpha y_{n-1}+\beta\tilde y_n,
\quad
a=1-\frac1{\sqrt2},\quad
\alpha=-\sqrt2,\quad
\beta=1+\sqrt2
\]

连接。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(5)）两个隐式方程都长得像 backward Euler，所以现有求解器可以把它理解成“同一个隐式网络求解核心调用两次”；特定系数组合抵消一阶截断误差，使整体达到二阶。

映射到线性电感 \(di/dt=v/L\) 后，第一和第二 stage 分别是

\[
\tilde i_n=\frac{\tilde h}{L}\tilde v_n+i_{n-1},
\qquad
i_n=\frac{\tilde h}{L}v_n+\tilde i_{n-1}.
\]

因此两阶段都对应 \(G=\tilde h/L\) 的 Norton 支路，只是 history current 不同。[pdf:E02]（PDF 物理页 2，Eqs. (7)–(11)）线性电容同理得到 \(G=C/\tilde h\)。这件事的工程意义是：对线性网络，第二次求解通常可复用同一稀疏矩阵 factorization，只做新的右端项和 backward substitution。

论文用 pure integrator 的 frequency response 检查精度。2S-DIRK 的归一化响应为

\[
H_{\mathrm{2S-DIRK}}(j\omega)
=\frac{\sqrt2-1+e^{-j\omega/\sqrt2}}
{\sqrt2(1-e^{-j\omega})}.
\]

Fig. 3 表明其幅值误差略优于 trapezoidal，但相位误差略差；trapezoidal 因时间对称而相位误差为零。作者据此只得出“精度几乎相同或略好”，并没有证明对所有 EMT 网络都严格更准。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Fig. 3 与 Eq. (42)）

更关键的是 test equation \(dy/dt=\lambda y\) 的 stability function。令 \(z=h\lambda\)，论文给出

\[
R_{\mathrm{2S-DIRK}}(z)=\frac{1+\sqrt2az}{(1-az)^2},
\quad
R_{\mathrm{BE}}(z)=\frac1{1-z},
\quad
R_{\mathrm{TR}}(z)=\frac{2+z}{2-z}.
\]

当 \(\operatorname{Re}\lambda\to-\infty\) 时，2S-DIRK 与 backward Euler 的 \(R\to0\)，无限快模态被压掉；trapezoidal 的 \(R\to-1\)，于是 \(y_n=-y_{n-1}\)，形成不衰减的正负交替。这就是“stiff decay”相对于仅有 A-stability 的物理含义。[pdf:E05]（PDF 物理页 5，Eqs. (48)–(52)）

## § 7 — 实验设计与结论

**问题 1：2S-DIRK 的低频/暂态精度是否至少不逊于常用方法？**  
实验：对 \(R=100\,\Omega\) 的串联 RC 电路施加从 0 V 上升到 1 V 的输入，取 \(C=1\,\mu\text{F}\) 与 \(10\,\mu\text{F}\)，对应 \(\tau=0.1\) ms 与 1 ms；步长均为 0.1 ms，并与解析解比较。[pdf:E06]（PDF 物理页 6，Figs. 4–5）  
答案：在 \(\tau=h\) 和 \(\tau=10h\) 两种情况下，2S-DIRK 的偏差最小，trapezoidal 次之，Gear-Shichman 和 backward Euler 更大；但差异只来自两个一阶 RC 例子，不能外推为复杂 EMT 网络上的统一误差排序。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Figs. 5–6）

**问题 2：发生电感电流中断时，stiff decay 是否真的消除伪振荡？**  
实验：\(R=100\,\Omega\)、\(L=10\) mH 的串联 RL 支路由 1 A 电流源激励，电流在 1.0–1.1 ms 内降到 0，步长为 0.1 ms；将四种积分方法与解析解比较。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Figs. 7–8）  
答案：2S-DIRK 与 backward Euler 正确复现尖峰及随后归零；Gear-Shichman 有偏大的峰值和一次 undershoot；trapezoidal 在约 \(+200/-200\) V 之间持续交替。该实验直接验证了 \(R\to0\) 与 \(R\to-1\) 的差别。[pdf:E07]（PDF 物理页 7，Fig. 8）

**问题 3：在 CDA 能识别事件时，2S-DIRK 会不会破坏正常结果？**  
实验：Test Circuit 1 是 100 V r.m.s.、60 Hz 半波整流器，含 10 mH、100 \(\Omega\) 和 20 V 直流源；Test Circuit 2 是用于 77-kV 励磁涌流的简化饱和电抗器网络，使用分段线性 \(\phi-i\) 曲线。两者步长均为 0.1 ms。[pdf:E08]（PDF 物理页 8，Figs. 9–13）  
答案：2S-DIRK 与 CDA 的曲线在图中无法区分，而裸 trapezoidal 在半波整流器中出现持续振荡；Test Circuit 2 的 trapezoidal 曲线未展示，只由正文报告同类失效。因此这里支持“2S-DIRK 不劣于成功触发的 CDA”，但缺少定量误差和统计重复。

**问题 4：CDA 检测不到传播后的突变时会怎样？**  
实验：Test Circuit 3 用 100 V step source 经无损 distributed-parameter line 激励 1000 pF 电容；线路 \(Z_0=30\,\Omega\)、波速 \(1.73\times10^8\) m/s、长度 10 km，步长 1 \(\mu\)s。作者测试的三个 EMTP 版本都未能在接收端识别传播后的突变。[pdf:E08]（PDF 物理页 8，Fig. 14 与正文）  
答案：2S-DIRK 给出干净的阶跃响应和瞬态电流；CDA 结果在每次到达波头后出现衰减振铃。这个案例最有力，因为它把两者差别定位到“积分器固有 damping”与“事件检测触发 damping”。[pdf:E09]（PDF 物理页 9，Fig. 15）

**成本问题：代价是否可接受？**  
论文只做 operation count，没有给 wall-clock benchmark。线性动态元件每步更新中，trapezoidal 需 1 次加法、1 次乘法和 1 次电路求解；2S-DIRK 需 1 次加法、2 次乘法和 2 次电路求解。若 CDA 很少触发，2S-DIRK 计算时间预计略低于 trapezoidal+CDA 的两倍；若 PWM 场景频繁触发 CDA，两者时间会接近。由于没有具体网络规模、稀疏度、处理器或实测时间，这只能算复杂度论证，不是实时性能证据。[pdf:E09]（PDF 物理页 9，Fig. 15 后的计算量讨论）

## § 8 — Take-aways

**5 句话：**

1. 论文把 EMT 中的持续伪振荡准确归因于 trapezoidal method 缺少 stiff decay，而不是缺少 A-stability。[pdf:E05]
2. 2S-DIRK 用两个可顺序求解的 implicit stage，在二阶精度与高频耗散之间取得了比 backward Euler 更合适的平衡。[pdf:E02][pdf:E05]
3. 线性电感、电容的两阶段 conductance 相同，使第二次网络求解有机会复用 factorization；非线性工作点变化时则未必。[pdf:E02][pdf:E03]
4. 简单 RC/RL 和三个 CDA 对比电路支持作者的机制解释，尤其是 distributed line 传播后的事件检测失败案例。[pdf:E06][pdf:E07][pdf:E08][pdf:E09]
5. 论文没有证明真实大规模 EMT、实时 CPU 或 FPGA 上的总成本，也没有解决 off-grid switching event 的精确定位。

**3 句话：**

1. 2S-DIRK 的价值不是“绝对更准”，而是用接近 trapezoidal 的精度换来对无限刚性伪模态的内生衰减。
2. 它避免依赖 CDA 的事件检测，但每步固定增加第二次网络求解。
3. 能否成为实时 EMT/FPGA 内核，取决于 factorization 复用、off-grid 事件处理和有限精度误差，而这些都超出本文证据。

**1 句话：**  
这是一篇把“检测到突变才加阻尼”改成“积分器每一步都具备 stiff decay”的 EMT 数值方法论文。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**真实开关事件可以准确落在完整时间步边界，并允许用一个时间步内的线性插值来表示开关过渡。** 作者明确写道，2S-DIRK 假设相邻完整步之间的状态连续，因此理想开关应从一个步点开始、在下一个步点结束；中间 stage 的开关电流或电压取旧值的 \(1/\sqrt2\)。[pdf:E10]（PDF 物理页 10，Appendix B，Eqs. (57)–(58)）

这不是无关紧要的实现细节。若开关命令实际发生在 \(t_{n-1}+\theta h\) 且 \(\theta\neq0\)，强制对齐到网格会造成最多一个步长的时刻误差；跨一步的人工平滑还会改变理想开关释放或吸收能量的瞬时路径。于是“没有振铃”可能同时包含两种效应：2S-DIRK 的 stiff decay，以及开关事件被规则化后的额外平滑。

论文的 RC/RL 基准和 Appendix B 都把事件安排在步点上，Test Circuit 3 又是外部 step 经线路传播，而不是大量异步 PWM 边沿。论文没有扫描事件相位、没有报告事件定位误差，也没有检查 discrete energy balance。因此，本文充分证明的是“在其事件表示下不产生持续伪振荡”，而不是“任意异步开关 EMT 都同时保持二阶时序精度和正确能量交换”。

## § 10 — 最小复现实验

一周内可完成一个不依赖商业 EMTP 的最小复现，目标只验证两个核心点：stiff decay 机制和事件相位敏感性。

1. 用 Python、Julia 或 MATLAB 实现四个积分器：2S-DIRK、trapezoidal、backward Euler、Gear-Shichman。先复现论文的 \(R=100\,\Omega\)、\(C=1\,\mu\text{F}\)、\(h=0.1\) ms RC 算例，以及 \(R=100\,\Omega\)、\(L=10\) mH、1 A 中断的 RL 算例。[pdf:E06][pdf:E07]
2. 对 RC 算例测量相对解析解的 \(L_\infty\) 与 RMS error；对 RL 算例测量事件后 20 步内的最大伪振荡、相邻样本符号翻转次数和残余能量。
3. 再把 RL 中断时刻从恰好落在网格点改成 \(t_e=t_k+\theta h\)，扫描 \(\theta=0,0.1,\ldots,0.9\)。2S-DIRK 分别采用论文的一步插值和一个带 root localization 的参考实现。
4. 支持论文 claim 的最低结果是：在 \(\theta=0\) 时，2S-DIRK 的残余伪振荡随步推进到机器精度，而 trapezoidal 保持近似等幅交替；同时 2S-DIRK 的 RC 误差不高于 trapezoidal 同一量级。
5. 反驳或显著收窄 claim 的结果是：off-grid 扫描中，论文式开关表示产生不随 \(h^2\) 收敛的事件时刻误差、明显的能量偏差，或在某些 \(\theta\) 下恢复持续振荡。

这个复现不需要重建作者的 Sparse Tableau 求解器，也不需要完成 FPGA 映射；它直接测试决定论文结论的数值机制。

## § 11 — 最强反例设计

最强攻击不是再找一个“CDA 忘了触发”的案例，而是构造一个 **off-grid 异步开关驱动的近无损混合系统**，检查 2S-DIRK 是否把真实高频能量也当成伪模态抹掉。

具体做法是：建立理想开关、极小电阻 \(R\)、电感 \(L\)、电容 \(C\) 和一段无损 distributed line 组成的网络，使开关在 \(t_k+\theta h\) 动作；选择参数让 LC 固有频率处在 Nyquist frequency 的 0.2–0.45 倍，而不是无限刚性极限。用高精度 event-located implicit solver 作为参考，扫描 \(\theta\)、\(h\)、线路时延与初始储能，比较：

- 开关时刻和首个峰值误差；
- 每次切换前后的离散能量不平衡；
- 真实 LC 振荡的幅值/相位衰减；
- 伪交替模态是否消失；
- 为达到同一误差所需的网络求解次数。

若 2S-DIRK 在抑制 \((-1)^n\) 伪模态的同时，系统性地过度衰减参考解中应保留的高频物理振荡，或者其误差主要由一步开关平滑而非积分截断误差决定，那么“几乎同等精度且对任何输入无伪振荡”的表述必须收窄到特定频带和事件表示。[pdf:E05][pdf:E10]（PDF 物理页 5、10）

## § 12 — Follow-up Research Idea

**候选方向：event-located、energy-accounted 的 hybrid 2S-DIRK EMT 内核。** 这里未做完整相关工作检索，因此不声称 novelty。

**(a) 未满足需求。** 现有论文在积分器层面消除了 stiff numerical ringing，却把理想开关事件约束为“步点发生、跨一步完成”。下一代实时 EMT 尤其是 PWM converter 和多速率控制耦合，需要同时满足：异步事件时刻准确、真实高频能量不过度耗散、伪无限刚性模态快速衰减。

**(b) 为什么可能有本领域价值。** 电力系统 EMT 研究通常看重数值稳定性、可验证误差、真实设备或实时平台上的可执行性。若一个方法能在不回退到全局小步长的情况下，给出事件时刻、能量交换和 stiff decay 的联合保证，就改变了“精度与振铃只能二选一”的问题定义。

**(c) 可借鉴的相邻方法。** 可把 hybrid systems 的 root finding/dense output、port-Hamiltonian 或 discrete-gradient 的 energy accounting，与 DIRK 的 L-stable stage 结合；事件只在受影响的局部子网络定位，其余线性网络继续复用 factorization。这里的关键不是再加一个 damping 模块，而是让事件解析与数值耗散各自只处理自己负责的误差来源。

**(d) 第一个证伪实验。** 对 §11 的 off-grid RLC+line 网络扫描 \(\theta\in[0,1)\)。若新方法不能同时做到：无持续交替伪振荡、事件时刻二阶收敛、切换前后能量误差随 \(h\) 系统下降，且网络求解次数没有因事件定位失控增长，那么该方向应被否定。

**(e) 与本文的实质区别。** 本文的目标是用固定 2S-DIRK 取代 trapezoidal+CDA，使阻尼不依赖事件检测；候选方向则把“事件位置误差”和“stiff 模态衰减”拆成两个可审计机制，并把 energy fidelity 纳入验收。若以后面向 FPGA，实现研究还必须进一步回答定点量化、双 stage 数据依赖、矩阵求解流水线和最坏情况 latency；本文没有提供这些证据。
