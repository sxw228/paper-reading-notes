# Deep Learning-Based Equivalent Modelling of Hybrid RES Plant for Efficient, Repetitive Power System Transient Stability Studies

作者：Ana Radovanović；Jovica V. Milanović  
出处：IEEE Transactions on Power Systems，Vol. 39，No. 2，pp. 3008–3020  
年份：2024（2023 年 online publication）  
DOI：10.1109/TPWRS.2023.3281498  
Zotero key：T6QUXW9V  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“用 LSTM 预测一条功率曲线”这么窄的问题，而是：在一年内 HRES（hybrid renewable energy source）电站的风、光、径流式水电出力不断变化、外部短路故障也不断变化时，能否用少量 dynamic equivalent model（DEM）替代含大量单元、控制器和保护的详细模型，反复开展暂态稳定仿真，同时仍可靠复现 PCC（point of common coupling）处的有功、无功时域响应。作者把 PCC 正序电压的实部和虚部作为输入，把 PCC 有功、无功作为输出，并希望只根据预报到的电站运行组成就选出当时要用的 DEM。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

工程价值有两层。第一，HRES 详细模型会把大系统年度、多场景稳定评估变成高计算量任务，而且详细参数还可能因数据难取得或保密而不可用；黑箱 DEM 可以把站内复杂性收缩到边界端口。[pdf:E01]（PDF 物理页 1，Introduction）第二，已有 equivalent 往往只在少数运行点和扰动上建立，或者只优化全系统 transient stability index（TSI），未证明模型能覆盖全年、也未必保留 PCC 波形。因此本文真正检验的是两件事：少量模型能否覆盖典型年度响应；以及“把波形拟合得很准”是否真的会让系统级 TSI 判断更准。[pdf:E02]（PDF 物理页 2，Introduction）

本文研究的是 positive-sequence RMS transient stability simulation，不是 EMT 开关瞬态；论文也明确指出稳定模型不适合 electromagnetic transients。[pdf:E06]（PDF 物理页 6，Eq. (5) 前的方法说明）因此其价值应理解为提高重复 RMS 稳定研究的可用性，而不能外推成面向微秒级电磁暂态或 FPGA 实时仿真的等值方案。

## § 2 — 前人工作与不足

论文对前人工作的梳理可分为三类。物理型 grey-box aggregation 会把风电场或光伏站缩放成 single-machine 或 multi-machine equivalent，但 coherent groups 会随风速、辐照度、出力和控制参数改变，因而仍面对运行点依赖。system identification 路线曾用 Prony、线性/transfer function（TF）、Gaussian process 和 recurrent ANN 建模 ADN、microgrid 或 RES plant；其中 LSTM 已被用于 ADN equivalent，以缓解普通 recurrent ANN 的 vanishing gradient。不过这些 ANN 工作往往只覆盖一种主要发电技术，且训练响应数量少。[pdf:E01]（PDF 物理页 1，Introduction）[pdf:E02]（PDF 物理页 2，prior work）

本文最直接的前作是作者自己的 TF-based HRES DEM。它先按系统 TSI 聚类，再让同一 TSI cluster 的响应共享一个 TF equivalent，所以两个时域形状明显不同的 PCC 响应，只要产生相近的全局 TSI，就可能被同一个模型代表。[pdf:E02]（PDF 物理页 2，和工作 [18] 的区别）这不是简单的“TF 表达能力不足”，而是建模目标本身不同：前作优先保住一个全局指标，本文则先按响应形状聚类、再用 LSTM 拟合，同时反过来检验这种额外波形精度是否值得。

作者声称的相对增量主要是：用历史生产与故障统计构造全年较可能的场景；用 hierarchical clustering（HC）按 P/Q 波形形状分组；用 PSO 系统搜索 LSTM 拓扑而非 trial-and-error；设计较省训练成本的样本选择；并提供仅凭 individual RES output 选择 DEM 的规则。[pdf:E03]（PDF 物理页 3，major contributions 与 Fig. 1）这里的 novelty 只按论文自身的相关工作定位陈述；本卡没有联网复核 2023 年前后的全部相关文献，所以不作独立 novelty 结论。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，而不是作者逐字陈述。研究者首先会发现：详细 HRES plant 虽然能表达 limiter、ramp rate、control 和 protection，却不适合在大量年度场景中重复运行；纯粹按一个 operating point 建模又无法处理全年出力分布。[pdf:E03]（PDF 物理页 3，Methodology opening）于是第一步自然是把历史风、光、水出力压缩成少数 characteristic plant compositions，再以 transmission-network fault statistics 为约束做 Monte Carlo（MC），让训练数据覆盖“高概率年度工况”而不是任意手造故障。

第二步的冲突是：同一出力组成在不同故障下会产生不同 P/Q 波形，而同一 TSI 又可能对应不同波形。如果目标是端口动态 equivalent，就应先把 P/Q response 做尺度无关的比较，再按 shape 分组。论文比较四种 normalization 后采用 z-normalization，并把每个案例的 z-normalized P、Q 拼成一个向量做 agglomerative HC。[pdf:E04]（PDF 物理页 4，Section II-C、Fig. 2、Eq. (1)–(3)）

第三步是把每个 response cluster 变成可执行 DEM。LSTM 用近期 PCC 电压历史恢复动态记忆，inverse z-normalization 再把网络输出还原到当前工况的 MW/Mvar。若每个 cluster 都部署一个模型，使用者在仿真前还不知道故障，无法仅凭出力选 cluster；所以作者又为每个 characteristic composition 选出综合误差最低且支持样本较多的一个 DEM，最后把模型选择问题收缩为“当前出力最接近哪个 characteristic composition”。[pdf:E05]（PDF 物理页 5，DEM structure 与 Eq. (4)）[pdf:E08]（PDF 物理页 8，Section II-E 与 Eq. (12)）

## § 4 — 核心 Intuition

核心 intuition 是：先用历史数据把“全年可能遇到的运行组成”离散化，再用故障统计生成这些组成下的动态响应；对响应形状聚类后，每一类交给一个具有时间记忆的 LSTM equivalent。在线使用时不预测故障类别，而只按 forecasted plant composition 选择预先训练好的一个 DEM；作者的关键赌注是，一个 composition 对应的单一 DEM 足以在多种常见故障下保持可接受稳定指标。[pdf:E03]（PDF 物理页 3，Fig. 1 与 methodology）

## § 5 — 具体方法与完整 Pipeline

以“某时刻预测到 PV、WF、HPP 各自出力，需要在 IEEE 9-bus 系统中反复测试短路”为例，完整 pipeline 如下。

1. **年度运行组成压缩。** 对 2015–2018 年 Central-Northern Italy 的逐小时 PV、WF、run-of-river HPP production data 做 fuzzy c-means；MSE、CDI、MIA 三个指标分别建议 9、6、10 个 cluster，取中位数 9，cluster centroid 即九种 characteristic HRES compositions。[pdf:E10]（PDF 物理页 10，Section IV 与 Table I）
2. **构造较可能的年度扰动响应。** 对每个 characteristic composition 生成 1,000 个 MC 案例：individual plant output 在 centroid 周围 ±5% 变化，站内连接线长度在 0.5–5 km 采样；fault type、location、impedance 按 transmission-network fault statistics 取样。详细 HRES 与网络在 DIgSILENT/PowerFactory 中仿真，得到 PCC P/Q 和 synchronous generators rotor angles。[pdf:E04]（PDF 物理页 4，Section II-B）
3. **按波形而非绝对功率聚类。** 每个 P/Q response 先 z-normalize，再拼成一个向量；使用 average-linkage、Euclidean-distance 的 agglomerative HC，并以 MSE、CDI、MIA 的 elbow 选 cluster 数。9,000 个响应最终形成 12 个 response clusters。[pdf:E04]（PDF 物理页 4，Section II-C）[pdf:E10]（PDF 物理页 10，simulation results）
4. **每个 cluster 训练一个 LSTM DEM。** 网络输入共 10 个量，即 PCC 正序电压实部、虚部相对 pre-disturbance value 的 normalized deviation，在当前步和前四步各取一次；输出是 z-normalized P、Q。LSTM 后接 fully connected（FC）layers，inverse normalization 用当前 pre-disturbance P/Q 与该 cluster 的 representative standard deviation 恢复绝对功率。[pdf:E05]（PDF 物理页 5，Fig. 3、Section II-D-1、Eq. (4)）
5. **搜索架构并控制训练成本。** hidden-layer 数从少到多迭代，total DEM error 改善低于 1% 时停止；给定层数后，PSO 搜索每层 LSTM cells/FC neurons。训练样本不是随机铺满 cluster，而是在第一摆峰值的响应范围内等距抽取；training/validation 比例为 70/30，early stopping 采用 validation error 连续 6 次上升的规则，Adam 使用默认 hyperparameters。[pdf:E06]（PDF 物理页 6，Fig. 4–5 与 Eq. (5)–(7)）[pdf:E07]（PDF 物理页 7，Fig. 6–7 与 training description）
6. **把 12 个初始 DEM 缩减成可部署集合。** 对每种 characteristic composition，计算每个相关 DEM 的 cluster response error 除以该组成在该 cluster 中的 response 数；index 最小者成为该组成的模型。任意新组成先找 Euclidean distance 最近的 characteristic composition，再使用它的 best DEM。[pdf:E08]（PDF 物理页 8，Section II-E 与 Eq. (12)）在本文案例中，12 个模型缩减为 DEM 1、6、8、10 四个。[pdf:E11]（PDF 物理页 11，Fig. 10 与结果说明）
7. **在 PowerFactory 中执行。** 每个 simulation time step，PowerFactory 把 PCC phase voltage 变换成正序电压的实、虚部并经 Matlab interface 送入 `.mat` DEM；Matlab 返回 P/Q，PowerFactory 用 PCC 上的 controllable constant-power load 注入对应功率。[pdf:E08]（PDF 物理页 8，Fig. 8、Section II-F）

离散与事件边界必须明确：论文报告的 simulation duration 为 10 s、sampling rate 为 1 ms，fault 在 1 s 发生并持续 100 ms；这说明数据步长，但没有报告 solver 的数值积分细节或 multi-rate strategy。[pdf:E10]（PDF 物理页 10，Section IV）详细模型包含 WF/PV 的 fault-ride-through、limiter、ramp rate 和 protection，所测案例中它们不因故障脱网；论文未报告 DEM 的显式 switch/event state，也未验证 individual plant tripping。[pdf:E10]（PDF 物理页 10，test-system controls）并行实现只报告 PSO 在 8-core Intel Xeon E5-2650 v2、64 GB RAM、Nvidia V100 上运行，architecture search 用时 6–48.5 h；没有报告 equivalent simulation 的 speedup、实时步长余量、数值精度、定点化、FPGA 映射、资源占用或端到端 latency。[pdf:E11]（PDF 物理页 11，implementation results）因此这是一套 Matlab + PowerFactory 的 RMS software workflow，不是已实现的 EMT/FPGA pipeline。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出 LSTM cell 内部方程的新推导；数学核心是“波形可比化 → 绝对量重建 → 模型/架构选择 → 稳定性验证”这条误差闭环。

第一步把任一 P 或 Q 响应 \(Y(t)\) 标准化：

\[
z(t)=\frac{Y(t)-Y_{\mathrm{mean}}}{SD(Y(t))},\qquad
Y_{\mathrm{mean}}=\frac{1}{n}\sum_{t=1}^{n}Y_t,
\]

\[
SD(Y(t))=\sqrt{\frac{1}{n-1}\sum_{t=1}^{n}(Y_t-Y_{\mathrm{mean}})^2}.
\]

这里 \(z(t)\) 消除 operating level 和幅值尺度，让 HC 更关注 shape；\(n\) 是样本数。[pdf:E04]（PDF 物理页 4，Eq. (1)–(3)）

第二步把 LSTM 输出还原成可注入网络的实际功率：

\[
Y_{\mathrm{DEM}}[t]=z_{\mathrm{LSTM}}^{Y}[t]\cdot SD_{\mathrm{rep}}^{Y}+Y_{\mathrm{SS}}.
\]

\(Y_{\mathrm{SS}}\) 是该案例 pre-disturbance P 或 Q，\(SD_{\mathrm{rep}}^{Y}\) 是相应 response cluster 的 representative standard deviation。直觉上，LSTM 只生成“标准化动态偏移形状”，工况的基线与 cluster 的典型动态尺度负责把它变回 MW/Mvar。[pdf:E05]（PDF 物理页 5，Eq. (4) 与变量定义）

第三步定义 architecture search 的误差。单一 response、单一时刻的相对误差为

\[
DEM\_Y_{i,t}^{Err}=\frac{Y_{\mathrm{DEM},i,t}-Y_{\mathrm{ORG},i,t}}
{Y_{\mathrm{ORG},i,t}}\times100\%.
\]

作者在 fault clearing 后的每个 time step，对 cluster 内这些绝对误差取 95th percentile，再跨时间取最大值：

\[
95PCTL_Y=\max_{1+N_{\mathrm{Flt}}\le t\le N_T}
95PCTL\left(\{|DEM\_Y_{i,t}^{Err}|\}_{1\le i\le N_{\mathrm{Resp}}}\right),
\]

并以

\[
PSO_{\mathrm{Cost}}=DEM^{Err}
=\sqrt{(95PCTL_P)^2+(95PCTL_Q)^2}
\]

搜索结构。这个 cost 针对 cluster 内较坏的尾部响应，而不是只优化平均案例。[pdf:E06]（PDF 物理页 6，Eq. (5)–(7)）

真正训练网络时使用可微的 mean squared cost：

\[
LSTM_{\mathrm{Cost}}=
\frac{1}{N_{\mathrm{SubResp}}}\sum_{i=1}^{N_{\mathrm{SubResp}}}
\frac{1}{N_T}DEM_i^{SErr},
\]

\[
DEM_i^{SErr}=DEM_i^{SErr,Flt}+DEM_i^{SErr,AftFlt}.
\]

fault-duration 部分和 post-fault 部分分别累加 P、Q relative error 的平方；前者乘 \(w=0.01\)，后者不降权。作者这样保留从 fault occurrence 开始的可微训练序列，同时把稳定分析真正关心的 post-fault response 放在主导位置。[pdf:E07]（PDF 物理页 7，Eq. (8)–(11) 与说明）

第四步把 response-cluster 模型变成 composition-selector。对第 \(q\) 个 characteristic composition 和第 \(p\) 个 DEM：

\[
IdxDEM_p^q(\%)=\frac{DEM_{p}^{Err,RespRel_q}}
{NRespRel_p^q}.
\]

分子是在 cluster \(p\) 中、属于 composition \(q\) 的 responses 的 total error，分母是这些 responses 的数量；index 最小者被选为该 composition 的 DEM。[pdf:E08]（PDF 物理页 8，Eq. (12)）这个除法使少数高误差响应和大量相关响应之间形成经验折衷，但它不是统计置信界。

最后，单个 validation case 的波形误差取 fault clearing 后最大相对差，P/Q total error 再作 Euclidean combination：

\[
DEM_{i,Y}^{Err,CS}=\max_{1+N_{\mathrm{Flt}}\le t\le N_T}|DEM\_Y_{i,t}^{Err}|,
\]

\[
DEM_i^{Err,CS}=\sqrt{(DEM_{i,P}^{Err,CS})^2+(DEM_{i,Q}^{Err,CS})^2}.
\]

系统级 TSI error 为

\[
TSI^{Err}=100\left|\frac{TSI_{\mathrm{ORG}}-TSI_{\mathrm{DEM}}}
{TSI_{\mathrm{ORG}}}\right|,\qquad
TSI=\frac{360-\delta_{\max}}{360+\delta_{\max}}\times100\%,
\]

其中 \(\delta_{\max}\) 是同一时刻任意两台 synchronous generators 的最大 rotor-angle difference。[pdf:E08]（PDF 物理页 8，Eq. (13)–(16) 及变量定义）

## § 7 — 实验设计与结论

**问题一：历史数据能否压缩成少量、可训练的年度场景？ →** 作者用 2015–2018 逐小时 production/demand data 得到 9 个 characteristic compositions，每个生成 1,000 个 MC simulations，共 9,000 个开发案例；HC 得到 12 个 response clusters，而 composition-based selection 最终只需 4 个 DEM。[pdf:E10]（PDF 物理页 10，Table I 与 MC setup）[pdf:E11]（PDF 物理页 11，Fig. 10）**答案：** 在这个三技术、单区域、按给定 fault statistics 生成的测试系统里，模型数确实从 12 降到 4；这证明的是经验压缩，不是任意技术组合都固定只需四个。

**问题二：只给每个 characteristic composition 一个 DEM，会损失多少开发集精度？ →** 用四个选定 DEM 重新运行全部 9,000 个开发案例，比较 detailed/equivalent P、Q response 的 post-fault maximum error，并计算 TSI error。P error 的 50th/95th percentile 为 1.4%/5.8%，Q 为 5.6%/20.4%；Q 的 absolute error 是 1.2/3.9 Mvar；TSI error 为 0.1%/0.6%。[pdf:E11]（PDF 物理页 11，Fig. 11 与正文）**答案：** composition-only selection 对 real power 和 TSI 很准，但 reactive-power relative error 的尾部明显较大；小 Q denominator 是部分原因。

**问题三：模型能否跨年份泛化？ →** 用同一区域 2019 measurement data 另建 non-training MC cases，再按 forecasted composition 选模型。P、Q maximum response error 的 median 分别为 1.8%、8.8%，95th percentile 为 8.7%、28.6%；Q absolute error 的 50th/95th percentile 为 1.2/3 Mvar，TSI error 约为 0.7%/3%。[pdf:E11]（PDF 物理页 11，2019 test opening）[pdf:E12]（PDF 物理页 12，Fig. 12–13 与正文）**答案：** 同分布式跨年测试仍保持较小 TSI error，但 Q relative-error 尾部进一步扩大。

**问题四：追求更准的 PCC 波形是否显著改善系统稳定判断？ →** 将 LSTM DEM 与按 TSI 聚类得到的 TF DEM 对比。LSTM 在 development/test cases 的 median TSI error 只比 TF 小 0.04%/0.3%，而在多数 plant compositions 上又确实更好地拟合 P/Q shape。[pdf:E12]（PDF 物理页 12，comparison 与 Conclusion）**答案：** 作者的反直觉结论是：对该测试范围，high-fidelity time-domain response 不是获得可靠 TSI assessment 的必要条件；LSTM 的主要优势是波形保真与潜在的多指标/多扰动适用性，而不是已证明的 TSI 数量级提升。

**问题五：哪些关键验证没有做？ →** 论文没有给出 wall-clock simulation speedup、部署内存、实时性、其他网络规模、field measurement playback、different protection regime、extreme disturbance 或 individual plant tripping 结果；作者把最后一项明确列为 future work。[pdf:E12]（PDF 物理页 12，Conclusion）因此标题中的 “efficient, repetitive” 主要由模型压缩和训练策略支撑，不是由端到端运行时间 benchmark 支撑。

## § 8 — Take-aways

**5 句话：**  
1. 论文把年度历史 production data 和 fault statistics 转成 9,000 个较可能的 HRES transient-stability cases，再按 P/Q shape 聚类。[pdf:E03]（PDF 物理页 3，Fig. 1）  
2. 每个 response cluster 用一个 LSTM DEM 表示，输入是五个时刻的 PCC 正序电压实、虚部，输出经 inverse z-normalization 变回 P/Q。[pdf:E05]（PDF 物理页 5，Fig. 3、Eq. (4)）  
3. composition-based selector 把 12 个初始模型压缩为 4 个，使使用者只需知道 individual RES output。[pdf:E11]（PDF 物理页 11，selection results）  
4. 2019 non-training cases 的 median P/Q error 为 1.8%/8.8%，median TSI error 约 0.7%，但 Q 的 95th-percentile relative error 达 28.6%。[pdf:E12]（PDF 物理页 12，test results）  
5. LSTM 的波形拟合更好，却只把 median TSI error 相对 TF 改善 0.3%（test year），所以本文也给出了一个重要负结论：更精细的端口波形不必然带来更准确的 TSI。[pdf:E12]（PDF 物理页 12，TF comparison）

**3 句话：** 这是一套用历史分布定义 training domain、用 shape clustering 定义模型族、再用 operating composition 做在线选择的 RMS dynamic-equivalent workflow。[pdf:E03]（PDF 物理页 3，Fig. 1）它在同一区域跨年 MC 测试中以四个 DEM 保持较小 TSI error，但 reactive-power relative error 尾部较大，且没有覆盖 protection-induced topology change。[pdf:E12]（PDF 物理页 12，test results 与 Conclusion）对 EMT/FPGA 读者，最重要的不是 LSTM 名称，而是论文没有给出 EMT 离散、real-time runtime 或 hardware mapping，不能把其结果直接当作实时等值实现证据。

**1 句话：** 用少量 composition-selected LSTM 可以在典型年度 RMS 故障中复现 HRES 端口动态，但论文自己的对比也说明，波形更准不等于 TSI 显著更准。[pdf:E12]（PDF 物理页 12，Conclusion）

## § 9 — 最脆弱的假设

失败代价最大的假设是：**仅凭 pre-disturbance HRES composition 选择一个固定 DEM，就足以覆盖该组成下所有实际相关 disturbance regimes。** selector 不使用 fault type、location、impedance、clearing action 或 protection event；它隐含假设这些因素虽改变 response，却不会把系统推入训练 clusters 未覆盖的机制状态。[pdf:E08]（PDF 物理页 8，Section II-E）

论文给出的支持证据是：fault statistics 驱动的大量 MC cases、9,000 个开发响应，以及同区域 2019 non-training cases 的小 TSI median error。[pdf:E10]（PDF 物理页 10，MC setup）[pdf:E12]（PDF 物理页 12，test results）但这些案例仍围绕“most probable annual responses”，WF/PV 具备 fault-ride-through 且不在故障中断开；作者没有测试 individual plant tripping，并明确把 extreme disturbance with tripping 留给 future work。[pdf:E10]（PDF 物理页 10，control/protection assumptions）[pdf:E12]（PDF 物理页 12，Conclusion）一旦同一 composition 因保护动作进入不同 topology，使用相同 \(Y_{\mathrm{SS}}\)、cluster representative \(SD_{\mathrm{rep}}\) 和同一个 LSTM 的机制基础会失效；这比普通的参数误差更可能直接破坏等值模型。

## § 10 — 最小复现实验

一周内最值得复现的是“composition-only selector 在 unseen faults 下能否保住 TSI”，而不是完整重做全年 PSO。

- **数据：** 在 IEEE 9-bus + PV/WF/HPP detailed model 上选两个差异较大的 characteristic compositions；每个 composition 生成约 200 个 training/validation faults，再生成 100 个 unseen fault location/impedance/clearing cases。保持 1 ms sampling 和 10 s 窗口，记录 PCC 正序电压、P/Q 与 synchronous-generator rotor angles；这些量与论文的模型接口和验证指标一致。[pdf:E09]（PDF 物理页 9，Fig. 9 与 test-system description）[pdf:E10]（PDF 物理页 10，simulation setup）
- **实现：** P/Q 做 z-normalization；每个 composition 先直接训练一个小型 LSTM，不做完整 PSO，只保留论文的五步电压窗口、inverse normalization、70/30 split、post-fault-oriented loss 和 early stopping。这样验证 selector claim，而不是把时间花在架构搜索。
- **测量：** 对 unseen cases 计算 P/Q post-fault maximum relative/absolute error 与 TSI error，同时记录 detailed 与 DEM 的稳定/不稳定判断是否一致。
- **支持标准：** 若两个 composition 的 unseen-case median/95th-percentile TSI error 能接近论文 2019 benchmark 的约 0.7%/3%，且没有稳定类别翻转，就支持“只用 composition 可覆盖常见故障”的核心 claim。[pdf:E12]（PDF 物理页 12，2019 results）
- **反驳标准：** 若在 composition 完全匹配时仍出现可重复的稳定类别翻转，或少数 fault regime 形成系统性的 TSI-error tail，即使平均 P/Q error 尚可，也反驳 selector 的充分性。

该复现不会验证“训练更快”或“适合 FPGA”，因为论文没有提供可对照的 simulation speedup、fixed-point 或 hardware resource 指标。[pdf:E11]（PDF 物理页 11，reported platform and runtime）

## § 11 — 最强反例设计

最强反例是构造**相同 pre-disturbance composition、相近 PCC voltage sag，但不同保护结果**的一对场景：场景 A 故障清除后 PV/WF 全部 ride through；场景 B 只改变 clearing time、fault impedance 或 protection threshold，使一个 RES plant 触发 crowbar 后持续限流，或直接 tripping。selector 在两者开始前看到的 individual RES output 完全相同，因此必然选择同一个 DEM；而 detailed system 的 post-fault topology、可用容量和控制状态已经不同。

具体攻击步骤是：固定 Table I 中一个高 HPP 或高 WF composition，逐步扫 fault clearing time，找到 protection boundary 两侧的成对案例；训练集只含 non-tripping cases，测试集加入 tripping cases。若 DEM 在 B 中仍回到由原 \(Y_{\mathrm{SS}}\) 和 \(SD_{\mathrm{rep}}\) 定义的连续响应，而 detailed model 出现永久功率台阶、不同 rotor-angle separation 甚至稳定类别变化，那么失败可以明确归因于 missing event/topology state，而不是一般的 hyperparameter 不佳。该反例直接击中论文承认未覆盖的 extreme disturbance and plant tripping。[pdf:E12]（PDF 物理页 12，Conclusion）

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：** 把问题从“按 operating composition 选择一个全年 DEM”改成“对 protection-driven regime change 给出可检测、可拒绝、可切换的 hybrid dynamic equivalent”。需求来自第 9 节：实际 HRES plant 的关键风险不是同一连续动力学内的波形误差，而是 fault ride-through、limiter、crowbar、unit tripping 造成动力学模式和 topology 改变；单一 composition selector 无法观测这种变化。[pdf:E10]（PDF 物理页 10，reported controls and protection）[pdf:E12]（PDF 物理页 12，future work）

这个方向的研究价值在于把 equivalent model 从无条件 point predictor 变成带适用域的 stability-analysis component：常见 regime 内给 P/Q 响应，检测到 out-of-distribution event 时明确 abstain 或切换 event-conditioned expert，并为 TSI 结果提供 coverage boundary。可借鉴相邻领域的 hybrid-system identification、change-point detection、mixture-of-experts 和 calibrated out-of-distribution detection，但这些工具在本卡中只是候选方法，不是已检索确认的新组合。

第一个可证伪实验采用 leave-one-event-regime-out：用 normal ride-through、current-limit、crowbar 等若干 regime 训练，把 individual-plant tripping 整类留作测试；比较原 composition-only DEM、event-conditioned DEM 和 detailed model。如果新方法既不能在 tripping 前及时拒绝，也不能显著减少 TSI category flip，那么“显式 regime state 能补上 composition selector 缺口”的研究假设被否证。它与本文的实质区别不是多加一层 LSTM，而是改变接口和评价目标：输入从静态 composition 扩展到可观测 event evidence，输出从无条件 P/Q trajectory 扩展为 trajectory 加 applicability decision，目标从平均年度拟合转为跨保护模式的可审计稳定判断。
