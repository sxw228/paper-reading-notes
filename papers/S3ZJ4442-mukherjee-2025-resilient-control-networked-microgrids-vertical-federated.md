# Resilient Control of Networked Microgrids Using Vertical Federated Reinforcement Learning: Designs and Real-Time Test-Bed Validations

- 作者：Sayak Mukherjee；Ramij Raja Hossain；Sheik M. Mohiuddin；Yuan Liu；Wei Du；Veronica Adetola；Rohit A. Jinsiwale；Qiuhua Huang；Tianzhixi Yin；Ankit Singhal
- 出处：IEEE Transactions on Smart Grid，Vol. 16，No. 2，pp. 1897–1910
- 年份：2025
- DOI：10.1109/TSG.2024.3466768
- Zotero key：S3ZJ4442
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 论文要解决的不是一般的微电网能量管理，而是一个更具体的闭环安全问题：在多个微电网相互电气耦合、GFM（grid-forming）逆变器模型不完全可知、不同微电网又不愿共享原始运行数据时，如何增加一个上层 resilient control，使遭到恶意篡改的 GFM 有功或电压 set-point 不再把整个网络化微电网拖出可接受运行范围。作者把问题凝结为两个问题：一是未知模型和不确定性下的高层控制如何保持有效，二是在有限数据共享下如何仍然学习到跨微电网的耦合动态；这两个问题见 PDF 物理页 2、Section I-A。[pdf:E02]

重要性来自攻击入口与物理闭环的直接连接。GFM 的 set-point 进入一次控制；如果攻击者改变该信号，扰动不是停留在信息层，而会直接改变逆变器电压、频率和功率响应。作者因此在既有一次/二次控制之上叠加补偿量 \(P_i^{res}\) 或 \(V_i^{res}\)，试图把被攻击的 set-point 拉回到可用区间；问题定义和 Eq. (4)–(7) 位于 PDF 物理页 3–4。[pdf:E03] [pdf:E04]

这项工作的工程价值有三层。第一，它不要求 resilient controller 知道完整的逆变器和网络模型。第二，它让每个微电网保留本地原始测量，只交换 critic 神经网络参数。第三，它把在 GridLAB-D/HELICS phasor-domain 环境中训练的 policy 搬到 Hypersim 实时 EMT/HIL 环境中检验，而不是只报告训练曲线。摘要对 FedSAC、三个耦合微电网和实时 test-bed 的总体 claim 位于 PDF 物理页 1。[pdf:E01]

## § 2 — 前人工作与不足

**论文对相关工作的归纳。** 在控制侧，既有工作已经覆盖 GFM 一次控制、集中式或分布式二次控制，以及网络化微电网中的 energy management、economic dispatch 和 frequency control；在学习侧，单 agent RL、MARL 和安全 RL 已用于多类电力系统控制问题。尤其是 Wang 与 Pal 的工作 [35] 已研究针对 IBR droop gain 的 destabilizing attack 及 RL defense，但作者认为它没有处理多所有者网络化微电网中的数据隐私。与此同时，Fed-RL 已被用于配电网 volt-var control、风电预测、smart-home energy management、能源/碳交易和多微电网管理，但尚处早期阶段。以上是作者在 PDF 物理页 2、Section I-A 的文献定位，并非本卡独立完成的全领域 novelty 检索。[pdf:E02]

真正的缺口不是“以前没人用 RL”，而是三个约束同时出现：模型可能被 OEM 隐藏或受运行不确定性影响；微电网之间存在动态电气耦合，因此完全独立训练可能损失协同性；多方所有权又使集中收集原始电压数据不可接受。集中式学习能看到全局但要汇集数据，完全 decentralized SAC 不共享原始数据却各自只看本地，普通 MARL 也不自动给出隐私边界。作者选择 vertical Fed-RL，正是为了让 critic 参数承担跨区域信息融合，而 actor 与原始 measurement 留在本地。论文对集中、分散与 federated 数据流的讨论位于 PDF 物理页 5，Section II-C.2。[pdf:E05]

仍需保留两个边界。其一，论文所谓 privacy 主要是“raw data 不上传”，没有给出 differential privacy、参数反演攻击或信息泄漏的定量实验；作者只说还可以另加 encryption/privacy-preserving techniques。其二，论文把本工作描述为其 2023 conference paper [47] 的扩展，主要新增更现实的系统模型和实时 HIL 检验；因此不应把所有组成部分都单独宣称为首次提出。[pdf:E02] [pdf:E07]

## § 3 — 重建作者的思考路径

以下是**基于证据的逆向重建**，不是作者逐字给出的研发日记。

1. 已知网络化微电网采用层级控制，GFM set-point 是高层调度/二次控制与设备一次控制之间的关键接口；如果该接口被篡改，后果会进入物理动态，而不是只产生错误报文。[pdf:E03] [pdf:E04]
2. 若精确模型可得，可以尝试 observer、robust control 或 model-based compensation；但实际存在 OEM 模型遮蔽、复杂耦合和运行不确定性，因此先把 resilient controller 写成只依赖观测的反馈 \(u^{res}=f_\theta(O)\)，并用 RL 从交互中学习。[pdf:E04]
3. 单个全局 RL controller 虽容易利用全网数据，却破坏多所有者的数据边界；每个微电网完全独立训练虽不传数据，却无法显式吸收其他微电网经 tie-line 施加的影响。[pdf:E05] [pdf:E06]
4. actor 只负责本区域连续 set-point correction，而 critic 评价长期回报。由此可以把原始 measurement 与 actor 留在本地，只把 critic 参数送到 coordinator 做 FedAvg，再把聚合后的 critic 发回各微电网。这样，actor 的梯度间接含有其他区域 critic 的信息，同时不上传本地电压轨迹。[pdf:E07]
5. phasor-domain 环境训练快但不含高频开关和快速 EMT 细节，所以最后必须把同一 policy 放入更高保真的实时 Hypersim 环境，检查它是否仍能在模型分辨率变化后压住电压扰动。[pdf:E10] [pdf:E11]

这条路径的关键转折是：不把“隐私”和“耦合”当成只能二选一的系统架构问题，而把跨区耦合信息压缩进共享的 critic 参数。不过，这只是架构性隐私，不等于已经证明参数不可泄漏本地信息。

## § 4 — 核心 Intuition

每个微电网只用自己的电压测量训练本地 actor–critic，但把 critic 参数交给中央 coordinator 平均，再用返回的聚合 critic 更新本地 actor；critic 因而成为跨微电网耦合信息的载体，而原始运行轨迹不必离开本地。[pdf:E07] 被攻击的 GFM set-point 再叠加 actor 给出的连续补偿量，使 policy 学到“何时不动作、攻击后如何把端电压拉回稳态附近”。[pdf:E04] 最后用归一化缓和不同微电网之间、以及 GridLAB-D 与 Hypersim 之间的状态尺度差异，支持 phasor-domain 训练到实时 EMT 仿真的迁移。[pdf:E07] [pdf:E12]

## § 5 — 具体方法与完整 Pipeline

以“三个微电网中的 GFM 51、105、80 可能遭到电压 set-point 攻击”为例，完整 pipeline 如下。

1. **被控对象与攻击注入。** 每个微电网包含 GFM、GFL 和 diesel generator，并通过 tie-line 耦合。正常 GFM 采用 \(P-f\) 与 \(Q-V\) droop；攻击把 \(P_i^{attack}\) 或 \(V_i^{attack}\) 加到基础 set-point，resilient layer 再加 \(P_i^{res}\) 或 \(V_i^{res}\)。论文实际实验聚焦 voltage set-point attack，actor action 是相应 GFM 的 \(V_i^{res}\)。模型与 Eq. (1)–(7) 位于 PDF 物理页 3–4。[pdf:E03] [pdf:E04]
2. **本地 observation、action 与 reward。** 第 \(k\) 个微电网只观察本地 GFM 与 GFL bus 的三相端电压 \(o_k\)，连续 action 是本地 GFM voltage set-point correction。攻击前乱动作会受罚；攻击后 reward 惩罚当前电压偏离攻击前稳态值。控制器把电网当作 POMDP，不使用文中列出的 GFM 动态方程进行在线模型求解。[pdf:E04]
3. **ResRLCoSIM 采样。** GridLAB-D 负责 distribution-grid phasor-domain dynamics，HELICS 负责 co-simulation communication，OpenAI Gym 风格的 `reset()` 和 `step()` 产生攻击场景下的 observation、action、reward 和 next observation。训练轨迹留在各本地 replay buffer。[pdf:E05] 图 1(a) 的完整交互结构位于 PDF 物理页 6。[pdf:E06]
4. **本地 SAC 更新。** 每个微电网各有一个 stochastic actor \(\pi_{\theta_k}\)、两个 critic \(Q_{\phi_k^1},Q_{\phi_k^2}\)、对应 target critic 和本地 replay buffer。SAC 用 entropy regularization 在期望回报与探索随机性间折中。[pdf:E07] [pdf:E08]
5. **vertical federation。** 到 federated update step 时，各区域只上传 critic 和 target-critic 参数；coordinator 对每一组参数做 FedAvg，再把聚合参数下发并覆盖各本地 critic。随后，各 actor 用本地 observation/action 和更新后的 critic 做 policy update。原始电压轨迹不上传，但论文没有对 critic 参数泄漏做 formal privacy guarantee。[pdf:E07] [pdf:E08]
6. **为可训练性做的两个特殊处理。** 不同微电网的稳态电压分布不同，作者先以各自稳态电压做逐相归一化。标准 SAC 的 Clipped Double Q 在作者的 federated averaging 后期会使 actor training 不稳定，因此只在前半段 iteration 使用，后半段选择一个 critic/target pair 继续 federation 与 actor–critic update。[pdf:E07] [pdf:E08]
7. **sim-to-real transfer。** 训练完成后，actor policy 被导入 Python；Python 通过 UDP 接收 Hypersim measurement、计算 correction，再回写 Hypersim set-point。IEEE 123-node 网络、generator、GFM/GFL inverter、load 及其 controller 都建模在 Hypersim 中，Hypersim 以 50 µs time step 做实时 EMT 仿真。[pdf:E06] [pdf:E11]

**EMT/FPGA 边界。** 这篇论文报告的是 GridLAB-D/HELICS phasor-domain 训练，以及 OPAL-RT Hypersim 上的实时 EMT/HIL test-bed 验证。文中没有 FPGA RTL/HLS 映射、fixed-point 格式、resource utilization、pipeline latency 或 timing closure；50 µs 是 Hypersim 仿真步长，不是已证明的 FPGA controller deadline。文中描述的电网、逆变器和负荷仍是 Hypersim 模型，因此结果不能外推为现场物理微电网部署。[pdf:E10] [pdf:E11]

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有稳定性 theorem 或闭环收敛证明；数学部分主要是把 set-point attack 写成 POMDP control，并给出 FedSAC 更新。下面按工程含义解释。

**1. GFM 与 droop。** 作者用内部相角和电压表示第 \(i\) 个 GFM：

\[
\dot{\delta}_i=u_i^\delta,\qquad E_i=u_i^V .
\]

一次控制为

\[
\omega_i^{ref}=\omega_i^{nom}-m_{P_i}(P_i-P_i^{set}),\qquad
V_i^{ref}=V_i^{set}-m_{Q_i}(Q_i-Q_i^{nom}).
\]

直观上，\(P-f\) droop 用有功偏差改变 frequency reference，\(Q-V\) droop 用无功偏差改变 voltage reference。论文强调这些方程用于仿真对象，而不是被 resilient controller 当作已知模型；Eq. (1)–(3) 及变量解释位于 PDF 物理页 3。[pdf:E03]

**2. 攻击与补偿。** 被篡改后的 set-point 再叠加 resilient action：

\[
P_i^{set}=P_{i-base}^{set}+P_i^{attack}+P_i^{res},\qquad
V_i^{set}=V_{i-base}^{set}+V_i^{attack}+V_i^{res}.
\]

如果 actor 能给出与攻击影响相抵的 \(V_i^{res}\)，终端电压就可返回攻击前稳态附近。这里不是要求精确估计 \(V_i^{attack}\)，而是直接以测得电压闭环学习补偿。Eq. (4)–(7) 位于 PDF 物理页 3–4。[pdf:E03] [pdf:E04]

**3. POMDP 与 reward。** resilient action 写成 \(u^{res}=f_\theta(O)\)。对 voltage set-point attack，作者采用

\[
r_t=
\begin{cases}
-c\,u_{ivld}, & t\le t_a,\\
-\displaystyle\sum_i Q_i\lVert V_i(t)-V_{i,ss}\rVert_2, & \text{otherwise}.
\end{cases}
\]

\(t_a\) 是攻击时刻，\(u_{ivld}\) 是未发生攻击时仍动作的 penalty，\(V_{i,ss}\) 是攻击前稳态电压，\(Q_i\) 与 \(c\) 是权重。第一项让 policy 学会攻击前不乱补偿，第二项让攻击后电压靠近原稳态。注意此处作者又用 \(Q_i\) 表示 reward weight，与 droop 方程中的 reactive power 记号重名；复现时应显式改名。Eq. (8) 和解释位于 PDF 物理页 4–5。[pdf:E04] [pdf:E05]

**4. SAC target 与 federated averaging。** 对本地 transition，FedSAC 的 soft target 为

\[
y_k=r_k+\gamma(1-d_k)\left[
\min_{i=1,2}Q_{\phi_k^{tar,i}}(o'_k,\tilde u_k^{res})
-\zeta\log\pi^k(\tilde u_k^{res}\mid o'_k)
\right].
\]

critic 拟合 \(y_k\)，actor 则选择能提高 critic value 且保持适度 entropy 的 action。到 federated step 时，

\[
\phi_{fed}^{i}=\frac{1}{m}\sum_{k=1}^{m}\phi_k^{i},\qquad
\phi_{fed}^{tar,i}=\frac{1}{m}\sum_{k=1}^{m}\phi_k^{tar,i},
\]

随后每个本地 critic 都替换为聚合参数。Algorithm 2 的 target、critic/policy update、target soft update 与 FedAvg 位于 PDF 物理页 8。[pdf:E08]

**复现歧义。** Algorithm 2 初始化时明确 policy 参数是 \(\theta_k\)、critic 参数是 \(\phi_k\)，但 policy-update 行的梯度下标排版成了 \(\phi\)；Algorithm 1 也出现 actor 记号不一致。按标准 SAC 机制，actor 应对 \(\theta_k\) 求梯度。这个记号问题不改变作者文字描述，却会影响照抄伪代码的复现。[pdf:E07] [pdf:E08]

## § 7 — 实验设计与结论

**问题 1：FedSAC 是否比不共享信息的 decentralized SAC 更能利用耦合？ → 实验。** 修改后的 IEEE 123-bus 系统由三个 tie-line 耦合微电网组成；每个微电网有 1 台 600 kW GFM、1 台 350 kW GFL 和 1 台 600 kVA diesel generator，总 peak load 为 3500 kW，frequency droop 为 1%，voltage droop 为 5%。GFM 位于 bus 51、105、80，GFL 位于 bus 42、101、76；每个 agent 的 observation 维数是 \(3\times2=6\)，action 是一个 GFM voltage set-point。训练使用 7 类 attack scenario，每 episode 40 个 time step；两层网络各 64 个 neuron，ReLU，learning rate 0.0003，buffer \(10^6\)，batch size 256，\(\rho=0.005\)，\(\gamma=0.99\)。这些设置位于 PDF 物理页 8、Section V。[pdf:E08] **→ 答案。** Fig. 3(b) 中 FedSAC 的 total episodic reward 高于 decentralized SAC。四个额外 test case 的 episodic reward 分别为 FedSAC \(-286.22,-298.25,-369.71,-285.44\)，decentralized SAC \(-583.60,-450.13,-698.83,-546.87\)；reward 越不负越好。Table I 位于 PDF 物理页 10。[pdf:E09] [pdf:E10]

**问题 2：policy 能否压住训练外的 set-point attack？ → 实验。** 作者先画出两个互补的大扰动 scenario：Scenario 1 使电压向上偏离，Scenario 2 使其向下偏离；分别观察三个 GFM 和三个 GFL terminal voltage。随后又测试 300 个未用于训练的 adversarial attack scenario，并统计三个 agent 的 reward histogram。Fig. 3–7 位于 PDF 物理页 9–10。[pdf:E09] [pdf:E10] **→ 答案。** 在展示的两个 scenario 中，无 resilient control 的曲线越过图中的虚线 tolerance，而红色 control curve 回到界内；300 个 scenario 的 histogram 更集中在高 reward 区。但论文没有给出 300 次测试的逐次成功率、置信区间或 worst-case voltage deviation，因此可以说“展示出较好的分布外场景恢复”，不能说已覆盖任意攻击。

**问题 3：phasor-domain 训练的 policy 到实时 EMT/HIL 后是否仍工作？ → 实验。** 作者把同一 policy 接入 Python–Hypersim UDP co-simulation，Hypersim 以 50 µs step 实时运行。GFM set-point 在 20 s、70 s 和 120 s 被依次改到不同水平；一组 scenario 攻击 GFM 51 与 105，另一组同时攻击 GFM 51、105、80。离线训练只使用单次类型的 perturbation，而 HIL 测试采用连续 sudden perturbation。Fig. 8 与对应文字位于 PDF 物理页 11。[pdf:E11] **→ 答案。** 图中无 RL 时，多 GFM 在 70–120 s 同时降 set-point 的情形会出现失稳或很大的 transient；接入 RL 后 GFM/GFL 电压最终被约束并拉回目标区域。作者据此认为 normalization/scaling 缓和了 GridLAB-D 与 Hypersim 的差异。[pdf:E11] [pdf:E12]

**问题 4：是否证明了隐私？ → 实验。** 论文展示的证据是架构数据流：本地原始电压不上传，上传的是 critic 参数。[pdf:E05] [pdf:E07] **→ 答案。** 这足以证明实现避免了集中汇集 raw measurement，但没有针对 membership inference、gradient/model inversion、通信窃听或 differential privacy budget 的实验，所以“privacy preserving”只能按 raw-data-sharing 边界理解。

**不得外推的范围。** 实时 test-bed 是 OPAL-RT Hypersim 上的 EMT/HIL simulation，不是现场设备部署；论文未报告 FPGA、fixed-point、计算资源、controller inference worst-case latency，也未系统 sweep communication loss/delay。因而实验支持的是“在作者所建的实时仿真 test-bed 和所测攻击中有效”，而不是“已证明任意实时网络和任意攻击下安全”。[pdf:E11] [pdf:E12]

## § 8 — Take-aways

**5 句话**

1. 论文把网络化微电网的 GFM set-point attack 写成一个只依赖本地端电压的 model-free 补偿问题。[pdf:E04]
2. vertical FedSAC 的核心不是共享 trajectory，而是 federated averaging 各区域 critic 参数，再用聚合 critic 更新本地 actor。[pdf:E07] [pdf:E08]
3. 在修改后的 IEEE 123-bus 三微电网系统中，FedSAC 的训练和四个 test-case reward 均优于完全 decentralized SAC。[pdf:E09] [pdf:E10]
4. 从 GridLAB-D/HELICS 训练迁移到 50 µs Hypersim 实时 EMT/HIL 后，policy 在文中连续 set-point perturbation 下仍能把电压约束回来。[pdf:E11]
5. 证据尚未覆盖快速自适应攻击、通信损失、formal privacy leakage、现场硬件或 FPGA 实现，因此“resilient”“private”“sim-to-real”都必须限定在论文实测范围内。[pdf:E04] [pdf:E12]

**3 句话**

1. 作者用本地 actor–critic 加全局 critic averaging，在不上传原始电压轨迹的前提下吸收耦合微电网的信息。[pdf:E07]
2. simulation 与实时 EMT/HIL 的曲线和 reward 支持该机制在所测 set-point attack 下有效。[pdf:E10] [pdf:E11]
3. 最危险的开放问题是攻击速度一旦接近控制回路更新速度，论文自己承认的可行性前提就会失效。[pdf:E04]

**1 句话**

这篇论文证明了 vertical FedSAC 是网络化微电网 set-point attack 防御的一条有实时 EMT/HIL 证据的可行路线，但没有给出超出其攻击时标和数据共享边界的安全保证。[pdf:E04] [pdf:E11]

## § 9 — 最脆弱的假设

最脆弱的假设是：**攻击幅值处于可补偿的 feasible limits 内，而且攻击者改变 set-point 的时标比系统 transient evolution 和防御回路慢。** 作者明确写道，若 attack signal 未按 nominal set-point 合理缩放，系统会立即 collapse、control 不足；若攻击者能在与 transient evolution 相同的时标改变 set-point，防御端理想上必须知道攻击者的精确动作，而这在作者看来不可行。该假设及理由位于 PDF 物理页 4、Eq. (6)–(7) 后。[pdf:E04]

这不是外围假设，而是整个反馈机制的可辨识性前提。actor 只看端电压，没有直接观察 \(V_i^{attack}\)；如果攻击在两次 measurement/action 之间反复换向，policy 看到的是滞后结果，输出 correction 时攻击已经改变，补偿就可能从负反馈变成相位滞后的正反馈。更严重的是，所有 GFM 同时受攻击时，耦合会把局部滞后放大成全网 transient。

论文提供的证据是若干随机攻击、300 个 held-out scenario 和 Hypersim 中 20/70/120 s 的 sequential step perturbation；这些都说明较慢、分段恒定的攻击可以恢复。[pdf:E09] [pdf:E11] 论文没有报告 attack-rate sweep、measurement-to-action latency、UDP packet loss/delay、time synchronization error 或接近控制带宽的 adaptive attacker。因此，最关键的适用包络仍未知；一旦该假设不成立，核心“resilient control”claim 会直接失效，而不仅是 reward 略有下降。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 HIL，而是一个更窄、可证伪的 claim：**critic FedAvg 是否真的在耦合微电网中优于三个独立 SAC，且优势不是单一 seed 或 reward scaling 造成的。**

1. 使用修改后的 IEEE 123-bus 三微电网模型；若作者模型不可得，则用公开 IEEE 123-bus 拆成三个 tie-line 耦合区域，明确标注这是结构近似而非逐字复现。每个区域保留 1 个 GFM、1 个 GFL、1 个 generator，本地 observation 取两个 inverter bus 的三相电压，action 取 GFM voltage set-point correction。论文的设备、bus 和 state/action 配置见 PDF 物理页 8。[pdf:E08]
2. 实现两组算法：A 为三个独立 Stable-Baselines3 SAC；B 使用相同 actor、critic、buffer 和 sample，仅每 10 step 平均 critic/target-critic 参数，且 100 step 后才开始 federation。其他超参数固定为论文报告值，并至少跑 5 个 seed。federation schedule 与训练说明位于 PDF 物理页 9。[pdf:E09]
3. 训练集用 7 类单 GFM voltage set-point attack、每 episode 40 step；测试集生成 300 个未见 attack，固定相同的 attack sample 给 A/B。除 episodic reward 外，额外记录最大电压偏差、恢复时间和积分绝对偏差，避免 reward definition 掩盖物理失败。[pdf:E08] [pdf:E09]
4. **支持 claim 的判据：** B 在 held-out attacks 上的 median reward、最大电压偏差和恢复时间都稳定优于 A，且 seed bootstrap interval 不跨越零差异。**反驳 claim 的判据：** 优势在控制 seed、normalization 和 sample budget 后消失，或 B 的平均 reward 提升却出现更差的 worst-case voltage excursion。

该最小实验只能验证“federated critic 对协调有增益”，不能验证 50 µs 实时执行、EMT fidelity、formal privacy 或 FPGA 可实现性。

## § 11 — 最强反例设计

最强反例应直接攻击第 9 节的时标假设，而不是再增加一个随机 step attack。保持 attack amplitude 在论文所谓 feasible range 内、总注入能量相同，只扫描 attack period 与 controller measurement/action update period 的比值：从远慢于控制回路，逐步提高到相当于一次 update，再到两次 update 之间可换向。攻击三台 GFM 的 voltage set-point，并让符号按当前 correction 反向选择，使攻击者始终最大化下一步电压偏差。这样排除了“只是攻击更大”的替代解释，单独检验 policy 对攻击速度和相位的脆弱性。论文承认同 transient timescale 的攻击会使防御不可行，这一前提位于 PDF 物理页 4。[pdf:E04]

在同一 50 µs Hypersim EMT model 上记录四个量：maximum voltage excursion、超限持续时间、是否失稳、RL action 与 attack 的相位差；慢速 step attack 作为正对照，原文 Fig. 8 的 20/70/120 s scenario 作为基线。[pdf:E11] 如果存在一个幅值并不更大、仅时标更快的 attack，使接入 RL 的系统比无 RL 或固定安全 limiter 更早失稳，就说明 FedSAC 学到的是训练分布下的 disturbance rejection，而不是可推广的 cyber resilience。反之，若在完整 rate sweep 中仍保持 bounded voltage，才真正补强论文的核心 claim。

## § 12 — Follow-up Research Idea

**候选判断，不声称 novelty。** 在电力系统控制领域，高影响工作通常不只看平均 reward，还看物理安全边界、跨工况鲁棒性、可复现实验和 EMT/real-time validation。基于第 9 节，值得改变的问题定义为：不再问“policy 在若干攻击下能否恢复”，而是求一个**可认证的攻击速率–通信时延–可补偿幅值韧性包络**，并让 federated policy 只在该包络内承担性能优化。

- **(a) 未满足需求。** 运营者需要知道 controller 在什么攻击变化率、measurement delay 和 set-point magnitude 下仍保证 voltage bounded，而不是只知道 300 个 sampled scenario 的 reward 较好。论文已证明 sampled attack 和实时 EMT test-bed 的可行性，却没有给出这条边界。[pdf:E09] [pdf:E11]
- **(b) 研究价值。** 一个明确的 region of validity 可以直接用于上线许可、fallback 触发和 cyber-resilience test specification；它把 empirical success 转化为可审计的工程承诺。
- **(c) 相邻方法。** 可借鉴 robust control 的 input-to-state safety、reachability/viability analysis，以及 adversarial system identification：先从 EMT roll-out 识别 conservative local dynamics envelope，再在各微电网本地计算 reachable set，只联合共享压缩后的安全约束或 certificate parameter，而不是原始 trajectory。
- **(d) 第一个证伪实验。** 在实时 Hypersim 中对 attack rate、delay 和幅值做网格 sweep；只要在宣称的 certificate envelope 内出现一次未预测的 voltage-bound violation，想法就被证伪。反过来，包络外失败不能算反例，因为边界已事先声明。
- **(e) 与本文的实质区别。** 本文优化期望 discounted reward，并以 sampled attack 和曲线说明恢复；新问题的输出是一个最坏情形安全包络和明确 fallback 条件，研究目标从“经验上恢复得好”改成“事先知道何时还能安全”。本文自己把快速攻击列为不可行边界，且 sim-to-real 讨论承认模型与时标差异，因此这个方向直接针对现有 claim 最薄弱处。[pdf:E04] [pdf:E12]

在没有对 safe federated RL、reachability-based microgrid defense 和 attack-rate certification 做系统全文检索前，这只能称为候选研究方向，不能宣称新颖性。
