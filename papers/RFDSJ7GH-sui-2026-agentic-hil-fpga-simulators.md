# Agentic HiL: A Multi-Agent LLM Framework for Autonomous Generation of FPGA-based Real-Time Power Electronics Simulators

- **作者**：Qingcheng Sui, Yang Li, Jiaze Kong, Yu Zuo, Wilmar Martinez
- **出处**：IEEE Energy Conversion Congress and Exposition (ECCE 2026)
- **年份**：2026
- **DOI**：未报告
- **Zotero key**：RFDSJ7GH

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

碳化硅（SiC）等宽禁带器件将现代电力电子变换器的开关频率推向数百千赫兹，迫使硬件在环（HiL）实时仿真的离散积分步长 $\Delta t$ 压缩至亚微秒乃至数十纳秒级（物理页 1 Section I）[pdf:E02]。在此硬实时确定性延迟约束下，通用 CPU 受制于调度抖动与外设往返延迟无法闭合单步计算，FPGA 成为主导计算平台；同时，UltraZohm 等开源快速控制原型（RCP）与高速模型预测控制（FCS-MPC）均直接部署在 FPGA 上，促使业界探索“控制器与被控功率级仿真器共置于单颗商用 FPGA”的低成本闭环验证架构（物理页 1 Section I 与物理页 6 Section IV）[pdf:E02][pdf:E16]。

然而，将连续时间电路拓扑转化为在 FPGA 上以 $50\text{ ns}$ 步长运行的 Verilog RTL 面临三重跨学科壁垒（物理页 1 Abstract & Section I）[pdf:E01][pdf:E02]：
1. **连续物理与数值离散耦合**：需列写分段开关状态方程或伴随导纳矩阵，权衡显式/隐式积分稳定性，并精确处理二极管过零关断等断续导通模态（DCM）代数边界（物理页 2–3 Section II-A & III-A）[pdf:E05][pdf:E09]。
2. **定点量化与片上硬核位宽耦合**：整数位过窄会在启动浪涌时引发补码回绕饱和，小数位过窄则在微步长下因单步增量落入最低有效位（LSB）以下导致截断漂移，而总字长一旦跨过 `DSP48E1`（$25 \times 18\text{-bit}$）原语上限又会使硬核消耗倍增（物理页 3–4 Section II-A & III-A）[pdf:E07][pdf:E10]。
3. **超低延迟 RTL 编码与波形调试繁琐**：HiL 要求单步计算延迟 $t_{\text{calc}} \ll \Delta t$ 而非高吞吐深流水，且定点移位错位或符号扩展遗漏在闭环反馈下极难靠人工翻查 VCD 波形定位（物理页 3 Section II-B & II-C）[pdf:E08]。

本文提出 `Agentic HiL`（亦称 `Agentic HiL Coder`），用多智能体 LLM 串联物理离散定标、波形驱动 RTL 修复与低延迟综合闭环，尝试降低实时仿真器硬件开发门槛（物理页 1–2 Abstract & Fig. 1）[pdf:E01][pdf:E03]。

## § 2 — 前人工作与不足

作者围绕 FPGA 实时功率级仿真器生成梳理了三类前人路线及其核心瓶颈（物理页 1 Section I）[pdf:E02]：

1. **手工定制的电力电子 FPGA 实时仿真方法**（如 Lauss & Strunz `[2]`、Dinavahi 团队器件级与网络分析模型 `[3], [6], [7], [15]`、Bai 等人综述 `[4], [5]` 及 Milton & Benigni 延迟插入法 LIM `[14]`，物理页 1–2 & 6）[pdf:E02][pdf:E06][pdf:E16]：证明了预计算状态空间矩阵与伴随离散电路（ADC）可实现纳秒级开关瞬态仿真，但从方程离散、定点对齐到 Testbench/VCD 排错全靠跨学科专家手写，单个简单拓扑常耗时数天（物理页 2 Fig. 2 与物理页 5 Section III-C）[pdf:E04][pdf:E14]。
2. **面向数字逻辑的多智能体硬件生成框架**（AutoGen `[11]`、ReAct `[12]` 与 NVIDIA `VerilogCoder` `[13]`，物理页 1 Section I）[pdf:E02]：`VerilogCoder` 利用任务图规划与 AST 波形追踪修复 FSM 等数字逻辑，但缺乏物理与数值机制——既不能从电路拓扑列写稳定离散方程，也只会做逐比特布尔比对，无法区分合法的定点量化底噪与移位/溢出引发的数值发散，更缺乏 $t_{\text{calc}} \ll \Delta t$ 的单步低延迟约束意识（物理页 1 Section I 与物理页 3 Section II-B/C）[pdf:E02][pdf:E08]。
3. **工业界模型驱动 HDL 生成工具**（MATLAB/Simulink `HDL Coder` 与 `Simscape HDL Workflow Advisor`，物理页 1 Section I 与物理页 5–6 Section III-C）[pdf:E02][pdf:E14][pdf:E15]：具备成熟的框图转 HDL 与定点支持，但作者指出其预设物理建模、离散策略选择与定点字长整定已由领域专家手动完成，前端建模与参数探索仍高度依赖人工介入。

## § 3 — 重建作者的思考路径

站在 `VerilogCoder` 与经典电力电子 FPGA 求解算法（作者此前已有高频 Boost FPGA MPC 基础 `[10]`，物理页 6）[pdf:E16] 的交汇点逆向推演：

1. **为什么不能让单个 LLM 从拓扑一步生成定点 Verilog？** 一步直译时，波形出错无法分辨是微分方程列错、欧拉格式失稳、定点饱和，还是 Verilog 右移错了一位。必须切出中间锚点：先在软件层生成经验证的**可执行定点 C 黄金参考模型（`model_fixed.cpp`）**，再让硬件端智能体只对 RTL 与黄金模型的数值等价负责（物理页 2 Fig. 1 & Fig. 2）[pdf:E03][pdf:E04]。
2. **没有人工标准答案时，前端如何自证方程没列错？** 同一直流变换器可独立走前向欧拉状态空间（`SS+FE`）、后向欧拉状态空间（`SS+BE`）和诺顿伴随节点分析（`ADC+MNA+BE`）三条推导路径。只要三者在微步长下浮点波形高度吻合（RMSE 低于阈值），即可在进入硬件前大概率排除建模与离散错误，再据此统计动态峰值并扫描小数位宽锁定 Q 格式（物理页 2–3 Section II-A）[pdf:E05][pdf:E06][pdf:E07]。
3. **硬件仿真如何替代人工查 VCD？** 将布尔判据替换为相对黄金参考的**逐拍物理波形 RMSE**：当移位错位或乘法回绕引发电流/电压 RMSE 突刺时，结合 VCD 异常时刻与 `Pyverilog` AST 算术依赖树反向回溯，即可定位故障赋值节点（物理页 2 Fig. 1 与物理页 3 Section II-B）[pdf:E03][pdf:E08]。
4. **如何守住 $50\text{ ns}$ 单步硬实时边界？** 摒弃吞吐率导向的深流水，按原语定制最小流水深度（用 `DSP48E1` 时取 4 级原生流水，纯 LUT 时压为单拍组合逻辑），并用同源高频时钟分频使能消除跨时钟域握手开销（物理页 3 Section II-C 与物理页 5 Section III-C）[pdf:E08][pdf:E13]。

## § 4 — 核心 Intuition

通用硬件智能体在实时电力电子仿真上失灵的根源，是把连续系统离散误差、定点动态范围量化和 RTL 位操作缺陷混在同一个布尔仿真反馈环里。本文的核心支点是**以“多离散路线互验的定点 C 黄金模型”为隔离墙做两级解耦**：前半程在软件域用三求解器交叉验证与位宽扫描锁死物理精度和 24-bit 定点格式，后半程在硬件域以物理波形 RMSE 为探针驱动 VCD-to-AST 算术节点回溯，配合贴合原语潜伏期的最小流水规划闭合亚微秒单步时序（物理页 2 Fig. 1 & Fig. 2，物理页 3 Section II）[pdf:E03][pdf:E04][pdf:E07][pdf:E08]。

## § 5 — 具体方法与完整 Pipeline

### 5.1 正面回答本次阅读重点（Focus 四问深度拆解）

1. **Physics / Debug / Hardware 各角色的具体输入输出**：
   正文分设三个子模块，而架构图 Fig. 1 与 Fig. 2 将后两者整合在后端 `Hardware Agent` / `Verilog Agents` 闭环内（物理页 2–3 Section II, Fig. 1 & Fig. 2）[pdf:E03][pdf:E04][pdf:E08]：
   - **Physics-Aware Modeling Agent**：**输入**为自然语言拓扑与器件参数描述（第 IV 节确认当前未接 SPICE 网表，物理页 6 Section IV）[pdf:E16] 及目标时钟与步长 $\Delta t$。**执行** KVL/KCL 建模、`SS+FE` / `SS+BE` / `ADC+MNA+BE` 三路线互验、静态动态范围分析与小数位宽扫描（物理页 2–3 Section II-A）[pdf:E05][pdf:E06][pdf:E07]。**输出**浮点脚本 `model.py`、可执行 C 定点黄金模型 `model_fixed.cpp` 与封装了 $\Delta t$、离散系数及 Q 格式约束的 `spec.json`（物理页 2 Fig. 1 & Fig. 2）[pdf:E03][pdf:E04]。
   - **Hardware Architecture & Synthesis Loop**：**输入**为 `spec.json`、`model_fixed.cpp` 与目标 FPGA 原语/时钟约束。**执行**算子并行映射（绑定独立 `DSP48E1` 或纯 LUT 组合乘法器）、面向 $t_{\text{calc}} \ll \Delta t$ 的最小流水级数规划与静态时序检查；违例时仅在瓶颈路径局部插寄存器（物理页 2 Fig. 1 与物理页 3 Section II-C）[pdf:E03][pdf:E08]。**输出**约 200 行求解器核 `solver_core.v` 与约 200 行板级顶层代码（MMCM、分频使能、PWM 与 DAC 接口，合计不足 500 行，物理页 2 Fig. 2 与物理页 5 Section III-C）[pdf:E04][pdf:E14]。注：Fig. 1 标注工具链为开源 `iverilog / yosys / Pyverilog` [pdf:E03]，但 Zynq-7020 上板实测依赖 Xilinx `DSP48E1`、`MMCM` 与厂商时序闭环（物理页 5–6 Section III-C & Table IV）[pdf:E13][pdf:E15]。
   - **Waveform-Driven Hardware Debugging Agent**：**输入**为 `iverilog` 仿真 `solver_core.v` 生成的 `.vcd` 波形、`model_fixed.cpp` 黄金序列及 `Pyverilog` 解析的 RTL AST（物理页 2 Fig. 1 & Fig. 2，物理页 3 Section II-B）[pdf:E03][pdf:E04][pdf:E08]。**执行**逐拍波形 RMSE 检验；遇电流/电压误差尖峰时沿 VCD 跳变向 AST 算术节点反向回溯，定位移位错位、缺失有符号扩展或乘法器回绕溢出。**输出**节点级修复补丁并交由 `Verilog Coder: Repair` 重写 `solver_core.v`（物理页 2 Fig. 2 与物理页 3 Section II-B）[pdf:E04][pdf:E08]。

2. **状态空间（SS）与 ADC+MNA 两条离散路线如何在 DCM 和定点位宽上工作**：
   - **DCM 机制**：SS 路线离线预计算各开关模态离散矩阵 $\Phi_{M_s}, \Gamma_{M_s}$ 供在线查表选通（物理页 2 Eq. (1)）[pdf:E05]。在二极管整流 Buck 中，除主管导通充电与关断续流外，当电感电流跌穿零点时二极管反向阻断，进入第三种电感开路死区模态（物理页 3 Section III-A & Fig. 3）[pdf:E09]。Fig. 10 内部信号揭示了其硬件细节：RTL 先算出未钳位的 24 位有符号候选电流 `iL_n[23:0]`（过零时出现 `0xFFFF_FDE7C` 等负数补码），随即置位 `dcm` 标志、以 `iL_pos[23:0]` 强制零电流钳位并切入电容独立放电方程（物理页 5 Fig. 10）[pdf:E13]。ADC+MNA 路线将电感电容化为后向欧拉诺顿伴随导纳与历史电流源装配 $Y \cdot v = i$（物理页 2 Eq. (2)）[pdf:E06]。虽然正文称 ADC 用受控源表示开关从而保持 $Y$ 恒定，但恒导纳开关在 DCM 下必产生虚拟损耗与寄生振荡；本文软件侧 `ADC+MNA+BE` 与 `SS+BE` 呈微伏级无损重合（物理页 3 Section III-A）[pdf:E09]，说明其软件验证仍按理想/二值开关切模态求解，且最终上板的 Buck/Boost 硬件核全为显式展开的状态空间乘加结构，并未实现在线求解 $Y \cdot v = i$ 的 MNA 硬件电路（物理页 5–6 Section III-C & Table IV）[pdf:E13][pdf:E15]。
   - **定点位宽机制**：采用含符号位的 $Q_m.n$ 格式。先由全时域浮点包络（覆盖启动浪涌峰值）定整数位 $m$ 防饱和（$24\text{ V}$ Buck 取 `Q7.17` 覆盖 $\pm 64\text{ V}$，Boost 取 `Q9.15` 覆盖 $\pm 256\text{ V}$），再扫小数位 $n$ 将总字长定在 **24-bit**——恰好卡在 `DSP48E1` 的 $25 \times 18\text{-bit}$ 输入上限内实现单 DSP 乘加，内部保留 48-bit 乘积 `p01_s2[47:0]` 与累加和 `sum0_s3[47:0]`、`sum1_s3[47:0]`，末级再算术右移回 24-bit 状态寄存器（物理页 3–5 Section III & Fig. 10）[pdf:E09][pdf:E10][pdf:E11][pdf:E13]。

3. **生成扁平无 BRAM 电路在多开关 / 大规模复杂电力电子系统上的真实扩展死结**：
   生成电路对片上 `BRAM` 占用严格为 **0%**，全靠常数硬编码与组合/浅流水空间全展开（物理页 2 Fig. 1 与物理页 6 Table IV）[pdf:E03][pdf:E15]。推向多开关复杂拓扑（如八开关 DAB、LLC、三电平或 MMC）时面临四重死结：
   - **$O(N^2 \cdot 2^n)$ 常数与多路选择布线爆炸**：$n$ 开关含 $2^n$ 组 $N \times N$ 矩阵（计入二极管断续亚模态更多），无 BRAM 页表寻址而用扁平 LUT 硬编码加高扇入 MUX 树选通，会迅速引发布线拥塞击穿 $180\text{ MHz}$ 时序。
   - **空间全展开耗尽 DSP 硬核与 9 拍实时窗口锁死**：全展开每步需 $O(N^2)$ 个并行乘法器，在仅 220 个 `DSP48E1` 的 Zynq-7020 上，稠密耦合状态一旦超过 15 阶即耗尽全片 DSP；若改用 BRAM + 分时复用 MAC，在 $180\text{ MHz}$ 下整个 $50\text{ ns}$ 步长总共仅有 **9 个时钟周期**（扣去 4 拍 DSP 流水潜伏期仅余 5 拍），根本无法容纳串行矩阵迭代。
   - **MNA 硬件求逆缺失**：稀疏 $Y$ 离线求逆后退化为稠密 $Y^{-1}$，扁平展开同样触发 $O(N^2)$ 算子爆炸，而在线稀疏消去回代缺乏对应的存储调度硬件模板。
   - **耦合反馈下 AST 回溯失灵**：上千行扁平乘加树中多状态每拍互馈，单点移位错误瞬间污染全局波形，标量 RMSE 丧失节点级定位分辨力。

4. **与商业工具（MATLAB HDL Coder / Simscape HDL / Vitis HLS）的真实对比缺口**：
   - **零同平台定量对比**：实验仅与离线浮点 `PLECS` 比精度（物理页 5 Table III）[pdf:E12]，完全缺失 `HDL Coder`、`Simscape HDL Workflow Advisor` 或 `Vitis HLS` 在同颗 Zynq-7020 上的 LUT/DSP/延迟/工时对照。
   - **混淆了商业物理综合能力边界**：`Simscape HDL Workflow Advisor` 本身支持从物理拓扑自动提取分段状态空间/伴随矩阵并生成支持 BRAM 资源共享的可综合 HDL；且本文第 IV 节承认自然语言易推错 MNA、后续仍需退回解析 SPICE 网表（物理页 6 Section IV）[pdf:E16]，届时前端输入层级与 Simscape 物理网络并无本质落差。
   - **回避了确定性 HLS 编译强基线**：前端 `Physics Agent` 已生成无循环标量定点 C++ 代码 `model_fixed.cpp`（物理页 2 Fig. 1）[pdf:E03]，直接将其送入确定性的 `Vitis HLS`（`ap_fixed` + `PIPELINE II=1`）即可零移位错误地产出同等百级 LUT / 低延迟 RTL；用概率性 LLM 重写 Verilog 再搭波形调试器修补自造的移位/符号漏洞，缺乏相对确定性 HLS 后端的必要性消融。
   - **缺失异构字长与自主率统计**：未采用工业级逐变量异构定点位宽（电压与电流共用单一 Q 格式浪费动态位），且未披露基座模型、修复轮次与人工审查干预比例（物理页 6 Section IV）[pdf:E16]。

### 5.2 贯穿实例流水线（以二极管整流 DCM Buck 为例）

输入 $24\text{ V}$ 转负载 $10\text{ }\Omega$（$L = 100\text{ }\mu\text{H}, C = 100\text{ }\mu\text{F}, f_{\text{sw}} = 20\text{ kHz}$）参数与 $50\text{ ns}$ 步长约束（物理页 3 Section III-A）[pdf:E09]：① `Physics Agent` 构建充电、续流与 DCM 阻断三模态方程，交叉核验 `SS+FE`、`SS+BE` 与 `ADC+MNA+BE` 浮点轨迹一致后，按启动浪涌包络与位宽扫描选定 24-bit `Q7.17`，导出 `model_fixed.cpp` 与 `spec.json`（物理页 2–4）[pdf:E03][pdf:E07][pdf:E10]；② `Hardware Agent` 基于板载 $50\text{ MHz}$ 时钟经 `MMCM` 生成 $180\text{ MHz}$ `clk_solver`，由 `div_cnt[3:0]` 每 9 拍产生 $20\text{ MHz}$ 同源使能 `io_en` 免除跨时钟域同步，并用 3 个 `DSP48E1` 构造 `S1–S4` 四级流水核 `solver_core.v`（`S2` 算 48 位积、`S3` 算 48 位和、`S4` 右移并对 `iL_n` 实施零电流钳位更新 `iL_out`/`vC_out` 及 14 位 DAC 通道 `da_ch1`/`da_ch2`）（物理页 5 Fig. 10）[pdf:E13]；③ `Debugging Agent` 比对 `iverilog` VCD 与黄金模型 RMSE，经 `Pyverilog` AST 修平算术偏差后交综合环路闭合时序并下板实测（物理页 3–4 Section II-B/C & Fig. 6）[pdf:E08][pdf:E10]。

## § 6 — 核心数学推导（无形式化数学则跳过）

1. **分段线性状态空间离散递推（物理页 2 Eq. (1)）**[pdf:E05]：
   在开关模态 $M_s$ 下对连续方程 $\dot{x} = A_{M_s} x + B_{M_s} u$ 以步长 $\Delta t$ 离散：
   $$x[k + 1] = \Phi_{M_s} \cdot x[k] + \Gamma_{M_s} \cdot u[k] \tag{1}$$
   前向欧拉取 $\Phi_{M_s}^{\text{FE}} = I + \Delta t A_{M_s}$ 免求逆但受显式稳定域 $|1 + \Delta t \lambda_i| \le 1$ 限制；后向欧拉取 $\Phi_{M_s}^{\text{BE}} = (I - \Delta t A_{M_s})^{-1}, \Gamma_{M_s}^{\text{BE}} = (I - \Delta t A_{M_s})^{-1}\Delta t B_{M_s}$，具备 L-稳定阻尼特性，离线预计算全部模态矩阵查表即可消除在线求逆（物理页 2 Section II-A）[pdf:E05]。对含二极管的 DCM 续流态，若试探电流 $\tilde{i}_L[k+1] < 0$，施加非光滑投影 $i_L[k+1] = \max(0, \tilde{i}_L[k+1])$ 并切入电感开路模态，否则反灌电流会将异步 Buck 误算为稳态 $12\text{ V}$ 的同步 Buck（物理页 3 Section III-A & 物理页 5 Table III）[pdf:E09][pdf:E12]。

2. **伴随离散电路与节点电压分析（ADC+MNA，物理页 2 Eq. (2)）**[pdf:E06]：
   按后向欧拉（步长 $h = \Delta t$）将电感化为诺顿导纳 $G_L = h/L$ 并联历史电流源 $J_L = \pm i_L[k]$，电容化为 $G_C = C/h$ 并联 $J_C = -G_C v_C[k]$，按 KCL 印花得到：
   $$Y \cdot v = i \tag{2}$$
   原文对 $J_L$ 写 `±` 暴露了未显式引入有向支路-节点关联矩阵 $A$ 时支路极性与节点注入极性的符号歧义（呼应第 IV 节所述自然语言推导 MNA 易出伴随映射错误，物理页 6 Section IV）[pdf:E16]。此外，仅当采用引入虚拟开关损耗的恒导纳开关模型时 $Y$ 才在开关动作中数值不变；理想或二值电导开关仅保持稀疏图结构不变而非 $Y^{-1}$ 恒定。

3. **微步长量化下界与硬实时延迟不等式**：
   当 $\Delta t \ll RC$ 时，单步电容电压增量 $\Delta v_C = (\Delta t / C) i_C$ 极小；若 $Q_m.n$ 的 $\text{LSB} = 2^{-n}$ 逼近 $|\Delta v_C|$，右移截断将引发显著极限环偏差（物理页 4 Table I/II）[pdf:E10][pdf:E11]。硬件侧设时钟周期 $T_{\text{clk}}$、流水级数 $P$、外设建立开销 $t_{\text{io}}$，须满足 $t_{\text{calc}} = P \cdot T_{\text{clk}} \le \Delta t - t_{\text{io}}$，保证单步状态在下一帧步长使能脉冲前写回完毕（物理页 3 Section II-C 与物理页 5 Fig. 10）[pdf:E08][pdf:E13]。

## § 7 — 实验设计与结论

实验在浮点仿真与 Xilinx Zynq-7020（`xc7z020clg400-2`，含 53,200 LUTs、106,400 FFs、4.9 Mbit BRAM、220 个 `DSP48E1`，物理页 5 Section III-C）[pdf:E13] 上围绕三项问题展开：

1. **DCM 与长时标欠阻尼 CCM 下的多路线交叉精度（对照商业 `PLECS`）**：
   - **拓扑参数**：① 异步 Buck（DCM）：$V_{\text{in}} = 24\text{ V}, L = 100\text{ }\mu\text{H}, C = 100\text{ }\mu\text{F}, R_L = 10\text{ }\Omega, f_{\text{sw}} = 20\text{ kHz}, D = 0.5, \Delta t = 50\text{ ns}$，仿真 $10\text{ ms}$ 取末 $2\text{ ms}$ 评稳态（物理页 3 Section III-A）[pdf:E09]；② Boost（CCM）：$V_{\text{in}} = 100\text{ V}, L = 1\text{ mH}, C = 470\text{ }\mu\text{F}, R = 20\text{ }\Omega, f_{\text{sw}} = 20\text{ kHz}, D = 0.5$，强欠阻尼（$\zeta \approx 0.036, \tau \approx 18.8\text{ ms}$），仿真至 $60\text{ ms}$（稳态纹波 $\Delta i_L \approx 2.65\text{ A}$ p-p，物理页 4–5 Section III-B, Fig. 7 & Fig. 8）[pdf:E11][pdf:E12]。
   - **定量结果（物理页 5 Table III）**[pdf:E12]：Buck 稳态电压 `PLECS` 为 `12.92612 V`，`SS+FE`（`12.92615 V`）、`SS+BE`（`12.92609 V`）与 `ADC+MNA+BE`（`12.92609 V`）彼此偏差 `< 1 µV`，相对 `PLECS` 的 MAE 均为 `0.19 mV`（物理页 3 Fig. 3/4 与物理页 4 Fig. 5）[pdf:E09][pdf:E10]；Boost 稳态电压 `PLECS` 为 `201.9418 V`，`SS+FE`（`201.9448 V`）与 `SS+BE`（`201.9388 V`）误差为 `2.98 mV`，`ADC+MNA+BE`（`201.9386 V`）误差为 `3.15 mV`。

2. **定点 Q 格式位宽扫描消融（物理页 4 Table I & Table II）**[pdf:E10][pdf:E11]：

| 拓扑 | Q 格式（总位宽） | 稳态误差 [mV] | 指标 DSP 数 | 角色与拐点结论 |
| :--- | :---: | :---: | :---: | :--- |
| **Buck** | `Q7.25` (32b) / `Q7.21` (28b) | `0.56` / `0.56` | 2 / 2 | 超 25-bit 乘法器上限，DSP 翻倍 |
| **Buck** | **`Q7.17` (24b)** / `Q7.13` (20b) | **`4.87`** / `97.2` | **1** / 1 | **选中 `Q7.17`（`< 0.04%`）**；20b 截断恶化 20 倍 |
| **Boost** | `Q9.23` (32b) / `Q9.19` (28b) | `3.02` / `3.39` | 2 / 2 | 逼近浮点下限，但跨入双 DSP 区 |
| **Boost** | **`Q9.15` (24b)** / `Q9.13` (22b) | **`7.45`** / `40.8` | **1** / 1 | **选中 `Q9.15`**；缩 2 bit 误差陡增逾 5 倍 |

3. **Zynq-7020 资源、时序与示波器实测（物理页 1 Abstract、页 4 Fig. 6、页 5 Fig. 9/10、页 6 Table IV）**[pdf:E01][pdf:E10][pdf:E12][pdf:E13][pdf:E15]：
   - **Buck（DSP 四级流水核）**：占 `156` LUTs（`0.29%`，核占 `128` LUTs，注：Section IV 笔误写为 `129`）、`264` FFs（`0.25%`，核占 `187`）、`3` 个 `DSP48E1`（`1.4%`）、`0` BRAM；$180\text{ MHz}$ 下 4 拍延迟 `22.22 ns`（摘要记 `22.2 ns`，占 $50\text{ ns}$ 步长 `< 45%`，留 `> 27 ns` 给 I/O），时序裕量正文报 `+0.201 ns`（Table IV 表注报 `+0.01 ns`）[pdf:E13][pdf:E15][pdf:E16]。
   - **Boost（纯 LUT 浅组合核）**：占 `61` LUTs（`0.11%`）、`57` FFs（`0.05%`）、`0` DSP、`0` BRAM；单拍延迟 `5.56 ns`（摘要记 `5.6 ns`），留 `> 44 ns` 给 I/O（第 5 页正文泛写两拓扑均留 `> 44 ns` 系以偏概全笔误）[pdf:E13][pdf:E15]。两拓扑在 $20\text{ MHz}$ 更新率下的示波器实测波形均与仿真吻合（Fig. 6 & Fig. 9）[pdf:E10][pdf:E12]。

## § 8 — Take-aways

**5 句话版**
本文提出多智能体框架 `Agentic HiL`，探索从电路拓扑描述自主生成 FPGA 亚微秒硬实时电力电子仿真器。前端物理智能体通过状态空间与伴随节点三路线浮点互验及位宽扫描，生成 24-bit 定点 C 语言黄金参考以隔离建模量化与硬件编码错误。后端硬件与调试智能体围绕 $t_{\text{calc}} \ll \Delta t$ 规划最小流水深度，并利用相对黄金模型的波形 RMSE 触发 VCD-to-AST 回溯修补移位与符号扩展缺陷。在 Zynq-7020 上针对 $50\text{ ns}$ 步长的 DCM Buck 与 CCM Boost 实测表明，生成电路仅耗不足 `0.3%` LUT 并在 `22.22 ns` 内闭合毫伏级精度。但当前方案受限于零 BRAM 全展开架构与自然语言建模歧义，在多开关高阶系统上面临 $O(N^2 \cdot 2^n)$ 扩展死结，且缺少相对确定性 HLS 与 Simscape HDL 的同平台定量对标。

**3 句话版**
`Agentic HiL` 以“多离散路线互验的 24-bit 定点黄金模型”切开了连续电路数值离散与低延迟 Verilog 调试的跨层耦合。借助波形 RMSE 驱动的 AST 算术回溯与贴合 `DSP48E1` 位宽拐点的浅流水设计，系统在 Zynq-7020 上以百级 LUT 和 `22.22 ns` 延迟跑通了 $50\text{ ns}$ 步长的二阶 Buck/Boost 硬件在环仿真。然而其无存储空间全展开在多开关耦合拓扑上不可扩展，且尚未证实“LLM 写 RTL + 波形排错”优于将同一定点 C 模型直接交由确定性 HLS 编译。

**1 句话版**
`Agentic HiL` 用“软件多路线互验定标黄金模型 + 硬件波形 RMSE 引导 AST 修补扁平 RTL”走通了二阶变换器 $50\text{ ns}$ 步长 FPGA 仿真验证，但尚未跨越大规模多开关存储复用瓶颈与确定性 HLS 基线对标。

## § 9 — 最脆弱的假设

全文一旦失效代价最大的唯一核心假设是：**“在闭环状态自回归的定点电路求解器中，输出波形标量 RMSE 尖峰配合静态 AST 回溯足以唯一归因并自动修复 RTL 算术映射缺陷”**。

- **已有证据**：Section II-B 定性说明了通过电流 RMSE 尖峰回溯修复移位、符号扩展与乘法溢出（物理页 3）[pdf:E08]，并在约 200 行核代码的二阶 Buck/Boost 上取得板级实测成功（物理页 4–6）[pdf:E10][pdf:E12][pdf:E14][pdf:E15]。
- **缺失与回避的关键证据**：
  1. **高阶状态互馈引发的全网误差传染**：在 $x[k+1] = \Phi x[k] + \Gamma u[k]$ 闭环中，二阶电路仅有寥寥数个乘法节点，枚举即可定位；但升至 6–12 阶耦合变流器后，单一非对角系数移位偏差会在 2–3 拍内污染全部状态波形，标量 RMSE 处处报警，AST 回溯无法剥离源头算子与被传染节点。
  2. **非尖峰型静默缺陷漏检**：右移截断偏置或流水线分支间错 1 拍（$5.56\text{ ns}$）不会产生单拍溢出突刺，只会造成慢速稳态漂移或寄生阻尼失真，基于“突刺”的定位器对此失明。
  3. **零故障注入与收敛率统计**：全文未公布任何修复轮次、一次通过率或故障召回率，且第 IV 节承认部署前仍需人工审查 RTL（物理页 6 Section IV）[pdf:E16]。

## § 10 — 最小复现实验

可在 **1 周内（约 350 行 Python + `iverilog`/`Pyverilog` + Vivado WebPACK）** 完成如下最小证伪实验，检验（A）波形回溯在 4 阶耦合拓扑上的退化率，以及（B）相对确定性 HLS 后端的真实收益：

1. **输入拓扑**：基准组 $T_2$ 采用原文 DCM Buck 参数（$24\text{ V}, 100\text{ }\mu\text{H}, 100\text{ }\mu\text{F}, 10\text{ }\Omega, 20\text{ kHz}, \Delta t = 50\text{ ns}, \text{Q7.17}$，物理页 3–4）[pdf:E09][pdf:E10]；扩展组 $T_4$ 采用 4 阶耦合 Cuk 变换器（$L_1, L_2, C_1, C_2$ 四状态，被动二极管断续判据为耦合电流和 $i_{L_1} + i_{L_2} = 0$）。
2. **最小实现模块**：① `SymPy` 自动生成 $T_2, T_4$ 的 `SS+BE` 24-bit 定点参考 `model_fixed.cpp`；② 对照支路将 `model_fixed.cpp` 用 `ap_fixed<24,7>` 直接喂入 `Vitis HLS`（$180\text{ MHz}$, `PIPELINE II=1`）生成 RTL；③ 测试支路向 LLM 生成的扁平 `solver_core.v` 系统注入 5 类定点缺陷（右移偏 1 位、负数逻辑右移、累加前截断、钳位后判过零死锁、跨分支错 1 拍），喂入 `iverilog` 逐拍 RMSE 与 `Pyverilog` AST 限制 5 轮自动修复（每类重复 10 次）。
3. **观测指标与判据**：统计 5 轮内逐拍零额外误差修复率及 `xc7z020clg400-2` 综合后 LUT/DSP/$t_{\text{calc}}$。若 $T_4$ 或非尖峰缺陷修复率跌破 $40\%$，而确定性 `Vitis HLS` 从同一 `model_fixed.cpp` 零调试生成的 RTL 延迟同样 $\le 25\text{ ns}$ 且 DSP 相当，则证伪后端 LLM 直写扁平算术 RTL 的工程优越性。

## § 11 — 最强反例设计

### 11.1 物理病态反例：含励磁支路阶数退化与多时间尺度刚性的串联谐振 LLC 变换器

取作者在 Section IV 拟扩展的 **LLC 谐振变换器**（物理页 6）[pdf:E16]：$V_{\text{in}} = 400\text{ V}$，$f_{\text{sw}} = 200\text{ kHz}$（含 $150\text{ ns}$ 死区），原边 4 开关 + 副边 4 二极管，$L_r = 25\text{ }\mu\text{H}, C_r = 100\text{ nF}, L_m = 125\text{ }\mu\text{H}$，输出大电容 $C_o = 470\text{ }\mu\text{F}$，$\Delta t = 50\text{ ns}$。该方法将遭遇三重可预测崩溃：
1. **动态降阶与伴随伪阻尼**：副边整流桥断续关断时，$L_r$ 与 $L_m$ 强行串联产生代数约束 $i_{L_r} \equiv i_{L_m}$，独立状态从 4 阶退化为 3 阶，朴素 4 阶矩阵求逆奇异；若加虚拟大电阻或用恒导纳 ADC 开关，又会在 $200\text{ kHz}$ 谐振腔引入严重寄生阻尼，抹平死区零电压开通（ZVS）相位。
2. **24-bit 单一全局 Q 格式的“防饱和—下溢停滞”死锁**：谐振电容峰值超 $600\text{ V}$ 迫使全局格式至少取 `Q11.13`（$\pm 1024\text{ V}$，$\text{LSB} \approx 0.122\text{ mV}$）；此时输出大电容 $C_o$ 在 $1\text{ A}$ 电流下的 $50\text{ ns}$ 单步增量仅 $\Delta v_{C_o} \approx 0.106\text{ mV} < 1\text{ LSB}$，每步更新被定点截断清零而发生**静默量化停滞**；若扩至 36-bit 以上，单乘法器裂变为 4 个级联 `DSP48E1`，直接击穿 9 拍实时窗口。
3. **8 开关混杂模态爆炸与自然语言变压器极性盲区**：原副边 8 开关含十余种有效换流/断续亚模态，无 BRAM 硬编码系数网络引发布线拥塞；且自然语言描述理想变压器同名端与隔离地极易令 LLM 推错耦合符号（物理页 6 Section IV）[pdf:E16]。

### 11.2 审稿人替代解释

Zynq-7020 上 `156` / `61` LUTs 与 `22.22 ns` / `5.56 ns` 的极佳数字，本质源于二阶开环拓扑离散后仅剩 4–6 次常系数标量乘加（其中近 1 或 2 幂次系数被综合器常量折叠），而非多智能体具备特殊架构优化能力；一旦 `Physics Agent` 算出 `model_fixed.cpp`，30 行确定性代码模板即可零差错生成同等硬件，后端波形调试很大程度上只是在弥补“用概率性 LLM 充当确定性算术编译器”自造的移位漏洞。

## § 12 — Follow-up Research Bet

### 主研究押注：面向多时间尺度开关网络的“异构增量算子状态表示 + 片上 BRAM 消去树时分协处理器”联合编译

针对本文暴露的“微步长下绝对状态表示吞噬小数有效位”（物理页 4 Table I/II）[pdf:E10][pdf:E11] 与“片上 `4.9 Mbit` BRAM 零利用却受困于多开关常数硬编码”（物理页 5–6 Section III-C & Table IV）[pdf:E13][pdf:E15] 两大反常，提出同时改变**状态表示、系统编译边界与时间尺度结构**三项基本变量的主押注：
- **改变状态表示与量化变量**：废除统一字长的绝对状态覆盖递推，改为**逐支路异构量纲归一化的增量算子（$\delta$-form）双字长表示**——用 24×18-bit 乘法器专算满量程单步导数增量 $\Delta x[k]$，而将绝对状态驻留在 `DSP48E1` 原生 48-bit `P` 累加寄存器内跨步无损累加（仅截取高 24-bit 回送乘法输入），零额外 DSP 开销即可将慢电容等效积分尾数精度推升至 35 bit 以上，根治微步长量化停滞。
- **改变智能体系统边界与硬件微架构**：将 LLM 严格限制在前端“SPICE/拓扑规范 $\to$ 带方向关联矩阵的分块伴随网表与被动开关互补图”编译；后端改用确定性的**双端口 BRAM 模态系数页表 + 固定流水深度分块乘加阵列编译器**，按开关导通编码与二极管电流符号在 1 拍内从闲置 BRAM 寻址读出活动行系数，将多开关逻辑复杂度从指数级硬编码降为常数级数据通路加线性存储深度。
- **改变时间尺度耦合速率**：在 $50\text{ ns}$ 基础节拍上实施双速率解耦——高频电感/谐振腔子网每拍全速更新，大容量直流母线电容节点每 $K$ 拍做一次聚合电荷更新并在中间拍以恒压诺顿源注入，把稀缺的单步时钟节拍集中供给多开关换流子网。

### Wild-card 备选方向（一句话不同机制）

彻底抛弃在线数值积分与矩阵乘加通路，离线利用分段仿射（PWA）显式映射将含非线性结电容/磁饱和的变换器单步状态推进预编译为驻留在片上大容量闲置 BRAM 中的多分辨率超立方体查找表加单级硬件线性插值器，将任意刚性电路的单步延迟恒定锁死在 2 个时钟周期。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title / Authors / Abstract — Agentic HiL 问题定义、三大机制与 Buck/Boost 总体硬件指标"
[pdf:E02]: <_evidence/E02-p001-page.png> "PDF 物理页 1，Section I — 宽禁带亚微秒 HiL 步长约束、VerilogCoder 局限与 MATLAB HDL Coder / Simscape HDL 对比"
[pdf:E03]: <_evidence/E03-p002-page.png> "PDF 物理页 2，Section I-3 & Section II / Fig. 1 — Agentic HiL 双智能体技能框图、spec.json / model_fixed.cpp 接口与 iverilog/yosys/Pyverilog 工具链"
[pdf:E04]: <_evidence/E04-p002-page.png> "PDF 物理页 2，Section II / Fig. 2 — 传统手动 HiL 流程与 Agentic HiL 自动化闭环（model.py -> model_fixed.cpp -> solver_core.v -> VCD Tracer）对比"
[pdf:E05]: <_evidence/E05-p002-page.png> "PDF 物理页 2，Section II-A / Eq. (1) — 状态空间（State-Space）前向/后向欧拉离散递推与 2^n 开关模态离线预计算查找表"
[pdf:E06]: <_evidence/E06-p002-page.png> "PDF 物理页 2，Section II-A / Eq. (2) — ADC+MNA 诺顿伴随等效支路（GL, JL, GC, JC）与恒定结构节点导纳矩阵 Y"
[pdf:E07]: <_evidence/E07-p003-page.png> "PDF 物理页 3，Section II-A — 静态变量范围分析、定点 Q 格式选择、C 语言 Golden Reference 与三路线（SS+FE/SS+BE/ADC+MNA+BE）交叉验证"
[pdf:E08]: <_evidence/E08-p003-page.png> "PDF 物理页 3，Section II-B & II-C — 波形驱动硬件调试智能体（VCD 到 AST 反向回溯）与超低延迟导向硬件架构综合闭环"
[pdf:E09]: <_evidence/E09-p003-page.png> "PDF 物理页 3，Section III-A / Fig. 3 & Fig. 4 — 二极管整流 Buck 变换器（DCM）实验参数、零电流钳位稳态波形与相对 PLECS 绝对误差收敛曲线"
[pdf:E10]: <_evidence/E10-p004-page.png> "PDF 物理页 4，Section III-A / Fig. 5, Table I & Fig. 6 — Buck 启动暂态波形、Q7.13–Q7.25 定点位宽扫描表与 Zynq-7020 示波器实测波形"
[pdf:E11]: <_evidence/E11-p004-page.png> "PDF 物理页 4，Section III-B / Fig. 7 & Table II — Boost 变换器（CCM 欠阻尼谐振）参数、启动暂态波形与 Q9.13–Q9.23 定点位宽扫描表"
[pdf:E12]: <_evidence/E12-p005-page.png> "PDF 物理页 5，Section III-B / Fig. 8, Fig. 9 & Table III — Boost 60 ms 稳态纹波、示波器实测波形与全方法相对 PLECS 稳态误差对照表"
[pdf:E13]: <_evidence/E13-p005-page.png> "PDF 物理页 5，Section III-C / Fig. 10 — 180 MHz / 20 MHz 同源使能架构、DSP48E1 四级流水线（22.22 ns）与 GTKWave 内部寄存器波形"
[pdf:E14]: <_evidence/E14-p005-page.png> "PDF 物理页 5，Section III-C — 生成 RTL 代码行数构成（约 200 行求解器核 + 200 行板级封装）及与手工编码、MATLAB HDL Coder 定性对比"
[pdf:E15]: <_evidence/E15-p006-page.png> "PDF 物理页 6，Section III-C / Table IV — XC7Z020 硬件资源占用表（Buck 与 Boost 的 LUT/FF/DSP48E1 占比）与时序裕量汇总"
[pdf:E16]: <_evidence/E16-p006-page.png> "PDF 物理页 6，Section IV — 结论、三大局限（限于二状态拓扑、RTL 需人工审查、自然语言推导 MNA 易错）与单芯片 RCP+HiL 共部署展望"
