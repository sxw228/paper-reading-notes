# Detailed Multi-Domain Modeling and Faster-Than-Real-Time Hardware Emulation of Small Modular Reactor for EMT Studies

作者：Weiran Chen；Venkata Dinavahi；Ning Lin  
出处：IEEE Transactions on Energy Conversion，Vol. 39，No. 3，pp. 1644–1657  
年份：2024  
DOI：10.1109/TEC.2024.3375256  
Zotero key：TU5BENUB  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“能否建立一个 SMR 模型”，而是更苛刻的问题：怎样把小型模块化反应堆（small modular reactor, SMR）的核、热、机械、电气和控制动态与电力系统的 electromagnetic transient（EMT）模型放在同一次仿真中，同时让求解在 FPGA 上跑得比被模拟的物理过程更快。困难集中在点堆中子动力学：六组缓发中子加一组瞬发中子形成强刚性非线性常微分方程；“刚性”表示同一系统内快、慢时间尺度相差很大，显式积分会被最快模态的稳定性要求迫使使用极小步长，而隐式积分又需要迭代，计算延迟不利于实时执行。[pdf:E02]（PDF 物理页 2，Introduction 与 Section II-A）

作者面向的是一台 150 MWth/45 MWe 的 iPWR 型 SMR。其系统级核心模型包含点堆动力学、反应堆热工水力、蒸汽发生器、控制棒和汽轮机调速器，排除稳压器、上腔室等辅助设备后仍为 25 阶 ODE；论文希望把其中最刚性的七阶部分改造成可直接更新的半解析关系，使总动态模型降为 18 阶，再与同步机（SM）、模块化多电平变换器（MMC）、两区 12 kV MVDC 舰船配电网和负载共同部署到一块 Xilinx VCU118 上。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E02]（PDF 物理页 2，Introduction 与 Section II）

这一目标有两重工程价值。第一，核电机组的在线验证通常不可行，hardware-in-the-loop（HIL，真实 I/O 环境下由实时模型参与闭环测试）是安全控制和系统联调的重要替代手段；第二，热传导、氙/钐中毒等过程可持续数分钟乃至数十小时，仅仅“实时”仍可能太慢，faster-than-real-time（FTRT）可以压缩调试、场景遍历和故障预测的墙钟时间。[pdf:E02]（PDF 物理页 2，Introduction）论文最终报告：一个仿真步长代表 10 μs 物理时间，而 FPGA 每约 800 ns 完成一次数据更新，因此 30 s 仿真只需约 2.4 s，得到约 12.5 倍 FTRT；这里的 800 ns 是墙钟计算间隔，不是 EMT 模型的物理时间步长。[pdf:E12]（PDF 物理页 12，Fig. 16(h) 后正文）[pdf:E13]（PDF 物理页 13，Conclusion）

## § 2 — 前人工作与不足

论文给出的既有建模路线已经相当成熟：PWR 的系统级模型通常把六组缓发中子和瞬发中子写成七阶点堆模型，用 Mann 三节点模型表示燃料和两段冷却剂，再以热腿、下降段、三节点蒸汽发生器、控制棒回路和汽轮机调速器补齐热—机—控动态。完整 PWR 文献中出现过 55 阶模型，而作者选取的核心组合为 25 阶；问题不在于这些子模型不存在，而在于它们与高频电气 EMT 联算后，计算依赖和刚性同时暴露。[pdf:E01]（PDF 物理页 1，Introduction）

对点堆方程，已有解析解通常要求忽略反馈或预先给定反应性 \(\rho(t)\)；已有数值方法虽然能够避免传统 Euler/Runge–Kutta 被绝对稳定区间直接限制，但隐式算法的迭代次数会拉长每一步执行时间。作者还指出，当时 SMR HIL 工作多部署于 CPU 平台，受到顺序执行和存储体系限制；即使 CPU 做到实时，也不能自动解决持续数分钟到数十小时的场景耗时。[pdf:E02]（PDF 物理页 2，Introduction）

因此，论文针对的是三个彼此耦合的不足：数值层面要在强刚性区间保持收敛，调度层面要把长依赖链改造成可流水的任务图，平台层面要在一个完整多域算例而非孤立反应堆方程上证明实际 FTRT。需要注意的是，作者没有与 CPU/GPU 端到端实现或商业实时仿真器做同模型墙钟对比，也没有用真实反应堆测量数据验证模型；论文的比较基线主要是 ode15s、RK4、基于 Jacobi 迭代的 Hammer–Hollingsworth implicit Runge–Kutta（IRK）以及 Simulink 离线结果。[pdf:E05]（PDF 物理页 5，Table I 与相邻正文）[pdf:E09]（PDF 物理页 9，Fig. 10–11 与相邻正文）

## § 3 — 重建作者的思考路径

以下是基于原文背景的合理重建，不是作者逐句陈述的研究日志。

第一步，从物理模型出发，会发现 25 阶本身并非 FPGA 的唯一障碍；真正控制显式步长的是点堆 Jacobian 的最负特征值。六组缓发中子衰变常数跨越多个量级，而瞬发中子寿命只有 \(\Lambda=2\times10^{-5}\,\mathrm{s}\)，所以快模态决定稳定步长，慢模态决定有意义的响应，直接用统一显式步长会浪费大量运算。[pdf:E03]（PDF 物理页 3，Eq. (5)–(8) 与 stiffness analysis）

第二步，研究者会注意到缓发中子方程对 \(C_i\) 是线性的；若把一个步长内的瞬发中子密度 \(n(\tau)\) 用末端一阶 Taylor 多项式表示，\(C_i\) 可以精确积分成指数项，而不必把六个缓发中子状态继续交给通用 ODE 迭代器。这样，最刚性的七阶子系统就可能被重写为“前一步状态 \(\rightarrow\) 本步闭式更新”，把通用 25 阶 ODE 缩为其余 18 阶状态方程。[pdf:E04]（PDF 物理页 4，Eq. (14)–(19)）

第三步，闭式公式仍会因为温度反馈、控制棒反应性和其余 18 阶状态相互依赖而形成组合长路径。若允许反应性 \(\rho\) 和中子密度 \(n\) 各引入一个 unit delay（一个仿真步长的离散延迟），就能把依赖环切开；接着依据各公式的真实依赖关系并行计算 \(G_1,G_2,\rho_{\mathrm{ext}}\) 等无关任务，并把不同迭代流水重叠。[pdf:E04]（PDF 物理页 4，Fig. 3 及 unit-delay 说明）[pdf:E08]（PDF 物理页 8，Section IV-A）

最后，把反应堆输出机械功率接到同步机，再以电流源、臂级平均 MMC、受控 \(V\!-\!I\) 源和两端口 RL 网络把电源、网络和负载解耦，便得到适合 HLS 的模块边界。这个路径的核心不是“FPGA 比 CPU 快”的泛化，而是先改变数学依赖，再让 FPGA 的并行和流水有结构可用。[pdf:E06]（PDF 物理页 6，Eq. (20)–(23) 与 Section III）[pdf:E08]（PDF 物理页 8，Section IV-A）

## § 4 — 核心 Intuition

把导致刚性的六个缓发中子状态从通用逐步积分中拿出来，用指数解析积分和末端一阶 Taylor 近似直接消元，就能在保留反馈接口的同时把 SMR 动态模型从 25 阶降到 18 阶。[pdf:E04]（PDF 物理页 4，Eq. (14)–(19)）再用两个 unit delay 切断反应性—中子密度—热工状态的组合依赖环，FPGA 才能把独立公式并行、把相邻仿真步流水重叠。[pdf:E08]（PDF 物理页 8，Section IV-A）真正让 FTRT 成立的是“半解析降阶 + 依赖图重排 + 硬件流水”三者同时成立，而不是单独提高时钟频率。[pdf:E09]（PDF 物理页 9，Fig. 10 与硬件实现）

## § 5 — 具体方法与完整 Pipeline

以“舰船从全速前进转入 crash stop”为例，输入、处理和输出链如下。

1. **核动力输入与状态。** 点堆模型接收总反应性 \(\rho(t)\)，它由控制棒反应性、燃料温度和两段冷却剂温度反馈共同构成；六组 \(C_i\) 描述缓发中子先驱核，\(n\) 描述平均瞬发中子密度。论文给定 \(\Lambda=2\times10^{-5}\,\mathrm{s}\)、六组 \(\beta_i\) 与 \(\lambda_i\)，并用这些参数分析刚性。[pdf:E03]（PDF 物理页 3，Eq. (5)–(13)）

2. **半解析点堆更新。** 在 \([t_n,t_{n+1}]\) 内，以 \(t_{n+1}\) 处的一阶 Taylor 式近似 \(n(\tau)\)，对每个 \(C_i\) 的线性方程做指数积分，得到 \(G_{1,i}\)、\(G_{2,i}\) 及 \(C_{i,n+1}\) 的闭式表达；再把它们代回中子平衡式，直接求 \(n'_{n+1}\) 和 \(n_{n+1}\)。\(\rho(t)\) 使用一步延迟，使本步的 \(n\) 可由已知量直接计算，随后再更新其他 18 个 ODE 状态。[pdf:E04]（PDF 物理页 4，Eq. (14)–(19) 与 Fig. 3）

3. **18 阶 SMR 主体。** 状态向量包含燃料、冷却剂、热腿、入口、蒸汽发生器一次/金属/蒸汽温度，蒸汽压力，三级汽轮机状态，以及平均温度控制、调速和控制棒回路状态；输入为 \(n,w,w_{\mathrm{ref}},P_{\mathrm{ref}}\)。稀疏矩阵 \(A,B\) 用 coordinate format（COO，只存非零元素的位置和值）表达，SMR 输出机械功率 \(P_m=tb_1+tb_2\) 驱动同步机。[pdf:E06]（PDF 物理页 6，Table II–III 与 Eq. (20)–(23)）

4. **电气域接口。** 同步机采用基于转子 \(dq\) 坐标系的受控电流源九阶模型，其中七阶电磁部分用 trapezoidal method 离散，二阶机械部分通过 \(P_m,w\) 与 SMR 往返耦合。MMC 使用 arm-level averaged（ALA，臂级平均）模型，把开关周期内的子模块臂近似成耦合受控 \(V\!-\!I\) 源，并在 \(\Sigma/\Delta-\alpha\beta0\) 坐标下形成 13 阶状态空间；两区 MVDC 网络用 RL 两端口与受控源解耦，推进电机模块采用平均值 DC–AC inverter 和 SVPWM。[pdf:E07]（PDF 物理页 7，Fig. 6–8 与 Eq. (24)–(25)）[pdf:E08]（PDF 物理页 8，Fig. 9 与 Eq. (26)）

5. **时间推进与依赖重排。** 点堆部分使用半解析一阶更新，Eq. (20) 的 18 阶状态使用 trapezoidal integration；Eq. (23)、Eq. (16)、Eq. (17) 和 Eq. (13) 的 \(F_2\) 可并行，其余六个有真实数据依赖的计算按序执行。作者再对 \(n(t)\) 增加一步延迟，把 Eq. (20) 从最长路径拆下，使下一仿真步不必等待当前步全部输出完成；SMR solver 每 92 个 clock cycle 更新一次。[pdf:E08]（PDF 物理页 8，Section IV-A–B）[pdf:E09]（PDF 物理页 9，Fig. 10）

6. **FPGA 映射与输出。** 各模块先以 C 在 Vitis HLS 中综合成 IP，再在 Vivado 中部署到 Virtex UltraScale+ VCU118（xcvu9p-flga2104-2L-e）。内部计算采用 IEEE 32-bit single-precision floating point，板上运行时钟 300 MHz；完整系统最长路径为 231 cycle，经一个接收缓冲周期后约每 800 ns 更新。板上数值转成 16-bit signed hexadecimal，经 FMC-DAC34H8 输出到示波器。[pdf:E08]（PDF 物理页 8，Table IV 与 Section IV）[pdf:E09]（PDF 物理页 9，Fig. 11 与硬件实现）

7. **场景输出。** 电机在 0–5 s 停止、5–15 s 加速至 1800 rpm、15–30 s crash stop；模型输出反应性、中子功率、热工状态、汽轮机/同步机功率、MMC 直流电压与电机波形。3,000,000 个 10 μs 仿真步在约 2.4 s 墙钟时间完成，从而得到 12.5 倍 FTRT。[pdf:E11]（PDF 物理页 11，Fig. 14–15 后测试场景正文）[pdf:E12]（PDF 物理页 12，Fig. 16 与相邻正文）

论文**未报告**：显式的零交叉/事件定位算法；统一的多速率调度器或各子域独立步长；开关级 MMC 在全部实验中的逐器件求解方式；BRAM/URAM、功耗、温度、timing slack 和不同 FPGA 器件上的可移植结果；ADC 输入、外部真实控制器或其他 device-under-test 的闭环 HIL 延迟。论文展示的是单块 VCU118 上的模型、DAC 和示波器输出，不能据此认定已经完成真实反应堆控制器的闭环 HIL。

## § 6 — 核心数学推导（无形式化数学则跳过）

点堆模型的起点是

\[
\frac{dn}{dt}=\frac{\rho-\beta}{\Lambda}n+\sum_{i=1}^{6}\lambda_i C_i,\qquad
\frac{dC_i}{dt}=\frac{\beta_i}{\Lambda}n-\lambda_i C_i .
\]

其中 \(n\) 是平均瞬发中子密度，\(C_i\) 是第 \(i\) 组缓发中子密度，\(\rho\) 是堆芯反应性，\(\Lambda\) 是瞬发中子寿命，\(\beta_i\) 是各组缓发中子份额且 \(\beta=\sum_i\beta_i\)，\(\lambda_i\) 是衰变常数。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2)）

若暂把 \(\rho(t)\) 视为常数 \(\rho_0\)，Laplace 逆变换给出 \(n(t)=\sum_{j=1}^{m+1}A_j e^{\omega_jt}\)，特征根满足

\[
\rho_0=\Lambda\omega+\sum_i\frac{\beta_i\omega}{\omega+\lambda_i}.
\]

六组参数使特征根跨越多个量级；显式 Euler 的稳定步长受 \(h<2/\max_i|\omega_i|\) 约束，所以最快三模态决定步长，而感兴趣的慢响应并未因此变快。这就是作者不直接在 FPGA 上堆叠 RK4 流水的原因。[pdf:E03]（PDF 物理页 3，Eq. (4)–(8) 与 stiffness analysis）

作者在一个步长内采用末端一阶展开

\[
n(\tau)\approx n_{n+1}+n'_{n+1}(\tau-t_{n+1}),
\]

并把反应性积分写成

\[
F_1=\frac{h[\rho_{n+1}+\rho_n]}{2\Lambda},\qquad
F_2=-\frac{h^2\rho_n}{2\Lambda}.
\]

对缓发中子方程使用 integrating factor，可得到

\[
\begin{aligned}
C_{i,n+1}&=e^{-\lambda_i h}C_{i,n}
+\frac{\beta_i}{\Lambda}\left(G_{1,i}n_{n+1}+G_{2,i}n'_{n+1}\right),\\
G_{1,i}&=e^{-\lambda_i h}\frac{e^{\lambda_i h}-1}{\lambda_i},\\
G_{2,i}&=e^{-\lambda_i h}\frac{1-e^{\lambda_i h}+\lambda_i h}{\lambda_i^2}.
\end{aligned}
\]

这一步的物理直觉是：缓发中子先驱核的自然衰减 \(e^{-\lambda_i h}\) 被解析保留，只把步内 \(n(\tau)\) 的变化近似到一阶，因而不会像显式 RK4 那样直接受最快衰减常数控制。[pdf:E04]（PDF 物理页 4，Eq. (14)–(17)）

令

\[
D=1-\sum_i\frac{\lambda_i\beta_i}{\Lambda}G_{2,i},\quad
Q=\sum_i\lambda_i e^{-\lambda_i h}C_{i,n},\quad
A=\frac{\rho_{n+1}-\beta}{\Lambda}+
\sum_i\frac{\lambda_i\beta_i}{\Lambda}G_{1,i},
\]

则 Eq. (18) 可读成

\[
n'_{n+1}=\frac{A n_{n+1}+Q}{D}.
\]

把它和 \(C_{i,n+1}\) 代回步长积分式，Eq. (19) 便是只含已知旧状态、\(\rho_n,\rho_{n+1}\) 和待求 \(n_{n+1}\) 的线性分式，因而可直接解出 \(n_{n+1}\)，再回代更新 \(n'_{n+1}\) 与全部 \(C_{i,n+1}\)。这完成了七阶点堆 ODE 的代数化更新，使剩余 SMR 状态空间为 18 阶。[pdf:E04]（PDF 物理页 4，Eq. (18)–(19)）

近似代价有两层。第一，一阶 Taylor 的 local truncation error（LTE，单步局部截断误差）为 \(n^{(2)}(t_{n+1})h^2/2\)，在 prompt-critical 区间可能不如高阶 RK；第二，为了让 \(\rho_{n+1}\) 和其余状态成为已知量，作者使用 \(\rho=z^{-1}\!\ast\rho\) 的 unit delay，硬件调度又对 \(n\) 增加一步延迟。论文以 \(h=0.1\,\mathrm{s}\) 相对一分钟热工瞬态约小 600 倍、以及 10 μs 采样相对约 1 ms 中子瞬态小 100 倍为理由，认为这些延迟可忽略；这是方法的适用条件，不是无条件定理。[pdf:E04]（PDF 物理页 4，unit-delay 与 LTE 讨论）[pdf:E08]（PDF 物理页 8，Section IV-A）

## § 7 — 实验设计与结论

**问题 1：半解析 solver 在强刚性区间是否比显式/隐式基线更适合实时计算？**  
实验：用 \(\rho=0.003,-0.007,0.007\) 三个 step input，在 \(h=0.1\) 下比较 RK4、IRK、proposed method，并以变步长 \(h\le10\,\mu\mathrm{s}\) 的 ode15s 为参考；再由 Vitis HLS 比较 cycle 和 DSP/FF/LUT。答案：在前两个刚性工况，RK4 不收敛；IRK 的平均相对误差分别为 4.4471% 和 4.2807%，proposed method 为 0.0186% 和 0.0047%。在 \(\rho=0.007\) 工况，proposed method 误差为 0.6452%，弱于 RK4 的 0.0170% 和 IRK 的 0.0163%，但把步长降到 0.01 后降至 0.0221%。综合延迟为 RK4 488 cycle、IRK 841–14,120 cycle、proposed method 80 cycle；在该 HLS 比较采用的 10 ns/cycle 口径下，对应约 5 μs、8.4–141.2 μs 和 0.8 μs。[pdf:E05]（PDF 物理页 5，Table I 与相邻正文）这支持“刚性 delayed-critical 区间的速度—精度折中更好”，不支持“所有反应性区间都比高阶方法更精确”。另需注意，Table I 把 \(\rho=0.007\) 标成 \(>\beta\)，而 Section II-A 所列六个 \(\beta_i\) 四舍五入后之和正好为 0.007；第三工况与 prompt-critical 边界的严格关系无法仅凭表中舍入值确定。[pdf:E03]（PDF 物理页 3，参数列表）[pdf:E05]（PDF 物理页 5，Table I）

**问题 2：多域模块综合到 FPGA 后是否保持离线模型数值行为，并装得进单板？**  
实验：以 Simulink 离线输出作为 HLS testbench 输入，比较 SMR、SM-MMC、RLC-PMM 三个模块；Table IV 同时报告 latency 和资源。答案：三模块 TB error 分别为 2.8‱、3.5‱、1.1‱，即 0.028%、0.035%、0.011%；SMR、SM-MMC、RLC-PMM latency 分别为 92、162、126 cycle，完整依赖图最长路径为 231 cycle。合计使用 486 DSP、58,932 FF、64,259 LUT；相对 VCU118 全板资源约为 7.1%、2.5%、5.4%。[pdf:E08]（PDF 物理页 8，Table IV）[pdf:E09]（PDF 物理页 9，Section IV-B–C）这是对“离线模型到 HLS 实现”的一致性证据，但 TB error 的数学定义、每个通道的最坏误差和 timing closure slack 未报告。

**问题 3：为什么需要 FTRT，而不是普通实时？**  
实验：离线模拟 reactor scram。控制棒按 80 steps/min 插入、2 s 完成；在 \(t=25\,\mathrm{s}\) 触发 trip，堆芯总反应性降到约 \(-10{,}719\) pcm，中子密度和机械功率衰减，热工状态约 200 s 才稳定。答案：即使单步实时，长热工过程仍令调试耗时，FTRT 可以直接压缩这种墙钟等待。[pdf:E10]（PDF 物理页 10，Fig. 12 与相邻正文）

**问题 4：把 EMT 与 SMR 热工动力学联算会不会揭示单域模型看不到的风险？**  
实验：50 MVA、6.6 kV、60 Hz 同步机接无限大母线，在 \(t=1\,\mathrm{s}\) 施加三相短路，0.1 s 后清除；比较 SMR、恒定端口和带保护 SMR 三种情形。答案：作者观察到 SMR 对毫秒级 EMT 波形影响较小，但 EMT 引起频率/电压扰动后，SMR 的低压/低频补偿动作推动蒸汽压力一度超过 1.1 p.u.，并在 3 s 内诱发控制棒速度信号振荡。这一结果说明耦合方向是非对称的：慢反应堆未必改变首个 EMT 尖峰，快速电网故障却可能通过控制器和热工状态放大为后续安全问题。[pdf:E10]（PDF 物理页 10，Fig. 13 与故障说明）[pdf:E11]（PDF 物理页 11，Fig. 14–15）

**问题 5：完整硬件模型能否在真实板卡上达到 12.5 倍 FTRT？**  
实验：对 30 s、\(h=10\,\mu\mathrm{s}\) 的全速前进/crash-stop 舰船工况做 3,000,000 次迭代，并用示波器采集 SMR、SM、MMC、网络和 PMSM 波形。答案：每步约 800 ns，完整周期约 2.4 s，因而是 \(10\,\mu\mathrm{s}/0.8\,\mu\mathrm{s}=12.5\) 倍 FTRT；电机在约 18–20 s 进入第二象限并回馈能量，平均与开关 MMC 臂电压波形对齐，直流母线约在 12 kV 到 10.5 kV 间波动。[pdf:E12]（PDF 物理页 12，Fig. 16 与相邻正文）结论页再次明确 30 s、10 μs、800 ns、2.4 s 和 12.5 倍之间的关系。[pdf:E13]（PDF 物理页 13，Conclusion）该实验没有报告重复次数、跨板卡方差、功耗或物理设备闭环，因此证明的是这次 FPGA emulation 的执行速度，不是任意 SMR HIL 系统的普遍加速比。

## § 8 — Take-aways

**5 句话：**  
1. 论文把强刚性的七阶点堆中子动力学改写为指数积分与一阶 Taylor 近似结合的半解析更新，使 SMR 主状态模型从 25 阶降到 18 阶。[pdf:E04]（PDF 物理页 4，Eq. (14)–(19)）  
2. 在两个刚性 step-reactivity 测试中，RK4 不收敛，而 proposed method 的平均相对误差为 0.0186% 和 0.0047%，明显低于 IRK 的 4.4471% 和 4.2807%。[pdf:E05]（PDF 物理页 5，Table I）  
3. 作者用 unit delay、task-level parallelism 和 pipeline 重排公式依赖，使完整系统最长路径为 231 cycle，并在 VCU118 上约每 800 ns 更新一次。[pdf:E08]（PDF 物理页 8，Table IV）[pdf:E09]（PDF 物理页 9，Fig. 10–11）  
4. 30 s、10 μs 步长的舰船工况需要三百万步，却在约 2.4 s 墙钟时间内完成，即约 12.5 倍 FTRT。[pdf:E12]（PDF 物理页 12，Fig. 16(h) 与相邻正文）  
5. 最重要的边界是：精度和流水都依赖“被插入的一步延迟远短于核热工瞬态”这一尺度分离，论文只在有限反应性和场景下验证了它。[pdf:E04]（PDF 物理页 4，unit-delay 讨论）[pdf:E08]（PDF 物理页 8，Section IV-A）

**3 句话：**  
1. 核心贡献是先在数学上消除刚性缓发中子状态的通用迭代，再在硬件上消除不必要的数据依赖。[pdf:E04]（PDF 物理页 4，Eq. (14)–(19)）[pdf:E09]（PDF 物理页 9，Fig. 10）  
2. 结果证明一套含 SMR、同步机、MMC、MVDC 网络和电机负载的单 FPGA 模型可以用 32-bit floating point 以约 12.5 倍 FTRT 运行。[pdf:E09]（PDF 物理页 9，硬件实现）[pdf:E13]（PDF 物理页 13，Conclusion）  
3. 它尚未证明快速反应性变化、保护边界、真实控制器闭环和其他硬件平台上仍能保持同样的精度、稳定性与加速比。

**1 句话：**  
这是一项把刚性 ODE 的结构性改写真正落到 FPGA 多域 EMT emulator 上的工程工作，其价值很高，但“延迟可忽略”的适用边界仍需要比当前几个工况更严格的证伪式验证。

## § 9 — 最脆弱的假设

最脆弱的假设是：为了闭式求解和流水拆环而加入的 \(\rho\) 与 \(n\) 的 unit delay，相对被模拟动力学足够短，所以不会改变关键状态、稳定性或保护判断。这个假设一旦失败，半解析公式仍可能快速执行，却会快速地产生相位滞后或错误的阈值穿越；那么“多域 EMT 可用于 SMR 安全研究”的核心工程价值会比单纯误差上升更严重地受损。

论文给了三类支持证据：\(h=0.1\,\mathrm{s}\) 相对一分钟热工瞬态约小 600 倍；硬件场景的 10 μs step 相对作者引用的约 1 ms 中子瞬态小 100 倍；HLS 与 Simulink 的三模块 testbench error 处于 1.1‱–3.5‱，即 0.011%–0.035%。[pdf:E04]（PDF 物理页 4，unit-delay 说明）[pdf:E08]（PDF 物理页 8，Section IV-A 与 Table IV）这些证据仍不闭合“所有相关瞬态都慢于一步延迟”：论文自己指出点堆瞬态可落在 \(10^{-5}\)–\(10^{-3}\,\mathrm{s}\) 范围，并承认 prompt-critical 区间的一阶方法精度较弱；短路案例又在安全压力阈值和控制棒动作附近出现耦合效应。[pdf:E02]（PDF 物理页 2，Introduction）[pdf:E05]（PDF 物理页 5，Table I 后讨论）[pdf:E11]（PDF 物理页 11，Fig. 14–15）未报告的关键证据包括：对 \(\tau_{\rho}/h\) 的系统 sweep、延迟前后闭环特征根比较、保护阈值误判率，以及真实控制器/反应堆数据校准。

## § 10 — 最小复现实验

一周内最值得复现的是“半解析 solver 在强刚性区间的速度—误差优势，以及 unit delay 何时开始破坏结果”，无需先搭完整舰船系统。

1. 直接实现 Eq. (1)–(2) 的六组点堆模型，使用论文给出的 \(\Lambda,\beta_i,\lambda_i\)，并以高精度 Radau/ode15s、RK4、论文 Eq. (14)–(19) 三条求解链并行运行。[pdf:E02]（PDF 物理页 2，Eq. (1)–(4)）[pdf:E03]（PDF 物理页 3，参数列表）
2. 先复现 \(\rho=0.003,-0.007,0.007\) 三个 step input 和 \(h=0.1\)，记录 \(n(t)\) 的平均/最大相对误差、是否收敛和单步运算时间；再把 \(h\) 降到 0.01，核对第三工况的误差是否接近论文报告的 0.0221%。[pdf:E05]（PDF 物理页 5，Table I）
3. 在不改变幅值的前提下，把 \(\rho(t)\) 改成不同上升时间的 ramp 与短脉冲，令特征时间 \(T_\rho/h\) 从 600、100 逐步降到 10、2、1；分别启用/禁用 \(\rho\) 的一步延迟，测量幅值误差、相位误差和峰值时刻偏移。
4. 若能使用同版本 Vitis HLS，再综合仅包含点堆更新的 C kernel；以 80 cycle、61 DSP、5,949 FF、5,686 LUT 作为同配置复现目标，而不把软件运行时间当成硬件 latency。[pdf:E05]（PDF 物理页 5，Table I）

支持核心 claim 的最低结果是：前两个刚性 step 中 proposed method 收敛，平均误差与论文量级一致且显著低于 IRK，同时 HLS latency 接近 80 cycle；反驳信号是：在论文声称可忽略延迟的 \(T_\rho/h\ge100\) 区间仍出现显著相位/峰值误差，或 proposed method 在 delayed-critical 工况的误差/latency 不再优于基线。全部输入都是解析生成的反应性轨迹，不需要外部 dataset；论文未提供代码、bitstream、随机种子或原始波形数据，因此复现应公开 solver 实现、编译配置和误差定义。

## § 11 — 最强反例设计

最强反例不是再增加一个普通短路，而是构造“快速反应性变化与保护阈值同时发生”的闭环场景，专门攻击 unit delay 的尺度分离。令电网故障触发低频/低压补偿，在接近 prompt-critical 边界时叠加有限斜率的控制棒 reactivity pulse；将 pulse rise time 从 \(100h\) 扫到 \(h\)，并把蒸汽压力保护阈值置于两种求解器预测峰值之间。以无延迟的高精度 implicit solver 为参考，比较论文 solver 的 \(n,\rho,P_s\)、特征根、峰值时刻和“是否触发保护”的离散结论。

如果论文方法只是产生小幅连续误差，却把压力是否越过 1.1 p.u.、控制棒是否动作或故障是否扩展的判断翻转，那么 12.5 倍加速不能补偿这种 decision error。短路实验已经表明 EMT 扰动可把蒸汽压力推过 1.1 p.u. 并激发控制棒速度振荡，因此这一反例直接落在论文声称的应用价值上，而不是脱离场景的极端数值测试。[pdf:E10]（PDF 物理页 10，短路场景设置）[pdf:E11]（PDF 物理页 11，Fig. 14–15）反过来，若在 \(T_\rho/h\ge100\) 以及保护边界附近，触发结论、峰值和稳定性都与参考解一致，才会实质增强“unit delay 可忽略”的论证。

## § 12 — Follow-up Research Idea

在电气、核电控制和 power-system EMT 交叉领域，高影响工作通常不仅看算得快，还看数值可信度、保护结论是否可靠、硬件实现是否可复现，以及是否在接近真实的系统边界上给出严格验证。本文已经证明单 FPGA FTRT 的工程可实现性，但尚未把“加速比”与“安全决策误差”纳入同一个可验证目标。

候选研究方向是建立一个**保护判据保真的自适应 FTRT 多域 emulator**：平时沿用本文的半解析、流水化 fast path；在线估计 \(|\dot{\rho}|h\)、刚性比、局部截断误差和保护阈值距离，一旦预计一步延迟可能改变阈值穿越，就仅对点堆—控制—热工闭环局部切换到无延迟 predictor-corrector 或 exponential integrator，并为每次切换输出可审计的误差预算。它改变的问题定义不是“再把 FPGA 做快一点”，而是“在保证保护动作与参考解一致的前提下，最大化可证明的 FTRT 加速比”。

- **未满足需求：** 当前固定 unit delay 的精度证据覆盖有限，尤其缺少快速反应性变化和保护边界附近的保证。[pdf:E04]（PDF 物理页 4，unit-delay 与 LTE 讨论）[pdf:E11]（PDF 物理页 11，压力与控制棒响应）
- **潜在研究价值：** 把硬件吞吐量、数值误差和核电保护 decision consistency 统一为一个验收指标，能把 FPGA emulator 从快速波形发生器推进到可用于安全 V&V 的可信工具。
- **可借鉴工具：** stiff ODE 的 exponential integrator、latency-aware co-simulation、hybrid-system event detection、reachability/interval error bound，以及 FPGA 上的动态 kernel scheduling。
- **首个证伪实验：** 使用第 11 节的 fast-reactivity/pressure-threshold 场景；若自适应方案不能在保持至少 10 倍 FTRT 的同时，把保护触发结论与高精度参考解保持一致，则该方向的核心价值不成立。
- **与本文的实质区别：** 本文以固定半解析式和固定延迟换取确定吞吐；候选方案把延迟误差变成运行时受控变量，并以保护判据保真而非纯墙钟加速作为优化目标。

本卡没有检索 PDF 之外的相关工作，因此上述方向只标记为候选研究想法，不声称 novelty。
