"""Build the standalone ten-level edition without changing the fifteen-level source."""
from pathlib import Path
import json,re,base64,sys
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'
def dumps(x): return json.dumps(x,ensure_ascii=False)
s=(OUT/'友爱奇旅-微缩冒险闯关游戏.html').read_text(encoding='utf-8')
def get(name): return json.loads(re.search(r'const '+name+r'=(.*?);\n',s,re.S)[1])
def put(name,value):
 global s
 s=re.sub(r'const '+name+r'=.*?;\n',lambda m:'const '+name+'='+dumps(value)+';\n',s,count=1,flags=re.S)
old=get('levels'); selection=[0,2,3,4,5,6,12,11,13,14]
levels=[old[i] for i in selection]
for i,l in enumerate(levels):l[0]=i//2
# One concrete question per scene, with short child-facing example answers.
copy=json.loads((ROOT/'work/ten_level_copy.json').read_text(encoding='utf-8'))
assert len(copy)==10
for level,row in zip(levels,copy):
 for index,key in [(1,'title'),(2,'story'),(3,'question'),(4,'judge'),(5,'hint'),(8,'answers')]:level[index]=row[key]
put('levels',levels)
put('levelImages',[get('levelImages')[i] for i in selection])
put('themes',['关心与分辨','尊重与接纳','安全与信任','求助与守护','约定与行动'])
s=s.replace("KEY='friendship-story-adventure-v3'","KEY='friendship-ten-levels-v1'")
s=s.replace('const chapterStarts=[0,2,8,10,13];','const chapterStarts=[0,2,4,6,8];')
stories=['小梅和科迪来到书本山谷，木桥缺了两段。全班学会关心同学、分辨行为，完成两次任务，收集两块木板，一起修好木桥。','过了木桥，我们来到积木森林。完成尊重名字、邀请伙伴两次任务，每次获得三个部件，拼出六部件飞机，飞向纽扣森林。','飞机降落在纽扣森林。全班学会远离危险、不替伤害保密，获得守护盾和星光法杖，守住村庄的安全通道。','小梅和科迪来到绳桥峡谷，缆车没有电。我们先学会安全地帮助同学，接通电源，再学会继续求助，充满电力，乘缆车上山。','山顶就在眼前！全班说出明天能做到的友爱约定，搭建树屋，再回顾安全行动，装上屋顶和星灯，点亮五颗友爱之星。']
goals=['两次任务 → 两块木板 → 修桥过河','两组部件，每组三个 → 拼好飞机 → 起飞','守护盾 → 星光法杖 → 安全通过森林','接通电源 → 充满电力 → 乘缆车上山','搭建树屋 → 点亮星空 → 全班约定']
parts=['关心木板','分辨木板','机身与双翼组件','起落架、尾翼与螺旋桨组件','守护盾','星光法杖','缆车电源','缆车满格电力','树屋地板','树屋屋顶与星灯']
for name,val in [('chapterStories',stories),('chapterGoals',goals),('partNames',parts)]:
 s=re.sub(r'const '+name+r'=\[.*?\];',lambda m:'const '+name+'='+dumps(val)+';',s,count=1,flags=re.S)
s=re.sub(r'levels.forEach\(\(l,i\)=>\{l\[2\]=plotLines\[i\];l\[3\]=levelQuestions\[i\];\}\);','',s)
s=re.sub(r'const plotLines=\[.*?\];\s*const levelQuestions=\[.*?\];','',s,flags=re.S)
# Adapt the original rich interactive scenes to two tasks per chapter.
a=s.index('function titleForTask()');b=s.index('function chapterOpening()',a)
s=s[:a]+"function titleForTask(){const r=levels[state.index][0],n=chapterLocal();return r===0?'把木板装到桥上':r===1?'安装三个飞机部件':r===2?n===0?'举起守护盾':'点亮安全小路':r===3?n===0?'接通缆车电源':'充满电力，乘缆车上山':n===0?'搭好树屋地板':'装好屋顶，点亮星空'}\n"+s[b:]
a=s.index('function paintStoryMini()');b=s.index('function miniComplete(',a)
mini=s[a:b]
mini=mini.replace('planeSVG(installed)','planeSVG(installed*3)').replace('${installed} / 6','${installed*3} / 6').replace('n===5','n===1').replace('n<5','n<1')
mini=mini.replace('const power=n+(mini.placed?1:0)','const power=n===0?(mini.placed?1:0):(mini.placed?3:1)')
mini=mini.replace("转动发电把手 ${mini.turns} / 3","转动把手，充满电力 ${mini.turns} / 2")
mini=mini.replace('n===2','n===1').replace('mini.turns===3','mini.turns===2')
mini=mini.replace("return miniComplete('第二格电力充好，缆车还差最后一格电。')","paintStoryMini();return")
mini=mini.replace('第一格电力接通，缆车开始苏醒。','电源已经接通，下一关继续充满电力。')
s=s[:a]+mini+s[b:]
s=s.replace('5 章连续剧情 · 15 道题','5 章连续剧情 · 10 道题').replace('35～45 分钟','25～30 分钟').replace('<title>','<title>10关精简版 · ',1)
# Silent edition: remove narration modules and synthesis while preserving animation.
a=s.index('const voiceClips=');b=s.index('// Scale the complete scene',a)
s=s[:a]+s[b:]
a=s.index('// Offline sound design');b=s.index('function effectsMotion()',a)
s=s[:a]+"""let effectsToken=0,effectsBusy=false,effectsTimer=0,effectsSnapshot=null;
function stopEffects(){effectsToken++;effectsBusy=false;clearTimeout(effectsTimer);document.querySelectorAll('.fx-overlay,.fx-particles,.fx-action-label').forEach(e=>e.remove());document.querySelectorAll('.fx-busy').forEach(e=>e.classList.remove('fx-busy'))}
"""+s[b:]
s=s.replace('playActionSound(action,r,state.build===2);','')
a=s.index("let controls=$('mini-effects');");b=s.index("animateEffect($('mini-play')",a)
s=s[:a]+s[b:]
s=s.replace('小石头','许牧宸').replace('遇到欺凌，大声说不！','遇到危险，离开求助！')
s=s.replace('onclick="closeDialog(\'mini-dialog\')">回到关卡，继续冒险 →', 'onclick="continueAfterMini()">${state.index===TOTAL-1?\'完成冒险，查看通关\':\'下一题\'} →')
s=s.replace('function miniComplete(message)', "function continueAfterMini(){if(state.phase!=='reward'||state.build!==2)return;closeDialog('mini-dialog');next()}\nfunction miniComplete(message)")
assert not any(x in s for x in ['data:audio','new Audio','AudioContext','speechSynthesis','小石头'])
a=s.index('let effectsToken=');b=s.index('// Scale the complete scene',a)
s=s[:a]+(ROOT/'work/ten_single_click.js').read_text(encoding='utf-8')+'\n'+s[b:]
s=s.replace('</style>', '''
.single-scene{position:relative;min-height:270px;overflow:hidden;border-radius:12px}
.single-scene>svg{display:block;width:100%;height:270px}
.single-guards{display:flex;justify-content:center;gap:60px;padding:30px}.single-guards svg{width:115px;height:130px}
.single-lights{font-size:48px;color:#ffe7a3;display:flex;justify-content:center;gap:55px;padding:35px 0}
.single-cable{height:140px;border-top:4px solid #dac896;margin:35px 30px 0;text-align:left}.cable-car{display:inline-block;font-size:85px;margin-left:5%}.single-cable.arrived .cable-car{margin-left:72%;transition:none}
</style>''')
from ten_voice import add_ten_voice
s=add_ten_voice(s,make='--generate-voice' in sys.argv)
s=s.replace('</style>', '''
#ten-voice-toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:#173e35;color:#f7e7b8;border:1px solid #a5baa966;border-radius:12px;padding:10px 16px;margin-bottom:12px}
#ten-voice-toolbar button,.ten-voice-controls button,.ten-question-voice button{font-size:14px;padding:6px 11px}
#ten-voice-toolbar button{background:#e9dfbf;color:#25483c;border-color:#cdbb8d}
.ten-voice-controls{display:flex;align-items:center;flex-wrap:wrap;gap:8px}.ten-voice-controls span{font-size:13px;margin-right:auto}.ten-voice-controls button:disabled{opacity:.4}
#ten-voice-toolbar>.ten-voice-controls{flex:1}#ten-voice-auto[aria-pressed=true]{background:#edcf85;color:#23483b}
.ten-question-voice{display:flex;gap:10px;margin:8px 0 12px}#ten-mini-voice{padding:10px;border-top:1px solid #b4a174;margin-top:8px}
</style>''')
(OUT/'友爱奇旅-10关精简版.html').write_text(s,encoding='utf-8')
print('Built voiced ten-level edition hosted by 许牧宸')
