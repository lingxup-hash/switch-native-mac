# switch-native-mac

在 Apple Silicon Mac 上把 Switch 游戏做成**原生程序**（静态重编译，而不是模拟器）的工作记录、方法和工具。

> **本仓库不含任何游戏内容。** 没有游戏文件（XCI/NSP/NCA）、没有从游戏里提取或生成的数据（RomFS、改写后的代码、着色器库）、没有存档、没有密钥。
> 所有工具都需要你用**自己合法拥有的游戏**和自己导出的 `prod.keys` 来运行。

## 用到的框架

| 项目 | 用途 | 许可证 |
|---|---|---|
| [seedds/nxnative](https://github.com/seedds/nxnative) | 通用 Switch → Mac/iOS 原生框架（马力欧派对、喷射战士3 用它） | MIT |
| [ly05010419/MacNativeGames](https://github.com/ly05010419/MacNativeGames) | 旷野之息、王国之泪的 Mac 原生版 | MIT |
| [c22dev/mush8](https://github.com/c22dev/mush8) | 马力欧卡丁车8 豪华版的 Mac 原生版 | GPL-3.0 |
| [REA](https://github.com/morluto/rea) + Ghidra 12.1.2 + [SwitchLoader](https://github.com/Adubbz/Ghidra-Switch-Loader) | 反汇编、反编译分析 | 各自许可证 |

## 进展一览（2026-10-23）

| 游戏 | 状态 |
|---|---|
| 超级马力欧派对 空前盛会（2.2.0） | 用 nxnative + 社区未合并的 NRO 加载 PR（#89/#90/#91）+ 本仓库两个补丁：**能启动、播片头、进入角色选择和派对广场**；3D 场景里有大块纯色平面的渲染错误，排查中 |
| 喷射战士3（9.3.0） | 静态分析通过（SDK 13、无 NRO），但原版没有同屏双人、原生版没有联网，已停止 |
| 旷野之息 1.6.0 | MacNativeGames 原生版可玩；本仓库有原生金手指（13 项） |
| 王国之泪 1.2.1 | MacNativeGames 原生版；实验性金手指补丁（未完整验收） |
| 马力欧卡丁车8 豪华版 4.0.1 | mush8 原生版可玩；存档金币改写实验 |

详细过程见 [`docs/`](docs/)，尤其是 [马力欧派对移植记录](docs/马力欧派对_可行性与移植记录.md)。

## 目录

- `docs/` — 可行性分析、诊断过程、环境准备、完整工作报告。
- `tools/xci/` — 整合 XCI（本体+更新+DLC 同在一个安全分区）拆成 nxnative 能用的 NSP：`list_xci.py`（不需要密钥，列出安全分区）、`split_groups.py` / `split_xci.py`（按 CNMT 分组写 PFS0，逐个校验 NCA 的 SHA-256）。
- `tools/re/` — 反汇编辅助：`nso2elf.py`（NSO → 标准 ELF，供 Ghidra/REA/capstone 用）、`elfsyms.py`（符号表、RELR、虚表还原）、`mdis.py`（带 PLT 导入名的反汇编）、`plt_callers.py`、`find_movie_calls.py`。
- `tools/run/` — 运行与诊断脚本（`DM_CTL` 自动按键截图、带窗口启动、nxnative survey）。脚本里的路径是作者本机的，用前改成自己的。
- `patches/nxnative/` — 对 nxnative 的两个补丁（见下）。
- `profiles/mario-party-jamboree/` — 马力欧派对的诊断 profile（64 GB 别名区）。
- `cheats/` — 金手指源码：旷野之息原生金手指（Swift/AppKit 界面 + Python/LLDB 后端）、旷野之息研究脚本、王国之泪 1.2.1 实验补丁（对 MacNativeGames）、马车8 金币实验记录。
- `research/` — 马车8 3.0.3 ARM32 路线调研、旷野之息着色器缓存补全实验。

## 两个 nxnative 补丁（马力欧派对）

1. **`MAX_MOD` 128 → 256，Bezel 档案新布局**：派对有 3 个主模块 + 139 个 NRO，超过原来的 128 个模块槽；它的 `.bea`（文件版本 0x60000）条目改为 0x48 字节内联排列。
2. **原生纹理模式下 `GetOutputBuffer` 要归还输出槽**：SDK 的 `DecoderImpl::GetOutputBuffer` 在原生纹理模式下调用 `CopyOutputBufferToClientTextureAndRelease`，拷进纹理的同时就还槽。游戏据此把帧的槽号标为 -1、不再还；host 不还槽会让 16 个视频槽 0.27 秒占满，片头黑屏。

补丁基于 nxnative `ebe75c9` 加上 PR #89、#90、#91。完整分支在作者的 nxnative 复刻：[lingxup-hash/nxnative `jamboree-nro`](https://github.com/lingxup-hash/nxnative/tree/jamboree-nro)。

另外马力欧派对需要大虚拟地址布局：游戏在 `nninitStartup` 里 `StandardAllocator::Initialize(nullptr, 56 GiB, true)`，profile 的 `mem_alias` 要容纳它（见 `profiles/`，做法照 nxnative 文档里 Absolum / Paper Mario 的先例）。

## 许可证

本仓库自写的代码和文档按 MIT 许可证发布（见 `LICENSE`）。`patches/` 与 `cheats/totk-1.2.1/` 里的补丁针对上游项目，随上游许可证（MIT）。游戏及其内容版权归任天堂及相关权利人所有。
