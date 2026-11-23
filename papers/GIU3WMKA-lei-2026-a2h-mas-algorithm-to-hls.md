# A2H-MAS: An Algorithm-to-HLS Multi-Agent System for Automated and Reliable FPGA Implementation

- **作者**：Jie Lei, Ruofan Jia, J. Andrew Zhang, Hao Zhang
- **出处**：Proceedings of the 2026 ACM/SIGDA International Symposium on Field Programmable Gate Arrays (FPGA 2026)（源 PDF 为 arXiv:2508.10904v3 预印本排版）
- **年份**：2026
- **DOI**：10.1145/3748173.3779557
- **Zotero key**：GIU3WMKA

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

算法研发与高效 FPGA 硬件实现之间的工程鸿沟，长期制约着无线通信物理层、雷达信号处理等强低延迟、严资源受限领域的快速落地（物理页 1，Abstract 与 Section I `[pdf:E01]`、`[pdf:E02]`）。工程实践中，算法研究者普遍在 MATLAB 中完成物理层原型开发与工具箱级仿真验证 `[pdf:E02]`；然而即便借助高层次综合（HLS）以 C/C++ 替代手写 RTL Verilog，从“功能正确的 MATLAB 脚本”跨越到“时序收敛、低延迟且省资源的 HLS C++ 硬件核”依旧高度依赖资深硬件工程师反复手工调优 `[pdf:E01]`、`[pdf:E02]`。

此前该流程长期卡住的根源在于两重结构性矛盾：
1. **CPU 帧级全局访存与 FPGA 样本流式流水范式的冲突**：MATLAB 代码默认将数万点基带波形驻留在全局内存中做整帧向量化运算与随机索引（物理页 4–6，Fig. 4 与 Section IV-D `[pdf:E07]`、`[pdf:E10]`），而 FPGA 依赖逐样本连续数据流（streaming）、局部移位寄存器、双口 BRAM 环形缓冲与恒定启动间隔（II）流水线 `[pdf:E10]`。若不改写微架构而直接语法翻译，综合器会将整帧数组映射为庞大寄存器阵列与多路复用网络，引发查找表（LUT）/触发器（FF）爆炸甚至布局布线后（post-route）时序违例（物理页 8，Table II `[pdf:E16]`）。
2. **黑盒库函数遮蔽与单一大模型长链路失控**：MATLAB 工具箱封装函数掩盖了底层算术与访存细节，阻碍硬件级重组（物理页 5，Section IV-C `[pdf:E09]`）；而单一大语言模型（LLM）在跨越模块切分、函数展开、流式改写、跨语言翻译、定点字长压缩与系统集成的长窗口任务时，极易出现指令幻觉、上下文遗忘与静默数值失真（物理页 1–2，Fig. 1 `[pdf:E02]`、`[pdf:E03]`）。

打通从初版 MATLAB 原型到可综合 HLS 硬件系统的可靠自动化链路，可将数周手工定点化、流式改写与 RTL 联调压缩为标准化闭环，直接生成可在软件无线电平台（如 NI USRP X310 RFNoC）上板运行的物理层硬件核（物理页 7，Section V `[pdf:E14]`）。

## § 2 — 前人工作与不足

作者在物理页 1–2（Section I–II）与物理页 9 参考文献中对比了三类前人路线并剖析其局限 `[pdf:E02]`、`[pdf:E04]`、`[pdf:E18]`：

1. **领域语料微调的专用 HDL 生成模型（VerilogEval、MG-Verilog、VGen、RTLLM、VeriGen）**：
   通过构建多粒度 Verilog 数据集微调中小规模基座模型 `[pdf:E02]`、`[pdf:E04]`。其瓶颈在于：高质量硬件代码语料稀缺且大规模微调算力高昂，难以在实际工程中频繁重训；同时 Claude Sonnet 4、GPT-4、Gemini 2.5、DeepSeek-Coder-V2 等通用前沿大模型在零样本/少样本代码推理与电路生成（如 `AnalogCoder`）上已反超微调小模型 `[pdf:E02]`、`[pdf:E18]`，真正瓶颈不在词法生成而在长链路工程可控性。
2. **单智能体迭代反馈框架（AutoChip、HDLAgent、HLSPilot、HDLCore）**：
   直接调用通用大模型并接入编译/仿真反馈修复代码 `[pdf:E02]`、`[pdf:E04]`，但存在三处硬伤：① **评测盲区**：偏重单模块功能正确性，忽视周期延迟、吞吐率、DSP/BRAM/LUT 开销与布局布线后主频等关键 PPA 指标 `[pdf:E03]`；② **优化层级倒置**：如 `HLSPilot` 默认输入已是 C/C++，仅在循环展开、流水等 pragma 层修补，未能触及对硬件效率起数量级决定作用的**算法结构选择与帧到流微架构重构**（物理页 2 与页 6，Section I 与 IV-E `[pdf:E03]`、`[pdf:E11]`）；③ **单 Agent 认知过载**：单一上下文难以可靠贯穿多模块无线接收机的全栈转换 `[pdf:E03]`。
3. **多智能体协作框架（ChatDev、MetaGPT、VeriMind）**：
   虽引入角色分工与验证协同（如 `VeriMind`） `[pdf:E04]`，但多依赖自然语言对话传递状态，缺乏面向“MATLAB 原型 → 流式重构 → HLS 综合与 RTL 协同仿真 → 多模块流式集成”的**低耦合文件契约、确定性工具护栏与冻结的阶段间参考真值**（物理页 3，Section III `[pdf:E05]`）。

## § 3 — 重建作者的思考路径

从无线通信硬件工程师试图用通用 LLM 把现成 MATLAB 接收机搬上 FPGA 时遭遇的真实失败现象出发，可逆向还原出本文核心设计的四步推演：

1. **直译翻车暴露真凶在计算范式**：让大模型直接把含工具箱调用和整帧向量运算的 MATLAB 脚本翻成 HLS C++ `[pdf:E03]`，不仅工具箱黑盒函数会被幻觉改错，整帧数组还会被综合成数万 LUT/FF 甚至布线时序直接失败 `[pdf:E16]`。可见在跨语言翻译前，必须先做**内置函数白盒内联**与**帧级全局数组向样本级流式缓冲的架构改写** `[pdf:E09]`、`[pdf:E10]`。
2. **同构语言先改架构、异构语言只做保真映射**：若边转 C++ 边改流式滑窗又同时砍定点位宽，一旦结果出错根本无法分离故障源。反之，留在 MATLAB 同构环境内先内联源码并改写为流式缓冲代码，即可利用秒级批处理命令直接对照原版数据验算逻辑等价，把收益最大的架构手术留在验证成本最低的软件层解决 `[pdf:E06]`、`[pdf:E09]`、`[pdf:E10]`。
3. **用文件契约、冻结真值与确定性规则锁死多智能体边界**：多模块长链路改写必然触发 LLM 遗忘与自由发挥。既然通信接收链路天然呈前馈数据流拓扑，便可先按数据流切分子模块，在原版测试台中截取各切口中间变量固化为 `in.txt`/`ref.txt` 并生成接口 JSON，让各专职 Agent 仅通过标准目录通信 `[pdf:E05]`、`[pdf:E07]`、`[pdf:E08]`；同时用确定性 `grep` 正则先将模块硬分类至四档流式可行域并绑定已验证的缓冲模板，消除盲目试错 `[pdf:E06]`、`[pdf:E10]`。
4. **HLS 层拆分“宽位宽初译”与“脚本化字长/指令 DSE”，强制 RTL 协同仿真签核**：初译 C++ 时先给足宽数据类型以隔离量化噪声 `[pdf:E11]`，跑通功能后再用自动化脚本扫描定点字长与 pragma；针对 HLS 综合静态报告延迟常与流握手真实运行周期偏离的痛点，强制用 C-RTL 协同仿真（`cosim`）卡死真实延迟，最后自动生成 AXI-Stream 顶层完成闭环上板 `[pdf:E12]`、`[pdf:E13]`。

## § 4 — 核心 Intuition

旧方法之所以在复杂硬件项目上失稳，是因为它逼迫单个大模型在一次跨语言跳跃中同时跨越“黑盒库函数展开、帧级转流式微架构、C++ 语法映射与定点字长/指令寻优”四重鸿沟，一旦保留帧级内存模型就会引发灾难性的逻辑膨胀与时序违例 `[pdf:E03]`、`[pdf:E16]`。A2H-MAS 的核心支点是**“按抽象层正交解耦：先在 MATLAB 同构层用规则与知识库完成帧到流及算法级重构，再以宽位宽无损翻译进 HLS C++，最后靠脚本化探索收紧定点字长与并行度”**，把决定数量级资源效率的架构变换前置到秒级可验的软件层 `[pdf:E10]`、`[pdf:E11]`、`[pdf:E12]`。配合文件系统标准接口、冻结的子模块输入输出真值以及确定性工具链（`grep` 分类、批处理测试与强制 RTL `cosim`），每个 Agent 的推理空间被压缩在可即时证伪的窄边界内，用确定性工程护栏对冲了大模型的幻觉与遗忘 `[pdf:E05]`、`[pdf:E06]`。

## § 5 — 具体方法与完整 Pipeline

### 5.1 正面回答本次阅读重点（Focus 四问拆解）

1. **各 Agent 的职责边界与解耦接口**：
   各专职 Agent 之间不共享隐式长对话，严格以标准模块目录 `MODULE_DIR/` 与元数据 `module_definition.json`（物理页 4 Fig. 4 标题拼写为 `module defination.json`）交接（物理页 3–5，Section III-A、Fig. 2、Fig. 4、Fig. 5 `[pdf:E05]`、`[pdf:E07]`、`[pdf:E09]`）。需注意源 PDF 存在一处编校错位：物理页 5 Fig. 5 图注写“seven modular phases”，物理页 6–7 Section IV-F/G 正文也误写为“fifth/sixth phase”，但 Fig. 5 图内框体与 Section IV 小节标题实为 **Phase I–VIII 共八个阶段** `[pdf:E09]`、`[pdf:E11]`、`[pdf:E12]`：
   - **Phase I（Modularization）**：按前馈数据流将 `ori.m` 拆解为最小接口子模块 `module_1..k.m` 并生成接口 JSON `[pdf:E08]`、`[pdf:E09]`；
   - **Phase II（Test Data Generation）**：在原测试台中挂载子模块，录制各切口输入输出固化为全流程唯一直通真值 `module_[name]_in.txt` 与 `module_[name]_ref.txt` `[pdf:E08]`、`[pdf:E09]`；
   - **Phase III（Function Flattening）**：调用 MATLAB 内置 `which` 定位工具箱与外部函数源码并内联为白盒文件 `module_[name]_flat.m` `[pdf:E09]`；
   - **Phase IV（Code Optimization）**：由 `Matlab-Optimization-Agent` 基于 `grep` 规则四分类与知识库缓冲模板，将帧级数组计算改写为样本流式 `module_[name]_opt.m` `[pdf:E05]`、`[pdf:E06]`、`[pdf:E10]`；
   - **Phase V（Algorithm-Hardware Co-Design）**：先于 pragma 调优实施算法级替换（如查表替超越函数迭代、相关转 FIR、按目标采样率配置多周期折叠降低并行乘法器） `[pdf:E09]`、`[pdf:E11]`；
   - **Phase VI（Code Translation）**：基于模板与知识库检索将 `opt.m` 译为采用流接口和宽初始位宽的 HLS C++ `module_[name].cpp` `[pdf:E09]`、`[pdf:E11]`；
   - **Phase VII（Refinement）**：保持代码结构不变，通过自动化脚本扫描定点字长、循环展开/流水因子与数组分割，清除 MATLAB 遗留冗余零初始化 `[pdf:E12]`；
   - **Phase VIII（Integration & Implementation）**：自动生成 `top.cpp`，以 AXI-Stream 与一对一流通道复制集成全系统，完成综合、协同仿真与比特流上板 `[pdf:E13]`。

2. **定点字长与流水架构优化机制**：
   采用“微架构流式化前置 + 定点字长延迟收缩”机制：在 MATLAB 层（Phase IV–V），先利用知识库中的**移位寄存器**（支撑 FIR 等多抽头并行读取实现 `II=1` 全流水）、**环形缓冲**（映射双口 BRAM 实现长延迟线单拍 $O(1)$ 更新）、**行缓冲**与**乒乓缓冲**消除全局内存随机访问 `[pdf:E10]`，并结合吞吐约束设定算子折叠周期以节省 DSP `[pdf:E11]`、`[pdf:E14]`；跨入 HLS 层后，Phase VI 故意分配宽数据类型以确保跨语言翻译零溢出 `[pdf:E11]`，待功能锁定后才在 Phase VII 用脚本化设计空间探索（DSE）收紧定点位宽、优化数组分割、剔除未初始化内存冗余清零并化简控制逻辑 `[pdf:E12]`、`[pdf:E16]`。

3. **验证闭环如何减少昂贵综合轮次**：
   构建分层早停漏斗：Phase I–IV 的全部拆解、内联与流式重构均通过秒级命令 `matlab -batch "run('module_[name]_opt_tb.m'); exit;"` 对照 `in.txt`/`ref.txt` 完成回归验算 `[pdf:E06]`、`[pdf:E08]`，绝不把算法或缓冲逻辑错误带入分钟级的 HLS 综合；进入 Xilinx Vitis HLS（Phase VI–VIII）后按 `csim → synthesis → C-RTL cosim` 递进 `[pdf:E12]`、`[pdf:E13]`，先由快速的 `csim` 拦截翻译 bug 与定点位宽截断越界，再对合格候选做综合，并强制以 RTL `cosim`（而非综合静态估算值）签核真实握手延迟，避免顶层拼装或生成比特流后因吞吐失配推倒重来 `[pdf:E12]`。

4. **实验如何设置基线与消融**：
   系统级选取 **5G NR SSB 检测**（5 子模块 + 顶层，USRP X310 RFNoC 部署）与 **WLAN 多制式时频同步**（4 子模块 + 顶层）验证多模块闭环能力 `[pdf:E14]`、`[pdf:E15]`；模块级抽取阈值计算 `calcThreshold` 与信号提取 `extractSSBsig` 设置三阶递进消融——`Direct`（LLM 从原始 MATLAB 直译 HLS C++ 的朴素基线）、`Adaptation`（正文亦作 `Adaption`，仅施加 MATLAB 层流式缓冲与状态机重构）、`Refinement`（叠加 HLS 定点字长调优、未初始化存储条件处理与控制化简），定量剥离前后端两级优化各自的贡献 `[pdf:E16]`。

### 5.2 贯穿实例工作流解析

以物理页 3–6 的分组检测子模块 `module_packet_detection`（Fig. 4）及滤波/延迟模板（Fig. 2–3、Fig. 5–6）为例：Phase I 切分后生成的 `module_definition.json` 明确定义模块 ID 为 `2`、输入为尺寸 `[26105, 2]` 的复数向量 `filteredWaveform`、输出为整型 `startOffset`，下游连接 `module_coarse_cfo_estimation` `[pdf:E07]`；Phase II 录制这 `26,105` 点双通道测试流与参考偏移量存入文本文件 `[pdf:E07]`、`[pdf:E08]`。Phase III 用 `which` 展平所有内置调用产出 `_flat.m` `[pdf:E09]`。进入 Phase IV 后，`Matlab-Optimization-Agent` 先运行确定性 `grep`（扫描 `fir(filt|1|2)`、`fft/ifft` 及高频标识符）将模块分入 `FULLY_STREAMABLE`（套用逐样本流式库）、`WINDOW_STREAMABLE`（环形缓冲滑窗增量更新）、`ADAPTIVE_STREAMABLE`（固定参数近似替代自适应变量）或 `BLOCK_ONLY`（仅做块内循环变换，禁止强转流式）四类 `[pdf:E06]`，再结合 Fig. 6 模板把帧级处理重写为外挂深度 `Depth: 512` 局部环形 BRAM 的流式结构 `opt.m` 并批处理验算 `[pdf:E09]`、`[pdf:E10]`。随后经 Phase V 算法折中、Phase VI 宽位宽 C++ 翻译、Phase VII 脚本化位宽/pragma DSE 与 `cosim` 延迟核验，最终由 Phase VIII 生成 `top.cpp`，在存在一对多数据依赖处自动复制 AXI-Stream 通道以维持一对一生产者—消费者语义，完成全系统综合与上板 `[pdf:E11]`、`[pdf:E12]`、`[pdf:E13]`。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 无编号形式化公式的原因说明

核查源 PDF 全 9 页版面可知，**全文无任何带编号的形式化数学公式（无 `Eq.`）**，仅在 Fig. 4 出现数组维度 `[26105, 2]` `[pdf:E07]`，在 Fig. 6 出现复杂度 `O(1)`、启动间隔 `II=1` 及离散缓冲索引代码 `[pdf:E10]`。其原因在于本文定位于**规则与工具驱动的多智能体编译工程框架**，未采用混合整数线性规划（MILP）或多面体调度理论建模 HLS，而是用“目录契约 + 经验测试向量回归 + 脚本枚举 + EDA 仿真器签核”替代解析推导 `[pdf:E05]`、`[pdf:E06]`、`[pdf:E12]`。

### 6.2 知识库原语隐含的离散硬件映射与严谨性支柱

物理页 6 Fig. 6 的两段核心代码实则封装了决定 FPGA 存储与流水效率的关键离散状态变换 `[pdf:E10]`：
1. **移位寄存器（`fir_filter_opt`）的空间并行解耦**：针对阶数 $L$ 的 FIR 滤波，帧级全局向量索引受限于片上 BRAM 每拍至多双端口读写的物理瓶颈，无法单拍喂饱 $L$ 路乘法器。代码通过 `shift_reg(2:L) = shift_reg(1:L-1); shift_reg(1) = x(i);` 将最近 $L$ 个样本显式驻留于无地址译码的触发器级联链（FF chain），使 `y(i) = sum(h .* shift_reg)` 的全部抽头在同一时钟沿并行可见，保证综合出 `II=1` 全流水电路 `[pdf:E10]`。
2. **环形缓冲（`delay_line_opt`）的模地址双口 BRAM 同构映射**：针对长延迟 `delay` 的顺序延迟线，若全缓冲移位会产生 $O(\text{delay})$ 寄存器翻转开销。代码利用静态数组 `buf` 与循环写指针 `ptr`，每拍仅写一次 `buf(ptr) = x(i)`，并用模运算 `read_ptr = mod(ptr-delay-1, delay)+1` 寻址历史样本后递增指针 `[pdf:E10]`。每拍恰好“一写一读”且数据原地不动，精准映射至单个双口 BRAM，将单样本更新复杂度降至 $O(1)$ `[pdf:E10]`。

方法整体的工程严谨性由三根结构支柱支撑：① `module_definition.json` 强类型接口定义防端口错位 `[pdf:E07]`；② 跨阶段复用的 `in.txt`/`ref.txt` 批处理回归防静默逻辑漂移 `[pdf:E08]`；③ 强制 RTL `cosim` 防静态延迟误判 `[pdf:E12]`。但缺乏形式化误差界也带来了明显短板：对 `WINDOW_STREAMABLE`/`ADAPTIVE_STREAMABLE` 的有损近似及 Phase VII 定点截断，全文未定义信噪比损失或跨模块误差传播上界 `[pdf:E06]`、`[pdf:E12]`。

## § 7 — 实验设计与结论

物理页 7–8 的 Section V 与 Table I、Table II 围绕“多模块系统端到端上板可行性”与“分阶段优化消融增益”展开定量验证 `[pdf:E14]`、`[pdf:E15]`、`[pdf:E16]`：

### 7.1 实验平台与基准规模

底层由 **Claude Code**（对应参考文献 `[6]` Claude Sonnet 4 `[pdf:E18]`）驱动代码生成与架构优化，配合 MATLAB 与 Xilinx Vitis HLS 测试两套无线系统 `[pdf:E14]`：
1. **5G NR SSB 检测系统**：符合 3GPP 标准，基于 **NI USRP X310** 与 **RFNoC** 实现；主同步互相关核 `pssCorrelator` 配置为**每 8 拍处理 1 个样本**以节省 DSP，仍满足 **7.68 Msps** 实时吞吐需求 `[pdf:E14]`；
2. **WLAN 时频同步系统**：支持 **20/40/80 MHz** 带宽及 **Non-HT、HT、VHT、HE** 四种物理层帧格式 `[pdf:E14]`。

### 7.2 全子模块与系统顶层综合结果（Table I）

1. **5G NR SSB 检测（5 子模块 + 顶层）** `[pdf:E14]`、`[pdf:E15]`：
   - 子模块：`pssCorrelator`（`6,329` LUTs, `21,088` FFs, `276` DSP, `0` BRAM, `254.00 MHz`）、`calcThreshold`（`173` LUTs, `274` FFs, `3` DSP, `1` BRAM, `322.27 MHz`）、`peakFinder`（`1,061` LUTs, `1,439` FFs, `0` DSP, `0` BRAM, `279.02 MHz`）、`collectLocations`（`85` LUTs, `211` FFs, `0` DSP, `0` BRAM, `332.78 MHz`）、`extractSSBsig`（`155` LUTs, `148` FFs, `0` DSP, `4` BRAMs, `269.11 MHz`）；
   - **Top level**：`8,669` LUTs、`24,216` FFs、`279` DSP、`7` BRAMs，主频 **`292.23 MHz`** `[pdf:E15]`。子模块累加为 `7,803` LUTs、`23,160` FFs、`279` DSP、`5` BRAMs，可见 `pssCorrelator` 占顶层 `98.9%` DSP，顶层流控与 FIFO 仅新增 `866` LUTs 与 `2` 块 BRAM，且在 `292.23 MHz` 下 8 拍折叠吞吐达 `36.53 Msps`（超 `7.68 Msps` 指标 `4.76` 倍）。
2. **WLAN 同步（4 子模块 + 顶层）** `[pdf:E14]`、`[pdf:E15]`：
   - 子模块：`filter_detect`（`908` LUTs, `4,190` FFs, `111` DSP, `0` BRAM, `407.83 MHz`）、`coarse_cfo`（`3,699` LUTs, `2,393` FFs, `15` DSP, `16` BRAMs, `359.19 MHz`）、`fine_timing`（`1,784` LUTs, `5,016` FFs, `68` DSP, `0` BRAM, `359.71 MHz`）、`fine_cfo`（`3,942` LUTs, `2,755` FFs, `16` DSP, `29` BRAMs, `358.81 MHz`）；
   - **Top level**：`10,981` LUTs、`14,787` FFs、`210` DSP、`76` BRAMs，布局布线后主频 **`337.61 MHz`** `[pdf:E14]`、`[pdf:E15]`。子模块累加仅 `45` 块 BRAM，顶层却跃升至 **`76` 块 BRAM（净增 `31` 块，`+68.9%`）**，暴露出跨多级同步分支做一对一流通道复制时的显著片上缓冲开销 `[pdf:E13]`、`[pdf:E15]`。

### 7.3 三阶段消融结果与评测盲区（Table II）

对 `calcThreshold` 与 `extractSSBsig` 对比 `Direct`、`Adaptation`（正文作 `Adaption`）与 `Refinement` `[pdf:E16]`：
- **`calcThreshold`**：`Direct` 耗费 `36,500` LUT、`80,434` FF、`38` DSP、`16` BRAM，延迟 `6,385` 周期且布局布线时序**失败（Clock: `Failed`）**；经 `Adaptation` 流式重构后降至 `685` LUT（`-98.12%`）、`1,176` FF（`-98.54%`）、`24` DSP、`4` BRAM，主频收敛至 `277.09 MHz`，延迟 `6,301` 周期；再经 `Refinement` 定点位宽与控制精化后压至 **`173` LUT**（较 `Direct` 压缩约 `211` 倍/`-99.53%`）、**`274` FF**、**`3` DSP**、**`1` BRAM**，主频提升至 **`322.27 MHz`**，延迟 `6,013` 周期 `[pdf:E16]`。
- **`extractSSBsig`**：`Direct` 为 `4,468` LUT、`7,071` FF、`0` DSP、`24` BRAM、`265.11 MHz`、延迟 `24,890` 周期；`Adaptation` 降至 `275` LUT（`-93.85%`）、`353` FF、`4` BRAM（`-83.33%`）、`253.29 MHz`、延迟腰斩至 `12,441` 周期；`Refinement` 进一步达 **`155` LUT**、**`148` FF**、**`4` BRAM**、**`269.11 MHz`**，延迟降至 **`6,730` 周期**（累计缩减 **`72.96%`**，对应正文所述最高 `73%` 降幅） `[pdf:E16]`。
- **客观评测缺口**：尽管物理页 8–9 Section VI 总结该框架具备强工程实用性与可扩展性 `[pdf:E17]`、`[pdf:E18]`，但实验未对比商业标杆 **MATLAB HDL Coder** 或同类智能体 `HLSPilot` `[pdf:E02]`、`[pdf:E18]`，未披露最重算力核 `pssCorrelator` 的消融数据，亦缺少 Token 消耗、综合迭代轮次、多轮成功率及定点化后的无线检测率/频偏估计精度曲线。

## § 8 — Take-aways

**5 句话版**：A2H-MAS 针对高实时无线通信领域将帧级 MATLAB 算法转化为高效 FPGA 硬件核的高门槛痛点，构建了规则引导与确定性工具约束的分层多智能体框架 `[pdf:E01]`、`[pdf:E03]`。它将端到端流程拆解为模块切分、测试数据固化、函数展平、MATLAB 流式优化、算法—硬件协同设计、宽位宽 C++ 翻译、脚本化 DSE 精化与 AXI-Stream 顶层集成八个低耦合阶段 `[pdf:E09]`、`[pdf:E11]`、`[pdf:E12]`、`[pdf:E13]`。核心方法论在于“算法与缓冲重构优先于 pragma 调优”，先在秒级可验的 MATLAB 层靠 `grep` 四分类与移位寄存器/环形缓冲知识库消除全局内存访问，进入 HLS 后先以宽位宽隔离翻译误差再脚本化压缩定点字长并强制用 RTL 协同仿真签核真实延迟 `[pdf:E06]`、`[pdf:E10]`、`[pdf:E11]`、`[pdf:E12]`。实验在 5G NR SSB 检测（USRP X310）与多制式 WLAN 同步上分别实现 `292.23 MHz` 与 `337.61 MHz` 系统主频，消融中相对 LLM 直译最高削减 `99.5%` LUT 与 `73%` 延迟并消除时序违例 `[pdf:E14]`、`[pdf:E15]`、`[pdf:E16]`。但框架强依赖单向前馈流拆解假设，面对跨模块紧耦合闭环反馈与多分支流复制引发的顶层 BRAM 膨胀仍存结构瓶颈 `[pdf:E06]`、`[pdf:E15]`。

**3 句话版**：A2H-MAS 利用标准化目录契约、冻结的子模块输入输出真值与确定性脚本工具，把易发生幻觉和遗忘的单一大模型改造为分阶段可验的 MATLAB-to-HLS 多智能体流水线 `[pdf:E03]`、`[pdf:E05]`、`[pdf:E08]`。其最大技术杠杆是把帧到流存储重构前置到同构 MATLAB 层用批处理秒级验证，跨入 HLS 后采用“宽位宽保真初译 + 脚本化定点字长/指令 DSE + 强制 RTL 协同仿真”的两步收敛机制 `[pdf:E10]`、`[pdf:E11]`、`[pdf:E12]`。该设计在 5G NR 与 WLAN 前馈同步系统上实现了百倍级逻辑压缩与 `>290 MHz` 时序收敛，但尚未攻克闭环反馈延迟失稳与顶层通道复制存储开销问题 `[pdf:E15]`、`[pdf:E16]`。

**1 句话版**：A2H-MAS 通过“MATLAB 同构层流式重构前置 + 文件契约与确定性仿真护栏 + HLS 宽位宽初译后置定点 DSE”的三重正交解耦，将不可控的大模型跨层硬件生成转化为步步可即时证伪的流水线编译工程 `[pdf:E05]`、`[pdf:E10]`、`[pdf:E12]`。

## § 9 — 最脆弱的假设

全文失败代价最大的唯一核心假设是：**“复杂算法总能无损或可控有损地切分为单向无环、局部独立的前馈数据流子模块（Feedforward Decoupled Submodule Assumption），使得逐模块孤立完成的流式近似与定点裁剪在用 AXI-Stream 拼回顶层后，仍能同时保住全局闭环收敛性与片上存储效率。”**

1. **论文提供的正面证据**：在 5G NR SSB 检测这类纯开环前馈链路上，数据单向流动，Phase II 录制的静态 `in.txt`/`ref.txt` 足以充当子模块完备验证边界 `[pdf:E08]`，顶层集成仅增 `2` 块 BRAM 即达 `292.23 MHz` `[pdf:E15]`。
2. **论文回避或缺失的关键证据**：
   - **静态阉割闭环反馈**：Fig. 3 对 `ADAPTIVE_STREAMABLE` 规定“将自适应参数替换为合理固定值并接受近似” `[pdf:E06]`，直接回避了锁相环（PLL）载波跟踪、自动增益控制（AGC）或判决反馈均衡（DFE）等逐拍紧耦合闭环——在真实闭环中，HLS 流水与 AXI-Stream 握手注入的多拍环路延迟 $z^{-D}$ 会直接压缩稳定域引发振荡，绝无法靠静态开环 `in.txt` 独立调优单模块后串联工作；
   - **顶层存储膨胀初露端倪**：即便在开环 WLAN 同步上，因单模块孤立优化未统筹跨阶段旁路数据生命周期，Phase VIII 通道复制使顶层 BRAM 从子模块之和的 `45` 块激增至 `76` 块（`+31` 块） `[pdf:E13]`、`[pdf:E15]`；
   - **缺失级联误差评估**：尽管作者在结论与展望中期待向计算机视觉与更广信号处理域扩展 `[pdf:E17]`、`[pdf:E18]`，但全文未提供多级有损窗口近似与定点截断级联后的漏检率或频偏均方误差曲线 `[pdf:E06]`、`[pdf:E12]`。

## § 10 — 最小复现实验

无需复现完整八智能体框架或购置 USRP X310，可在 **1 周内**利用单台装有 MATLAB/Octave 与免费版 Xilinx Vitis HLS（指定 USRP X310 同系 Kintex-7 器件 `xc7k410tffg900-2`）的工作站及通用 LLM API，完成核心二段式增益与级联精度的最小验证：

1. **输入构造（1 天）**：按 3GPP TS 38.211 编写约 120 行双模块帧级 MATLAB 原型 `ssb_tail_ori.m`，包含动态能量门限计算（对应 `calcThreshold`，输入 `26,105` 点复相关序列）与峰值窗口切片提取（对应 `extractSSBsig`） `[pdf:E07]`、`[pdf:E16]`，在 `-6..+10 dB` 信噪比下导出 `in.txt` 与 `ref.txt`。
2. **最小模块实现（2 天）**：① 用 30 行 Shell/Python 实现 Fig. 3 的 `grep` 扫描与 Fig. 6 环形缓冲/递推累加模板提示词生成流式 `opt.m` `[pdf:E06]`、`[pdf:E10]`；② 对照同一 LLM 从 `ori.m` 直译 C++（`Direct`）与从 `opt.m` 译为 32 位宽 `hls::stream` C++（`Adaptation`） `[pdf:E11]`、`[pdf:E16]`；③ 用 60 行 Python 驱动 Vitis HLS Tcl 扫描 `ap_fixed<W,I>` 总位宽 $W \in \{24,20,16,14,12\}$ 并移除零初始化，跑完 `csim → csynth → export_design -flow impl` 与 `cosim`（`Refinement`） `[pdf:E12]`。
3. **观测指标与判据（2 天）**：统计布局布线后 LUT/FF/DSP/BRAM、最高主频 $F_{\max}$、`cosim` 周期数及各信噪比下检测率损失 $\Delta P_d$。若 `Adaptation` 较 `Direct` 削减 `>90%` LUT/FF 并消除时序违例，且 `Refinement` 在 $\Delta P_d < 0.5\%$ 下再降 `30%–70%` DSP 或延迟，则核心机制获证实 `[pdf:E16]`；反之，若给单步直译提示词补入 `hls::stream` 与环形缓冲要求即可追平 `Adaptation`，则证伪同构 MATLAB 重构层的必要性。

## § 11 — 最强反例设计

1. **可构造病态失效场景：快时变多普勒信道下的二阶数字锁相环与判决反馈均衡联合闭环（Joint Carrier PLL + LMS-DFE）**
   紧接本文 WLAN 精频偏模块之后的基带解调必须执行逐符号闭环跟踪 `[pdf:E14]`、`[pdf:E15]`：设第 $n$ 拍均衡输出旋转去频偏后硬判决误差为 $e[n] = \tilde{s}[n] - \hat{y}[n]e^{-j\hat{\theta}[n]}$，必须在第 $n+1$ 拍前同时更新抽头 $w[n+1] = w[n] + \mu e[n]x^*[n]$ 与相位累加器 $\hat{\theta}[n+1]$。输入 A2H-MAS 将触发三重可预测崩溃：
   - **拆分则延迟失稳**：若 Phase I 拆为滤波、判决、更新三个子模块，Phase VIII 的 AXI-Stream 流水与握手寄存器会在环路内串入 $D \ge 10$ 拍延迟，使环路退化为大延迟 LMS/PLL 并在快衰落下发散；而因 Phase II–VII 均拿无延迟原版录制的静态开环 `in.txt`/`ref.txt` 单独测试，单模块验证将全部假阳性通过，直至顶层联调崩溃 `[pdf:E08]`、`[pdf:E13]`；
   - **不拆且走 `ADAPTIVE_STREAMABLE` 则失锁**：Fig. 3 规则会把自适应参数替换为固定常数 `[pdf:E06]`，在时变频偏下星座图持续旋转误码；
   - **不拆且硬保精确闭环则吞吐违例**：跨迭代复数乘加真依赖阻止 Vitis HLS 达成 `II=1`，启动间隔退化至 `8–16` 拍，跌破 `80 MHz` WLAN 实时采样率约束 `[pdf:E10]`、`[pdf:E14]`。
2. **消融增益的强替代解释**：Table II 中 `Direct` 耗费 `36,500` LUT 且时序失败，主因是裸提示词未声明流接口导致整帧数组被综合成寄存器/多路器网络 `[pdf:E16]`。该落差反映的是“流式硬件模型相对整帧数组模型”的天然优势，而非八智能体编排相对商业 **MATLAB HDL Coder**（自带帧到样本转换）或“带 `hls::stream` 规范的单轮提示词”的净胜出。

## § 12 — Follow-up Research Bet

### 12.1 主研究押注：基于类型化同步数据流图（Typed SDF IR）的字长—折叠率—环路重定时全图联合重写

针对本文暴露的两大未开发自由度——① 单模块孤立优化加顶层流复制导致 WLAN 顶层 BRAM 暴涨 `+68.9%`（`45` 增至 `76` 块） `[pdf:E15]`，② 自适应环路只能退化为固定常数近似 `[pdf:E06]`——提出主研究押注：**构建跨模块类型化同步数据流图中间表示，执行“定点字长—算子折叠率—反馈环路重定时”全图联合重写（Joint Wordlength–Folding–Retiming Graph Rewriting over Typed SDF IR）**。

本押注直接改变三项基本设计变量：
1. **改变状态表示**：将孤立目录与仅记录端口尺寸的 `module_definition.json` `[pdf:E07]` 升级为全系统同步数据流有向图 $\mathcal{G}=(\mathcal{V},\mathcal{E})$，在边上显式编码令牌生产/消费速率比、定点格式 $(W_I, W_F)_e$、量化噪声灵敏度权重及跨阶段旁路数据的共享双口 BRAM 生命周期；
2. **改变可控变量与系统边界**：打破“单模块流式定型 → 单模块位宽 DSE → 顶层被动复制流通道”的局部串行边界 `[pdf:E10]`、`[pdf:E12]`、`[pdf:E13]`，将各算子折叠因子 $\text{II}_v$、多分支共享多读指针环形 BRAM 分配（替代 `top.cpp` 消耗 `31` 块额外 BRAM 的冗余流复制）与全图边级位宽纳入整数规划与大模型图重写联合求解；
3. **改变物理与算法拓扑域**：从纯前馈无环图扩展至含逐拍回流的紧耦合反馈环路，对每个有向环施加闭环相位裕度导出的总流水级数预算约束 $\sum_{v \in C} d_v \le D_{\max}$，引导 Agent 执行前向预计算变换（Look-Ahead Pipelining）与跨模块寄存器重定时（Retiming），在不冻结自适应参数的前提下兼顾 `>300 MHz` 主频与闭环跟踪稳定。

### 12.2 Wild-Card 备选方向

**Wild-card 备选方向**：彻底省去 C++ HLS 语法层与每次数分钟的黑盒综合仿真循环，让大模型直接将展平后的 MATLAB 数据流子图编译为自带精确周期状态机与解析资源代价模型的硬件中间语言（如 Calyx 或 Spatial 原语），在百毫秒级静态调度求解器上完成全局流水对齐与位宽探索并直出可综合 Verilog。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title / Authors / Abstract"
[pdf:E02]: <_evidence/E02-p001-page.png> "PDF 物理页 1，Section I Introduction (MATLAB-to-HLS gap, HDL fine-tuning vs SOTA LLM agents)"
[pdf:E03]: <_evidence/E03-p002-page.png> "PDF 物理页 2，Fig. 1 & Section I Contributions (Single-agent failure modes vs A2H-MAS architecture)"
[pdf:E04]: <_evidence/E04-p002-page.png> "PDF 物理页 2，Section II Related Work (Agentic HDL/HLS frameworks and LLM-MAS)"
[pdf:E05]: <_evidence/E05-p003-page.png> "PDF 物理页 3，Section III-A & Fig. 2 Standardized Input-Output Interfaces"
[pdf:E06]: <_evidence/E06-p003-page.png> "PDF 物理页 3，Section III-B & Fig. 3 Rule-Guided and Tool-Driven Agent Workflow"
[pdf:E07]: <_evidence/E07-p004-page.png> "PDF 物理页 4，Section III-B/C & Fig. 4 Submodule Configuration File (module_packet_detection)"
[pdf:E08]: <_evidence/E08-p004-page.png> "PDF 物理页 4，Section IV-A & IV-B Phase I Modularization and Phase II Test Data Generation"
[pdf:E09]: <_evidence/E09-p005-page.png> "PDF 物理页 5，Fig. 5 Overall Workflow of A2H-MAS & Section IV-C Phase III Function Flattening"
[pdf:E10]: <_evidence/E10-p006-page.png> "PDF 物理页 6，Fig. 6 Knowledge Library (Shift Register / Circular Buffer) & Section IV-D Phase IV Code Optimization"
[pdf:E11]: <_evidence/E11-p006-page.png> "PDF 物理页 6，Section IV-E Phase V Algorithm-Hardware Co-Design & Section IV-F Phase VI Code Translation"
[pdf:E12]: <_evidence/E12-p007-page.png> "PDF 物理页 7，Section IV-F/G Vitis HLS Verification Cycle & Phase VII Refinement (Scripted DSE + RTL Cosim)"
[pdf:E13]: <_evidence/E13-p007-page.png> "PDF 物理页 7，Section IV-H Phase VIII Integration & Implementation (top.cpp & AXI-Stream replication)"
[pdf:E14]: <_evidence/E14-p007-page.png> "PDF 物理页 7，Section V & V-A Experimental Setup (5G NR USRP X310 RFNoC & WLAN Synchronization)"
[pdf:E15]: <_evidence/E15-p008-page.png> "PDF 物理页 8，Table I Implementation Results of All Submodules for 5G NR SSB Detection and WLAN Synchronization"
[pdf:E16]: <_evidence/E16-p008-page.png> "PDF 物理页 8，Table II & Section V-B Ablation Study (Direct vs Adaptation vs Refinement)"
[pdf:E17]: <_evidence/E17-p008-page.png> "PDF 物理页 8，Section VI Conclusion"
[pdf:E18]: <_evidence/E18-p009-page.png> "PDF 物理页 9，Section VI Future Extensions & References [1]-[26]"
