# Using Dynamic Phasors To Model and Analyze Selective Harmonic Compensated Single-Phase Grid-Forming Inverter Connected to Nonlinear and Resistive Loads

作者：Udoka C. Nwaneto；Andrew M. Knight  
出处：IEEE Transactions on Industry Applications, Vol. 59, No. 5, pp. 6136–6154  
年份：2023  
DOI：10.1109/TIA.2023.3282925  
Zotero key：3E2NUM8I  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是：怎样用 dynamic phasor（DP，动态相量）代替详细开关 electromagnetic transient（EMT）模型，既保留单相 grid-forming inverter（GFMI）在非线性负载下的关键谐波与暂态，又显著缩短仿真时间。孤岛运行的 GFMI 不再跟随外部电网，而要自己建立电压和频率；二极管桥整流器等非线性负载会抽取尖峰电流，经有限输出阻抗把电流畸变变成电压畸变。论文以“输出电压 THD 不超过 5%”作为工程约束，并指出详细开关模型准确但大系统计算慢，常规 phasor model 又因稳态和基波假设不适合谐波研究。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

作者的核心技术 claim 是：把交流侧的 1、3、5、7 次谐波和直流侧的 0、2、4、6 次分量显式保留后，DP 模型可以复现详细开关模型的主要动态与主导谐波；而且从两种模型推导出的控制对象小信号模型等价，因此详细模型、DP 模型和实验平台可以共用同一组控制器增益。[pdf:E02]（PDF 物理页 2，Section I 的 contributions）这项工作的价值不只是“跑得快”，而是试图让多变流器、非线性负载的系统级 harmonic study 能够在仍保留控制动态的模型上进行。

## § 2 — 前人工作与不足

论文回顾的 standalone inverter 控制包括 PI、PR 加 harmonic resonant（HR）、deadbeat、model predictive control、H-infinity、feedback linearization、sliding mode、Lyapunov 和 repetitive control。作者认为这些控制工作大多依赖详细开关模型；当微电网里有多个带 selective harmonic compensator（SHC）的 DER 和多个非线性负载时，开关频率时间尺度会把系统级 EMT 仿真的执行时间推高。已有三相微电网 DP 工作已经能在不平衡与谐波条件下建模，但作者指出单相、SHC 控制、同时连接电阻与二极管桥负载的 GFMI 尚未得到同等完整的 DP 建模；已有单相 standalone 双环控制工作又只补偿基波，无法抑制整流负载引起的 3、5、7 次电压谐波。[pdf:E02]（PDF 物理页 2，Section I）

这里需要保留证据边界：上述“已有工作不足”是论文作者对其引用文献的归纳，本卡没有联网逐篇复核，也不把作者的 “to the best of our knowledge” 升级为已独立证明的 novelty 结论。论文真正闭合的是模型构造、增益映射和给定工况下的验证，不是对所有单相 DP 文献的穷尽检索。

## § 3 — 重建作者的思考路径

下面是基于论文证据的逆向重建，而不是作者明说的研发日志。

第一步，工程上同时需要两件互相拉扯的东西：常规 phasor model 的大步长，以及 EMT 对暂态和谐波的保真。DP 提供了中间表示：用移动时间窗上的时变 Fourier 系数表示近周期波形；稳态时系数近似常数，暂态时缓慢变化，因此可以在不跟踪每次 PWM 开关动作的情况下保留选定频率分量。[pdf:E03]（PDF 物理页 3，Eqs. (3)–(6) 与 Section II）

第二步，不直接对开关电路生搬 Fourier 变换，而是先把 H 桥换成受控电压源、把二极管桥换成含 switching function 的等效变压器，得到连续时间 averaged model；再把 inverter、DBR、LCR 负载和双环控制器分别变到 DP 域。[pdf:E04]（PDF 物理页 4，Eqs. (7)–(23)）第三步，若 DP 与详细模型的 control plant 小信号传递函数相同，就能把详细模型上已经成熟的调参规则直接迁移到 DP 模型，避免“快模型必须重新调控制器”。第四步，用最容易暴露模型差异的工况验证：突然卸掉并联电阻负载，同时比较无换相电感和 10 mH 换相电感两种整流器接入方式。

## § 4 — 核心 Intuition

DP 的关键不是把全部开关波形压成一个基波 phasor，而是只追踪对问题真正重要的一小组、随时间缓慢变化的谐波系数。这样既保留 LC 功率级与控制器的动态，也绕开 20 kHz PWM 的逐开关积分；如果选定谐波覆盖了支配性频谱，模型就能以更大步长复现主要暂态和谐波。代价也同样直接：被截断的高次谐波不会凭空回来，因此 THD 和尖峰波形可能比真实系统更乐观。

## § 5 — 具体方法与完整 Pipeline

以论文实验对象为例，输入是 300 V 直流母线供电的单相 H 桥，输出端含 \(R_f\!-\!L_f\) 串联支路和并联 \(C_f\)，同时接电阻负载 \(R_l\) 与带 \(L_s,R_s,L_d,R_d,C_o,R_o\) 的单相 diode-bridge rectifier（DBR）。控制器是外电压环 PR+HRC 和内电流环 PI，并有输出电压 feedforward。Fig. 1 给出了详细开关模型与 averaged model 的一一对应拓扑。[pdf:E03]（PDF 物理页 3，Fig. 1）

完整 pipeline 如下：

1. **开关级到 averaged model。** 用受控电压源代替 H 桥，省略理想直流源动态；用电压、 电流 switching function \(S_v,S_c\) 描述 DBR 的交直流映射。换相电感可忽略时使用方波 switching function；\(L_s\) 不可忽略时，用由 overlap angle \(\mu\) 决定的 quasi-square 电压函数和 trapezoidal 电流函数，并把 \(L_s\) 并入直流电感动态。[pdf:E04]（PDF 物理页 4，Eqs. (10)–(20)）
2. **选择频谱状态。** 交流侧只保留 \(n=\{1,3,5,7\}\)，直流侧保留 \(n=\{0,2,4,6\}\)。乘法通过 DP convolution 展开，因此 DBR 的整流作用仍能把奇次交流分量映射到偶次直流分量。[pdf:E05]（PDF 物理页 5，Eqs. (24)–(36)）
3. **把控制器一起变到 DP 域。** 外环对 1、3、5、7 次电压分量分别提供 resonant compensation，内环 PI 同时处理每个 DP 的实部和虚部。作者据此得到 16 个内电流环实状态方程，而不是在时域逐点生成 PWM。[pdf:E05]（PDF 物理页 5，Eqs. (37)–(38)）
4. **增益设计与时间推进。** 由详细模型和 DP 模型共同的小信号 plant 设计控制增益；随后在 MATLAB 中用 user-written code 实现 DP 模型，在 MATLAB/Simulink/Simscape 中实现详细开关基线。论文把 DP 与开关模型分别以 0.5 ms 和 0.5 μs 步长运行，并在 \(t=0.2\) s 把 \(R_l\) 从 50 \(\Omega\) 阶跃到 10 k\(\Omega\)。[pdf:E09]（PDF 物理页 9，Section V-B、V-C 与 Fig. 7）
5. **输出与比较。** 由 DP 系数重构 \(v_f,i_T,i_s,v_d,i_d,v_o\) 的时域波形，比较单次谐波幅值、THD、CV(RMSE) 和 CPU execution time；再在硬件上重复两种 \(L_s\) 工况。

论文没有报告所用 Simulink solver、积分算法、误差容限或 stiffness 处理；“0.5 ms 对 0.5 μs”是两个独立模型的步长选择，不是同一仿真中的 multi-rate coupling。PWM 开关事件在 DP 模型中被平均化，论文没有另给离散事件处理算法。并行划分、GPU/多核加速、fixed-point 数值格式、FPGA 映射、片上资源、pipeline latency 和实时闭环执行均未报告；实验控制器是 C2000 微控制器，不是 FPGA。

## § 6 — 核心数学推导（无形式化数学则跳过）

**1. 从波形到动态相量。** 对基频为 \(\omega\) 的近周期波形，论文在滑动窗 \(T\) 上写成

\[
x(\tau)=\sum_{k=-\infty}^{\infty} X_k(t)e^{jk\omega\tau},\qquad
X_k(t)=\frac{1}{T}\int_{t-T}^{t}x(\tau)e^{-jk\omega\tau}\,d\tau .
\]

\(X_k(t)\) 就是第 \(k\) 个 DP；与固定 phasor 不同，它随暂态变化。时域重构采用 \(X_0\) 加各阶 DP 实部、虚部的 cosine/sine 组合；导数和乘积分别满足

\[
\frac{d\langle x\rangle_k}{dt}
=\left\langle\frac{dx}{dt}\right\rangle_k-jk\omega\langle x\rangle_k,
\qquad
\langle xu\rangle_k=\sum_i\langle x\rangle_{k-i}\langle u\rangle_i .
\]

第一式保留 envelope 动态，第二式是整流器频率搬移的数学入口。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(6)）

**2. 功率级的 DP 化。** 例如 inverter filter 的每个奇次分量满足

\[
L_f\frac{d\langle i_i\rangle_n}{dt}
=\langle v_i\rangle_n-\langle v_f\rangle_n-R_f\langle i_i\rangle_n
-jn\omega L_f\langle i_i\rangle_n ,
\]

\[
C_f\frac{d\langle v_f\rangle_n}{dt}
=\langle i_i\rangle_n-\langle i_T\rangle_n
-jn\omega C_f\langle v_f\rangle_n .
\]

它们与原 LC 微分方程相比多出的 \(-jn\omega\) 项，是在旋转的第 \(n\) 次谐波坐标中观察状态所产生的频移项。DBR 侧利用 \(S_v,S_c\) 的 DP 与 convolution 把交流奇次分量映射到直流偶次分量；当 \(L_s\neq0\) 时，\(\mu\) 又由输出电压幅值和平均直流电流更新。[pdf:E05]（PDF 物理页 5，Eqs. (24)–(36)）

**3. 为什么能共用控制增益。** 详细 averaged model 线性化后，内、外环 plant 为

\[
G_i(s)=\frac{1}{sL_f+R_f},\qquad
G_v(s)=\frac{R_{ac}}{sC_fR_{ac}+1}.
\]

DP 模型的实、虚通道在线性化后得到相同分母；交叉耦合项被 PI/PR/HR 对复数分量的同步处理吸收，因此作者认定 \(G'_i=G_i\)、\(G'_v=G_v\)，同一组 gains 可用于详细模型和 DP 模型。[pdf:E06]（PDF 物理页 6，Eqs. (42)–(47) 与 Fig. 2）附录进一步说明 regular phasor 通过把功率级导数置零而变成代数模型，因而会漏掉 startup 与 fault-clearing transient；DP 则保留这些状态导数并可加入整数倍谐波。[pdf:E17]（PDF 物理页 17，Eqs. (A1)–(A10)）

**4. 参数落地。** 论文使用 \(R_f=0.2\,\Omega\)、\(L_f=3.1\,\mathrm{mH}\)、\(C_f=20\,\mu\mathrm{F}\)、\(L_d=30\,\mathrm{mH}\)、\(C_o=470\,\mu\mathrm{F}\)、\(R_o=25\,\Omega\)、\(V_f^\*=127.3\,\mathrm{V}\)、\(\omega=377\,\mathrm{rad/s}\)、\(f_s=20\,\mathrm{kHz}\)。内环 \(k_{pi}=77,k_{ii}=0\)；外环各奇次 proportional gain 为 0.2，resonant gains 为 100、50、30、20，\(\omega_{cvn}=3.14\,\mathrm{rad/s}\)。由此得到电流环 crossover 约 25 krad/s、phase margin 90.1°。[pdf:E07]（PDF 物理页 7，Tables I–II、Eqs. (48)–(50) 与 Fig. 3）外电压环推导给出 \(k_{pv1}\approx\omega_{bv}C_f\) 的近似；在 \(\omega_{cvn}=3.14\,\mathrm{rad/s}\) 时 crossover 为 10.5 krad/s、phase margin 50°，把 \(\omega_{cvn}\) 增至 10 rad/s 会把 crossover 提至 14.5 krad/s、phase margin 降至 15.9°，体现“谐振带宽更宽但稳定裕度更小”的权衡。[pdf:E08]（PDF 物理页 8，Eqs. (52)–(55) 与 Fig. 4）

附录还在忽略高次谐波、稳态且 \(R_d\) 可忽略时，把 DBR 折算成

\[
R_{td}=\frac{\pi^2R_o}{8},
\]

再与 \(R_l\) 并联得到小信号外环所用的 \(R_{ac}\)。这个折算依赖稳态与低阶近似，不应当被外推到尖峰整流瞬态。[pdf:E18]（PDF 物理页 18，Eqs. (A18)–(A21)）

## § 7 — 实验设计与结论

**问题 1：DP 与详细模型是否可以共用控制增益？ →** 作者分别对 averaged model 和 DP model 做小信号化，并比较 current-loop Bode plot。**答案：** 在论文采用的时标分离与交叉耦合处理下，两者 plant 的 Bode 曲线重合，故直接采用相同 gains；不过论文也明确说实际 sampling/transport delay 会降低 phase margin，而仿真因步长很小忽略了该 delay。[pdf:E07]（PDF 物理页 7，Fig. 3 与 Section V-A）

**问题 2：当 \(L_s\approx0\) 时，DP 能否复现卸载暂态和谐波？ →** 在 \(t=0.2\) s 将 \(R_l\) 从 50 \(\Omega\) 变成 10 k\(\Omega\)，比较 0.5 ms 的 DP 与 0.5 μs 的开关模型。**答案：** 两者主要波形接近，但 DP 因只保留到 7 次谐波而低估电压 THD：卸载前论文报告 \(i_T\) THD 为 SW 28.09%、DP 28.73%，而 \(v_f\) THD 为 SW 1.95%、DP 0.12%。作者还观察到 DP 的 \(v_d\) 有约 8–10 V offset。[pdf:E10]（PDF 物理页 10，Figs. 8–9、Section V-C2 与 Eqs. (56a)–(56b)）

同一工况下，0.5 ms DP 的 CV(RMSE) 分别为 \(v_f\) 0.83%、\(i_T\) 3.07%、\(i_s\) 3.63%、\(v_d\) 2.75%、\(i_d\) 2.35%、\(v_o\) 1.65%。执行时间方面，SW 0.5 μs 为 1115.30 s；DP 同步长为 4.39 s，即 254.1 倍加速；DP 用 0.5 ms 为 0.34 s，即相对 SW 加速 3280.3 倍。[pdf:E11]（PDF 物理页 11，Tables III–IV）因此“大步长带来三千倍量级加速”的结论成立于该机器、该模型和该 solver 配置，不是与硬件无关的常数。

**问题 3：换相电感显著时是否仍有效？ →** 把 DBR 的 \(L_s\) 设为 10 mH，重复相同卸载阶跃。**答案：** \(L_s\) 滤去更多高频电流，使有限谐波 DP 更容易逼近开关模型；Fig. 10–12 显示波形和主导谐波趋势一致，但作者指出 current switching function 把真实指数换相近似成线性过渡，仍会抬高误差。[pdf:E12]（PDF 物理页 12，Figs. 10–12 与 Section V-D）

在 10 mH 工况下，0.5 ms DP 的 CV(RMSE) 为 \(v_f\) 0.56%、\(i_T\) 2.44%、\(i_s\) 2.83%、\(v'_d\) 7.26%、\(i_d\) 2.11%、\(v_o\) 0.80%；\(v'_d\) 是最明显例外，因为推导把交流电感当作直流电感。执行时间为 SW 1122.80 s、0.5 ms DP 0.36 s，即 3118.9 倍加速。[pdf:E13]（PDF 物理页 13，Tables V–VI）这说明增加 \(L_s\) 改善了多数状态的近似，却没有修复整流端电压建模误差。

**问题 4：仿真与真实硬件是否一致？ →** 实验平台采用 TI TIDM-HV-1PH-DCAC inverter、C2000 TMS320F28377D controller、300 V DC source、Semikron DBR 和 Keysight Power Analyzer；开关 dead band 为 0.2 μs，并重复 \(L_s\approx0\) 与 10 mH 两种工况。[pdf:E13]（PDF 物理页 13，Fig. 13 与 Section VI）在 \(L_s\approx0\) 时，\(R_l=50\,\Omega\) 的实验 \(i_T/v_f\) THD 为 26.90%/4.424%；移除 \(R_l\) 后为 44.05%/6.77%，扩展到 40 次谐波时为 43.81%/6.84%。因此最弱的无电阻负载工况里，实测电压 THD 已越过论文采用的 5% 门槛，而只看低阶 DP 很容易过于乐观。[pdf:E14]（PDF 物理页 14，Figs. 14–18 与 Section VI-A）

在 \(L_s=10\) mH 时，实验波形的畸变和 DC 侧幅值下降，与模型趋势一致；作者把 load-step 瞬间的差异归因于模型省略了 DC source inertia。[pdf:E15]（PDF 物理页 15，Figs. 19–22 与 Section VI-B）实验在卸载前报告 \(i_T/v_f\) THD 为 11.5%/1.1%，卸载后为 17.38%/1.88%，计入 40 次谐波后为 17.40%/2.05%。不过主导谐波也不是逐项精确：DP 给出的 \(i_T\) 前四项 RMS 为 4.66、0.70、0.32、0.21 A，实验为 4.40、0.47、0.16、0.09 A。[pdf:E16]（PDF 物理页 16，Fig. 23 与 Section VI-B、VII）所以更准确的结论是“波形动态和主导频谱趋势在两种给定工况下可用”，而不是“THD 或每个谐波幅值都高精度”。

论文没有实验多变流器耦合、频率偏移、控制饱和、弱直流源、不同整流器拓扑、随机开关噪声或实时仿真；结论也把 multi-converter validation 明确留给未来。因此本文证据不能外推到 FPGA 实时 EMT，也不能证明固定 7 次谐波截断在所有非线性负载下都足够。

## § 8 — Take-aways

**5 句话：**  
1. 论文用动态相量把单相 GFMI、SHC 控制和 DBR 非线性负载统一到一个保留暂态的低频 envelope 模型中。  
2. 交流侧追踪 1、3、5、7 次，直流侧追踪 0、2、4、6 次，使 DP 可以用 0.5 ms 而不是 0.5 μs 步长运行。  
3. 小信号推导表明详细 averaged model 与 DP model 具有相同的内、外环 plant，因此控制增益可直接映射。  
4. 在两种 \(L_s\) 工况下，DP 对主要波形和 dominant harmonics 与开关仿真、实验大体一致，并在论文机器上达到约 3119–3280 倍加速。  
5. 但固定谐波截断会显著低估 THD，并对整流端电压和较高次谐波产生系统性误差。

**3 句话：** DP 是常规 phasor 与开关 EMT 之间的工程折中：保留选定谐波的动态，换取大步长。本文最强结果是同增益下的模型、仿真和硬件趋势闭合以及三千倍量级的特定平台加速。最重要的限制是不能把“dominant harmonic 一致”误读成“THD 合规判断可靠”。

**1 句话：** 这篇论文证明了 fixed-order DP 能快速回答“主要动态和低阶谐波怎样变化”，但尚不能可靠回答“最坏工况下总谐波是否一定达标”。

## § 9 — 最脆弱的假设

最脆弱的假设是：对研究工况而言，交流侧 1、3、5、7 次与直流侧 0、2、4、6 次已经包含足以支配控制和电能质量判断的频谱信息。这个假设一旦不成立，模型最吸引人的两个用途会同时失效：SHC 调参看到的是被截断后的“较干净电压”，而 THD 合规判断又恰恰依赖所有被遗漏的高次分量。

论文自己给出了反向证据。\(L_s\approx0\) 时，DP 预测 \(v_f\) THD 0.12%，开关模型为 1.95%；实物在卸掉 \(R_l\) 后达到 6.77%（40 次计算为 6.84%），已经跨过 5% 门槛。[pdf:E10][pdf:E14]（PDF 物理页 10、14，Section V-C2 与 VI-A）作者也承认 THD 可能不准，建议比较单次谐波幅值；结论只声称 dominant harmonics 的高准确度。[pdf:E16]（PDF 物理页 16，Section VII）

支持该假设的证据是两种 \(L_s\) 和一个 DBR 参数集下的波形、低阶幅值与实验趋势一致；缺少的则是负载参数扫描、窄导通角、更强电容输入、频率漂移、多个 converter 的频谱互调，以及一个能根据截断误差自动判断“当前阶数是否够用”的证据界限。基于证据的判断是：固定阶数对系统级趋势研究有价值，但对 compliance gate 仍不够稳健。

## § 10 — 最小复现实验

一周内最小复现不需要先做硬件，可以只验证最核心且可证伪的 claim：“相同 gains 下，0.5 ms DP 能复现 0.5 μs 开关模型的卸载暂态与主导谐波，同时显著更快。”

1. 在 MATLAB/Simulink 中按 Tables I–II 建一个 H 桥开关基线；用 MATLAB code 实现 Eqs. (24)–(38) 的固定阶 DP，并使用完全相同的 PR+HRC/PI gains。
2. 分别设置 \(L_s\approx0\) 与 10 mH；在 0.2 s 把 \(R_l\) 从 50 \(\Omega\) 变为 10 k\(\Omega\)。保存 \(v_f,i_T,i_s,v_d,i_d,v_o\)，使用同一时间网格计算 CV(RMSE)，并比较 1、3、5、7 次 RMS 幅值与 execution time。
3. 预先定义支持标准：除论文已识别的 \(v'_d\) 外，六个主要状态的 CV(RMSE) 不高于 4%；\(v'_d\) 不高于 8%；0.5 ms DP 相对 0.5 μs SW 至少快 1000 倍；卸载前后各低阶幅值变化方向一致。任一主要状态超过阈值、出现不同稳定性结论，或加速不足，都反驳该复现版本的核心 claim。
4. 另把 THD 当作独立风险指标而不是通过门：若 DP 与 SW 对“是否超过 5%”给出相反判断，即使 CV(RMSE) 通过，也记录为模型不能用于 compliance 判定。

这些阈值是为一周复现实验制定的可证伪验收，不是论文原文的普适保证。

## § 11 — 最强反例设计

最强反例不是简单换一个负载，而是有意让“被省略频谱”主导控制结论：使用 \(L_s\approx0\)、大 \(C_o\)、较轻 \(R_o\) 形成很窄的整流导通脉冲，移除并联 \(R_l\)，保留真实 dead time、DC source impedance 和 controller saturation；再加入 58–62 Hz 频率漂移，使固定整数谐波与实际频率稍微失配。以详细 EMT 和硬件为基线，同时运行固定到 7 次的 DP。

攻击成功的判据是：DP 仍给出稳定、低于 5% 的 \(v_f\) THD 或可接受的低阶幅值，而 EMT/硬件出现高次或 interharmonic 驱动的 THD 超标、limit cycle、控制饱和或明显不同的暂态峰值。这个反例会排除“只是测量噪声导致 THD 不同”的替代解释，因为可以逐阶核对 9–40 次能量、控制输出饱和时间和时域残差；若差异随扩大 DP 阶数单调消失，就直接证明失败来自 fixed-order truncation，而不是开关模型本身。

## § 12 — Follow-up Research Idea

在电力电子与工业应用期刊语境中，高影响工作通常需要同时证明模型机制、控制可实现性、跨工况准确性、计算收益和硬件价值。基于第 9 节的限制，一个非增量候选方向是：**error-certified adaptive dynamic phasor**。它不再把目标定义为“预先固定几次谐波并尽量逼近 EMT”，而是让模型在线估计被截断频谱对控制状态和 THD 门限的影响；当误差上界可能改变稳定性或 5% 合规结论时，自动增加相量阶数或局部回退到短窗 EMT。

- **未满足需求：** 系统级研究既要 DP 的速度，也要知道“当前速度是以多少不可见误差换来的”，尤其不能在阈值附近给出没有置信边界的合规结论。
- **潜在研究价值：** 若能在多 converter、不同整流负载和频率漂移下仍给出可验证误差界，就把 DP 从经验选阶工具变成可用于工程决策的 certified reduced model。
- **可借鉴工具：** sparse spectral estimation 用于发现新频率，adaptive model-order reduction 用于按误差扩阶，hybrid simulation 用于只在高风险时间窗启用开关 EMT，robust control 用于把谱截断误差作为有界扰动。
- **第一个证伪实验：** 在第 11 节的窄导通角与频率漂移 sweep 中，要求预测区间始终包住 EMT/硬件的 \(v_f\) 峰值、1–40 次谐波幅值和 THD；若任何一次误差界漏包，或自适应后的执行时间退化到接近全程 EMT，该想法即失败。
- **与本文的实质区别：** 本文固定保留 1/3/5/7 与 0/2/4/6 次，并在事后解释误差；候选方法把“是否需要更多频率状态”变成模型运行时的受证据约束决策，同时把 compliance 结论而非波形相似度设为首要输出。

论文只把 multi-converter validation 列为未来工作，没有检索或验证上述自适应误差认证路线；因此这是一项基于本文局限形成的候选研究想法，不声称 novelty。
