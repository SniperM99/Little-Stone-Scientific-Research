from pathlib import Path
import re,json,subprocess,concurrent.futures,hashlib
root=Path('outputs/友爱奇旅-语音');root.mkdir(exist_ok=True)
scratch=Path('work/game-audio');scratch.mkdir(exist_ok=True)
html=Path('outputs/友爱奇旅-微缩冒险闯关游戏.html').read_text()
src=Path('work/story_minigames.js').read_text()
def arr(name,source):return json.loads(re.search(r'const '+name+r'=(\[.*?\]);',source,re.S).group(1))
levels=arr('levels',html);stories=arr('plotLines',src);questions=arr('levelQuestions',src);chapters=arr('chapterStories',src)
nums=['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五']
jobs=[]
for i,l in enumerate(levels):
    title=l[1]
    for kind,text,label in [('scene',f'第{nums[i]}关，{title}。发生了什么？{stories[i]} 请你回答：{questions[i]}','情景与问题'),('question',f'请你回答。{questions[i]}','问题'),('answer','参考答案。'+' '.join(l[8])+' 意思合理就可以，不用一字不差。','参考答案')]:
        jobs.append({'kind':kind,'index':i,'title':title,'text':text,'file':str(root/f'{i+1:02d}-{label}.mp3')})
for i,t in enumerate(chapters):jobs.append({'kind':'chapter','index':i,'title':f'第{nums[i]}章剧情','text':f'第{nums[i]}章。'+t,'file':str(root/f'章节{i+1:02d}-故事.mp3')})
jobs.extend([
 {'kind':'intro','index':0,'title':'游戏介绍','text':'欢迎来到友爱奇旅！小梅和科迪邀请一年三班的小朋友一起冒险。我们要修好木桥，拼好积木飞机，守住纽扣森林，给缆车充电，最后建好树屋，一起看星星。游戏有五章故事，十五道问题。每一关，请先看图、听问题，再举手。小石头会请一位同学回答。回答完毕，一起揭晓参考答案，再由小石头判断。答对后，全班获得奖励，一起完成小互动，就能继续前进。我们的目标是：不欺负同学，遇到困难会求助，也能安全地帮助别人。准备好了吗？一起出发吧！','file':str(root/'00-游戏介绍.mp3')},
 {'kind':'pledge','index':0,'title':'一年三班集体承诺','text':'请一年三班的小朋友，一起大声读。 一年三班，像个大家！团结友爱，不欺负他！遇到欺凌，大声说不！集体为家，团结向前！','file':str(root/'集体承诺-一年三班.mp3')}
])
def generate(j):
    tag=f"{j['kind']}-{j['index']:02d}";txt=scratch/(tag+'.txt');aiff=scratch/(tag+'.aiff');fp=Path(j['file'])
    if fp.exists() and txt.exists() and txt.read_text()==j['text']:return j
    txt.write_text(j['text'])
    subprocess.run(['/usr/bin/say','-v','Tingting','-r','175','-f',str(txt),'-o',str(aiff)],check=True,capture_output=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(aiff),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1','-codec:a','libmp3lame','-b:a','64k',str(fp)],check=True,capture_output=True)
    probe=subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(fp)],check=True,capture_output=True,text=True)
    j['duration']=round(float(probe.stdout.strip()),2);j['sha256']=hashlib.sha256(fp.read_bytes()).hexdigest()
    assert j['duration']>2 and fp.stat().st_size>10000
    return j
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    done=list(pool.map(generate,jobs))
Path('work/game_audio_manifest.json').write_text(json.dumps(done,ensure_ascii=False,indent=2))
notes='友爱奇旅普通话语音清单\n使用本机 Tingting 普通话女声生成，语速 175；语音已内嵌在游戏 HTML，可离线播放。\n\n'
notes+='\n'.join(f"{Path(j['file']).name} — {j['title']}" for j in done)
(root/'语音清单.txt').write_text(notes)
print(f"完成 {len(done)} 段普通话语音，总大小 {sum(Path(j['file']).stat().st_size for j in done)/1024/1024:.1f} MB。")
