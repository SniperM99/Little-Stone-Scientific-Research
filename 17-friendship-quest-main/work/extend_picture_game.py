from pathlib import Path
import runpy,json,re
m=runpy.run_path('work/build_picture_game.py')
levels=m['levels'];html=m['html']
new=[
[1,'打人推搡，不是游戏','有同学故意打人、踢人或用力推搡别人。被打的同学很害怕，身上也疼。','如果你被打了，或者看到同学被打，应该怎样做？','被打时先尽量远离危险、大声呼救，马上找附近老师；受伤请老师帮助处理。旁观者赶快请老师，不围观、不独自对打。应接受孩子按自身或旁观者视角作答。','先保护安全，赶快找附近的老师；受伤也要及时告诉大人。','平安之星','hurt'],
[1,'“不许告诉老师”的威胁','有人对同学说：“不准告诉老师，不然我还会打你。”这位同学很害怕，不知道能不能说。','被这样威胁时，要替对方保密吗？你应该怎样做？','不需要保守伤害自己的秘密。先到安全处，马上告诉老师、家长等可信赖的大人，把威胁的话说清楚；没有得到帮助就继续求助。不要求孩子当面对抗。','让你害怕、受伤的事不用保密。可信赖的大人会帮助你。','信任之星','threat'],
[1,'难听的话，也会伤人','有人故意用难听的话辱骂同学、嘲笑同学。对方已经很难过，他还是不停地骂。','听到这样的辱骂，你怎样保护自己，或帮助被骂的同学？','安全时可以明确说“请停止，我不喜欢这样”；离开对方，告诉老师或家长。旁观者不跟着骂、不起哄，在安全处陪伴同学、请大人帮助。危险时先离开，不要求必须先说停下。','不对骂、不起哄。先离开让你害怕的地方，再找可信赖的大人。','善言之星','insult']]
levels[5:5]=new
answers=[
['先关心同学：“别着急，我愿意听你说。”','陪他找老师，把故意藏文具的事情说清楚。'],
['可以说：“我陪你一起去告诉老师。”','也可以请家长帮助，把发生的事情说清楚。'],
['这次是不小心，不能只凭碰到一下就认定是故意欺负。','线索是：不小心碰到、马上道歉，还关心有没有受伤。'],
['不跟着叫外号，不起哄。','安全时说“请好好叫他的名字”，并请老师帮助。'],
['不跟着排斥，邀请这位同学一起玩。','持续被排斥时，可以陪他请老师帮助。'],
['先尽量远离危险，大声呼救，马上找附近老师。','看到别人被打，赶快请老师，不围观、不独自打回去。','如果受伤，要及时告诉大人，请大人帮助处理。'],
['不用保密！让人害怕、受伤的秘密，要告诉可信赖的大人。','先到安全处，把威胁的话告诉老师或家长。','如果还没得到帮助，就继续向其他可信赖的大人求助。'],
['不跟着骂，不起哄，也不用对骂。','安全时说“请停止”；有危险先离开，再告诉老师或家长。','看见同学被骂，可以安全地陪伴他，请老师帮助。'],
['可以说：“你一定又着急又委屈，我陪着你。”','认真听他说，再陪他找老师帮助。'],
['帮忙捡起彩笔，说：“我来帮你。”','不取笑，不要求同学用听话或物品来交换帮助。'],
['先离开危险，走到安全处，马上找老师。','安全时可以说“请停下”，但不用硬抢或打架。'],
['可以继续求助！求助不是告状。','再找老师、家长或其他可信赖的大人，直到得到帮助。'],
['不围观起哄，不独自冲上去打架。','赶快请老师来处理，在安全的地方陪伴同学。'],
['例如：好好叫同学的名字，借东西先问。','也可以说：邀请同学一起玩，看到同学难过时安全地帮助他。','说出一件具体、友善、明天能做到的事，就很好。'],
['记住：拒绝、离开、求助、帮助。','有危险先离开、找可信赖的大人；一次没解决，就继续求助。','帮助同学时不围观、不起哄、不独自对抗。']]
assert len(answers)==len(levels)==15
for l,a in zip(levels,answers):l.append(a)
# Use data-driven totals in every place, rather than a fixed old count.
html=html.replace('const levels=LEVELS;', 'const levels=LEVELS;\nconst TOTAL=levels.length;')
html=html.replace('const counts=[2,3,2,3,2];', 'const counts=themes.map((_,i)=>levels.filter(l=>l[0]===i).length);')
html=html.replace("KEY='friendly-town-picture-qa-v1'", "KEY='friendly-town-picture-qa-v2-reveal'")
html=html.replace('s.index<=12','s.index<=TOTAL').replace("'answer','reward'","'answer','reveal','reward'").replace('s.index===12','s.index===TOTAL')
html=html.replace('${n} / 12','${n} / ${TOTAL}').replace('${state.index+1} / 12','${state.index+1} / ${TOTAL}')
html=html.replace('5 个主题任务、12 个小关卡','5 个主题任务、${TOTAL} 个小关卡').replace('收集 12 枚','收集 ${TOTAL} 枚').replace('五个主题，共十二关','五个主题，共${TOTAL}关').replace('5 个主题 · 12 个关卡','5 个主题 · ${TOTAL} 个关卡')
html=html.replace('state.index===11', 'state.index===TOTAL-1').replace('state.index===12', 'state.index===TOTAL')
html=html.replace('约 30～40 分钟','约 35～45 分钟')
html=html.replace('看图听问题 → 举手 → 小石头请一位同学回答 → 判断对错', '看图听问题 → 举手回答 → 揭晓答案 → 判断对错')
html=html.replace('<li>听完口头回答后，小石头判断“答对了”或“答错了”。网页不会自动识别或判分。</li>', '<li>同学口头回答完毕后，点击“揭晓参考答案”。全班先一起看答案，再由小石头点击“答对了”或“答错了”。网页不会自动识别或判分。</li>')
html=html.replace('展开关卡下方的“主持人判定参考”可查看要点', '揭晓答案后，展开“主持人判定参考”可查看补充要点')
html=html.replace('有些同学遇到了委屈，有些事情需要帮助。', '藏文具、排斥、打人、威胁和辱骂，都需要我们认真对待。')
html=html.replace('分辨行为，尊重同学', '认识欺负，尊重同学')
# Three matching static object illustrations, without characters or violent depictions.
art=r'''
if(type==='hurt'){art=`<g transform="translate(150 232) rotate(-7)"><rect width="228" height="142" rx="18" fill="#f3ead1"/><path d="M72 0V-23Q114-56 156-23V0" stroke="#527451" stroke-width="13" fill="none"/><path d="M114 37V105M80 71H148" stroke="#b46749" stroke-width="24"/></g><g transform="translate(378 127)"><path d="M35 0L72 16L88 55L72 93L35 109L-3 93L-19 55L-3 16Z" fill="#b46749"/><path d="M7 55H63" stroke="#f4e8cf" stroke-width="10"/></g>${plaque(131,117,'打人不可以')}${leaf(483,381,23)}`}
if(type==='threat'){art=`<g transform="translate(154 191) rotate(-9)"><rect width="158" height="142" rx="14" fill="#657c67"/><path d="M36 3V-34Q77-88 122-34V3" stroke="#ead6a3" stroke-width="17" fill="none"/><path d="M79 57V101" stroke="#e9dbb8" stroke-width="12"/><circle cx="79" cy="53" r="14" fill="#e9dbb8"/><path d="M-12 139L170-12" stroke="#f4ebcf" stroke-width="17"/><path d="M-12 139L170-12" stroke="#b56c4b" stroke-width="7"/></g>${envelope(368,286,9)}${plaque(328,132,'不用保密')}${heart(414,222,.6)}`}
if(type==='insult'){art=`<g transform="translate(139 149) rotate(-7)"><path d="M0 0H224V143H108L55 180V143H0Z" fill="#eadcbc"/><path d="M40 40H177M40 70H154M40 100H132" stroke="#ad6c50" stroke-width="7" stroke-linecap="round"/><path d="M25 128L201 14" stroke="#f5ecd5" stroke-width="15"/><path d="M25 128L201 14" stroke="#a76145" stroke-width="6"/></g><g transform="translate(335 292) rotate(9)"><path d="M0 0H149V96H69L33 120V96H0Z" fill="#d8e0bc"/>${heart(74,49,.65)}</g>${plaque(329,111,'好好说话')}`}
'''
html=html.replace("if(type==='school'||cover)",art+"if(type==='school'||cover)")
start=html.index('function answerHTML()');end=html.index('\nfunction renderIntro()',start)
html=html[:start]+r'''function answerHTML(){const l=levels[state.index];if(state.phase==='reward')return `<div class="reward-box" role="status">${star()}<div><strong>答对啦！获得「${l[6]}」</strong><span>奖励送给认真思考、勇敢表达的全班同学。</span></div></div><div class="buttons"><button class="primary" onclick="next()">${state.index===TOTAL-1?'集齐奖励，完成游戏 →':'领取奖励，进入下一关 →'}</button><button onclick="revise()">重新判定</button></div>`;
if(state.phase==='reveal')return `<div class="revealed-answer" role="status"><div class="q-label">参考答案 · 一起看一看</div><ul>${l[8].map(t=>`<li>${t}</li>`).join('')}</ul></div><p class="instruction">对照刚才的回答，<strong>意思合理即可</strong>，不用一字不差。</p><div class="buttons"><button class="good" onclick="grade(true)">✓ 答对了</button><button class="wrong" onclick="grade(false)">✕ 答错了，再想想</button><button onclick="inviteAgain()">重新请一位</button></div><details class="hostref"><summary>主持人判定参考（补充说明）</summary><p>${l[4]}</p></details>`;
const retry=state.retry?`<div class="retry" role="status">这次还差一点，一起再想想：<br>${l[5]}</div>`:'';return `${retry}<p class="instruction">${state.phase==='answer'?'<strong>先听这位同学把答案说完。</strong><br>再揭晓参考答案，最后判断对错。':'<strong>现在请大家举手。</strong><br>小石头选一位同学，听听他的想法。'}</p><div class="buttons">${state.phase==='answer'?'<button class="primary" onclick="reveal()">同学回答完毕，揭晓参考答案 →</button><button onclick="inviteAgain()">重新请一位</button>':'<button class="primary" onclick="invite()">已请到同学，开始回答 →</button>'}</div>`}
function reveal(){if(state.phase!=='answer')return;state.phase='reveal';state.retry=false;save();render()}
''' +html[end:]
html=html.replace("function inviteAgain(){if(state.phase!=='answer')return;", "function inviteAgain(){if(!['answer','reveal'].includes(state.phase))return;")
html=html.replace("function grade(correct){if(state.phase!=='answer'", "function grade(correct){if(state.phase!=='reveal'")
html=html.replace("function revise(){if(state.phase!=='reward')return;state.phase='answer'", "function revise(){if(state.phase!=='reward')return;state.phase='reveal'")
html=html.replace('<section class="play">','<section class="play ${[\'reveal\',\'reward\'].includes(state.phase)?\'revealed\':\'\'}">')
style='''.revealed-answer{background:#e9edde;border:1px solid #bfccb0;border-radius:8px;padding:13px 17px;margin-bottom:13px}.revealed-answer ul{margin:8px 0 0;padding-left:22px}.revealed-answer li{font-size:18px;line-height:1.75;margin:4px 0}.revealed .story{display:none}.progress{gap:7px}.progress i{width:16px}@media(min-width:901px) and (max-height:850px){.revealed-answer{padding:10px 14px}.revealed-answer li{font-size:17px;line-height:1.65}.revealed .question{font-size:24px;margin-bottom:14px}}@media(max-width:900px){.progress{gap:4px}.progress i{width:11px}.revealed-answer li{font-size:18px}}'''
html=html.replace('</style>',style+'</style>')
# Single deliverable replaces the previous picture-Q&A page; old game versions stay separate.
Path('outputs/友爱小镇-看图问答闯关游戏.html').write_text(html.replace('LEVELS',json.dumps(levels,ensure_ascii=False)))
