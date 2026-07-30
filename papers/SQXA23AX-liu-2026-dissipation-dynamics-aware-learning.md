# Dissipation-Based Dynamics-Aware Learning Scheme for Transient Stability Analysis of Networked Black-Box Grid-Forming Inverters

- 作者：Zhong Liu、Jialin Zheng、Xiaonan Lu
- 出处：IEEE Transactions on Power Electronics, Vol. 41, No. 3, March 2026, pp. 3165–3170
- 年份：2026
- DOI：10.1109/TPEL.2025.3612948
- Zotero key：SQXA23AX

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把一条暂态波形拟合得更像”，而是一个更严格的问题：当并网的 grid-forming（GFM）逆变器因厂商控制器和参数保密而只能作为黑盒使用时，能否仅凭可测时间序列恢复足以进行 Lyapunov 暂态稳定分析的动力学，并进一步得到 region of attraction（ROA，吸引域）和稳定裕度。论文把现有 LSTM、NARX 等黑盒模型概括为轨迹点到轨迹点的映射；这种模型可以复现过去的状态序列，却没有显式给出状态导数所定义的向量场，因此不能直接支撑依赖 \(\dot x\) 或 \(\nabla V\!\cdot\!f(x)\) 的 Lyapunov 判据。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，是因为高比例 inverter-based resources（IBR）系统正在同时遭遇两个现实约束：一方面，大扰动后的动态由控制器、网络和限幅等非线性共同决定；另一方面，商业设备的内部控制细节往往不可获得。等面积判据适用范围窄且主要给出二元稳定判断，EMT 仿真则要为每个扰动场景单独配置和运行；Lyapunov 方法能够用 ROA 给出非二元的稳定范围，但传统 LMI、SOS 和 Brayton–Moser 构造又分别依赖显式非线性结构、多项式结构或人工推导。[pdf:E01]（PDF 物理页 1，Introduction 右栏）因此，若能从测量数据恢复“可供稳定性证明使用的动力学”，价值不只是加快一次仿真，而是尝试把逐工况计算转成可复用的稳定域判断。

需要同时限定论文的实际覆盖范围：它验证的是三台 droop-controlled GFM 组成的三母线系统，重点分析比电压动态更快的相角动态；这不是对任意厂商逆变器、任意运行点或任意 hybrid control mode 的普遍证明。[pdf:E04]（PDF 物理页 4，Section IV）

## § 2 — 前人工作与不足

论文点名了五类直接相关路线。第一，LSTM 与 NARX 用时间序列学习黑盒输入输出关系，但论文认为它们缺少显式状态导数，因而无法把所得模型直接嵌入 Lyapunov 导数条件。第二，EAC 由单机无穷大系统发展而来，论文强调其判断偏二元，若要估计裕度通常需要试探。第三，EMT 仿真能够复现特定扰动，却是 case-specific 的。第四，LMI 方法要先识别非线性项，SOS 主要面向多项式系统，遇到高度非线性系统可能求不出结果。第五，Brayton–Moser 方法依赖手工推导并受模型结构约束。[pdf:E01]（PDF 物理页 1，Introduction）

论文所借用的两个关键已有工具也很明确：Neural ODE 提供“由状态预测导数、再经 ODE solver 生成轨迹”的建模方式；neural Lyapunov control 提供“学习候选 \(V\) 并用 falsifier 寻找反例”的框架，参考文献 [13]、[14] 分别指向这两条路线。[pdf:E06]（PDF 物理页 6，References [13]–[14]）论文真正改变的是它们在黑盒 GFM 稳定分析中的连接方式：先从纯测量轨迹得到动力学代理，再让第二个网络在该代理上构造 Lyapunov 函数。

不过，前人比较也有明显缺口。论文没有对 LSTM/NARX 与 Level I FNN 做同数据、同外推工况的定量 baseline，也没有与其他 black-box stability classifiers 比较；ROA 部分只与文献 [15] 的显式模型 neural Lyapunov 结果做图形比较，没有报告集合重叠率、边界误差或保守度指标。[pdf:E05]（PDF 物理页 5，Fig. 6 与对应正文）所以原文足以说明“为什么需要一种动力学感知的黑盒路线”，却不足以证明这条路线相对所有可选黑盒方法都更准确或更省成本。

## § 3 — 重建作者的思考路径

以下是基于论文背景和既有工具重建的推理链，不是作者逐字给出的研发历史。

第一步，从稳定性分析的输入需求倒推建模目标。若最终要检验 \(\dot V(x)=\nabla V(x)\!\cdot\!f(x)<0\)，那么只预测下一时刻状态并不够；模型必须显式给出当前状态处的向量场 \(f(x)\)。第二步，在内部方程不可见时，把 \(f\) 本身表示成 FNN，并通过 ODE solver 积分出完整轨迹，再用轨迹误差训练网络。这样训练信号仍只需要可测轨迹，却把网络输出改成了状态导数。[pdf:E02]（PDF 物理页 2，Section III-A，Eqs. (5)–(8)）

第三步，即便已有动力学代理，Lyapunov 函数仍没有通用解析构造，因此把 \(V(x)\) 也参数化为网络，以正定性、沿轨迹递减和原点为零作为损失。第四步，有限随机样本无法排除样本间的违规点，于是让 SMT solver 在给定区域内主动搜索违反 Lyapunov 条件的状态，把找到的 counterexample 加回训练集，反复进行 learning–falsification。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eqs. (9)–(11)）

最后才得到论文的 bilevel 结构：Level I 解决“未知 \(f\)”；Level II 解决“未知 \(V\)”；ROA 是两级串联后的产物。这个思路的逻辑强点是把黑盒辨识和可解释稳定判据接起来，逻辑弱点则是两级误差也会串联：Level II 的形式化检查只看到了 Level I 给出的代理动力学。

## § 4 — 核心 Intuition

不要让神经网络只记住“状态接下来长什么样”，而要让它学习“状态此刻朝哪个方向变化”；后一种表示才能计算 Lyapunov 函数沿系统运动方向的变化率。随后用另一个网络表示 Lyapunov 函数，并让 SMT solver 不断寻找违反正定或耗散条件的状态，直到在指定区域内找不到反例。[pdf:E03]（PDF 物理页 3，Fig. 1）直观上，这是把一条条波形先还原成局部“流向地图”，再在这张地图上寻找一个处处下坡的能量地形。

## § 5 — 具体方法与完整 Pipeline

以论文的三台互联 GFM 为例，完整 pipeline 如下。

1. **输入与状态选择。** 在 Typhoon HIL 上施加多种大扰动，采集状态时间序列。由于论文假设 voltage-loop time constant 满足 \(\tau_v\gg\tau_a\)，只保留较快的相角偏差 \(x=[\delta'_1,\delta'_2,\delta'_3]\) 作为三维状态；三台逆变器的 droop 参数和三条线路阻抗在 Fig. 2 中给出，但训练过程不读取这些显式参数。[pdf:E04]（PDF 物理页 4，Fig. 2–3 与 Section IV）
2. **Level I：学习动力学。** 构造一个 3 输入、50 个 tanh hidden neurons、3 输出的 FNN \(f_\theta(x)\)。网络输出状态导数，ODE solver 把它积分成预测轨迹 \(\hat x(t)\)，训练则最小化预测轨迹与实测轨迹之间的 L1 loss。论文报告该网络在 Google Colab T4 GPU 上训练 1925 s。[pdf:E02][pdf:E04]（PDF 物理页 2，Eqs. (5)–(8)；物理页 4，case setup）
3. **由代理动力学生成 Level II 数据。** 训练好的 \(f_\theta\) 不再只是做 forecast，而是作为黑盒逆变器向量场的 surrogate，在状态空间采样点上提供导数信息。[pdf:E03]（PDF 物理页 3，Fig. 1 上半部分）
4. **Level II：学习耗散型 Lyapunov 函数。** 构造 3 输入、8 个 tanh hidden neurons、1 输出的 fully connected network \(V_\theta(x)\)。初始训练集从以原点为中心的 \([-1,1]^3\) 超立方体均匀抽取 \(N=1000\) 个状态，以正定性、\(\dot V<0\) 和 \(V(0)=0\) 组成 Lyapunov risk。[pdf:E03][pdf:E04]（PDF 物理页 3，Eq. (10)；物理页 4，Section IV）
5. **falsification loop。** SMT solver 用 Eq. (11) 搜索满足“离开原点小邻域且 \(V\le 0\) 或 \(\nabla V\!\cdot\!f\ge0\)”的状态。每次找到违规点，就固定加入 10 个 counterexamples 并重训；停止条件是找不到新反例或达到 5000 次迭代。该 case 在 182 s 后返回一个作者称为 valid 的 Lyapunov 函数。[pdf:E03][pdf:E05]（PDF 物理页 3，Eq. (11)；物理页 5，training paragraph）
6. **输出。** 利用最终 \(V_\theta\) 构造 ROA；若故障切除后的状态落在该区域内，则论文按 Lyapunov 不变性解释为会回到平衡点，并用 HIL 时域波形验证三个入域工况。[pdf:E04][pdf:E05]（PDF 物理页 4，ROA 解释；物理页 5，Figs. 6–7）

从 EMT/FPGA 实现角度，论文实际报告的是 Typhoon HIL 的 6-core processor、主机/示波器/DSP 控制器测试台，以及在 Colab T4 GPU 上进行离线 NN 训练。[pdf:E04]（PDF 物理页 4，Fig. 3 与实验设置）它没有报告 FPGA mapping、fixed-point word length、并行流水线、单步 latency、实时步长、资源占用或片上部署；也没有把故障施加/切除建模成一个显式 hybrid state transition。因而这篇文章应理解为“用 HIL 数据进行离线黑盒稳定域学习”，而不是 FPGA 实时稳定分析器。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文先用 droop-controlled GFM 的显式模型说明物理对象。相角和电压幅值偏差分别满足

\[
\tau_a\dot{\delta}' + \delta'=m_a(P^*-P),\qquad
\tau_v\dot E' + E'=n_v(Q^*-Q),
\]

多机互联还要满足由网络导纳决定的有功、无功潮流约束 Eqs. (3)–(4)。这些方程用于描述和 benchmark 三机系统，而论文强调训练时把内部 ODE 当作完全未知。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(4)）

Level I 把真实黑盒自治系统写成

\[
\dot x=f(x),\qquad x(t_0)=x_0,
\]

并以 FNN \(f_\theta(x)\) 近似右端向量场。网络经 ODE solver 生成 \(\hat x\)，损失为

\[
\ell=\|\hat x-x\|_1=\sum_{i=1}^{N}|\hat x_i-x_i|.
\]

Adam 根据该轨迹损失对全部参数更新。[pdf:E02]（PDF 物理页 2，Eqs. (5)–(8)）这里的关键 intuition 是：训练标签并不需要直接测得 \(\dot x\)；只要可微 ODE solver 能把网络导数积分成轨迹，轨迹误差就能反向传到向量场参数。

Level II 使用经典 Lyapunov 充分条件：

\[
V(0)=0,\quad x\ne0\Rightarrow V(x)>0,\quad
\dot V(x)=\nabla_xV(x)\cdot f(x)<0.
\]

若这些条件在考察域内成立，平衡点渐近稳定。[pdf:E03]（PDF 物理页 3，Eq. (9)）论文把条件软化为可训练的风险

\[
\mathcal L(\theta)=\frac1N\sum_{i=1}^{N}
\left[\max(-V_\theta(x_i),0)+\max(0,\dot V_\theta(x_i))+V_\theta^2(0)\right],
\]

三项分别惩罚非正的 \(V\)、非负的 \(\dot V\) 和不为零的原点值。[pdf:E03]（PDF 物理页 3，Eq. (10)）

随机采样只能说明样本点没有违规，因此 falsifier 再求解

\[
\Phi(x)=\left(\sum_{i=1}^{n}x_i^2\ge\varepsilon\right)
\land\left(V(x)\le0\ \lor\ \nabla_xV_\theta\cdot f(x)\ge0\right).
\]

若该逻辑式在限定状态域内 satisfiable，解就是 counterexample；否则候选 \(V\) 相对于被检查的动力学和求解域通过检查。[pdf:E03]（PDF 物理页 3，Eq. (11)）

这里必须精确区分两种“有效”。SMT 检查能够约束 \(V_\theta\) 相对于 learned \(f_\theta\) 的符号条件；论文没有给出 \(\|f-f_\theta\|\) 的全域误差上界，也没有把这个误差传播成 \(\nabla V\cdot f\) 的 robust margin。因此，从公式本身不能推出“相对于真实黑盒 \(f\) 也被形式化保证”。原文结论把有效性限定到 selected state space region，但它仍以 Level I 代理足够准确为隐含前提。[pdf:E06]（PDF 物理页 6，Conclusion）

## § 7 — 实验设计与结论

**问题一：Level I 是否学到了可用于积分的动力学？** 论文在三机 HIL 系统上用大扰动轨迹训练 3–50–3 FNN，再随机设置四个初始条件，比较 learned FNN 与 ground truth 的三维相轨迹。Fig. 4 四幅图标注的 error 分别为 0.0003、0.0009、0.0005 和 0.0002，轨迹视觉上高度重合。[pdf:E04]（PDF 物理页 4，Fig. 4）答案是“在这四个测试轨迹上拟合很好”；但论文没有定义该 error 的范数、单位或归一化方式，也没有做状态域全覆盖误差评估，因此不能把它外推为全域向量场准确。

**问题二：Level II 能否得到满足耗散条件的候选函数？** 论文在 \([-1,1]^3\) 中以 1000 个均匀样本起步，循环加入每批 10 个 SMT counterexamples，最多 5000 次；本例 182 s 后返回函数。Fig. 5 展示 \(V\) 与 \(\dot V\) 的曲面和标出的 valid region，作者据此判断满足 Eq. (9)。[pdf:E04][pdf:E05]（PDF 物理页 4，Fig. 5 与采样设置；物理页 5，训练结果段）答案是“相对于 learned dynamics，训练与 falsification loop 找到了通过检查的候选函数”；论文没有报告 SMT backend、容差、完整求解域约束或超时配置，独立复现这些“无反例”结论仍缺关键信息。

**问题三：黑盒方法所得 ROA 是否接近显式模型方法？** Fig. 6 在三个二维投影中画出 Actual、Our Method 和 Valid Region；正文把 proposed method 与文献 [15] 的显式模型 neural Lyapunov ROA 作比较，结论是边界“comparable”。[pdf:E05]（PDF 物理页 5，Fig. 6）图形支持定性接近，但没有 Jaccard overlap、Hausdorff distance、体积保守度等定量指标，所以“可比”不能进一步解释为边界误差已被严格控制。

**问题四：估计 ROA 内的故障后状态是否真的回稳？** Case 1 在 Lines 1–2、1–3、2–3 施加 \(Z_f=0.08\,\Omega\) 的三相阻抗故障，区间为 \(t\in[5.0,5.5]\) s；切除后状态为 \([-0.20,-0.29,-0.41]\)，位于估计 ROA 内，三相角与 GFM #1 A 相电流回稳。Case 2 在 Lines 1–2、2–3 使用同阻抗、同持续时间故障，切除状态也在 ROA 内并回稳。[pdf:E05]（PDF 物理页 5，Fig. 7 与 Case 1–2 正文）Case 3 则在两条线路施加 \(t=5.0\) 到 \(6.0\) s 的三相 bolted fault，延长到 1.0 s 后仍回到平衡点。[pdf:E06]（PDF 物理页 6，Case 3）答案是“这三个入域案例与稳定预测一致”。不得外推之处是：没有选择估计 ROA 外的后故障状态来验证不稳定，也没有专门攻击边界附近、运行点变化、current limiting 或控制模式切换。

整体实验支持 feasibility，却还不是强意义的泛化或安全保证。证据链为“少量轨迹上动力学误差小 → learned dynamics 上找到 \(V\) → 三组 ROA 内故障回稳”；其中最薄弱的一段是从少量轨迹误差过渡到整个三维认证区域内的向量场误差。

## § 8 — Take-aways

**5 句话：**

1. 论文把黑盒建模的目标从逐点轨迹预测改成显式状态导数学习，使测量数据能够进入 Lyapunov 稳定分析。[pdf:E02]
2. Level I 用 neural ODE 式 FNN 学习 \(f_\theta\)，Level II 用 neural Lyapunov network 与 SMT counterexample loop 学习 \(V_\theta\)。[pdf:E03]
3. 三机 Typhoon HIL 案例中，四条测试相轨迹误差很小，所得 ROA 与显式模型方法在图形上接近。[pdf:E04][pdf:E05]
4. 三组落入估计 ROA 的故障后状态都在时域波形中回到平衡点。[pdf:E05][pdf:E06]
5. 论文真正未闭合的是 learned dynamics 到真实黑盒 dynamics 的认证迁移，而不是候选 \(V\) 相对于 learned model 的符号检查。

**3 句话：**

1. 这项工作用“学导数而非只学轨迹”把黑盒辨识接到了 Lyapunov ROA 分析。
2. HIL 案例证明流程可以跑通，并给出了轨迹、Lyapunov 曲面、ROA 和故障回稳的相互印证。[pdf:E04][pdf:E05]
3. 但真实系统的全域模型误差没有被纳入证书，因此当前结果更适合称为 evidence-backed stability estimate，而非对未知逆变器的无条件稳定保证。

**1 句话：** 论文最有价值的贡献是把黑盒 GFM 的测量轨迹转成可做 Lyapunov 分析的动力学代理，最需要补上的则是代理误差下仍成立的 robust certificate。

## § 9 — 最脆弱的假设

失败代价最大的假设是：Level I 学到的 \(f_\theta(x)\) 在整个 Level II 认证域和 ROA 内都足够接近真实黑盒 \(f(x)\)，尤其不会把 \(\nabla V(x)\cdot f(x)\) 的符号判断弄反。只要某个稀疏覆盖区域满足 \(\nabla V\cdot f_\theta<0\) 而 \(\nabla V\cdot f\ge0\)，SMT solver 即使对代理模型穷尽搜索，也会把真实系统中的逃逸方向漏掉；此时核心产物 ROA 不再具有论文赋予它的稳定含义。

论文对这一假设给出的直接证据，是四个随机初始条件下 predicted 与 ground-truth phase portrait 的小 error，以及三个 ROA 内故障案例的稳定恢复。[pdf:E04][pdf:E05][pdf:E06] 缺少的证据则是：（1）覆盖 \([-1,1]^3\) 的导数误差或置信区间；（2）\(\dot V\) 负裕度相对于模型误差的下界；（3）未见状态、运行点或控制模式下的 out-of-distribution 检验；（4）边界外反例。基于这些证据，合理结论是“代理在展示的轨迹附近有效”，而不是“代理在整个证书域内已被保证有效”。

这个假设在实际设备上很容易因 current limiter、保护逻辑、饱和、离散模式切换、测量延迟或未激发的内部状态而失效。论文没有声称覆盖这些机制；把它们列为风险是基于黑盒系统辨识结构的推断，不是原文实验事实。

## § 10 — 最小复现实验

一周内最值得复现的不是整篇论文的全部图，而是“learned-model certificate 能否转移到真实动力学”这一关键点。

1. **数据。** 按 Fig. 2 的三机 droop 系统在 EMT/HIL 或高保真仿真中生成训练轨迹；使用与训练不同的初始状态和故障组合保留一套验证数据。状态仍取 \(x=[\delta'_1,\delta'_2,\delta'_3]\)，并保留仿真器可直接计算的真实 \(\dot x\) 作为只用于验证的 ground truth。[pdf:E04]
2. **实现。** 复现 3–50–3 tanh FNN、ODE trajectory L1 training，再复现 3–8–1 tanh \(V_\theta\)、\([-1,1]^3\) 的 1000 点初始采样、每轮 10 个 counterexamples 和最大 5000 轮设置。[pdf:E04][pdf:E05]
3. **测量。** 在 learned ROA 内做稠密采样和 adversarial search，同时计算 \(\dot V_{\rm learned}=\nabla V\cdot f_\theta\) 与 \(\dot V_{\rm true}=\nabla V\cdot f\)。随后从最接近符号翻转的状态启动真实 EMT/HIL 轨迹，观察它是否保持在 ROA 并回到平衡点。
4. **支持标准。** 所有搜索到的域内点都保持 \(V>0\) 且 \(\dot V_{\rm true}<0\)，并且从最差裕度状态启动的真实轨迹均不离开 ROA；同时应报告最小负裕度，而不只报告“零反例”。
5. **反驳标准。** 找到一个可重复的域内状态，使 learned model 判为 \(\dot V<0\)，但真实模型上 \(\dot V\ge0\)，或真实轨迹离开所估 ROA。一个这样的 counterexample 就足以否定“代理上的 certificate 自动转移到真实黑盒”的强版本 claim。

这个实验不需要复现完整 FPGA 或在线部署，因为原文也没有这部分；它只需要保留一个可访问真实导数的高保真模型来审计黑盒学习结果。

## § 11 — 最强反例设计

最强反例不是再挑一个普通故障看误差是否稍大，而是构造“观测轨迹不可区分、证书域内动力学不同”的黑盒。具体做法是：训练数据仍来自论文展示的有限故障轨迹，但在未被这些轨迹穿过的 ROA 边缘区域触发一个隐藏 control mode，例如 current limiting 或保护饱和。该模式在训练轨迹附近保持与原系统相同，因此 Level I 的四条验证轨迹仍可得到很小误差；一旦状态进入稀疏区域，它增加一个沿 \(\nabla V\) 上坡的向量场分量，使真实 \(\dot V\ge0\)，而 \(f_\theta\) 仍预测 \(\dot V<0\)。

实验上可在 HIL 中对 fault location、duration、pre-fault operating point 和 controller limit 做定向搜索，目标不是最大化轨迹均方误差，而是直接最大化

\[
\Delta\dot V=\nabla V(x)\cdot[f(x)-f_\theta(x)].
\]

一旦找到位于 learned ROA 内且 \(\Delta\dot V\) 足以造成符号翻转的状态，就从该状态或可达故障序列启动 HIL。若轨迹离开 ROA或不回到平衡点，而 SMT 对 \(f_\theta\) 仍报告无 counterexample，就直接证明失败来自模型不确定性被证书忽略，而不是 Lyapunov 网络训练不充分。

这是基于证据的反例设计。论文只验证了三个 ROA 内回稳案例，并未展示这种 hidden-mode 攻击；因此这里不声称已有实验已经发现失败，只说明什么结果会真正推翻核心机制。

## § 12 — Follow-up Research Idea

在 power electronics 与 power systems 领域，高影响结果通常不仅需要新的 learning architecture，还要同时给出可审查的稳定性论证、与强基线的定量比较、跨运行点或硬件条件的 HIL/实验验证，以及实现成本和适用边界。基于第 9 节，候选研究方向可以从“先学一个点估计动力学，再为它找 ROA”改成“直接为所有与数据一致的动力学集合构造 robust ROA”。

**（a）未满足需求。** 厂商黑盒恰恰意味着 \(f(x)\) 不可能被有限轨迹唯一确定；现有流程却把单个 \(f_\theta\) 当成后续 falsification 的唯一对象。[pdf:E03] 需要的是一个能显式表示“哪些动力学仍与数据相容”的 set-valued model，而不是更大但仍然单值的网络。

**（b）潜在研究价值。** 若能证明

\[
\max_{f\in\mathcal F(x)}\nabla V(x)\cdot f(x)<0
\]

在某一区域成立，那么证书面对的就是数据允许的最坏动力学，而非某个平均拟合模型。这样的 ROA 会更保守，但其边界、数据覆盖和失败条件都可解释，更接近黑盒设备接入和安全运行真正需要的保证。

**（c）相邻领域工具。** 可借鉴 set-membership system identification、differential inclusion、robust control 与 neural network bound propagation：先从保留验证轨迹得到状态相关的 residual set \(\mathcal E(x)\)，形成 \(\mathcal F(x)=f_\theta(x)\oplus\mathcal E(x)\)，再让 falsifier 搜索“存在某个允许误差使 \(\dot V\ge0\)”的 robust counterexample。关键不是给点估计附一个经验 error bar，而是让不确定性进入 Lyapunov 条件本身。

**（d）首个证伪实验。** 刻意把一种 controller limit 或一个运行点完全留出训练集，用其余数据构造 \(\mathcal F(x)\)。如果留出模式的真实导数频繁落在 \(\mathcal F(x)\) 之外，或 robust ROA 仍预测其入域轨迹稳定但 HIL 轨迹逃逸，那么研究设想首先在“不确定性集合可校准”这一步被证伪。

**（e）与本文的实质区别。** 本文的顺序是单值动力学辨识 \(f_\theta\) → 相对于该动力学训练和检查 \(V_\theta\)；候选方案的研究对象则是数据一致动力学集合 \(\mathcal F\) 与最坏情形 Lyapunov 证书，改变了“什么才算被认证”的问题定义，而不只是给 Level I 或 Level II 多加一个模块。

这个方向尚未在本卡中完成紧密相关工作的系统检索，因此只作为由本文证据约束出的候选想法，不声称 novelty。
