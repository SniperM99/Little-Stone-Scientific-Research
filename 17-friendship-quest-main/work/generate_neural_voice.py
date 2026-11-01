from pathlib import Path
import asyncio,edge_tts,json,subprocess,hashlib
root=Path('outputs/友爱奇旅-自然语音');root.mkdir(exist_ok=True)
jobs=json.loads(Path('work/game_audio_manifest.json').read_text())
async def main():
 sem=asyncio.Semaphore(3)
 async def make(j):
  async with sem:
   j=dict(j);p=root/Path(j['file']).name
   if not p.exists() or p.stat().st_size<10000:
    for attempt in range(3):
     try:
      await edge_tts.Communicate(j['text'],'zh-CN-XiaoxiaoNeural',rate='-8%').save(str(p));break
     except Exception:
      if attempt==2:raise
      await asyncio.sleep(2)
   j['duration']=float(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]));assert j['duration']>2
   j['file']=str(p);j['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();j['engine']='Microsoft neural TTS';j['voice']='zh-CN-XiaoxiaoNeural';print('完成',p.name,flush=True);return j
 done=await asyncio.gather(*(make(j) for j in jobs))
 Path('work/game_audio_manifest.json').write_text(json.dumps(done,ensure_ascii=False,indent=2))
 (root/'语音清单.txt').write_text('AI 合成普通话女声，非真人录音。晓晓神经网络语音，语速 -8%。语音已嵌入游戏，可离线播放。\n\n'+'\n'.join(Path(j['file']).name+' — '+j['title'] for j in done))
 print('全部完成',len(done),flush=True)
asyncio.run(main())
