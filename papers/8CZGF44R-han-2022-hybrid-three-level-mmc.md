# Real-Time Simulation of Hybrid Three-Level and Modular Multilevel Converter Based on Complete Equivalent Model for High Voltage Direct Current Transmission System

作者：Jintao Han、Levi M. Bieber、Jared Paull、Liwei Wang、Wei Li、Jean-Nicolas Paquin。  
出处：IEEE Open Access Journal of Power and Energy，Vol. 9。  
年份：2022；在线发表日期为 2021 年 12 月 23 日。  
DOI：10.1109/OAJPE.2021.3138345。标题、作者、出处、日期与 DOI 均见物理页 1。[pdf:E01]  
Zotero key：8CZGF44R。

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

**本文解决的是：如何保留 H3LC 内部逐子模块的开关与电容动态，同时把整个 HVDC 换流系统放进能够按时完成计算的 CPU–FPGA 实时仿真器。** 难点不只是子模块数量多，还包括三电平 T-type 主变换器、正常工作的 chainlink FBSM，以及故障时投入的 protection FBSM 必须协调运行。正常运行与闭锁时，电流通路和需要计算的等效电压都会变化。[pdf:E01][pdf:E02]（物理页 1 Abstract；物理页 2 Section I）

H3LC 用三电平主变换器承担主要电压合成，用交流侧 FBSM 链补偿方波与目标交流电压的差值，并用额外保护支路提供 DC fault blocking 所需的反向电压。保护支路在正常运行时被低损耗通路旁路，因此，正常运行模型不能简单代替故障闭锁模型。[pdf:E03]（物理页 3，Fig. 1、Section II-A）

工程瓶颈来自两个层次。第一，把每个半导体都放进电网求解器，会形成规模大、随开关状态变化的电路系统。第二，即使已经用等效电路缩小网络，逐 FBSM 电容更新、均压选择和 CPU–FPGA 数据交换仍然必须在实时期限内完成。本文因此同时改动电路表示、均压算法和计算任务划分，而不是单纯更换更快的硬件。[pdf:E02]（物理页 2，Section I）

其直接价值是为换流器控制与保护开发提供较细粒度的实时 EMT 模型。论文展示的是 CPU–FPGA 数字实时仿真；控制器也运行在 CPU 中，文中没有展示接入外部物理控制器的 HIL 实验。[pdf:E01][pdf:E10]（物理页 1 Abstract；物理页 6，Fig. 7）

## § 2 — 前人工作与不足

**最接近本文的工作已经解决了部分电路降阶与 FPGA 均压问题，本文的增量在于把这些能力重新组织成适合 H3LC 的完整实时实现。** 以下相关工作比较仅依据本文的介绍及参考文献记录。

Bieber 等人的 H3LC 工作，即本文参考文献 [3]，给出了具有 DC fault blocking 能力、降低半导体损耗的混合三电平与模块化多电平拓扑。本文沿用这一拓扑及控制背景，研究重点是模型与实时计算，而不是发明新的物理换流器。[pdf:E03][pdf:E04]（物理页 3，Section II；物理页 12，Reference [3]）

Han 等人的 [28]，题为 *Detailed equivalent and average value models of hybrid cascaded multilevel converters for efficient and accurate EMT-type simulation*，是最直接的建模前作。按照本文介绍，[28] 的 DEM 分别使用 EMoC 和 EMoP 表示正常 chainlink 与保护 FBSM，而 T-type 三电平部分仍显式建模。它已经大幅降低了逐器件模型的求解负担，但还保留着分散的等效模块和主变换器开关，网络节点与开关组合仍然有进一步缩减空间。[pdf:E02][pdf:E05][pdf:E07]（物理页 2，Section I；物理页 13，Reference [28]；物理页 4，Fig. 3）

同一前作中的 average-value model 适合电力系统级研究，却不能输出逐 SM 的开关行为，因此不能承担本文所针对的细粒度控制测试任务。这不是平均模型计算能力不够，而是它主动删除了这类测试需要观察的状态与事件。[pdf:E02]（物理页 2，Section I）

Saad 等人的 [14]、Li 与 Bélanger 的 [15]、Ould-Bachir 等人的 [16] 已研究 MMC 的 CPU–FPGA 实时仿真或等效电路实现。本文指出，这些方法不能直接移植到 H3LC：H3LC 不仅包含级联子模块，还包含三电平主变换器、保护支路及其协调控制；FBSM 还需要正插入、负插入、旁路三种状态，而不是只处理半桥子模块的插入与旁路。[pdf:E02][pdf:E04]（物理页 2，Section I；物理页 12，References [14]–[16]）

Li、Grégoire 与 Bélanger 的 [18] 是本文 FPGA 均压算法的直接起点。按本文转述，该工作以较低开关频率和较少 FPGA 资源实现 MMC 脉冲生成与电容均压，但对象是 half-bridge SM。本文必须补上 FBSM 的双极性状态，以及 H3LC 在三电平换相时整条 chainlink 同时反转极性的特殊操作。[pdf:E05][pdf:E11]（物理页 13，Reference [18]；物理页 7，Section IV-B）

因此，前人的不足主要是**模型结构与目标拓扑不匹配，以及网络求解、逐模块计算和通信没有针对 H3LC 联合组织**。论文没有提供与这些 MMC 实时系统在统一硬件、统一规模下的直接性能对照；若要判断跨拓扑的绝对优势，还需补读 [14]–[16]、[18] 和 [28] 的完整实现。

## § 3 — 重建作者的思考路径

以下是依据已有拓扑和前作重建的思考路径，而不是作者明确报告的研究过程。

首先，逐器件建模的昂贵之处并不等于所有内部状态都必须删除。串联 FBSM 对外表现为输出电压之和，而控制器真正需要保留的是各电容电压和开关状态。已有 DEM 已经证明，可以把大量内部开关计算移出电网节点求解，同时保留比平均模型更丰富的行为。[pdf:E02]（物理页 2，Section I 对 DM、DEM 与 average-value model 的比较）

其次，H3LC 的不同部分具有互补的工作方式：正常运行时保护支路被旁路，三电平主变换器与 chainlink 共同合成交流电压；闭锁时则依靠 FBSM 和二极管通路阻断故障贡献。[pdf:E03]（物理页 3，Section II-A）由此自然产生一个问题：是否有必要让三部分始终以独立开关网络存在，还是只需保留它们在不同工况下对端口施加的电压和导通关系？

再次，已有 CPU–FPGA 仿真经验提示，电网和上层控制可以采用较大时间步，而大量结构相同的子模块状态更新适合 FPGA 并行执行。真正需要跨设备传递的，可能是少量端口量，而不是每个模块的完整内部信息。[pdf:E02]（物理页 2，Section I）

最后，已有 FPGA 均压方法提示：控制器每次只需决定哪个模块投入或退出，并不总需要获得所有电容的完整排名。[pdf:E11]（物理页 7，Section IV-B 对 [18] 的讨论）如果把这种选择问题扩展到 FBSM 三种状态，并单独处理整链极性反转，就有机会同时降低网络求解负担、排序开销和通信量。

## § 4 — 核心 Intuition

把子模块保留为可更新的内部状态，不等于必须把每个子模块都保留为电网求解器中的开关节点。本文用少量受控电压源与二极管通路表达整个换流器的端口行为，再把大量重复的内部计算交给 FPGA。[pdf:E07][pdf:E08]（物理页 4–5，Figs. 4–5）均压时只寻找当前决策需要的极值模块，而不是反复给全部模块排完整名次，使细粒度状态能够与较小的实时计算负担共存。[pdf:E11]（物理页 7，Fig. 8）

## § 5 — 具体方法与完整 Pipeline

### 1. 先确定真实规模，再建立缩小后的电气网络

论文测试系统的**每相包含 256 个正常运行 CF 和额外 308 个保护 PF**，交流电网经 Wye–Delta 变压器连接换流器，直流侧通过 200 km 电缆接至 600 kV 电压源。[pdf:E13]（物理页 8，Fig. 9 及相邻正文）据此计算，每相共有 564 个 FBSM，三相共有 **768 个 CF、924 个 PF，合计 1692 个 FBSM**。这些总数是根据原文逐相数量作出的算术汇总。

CEM 并没有把这些模块全部放进电网求解器。原 DEM 的三相电路包含 24 个二极管、9 个交流侧受控电压源、3 个 FMS、保护支路中的 6 个反串联 IGBT，以及 T-type 部分的 12 个 IGBT；CEM 改为 18 个二极管、6 个交流侧受控电压源和 3 个理想开关，并以另外两个受控电压源表示上下 DC pole capacitor 电压。[pdf:E07][pdf:E08][pdf:E09]（物理页 4，Section III；物理页 5，Figs. 4–5 的说明；物理页 6，Table 1）

这里缩小的是电气网络及其开关状态空间，逐 CF 电容状态仍然保留。

### 2. CPU 生成较慢的控制命令

以论文的 1000 MW 逆变运行点为例，上层 PQ 与 qd 电流控制产生交流电压参考；下层控制据此生成 director switch 信号、三次谐波补偿及 chainlink 能量平衡修正，再通过 nearest level control 得到所需插入数量 `Nref,j`。[pdf:E06][pdf:E14]（物理页 4，Fig. 2；物理页 8，Section V-A）

CPU 1 运行控制系统，CPU 2 运行电网与换流器主电路。两个 CPU 经共享 RAM 交换测量量；CPU 与 FPGA 经 PCIe 在 CPU 同步时刻交换信息。FPGA 接收插入数量、主变换器开关信号以及电路测量量。[pdf:E10]（物理页 6，Fig. 7、Section IV-A）上层控制的完整方程和参数未在本文展开。[pdf:E06]

### 3. FPGA 用 PS-VBC 决定具体投入哪个 CF

FPGA 比较目标 `Nref,j` 与上一步实际插入数量 `Npre,j`。通常每个 FPGA 仿真步，每相只改变一个 CF 的插入或旁路状态。它根据插入极性与相电流判断电容正在充电还是放电，再从符合条件的已插入或已旁路集合中寻找最大值或最小值。[pdf:E11]（物理页 7，Fig. 8、Section IV-B）

例如，正插入且相电流为正时，已插入电容正在充电。若需增加一个模块，就选择旁路集合中电压最低的模块；若需减少一个模块，就旁路已插入集合中电压最高的模块。负插入时必须根据相反的电容充放电关系处理，不能直接沿用半桥的二状态逻辑。[pdf:E11]

**整链极性反转是专门的并行路径。** 在三电平主变换器换相附近，chainlink 参考可能在两个极性之间跳变；当上一时刻全部 CF 已投入且目标极性改变时，所有 CF 在一个 FPGA 仿真步内同时反转，而不是逐个经过旁路。[pdf:E11]（物理页 7，Fig. 8 Step 2）

### 4. 逐 CF 更新电容，而不是只更新刚改变状态的模块

开关选择完成后，每个 CF 都按自己的状态和共同相电流执行 Forward Euler 电容更新。旁路模块的状态系数为零，电压保持；正、负插入模块分别按对应符号充放电。[pdf:E08]（物理页 5，Eqs. (12)–(13)）因此，每步只改变一个 CF 的开关状态，不等于每步只更新一个电容。

PF 在正常运行时被旁路；闭锁后，其电容和等效电压按保护支路公式推进。[pdf:E08]（物理页 5，Eqs. (14)–(15)）正文给出了逐 PF 求和形式，但没有独立披露全部 PF 状态在 FPGA 中的存储组织与资源分项。

### 5. 将内部状态汇总成少量接口信号

FPGA 对每相生成正常 chainlink 电压、三电平电压、闭锁 chainlink 电压和保护支路电压四个分量，再加上下两个 DC pole capacitor 电压，共输出 **14 个信号，用于 8 个受控电压源**。14 是接口分量数，8 才是受控电压源总数。[pdf:E09][pdf:E10]（物理页 6，Table 1、Section IV-A）

这样，CPU 处理的是小型等效电路，逐模块电容与均压决策留在 FPGA 内部，避免每次同步交换全部模块状态。

### 6. 用多速率推进，而不是让全系统都采用 FPGA 步长

实际平台为 OPAL-RT OP5700，FPGA 为 Xilinx Virtex-7，文中提到 VC707 板卡。两个 CPU 的时间步均为 **30 μs**，FPGA 时间步为 **250 ns**；作者称 30 μs 是该配置下主电路与控制能够不发生 overrun 的最小 CPU 步长。[pdf:E10][pdf:E13]（物理页 6，Section IV；物理页 8，Section V）

每个 CPU 步内包含 120 个 FPGA 小步。返回 CPU 的受控源信号取这 120 个小步的平均值，而不是最后一个小步的值。[pdf:E10][pdf:E13]（物理页 6，Eqs. (21)–(22)；物理页 8，时间步说明）这提高的是内部状态和源信号的时间分辨率；电网电流仍由较慢的 CPU 电路模型提供，论文没有说明 CPU 同步间隔内是否对这些输入作插值。

### 7. 闭锁时切换等效通路，并保留 CF、PF 先后投入过程

闭锁后，正常运行受控源被置零；等效电路中的开关断开，使六脉波二极管桥表达主变换器的闭锁导通关系，同时启用闭锁 CF 和 PF 的等效电压。[pdf:E07][pdf:E08][pdf:E09]（物理页 4–6，Figs. 4–5、Table 1）

在实时故障算例中，故障发生于 0.29 s，0.292 s 闭锁并投入闭锁 CF 电压，0.294 s PF 提供额外阻断电压。FMS 要等电流从反串联 IGBT 转移至 PF 后才断开，因此闭锁源出现两次阶跃。[pdf:E16][pdf:E17]（物理页 10，Section V-D；物理页 11，Fig. 15）

### 8. FPGA 执行预算及未披露的实现边界

FPGA 时钟为 100 MHz，即每周期 10 ns。作者报告，对每相 256 个 CF 进行串并行极值搜索需要 21 个时钟周期，即 210 ns；另用 4 个周期生成开关函数并更新电容，合计 25 个周期，对应 250 ns 仿真步。[pdf:E12][pdf:E13]（物理页 7，Table 2 前正文；物理页 8，Section V）

原文说明，N 个数的串行极值比较需要 N−1 个周期，并行树需要 `ceil(log₂N)` 个周期；对 256 个数分别为 255 与 8 个周期。实际采用的 21 周期串并行组织没有给出分组数、比较树结构或流水调度，因此不能据此重建唯一 RTL。[pdf:E13]

普通逐个更新路径每个 CPU 步最多完成 120 次状态转换。正文报告实际 `Nref,j` 每个 CPU 步的变化小于 10，但没有说明该统计是否排除了整链极性反转；按 Fig. 8，整链反转显然走专用并行路径，不能机械地套用逐个更新预算。[pdf:E11][pdf:E13] 数值字长、fixed-point 或 floating-point 格式、舍入方式及 PCIe 延迟均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文具有明确数学模型。推导主线是：先用电压叠加表达链式模块，再用电容积分保留内部动态，最后把这些状态汇总为外部等效电压。

### 1. 为什么 CF 与 PF 都不可省略

正常运行的 chainlink 补偿三电平电压与基波、三次谐波参考之间的差：

$$
v_{cl,j}(\theta)=v_{3lc,j}(\theta)-v_{1h,j}(\theta)-V_{3h,j}\sin(3\theta).
$$

其中 `j` 为相别，`θ` 为换流器角度，`v3lc,j` 是三电平输出，`v1h,j` 是目标基波，`V3h,j` 是注入的三次谐波幅值。作者采用三次谐波注入，把所需 chainlink 电压幅值限制在约 `±vdc/4`。[pdf:E03]（物理页 3，Eqs. (1)–(5)）物理意义是让 CF 只合成主变换器没有提供的差额，从而减少所需模块。

但这组 CF 的电压不足以独立阻断最不利的交流侧故障馈入。论文给出阻断电压关系：

$$
2\left(\frac{v_{dc}}4+v_{PF,blk}\right)=\hat m_{max}\frac{v_{dc}}2\sqrt3.
$$

采用最大调制比 `m̂max=1.26`，作者将保护支路所需电压写为 `vPF,blk=0.3vdc`，从而得到：

$$
N_{PF}=\frac{0.3v_{dc}}{v_{dc}/4}N_{CF}=1.2N_{CF}.
$$

这些关系见物理页 3，Eqs. (6)–(8)。[pdf:E03] 当每相 CF 为 256 个时，`1.2×256=307.2`，向上取整为 308，与测试系统明确报告的 PF 数量一致。[pdf:E13] 向上取整是对设计数量的解释，不是原文另列的公式。

### 2. 从单个电容积分到整条 chainlink 电压

电容的基础关系是电流等于电容乘以电压变化率。对 FBSM，开关状态决定相电流以何种方向进入电容，因此：

$$
v^i_{c,j}(t+\Delta t)=v^i_{c,j}(t)+\frac{s_{i,j}i_j\Delta t}{C_{SM}},
\qquad s_{i,j}\in\{-1,0,1\}.
$$

`C_SM` 为 CF 电容，`vᶦc,j` 为第 i 个模块电容电压，`i_j` 为相电流，`Δt` 为仿真步长；三个状态依次表示负插入、旁路和正插入。整链正常输出是：

$$
v_{ncl,j}=\sum_{i=1}^{N_{CF}}s_{i,j}v^i_{c,j}.
$$

这是物理页 5 的 Eqs. (12)–(13)。[pdf:E08] 该表示保留了每个电容的记忆，但对电网只暴露电压之和，是 CEM 能缩小网络而不直接退化成平均模型的关键。

### 3. 正常与闭锁电压源如何组成

按正文 Eq. (9)，正常运行源为：

$$
V_{deblk,j}=b\left(v_{ncl,j}-v_{3lc,j}\right),
\qquad
v_{3lc,j}=s_{T1,j}v^{up}_{pc}-s_{T2,j}v^{lo}_{pc}.
$$

`b` 是运行模式系数，`sT1,j` 和 `sT2,j` 是上下 director switch 的开关函数，`vpc` 为 DC pole capacitor 电压。闭锁源为：

$$
V_{blk,j}=\bar b\left(v_{bcl,j}+v_{pb,j}\right).
$$

这些式子见物理页 5，Eqs. (9)、(11)、(16)。[pdf:E08] 从工况逻辑和 Table 1 可重建为：解锁时 `b=1、b̄=0`，闭锁时 `b=0、b̄=1`。[pdf:E09]

闭锁 CF 的电压按 Eq. (14) 使用整流后的电流幅值累积：

$$
v_{bcl,j}(t+\Delta t)=\sum_{i=1}^{N_{CF}}\left(v^i_{c,j}(t)+\frac{|i_j|\Delta t}{C_{SM}}\right).
$$

PF 的正文 Eq. (15) 则印为：

$$
v_{pb,j}(t+\Delta t)=\sum_{i=1}^{N_{PF}}\left(v^i_{c,PF,j}(t)+\frac{i_j\Delta t}{C_{SM,PF}}\right),
$$

其中 `C_SM,PF` 为 PF 电容，`vᶦc,PF,j` 为其电压。[pdf:E08]（物理页 5，Eqs. (14)–(15)）

**原文存在需要复现者消歧的符号不一致。** Eq. (10) 对闭锁模式的系数写法与 Table 1 的互补工况不一致；Eq. (9) 写 `vncl−v3lc`，Fig. 5(a) 旁注写成加号；PF 的 Eq. (15) 使用 `i_j`，Table 1 使用 `|i_j|`。[pdf:E08][pdf:E09] 按闭锁后二极管整流、模块电容被充电的物理描述，幅值写法更自然，但这属于物理解释，不能据此断言作者实际代码采用了哪种符号约定。

### 4. DC pole capacitor 通过 KCL 保留耦合

正常运行时，CEM 的 AC、DC 电路在网络结构上解耦，电容电流由直流电流与导通相电流重建；闭锁时改用受控源支路测量电流：

$$
i^{up}_{calc}=b\left(i_{dc}-\sum_j s_{T1,j}i_j\right)+\bar b\,i^{up}_{pc},
$$

$$
i^{lo}_{calc}=b\left(i_{dc}+\sum_j s_{T2,j}i_j\right)+\bar b\,i^{lo}_{pc}.
$$

随后对上下极分别积分：

$$
v^{up/lo}_{pc}(t+\Delta t)=v^{up/lo}_{pc}(t)+\frac{i^{up/lo}_{calc}\Delta t}{C_{pc}}.
$$

`i_dc` 是 DC 侧电流，`i_pc` 是对应受控源的测量电流，`C_pc` 是 pole-to-ground DC 电容。上述关系来自物理页 6，Eqs. (17)–(20)。[pdf:E09] 工程意义是电路节点虽然减少，AC/DC 间的电流平衡仍通过状态更新传递。

### 5. 120 小步平均到底平均了什么

论文定义：

$$
\tau=\frac{T_{CPU}}{T_{FPGA}},
\qquad
\bar v_{cs}(t+T_{CPU})=\frac1\tau\sum_{k=1}^{\tau}v_{cs}(t+kT_{FPGA}).
$$

`v_cs` 是 FPGA 计算的受控源信号。代入实际步长即：

$$
\bar v_{cs}(t+30\,\mu s)=\frac1{120}\sum_{k=1}^{120}v_{cs}(t+k\cdot250\,ns).
$$

公式及参数分别见物理页 6，Eqs. (21)–(22)，以及物理页 8 的实现说明。[pdf:E10][pdf:E13] 这相当于让 CPU 看到一个宏步内的离散平均源值，减少只取末值造成的偏差；它没有重建宏步内真实电网电流与开关事件的完整先后关系。

## § 7 — 实验设计与结论

### 问题一：合并等效模块后，正常功率动态是否改变？

**问题 →** CEM 缩小电路后，能否保持 DEM 的正常运行动态？  
**实验 →** 离线 DEM 与 CEM 在相同测试系统、相同 30 μs 步长下运行：初始零功率，0.2 s 指令变为从 DC 向 AC 传输 1000 MW，0.4 s 将同等功率反向传输。比较有功功率、a 相电流及 a 相 CF 电容电压总和。[pdf:E11][pdf:E13][pdf:E14]（物理页 7–8，Section V、Fig. 10）  
**答案 →** 图中两种模型的曲线高度重合，作者据此认为 CEM 保留了正常功率调节动态。论文未报告 RMSE、最大误差或误差随步长变化的结果。[pdf:E14]

### 问题二：闭锁及故障恢复时，电路等效是否仍成立？

**问题 →** 正常运行等效能否延续到二极管导通及保护支路投入后的状态？  
**实验 →** 离线模型在电缆中点施加 P–P fault，故障时刻为 0.39 s，0.56 s 清除，比较功率、交流电流、直流电流及直流电压。[pdf:E13][pdf:E15]（物理页 8–9，Section V-B、Fig. 11）  
**答案 →** 两种模型的闭锁、充电恢复和重新送电波形吻合。正文报告 DC pole capacitor 放电使故障电流在 0.392 s 达到 −42 kA，交流侧电流则在阻断后降至零。[pdf:E15]（物理页 9，Fig. 11 及相邻正文）这验证了作者展示的中点 P–P 故障过程，没有形成故障位置、故障电阻或保护延迟的参数扫描。

### 问题三：实时实现是否保留了逐模块电压行为？

**问题 →** CPU–FPGA 多速率实现是否只对端口量有效，而丢失模块级动态？  
**实验 →** 在 1000 MW 稳态下比较离线 CEM 与实时 CEM，展示 CF 电压总和、上极 DC 电容电压、选出的十个 CF 电容电压，以及 chainlink、三电平和等效源电压。[pdf:E15][pdf:E16]（物理页 9，Fig. 12；物理页 10，Fig. 13）  
**答案 →** 总量和源电压曲线接近，十个 CF 展示出插入充放电、旁路保持的行为。Fig. 12 的逐模块轨迹并不逐条相同；它支持相近的均压行为，不能据此认定模块编号对应的开关序列完全一致。[pdf:E15]

### 问题四：实时模型能否表达 CF 与 PF 的分阶段闭锁？

**问题 →** 多速率实现是否正确表达保护动作的先后关系？  
**实验 →** 实时比较算例在 0.29 s 故障，0.292 s 闭锁，0.294 s 投入 PF 阻断电压，0.39 s 清除故障，0.46 s 解锁，并将功率参考恢复至 1000 MW；比较整体电压电流、各等效源及选出的 CF、PF 电容电压。[pdf:E16][pdf:E17]（物理页 10–11，Figs. 14–16）  
**答案 →** 实时与离线 CEM 的波形接近，闭锁源显示 CF 与 PF 依次投入的两级变化，故障恢复后均压重新工作。恢复时相电流增大，模块电压纹波也随之增大。[pdf:E17][pdf:E18]（物理页 11–12，Figs. 15–17）此处的 0.29 s 故障与前一离线验证的 0.39 s 故障属于不同算例。

### 问题五：FPGA 资源与时间预算是多少？

物理页 7 的 Table 2 完整数据如下。表前明确说明该资源配置处理 **768 个 FBSM**，时钟为 100 MHz。[pdf:E12]

| FPGA resource | Used | Utilization | Available |
|---|---:|---:|---:|
| Slices | 59,791 | 78.78% | 75,900 |
| Registers | 163,663 | 26.95% | 607,200 |
| LUTs | 182,110 | 59.98% | 303,600 |
| RAM36 | 218 | 21.17% | 1,030 |
| RAM18 | 51 | 2.48% | 2,060 |
| DSP Blocks | 0 | 0% | 2,800 |

**768 恰好等于三相 CF 总数，而完整测试拓扑含 1692 个 CF+PF。** 论文没有单列 PF 的资源、状态存储和计算映射，因而不能将 Table 2 无条件解释为逐个实现全部 1692 个 FBSM 的完整资源分解。[pdf:E12][pdf:E13] 同样，正文引用平台可模拟多达 6000 个 SM 的既有结果，来源是 [15]，不是本文对 H3LC 完成的规模实测。[pdf:E10]

报告的时序预算为：[pdf:E12][pdf:E13]（物理页 7–8，Sections IV-B、V）

| 环节 | 报告周期或步长 | 对应时间 |
|---|---:|---:|
| FPGA 时钟 | 1 cycle | 10 ns |
| 串并行极值搜索 | 21 cycles | 210 ns |
| 开关函数生成与电容更新 | 4 cycles | 40 ns |
| 一个 FPGA 仿真步 | 25 cycles | 250 ns |
| 一个 CPU 仿真步 | 120 个 FPGA 步 | 30 μs |

这给出了计算内核的预算说明。论文没有提供独立的 PCIe 延迟表、CPU 分项执行时间、最坏执行时间分布或实现后的 timing slack；DSP 使用为零也不足以反推出采用了哪种数值格式。

### 问题六：离线 CEM 比已有模型快多少？

作者在 MATLAB/Simulink 2014b 中模拟 1 s 系统过程，计算机为 2.8 GHz Intel Core i5-7440HQ、8 GB RAM、Windows 10。[pdf:E17]（物理页 11，Section V-E）物理页 12 的 Table 3 完整报告如下：[pdf:E18]

| Numbers of FBSMs per phase | DM CPU time / s | DEM CPU time / s | CEM CPU time / s | Efficiency improvement of CEM to DEM |
|---:|---:|---:|---:|---:|
| 30 | 123 | 44 | 32 | 27.3% |
| 60 | 1,204 | 61 | 47 | 23.0% |
| 90 | 2,506 | 76 | 59 | 22.4% |
| 120 | 4,624 | 95 | 75 | 21.1% |
| 256 | 30,464 | 168 | 139 | 17.3% |

这里的 improvement 对应相对 DEM 的耗时削减，例如最大规模是从 168 s 降至 139 s；不能把 17.3% 读成速度提高 17.3 倍。作者将规模增大时收益比例下降解释为：chainlink FBSM 的计算占比逐渐增大，简化三电平部分带来的相对收益随之缩小。[pdf:E18]（物理页 12，Table 3 后正文）表头没有为各规模分别列出 CF、PF 数量，不应自行补齐未报告的 PF 配置。

总体证据支持在所示系统上的实时可运行性与波形一致性。准确性主基线是离线 DEM、CEM，DM 出现在耗时比较中；文中没有展示以全系统更小步长 DM 为基准的精度收敛研究，也没有 PS-VBC 对 full-sorting 的资源与均压效果消融表。[pdf:E11][pdf:E13][pdf:E18]

## § 8 — Take-aways

**5 句话。** CEM 的关键是减少进入电网求解器的开关网络，同时保留逐 CF 电容状态。[pdf:E07][pdf:E08] 正常 chainlink、保护支路和三电平主变换器被合并为统一的等效分支。[pdf:E07][pdf:E08] PS-VBC 用决策所需的极值搜索代替完整排序，并为整链极性反转设置专门路径。[pdf:E11] 实际系统采用 CPU 30 μs、FPGA 250 ns，并将每 120 个 FPGA 小步的源信号平均后交给 CPU。[pdf:E10][pdf:E13] 已展示工况的波形与离线模型接近，但完整 PF 硬件映射和更细参考步长下的误差仍缺少报告。[pdf:E12][pdf:E13][pdf:E18]

**3 句话。** 本文把电路降阶、逐模块更新、均压选择和通信压缩联合设计成 H3LC 实时仿真方案。[pdf:E07][pdf:E10][pdf:E11] 硬件证明集中在 250 ns 内部内核和报告的 FPGA 资源，精度证明集中在正常功率调节及中点 DC P–P fault 的波形比较。[pdf:E12][pdf:E13][pdf:E16] 阅读时必须区分完整拓扑的 1692 个 FBSM、Table 2 的 768 个 FBSM 配置，以及只属于 FPGA 内部计算的 250 ns 步长。[pdf:E12][pdf:E13]

**1 句话。** 这篇论文说明，把快速内部状态从电网节点求解中分离，可以让复杂混合换流器实时运行，但内部小步长的收益仍受较慢 CPU 电路和接口交换所限定。[pdf:E08][pdf:E10][pdf:E13]

## § 9 — 最脆弱的假设

**失败代价最大的假设是：CPU 宏步内没有被电网求解器解析的快速电流变化，不会显著改变 FBSM 充放电、二极管导通和闭锁过程，因此细步内部计算加平均源接口足以重现目标动态。** 这个假设比 FPGA 是否还能容纳更多模块更根本，因为它决定 250 ns 内部计算是否获得了足够及时的物理输入。[pdf:E08][pdf:E10][pdf:E13]（物理页 5，Eqs. (13)–(16)；物理页 6，Fig. 7、Eq. (22)；物理页 8，实现步长）

实际系统若在一个 CPU 步内发生电流快速换向、近端故障激起的高频振荡，或者主变换器换相与保护动作紧邻，FPGA 可能用较慢更新的电流完成许多小步。电容增量依赖开关状态与电流的乘积，均压选择又依赖电流符号，因此相同的宏步平均电压未必对应相同的电容轨迹和导通顺序。这是由论文方程推出的风险，而不是论文报告的失败现象。

作者给出的支持证据是正常运行和中点 DC 故障下，实时模型与离线模型的整体及部分模块波形接近。[pdf:E15][pdf:E16][pdf:E17] 缺少的关键证据是相对于更细全系统参考解的步长收敛、CPU 同步相位扫描，以及强烈宏步内电流变化下的模块级误差。离线 CEM、DEM 同样采用 30 μs，使当前比较不足以独立识别共同的时间离散偏差。[pdf:E11][pdf:E13]

## § 10 — 最小复现实验

**一周内最值得复现的是 PS-VBC 内核：在不搭完整 HVDC 网络的情况下，检验它能否按预算追踪插入指令并维持电容均压。** 以下是拟议实验，不是论文已完成的结果。

- **输入与状态。** 建立单相 256 个 CF，状态为逐模块电容电压和三值开关状态；用论文 Eq. (4) 的结构合成 chainlink 参考，再按 nearest level control 得到目标插入数。[pdf:E03][pdf:E06][pdf:E13] 初始电压扰动、电流幅值和频率作为自选实验参数公开记录；由于本文没有给出完整电容参数，可用每步归一化充电量表达电流强度。
- **两个实现。** 一个严格按 Fig. 8 执行 PS-VBC，包含每步单模块更新和全插入时的极性并行反转；另一个使用完整排序作决策参考。两者采用相同输入和 Eq. (13)，隔离电路模型、通信与均压算法差异。[pdf:E08][pdf:E11]
- **工况。** 覆盖正负插入、正负电流、目标连续变化、接近每宏步更新预算的变化，以及全插入后的极性反转；正常轨迹与压力轨迹分开统计。
- **测量。** 记录目标与实际插入数之差、追踪所需小步数、各模块电压、最大最小电压差、整链输出电压，以及完整排序与 PS-VBC 的决策差异。把一个 FPGA 步视为 250 ns、一个 CPU 步视为 120 个小步，核对逻辑吞吐量。[pdf:E13]

支持结果应包括：普通变化在允许的小步预算内完成，全链反转在专用单步路径完成，周期运行中电压离差与 full-sorting 参考保持同一量级。若预算内命令仍无法追上，或者 full-sorting 能维持均压而 PS-VBC 的离差持续扩大，就能反驳相应算法 claim。软件实验不能验证 21 周期搜索、250 ns 硬件时序或 Table 2 资源；这些需要 RTL 与综合实现。

## § 11 — 最强反例设计

**最有力的反例是制造 CPU 宏步内的电流换向，使正确均压决策和闭锁导通顺序依赖被平均接口丢弃的事件次序。** 论文现有的中点故障给出了显著暂态，却没有系统改变故障相对于 CPU 同步和三电平换相的相位。[pdf:E13][pdf:E16][pdf:E17]

拟议实验保持换流器拓扑与控制结构不变，把故障向换流器端移动，并改变线路电感、电容组合，使故障后的电流变化时间接近 CPU 宏步。随后在整个 30 μs 同步窗口内扫描故障施加时刻，重点覆盖三电平换相及 CF 极性反转附近。物理目标不是任意制造不连续输入，而是得到宏步内具有不同过零时刻和导通顺序的真实电路响应。

比较三个层次：论文的 30 μs/250 ns 多速率 CEM；全电路统一采用 250 ns、再以更小步长检查收敛的 CEM；以及用于检查电路等效本身的较小规模 DM。这样可以把电路表示错误与时间划分错误分开。

主要评价对象应是电流峰值、交流侧电流熄灭时刻、最大单模块电压及源信号阶跃时序，而不只是功率平均值。如果统一小步 CEM 与 DM 一致，多速率模型却出现随同步相位系统变化的模块过充或闭锁时序偏差，就能直接挑战核心实时接口假设。其最强替代解释是：原论文中的吻合部分来自离线、实时模型共享较粗电网时间尺度，而不是平均接口普遍保留了快速暂态。

## § 12 — Follow-up Research Bet

### 主 idea：把 FBSM 群体改写为电压分布动力学

**新的研究问题是：能否不再以逐模块身份列表为基本状态，而用按插入状态分组的电压分布，直接描述极值驱动的均压过程，并研究换流器规模变化时的群体动态？** 目标能力是把模块数量从必须逐项实例化的硬件规模，变为可以主动扫描的群体参数，使不同规模、初始分布和插入命令下的电压群体演化成为可计算对象。这是候选研究押注，不是本文已有结论。

其机制来自本文模型中一个很强的结构：在同一相、相同电容值下，具有相同插入状态的模块共享相电流，因此 Eq. (13) 对它们施加相同的电压平移；PS-VBC 又只从特定集合的电压极端选择一个模块。[pdf:E08][pdf:E11]（物理页 5，Eq. (13)；物理页 7，Fig. 8）由此可将三个插入状态分别表示为经验测度：

$$
\mu_s(v,t)=\frac1N\sum_{i:s_i(t)=s}\delta\left(v-v_i(t)\right),\qquad s\in\{-1,0,1\}.
$$

这是本节提出的新表示，不是论文公式。每个时间步中，充放电对应分布沿电压轴的平移；插入与旁路对应在分布极端搬移质量为 `1/N` 的原子；全链反转对应交换正、负插入分布；链电压由带符号的一阶矩得到。硬件随之从逐模块电压寄存器与身份索引选择，改为分布输运、分位端点和质量搬移的数据通路。

**这改变了状态表示、硬件映射和评价对象，也改变了研究目标。** 原论文主要问固定测试系统能否实时重现波形；新工作要问有限数量的极值选择，如何形成电压分布的聚集、展宽或群体分裂，以及这些现象怎样随模块数与命令变化速率改变。主要评价对象应从选出的十条电容轨迹，转为完整分布、极端尾部、插入集合组成和链电压之间的关系。

本文有两项具体结果支持探索这一方向。第一，Fig. 12 中离线、实时的个体轨迹不同，而总电压与宏观均压行为接近，提示模块身份未必是某些系统级问题的必要科学对象。[pdf:E15]（物理页 9，Fig. 12）第二，Table 3 中 CEM 相对 DEM 的耗时削减从 27.3% 降至 17.3%，作者解释为模块计算占比随规模增大而上升；继续只缩减外部电路，收益会受到内部计算的制约。[pdf:E18]（物理页 12，Table 3 及后文）这些现象支持研究动机，尚不能证明分布表示足够准确。

**最大的研究收益**是让群体规模和电压分布本身成为设计变量，并可能把硬件成本从模块数量转向分布复杂度。**最大的科学风险**是均压恰恰由质量只有 `1/N` 的极端模块决定：连续化或有限分辨率表示可能保留均值，却丢掉支配下一次决策的尾部信息，最终改变群体演化。即使宏观电压看起来正确，这个风险也可能使新理论失败。

最小区分实验应给出两组均值相同、低阶统计量接近但极端尾部不同的初始电压群体，对它们施加完全相同的电流与插入命令，比较逐模块 PS-VBC、新的分布动力学，以及仅保留均值或少量矩的模型。若只有逐模块模型能产生尾部依赖的后续差异，分布机制失败；若分布模型能重现该差异，而矩模型不能，就能排除收益仅来自普通平均化这一替代解释。随后才值得比较不同模块规模下的计算量和 FPGA 映射。

与最近工作的实质区别是：按本文介绍，[18] 优化的是基于模块选择的 FPGA 脉冲与均压计算，[28] 主要缩减外部等效电路，本文则把这些计算组织成 H3LC 实时系统。[pdf:E02][pdf:E05][pdf:E11] 新押注要替换的是内部状态的数学对象，并将电压群体及其尺度效应作为实验对象。本文未给出可用于精确对齐的串并行分组、数值字长，也没有补充这些细节的附录，因此首轮只能比较数学内核，不能把预期资源收益归因于未公开的 RTL 细节。[pdf:E13] 判断这一分布表示是否具有文献新颖性，还需补读 [18]、[28] 的完整状态实现，以及本文没有讨论的相关分布建模工作。

**Wild-card alternative：** 将正常时被旁路的 PF 支路重新设计为可独立交换储能的物理端口，研究它能否与 CF 分担 AC/DC 功率脉动并改变电容容量配置；这押注于新拓扑自由度，而不是新的状态表示。[pdf:E03]

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title, authors, journal masthead, publication dates, DOI, and Abstract"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Section I: H3LC motivation, DM/DEM/average-value models, prior CPU–FPGA work, and proposed modeling partition"
[pdf:E03]: <_evidence/E03-p003-page.png> "PDF 物理页 3，Fig. 1; Section II-A; Eqs. (1)–(8): topology, normal operation, blocking, and CF/PF sizing"
[pdf:E04]: <_evidence/E04-p012-page.png> "PDF 物理页 12，References [3] and [14]–[16]"
[pdf:E05]: <_evidence/E05-p013-page.png> "PDF 物理页 13，References [18] and [27]–[29]"
[pdf:E06]: <_evidence/E06-p004-page.png> "PDF 物理页 4，Section II-B and Fig. 2: higher/lower-level controls, energy balancing, nearest level control, and VBC"
[pdf:E07]: <_evidence/E07-p004-page.png> "PDF 物理页 4，Section III and Figs. 3–4: DEM components and CEM circuit structure"
[pdf:E08]: <_evidence/E08-p005-page.png> "PDF 物理页 5，Section III; Figs. 5–6; Eqs. (9)–(16): equivalent sources, switching states, and CF/PF capacitor updates"
[pdf:E09]: <_evidence/E09-p006-page.png> "PDF 物理页 6，Eqs. (17)–(20) and Table 1: DC pole capacitor calculations and source signals in each operation mode"
[pdf:E10]: <_evidence/E10-p006-page.png> "PDF 物理页 6，Section IV-A, Fig. 7, and Eqs. (21)–(22): CPU–FPGA partition, PCIe interface, signal count, and multirate averaging"
[pdf:E11]: <_evidence/E11-p007-page.png> "PDF 物理页 7，Section IV-B and Fig. 8; opening of Section V: PS-VBC, full-chain polarity reversal, and offline reference setup"
[pdf:E12]: <_evidence/E12-p007-page.png> "PDF 物理页 7，Table 2 and preceding paragraph: full FPGA resource utilization, 768-FBSM configuration, and 100 MHz clock"
[pdf:E13]: <_evidence/E13-p008-page.png> "PDF 物理页 8，Section V implementation and test-system paragraphs; Fig. 9: 30 μs/250 ns steps, 21+4 cycles, τ=120, CF/PF counts, and system parameters"
[pdf:E14]: <_evidence/E14-p008-page.png> "PDF 物理页 8，Section V-A and Fig. 10: offline normal-operation validation and power reversal"
[pdf:E15]: <_evidence/E15-p009-page.png> "PDF 物理页 9，Sections V-B–V-C and Figs. 11–12: offline DC fault, reported fault-current peak, and real-time normal-operation comparison"
[pdf:E16]: <_evidence/E16-p010-page.png> "PDF 物理页 10，Fig. 13; Fig. 14; Section V-D: normal source voltages and real-time fault/blocking/recovery sequence"
[pdf:E17]: <_evidence/E17-p011-page.png> "PDF 物理页 11，Figs. 15–16 and Sections V-D–V-E: staged CF/PF insertion, capacitor traces, and offline timing benchmark setup"
[pdf:E18]: <_evidence/E18-p012-page.png> "PDF 物理页 12，Fig. 17; Table 3 and adjacent discussion; Section VI: fault recovery, full offline execution-time table, scaling explanation, and conclusions"
