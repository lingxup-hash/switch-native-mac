# switch-native-mac

在 Apple Silicon Mac 上运行 Switch 游戏的原生移植工作记录、方法和工具。

这里不是通用的一键转换器，也不是完整游戏源码。不同框架的实现不同：nxnative 主要让 AArch64 游戏代码经必要的指令改写后原生执行，同时提供 Switch 系统接口兼容层和图形 API 转换；不能把它等同于“恢复完整 C++ 源码后重新编译”。

> **本仓库不含任何游戏内容。** 没有游戏文件（XCI/NSP/NCA）、没有从游戏里提取或生成的数据（RomFS、改写后的代码、着色器库）、没有存档、没有密钥。
> 所有工具都需要你用**自己合法拥有的游戏**和自己导出的 `prod.keys` 来运行。

## 从哪里开始

本仓库是方法、补丁和实验工具的集合，不是把任意 Switch 游戏一键转成 Mac 应用的通用安装器。

- **第一次使用**：[准备与使用边界](docs/入门与工具边界.md)。先选具体游戏、版本和对应上游，勿直接执行含作者绝对路径的脚本。
- **看当前成果**：[验证状态与后续事项](docs/验证状态与后续事项.md)。较晚的专项记录优先于早期完整报告，历史记录保留以便追溯。
- **旷野之息卡顿／穿模**：[性能与缓存排查](docs/旷野之息性能与缓存排查.md)。高瞬时 FPS 不代表跑动稳定，缓存预热不等于物理问题修复。
- **使用金手指**：[金手指说明](cheats/botw-trainer/README.md)。仅针对指定1.6.0原生构建，单次修改；“当前箭”是已装备箭种。
- **贡献与本地测试**：[CONTRIBUTING.md](CONTRIBUTING.md)。测试使用合成数据，不需要游戏或密钥，不配置自动付费运行任务。

## 用到的框架

| 项目 | 用途 | 许可证 |
|---|---|---|
| [seedds/nxnative](https://github.com/seedds/nxnative) | 通用 Switch → Mac/iOS 原生框架（马力欧派对、喷射战士3 用它） | MIT |
| [ly05010419/MacNativeGames](https://github.com/ly05010419/MacNativeGames) | 旷野之息、王国之泪的 Mac 原生版 | MIT |
| [c22dev/mush8](https://github.com/c22dev/mush8) | 马力欧卡丁车8 豪华版的 Mac 原生版 | GPL-3.0 |
| [REA](https://github.com/morluto/rea) + Ghidra 12.1.2 + [SwitchLoader](https://github.com/Adubbz/Ghidra-Switch-Loader) | 反汇编、反编译分析 | 各自许可证 |

## 进展一览（2026-10-23）

**当前是开发验证状态，不是全游戏兼容性声明。** 下表引用作者环境的运行记录；进入菜单、完成一场比赛与整款游戏通关分别看待。后续实验以具体提交和对应日志为准。

| 游戏 | 状态 |
|---|---|
| 超级马力欧派对 空前盛会（2.2.0） | 作者记录已启动、连续播放片头、进入角色选择；另有广场正常画面。**角色选择的 3D 预览异常**仍在排查；完整小游戏、保存重启、双手柄和体感尚未验收 |
| 喷射战士3（9.3.0） | 静态分析通过（SDK 13、无 NRO），但原版没有同屏双人、原生版没有联网，已停止 |
| 旷野之息 1.6.0 | MacNativeGames 原生版可玩；本仓库有原生金手指（13 项） |
| 王国之泪 1.2.1 | MacNativeGames 原生版；实验性金手指补丁（未完整验收） |
| 马力欧卡丁车8 豪华版 4.0.1 | mush8 原生版可玩；存档金币改写实验 |

详细过程见 [`docs/`](docs/)，尤其是 [马力欧派对移植记录](docs/马力欧派对_可行性与移植记录.md)。

## 从哪里开始

1. [马力欧派对复现指南](docs/马力欧派对_复现指南.md)：固定版本、构建顺序、诊断 profile 和启动方式。
2. [渲染排查与证据模板](docs/马力欧派对_渲染排查.md)：同场景对照、绘制调用定位及着色器验证。
3. [玩法及补丁验收清单](docs/马力欧派对_验收清单.md)：小游戏、多人、存档、影片槽位和其它游戏回归。

`tools/run/` 是作者环境的操作记录，含绝对路径，不应直接在别人的目录执行。复现指南给出了使用独立路径的命令示例；本轮文档整理没有重新构建或运行游戏。

## 目录

- `docs/` — 可行性分析、诊断过程、环境准备、完整工作报告。
- `tools/xci/` — 整合 XCI（本体+更新+DLC 同在一个安全分区）拆成 nxnative 能用的 NSP：`list_xci.py`（不需要密钥，列出安全分区）、`split_groups.py` / `split_xci.py`（历史分组脚本写 PFS0，比对文件名中的哈希前缀；详见使用边界，不能代替内容完整性验证）。
- `tools/re/` — 反汇编辅助：`nso2elf.py`（NSO → 标准 ELF，供 Ghidra/REA/capstone 用）、`elfsyms.py`（符号表、RELR、虚表还原）、`mdis.py`（带 PLT 导入名的反汇编）、`plt_callers.py`、`find_movie_calls.py`。
- `tools/run/` — 运行与诊断脚本（`DM_CTL` 自动按键截图、带窗口启动、nxnative survey）。脚本里的路径是作者本机的，用前改成自己的。
- `patches/nxnative/` — 对 nxnative 的两个补丁（见下）。
- `profiles/mario-party-jamboree/` — 马力欧派对的 Mac 诊断 profile（约 64 GiB 级别的虚拟别名区，不是物理内存需求）。
- `cheats/` — 金手指源码：旷野之息原生金手指（Swift/AppKit 界面 + Python/LLDB 后端）、旷野之息研究脚本、王国之泪 1.2.1 实验补丁（对 MacNativeGames）、马车8 金币实验记录。
- `research/` — 马车8 3.0.3 ARM32 路线调研（含对 remill 的 Thumb 提升测试补丁）、旷野之息着色器缓存补全实验。
- `examples/mush8/` — mush8 的构建清单和配置示例（路径为作者本机，`keys` 只是文件名）。

金手指实验参考过社区流传的 Atmosphere 金手指包（王国之泪 1.2.1 对应 Build ID `9B4E43650501A4D4`），那些代码作者另有其人、没有许可证声明，本仓库不转载，只放我们自己写的工具。

## 两个 nxnative 补丁（马力欧派对）

1. **`MAX_MOD` 128 → 256，Bezel 档案新布局**：派对有 3 个主模块 + 139 个 NRO，超过原来的 128 个模块槽；它的 `.bea`（文件版本 0x60000）条目改为 0x48 字节内联排列。
2. **原生纹理模式下 `GetOutputBuffer` 要归还输出槽**：SDK 的 `DecoderImpl::GetOutputBuffer` 在原生纹理模式下调用 `CopyOutputBufferToClientTextureAndRelease`，拷进纹理的同时就还槽。游戏据此把帧的槽号标为 -1、不再还；host 不还槽会让 16 个视频槽 0.27 秒占满，片头黑屏。

补丁基于 nxnative `ebe75c9` 加上 PR #89、#90、#91。完整分支在作者的 nxnative 复刻：[lingxup-hash/nxnative `jamboree-nro`](https://github.com/lingxup-hash/nxnative/tree/jamboree-nro)。

另外马力欧派对需要大虚拟地址布局：游戏在 `nninitStartup` 里 `StandardAllocator::Initialize(nullptr, 56 GiB, true)`，profile 的 `mem_alias` 要容纳它（见 `profiles/`，做法照 nxnative 文档里 Absolum / Paper Mario 的先例）。

## 许可证

本仓库自写的代码和文档按 MIT 许可证发布（见 `LICENSE`）。`patches/` 与 `cheats/totk-1.2.1/` 里的补丁针对上游项目，随上游许可证（MIT）。游戏及其内容版权归任天堂及相关权利人所有。
