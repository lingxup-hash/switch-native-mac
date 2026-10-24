from pathlib import Path
import subprocess,plistlib,time,os
root=Path('/Volumes/SwitchNative')
src=root/'Apps/Tears of the Kingdom 1.2.1.app'
dst=root/'Apps/Tears of the Kingdom 1.2.1 Cheat Test.app'
partial=dst.with_name(dst.name+'.partial')
runtime=root/'Builds/TOTK-cheat/totk/build/totk-native-v121'
assert runtime.is_file() and not dst.exists() and not partial.exists()
start=time.monotonic()
while not src.is_dir():
 if time.monotonic()-start>1800:raise RuntimeError('Normal app packaging did not finish in 30 minutes')
 time.sleep(5)
print('Normal app published; cloning validated app on APFS',flush=True)
subprocess.run(['cp','-cR',str(src),str(partial)],check=True)
exe=partial/'Contents/Resources/totk/build/totk-native'
subprocess.run(['cp','-c',str(runtime),str(exe)],check=True)
info=partial/'Contents/Info.plist'
j=plistlib.loads(info.read_bytes())
assert j['CFBundleShortVersionString']=='1.2.1'
j['CFBundleIdentifier']='org.macnativegames.totk.localcheat121'
j['CFBundleName']='Tears of the Kingdom 1.2.1 Cheat Test'
j['CFBundleDisplayName']=j['CFBundleName']
j['LSEnvironment']={
 'TOTK_LOCAL_CHEATS':str(root/'Runtime/TOTK-cheat121/cheats.conf'),
 'TOTK_PROFILE_DIR':str(root/'Runtime/TOTK-cheat121/profile'),
 'TOTK_SHADER_CONTRIB':str(root/'Runtime/TOTK-cheat121/shader-list-contribution.txt'),
 'TOTK_GAME_SLOT_DIR':str(root/'Runtime/MacNativeGames/TOTK/game-slot'),
}
info.write_bytes(plistlib.dumps(j))
print('Signing experimental runtime and outer app; keeping signed game-data bundle',flush=True)
subprocess.run(['codesign','--force','--sign','-',str(exe)],check=True)
subprocess.run(['codesign','--force','--sign','-',str(partial)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(partial)],check=True)
partial.rename(dst)
print('Experimental app ready:',dst,flush=True)
