# Mush8 构建结果

2026-10-22，Codex（Mac）。
来源：https://github.com/c22dev/mush8，提交 9f6e2b7c3cdbac4bde3c1878ea6978cc85476067。
应用：/Volumes/SwitchNative/Apps/Mush8.app，约 32MB。
结果：Release 构建和 Swift 启动器打包成功；codesign deep/strict 校验通过；CUA 实际打开主窗口，显示 Game data 与 Settings，未准备游戏数据时 Prepare 按钮禁用。
源码未修改。编译输出、Rust 下载缓存位于 T7。
配置目录：~/Library/Application Support/Mush8 -> /Volumes/SwitchNative/Runtime/Mush8。
准备输入目录：/Volumes/SwitchNative/GameFiles/MK8D/Mush8-input（基础游戏、prod.keys、Firmware 的本地链接；没有错误地链接 3.0.3 更新）。

选择输入目录后，CUA 读取窗口连续 timeout；尚未确认目录设置成功，已向用户询问当前窗口状态。无游戏运行或金手指验收证据。

已确认阻断：现有 3.0.3 NPDM Flags0=0x04，是 ARM32；实际 main 指令可按 ARM32 解码且与其金手指还原指令一致。Mush8 仅处理 ARM64，因此能提取文件不等于能运行。等待项目要求的 4.0.1 更新 NSP，再验证实际架构并寻找/适配该版本金手指。
