# A Generic Modeling Approach for Dual-Active-Bridge Converter Family via Topology Transferrable Networks

**作者：** Xinze Li, Fanfan Lin, Changjiang Sun, Xin Zhang, Hao Ma, Changyun Wen, Frede Blaabjerg, Homer Alan Mantooth  
**出处：** IEEE Transactions on Industrial Electronics, 72(2), 1524–1536, 2025  
**DOI：** 10.1109/TIE.2024.3406858  
**Zotero：** RI6H4AE3

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把某一个 DAB 拟合得更准”，而是一个更难的模型复用问题：一个模型在单电感、非谐振 DAB 上训练后，能否不采集新拓扑的数据、不重新训练，就迁移到串联 LC 谐振 DAB、三电平 NPC-DAB 和三端口 DAB？作者把这种能力称为 topology transfer，并提出 topology-transferrable physics-in-architecture mixture density network，简称 T²PA-MDN。论文摘要明确声称，模型只用源域的 5 条训练时序，然后零训练迁移到三类目标拓扑，并用 2 kW 硬件实验验证其中一部分工况。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题之所以重要，是因为功率变换器模型通常处在三难选择中。白盒模型能解释电路，但参数漂移、寄生参数和实际开关波形会造成 model discrepancy；黑盒模型可以拟合这些误差，却依赖大量覆盖充分的数据；常见灰盒模型把物理定律写进 loss，仍可能在换拓扑时重新采数和训练。论文把这些矛盾归结为两个工程瓶颈：一是物理一致性没有直接锁进模型结构，二是模型没有把“拓扑变化”和“随机波动”分开处理。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 1）

对 EMT 与实时仿真而言，这一问题还有一层直接含义：如果状态更新本身就是可执行的离散电路方程，那么它比任意时序网络更容易解释数值稳定性、状态依赖和每步计算量。论文没有实现 FPGA，也没有报告固定步长实时运行、定点位宽、资源占用或时序收敛；因此它对 FPGA 的价值目前是“结构上值得映射”，不是“已经证明可实时部署”。

## § 2 — 前人工作与不足

论文把已有路线分成三类。第一类是白盒模型，例如 generalized state-space averaging、降阶一阶 DAB 模型和包含开关状态转移的离散模型。它们的优点是 KCL/KVL 和元件关系明确，缺点是实际参数、寄生效应和环境噪声没有被完整建模时，解析结果与硬件存在系统偏差。[pdf:E02]（PDF 物理页 2，Introduction）

第二类是黑盒或纯数据驱动时序模型。它们能用可调参数吸收难以显式写出的行为，但性能依赖数据分布；换工况或换拓扑后，训练集没有覆盖的新模式就会成为 out-of-domain 输入。第三类是已有灰盒或 physics-informed 方法，例如用解析导纳塑造阻抗识别网络、用 Hammerstein 结构描述无线电能传输系统，以及把物理约束加进 loss 的 physics-in-loss 网络。论文指出，这些方法往往绑定具体拓扑或控制框图；物理只通过训练目标间接起作用时，既不能保证每一步都满足电路关系，也不能消除目标域再训练。[pdf:E02]（PDF 物理页 2，相关工作与挑战总结）

作者真正要超越的不是某一个 baseline，而是“模型结构与拓扑无关、所有差异都交给数据学习”这一默认前提。其替代方案是让网络结构跟随电路结构变化：增加电容就增加电容状态和对应支路，增加端口就增加支路电流和绕组约束；数据只负责识别参数和描述剩余波动。[pdf:E03]（PDF 物理页 3，Fig. 2 与贡献列表）

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为四步。

第一步，从 DAB 的高频交流侧出发。无论外部端口和调制怎样变化，关键行为仍由电感电流、电容电压、桥臂开关函数和变压器约束支配。单电感 DAB、串联 LC、NPC-DAB 和三端口 DAB 并不是四个完全无关的对象，而是共享一批物理元件关系、同时增加或删除局部状态的 topology family。[pdf:E03]（PDF 物理页 3，Section II-A 与 Fig. 2）

第二步，把连续状态方程改写成可递归执行的离散更新。普通 RNN 的隐藏状态没有固定物理意义；如果用 Euler 离散后的电路更新式直接构成 recurrent cell，隐藏状态就分别对应电感电流、电容电压等真实量，网络连接也对应电路依赖。[pdf:E04]（PDF 物理页 4，Section III-B、Eq. (1)–(2)）

第三步，把误差拆成两层。T²PA 先承担可解释、确定性的电路动力学，并通过少量源域数据识别 \(L\)、\(R\)、变比等参数；MDN 再对 T²PA 的残差拟合 Gaussian mixture，用概率分布而不是单一误差带描述波动。[pdf:E05]（PDF 物理页 5，Section III-C、Eq. (7)–(8)）

第四步，把迁移定义为“重新编译物理结构”，而不是“让一个固定网络猜新拓扑”。目标拓扑先推导状态空间方程，再离散化，最后修改 expert system 的开关函数和 T²PA 的状态、连接及输入。这个过程仍需要工程师知道目标电路；所谓 zero-data 指不使用目标域训练数据，并不表示不需要目标拓扑模型。[pdf:E06]（PDF 物理页 6，Section III-D 的三步迁移过程）

## § 4 — 核心 Intuition

T²PA-MDN 的核心直觉是：不要让神经网络重新发现 Kirchhoff 定律，而是把离散电路方程直接做成网络骨架，只让数据校准骨架中的物理参数。换拓扑时，像修改电路图一样增删状态支路；无法由该骨架解释的随机残差，再交给 MDN 形成概率分布。[pdf:E04] [pdf:E05]

因此，这里的“可迁移”不是固定权重对任意拓扑的抽象泛化，而是共享元件级计算规律、显式重构目标拓扑，再复用已经学到的参数化与残差建模方式。

## § 5 — 具体方法与完整 Pipeline

以从单电感 DAB 迁移到串联 LC DAB 为例，完整 pipeline 如下。

1. **Expert system 生成开关输入。** 根据 TPS、HPS-DC 或 PPS 调制，生成桥臂开关函数以及 \(v_p(t)\)、\(v_s(t)\) 等高频交流侧激励。它还可根据开通瞬间的电流方向判断 ZVS-on，并为 topology/circuit/modulation codesign 提供性能评价接口。[pdf:E07]（PDF 物理页 7，Fig. 9）
2. **T²PA 构造确定性状态更新。** 源域单电感 DAB 使用 \(i_L\) 作为状态，把下一时刻桥侧电压与上一时刻电流代入 backward Euler 更新。参数 \(\theta=\{L_k,R_L,n\}\) 既有物理含义，又可用少量源域波形训练。[pdf:E08]（PDF 物理页 8，Table III、Eq. (11)–(13)）
3. **先训练 T²PA。** 用 MSE \(L_1\) 调整物理参数和超参数，保存测试集误差最低的 checkpoint。源域共采 200 条时序，正文给出的划分是训练 5 条、测试 10 条、验证 185 条；Table III 却印成验证 180 条。两处都写成 92.5%，这是论文内部未解释的数据矛盾。[pdf:E06] [pdf:E08]（PDF 物理页 6、8，Table I、Table III 与 Section IV-B）
4. **再训练 MDN。** 计算实测波形与 T²PA 预测的残差，用 negative log-likelihood \(L_2\) 拟合两个 Gaussian components 的均值、协方差和权重。这样 T²PA 给中心轨迹，MDN 给条件波动分布。[pdf:E06]（PDF 物理页 6，Eq. (9)–(10b) 与 Table I）
5. **迁移到串联 LC。** 在单电感模型上增加电容电压 \(v_C\) 状态和电容支路，把原来的一条电流更新扩展成 \(i_L\) 与 \(v_C\) 的耦合 backward Euler 更新；不使用目标域训练数据。[pdf:E09]（PDF 物理页 9，Fig. 13、Eq. (14)–(16)）
6. **迁移到 NPC-DAB。** 电气状态仍可用单电感更新式，但 expert system 增加 NPC 桥的开关信号和两个 duty cycles \(\varphi_1,\varphi_2\)，以表达不对称的 \(v_p,v_s\)。论文在这一案例中没有增加 T²PA 状态。[pdf:E09]（PDF 物理页 9，Fig. 14）
7. **迁移到三端口 DAB。** 新增 \(i_{L2},i_{L3}\) 状态、第三端口电压 \(v_t\) 和三绕组约束；三条支路分别用 backward Euler 更新，并通过匝数关系耦合。[pdf:E10]（PDF 物理页 10，Fig. 15、Eq. (17)–(19)）

论文未报告训练硬件、训练时间、推理 latency、实时步长上限、定点化或 FPGA 映射。其数值更新具有局部乘加、除法和小状态量的特点，理论上适合流水化；但 MDN、动态调制逻辑和除法器的资源/时序代价仍需独立验证。

## § 6 — 核心数学推导

先看物理意义。一般电路可写为

\[
\frac{dx(t)}{dt}=g(u(t);\theta)x(t)+h(u(t);\theta),
\]

其中 \(x\) 是储能元件状态，\(u\) 是开关函数产生的外部激励，\(\theta\) 是元件和控制参数。T²PA 不是把这条式子放进 loss，而是把它变成 recurrent cell 的数据通路。[pdf:E04]（PDF 物理页 4，Eq. (1)）

显式 Euler 用当前时刻斜率推进，计算轻，但对 stiff 或开关突变问题可能不稳定；backward Euler 用下一时刻输入和状态形成隐式更新，代价更高但稳定性更强。论文把可解析的隐式式直接化简，避免每一步再做非线性迭代。[pdf:E05]（PDF 物理页 5，Eq. (3)–(6)）

对单电感 DAB，连续式为

\[
\frac{d i_L}{dt}
=-\frac{R_L}{L_k}i_L+\frac{v_p}{L_k}-\frac{n v_s}{L_k},
\]

backward Euler 后得到

\[
i_L(t_{k+1})=
\frac{L_k i_L(t_k)+\Delta t_k\!\left[v_p(t_{k+1})-n v_s(t_{k+1})\right]}
{L_k+R_L\Delta t_k}.
\]

分子中的 \(L_k i_L(t_k)\) 表示上一时刻储存的磁链贡献，桥侧电压差在 \(\Delta t_k\) 内改变磁链；分母的 \(R_L\Delta t_k\) 则体现电阻耗散。[pdf:E08]（PDF 物理页 8，Eq. (11)–(13)）

加入串联电容后，电感方程多出 \(-v_C/L_k\)，同时 \(i_L=C_s\,dv_C/dt\)。所以 topology transfer 的本质是增加一个电荷状态，并把它接入原电流更新，而不是让固定网络从数据里猜出电容动力学。[pdf:E09]（PDF 物理页 9，Eq. (14)–(16)）

三端口案例同理：三个漏感电流由各自桥侧电压和绕组电压驱动，再由理想变压器匝数和安匝关系耦合。Eq. (17)–(19) 把三个连续支路离散成三条可并行计算的更新，但绕组电压求解仍形成跨支路依赖。[pdf:E10]（PDF 物理页 10，Eq. (17)–(19)）

MDN 使用 Gaussian mixture

\[
p_{\mathrm{MDN}}(x)=\sum_{i=1}^{N}\lambda_i p_i(x\mid\mu_i,\Sigma_i)
\]

描述残差。它输出的不是“另一个确定性补偿值”，而是条件均值、协方差和 mixture weight；论文据此画出 99% confidence 区域。[pdf:E05]（PDF 物理页 5，Eq. (7)–(8)）

## § 7 — 实验设计与结论

**问题 1：少量源域数据能否识别单电感 DAB？**  
实验使用 200 V 输入、80–120 V 输出、20 kHz、100–2000 W 的 2 kW 级平台，示波器采样率为 8 ns/point；源域训练只使用 5 条时序。T²PA 单独预测达到 \(R^2=99.82\%\)，源域 MAPE 为 2.27%。[pdf:E08] [pdf:E12]（PDF 物理页 8，Table II/III；物理页 11，Fig. 17）

**问题 2：目标拓扑不训练能否保持可接受误差？**  
论文把模型迁移到 series-LC、NPC-DAB 和 three-port DAB，Table III 对三个目标域均记为训练 0、测试 0、验证 200。Fig. 17 给出的 MAPE 分别为：series-LC 的 \(i_L\) 3.52%、\(v_C\) 4.67%；NPC-DAB 的 \(i_L\) 3.13%；three-port 的三支路电流 4.08%、5.3%、3.19%。[pdf:E08] [pdf:E12]（PDF 物理页 8、11）

**问题 3：是否优于通用时序网络和 physics-in-loss？**  
Table IV 报告源域 validation MAE：SVR 1.991 A、LSTM 1.193 A、TCN 0.726 A、TST 0.569 A、physics-in-loss 0.264 A、T²PA-MDN 0.161 A；各算法重复 10 次，表中列出 p-value。相对 TST 和 physics-in-loss，0.161 A 对应约 71.7% 和 39.0% 的 MAE 降幅，这就是结论中“71.7% 与 39% 更高准确度”的数值来源。[pdf:E11] [pdf:E13]（PDF 物理页 10，Table IV；物理页 11，Conclusion）

**问题 4：是否有硬件而不仅是仿真？**  
有，但覆盖不完整。Fig. 18 在真实单电感 DAB 上展示多组 step-down、unit-gain 和 step-up 工况；Fig. 19 在真实 series-LC 目标域展示 \(i_L,v_C\) 测量与预测。NPC-DAB 和 three-port 的迁移证据来自案例仿真图，不是同等级硬件验证。[pdf:E12] [pdf:E13]（PDF 物理页 11，Fig. 18–19）

因此，论文支持“在本文给定的 DAB family、显式物理结构和测试范围内，少数据源域训练加人工结构重构可以实现零目标数据迁移”。它没有证明任意电力电子拓扑、未知寄生参数、未见开关模式或长期闭环运行下都能保持同样性能。

## § 8 — Take-aways

**5 句话：**

1. T²PA 把离散电路方程做成 recurrent architecture，而不是只把物理写进 loss。  
2. topology transfer 通过增删物理状态和网络支路完成，因此仍需要已知目标电路方程。  
3. MDN 在 T²PA 之后拟合残差分布，把中心动力学与随机波动分开。  
4. 论文在单电感 DAB 上用 5 条训练时序，并对 series-LC、NPC-DAB、three-port 做零目标数据迁移。[pdf:E01] [pdf:E08]  
5. 结果有 2 kW 硬件支持，但硬件目标域只覆盖 series-LC，且没有 FPGA/实时计算验收。[pdf:E13]

**3 句话：**  
这是一种“可训练的电路离散求解器”，不是普通黑盒 RNN。它的泛化来自显式重构目标拓扑，而不是固定网络自动理解任意新电路。最值得继续研究的是怎样把手工结构迁移变成可验证、可编译、带 OOD 告警的通用建模流程。

**1 句话：**  
论文最有价值的贡献，是把 topology transfer 从数据分布迁移改写成了物理状态更新图的结构迁移。

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标拓扑能被正确的显式状态方程完整描述，而且源域学到的未建模残差分布在结构迁移后仍然适用。**

T²PA 的零数据迁移并不自动发现目标拓扑。工程师必须知道增加哪些状态、怎样写状态方程、选显式还是隐式离散，并正确更新开关 expert system。只要目标电路出现训练源域没有的 hidden mode，例如磁芯饱和、死区与器件 \(C_{\mathrm{oss}}\) 共同引起的换流模式、间歇导通、温度相关参数或保护逻辑，单纯增加理想 \(L/C\) 支路就不再充分。更严重的是，MDN 把源域 T²PA 残差主要解释为 aleatoric uncertainty；若目标域残差来自新的结构性缺模，把它继续当随机波动会给出看似平滑但失准的置信区间。[pdf:E05] [pdf:E09]

论文提供的正面证据是三种目标结构的仿真对齐，以及 series-LC 的硬件波形对齐。[pdf:E09] [pdf:E10] [pdf:E13] 但它没有报告跨拓扑 confidence calibration、OOD detection、长时滚动稳定性，也没有在 NPC-DAB 与 three-port 上进行硬件验证。因此“零目标数据”越成功，越需要额外证明模型不会把目标域系统误差伪装成随机不确定性。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 MDN，而是核心 topology transfer claim：**单电感源域训练出的物理 recurrent cell，增加一个电容状态后，能否在不训练目标域的条件下预测 series-LC。**

可执行方案如下：

1. 用 PLECS、Simulink 或 SPICE 建立同一开关级 DAB，设置 \(V_1=200\) V、\(V_2=80\)–120 V、\(f_s=20\) kHz、\(L_k=160\,\mu\text{H}\)、\(R_L=1.2\,\text{m}\Omega\)，源域只生成 5 条训练时序；参数来自 Table II。[pdf:E08]
2. 按 Eq. (13) 实现单状态 backward-Euler cell，只训练 \(L_k,R_L,n\)，测源域 one-step MAE 和整周期 rollout MAPE。
3. 不使用 series-LC 训练数据，加入 \(C_s=760\) nF 和 Eq. (16) 的 \(v_C\) 状态，保持其余训练结果不变。[pdf:E09]
4. 在至少 20 个未见的电压、功率和相移组合上比较 \(i_L,v_C\) 与开关级仿真，并与两个 baseline 比较：名义参数白盒模型、使用目标域数据重训的 T²PA 上限。
5. 支持核心 claim 的标准：零训练迁移在全部工况上显著优于名义白盒，且与论文 Fig. 17 的 3.52%/4.67% MAPE 同量级；反驳标准：误差集中出现在新换流模式，或必须用目标数据重训才能消除系统偏差。

若时间允许，再增加 MDN，并用 coverage test 检查论文标称 99% 区间是否真的覆盖约 99% 的目标域样本，而不是只看带状图是否“包住曲线”。

## § 11 — 最强反例设计

最强反例不是随便换一种非 DAB 拓扑，而是在论文声称可迁移的 series-LC 内，故意制造**新离散模式**：加入死区、非线性 \(C_{\mathrm{oss}}\)、变压器磁化支路和接近轻载断续导通的工况，同时跨越谐振点改变功率方向。名义拓扑仍是 series-LC，Eq. (14)–(16) 却不再包含决定换流的全部状态。

实验分四组：理想元件、只加寄生、只跨模式、寄生加跨模式；每组都禁止目标域训练。除了 MAPE，还测三项更尖锐的量：开关事件附近的峰值误差、连续多周期 rollout 是否漂移、99% prediction interval 的实际 coverage。如果误差在换流边界系统性偏向一侧、coverage 显著低于 99%，而少量目标数据重训后立即恢复，就说明原结果的替代解释是“测试工况没有离开手工状态方程的有效区间”，而不是残差模型真正具有 topology-invariant 泛化。

这个反例直接攻击论文的核心机制：如果新的物理模式不能通过既有状态支路表达，deformable architecture 只是结构正确的低阶模型，并不等于零数据泛化。

## § 12 — Follow-up Research Idea

电力电子领域评价高影响研究，通常不仅看平均误差，还看跨工况稳定性、硬件覆盖、模型可实现性，以及能否减少真实设计和验证成本。基于第 9 节的限制，一个更非增量的候选方向是：**把手工 topology transfer 改成“电路图到可验证神经求解器”的 compiler。**

（a）未满足的需求是：当前 T²PA 仍要求专家为每个目标拓扑手推状态方程和手改网络，且没有办法判断目标域出现了未建模模式。  
（b）研究价值在于把“某个 DAB family 的零数据迁移”提升为可审计的 component-level composition：输入 circuit graph、器件模型和 modulation schedule，自动生成满足 KCL/KVL 的隐式更新图，同时输出每步残差和 OOD 指标。  
（c）可借鉴相邻领域的 differentiable programming、port-Hamiltonian/energy-based modeling、graph compiler、hybrid automata 和 conformal calibration。  
（d）第一个证伪实验是 leave-one-topology-out：只用若干元件级 residual operators 训练，完全留出 series-LC、NPC 或 three-port 中的一类，在零目标数据下测试电荷/磁链守恒、长时 rollout 稳定性、事件误差和置信区间 coverage；任一结构必须人工特调或 OOD 告警失效，就否定“compiler 泛化”。  
（e）它与本文的实质区别是：本文迁移的是人工重构后的 T²PA 网络；新方向迁移的是可复用元件算子和编译规则，并把“不能安全迁移”作为一等输出，而不是总给出预测。

论文自己提出了提高精度、扩大 converter 范围和面向优化/健康监测的未来方向，但没有解决自动结构生成与失效检测。[pdf:E14]（PDF 物理页 12，future work）上述方向因此只是证据约束下的候选研究想法；在完成更广泛相关工作检索前，不声称其 novelty。
