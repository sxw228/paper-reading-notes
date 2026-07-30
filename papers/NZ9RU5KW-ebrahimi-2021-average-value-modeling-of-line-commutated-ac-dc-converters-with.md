# Average-Value Modeling of Line-Commutated AC–DC Converters With Unbalanced AC Network

作者：Seyyedmilad Ebrahimi、Navid Amiri、Juri Jatskevich。[pdf:E01]（PDF 物理页 001，论文首页）

出处：IEEE Transactions on Energy Conversion, Vol. 36, No. 4, pp. 3533–3544。[pdf:E01]（PDF 物理页 001，页眉与首页）

年份：2021。[pdf:E01]（PDF 物理页 001，页眉与首页）

DOI：10.1109/TEC.2021.3084124。[pdf:E01]（PDF 物理页 001，首页脚注）

Zotero key：NZ9RU5KW

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的问题是：怎样在外部 AC 网络不平衡时，仍用比逐开关仿真便宜得多的 average-value model 重建 line-commutated rectifier（LCR）的 AC/DC 波形、谐波和低频动态。详细开关模型必须处理每个器件的导通、换相、过零检测和插值，通常需要很小的时间步；当系统里有多个换流器，或者优化与控制设计要求反复仿真时，LCR 会成为系统级 EMT 研究的计算瓶颈。[pdf:E01]（PDF 物理页 001，Abstract 与 Section I）

这不是单纯的“把平均值算快一点”。AC 网络不平衡可来自不对称故障、线路阻抗不等、负载或电源不平衡；它不仅改变 fundamental positive/negative sequence，还会改变 AC 侧谐波组成和 DC 侧 ripple，继而影响保护、控制和稳定性判断。作者因此把 PAVM 的输出目标从慢变量平均值扩展为：在不显式执行离散换相的前提下，同时重建正、负序 AC 谐波与 DC 谐波。[pdf:E01]（PDF 物理页 001，Abstract 与 Section I）[pdf:E02]（PDF 物理页 002，贡献列表与 Fig. 1）

工程价值在于让大规模 AC–DC EMT 仿真可以采用更大的有效时间步，同时保留故障期间波形、谐波谱和 small-signal impedance 等系统级研究所需的信息。需要注意，这篇论文验证的是一套缩比实验与仿真模型，不是 FPGA 或实时平台上的硬件实现；作者只把 offline/real-time EMT 部署列为潜在用途。[pdf:E09]（PDF 物理页 009，Section V-B）[pdf:E11]（PDF 物理页 011，Conclusion）

## § 2 — 前人工作与不足

论文把已有 LCR average-value model 分成 analytical AVM（AAVM）与 parametric AVM（PAVM）。AAVM 用解析关系描述平均行为，适合快速系统仿真，但作者指出，已有用于不平衡 LCC-HVDC 的 dynamic-phasor AAVM 通常只适用于其推导所针对的单一 operating mode。PAVM 则用详细开关模型的短时扫描建立数值参数函数，已有工作能处理内部开关故障造成的不对称，但并未同时表述“外部 AC 网络不平衡引起的正/负序 AC 谐波”和“DC 侧振荡分量”。[pdf:E01]（PDF 物理页 001，Section I 末段）[pdf:E02]（PDF 物理页 002，Section I 贡献列表）

作者还对比了一个把 DC 子系统阻抗解析映射到 AC 侧的既有 impedance 模型。该方法依赖 ideal switch、忽略谐波和 commutating inductance 等简化，论文的频域结果显示它在所测频段不能准确匹配详细开关模型；这说明“平均模型足够快”并不自动等于“仍能用于不平衡系统的稳定性分析”。[pdf:E09]（PDF 物理页 009，Section V-C 与 Eq. (54)–(55)）

关于 novelty，只能准确复述作者的自我定位：作者称，此前尚未报告面向 AC 网络不平衡、同时覆盖上述 AC 与 DC 谐波的 PAVM。[pdf:E02]（PDF 物理页 002，Section I）本卡按 PDF-only 边界没有联网核查相关文献，因此不把“首次”当作独立确认的事实。

## § 3 — 重建作者的思考路径

可以把作者的思考路径逆向重建为五步。

1. 详细开关模型准确，但它把大量计算花在离散换相事件上；系统级 EMT 研究真正关心的常常是端口波形、谐波与慢动态，而不是每个器件事件本身。[pdf:E01]（PDF 物理页 001，Section I）
2. 传统 average-value model 省掉事件后通常只保留较慢的平均关系，因而在外部不平衡下丢失了重要的波形信息。对 six-pulse LCR 而言，不平衡会引入新的 AC 序分量与 DC 低阶 ripple，简单的 balanced template 不再够用。[pdf:E03]（PDF 物理页 003，Eq. (13)–(18)）
3. symmetrical components 能把不平衡源拆成 positive/negative sequence；对每一个谐波阶次再使用正向和反向旋转的 \(qd\) 坐标系，就能把目标谐波变成便于平均提取的 DC 量。[pdf:E04]（PDF 物理页 004，Eq. (28)–(33) 与 Fig. 3）
4. 这些端口关系很难完整解析推导，但可以用详细开关模型在不同不平衡程度、相角和负载下做短时扫描，把幅值增益和相位保存成 lookup table。[pdf:E05]（PDF 物理页 005，Eq. (37)–(42) 与其后正文）
5. 在线仿真时只需检测输入的序分量、查表并合成有限阶谐波，即可用连续受控源代替离散器件，从而保留端口波形而避开开关事件。[pdf:E06]（PDF 物理页 006，Algorithm 1 与 Eq. (43)–(53)）[pdf:E07]（PDF 物理页 007，Fig. 6–7）

这条路径的关键不是发现一个新的电路定律，而是改变模型的状态表示：把“每个开关何时动作”压缩成“给定不平衡、相位和负载时，各序谐波应该具有多大幅值和相位”。

## § 4 — 核心 Intuition

外部不平衡造成的复杂波形，可以被拆成少数正、负序 AC 谐波和偶次 DC ripple；只要分别学习这些分量相对于运行点的幅值与相位，就不必重演每次换相。[pdf:E03]（PDF 物理页 003，Eq. (13)–(18)）作者用详细开关模型离线建立这些映射，在线阶段只做序分解、查表和有限谐波合成。[pdf:E05]（PDF 物理页 005，Section IV-A）因此，PAVM 用一个连续、可线性化的端口模型换取较大的仿真步长，同时尽量保留故障波形和频域阻抗信息。

## § 5 — 具体方法与完整 Pipeline

以论文的 phase-\(c\) 断线实验为例，完整 pipeline 如下。

1. **定义端口与运行点。** 模型输入是 AC 源电压 \(\mathbf e_{abcs}\)、LCR 端电压 \(\mathbf v_{abcs}\) 和 DC 电流 \(i_{dc}\)；输出是 AC 电流 \(\mathbf i_{abcs}\) 与 DC 电压 \(v_{dc}\)。外部 AC、DC 子系统仍由 EMT 程序原生求解，LCR 本体用连续受控电流源和电压源接口。[pdf:E06]（PDF 物理页 006，Section IV-B）[pdf:E07]（PDF 物理页 007，Fig. 6–7）
2. **离线生成参数函数。** 在详细开关模型上扫描不平衡因子 \(A_{\mathrm{imb}}\)、负序相移 \(\gamma_{\mathrm{imb}}\) 和负载动态导纳 \(y_d\)，计算各阶正/负序 AC 电流的幅值、相位，以及 DC 平均电压和 ripple 的幅值、相位，保存为 3-D lookup table。Algorithm 1 明确要求在每个不平衡与相角组合下改变 DC 负载并重新计算这些函数；对 thyristor LCR，firing angle 还要增加为额外维度。[pdf:E05]（PDF 物理页 005，Eq. (37)–(42)）[pdf:E06]（PDF 物理页 006，Algorithm 1）
3. **在线识别不平衡与相角。** 对 \(\mathbf e_{abcs}\) 做正、负序 \(qd\) 变换，得到 \(A_{\mathrm{imb}}\) 与 \(\gamma_{\mathrm{imb}}\)；由 terminal voltage 的 PLL，或由 source angle 加相移 \(\delta\)，得到合成谐波所需的 \(\theta_e\)。再以 \(\bar i_{dc}/\lVert\bar{\mathbf v}^{1,+e}_{qds}\rVert\) 形成 \(y_d\)。[pdf:E04]（PDF 物理页 004，Eq. (28)–(32)）[pdf:E05]（PDF 物理页 005，Eq. (42)）[pdf:E06]（PDF 物理页 006，Eq. (50)）
4. **查表并重建 AC 电流。** lookup table 返回各阶正、负序电流的归一化幅值与相位；模型在多个正向/反向旋转 \(qd\) frame 内构造谐波，再变回 \(abc\) 并相加。论文验证模型保留到 AC 第 7 阶，即 \(n_{\max}=7\)。[pdf:E06]（PDF 物理页 006，Eq. (43)–(49)）[pdf:E07]（PDF 物理页 007，Section V-A）
5. **重建 DC 电压。** 模型用查表得到的平均增益生成 \(\bar v_{dc}\)，再加入 \(h=2\) 的主要 ripple；验证模型取 \(h_{\max}=2\)。在 phase-\(c\) 于 \(t=2.13\,\text{s}\) 断开后，\(A_{\mathrm{imb}}\) 从 0 变为 50%，电路事实上成为单相整流器带 DC 负载，模型仍连续产生 AC/DC 端口量。[pdf:E06]（PDF 物理页 006，Eq. (51)–(53)）[pdf:E07]（PDF 物理页 007，Section V-A）
6. **选择子系统表示。** PAVM-DH 对所保留谐波使用完整动态方程；PAVM-PH 对谐波使用稳态 algebraic phasor。后者更快，但要求仿真器能同时容纳 dynamic fundamental 与 phasor harmonics。[pdf:E07]（PDF 物理页 007，PAVM-DH/PAVM-PH 定义）[pdf:E09]（PDF 物理页 009，Section V-B）

论文没有报告固定步长离散化、定点数值格式、并行调度、流水线、存储布局、FPGA 资源、时序闭合、HIL I/O 延迟或实际执行平台。Fig. 6 显示不同谐波支路在数据依赖上具有潜在并行性，但这是基于结构图的推断，不是作者完成的 FPGA mapping。[pdf:E07]（PDF 物理页 007，Fig. 6）实测计算只来自桌面 CPU 上的 MATLAB/Simulink 变步长求解，不应外推为实时或 FPGA 性能。[pdf:E09]（PDF 物理页 009，Section V-B）

## § 6 — 核心数学推导（无形式化数学则跳过）

数学上的第一步是把外部不平衡量化。没有 neutral connection，因此系统模型不含 zero sequence；源电压写成正、负序之和，并定义

\[
A_{\mathrm{imb}}=\frac{E_{\mathrm{neg}}}{E_{\mathrm{pos}}+E_{\mathrm{neg}}}\times100\%.
\]

\(A_{\mathrm{imb}}=0\) 表示纯正序平衡源，\(A_{\mathrm{imb}}=100\%\) 表示只有负序。这一定义提供了可用于查表的连续不平衡坐标。[pdf:E02]（PDF 物理页 002，Eq. (1)–(4)）

第二步是确定需要保留的频率结构。balanced six-pulse LCR 的 AC 侧主要含 \(6k\pm1\) 次谐波，而不平衡会使三次及其奇数倍不再作为零序消失，因此作者把候选 AC 阶次扩展为

\[
n\in\{1,3,5,7,9,\ldots\}.
\]

DC 变量由平均值与 ripple 组成；平衡时 ripple 通常是 \(6k\) 次，不平衡时扩展为

\[
h\in\{2,4,6,8,\ldots\},
\]

其中 \(h=2\) 通常占主导。[pdf:E03]（PDF 物理页 003，Eq. (13)–(18)）

第三步是把每个目标谐波变成可平均的坐标量。对 AC 变量分别使用以 \(+n\theta_e\) 和 \(-n\theta_e\) 旋转的 Park transform：

\[
\mathbf v^{n,+e}_{qds}=K_s(n\theta_e)\mathbf v_{abcs},\qquad
\mathbf v^{n,-e}_{qds}=K_s(-n\theta_e)\mathbf v_{abcs},
\]

电流同理。目标的第 \(n\) 次正序或负序分量在相应 frame 内成为 DC 量，对其平均即可得到幅值和相位；其余分量仍是 ripple 并被平均滤除。[pdf:E04]（PDF 物理页 004，Eq. (31)–(33)）

第四步把详细模型的结果压缩成无量纲参数函数。代表性关系为

\[
w^n_{i,\mathrm{pos}}(\cdot)=
\frac{\lVert\bar{\mathbf i}^{n,+e}_{qds}\rVert}{\bar i_{dc}},\qquad
w^h_{v,dc}(\cdot)=
\frac{V^h_{dc}}{\lVert\bar{\mathbf v}^{1,+e}_{qds}\rVert},\qquad
y_d=\frac{\bar i_{dc}}{\lVert\bar{\mathbf v}^{1,+e}_{qds}\rVert}.
\]

负序增益、DC 平均增益和各分量相角按同样方式定义。它们不是解析闭式模型，而是 \((A_{\mathrm{imb}},\gamma_{\mathrm{imb}},y_d)\) 的数值 lookup table。[pdf:E05]（PDF 物理页 005，Eq. (37)–(42)）

最后，在线模型把查表结果重新合成为端口量：

\[
\mathbf i_{abcs}=\sum_{n=1}^{n_{\max}}
\left[K_s(n\theta_e)^{-1}\bar{\mathbf i}^{n,+e}_{qds}
+K_s(-n\theta_e)^{-1}\bar{\mathbf i}^{n,-e}_{qds}\right],
\]

\[
v_{dc}=\bar v_{dc}+\sum_{h=2}^{h_{\max}}v^h_{dc}.
\]

直觉上，第一式把各序谐波“旋回”真实三相坐标，第二式把 DC baseline 与有限个 ripple 相加。\(n_{\max}\) 与 \(h_{\max}\) 越高，波形越细，但计算量也越大。[pdf:E06]（PDF 物理页 006，Eq. (49)–(53)）

## § 7 — 实验设计与结论

**问题 1：在严重外部不平衡和故障瞬态下，PAVM 能否重建 AC/DC 波形？** 实验使用 60 Hz permanent-magnet synchronous generator、six-pulse diode LCR、RLC 低通滤波器和 \(32.78\,\Omega\) 负载，使整流器工作于 CCM-1；详细模型在 MATLAB/Simulink 与 PLECS 中实现，PAVM 使用 \(n_{\max}=7\)、\(h_{\max}=2\)。在 \(t=2.13\,\text{s}\) 断开 phase \(c\)，使 \(A_{\mathrm{imb}}\) 从 0 变为 50%。[pdf:E07]（PDF 物理页 007，Section V-A）答案是：图中 PAVM-DH、PAVM-PH 与实验、详细模型的 AC/DC 波形和主要谐波相互接近，phase-\(c\) 电流归零后仍能跟踪故障瞬态；作者认为第 7 阶 AC 谐波与第 2 阶 DC ripple 已足够覆盖该工况的主要失真。[pdf:E08]（PDF 物理页 008，Fig. 8–11）论文没有报告 waveform RMSE、最大误差或置信区间，因此“high accuracy”主要由波形叠合与频谱柱状图支撑，不能转换成已验证的数值误差界。

**问题 2：模型是否更快？** 同一 5 s transient study 使用 ode23tb，三种模型统一最大步长 \(10^{-3}\,\text{s}\)、相对/绝对容差 \(10^{-3}\)，运行于 Intel Core i7-4510U 2.00 GHz。详细开关模型、PAVM-DH、PAVM-PH 的 CPU time 分别为 8.43 s、3.17 s、0.65 s；步数分别为 25,733、15,323、5,046；平均步长分别为 194、326、990 \(\mu\text{s}\)。[pdf:E09]（PDF 物理页 009，Table I 与 Section V-B）答案是：PAVM-PH 在这个 benchmark 中约快 13 倍，PAVM-DH 约快 2.7 倍；PH 的优势来自省掉谐波动态状态。作者在结论中使用了“orders of magnitude”这一更强表述。[pdf:E11]（PDF 物理页 011，Conclusion）但表中直接支持的是一个平台、一个 solver、一个 5 s 工况下的上述倍率，不能外推为所有 EMT 系统。

**问题 3：连续 PAVM 能否用于 small-signal impedance？** 作者向正、负序 AC 源注入不同频率的小扰动，以详细模型线性化结果、既有解析公式和 PAVM 互相比较。由于 60 Hz six-pulse LCR 的开关频率为 360 Hz，AVM 的频率能力按半开关频率限制到 180 Hz。[pdf:E09]（PDF 物理页 009，Section V-C）答案是：Fig. 12–13 中 PAVM 与详细模型的正、负序阻抗曲线接近，而简化解析模型偏差明显；但论文没有给出阻抗误差的汇总数字。[pdf:E10]（PDF 物理页 010，Fig. 12–13）

**问题 4：模型能否跟踪 sub-synchronous oscillation？** 作者在 \(t=1.5\,\text{s}\) 给 60 Hz 发电机频率叠加 3、10、23 Hz 的三项衰减振荡，并比较详细模型与 PAVM 的 AC 波形及 DC 平均量。[pdf:E10]（PDF 物理页 010，Eq. (56)–(57) 与 Fig. 14）答案是：PAVM 跟踪了这些低频动态，放大图中与详细模型接近。[pdf:E11]（PDF 物理页 011，Fig. 15–16）这验证的是给定合成扰动下的模型响应，不是实际电网 subsynchronous instability 的闭环硬件实验。

附录报告了缩比装置的主要参数：8 极发电机、\(0.153\,\text{V·s/rad}\) 电压常数、\(r_s=0.748\,\Omega\)、\(L_d=6.06\,\text{mH}\)、\(L_q=7.6\,\text{mH}\)；二极管 \(R_{\mathrm{on}}=0.09\,\Omega\)、\(V_{\mathrm{on}}=0.637\,\text{V}\)；DC filter 为 \(r_f=0.605\,\Omega\)、\(L_f=12.40\,\text{mH}\)、\(C_f=470\,\mu\text{F}\)。[pdf:E11]（PDF 物理页 011，Appendix）lookup table 的实际网格范围、步长、表项数据、内存占用和生成时间未报告，限制了精确独立复现。

## § 8 — Take-aways

**5 句话**

1. 论文把外部 AC 网络不平衡显式拆成正、负序 AC 谐波与偶次 DC ripple，使 PAVM 不只输出平均量。[pdf:E02]（PDF 物理页 002，贡献列表）[pdf:E03]（PDF 物理页 003，Eq. (13)–(18)）
2. 核心工程做法是用详细开关模型离线生成 \((A_{\mathrm{imb}},\gamma_{\mathrm{imb}},y_d)\) 三维参数表，在线只做检测、查表和谐波合成。[pdf:E05]（PDF 物理页 005，Section IV-A）
3. phase-\(c\) 断线实验表明，保留到 AC 第 7 阶和 DC 第 2 阶时，PAVM 能在该缩比 CCM-1 工况中重建主要波形与频谱。[pdf:E07]（PDF 物理页 007，Section V-A）[pdf:E08]（PDF 物理页 008，Fig. 8–11）
4. PAVM-PH 在单个 CPU benchmark 中以 0.65 s 完成详细模型耗时 8.43 s 的 5 s 仿真，并保持连续、可线性化的端口表示。[pdf:E09]（PDF 物理页 009，Table I 与 Section V-C）
5. 论文的主要缺口是没有量化波形误差、参数表覆盖边界和实时/FPGA 实现，因此速度与准确性结论应限于已测系统和 operating region。

**3 句话**

1. 这项工作用 sequence-aware harmonic lookup table 代替逐开关事件，在外部不平衡下保留端口波形。[pdf:E06]（PDF 物理页 006，Algorithm 1 与 Eq. (43)–(53)）
2. 实验、CPU transient benchmark、阻抗扫描和合成 sub-synchronous disturbance 共同证明了方法在作者所测范围内兼顾准确性与速度。[pdf:E08]（PDF 物理页 008，Fig. 8–11）[pdf:E10]（PDF 物理页 010，Fig. 12–14）
3. 真正尚未被回答的问题是：这三个查表坐标能否在未见故障、mode transition 和不同网络动态下唯一决定换流器端口行为。

**1 句话**

PAVM 的价值是把不平衡 LCR 的开关事件压缩成可快速合成的序谐波端口模型，而它的风险也恰好来自这次压缩可能遗漏决定换相行为的状态。

## § 9 — 最脆弱的假设

最脆弱的假设是：\((A_{\mathrm{imb}},\gamma_{\mathrm{imb}},y_d)\) 加上当前电气输入，足以把 LCR 的端口谐波映射变成在目标 operating region 内近似单值、可插值的函数。论文的所有 AC/DC 幅值与相位都储存在以这三个量为坐标的 3-D lookup table 中；thyristor 情况才额外加入 firing angle。[pdf:E05]（PDF 物理页 005，Eq. (37)–(42)）[pdf:E06]（PDF 物理页 006，Algorithm 1）

如果两个不同历史具有相同的这三个坐标，却因 conducting pair、commutation overlap、fault inception angle、DC filter state 或接近 CCM/DCM 边界而产生不同的下一时刻端口波形，表就不能同时表示它们。此时继续增加谐波阶次只会更精细地合成错误的目标幅值与相位，核心的“无事件而保持高保真”会失效。这是基于模型结构的推断，不是论文显式承认的失败。

论文提供的支持是：在 \(32.78\,\Omega\)、CCM-1 的缩比装置中，phase-\(c\) 断线使 \(A_{\mathrm{imb}}=50\%\) 后，PAVM 与实验及详细模型波形接近；频域与合成低频扰动也得到匹配。[pdf:E07]（PDF 物理页 007，Section V-A）[pdf:E08]（PDF 物理页 008，Fig. 8–11）[pdf:E10]（PDF 物理页 010，Fig. 12–14）缺少的证据是跨导通模式、跨拓扑、接近 commutation failure、不同 fault inception angle、不同表格分辨率与表外输入的系统性误差边界。

## § 10 — 最小复现实验

一周内最有价值的不是复刻全部论文，而是验证“有限序谐波 PAVM 在 phase-\(c\) 断线时，能否以更少计算重建主要端口波形”。

1. 在 MATLAB/Simulink + PLECS，或任一具有理想开关和变步长 solver 的 EMT 环境中，建立 60 Hz six-pulse diode bridge、发电机等效与 RLC DC filter；采用附录报告的发电机、二极管和滤波器参数，并令总 DC 负载为 \(32.78\,\Omega\)。[pdf:E07]（PDF 物理页 007，test setup）[pdf:E11]（PDF 物理页 011，Appendix）
2. 建立详细开关 baseline；再按 Algorithm 1 对 \(A_{\mathrm{imb}}\)、\(\gamma_{\mathrm{imb}}\) 与 \(y_d\) 做一个公开记录的稀疏扫描，提取 \(n=\{1,3,5,7\}\) 的正、负序 AC 电流和 \(h=\{0,2\}\) 的 DC 分量。论文未报告实际网格范围与步长，所以这一步只能验证机制，不能声称 byte-for-byte 复现作者的参数表。[pdf:E06]（PDF 物理页 006，Algorithm 1）
3. 先运行平衡稳态，再于 \(t=2.13\,\text{s}\) 断开 phase \(c\)。同时运行详细模型、PAVM-DH；若环境支持 dynamic/phasor 混合，再加入 PAVM-PH。[pdf:E07]（PDF 物理页 007，Section V-A）
4. 对 \(v_{dc},i_{dc},v_{ab},v_{bc},v_{ca},i_a,i_b,i_c\) 报告 fault 后两个 line cycles 的 normalized RMSE、峰值误差和相位误差；对 AC 的 1/3/5/7 阶正负序、DC 的 0/2 阶报告幅值误差；在统一 solver tolerance 下记录 CPU time、步数和平均步长。
5. 预先把“支持”定义为：上述主要波形 NRMSE 不超过 5%，所保留谱线幅值误差不超过 10%，并且 PAVM-DH 至少快 2 倍。把任一误差阈值持续突破，或速度不增反降，定义为对这个最小 claim 的反驳。这些阈值是复现实验自行预注册的判据，不是论文报告的标准。

这个实验不需要先实现 impedance scan、sub-synchronous oscillation 或 FPGA；它直接检查论文最中心的 accuracy-speed trade-off。若第一阶段通过，再补表格分辨率 sweep，观察速度、内存与误差如何变化。

## § 11 — 最强反例设计

最有力的攻击不是再换一种普通不平衡比例，而是制造“查表坐标相同、真实端口行为不同”的历史碰撞。

具体做法是用详细开关模型生成两条轨迹。轨迹 A 从平衡稳态缓慢进入某个 \((A_{\mathrm{imb}},\gamma_{\mathrm{imb}},y_d)\)；轨迹 B 在不同 fault inception angle 突然发生相位跳变或单相断线，并把 DC 负载调到相同的 \(\bar i_{dc}/\lVert\bar{\mathbf v}^{1,+e}_{qds}\rVert\)。选择接近 CCM/DCM 或 commutation-overlap 边界的运行点，使两条轨迹在某一时刻具有几乎相同的 PAVM 输入坐标，却保留不同的 conducting pair 或 filter state。PAVM 的表项由这三个坐标决定，因此会给出近乎相同的谐波幅值和相位；详细模型若给出显著不同的下一周期电流、DC ripple 或 commutation failure 行为，就说明参数化不是充分状态。[pdf:E05]（PDF 物理页 005，3-D lookup table 定义）[pdf:E06]（PDF 物理页 006，Algorithm 1 与在线合成）

攻击判据可以设为：两条详细轨迹在坐标距离小于表格一个 interpolation cell 时，任一关键波形的下一周期 NRMSE 差异超过 10%，或只有一条轨迹发生换相失败，而 PAVM 对两者给出相同预测。这个结果会直接挑战核心机制，而不是只说明需要把 \(n_{\max}\) 从 7 增加到更高。论文现有 phase-\(c\) 断线、阻抗扫描和合成低频扰动没有执行这种 history-collision 检验。[pdf:E08]（PDF 物理页 008，Fig. 8–11）[pdf:E10]（PDF 物理页 010，Fig. 12–14）

## § 12 — Follow-up Research Idea

在 EMT、电力电子与实时仿真领域，高影响结果通常需要同时证明：模型在故障和 mode transition 下可信、能显著降低系统级计算成本、具有可实现的实时数值结构，并能改善稳定性分析或大规模系统研究。本文已经用波形、CPU 时间、阻抗和低频扰动覆盖了其中一部分验证轴，但没有给出模型有效域与误差保证。[pdf:E09]（PDF 物理页 009，Section V-B/C）[pdf:E11]（PDF 物理页 011，Conclusion）

**候选研究方向：建立“状态歧义感知、带误差证书的 hybrid PAVM”。** 这不是把 lookup table 变密或再增加一个谐波，而是把研究目标从“给出一个快速点预测”改成“在线判断平均模型何时足以唯一决定端口行为，并在不充分时给出误差集合或触发局部事件解析”。

**(a) 未满足的需求。** 现有 3-D 参数化没有告诉使用者当前输入是否处于训练覆盖内，也没有识别相同坐标下由换相历史造成的多值输出。大规模 EMT 或 HIL 需要的是可被信任的加速，而不只是平均情况下更快。

**(b) 可能的研究价值。** 如果模型能在大多数时间保持 PAVM 速度，同时在 fault inception、mode boundary 或 commutation failure 前给出可验证的误差上界，并只对少数局部时间窗启用详细 micro-solver，它将把速度比较提升为“精度预算受控的系统级仿真”。这可能直接服务多换流器 AC–DC 网络的稳定性分析与实时测试。

**(c) 可借鉴的方法。** 可以借鉴 hybrid-systems reachability 与 set-membership identification：不把 lookup table 输出视为单点，而是学习在给定可观测量和短历史窗口下允许的谐波系数集合；再用 mode observer 判断集合是否收缩到可接受误差。如果面向 FPGA，集合传播、observer 与局部 micro-solver 必须进一步约束为固定步长、定点和可流水的计算图，但这些实现要求仍需单独验证。

**(d) 第一个证伪实验。** 先执行第 11 节的 history-collision 数据集；若新模型不能在输出分叉发生前扩大不确定度集合或触发详细求解，或者其上界频繁失效，就直接否定“误差可证”的核心 claim。反过来，如果它对所有普通工况都触发 fallback，也说明没有获得有用加速。

**(e) 与本文的实质区别。** 本文把 \((A_{\mathrm{imb}},\gamma_{\mathrm{imb}},y_d)\) 映射到单一谐波幅值和相位，再无条件合成端口量；候选方法把“参数是否构成充分状态”本身变成在线可检验对象，输出带有效域与不确定度的模型选择，而不是固定的点估计。[pdf:E05]（PDF 物理页 005，Eq. (37)–(42)）由于本卡没有在 PDF 外检索相关工作，这一方向只作为候选，不声称 novelty。
