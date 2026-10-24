# Mush8 3.0.3 兼容性初查

日期：2026-10-22；源码提交 9f6e2b7c3cdbac4bde3c1878ea6978cc85476067。

已执行：
- NSZ 解压为独立 NSP，原文件保留；工具输出 NCA VERIFIED 并成功退出。
- Mush8 自带 nxfs 编译成功。
- 用 nxfs 对本地基础 NSP 与 3.0.3 更新 NSP 执行 extract，退出码 0。
- 从游戏 control.nacp 读到真实版本 3.0.3；main、sdk、subsdk0、rtld 和 main.npdm 提取成功。

源码发现：README 指定 4.0.1；Mac 启动器可选择更新文件；导入与加载路径未发现强制拒绝 3.0.3 的版本检查；nxfs 仅枚举 .nca，因此 NSZ 需要先解压。services/am.rs 的命令 23 固定返回 4.0.1，潜在适配点，尚未修改。

结论：3.0.3 通过导入阶段，不能仅凭 README 判为不兼容。但尚未验证指令改写、RomFS 合并读取、图形预编译、启动、比赛、存档或多人兼容性。

更新 NSP：/Volumes/SwitchNative/GameFiles/MK8D/update-3.0.3
提取输出：/Volumes/SwitchNative/Builds/Mush8/compat-3.0.3

## 2026-10-22 后续复核：发现阻断

3.0.3 的 main.npdm Flags0（偏移 0xC）为 0x04，Is64BitInstruction 位为 0；地址空间类型为 32-bit no-reserved。对 main 的 0x8FD7F0 附近实际代码反汇编：ARM32 可完整解码为 mov/cmp/movweq/add/pop 等，ARM64 无法解码。0x8FD7F8 原始值为 0x03000001，与 3.0.3 金手指的还原值吻合。Mush8 nxpatch/classify.rs 固定 Capstone arm64，运行架构也是直接 AArch64。

因此：导入测试通过不代表可运行；当前 Mush8 无法直接运行这份 32 位 3.0.3。应提供项目要求的 4.0.1 更新，并重新验证实际代码架构与金手指地址；不可把 3.0.3 的 ARM32 指令补丁应用到 ARM64 版。暂不扩展到新建 ARM32 翻译器。

格式参考：https://switchbrew.org/wiki/NPDM#Flags0
