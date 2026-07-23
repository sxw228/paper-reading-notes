# MSDF-SGD：面向任意精度训练的最高有效位优先随机梯度下降

## 论文身份与证据边界

- 论文：Changjun Song, Yongming Tang, Jiyuan Liu, Sige Bian, Danni Deng, He Li, “MSDF-SGD: Most-Significant Digit-First Stochastic Gradient Descent for Arbitrary-Precision Training”
- 出处：2023 33rd International Conference on Field-Programmable Logic and Applications (FPL)
- DOI：10.1109/FPL60245.2023.00030
- Zotero key：`TSXICTYN`
- slug：`song-msdfsgdmost-significant-digit-first2023`
- 源文件：`_source.pdf`
- PDF SHA-256：`499500ab89d85962999393c4c3f3325eda0fb1ff3ea21f2f6c9bde7326d652c9`
- 领域定位：这不是 EMT、实时电磁暂态仿真或 HIL 论文，而是一篇直接面向 FPGA 上机器学习训练的算法-架构协同论文。下面只分析其 MSDF 算术、SGD 数据流、早停机制和真实硬件证据，不把它强行映射为 EMT 方法。

## § 1 — 研究问题与重要性

论文要解决的不是一般意义上的“让 SGD 更快”，而是一个更具体的硬件约束：现有 bit-serial 训练加速器可以在运行时改变输入数据的精度，但模型参数和点积、梯度等中间量的位宽通常在设计时固定。不同数据集、不同训练阶段乃至不同样本需要多少位才能兼顾准确率和吞吐量并不容易预先知道；如果为每种精度保存一份数据或重新生成硬件，灵活性和存储收益就会消失。作者因此提出 MSDF-SGD，希望数据、模型和中间量都能按最高有效位优先的串行流处理，让“运行多少个 digit”直接决定本次计算精度。[pdf:E01]

这个问题的重要性来自训练而非推理。训练需要反复读取样本、计算点积或梯度并写回模型，低精度可以同时减少计算和数据搬运，但精度过低又可能改变优化轨迹。MSDF-SGD 的目标是把精度从静态硬件参数变成运行时调度量，并利用最高有效位先到达这一时序性质，在分类 margin 已经足够时提前跳过剩余特征和模型更新。[pdf:E01][pdf:E04]

作者把核心贡献概括为四项：任意精度的数据/模型/中间量架构、针对 piecewise loss 的早停、在三个线性分类数据集上的 FPGA 评估，以及用于生成更复杂训练数据流的编程接口。这里需要立即划清证据强度：前三项有架构或实验支撑；“支持多层、非线性模型”只展示了接口语法与生成思路，没有给出相应模型的端到端训练实验。[pdf:E01][pdf:E07]

## § 2 — 前人工作与不足

论文把前人方法分为两类。第一类是面向 inference 的 bit-serial accelerator。Stripes 和 Pragmatic 串行读取输入、并行读取模型，因此只有输入精度可变；Loom 让输入和模型都按 bit-serial 读取，但乘积位宽仍固定。FGIE 使用 MSDF 并让输入、模型和中间量都可变，但它服务于 MLP inference，不是训练。[pdf:E02]

第二类更接近本文的训练场景。Bis-KM 用 LSDF bit-serial 算术加速 FPGA 上的 K-means，但模型与中间量精度不灵活；MLWeaving 用 SGD 训练线性模型，输入精度可调，但模型参数和中间量固定为 32 bit。论文 Table I 据此把 MSDF-SGD列为唯一同时满足 flexible inputs、flexible models、flexible intermediates 且用于 SGD training 的 MSDF 架构；这是作者依据其所列工作的“first”主张，不应扩大成对全部文献的独立穷尽证明。[pdf:E02]

这些不足不是简单的“前人没想到可变精度”。LSDF 从最低有效位开始产生结果，即使输入是串行的，早期结果也不能可靠回答 margin 是否已经大于阈值，而且常见 Bis-Mul 仍输出固定宽度的 bit-parallel 结果。MSDF online arithmetic 则用冗余 signed-digit 表示，从最高有效位开始交付结果，因而既能随计算时间增加精度，又能在无需完整结果的比较任务中暴露提前结束的机会。[pdf:E02]

## § 3 — 重建作者的思考路径

下面是基于论文背景和方法结构重建的思考路径，不是作者逐字陈述。

第一步，训练加速的真正瓶颈不只在乘法器，还在样本读取、点积累加和模型更新三段流水之间的吞吐匹配。只让输入位宽可变，会把固定宽度的模型与中间量留成新的瓶颈。[pdf:E01][pdf:E03]

第二步，bit-serial 把数值精度变成时间：多运行若干周期就多获得若干 digit。但如果按 LSDF 顺序交付，先得到的是对大小判断最没帮助的低位；换成 MSDF online arithmetic，前缀已经包含数值的主要量级，比较器可以在完整点积到达前开始工作。[pdf:E02][pdf:E04]

第三步，寻找一个能把“提前得到高位”转化成“少做训练工作”的控制条件。线性分类器的 hinge-loss 类目标正好具有 piecewise 性质：当 `y_i × dot > 1` 时，本样本不再触发对应的模型更新。于是，若比较器能从点积的 MSDF 前缀确认 margin 已越过阈值，就可以中止尚未完成的乘加、跳过未读取特征，并直接调度下一个样本。[pdf:E03][pdf:E04]

第四步，算术顺序改变后，内存布局也必须改变。若普通布局仍按完整 feature 连续存储，读取一个 cache line 后无法同时得到许多 feature 的同一 digit。作者因此把同一 digit 位置的多个 feature 组成 word，使一次 memory transaction 天然匹配 inter-feature parallelism，也让“停止读取低位”成为连续的地址跳转。[pdf:E04]

第五步，串行化会降低单通道吞吐，所以需要分别设置 loading、dot-product、update 的 feature parallelism，并让三段的“并行度/精度”比值大致平衡。由此形成一个算法、数值表示、内存布局、并行度和控制流共同设计的系统，而不是单独替换乘法器。[pdf:E03][pdf:E05]

## § 4 — 核心 Intuition

MSDF-SGD 的核心是把“精度”变成一条从最高有效位向最低有效位逐步展开的时间流：计算得越久，结果越精确，但很多样本并不需要等到全部低位到齐。对具有 margin 条件的 SGD，只要高位前缀已经足以判定本样本无需更新，就立刻跳到下一个样本，从而同时省掉后续算术和后续内存访问。[pdf:E01][pdf:E04]

它能奏效的关键不只是 MSDF 乘加器，而是内存也按 digit plane 重排、三个训练阶段按各自精度配置并行度、比较器又被接入点积流水。任一环节仍按固定宽度或传统布局工作，运行时任意精度和早停收益都会被其他环节抵消。[pdf:E03][pdf:E04][pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以论文 Fig. 4 的两样本简化例子理解数据入口：`FPD=4`、`FPI=2`，每个 feature 有 4 个 digit，但本次只使用前三个。传统布局会连续存放一个 feature 的全部 digit；MSDF layout 则先把四个 feature 的第一位组成一个 4-bit word，再存第二位和第三位，未采用的最低位 word 不读取。这样一次访问拿到多个 feature 的同一显著位，早停时地址可以直接跳到下一样本的首个 word。[pdf:E04]

完整训练 pipeline 如下：

1. **精度与吞吐配置。** 用户分别指定输入、点积中间量和模型更新的精度 `K_I`、`K_D`、`K_U`。硬件的三个并行度是输入加载 `FP_I`、点积计算 `FP_D`、模型更新 `FP_U`。论文建议让 `FP_I/K_I ≈ FP_U/K_U ≈ FP_D/K_D`，避免某一段成为流水瓶颈；实验采用 `K_I:K_D:K_U=1:2:4`，因此 MSDF-4 表示 4-bit 输入、8-bit 中间量和 16-bit 模型。[pdf:E05]
2. **Loading。** 外部内存按 MSDF layout 送出 digit stream。输入以 `FP_I` 的 line rate 串行加载，累计成 `FP_D` 个 channel 后缓存在 signed-digit vector 中；加载与后续点积采用 ping-pong buffer 重叠执行。[pdf:E03][pdf:E04]
3. **Accumulating。** `FP_I` 路 MSDF multiplier 同时消费样本与模型 digit，adder tree 在乘积最高位到达后即开始累加。多个单元共同给出 `FP_D` 维局部点积，重复处理后得到完整 `M` 维 `dot`。MSDF operator 统一经历 Init、Transmit 和 Fill 三段；输出流长度决定精度，初始 online delay 则决定首个有效 digit 何时出现。[pdf:E02][pdf:E03][pdf:E04]
4. **Early termination。** 每一轮 partial dot product 的显著位都送往比较器。若 `y_i × dot > 1` 被判定成立，硬件中止当前累加与后续 model update，并跳过本样本未处理的 feature，直接开始下一样本。Fig. 3 的例子中，无早停时下一 feature 在 C11 开始；发生早停时，新样本在 C9 开始。[pdf:E03][pdf:E04]
5. **Updating。** 未早停时，Algorithm 1 先计算 `e = dot - y_i`，再求 `g = e × x_i`，最后执行 `w ← w - λg`。作者把学习率 `λ` 设为 2 的负整数次幂，以便在串行表示中简化实现。mini-batch 模式使用 local model 暂存，batch 完成后再更新 global model。[pdf:E03][pdf:E04]
6. **模型调度。** 与通过多个样本共享模型、最后求平均的 inter-sample parallelism 不同，MSDF-SGD 串行更新模型并逐样本调度；这降低了 BRAM 的读写位宽，但也把收益绑定到单样本早停频率。论文给出的反例尺度是：若同步更新 64k-bit model vector，需要超过 900 个 BRAM，锁步访问还会压低频率。[pdf:E03]

从硬件映射看，Fig. 2 的 I、II、III 三个模块分别对应 loading、accumulating、updating；global/local model、input buffer、比较器和 early-termination shortcut 构成闭环。这个结构直接面向 FPGA 训练，而不是把 CPU 版 SGD 原样翻译成 RTL。[pdf:E04]

## § 6 — 核心数学推导

论文先给出经验风险最小化形式：

`min_w (1/N) Σ_{i=1}^N f(w^T x_i, y_i)`，

其中 `x_i` 是含 `M` 个 feature 的第 `i` 个样本，`w` 是模型向量，`y_i` 是标签，数据集共有 `N` 个样本。SGD 不对整个数据集求一次梯度，而是用单一样本近似下降方向：

`w ← w - λ × ∂f(w^T x_i, y_i)/∂w`。

这两式解释了硬件为何可分成取样、点积和更新三段，也解释了为何逐样本跳过能减少真实工作量。[pdf:E02]

Algorithm 1 把本文使用的线性分类训练具体化。对每个 epoch 和样本，先分块累计 `dot = w^T x_i`；若 `y_i × dot > 1`，执行 early termination；否则计算 `e = dot - y_i`、`g = e x_i`，再做 `w ← w - λg`。[pdf:E03] 从 hinge-loss 的直觉看，`y_i × dot` 是分类 margin，超过 1 意味着样本已在安全侧，继续精化低位并执行更新的边际价值很低。需要注意，论文没有在 Eq. (1) 中写出完整的具体 loss，也没有展开从该 loss 到 Algorithm 1 的逐项推导，因此这里不能把算法中的误差项强行等同于某个未明示的标准 hinge-loss 变体。

MSDF 数值层使用 digit 集 `{1,0,-1}` 的冗余 signed-digit 表示，并以 `x_j = x_j^+ - x_j^-` 编码每个 digit。冗余表示的作用是让 online operator 能在低位尚未输入时开始输出高位，避免普通进位链必须等待全部低位。论文展示了 comparator、adder、multiplier 的结构与 Init/Transmit/Fill 时序，但没有给出这些 operator 的完整 recurrence 或误差界，因此本卡不补造电路级推导。[pdf:E02][pdf:E03]

三个阶段的吞吐平衡式可以从“每批工作量约与精度成正比、与并行度成反比”理解。若 loading、dot、update 的周期数分别近似与 `K_I/FP_I`、`K_D/FP_D`、`K_U/FP_U` 成正比，那么令三者接近就能减少流水空泡。这正是作者建议 `FP_I/K_I ≈ FP_D/K_D ≈ FP_U/K_U` 的物理含义；它是工程配平规则，不是收敛定理。[pdf:E05]

## § 7 — 实验设计与结论

**问题一：降低三类数值的精度会不会破坏分类准确率？** 作者在 MNIST、Epsilon、Gisette 上训练线性分类器 100 epochs，比较 MSDF-4、MSDF-8、MSDF-16。Fig. 5 报告的准确率分别为：MNIST `93.6/90.6/90.6%`，Epsilon `86.0/86.2/85.9%`，Gisette `97.5/97.5/97.4%`。在这三组结果中，低精度没有显示出系统性准确率损失；作者推测低位主要承载数据噪声。但图中没有误差条，正文没有报告随机种子或多次重复，因此它只能说明这些具体训练设置下的观察，不能证明低位普遍无用。[pdf:E05]

**问题二：任意精度是否真的转化为吞吐收益？** 以 MSDF-16 为 1，MSDF-2 在三个数据集上约为 `3.03/3.05/2.98×`，MSDF-4 为 `2.80/2.81/2.75×`，MSDF-8 为 `1.75/1.79/1.73×`。吞吐随精度降低而上升，但输入低于 4 bit 后收益转为次线性，因为单个计算周期内没有足够数据填满加载并行度，serial latency 开始占主导。[pdf:E05][pdf:E06]

**问题三：早停本身贡献多少？** 作者对比启用与禁用早停的 elapsed time。MNIST、Epsilon、Gisette 的最高加速分别为 `2.02×`、`1.23×`、`1.62×`，表明收益强烈依赖数据集有多少样本能提前跨过 margin。[pdf:E05][pdf:E06]

**问题四：相对已有硬件和 CPU 方法是否更快？** 作者以 MLWeaving-4/32 为 FPGA baseline，以 Hogwild、ModelAverage 为 CPU baseline；所有硬件方法按 200 MHz 比较，CPU 数字则取自 Wang 等人的工作，使用 14-core 和 AVX2，并非本文在同一平台上的重新测量。Fig. 8 显示 MSDF-4 达到相同 loss 时，相比 MLWeaving-4 在 Gisette 和 Epsilon 上约快 `1.6×` 和 `1.4×`；相对 CPU 方法，作者报告最高 `8.6×` convergence-efficiency speedup。正文还报告 MSDF-4 相比 MLWeaving-4 少 `40%` memory transaction，原因是早停跳过 loading；这应理解为访问量下降，不是 FPGA 静态 BRAM 容量减少。[pdf:E06]

**问题五：硬件是否真实落地？** MSDF-SGD 部署在 Zynq UltraScale+ XCZU19EG MPSoC，频率 200 MHz，`FP_I=512`、`FP_D=1024`、`FP_U=2048`。Table III 报告总资源为 `279,054 LUT (53.38%)`、`347,688 FF (33.26%)`、`108 BRAM (10.97%)`，并说明全部算术由 MSDF operator 实现、DSP 使用量为 0。early-termination shortcut 本身只占 `108 LUT`、`96 FF`、`1 BRAM`。这些是明确的 FPGA implementation evidence，而不是根据算法结构推断的“可上 FPGA”。[pdf:E05]

**问题六：能否扩展到复杂模型？** 论文给出以 `INPUTS`、`OUTPUTS`、`MODEL`、`GRAD` 描述模型和梯度的接口，并支持基本运算、`sum/norm`、`relu/sigmoid/log`；dynamic-scheduling HLS 用于生成 dataflow component 和 handshake。可是论文没有展示多层或非线性模型的训练精度、资源、频率、吞吐或收敛曲线，所以“可生成”与“已验证为有效训练加速器”必须分开。[pdf:E07]

## § 8 — Take-aways

### 5 句话

1. MSDF-SGD 把输入、模型和中间量全部改成最高有效位优先的串行流，使运行时间直接对应数值精度。[pdf:E01][pdf:E02]
2. 它真正的系统创新是算术、digit-plane 内存布局、三阶段并行度和逐样本控制流的联合设计，而不是单个 MSDF multiplier。[pdf:E03][pdf:E04]
3. 对 margin 型 piecewise loss，高位前缀可让比较器提前确认无需更新，从而跳过低位、剩余 feature 和模型写回。[pdf:E04]
4. XCZU19EG 上的资源与 200 MHz 实验，以及相对 MLWeaving 的吞吐/收敛曲线，证明这不是纯软件设想；但收益大小随数据集早停机会明显变化。[pdf:E05][pdf:E06]
5. 编程接口只证明了生成路径的表达能力，尚未证明复杂非线性模型的训练质量和硬件效率。[pdf:E07]

### 3 句话

1. 论文把可变精度从输入扩展到整个 SGD 数据路径，并用 MSDF 前缀驱动控制决策。[pdf:E01][pdf:E02]
2. 其 `1.6×` 硬件 baseline 加速主要来自早停，而早停在不同数据集上只有 `1.23×` 到 `2.02×`，说明数据分布决定了系统收益。[pdf:E05][pdf:E06]
3. 真正尚未闭合的是：低位何时可以安全省略，以及复杂模型中这种省略是否仍保持收敛。

### 1 句话

MSDF-SGD 的本质是让“数值精度前缀”同时成为计算结果和硬件调度信号，但论文只在线性分类器上验证了这种做法的有效范围。[pdf:E04][pdf:E07]

## § 9 — 最脆弱的假设

最脆弱的假设是：**高位前缀通常足以做出与完整精度一致的更新/不更新决策，而且被省略的低位既不会频繁改变 margin 分支，也不会长期改变收敛轨迹。**

这个假设一旦失效，论文最有辨识度的收益会同时受损。若样本集中在 decision boundary 附近，`y_i × dot` 与 1 的差距可能由许多低位及乘加抵消共同决定；系统要么过早判定并错误跳过一次更新，要么必须等待几乎全部 digit 才能安全判定，前者伤害收敛，后者消灭加速。论文的 Fig. 5 说明三个数据集的最终准确率没有因所选精度明显下降，Fig. 6 又说明早停确实节省了时间，但没有报告“partial comparison 与完整 dot 判定不一致的比例”、margin 分布、每样本实际消费的 digit 数，或逐步误差界。[pdf:E05][pdf:E06]

证据覆盖也偏窄：只有三个线性分类 workload，其中 Epsilon、Gisette 是二分类，MNIST 虽有 10 类，但论文没有在算法描述中解释 multiclass 映射；没有 error bar、seed、学习率具体值或输入缩放细节。更复杂模型仅有接口，没有真实训练结果。[pdf:E03][pdf:E05][pdf:E07] 因此，硬件资源和既有 workload 的速度结果可信，但“任意精度训练普遍可安全早停”仍未被证明。

另一个比较边界是 CPU baseline 来自既有工作而非统一平台复测，且正文明确提到 CPU memory bandwidth 约为 FPGA 的 4 倍。`8.6×` 是特定 loss-vs-time 比较下的 convergence-efficiency 结果，不宜解释成对通用 CPU 训练的无条件加速。[pdf:E06]

## § 10 — 最小复现实验

一周内最值得复现的不是整套编程接口，而是“MSDF 前缀早停能否在不改变训练决策的前提下节省 digit”这一因果核心。

1. 选 Epsilon 或 Gisette，复现论文的线性分类器；把输入、模型和中间量量化为 MSDF-4 对应的 `4/8/16 bit`，另保留完整精度或 32-bit fixed-point reference。[pdf:E05]
2. 写一个 bit-/digit-accurate 软件模拟器，按最高有效位逐位暴露乘积与累加结果，并严格复现 Algorithm 1 的 `y_i × dot > 1` 分支。每个样本同时计算完整 dot，记录 partial comparator 首次给出结论的周期、最终分支是否一致、跳过的 feature/digit 数。[pdf:E03][pdf:E04]
3. 做三组对照：禁用早停、论文式早停、只有在“剩余低位的最坏区间也不可能把 margin 拉回 1 以下”时才早停。第三组不是论文原方法，而是用于判断论文加速是否依赖未经量化的判定风险。
4. 测量 final loss、test accuracy、逐样本分支不一致率、平均消费 digit、估算周期和 memory word 读取量；至少运行多个 seed，并按完整 margin 到 1 的距离分桶。
5. 支持核心 claim 的结果是：论文式早停分支不一致率接近 0，final loss/accuracy 与无早停等价，同时平均 digit 和 memory access 明显下降，并出现接近论文所报 `1.23×–1.62×` 的数据集相关收益。[pdf:E06] 反驳结果是：边界样本出现系统性误判或收敛漂移，或者为了保持零误判必须读取绝大多数 digit，导致收益接近 1。

若时间允许，再把一个 MSDF multiplier-adder-comparator 链在 XCZU19EG 或同代 UltraScale+ 上综合，以检查 online delay、200 MHz 和资源数量级；但这属于第二优先级，因为论文最需要先验证的是早停的数值正确性，而不是再次证明 MSDF operator 能综合。[pdf:E05]

## § 11 — 最强反例设计

最强反例是一组 **margin-adversarial、低位决定分支** 的样本。构造两类输入，使它们的高位 digit 完全相同，但通过多个 feature 的正负抵消，让完整点积分别落在 `1-ε` 和 `1+ε`；决定符号的差异只存在于最低若干位。再逐渐减小 `ε`，并提高 feature 数，使部分和的高位在很长时间内看似已经稳定。

这个反例会迫使系统落入二选一：

- 如果比较器只根据当前 MSDF 前缀断言 `y_i × dot > 1`，就可能把本应更新的 `1-ε` 样本误判为无需更新，长期累积后改变分类边界。
- 如果实现为了正确性等待到所有未到达 digit 的误差范围都无法翻转比较结果，那么越靠近 margin，越接近完整精度运行，早停和 memory-traffic 优势消失。

实验应同时加入“低位不是独立噪声、而是与标签相关”的数据版本，以直接挑战作者对 Fig. 5 的解释。成功反例不是只让准确率下降，而是展示下降或加速消失与 margin 距离、抵消强度和低位信息量之间可预测的关系。这样可以排除“只是超参数没调好”的替代解释，并精准攻击 MSDF 前缀驱动训练控制这一核心机制。[pdf:E04][pdf:E05]

## § 12 — Follow-up Research Idea

### 候选想法：带可证误差界的 anytime training fabric

FPGA/数字设计领域通常不会只凭算法新颖性评价高影响工作；它还要求可综合架构、时序与资源闭合、端到端 workload、与强 baseline 的同条件比较，以及对数值误差和系统可扩展性的可复现验证。基于这些标准，一个非增量方向不是再增加一种 precision setting，而是把训练目标改成：**硬件在任意 digit 前缀处都给出剩余误差的可计算区间，只有当该区间能证明更新决策或梯度误差满足预算时才允许终止。**

（a）驱动需求是现有 MSDF-SGD 把精度交给用户配置，并依赖数据集自然产生可早停 margin，却没有给每次提前结束一个可核验的数值正确性契约。[pdf:E05][pdf:E06]

（b）潜在研究价值在于把“任意精度”从性能旋钮升级为 correctness-aware scheduling：同一套 fabric 可根据样本 margin、层敏感度和当前优化阶段自动分配 digit，报告的是有界训练误差与实际节省，而不是只报告平均精度。

（c）可借鉴相邻领域的 interval arithmetic、anytime algorithm、mixed-precision error budgeting 和鲁棒优化。每个 MSDF operator 除结果前缀外还传播一个“未到达低位的最大剩余量”，scheduler 用该区间判断比较分支是否不可翻转，或梯度扰动是否落在本轮预算内。

（d）第一个能够证伪它的实验就是第 11 节的 margin-adversarial 数据：若证书为了保持正确几乎总要等到完整精度，或者区间传播的 LUT/时序开销超过省下的周期，那么这个方向不成立。

（e）它与本文的实质区别是问题定义不同。MSDF-SGD 证明了 MSDF 数据流、运行时精度和早停可以在三个线性分类 workload 上带来收益，并用接口表达更复杂模型；新方向要求每次早停都携带可验证的数值理由，并把“复杂模型是否仍可安全省略 digit”作为核心实验，而不是接口扩展项。[pdf:E04][pdf:E07]

在未检索更广泛的 certified approximate computing、interval online arithmetic 和 adaptive-precision training 文献前，这只能称为候选研究方向，不能声称 novelty。

## PDF 证据缓存

| ID | PDF 物理页 | 定位 | 上下文图 |
|---|---:|---|---|
| E01 | 1 | 标题、摘要、Introduction、C1–C4 | [E01-p001-abstract-contributions.png](_evidence/E01-p001-abstract-contributions.png) |
| E02 | 2 | Eq. (1)–(2)、LSDF/MSDF 背景、Table I、operator 时序说明 | [E02-p002-sgd-msdf-priorwork.png](_evidence/E02-p002-sgd-msdf-priorwork.png) |
| E03 | 3 | Fig. 1、Algorithm 1、feature parallelism、架构入口 | [E03-p003-operators-algorithm-parallelism.png](_evidence/E03-p003-operators-algorithm-parallelism.png) |
| E04 | 4 | Fig. 2–4、更新、早停时序、MSDF memory layout | [E04-p004-architecture-termination-memory.png](_evidence/E04-p004-architecture-termination-memory.png) |
| E05 | 5 | Table II–III、硬件配置、精度配置、Fig. 5–6 | [E05-p005-setup-resources-precision.png](_evidence/E05-p005-setup-resources-precision.png) |
| E06 | 6 | Fig. 7–8、hardware/CPU baseline、吞吐和收敛比较 | [E06-p006-throughput-convergence.png](_evidence/E06-p006-throughput-convergence.png) |
| E07 | 7 | Table IV、dynamic-scheduling HLS 接口、Conclusion | [E07-p007-interface-conclusion.png](_evidence/E07-p007-interface-conclusion.png) |
