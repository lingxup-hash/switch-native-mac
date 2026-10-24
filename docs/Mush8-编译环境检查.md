# Mush8 编译环境检查

日期：2026-10-22
源码：https://github.com/c22dev/mush8
本地：/Volumes/SwitchNative/Projects/Mush8
提交：9f6e2b7c3cdbac4bde3c1878ea6978cc85476067
当前源码浅克隆；工作区未修改。

环境：Rust/Cargo 1.99.0（复用现有安装），CMake 4.4.4、pkgconf 3.0.10（本次安装），Xcode 27.2 Beta 2，Metal 工具链已安装。
验证：cargo fetch --locked 成功；cargo check --locked --offline --workspace 成功；Mac Launcher.swift 类型检查成功。
日志：/Volumes/SwitchNative/Builds/Mush8/logs
项目环境：source /Volumes/SwitchNative/Tools/mush8-env.sh
Rust 下载缓存：/Volumes/SwitchNative/Cache/cargo
检查产物：/Volumes/SwitchNative/Builds/Mush8/target

官方 make-app.sh 固定从源码内 target/release 复制程序。后续打包时需将 CARGO_TARGET_DIR 临时设为源码目录/target，或在独立工作目录安排同等路径，不能直接使用外部 target 设置运行该脚本。

状态边界：已具备 Mac 编译环境并通过源码检查；尚未完成 release 链接、应用打包或游戏运行验证。
游戏输入需要自己的基础 NSP、4.0.1 更新 NSP、prod.keys 和 Firmware；DLC 可选。现有固件只验证过 MacNativeGames 字体，Mush8 的 Mii 数据尚未验证。
