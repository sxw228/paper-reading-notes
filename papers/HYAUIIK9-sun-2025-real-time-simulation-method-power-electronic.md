# Real-Time Simulation Method for Power Electronic Converters With Low Resource Consumption

- 作者：Zonghui Sun，Guangsen Wang，Zhuolan Li，Xizheng Guo，Yu Zhang
- 出处：IEEE Transactions on Power Electronics，Vol. 40，No. 4
- 年份：2025
- DOI：10.1109/TPEL.2024.3485920
- Zotero key：HYAUIIK9
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的 FPGA 实时仿真瓶颈：`R_on/R_off` 开关模型精度高、适合 power electronic converter（PEC）的系统级仿真，但二极管状态判定常需迭代，状态更新又包含大量矩阵乘法；变量位宽为保精度而增大后，有限的 DSP48 乘法器和乘法延迟会同时卡住可容纳的系统规模与最小仿真步长。步长不能继续缩小时，高频门极信号会欠采样，显式离散的累计误差也会增大。作者因此把目标定成：对由半桥桥臂组成的变换器，在不使用 DSP48 的条件下保留 `R_on/R_off` 模型，并把实时步长压到 20 ns。论文用 50 kHz DAB 和 100 kHz AC-DC-AC 两个案例验证这一目标。[pdf:E01]（PDF 物理页 1，摘要与 Introduction）

它的重要性不只在“少用一种 FPGA 资源”。DSP48 是数量有限且常被控制器、滤波器和其他模型共享的硬核资源；若开关网络求解器能转用较充裕的 LUT，就能把 DSP48 留给不可避免的可变系数运算。20 ns 对文中两个案例分别相当于每个开关周期约 1000 和 500 个仿真点，这是由论文给出的 50/100 kHz 与 20 ns 参数直接计算出的采样密度；它解释了为什么作者把资源消耗、组合路径延迟和数值误差放在同一个问题里，而不是分别优化。[pdf:E03][pdf:E05]（PDF 物理页 3、5，DAB 设置与 Table V）

## § 2 — 前人工作与不足

论文给出的相关工作脉络集中在“怎样消除 `R_on/R_off` 模型的状态迭代”。文献 [5] 用电感电流判断二极管状态；[3] 和 [6] 分别处理 LLC 全桥臂和 MMC 子模块；[7] 给出面向任意拓扑的通用方法；[8]、[9] 则针对半桥桥臂给出较高通用性的状态预匹配。作者的判断是：这些方法解决了不同范围内的迭代问题，却没有同时消掉状态变量更新中的大规模乘法，因此 DSP48 仍限制系统规模和时序。[pdf:E01]（PDF 物理页 1，Introduction）

最直接的比较对象是作者自己的前作 [9]：在同一类 AC-DC-AC 拓扑、同为 100 kHz 且目标器件同为 XC7K325T 时，[9] 使用 3791 LUT、116 DSP48、5 BRAM、329 flip-flop，步长 25 ns；本文使用 5074 LUT、0 DSP48、5 BRAM、759 flip-flop，步长 20 ns。这里的真实改进是“用更多 LUT/flip-flop 换掉全部 DSP48，并缩短 5 ns 步长”，不是每一类资源都更少。文献 [10] 的行还同时换成了 2 kHz 拓扑工况和 XC7K410T 器件，因此只能说明量级，不能当成严格的同平台优越性证明。[pdf:E05]（PDF 物理页 5，Table V）

## § 3 — 重建作者的思考路径

下面是基于引言、公式和实验安排的重建，不是作者逐字陈述。

第一步，从已有状态预匹配工作出发，可以认为“开关状态迭代”已不再是唯一障碍；即使状态一次判定，时变矩阵乘法仍会消耗 DSP48 并拉长关键路径。第二步，观察半桥：两个开关电阻各自只有 `R_on`、`R_off` 两种取值，所以一个桥臂只有四种离散电阻组合。与其让整个系统矩阵随组合切换，不如把桥臂对外暴露为一个受控电流源和一个受控电压源，把开关造成的变化收进端口量 `i_a`、`v_b`，使系统状态方程的矩阵保持常数。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Eq. (1)–(5)）

第三步，既然每个桥臂只有四种状态，就可离线枚举四种 `R_a/R_b` 组合，把运行期工作改为计算 12 个“常系数 × 变量”的中间量并按状态选择加减，而不是重建、存储或乘以时变矩阵。第四步，常系数固定后，可把其二进制展开成若干个 2 的幂，用位移与加法实现乘法；FPGA 上由 LUT 构成的加法网络便可替代 DSP48。最后，把一次步进拆成先更新状态、再并行更新各桥臂开关量的两阶段结构，以 20 ns 固定步长验证精度和时序。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (6)–(7)、Fig. 2–4）

## § 4 — 核心 Intuition

核心不是给乘法器做得更小，而是先重写模型，让所有运行期乘法都变成“固定常数乘以变量”。半桥的四种 `R_on/R_off` 组合可预先枚举，开关变化只决定从预计算形式中选哪组加减；固定常数再展开成二进制位移和加法，于是 DSP48 被 LUT 加法网络取代。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (4)–(7)、Fig. 3）

## § 5 — 具体方法与完整 Pipeline

以 DAB 为例，完整 pipeline 如下。

1. **定义系统端口。** 将每个半桥臂替换成 Fig. 1 的受控源等效结构。系统写成状态向量 `x`、输入 `u`、全部桥臂受控电流组成的 `i` 与受控电压组成的 `v`。DAB 取 `x=[i_Lp,v_o]^T`、`u=v_in`、`i=[i_S5,i_S7]^T`、`v=[v_S2,v_S4,v_S6,v_S8]^T`。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (1) 与 Case Study 1）
2. **Stage 1 更新状态。** 在采样点 `k` 读取 `x(k-1)`、`u(k-1)`、`i(k-1)`、`v(k-1)`，以 forward Euler 和常系数矩阵计算 `x(k)`。这是时序电路路径。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (7)、Fig. 2 与 Fig. 4）
3. **恢复每个桥臂的局部输入。** 用输出方程 `[i_h,v_h]^T=Cx+Du` 得到桥臂输入电流与电压；这一步把系统状态重新投影到桥臂判断所需的局部量。[pdf:E02]（PDF 物理页 2，Eq. (3)）
4. **并行判定开关并生成中间量。** 门极 `g_a,g_b` 直接给出三个主动开关组合；双管均关断时，再由 `v_h`、`i_h R_on`、`i_h R_off` 的分段条件决定二极管对应状态。同时计算 12 个 `p` 量。论文在 Fig. 2 中明确把 `p_1…p_12` 与状态组合 `σ_h` 画成并行操作。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (5)–(6)、Fig. 2）
5. **Stage 2 更新受控源。** 按四值状态 `σ_h` 从 `p` 量中选择加减式，得到每个桥臂的 `i_a(k)`、`v_b(k)`，再合并为下一步使用的向量 `i(k)`、`v(k)`。各半桥臂之间可并行；论文把该段实现为组合电路。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (4)、Fig. 2 与 Fig. 4）
6. **把常数乘法映射为 SAO。** 把定点常数写成若干个二进制幂之和，变量分别位移后相加；logical operations 与 shift addition operations（SAOs）由 LUT 实现，不调用 DSP48。论文没有报告共享加法子表达式、流水级数或具体二进制项数，只展示了原理图。[pdf:E03]（PDF 物理页 3，Fig. 3–4）
7. **固定步长执行并输出波形。** 文中没有多速率积分器，两个案例都以单一 20 ns 步长运行。DAB 离线模型使用 34 bit 变量格式（24 bit 小数、9 bit 整数、1 bit 符号），矩阵元素使用 32 bit 小数加 1 bit 符号；AC-DC-AC 变量扩大为 47 bit（37 bit 小数、9 bit 整数、1 bit 符号），矩阵元素仍使用 32 bit 小数。实际 RTS 平台为 AX7325B，器件 XC7K325TFFG900-2，DAB 波形经 14 bit AD9767 输出到示波器。[pdf:E03][pdf:E04][pdf:E05]（PDF 物理页 3–5，两个 Case Study）

论文未报告动态步长、事件插值、自动定点位宽搜索、跨桥臂资源复用、片上控制器开销或 place-and-route 的时序裕量；这些不能从“20 ns 可以运行”反推出来。

## § 6 — 核心数学推导（无形式化数学则跳过）

**1. 把开关变化移出系统矩阵。** 作者先写出

$$
\dot{\mathbf{x}}
=\mathbf{M}_A\mathbf{x}+\mathbf{M}_B\mathbf{u}
+\mathbf{M}_i\mathbf{i}+\mathbf{M}_v\mathbf{v},
\tag{1}
$$

其中 `x`、`u` 分别为状态与输入，`i`、`v` 汇集各半桥的受控电流 `i_a` 和受控电压 `v_b`；开关状态的影响由 `i_a,v_b` 承担，所以四个 `M` 矩阵为常数。[pdf:E02]（PDF 物理页 2，Eq. (1)）

**2. 从半桥电阻网络得到受控源。** 令上、下管等效电阻为 `R_a,R_b∈{R_on,R_off}`，Kirchhoff 方程给出

$$
\begin{bmatrix}i_a\\v_b\end{bmatrix}
=
\begin{bmatrix}
\dfrac{R_b}{R_a+R_b} & -\dfrac{1}{R_a+R_b}\\[4pt]
-\dfrac{R_aR_b}{R_a+R_b} & -\dfrac{R_b}{R_a+R_b}
\end{bmatrix}
\begin{bmatrix}i_h\\v_h\end{bmatrix},
\qquad
\begin{bmatrix}i_h\\v_h\end{bmatrix}=\mathbf C\mathbf x+\mathbf D\mathbf u.
\tag{2–3}
$$

物理上，`i_h,v_h` 是桥臂从外部系统看到的输入电流与电压，`i_a,v_b` 是桥臂反馈给系统的 Norton/Thévenin 型受控源量。[pdf:E02]（PDF 物理页 2，Fig. 1、Eq. (2)–(3)）

**3. 穷举四个开关组合。** 因为 `R_a,R_b` 只有两值，作者把运行期乘积整理为

$$
\begin{aligned}
&p_1=\tfrac12 i_h,\quad p_2=\tfrac12R_{\rm on}i_h,\quad
p_3=\tfrac12R_{\rm off}i_h,\\
&p_4=\frac{R_{\rm on}i_h}{R_{\rm on}+R_{\rm off}},\quad
p_5=\frac{R_{\rm off}i_h}{R_{\rm on}+R_{\rm off}},\quad
p_6=\frac{R_{\rm on}R_{\rm off}i_h}{R_{\rm on}+R_{\rm off}},\\
&p_7=\tfrac12v_h,\quad p_8=\frac{v_h}{2R_{\rm on}},\quad
p_9=\frac{v_h}{2R_{\rm off}},\\
&p_{10}=\frac{R_{\rm on}v_h}{R_{\rm on}+R_{\rm off}},\quad
p_{11}=\frac{R_{\rm off}v_h}{R_{\rm on}+R_{\rm off}},\quad
p_{12}=\frac{v_h}{R_{\rm on}+R_{\rm off}}.
\end{aligned}
\tag{5}
$$

随后只做状态选择：

$$
i_a=
\begin{cases}
p_1-p_9,&\sigma_h=\sigma_{h0}\\
p_4-p_{12},&\sigma_h=\sigma_{h1}\\
p_5-p_{12},&\sigma_h=\sigma_{h2}\\
p_1-p_8,&\sigma_h=\sigma_{h3}
\end{cases},
\quad
v_b=
\begin{cases}
-p_3-p_7,&\sigma_h=\sigma_{h0}\\
-p_6-p_{10},&\sigma_h=\sigma_{h1}\\
-p_6-p_{11},&\sigma_h=\sigma_{h2}\\
-p_2-p_7,&\sigma_h=\sigma_{h3}.
\end{cases}
\tag{4}
$$

`σ_h=2σ_a+σ_b` 编码四种管态；当门极未直接决定导通支路时，Eq. (6) 再按 `v_h` 与 `i_hR_on/i_hR_off` 的区间关系选状态，从而取消二极管状态迭代。[pdf:E02]（PDF 物理页 2，Eq. (4)–(6)）

**4. 显式离散形成两阶段依赖。**

$$
\mathbf{x}(k)=
(\mathbf I+\Delta t\mathbf M_A)\mathbf{x}(k-1)
+\Delta t\mathbf M_B\mathbf u(k-1)
+\Delta t\mathbf M_v\mathbf v(k-1)
+\Delta t\mathbf M_i\mathbf i(k-1).
\tag{7}
$$

这说明 `x(k)` 只依赖上一步的桥臂反馈，算完 `x(k)` 后才在 Stage 2 生成 `i(k),v(k)`；因此桥臂状态与状态积分被明确解耦，但也保留了 forward Euler 的一步显式滞后与稳定性约束。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (7)、Fig. 2）

**5. 位移加法替代常数乘法。** 若定点常数 `c=2^{m_1}+2^{m_2}+\cdots+2^{m_n}`，则 `cq(k)` 可实现为 `q(k)<<m_1 + … + q(k)<<m_n`。这不是消灭运算量，而是把乘法器硬核换成若干连线移位与 LUT 加法器；成本取决于常数的非零二进制项数和加法树深度。[pdf:E03]（PDF 物理页 3，Fig. 3）

实验还使用两个辅助公式。DAB 传输功率按

$$
P=\frac{n v_{\rm in}v_oD(1-D)}{2f_sL_p}
\tag{8}
$$

设置相移占空比 `D=0.235`；误差指标是

$$
\delta=\frac{\lVert f_{\rm Model}-f_{\rm Ref}\rVert_2}
{\lVert f_{\rm Ref}\rVert_2}\times100\%.
\tag{9}
$$

[pdf:E03]（PDF 物理页 3，Eq. (8)–(9)）

## § 7 — 实验设计与结论

**问题一：SAO 模型在长时间离线仿真中是否仍接近参考模型？**  
实验：DAB 使用 `L_p=90 μH`、`C_o=330 μF`、`v_in=300 V`、`R_o=50 Ω`、`n=1`、`f_s=50 kHz`、`P=1.8 kW`，20 ns 步长、200 ns dead time、`R_on=1 mΩ`、`R_off=100 kΩ`，与 MATLAB/Simulink 参考模型比较 0.2 s。答案：`i_Lp` 最大绝对误差小于 0.12 A；二范数相对误差为 `i_Lp=0.356%`、`v_o=0.266%`。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Table I、Fig. 6、Table II）

**问题二：实时模型与真实 DAB 硬件波形是否一致？**  
实验：在 AX7325B/XC7K325T 平台运行相同工况，经 14 bit DAC 输出，并与采用 FF6MR12W2M1-B11 SiC MOSFET 和 EE50 变压器磁芯的硬件台架比较。答案：Fig. 8 中 `i_Lp` 的绝对差小于 3 A，波形总体贴合。作者把主要误差归因于示波器、电流传感器和 DAC 精度，但没有用校准或不确定度分解验证这一归因，因此“误差源主要是测量链”只能视为作者解释，不能当成已隔离的因果结论。[pdf:E04]（PDF 物理页 4，Fig. 7–8 及相邻正文）

**问题三：方法能否扩展到开关更多、频率更高的 AC-DC-AC？**  
实验：第二个模型含整流桥、DC link 与三相逆变桥，`L_in=5 mH`、`C_d=8 mF`、三相电感均为 `2 mH`、负载电阻均为 `2 Ω`、输入 `380 V/50 Hz`、开关频率 `100 kHz`；采用 SPWM、20 ns 步长、60 ns dead time，并使用 47 bit 状态/输入/开关变量。答案：离线仿真 0.1 s 内，`i_in`、`i_u` 最大绝对误差分别小于 0.032 A、0.005 A，二范数相对误差分别为 0.0009%、0.0012%；FPGA 实时波形也能以 20 ns 步长输出。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Table III–IV、Fig. 10–11）

**问题四：资源与时序是否优于已有方法？**  
实验：Table V 汇总两个本文模型及 [9]、[10]。答案：本文 DAB 使用 1994 LUT、0 DSP48、0 BRAM、327 flip-flop；AC-DC-AC 使用 5074 LUT、0 DSP48、5 BRAM、759 flip-flop，两者都是 20 ns。与同器件、同拓扑、同开关频率的 [9] 相比，本文把 116 个 DSP48 降到 0、步长由 25 ns 降到 20 ns，代价是 LUT 从 3791 增至 5074、flip-flop 从 329 增至 759。论文没有给出 post-route slack、功耗、综合约束和精度对齐后的消融，因此能确认的是这两个实现点的资源置换和步长结果，不能外推为所有半桥拓扑上都具有更低总成本。[pdf:E05]（PDF 物理页 5，Table V 与 Conclusion）

## § 8 — Take-aways

**5 句话**

1. 论文把半桥开关变化从时变系统矩阵中抽离到受控电流、受控电压端口，使状态方程系数保持常数。[pdf:E02]（PDF 物理页 2，Eq. (1)–(3)）
2. 四种 `R_on/R_off` 组合被穷举为 12 个常系数乘积和四组加减选择，同时用分段状态判据取消二极管迭代。[pdf:E02]（PDF 物理页 2，Eq. (4)–(6)）
3. 固定系数乘法被二进制位移加法替代，两个 FPGA 案例因此都使用 0 个 DSP48。[pdf:E03][pdf:E05]（PDF 物理页 3、5，Fig. 3 与 Table V）
4. 50 kHz DAB 与 100 kHz AC-DC-AC 均达到 20 ns 步长，离线相对误差最高分别为 0.356% 和 0.0012%。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Table II、IV–V）
5. 现有证据说明这两个固定参数、半桥型案例成立，但没有证明任意系数分布、非线性元件或在线参数变化下仍保持资源和时序优势。[pdf:E05][pdf:E06]（PDF 物理页 5–6，Table V 与 Conclusion）

**3 句话**

1. 作者先把半桥建模问题改写成常系数状态更新加离散端口选择，再用 LUT 位移加法取代 DSP48。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (1)–(7)、Fig. 3）
2. 两个案例以 0 DSP48、20 ns 步长获得了与离线参考接近的结果，DAB 还与硬件波形进行了比较。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Fig. 8、Table V）
3. 最关键的未决问题是 SAO 加法网络的规模与关键路径如何随系数二进制复杂度、系统维数和参数变化增长。

**1 句话**

1. 这篇论文的价值是通过“先把模型变成常系数，再把常数乘法变成位移加法”用 LUT 换出 DSP48，但其可扩展边界仍需更广泛的同平台综合证据。

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标变换器能在固定参数下形成常系数矩阵，而且这些常数的定点二进制展开足够便宜，使 SAO 加法网络不会反过来成为 LUT、精度或关键路径瓶颈。** 一旦模型含饱和磁性、温度相关器件参数、在线参数辨识、连续变化的导通压降，或控制/网络重构让系数必须在运行期变化，“常数乘变量”就退化回可变乘法；即使系数确实固定，若高精度表示具有很多非零二进制位，位移后仍需深加法树，20 ns 时序和低 LUT 消耗也可能消失。

论文对这一假设给出的正面证据是：DAB 与 AC-DC-AC 分别使用 34 bit、47 bit 变量格式，在 XC7K325T 上均报告 0 DSP48 和 20 ns 步长，且 Table V 给出低占比 LUT 结果。[pdf:E03][pdf:E05]（PDF 物理页 3、5）缺失的证据包括：各常数的非零位统计、加法树深度、post-route 最差负裕量/余量、不同参数尺度与更高阶拓扑的资源增长曲线，以及参数变化时是否必须重新生成 bitstream。这个假设若失败，论文的“低资源、短步长”核心贡献会同时失效，因此比单个波形误差或某个传感器噪声更关键。

## § 10 — 最小复现实验

一周内只复现 DAB，不搭建功率硬件，做一个 bit-accurate RTL 与 post-route 对比即可检验核心 claim。

1. 用 Table I 参数建立 DAB：`L_p=90 μH`、`C_o=330 μF`、`v_in=300 V`、`R_o=50 Ω`、`n=1`、`f_s=50 kHz`、`D=0.235`，并使用 20 ns 步长、200 ns dead time、`R_on=1 mΩ`、`R_off=100 kΩ` 和论文的 34 bit/矩阵定点格式。[pdf:E03]（PDF 物理页 3，Table I 与 Case Study 1）
2. 实现两个数值完全同构的 solver：A 为 Eq. (1)–(7) 的 SAO 版本，B 只把同一批常系数乘法换成 DSP48，其他状态判据、位宽和流水边界保持一致；目标器件固定为 XC7K325T，避免器件差异。
3. 用 MATLAB/Simulink 或高精度离散参考模型驱动同一组门极信号，运行 0.2 s，记录 `i_Lp`、`v_o`、最大绝对误差和 Eq. (9) 的二范数相对误差；同时记录综合与 place-and-route 后的 LUT、DSP48、BRAM、flip-flop、关键路径和 20 ns 时序是否闭合。
4. 支持 claim 的最低条件是：A 使用 0 DSP48、真实 post-route 时序满足 20 ns，且 `i_Lp≤0.356%`、`v_o≤0.266%`，最大 `i_Lp` 误差不超过 0.12 A 的报告边界，同时 A 相比 B 确实释放 DSP48。[pdf:E04]（PDF 物理页 4，Fig. 6 与 Table II）
5. 只要 A 无法在相同位宽和数值误差下闭合 20 ns，或者为了 0 DSP48 付出的 LUT/流水代价使其失去论文声称的低资源优势，就反驳最核心的工程 claim；不需要先复现第二个拓扑。

## § 11 — 最强反例设计

最强反例不是简单增加开关数，而是在论文仍声称适用的“半桥桥臂型 PEC”范围内，构造一个**固定但二进制复杂、数值病态的常系数系统**。例如用多个半桥连接不同数量级的 `L/C/R` 支路，使离散矩阵中大量系数需要 32–40 bit 精度且 canonical signed-digit 表示仍有较多非零项；保持 `R_on/R_off` 模型和固定拓扑，不引入论文范围外的器件模型。这样可以只攻击“所有常数乘法换成 SAO 后仍低资源、低延迟”的机制，而不混入二极管迭代或模型不兼容。

在同一 FPGA、同一 forward Euler 步长和相同误差约束下，实现三版：本文式独立 SAO、DSP48 乘法、允许共享子表达式的 multiple-constant multiplication。逐步增加状态数与系数非零位数，测量 LUT、DSP、寄存器、加法树层数、post-route 时序和数值误差。若独立 SAO 的 LUT 或关键路径在中等规模时超过 DSP 版，或为满足 20 ns 必须增加流水而破坏 Eq. (7) 的一步依赖，便得到一个机制级反例：论文在两个友好系数实例上的成功不能推出一般的“低资源消费”。该攻击的事实前提是论文只报告两个实现点且未报告系数复杂度和时序裕量。[pdf:E03][pdf:E05]（PDF 物理页 3、5，Fig. 3–4 与 Table V）

## § 12 — Follow-up Research Idea

电力电子实时仿真的高影响工作通常不仅要给出新的离散形式，还要在真实 FPGA 上证明精度、稳定性、固定步长可达性、资源/功耗可扩展性，并在多种拓扑和故障工况中保留工程价值。基于第 9 节，候选方向是：**把“状态坐标选择—定点量化—multiple-constant multiplication（MCM）网络—实时步长”联合成一个误差约束的硬件/模型协同优化问题。** 它不是在本文后面再加一个压缩模块，而是改变建模目标：不再先固定物理状态方程再逐个把乘法换成移位，而是寻找数值条件良好、同时具有低二进制复杂度的等价状态基，使多个系数共享移位中间项。

（a）驱动需求是：本文方法的成本取决于未报告的系数二进制结构，复杂拓扑可能让 LUT 加法网络成为新瓶颈。[pdf:E03][pdf:E05]（PDF 物理页 3、5，Fig. 3–4 与 Table V）（b）若能在相同精度与稳定性下给出跨拓扑的资源增长界和可综合实现，它会直接提升 HIL 平台可容纳的变换器规模，而不仅是单案例节省。（c）可借鉴数字信号处理中的 MCM、canonical signed digit、approximate computing，以及控制理论中的 similarity transformation 与 condition-number 约束。（d）第一个证伪实验是在同一 XC7K325T 上，对 DAB、AC-DC-AC 和第 11 节的病态半桥网络比较“本文逐项 SAO、DSP48、联合优化”三者的 Pareto frontier；若联合优化不能在误差、20 ns 时序、LUT/DSP 至少一个维度形成严格改进，该想法即失败。（e）它与本文的实质区别是：本文固定模型后替换乘法器，候选方向则把可实现的算术结构反向纳入状态空间选择和误差设计。

这只是基于本论文证据形成的候选研究方向；本卡没有对 MCM 与 power-electronics real-time simulation 的交叉文献做完整检索，因此不声称 novelty。
