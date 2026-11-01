from pathlib import Path
import json,os,urllib.request,urllib.error,subprocess,concurrent.futures,time,hashlib,sys
root=Path('outputs/友爱奇旅-自然语音');root.mkdir(exist_ok=True)
jobs=json.loads(Path('work/game_audio_manifest.json').read_text())
MODEL='gpt-4o-mini-tts';VOICE='coral'
DIRECTION='用标准、自然的中国大陆普通话朗读。你是一位温暖亲切的女老师，正在给一年级小朋友讲一个合作冒险故事。用轻松、自然的口语节奏，语速略慢但不要逐字顿读。句子有自然的抑扬和呼吸，问句带轻柔的提问语气；在情景结束和问题开始之间稍作停顿，让孩子有思考空间。说到欺负、害怕或求助时认真温柔，不夸张、不吓人。只朗读给出的文字，不添加任何内容。'
def generate(j):
 j=dict(j);dst=root/Path(j['file']).name;j['file']=str(dst);j['engine']=MODEL;j['voice']=VOICE
 if not dst.exists():
  payload=json.dumps(dict(model=MODEL,voice=VOICE,input=j['text'],instructions=DIRECTION,response_format='mp3',speed=.95)).encode()
  req=urllib.request.Request('https://api.openai.com/v1/audio/speech',data=payload,headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'})
  for attempt in range(3):
   try:
    with urllib.request.urlopen(req,timeout=120) as r:data=r.read()
    assert len(data)>10000
    dst.write_bytes(data);break
   except urllib.error.HTTPError as e:
    msg=e.read().decode(errors='replace')
    try:msg=json.loads(msg).get('error',{}).get('message','request failed')
    except:msg='request failed'
    if e.code in (429,500,502,503) and attempt<2:time.sleep(3*(attempt+1));continue
    raise RuntimeError(f'API HTTP {e.code}: {msg}') from None
 j['duration']=float(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(dst)]));assert j['duration']>2
 j['sha256']=hashlib.sha256(dst.read_bytes()).hexdigest();print('完成',dst.name,round(j['duration'],1),'秒',flush=True);return j
if __name__=='__main__':
 if '--sample' in sys.argv:generate(jobs[0])
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:done=list(pool.map(generate,jobs))
  Path('work/game_audio_manifest.json').write_text(json.dumps(done,ensure_ascii=False,indent=2))
  (root/'语音清单.txt').write_text('AI 生成普通话语音，非真人录音。\n模型：'+MODEL+'；音色：'+VOICE+'。\n\n'+'\n'.join(Path(j['file']).name+' — '+j['title'] for j in done))
  print('全部完成：',len(done),'段',flush=True)
