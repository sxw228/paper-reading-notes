# Matrix Low-dimensional Qubit Casting Based Quantum Electromagnetic Transient Network Simulation Program

- 作者：Qi Lou、Yijun Xu、Wei Gu
- 出处：*IEEE Transactions on Quantum Engineering*，2026（源 PDF 为 accepted author version）
- DOI：10.1109/TQE.2026.3712782
- Zotero key：EY822HYI

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是“如何用量子计算机取代整个 EMT 仿真器”，而是一个更窄、也更现实的问题：当 VQLS（variational quantum linear solver）被用来求解每个 EMT 时间步的节点方程时，怎样减少导纳矩阵到 Pauli operator 的预处理量、怎样减少一次 cost-function evaluation 所需的量子电路数，以及怎样避免高频开关引起的导纳矩阵反复重建。作者把前两项归结为 VQLS-QEMTP 的资源瓶颈，把第三项归结为它尚未进入 power-electronic switching network 的原因。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E02]（PDF 物理页 2，contributions）

工程上，经典 EMTP 先把 R、L、C 等支路离散成 Norton 等值，再在每个时间步求解

$$
\mathbf G\mathbf v(t)=\mathbf i_{\mathrm{inj}}(t)+\mathbf I_{\mathrm{history}}\equiv \mathbf i(t),
$$

其中 $\mathbf G$ 是节点导纳矩阵，右端同时包含当前注入和历史电流。[pdf:E03]（PDF 物理页 2，Fig. 1 与 Eq. (1)）大规模 converter-dominated network 的困难并不只在一次线性求解：开关事件会改变网络拓扑，如果每次变化都触发高维 Pauli projection，预处理就会反复发生。因此，本论文的价值应理解为“降低量子线性求解接口的结构化数据准备成本，并使固定导纳形式的开关网络能够进入同一 QEMTP pipeline”，而不是已经给出了可实时部署的量子 EMT 平台。

这里必须先划清实现边界。论文提出的是 quantum algorithm 及其经典-量子混合执行流程；案例中的量子电路由 statevector simulation 评估。论文没有报告 FPGA 映射、HDL、定点位宽、片上资源、时序收敛、WCET、HIL 接口或 FPGA 实时步长，因此不能把本文结果外推为 FPGA EMT 实现，也不能把“quantum circuit reduction”理解成 FPGA logic reduction。[pdf:E13]（PDF 物理页 8，Case Study 计算环境）[pdf:E14]（PDF 物理页 9，两个 switching case 的 statevector 设置）

## § 2 — 前人工作与不足

作者把最相关的 QEMTP 路线分成两代。第一代是 HHL-based QEMTP：它证明了量子线性方程算法可以嵌入 EMTP，但作者引用的 RLC 示例已经需要 7 qubits 和 102 circuit layers，只在 noise-free quantum simulator 上测试；深电路及其噪声敏感性使它不适合当前 NISQ hardware。[pdf:E01]（PDF 物理页 1，Introduction）

第二代是 VQLS-based QEMTP。VQLS 用 shallow variational circuit 表示候选电压状态，由量子侧评估 cost function、经典侧更新参数；其优点是 circuit width 随问题规模对数增长、深度较浅，并已有相关工作在 IBM real quantum hardware 上测试。代价是三个具体瓶颈：

1. 把 $N\times N$ 导纳矩阵直接投影到 $n=\lceil\log_2 N\rceil$ 个 qubits 的 Pauli basis，会生成数量巨大的 basis coefficient。论文举例称，1024 维矩阵虽只需 10 qubits，但 Pauli bases 超过 100 万，NumPy 映射超过 7 小时。[pdf:E05]（PDF 物理页 3，Eq. (8)–(10) 与 Remark 1）[pdf:E06]（PDF 物理页 4，Remark 1 续文）
2. 一次 VQLS cost evaluation 需要并行执行大量 Hadamard-test circuits；之后还要做 classical parameter optimization、state tomography 和 iterative error compensation。[pdf:E06]（PDF 物理页 4，Fig. 4、Eq. (11)–(16)）
3. 既有 QEMTP switching representation 会随开关状态改变导纳矩阵，因而不断重做 projection。作者指出先前 VQLS-QEMTP 案例主要是缺少 power-electronic switching device 的 IEEE networks，难以代表微秒以下开关 EMT。[pdf:E02]（PDF 物理页 2，challenge 3）

因此，论文真正补的不是“量子 EMT 从无到有”，而是既有 VQLS-QEMTP 的 matrix preprocessing、cost-circuit count 和 switching-topology interface。论文自己也明确说，提出的方法不加速完整 QEMTP workflow 的端到端执行，只缓解其中两类瓶颈。[pdf:E02]（PDF 物理页 2，contribution 后的限定）

## § 3 — 重建作者的思考路径

如果不预先知道论文的三项贡献，一个研究者可以沿下面的路径走到类似方案。

第一步，从经典 EMT 的数据结构出发。离散后的网络在每个时间步都落到 $\mathbf G\mathbf v=\mathbf i$；把它送进量子线性求解器前，需要扩充到 $2^n$ 维、归一化电流和电压向量，再形成 $\widetilde{\mathbf G}|v\rangle=|i\rangle$。[pdf:E03]（PDF 物理页 2，Eq. (1)–(2)）[pdf:E04]（PDF 物理页 3，Eq. (3)–(7)）

第二步，观察瓶颈不是 qubit count 本身，而是经典矩阵到 Pauli coefficients 的展开，以及随后按这些 coefficients 构造的 Hadamard tests。也就是说，“状态只需 $\log_2N$ 个 qubits”并不意味着数据装载和 operator construction 也是 logarithmic cost。[pdf:E05]（PDF 物理页 3，Admittance Matrix Projection）

第三步，从 EMT matrix 的结构而不是从通用量子算法入手。电力网络中有重复的串并联模块，导纳矩阵常呈实数、对称或近似结构化；Kronecker decomposition 可以把一个高维矩阵写成若干低维矩阵对的 tensor products。若先在低维因子上做 Pauli projection，再利用 tensor-product basis 重组，可能避免直接扫描全部高维 basis。

第四步，继续追问 Pauli basis 是否全部有效。对 real symmetric matrix，$\sigma_Y$ 是四个 Pauli matrices 中唯一的反对称、含虚数元素者；含奇数个 $\sigma_Y$ 的 tensor-product basis 与实对称矩阵的 inner product 为零。于是相应 imaginary-part circuits 可以直接删除，而不改变同一实对称问题的 projection。[pdf:E09]（PDF 物理页 6，Theorem 2 起始）[pdf:E10]（PDF 物理页 6，Eq. (25)–(30)）

第五步，处理 switching topology。若开关能用固定导纳和历史电流源表示，那么 ON/OFF 切换只更新 source/history term，不改 $\mathbf G$；同一个 quantum operator mapping 就可以跨开关事件复用。这条路径自然导向 FASM（fixed admittance switch model），但也把物理模型误差引入了核心链路。[pdf:E11]（PDF 物理页 7，Eq. (32)–(33)）[pdf:E12]（PDF 物理页 7，Fig. 6 与 Algorithm 1）

## § 4 — 核心 Intuition

MLQC 的核心直觉是：不要把整个高维导纳矩阵一次性投影到全部 Pauli bases，而要先把它分解成少量低维 Kronecker factors，在小矩阵上投影后再拼回完全相同的 operator。[pdf:E08]（PDF 物理页 5，Eq. (21)–(23)）如果导纳矩阵是 real symmetric，含奇数个 $\sigma_Y$ 的 basis coefficient 必为零，所以 corresponding quantum circuits 不必运行。[pdf:E09]（PDF 物理页 6，Theorem 2）最后，用 FASM 固定开关的导纳，把 topology event 变成 history-current update，就能复用已构造的 operator。[pdf:E11]（PDF 物理页 7，FASM）

## § 5 — 具体方法与完整 Pipeline

以论文的 Buck converter 为例，输入是 $50\ \mathrm V$ DC source、duty cycle 0.8 的一对交替开关和 RLC network；输出是每个 $25\ \mu\mathrm s$ 时间步的 inductor current、output voltage 和 switch voltage。[pdf:E14]（PDF 物理页 9，DC-DC parameter settings）

1. **经典 EMT 离散。** 把支路变成 Norton equivalents，建立节点方程 $\mathbf G\mathbf v(t)=\mathbf i(t)$。FASM 用固定 $Y_{\mathrm{sw}}$ 与随 ON/OFF 状态更新的 history-current source 表示开关，因此开关动作不再改写 $\mathbf G$。[pdf:E03]（PDF 物理页 2，Fig. 1 与 Eq. (1)）[pdf:E11]（PDF 物理页 7，Eq. (32)–(33)）
2. **量子维度对齐。** 若节点维数 $N$ 不是 $2^n$，在 $\mathbf G$ 右下角补 identity block，把电压、电流向量补零并归一化，得到 $\widetilde{\mathbf G}|v\rangle=|i\rangle$。[pdf:E04]（PDF 物理页 3，Eq. (3)–(6)）
3. **经典 MLQC preprocessing。** 用 generalized Kronecker decomposition 写成 $\widetilde{\mathbf G}=\sum_{r=1}^{R}\boldsymbol\Gamma_r\otimes\mathbf Z_r$；对 $\boldsymbol\Gamma_r$、$\mathbf Z_r$ 分别做低维 Pauli projection，再合并相同 high-dimensional basis 的 coefficients。[pdf:E07]（PDF 物理页 5，Eq. (17)–(20)）[pdf:E08]（PDF 物理页 5，Eq. (21)–(23)）
4. **real-only circuit pruning。** 若当前 $\widetilde{\mathbf G}$ 满足 real symmetric 条件，删除所有含奇数个 $\sigma_Y$ 的 basis term，并只计算 Hadamard test 的 real part。作者称这会在不损失该问题精度的前提下减少约一半 quantum circuits。[pdf:E10]（PDF 物理页 6，Quantum Circuit Reduction 与 Eq. (30)）
5. **每个时间步的 hybrid VQLS。** 经典侧根据外部注入与 history term 计算 $\mathbf i(t)$；概念上的 quantum side 准备 $|i\rangle$，运行 parameterized $R_y$ 与 controlled-Z ansatz 及 Hadamard-test circuits；经典 optimizer 更新 $\alpha$，直到 cost 收敛。[pdf:E05]（PDF 物理页 3，Fig. 2、Eq. (8)–(10)）[pdf:E06]（PDF 物理页 4，Eq. (11)–(13)）
6. **readout 与误差补偿。** 对 $|v\rangle$ 做 tomography，经典侧计算 residual；若超过阈值 $\epsilon$，再解 correction equation 并更新电压，随后推进 EMT history term 和下一个时间步。[pdf:E06]（PDF 物理页 4，Eq. (14)–(16)）完整顺序见 Algorithm 1。[pdf:E12]（PDF 物理页 7，Algorithm 1）

这条 pipeline 的实现位置必须明确区分：

| 环节 | 论文中的角色 | 本文实验实际执行 |
|---|---|---|
| EMT discretization、FASM、GKD/MLQC、Pauli coefficient generation | 经典预处理 | NumPy / SciPy / PyQPanda numerical environment |
| state preparation、ansatz、Hadamard tests、tomography | quantum-algorithm layer | statevector simulation，不是物理 quantum hardware |
| parameter optimization、residual correction、time marching | 经典控制与后处理 | classical numerical code |
| FPGA mapping、fixed-point datapath、on-chip memory、real-time I/O | 论文未定义 | 未报告，不能从 quantum circuit count 推导 |

上述实验边界由 Case Study 的软件环境和 statevector 声明直接确定。[pdf:E13]（PDF 物理页 8，Case Study）[pdf:E14]（PDF 物理页 9，DC-DC 与 AC-DC settings）

## § 6 — 核心数学推导

### 6.1 从 EMT 方程到 quantum linear system

经典 EMT 的 Eq. (1) 是 $\mathbf G\mathbf v=\mathbf i$。为了容纳 $n$-qubit Hilbert space，作者把 $N$ 维矩阵补成 $2^{\lceil\log_2N\rceil}$ 维：

$$
\widetilde{\mathbf G}=
\begin{bmatrix}
\mathbf G & \mathbf 0\\
\mathbf 0 & \mathbf I
\end{bmatrix},
\qquad
\hat{\mathbf v}=\begin{bmatrix}\mathbf v\\\mathbf0\end{bmatrix},
\qquad
\hat{\mathbf i}=\begin{bmatrix}\mathbf i\\\mathbf0\end{bmatrix}.
$$

归一化 $\hat{\mathbf v}$、$\hat{\mathbf i}$ 后得到 $\widetilde{\mathbf G}|v\rangle=|i\rangle$。这里的 intuition 是“让经典节点向量变成 quantum-state amplitude”，而不是改变 EMT 的物理方程。[pdf:E04]（PDF 物理页 3，Eq. (3)–(6)）

### 6.2 为什么直接 Pauli mapping 很贵

传统做法写成

$$
\widetilde{\mathbf G}=\sum_i c_i\mathbf g_i,\qquad
c_i=\frac{1}{2^n}\operatorname{Tr}(\widetilde{\mathbf G}\mathbf g_i),
$$

其中 $\mathbf g_i$ 遍历 $n$ 个 Pauli operators 的 tensor-product bases。高维 basis 数与逐项 trace 计算共同造成 preprocessing explosion；VQLS 再用这些 terms 构造 local cost function，并通过 Hadamard tests 求其期望值。[pdf:E05]（PDF 物理页 3，Eq. (8)–(10)）[pdf:E06]（PDF 物理页 4，Eq. (11)）

### 6.3 MLQC 为什么能降维且可保持 lossless

Naive Kronecker decomposition 只保留一个 $\mathbf B\otimes\mathbf C$，可能带来 approximation error。GKD 则取 rank-$R$ 展开

$$
\widetilde{\mathbf G}\approx\sum_{r=1}^{R}\mathbf B_r\otimes\mathbf C_r,
$$

并用重排矩阵的 singular values/vectors 构造每个 factor；当 $R$ 取允许的最大值时，这个展开等价于完整 SVD，论文据此称 decomposition 可 lossless。[pdf:E07]（PDF 物理页 5，Eq. (17)–(20)）

MLQC 再把每个低维 factor 分别展开为 Pauli bases：

$$
\boldsymbol\Gamma_r=\sum_i c_{ir}\boldsymbol\gamma_i,\qquad
\mathbf Z_r=\sum_j c_{jr}\boldsymbol\zeta_j,
$$

于是

$$
\widetilde{\mathbf G}
=\sum_{i,j}\sum_{r=1}^{R}c_{ir}c_{jr}
(\boldsymbol\gamma_i\otimes\boldsymbol\zeta_j)
=\sum_k c_k\mathbf g_k.
$$

由于 Pauli-space representation 唯一，只要 GKD 重建的矩阵与原矩阵相同，低维投影再合并与直接高维投影必须得到同一个 operator。[pdf:E08]（PDF 物理页 5，Eq. (21)–(23) 与 Theorem 1）作者给出的复杂度是：dense Pauli mapping 为 $O(N^4)$；MLQC 由 rank-$R$ SVD 和低维 projection 主导，为 $O(RN^2)$，因 $R\le N$，lossless worst case 为 $O(N^3)$；重复串并联结构若使 $R\ll N$，才会进一步受益。[pdf:E08]（PDF 物理页 5，Remark 2）[pdf:E09]（PDF 物理页 6，complexity conclusion）

### 6.4 real-only reduction 的成立条件

若 $\widetilde{\mathbf G}$ real symmetric，则 $\widetilde{\mathbf G}+\widetilde{\mathbf G}^T=2\widetilde{\mathbf G}$。$\sigma_I,\sigma_X,\sigma_Z$ 对称，而 $\sigma_Y+\sigma_Y^T=0$；因此任何含奇数个 $\sigma_Y$ 的 tensor-product basis 都是 antisymmetric，其与 real symmetric $\widetilde{\mathbf G}$ 的 projection coefficient 为零。[pdf:E09]（PDF 物理页 6，Theorem 2 与 Eq. (24)）[pdf:E10]（PDF 物理页 6，Eq. (25)–(29)）这允许删除对应 imaginary calculations，只保留 real Hadamard-test result。注意：这不是任意 EMT matrix 的无条件定理；一旦导纳矩阵非对称或含不可忽略的复数项，删项结论就不能直接使用。

### 6.5 FASM 如何固定导纳

FASM 把 switch 写成固定 $Y_{\mathrm{sw}}$ 与 history current source。ON/OFF 的差别进入

$$
I_{h-\mathrm{on}}(t)=\alpha_{\mathrm{on}}Y_{\mathrm{sw}}U(t-\Delta t)
+\beta_{\mathrm{on}}I(t-\Delta t),
$$

$$
I_{h-\mathrm{off}}(t)=\alpha_{\mathrm{off}}Y_{\mathrm{sw}}U(t-\Delta t)
+\beta_{\mathrm{off}}I(t-\Delta t),
$$

而不改变网络导纳 stamp。[pdf:E11]（PDF 物理页 7，Eq. (32)–(33)）这正是能够跨 switching event 复用 MLQC/Pauli mapping 的原因，但它也意味着 QEMTP 求解的是 FASM-defined network，而不是自动等价于 ideal/binary switch network。

## § 7 — 实验设计与结论

### 问题 1：MLQC 是否真的加速 Pauli mapping，同时保持矩阵重建精度？

**实验。** 对 $n=2,\ldots,10$、$N=4,\ldots,1024$ 的 random dense real symmetric matrices，设置 $R=N$ 避免利用低秩结构；$n\le8$ 重复 100 次，$n=9,10$ 重复 10 次。比较 MLQC 与 direct Pauli mapping 的 time 和 Frobenius reconstruction error。[pdf:E13]（PDF 物理页 8，Eq. (34)、Table I）

**答案。** $N=4$ 时 initialization overhead 使 MLQC 更慢；之后 speedup 随维数上升，在 $N=512$ 为 90.0524×、$N=1024$ 为 141.746×，reported mapping error 低于 $10^{-14}$。但 $R=1$ 时，9-qubit case 的 error 接近 0.5，说明速度来自 aggressive truncation 时会严重损失精度，论文后续实验因此使用最大 $R$。[pdf:E13]（PDF 物理页 8，Table I 与 Fig. 7）

### 问题 2：在 switching DC-DC EMT 中，MLQC-QEMTP 是否保持和原 VQLS-QEMTP 相近的数值结果？

**实验。** Buck case 使用 $50\ \mathrm V$、duty 0.8、$\epsilon=10^{-7}$、3 ansatz layers、random seed 42、CG stopping criterion $\mathrm{gtol}<10^{-5}$，statevector simulator，步长 $25\ \mu\mathrm s$。比较 classical EMTP、VQLS-QEMTP、MLQC-QEMTP 的 current/voltage waveforms 和相对误差。[pdf:E14]（PDF 物理页 9，DC-DC settings）[pdf:E15]（PDF 物理页 10，Fig. 8–9）

**答案。** 相对于 FASM-based EMTP benchmark，两种 quantum solver 的多数 relative error 约在 $10^{-9}$ 到 $10^{-10}$，论文未观察到 error accumulation；Table III 报告 DC-DC RMSE（$10^{-9}$ p.u.）为 VQLS 0.1177、MLQC 0.09987。[pdf:E14]（PDF 物理页 9，DC-DC results）[pdf:E15]（PDF 物理页 10，Table III）这里的 reference 是同一 FASM model，不是 binary-switch physical ground truth。

### 问题 3：在 switching AC-DC EMT 中，结果是否仍成立？

**实验。** three-phase full bridge 使用 $400\ \mathrm V$ RMS line voltage、4 mF DC-link capacitor、0.5 mH inductor、100 $\Omega$ load，并在 $t=0.02\ \mathrm s$ 阶跃到 50 $\Omega$；SPWM 为 2.5 kHz，EMT step 为 $10\ \mu\mathrm s$。VQLS 设置 $\epsilon_{\mathrm{set}}=10^{-10}$、5 ansatz layers、seed 42、$\mathrm{gtol}<10^{-7}$，仍由 statevector simulation 评估。[pdf:E14]（PDF 物理页 9，AC-DC settings）

**答案。** Fig. 11 的 capacitor voltage、inductor current 和 switch voltage 与另外两条曲线基本重合；作者报告 solver discrepancy 在 $10^{-7}$ 内且没有可观察 accumulation。Table III 报告 AC-DC RMSE（$10^{-9}$ p.u.）为 VQLS 8.9428、MLQC 4.8341。[pdf:E15]（PDF 物理页 10，Table III）[pdf:E17]（PDF 物理页 11，Fig. 11）这些结果证明的是 statevector VQLS 对同一 FASM equation 的数值一致性，不证明 real hardware execution，也不证明 FASM 对 switching transient 的物理误差同样小。

### 问题 4：结构化 EMT network 的 preprocessing 能否扩到更大维数？

**实验。** photovoltaic plant 由 10–70 个 series-connected three-phase bridge units 构成；每个 unit 使用 900 V DC side、0.5 $\Omega$、2500 Hz switching、8 mF、1 mH。对应 problem dimension 为 83–563、qubits 为 7–10。[pdf:E16]（PDF 物理页 10，Fig. 10 后的 network parameters）[pdf:E17]（PDF 物理页 11，Fig. 12）

**答案。** 该结构只需 rank 5–8，Table IV 报告 MLQC 相对 direct Pauli mapping 的 speedup 为 47.819×–87.946×，mapping error 仍在 $10^{-15}$ order。[pdf:E18]（PDF 物理页 12，Table IV）但这不是大系统 full QEMTP run：论文承认 10-converter case 已有 1193 Pauli terms，单次 cost evaluation 需 22,771,984 circuits，real-only 后仍需 11,385,992 circuits，超出当前资源。[pdf:E16]（PDF 物理页 10，benchmark limitation）

### 问题 5：端到端量子优势是否已经成立？

**答案是否定的。** 论文的 Discussion 指出，state preparation 一般为 $O(N)$（除非存在 efficient QRAM），完整 nodal-voltage readout 至少需要 $O(N/\epsilon_{\mathrm{tom}})$ samples，此外还有 variational optimization、repeated cost evaluation、correction、compilation、backend communication 和 classical postprocessing；其实现中超过 4 qubits 的 EMT network 已难以可靠模拟，cost-function sampling burden 仍为 $O(N^4)$。[pdf:E17]（PDF 物理页 11，Discussion）所以报告的 speedup 是 preprocessing 子阶段 speedup，不是 wall-clock end-to-end quantum advantage。

## § 8 — Take-aways

**5 句话：**

1. 论文把 VQLS-QEMTP 的高维 Pauli mapping 改写为低维 Kronecker factors 上的 mapping，并在 full-rank 条件下保持同一 operator。[pdf:E08]
2. 对 real symmetric admittance matrix，含奇数个 $\sigma_Y$ 的 Pauli bases 系数为零，因而可以删去相应 circuits。[pdf:E10]
3. FASM 固定开关导纳，使 switching event 不再触发 matrix reprojection，但也引入独立的 switching-model error。[pdf:E11] [pdf:E19]
4. statevector cases 支持 preprocessing acceleration 和同一 FASM equation 下的 solver accuracy，却没有验证 physical quantum hardware、end-to-end advantage 或 FPGA implementation。[pdf:E14] [pdf:E17]
5. 最大规模实验只完成 MLQC preprocessing benchmark；论文明确承认 full QEMTP 仍受数百万 circuits、state preparation、tomography 和 optimization 限制。[pdf:E16] [pdf:E17]

**3 句话：**

1. MLQC 的贡献是利用 EMT admittance matrix 的 Kronecker structure 来减少 operator construction，而不是让整个 EMT 仿真复杂度变成 logarithmic。
2. real-only reduction 与 FASM 分别依赖 real-symmetric matrix 和 fixed-admittance switch approximation，这两个成立条件比“量子求解器本身是否收敛”更值得优先核验。
3. 目前最稳妥的结论是：论文显著缓解了 VQLS-QEMTP 的两个前端瓶颈，并把 switching converter case 接入了 statevector validation；可扩展、实时、硬件化 QEMTP 仍未实现。

**1 句话：**

这是一篇针对 VQLS-QEMTP 数据准备与 circuit-count 瓶颈的结构化降维论文，不是一篇已经实现量子或 FPGA 实时 EMT 加速的系统论文。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**用 FASM 固定导纳以后，相对于同一 FASM-based EMTP benchmark 的极小 solver discrepancy，可以代表 high-frequency switching EMT 的有效精度。**

这实际上合并了两个不同误差源。主文的 $10^{-9}$–$10^{-7}$ 量级误差比较的是 VQLS/MLQC solver 与同一 FASM equations 的数值差；FASM 相对于 binary/ideal switch 的 modeling error 被单独放在 Appendix B。作者明确承认，固定导纳在 topology transition 时会产生 switching-instant local error，且这些误差是 model-induced，不属于主文报告的 quantum-solver discrepancy。[pdf:E14]（PDF 物理页 9，benchmark 定义）[pdf:E19]（PDF 物理页 12，Appendix B 与 Fig. 13）

这个假设可能在 hard switching、diode commutation、强寄生参数、弱阻尼或控制器对 switching spike 敏感时失效。Fig. 13 甚至显示原 FASM 在开关瞬间有明显偏差；cross-initialization 把 resulting model error 稳定在约 $10^{-5}$，但论文把它列为 future work，并未纳入主 QEMTP case。[pdf:E19]（PDF 物理页 12，Fig. 13 后正文）换言之，论文对“求解近似 FASM system”给了充分数值证据，却没有给出足够证据证明“该 FASM system 在所声称的高频 switching regime 始终保持可接受的 physical-model fidelity”。如果这个假设不成立，论文最吸引人的 switching-QEMTP claim 会退化为对一个固定导纳 surrogate 的高精度求解。

## § 10 — 最小复现实验

一周内最值得做的不是复刻全部 10-qubit benchmark，而是做一个**误差分层的 4-dimensional Buck reproduction**。

1. 从作者公开仓库取得 case code，固定论文参数：$V_{\mathrm{in}}=50\ \mathrm V$、duty 0.8、$\Delta t=25\ \mu\mathrm s$、3 ansatz layers、seed 42；同时实现 binary-switch classical EMTP 与 FASM-based classical EMTP。[pdf:E13]（PDF 物理页 8，repository 与软件版本）[pdf:E14]（PDF 物理页 9，DC-DC settings）
2. 对同一个 FASM $\mathbf G$，分别计算 direct Pauli mapping、full-rank MLQC mapping，并比较 $\|\widetilde{\mathbf G}-\widetilde{\mathbf G}_{\mathrm{MLQC}}\|_F/\|\widetilde{\mathbf G}\|_F$、coefficient equality、wall-clock preprocessing time。
3. 在 statevector VQLS 中同时运行 unpruned circuits 与 real-only circuits；比较每个 cost evaluation 的 circuit count、最终 residual、nodal voltage error。4-dimensional case 的论文预期是每次 cost function 节省 128 circuits。[pdf:E14]（PDF 物理页 9，Quantum Circuit Reduction）
4. 最关键的是分别报告三条误差：MLQC reconstruction error、VQLS solver error（相对同一 FASM linear system）、FASM modeling error（相对 binary-switch EMTP），并把 switching instants 单独放大。

支持核心 claim 的最低结果是：full-rank MLQC reconstruction 保持约 $10^{-14}$ 或更小；real-only 与 unpruned statevector solutions 在同一 FASM matrix 下无可辨别差异；circuit count 按论文减少；同时 FASM-to-binary error 在预先定义的 switching-window tolerance 内。只要 MLQC coefficients 不一致、real-only pruning 在非对称 matrix 下改变解，或 switching-window FASM error 明显主导总误差，就应视为对相应 claim 的反驳，而不是用全时域平均 RMSE 掩盖。

## § 11 — 最强反例设计

最强反例应直接攻击“高频 switching case 的高精度来自量子算法，而不是 reference model 被替换”这一点。构造一个带 diode reverse recovery、dead time、很小 snubber capacitance 和低阻尼支路的 full bridge，使 switching instant 对后续 controller state 或 peak current 有可观测影响；使用 event-resolved binary-switch EMT 作为独立 reference，再比较：

- binary-switch EMTP；
- 原始 FASM-based EMTP；
- FASM + cross-initialization；
- MLQC-QEMTP（仍求解 FASM equations）。

评价指标不能只用全时域 RMSE，而要包括 switching-window peak error、event timing error、energy imbalance、后续若干周期的 state deviation。若 MLQC-QEMTP 与 FASM benchmark 仍保持 $10^{-9}$ 级一致，而 FASM 与 binary reference 在上述指标上出现工程上不可接受的偏差，那么论文的 solver accuracy 仍然成立，但“适用于 high-frequency switching EMT network”的强解释被推翻。这个反例尤其有力，因为 Appendix B 已经承认 switching-instant error，并说明 cross-initialization 尚未进入当前 QEMTP。[pdf:E19]（PDF 物理页 12，Appendix B）

第二个应同时记录但不混入主反例的边界是 non-symmetric EMT matrix。加入受控源、非互易耦合或使 MNA operator 明显非对称的 converter/control interface，直接测量 odd-$\sigma_Y$ coefficients；若它们非零，real-only pruning 就不再由 Theorem 2 保证。[pdf:E09]（PDF 物理页 6，Theorem 2 的 real-symmetric 前提）这不会推翻 MLQC 本身，却会推翻“普遍减半 quantum circuits”的外推。

## § 12 — Follow-up Research Idea

在 quantum engineering 与 power-system EMT 交叉领域，高影响工作最终要同时回答三件事：是否保留 switching physics、是否给出端到端资源与时间、是否在可复核 hardware 或至少 noise-aware execution 上成立。本文已经把 preprocessing 降维做得很清楚，却尚未把 physical-model error、variational error、sampling/readout cost 和 wall-clock time放进同一验收问题。[pdf:E17]（PDF 物理页 11，Discussion）

**候选研究想法：error-budgeted event-stratified QEMTP。** 它不再把目标定义为“每个时间步都用同一个量子线性求解器”，而是把 EMT 分成 switching-event windows 与 smooth intervals：事件窗口用可验证的 classical event-resolved model，平稳区间才使用可复用的 MLQC quantum operator；一个 online error estimator 在 physical-model、Kronecker truncation、VQLS optimization、sampling/tomography 四层之间分配统一误差预算。

- **未满足需求。** 当前 tiny solver residual 不能说明 total EMT fidelity，而 full-state readout 和 repeated cost evaluations 又可能吞掉 preprocessing saving。
- **潜在价值。** 研究目标从“减少 Pauli mapping”改成“在给定 total waveform error 下最小化端到端 cost”，能让 quantum claim 与 EMT 工程验收处在同一坐标系。
- **可借鉴工具。** 可以借鉴 hybrid-systems event localization、a posteriori error estimation、multirate waveform relaxation，以及 randomized measurement/readout compression；这些方法分别对应事件边界、误差预算、跨时间尺度和 readout cost。
- **首个证伪实验。** 在前述 switching-stress benchmark 上固定相同 peak/event/waveform tolerance，比较 classical sparse EMTP、全 FASM-QEMTP 与 event-stratified QEMTP 的 end-to-end wall time、shots、tomography samples 和 total error。若事件窗口频繁到无法复用 operator，或 readout/optimization overhead 仍使总成本高于 classical baseline，这个想法就被证伪。
- **与本文的实质区别。** 本文优化固定 VQLS-QEMTP pipeline 的 preprocessing 和 circuit construction；这个方向改变问题定义，用“总误差约束下何时值得调用 quantum solver”替代“如何让每一步都进入 quantum solver”。

这只是由本文证据约束得到的候选方向；本卡未对全部相邻文献做系统检索，因此不声称 novelty。
