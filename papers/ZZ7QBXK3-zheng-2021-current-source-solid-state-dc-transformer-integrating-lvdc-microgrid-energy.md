# Current-Source Solid-State DC Transformer Integrating LVDC Microgrid, Energy Storage, and Renewable Energy Into MVDC Grid

作者：Liran Zheng，Rajendra Prasad Kandula，Deepak Divan  
出处：IEEE Transactions on Power Electronics，Vol. 37，No. 1，January 2022  
年份：2021（在线发表；纸本卷期为 2022 年）  
DOI：10.1109/TPEL.2021.3101482  
Zotero key：ZZ7QBXK3  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是“能否做一台隔离 DC–DC 变换器”，而是一个更具体的工程问题：怎样在 MVdc 与 LVdc/LVac 之间实现可双向、可升降压、软开关且器件导通路径尽量短的 solid-state transformer（SST）。应用对象包括 LVdc 微电网接入 MVdc 配电网，以及风电、光伏和储能场站的 MVdc 集电。论文给出的典型背景是：光伏侧常见电压为 1–1.5 kV，风机 PMSG 输出通常低于 1 kV，例如 690 V；这些低压资源若要接入 MVdc，需要隔离和升压接口。[pdf:E01]（PDF 物理页 1，Abstract、Section I、Fig. 1）

工程瓶颈在器件损耗。作者指出，近期 MV DCT prototype 中 device-related loss 是主导损耗；他们此前的 current-source（CS）SST 为每个 bridge switch 串联了 MOSFET/IGBT 与 diode，以取得 reverse-blocking 能力，但这使主电流路径上的结压降和器件数偏多。[pdf:E02]（PDF 物理页 2，Section I、Fig. 2(a)）论文的核心目标因此是：不改变 CS SST 的能量传递机制，用端口电压极性与开关承压需求证明某些 transistor 或 diode 可以删除，从而得到 dc–dc 和 dc–ac 两种 reduced-switch CS SST。[pdf:E02]（PDF 物理页 2，Section I、Fig. 2(b)(c)）

论文直接声称，这种方案保留 single-stage isolated conversion、主开关 full-voltage-range ZVS、谐振开关 ZCS、controlled \(dv/dt\)、双向功率流、ISOP 模块化和无 electrolytic dc-link capacitor 等特性。[pdf:E01]（PDF 物理页 1，Abstract）如果这些性质在实际 MV 设备中成立，价值不只是少几个开关：它可能同时降低导通损耗、器件数、滤波与 EMI 压力，并减少从可再生能源到 MVdc 母线的转换级数。

## § 2 — 前人工作与不足

论文把既有 DCT 路线分成三类。第一类是 resonant DCT：效率高，但通常以固定频率 open-loop 运行，调节能力弱。第二类是 dual-active bridge（DAB）及其模块化变体：具备可控性、部分 ZVS 和 controlled \(dv/dt\)，但在宽 buck–boost 比或轻载下可能失去 ZVS，并出现较大的 circulating current 与效率下降。第三类用“两级化”规避这一矛盾：让 DAB 或 resonant stage 固定在接近 unity conversion ratio，再加 hard-switching regulation stage；它还可避免 MV 故障直接暴露 dc-link capacitor，但代价是更多器件和额外转换级。[pdf:E02]（PDF 物理页 2，Section I）

作者此前的 S4T 路线把 transformer magnetizing inductance 当作 current-source dc link，能够在宽电压范围做 ZVS 和单级双向转换；不足是 dc 端采用完整 reverse-blocking bridge，每个位置需要 series diode 与 transistor。[pdf:E02]（PDF 物理页 2，Fig. 2(a) 与相邻正文）本论文与 prior CS DCT 的差异不是另加一个辅助换流级，而是依据实际承受的正、负电压范围，删除没有被使用的反向阻断器件。Table I 报告，zero vector 的导通压降器件数从 4 降到 2，MV/LV active vector 从 4 降到 3，对应 50% 和 25% 的减少。[pdf:E04]（PDF 物理页 4，Table I）

需要谨慎解释“前人不足”。论文并未证明 DAB 或两级 DAB 在所有指标上劣于 proposed CS DCT。作者明确说总体 efficiency、power density 等高度依赖具体 use case，不能给出一般性结论；两级 DAB 在 MV 故障时隔离 dc-link capacitor 仍有优势。[pdf:E09]（PDF 物理页 9，Section VI、Tables III–IV）因此，本论文的可靠定位是“在宽 buck–boost、器件损耗主导且希望保留 CS link 的场景中，减少 reverse-blocking bridge 的冗余器件”，而不是“普遍替代所有 DCT”。

## § 3 — 重建作者的思考路径

可以从论文出现之前已经存在的工程事实重建这条路径。

第一步，MVdc 接口必须隔离并完成很大的电压变比，而风、光、储端电压还会波动；所以只在 nominal ratio 高效不够，buck 与 boost 两侧都需要可控运行。[pdf:E01]（PDF 物理页 1，Section I）

第二步，DAB 的宽变比 circulating current/ZVS 范围与两级方案的额外器件形成取舍。已有 S4T 说明可以把 magnetizing inductance 直接作为 current link：LV vector 给 \(L_m\) 充能，MV vector 从 \(L_m\) 放能，谐振辅助支路只负责重置 capacitor voltage 和创造软开关条件。[pdf:E03]（PDF 物理页 3，Figs. 3–4）

第三步，如果 current-source bridge 中某些器件在整个正常工作电压集合内只需阻断一个极性，那么“transistor + series diode”的完整 reverse-blocking position 是过度配置。对 switch voltage 做集合分析，比从波形经验上直接短接器件更可靠：Eq. (1)–(4) 给出端口和 transformer voltage 的范围，由 KVL 推出 AP/BN 与 BP/AN 的正、负阻断边界。[pdf:E04]（PDF 物理页 4，Eq. (1)–(4)）

第四步，删除器件不能破坏原有换流。因而作者保留 zero vector、MV/LV active vector、ZVS transition 和 LC resonance 的时序，让 resonant capacitor 先被放到合适负电压，再翻转成正电压；这样 main switches 在 turn-on 前已近似零压，resonant switches 则在 current 回到零时关断。[pdf:E03]（PDF 物理页 3，Figs. 3–4 及 Section II-B）

第五步，reduced dc-link inductance 只有约 40% peak-to-peak current ripple，不能像大 dc-link capacitor 那样缓冲能量，所以需要按每个 switching cycle 预测 LV vector 与 MV vector 的持续时间，而不是只用慢速平均模型调节。[pdf:E06]（PDF 物理页 6，Section IV）由此形成完整方案：拓扑减器件、谐振支路保软开关、predictive control 管快速 link dynamics。

## § 4 — 核心 Intuition

核心 intuition 是：current-source bridge 的每个“完整反向阻断开关”并不真的需要在两个方向上都具有相同的可控器件；端口电压和 transformer voltage 的可达范围决定了部分位置只需 transistor 或 diode，因此可删掉未被实际使用的半个开关位置。[pdf:E04]（PDF 物理页 4，Eq. (1)–(4)、Table I）能量传递仍由 \(L_m\) 在 LV 与 MV active vector 之间交替充放完成，而 resonant capacitor 通过自适应预充/翻转为下一 active vector 建立 ZVS 条件，所以 buck 与 boost 不需要换拓扑。[pdf:E03]（PDF 物理页 3，Figs. 3–4）

## § 5 — 具体方法与完整 Pipeline

以“150 V 侧电源向 600 V nominal MV 侧负载送能”的 dc–dc prototype 为具体例子，完整 pipeline 如下。

1. **拓扑入口。** MV 与 LV 两侧各有 bridge，transformer magnetizing inductance \(L_m\) 充当 current-source dc link；两侧辅助支路包含 leakage-management diode、resonant capacitor \(C_r\)、resonant inductor \(L_r\) 与 resonant switch。Fig. 2(b) 中删去部分 series diode/transistor，dc–ac 版本则把 LV 端换成 three-phase CSI bridge。[pdf:E02]（PDF 物理页 2，Fig. 2(b)(c)、Section II-A）
2. **zero vector。** 电流先在两侧 bridge 内 freewheel，\(i_m\) 基本不变。论文分析假设两侧器件具有相同 per-unit on-state resistance；若不相同，电流按 impedance division 分配。[pdf:E03]（PDF 物理页 3，Fig. 4(a) 及相邻正文）
3. **ZVS transition 到 MV vector。** 关断 zero-vector switches 后，\(i_m\) 对 resonant capacitors 充放电。当 MV-side capacitor voltage 达到 MV 输出电压条件时，目标主开关近零压导通；在 MV vector 中，\(L_m\) 向 MV 负载送能，\(i_m\) 下降。[pdf:E03]（PDF 物理页 3，Fig. 4(b)(c)）
4. **resonance。** buck 工况若下一 LV vector 的 ZVS 余量不足，控制先延长一个 capacitor-replenishing transition；boost 工况可跳过。随后 \(L_rC_r\) resonance 把 capacitor voltage 从负值翻到正值，resonant current 回到零后关断辅助开关，取得 ZCS。[pdf:E04]（PDF 物理页 4，Section II-B）
5. **LV vector。** 进入 LV active vector，LV 源给 \(L_m\) 充能，\(i_m\) 上升。反向功率流使用 complementary active switches，非 active states 不变。[pdf:E04]（PDF 物理页 4，Section II-B）
6. **每周期控制。** digital controller 先用 Eq. (23) 由 peak-current reference 算 \(T_{\mathrm{LV}}\)，再更新 \(i_m(t+T_{\mathrm{LV}})\)；用输出 voltage error、load-current feedforward 与上一周期 charge correction 算 \(T_{\mathrm{MV}}\)，并用 lower current limit 防止 link 过度去能，最后以 Eq. (28) 填充 freewheeling time。[pdf:E06]（PDF 物理页 6，Eq. (23)–(28)）
7. **输出。** dc–dc 版本得到隔离、双向、可升降压的 MVdc/LVdc 接口；dc–ac 版本以 three-phase current-source vectors 直接得到 single-stage isolated MVdc/LVac conversion。[pdf:E08]（PDF 物理页 8，Figs. 8–9、Section V-B）

从 EMT/FPGA 实现视角，论文报告了 switching-cycle predictive timing，但**未报告** EMT 离散求解器、固定时间步长、事件迭代、multi-rate partition、FPGA 数据通路、定点位宽、资源占用、pipeline latency 或实时硬件平台。它是一篇 power-converter topology/control 论文，不能外推为 FPGA real-time simulation 方法。控制器的具体 processor/FPGA 型号、采样与 PWM 计算延迟也未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

数学主线分为“为什么能删器件”“怎样定参数”“怎样每周期控制”三层。

**1. 阻断电压集合决定删哪些器件。** 先假设正常 buck–boost 范围

\[
v_{\mathrm{MV}},v_{\mathrm{LV}}\in[V_{\min},V_{\max}],
\qquad
v_{x\mathrm{MV}},v_{x\mathrm{LV}}\in[-V_{\max},V_{\max}].
\]

由 KVL，

\[
v_{\mathrm{AP}}+v_{\mathrm{BN}}
=v_{x\mathrm{MV}}-v_{\mathrm{MV}}
\in[-2V_{\max},\,V_{\max}-V_{\min}],
\]

\[
v_{\mathrm{BP}}+v_{\mathrm{AN}}
=v_{x\mathrm{MV}}+v_{\mathrm{MV}}
\in[V_{\min}-V_{\max},\,2V_{\max}].
\]

这些集合说明 AP/BN 组合在负向需要约 2 pu 阻断，而正向小于 1 pu；BP/AN 组合相反。因此某些位置的一只 diode 或一只 transistor 可删除。这个推导适用于正值 dc 端口；作者明确说 ac 端因电压不属于 \([V_{\min},V_{\max}]\)，不能照搬。[pdf:E04]（PDF 物理页 4，Eq. (1)–(4)、Section II-C）

**2. link ripple 与 voltage conversion。** active vector 期间，magnetizing current 的变化为

\[
\Delta I_m=\frac{V_{\mathrm{MV}}}{L_m}T_{\mathrm{MV}}
=\frac{V_{\mathrm{LV}}}{L_m}T_{\mathrm{LV}},
\]

所以稳态 conversion ratio 为

\[
\frac{V_{\mathrm{MV}}}{V_{\mathrm{LV}}}
=\frac{T_{\mathrm{LV}}}{T_{\mathrm{MV}}}.
\]

直观上，较高电压侧只需更短的施压时间；两侧对 \(L_m\) 造成的 current rise/fall 必须在一个周期内抵消。[pdf:E04]（PDF 物理页 4，Eq. (5)–(7)）

**3. charge balance、soft-switch overhead 与连续导通。** Eq. (8)–(11) 用 active-vector charge 得到两端平均电流和 filter-capacitor ripple。谐振支路由 \(L_rC_r\) 决定 resonance duration、peak resonant current 与 capacitor voltage stress；Eq. (18) 把目标 capacitor voltage 与 \(dv/dt\) 联系起来。[pdf:E05]（PDF 物理页 5，Eq. (8)–(18)）soft-switch transition 与 resonance 不传输端口能量，因此

\[
D_{\mathrm{eff}}
=1-\frac{T_r+T_{\mathrm{ZVS}}}{T_{\mathrm{sw}}},
\qquad
I_{m(\mathrm{avg})}=\frac{i_{\mathrm{MV}}+i_{\mathrm{LV}}}{D_{\mathrm{eff}}},
\qquad
I_{m(\mathrm{avg})}>\frac{\Delta I_m}{2}.
\]

最后一个不等式是 continuous conduction 的边界；如果 \(D_{\mathrm{eff}}\) 太低，为相同功率就需要更大的 link current。[pdf:E05]（PDF 物理页 5，Eq. (19)–(22)）

50 kVA、6 kV/1.5 kV 设计例采用 \(L_m=20\) mH、MV 侧 \(L_r=48\ \mu\text{H}\)、\(C_r=2\) nF、\(C_{f\mathrm{MV}}=2.5\ \mu\text{F}\)，LV 侧 \(L_r=3\ \mu\text{H}\)、\(C_r=32\) nF、\(C_{f\mathrm{LV}}=16\ \mu\text{F}\)。作者据 Eq. (18) 选择 2 nF 以把设计 \(dv/dt\) 控制在 4 kV/\(\mu\)s，并计算每周期 ZVS transition 约 3.0 \(\mu\)s、resonant time 约 1.2 \(\mu\)s、lost duty 约 7%，即 \(D_{\mathrm{eff}}\) 约 93%。[pdf:E05]（PDF 物理页 5，Table II）[pdf:E06]（PDF 物理页 6，Section III-B）

**4. predictive timing。** Eq. (23)–(24) 用当前 \(i_m\) 与 peak reference 决定 \(T_{\mathrm{LV}}\)；Eq. (25) 对 \(T_{\mathrm{MV}}\) 同时加入 output-voltage charge deficit、load-current feedforward 和上一周期 timing correction；Eq. (27) 是 link-current lower-limit saturation，Eq. (28) 保持 constant switching frequency。[pdf:E06]（PDF 物理页 6，Eq. (23)–(28)）这是一种每个 switching cycle 的 model-based timing 计算，不是对完整 switched circuit 做数值积分。

## § 7 — 实验设计与结论

**问题 1：reduced dc link 能否在 dc–dc 负载和电压突变时受控？ →** 作者仿真 16 kHz、50 kVA、6 kV/1.5 kV module：15 ms 时 load 从 100% 降到 50%，25 ms 恢复；另在 35 ms 将 MV reference 从 5.5 kV 升到 6.5 kV，跨过 4:1 nominal ratio 的 buck/boost 边界。**答案：** 论文报告 load step 时 MV voltage overshoot/undershoot 小于 2%，50%→100% 的 settling 约两个 switching cycles；voltage step 的 settling 约 2 ms，buck/boost 切换没有明显模式跳变。[pdf:E06]（PDF 物理页 6，Section V-A）[pdf:E07]（PDF 物理页 7，Figs. 5–7）

**问题 2：同一拓扑思想能否扩展为 single-stage dc–ac？ →** 作者仿真 16 kHz、50 kVA、6 kV dc/1 kV three-phase ac module，在 100 ms 做 100%→50% load step；LVac 端使用 delta-connected 5 \(\mu\)F capacitors 和每相 5.2 mH filter inductor，MVdc 侧为 3.6 mH。**答案：** 波形显示 step 前后三相 voltage/current 近似正弦，dc-link current 受控，settling 为数毫秒量级；但论文没有报告 THD 数值，也没有硬件 dc–ac prototype。[pdf:E07]（PDF 物理页 7，Section V-B）[pdf:E08]（PDF 物理页 8，Figs. 8–9）

**问题 3：减器件是否真的降低 semiconductor loss？ →** 作者在相同 16 kHz 与相同 device model 条件下比较 proposed CS、prior CS 与 DAB + regulation。nominal 6 kV→1.5 kV、50 kW 时，总 device loss 分别为 502.1、680.8、453.0 W；5.4 kV→1.8 kV、50 kW 时为 446.8、604.2、413.8 W。**答案：** proposed CS 相比 prior CS 的 device loss 约降 26%，但两级 DAB 在这两个表中的估算 total loss 仍略低；作者的优势表述是“以更少器件取得相近损耗和 controlled \(dv/dt\)”，不是绝对效率最高。[pdf:E09]（PDF 物理页 9，Table IV）[pdf:E10]（PDF 物理页 10，Table V）

**问题 4：删减后的阻断极性、buck/boost 换流与 ZVS 能否在硬件中出现？ →** 作者搭建 1.5 kVA、16 kHz prototype，额定 600/150 V，\(L_m=4.3\) mH，使用 nanocrystalline transformer、1.7 kV discrete SiC MOSFET/diode self-assembled reverse-blocking module；由于商用 MV reduced-switch module 缺失，AP 位置的 diode 被电缆短路，AN 位置 MOSFET 全程导通。[pdf:E10]（PDF 物理页 10，Fig. 10、Table VI）在 120→800 V boost 测试中，波形支持 AP 只阻断负压、AN 只阻断正压，device/transformer \(dv/dt<500\) V/\(\mu\)s，且 turn-on 时 device voltage 与 current 几乎不重叠。[pdf:E11]（PDF 物理页 11，Figs. 11–14）在 150→400 V buck 测试中，作者观察到 resonance 前的额外负向 discharge、对应的极性阻断关系和 controlled \(dv/dt<500\) V/\(\mu\)s；Figs. 15、20 用电压/电流无明显重叠支持 boost 与 buck 下的 ZVS。[pdf:E12]（PDF 物理页 12，Figs. 15–19）[pdf:E13]（PDF 物理页 13，Fig. 20、Conclusion）

不得外推的范围是：hardware verification 是 scaled-down dc–dc prototype，不是完整 6 kV/50 kVA prototype；dc–ac、ISOP 多模块、MV fault recovery、长期可靠性、EMI spectrum、thermal cycling、效率曲线和 FPGA real-time execution 均未报告。作者在 Conclusion 也把 full-scale MV experiment 留作未来工作。[pdf:E13]（PDF 物理页 13，Section VIII）

## § 8 — Take-aways

**5 句话。**  
1. 论文用 switch-voltage 可达集合证明 current-source SST 的 dc-port reverse-blocking bridge 存在可删除的 transistor/diode，而不是靠经验简化。  
2. 减器件后仍沿用 \(L_m\) 充放能、resonant capacitor 翻压和 adaptive replenishing 的换流机制，从而覆盖 buck/boost ZVS。  
3. predictive control 直接按 switching cycle 计算 \(T_{\mathrm{LV}}\)、\(T_{\mathrm{MV}}\) 与 freewheel time，以管理约 40% ripple 的 reduced current link。  
4. 仿真覆盖 50 kVA dc–dc 与 dc–ac dynamics，硬件只覆盖 1.5 kVA dc–dc boost/buck、阻断极性与 ZVS。  
5. 最稳妥的贡献结论是“相对 prior CS DCT，器件和估算 device loss 显著减少”，而不是“系统效率普遍优于 DAB”。

**3 句话。**  
这项工作把拓扑简化问题转化为开关承压极性的集合分析，并在不改 CS link 主机制的前提下减少导通路径器件。仿真和 scaled-down hardware 支持控制、buck/boost ZVS 与删减位置的极性判断，但 full-scale MV、故障与长期指标仍缺证据。对 EMT/FPGA 研究者，它提供的是值得建模和实时验证的 converter/control case，而不是现成的 FPGA solver 或 implementation。

**1 句话。**  
用“只保留每个桥臂位置真正需要的阻断能力”减少器件，再用谐振换流和每周期预测控制守住宽变比软开关，是本文最核心的工程思想。

## § 9 — 最脆弱的假设

最脆弱的假设是：Eq. (1)–(4) 定义的**正常工作电压集合足以覆盖 reduced-switch 位置在真实系统中的全部承压状态**。这是核心假设，因为被删除的 diode/transistor 不能靠控制在事后补回来；如果 startup、shutdown、grid fault、transformer leakage transient、device mismatch 或 common-mode parasitic 让该位置遇到推导外的极性和幅值，核心器件简化会直接变成过压或不可控导通风险。正常集合还假设 \(V_{\min},V_{\max}>0\)，ac 端已经被作者明确排除在同一推导之外。[pdf:E04]（PDF 物理页 4，Eq. (1)–(4)、Section II-C）

论文为该假设提供的证据是：scaled-down prototype 在 120→800 V boost 与 150→400 V buck 下，AP/AN 的实测 voltage polarity 符合推导，ZVS 和 controlled \(dv/dt\) 也出现。[pdf:E11]（PDF 物理页 11，Figs. 13–14）[pdf:E12]（PDF 物理页 12，Figs. 18–19）缺少的证据则是 full-scale 6 kV module、bidirectional reversal transient、fault/ride-through、器件参数失配、寄生振荡和绝缘/共模条件下的 worst-case voltage envelope。特别是 prototype 用短接和常导通模拟器件删减，并非可量产 MV reduced-switch module；作者把这类 module 的可用性与 full-scale experiment 明确留到未来。[pdf:E13]（PDF 物理页 13，Conclusion）

## § 10 — 最小复现实验

一周内最有价值的最小复现不是先搭 6 kV 硬件，而是做一个能证伪“删减位置在规定工况内不需要另一极性阻断”的 switched-circuit envelope test。

- **数据与参数：** 采用 Table VI 的 1.5 kVA prototype 参数：16 kHz、600/150 V、\(L_m=4.3\) mH、leakage inductance 5.5 \(\mu\)H、MV \(L_r/C_r=80\ \mu\text{H}/6.25\) nF、LV \(L_r/C_r=5\ \mu\text{H}/100\) nF，以及两侧 filter capacitance。[pdf:E10]（PDF 物理页 10，Table VI）
- **实现：** 在 PLECS、PSIM 或 Simulink/Simscape 中并排建立 full reverse-blocking bridge 与 proposed reduced bridge，复现 Fig. 3 的 zero/MV/resonant/LV vector 顺序和 Eq. (23)–(28) timing。扫 \(v_{\mathrm{LV}}=120\)–150 V、\(v_{\mathrm{MV}}=400\)–800 V、10%–100% load，并加入 \(\pm20\%\) device on-resistance、\(L_m\)、\(L_r\)、\(C_r\) 偏差。
- **测量：** 对 AP、AN、BP、BN 记录每周期 peak positive/negative blocking voltage、turn-on 时 \(v_{\mathrm{DS}}\)、turn-off \(dv/dt\)、\(i_m\) valley、resonant current peak，并比较 full 与 reduced bridge 的端口波形和 semiconductor conduction loss。
- **支持标准：** 所有正常扫点中，被删除器件对应的反向电压不超过所保留器件/寄生通道的安全边界；reduced 与 full bridge 的端口稳态误差小于 1%，且 boost/buck turn-on voltage 接近零，趋势与 Figs. 15、20 一致。[pdf:E12]（PDF 物理页 12，Fig. 15）[pdf:E13]（PDF 物理页 13，Fig. 20）
- **反驳标准：** 任一参数组合使删减位置出现持续的错误极性阻断需求、超过器件 rating 的尖峰、丢失 ZVS 或 \(i_m\) 进入不可恢复的 discontinuous/overcurrent 状态，即足以反驳“该正常范围内可无惩罚删减”的 claim。

这个复现优先验证拓扑机制，而不声称复现作者的 50 kVA loss table；后者还依赖论文采用的具体 SiC die 数据、磁件损耗与热条件。

## § 11 — 最强反例设计

最强反例是构造一个**仍属于实际 MVdc 接口应处理、但越出 Eq. (1)–(4) 正常稳态集合的快速 transient**：在反向功率流时触发 MV 端 pole-to-pole fault 或快速 bus recovery，同时让两侧 on-state resistance 严重不匹配并加入 transformer leakage/common-mode capacitance。比较 full reverse-blocking CS DCT 与 reduced-switch CS DCT，测量被删位置的瞬态 voltage polarity、peak stress、uncontrolled current path、ZVS recovery 和 fault energy。

这个反例比“负载再大一点”更有力，因为它直接攻击删器件的逻辑前提。若 full bridge 能利用完整 reverse blocking 把 fault current 或 recovery transient 隔离，而 reduced bridge 因缺少某只 diode/transistor 形成不可控通路，那么“没有 disadvantages or penalties”的作者表述就不能推广到 grid-interface duty。论文自己的比较承认两级 DAB 能在 MV fault 时断开 dc-link capacitor，而本文硬件没有验证 fault handling。[pdf:E09]（PDF 物理页 9，Section VI、Table III）

判据应是器件 physics 级而非只看 controller 是否稳定：任何删减位置的 peak voltage 超 rating、fault current \(I^2t\) 明显高于 full bridge、或恢复后若干周期无法重新建立 ZVS，都构成具体反例。相反，如果 reachable transient envelope 仍严格落在保留器件能力内，才说明简化不仅对稳态 buck/boost 成立。

## § 12 — Follow-up Research Idea

电力电子领域通常看重可解释的拓扑增益、可实现的器件/磁件设计、宽工况效率与热数据、故障安全、MV prototype 和可重复的动态实验，而不只看 nominal waveform。基于第 9 节，候选研究方向是：**从“手工分析正常电压集合后删器件”升级为“面向正常、切换与故障全状态的可达集约束拓扑综合”**。由于本卡未做论文外的系统相关工作检索，这里明确标为候选想法，不声称 novelty。

**(a) 未满足的需求。** MVdc SST 既想减少器件，又必须保证 startup、bidirectional reversal、fault isolation 和 recovery；目前论文只对正值 dc-port 正常集合和 scaled-down steady buck/boost 给出闭合证据。[pdf:E04]（PDF 物理页 4，Eq. (1)–(4)）[pdf:E13]（PDF 物理页 13，Conclusion）

**(b) 研究价值。** 若能把“每个位置必须保留哪些 controllable/blocking capabilities”写成 hybrid switched system 的 reachable-set 约束，再共同优化 semiconductor VA、conduction loss、fault energy 和 soft-switch margin，结果将是带安全证书的 topology family，而不是单一工况的器件删减。它能直接回应 MV prototype 最关心的可靠性与 protection。

**(c) 可借鉴的方法。** 可借鉴 formal reachability、hybrid automata、robust optimization 与 power-module topology synthesis：开关状态是离散变量，\(i_m\)、\(v_C\)、leakage current 是连续状态，器件极性/额定值是安全约束；控制器、parasite 与参数偏差共同定义可达集合。

**(d) 第一个证伪实验。** 在作者 Table VI 级别 prototype 上加入可编程 dc breaker 与可切换 full/reduced device positions，执行双向 power reversal 加 bus fault/recovery 的组合序列。若综合器给出的 reduced topology 在任何重复试验中超出预测 voltage/current envelope，或者只能靠过大的 snubber/derating 才安全，想法即被证伪。

**(e) 与本文的实质区别。** 本文从已知 CS converter 的正常运行波形推导两个 reduced-switch topology，再分别做仿真和缩比验证；候选工作把问题改写为“给定全 operating/fault specification，自动求最小 blocking/controllable device set，并输出可验证安全边界”。研究目标从 nominal efficiency-oriented reduction 变为 safety-constrained topology synthesis，这不是再加一个辅助支路或换一类 SiC device。
