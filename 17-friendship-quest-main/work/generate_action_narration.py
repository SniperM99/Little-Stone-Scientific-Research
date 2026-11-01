from pathlib import Path
import asyncio,json,subprocess,hashlib
import edge_tts
root=Path('outputs/友爱奇旅-互动解说');root.mkdir(exist_ok=True)
rows=[]
def add(i,action,text,k=None):rows.append(dict(key=f'{i}:{action}'+(f':{k}' if k is not None else ''),index=i,action=action,text=text,file=str(root/(f'{i+1:02d}-{action}'+(f'-{k+1}' if k is not None else '')+'.mp3'))))
add(0,'place','关心木板安装完成，第一段桥面修好了。再收集一块木板，就能修好木桥啦！')
add(1,'place','陪伴木板安装完成，木桥已经修好了。点击一起过桥，我们继续出发吧！')
add(1,'cross','木桥全部修好啦！小梅和科迪平安过河，下一站，积木森林！')
parts=['飞机机身积木','左机翼积木','右机翼积木','起落架积木','尾翼积木','螺旋桨积木']
for i,part in enumerate(parts,2):add(i,'place',part+'安装完成，'+('六个部件全部集齐。点击起飞，飞向纽扣森林吧！' if i==7 else '飞机越来越完整了。全班一起努力，继续收集下一个部件吧！'))
add(7,'fly','螺旋桨转起来啦！积木飞机起飞了，小梅和科迪一起飞向纽扣森林！')
add(8,'guard','左侧的护盾举起来了，挡住了偷袭。再守住右侧，伙伴们就更安全啦！',0)
add(8,'guard','右侧的护盾举起来了，挡住了偷袭。再守住左侧，伙伴们就更安全啦！',1)
# The final action can be either side, so completion clips are selected by progress rather than side.
add(8,'guard-done','两侧的护盾都举起来了！守护盾挡住了偷袭，村口的伙伴们安全啦！')
for k in range(3):add(9,'light',f'第{["一","二","三"][k]}条小路被星光照亮了。'+('三条小路都亮起来啦，狼族退远了，大家可以安全前往绳桥峡谷！' if k==2 else '继续点亮小路，让伙伴安全通过吧！'),k)
add(10,'charge','第一格电力接通啦，缆车开始苏醒。再加两格电力，我们就能出发了！')
for k in range(3):add(11,'crank',['转动第一圈，发电把手动起来了。再转两圈，继续积累电力！','转动第二圈，电力正在增加。再转一圈，就能充好第二格电啦！','第二格电力充好啦！缆车还差最后一格电，我们一起加油！'][k],k)
add(12,'charge','第三格电力充好啦！缆车已经充满电，点击乘坐缆车，我们出发去山顶吧！')
add(12,'ride','缆车出发啦！小梅和科迪一起越过峡谷，山顶的星空小屋越来越近了。')
add(12,'arrive','叮咚，到站啦！缆车平安抵达山顶，现在，我们一起建造观星树屋吧！')
for k in range(3):add(13,'floor',f'第{["一","二","三"][k]}块地板安装完成。'+('三块地板都搭好了，接下来安装屋顶和星灯吧！' if k==2 else '树屋越来越稳固了，我们继续搭下一块吧！'),k)
add(14,'roof','屋顶安装完成，星灯也亮起来了。树屋建好啦，点击一起看星星吧！')
add(14,'stars','抬头看，星空好美呀！请依次点亮关心、尊重、勇气、互助和友爱，让五颗星记住我们的约定。')
for k,t in enumerate(['关心','尊重','勇气','互助','友爱']):add(14,'star',t+'之星亮起来啦！'+['看到同学难过，主动关心他。','叫同学的名字，尊重每一位伙伴。','遇到欺负，勇敢说不，及时求助。','安全地帮助同学，一起面对困难。','让我们的班级，像家一样温暖。'][k],k)
add(14,'finish','五颗友爱之星全部点亮，树屋也建好了！小梅、科迪和全班一起欣赏星空。冒险成功，一年三班，像个大家！')
async def main():
 sem=asyncio.Semaphore(3)
 async def gen(j):
  async with sem:
   p=Path(j['file'])
   if not p.exists() or p.stat().st_size<10000:
    for attempt in range(3):
     try:await edge_tts.Communicate(j['text'],'zh-CN-XiaoxiaoNeural',rate='-8%').save(str(p));break
     except Exception:
      if attempt==2:raise
      await asyncio.sleep(2)
   j['duration']=float(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]));assert j['duration']>2
   j['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();print('完成',j['key'],flush=True);return j
 done=await asyncio.gather(*(gen(j) for j in rows))
 Path('work/action_narration_manifest.json').write_text(json.dumps(done,ensure_ascii=False,indent=2))
 (root/'语音清单.txt').write_text('AI 合成普通话解说：晓晓神经网络女声，语速 -8%。\n\n'+'\n'.join(Path(j['file']).name+'：'+j['text'] for j in done))
 print('共',len(done),'段互动音频解说',flush=True)
asyncio.run(main())
