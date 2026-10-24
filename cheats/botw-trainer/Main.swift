import AppKit

final class Controller: NSObject, NSApplicationDelegate {
 var window:NSWindow!
 let status=NSTextField(labelWithString:"正在检查游戏…")
 let result=NSTextField(wrappingLabelWithString:"先载入存档，再选择功能。装备和箭数量操作前请打开背包。")
 let picker=NSPopUpButton(frame:.zero,pullsDown:false)
 var actionButtons:[NSButton]=[]
 var busy=false
 let entries:[(String,String)]=[
 ("materials","已有材料补到 999 · 苹果实测通过"),
 ("rupees","卢比设为 999999 · 已确认显示"),
 ("health","生命恢复至 120（30心）· 已确认显示"),
 ("arrows","当前箭补到 999 · 数量读写已验证"),
 ("weapon_dur","当前武器高耐久 · 数值已验证"),
 ("bow_dur","当前弓高耐久 · 数值已验证"),
 ("shield_dur","当前盾高耐久 · 数值已验证"),
 ("weapon_attack","当前武器攻击力 +999 · 已确认显示"),
 ("shield_boost","当前盾强化 · 已确认显示"),
 ("bow_attack","弓攻击力 +999 · 已确认显示"),
 ("bow_fast_attack","弓速射 +10000 攻击 · 加伤已确认"),
 ("bow_fast","弓速射 · 已确认词条"),
 ("bow_five","弓五连发 +5 攻击 · 已确认显示")]
 func applicationDidFinishLaunching(_ notification:Notification){
  NSApp.setActivationPolicy(.regular)
  let menu=NSMenu();let item=NSMenuItem();menu.addItem(item);let sub=NSMenu();sub.addItem(withTitle:"退出金手指",action:#selector(NSApplication.terminate(_:)),keyEquivalent:"q");item.submenu=sub;NSApp.mainMenu=menu
  window=NSWindow(contentRect:NSRect(x:0,y:0,width:580,height:420),styleMask:[.titled,.closable,.miniaturizable],backing:.buffered,defer:false)
  window.title="旷野之息金手指";window.center();window.isReleasedWhenClosed=false
  let stack=NSStackView();stack.orientation = .vertical;stack.alignment = .leading;stack.spacing=18;stack.translatesAutoresizingMaskIntoConstraints=false
  let content=window.contentView!;content.addSubview(stack)
  NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo:content.leadingAnchor,constant:28),stack.trailingAnchor.constraint(equalTo:content.trailingAnchor,constant:-28),stack.topAnchor.constraint(equalTo:content.topAnchor,constant:28)])
  let title=NSTextField(labelWithString:"旷野之息 · 金手指");title.font = .systemFont(ofSize:24,weight:.semibold);stack.addArrangedSubview(title)
  status.font = .systemFont(ofSize:13);status.textColor = .secondaryLabelColor;stack.addArrangedSubview(status)
  picker.addItems(withTitles:entries.map{$0.1});picker.translatesAutoresizingMaskIntoConstraints=false;picker.widthAnchor.constraint(equalToConstant:524).isActive=true;stack.addArrangedSubview(picker)
  let row=NSStackView();row.orientation = .horizontal;row.spacing=10
  for (name,sel) in [("执行所选功能",#selector(apply)),("检查目标",#selector(inspect)),("恢复本次修改",#selector(restore))] {
   let b=NSButton(title:name,target:self,action:sel);b.bezelStyle = .rounded;row.addArrangedSubview(b);actionButtons.append(b)
  }
  stack.addArrangedSubview(row)
  result.font = .systemFont(ofSize:14);result.maximumNumberOfLines=4;result.widthAnchor.constraint(equalToConstant:524).isActive=true;result.heightAnchor.constraint(greaterThanOrEqualToConstant:65).isActive=true;stack.addArrangedSubview(result)
  let note=NSTextField(wrappingLabelWithString:"单次修改，不是持续锁定。四种弓效果互斥，选择新效果会替换旧效果。\n恢复仅适用于当前游戏进程、原装备；不撤销已保存的存档。")
  note.font = .systemFont(ofSize:12);note.textColor = .secondaryLabelColor;note.widthAnchor.constraint(equalToConstant:524).isActive=true;stack.addArrangedSubview(note)
  let bottom=NSStackView();bottom.orientation = .horizontal;bottom.spacing=12
  bottom.addArrangedSubview(NSButton(title:"打开游戏（兼容测试）",target:self,action:#selector(openGame)))
  bottom.addArrangedSubview(NSButton(title:"刷新状态",target:self,action:#selector(refresh)))
  stack.addArrangedSubview(bottom)
  window.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true);refresh()
 }
 func applicationShouldTerminateAfterLastWindowClosed(_ sender:NSApplication)->Bool{true}
 func run(_ action:String){
  guard !busy else {return};busy=true
  actionButtons.forEach{$0.isEnabled=false};picker.isEnabled=false
  let code=entries[max(0,picker.indexOfSelectedItem)].0
  if action != "status" {result.stringValue="处理中，游戏可能短暂停顿…"}
  DispatchQueue.global(qos:.userInitiated).async {
   var message="";var ok=false
   do {
    let process=Process();process.executableURL=URL(fileURLWithPath:"/opt/homebrew/bin/python3.14")
    let script=Bundle.main.resourceURL!.appendingPathComponent("bridge.py").path
    process.arguments=[script,action,code]
    var env=ProcessInfo.processInfo.environment;env["PYTHONDONTWRITEBYTECODE"]="1";process.environment=env
    let pipe=Pipe();process.standardOutput=pipe;process.standardError=pipe
    try process.run();let data=pipe.fileHandleForReading.readDataToEndOfFile();process.waitUntilExit()
    if let j=try JSONSerialization.jsonObject(with:data) as? [String:Any]{message=j["message"] as? String ?? "未返回结果";ok=j["ok"] as? Bool ?? false}
    else {message="工具未返回有效结果，请查看本地日志"}
   } catch {message=error.localizedDescription}
   DispatchQueue.main.async {
    self.busy=false;self.actionButtons.forEach{$0.isEnabled=true};self.picker.isEnabled=true
    if action == "status" {self.status.stringValue=message}
    else {self.result.stringValue=message;self.result.textColor=ok ? .labelColor : .systemRed}
   }
  }
 }
 @objc func apply(){run("apply")}
 @objc func inspect(){run("inspect")}
 @objc func restore(){run("restore")}
 @objc func refresh(){run("status")}
 @objc func openGame(){
  let config=NSWorkspace.OpenConfiguration();config.environment=["TOTK_RENDER_STREAM":"0"]
  NSWorkspace.shared.openApplication(at:URL(fileURLWithPath:"/Volumes/SwitchNative/Apps/Breath of the Wild.app"),configuration:config){_,error in
   DispatchQueue.main.async {self.result.stringValue=error?.localizedDescription ?? "已打开兼容测试模式。载入存档后请打开背包，再执行功能。";self.refresh()}
  }
 }
}
let delegate=Controller();NSApplication.shared.delegate=delegate;NSApplication.shared.run()
