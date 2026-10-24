# MacNativeGames 编译准备

日期：2026-10-22
来源：https://github.com/ly05010419/MacNativeGames.git
源码：/Volumes/SwitchNative/Projects/MacNativeGames
提交：d655ee4474baccb55c87160f0f0a0eaed25d0189
下载方式：浅克隆当前分支，保留完整当前源码，不包含全部历史。
验证：工作区干净；build_app.py --help 通过；项目 prerequisites 检查通过。

## 下一步输入

将自己的王国之泪基础游戏 XCI 或 NSP 放入 /Volumes/SwitchNative/GameFiles/TOTK。
自己的 prod.keys 保存在本地，仅提供路径，不在聊天里贴密钥内容。
更新包可选；NSP 或缺少系统分区的 XCI 还需自己的固件字体来源。
拿到实际文件路径后，按游戏版本确认构建参数。

## 构建位置

--work /Volumes/SwitchNative/Builds/TOTK
-o "/Volumes/SwitchNative/Apps/Tears of the Kingdom.app"
开始前加载 source /Volumes/SwitchNative/Tools/switch-env.sh。
项目会在构建过程中建立环境、安装锁定的 Python 依赖并下载锁定的工具源码。
运行时上游默认把存档、着色器缓存和日志写入用户 Library；首次运行前需配置或迁移到 T7，以满足本项目存储约定。

当前仅完成源码下载和编译前检查，没有导入游戏、编译游戏或运行游戏。
