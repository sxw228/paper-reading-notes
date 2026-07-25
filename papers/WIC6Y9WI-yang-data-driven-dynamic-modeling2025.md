# Data-driven dynamic modeling for inverter-based resources using neural networks

Zotero key：WIC6Y9WI
年份：2025
DOI：10.1038/s41467-025-66604-z

Yang 等发表于 *Nature Communications*（2025），DOI：`10.1038/s41467-025-66604-z`。本文提出 LSTMCI：把 LSTM、显式变量交互的 Cross layer 和物理 inverter dynamic model 串起来，为电力系统时域仿真提供 IBR 的电流注入模型。[pdf:E01][pdf:E02]

> **适用边界先行。** 论文工作在 phasor-domain transient-stability / RMS 级时域框架：输入含母线电压幅值与相角，作者明确说频率由相角导数隐含表示；数据主要为 100 Hz，并用 1 Hz low-pass 处理。它研究的是机电暂态、控制与保护过程，不是开关级或微秒级 EMT。论文没有给出固定端口导纳、passivity、任意多模型互联稳定性或 EMT 误差证明。[pdf:E04][pdf:E08][pdf:E10]

## § 1 — 研究问题与重要性

论文要解决的问题是：当 IBR 厂商模型精确但专有、计算昂贵，而通用 RMS 动态模型又难以覆盖不同设备和控制器时，能否从数据学到一个既保留历史依赖、又通过物理 inverter 接口约束输出的替代模型，用于大系统机电暂态仿真。[pdf:E01][pdf:E08]

这件事重要，不只是因为波形 MAE 更小。IBR 模型误差可能改变系统级稳定性判断：论文对严重三相接地故障后的转子角响应做 Prony 分析，vendor model 与 LSTMCI 都给出负 damping ratio 的不稳定主模态，而 default model 给出正 damping ratio 的稳定模态。也就是说，模型误差可能让规划者把“会失稳”误判为“稳定”。[pdf:E05][pdf:E08]

但这里的“稳定性研究”是秒级转子角低频振荡与 transient stability，不是 EMT 中的开关瞬态、谐波或端口数值稳定性。这个区分决定了本文可为 EMT 建模提供思想启发，却不能直接充当 EMT 证据。

## § 2 — 前人工作与不足

论文比较了三类既有方案。第一类是 vendor model：通常最可信，但受软件平台、保密和计算成本限制，难以直接扩展到数千母线的大系统。第二类是 default / generic dynamic model：结构透明、容易仿真，却需要针对场景调参；在未优化的 LVRT、HVRT 和功率恢复过程中会出现明显偏差。第三类是纯 neural network 与 PINN：纯网络能拟合序列，但输出不必满足 inverter 物理接口；PINN 的上限又受其嵌入的简化 generic model 方程限制，MLP 结构也不擅长长时序依赖。[pdf:E04][pdf:E07][pdf:E08]

LSTMCI 的定位不是“用一个网络替代所有 IBR”。Table 2 显示它仍是一个具体结构选择：LSTM-8 + Cross layer + inverter model，共 1940 个参数；对不同 IBR 和控制策略，需要代表性数据并训练不同模型实例。[pdf:E09][pdf:E10][pdf:E11]

## § 3 — 重建作者的思考路径

可以从三个已知失败模式重建这条路线。首先，故障后的 IBR 输出有明显路径依赖，单个静态映射不能只看当前电压决定恢复过程，因此需要能携带 cell / hidden state 的 recurrent model。其次，有功、无功、dq 量和限制器之间存在乘积、平方及高阶交互，普通 LSTM 未必高效表达，于是引入 Cross layer 显式制造变量交互。最后，系统仿真器需要组件返回电流注入；若网络直接输出任意电流，物理一致性薄弱，因此让网络先产生 inverter model 的驱动量，再由物理 inverter model 生成 \(I_p,I_q\)。[pdf:E02][pdf:E10]

这条思路的关键不是“物理和 AI 拼在一起”这句口号，而是把学习器放在物理接口内部：网络负责难以建模的历史动态，显式 inverter block 负责把结果约束成仿真器能消费的电流注入。

## § 4 — 核心 Intuition

LSTMCI 把 IBR 看成“有记忆的电流注入器”：LSTM 保存故障前后历史，Cross layer补充电气变量之间的显式交互，物理 inverter model 把学习到的内部表示变成 \(I_p,I_q\)。这样做既比 generic model 更能适应非线性恢复路径，又比纯 neural network 更接近仿真器要求的物理接口。[pdf:E02][pdf:E10]

## § 5 — 具体方法与完整 Pipeline

以风电场接入时域仿真器为例，完整流程是：

1. 为该风电场单独准备 vendor model 或测量产生的故障序列，覆盖稳态、故障和恢复段。论文中的训练数据以单次扰动为主，并非包含连续多保护动作的全组合。[pdf:E06][pdf:E09]
2. 在每个采样时刻，把电压幅值 \(V_t\)、相角 \(\theta_t\)、相移特征 \(\Phi_t\)、上一时刻电流 \(I_{p,t-1},I_{q,t-1}\) 等送入 LSTMCI；不同控制策略通过各自数据训练独立实例，不是共享一个零样本 universal model。[pdf:E10][pdf:E11]
3. LSTM 用 hidden/cell state 表达历史，Cross layer 计算当前状态、输入和上一时刻输出的 pairwise interaction，FC 层生成 REGC_A 等 inverter block 所需的输入。[pdf:E02][pdf:E10]
4. 物理 inverter block 输出 \(I_p,I_q\)，作为该 IBR 在 phasor-domain 时域网络中的电流注入。[pdf:E02][pdf:E10]
5. 在每个仿真步内，时域求解器把本步母线 \(V_t,\theta_t\) 送给各 LSTMCI，各实例把 \(I_{p,t},I_{q,t}\) 返回；双方做 alternating iteration，收敛后才进入 \(t+1\)，同时传递收敛的模型状态。[pdf:E11]
6. 大系统里每台 IBR 对应独立 LSTMCI 实例。论文认为这种独立性利于并行或分布式计算，但没有证明多个实例与网络互联后的全局收敛或稳定性。[pdf:E09]

这里不存在“固定导纳先盖章、历史网络只修正电流源”的端口结构。LSTMCI 直接参与本步电压—电流交替迭代，因此不能被等同为固定 \(Y\) 的 EMT Norton 端口。

## § 6 — 核心数学推导

论文没有完整的可证明系统辨识理论，数学主要定义误差、Cross layer、归一化和训练损失。

评价指标是

\[
\mathcal L_{\mathrm{MAE}}=\frac1N\sum_{i=1}^{N}|\xi_i-\hat\xi_i|,\qquad
\mathcal L_{\mathrm{MSE}}=\frac1N\sum_{i=1}^{N}(\xi_i-\hat\xi_i)^2 .
\]

MAE 表示平均幅值偏差；MSE 对少数大误差惩罚更重。论文在原始 p.u. 尺度上计算二者，而不是在归一化尺度上报指标。[pdf:E04]

Cross layer 的核心为

\[
\mathcal I=(M_h\otimes l^T)W_I l,\qquad
l=[h_t^T,x_t^T,y_{t-1}^T]^T .
\]

\(l\) 合并当前 hidden state、当前输入和上一时刻输出，Kronecker product 与权重矩阵显式构造变量交互。当前认证发现历史 trusted 稿曾把式 (4) 的 \(y_{t-1}\) 误写为 \(V_{t-1}\)，已按 PDF 物理页 10 修正。[pdf:E10]

训练采用复合 MAE：

\[
\mathcal L=\mathcal L_{\mathrm{MAE}}(\xi,\hat\xi)
+\lambda_k\mathcal L_{\mathrm{MAE}}(\xi_k,\hat\xi_k),
\]

第二项提高关键时段的权重；文中选择 pre-fault 段帮助模型建立初始稳态，也允许把 DC-link voltage、PLL states 等可测内部量加入 multi-task 辅助目标。训练使用 Adam，batch size 4、step size 0.001、两项衰减率 0.9 和 0.999。[pdf:E11]

这些公式说明“怎么拟合”，但没有给出辨识唯一性、误差随仿真步传播的上界、alternating iteration 收敛半径或互联稳定定理。

## § 7 — 实验设计与结论

**问题一：LSTMCI 是否比 default model 更准确？** 作者在 wind farm、PV station 和 grid-forming BESS 上分别比较四类 LVRT/HVRT 场景。[pdf:E03] 风电场总体 MAE 从 5.97% 降至 2.63%，MSE 从 2.72% 降至 0.248%；PV 的 MAE 从 4.53% 降至 1.34%，MSE 从 1.95% 降至 0.174%；BESS 的 MAE 从 8.04% 降至 2.11%，MSE 从 2.83% 降至 0.145%。这些是三个独立建模对象和实例上的结果，不是一个模型跨对象直接泛化。[pdf:E04][pdf:E05][pdf:E06]

**问题二：更准确的 IBR 模型会不会改变系统稳定性判断？** 作者在 5075-bus 系统施加严重三相接地故障，并对 G2 相对 G1 的转子角做 Prony 分析。vendor model 与 LSTMCI 的主频分别为 0.799 Hz 和 0.794 Hz，damping ratio 分别为 -0.395 和 -0.411；default model 为 0.887 Hz、damping ratio 0.024。作者据此判断前两者显示不稳定趋势，而 default model 给出相反的稳定结论。[pdf:E05][pdf:E08]

**问题三：连续 LVRT—保护序列是否真是 held-out？** 是，但边界很具体。训练数据只包含 single disturbance；测试序列先降到 0.4 p.u.，200 ms 后 zone protection 把 PCC 拉到 0.75 p.u.，再过 400 ms 第二个保护恢复正常。序列后半段属于未训练组合。LSTMCI 相对 vendor model 的 MAE 为 P 2.04%、Q 0.73%，default model 为 P 13.61%、Q 2.62%。这支持“对这一个组合序列有 extrapolation”，不支持对任意保护逻辑、设备或网强的普遍 OOD 保证。[pdf:E06][pdf:E09]

**问题四：是否无需目标域再训练？** 否。论文明确用不同代表性数据训练不同控制策略和 IBR 的独立 LSTMCI 实例；vendor-generated data 是主要来源，实测数据和 transfer learning 被作为部署与更新路径。连续序列可 held-out，但目标设备、控制类型和运行域并不是无条件零样本迁移。[pdf:E08][pdf:E09][pdf:E11]

## § 8 — Take-aways

**5 句话：** LSTMCI 用 recurrent memory 表示 IBR 的历史依赖。Cross layer 显式表达电气变量交互。物理 inverter block 把学习结果转成仿真器需要的电流注入。它在三个 IBR 实例和一个 held-out 连续 LVRT—保护序列上显著优于 tuned default model，并在一个 Prony 案例中复现 vendor model 的失稳判断。全部证据属于 phasor-domain 机电暂态，不能外推为 EMT 固定导纳接口或互联稳定性证明。

**3 句话：** 这篇论文最强的价值，是说明 IBR 模型精度会改变系统稳定性结论，而不只是降低波形误差。最可信的泛化证据是“single-disturbance 训练、continuous protection sequence 测试”，但仍局限于已建模对象及其代表性数据。工程上它是多实例、逐步电压—电流迭代的 RMS 动态模型。

**1 句话：** LSTMCI 是有物理输出接口的 learned-history RMS 电流注入模型，不是经过可组合稳定证明的 EMT 固定导纳模型。

## § 9 — 最脆弱的假设

最脆弱的假设是：训练用 vendor model 或测量数据在目标 IBR、控制器版本、运行点和保护逻辑上足够代表部署域。这个假设一旦失效，物理 inverter block 只能约束输出形式，不能阻止 LSTM 的内部历史表示学到错误恢复路径。

论文给出的支持是三个对象、多个扰动和一个连续 held-out 序列；作者也明确承认 vendor data 可能与实测不完全一致、设备会因 aging 或 firmware update 产生 concept drift，模型还对 inverter 初始参数和 measurement noise 敏感。[pdf:E08][pdf:E09] 缺少的证据包括：跨厂商零样本迁移、保护逻辑结构变化、弱网/强网大范围变化、多个 learned instances 强耦合时的闭环稳定性，以及 EMT 时标下的开关谐波与数值刚性。

## § 10 — 最小复现实验

一周内最有信息量的复现不是重建 5075-bus 全系统，而是复现 Fig. 7a：

1. 使用论文公开的 Code Ocean capsule 与同一 wind-farm 模型，只用 single-disturbance 轨迹训练一个 LSTMCI 和一个参数量相近的 plain LSTM。
2. 测试固定的连续序列：0.4 p.u. LVRT，200 ms 后回到 0.75 p.u.，再过 400 ms 恢复正常；该组合不得进入训练。
3. 同时运行 vendor model，测 P/Q 的时域 MAE、最大恢复偏差、保护切换后 100 ms 内的峰值误差，并记录本步 alternating iteration 的迭代次数。
4. 支持论文 claim 的结果是：LSTMCI 接近论文报告的 P 2.04%、Q 0.73%，且显著优于 default/plain LSTM；反驳信号是误差只在已训练片段低、保护切换后快速累积，或网络—模型迭代出现不收敛。

这样既复核 extrapolation，也第一次把“波形准确”与“仿真器内闭环可用”分开测量。[pdf:E09][pdf:E11]

## § 11 — 最强反例设计

最强反例是构造训练分布外的**耦合保护—网强—多实例**场景，而不是再换一个单独 voltage dip。让两个或更多不同控制策略的 IBR 各用独立 LSTMCI 接入弱网，在故障期间依次触发 current limit、PLL mode switch、zone protection 和恢复斜坡，同时扫描短路比与线路 \(R/X\)。保持每个单模型的离线 MAE 都不差，再观察 alternating iteration 是否出现多解、振荡或错误收敛，以及系统 Prony 模态是否仍与 vendor models 一致。

如果单实例误差很小但互联系统给出错误阻尼符号，说明论文的主要成功来自单设备轨迹拟合，并没有解决 learned component 的 composability。若保护切换后内部状态落入训练未覆盖区域并持续偏离，则 Fig. 7a 的组合泛化只能视为一个成功案例，不能视为普遍机制。[pdf:E08][pdf:E09][pdf:E11]

## § 12 — Follow-up Research Idea

**候选想法，不声称已验证 novelty：把问题从“更准的 RMS 轨迹替代模型”改成“可预装配、可组合验证的 learned-history EMT 端口”。**

需求来自实时 EMT：网络矩阵希望每步保持固定、可预先分解的端口导纳，而 learned history 只更新等效历史电流源；同时还要在多实例并联时给出能量或增量 passivity 约束。可以借鉴 behavioral system identification、port-Hamiltonian / dissipativity、Norton companion model 和 contraction analysis，让学习器预测历史源或受约束残差，而不是直接参与不可控的本步电压—电流闭环。

第一个可证伪实验是：在相同训练数据下比较 LSTMCI 式本步交替迭代、固定 \(Y\)+learned history source 和高精度 EMT reference；扫描步长、短路比、并联实例数及保护切换。若固定导纳版本无法同时保持亚步长 EMT 误差、网络复用效率和多实例稳定裕度，这个研究方向就失败。它与本文的实质区别是把目标从“单设备 RMS 波形准确”改为“端口结构、数值复用和互联稳定同时可验证”；本文没有提供这项结论，只提供了 learned history、物理输出接口和稳定性误判风险这三个动机。[pdf:E05][pdf:E10][pdf:E11]
