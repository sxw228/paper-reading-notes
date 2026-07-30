# Physics-Informed Neural Network Based Online Impedance Identification of Voltage Source Converters

作者：Mengfan Zhang，Qianwen Xu，Xiongfei Wang  
出处：IEEE Transactions on Industrial Electronics，Vol. 70，No. 4  
年份：2023  
DOI：10.1109/TIE.2022.3177791  
Zotero key：PIZZEKQZ  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是：在 converter 控制器和滤波器内部结构未知、运行点又随可再生能源与负载变化时，怎样用有限的在线测量数据识别 VSC 端口的多运行点 dq 导纳模型，并据此判断 converter-grid interaction stability。阻抗稳定性分析只需要 converter 与 grid 的端口模型，不必公开完整控制实现；但固定运行点测得的阻抗不能代表持续变化的运行点，而在线数据又太少，普通 ANN 容易过拟合。作者把这两处工程瓶颈概括为“黑箱 + 变工况 + 小数据”，并提出以 VSC 的部分物理结构压缩 ANN，再用少量目标机数据完成在线迁移；这是论文的核心 claim（PDF 物理页 1，Abstract 与 Section I）[pdf:E01]。

这项工作的价值不在于替代详细 EMT 模型，而在于为无法取得厂商内部模型的系统提供一个端口级、随运行点变化的稳定性分析入口。若识别模型能在目标 converter 上及时更新，运营者可以把广义 Nyquist 判据用于运行点扫描，而不是只在少数离线工况上做一次性判断。这里“及时”只是应用需求；论文没有报告在线训练的 wall-clock latency、更新周期或实时部署资源，因此不能从题名中的 online 进一步推出实时闭环可执行性。

## § 2 — 前人工作与不足

论文在 Section I 把既有路线分成四类。解析 impedance model 能支持 GNC，但需要已知控制结构与参数；测量法保护厂商知识产权，却通常只覆盖固定运行点；polytopic model 用多个运行点的小信号模型加权，但只在有限点上预测且精度难保证；gray-box 或近似解耦模型仍要求已知控制结构或等价结构。ANN-based MOP model 可以从测量数据学习运行点到阻抗的映射，却依赖较大的训练集，在线小样本会带来过拟合；已有 transfer-learning 工作以仿真数据加速训练，但作者认为仍缺解析与实验验证。论文还强调，这些路线主要依赖离线仿真或实验，尚未处理变化运行剖面下的在线识别（PDF 物理页 1-2，Section I）[pdf:E01] [pdf:E02]。

因此，作者并不是声称“此前没人做阻抗识别”，而是改变了可用信息的组合：目标 VSC 的内部实现仍未知，但允许使用一个通用 VSC 的解析结构与仿真数据，并允许从目标机取得少量端口扰动数据。这个边界很重要，因为方法的有效性取决于通用模型是否给出了对目标机有益而不是误导性的 inductive bias。

## § 3 — 重建作者的思考路径

以下是基于论文证据的思路重建，不是作者逐字陈述。

第一步，从稳定性任务倒推最小必需信息：GNC 只需要端口阻抗/导纳，而厂商又不愿公开控制器，所以应把目标机视为黑箱，直接在 PCC 测量端口响应。第二步，运行点变化使“一点一个模型”不可用，于是模型必须显式接收运行点和频率，输出整个 dq 导纳矩阵。第三步，普通 ANN 虽然能拟合这张多维曲面，但在线测量昂贵且样本稀疏，完全自由的网络会把数据用在重新发现已知的 VSC 结构上（PDF 物理页 1-2，Section I 与 Fig. 1）[pdf:E01] [pdf:E02]。

第四步，作者从一般 grid-connected VSC 的小信号模型看到一个可利用的分解：控制、filter、PLL 与 delay 形成频率相关传递函数，而稳态 \(V_d,V_q,I_d,I_q\) 以相对简单的组合进入闭环导纳。于是可把这部分函数结构固化为网络连线，只让网络学习仍未知的频率函数。一般 VSC 的框图、PLL 线性化和数字控制 delay 为该分解提供了物理起点（PDF 物理页 3，Section III-A，Fig. 2-4 与 Eq. (1)-(10)）[pdf:E03]。

第五步，先用通用 VSC 的丰富仿真数据学到初始权重，再把目标 VSC 的少量测量送入该网络更新，即把“从零学习未知函数”改为“校正一个带物理先验的初始函数”。这就是作者采用 transfer learning 的直接理由，而不是把微分方程 residual 加进 loss；本文所谓 physics-informed neural network，实质上是由解析导纳结构约束网络拓扑。

## § 4 — 核心 Intuition

VSC 导纳并不是任意的五输入黑箱函数：频率决定控制、PLL、滤波与 delay 的动态形状，运行点变量再以受物理关系约束的方式调制这些形状。把这种分工预先写进 ANN，就能让稀疏在线数据主要负责校正目标机与通用机之间的差异，而不是从头学习全部映射。随后用 transfer learning 把离线通用模型转成目标 VSC 的在线 MOP-admittance model（PDF 物理页 2-4，Fig. 1、Eq. (12)-(18)）[pdf:E02] [pdf:E04]。

## § 5 — 具体方法与完整 Pipeline

以“已知 VSC I 帮助识别黑箱 VSC II”为例，完整 pipeline 如下。

1. **建立通用物理骨架。** 对一般 grid-connected VSC 的 filter、current controller、PLL 与数字 delay 做 dq 小信号建模，得到闭环导纳 \(Y_{tcl,dq}^m(s)\)。作者将导纳拆成频率相关函数与稳态运行点相关项，而不是直接把解析模型当作最终目标机模型（PDF 物理页 3-4，Section III-A 与 Eq. (1)-(18)）[pdf:E03] [pdf:E04]。
2. **重构并离线训练 ANN。** 网络输入为扰动频率 \(f_p\) 和运行点 \(I_d,I_q,V_d,V_q\)。Layer I 用频率学习 \(F_1(s)\) 至 \(F_5(s)\)，Layer II 实现运行点与这些函数的组合 \(G\)，Layer III 计算 dq 导纳四个元素的 magnitude 与 phase。通用 VSC 仿真产生密集数据，训练得到 offline MOP-admittance model（PDF 物理页 4-5，Eq. (17)-(18) 与 Fig. 5）[pdf:E04] [pdf:E05]。
3. **在目标机取得端口数据。** 在 PCC 对同一频率做两次独立电流扰动，测量电压、电流响应；用 Park transform 从 abc 转到 dq，再用 FFT 取出注入频率处的复数分量，解一个 \(2\times2\) 线性方程得到 \(Y_{dd},Y_{dq},Y_{qd},Y_{qq}\)。作者把扰动幅值设为运行点电流的 5%，理由是在不明显移动运行点与不过度受噪声影响之间折中（PDF 物理页 5，Fig. 6-7、Eq. (19) 及相邻正文）[pdf:E05]。
4. **迁移到黑箱目标 VSC。** 把少量目标测量送入已训练网络继续训练，得到目标机的 online MOP-admittance model。作者把 source domain 写成通用机仿真数据、target domain 写成目标机现场测量数据，并假定两者输入边际分布可以被安排为相同（PDF 物理页 5-6，Section III-B）[pdf:E05] [pdf:E06]。Case study 随后把这一步具体化为 VSC I 的密集离线频率/电流网格与 VSC II 的稀疏在线网格，并与普通 ANN 的误差曲面比较（PDF 物理页 8，Section IV-A、Fig. 13-14）[pdf:E07]。
5. **用于稳定性判断。** 在所需运行点查询目标导纳模型，与 grid impedance 组成 return ratio，扫描 eigenlocus 并用 GNC 判断稳定/不稳定；论文最后用两个运行点的硬件实验验证了预测方向（PDF 物理页 9-11，Section IV-C、Fig. 19-21）[pdf:E08] [pdf:E09] [pdf:E10]。

论文没有报告 switch-level event handling、离散时间推进算法、多速率调度、fixed-point/浮点数值格式、网络训练并行化、FPGA 映射、资源占用、时序收敛、实时步长或在线更新 latency。实际实验用 dSPACE DS1007 控制 VSC、Chroma 61845 作为 grid simulator；这证明了 converter-grid 稳定性实验，不等于证明识别训练已在 FPGA 或实时控制器上在线执行（PDF 物理页 10，Fig. 20 与相邻正文）[pdf:E09]。

## § 6 — 核心数学推导（无形式化数学则跳过）

先给直观背景。dq 小信号模型把三相正弦量变成同步旋转坐标系中的近直流量；在某个稳态运行点附近线性化后，端口电压微扰 \(\Delta V_{dq}\) 与电流微扰 \(\Delta I_{dq}\) 由一个 \(2\times2\) 频域导纳矩阵联系。对该矩阵的四个元素建模，才能保留 d/q 轴自导纳和交叉耦合。

**1. 数字 delay 与 PLL 动态。** 作者把采样计算延时 \(T_s\) 和 PWM 的 \(0.5T_s\) 合并为

\[
G_{\mathrm{del}}(s)=e^{-1.5T_s s}.
\]

同步坐标系 PLL 的线性化写成

\[
\Delta\theta=G_{\mathrm{PLL}}(s)\Delta V_q,\qquad
G_{\mathrm{PLL}}(s)=
\frac{s k_{p\text{-pll}}+k_{i\text{-pll}}}
{s^2+\left(s k_{p\text{-pll}}+k_{i\text{-pll}}\right)V_d}.
\]

\(k_{p\text{-pll}}\) 与 \(k_{i\text{-pll}}\) 分别是 PLL 的比例、积分参数；这些关系再进入 current/voltage 的 dq 变换线性化（PDF 物理页 3，Eq. (1)-(9)）[pdf:E03]。

**2. 闭环导纳。** 合并 filter、controller、delay 与 PLL 路径后，作者得到

\[
Y_{tcl,dq}^{m}(s)
=
\left[I^{m}+T_{dq}^{m}(s)\right]^{-1}Y_{to,dq}^{m}(s)
-G_{cl,dq}^{m}(s)Y_{\mathrm{PLL}}^{m}(s).
\]

这里 \(I^m\) 是单位对角矩阵；\(T_{dq}^{m}\) 表示 current-loop 前向动态，\(Y_{to,dq}^{m}\) 汇集 filter 与 PLL 耦合前的端口关系，\(G_{cl,dq}^{m}\) 是闭环电流通道，\(Y_{\mathrm{PLL}}^{m}\) 是 PLL 引入的耦合项。工程含义是：端口导纳同时受 plant/filter、本地闭环控制与 PLL 坐标扰动影响，并随稳态运行点、频率和控制参数变化（PDF 物理页 4，Eq. (11)-(12)）[pdf:E04]。

**3. 把物理式变成网络结构。** 作者进一步写成

\[
Y_{dq}^{m}(s)=
\left[
O_{dq}^{m}(s)
-P_{dq}^{m}(s)V_{s,dq}^{m}
-Q_{dq}^{m}(s)I_{s,dq}^{m}
\right]
\left[R_{dq}^{m}(s)\right]^{-1}.
\]

以 \(Y_{dd}\) 为例，

\[
Y_{dd}(s)=F_1(s)-V_qF_2(s)-V_dF_3(s)-I_qF_4(s)-I_dF_5(s)
=G\!\left[V_q,V_d,I_q,I_d,F_1(s),\ldots,F_5(s)\right].
\]

这一步把“频率函数” \(F_1\ldots F_5\) 与“运行点组合” \(G\) 分开，直接对应网络 Layer I 和 Layer II；Layer III 再取 magnitude 与 phase。物理知识压缩 ANN 的含义就在这里：不是给 loss 增加一个抽象物理惩罚，而是删除与该函数分解不一致的自由连接（PDF 物理页 4，Eq. (13)-(18)）[pdf:E04]。

**4. 从两次扰动解导纳。** 令两次独立注入在 \(f_p\) 处形成两列电压响应和两列电流响应，则核心关系是

\[
Y_{dq}^{m}(f_p)
=
\begin{bmatrix}
V_{d1}(f_p) & V_{d2}(f_p)\\
V_{q1}(f_p) & V_{q2}(f_p)
\end{bmatrix}^{-1}
\begin{bmatrix}
I_{d1}(f_p) & I_{d2}(f_p)\\
I_{q1}(f_p) & I_{q2}(f_p)
\end{bmatrix}.
\]

但必须保留一个原文不一致：Eq. (19) 的 PDF 版右下角印成 \(I_{q1}(f_p)\)，紧邻正文却明确把第二次注入的该量写成 \(I_{q2}(f_p)\)。上式按“两次独立响应各占一列”的物理关系展示，正式复现前仍应查作者代码或勘误，不能把本卡的解释当作已认证更正（PDF 物理页 5，Eq. (19) 与前置正文）[pdf:E05]。

## § 7 — 实验设计与结论

- **问题 1：物理结构是否能在相同控制拓扑、不同参数的黑箱 VSC 上减少小样本误差？** 实验把 VSC I 设为已知 source、VSC II 设为黑箱 target。两者都是 PI current control + PLL，但参数明显不同，例如 switching frequency 为 20 kHz/10 kHz，inverter inductance 为 1 mH/3 mH；完整参数见 Table I（PDF 物理页 6，Table I）[pdf:E06]。VSC I 离线数据覆盖 \(f_p=1\) 至 100 Hz、1 Hz 间隔和 \(I_d=20\) 至 70 A、1 A 间隔；VSC II 在线只测 200 个点，候选网格为 \(f_p=1\) 至 101 Hz、5 Hz 间隔和 \(I_d=20\) 至 70 A、5 A 间隔。验证数据更密，为 \(f_p=1\) 至 100 Hz、0.1 Hz 间隔和 \(I_d=20\) 至 70 A、0.1 A 间隔（PDF 物理页 8-9，Section IV-A、Fig. 13-14）[pdf:E07] [pdf:E08]。作者报告 proposed model 与 field-measured data 的误差小于 1%，而相同稀疏数据训练的随机初始化 two-hidden-layer ANN 表现较差。
- **问题 2：先验来自标准 PI VSC 时，能否迁移到控制结构未知且含 active damping 的 LCL target？** 作者把 target 改成 active-damping-controlled LCL VSC，给出 grid-side inductor \(L_2=3\) mH、filter capacitor \(C=5\,\mu\mathrm{F}\)，仍以 VSC I 仿真数据离线训练，再用 target field measurement 迁移。作者再次报告 Fig. 18 的识别误差小于 1%，据此声称可从标准 PI source 迁移到未知控制结构 target（PDF 物理页 9-10，Section IV-B、Fig. 16-18）[pdf:E08] [pdf:E09]。
- **问题 3：识别模型能否给出正确的稳定性方向？** grid inductor 设为 18 mH；Table II 的 case a 为 \(I_d=18\) A、\(I_q=0\) A、\(V_d=311\) V，预测不稳定，case b 为 \(I_d=15\) A、\(I_q=8\) A、\(V_d=311\) V，预测稳定。GNC eigenlocus 与实验波形方向一致：case a 三相电流明显畸变/振荡，case b 近似稳定正弦（PDF 物理页 9-11，Table II、Fig. 19-21）[pdf:E08] [pdf:E09] [pdf:E10]。

这些实验支持“在作者选择的两个 source-target 关系和两个稳定性运行点上有效”，不能外推为任意未知控制结构都可迁移。论文也没有报告 ANN 宽度、optimizer、learning rate、epoch、初始化 seed、训练时间、在线计算资源、噪声敏感性或多次重复统计。另一个报告边界是：正文用“less than 1%”描述 Fig. 13 与 Fig. 18，但图轴分别标为 magnitude error (dB) 与 phase error (deg)，没有定义如何从这些轴量转换成百分比误差；因此“小于 1%”只能按作者原始 claim 记录，不能视为已闭合的统一误差指标（PDF 物理页 8-10，Fig. 13-14、Fig. 18 与相邻正文）[pdf:E07] [pdf:E08] [pdf:E09]。

## § 8 — Take-aways

**5 句话版：**

1. 论文把通用 VSC 的小信号导纳分解直接编码进 ANN 拓扑，以减少在线黑箱识别所需的数据。
2. offline 阶段从通用 VSC 仿真中学习频率相关函数，online 阶段用目标 VSC 的少量 PCC 扰动数据校正模型。
3. 在同拓扑异参数和 active-damping LCL 两个 target 上，作者都报告 proposed model 的识别误差小于 1%，但没有给出百分比误差定义。
4. 识别出的 MOP-admittance model 在两个运行点上给出了与硬件波形一致的稳定性方向。
5. 最关键的未决项不是“网络能否拟合”，而是通用 VSC 的物理先验何时仍适用于结构未知的 target，以及 online 更新是否真的满足部署 latency。

**3 句话版：**

1. 这是一个以解析结构约束网络连接的 physics-informed ANN，而不是以方程 residual 约束 loss 的典型 PINN。
2. 它用离线仿真先验换取在线小样本效率，并在两个实验对象上展示了可行性。
3. 但 transfer validity、误差定义、训练复现细节和实时执行代价仍未闭合。

**1 句话版：**

论文证明了“VSC 导纳的结构化先验可以帮助小样本迁移”这一有价值的实验信号，但尚未证明该先验对任意黑箱 VSC 都安全，也未证明识别过程具备可部署的实时性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**从通用 VSC 解析式得到的频率/运行点函数分解，对控制和 filter 结构未知的 target 仍是正确或至少无害的 inductive bias。** 如果 target 的关键动态无法由 \(F_1\ldots F_5\) 与 \(G\) 的既定组合表达，transfer learning 不是从好起点微调，而是在错误函数族内强行拟合；稀疏样本反而可能让错误先验在未测频点保持得更牢。

论文为该假设提供的证据是：source 与 PI target 的参数差异较大，且同一 source 还成功迁移到一个 active-damping LCL target，二者的报告误差均小于 1%（PDF 物理页 6、9-10，Table I 与 Section IV-A/B）[pdf:E06] [pdf:E08] [pdf:E09]。但作者在 transfer-learning 论述中只说 source/target 输入分布 \(P(X_s)=P(X_t)\) 可以容易保证；相同输入采样分布并不能保证条件映射 \(P(Y\mid X)\) 相近，更不能保证隐藏的 resonance、delay、saturation 或 mode switching 落在同一函数族（PDF 物理页 6，Section III-B）[pdf:E06]。缺失证据包括：结构差异的系统化扫描、先验失配检测、分布外不确定度、窄带 resonance 附近的自适应采样，以及错误模型对 GNC 稳定性结论的最坏影响。

## § 10 — 最小复现实验

一周内最值得复现的是“相同 200 个 target 点下，结构化 ANN 是否比自由 ANN 更可靠”，无需先搭完整硬件。

1. 在 MATLAB/Simulink 或 Python control environment 中建立论文 Table I 的 VSC I、VSC II 平均小信号模型；按论文范围生成 source dense grid、target 200-point sparse set 和不参与训练的 dense validation grid。VSC 参数与采样范围直接按 PDF 物理页 6、8-9 的 Table I 和 Section IV-A 设置 [pdf:E06] [pdf:E07] [pdf:E08]。
2. 实现两个模型：按 Eq. (17)-(18)/Fig. 5 的 structured ANN，以及参数量尽量匹配的 two-hidden-layer ANN。两者使用完全相同的 target 点、optimizer budget 和至少 10 个随机 seeds。
3. 不沿用论文未定义的“1%”口径，预先定义复数矩阵相对误差
   \[
   e_Y=\frac{\lVert \hat Y-Y\rVert_F}{\lVert Y\rVert_F},
   \]
   并同时报告每个矩阵元素的 magnitude/phase error、95th percentile、最坏频点和 GNC 稳定性误分类率。
4. **支持核心 claim 的结果：** structured ANN 在大多数 seeds 上的 dense-grid median 与 95th-percentile \(e_Y\) 都显著低于自由 ANN，并在 case a/b 复现正确的稳定性方向；若优势只存在于训练点、对 seed 不稳定，或 GNC 分类没有改善，则反驳“小样本结构先验带来可靠在线识别”的强版本。

这个最小实验还应把 Eq. (19) 的 \(I_{q1}/I_{q2}\) 下标不一致记录为实现决策，并用矩阵维度与合成数据单独验证两次独立扰动的解算，否则可能把排版问题误当作模型误差（PDF 物理页 5，Eq. (19)）[pdf:E05]。

## § 11 — 最强反例设计

最强反例不是简单增加噪声，而是构造**输入边际分布相同、条件导纳映射不同**的 target。保持论文的 \(f_p\)、\(V_d,V_q,I_d,I_q\) 采样范围不变，在 target 中加入一个 source 模型没有的窄带 active-damping/notch 动态，并让其 resonance 落在 5 Hz 稀疏采样网格之间；再加入随运行点移动的 digital delay 或 saturation，使该窄峰决定 GNC 是否包围 \((-1,0)\)。这样 \(P(X_s)=P(X_t)\) 仍可由实验设计满足，但 \(Y(f,\mathrm{op})\) 的局部结构不再服从 source 的平滑先验。

用相同 200 点分别训练 proposed structured ANN、自由 ANN 和一个带不确定度的局部模型，在密集频扫上检查被漏掉的 resonance 以及 stability classification。若 structured ANN 在训练/平均误差上仍很好，却在 resonance 附近给出错误稳定性结论，而自由或不确定度模型能报警，这将直接推翻“部分物理 + 相同输入分布足以支撑未知结构在线识别”的核心泛化解释。该攻击针对的是作者从 active-damping 单个 case 推向“unknown control structure”的外推，而不是否认论文现有两例本身（PDF 物理页 9-11，Section IV-B/C、Fig. 16-21）[pdf:E08] [pdf:E09] [pdf:E10]。

## § 12 — Follow-up Research Idea

**候选方向：从“总要输出一个在线导纳模型”改成“带 transfer-validity certificate 的主动在线识别”。** 这里不声称 novelty；本卡没有联网补充相关工作，必须先检索 safe transfer learning、active impedance measurement、set-membership identification 和 robust stability certification 的交叉文献。

**(a) 未满足需求。** 实际运营者需要知道的不只是 \(\hat Y\)，还需要知道 source physics 是否仍适用于当前 target、未测频带的误差上界是否会改变稳定性判定，以及何时必须追加扰动。论文的硬件结果只覆盖两个运行点，而 Fig. 21 已显示错误分类可能对应从稳定正弦到明显畸变的系统级后果（PDF 物理页 11，Fig. 21）[pdf:E10]。

**(b) 潜在研究价值。** 电力电子领域更看重可验证的稳定性边界、真实 converter 实验和工程可执行性。若模型能在先验失配时拒绝给出过度自信结论，并以最少扰动收紧 GNC margin 的置信界，其贡献会从“更省数据的拟合器”提升为“可安全使用的在线稳定性诊断器”。

**(c) 可借鉴工具。** 可结合 Bayesian/ensemble uncertainty、set-membership frequency-response bounds、safe transfer 的 domain-shift detector，以及 active learning 选择最能缩小 Nyquist uncertainty 的下一扰动频率。解析 VSC 结构仍用作 prior，但不再被视为永远正确的硬拓扑。

**(d) 第一个证伪实验。** 采用 §11 的移动窄带 resonance target，限制总扰动点仍为 200；比较固定 5 Hz 网格与 certificate-driven active probing。若新方法不能在相同预算下更早发现 prior mismatch、不能覆盖真实 \(Y\)，或最终 GNC 分类错误率没有下降，就应否定这个方向。

**(e) 与本文的实质区别。** 本文优化的是“给定 source prior 和少量 target 数据，怎样得到一个点估计模型”；新问题是“怎样判定这次 transfer 是否可信，并把有限测量主动分配给会改变稳定性结论的区域”。后续若考虑 FPGA，应先报告实际 online inference/update graph、precision、资源、latency 与 sampling schedule，再讨论映射；本文没有提供这些信息，不能直接沿用其 online 表述作为 FPGA feasibility 证据。
