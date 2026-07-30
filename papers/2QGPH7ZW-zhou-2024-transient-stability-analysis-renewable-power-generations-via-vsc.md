# Transient Stability Analysis of Renewable Power Generations via VSC-HVDC

作者：Xu Zhou，Li Guo，Xialin Li，Zhi Wang，Jiebei Zhu，Chengshan Wang  
出处：IEEE Transactions on Industrial Electronics，Vol. 72，No. 5，pp. 4889–4899  
年份：2024（在线发表；卷期版本为 2025 年 5 月）  
DOI：10.1109/TIE.2024.3476958  
Zotero key：2QGPH7ZW  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究一种具体但越来越常见的失稳场景：大规模 renewable power generation（RPG）通过 VSC-HVDC 送出，RPG 侧采用 grid-following 的 \(U_{\mathrm{dc}}-v_{\mathrm{ac}}\) 控制和 PLL，送端 VSC-HVDC 侧采用 grid-forming 的 \(V/f\) 控制。大功率阶跃发生后，两侧变流器不是两个可分别判断稳定性的独立装置；RPG 的 PLL、直流电压外环与 VSC-HVDC 的电压环共同改变 PCC 电压、相角和功率，因此会出现 transient synchronization instability。作者的目标是把这种多控制环、强非线性的动态耦合压缩为可解释的等效运动方程，再用加速面积与减速面积判断首摆稳定性，并把判断结果扩展成 power feasible region（PFR）。论文摘要明确把 reduced-order model、equivalent motion equation、面积判据、PFR 和 RT-LAB 验证列为完整贡献链。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要之处不只在于“故障后有没有平衡点”。论文给出的关键反例是：300 MW 先升到 500 MW、再升到 587 MW时系统能够稳定，而 300 MW 一步升到 587 MW时却失步；也就是说，相同的最终功率附近可以存在小扰动稳定平衡点，但到达它的暂态轨迹仍可能越过同步边界。[pdf:E07]（PDF 物理页 4，Section II-C，Fig. 3）对工程运行而言，这意味着静态额定值或小信号稳定性不能直接回答“允许多大的功率突变”；PFR 的价值正是把初始功率 \(P_0\)、扰动后功率 \(P_1\) 与暂态可接受性连成一张运行边界图。

系统对象也决定了这不是传统同步机 EAC 的直接套用。Fig. 1 显示 RPG 侧的 PLL、\(U_{\mathrm{dc}}\) 外环和 \(v_{\mathrm{ac}}\) 外环，与 VSC-HVDC 侧的双闭环 \(V/f\) 控制经线路和 PCC 相互作用。[pdf:E03]（PDF 物理页 2，Section II-A，Fig. 1）因此真正需要回答的是：在“电压由 grid-forming 端建立、相位由 grid-following 端跟随”的混合系统里，哪些控制动态进入等效加速功率，怎样据此判稳，以及参数变化如何移动安全功率边界。

## § 2 — 前人工作与不足

论文把此前工作分成三层。第一层是 weak-grid-connected VSC 的 PLL 同步稳定性研究，常用 phase trajectory、EAC 或 Lyapunov direct method；作者认为这些对象阶次较低、系统间耦合较弱，所以已有工具相对成熟。第二层开始讨论 grid-following 与 grid-forming 混合系统，但常把 grid-following 端约化为只保留 PLL 的受控电流源，把 grid-forming 端看成只保留稳态 droop 的理想电压源。第三层关注风电场或太阳能-储能系统中的直流电压动态，但没有同时保留 VSC-HVDC 侧非理想电压控制动态以及两类变流器外环之间的作用。[pdf:E02]（PDF 物理页 1，Introduction）

具体而言，论文指出文献 [15] 只分析 MMC-connected wind farm 的 PLL，忽略 \(V/f\) 动态；文献 [16] 对两类变流器的约化过强；文献 [19] 更关注 RPG 侧 dc-link voltage control，没有建立两类变流器的完整 interaction mechanism。论文还认为，多控制环耦合后模型变成高阶强非线性系统，传统 EAC 或 Lyapunov 法不能直接使用，而纯数字积分虽然可判断轨迹，给出结论较晚。[pdf:E02]（PDF 物理页 1，Introduction）这些是论文对 prior work 的陈述，本卡没有用外部全文独立复核。

作者声称的差异有两个：一是把 EAC 与 numerical integration 组合，使随控制状态变化的“机械功率/电磁功率”曲线仍可用于面积判据；二是首次构造考虑交互耦合的 RPG PFR。[pdf:E01][pdf:E02]（PDF 物理页 1，Abstract 与 Introduction；物理页 2 顶部的贡献续文）“首次”是作者原文 claim，不是本卡完成 novelty search 后的结论。

## § 3 — 重建作者的思考路径

可以从论文之前已经存在的知识和一个异常现象逆向重建这条路线。传统 EAC 的吸引力在于，它把暂态稳定转换为“扰动给系统增加了多少动能、之后又能消掉多少”的几何问题；但这里的 grid-forming 端电压幅值 \(V_m\) 会被电压环动态改变，grid-following 端的注入电流也会被直流电压和交流电压外环改变，因此功率-相角曲线本身会随时间移动，不能预先画成一条固定正弦曲线。

下一步自然是保留最可能决定同步时间尺度的状态，同时去掉更快的动态：假定 RPG 侧电流内环已经跟踪参考值，忽略滤波器和线路的 electromagnetic transients，但保留 \(U_{\mathrm{dc}}\) 外环、PLL 以及 VSC-HVDC 电压环。这样得到单 RPG 的六阶模型。[pdf:E04][pdf:E06]（PDF 物理页 2，Section II-B；物理页 3，Eq. (10)–(11)）作者先用 detailed switching model 对三个功率阶跃工况验证这个 reduced-order model，观察到约化曲线与详细模型的 \(V_t\)、\(\Delta\theta\)、\(U_{\mathrm{dc}}\)、\(V_{tq}\) 波形接近，同时保留了直接 300→587 MW 时的失稳现象。[pdf:E07]（PDF 物理页 4，Fig. 3）

有了可信的同步尺度模型，作者把 RPG PLL 相角相对 VSC-HVDC 参考相角的差 \(\delta_{\mathrm{pll},k}\) 写成 rotor-like motion equation，并把等效输入拆成 RPG 自身控制产生的 self-coupling、VSC-HVDC 电压控制产生的 synchronous coupling、以及其他 RPG 产生的 mutual coupling。然后不再尝试给高阶系统构造闭式能量函数，而是沿数值轨迹更新这些项，对第一摆的加速区和减速区做积分。[pdf:E08][pdf:E09]（PDF 物理页 4，Eq. (13)–(17)；物理页 5，Fig. 4 与 Eq. (18)–(19)）

最后，把一次“给定 \(P_0,P_1\) 是否稳定”的分类器放进二分搜索，就能对每个初始功率求允许的最大扰动后功率，再扫出 PFR。这个思考路径的核心不是发明新的时域模型，而是把高阶数值模型当作随轨迹更新功率曲线的生成器，再借用 EAC 的可解释面积作为提前判据。

## § 4 — 核心 Intuition

把 grid-following RPG 相对 grid-forming VSC-HVDC 的相角差看成“等效转子角”：功率突变先让等效输入大于等效输出，轨迹获得加速面积；随后只有足够的减速面积把这部分“动能”还回去，系统才会回到同步。与经典 EAC 不同，论文不假设 \(V_m\) 或功率-相角曲线固定，而是由六阶控制模型数值更新，再沿实际轨迹积分。[pdf:E08][pdf:E10]（PDF 物理页 4，Eq. (13)–(14)；物理页 5，Eq. (20)）

普通语言说，论文把“多环控制器在功率阶跃后互相拉扯”的问题，转换成“这次拉扯一共把相角推了多远，后续制动力够不够”的问题。PFR 则把这个单次判断批量运行，得到每个起点还能安全迈多大一步。

## § 5 — 具体方法与完整 Pipeline

以论文的单 RPG 场景为例，输入是系统主电路与控制参数、扰动前稳定运行点 \(P_0\)、扰动后参考功率 \(P_1\)，输出是暂态同步稳定/失稳分类；外层再输出 PFR。

1. **建立控制拓扑。** RPG 侧用 PLL 对齐 PCC 电压 \(V_s\)，有 \(U_{\mathrm{dc}}-i_{d,\mathrm{ref}}\) 与 \(v_{\mathrm{ac}}-i_{q,\mathrm{ref}}\) 外环；VSC-HVDC 侧用 voltage/current double closed loop 建立 \(V_m\) 和频率参考。[pdf:E03]（PDF 物理页 2，Fig. 1）
2. **约化到同步时间尺度。** 作者忽略 RPG 电流内环动态，假设 \(i_d,i_q\) 已跟踪参考；同时忽略滤波器和线路的 electromagnetic transients，并明确“小信号稳定、存在稳定平衡点”是后续分析的前提。[pdf:E04]（PDF 物理页 2，Section II-B）
3. **计算电气量与控制状态。** RPG 端被表示为受控电流源，VSC-HVDC 的 \(V/f\) 电压环和 RPG 的 \(U_{\mathrm{dc}}\)、PLL 动态共同决定 \(V_t,V_m\) 与相角。Eq. (5)–(9)给出电压环电流参考、RPG 电流参考、dc-link voltage 与 PLL 积分关系。[pdf:E05]（PDF 物理页 3，Fig. 2，Eq. (1)–(9)的采用范围）
4. **推进六阶模型。** 单 RPG 状态包含 \(U_{\mathrm{dc}}\)、\(I_{td,\mathrm{ref}}\)、PLL 相角 \(\theta_{\mathrm{pll}}\)、PLL 积分状态 \(x_{\mathrm{pll}}\)、以及 VSC-HVDC 侧 \(I_{md,\mathrm{ref}},I_{mq,\mathrm{ref}}\)。Eq. (10)–(11)给出其微分方程和耦合系数。[pdf:E06]（PDF 物理页 3，Eq. (10)–(11)）
5. **构造等效运动与耦合项。** 令 \(\delta_{\mathrm{pll},k}=\theta_{\mathrm{pll},k}-\theta_m\)，把等效输入 \(P_{mk}\) 分成 self-coupling \(P_{mkt}\)、synchronous coupling \(P_{mks}\) 和 mutual coupling \(P_{mkjs}\)。单 RPG 时 \(P_{mkjs}=0\)；多 RPG 时其他变流器的电流、相角和线路阻抗通过该项进入。[pdf:E08][pdf:E09]（PDF 物理页 4，Eq. (13)–(17)；物理页 5，Eq. (18)–(19)）
6. **沿第一摆积分判稳。** 从扰动前平衡点 \(a\) 出发，跟踪 \(\Delta P_k=P_{mk}-D_k\Delta\omega_{\mathrm{pll},k}-P_{ek}\)。在第一次 \(\Delta P_k=0\) 前积出 \(S_{\mathrm{acc},k}\)，再到相角首次达到极值的点 \(c\) 积出 \(S_{\mathrm{dec},k}\)。作者以 \(\Delta S_k=S_{\mathrm{acc},k}-S_{\mathrm{dec},k}=0\) 为稳定条件，否则判失稳。[pdf:E09][pdf:E10]（PDF 物理页 5，Fig. 4 与 Eq. (20)）
7. **构造 PFR。** 对固定 \(P_0\)，令二分上界 \(a=P_n\)、下界 \(b=P_0\)，用面积判据测试中点 \(P_1=(a+b)/2\)，直至区间不超过 \(P_{\mathrm{err}}=5\) MW，输出 \(P_{1,\max}\)。扫描不同 \(P_0\) 形成 \(\Omega_t\)。[pdf:E12]（PDF 物理页 6，PFR Algorithm 与 Eq. (21)）

论文报告的数值实现是 PSCAD/EMTDC detailed switching simulation、六阶连续时间模型和 RT-LAB HIL；附录说明控制算法运行在 TI DSP28335 上，control period 为 100 \(\mu\mathrm{s}\)。[pdf:E20]（PDF 物理页 10，Table A1 与 Fig. A1）论文没有报告求解器、积分步长、面积积分的数值容差、multirate 处理、定点数位宽、FPGA 映射、FPGA 资源、时序收敛或实时步长裕量。因此这是一篇 EMT/控制稳定性与 HIL 论文，不是 FPGA 实现论文；不能从 DSP 的 100 \(\mu\mathrm{s}\) 控制周期外推出 FPGA 可实现性。

## § 6 — 核心数学推导（无形式化数学则跳过）

第一层是 dc-link energy balance。论文的 Eq. (7) 为

\[
\frac{dU_{\mathrm{dc}}}{dt}
=\frac{P_{\mathrm{ref}}-P_{\mathrm{dc}}}{C_{\mathrm{dc}}U_{\mathrm{dc}}}.
\]

它表达的物理意义很直接：输入功率参考与交流侧送出功率不相等时，差额先充放直流电容，\(U_{\mathrm{dc}}\) 的变化再经 PI 外环改变 \(I_{td,\mathrm{ref}}\)。PLL 的角度与积分状态、VSC-HVDC 电压环的 \(d/q\) 电流参考一起构成 Eq. (10) 的六阶状态模型。[pdf:E05][pdf:E06]（PDF 物理页 3，Eq. (7)、(10)–(11)）

第二层是把相对相角动态写成等效运动方程。按 Eq. (13) 的符号，可压缩为

\[
J_k\Delta\dot{\omega}_{\mathrm{pll},k}
=P_{mkt}+P_{mks}+P_{mkjs}
-D_k\Delta\omega_{\mathrm{pll},k}-P_{ek},
\]

\[
J_k=\frac{1}{k_{ik}},\qquad
D_k=\frac{k_{pk}}{k_{ik}}V_m\cos\delta_{\mathrm{pll},k},
\]

\[
P_{ek}
=\left(V_m+\frac{k_{pk}}{k_{ik}}\dot V_m\right)
\sin\delta_{\mathrm{pll},k}.
\]

这里 \(k_{pk},k_{ik}\) 是 PLL 的 proportional/integral gains。最关键的一项是 \(\dot V_m\)：它说明 VSC-HVDC 电压环不只是慢慢改变稳态电压，还直接进入等效 electromagnetic power，所以把 grid-forming 端近似成恒压源会漏掉暂态耦合。[pdf:E08]（PDF 物理页 4，Eq. (13)–(17)）

第三层是面积判据。作者把 \(a\to b\) 定义为加速段、\(b\to c\) 定义为减速段，分别积分 self/synchronous/mutual coupling 与 \(P_{ek}+D_k\Delta\omega\) 的差，得到

\[
\Delta S_k
=S_{\mathrm{acc},k}-S_{\mathrm{dec},k}
=\Delta S_{mk}-\Delta S_{ek}.
\]

作者规定 \(\Delta S_k=0\) 时 transient synchronization stable，否则 unstable。[pdf:E10]（PDF 物理页 5，Eq. (20)）Fig. 4 的几何意义是：\(a\to b\) 的橙色面积把相角推快；\(b\to c\) 的蓝色面积必须完整吸收它，轨迹才会在 \(c\) 点速度归零并回到新平衡。[pdf:E09]（PDF 物理页 5，Fig. 4）需要注意，正文没有给出数值计算中“等于零”的容差；Table II 对稳定工况报告的是相等到两位小数，而不是严格的解析恒等式。

第四层是运行边界。论文用

\[
\Omega_t
\triangleq
\{P\in\mathbb{R}\mid
\boldsymbol{x}_{P_0}\in\Omega_s(\boldsymbol{x}_{P_0+\Delta P}),
\ P\le P_n\}
\]

描述 PFR，并用 5 MW 终止宽度的二分算法寻找每个 \(P_0\) 的 \(P_{1,\max}\)。[pdf:E12]（PDF 物理页 6，Eq. (21) 与 Algorithm）它更接近一个由数值分类器采样得到的 operational envelope，而不是有闭式边界证明的 invariant set。

## § 7 — 实验设计与结论

**问题 1：六阶约化模型是否保留了核心失稳现象？**  
实验：在 PSCAD/EMTDC detailed switching model 与 Eq. (10) reduced-order model 中施加三种 dc-side power step：300→500 MW、500→587 MW、300→587 MW，比较 \(V_t\)、相角、\(U_{\mathrm{dc}}\) 和 \(V_{tq}\)。  
答案：前两种稳定、最后一种失稳，约化模型曲线与详细模型在三种工况下接近。[pdf:E07]（PDF 物理页 4，Fig. 3）这支持模型用于这些大功率阶跃的同步稳定分析，但论文没有报告逐点误差、最大偏差或更广参数域的 fidelity metric。

**问题 2：面积判据能否解释并区分三种工况？**  
实验：对三个 case 计算 \(S_{\mathrm{acc}}\) 与 \(S_{\mathrm{dec}}\)。  
答案：case 1 为 9.79 对 9.79，case 2 为 4.12 对 4.12，均判稳定；case 3 为 27.64 对 9.60，判失稳。[pdf:E10][pdf:E11]（PDF 物理页 5，Table I 与 Eq. (20)；物理页 6，Table II）这些结果与 Fig. 3 的时域分类一致。Table II 的 \(S_{\mathrm{dec}}\) 符号与 Eq. (20) 中分项书写存在不够清楚之处：表中用正的“可用减速面积”表达，正文公式的分项若按字面相减会得到相反符号；复现时必须先固定符号约定。

**问题 3：面积法是否比等待相角越界更早给出失稳结论？**  
实验：case 3 中，对比到减速面积完成时的点 A 与传统时域判据 \(\delta>\pi\) 且继续增加的点 B。  
答案：作者在 Fig. 8 报告 A 为 0.48 s、B 为 0.83 s，因此称所需仿真时长缩短。[pdf:E11][pdf:E13]（PDF 物理页 6，Section III-C；物理页 7，Fig. 8）这证明的是“沿同一轨迹更早形成分类”，不是实际 CPU/GPU wall-clock 加速；论文没有报告每种方法的运算量、执行时间或硬件资源。

**问题 4：PFR 能否预测主电路参数变化后的稳定边界？**  
实验：改变 RPG 线路电感 \(L_{tf}=0.45,0.47,0.50\) H，并在 RT-LAB 上测试 100→500 MW。  
答案：论文文字与 Fig. 10–11 表明 0.45/0.47 H 工况保持稳定，而 0.50 H 工况失稳，HIL 波形与 PFR 的方向一致。[pdf:E14]（PDF 物理页 7，Fig. 9–11 与 Section IV-B）作者另报告 \(P_0=300\) MW 时最大上升功率约为 285 MW，即直接到 585 MW仍在边界内。[pdf:E12]（PDF 物理页 6，Section IV-A）这个边界以 5 MW 二分终止宽度得到，不应解释成小于 5 MW 精度的精确安全极限。

**问题 5：外环、PLL 与 VSC-HVDC 电压环参数是否会移动 PFR？**  
实验：分别扫描 \(k_{pvac}\)、\(k_{pudc}\)、PLL 的 \(k_{ppll},k_{ipll}\) 以及 VSC-HVDC 电压环 \(k_{pmv},k_{imv}\)，选取若干 operating point 做 RT-LAB 验证。  
答案：Fig. 12–17 显示所有这些参数都会明显改变 PFR，而不是只有 RPG 侧 PLL 参数起作用。[pdf:E15][pdf:E16]（PDF 物理页 8，Fig. 12–17）较清楚的两组结果是：100→550 MW时 \(k_{ppll}=0.03\) 失稳、\(0.10\) 稳定；100→500 MW时 \(k_{pmv}=0.17\) 失稳、\(0.07\) 稳定。[pdf:E17][pdf:E18]（PDF 物理页 9，Fig. 18 及相邻正文）

但这一部分存在必须保留的原文不一致：Fig. 13 caption 写 \(k_{pvac}=0.01/0.03\)，正文一处写 \(0.01/0.001\)，且相邻段落对 \(k_{pvac}=0.01\) 在 200→500 MW 下的稳定性表述互相冲突；Fig. 14 caption 写 \(k_{pudc}=0.03/0.003\)，正文又写 \(0.01/0.001\)；Fig. 17 caption 仍称 “PLL control parameters”，但图中变量实际是 \(k_{pmv},k_{imv}\)；Fig. 18 caption 把第二个 \(k_{pmv}=0.17\) 误写为 \(k_{ppll}=0.17\)，而图内标注和正文均指向 \(k_{pmv}\)。[pdf:E15][pdf:E16][pdf:E17]（PDF 物理页 8–9，Fig. 13–18）因此本卡只接受“这些参数会改变 PFR”以及上述图内/正文相互一致的 PLL、\(k_{pmv}\) 两组分类，不把全部外环参数数值当作已无歧义闭合的实验记录。

**问题 6：判据能否扩展到多个 RPG-side converters？**  
实验：在 PSCAD/EMTDC 中建立 \(N=3\) 的系统，三台 VSC 控制与容量相同，但线路电感分别为 0.50、0.47、0.45 H。300→500 MW时三台均满足面积条件；300→587 MW时仅 VSC1 的 \(S_{\mathrm{acc}}=27.64\) 大于 \(S_{\mathrm{dec}}=9.60\)。  
答案：作者把多机系统条件写成所有 VSC 的 \(S_{\mathrm{acc},k}\le S_{\mathrm{dec},k}\) 必须同时成立；case 4 三台稳定，case 5 因 VSC1 失稳而整体失稳。[pdf:E17][pdf:E18][pdf:E19]（PDF 物理页 9，Table III、Fig. 19–21；物理页 10，Eq. (22)）Table III 第二组标题重复写成 “Case4”，正文明确称其为 case 5，属于表格标签错误。

**实验平台与不得外推的范围。** RT-LAB 实现主电路，TI DSP28335 实现控制，控制周期 100 \(\mu\mathrm{s}\)；额定值为 600 MVA、333 kV、50 Hz，Table A1 给出电容、电感和 PI 参数。[pdf:E20]（PDF 物理页 10，Table A1 与 Fig. A1）论文没有报告 RT-LAB 计算节点型号、模型实时步长、PWM/switching frequency、overrun、重复次数、噪声统计、保护逻辑、限流、饱和、通信延迟或 FPGA 资源；验证也集中于 dc-side power step，不覆盖交流故障、控制模式切换或 current limiting。因而结论不能直接外推到含硬限幅、保护动作和 EMT 快过程的所有 VSC-HVDC 场景。

## § 8 — Take-aways

**5 句话：**

1. 论文证明了在 grid-following RPG 与 grid-forming VSC-HVDC 组合中，暂态同步稳定性同时受两侧控制环影响，不能把送端 VSC 当作恒压背景。[pdf:E19]（PDF 物理页 10，Conclusion）
2. 六阶 reduced-order model 把 dc-link、PLL 和 VSC-HVDC 电压环保留下来，并在三个功率阶跃工况中复现 detailed switching model 的稳定/失稳分类。[pdf:E07]
3. 作者用随数值轨迹变化的等效功率曲线计算加速/减速面积，使高阶强非线性模型仍能获得可解释的首摆判据。[pdf:E08][pdf:E10]
4. 把该判据放入 5 MW 终止宽度的二分搜索即可构造 PFR，用于比较线路和控制参数对允许功率突变的影响。[pdf:E12][pdf:E14]
5. RT-LAB 结果支持若干选定工况，但参数标注不一致、未建模限流与 EMT 快过程、缺少数值容差和性能基准，使 PFR 目前更像经实验支持的设计地图，而非具有完备鲁棒保证的安全证书。

**3 句话：**

1. 核心贡献是把 GFL–GFM 多环耦合翻译成 rotor-like motion equation，再用 numerical trajectory 上的 EAC 判稳。
2. 该判据解释了为什么相同最终功率可因阶跃路径不同而稳定或失稳，并可批量生成 PFR。
3. 最需要谨慎的是 reduced-order assumption 和实验记录一致性；论文尚未证明在 current limit、保护和快速电磁暂态介入时边界仍可靠。

**1 句话：**

这篇论文给出了一个物理可解释、能在 selected HIL cases 中工作的 VSC-HVDC 暂态功率边界方法，但它还不是对实际混合控制与保护逻辑具有鲁棒保证的安全域。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在大功率阶跃的全过程里，RPG 电流内环仍足够快且不进入限流/饱和，滤波器和线路的 electromagnetic transients 也足够快，从而六阶同步时间尺度模型始终是有效的。** 作者明确用这一假设删除 RPG 电流环和网络电磁状态，并要求扰动前后存在小信号稳定平衡点。[pdf:E04]（PDF 物理页 2，Section II-B）

这个假设失败的代价最大，因为面积判据的 \(P_m,P_e,D\) 全部由约化模型生成。实际大功率阶跃会推高电流参考、压低或抬高 dc-link voltage，也可能触发 modulation saturation、current limiter、PLL limiter 或保护模式切换；一旦 \(i_d,i_q\) 不再即时跟踪参考，原来的六阶向量场、相角转折点和面积都同时改变，PFR 可能在最需要保护的边界附近给出错误分类。

论文提供的支持是 Fig. 3 中三个 case 的 switching-model 对照，以及若干 RT-LAB operating points 的稳定方向与 PFR 一致。[pdf:E07][pdf:E14][pdf:E15][pdf:E17]（PDF 物理页 4、7–9）但没有证据说明这些工况触及电流限幅，也没有报告限流阈值、PWM 饱和、保护逻辑或 EMT 尺度误差。因此“约化在 selected cases 中有效”有证据，“约化在 PFR 全边界和保护动作下仍有效”没有证据。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 RT-LAB，而是“面积判据能否重现三种功率阶跃分类，并比 \(\delta>\pi\) 更早给出 case 3 失稳结论”。

使用 Table A1 的 600 MVA、333 kV、50 Hz 与主电路/控制参数，按 Eq. (5)–(12)实现单 RPG 六阶 ODE；初值由 \(P_0\) 下的稳态方程数值求解，因为论文没有直接给出完整初始状态。[pdf:E05][pdf:E06][pdf:E07][pdf:E20]（PDF 物理页 3，Eq. (5)–(11)；物理页 4，Eq. (12)；物理页 10，Table A1）积分 300→500、500→587、300→587 MW 三个 case，同时记录 \(\delta_{\mathrm{pll}}\)、\(P_{mk}-D_k\Delta\omega_{\mathrm{pll}}\)、\(P_{ek}\)，按 Fig. 4 的 \(a,b,c\) 定义计算 \(S_{\mathrm{acc}},S_{\mathrm{dec}}\)。采用 Table II 的结果作为量级对照，但提前声明面积符号和“相等”的数值容差，例如以 \(|S_{\mathrm{acc}}-S_{\mathrm{dec}}|/\max(S_{\mathrm{acc}},S_{\mathrm{dec}})\le 1\%\) 作为复现用工作定义，而不是假装论文已经给出该容差。[pdf:E09][pdf:E10][pdf:E11]（PDF 物理页 5–6）

支持 claim 的最低结果是：前两例相角有界且面积近似平衡，case 3 面积明显不平衡并失步；case 3 的面积分类时刻接近 0.48 s，早于 \(\delta>\pi\) 的约 0.83 s。[pdf:E13]（PDF 物理页 7，Fig. 8）反驳结果是：在合理积分步长和容差变化下分类翻转，或者无法用论文给出的方程与参数恢复三例顺序。复现还应报告 solver、步长、初值求解残差和面积积分规则，补上论文未报告的数值信息。若有现成 EMT 工具，可再做一例 switching-model 对照；没有也不阻碍对核心判据的最小测试。

RT-LAB 与 DSP 参数可以作为后续扩展，而不是一周实验的阻塞项。论文只报告 DSP28335 控制周期 100 \(\mu\mathrm{s}\)，没有给出完整可直接部署的控制代码或实时模型包。[pdf:E20]（PDF 物理页 10，Appendix）

## § 11 — 最强反例设计

最强反例是在论文 PFR 边界附近主动引入**现实的 current limiting 与 controller saturation**，而不是再换一组无约束 PI 参数。选取作者报告的 \(P_0=300\) MW、边界约 \(P_1=585\) MW附近，分别测试 570、580、585、590 MW；在 detailed switching model 或 HIL 中设置不同限流阈值、anti-windup、PWM modulation ceiling，并保留 PLL 与 \(V/f\) 环。对每个工况，一边用论文的无约束六阶模型生成面积/PFR 预测，一边记录实际相角是否失步、何时触发限流、限流持续时间以及 \(V_{\mathrm{ac}},U_{\mathrm{dc}}\)。

这个反例最有力，因为它直接攻击第 9 节的模型闭合条件。若原方法在无约束模型中预测稳定，但硬件因为限流导致 \(P_e\) 不足而失步，PFR 不是保守安全边界；反过来，若限流削弱加速功率并使系统保持稳定，而原模型判失稳，PFR 又会过度保守。只要在可重复的边界工况中出现稳定类别错配，就能推翻“现有 PFR 可直接指导 protection strategy design”的强版本，而不只是说明精度稍差。

论文现有实验没有报告限流、饱和与保护设置，因此这一反例目前既未被证实也未被排除。它是基于论文建模边界的候选攻击，不是对作者实验结果造假的指控。

## § 12 — Follow-up Research Idea

在电力电子与电力系统控制领域，高影响研究通常不仅看解析新颖性，还看模型边界是否透明、能否在 switching simulation 与 HIL/physical prototype 中重复、是否给出工程可实现的保护与参数设计规则。基于第 9 节局限，一个非增量方向是把标量 PFR 改写为**含控制模式和保护事件的 hybrid viability tube**：研究目标不再是“给定 \(P_0,P_1\) 的首摆面积是否平衡”，而是“在电流限幅、PWM 饱和、PLL/V-f 模式切换、参数不确定和多机相互作用下，哪些状态-功率-模式组合保证在有限时间内仍可回到同步集合”。

（a）驱动需求是现有 PFR 在工程上最关键的保护边界处恰好缺少模型闭合；保护动作不是小修正，而会切换系统向量场。  
（b）研究价值在于把运行边界从 nominal design map 提升为可检验的 protection-aware safety certificate，并能直接回答限流阈值、恢复逻辑和 GFL/GFM 配比如何共同决定安全裕量。  
（c）可以借鉴 hybrid systems reachability、Hamilton–Jacobi viability、set-valued uncertainty propagation 与 control barrier function；EAC 面积可保留为低维解释器或快速外层筛选器，而不是唯一证书。  
（d）第一个证伪实验是在 \(P_0=300\) MW、\(P_1=570\)–590 MW边界带内随机化限流阈值、控制增益和线路阻抗，对比 nominal PFR、hybrid viability tube 与 switching/HIL 真值；若新方法不能显著减少 false-safe 分类，或计算成本无法在保护设计周期内接受，想法即被否证。  
（e）它与本文的实质区别是改变了“稳定边界”的对象：本文边界定义在功率平面、基于单一连续约化模型和首摆面积；新方向把离散模式、内部状态与不确定性纳入边界本身。

论文作者已把“RPG 从 grid-following 改为 grid-forming”以及“不同 GFL/GFM 比例下的多机稳定性”列为 future work。[pdf:E19]（PDF 物理页 10，Conclusion）上述方向与之相邻，但重点不是简单更换控制策略或增加一台变流器，而是建立跨模式、保护感知的安全域。由于本任务没有联网检索相邻工作的完整全文，这仍是**候选研究想法**，不声称 novelty。
