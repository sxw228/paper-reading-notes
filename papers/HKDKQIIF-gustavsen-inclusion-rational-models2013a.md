# Inclusion of Rational Models in an Electromagnetic Transients Program: Y-Parameters, Z-Parameters, S-Parameters, Transfer Functions

- 作者：Bjørn Gustavsen；H. M. Jeewantha De Silva
- 出处：IEEE Transactions on Power Delivery, Vol. 28, No. 2
- 年份：2013
- DOI：10.1109/TPWRD.2013.2247067
- Zotero key：HKDKQIIF
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理一个很具体的工程接口问题：已经从频率扫描或测量中得到多端口器件、线路或子网络的 rational model 后，怎样把它直接接入 EMTP-type 电磁暂态求解器，而不必先把原始的 Y-parameters、Z-parameters 或 S-parameters 强行转换成某一种统一参数。作者还把不直接向主电路注入功率的多输入、多输出 transfer function 纳入同一离散卷积框架。论文的目标不是提出新的拟合算法，而是把已有 frequency-domain macromodel 变成求解器每个固定步长都能更新的 Norton companion model，即固定导纳矩阵与 history current source 的并联表示。[pdf:E01]（PDF 物理页 1，Abstract、Introduction）

这个问题重要，是因为 frequency-dependent component 的端口特性通常不能由少数常参数 RLC 元件忠实表达。变压器高频模型、frequency-dependent network equivalent（FDNE）和实测电缆模型都可能天然以不同参数集出现；若求解器只接受 Y-parameter，S→Y 或 Z→Y 的转换会放大测量与拟合误差，而通过大量等效 RLC 支路实现 rational model 也会受到有限精度影响。[pdf:E01]（PDF 物理页 1，Introduction）因此，价值不只是“多支持三种文件格式”，而是尽量保留模型在其原生参数表示中的精度，并让这些模型进入标准 Dommel/EMTP 时间步循环。

论文直接证明的是离线 Matlab/PSCAD 环境中的接口正确性和三个应用例；它没有报告 FPGA、GPU、实时数字仿真器板卡上的资源、固定延迟或硬实时吞吐。因此本文可为 EMT/实时求解器的模型接口设计提供数学基础，但不能据此声称已有 FPGA 实现或实时性能。

## § 2 — 前人工作与不足

论文之前已经存在三块成熟基础。第一，vector fitting（VF）及相关方法能够把采样的频率响应拟合成满足 symmetry、causality、stability 和 passivity 要求的 pole-residue 或 state-space rational model。第二，Y-parameter rational model 已可通过等效电路或 convolution 接入 EMTP，frequency-dependent transmission line 也长期使用递归卷积。第三，S-parameters 在高频测量中很常用，因为相对直接测量导纳，它们更适合与 50 Ω 或 75 Ω 测量系统配合。[pdf:E01]（PDF 物理页 1，Introduction）；[pdf:E02]（PDF 物理页 2，Section II–III）

不足发生在“模型已经拟合好”到“求解器能够消费它”的最后一公里。等效 RLC 网络会引入数值精度问题；多数 EMTP 工具没有面向用户自定义 rational model 的通用 convolution 接口；S-parameter model 更没有直接接口，只能先转换成 Y-parameter 再拟合，而转换可能严重恶化最终模型。[pdf:E01]（PDF 物理页 1，Introduction）即便数学上不同参数集可相互转换，拟合误差在不同端接条件下的放大规律也不同：Y-based model 更偏向低阻抗端接，Z-based model 更偏向高阻抗端接，实测参数转换还可能出现大幅误差放大。[pdf:E09]（PDF 物理页 9，Section XI Discussion）所以先前工作的真正缺口不是缺少参数变换公式，而是缺少一种能够保留原生表示并直接进入电路求解器的统一时间域接口。

## § 3 — 重建作者的思考路径

下面是基于论文证据重建的推断，而不是作者逐字陈述的研究日志。

研究者首先会注意到，Dommel-type EMTP 的全局方程要求每个动态元件在当前时间步提供一个不随当前未知量变化的 conductance matrix，以及一个由历史状态计算的 source；这正是 Norton companion model 的接口契约。[pdf:E05]（PDF 物理页 5，Section VII、Fig. 5）与此同时，Y、Z、S 和 H 虽然端口变量不同，但拟合后都能写成同一个 state-space 形式。于是问题可先被抽象成：如何把一般的

\[
\dot{\mathbf{x}}=\mathbf{A}\mathbf{x}+\mathbf{B}\mathbf{u},\qquad
\mathbf{y}=\mathbf{C}\mathbf{x}+\mathbf{D}\mathbf{u}+\mathbf{E}\dot{\mathbf{u}}
\]

离散成“只依赖上一时刻输入的状态更新 + 当前输入的代数项”。论文用固定步长 trapezoidal integration 完成这一点，并通过变量代换消除状态对当前步输入的 simultaneous dependency。[pdf:E03]（PDF 物理页 3，Eq. 17–25）

接着，只需对每种参数表示重新解释输入和输出：Y 模型是 \(v\rightarrow i\)，Z 模型是 \(i\rightarrow v\)，S 模型是 incident power wave \(a\rightarrow\) reflected wave \(b\)，H 模型则是一般 \(u\rightarrow y\)。前三者最终都要化成 Norton 形式，H 因为不直接与电路端口交换功率，可以直接输出。[pdf:E04]（PDF 物理页 4，Section V）最后，用一个可精确建模的 RLC 二端口检验“接口代数是否正确”，再用实际规模的子网络与实测电缆检验“这一接口是否能承载真实来源的 rational model”。这条路径把模型拟合误差与接口实现误差分开了。

## § 4 — 核心 Intuition

无论端口数据最初叫 Y、Z、S 还是 transfer function，拟合后的内部动态都可以看成一组由上一步输入驱动的递归状态；当前步只剩一个固定线性映射。把这个固定映射 stamp 到全局导纳矩阵、把递归状态折成 history source，就能让不同参数模型遵守同一个 EMTP 元件接口。[pdf:E03]（PDF 物理页 3，Eq. 24–25）；[pdf:E04]（PDF 物理页 4，Section V）

真正关键的是保留模型的原生参数表示直到接口末端，而不是先做可能放大误差的参数转换。[pdf:E09]（PDF 物理页 9，Discussion）

## § 5 — 具体方法与完整 Pipeline

以“把一根测得 S-parameters 的四导体电缆接入 EMTP”为例，完整 pipeline 如下。

1. **获取端口频率响应。** 输入可以是 \(n\)-port 的 \(\mathbf{Y}(s)\)、\(\mathbf{Z}(s)\)、\(\mathbf{S}(s)\)，或不直接与主电路端口相互作用的 \(\mathbf{H}(s)\)。S-parameters 用参考阻抗 \(\mathbf{Z}_0\) 下的 incident/reflected power waves 定义；本文电缆例使用 50 Ω reference impedance。[pdf:E02]（PDF 物理页 2，Eq. 7–11）；[pdf:E08]（PDF 物理页 8，Section X）

2. **拟合 compact rational model。** 用 VF 等方法把频率样本拟合为共同极点的 pole-residue 形式
   \[
   \mathbf{F}(s)=\mathbf{R}_0+\sum_{m=1}^{N}\frac{\mathbf{R}_m}{s-a_m}+s\mathbf{E},
   \]
   或等价 state-space 形式。对 S-parameter，improper term \(s\mathbf{E}\) 取零。[pdf:E02]（PDF 物理页 2，Eq. 12–14）模型提取时还需按参数类型约束 symmetry、realness、stability/causality 和 passivity；一般 transfer function 不要求端口互易对称或 passivity。[pdf:E03]（PDF 物理页 3，Table II）

3. **形成统一离散递归。** 对 state equation 使用固定步长 trapezoidal integration，并做变量代换，把递归写成
   \[
   \mathbf{x}_k=\boldsymbol{\alpha}\mathbf{x}_{k-1}+\mathbf{B}\mathbf{u}_{k-1},\qquad
   \mathbf{y}_k=\widetilde{\mathbf{C}}\mathbf{x}_k+\mathbf{G}\mathbf{u}_k.
   \]
   非零 \(s\mathbf{E}\) 对应的 derivative contribution 通过扩充状态、\(\boldsymbol{\alpha}\)、\(\mathbf{B}\)、\(\widetilde{\mathbf{C}}\) 和 \(\mathbf{G}\) 并入同一递归。[pdf:E03]（PDF 物理页 3，Eq. 17–25）；[pdf:E04]（PDF 物理页 4，Eq. 26–31）

4. **按参数集生成 Norton 接口。** Y 模型直接给出 \(\mathbf{i}_k=\widetilde{\mathbf{C}}\mathbf{x}_k+\mathbf{G}\mathbf{v}_k\)，所以 \(\mathbf{G}\) 是 conductance，\(-\widetilde{\mathbf{C}}\mathbf{x}_k\) 是 history current。Z 模型先得到 Thevenin form，再用矩阵逆转为 Norton form。S 模型先由 \((\mathbf{a},\mathbf{b})\) 与 \((\mathbf{v},\mathbf{i})\) 的关系消去当前 incident wave，得到 \(\mathbf{G}_{\mathrm{Norton}}\) 和 \(\mathbf{i}_{\mathrm{his},k}\)，随后用上一时刻 terminal voltage 重建 \(\mathbf{a}_{k-1}\) 并更新状态。[pdf:E04]（PDF 物理页 4，Eq. 32–43）；[pdf:E05]（PDF 物理页 5，Table III）

5. **进入 EMTP 时间步。** 第一个时间步依据 \(\Delta t\) 初始化离散系数和固定 conductance matrix，并 stamp 到全局矩阵；以后每步先由各模型更新 history source，再解全局节点电压，最后更新各元件状态。[pdf:E05]（PDF 物理页 5，Section VII、Fig. 5）

6. **电缆实例。** 论文把 150 m 四导体电缆在 9 kHz–50 MHz 测得的 \(8\times8\) S-parameter 拟合为 \(N=200\) 项 pole-residue model，并用 residue-matrix spectral perturbation 强制 passivity；该模型直接走 S-interface，不先转换为 Y 模型。[pdf:E08]（PDF 物理页 8，Section X）

计算优化方面，pole-residue 转换会得到 diagonal \(\mathbf{A}\) 和 selector-like sparse \(\mathbf{B}\)，可避免一般密集矩阵乘法；共轭复极点只计算一半并对实部乘二时，对以复极点为主的模型可接近节省 50% 计算时间。[pdf:E05]（PDF 物理页 5，Section VI、Eq. 44–49）这是算法层面的计算量分析，不是硬件实测速度。

## § 6 — 核心数学推导（无形式化数学则跳过）

先从统一模型开始。论文令 \(\mathbf{F}\) 代表 \(\mathbf{Y},\mathbf{Z},\mathbf{S}\) 或 \(\mathbf{H}\)：

\[
\mathbf{F}(s)=\mathbf{D}+\mathbf{C}(s\mathbf{I}-\mathbf{A})^{-1}\mathbf{B}+s\mathbf{E}.
\]

它在时域对应 \(\dot{\mathbf{x}}=\mathbf{A}\mathbf{x}+\mathbf{B}\mathbf{u}\) 与 \(\mathbf{y}=\mathbf{C}\mathbf{x}+\mathbf{D}\mathbf{u}+\mathbf{E}\dot{\mathbf{u}}\)。这里 \(\mathbf{x}\) 是极点动态的“记忆”，\(\mathbf{D}\) 是瞬时通道，\(\mathbf{E}\) 是与输入变化率相关的 improper part。[pdf:E02]（PDF 物理页 2，Eq. 12–13）；[pdf:E03]（PDF 物理页 3，Eq. 17）

对 regular part \(\mathbf{E}=0\)，trapezoidal integration 先产生同时含 \(\mathbf{u}_k\) 和 \(\mathbf{u}_{k-1}\) 的状态式。通过变量代换，把当前输入 \(\mathbf{u}_k\) 从状态更新中移走，得到

\[
\begin{aligned}
\mathbf{x}_k&=\boldsymbol{\alpha}\mathbf{x}_{k-1}+\mathbf{B}\mathbf{u}_{k-1},\\
\mathbf{y}_k&=\widetilde{\mathbf{C}}\mathbf{x}_k+\mathbf{G}\mathbf{u}_k,\\
\boldsymbol{\alpha}
&=\left(\mathbf{I}-\mathbf{A}\frac{\Delta t}{2}\right)^{-1}
  \left(\mathbf{I}+\mathbf{A}\frac{\Delta t}{2}\right).
\end{aligned}
\]

直觉上，第一行只推进“记忆”，第二行把记忆贡献和当前端口的静态线性贡献相加。由于 \(\mathbf{G}\) 在固定 \(\Delta t\) 下不变，它可以只在初始化时 stamp 一次；\(\widetilde{\mathbf{C}}\mathbf{x}_k\) 则成为每步更新的 history term。[pdf:E03]（PDF 物理页 3，Eq. 18–25）

Y-interface 最直接：

\[
\mathbf{i}_k=\widetilde{\mathbf{C}}\mathbf{x}_k+\mathbf{G}\mathbf{v}_k,\qquad
\mathbf{i}_{\mathrm{his},k}=-\widetilde{\mathbf{C}}\mathbf{x}_k .
\]

符号差来自论文采用的 Norton source 方向约定。Z-interface 的原生输出是电压，因此先得到 Thevenin source \(\mathbf{v}_{\mathrm{his},k}=\widetilde{\mathbf{C}}\mathbf{x}_k\)，再以 \(\mathbf{G}_{\mathrm{Norton}}=\mathbf{Z}_{\mathrm{Thevenin}}^{-1}\) 转为电流源形式。[pdf:E04]（PDF 物理页 4，Eq. 32–36）

S-interface 的关键是 power-wave 变量：

\[
\mathbf{v}=\sqrt{\mathbf{Z}_0}(\mathbf{a}+\mathbf{b}),\qquad
\mathbf{i}=\sqrt{\mathbf{Z}_0}^{-1}(\mathbf{a}-\mathbf{b}),\qquad
\mathbf{b}_k=\widetilde{\mathbf{C}}\mathbf{x}_k+\mathbf{G}\mathbf{a}_k .
\]

把 \(\mathbf{a}_k\) 从这三式中消去，就得到以 terminal voltage 为当前未知量的 Norton conductance 与 history current；上一时刻的 \(\mathbf{a}_{k-1}\) 再由 \(\mathbf{v}_{k-1}\) 和 \(\mathbf{x}_{k-1}\) 恢复。这样 S-model 可以直接进入 nodal solver，而无需先把整套频率数据转换成 Y-parameters。[pdf:E04]（PDF 物理页 4，Eq. 37–43）；[pdf:E05]（PDF 物理页 5，Table III）

## § 7 — 实验设计与结论

**问题一：四种接口的离散实现是否在没有拟合误差时给出相同暂态？** 作者构造一个二端口五节点 RLC 电路，以 501 个对数频率点覆盖 10 Hz–100 kHz；Y、Z 使用 10 阶模型，S、H 使用 11 阶模型。端口 1 经 5 Ω 电阻施加单位阶跃，端口 2 开路，固定步长为 10 μs，并以 PSCAD 中原始 lumped circuit 的 trapezoidal simulation 为参考。[pdf:E06]（PDF 物理页 6，Section VIII、Fig. 6–11）答案是肯定的：Y/Z/S 的端口 1 电流曲线几乎一致，与 lumped model 的差小于 \(1\times10^{-13}\) A；端口 2 电压由 Y/Z/S/H 得到的结果也几乎一致，与 lumped model 的差小于 \(2\times10^{-12}\) V。[pdf:E07]（PDF 物理页 7，Fig. 12–15 及相邻正文）这主要验证接口代数和代码实现，不代表低阶拟合通常都能达到该误差。

**问题二：computed Y-parameters 能否替代一个实际规模子网络？** 作者使用一个 345 kV、27-bus、22 条 transmission line 的系统，线路最长 200 km；从 bus 100 观察子网络，在 1 Hz–2 kHz 之间每 20 Hz 扫描一次并用 VF 形成 reduced-order admittance equivalent。bus 104 在 0.10 s 发生 line-to-ground fault，0.21 s 清除，仿真步长 50 μs。[pdf:E07]（PDF 物理页 7，Section IX、Fig. 16–17）；[pdf:E08]（PDF 物理页 8，Fig. 18–19 及正文）答案是低频和主暂态波形吻合，但 2 kHz 模型上限使高频分量不能被准确重现。[pdf:E08]（PDF 物理页 8，Section IX）这既是正结果，也是论文最重要的适用边界之一。

**问题三：measured S-parameters 能否不经 Y-model 重拟合而直接进入 EMTP？** 作者使用 150 m 四导体工业电缆，在 9 kHz–50 MHz、50 Ω reference impedance 下测得 S-parameters；拟合 \(8\times8\)、\(N=200\) 的 passive pole-residue model。发送端导体 1 施加单位阶跃，其他导体在发送端接地，接收端全部开路，步长 0.01 μs。[pdf:E08]（PDF 物理页 8，Section X、Fig. 20–22）作者把同一 rational S-model 在复频域采样后转换成 Y samples，并用 nodal analysis 加 Numerical Laplace Transform 得到独立频域参考。接收端电压和发送端电流的 simulation 与 NLT 曲线紧密重合，因此接口正确地再现了给定 S rational model 的信息。[pdf:E09]（PDF 物理页 9，Fig. 23–24 及相邻正文）

论文没有报告 wall-clock time、实时因子、内存、CPU 型号、FPGA resource、定点误差或多核 scaling。文中“接近 50%”仅是利用共轭极点减少卷积计算的算法估计。[pdf:E05]（PDF 物理页 5，Section VI）

## § 8 — Take-aways

**5 句话：**

1. Y、Z、S 和 transfer-function rational model 可以先统一成 state-space recurrence，再分别映射到 EMTP 所需的 Norton companion form。[pdf:E03]（PDF 物理页 3，Eq. 24–25）；[pdf:E04]（PDF 物理页 4，Section V）
2. 直接支持原生参数集的主要价值，是避免参数转换对已有测量与拟合误差的放大。[pdf:E09]（PDF 物理页 9，Discussion）
3. 二端口 RLC 例把接口实现误差压到约 \(10^{-12}\)–\(10^{-13}\) 量级，说明四条接口在拟合足够准确时数学上一致。[pdf:E07]（PDF 物理页 7，Fig. 12–15）
4. 子网络和实测电缆例说明该方法能承载 computed Y-data 与 measured S-data，但子网络例也直接暴露了拟合带宽决定可重现暂态频谱的边界。[pdf:E08]（PDF 物理页 8，Sections IX–X）
5. 本文证明的是模型接口，不是 model extraction 在所有工况下的正确性，也不是实时硬件实现。

**3 句话：** 论文把不同端口参数的 rational model 统一成“固定 conductance + history source”，从而嵌入标准 EMTP 时间步。[pdf:E05]（PDF 物理页 5，Section VII）原生参数直连能减少转换误差，但最终暂态精度仍取决于拟合频带、参数表示、端接条件和 physicality。三组示例支持接口正确性，却没有给出硬实时或 FPGA 证据。

**1 句话：** 这项工作的核心不是再发明一种 rational fitting，而是让拟合结果以最少的参数转换损失进入 EMTP。[pdf:E10]（PDF 物理页 10，Section XII Conclusion）

## § 9 — 最脆弱的假设

最脆弱的假设是：**所选参数表示下的 rational model，已经在实际暂态会激发的频谱和端接条件上足够准确，而且满足稳定性与 passivity；接口本身不会修复一个超出有效域的模型。**

这个假设一旦失败，论文最漂亮的 Norton 推导仍会稳定而高效地计算出错误波形。论文自己的证据已经展示两种失效入口。第一，2 kHz 截止的子网络 equivalent 能复现主波形，却不能准确复现高频分量。[pdf:E08]（PDF 物理页 8，Section IX）第二，Discussion 明确指出 Y-based fit 对低阻端接通常更准确，Z-based fit 对高阻端接更准确，实测参数在转换后还可能出现大误差放大。[pdf:E09]（PDF 物理页 9，Section XI）

论文对这个假设提供的是三个成功案例和模型提取阶段的 physicality 要求，而不是跨端接、跨频带的误差上界。[pdf:E03]（PDF 物理页 3，Table II）尤其是二端口验证刻意把 fitting error 做到近乎为零，因此它很好地隔离了接口 bug，却没有压力测试“拟合略有误差时哪种接口更可信”。这是本文最关键、失败代价也最大的证据缺口。

## § 10 — 最小复现实验

一周内最小复现应选择论文 Fig. 6 的二端口 RLC 电路，因为它能把接口实现误差与复杂设备建模误差分开。

1. 按 Fig. 6 重建原始 lumped circuit，并在 10 Hz–100 kHz 的 501 个对数频点上计算端口 \(\mathbf{Y}\)；由矩阵关系得到 \(\mathbf{Z}\)、\(\mathbf{S}\) 和 \(H=-Y_{21}/Y_{22}\)，其中 \(\mathbf{Z}_0=\mathrm{diag}(100,200)\ \Omega\)。[pdf:E06]（PDF 物理页 6，Fig. 6、Eq. 50、Section VIII-B）
2. 使用同一 pole set 或现成 VF 实现拟合 Y/Z/S/H，然后只实现 Eq. 24–43 所需的四条离散接口。参考解直接对原始 RLC 进行同样的 10 μs trapezoidal simulation。
3. 复现实验输入：端口 1 经 5 Ω 施加单位阶跃，端口 2 开路；测量端口 1 电流、端口 2 电压，以及四种接口相对 lumped reference 的最大绝对误差。[pdf:E06]（PDF 物理页 6，Fig. 11 及 Section VIII-C）
4. **支持 claim 的标准：** 先确认 frequency-domain fit error 足够小，再观察 Y/Z/S/H 暂态彼此重合，且误差接近论文报告的 \(10^{-12}\)–\(10^{-13}\) 数量级。[pdf:E07]（PDF 物理页 7，Fig. 12–15）
5. **反驳接口 claim 的标准：** 在 fit error 和数值精度已控制后，任一参数接口出现系统性偏差、能量增长或对 \(\Delta t\) 异常敏感。若只有拟合频带外发生偏差，则反驳的是有效域假设，而不是接口代数。

为了让复现更有诊断力，可再加一个不改变主任务的小检查：把 \(\Delta t\) 减半，验证接口间差异按数值离散误差下降；不要一开始就复现 27-bus 网络或 200 项电缆模型。

## § 11 — 最强反例设计

最强反例不是让 VF 故意拟合失败，而是构造一个**训练频点上误差很小、目标暂态中却必然失败**的多端口网络。具体做法是：在原拟合频带上方紧邻处加入一个高 Q、弱阻尼模态；频率扫描仍沿用较稀的采样网格，使样本点避开窄共振；训练时使用低阻端接并拟合 Y-model，暂态时切换到开路或高阻端接，同时用陡峭开关沿激发带外能量。对照组使用覆盖该模态的加密扫描和 Z/S 原生拟合。

这个反例有三个可预测结果：样本点上的 fit metric 仍会很好看；原 Y-interface 不会数值报错；但高阻端接下的峰值、衰减率或振铃频率会显著偏离 detailed circuit。它直接结合了论文已承认的两个弱点：有限上频率不能重现高频分量，以及 Y/Z 拟合精度依赖端接阻抗。[pdf:E08]（PDF 物理页 8，Section IX）；[pdf:E09]（PDF 物理页 9，Discussion）

若这种失配出现，即使 passivity enforcement 能阻止非物理能量生成，也不能证明 transient fidelity。反过来，若作者方法配合一套明确的频带/端接有效域仍能给出可靠误差界，这个反例才算被击败。

## § 12 — Follow-up Research Idea

在 EMT、电力系统建模领域，高影响工作的评价重点通常是：数学稳定与物理一致性、跨工况的暂态保真度、可复现的工程系统验证，以及能否进入真实求解器工作流；单纯多支持一种文件格式或多跑一个案例通常不够。基于第 9 节，候选方向是把问题从“把一个 rational model 接入 EMTP”改写为：

**为多端口 frequency-dependent model 联合生成可执行 macromodel 与端接/频谱条件下的 transient-error certificate。**

（a）驱动需求是：现有接口知道怎样高效计算，却不知道当前 excitation、termination 和 switching spectrum 是否已超出模型的有效域；2 kHz 子网络例证明“数值正常运行”不等于“高频暂态可信”。[pdf:E08]（PDF 物理页 8，Section IX）

（b）研究价值在于把模型选择从经验判断变成可审计保证。交付物不再只有 \(\mathbf{A},\mathbf{B},\mathbf{C},\mathbf{D}\)，还包括在一类端接和输入频谱下的误差界、在线有效域指示量，以及越界时触发重新拟合或局部 detailed model 的规则。这改变了研究目标，而不是给现有接口外挂一个监视器。

（c）可借鉴相邻领域的 passivity-preserving model order reduction、robust control 中的 \(H_\infty\) / structured uncertainty bound，以及 system identification 的 frequency-dependent confidence set。论文已有 passivity 和原生参数选择基础，但没有 transient error certificate。[pdf:E03]（PDF 物理页 3，Table II）；[pdf:E09]（PDF 物理页 9，Discussion）

（d）第一个可证伪实验：随机生成一组含弱阻尼模态的多端口 RLC/线路网络，划分未见过的端接与开关波形；对每个模型先预测 transient-error upper bound，再与 detailed simulation 的峰值、能量和波形误差比较。只要真实误差频繁超过 certificate，或 certificate 始终宽到没有决策价值，这个方向就失败。

（e）它与本文的实质区别是：本文假定 model extraction 已足够准确，然后证明接口能忠实执行该模型；新方向把“何时足够准确”本身纳入模型输出和求解器决策。由于本次没有对 2013 年后的 error-bounded parametric macromodel、robust MOR 与 EMT 接口工作做系统检索，这只是候选研究想法，不声称 novelty。
