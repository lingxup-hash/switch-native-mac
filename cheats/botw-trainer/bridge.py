import sys,os,json,subprocess,fcntl,uuid,shutil,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/Volumes/SwitchNative/Runtime/BotWTrainer');ROOT.mkdir(exist_ok=True)
SRC=Path(__file__).parent
EXE='/Volumes/SwitchNative/Apps/Breath of the Wild.app/Contents/Resources/totk/build/totk-native'
def game():
 rows=subprocess.check_output(['/bin/ps','-axo','pid=,command='],text=True).splitlines()
 found=[]
 for row in rows:
  parts=row.strip().split(None,1)
  if len(parts)==2 and parts[1].startswith(EXE+' rewritten/botw160 boot'):found.append(int(parts[0]))
 if len(found)!=1:raise ValueError('请先打开旷野之息 1.6.0，并载入存档')
 pid=found[0];start=subprocess.check_output(['/bin/ps','-p',str(pid),'-o','lstart='],text=True).strip()
 return pid,start
def main():
 action=sys.argv[1] if len(sys.argv)>1 else 'status';code=sys.argv[2] if len(sys.argv)>2 else ''
 if action not in ('status','inspect','apply','restore'):raise ValueError('未知操作')
 from core import CASES,atomic_backup
 if action in ('inspect','apply') and code not in CASES:raise ValueError('未知功能')
 pid,start=game()
 if action=='status':return {'ok':True,'message':f'游戏已运行 · 1.6.0（进程 {pid}）'}
 lock=(ROOT/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 nonce=uuid.uuid4().hex;result=ROOT/(nonce+'.result.json')
 request={'action':action,'code':code,'pid':pid,'start':start,'result':str(result),'root':str(ROOT)}
 req=ROOT/(nonce+'.request.json');req.write_text(json.dumps(request));req.chmod(0o600)
 if action=='apply':
  backup=ROOT/('profile-backup-'+str(pid)+'-'+hashlib.sha256(start.encode()).hexdigest()[:12])
  atomic_backup('/Volumes/SwitchNative/Runtime/MacNativeGames/BotW/profile',backup)
 env=os.environ.copy();env['BOTW_TRAINER_REQUEST']=str(req);env['PYTHONDONTWRITEBYTECODE']='1'
 cmd=['/usr/bin/xcrun','lldb','-b','-p',str(pid),'-o','command script import '+str(SRC/'debugger.py'),'-o','detach','-o','quit']
 log=ROOT/(nonce+'.lldb.log')
 with log.open('w') as f:
  subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=45)
 if not result.exists():raise ValueError('连接游戏失败，请查看本地日志；未确认修改成功')
 return json.loads(result.read_text())
try:print(json.dumps(main(),ensure_ascii=False))
except Exception as e:print(json.dumps({'ok':False,'message':str(e)},ensure_ascii=False));sys.exit(1)
