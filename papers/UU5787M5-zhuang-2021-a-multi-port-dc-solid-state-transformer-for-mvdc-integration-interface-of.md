# A Multiport DC Solid-State Transformer for MVDC Integration Interface of Multiple Distributed Energy Sources and DC Loads in Distribution Network

作者：Yizhan Zhuang, Fei Liu, Yanhui Huang, Shiwen Wang, Shangzhi Pan, Xiaoming Zha, Xiaoguang Diao

出处：IEEE Transactions on Power Electronics, Vol. 37, No. 2, pp. 2283-2296, February 2022；论文首页记载在线出版日期为 2021-08-18

年份：2021（在线出版；正式卷期为 2022 年）

DOI：10.1109/TPEL.2021.3105528

Zotero key：UU5787M5

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 传统 MVdc/LVdc 配电架构先用 dc solid-state transformer（DCSST）把中压直流变为低压直流，再让 PV、储能和直流负载通过各自的 LVdc converter 接入公共 LVdc bus。这样从设备端到 MVdc grid 要经过两级功率变换，而且设备之间没有由接口本身提供的 galvanic isolation；公共 LVdc bus 或其输出端短路还会形成共同故障点。论文要解决的问题是：能否让不同类型、不同功率方向的多个直流端口直接接入串联的 MVdc 侧，同时保持各串联模块电压均衡，并保留高频隔离？[pdf:E01]（PDF 物理页 1，Abstract、Section I、Fig. 1）

作者给出的答案是一种 multiport DC solid-state transformer（MDCSST）：每个独立低压端口经一个 dual-active-bridge（DAB）submodule 接到串联的高压侧，各相邻 submodule 之间再放置 LC branch 传递差额功率。按 Table I 的器件计数，在有 \(N\) 个直流单元时，传统方案有 LVdc bus、两级功率变换和 \(8N\) 个开关，而 MDCSST 没有 LVdc bus、只有一级接口和 \(6N\) 个开关；两者的电感数分别为 \(2N\) 与 \(2N-1\)，电容数分别为 \(3N\) 与 \(3N-1\)。这些是拓扑级计数，不等于已经证明全寿命成本或效率更优。[pdf:E02]（PDF 物理页 2，Fig. 2、Table I、Section I）

工程价值在于，它试图把“端口功率管理、隔离升压、MVdc 串联叠压”合并到一个模块化接口中。真正困难的不是把半桥串起来，而是端口功率天然不相等：若每个高压侧模块仍要维持相同电压，差额能量必须找到受控路径，否则某些器件会过压。论文的主要技术贡献正是给这条差额能量提供 LC branch，并把其功率指令纳入电压均衡控制。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

**论文直接陈述。** 高变比 DCSST 的常见路线是 input-series/output-parallel（ISOP）模块化结构；此前工作已分别研究 DAB 回流功率抑制、series-resonant DAB、混合 resonant/DAB、短路切除、故障 submodule 旁路和全工况控制。这些工作改进了效率或故障处理，但若 PV、储能、负载仍接公共 LVdc bus，就仍需额外的低压变换器，也保留了公共母线故障点。[pdf:E02]（PDF 物理页 2，Section I）

更直接相关的是 input-independent/output-series（IIOS）接口 [25]-[29]：它取消 LVdc bus，使各低压端口彼此隔离并直接串联形成 MVdc。其关键缺口是端口功率不同会令各模块电压失衡。[25] 的 power equalizer 对 \(N\) 个模块需要 \(N-1\) 个均衡器，每个均衡器含两个有源开关和一个电感；[28]、[29] 已用无额外开关的 LC branch 做电压均衡，但低压端口只接 PV。本文相对于这些工作的实质推进，是把 LC 均衡路径扩展到 PV、储能、直流负载混接，并给出相应的多控制模式和并/离网切换。[pdf:E02]（PDF 物理页 2，Section I、Fig. 2）

**边界。** 论文没有做相同额定电压、功率和器件技术下的 efficiency、power density、BOM cost 或 fault-tolerance 对照，因此“更经济、更可靠”主要来自拓扑计数与架构推断，而不是完整的实验对比。

## § 3 — 重建作者的思考路径

下面是基于论文背景证据重建的合理路径，不是作者逐字陈述。

第一步，若目标只是高变比隔离，可以沿用 ISOP DCSST；但每个分布式能源或负载还要另配 LVdc converter，接口级数和公共故障点并未消失。第二步，改用 IIOS：让每个低压端口拥有自己的 DAB，所有高压半桥串联叠压。这样端口可以是源也可以是负载，隔离和升压也能在同一级完成。[pdf:E02]（PDF 物理页 2，Fig. 2、Table I）

第三步立即出现能量约束：串联端共享同一 bus current，但低压端口功率不同；若没有横向功率通道，每个 submodule 的高压侧电容能量变化不同，电压就会分叉。第四步，与其给每对模块增加有源 equalizer，不如利用相邻半桥本已有的开关节点，用串联 \(L_B-C_B\) 支路和相移控制双向搬运差额功率。第五步，把各端口的 CFBC、CFBV、MPPT、CBV 控制都统一为对 \(\varphi_{SM}\) 的调节，再由 LC branch 的 \(\varphi_B\) 完成模块间均压；并用端口功率 feedforward 直接计算差额功率，避免只等相邻电压偏差出现后才纠正。[pdf:E03]（PDF 物理页 3，Figs. 3-6、Section II）[pdf:E04]（PDF 物理页 4，Figs. 7-9、Section III-A）[pdf:E05]（PDF 物理页 5，Fig. 10、Eqs. (6)-(7)）

## § 4 — 核心 Intuition

每个低压端口先独立决定自己要吸收或送出多少功率，而串联高压侧要求每个模块承担相同的电压份额；两者之间的不一致就是“差额功率”。MDCSST 不强迫各端口等功率，而是让相邻 LC branch 像一条双向能量旁路，把差额从功率富余模块逐级搬到功率不足模块；端口相移管纵向功率，LC 相移管横向均衡。[pdf:E03]（PDF 物理页 3，Figs. 3-6）[pdf:E05]（PDF 物理页 5，Fig. 10）

## § 5 — 具体方法与完整 Pipeline

以论文的五模块系统为例，SM#1、SM#2 接 PV，SM#3、SM#4 接储能，SM#5 接直流负载。完整能量与控制 pipeline 是：

1. **端口进入 DAB submodule。** 每个 SM 的低压侧是 full bridge（FB），经高频变压器和漏感 \(L_{SM}\) 接到高压侧 half bridge（HB）；所有 HB 串联形成 MVdc bus。变压器提供 galvanic isolation，串联 HB 完成电压叠加。[pdf:E03]（PDF 物理页 3，Fig. 3、Section II-A）
2. **端口功率由 \(\varphi_{SM}\) 控制。** FB 与 HB 的 50% duty 方波之间施加相移；\(\varphi_{SM}>0\) 时平均 FB 电流为正，功率流入 FB 端，\(\varphi_{SM}<0\) 时功率反向。作者为便于控制把相移限制在 \([-T_s/4,T_s/4]\)。[pdf:E03]（PDF 物理页 3，Figs. 4-5、Eqs. (1)-(3)）
3. **同一功率级适配不同端口。** 储能可用 constant FB current（CFBC）决定充放电电流；直流负载用 constant FB voltage（CFBV）；PV 用 perturb-and-observe MPPT 加电流环；离网时储能或 PV 以 bus-voltage 外环加电流内环实现 CBV。四种策略最终都输出 \(\varphi_{SM}\)。[pdf:E04]（PDF 物理页 4，Fig. 9、Section III-A）
4. **LC branch 搬运差额功率。** 每两个相邻 HB 之间有一个 \(L_B-C_B\) 支路。两端开关组之间的相移 \(\varphi_B\) 决定传输方向：正相移从上 SM 向下 SM，负相移反向；volt-second balance 给出 \(V_{CB}=V_H\)。[pdf:E04]（PDF 物理页 4，Figs. 6-8、Eqs. (4)-(5)）
5. **均压闭环叠加功率 feedforward。** 相邻 HB 电压差进入 PI，所有端口功率又经 Eq. (7) 算出各 LC branch 的目标差额功率，再由支路功率方程换算为 \(\varphi_{B,e}\)。二者相加形成最终 \(\varphi_B\)，使端口突变发生时不必等远端模块电压先偏移才动作。[pdf:E05]（PDF 物理页 5，Fig. 10、Eqs. (6)-(7)）
6. **系统级 mode manager 切换功率责任。** 论文定义六种模式：并网时 PV 维持 MPPT，电网吸收富余或补足缺口，必要时给电池充电；离网时由电池建立 bus voltage，电池满充后改由 PV 的 CBV 控制建立 bus voltage。模式切换改变的是各端口控制目标，不改变主功率拓扑。[pdf:E05]（PDF 物理页 5，Section III-C）[pdf:E06]（PDF 物理页 6，Fig. 11）

**EMT/FPGA 覆盖边界。** 论文的仿真是开关级 MATLAB/Simulink，报告 simulation step 为 100 ns，但未报告 solver 类型、离散积分格式、代数环处理、事件插值、多速率调度或数值位宽；硬件控制器型号、采样频率、PWM 更新时序、计算依赖、并行划分、fixed-point 量化与 FPGA 映射也均未报告。因此不能据此声称它已经给出 EMT real-time 或 FPGA implementation pipeline。[pdf:E08]（PDF 物理页 8，Section IV-A、Table II）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线是先得到两个相移功率级的平均电流，再用功率守恒求每条均衡支路应搬运的差额。

对单个 DAB SM，在一个开关周期内分段写出漏感电流斜率并施加半周期反对称条件 \(i_F(t_0)=-i_F(t_2)\)，得到

\[
i_{F,\mathrm{AVE}}=
\begin{cases}
\dfrac{V_F(-2\varphi_{SM}+T_s)\varphi_{SM}}{T_sL_{SM}}, & \varphi_{SM}\ge 0,\\[6pt]
\dfrac{V_F(2\varphi_{SM}+T_s)\varphi_{SM}}{T_sL_{SM}}, & \varphi_{SM}<0.
\end{cases}
\]

它说明相移的符号给出功率方向，幅值在 \(\pm T_s/4\) 附近达到作者选用控制区间内的峰值；由峰值电流至少覆盖额定端口电流，可得

\[
L_{SM}\le \frac{V_F^2T_s}{8|P_{SM}|}.
\]

前一式及变量定义见物理页 3，后一设计约束跨物理页 5-6。[pdf:E03]（PDF 物理页 3，Eqs. (1)-(3)、Fig. 5）[pdf:E05]（PDF 物理页 5，Eqs. (8)-(9)）[pdf:E06]（PDF 物理页 6，Eq. (10)）

LC branch 使用同样的 state-space averaging。作者得到

\[
i_{B1,\mathrm{AVE}}=-i_{B2,\mathrm{AVE}}
=\frac{V_H(-2\varphi_B+T_s)\varphi_B}{4T_sL_B},\qquad \varphi_B\ge0,
\]

负相移区间使用 \(V_H(2\varphi_B+T_s)\varphi_B/(4T_sL_B)\)。这里 PDF 有一处必须保留的不一致：Eq. (5) 前的文字写“when \(\varphi_B\le0\)”，但公式末尾又印成“\(\varphi_B\ge0\)”。结合 Fig. 8 和紧随其后的功率方向说明，负支路显然对应 \(\varphi_B<0\)，但本卡不把推断伪装成作者已更正的公式。[pdf:E04]（PDF 物理页 4，Eqs. (4)-(5)、Fig. 8）

对第 \(k\) 条 LC branch，要求它两侧模块组的平均输出功率相等，可由 Eq. (6) 解得

\[
P_{B,k}=
\frac{(N-k)\sum_{i=1}^{k}P_{SM,i}
-k\sum_{i=k+1}^{N}P_{SM,i}}{N}.
\]

这条式子最重要的物理意义是：支路指令不是只由相邻两个端口决定，而是由该“切面”两侧全部端口功率决定。它既解释了 feedforward 为什么要读取所有 \(P_{SM,i}\)，也暴露了规模扩大后中心支路可能成为功率瓶颈。[pdf:E05]（PDF 物理页 5，Eqs. (6)-(7)、Fig. 10）

支路器件按最大差额功率 \(P_{B,\max}\) 选取：

\[
L_B\le\frac{V_H^2T_s}{32P_{B,\max}},\qquad
C_B\ge\frac{T_sP_{B,\max}}{\rho V_H^2},
\]

其中 \(\rho\) 是允许的电容电压纹波比例。作者还分析出共享 HB 开关 \(Q_1,Q_2\) 可以 ZVS turn-on，但是 hard turn-off；current reversing process 不传有功却产生损耗，且平均开通电流主要由所有 SM 的平均功率决定。因此“无额外有源开关”不等于“均衡免费”。[pdf:E06]（PDF 物理页 6，Eqs. (11)-(18)）[pdf:E07]（PDF 物理页 7，Eqs. (19)-(26)、Figs. 12-13）

## § 7 — 实验设计与结论

**问题 1：端口功率突变时，串联 HB 电压能否保持均衡？**  
**实验：** 作者在 MATLAB/Simulink 建立五 SM 开关模型，两个 PV 端口、两个 battery 端口、一个 load 端口，step 为 100 ns。仿真参数包括 4 kV bus、每 SM 400 V FB nominal voltage、800 V HB voltage、50 kHz switching、\(L_{SM}=4.27\,\mu H\)、\(L_B=1.07\,\mu H\)、\(C_B=160\,\mu F\)。并网 case 在 \(t=1\rm\,s\) 把负载电流由 80 A 降到 40 A；离网 case 还在 \(t=3\rm\,s\) 降低 PV 电流。[pdf:E08]（PDF 物理页 8，Table II、Fig. 14、Section IV-A）[pdf:E09]（PDF 物理页 9，Fig. 15）  
**答案：** Fig. 14 中 bus 保持 4 kV，五个 HB 稳态约为 800 V，负载突变时图中标注的单模块瞬态偏差为 8-20 V；Fig. 15 的离网负载/PV 切换也没有持续失衡。它支持“给定五模块、给定模型和给定扰动下可均压”，但不是对任意端口分布或任意 \(N\) 的证明。

**问题 2：六种功率模式和并/离网切换能否在硬件上工作？**  
**实验：** 作者搭建 480 V、五 SM 降额样机。低压端为 48 V，HB 每模块约 96 V，switching frequency 为 20 kHz，\(L_{SM}=9.6\,\mu H\)、\(L_B=7\,\mu H\)、\(C_B=180\,\mu F\)，变压器为 11:11。受实验条件限制，PV 被 48 V 恒压 dc source 替代并使用 constant-current control；MVdc grid 被 dc source 加并联耗能电阻替代，line parameters 被忽略。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E09]（PDF 物理页 9，Table III、Section IV-B）[pdf:E10]（PDF 物理页 10，Fig. 16）

**答案：** Fig. 17 依次验证 mode 1 → mode 2 → mode 1：理论 grid current 分别为 0.4 A、-0.2 A、0.2 A，实测约为 0.32 A、-0.22 A、0.18 A，端口和 bus 电压在切换中维持稳定。[pdf:E10]（PDF 物理页 10，Fig. 17 及相邻正文）Fig. 18 验证离网电池建压、并网后充电和充满后的 mode 4 → 3 → 2 转换；文中报告的相关 battery/grid currents 与功率方向一致，但同一段出现算术书写不一致：先得到 grid 需提供 499.2 W，后面却写成 \(576/480=1.04\rm\,A\)，而 \(1.04\rm\,A\) 实际对应 \(499.2/480\)。[pdf:E11]（PDF 物理页 11，Fig. 18 及相邻正文）Fig. 19 又验证 mode 1 → 6 → 5，Fig. 20 的实测开关与电感波形在形状上与理论 Figs. 4、7 一致。[pdf:E12]（PDF 物理页 12，Figs. 19-20、Section V）

**不能外推的范围。** 论文没有报告效率曲线、损耗分解实测、thermal behavior、EMI、短路或开路故障、控制延迟、参数容差、长期可靠性、MVdc 绝缘样机、模块数扩展或与传统 DCSST 的同规格硬件对照。实验还没有真实 PV 的 P-V/MPPT 动态，也没有真实 MVdc line。因此实验支持的是降额五模块原理样机的功率路由与电压均衡，不足以直接支持中压规模的成本、效率和可靠性结论。

## § 8 — Take-aways

**5 句话**

1. 本文把 PV、储能和直流负载分别接入独立 DAB submodule，再把高压 half bridges 串联成 MVdc 接口。
2. 相邻 LC branch 负责搬运端口功率差，使串联模块仍能维持近似相同的高压侧电压。
3. CFBC、CFBV、MPPT、CBV 四类端口控制和六种系统运行模式统一落到相移控制上。
4. 五模块仿真与 480 V 降额样机验证了并网、离网及模式切换时的功率方向和电压均衡。[pdf:E08]（PDF 物理页 8，Fig. 14）[pdf:E10]（PDF 物理页 10，Figs. 16-17）[pdf:E12]（PDF 物理页 12，Figs. 19-20）
5. 论文没有证明这种相邻链式均衡在更多模块、真实 MVdc 应力和极端功率空间分布下仍具可接受的损耗与动态裕度。

**3 句话**

1. MDCSST 用“独立端口 DAB + 串联 HB + 相邻 LC 均衡”取消公共 LVdc bus 和额外端口 converter。
2. 它在五模块模型和降额样机中完成了多类端口与并/离网模式的统一控制。
3. 最关键的未决问题是差额功率沿链传输时的可扩展性，而非控制模式是否足够多。

**1 句话**

这篇论文证明了多端口 IIOS DC transformer 的五模块可行性，但尚未证明相邻 LC 差额功率网络能无代价地扩展到真正的 MVdc 系统。

## § 9 — 最脆弱的假设

最脆弱的假设是：**无论端口功率怎样分布，相邻 LC chain 都有足够的功率容量、相移裕度和动态速度，在共享 HB 开关不过应力、损耗可接受的条件下维持全部串联模块电压均衡。**

这不是附属假设，而是核心贡献的承重点。IIOS 结构一旦失衡，某些 HB 电容电压上升，直接增加器件过压风险；MDCSST 又把所有差额功率都压到 \(N-1\) 条相邻支路上。Eq. (7) 表明第 \(k\) 条支路承担的是切面两侧全部端口功率的函数，而 Eqs. (13)-(19) 又说明更大的 \(P_{B,\max}\) 会要求更小的 \(L_B\)、更大的 \(C_B\) 或更高电流应力。[pdf:E05]（PDF 物理页 5，Eq. (7)）[pdf:E06]（PDF 物理页 6，Eqs. (13)-(18)）[pdf:E07]（PDF 物理页 7，Eq. (19)、loss analysis）

论文给出的支持证据是五模块、两 PV + 两 battery + 一 load 的仿真和 480 V 样机，且受测工况下 HB 电压确实保持稳定。[pdf:E08]（PDF 物理页 8，Fig. 14）[pdf:E09]（PDF 物理页 9，Fig. 15）缺少的是随 \(N\) 增大、端口功率在空间上聚集、元件参数失配、控制延迟、支路相移/电流饱和、单支路故障和真实 MVdc dv/dt 同时出现时的证据。若这条假设失效，论文的多端口直连价值会被额外均衡容量、降额或保护成本抵消。

## § 10 — 最小复现实验

一周内最值得复现的不是整台样机，而是“Eq. (7) feedforward 是否真的在端口突变时稳定五个 HB 电压”。

- **数据与参数：** 使用 Table II 的五 SM simulation 参数：4 kV bus、400 V FB、800 V/SM、50 kHz、\(L_{SM}=4.27\,\mu H\)、\(L_B=1.07\,\mu H\)、\(C_B=160\,\mu F\)、100 ns step；复用 Fig. 14 的并网负载阶跃和 Fig. 15 的离网负载/PV 阶跃。[pdf:E08]（PDF 物理页 8，Table II、Fig. 14）[pdf:E09]（PDF 物理页 9，Fig. 15）
- **实现：** 在 Simulink、PLECS 或等价开关仿真器中实现 DAB SM、相邻 LC branch、端口控制和 HB-voltage PI。做两组完全相同的 run：A 组使用“电压 PI + Eq. (7) power feedforward”，B 组只使用相邻电压 PI。
- **测量：** 对每次阶跃记录 \(\max_i|v_{H,i}-v_{bus}/5|\)、恢复到稳态带宽所需时间、每条 \(P_{B,k}\)、峰值 \(i_{LB}\)、\(\varphi_B\) 是否触及 \(\pm T_s/4\)，并做全系统瞬时功率守恒检查。
- **支持判据：** A 组应复现 Fig. 14/15 的稳态均压与正确功率方向，并在相同 PI 参数下比 B 组有更小峰值偏差或更短恢复时间，同时无 branch saturation。这里“优于 B 组”是为检验 feedforward 机制而设的复现判据，不是论文已经报告的 ablation。
- **反驳判据：** 使用论文给定参数和工况仍出现持续电压漂移、Eq. (7) 与仿真支路平均功率不符、必须超出 \(\pm T_s/4\) 才能恢复，或 A 组并不比 B 组更快，都会直接削弱核心均衡 claim。还应特别检查 Eq. (5) 的符号条件和 Fig. 18 相邻正文的算术不一致，避免把排版错误写进控制器。

## § 11 — 最强反例设计

最强反例不是再加一个普通负载阶跃，而是构造**空间聚集、总功率仍平衡**的端口分布：在一个较大的偶数 \(N\) 系统里，让前 \(N/2\) 个端口各输出 \(+P\)，后 \(N/2\) 个端口各吸收 \(-P\)，系统离网且总功率为零。由 Eq. (7)，中心切面支路必须搬运约 \(NP/2\) 的功率；它不是额定单端口功率 \(P\)，而是随模块数线性增加。[pdf:E05]（PDF 物理页 5，Eq. (7)）

实验应固定每个 SM 与每条 LC branch 的器件额定值、相移上限和总被动器件体积，只把 \(N\) 从 4、8、16 逐步增加，并加入 10% \(L_B/C_B\) 容差、一个 PWM period 的测量/计算延迟和实际开关损耗。观察中心支路是否先触及 \(\varphi_B\) 或电流上限，随后导致 HB 电压漂移、过压保护或热限制。Eqs. (13)-(19) 预测支路容量需求会随 \(P_{B,\max}\) 增长；hard turn-off 和 current reversing process 又会把这种功率路由变成真实损耗。[pdf:E06]（PDF 物理页 6，Eqs. (13)-(18)）[pdf:E07]（PDF 物理页 7，Eqs. (19)-(26)）

如果该反例成立，它给出一个比“样机不够大”更具体的替代解释：五模块成功是因为论文的端口排列和功率幅值没有逼近 chain cut 的极限，而不是相邻 LC 架构天然可扩展。若在固定合理器件额定下，16 模块仍能通过所有上述工况且效率和热应力可接受，反例才被实质削弱。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响工作通常不只要求新拓扑，还要求可证明的器件应力/损耗边界、严格动态验证、可扩展控制以及接近目标电压和功率等级的硬件证据。基于第 9 节，候选方向是：**把多端口 SST 的功率端口排列与均衡网络作为 graph cut co-design 问题，而不是预先固定为相邻 LC chain。** 由于本卡按协议没有联网补充相关工作，这只是证据约束下的候选研究想法，不声称 novelty。

**(a) 未满足需求。** 相邻 chain 的中心 cut 可能汇集大量差额功率；增加模块数时，均衡支路的 VA rating、损耗和故障传播可能先于主功率级成为瓶颈。

**(b) 研究价值。** 目标不再是“给 chain 再加一个控制器”，而是给定端口功率不确定集、器件 VA budget 和 \(N-1\) 故障条件，联合求解端口放置、均衡图拓扑和控制律，使 worst-case cut power、HB voltage deviation 与 loss 有可验证上界。若能在 MVdc 样机上证明这些上界，它会直接回应工程可扩展性和可靠性。

**(c) 可借鉴工具。** 可借鉴 network flow/min-cut、robust optimization 和 graph-based distributed control；候选硬件可比较相邻 chain、稀疏 skip-link 或分层 resonant balancing，但不预设哪一种一定更好。

**(d) 首个证伪实验。** 在相同总半导体 VA、总电感储能、总电容体积和控制带宽下，对 chain 与候选图施加第 11 节的 clustered source/load 扫描和单支路开路。若候选图不能显著降低最大 branch power、峰值 HB 偏差或总损耗，或者故障隔离更差，则该方向立即被证伪。

**(e) 与本文的实质区别。** 本文在固定相邻 LC chain 上解决“怎样控制差额功率”；候选工作改问“什么均衡连接结构与端口布局，能让最坏差额功率在规模增长和故障下仍可控”。它改变的是问题定义和可扩展性目标，而不是给现有 Fig. 10 再叠加一个补偿环。
