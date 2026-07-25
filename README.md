# Paper Reading Notes

面向 Codex 与 ChatGPT 网页端的论文精读卡仓库。每篇论文对应 `papers/` 下的一份 Markdown；所有卡片属于同一正式语料集合，数量由当前文件自动计算。

## Agent 访问入口

- Codex 本地索引：`D:\proj\mac\paper-reading-notes\README.md`
- Codex 本地卡片目录：`D:\proj\mac\paper-reading-notes\papers`
- ChatGPT 网页端索引：https://github.com/sxw228/paper-reading-notes
- 下表中的相对链接在本地解析为 Codex 可读路径，在 GitHub 上解析为 ChatGPT 可打开的网页链接。
- 命中 Zotero key、DOI 或论文身份后，优先完整读取精读卡；只有卡片缺少所需事实或需要核对原文位置时才回到源 PDF。
- AnySearch 与 ai4scholar 只发现候选；已选论文缺少 PDF 时，Agent 将其加入 Zotero 并等待用户手动取得和挂载全文。

## 检索模式

- **本地优先（默认）**：只检索本索引、精读卡正文和本地 Zotero，不访问全网；本地证据不足时先报告缺口。
- **免费链路**：先走本地链路，再使用 AnySearch 补充候选。
- **付费链路**：先走本地链路，再使用 AnySearch 与 ai4scholar 补充并交叉核对候选。
- Asta 当前不可用，不属于以上任一模式。

## 全部精读卡（176）

| 年份 | Zotero key | 论文 | DOI |
|---:|---|---|---|
| 2026 | `WGUS4P5R` | [A General FPGA-Based Accelerated Solver for Electromagnetic Transient Simulations](papers/WGUS4P5R-liang-2026-general-fpga-solver.md) | 10.3390/electronics15030606 |
| 2026 | `6EN6SEVB` | [A Generalized Fixed-Admittance ADC Model for Two-Level Converters in EMT Simulation](papers/6EN6SEVB-cao-2026-generalized-fixed-admittance-adc.md) | — |
| 2026 | `AUH78FB2` | [Harmonic-Preserved Average-Value Model for Converters in Electromagnetic Transient Simulation](papers/AUH78FB2-cao-2026-harmonic-preserved-avm.md) | — |
| 2025 | `YV7C8DG7` | [A Bridge-Arm-Module-Based Fixed-Admittance ADC Model for Converters in EMT Simulation — 中文深度精读](papers/YV7C8DG7-cao-bridge-arm-module-based-fixed-admittance-adc2025.md) | — |
| 2025 | `9Y7KA9KJ` | [A General Interface-Free Delayed Real-Time Simulation Method with A-Stability for Power Electronic Converters](papers/9Y7KA9KJ-xu-2025-interface-free-delayed-rt-sim.md) | — |
| 2025 | `X98GS3IY` | [A State Variables Elimination-Based EMTP-Type Constant Admittance Equivalent Modeling Method for Power Electronic Converters](papers/X98GS3IY-xu-state-variables-elimination-based2025.md) | — |
| 2025 | `23XSBNW6` | [Data-Driven Modeling of Modular Multilevel Converters Based on HHT and CNN-LSTM-AM Neural Network](papers/23XSBNW6-data-driven-mmc-hht-cnn-lstm-am.md) | 10.1109/TIE.2024.3433509 |
| 2025 | `DB48HZNK` | [Electromagnetic Transient Equivalent Modeling and Real-Time Simulation Method for Bidirectional DC/DC Converters](papers/DB48HZNK-xu-2025-bdc-constant-admittance.md) | 10.1109/TIA.2025.3574123 |
| 2025 | `RN4D47F6` | [Few-Shot Data-Driven Modeling of Unified Grid Tied VSCs for Multioperation Impedance Identification Based on PINN](papers/RN4D47F6-few-shot-unified-vsc-impedance-pinn.md) | 10.1109/TIE.2024.3508059 |
| 2025 | `UXCRX7BC` | [FPGA Accelerated Large-Scale State-Space Equations for Multi-Converter Systems](papers/UXCRX7BC-fpga-accelerated-large-scale-state-space-equations.md) | 10.3390/electronics14193966 |
| 2025 | `S6VU8IS7` | [Hardware-in-the-Loop Simulation of ANPC Based on Modified Predictor–Corrector Method](papers/S6VU8IS7-hardware-in-the-loop-simulation-of-anpc.md) | 10.3390/sym17122121 |
| 2025 | `ERGUNQ4T` | [Improving Accuracy of Interpolation Algorithm in EMT Simulation: A Padé Approximation and Switching Theorem Based Approach](papers/ERGUNQ4T-cao-improving-accuracy-interpolation2025.md) | — |
| 2025 | `WCL8I4BR` | [Low-Dimensional Equivalent Models and Multithreading-Based Parallel EMT Simulation Method for Multi-Converter Systems](papers/WCL8I4BR-xu-2025-low-dimensional-parallel-emt.md) | — |
| 2025 | `WK32GRFH` | [MTOF: A Novel FPGA-Based EMT Toolbox in MATLAB](papers/WK32GRFH-ma-2025-mtof-fpga-emt-toolbox.md) | 10.1109/TPWRS.2025.3535841 |
| 2025 | `I46Z825J` | [Progress and Application of Equivalent Models for Power System Simulation With Renewable Penetration: A Review](papers/I46Z825J-progress-application-equivalent2025.md) | — |
| 2025 | `AD4UYL5V` | [Scalable and Real-Time Power System Simulation Based on Heterogeneous CPU-FPGA Co-operation](papers/AD4UYL5V-yang-scalable-real-time-power2025.md) | — |
| 2025 | `5CT7KTF3` | [万兆以太网高带宽低延迟接口的 FPGA 轻量化设计：论文精读](papers/5CT7KTF3-song-2025-10gbe-fpga-interface.md) | — |
| 2024 | `KSDKQ9U8` | [An Efficient Electromagnetic Transient Modeling Method Based on Unit Division and Parallel Simulation Framework for Large-scale Photovoltaic Power Stations](papers/KSDKQ9U8-xu-efficient-electromagnetic-transient2024.md) | — |
| 2024 | `8SJQSIC8` | [Low Cost and Optimized FPGA-HIL Real Time Simulation of a Boost Converter Powered by a Photovoltaic Panel](papers/8SJQSIC8-low-cost-optimized-fpga-hil-pv-boost.md) | 10.1109/TLA.2024.10738270 |
| 2024 | `VNMA2TC9` | [电力电子换流器无延时解耦并行仿真模型](papers/VNMA2TC9-xu-ming-wang-dian-li-dian-zi-huan-liu-qi-wu-yan-shi-jie-ou-bing-xing-fang-zhen-mo-xing2024.md) | — |
| 2023 | `RJNWWZWE` | [A Novel Decoupled EMT Approach and Parallel Simulation Framework for Modularized Solid-State Transformers](papers/RJNWWZWE-feng-novel-decoupled-emt2023.md) | — |
| 2023 | `6I9KI3B7` | [An Efficient Half-Bridge MMC Model for EMTP-Type Simulation Based on Hybrid Numerical Integration](papers/6I9KI3B7-gao-efficient-half-bridge-mmc2023.md) | — |
| 2023 | `NE5PGQA4` | [An FPGA-Based Hierarchical Parallel Real-Time Simulation Method for Cascaded Solid-State Transformer](papers/NE5PGQA4-li-fpgabased-hierarchical-parallel2023a.md) | — |
| 2023 | `IIP2G4XE` | [Basics of Electromagnetic Transients: Underlying mathematics](papers/IIP2G4XE-ma-basics-electromagnetic-transients2023.md) | — |
| 2023 | `UXWRM3U7` | [Comparative Modeling and Analysis of EMT and Phasor RMS Grid-Forming Converters Under Different Power System Dynamics](papers/UXWRM3U7-favuzza-comparative-modeling-analysis2023.md) | — |
| 2023 | `CUCXEQHE` | [Detailed Parametric Modeling of AC-DC Converters for EMT Simulators](papers/CUCXEQHE-hosseinian-detailed-parametric-modeling2023a.md) | — |
| 2023 | `KDH2T488` | [Extended Discrete-State Event-Driven Hardware-in-the-Loop Simulation for Power Electronic Systems Based on Virtual-Time-Ratio Regulation](papers/KDH2T488-zeng-extended-discrete-state-event-driven2023.md) | 10.1109/JESTPE.2023.3266348 |
| 2023 | `Q5W4UKM2` | [Improved Interpolation Algorithm Accounting for Multiple Switching Actions and Reinitialization](papers/Q5W4UKM2-cao-improved-interpolation-algorithm2023.md) | — |
| 2023 | `TSXICTYN` | [MSDF-SGD：面向任意精度训练的最高有效位优先随机梯度下降](papers/TSXICTYN-song-msdfsgdmost-significant-digit-first2023.md) | — |
| 2023 | `3T22B4ZQ` | [Oversampling Techniques to Improve the Accuracy of Hardware-in-the-Loop Switching Models](papers/3T22B4ZQ-yushkova-oversampling-techniques-improve2023.md) | 10.1109/TPEL.2023.3243702 |
| 2023 | `V3X4JZ7M` | [Overview of Interface Algorithms, Interface Signals, Communication and Delay in Real-Time Co-Simulation of Distributed Power Systems](papers/V3X4JZ7M-buraimoh-2023-rt-cosimulation-interface-survey.md) | — |
| 2023 | `SKEEWQ9V` | [Portal Analysis Approach Used for the Efficient Electromagnetic Transient (EMT) Simulation of Power Electronic Systems](papers/SKEEWQ9V-gao-portal-analysis-approach2023.md) | — |
| 2023 | `CKMGIXXY` | [Real-Time HIL Emulation of DRM With Machine Learning Accelerated WBG Device Models](papers/CKMGIXXY-zhang-real-time-hilemulation2023.md) | — |
| 2023 | `PZAPQ5B3` | [Unified Real-Time Simulation Method for DC/DC Conversion Systems Consisting of Cascaded Dual-Port Submodules](papers/PZAPQ5B3-li-unified-real-time-simulation2023a.md) | — |
| 2023 | `5EF8STIQ` | [Universal Equivalent Model for Real-Time CPU/FPGA Co-Simulation of Hybrid Cascaded Multilevel Converters](papers/5EF8STIQ-bieber-2023.md) | — |
| 2023 | `3PWIK7BV` | [基于 FPGA 的电力电子系统电磁暂态实时仿真通用解算器](papers/3PWIK7BV-zhou-bin-ji-yu-fpgade-dian-li-dian-zi-xi-tong-dian-ci-zan-tai-shi-shi-fang-zhen-tong-yong-jie-suan-qi2023.md) | — |
| 2022 | `G8FRSHQ9` | [A Discrete Small-Step Synthesis Real-Time Simulation Method for Power Converters](papers/G8FRSHQ9-li-discrete-small-step-synthesis2022a.md) | — |
| 2022 | `NQV723Z7` | [A Review of Recent Best Practices in the Development of Real-Time Power System Simulators from a Simulator Manufacturer’s Perspective](papers/NQV723Z7-sidwall-review-recent-best2022.md) | — |
| 2022 | `BPS56KS3` | [An Event-Driven Parallel Acceleration Real-Time Simulation for Power Electronic Systems Without Simulation Distortion in Circuit Partitioning](papers/BPS56KS3-zheng-event-driven-parallel-acceleration2022a.md) | — |
| 2022 | `9JJGN3GT` | [An Event-Driven Real-Time Simulation for Power Electronics Systems Based on Discrete Hybrid Time-Step Algorithm](papers/9JJGN3GT-zheng-event-driven-real-time-simulation2022.md) | — |
| 2022 | `28WF29I5` | [Analysis of the aliasing effect caused in hardware-in-the-loop when reading PWM inputs of power converters](papers/28WF29I5-zamiri-2021-aliasing-effect.md) | 10.1016/j.ijepes.2021.107678 |
| 2022 | `APUJJSHA` | [Average-Value Model for Voltage-Source Converters With Direct Interfacing in EMTP-Type Solution](papers/APUJJSHA-ebrahimi-average-value-model-voltage-source2022a.md) | — |
| 2022 | `3W3VNJJR` | [Direct Interfacing of Parametric Average-Value Models of AC–DC Converters for Nodal Analysis-Based Solution](papers/3W3VNJJR-ebrahimi-direct-interfacing-parametric2022.md) | 10.1109/TEC.2022.3177131 |
| 2022 | `4D3SE52Z` | [Hardware-in-the-Loop Simulations: A Historical Overview of Engineering Challenges](papers/4D3SE52Z-mihalic-hardwareinthe-loop-simulations-historical2022a.md) | 10.3390/electronics11152462 |
| 2022 | `88NW8NQG` | [Machine Learning Based Modeling for Real-Time Inferencer-in-the-Loop Hardware Emulation of High-Speed Rail Microgrid](papers/88NW8NQG-zhang-machine-learning-based2022.md) | — |
| 2022 | `8SKXZQBK` | [Methods for the Accurate Real-Time Simulation of High-Frequency Power Converters](papers/8SKXZQBK-chalangar-methods-accurate-real-time2022.md) | — |
| 2022 | `DWXFPT5X` | [On Modeling Depths of Power Electronic Circuits for Real-Time Simulation - A Comparative Analysis for Power Systems](papers/DWXFPT5X-carne-modeling-depths-power2022.md) | — |
| 2022 | `CAQJVVPV` | [Real-Time Simulation of Power System Electromagnetic Transients on FPGA Using Adaptive Mixed-Precision Calculations](papers/CAQJVVPV-ma-2022.md) | — |
| 2022 | `JLRJ4EJB` | [半隐式延迟解耦电磁暂态并行仿真方法（一）：原理及交流分网与并行](papers/JLRJ4EJB-yao-shu-jun-ban-yin-shi-yan-chi-jie-ou-dian-ci-zan-tai-bing-xing-fang-zhen-fang-fa-yi-yuan-li-ji-jiao-liu-fen-wang-yu-bing-xing2022.md) | — |
| 2022 | `RUEIE6M9` | [电力电子设备及含电力电子设备电力系统实时仿真研究综述](papers/RUEIE6M9-xu-jin-dian-li-dian-zi-she-bei-ji-han-dian-li-dian-zi-she-bei-dian-li-xi-tong-shi-shi-fang-zhen-yan-jiu-zong-shu2022.md) | — |
| 2022 | `6ZEYBA3W` | [直驱风力发电单元的电磁暂态半隐式延迟解耦与仿真方法](papers/6ZEYBA3W-yao-shu-jun-zhi-qu-feng-li-fa-dian-dan-yuan-de-dian-ci-zan-tai-ban-yin-shi-yan-chi-jie-ou-yu-fang-zhen-fang-fa2022.md) | — |
| 2021 | `8BIZE27F` | [A Direct Mapped Method for Accurate Modeling and Real-Time Simulation of High Switching Frequency Resonant Converters](papers/8BIZE27F-chalangar-direct-mapped-method2021.md) | — |
| 2021 | `AMTY4M96` | [Accurate and Stable Hardware-in-the-Loop (HIL) Real-Time Simulation of Integrated Power Electronics and Power Systems](papers/AMTY4M96-lauss-accurate-stable-hardwareinthe-loop2021.md) | — |
| 2021 | `LX3QYBSD` | [Characterization of Time Delay in Power Hardware in the Loop Setups](papers/LX3QYBSD-guillo-sansano-characterization-time-delay2021.md) | 10.1109/TIE.2020.2972454 |
| 2021 | `2DMZSU5N` | [Comparison and Selection of Grid-Tied Inverter Models for Accurate and Efficient EMT Simulations](papers/2DMZSU5N-sano-comparison-selection-grid-tied2021.md) | — |
| 2021 | `QSWWGCX2` | [Compensation method for parallel real-time EMT studies](papers/QSWWGCX2-bruned-compensation-method-parallel2021b.md) | — |
| 2021 | `Z2ZQDR9T` | [Embedding an Electrical System Real-Time Simulator with Floating-Point Arithmetic in a Field Programmable Gate Array](papers/Z2ZQDR9T-queiroz-2021.md) | — |
| 2021 | `N9E5UDFK` | [Hardware-in-the-Loop and Digital Control Techniques Applied to Single-Phase PFC Converters](papers/N9E5UDFK-lamo-2021.md) | 10.3390/electronics10131563 |
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
| 1992 | `X39IQQMX` | [Real-time digital simulator for power system analysis on a hypercube computer](papers/X39IQQMX-taoka-realtime-digital-simulator1992a.md) | 10.1109/59.141680 |
| 1991 | `QNSJH7TM` | [Power converter simulation module connected to the EMTP](papers/QNSJH7TM-mahseredjian-power-converter-simulation1991.md) | 10.1109/59.76692 |
| 1990 | `WMRKXT92` | [A Real Time Power System Simulation Laboratory Environment](papers/WMRKXT92-foley-real-time-power1990a.md) | 10.1109/59.99392 |
| 1989 | `GKDER7DW` | [Real-time digital simulator of the electromagnetic transients of transmission lines with frequency dependence](papers/GKDER7DW-wang-realtime-digital-simulator1989a.md) | 10.1109/61.35654 |
| 1989 | `B49IQ77A` | [Suppression of Numerical Oscillations in the EMTP](papers/B49IQ77A-marti-suppression-numerical-oscillations1989.md) | 10.1109/59.193849 |
| 1974 | `BR8MRFK8` | [Computation of Electromagnetic Transients](papers/BR8MRFK8-dommel-computation-electromagnetic-transients1974a.md) | 10.1109/PROC.1974.9550 |
| 1971 | `CT8HAT9V` | [Nonlinear and Time-Varying Elements in Digital Simulation of Electromagnetic Transients](papers/CT8HAT9V-dommel-nonlinear-time-varying-elements1971.md) | 10.1109/TPAS.1971.292905 |
| 1969 | `3MTIVAU5` | [Digital Computer Solution of Electromagnetic Transients in Single- and Multiphase Networks](papers/3MTIVAU5-dommel-digital-computer-solution1969.md) | 10.1109/TPAS.1969.292459 |
| — | `HMZB9NFG` | [A High-Stability Real-Time Simulation Model for DC–AC Power Electronic Converters and Digital Twin Applications](papers/HMZB9NFG-high-stability-real-time-simulation-model.md) | — |
| — | `S2N95R33` | [A Real-Time Simulation Model with Constant Admittance Matrix for Multiple Grid-Connected Converters System](papers/S2N95R33-constant-admittance-multi-converter-rts.md) | — |
| — | `C5DJZKNP` | [ANN-Aided Data-Driven IGBT Switching Transient Modeling Approach for FPGA-Based Real-Time Simulation of Power Converters](papers/C5DJZKNP-zotero-item-1086.md) | — |
| — | `MP9ZE98M` | [Heterogeneous Real-Time Co-Emulation for Communication-Enabled Global Control of AC/DC Grid Integrated With Renewable Energy](papers/MP9ZE98M-zotero-item-941.md) | — |
| — | `E87DFKRD` | [Suppression of Chattering in the Real-Time Simulation of the Power Converter](papers/E87DFKRD-liu-suppression-chattering-real-time.md) | — |

## 维护

新增、删除或重命名卡片后运行：

```powershell
python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py"
python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py" --check
```

`README.md` 由该脚本生成；不要手工维护论文清单或固定数量。
