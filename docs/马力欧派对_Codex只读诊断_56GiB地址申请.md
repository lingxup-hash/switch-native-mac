# Mario Party Jamboree：只读诊断

2026-10-23。核查工作树 /Volumes/SwitchNative/Projects/nxnative-jamboree，HEAD 8ed1771；检查前后git工作区均无未提交改动。本轮未改代码/profile，未构建、启动游戏、运行测试或连接调试器。只读取现有源文件、日志、NSO/NPDM，并在内存中解压与反汇编main；未读取密钥内容。

## 当前卡点

Mac host和游戏改写产物已经构建。139个NRO已预映射，但这不等于139个模块已完成按需加载、重定位与初始化验证。最近boot1_2025.log在nninitStartup主动nn::diag abort，尚未进入nnMain/菜单。根目录可行性报告开头的“未构建未启动”是早期段落，后面的20:50记录和真实日志已更新为构建成功、启动中止。

## 新的静态证据：56GiB地址申请对4.375GiB区域

目标main Build ID d70ce1726c979e45ed4200e9c2b23b2a，游戏2.2.0。

- main+0x98282c调用PLT 0x144dd10；按JMPREL/GOT/dynsym解析为nn::os::IsVirtualAddressMemoryEnabled()。
- true分支main+0x982840加载0xe00000000，即56GiB；0x982848写入启动参数结构。
- 0x98285c进入0x98254c；后者+0x982598将结构+0x20的大小读入x1，+0x98259c进入0x982968。
- +0x982978令x1=null，+0x982980把大小移入x2；+0x982984进入0x9829ac，后者置w3=1，跳到PLT 0x144dd60。
- 0x144dd60按导入重定位表解析为nn::mem::StandardAllocator::Initialize(void*, size_t, bool)。因此此路径是Initialize(nullptr, 56GiB, true)，不是仅凭大常量猜测。
- 日志的main+0x982988、+0x9825a0、+0x982860恰是这条调用链的返回地址，和上述路径吻合。
- NPDM offset0x14实际为0x1000000，即16MiB系统资源；profile sys_resource同样16MiB。hle_svc.c的GetInfo(SysResTotal)按该值回答，因此走虚拟地址模式与文件声明一致，不能直接认定GetInfo返回错。
- 临时profile：mem_reserve=0x140000000（5GiB），mem_alias=0x118000000（4.375GiB），mem_stack=0x10000000。hle_svc.c第40–42行直接按这些值切分区域。

判断：56GiB虚拟地址请求无法容纳在4.375GiB alias区域内，是当前断言的强证据解释；尚未在修改后的运行对照中证实排除所有其它问题。虚拟地址预留不等于实际占用56GiB物理内存。

另有main+0x9829c0附近的16GiB临时AllocateAddressRegion/AllocateMemoryPages/FreeMemoryPages/FreeAddressRegion路径。应观察其返回结果和生命周期，不能把16GiB与56GiB直接相加成常驻内存需求。

## 建议Claude按顺序验证（本轮未执行）

1. 先确认仍是以上Build ID及代码路径；若Claude已换版本，不能复用偏移。
2. 单独的Mac诊断profile扩大虚拟地址布局，使alias至少容纳56GiB加SDK节点管理与对齐余量；64GiB级别可作为试验量级，mem_reserve必须同步扩大并给stack/heap留空间。不要只增alias而总reserve不变，也不要把物理app_pool伪报为64GiB。仓库docs/agents/03-bringup.md的Absolum和Paper Mario段落已有大虚拟区域诊断先例。
3. 只增量重建受profile影响的host并短启动观察（由Claude安排）：是否越过此断言、进入nnMain，AllocateAddressRegion的请求/结果、MapPhysicalMemory的实际承诺量、峰值内存。当前3个着色器失败不需要为这个CPU启动断言反复全量重编。
4. 若扩大虚拟地址后越过此点，再评估正式方案：Mac保留大虚拟布局，或按实际使用范围做build-ID限定的分配器容量/SDK节点与对齐适配。不要直接绕过断言，也不要未经验证把sys_resource改0去强迫另一条路径；本游戏NPDM确实声明非零。
5. 原位修复应由Claude负责，我不在其工作树另做补丁。适配通过此点后，再验证boot.nro/menu.nro及小游戏NRO真实LoadModule、符号绑定、构造函数、卸载和反复进出场景。

## 后续独立风险

- 着色器25693个中25690成功、3个失败。dmsh_build.log明确原因：SPIRV-Cross的Subgroup builtins不支持当前函数类型。需定位这3个着色器实际stage/入口上下文，再决定合法降级或翻译器适配；不能只忽略错误。当前还没到能证明它们影响哪个画面的阶段。
- 日志有纹理查询默认回答与未识别绑定类型，进入渲染后需按实际画面定位，不能拿着色器产物数量证明画面正确。
- SDK17.5.9、NRO运行时、影片模块、手柄/体感及多人输入仍需真实验收；“全部导入组合未出现过”不等于1260个导入都需要新增实现。
- 补丁Program NCA整体哈希不符的原因仍未确定。提取和运行到启动逻辑不是完整文件验证，不能声称输入已完全无损。

## 关键证据位置

- Tools/MarioPartyJamboree/boot1_2025.log
- Tools/MarioPartyJamboree/build_mac_2025.log
- GameFiles/MarioPartyJamboree/0100965017338000_build/profile/0100965017338000/game.tsv
- GameFiles/MarioPartyJamboree/0100965017338000_build/logs/dmsh_build.log
- Projects/nxnative-jamboree/dm/host/hle_svc.c:40–42、279–295
- Projects/nxnative-jamboree/docs/agents/03-bringup.md:61、75、78、247

以上路径均相对于 /Volumes/SwitchNative/。结论是有具体可验证的解决路线，不是已修复或保证整款游戏可玩。
