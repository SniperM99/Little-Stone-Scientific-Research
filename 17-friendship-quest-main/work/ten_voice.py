"""Consistent Xiaoxiao neural narration for the current ten-level edition."""
from pathlib import Path
import asyncio,base64,hashlib,json,os,re,sys
ROOT=Path(__file__).resolve().parent.parent
VOICE='zh-CN-XiaoxiaoNeural'
RATE='-8%'
def manifest(s):
 def arr(name):return json.loads(re.search(r'const '+name+r'=(\[.*?\]);',s,re.S)[1])
 levels=arr('levels');stories=arr('chapterStories');goals=arr('chapterGoals')
 labels=arr('singleLabels') if 'const singleLabels=["' in s else ['放好木板','修好木桥，一起过河','安装机身与双翼','拼好飞机，起飞','举起护盾，守护伙伴','点亮全部安全小路','接通缆车电源','充满电力，乘车上山','搭好全部树屋地板','建好树屋，点亮星空']
 messages=['第一块木板装好了！','木桥修好了，小梅和科迪平安过河！','机身和双翼安装完成！','六个部件拼好了，飞机飞向纽扣森林！','两侧护盾展开，伙伴们安全了！','三条小路全部亮起，大家安全通过森林！','电源接通了，缆车开始苏醒！','电力充满，缆车平安抵达山顶！','三块地板搭好了，友爱树屋更加稳固！','屋顶和星灯亮起来，五颗友爱之星闪耀，冒险成功！']
 titles=['修好书本谷的木桥','拼出积木飞机','守住纽扣森林','让缆车重新通电','建好树屋，一起看星星']
 rows=[]
 def add(kind,i,title,text):
  digest=hashlib.sha256((VOICE+RATE+text).encode()).hexdigest()[:12]
  rows.append(dict(kind=kind,index=i,title=title,text=text,voice=VOICE,rate=RATE,file=f'outputs/友爱奇旅-10关晓晓配音/{kind}-{i:02d}-{digest}.mp3'))
 add('intro',0,'游戏介绍','同学们好，欢迎来到友爱奇旅！小梅和科迪邀请全班一起修木桥、拼积木飞机、守护纽扣森林、启动缆车，最后建树屋、看星星。五章，每章两关，一共十关。我们要学会不欺负人、理解同学，遇到困难会求助，也能安全地帮助别人。想回答先举手，别人说话认真听。揭晓答案后，由主持人判断。答错不扣星，可以再想一想。答对后，点击一次完成互动，再继续冒险。准备好了吗？我们出发！')
 for i,l in enumerate(levels):
  add('scene',i,l[1],f'第{i+1}关，{l[1]}。发生了什么？{l[2]} 请你回答。{l[3]} 请大家举手回答。')
  add('question',i,'只听问题',l[3]+' 请大家举手回答。')
  add('answer',i,'参考答案','参考答案。'+' '.join(l[8]))
  add('reward',i,'回答正确','回答正确！获得'+arr('partNames')[i]+'。')
  add('done',i,'互动完成',messages[i])
 for i,t in enumerate(stories):add('chapter',i,titles[i],f'第{i+1}章，{titles[i]}。{t} 本章两道题。'+goals[i].replace('→','，')+'。准备好后，点击进入本章任务。')
 add('pledge',0,'通关与班级承诺','树屋建好了，一起看星星！木桥、飞机、守护盾、缆车和树屋，都是全班一起完成的。谢谢每位举手、倾听、回答和帮助伙伴的同学。现在请全班一起读：一年三班，像个大家！团结友爱，不欺负他！遇到危险，离开求助！集体为家，团结向前！让我们把今天的友爱约定，带到明天的教室。')
 add('map',0,'冒险地图','冒险地图。我们依次经过书本山谷、积木森林、纽扣森林、绳桥峡谷和山顶星空小屋。五章，每章两关。完成当前互动，才能解锁下一步。关闭地图可以回到刚才的页面。')
 add('pause',0,'休息一下','我们先休息一下。现在的进度已经保存，准备好后，点击继续冒险。')
 add('reset',0,'重新开始提示','确定要重新开始吗？重新开始会清除本版当前进度。不想重来，可以关闭这个窗口继续冒险。')
 return rows

async def generate(rows):
 import edge_tts
 proxy=os.getenv('TEN_TTS_PROXY')
 if proxy is None:
  import urllib.request
  proxy=urllib.request.getproxies().get('https')
  if proxy and proxy.startswith('https://127.0.0.1:'):proxy='http://'+proxy[len('https://'):]
 sem=asyncio.Semaphore(3)
 async def one(row):
  p=ROOT/row['file'];p.parent.mkdir(exist_ok=True)
  async with sem:
   if not p.exists() or p.stat().st_size<1000:
    tmp=p.with_suffix('.tmp.mp3')
    for attempt in range(3):
     try:
      await edge_tts.Communicate(row['text'],VOICE,rate=RATE,proxy=proxy).save(str(tmp))
      assert tmp.stat().st_size>1000
      tmp.replace(p);break
     except Exception:
      if attempt==2:raise
      await asyncio.sleep(2)
   print('Ready',row['kind'],row['index'],flush=True)
 await asyncio.gather(*(one(row) for row in rows))

def add_ten_voice(s,make=False):
 rows=manifest(s)
 (ROOT/'work/ten_neural_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 if make:asyncio.run(generate(rows))
 clips={}
 for row in rows:
  p=ROOT/row['file'];assert p.exists() and p.stat().st_size>1000, f'Missing narration: {p}; run python work/build_ten_levels.py --generate-voice'
  clips.setdefault(row['kind'],{})[str(row['index'])]={'title':row['title'],'text':row['text'],'src':'data:audio/mpeg;base64,'+base64.b64encode(p.read_bytes()).decode()}
 script='const tenVoiceClips='+json.dumps(clips,ensure_ascii=False)+';\n'+(ROOT/'work/ten_voice.js').read_text(encoding='utf-8')
 assert s.count('\nrender();\n</script>')==1
 return s.replace('\nrender();\n</script>','\n'+script+'\nrender();\n</script>')
