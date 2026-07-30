# Paper Reading Notes

面向 Codex 与 ChatGPT 网页端的论文精读卡仓库。每篇论文对应 `papers/` 下的一份 Markdown；所有卡片属于同一正式语料集合，数量由当前文件自动计算。

## Agent 访问入口

- Codex 本地索引：`D:\proj\mac\paper-reading-notes\README.md`
- Codex 本地卡片目录：`D:\proj\mac\paper-reading-notes\papers`
- ChatGPT 网页端索引：https://github.com/sxw228/paper-reading-notes
- 下表中的相对链接在本地解析为 Codex 可读路径，在 GitHub 上解析为 ChatGPT 可打开的网页链接。
- 文献检索先搜索全部卡片正文和 Zotero；这两者都是本地候选发现源，不只是外部结果的查重工具。
- 命中 Zotero key、DOI 或论文身份后，优先完整读取精读卡；只有卡片缺少所需事实或需要核对原文位置时才回到源 PDF。
- 相关性筛选只排除不相关、重复、非论文和身份不明项；不在制卡前替用户判断学术质量。未指定数量时默认形成最相关的 5 篇入围候选。
- 所有入围且无正式精读卡的论文都生成 ChatGPT 网页端 ZIP 与 prompt；缺 PDF 时先加入或复用 Zotero，并等待用户手动取得和挂载。
- 用户交回 reading-result ZIP 即表示同意保留，技术验收通过后直接归档。用户明确不要的论文以 Zotero `reading-card:rejected` 标签持久排除。

## 检索模式

- **本地优先（默认）**：只检索本索引、精读卡正文和本地 Zotero，不访问全网；本地证据不足时先报告缺口。
- **免费链路**：先走本地链路，再使用 AnySearch 补充候选。
- **付费链路**：先走本地链路，再使用 AnySearch 与 ai4scholar 补充并交叉核对候选。
- Asta 当前不可用，不属于以上任一模式。
- AnySearch 与 ai4scholar 只负责外部候选发现；外部结果仍需逐篇经过本地精读卡与 Zotero 身份门。

## 全部精读卡（316）

| 年份 | Zotero key | 论文 | DOI |
|---:|---|---|---|
| 2026 | `4JETCWNK` | [A Digital Twin Framework With Deep Feature Extraction and Gaussian Process for Multi-Objective Optimization in Semiconductor Manufacturing](papers/4JETCWNK-lin-2026-digital-twin-semiconductor.md) | — |
| 2026 | `WGUS4P5R` | [A General FPGA-Based Accelerated Solver for Electromagnetic Transient Simulations](papers/WGUS4P5R-liang-2026-general-fpga-solver.md) | 10.3390/electronics15030606 |
| 2026 | `6EN6SEVB` | [A Generalized Fixed-Admittance ADC Model for Two-Level Converters in EMT Simulation](papers/6EN6SEVB-cao-2026-generalized-fixed-admittance-adc.md) | — |
| 2026 | `BDZJXT4T` | [Deep Learning-Based Modeling for Power Converters via Physics-Enhanced Hierarchical Neural Network](papers/BDZJXT4T-shang-2026-physics-enhanced-hierarchical-nn.md) | 10.1109/TPEL.2025.3629881 |
| 2026 | `SQXA23AX` | [Dissipation-Based Dynamics-Aware Learning Scheme for Transient Stability Analysis of Networked Black-Box Grid-Forming Inverters](papers/SQXA23AX-liu-2026-dissipation-dynamics-aware-learning.md) | — |
| 2026 | `AUH78FB2` | [Harmonic-Preserved Average-Value Model for Converters in Electromagnetic Transient Simulation](papers/AUH78FB2-cao-2026-harmonic-preserved-avm.md) | — |
| 2026 | `XBMXWRW2` | [High-Fidelity Real-Time Simulation of Power Electronics Converters via FPGA-Accelerated Dynamic Connectionist Neural Network](papers/XBMXWRW2-weng-2026-fpga-dynamic-connectivity.md) | — |
| 2026 | `4XBSVW9U` | [Hybrid Data-Physics-Driven Modeling Method for Real-Time Simulation of Cascaded Power Electronics Systems](papers/4XBSVW9U-gao-2026-hybrid-data-physics-driven-modeling-method.md) | — |
| 2026 | `6U2FKKJD` | [Hybrid Modeling Approach Combining Analytical and Neural Ordinary Differential Equations for Accelerated Simulation of Grid-Tied Inverter｜论文精读证据卡](papers/6U2FKKJD-liang-2026-hybrid-modeling.md) | — |
| 2026 | `EY822HYI` | [Matrix Low-dimensional Qubit Casting Based Quantum Electromagnetic Transient Network Simulation Program](papers/EY822HYI-lou-2026-matrix-low-dimensional-qubit-casting-quantum.md) | — |
| 2026 | `GTP6BF5S` | [Multilayer Device-Level Electro-Thermal Real-Time Simulation and Multipurpose HIL Testing of Power Electronics Converters](papers/GTP6BF5S-bai-2026-electro-thermal-rts-hil.md) | — |
| 2026 | `PXQN7NA7` | [Neural Controlled Differential Equations for EMT-Level Surrogate Modeling of Grid-Forming Inverters](papers/PXQN7NA7-qu-2026-neural-cde-emt-gfm-inverters.md) | 10.48550/arXiv.2607.16258 |
| 2026 | `WDR7TD5U` | [Neural Surrogate Solver for Efficient Edge Inference of Power Electronic Hybrid Dynamics](papers/WDR7TD5U-zheng-2026-neural-surrogate-solver-efficient-edge-inference.md) | — |
| 2026 | `NVRUXU44` | [Physics-Embedded Neural ODEs for Sim-to-Real Edge Digital Twins of Hybrid Power Electronics Systems](papers/NVRUXU44-zheng-2026-physics-embedded-neural-odes-sim-real.md) | — |
| 2026 | `IZFCMVP8` | [Real-Time Surrogate Modeling for Fast Transient Prediction in Inverter-Based Microgrids Using CNN and LightGBM](papers/IZFCMVP8-ogiesoba-eguakun-2026-cnn-lightgbm-microgrid-surrogate.md) | — |
| 2025 | `YV7C8DG7` | [A Bridge-Arm-Module-Based Fixed-Admittance ADC Model for Converters in EMT Simulation — 中文深度精读](papers/YV7C8DG7-cao-bridge-arm-module-based-fixed-admittance-adc2025.md) | — |
| 2025 | `9Y7KA9KJ` | [A General Interface-Free Delayed Real-Time Simulation Method with A-Stability for Power Electronic Converters](papers/9Y7KA9KJ-xu-2025-interface-free-delayed-rt-sim.md) | — |
| 2025 | `RI6H4AE3` | [A Generic Modeling Approach for Dual-Active-Bridge Converter Family via Topology Transferrable Networks](papers/RI6H4AE3-li-2025-generic-modeling-dab-family.md) | 10.1109/TIE.2024.3406858 |
| 2025 | `6AXZCAXB` | [A Hierarchical Multiarea Hybrid Equivalent for Efficient Simulation of Scalable Power Electronics Systems](papers/6AXZCAXB-jin-2025-hierarchical-multiarea-hybrid-equivalent-efficient-simulation.md) | — |
| 2025 | `X98GS3IY` | [A State Variables Elimination-Based EMTP-Type Constant Admittance Equivalent Modeling Method for Power Electronic Converters](papers/X98GS3IY-xu-state-variables-elimination-based2025.md) | — |
| 2025 | `69CY3T2T` | [An Equivalent Switching Model for FPGA-Based Real-Time Simulation of SiC MOSFET Transient Behaviors in Power Electronic Converters](papers/69CY3T2T-wang-2025-equivalent-switching-model-fpga-real-time.md) | — |
| 2025 | `HGT3A92C` | [An Extendable High-Voltage Gain Soft-Switching Bidirectional DC–DC Converter With Coupled Inductor](papers/HGT3A92C-yuan-2025-extendable-high-voltage-gain-soft-switching.md) | — |
| 2025 | `GYR82VTM` | [An Overview of Digital Twin Technology for Power Electronics: State-of-the-Art and Future Trends](papers/GYR82VTM-wu-2025-overview-digital-twin-technology-power-electronics.md) | — |
| 2025 | `CEGDREBJ` | [Applications of Data-Driven Dynamic Modeling of Power Converters in Power Systems: An Overview](papers/CEGDREBJ-subedi-2025-applications-data-driven-dynamic-modeling-power.md) | — |
| 2025 | `3PR5MK85` | [Artificial Intelligence Aided Black-Box Modeling of Three-Phase Single-Stage Photovoltaic Inverter Systems](papers/3PR5MK85-men-2025-artificial-intelligence-aided-black-box-modeling.md) | — |
| 2025 | `WIC6Y9WI` | [Data-driven dynamic modeling for inverter-based resources using neural networks](papers/WIC6Y9WI-yang-data-driven-dynamic-modeling2025.md) | 10.1038/s41467-025-66604-z |
| 2025 | `23XSBNW6` | [Data-Driven Modeling of Modular Multilevel Converters Based on HHT and CNN-LSTM-AM Neural Network](papers/23XSBNW6-data-driven-mmc-hht-cnn-lstm-am.md) | 10.1109/TIE.2024.3433509 |
| 2025 | `39XCSPF6` | [Data-Enabled Finite State Predictive Control for Power Converters via Adaline Neural Network](papers/39XCSPF6-wu-2025-data-enabled-finite-state-predictive-control.md) | — |
| 2025 | `B9CEUDKD` | [Electromagnetic Oscillation Stabilizer for Large-Scale Power Electronics-Dominated Power Systems in LTP Framework - Part I: Functional Derivative-Based Measures of Modal Controllability and Observability](papers/B9CEUDKD-du-2025-electromagnetic-oscillation-stabilizer-large-scale-power.md) | — |
| 2025 | `472N844P` | [Electromagnetic Oscillation Stabilizer for Large-Scale Power Electronics-Dominated Power Systems in LTP Framework–Part II: Generalized Periodic Stabilization Control and Design](papers/472N844P-du-2025-electromagnetic-oscillation-stabilizer-large-scale-power.md) | 10.1109/TPEL.2025.3588607 |
| 2025 | `DB48HZNK` | [Electromagnetic Transient Equivalent Modeling and Real-Time Simulation Method for Bidirectional DC/DC Converters](papers/DB48HZNK-xu-2025-bdc-constant-admittance.md) | 10.1109/TIA.2025.3574123 |
| 2025 | `FRBTTI37` | [Evaluation of Pulsed Charging Procedures and Their Impact on Lithium-Ion Battery Lifetime for Electric Vehicle Fast Charging Applications](papers/FRBTTI37-althurthi-2025-pulsed-charging.md) | 10.1109/TTE.2025.3606784 |
| 2025 | `9MWPSD9R` | [Extended Physics-Informed Neural Networks for Parameter Identification of Switched Mode Power Converters With Undetermined Topological Durations](papers/9MWPSD9R-xiang-2025-extended-pinn.md) | — |
| 2025 | `2QU5U53K` | [Fast Transient Simulation of System-Level Power Delivery Networks via Parallel Waveform Relaxation](papers/2QU5U53K-moglia-2025-fast-transient-simulation-system-level-power.md) | 10.1109/TCPMT.2024.3410146 |
| 2025 | `RN4D47F6` | [Few-Shot Data-Driven Modeling of Unified Grid Tied VSCs for Multioperation Impedance Identification Based on PINN](papers/RN4D47F6-few-shot-unified-vsc-impedance-pinn.md) | 10.1109/TIE.2024.3508059 |
| 2025 | `UXCRX7BC` | [FPGA Accelerated Large-Scale State-Space Equations for Multi-Converter Systems](papers/UXCRX7BC-fpga-accelerated-large-scale-state-space-equations.md) | 10.3390/electronics14193966 |
| 2025 | `VU6WQA4S` | [FPGA-Based Real-Time X-in-the-Loop Simulation Testbench for Dynamic Wireless Power Transfer System With Stochastic and Nonlinear Inductance](papers/VU6WQA4S-zheng-2025-fpga-real-time-x-loop-simulation.md) | 10.1109/TTE.2024.3410683 |
| 2025 | `WKJURDUK` | [Hardware-in-the-Loop Real-Time Transient Emulation of Large-Scale Renewable Energy Installations Based on Hybrid Machine Learning Modeling](papers/WKJURDUK-chen-2025-hil-hybrid-ml-large-scale-renewables.md) | 10.1109/JESTIE.2024.3434364 |
| 2025 | `S6VU8IS7` | [Hardware-in-the-Loop Simulation of ANPC Based on Modified Predictor–Corrector Method](papers/S6VU8IS7-hardware-in-the-loop-simulation-of-anpc.md) | 10.3390/sym17122121 |
| 2025 | `BF67SD5X` | [Hierarchical Control of DC Coupled Fast EV Charging Station](papers/BF67SD5X-sharida-2025-hierarchical-control-dc-coupled-fast-ev.md) | — |
| 2025 | `QK8IUSV2` | [High-Order Generalized Averaging Method for Power Electronics Modeling From DC to Above Half the Switching Frequency](papers/QK8IUSV2-li-2024-high-order-generalized-averaging-method-power-electronics-modeling.md) | 10.1109/TPEL.2024.3450712 |
| 2025 | `ERGUNQ4T` | [Improving Accuracy of Interpolation Algorithm in EMT Simulation: A Padé Approximation and Switching Theorem Based Approach](papers/ERGUNQ4T-cao-improving-accuracy-interpolation2025.md) | — |
| 2025 | `92D8V2EG` | [Integration of EV Fast Charging Station into a DC-Based Microgrid](papers/92D8V2EG-dicorato-2025-ev-fast-charging.md) | — |
| 2025 | `B2VFUNGH` | [Isolated Three-Phase Soft-Switching DC-DC Converter With Reduced Voltage Stress on Rectifier Diodes for Off-Board Chargers](papers/B2VFUNGH-oliveira-2025-isolated-three-phase-soft-switching-dc.md) | 10.1109/TPEL.2025.3544514 |
| 2025 | `VSGHRUZC` | [Latent-Feature-Informed Neural ODE Modeling for Lightweight Stability Evaluation of Black-Box Grid-Tied Inverters](papers/VSGHRUZC-zheng-2025-latent-feature-informed-neural-ode-modeling.md) | — |
| 2025 | `G7H6ERBD` | [Long-Horizon FCS-MPC Trained 1-D Convolution Neural Networks for FPGA-Based Power-Electronic Converter Control With a Si/SiC Hybrid Converter Case Study](papers/G7H6ERBD-li-2025-long-horizon-fcs-mpc.md) | — |
| 2025 | `WCL8I4BR` | [Low-Dimensional Equivalent Models and Multithreading-Based Parallel EMT Simulation Method for Multi-Converter Systems](papers/WCL8I4BR-xu-2025-low-dimensional-parallel-emt.md) | — |
| 2025 | `2FFQMMBK` | [Machine-Learning-Reinforced Massively Parallel Transient Simulation for Large-Scale Renewable-Energy-Integrated Power Systems](papers/2FFQMMBK-cheng-2025-ml-reinforced-massively-parallel-transient.md) | 10.1109/TPWRS.2024.3409729 |
| 2025 | `WK32GRFH` | [MTOF: A Novel FPGA-Based EMT Toolbox in MATLAB](papers/WK32GRFH-ma-2025-mtof-fpga-emt-toolbox.md) | 10.1109/TPWRS.2025.3535841 |
| 2025 | `UFC7VDPM` | [Mutual Information-Enhanced NARX-NN Digital Twins for Power Electronics in Smart Grid Applications — 中文精读证据卡](papers/UFC7VDPM-nalepa-2025-mutual-information-narx-nn.md) | — |
| 2025 | `AF87BKAC` | [Physics Informed Neural Network—Estimated Circuit Parameter Adaptive Modulation of DAB](papers/AF87BKAC-dey-2025-physics-informed-neural-network-estimated-circuit.md) | — |
| 2025 | `I46Z825J` | [Progress and Application of Equivalent Models for Power System Simulation With Renewable Penetration: A Review](papers/I46Z825J-progress-application-equivalent2025.md) | — |
| 2025 | `3Z3KVXUH` | [Real-Time Multi-Stability Risk Assessment and Visualization of Power Systems: A Graph Neural Network-Based Method](papers/3Z3KVXUH-chen-2025-real-time-multi-stability-risk-assessment.md) | — |
| 2025 | `QLM3QRG5` | [Real-Time Simulation Method Based on Voltage Controlled Current Source for Power Electronic Converters With Low Resource Consumption](papers/QLM3QRG5-sun-2025-real-time-simulation-method-voltage-controlled.md) | — |
| 2025 | `8TC6G8FU` | [Real-Time Simulation Method for High-Frequency Power Electronic Converters With Blocking Mode](papers/8TC6G8FU-sun-2025-blocking-mode.md) | 10.1109/TIE.2025.3589443 |
| 2025 | `HYAUIIK9` | [Real-Time Simulation Method for Power Electronic Converters With Low Resource Consumption](papers/HYAUIIK9-sun-2025-real-time-simulation-method-power-electronic.md) | — |
| 2025 | `DQQ2BHC4` | [Reconfigurable LLC Resonant Converter for Wide Voltage Range and Reduced Voltage Stress in DC-Connected EV Charging Stations](papers/DQQ2BHC4-zuo-2025-reconfigurable-llc.md) | — |
| 2025 | `S3ZJ4442` | [Resilient Control of Networked Microgrids Using Vertical Federated Reinforcement Learning: Designs and Real-Time Test-Bed Validations](papers/S3ZJ4442-mukherjee-2025-resilient-control-networked-microgrids-vertical-federated.md) | — |
| 2025 | `AD4UYL5V` | [Scalable and Real-Time Power System Simulation Based on Heterogeneous CPU-FPGA Co-operation](papers/AD4UYL5V-yang-scalable-real-time-power2025.md) | — |
| 2025 | `P93T3JQ8` | [Splitting State-Space Method for Converter-Integrated Power Systems EMT Simulations](papers/P93T3JQ8-fu-2025-splitting-state-space-method-converter-integrated.md) | — |
| 2025 | `B4XIDARI` | [State-Space Driven Digital Twin for Condition Monitoring and Predictive Health Assessment in Grid-Integrated Power Converter System](papers/B4XIDARI-kumar-2025-state-space-driven-digital-twin-condition.md) | 10.1109/TICPS.2025.3586823 |
| 2025 | `XRMS6SCG` | [Switching-Period-Synchronization-Based Real-Time Simulation Method Suitable for Power Converters With High Switching Frequency](papers/XRMS6SCG-xu-2025-switching-period-synchronization.md) | 10.1109/TIE.2025.3553165 |
| 2025 | `MTD6NVL4` | [Transfer Learnable Physics-Informed Neural Network Surrogating Grid-Tied Inverters for Renewable Power System Simulation](papers/MTD6NVL4-yuan-2025-transfer-learnable-pinn.md) | 10.1109/TIE.2025.3613652 |
| 2025 | `5CT7KTF3` | [万兆以太网高带宽低延迟接口的 FPGA 轻量化设计：论文精读](papers/5CT7KTF3-song-2025-10gbe-fpga-interface.md) | — |
| 2024 | `BN4C9XBE` | [A Controller HIL Testing Approach of High Switching Frequency Power Converter via Slower-Than-Real-Time Simulation](papers/BN4C9XBE-bai-2024-controller-hil-testing-approach-high-switching-frequency-power.md) | 10.1109/TIE.2023.3321992 |
| 2024 | `QBIDR8AW` | [A Data-Driven Modeling Method of Virtual Synchronous Generator Based on LSTM Neural Network](papers/QBIDR8AW-tian-2023-data-driven-modeling-method-virtual-synchronous-generator-lstm.md) | 10.1109/TII.2023.3333673 |
| 2024 | `XPWVTPC2` | [A Model Review for Controller-Hardware-in-the-Loop Simulation in EV Powertrain Application](papers/XPWVTPC2-gong-2024-model-review-controller-hardware-loop-simulation-ev-powertrain.md) | 10.1109/TTE.2023.3290999 |
| 2024 | `85WBSMAJ` | [A Modified Algorithm for the L/C-based Switch Model of Power Converters in Real-Time Simulation Based on FPGA](papers/85WBSMAJ-wang-2024-modified-algorithm-l-c-switch-model-power-converters.md) | — |
| 2024 | `QE8CSJG9` | [A Multiport Power Electronic Transformer With MVDC Integration Interface for Multiple DC Units](papers/QE8CSJG9-zhu-2023-multiport-power-electronic-transformer-mvdc-integration-interface-multiple.md) | 10.1109/TIE.2023.3331147 |
| 2024 | `9ELPM74G` | [A Semi-Implicit Parallel Leapfrog Solver With Half-Step Sampling Technique for FPGA-Based Real-Time HIL Simulation of Power Converters](papers/9ELPM74G-zheng-2024-semi-implicit-parallel-leapfrog-solver-half-step-sampling.md) | — |
| 2024 | `2HRFCGK4` | [Admittance-Based Modeling for Electromagnetic Transient and Stability Analysis of Power-Electronic-Based Energy Conversion Systems](papers/2HRFCGK4-vahabzadeh-2024-admittance-modeling-electromagnetic-transient-stability-analysis-power.md) | 10.1109/TEC.2024.3373794 |
| 2024 | `4HPA7DVH` | [An Admittance-Reshaping Control Method for Improving the Stability of Multi-Parallel Grid-Connected Converters](papers/4HPA7DVH-li-2025-admittance-reshaping.md) | 10.1109/TPEL.2024.3519167 |
| 2024 | `KSDKQ9U8` | [An Efficient Electromagnetic Transient Modeling Method Based on Unit Division and Parallel Simulation Framework for Large-scale Photovoltaic Power Stations](papers/KSDKQ9U8-xu-efficient-electromagnetic-transient2024.md) | — |
| 2024 | `64FITWZB` | [Circuit Dynamics Prediction via Graph Neural Network & Graph Framework Integration: Three Phase Inverter Case Study](papers/64FITWZB-khamis-agamy-2024-gnn-three-phase-inverter.md) | — |
| 2024 | `K7VW84V3` | [Circuit Topology Aware GNN-Based Multi-Variable Model for DC-DC Converters Dynamics Prediction in CCM and DCM](papers/K7VW84V3-khamis-agamy-2024-topology-aware-gnn-converter-dynamics.md) | 10.1007/s00521-024-10293-0 |
| 2024 | `E2XUA9FR` | [Convergence Enhancement for Neural Network Integrated Power System Time Domain Simulation](papers/E2XUA9FR-wang-2024-convergence-enhancement-neural-network-integrated-power-system-time.md) | 10.1109/TPWRS.2024.3421902 |
| 2024 | `CS6KJKT3` | [Data-Light Physics-Informed Modeling for the Modulation Optimization of a Dual-Active-Bridge Converter](papers/CS6KJKT3-li-2024-data-light-physics-informed-modeling-modulation-optimization-dual.md) | — |
| 2024 | `T6QUXW9V` | [Deep Learning-Based Equivalent Modelling of Hybrid RES Plant for Efficient, Repetitive Power System Transient Stability Studies](papers/T6QUXW9V-radovanovic-2023-deep-learning-equivalent-modelling-hybrid-res-plant-efficient.md) | 10.1109/TPWRS.2023.3281498 |
| 2024 | `TU5BENUB` | [Detailed Multi-Domain Modeling and Faster-Than-Real-Time Hardware Emulation of Small Modular Reactor for EMT Studies](papers/TU5BENUB-chen-2024-detailed-multi-domain-modeling-faster-than-real-time.md) | 10.1109/TEC.2024.3375256 |
| 2024 | `9E2J63DH` | [FireAxe：面向大规模 RTL 设计的分区式 FPGA 加速仿真](papers/9E2J63DH-whangbo-2024-fireaxe-partitioned-fpga.md) | 10.1109/ISCA59077.2024.00044 |
| 2024 | `7BZSU9CP` | [FPGA-Based Implicit–Explicit Real-Time Simulation Solver for Railway Wireless Power Transfer With Nonlinear Magnetic Coupling Components](papers/7BZSU9CP-xu-2024-fpga-implicit-explicit-real-time-simulation-solver-railway.md) | 10.1109/TTE.2023.3332583 |
| 2024 | `NGZA9TJT` | [FPGA-Based Real-Time Simulation of Five-Phase PMSM System for Fault Tolerant Controller-HIL Applications](papers/NGZA9TJT-bai-2024-fpga-real-time-simulation-five-phase-pmsm-system.md) | 10.1109/TIA.2024.3439490 |
| 2024 | `SEBQTF7G` | [General Linearized Model of Voltage Source Converter With Fixed Nodal Admittance Matrix](papers/SEBQTF7G-zhang-2024-fixed-nodal-admittance.md) | 10.1109/TPEL.2024.3409537 |
| 2024 | `TWHDM94J` | [Generalized Envelope-Based Modeling of Single-Phase Grid-Connected Power Converters](papers/TWHDM94J-azcondo-2024-generalized-envelope-modeling-single-phase-grid-connected-power.md) | 10.1109/TIE.2024.3379631 |
| 2024 | `8SJQSIC8` | [Low Cost and Optimized FPGA-HIL Real Time Simulation of a Boost Converter Powered by a Photovoltaic Panel](papers/8SJQSIC8-low-cost-optimized-fpga-hil-pv-boost.md) | 10.1109/TLA.2024.10738270 |
| 2024 | `7G3RKDGD` | [Modeling Method for the Real-Time Simulation of Bridge-Based High-Switching-Frequency Power Electronic Converters](papers/7G3RKDGD-sun-2024-modeling-method-real-time-simulation-bridge-high-switching.md) | 10.1109/TPEL.2024.3402428 |
| 2024 | `2RVAK9MA` | [Modeling of Inverter-Based Resources for Power System Harmonics Studies](papers/2RVAK9MA-xu-2024-modeling-inverter-resources-power-system-harmonics-studies.md) | 10.1109/TPWRD.2024.3486566 |
| 2024 | `RTSQC3D8` | [MPSoC-Based Dynamic Adjustable Time-Stepping Scheme With Switch Event Oversampling Technique for Real-Time HIL Simulation of Power Converters](papers/RTSQC3D8-zheng-2024-mpsoc-dynamic-adjustable-time-stepping-scheme-switch-event.md) | 10.1109/TTE.2023.3310509 |
| 2024 | `SDDPKDTK` | [Neural ODE Model of Power Electronic Converters With Accelerated Computation and High Fidelity](papers/SDDPKDTK-ge-2024-neural-ode-model-power-electronic-converters-accelerated-computation.md) | 10.1109/TCSI.2024.3460803 |
| 2024 | `MXWJUTSZ` | [ParaEMT: An Open Source, Parallelizable, and HPC-Compatible EMT Simulator for Large-Scale IBR-Rich Power Grids](papers/MXWJUTSZ-xiong-2024-paraemt-open-source-parallelizable-hpc-compatible-emt-simulator.md) | 10.1109/TPWRD.2023.3342715 |
| 2024 | `MRR5H86Z` | [PI-Controlled Variable Time-Step Power System Simulation Using an Adaptive Order Differential Transformation Method](papers/MRR5H86Z-huang-2024-pi-controlled-variable-time-step-power-system-simulation.md) | 10.1109/TPWRS.2024.3361442 |
| 2024 | `43HISH3I` | [Temporal Modeling for Power Converters With Physics-in-Architecture Recurrent Neural Network](papers/43HISH3I-li-2024-temporal-modeling-power-converters-physics-architecture-recurrent-neural.md) | 10.1109/TIE.2024.3352119 |
| 2024 | `AS5V4T4Z` | [Topology-Aware Matrix Partitioning Method for FPGA Real-Time Simulation of Power Electronics Systems](papers/AS5V4T4Z-xu-2024-topology-aware-matrix-partitioning-method-fpga-real-time.md) | 10.1109/TIE.2023.3308137 |
| 2024 | `2QGPH7ZW` | [Transient Stability Analysis of Renewable Power Generations via VSC-HVDC](papers/2QGPH7ZW-zhou-2024-transient-stability-analysis-renewable-power-generations-via-vsc.md) | 10.1109/TIE.2024.3476958 |
| 2024 | `VNMA2TC9` | [电力电子换流器无延时解耦并行仿真模型](papers/VNMA2TC9-xu-ming-wang-dian-li-dian-zi-huan-liu-qi-wu-yan-shi-jie-ou-bing-xing-fang-zhen-mo-xing2024.md) | — |
| 2023 | `B5UM632K` | [A Dual-Active Bridge Converter With a Wide Output Voltage Range (200–1000 V) for Ultrafast DC-Connected EV Charging Stations](papers/B5UM632K-zayed-2023-dual-active-bridge-converter-wide-output-voltage-range.md) | — |
| 2023 | `RJNWWZWE` | [A Novel Decoupled EMT Approach and Parallel Simulation Framework for Modularized Solid-State Transformers](papers/RJNWWZWE-feng-novel-decoupled-emt2023.md) | — |
| 2023 | `44RJP3FJ` | [A Survey of Power System State Estimation Using Multiple Data Sources: PMUs, SCADA, AMI, and Beyond](papers/44RJP3FJ-cheng-2023-survey-power-system-state-estimation-multiple-data-sources.md) | 10.1109/TSG.2023.3286401 |
| 2023 | `ENTJJJZG` | [A Widely Applicable Modeling and Efficient Simulation Method for Power Electronics Grids Based on Unit Switching Circuits](papers/ENTJJJZG-wang-2023-widely-applicable-modeling-efficient-simulation-method-power-electronics.md) | 10.1109/TSG.2023.3261440 |
| 2023 | `6I9KI3B7` | [An Efficient Half-Bridge MMC Model for EMTP-Type Simulation Based on Hybrid Numerical Integration](papers/6I9KI3B7-gao-efficient-half-bridge-mmc2023.md) | — |
| 2023 | `NE5PGQA4` | [An FPGA-Based Hierarchical Parallel Real-Time Simulation Method for Cascaded Solid-State Transformer](papers/NE5PGQA4-li-fpgabased-hierarchical-parallel2023a.md) | — |
| 2023 | `IIP2G4XE` | [Basics of Electromagnetic Transients: Underlying mathematics](papers/IIP2G4XE-ma-basics-electromagnetic-transients2023.md) | — |
| 2023 | `A94XDBDV` | [Capacitance Minimization and Constraint of CHB Power Electronic Transformer Based on Switching Synchronization Hybrid Phase-Shift Modulation Method of High Frequency Link](papers/A94XDBDV-pan-2023-capacitance-minimization-constraint-chb-power-electronic-transformer-switching.md) | 10.1109/TPEL.2023.3239164 |
| 2023 | `UXWRM3U7` | [Comparative Modeling and Analysis of EMT and Phasor RMS Grid-Forming Converters Under Different Power System Dynamics](papers/UXWRM3U7-favuzza-comparative-modeling-analysis2023.md) | — |
| 2023 | `I7PMA3DJ` | [Compensation Method for Parallel and Iterative Real-Time Simulation of Electromagnetic Transients](papers/I7PMA3DJ-bruned-2023-compensation-method-parallel-iterative-real-time-simulation-electromagnetic.md) | — |
| 2023 | `SWBQS25Q` | [Comprehensive Mapping of Continuous/Switching Circuits in CCM and DCM to Machine Learning Domain Using Homogeneous Graph Neural Networks](papers/SWBQS25Q-khamis-agamy-2023-homogeneous-gnn-circuits.md) | — |
| 2023 | `CUCXEQHE` | [Detailed Parametric Modeling of AC-DC Converters for EMT Simulators](papers/CUCXEQHE-hosseinian-detailed-parametric-modeling2023a.md) | — |
| 2023 | `AFZ7V45M` | [Effinformer: A Deep-Learning-Based Data-Driven Modeling of DC-DC Bidirectional Converters](papers/AFZ7V45M-shang-2023-effinformer-deep-learning-data-driven-modeling-dc-dc.md) | 10.1109/TIM.2023.3318701 |
| 2023 | `KDH2T488` | [Extended Discrete-State Event-Driven Hardware-in-the-Loop Simulation for Power Electronic Systems Based on Virtual-Time-Ratio Regulation](papers/KDH2T488-zeng-extended-discrete-state-event-driven2023.md) | 10.1109/JESTPE.2023.3266348 |
| 2023 | `F5D8K2X9` | [Fast DC Charging Infrastructures for Electric Vehicles: Overview of Technologies, Standards, and Challenges](papers/F5D8K2X9-franzese-2023-fast-dc-charging-infrastructures-electric-vehicles-overview-technologies.md) | 10.1109/TTE.2023.3239224 |
| 2023 | `IH3ZEJ96` | [Harmonic State-Space Modeling and Closed-Loop Control of Single-Stage High-Frequency Isolated DC–AC Converter](papers/IH3ZEJ96-wang-2023-harmonic-state-space-modeling-closed-loop-control-single.md) | 10.1109/TIE.2023.3281682 |
| 2023 | `KMA5XUKW` | [Impedance Reshaping Method of DFIG System Based on Compensating Rotor Current Dynamic to Eliminate PLL Influence](papers/KMA5XUKW-xiong-2023-impedance-reshaping-method-dfig-system-compensating-rotor-current.md) | 10.1109/TPEL.2023.3346042 |
| 2023 | `Q5W4UKM2` | [Improved Interpolation Algorithm Accounting for Multiple Switching Actions and Reinitialization](papers/Q5W4UKM2-cao-improved-interpolation-algorithm2023.md) | — |
| 2023 | `ZFMDNBXF` | [Manticore：用 Static Bulk-Synchronous Parallelism 加速 RTL 仿真](papers/ZFMDNBXF-emami-2023-manticore-static-bsp.md) | — |
| 2023 | `TSXICTYN` | [MSDF-SGD：面向任意精度训练的最高有效位优先随机梯度下降](papers/TSXICTYN-song-msdfsgdmost-significant-digit-first2023.md) | — |
| 2023 | `IIZI5QDP` | [On Model Order Reduction and Exponential Integrator for Transient Circuit Simulation](papers/IIZI5QDP-wang-2023-model-order-reduction-exponential-integrator-transient-circuit-simulation.md) | — |
| 2023 | `3T22B4ZQ` | [Oversampling Techniques to Improve the Accuracy of Hardware-in-the-Loop Switching Models](papers/3T22B4ZQ-yushkova-oversampling-techniques-improve2023.md) | 10.1109/TPEL.2023.3243702 |
| 2023 | `V3X4JZ7M` | [Overview of Interface Algorithms, Interface Signals, Communication and Delay in Real-Time Co-Simulation of Distributed Power Systems](papers/V3X4JZ7M-buraimoh-2023-rt-cosimulation-interface-survey.md) | — |
| 2023 | `S3UTQMTH` | [Physics-Aware Neural Dynamic Equivalence of Power Systems](papers/S3UTQMTH-shen-2023-physics-aware-neural-dynamic-equivalence-power-systems.md) | 10.1109/TPWRS.2023.3328162 |
| 2023 | `PIZZEKQZ` | [Physics-Informed Neural Network Based Online Impedance Identification of Voltage Source Converters](papers/PIZZEKQZ-zhang-2023-physics-informed-neural-network-online-impedance-identification-voltage.md) | 10.1109/TIE.2022.3177791 |
| 2023 | `SKEEWQ9V` | [Portal Analysis Approach Used for the Efficient Electromagnetic Transient (EMT) Simulation of Power Electronic Systems](papers/SKEEWQ9V-gao-portal-analysis-approach2023.md) | — |
| 2023 | `WZD5RAVE` | [Power System Recovery from Momentary Cessation with Transient Stability Improvement](papers/WZD5RAVE-savastianov-2023-power-system-recovery-from-momentary-cessation-transient-stability.md) | — |
| 2023 | `CKMGIXXY` | [Real-Time HIL Emulation of DRM With Machine Learning Accelerated WBG Device Models](papers/CKMGIXXY-zhang-real-time-hilemulation2023.md) | — |
| 2023 | `V6Z6HNCB` | [Recursive Multi-Channel Prony for PMU](papers/V6Z6HNCB-khodaparast-2023-recursive-multi-channel-prony-pmu.md) | 10.1109/TPWRD.2023.3335999 |
| 2023 | `6GGQ3HNF` | [Revisiting Power Systems Time-Domain Simulation Methods and Models](papers/6GGQ3HNF-lara-2023-revisiting-power-systems-time-domain-simulation-methods-and-models.md) | 10.1109/TPWRS.2023.3303291 |
| 2023 | `8RWZG7SG` | [Sinusoidal Phase Shift Modulation for V2H Operational Mode in Current-Fed Bidirectional Onboard Charger](papers/8RWZG7SG-kumar-2023-sinusoidal-phase-shift-modulation-for-v2h-operational-mode-in-current-fed.md) | 10.1109/TTE.2023.3298819 |
| 2023 | `ZF6SEKTE` | [Supervisory Control System for a Grid-Connected MVDC Microgrid Based on Z-Source Converters With PV, Battery Storage, Green Hydrogen System and Charging Station of Electric Vehicles](papers/ZF6SEKTE-garcia-trivino-2023-supervisory-control-system-for-a-grid-connected-mvdc-microgrid.md) | — |
| 2023 | `PZAPQ5B3` | [Unified Real-Time Simulation Method for DC/DC Conversion Systems Consisting of Cascaded Dual-Port Submodules](papers/PZAPQ5B3-li-unified-real-time-simulation2023a.md) | — |
| 2023 | `5EF8STIQ` | [Universal Equivalent Model for Real-Time CPU/FPGA Co-Simulation of Hybrid Cascaded Multilevel Converters](papers/5EF8STIQ-bieber-2023.md) | — |
| 2023 | `3E2NUM8I` | [Using Dynamic Phasors To Model and Analyze Selective Harmonic Compensated Single-Phase Grid-Forming Inverter Connected to Nonlinear and Resistive Loads](papers/3E2NUM8I-nwaneto-2023-using-dynamic-phasors-to-model-and-analyze-selective-harmonic-compensated.md) | 10.1109/TIA.2023.3282925 |
| 2023 | `F2HU8FFA` | [从图论到图神经网络：GNN 在电力电子中的机会](papers/F2HU8FFA-li-2023-gnn-opportunities-power-electronics.md) | 10.1109/ACCESS.2023.3345795 |
| 2023 | `3PWIK7BV` | [基于 FPGA 的电力电子系统电磁暂态实时仿真通用解算器](papers/3PWIK7BV-zhou-bin-ji-yu-fpgade-dian-li-dian-zi-xi-tong-dian-ci-zan-tai-shi-shi-fang-zhen-tong-yong-jie-suan-qi2023.md) | — |
| 2022 | `CTE2V4RE` | [A Deep Learning-Based Modeling of a 270 V-to-28 V DC-DC Converter Used in More Electric Aircrafts](papers/CTE2V4RE-duenas-2022-a-deep-learning-based-modeling-of-a-270-v-to-28-v-dc-dc-converter-used-in.md) | 10.1109/TPEL.2021.3098468 |
| 2022 | `G8FRSHQ9` | [A Discrete Small-Step Synthesis Real-Time Simulation Method for Power Converters](papers/G8FRSHQ9-li-discrete-small-step-synthesis2022a.md) | — |
| 2022 | `FMFFDIHC` | [A Full-Feedforward Technique to Mitigate the Grid Distortion Effect on Parallel Grid-Tied Inverters](papers/FMFFDIHC-khajeh-2022-a-full-feedforward-technique-to-mitigate-the-grid-distortion-effect-on.md) | 10.1109/TPEL.2022.3146235 |
| 2022 | `QQTERPD8` | [A High Power Density Wide Range DC–DC Converter for Universal Electric Vehicle Charging](papers/QQTERPD8-mukherjee-2022-a-high-power-density-wide-range-dc-dc-converter-for-universal-electric.md) | 10.1109/TPEL.2022.3217092 |
| 2022 | `FF6MDWXT` | [A Medium Voltage Input Multiport Isolated Output DC Transformer With Power Self-Balancing and Output Fault Isolation](papers/FF6MDWXT-guan-2022-a-medium-voltage-input-multiport-isolated-output-dc-transformer-with-power.md) | 10.1109/TPEL.2022.3230850 |
| 2022 | `BUKM648G` | [A Multivariable Phase-Locked Loop-Integrated Controller for Enhanced Performance of Voltage Source Converters Under Weak Grid Conditions](papers/BUKM648G-hoseinizadeh-2022-a-multivariable-phase-locked-loop-integrated-controller-for-enhanced.md) | — |
| 2022 | `BWKRWMKH` | [A Novel Resilient Control of Grid-Integrated Solar PV-Hybrid Energy Storage Microgrid for Power Smoothing and Pulse Power Load Accommodation](papers/BWKRWMKH-behera-2022-a-novel-resilient-control-of-grid-integrated-solar-pv-hybrid-energy.md) | 10.1109/TPEL.2022.3217144 |
| 2022 | `NQV723Z7` | [A Review of Recent Best Practices in the Development of Real-Time Power System Simulators from a Simulator Manufacturer’s Perspective](papers/NQV723Z7-sidwall-review-recent-best2022.md) | — |
| 2022 | `4CJFU6DG` | [A Topology-Reconfigurable LLC Resonant Converter for Wide Output Range Applications](papers/4CJFU6DG-li-2022-a-topology-reconfigurable-llc-resonant-converter-for-wide-output-range.md) | 10.1109/TVT.2022.3178712 |
| 2022 | `BPS56KS3` | [An Event-Driven Parallel Acceleration Real-Time Simulation for Power Electronic Systems Without Simulation Distortion in Circuit Partitioning](papers/BPS56KS3-zheng-event-driven-parallel-acceleration2022a.md) | — |
| 2022 | `9JJGN3GT` | [An Event-Driven Real-Time Simulation for Power Electronics Systems Based on Discrete Hybrid Time-Step Algorithm](papers/9JJGN3GT-zheng-event-driven-real-time-simulation2022.md) | — |
| 2022 | `VV9VXZU2` | [An Isolated Multilevel DC–DC Converter Topology With Hybrid Resonant Switching for EV Fast Charging Application](papers/VV9VXZU2-rathore-2022-an-isolated-multilevel-dc-dc-converter-topology-with-hybrid-resonant.md) | 10.1109/TIA.2022.3168504 |
| 2022 | `28WF29I5` | [Analysis of the aliasing effect caused in hardware-in-the-loop when reading PWM inputs of power converters](papers/28WF29I5-zamiri-2021-aliasing-effect.md) | 10.1016/j.ijepes.2021.107678 |
| 2022 | `BUPEE4PJ` | [Applications of Physics-Informed Neural Networks in Power Systems - A Review](papers/BUPEE4PJ-huang-2022-applications-of-physics-informed-neural-networks-in-power-systems-a-review.md) | 10.1109/TPWRS.2022.3162473 |
| 2022 | `APUJJSHA` | [Average-Value Model for Voltage-Source Converters With Direct Interfacing in EMTP-Type Solution](papers/APUJJSHA-ebrahimi-average-value-model-voltage-source2022a.md) | — |
| 2022 | `M3DQ26J6` | [Closed-Loop Interconnected Model of Multi-Inverter-Paralleled System and Its Application to Impact Assessment of Interactions on Damping Characteristics](papers/M3DQ26J6-liao-2022-closed-loop-interconnected-model-of-multi-inverter-paralleled-system-and-its.md) | 10.1109/TSG.2022.3194148 |
| 2022 | `FU4FCKQE` | [Design and Implementation of a Reconfigurable Phase Shift Full-Bridge Converter for Wide Voltage Range EV Charging Application](papers/FU4FCKQE-lyu-2022-design-and-implementation-of-a-reconfigurable-phase-shift-full-bridge.md) | 10.1109/TTE.2022.3176826 |
| 2022 | `3W3VNJJR` | [Direct Interfacing of Parametric Average-Value Models of AC–DC Converters for Nodal Analysis-Based Solution](papers/3W3VNJJR-ebrahimi-direct-interfacing-parametric2022.md) | 10.1109/TEC.2022.3177131 |
| 2022 | `6DT5727A` | [Embedded Fully FPGA-Based Real-Time Simulators for Static Power Converters With Power Switch Characteristics Approximated by Identification](papers/6DT5727A-idkhajine-2022-embedded-fully-fpga-based-real-time-simulators-for-static-power.md) | 10.1109/TIE.2021.3112999 |
| 2022 | `ZJ8B7MGM` | [Fast Simulation Model of Voltage Source Converters With Arbitrary Topology Using Switch-State Prediction](papers/ZJ8B7MGM-gao-2022-fast-simulation-model-of-voltage-source-converters-with-arbitrary-topology.md) | 10.1109/TPEL.2022.3176687 |
| 2022 | `93K77JMM` | [Feasibility Study of Neural ODE and DAE Modules for Power System Dynamic Component Modeling](papers/93K77JMM-xiao-2022-feasibility-study-of-neural-ode-and-dae-modules-for-power-system-dynamic.md) | 10.1109/tpwrs.2022.3194570 |
| 2022 | `4D3SE52Z` | [Hardware-in-the-Loop Simulations: A Historical Overview of Engineering Challenges](papers/4D3SE52Z-mihalic-hardwareinthe-loop-simulations-historical2022a.md) | 10.3390/electronics11152462 |
| 2022 | `HR69NSK4` | [Hybrid Parallel-in-Time-and-Space Transient Stability Simulation of Large-Scale AC/DC Grids](papers/HR69NSK4-cheng-2022-hybrid-parallel-in-time-and-space-transient-stability-simulation-of-large.md) | 10.1109/TPWRS.2022.3153450 |
| 2022 | `QKH3U798` | [In-Depth Design and Multiobjective Optimization of an Integrated Transformer for Five-Phase LLC Resonant Converters](papers/QKH3U798-wang-2022-in-depth-design-and-multiobjective-optimization-of-an-integrated-transformer.md) | 10.1109/TPEL.2022.3187465 |
| 2022 | `W6P6QMUV` | [Intelligent EV Charging for Urban Prosumer Communities: An Auction and Multi-Agent Deep Reinforcement Learning Approach](papers/W6P6QMUV-zou-2022-intelligent-ev-charging-for-urban-prosumer-communities-an-auction-and-multi.md) | 10.1109/TNSM.2022.3160210 |
| 2022 | `88NW8NQG` | [Machine Learning Based Modeling for Real-Time Inferencer-in-the-Loop Hardware Emulation of High-Speed Rail Microgrid](papers/88NW8NQG-zhang-machine-learning-based2022.md) | — |
| 2022 | `P7CRNXAX` | [Massively Parallel Modeling of Battery Energy Storage Systems for AC/DC Grid High-Performance Transient Simulation](papers/P7CRNXAX-lin-2022-massively-parallel-modeling-of-battery-energy-storage-systems-for-ac-dc-grid.md) | 10.1109/TPWRS.2022.3196286 |
| 2022 | `8SKXZQBK` | [Methods for the Accurate Real-Time Simulation of High-Frequency Power Converters](papers/8SKXZQBK-chalangar-methods-accurate-real-time2022.md) | — |
| 2022 | `DWXFPT5X` | [On Modeling Depths of Power Electronic Circuits for Real-Time Simulation - A Comparative Analysis for Power Systems](papers/DWXFPT5X-carne-modeling-depths-power2022.md) | — |
| 2022 | `JW323723` | [Optimal Control of Semi-Dual Active Bridge DC/DC Converter With Wide Voltage Gain in a Fast-Charging Station With Battery Energy Storage](papers/JW323723-rafi-2022-optimal-control-of-semi-dual-active-bridge-dc-dc-converter-with-wide-voltage.md) | 10.1109/TTE.2022.3170737 |
| 2022 | `IGDDM7VQ` | [Parameter Estimation of Power Electronic Converters With Physics-Informed Machine Learning](papers/IGDDM7VQ-zhao-2022-parameter-estimation-of-power-electronic-converters-with-physics-informed.md) | 10.1109/TPEL.2022.3176468 |
| 2022 | `48CPC5RW` | [Passivity-Based Design of a Fractional-Order Virtual Capacitor for Active Damping of Multiparalleled Grid-Connected Current-Source Inverters](papers/48CPC5RW-azghandi-2022-passivity-based-design-of-a-fractional-order-virtual-capacitor-for.md) | 10.1109/TPEL.2022.3148242 |
| 2022 | `CAQJVVPV` | [Real-Time Simulation of Power System Electromagnetic Transients on FPGA Using Adaptive Mixed-Precision Calculations](papers/CAQJVVPV-ma-2022.md) | — |
| 2022 | `R6RA22XZ` | [Research on Harmonic State-Space Modeling and Calculation Analysis of Low-Switching-Frequency Grid-Connected Inverter Considering the Impact of Digitization](papers/R6RA22XZ-cai-2022-research-on-harmonic-state-space-modeling-and-calculation-analysis-of-low.md) | 10.1109/TPEL.2022.3201626 |
| 2022 | `IWAB26RM` | [Scalable Many-Core Algorithms for Tridiagonal Solvers](papers/IWAB26RM-balogh-2022-scalable-many-core-tridiagonal.md) | — |
| 2022 | `M786E779` | [Simulation of Switched-Mode Power Conversion Circuits With Extended Impedance Method](papers/M786E779-liu-2022-simulation-of-switched-mode-power-conversion-circuits-with-extended-impedance.md) | 10.1109/TCSI.2022.3178447 |
| 2022 | `6EBZEVAX` | [State-Feedback Reshaping Control of Voltage Source Converter](papers/6EBZEVAX-cecati-2022-state-feedback-reshaping-control-of-voltage-source-converter.md) | 10.1109/TPEL.2022.3191428 |
| 2022 | `F494RRVH` | [Truncation Number Selection of Harmonic State-Space Model Based on the Floquet Characteristic Exponent](papers/F494RRVH-zhu-2022-truncation-number-selection-of-harmonic-state-space-model-based-on-the.md) | 10.1109/TIE.2022.3172780 |
| 2022 | `UV322KHI` | [Wide Voltage Input Full Bridge(FB)/Half Bridge(HB) Morphing-Based LLC DC–DC Converter Using Numerical Optimal Trajectory Control](papers/UV322KHI-sha-2022-wide-voltage-input-full-bridge-fb-half-bridge-hb-morphing-based-llc-dc-dc.md) | 10.1109/TIE.2022.3177810 |
| 2022 | `JLRJ4EJB` | [半隐式延迟解耦电磁暂态并行仿真方法（一）：原理及交流分网与并行](papers/JLRJ4EJB-yao-shu-jun-ban-yin-shi-yan-chi-jie-ou-dian-ci-zan-tai-bing-xing-fang-zhen-fang-fa-yi-yuan-li-ji-jiao-liu-fen-wang-yu-bing-xing2022.md) | — |
| 2022 | `RUEIE6M9` | [电力电子设备及含电力电子设备电力系统实时仿真研究综述](papers/RUEIE6M9-xu-jin-dian-li-dian-zi-she-bei-ji-han-dian-li-dian-zi-she-bei-dian-li-xi-tong-shi-shi-fang-zhen-yan-jiu-zong-shu2022.md) | — |
| 2022 | `6ZEYBA3W` | [直驱风力发电单元的电磁暂态半隐式延迟解耦与仿真方法](papers/6ZEYBA3W-yao-shu-jun-zhi-qu-feng-li-fa-dian-dan-yuan-de-dian-ci-zan-tai-ban-yin-shi-yan-chi-jie-ou-yu-fang-zhen-fang-fa2022.md) | — |
| 2021 | `8BIZE27F` | [A Direct Mapped Method for Accurate Modeling and Real-Time Simulation of High Switching Frequency Resonant Converters](papers/8BIZE27F-chalangar-direct-mapped-method2021.md) | — |
| 2021 | `UU5787M5` | [A Multiport DC Solid-State Transformer for MVDC Integration Interface of Multiple Distributed Energy Sources and DC Loads in Distribution Network](papers/UU5787M5-zhuang-2021-a-multi-port-dc-solid-state-transformer-for-mvdc-integration-interface-of.md) | 10.1109/TPEL.2021.3105528 |
| 2021 | `8ZJNQ5IW` | [A Novel Decoupling Control Approach for Improving Dynamic Performance and Stability of Multiple Grid-Connected Converters](papers/8ZJNQ5IW-zhang-2021-a-novel-decoupling-control-approach-for-improving-dynamic-performance-and.md) | 10.1109/TIE.2021.3116556 |
| 2021 | `AMTY4M96` | [Accurate and Stable Hardware-in-the-Loop (HIL) Real-Time Simulation of Integrated Power Electronics and Power Systems](papers/AMTY4M96-lauss-accurate-stable-hardwareinthe-loop2021.md) | — |
| 2021 | `XU9MUVXF` | [An Automated Semi–symbolic State Equation Generation Method for Simulation of Power Electronic Systems](papers/XU9MUVXF-yu-2021-an-automated-semi-symbolic-state-equation-generation-method-for-simulation-of.md) | 10.1109/TPEL.2020.3025785 |
| 2021 | `MGDS4WD8` | [Average-Value Modeling of Direct-Driven PMSG-Based Wind Energy Conversion Systems](papers/MGDS4WD8-zhang-2021-average-value-modeling-of-direct-driven-pmsg-based-wind-energy-conversion.md) | 10.1109/TEC.2021.3095486 |
| 2021 | `NZ9RU5KW` | [Average-Value Modeling of Line-Commutated AC–DC Converters With Unbalanced AC Network](papers/NZ9RU5KW-ebrahimi-2021-average-value-modeling-of-line-commutated-ac-dc-converters-with.md) | 10.1109/TEC.2021.3084124 |
| 2021 | `7DQGB3MP` | [Black-Box Modeling of DC-DC Converters Based on Wavelet Convolutional Neural Networks](papers/7DQGB3MP-rojas-duenas-2021-black-box-modeling-of-dc-dc-converters-based-on-wavelet.md) | 10.1109/TIM.2021.3098377 |
| 2021 | `LX3QYBSD` | [Characterization of Time Delay in Power Hardware in the Loop Setups](papers/LX3QYBSD-guillo-sansano-characterization-time-delay2021.md) | 10.1109/TIE.2020.2972454 |
| 2021 | `D299JA8D` | [Clustering-Based Modeling and Interaction Analysis of Multiple Differently Parameterized Grid-Side Inverters in PMSG Wind Turbines](papers/D299JA8D-liao-2021-clustering-based-modeling-and-interaction-analysis-of-multiple-differently.md) | 10.1109/TEC.2021.3071155 |
| 2021 | `2DMZSU5N` | [Comparison and Selection of Grid-Tied Inverter Models for Accurate and Efficient EMT Simulations](papers/2DMZSU5N-sano-comparison-selection-grid-tied2021.md) | — |
| 2021 | `QSWWGCX2` | [Compensation method for parallel real-time EMT studies](papers/QSWWGCX2-bruned-compensation-method-parallel2021b.md) | — |
| 2021 | `ZZ7QBXK3` | [Current-Source Solid-State DC Transformer Integrating LVDC Microgrid, Energy Storage, and Renewable Energy Into MVDC Grid](papers/ZZ7QBXK3-zheng-2021-current-source-solid-state-dc-transformer-integrating-lvdc-microgrid-energy.md) | 10.1109/TPEL.2021.3101482 |
| 2021 | `G4HJD7JE` | [Determination of Optimal Shift Frequency for Shifted Frequency-Based Simulation](papers/G4HJD7JE-gao-2021-determination-of-optimal-shift-frequency-for-shifted-frequency-based.md) | 10.1109/TPWRS.2021.3076829 |
| 2021 | `Z2ZQDR9T` | [Embedding an Electrical System Real-Time Simulator with Floating-Point Arithmetic in a Field Programmable Gate Array](papers/Z2ZQDR9T-queiroz-2021.md) | — |
| 2021 | `N9E5UDFK` | [Hardware-in-the-Loop and Digital Control Techniques Applied to Single-Phase PFC Converters](papers/N9E5UDFK-lamo-2021.md) | 10.3390/electronics10131563 |
| 2021 | `C6M2RQVP` | [High-Throughput FPGA Implementation of Matrix Inversion for Control Systems](papers/C6M2RQVP-zhang-2021-high-throughput-fpga-implementation-of-matrix-inversion-for-control-systems.md) | 10.1109/TIE.2020.2994865 |
| 2021 | `HMTDNJN5` | [Hybrid Average-Value/Detailed Modeling of Line-Commutated AC–DC Converters With Internal Faults For Electromagnetic Transient Simulations](papers/HMTDNJN5-ebrahimi-hybrid-average-value-detailed2021.md) | — |
| 2021 | `GWCRGVPI` | [Simulation Credibility Assessment Methodology With FPGA-based Hardware-in-the-Loop Platform：中文精读](papers/GWCRGVPI-dai-2021.md) | — |
| 2021 | `ZPWPBDZZ` | [The Impact of Time Delays for Power Hardware-in-the-Loop Investigations](papers/ZPWPBDZZ-ihrens-impact-time-delays2021.md) | 10.3390/en14113154 |
| 2021 | `PVZ8FUEY` | [一种面向实时仿真的两电平 VSC 建模方法](papers/PVZ8FUEY-lin-chang-yi-zhong-mian-xiang-shi-shi-fang-zhen-de-liang-dian-ping-vscjian-mo-fang-fa2021.md) | — |
| 2021 | `BME3QXGI` | [基于FPGA的电力电子系统实时仿真算法](papers/BME3QXGI-wang-ran-ji-yu-fpgade-dian-li-dian-zi-xi-tong-shi-shi-fang-zhen-suan-fa2021.md) | — |
| 2020 | `RQUEF5PX` | [A Device-Level Transient Modeling Approach for the FPGA-Based Real-Time Simulation of Power Converters](papers/RQUEF5PX-bai-device-level-transient-modeling2020.md) | — |
| 2020 | `48BGU93J` | [An Inverter Model Simulating Accurate Harmonics With Low Computational Burden for Electromagnetic Transient Simulations](papers/48BGU93J-horiuchi-inverter-model-simulating2020.md) | — |
| 2020 | `77AIWIPB` | [Electrothermal Transient Behavioral Modeling of Thyristor-Based Ultrafast Mechatronic Circuit Breaker for Real-Time DC Grid Emulation](papers/77AIWIPB-lin-electrothermal-transient-behavioral2020a.md) | — |
| 2020 | `QWGMUZH5` | [FPGA-based real-time simulation for EV station with multiple high-frequency chargers based on C-EMTP algorithm](papers/QWGMUZH5-li-fpgabased-realtime-simulation2020a.md) | 10.1186/s41601-020-00171-x |
| 2020 | `WNRAZ79Z` | [FPGA-Based Sub-Microsecond-Level Real-Time Simulation for Microgrids With a Network-Decoupled Algorithm](papers/WNRAZ79Z-xu-fpgabased-sub-microsecond-level-real-time2020.md) | — |
| 2020 | `2JDC4NQ2` | [FPGA-Based Submicrosecond-Level Real-Time Simulation of Solid-State Transformer With a Switching Frequency of 50 kHz](papers/2JDC4NQ2-xu-fpgabased-submicrosecond-level-real-time2020b.md) | 10.1109/JESTPE.2020.3037233 |
| 2020 | `H945MNEB` | [High-Speed Electromagnetic Transient (EMT) Equivalent Modelling of Power Electronic Transformers](papers/H945MNEB-xu-high-speed-electromagnetic-transient2020a.md) | — |
| 2020 | `W45NEA75` | [Interfacing of Parametric Average-Value Models of LCR Systems in Fixed-Time-Step Real-Time EMT Simulations](papers/W45NEA75-ebrahimi-interfacing-parametric-average-value2020.md) | — |
| 2020 | `J6Z2HH73` | [Machine Learning Building Blocks for Real-Time Emulation of Advanced Transport Power Systems](papers/J6Z2HH73-zhang-machine-learning-building2020.md) | — |
| 2020 | `WSWEB4XQ` | [Multi-Rate Real-Time Simulation Method Based on the Norton Equivalent](papers/WSWEB4XQ-zhu-multi-rate-real-time-simulation2020b.md) | — |
| 2020 | `GFMQBWWJ` | [Parallel-in-Time Object-Oriented Electromagnetic Transient Simulation of Power Systems](papers/GFMQBWWJ-cheng-parallelin-time-object-oriented-electromagnetic2020.md) | 10.1109/OAJPE.2020.3012636 |
| 2020 | `4FG4XQ9E` | [Power Electronic Converter Based Flexible Transmission Line Emulation](papers/4FG4XQ9E-dutta-power-electronic-converter2020.md) | 10.1109/TIE.2019.2922940 |
| 2020 | `9C62Z4RV` | [Real-Time Hardware-in-the-Loop Emulation of High-Speed Rail Power System With SiC-Based Energy Conversion](papers/9C62Z4RV-liang-real-time-hardwareinthe-loop-emulation2020.md) | — |
| 2020 | `YRXGNX4M` | [Real-Time Simulation of Power Electronic Systems Based on Predictive Behavior](papers/YRXGNX4M-liu-real-time-simulation-power2020.md) | — |
| 2020 | `65GH88NM` | [Real-Time Simulation-Based Testing of Modern Energy Systems: A Review and Discussion](papers/65GH88NM-benigni-real-time-simulation-based-testing2020a.md) | — |
| 2020 | `C6WAFSRS` | [Review of Real-time Simulation of Power Electronics](papers/C6WAFSRS-li-review-realtime-simulation2020.md) | — |
| 2020 | `8CFI93TR` | [Stability Evaluation of Interpolation, Extrapolation, and Numerical Oscillation Damping Methods Applied in EMT Simulation of Power Networks With Switching Transients](papers/8CFI93TR-zhao-stability-evaluation-interpolation2020.md) | — |
| 2020 | `48FKD8EU` | [Use of efficient task allocation algorithm for parallel real-time EMT simulation](papers/48FKD8EU-bruned-use-efficient-task2020b.md) | — |
| 2019 | `P2SAJ8VM` | [A Fast and Stable Method for Modeling Generalized Nonlinearities in Power Electronic Circuit Simulation and Its Real-Time Implementation](papers/P2SAJ8VM-huang-fast-stable-method2018.md) | 10.1109/TPEL.2018.2851570 |
| 2019 | `WV2NL3DR` | [A Generalized Associated Discrete Circuit Model of Power Converters in Real-Time Simulation](papers/WV2NL3DR-wang-generalized-associated-discrete2019.md) | — |
| 2019 | `V68XCBXG` | [A Network Analysis Modeling Method of the Power Electronic Converter for Hardware-in-the-Loop Application](papers/V68XCBXG-liu-network-analysis-modeling.md) | 10.1109/TTE.2019.2932959 |
| 2019 | `YQDA3CV2` | [A new SRF-based power angle control method for UPQC-DG to integrate solar PV into grid](papers/YQDA3CV2-patel-new-srfbased-power2019.md) | 10.1002/etep.2667 |
| 2019 | `IGYGRYEQ` | [A parallel modular computing approach to real-time simulation of multiple fuel cells hybrid power system](papers/IGYGRYEQ-zhang-parallel-modular-computing2019.md) | — |
| 2019 | `BB9CSDWX` | [An Efficient Hierarchical Zonal Method for Large-Scale Circuit Simulation and Its Real-Time Application on More Electric Aircraft Microgrid](papers/BB9CSDWX-huang-efficient-hierarchical-zonal2019a.md) | — |
| 2019 | `N35N4HZE` | [An FPGA-Based IGBT Behavioral Model With High Transient Resolution for Real-Time Simulation of Power Electronic Circuits](papers/N35N4HZE-bai-fpgabased-igbtbehavioral2019.md) | — |
| 2019 | `RLV9PXZN` | [Device-level modelling and FPGA-based real-time simulation of the power electronic system in fuel cell electric vehicle](papers/RLV9PXZN-bai-devicelevel-modelling-fpgabased2019.md) | — |
| 2019 | `BMLVFF5E` | [Exact Nonlinear Micromodeling for Fine-Grained Parallel EMT Simulation of MTDC Grid Interaction With Wind Farm](papers/BMLVFF5E-lin-exact-nonlinear-micromodeling2019a.md) | — |
| 2019 | `Y9DDITL4` | [FPGA-Based Device-Level Electro-Thermal Modeling of Floating Interleaved Boost Converter for Fuel Cell Hardware-in-the-Loop Applications](papers/Y9DDITL4-bai-fpgabased-device-level-electro-thermal2019.md) | 10.1109/TIA.2019.2918048 |
| 2019 | `MZ9JHCQ7` | [FPGA-Based Real-Time Simulation of High-Power Electronic System With Nonlinear IGBT Characteristics](papers/MZ9JHCQ7-liu-fpgabased-real-time-simulation2019.md) | — |
| 2019 | `MVM9WQ5V` | [Real-Time Multi-FPGA Simulation of Energy Conversion Systems](papers/MVM9WQ5V-milton-2019-lb-lmc-multi-fpga.md) | — |
| 2019 | `DESMS3TW` | [Real-time simulation of large-scale HTS systems: multi-scale and homogeneous models using the T–A formulation](papers/DESMS3TW-berrospe-juarez-realtime-simulation-largescale2019a.md) | 10.1088/1361-6668/ab0d66 |
| 2019 | `DTD3ZZTF` | [Variable Time-Stepping Modular Multilevel Converter Model for Fast and Parallel Transient Simulation of Multiterminal DC Grid](papers/DTD3ZZTF-lin-variable-time-stepping-modular2019a.md) | 10.1109/TIE.2018.2880671 |
| 2018 | `VPG57F8G` | [A 400-V/50-kVA Digital–Physical Hybrid Real-Time Simulation Platform for Power Systems](papers/VPG57F8G-mao400-v50k-vadigital2018.md) | 10.1109/TIE.2017.2760844 |
| 2018 | `X5A2JZWW` | [A Benchmark System for Hardware-in-the-Loop Testing of Distributed Energy Resources](papers/X5A2JZWW-kotsampopoulos-benchmark-system-hardwareinthe-loop2018a.md) | 10.1109/JPETS.2018.2861559 |
| 2018 | `FD55F6GJ` | [A new approach for FPGA-based real-time simulation of power electronic system with no simulation latency in subsystem partitioning](papers/FD55F6GJ-liu-new-approach-fpgabased2018.md) | 10.1016/j.ijepes.2018.01.053 |
| 2018 | `FEX2JNU8` | [A Novel Platform for Powertrain Modeling of Electric Cars With Experimental Validation Using Real-Time Hardware in the Loop (HIL): A Case Study of GM Second Generation Chevrolet Volt](papers/FEX2JNU8-abdelrahman-novel-platform-powertrain2018.md) | 10.1109/TPEL.2018.2793818 |
| 2018 | `5LPF9783` | [A System-Level FPGA-Based Hardware-in-the-Loop Test of High-Speed Train](papers/5LPF9783-liu-system-level-fpgabased-hardwareinthe-loop2018.md) | 10.1109/TTE.2018.2866696 |
| 2018 | `CG5WUJQN` | [An improved control method for unified power quality conditioner with unbalanced load](papers/CG5WUJQN-patel-improved-control-method2018.md) | 10.1016/j.ijepes.2018.02.035 |
| 2018 | `9PFHAKN7` | [Design and Implementation of Real-Time Mpsoc-FPGA-Based Electromagnetic Transient Emulator of CIGRÉ DC Grid for HIL Application](papers/9PFHAKN7-shen-2018.md) | 10.1109/JPETS.2018.2866589 |
| 2018 | `75JVEBMG` | [Detailed Device-Level Electrothermal Modeling of the Proactive Hybrid HVDC Breaker for Real-Time Hardware-in-the-Loop Simulation of DC Grids](papers/75JVEBMG-lin-detailed-device-level-electrothermal2018a.md) | 10.1109/TPEL.2017.2685423 |
| 2018 | `IDUSA32I` | [Extendable multirate real-time simulation of active distribution networks based on field programmable gate arrays](papers/IDUSA32I-wang-extendable-multirate-realtime2018.md) | 10.1016/j.apenergy.2018.07.099 |
| 2018 | `JKF7XR53` | [High-Speed EMT Modeling of MMCs With Arbitrary Multiport Submodule Structures Using Generalized Norton Equivalents](papers/JKF7XR53-xu-high-speed-emtmodeling2017.md) | 10.1109/TPWRD.2017.2740857 |
| 2018 | `BFRVBV2Z` | [On the Numerical Accuracy of Electromagnetic Transient Simulation With Power Electronics](papers/BFRVBV2Z-tant-numerical-accuracy-electromagnetic2018.md) | 10.1109/TPWRD.2018.2797259 |
| 2018 | `KNJRSBSA` | [Real-Time Device-Level Simulation of MMC-Based MVDC Traction Power System on MPSoC](papers/KNJRSBSA-liang-real-time-device-level-simulation2018.md) | 10.1109/TTE.2018.2823059 |
| 2018 | `C95T96KI` | [Real-Time FEM Computation of Nonlinear Magnetodynamics of Moving Structures on FPGA for HIL Emulation](papers/C95T96KI-jandaghi-real-time-femcomputation2018a.md) | 10.1109/TIE.2018.2801843 |
| 2018 | `2REETHNT` | [Real-Time FPGA-RTDS Co-Simulator for Power Systems](papers/2REETHNT-yang-2018.md) | 10.1109/ACCESS.2018.2862893 |
| 2018 | `BHAH8H6B` | [电力系统高效电磁暂态仿真技术综述](papers/BHAH8H6B-dong-yi-feng-dian-li-xi-tong-gao-xiao-dian-ci-zan-tai-fang-zhen-ji-shu-zong-shu2018.md) | 10.13334/j.0258-8013.pcsee.171055 |
| 2017 | `VJM8SKS5` | [Behavioral Device-Level Modeling of Modular Multilevel Converters in Real Time for Variable-Speed Drive Applications](papers/VJM8SKS5-lin-behavioral-device-level-modeling2017.md) | 10.1109/JESTPE.2017.2673818 |
| 2017 | `LEPB3LJE` | [Dynamic Variable Time-Stepping Schemes for Real-Time FPGA-Based Nonlinear Electromagnetic Transient Emulation](papers/LEPB3LJE-shen-dynamic-variable-time-stepping2017.md) | 10.1109/TIE.2017.2652403 |
| 2017 | `2PHB9G4M` | [Synchronisation mechanism and interfaces design of multi-FPGA-based real-time simulator for microgrids](papers/2PHB9G4M-li-2017-synchronisation-multi-fpga-microgrids.md) | — |
| 2017 | `UH7E95KD` | [Three-Phase Power Converter-Based Real-Time Synchronous Generator Emulation](papers/UH7E95KD-yang-three-phase-power-converter-based2017.md) | 10.1109/TPEL.2016.2553168 |
| 2017 | `MKZBHF94` | [基于多FPGA的电力电子实时仿真系统](papers/MKZBHF94-zhu-jian-xin-ji-yu-duo-fpgade-dian-li-dian-zi-shi-shi-fang-zhen-xi-tong2017.md) | 10.7500/AEPS20160907050 |
| 2016 | `WIFUHPW8` | [ADC-Based Embedded Real-Time Simulator of a Power Converter Implemented in a Low-Cost FPGA: Application to a Fault-Tolerant Control of a Grid-Connected Voltage-Source Rectifier](papers/WIFUHPW8-dagbagi-adcbased-embedded-real-time2016.md) | 10.1109/TIE.2015.2491883 |
| 2016 | `TX8IWQ2Z` | [An Advanced HIL Simulation Battery Model for Battery Management System Testing](papers/TX8IWQ2Z-barreras-advanced-hilsimulation2016.md) | 10.1109/TIA.2016.2585539 |
| 2016 | `KVPMC7K7` | [An Equivalent Circuit Method for Modelling and Simulation of Modular Multilevel Converters in Real-Time HIL Test Bench](papers/KVPMC7K7-li-equivalent-circuit-method2016a.md) | 10.1109/TPWRD.2016.2541461 |
| 2016 | `CAT5QBIK` | [Characteristics and Design of Power Hardware-in-the-Loop Simulations for Electrical Power Systems](papers/CAT5QBIK-lauss-characteristics-design-power2015a.md) | 10.1109/TIE.2015.2464308 |
| 2016 | `WANJHN6H` | [Detailed Magnetic Equivalent Circuit Based Real-Time Nonlinear Power Transformer Model on FPGA for Electromagnetic Transient Studies](papers/WANJHN6H-liu-detailed-magnetic-equivalent2016a.md) | — |
| 2016 | `TWTFXPGE` | [Real-Time Simulation-Based Multisolver Decoupling Technique for Complex Power-Electronics Circuits](papers/TWTFXPGE-gregoire-2016-multisolver-decoupling.md) | — |
| 2016 | `WFT6K3AE` | [Static and Dynamic Power System Load Emulation in a Converter-Based Reconfigurable Power Grid Emulator](papers/WFT6K3AE-wang-static-dynamic-power2016.md) | 10.1109/TPEL.2015.2448548 |
| 2015 | `GAMCUNPR` | [A Network Tearing Technique for FPGA-Based Real-Time Simulation of Power Converters](papers/GAMCUNPR-ould-bachir-network-tearing-technique2015.md) | — |
| 2015 | `27W8T9ID` | [CPU/FPGA-Based Real-Time Simulation of a Two-Terminal MMC-HVDC System](papers/27W8T9ID-ould-bachir-2015-cpu-fpga-mmc-hvdc.md) | — |
| 2015 | `G7MWPVIS` | [FPGA-Based Detailed Real-Time Simulation of Power Converters and Electric Machines for EV HIL Applications](papers/G7MWPVIS-herrera-fpgabased-detailed2015.md) | 10.1109/TIA.2014.2350074 |
| 2015 | `XFCSIJAJ` | [Parallel Scheduling of Task Trees with Limited Memory](papers/XFCSIJAJ-eyraud-dubois-2015-task-trees-limited-memory.md) | — |
| 2015 | `Z36387C2` | [Real-Time Simulation Technologies for Power Systems Design, Testing, and Analysis](papers/Z36387C2-omarfaruque-real-time-simulation-technologies2015.md) | — |
| 2015 | `HQ36QJRB` | [The Limitations of Digital Simulation and the Advantages of PHIL Testing in Studying Distributed Generation Provision of Ancillary Services](papers/HQ36QJRB-kotsampopoulos-limitations-digital-simulation2015a.md) | 10.1109/TIE.2015.2414899 |
| 2014 | `BNFRNR38` | [A General Framework for FPGA-Based Real-Time Emulation of Electrical Machines for HIL Applications](papers/BNFRNR38-tavana-general-framework-fpgabased2014a.md) | — |
| 2014 | `K7FGD3VE` | [A Parallel Approach to Real-Time Simulation of Power Electronics Systems](papers/K7FGD3VE-benigni-parallel-approach-real-time2014.md) | 10.1109/TPEL.2014.2361868 |
| 2014 | `H3W376GN` | [Direct Interfacing of Dynamic Average Models of Line-Commutated Rectifier Circuits in Nodal Analysis EMTP-Type Solution](papers/H3W376GN-chiniforoosh-direct-interfacing-dynamic2014.md) | 10.1109/TCSI.2013.2290830 |
| 2014 | `25FW7XW4` | [FPGA-Based Real-Time Simulation of a DC/DC Converter](papers/25FW7XW4-deter-2014-fpga-real-time-dcdc-converter.md) | — |
| 2014 | `2TKT64RA` | [Hardware Emulation Building Blocks for Real-Time Simulation of Large-Scale Power Grids](papers/2TKT64RA-chen-hardware-emulation-building2013a.md) | 10.1109/TII.2013.2243742 |
| 2014 | `7AIG3J5M` | [On the Use of Real-Time Simulation Technology in Smart Grid Research and Development](papers/7AIG3J5M-dufour-use-real-time-simulation2014a.md) | — |
| 2014 | `BHV5NM47` | [基于 FPGA 的配电网暂态实时仿真研究（一）：功能模块实现](papers/BHV5NM47-wang-cheng-shan-ji-yu-fpgade-pei-dian-wang-zan-tai-shi-shi-fang-zhen-yan-jiu-yi-gong-neng-mo-kuai-shi-xian2014.md) | 10.13334/j.0258-8013.pcsee.2014.01.019 |
| 2014 | `7CPE3YEM` | [基于 FPGA 的配电网暂态实时仿真研究（二）：系统架构与算例验证](papers/7CPE3YEM-wang-cheng-shan-ji-yu-fpgade-pei-dian-wang-zan-tai-shi-shi-fang-zhen-yan-jiu-er-xi-tong-jia-gou-yu-suan-li-yan-zheng2014.md) | — |
| 2014 | `V3IYP9LS` | [基于传输线分网的并行多速率电磁暂态仿真算法](papers/V3IYP9LS-mu-qing-ji-yu-chuan-shu-xian-fen-wang-de-bing-xing-duo-su-lu-dian-ci-zan-tai-fang-zhen-suan-fa2014.md) | — |
| 2013 | `Z4B8AE88` | [A fully automated reconfigurable calculation engine dedicated to the real-time simulation of high switching frequency power electronic circuits](papers/Z4B8AE88-ouldbachir-fully-automated-reconfigurable2013.md) | 10.1016/j.matcom.2012.07.021 |
| 2013 | `ENI8NE24` | [Comprehensive Real-Time Simulation of the Smart Grid](papers/ENI8NE24-guo-comprehensive-real-time-simulation2013a.md) | — |
| 2013 | `HKDKQIIF` | [Inclusion of Rational Models in an Electromagnetic Transients Program: Y-Parameters, Z-Parameters, S-Parameters, Transfer Functions](papers/HKDKQIIF-gustavsen-inclusion-rational-models2013a.md) | — |
| 2013 | `JCK2ZZKM` | [Multi-FPGA digital hardware design for detailed large-scale real-time electromagnetic transient simulation of power systems](papers/JCK2ZZKM-chen-multi-fpgadigital-hardware2013.md) | 10.1049/iet-gtd.2012.0374 |
| 2013 | `CTQUEIHA` | [Real-Time Simulation of MMCs Using CPU and FPGA](papers/CTQUEIHA-saad-real-time-simulation-mmcs2013a.md) | — |
| 2011 | `PHUPVIVA` | [A Combined State-Space Nodal Method for the Simulation of Power System Transients](papers/PHUPVIVA-dufour-2011-state-space-nodal.md) | — |
| 2011 | `HDU7A3A9` | [Ultralow-Latency Hardware-in-the-Loop Platform for Rapid Validation of Power Electronics Designs](papers/HDU7A3A9-majstorovic-ultralow-latency-hardwareinthe-loop-platform2011.md) | 10.1109/TIE.2011.2112318 |
| 2010 | `P37EV2TG` | [A Megawatt-Scale Power Hardware-in-the-Loop Simulation Setup for Motor Drives](papers/P37EV2TG-steurer-megawatt-scale-power-hardwareinthe-loop2009.md) | 10.1109/TIE.2009.2036639 |
| 2010 | `NK7GZT2W` | [Efficient Modeling of Modular Multilevel HVDC Converters (MMC) on Electromagnetic Transient Simulation Programs](papers/NK7GZT2W-gnanarathna-efficient-modeling-modular2010.md) | — |
| 2010 | `4WXTWIBC` | [Hardware-in-the-Loop Simulation of Power Electronic Systems Using Adaptive Discretization](papers/4WXTWIBC-faruque-hardwareinthe-loop-simulation-power2009.md) | 10.1109/TIE.2009.2036647 |
| 2010 | `IQ3FF3TB` | [Massively Parallel Implementation of AC Machine Models for FPGA-Based Real-Time Simulation of Electromagnetic Transients](papers/IQ3FF3TB-matar-massively-parallel-implementation2010.md) | — |
| 2009 | `Z4RFE9X6` | [Simulation Tools for Electromagnetic Transients in Power Systems: Overview and Challenges](papers/Z4RFE9X6-mahseredjian-simulation-tools-electromagnetic2009a.md) | — |
| 2008 | `HZWN86RV` | [FPGA-Based Real-Time EMTP](papers/HZWN86RV-yuan-fpgabased-real-time-emtp2008.md) | 10.1109/TPWRD.2008.923392 |
| 2008 | `B5F7FGPC` | [Numerical Integration by the 2-Stage Diagonally Implicit Runge-Kutta Method for Electromagnetic Transient Simulations](papers/B5F7FGPC-noda-numerical-integration2-stage2008.md) | — |
| 2007 | `DSATQRHR` | [A Low-Cost Real-Time Hardware-in-the-Loop Testing Approach of Power Electronics Controls](papers/DSATQRHR-lu-low-cost-real-time-hardwareinthe-loop2007.md) | 10.1109/TIE.2007.892253 |
| 2007 | `I4ZM9CCW` | [An Optimization-Enabled Electromagnetic Transient Simulation-Based Methodology for HVDC Controller Design](papers/I4ZM9CCW-filizadeh-optimization-enabled-electromagnetic-transient2007.md) | — |
| 2007 | `X42DCC9J` | [Real-Time Digital Hardware Simulation of Power Electronics and Drives](papers/X42DCC9J-parma-real-time-digital-hardware2007.md) | 10.1109/TPWRD.2007.893620 |
| 2006 | `6KBUIWBJ` | [A Versatile Cluster-Based Real-Time Digital Simulator for Power Engineering Research](papers/6KBUIWBJ-pak-versatile-cluster-based-real-time2006.md) | 10.1109/TPWRS.2006.873414 |
| 2006 | `WMSCF7WU` | [A Voltage-Behind-Reactance Synchronous Machine Model for the EMTP-Type Solution](papers/WMSCF7WU-wang-voltage-behind-reactance-synchronous-machine2006.md) | 10.1109/TPWRS.2006.883670 |
| 2005 | `KBDGFVZS` | [Real-Time Simulation of Voltage Source Converters Based on Time Average Method](papers/KBDGFVZS-lian-real-time-simulation-voltage2005.md) | 10.1109/TPWRS.2004.831254 |
| 2004 | `TN5WKIIU` | [Flexible Numerical Integration for Efficient Representation of Switching in Real Time Electromagnetic Transients Simulation](papers/TN5WKIIU-strunz-flexible-numerical-integration2004.md) | 10.1109/TPWRD.2004.824387 |
| 2003 | `77RFV9T6` | [Real Time Network Simulation With PC-Cluster](papers/77RFV9T6-hollman-real-time-network2003.md) | 10.1109/TPWRS.2002.804917 |
| 2000 | `ZKE3JAMD` | [Efficient and Accurate Representation of Asynchronous Network Structure Changing Phenomena in Digital Real Time Simulators](papers/ZKE3JAMD-strunz-efficient-accurate-representation2000.md) | 10.1109/59.867145 |
| 1999 | `SU58NJKX` | [Real Time Digital Power System Simulator Design Considerations and Relay Performance Evaluation](papers/SU58NJKX-jakominich-real-time-digital1999.md) | 10.1109/61.772314 |
| 1997 | `J2DWNXG9` | [Creating an Electromagnetic Transients Program in MATLAB: MatEMTP](papers/J2DWNXG9-mahseredjian-creating-electromagnetic-transients1997.md) | 10.1109/61.568262 |
| 1996 | `RUVP93QN` | [Design, implementation and validation of a real-time digital simulator for protection relay testing](papers/RUVP93QN-kezunovic-design-implementation-validation1996a.md) | 10.1109/61.484012 |
| 1995 | `2PA879GG` | [Comparison of the ATP version of the EMTP and the NETOMAC program for simulation of HVDC systems](papers/2PA879GG-lehn-comparison-atpversion1995a.md) | 10.1109/61.473344 |
| 1992 | `DTXXBU2G` | [A real time digital simulator for testing relays](papers/DTXXBU2G-mclaren-real-time-digital1992.md) | 10.1109/61.108909 |
| 1992 | `TUDTMNXF` | [Highly Parallel Sparse Cholesky Factorization](papers/TUDTMNXF-gilbert-schreiber-1992-highly-parallel-sparse-cholesky.md) | — |
| 1992 | `X39IQQMX` | [Real-time digital simulator for power system analysis on a hypercube computer](papers/X39IQQMX-taoka-realtime-digital-simulator1992a.md) | 10.1109/59.141680 |
| 1991 | `QNSJH7TM` | [Power converter simulation module connected to the EMTP](papers/QNSJH7TM-mahseredjian-power-converter-simulation1991.md) | 10.1109/59.76692 |
| 1990 | `WMRKXT92` | [A Real Time Power System Simulation Laboratory Environment](papers/WMRKXT92-foley-real-time-power1990a.md) | 10.1109/59.99392 |
| 1989 | `GKDER7DW` | [Real-time digital simulator of the electromagnetic transients of transmission lines with frequency dependence](papers/GKDER7DW-wang-realtime-digital-simulator1989a.md) | 10.1109/61.35654 |
| 1989 | `B49IQ77A` | [Suppression of Numerical Oscillations in the EMTP](papers/B49IQ77A-marti-suppression-numerical-oscillations1989.md) | 10.1109/59.193849 |
| 1989 | `U6HIF8TT` | [Task Scheduling for Parallel Sparse Cholesky Factorization](papers/U6HIF8TT-geist-ng-1989-parallel-sparse-cholesky-scheduling.md) | — |
| 1974 | `BR8MRFK8` | [Computation of Electromagnetic Transients](papers/BR8MRFK8-dommel-computation-electromagnetic-transients1974a.md) | 10.1109/PROC.1974.9550 |
| 1971 | `CT8HAT9V` | [Nonlinear and Time-Varying Elements in Digital Simulation of Electromagnetic Transients](papers/CT8HAT9V-dommel-nonlinear-time-varying-elements1971.md) | 10.1109/TPAS.1971.292905 |
| 1969 | `3MTIVAU5` | [Digital Computer Solution of Electromagnetic Transients in Single- and Multiphase Networks](papers/3MTIVAU5-dommel-digital-computer-solution1969.md) | 10.1109/TPAS.1969.292459 |
| — | `HMZB9NFG` | [A High-Stability Real-Time Simulation Model for DC–AC Power Electronic Converters and Digital Twin Applications](papers/HMZB9NFG-high-stability-real-time-simulation-model.md) | — |
| — | `S2N95R33` | [A Real-Time Simulation Model with Constant Admittance Matrix for Multiple Grid-Connected Converters System](papers/S2N95R33-constant-admittance-multi-converter-rts.md) | — |
| — | `C5DJZKNP` | [ANN-Aided Data-Driven IGBT Switching Transient Modeling Approach for FPGA-Based Real-Time Simulation of Power Converters](papers/C5DJZKNP-zotero-item-1086.md) | — |
| — | `MP9ZE98M` | [Heterogeneous Real-Time Co-Emulation for Communication-Enabled Global Control of AC/DC Grid Integrated With Renewable Energy](papers/MP9ZE98M-zotero-item-941.md) | — |
| — | `5WB6J2JA` | [Modeling Method for DFIG-Based Wind Farm in High-Efficiency Real-Time Electromagnetic Transient (EMT) Simulations](papers/5WB6J2JA-liu-dfig-wind-farm-real-time-emt.md) | — |
| — | `L43KXQGH` | [Shiwei Xia et al. (2025) — Real-Time Modeling Method for Large-Scale Photovoltaic Power Stations Using Nested Fast and Simultaneous Solution](papers/L43KXQGH-xia-nested-fast-simultaneous-solution.md) | — |
| — | `E87DFKRD` | [Suppression of Chattering in the Real-Time Simulation of the Power Converter](papers/E87DFKRD-liu-suppression-chattering-real-time.md) | — |
| — | `GADZUETV` | [Wang et al. 2025：面向并行 EMT 的 state-variable-preserving 建模](papers/GADZUETV-wang-state-variable-preserving-parallel-emt.md) | 10.1049/gtd2.70013 |

## 维护

新增、删除或重命名卡片后运行：

```powershell
python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py"
python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py" --check
```

`README.md` 由该脚本生成；不要手工维护论文清单或固定数量。
