const chapterStarts=[0,2,8,10,13];
const chapterTitles=['修好书本谷的木桥','拼出积木飞机','守住纽扣森林','让缆车重新通电','建好树屋，一起看星星'];
const chapterStories=[
  "小梅和科迪来到书本山谷，发现前方的木桥被风吹坏了。桥面缺了两段，暂时不能过河。接下来，全班一起帮助遇到困难的同学；每完成一次任务，就能得到一块修桥木板。",
  "过了木桥，小梅和科迪走进积木森林。他们需要拼一架飞机，才能继续前进。全班将完成六次友爱任务，收集机身、左右机翼、起落架、尾翼和螺旋桨，一起把飞机拼好。",
  "积木飞机降落在纽扣森林。狼族正悄悄靠近纽扣村庄，村里的伙伴需要保护。全班学会理解和帮助同学，就能获得守护盾与星光法杖，和小梅、科迪一起守住村庄。",
  "狼族退远了，小梅和科迪来到绳桥峡谷。缆车停在站台，因为电池没有电，暂时不能出发。全班完成三次安全求助任务，就能充满三格电，乘缆车前往山顶。",
  "缆车平安到站，山顶的星空小屋就在眼前！小梅和科迪想在大树上搭一个观星树屋。全班许下友爱约定，一起铺好地板、装上屋顶和星灯，最后坐下来欣赏星空。"
];
const chapterGoals=['收集 2 块木板 → 修好木桥 → 过河','集齐 6 个飞机部件 → 拼装 → 起飞','获得守护盾与星光法杖 → 抵御狼族偷袭','收集 3 格电力 → 供电 → 乘缆车到山顶','搭地板 → 装屋顶星灯 → 建树屋 → 看星星'];
const partNames=['关心木板','陪伴木板','飞机机身积木','左机翼积木','右机翼积木','起落架积木','尾翼积木','螺旋桨积木','守护盾','星光法杖','第一格电力','第二格电力','第三格电力','树屋地板','树屋屋顶与星灯'];
const plotLines=[
  "课前，一位同学发现自己的铅笔不见了。有个同学故意把铅笔藏在书包里，看见他到处找，也不肯拿出来。找不到铅笔的同学又着急又难过。",
  "一位同学悄悄告诉你：“有人经常把我的文具藏起来。我想告诉老师，可是又怕他以后更欺负我。”说完，他低下头，不知道该怎么办。",
  "一位同学从座位旁经过时，不小心轻轻碰到了旁边的同学。他马上停下来，说：“对不起！你有没有受伤？”",
  "有人每天叫一位同学难听的外号。那位同学已经说了：“我不喜欢，请叫我的名字。”可是，叫外号的人还是不停地叫，还让别人一起笑。",
  "课间，几位同学正在玩游戏。有一人对大家说：“谁都不许和他玩！”被排斥的同学站在旁边，很想参加，却没有人邀请他。",
  "课间，有人故意用手打同学，还用力推搡他。被打的同学身上很疼，也很害怕。老师就在附近，他需要尽快得到帮助。",
  "一位同学被欺负后，想去告诉老师。欺负他的人却说：“不准告诉老师，不然我还会打你！”这位同学很害怕，不知道还能不能说。",
  "有人对着一位同学大声说难听的话，还嘲笑他。被骂的同学很难过，说：“请不要再骂我了。”可是，骂人的同学仍然没有停下来。",
  "一位同学的橡皮被人故意藏起来了。他把书包和桌面找了好几遍，还是没有找到。他小声说：“我很着急，也觉得很委屈。”",
  "快上课了，一位同学不小心把彩笔碰掉了，彩笔散落一地。他正一支一支地捡，担心来不及收好。你就在他的旁边。",
  "有人抢走一位同学的铅笔盒，不肯归还，还想推他。被抢东西的同学很害怕。附近就有老师，可以请老师帮忙。",
  "一位同学告诉你：“我已经向一位大人说过自己被欺负的事，可是，欺负我的人还是没有停下来。我还能再找人帮忙吗？”",
  "你在走廊里看见有人故意推搡一位同学。被推的同学很害怕，有些人围着看，还有人在笑。老师就在旁边的教室里。",
  "大家都希望班级像家一样温暖，没有人被取笑，也没有人被排斥。要做到这一点，每位同学都可以从一件小事开始。",
  "有的同学会因为被推打而害怕，有的会因为被骂、被排斥而难过。想让大家在班里安心相处，我们既要学会保护自己，也要学会安全地帮助同学。"
];
const levelQuestions=[
  "你会对这位着急的同学说什么？又可以怎样帮助他？",
  "这位同学不敢告诉老师，你可以怎样陪他一起求助？",
  "这次是故意欺负人，还是不小心碰到？你是从哪里看出来的？",
  "如果你听见有人这样叫外号，会怎样帮助被取笑的同学？",
  "你可以怎样邀请这位同学，让他不再孤单地站在一旁？",
  "如果你是被打的同学，现在最应该怎样保护自己？",
  "面对“不准告诉老师”的威胁，这件事要保密吗？他可以找谁帮忙？",
  "看到同学被这样辱骂，你会怎样帮助他，同时保护好自己？",
  "你会对他说一句什么话，让他知道你理解他、愿意陪着他？",
  "你能帮他做什么？可以对他说一句什么话？",
  "如果你是被抢铅笔盒的同学，怎样做才能先让自己安全？",
  "求助过一次还没有解决，还能继续求助吗？接下来可以找谁？",
  "你怎样做，既能帮助被推搡的同学，又能保护好自己？",
  "请说一件你明天就能做到的友爱小事。",
  "遇到欺负时，你会怎样保护自己？看到同学被欺负，你又会怎样安全地帮助他？"
];
levels.forEach((l,i)=>{l[2]=plotLines[i];l[3]=levelQuestions[i];});
let mini={};
function chapterLocal(){return state.index-chapterStarts[levels[state.index][0]]}
function startMini(){if(state.phase!=='reward'||state.build===2)return;state.build=1;save();render();mini={placed:false,selected:[],turns:0,rode:false,stargazing:false};$('mini-dialog').showModal();paintStoryMini()}
function titleForTask(){const r=levels[state.index][0];return r===0?'把木板装到桥上':r===1?'把积木装到飞机上':r===2?state.index===8?'举起守护盾':'点亮星光法杖':r===3?'给缆车充入电力':state.index===13?'搭好树屋地板':'装好屋顶，点亮星空'}
function chapterOpening(){const r=levels[state.index][0];$('app').innerHTML=`<section class="chapter-opening"><img src="${chapterImages[r]}" alt="小梅和科迪在${regions[r]}的剧情场景"><div class="chapter-opening-copy"><div class="eyebrow">第 ${r+1} 章 / 5 · ${regions[r]}</div><h1>${chapterTitles[r]}</h1><p>${chapterStories[r]}</p><div class="chapter-objective">本章目标：${chapterGoals[r]}</div><button class="primary" onclick="beginChapter()">进入本章任务 →</button><small>本章 ${counts[r]} 道问题 · 每次帮助伙伴，都会推动冒险向前。</small></div></section>`}
function beginChapter(){if(state.phase!=='chapter')return;state.phase='ask';state.retry=false;save();render()}
function planeSVG(parts){return `<svg class="plane-craft" viewBox="0 0 650 300" aria-label="已拼好 ${parts} 个飞机部件"><ellipse cx="330" cy="249" rx="225" ry="18" fill="#0d292c55"/><g opacity="${parts>=1?1:.16}"><path d="M130 147L406 113L490 157L414 196L139 183Z" fill="#c9965a" stroke="#f0cd97" stroke-width="4"/><path d="M157 145L399 117L418 143L165 170Z" fill="#dfa55e"/><rect x="277" y="121" width="75" height="49" rx="6" fill="#749c97"/></g><path opacity="${parts>=2?1:.15}" d="M290 150L212 45L290 29L380 137Z" fill="#b86f57" stroke="#ebc39a" stroke-width="4"/><path opacity="${parts>=3?1:.15}" d="M295 159L231 264L320 273L392 158Z" fill="#b86f57" stroke="#ebc39a" stroke-width="4"/><g opacity="${parts>=4?1:.15}" fill="#384c4d" stroke="#d1b68c" stroke-width="5"><circle cx="381" cy="213" r="23"/><circle cx="164" cy="206" r="19"/></g><path opacity="${parts>=5?1:.15}" d="M154 161L97 80L160 68L212 158Z" fill="#79956d" stroke="#d6dbb0" stroke-width="4"/><g opacity="${parts>=6?1:.15}" transform="translate(483 155)"><path d="M0-59Q25-50 7-6Q18 30-3 63Q-26 50-9 7Q-26-30 0-59" fill="#dac58e" stroke="#eae1b8" stroke-width="3"/><circle r="11" fill="#6b7558"/></g></svg>`}
function bridgeSVG(parts){return `<svg class="story-bridge" viewBox="0 0 650 250" aria-label="木桥已修复 ${parts} / 2 段"><path d="M0 120L125 93L156 245H0M499 245L524 93L650 120V250H499Z" fill="#9c875e"/><path d="M111 80Q321 184 539 80M111 116Q321 219 539 116" stroke="#e6d3a0" stroke-width="6" fill="none"/>${Array.from({length:10},(_,n)=>`<path d="M${137+n*36} ${110+Math.sin(n/9*Math.PI)*44}l30 0l-2 30l-30 0Z" fill="${n<parts*5?'#d1a36c':'#284943'}" stroke="#d8c498" stroke-width="3" ${n<parts*5?'':'stroke-dasharray="5 6"'}/>`).join('')}<path d="M115 70V220M536 70V220" stroke="#dbc293" stroke-width="11"/></svg>`}
function wolfSVG(hidden=false){return `<svg viewBox="0 0 110 105" aria-hidden="true" class="wolf-symbol ${hidden?'retreated':''}"><path d="M14 35L10 4L42 23L67 23L100 4L96 39L84 76L56 99L27 76Z" fill="#7a8790"/><path d="M29 42L54 55L80 42L72 76L55 88L36 75Z" fill="#c4c5bc"/><path d="M45 71L55 66L65 71L55 80Z" fill="#364b4c"/><path d="M30 47L40 50M71 50L81 47" stroke="#e9dfb6" stroke-width="5" stroke-linecap="round"/></svg>`}
function shieldSVG(){return '<svg viewBox="0 0 100 110" aria-hidden="true"><path d="M50 5L88 22V54Q86 86 50 105Q14 86 12 54V22Z" fill="#739781" stroke="#e7d29d" stroke-width="6"/><path d="M26 51L44 69L75 34" stroke="#f8e5ad" stroke-width="9" fill="none"/></svg>'}
function cabinSVG(floor,roof){return `<svg class="treehouse-craft" viewBox="0 0 650 320" aria-label="树屋建造进度"><path d="M309 315V100M308 170L195 96M310 200L443 99" stroke="#a27c54" stroke-width="35" stroke-linecap="round"/><g fill="#648974"><ellipse cx="198" cy="71" rx="135" ry="67"/><ellipse cx="439" cy="64" rx="132" ry="67"/><ellipse cx="325" cy="25" rx="140" ry="73"/></g>${floor?'<path d="M170 234H462L485 261H151Z" fill="#e5b87d" stroke="#efcea0" stroke-width="5"/><path d="M185 238V288M449 238V288" stroke="#bc9462" stroke-width="13"/>':''}${roof?'<path d="M202 231V121L324 72L442 121V231Z" fill="#b98c5f"/><path d="M179 125L324 61L465 125" stroke="#dec091" stroke-width="22" fill="none"/><rect x="223" y="153" width="56" height="56" fill="#f4d794"/><rect x="368" y="153" width="56" height="56" fill="#f4d794"/><path d="M303 234V168H345V234" fill="#6e9180"/><path d="M194 132Q329 177 454 132" stroke="#f4d794" stroke-width="4" fill="none"/>':''}<path d="M292 265L264 319M345 265L375 319" stroke="#c4b483" stroke-width="8"/></svg>`}
function paintStoryMini(){if(!$('mini-dialog').open)return;const i=state.index,r=levels[i][0],n=chapterLocal(),before=n,installed=n+(mini.placed?1:0);$('mini-title').textContent=titleForTask();$('mini-goal').textContent='获得：'+partNames[i]+' · '+chapterGoals[r];let h='';
if(r===0){h=`<div class="craft-stage book-stage">${bridgeSVG(installed)}<div class="craft-meter">木桥进度 ${installed} / 2 段</div></div><div class="craft-actions">${!mini.placed?`<button class="primary" onclick="storyAct('place')">把${partNames[i]}放到桥上 ＋</button>`:n===1?'<button class="primary" onclick="storyAct(\'cross\')">木桥修好了，一起过桥 →</button>':''}</div><p>关心与陪伴，帮助伙伴，也让我们走到一起。</p>`}
if(r===1){h=`<div class="craft-stage block-stage ${mini.flying?'airborne':''}">${planeSVG(installed)}<div class="craft-meter">积木飞机 ${installed} / 6 个部件</div></div><div class="craft-actions">${!mini.placed?`<button class="primary" onclick="storyAct('place')">安装${partNames[i]} ＋</button>`:n===5?'<button class="primary" onclick="storyAct(\'fly\')">飞机拼好了，飞向纽扣森林 →</button>':''}</div><p>每一个部件都重要，每一位伙伴也都重要。</p>`}
if(r===2){if(n===0){h=`<div class="wolf-defense"><div class="defense-gear">${shieldSVG()}<b>守护盾已装备</b></div><div class="wolf-lanes">${[0,1].map((_,k)=>`<button class="wolf-lane ${mini.selected.includes(k)?'protected':''}" onclick="storyAct('guard',${k})">${wolfSVG(mini.selected.includes(k))}<b>${mini.selected.includes(k)?'这一侧已守住 ✓':k?'举盾守住右侧':'举盾守住左侧'}</b></button>`).join('')}</div></div><p>点击两侧举起护盾，挡住偷袭。保护伙伴，不追打狼族。</p>`}else{h=`<div class="staff-defense"><div class="staff">✦<span></span></div><div class="wolf-lanes">${[0,1,2].map((_,k)=>`<button class="starlight-lane ${mini.selected.includes(k)?'protected':''}" onclick="storyAct('light',${k})">${wolfSVG(mini.selected.includes(k))}<span>${mini.selected.includes(k)?'✦ 安全之光':'点亮这里的星光 ✧'}</span></button>`).join('')}</div></div><p>用星光照亮三条小路，让狼族退远，伙伴安全通过。</p>`}}
if(r===3){const power=n+(mini.placed?1:0);h=`<div class="cable-stage ${mini.rode?'cable-arrived':''}"><svg viewBox="0 0 650 235" aria-label="缆车位置"><path d="M35 66L610 28" stroke="#c7b88c" stroke-width="6"/><path d="M42 62V220M598 27V220" stroke="#a58c69" stroke-width="16"/><path d="M0 220H140L120 235H0M500 235L520 220H650V235" fill="#b5a17c"/><g class="gondola" transform="translate(${mini.rode?475:92} ${mini.rode?27:55})"><path d="M30 0V43" stroke="#dac99a" stroke-width="6"/><rect x="-15" y="43" width="100" height="93" rx="12" fill="#af7654" stroke="#ebc995" stroke-width="4"/><rect x="0" y="55" width="70" height="43" rx="4" fill="#92b7b2"/><path d="M35 55V99" stroke="#e5d5ad" stroke-width="4"/></g></svg><div class="power-cells">${[0,1,2].map((_,k)=>`<span class="${k<power?'charged':''}">⚡</span>`).join('')}</div><b>缆车电力 ${power} / 3 格</b></div><div class="craft-actions">${!mini.placed?(n===0?'<button class="primary" onclick="storyAct(\'charge\')">连接电线，充入第一格电力 ⚡</button>':n===1?`<button class="primary" onclick="storyAct('crank')">转动发电把手 ${mini.turns} / 3</button>`:'<button class="primary" onclick="storyAct(\'charge\')">闭合总开关，充入最后一格电 ⚡</button>'):n===2?!mini.rode?'<button class="primary" onclick="storyAct(\'ride\')">电力充足，乘坐缆车前行 →</button>':'<button class="primary" onclick="storyAct(\'arrive\')">到站啦！抵达山顶 →</button>':''}</div><p>遇到困难继续求助，就像一格一格积累力量，直到得到帮助。</p>`}
if(r===4){if(n===0){h=`<div class="craft-stage treehouse-stage">${cabinSVG(mini.selected.length>0,false)}<div class="floor-pieces">${[0,1,2].map((_,k)=>`<button class="floor-plank ${mini.selected.includes(k)?'placed':''}" onclick="storyAct('floor',${k})">${mini.selected.includes(k)?'✓':'＋'} 地板 ${k+1}</button>`).join('')}</div></div><p>把三块地板安好，每一块都承载着一份友爱约定。</p>`}else if(!mini.stargazing){h=`<div class="craft-stage treehouse-stage">${cabinSVG(true,mini.placed)}</div><div class="craft-actions">${!mini.placed?'<button class="primary" onclick="storyAct(\'roof\')">安装屋顶与星灯 ✦</button>':'<button class="primary" onclick="storyAct(\'stars\')">树屋建成！一起看星星 ✧</button>'}</div><p>屋顶遮风，友爱守护。树屋准备好了，我们一起看星空。</p>`}else{h=`<div class="star-sky"><img src="${chapterImages[4]}" alt="小梅和科迪在山顶树屋一起看星星"><div class="constellation">${['关心','尊重','勇气','互助','友爱'].map((t,k)=>`<button class="sky-star ${mini.selected.includes(k)?'lit':''}" style="left:${[13,31,52,72,84][k]}%;top:${[41,20,35,15,48][k]}%" onclick="storyAct('star',${k})">✧<small>${t}</small></button>`).join('')}</div></div><div class="craft-actions"><button class="primary" onclick="storyAct('finish')" ${mini.selected.length<5?'disabled':''}>${mini.selected.length<5?'点亮五颗属于全班的星星':'和小梅、科迪一起欣赏星空 ✦'}</button></div><p>这五颗星，记住了全班一起完成的冒险。</p>`}}$('mini-play').innerHTML=h;$('mini-status').textContent='';}
function storyAct(action,k){if(state.phase!=='reward'||state.build!==1||!$('mini-dialog').open)return;const r=levels[state.index][0],n=chapterLocal();
if(r===0){if(action==='place'&&!mini.placed){mini.placed=true;if(n===0)return miniComplete('第一段桥面修好了，还差一块木板。');paintStoryMini();return}if(action==='cross'&&mini.placed&&n===1)return miniComplete('木桥全部修好！小梅和科迪过河，进入积木森林。')}
if(r===1){if(action==='place'&&!mini.placed){mini.placed=true;if(n<5)return miniComplete(partNames[state.index]+'安装完成，飞机越来越完整了。');paintStoryMini();return}if(action==='fly'&&mini.placed&&n===5)return miniComplete('六个部件集齐，积木飞机起飞，前往纽扣森林！')}
if(r===2){const type=n===0?'guard':'light',total=n===0?2:3;if(action===type&&Number.isInteger(k)&&k>=0&&k<total&&!mini.selected.includes(k)){mini.selected.push(k);if(mini.selected.length===total)return miniComplete(n===0?'守护盾挡住了偷袭，村口已经安全。':'三条小路被星光照亮，狼族退远，大家安全前往绳桥峡谷。');paintStoryMini();return}}
if(r===3){if(action==='charge'&&!mini.placed&&n!==1){mini.placed=true;if(n===0)return miniComplete('第一格电力接通，缆车开始苏醒。');paintStoryMini();return}if(action==='crank'&&n===1&&!mini.placed){mini.turns++;if(mini.turns===3){mini.placed=true;return miniComplete('第二格电力充好，缆车还差最后一格电。')}paintStoryMini();return}if(action==='ride'&&n===2&&mini.placed){mini.rode=true;paintStoryMini();return}if(action==='arrive'&&n===2&&mini.rode)return miniComplete('缆车平安到站！山顶星空小屋就在眼前。')}
if(r===4){if(n===0&&action==='floor'&&Number.isInteger(k)&&k>=0&&k<3&&!mini.selected.includes(k)){mini.selected.push(k);if(mini.selected.length===3)return miniComplete('树屋地板全部搭好，最后再安装屋顶和星灯。');paintStoryMini();return}if(n===1){if(action==='roof'&&!mini.placed){mini.placed=true;paintStoryMini();return}if(action==='stars'&&mini.placed){mini.stargazing=true;mini.selected=[];paintStoryMini();return}if(action==='star'&&mini.stargazing&&Number.isInteger(k)&&k>=0&&k<5&&!mini.selected.includes(k)){mini.selected.push(k);paintStoryMini();return}if(action==='finish'&&mini.stargazing&&mini.selected.length===5)return miniComplete('树屋建好了，五颗友爱之星点亮。小梅、科迪和全班一起看星星！')}}
}
function miniComplete(message){if(state.phase!=='reward'||state.build!==1)return;state.build=2;save();render();$('mini-play').innerHTML=`<div class="story-win"><img src="${chapterImages[levels[state.index][0]]}" alt="本章冒险场景"><div>${star()}<h3>全班合作，剧情向前一步！</h3><p>${message}</p><button class="primary" onclick="closeDialog('mini-dialog')">回到关卡，继续冒险 →</button></div></div>`;$('mini-status').textContent='互动任务完成，下一步已解锁。'}
function bridgeHTML(){const r=levels[state.index][0],n=chapterLocal(),done=state.phase==='reward'&&state.build===2;return `<div class="quest-panel"><div class="quest-badge">${['▤','✈','✦','⚡','⌂'][r]}</div><div><b>${chapterTitles[r]}</b><span>${done?'✓ 本关剧情已完成':state.phase==='reward'?'获得 '+partNames[state.index]+'，去完成剧情互动':'帮助伙伴后，获得 '+partNames[state.index]}</span></div></div>`}
