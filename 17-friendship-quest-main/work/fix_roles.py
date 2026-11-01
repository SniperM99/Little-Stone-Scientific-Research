from pathlib import Path
import re,json
s=Path('work/animated-before-rolefix.html').read_text()
films=[
[['start','阿力看见米米把铅笔放在桌上。','这是我的铅笔。',1],['hide','阿力故意把米米的铅笔藏进自己的包。','藏起来，让她找不到。',0],['sad','米米找不到铅笔，很着急。小光看见了。','我的铅笔去哪了？',1]],
[['hide','阿力又藏起了米米的铅笔。','就不让她找到。',0],['sad','米米告诉小光，她不敢找大人。','我怕他再欺负我。',1],['ask','小光听见了，现在等全班给他出主意。','我该怎样帮助米米？',2]],
[['start','阿力经过米米身边，不小心轻轻碰到她。','哎呀，没看见你！',0],['sorry','阿力马上停下，向米米道歉。','对不起，你受伤了吗？',0],['ask','小光看见了：这次是不小心，还是故意？','我应该怎样判断？',2]],
[['name','阿力故意叫米米难听的外号。','我要叫你难听的外号。',0],['name','米米已经拒绝，阿力还在继续叫。','别这样叫我，我不喜欢。',1],['ask','小光听见了，他可以阻止起哄、找大人。','我现在应该做什么？',2]],
[['exclude','阿力对小光说，不许和米米一起玩。','不许和米米玩！',0],['alone','米米被排斥在游戏外，很孤单。','我也想和大家一起玩。',1],['ask','小光要决定：听阿力的，还是支持米米？','我要怎样对待米米？',2]],
[['hide','阿力故意把米米的橡皮藏进包里。','藏起来，看她着急。',0],['search','米米找了很久，急得快哭了。','我的橡皮找不到了。',1],['ask','小光站在旁边，想先安慰米米。','我对她说什么才好？',2]],
[['drop','米米的彩笔不小心掉了一地。','哎呀，彩笔掉了。',1],['sad','米米蹲着找彩笔，担心来不及收好。','好多支，捡不完怎么办？',1],['ask','小光看见米米需要帮助。全班来教他。','我该做什么、说什么？',2]],
[['snatch','阿力抢走米米的铅笔盒，不肯还。','我拿着，就是不还。',0],['worried','米米已经说请停下，却觉得更不安全。','请停下，把东西还给我。',1],['ask','小光看见老师在门外，要给米米一个建议。','怎样做才能先保证安全？',2]],
[['teacher','米米找过一位大人，但阿力仍在叫外号。','说过了，还是没有停。',1],['sad','米米有点灰心，问小光还能不能继续说。','我还能再找大人吗？',1],['ask','小光要给米米一个能继续获得帮助的建议。','我应该怎样回答她？',2]],
[['worried','阿力挡着米米，故意推搡她。画面不重演动作。','请停下，我不喜欢！',1],['teacher','小光看见了；老师就在教室门外。','老师就在门口。',2],['ask','小光要帮助米米，也要保护好自己。','我怎样帮她最安全？',2]],
[['tree','米米说，希望班级里不再有人受委屈。','我希望每天都安心。',1],['tree','阿力认识到做错了，愿意学习改变行为。','我愿意改正。',0],['tree','小光邀请全班选出第一条友爱约定。','我们先一起做到哪一条？',2]],
[['pledge','米米知道，遇到困难可以继续向大人求助。','我会告诉可信赖的大人。',1],['pledge','阿力承诺不再欺负同学，做错就改正。','我会尊重每位同学。',0],['shield','小光请全班决定，怎样每天守护班级。','我们一起怎么做？',2]]]
questions=[
'小光看见米米着急，应该先怎样做？',
'米米不敢找大人，小光应该怎样帮助她？',
'阿力是不小心碰到米米。小光应该怎样判断？',
'阿力不停叫米米外号，小光应该怎样做？',
'阿力不让米米加入游戏，小光应该怎样做？',
'米米找不到橡皮很着急，小光应该对她说什么？',
'米米的彩笔掉了，小光应该怎样帮助她？',
'米米觉得不安全，小光应该建议她怎么做？',
'求助后还没解决，小光应该给米米什么建议？',
'小光看见米米被欺负，现在怎样帮助最安全？',
'小光邀请全班表决：我们先实践哪条友爱约定？',
'小光请全班表决：每天怎样守护温暖的班级？']
actions=[
[['heart','关心米米','问问发生了什么'],['snow','只管天气','不问米米怎么了'],['away','不管米米','自己没事就好']],
[['laugh','笑她胆小','让她更难过'],['teacher','陪她找老师','一起把事情说清'],['mute','让她忍着','不要告诉大人']],
[['stop','认定是故意','不听阿力解释'],['heart','先关心米米','听解释，分清不小心'],['fight','让米米推回去','碰了就还回去']],
[['laugh','跟着叫外号','和阿力一起起哄'],['mute','叫米米忍着','别把事情说出去'],['teacher','不跟着起哄','请老师帮助制止']],
[['friends','邀请米米加入','不排斥，请老师帮助'],['away','也不和她玩','按阿力说的做'],['mute','装作没看见','不理这件事']],
[['mute','说她太爱哭','橡皮而已有啥好哭'],['heart','理解并陪伴','你很着急，我陪你求助'],['fight','找阿力打架','用打架解决问题']],
[['laugh','笑她笨手笨脚','取笑米米'],['lock','要求她听话','不听我的就不帮'],['pencil','帮她捡彩笔','说：我来帮你']],
[['door','先离开找老师','安全时说“请停下”'],['fight','让她打回去','先抢回东西再说'],['mute','让她别告诉大人','自己忍一忍']],
[['mute','让她不再说','说过一次就够了'],['teacher','鼓励继续求助','找其他可信赖的大人'],['away','建议不去学校','永远躲开学校']],
[['laugh','围观起哄','看着米米被欺负'],['fight','独自冲上去打架','不找大人帮忙'],['teacher','马上去请老师','不围观，安全陪伴']],
[['name','好好叫名字','不叫难听的外号'],['pencil','借东西先问','同意后再拿'],['friends','不让伙伴落单','安全地帮助同学']],
[['mute','游戏结束就忘记','课间不用遵守'],['shield','全班一起行动','不欺负、会求助、愿帮助'],['alone','只让班长负责','其他同学不用管']]]
results=['小光先关心米米，知道了铅笔被阿力故意藏起。','小光陪米米把事情告诉老师，米米不必独自面对。','小光先关心米米，听见了阿力的道歉。这次是不小心。','小光不跟着叫外号，并向老师求助，让伤害停止。','小光邀请米米一起玩，不听从排斥，并请老师帮助。','小光说：“你一定很着急。我陪你去找老师。”','小光说：“我来帮你。”和米米一起把彩笔收好。','小光建议米米先到安全处找老师；东西请大人帮助拿回。','小光鼓励米米继续向老师、家长等可信赖的大人求助。','小光马上请老师处理，不独自对抗；在安全处陪伴米米。','三个约定都很好，全班选出其中一个作为先实践的行动。','阿力学会改正，米米知道求助，小光和全班一起守护友爱。']
# Replace data, keeping all original decision correctness and flow.
s=re.sub(r'const films=\[.*?\n\];', 'const films='+json.dumps(films,ensure_ascii=False)+';',s,flags=re.S)
s=re.sub(r'const actions=\[.*?\n\];','const actions='+json.dumps(actions,ensure_ascii=False)+';\nconst questions='+json.dumps(questions,ensure_ascii=False)+';',s,flags=re.S)
s=re.sub(r'const shortResults=\[.*?\];', 'const shortResults='+json.dumps(results,ensure_ascii=False)+';',s,flags=re.S)
# Rebuild the cast in-place at fixed locations, in every shot.
start=s.index('function room(');end=s.index('\nfunction introArt()',start)
s=s[:start]+Path('work/fixed_room.js').read_text()+s[end:]
s=s.replace("KEY='xiaoshitou-animated-game-v1'", "KEY='xiaoshitou-animated-fixedcast-v2'")
s=s.replace("render();stopSpeech()", "render();stopSpeech()")
# Every visible title, prompt and hint explicitly uses the same cast.
titles=['阿力藏起米米的铅笔','米米不敢求助','阿力不小心碰到米米','阿力不停叫米米外号','阿力不让米米一起玩','米米找不到橡皮很着急','米米的彩笔掉了一地','阿力抢走米米的铅笔盒','求助一次还没解决','小光怎样安全帮助米米','全班选一条友爱约定','全班一起守护友爱']
# Override old prose used for optional read-aloud and wrong-answer hints as well.
hints=['米米着急是因为阿力故意藏了她的铅笔。小光要先关心同学，问清发生了什么。','米米害怕，不代表她只能忍着。小光可以陪她找可信赖的大人。','这次是不小心，而且阿力马上道歉。小光可以先关心米米，听清经过。','米米已经说不喜欢，阿力还继续叫。小光不该跟着起哄，应请大人帮助。','米米也有参加游戏的权利。小光可以邀请她，不跟着排斥。','先接住米米的心情，再陪她安全地求助。取笑和打架都帮不了她。','小光可以帮捡彩笔，不取笑，也不要求米米听自己的话作为交换。','米米的安全比拿回铅笔盒更重要。先离开危险，找老师帮助。','一次没解决，还可以继续找其他可信赖的大人。求助不是告状。','小光也要保护自己。请老师来处理，比围观或自己打架更安全。','','温暖的班级需要每个人每天行动，不能只靠班长。']
overrides='\nscenes.forEach((s,i)=>{s.title='+json.dumps(titles,ensure_ascii=False)+'[i];s.hint='+json.dumps(hints,ensure_ascii=False)+'[i];s.good='+json.dumps(results,ensure_ascii=False)+'[i];s.story=films[i].map(f=>f[1]).join("。");s.voice="请一位同学说说：小光为什么这样做？再全班一起练习。";});\n'
s=s.replace('const $=id=>',overrides+'const $=id=>')
s=s.replace('<section class="film" id="film"', '<div class="role-legend"><span class="bear-role"><b>小熊阿力</b>行为角色 · 做错要改正</span><span class="rabbit-role"><b>小兔米米</b>遇到困难 · 需要帮助</span><span class="monkey-role"><b>小猴小光</b>行动员 · 全班决定他怎么做</span></div><div class="mission-brief"><strong>这关要决定：</strong>${questions[i]}</div><section class="film" id="film"')
s=s.replace('<b>轮到全班决定：下一步怎么做？</b>', '<b>请帮小光选一个行动</b>')
s=s.replace('举手表决后，小石头点击一个行动图标','全班举手 → 小石头替小光点选行动')
s=s.replace("film.innerHTML=room(frame[0],frame[2])+", "film.innerHTML=room(frame[0],frame[2])+")
s=s.replace('class="subtitle" aria-live="polite">${frame[2]}','class="subtitle" aria-live="polite">${["阿力","米米","小光"][frame[3]]}：${frame[2]}')
s=s.replace("[1,3,7,8,9].includes(i)?'老师，我们需要帮助。':'有伙伴在，心里暖暖的。'", "[1,3,7,8,9].includes(i)?'老师，米米需要帮助。':i===6?'米米，我来帮你捡。':'米米，我愿意帮助你。'")
s=s.replace("if(i===10)","if(i===10)")
s=s.replace('你们的行动，让伙伴不再孤单。','小光采取了全班选出的行动。')
s=s.replace('小光暂停了这次行动：','先暂停：小光这样做，还不能帮到米米。')
s=s.replace('看见故事，<span style="color:var(--cyan)">点亮友爱</span>', '认识三个角色，<span style="color:var(--cyan)">一起帮助米米</span>')
s=s.replace('看动画 → 全班举手 → 点选行动 → 看见结果','阿力做出行为 → 米米遇到困难 → 全班指挥小光行动')
s=s.replace('一人操作，全班合作 · 动画互动游戏','固定三个角色 · 一人操作，全班合作')
s=s.replace('先看清发生了什么，再一起决定。','先看清阿力做了什么、米米怎么了，再指挥小光。')
s=s.replace('全班暂选 ','小光将执行 ')
s=s.replace('执行全班决定 →','让小光行动 →')
s=s.replace('先投票，再点选。确认前可以改选。','全班表决小光怎么做，选好后再让他行动。')
s=s.replace('<p>① 每关先播放', '<p><strong>固定角色：</strong>小熊阿力演示行为（做错就改正），小兔米米是需要帮助的同学，小猴小光是全班指挥的行动员。三个角色始终在左、中、右，不互换身份。第3关特意比较“不小心”与“故意”。</p><p>① 每关先播放')
# Keep characters still; move only the relevant prop or arm. Give children time to follow.
s=s.replace('},3000)', '},4200)')
css='''
.role-legend{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:8px}.role-legend span{border:1px solid #476079;border-radius:10px;padding:6px 14px;font-size:13px;color:#c9daec;background:#10243a}.role-legend b{font-size:19px;margin-right:12px}.bear-role b{color:#ffcc9d}.rabbit-role b{color:#a5eff6}.monkey-role b{color:#d2c7ff}.mission-brief{background:#20384e;border-left:4px solid #ffe29c;padding:9px 17px;margin-bottom:10px;border-radius:8px;font-size:21px;color:#f5f8ff}.mission-brief strong{color:#ffe29c}.film{max-height:calc(100vh - 315px);min-height:365px}.film .walking,.film .bobbing,.film .joining,.film .leaving{animation:none!important}.film .speech-bubble{animation:fade-only .3s ease-out}.tap.selected,.tap:hover{transform:none}.film .casting-label{font-weight:700;paint-order:stroke;stroke:#203b51;stroke-width:5px;stroke-linejoin:round}.film .hiding{animation:fixed-hide 2.4s ease-in-out forwards}.film .reaching{transform-box:fill-box;transform-origin:top left;animation:reach .9s ease-in-out 2}.film .picking{animation:pick-prop 2.2s ease-in-out forwards}.votequestion{top:44%;font-size:19px}.film .caption b{font-size:22px}.subtitle{font-size:23px;padding:8px 18px}.intro-art{height:230px}@keyframes fade-only{from{opacity:0}to{opacity:1}}@keyframes fixed-hide{0%,15%{transform:translate(0,0);opacity:1}75%,100%{transform:translate(-235px,15px);opacity:0}}@keyframes reach{50%{transform:rotate(-12deg)}}@keyframes pick-prop{0%{transform:translate(0,0);opacity:1}80%,100%{transform:translate(170px,-75px);opacity:0}}@media(min-width:901px) and (max-height:800px){.role-legend{gap:7px;margin-bottom:6px}.role-legend span{padding:4px 11px;font-size:12px}.role-legend b{font-size:17px}.mission-brief{font-size:19px;padding:6px 14px;margin-bottom:7px}.film{min-height:310px;max-height:calc(100vh - 290px)}.film .caption b{font-size:18px}.subtitle{font-size:20px}.tap{min-height:100px;bottom:3%}.tap svg{height:48px;width:48px}.tap b{font-size:18px}.tap small{font-size:12px}.votequestion{top:41%;font-size:17px}}@media(max-width:900px){.role-legend span{padding:6px;font-size:11px}.role-legend b{display:block;font-size:16px}.mission-brief{font-size:18px}.film{min-height:400px;max-height:none}.film .caption b{font-size:16px}.votequestion{font-size:16px}.subtitle{font-size:18px}.film svg.world{object-fit:contain}}
'''
s=s.replace('</style>',css+'</style>')
Path('outputs/友爱星舰-动画点选游戏.html').write_text(s)
