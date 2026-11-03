// Complete in place with one click, without flashes or intermediate screens.
let effectsBusy=false,effectsTimer=0;
function stopEffects(){clearTimeout(effectsTimer);effectsTimer=0;effectsBusy=false}
const singleLabels=['放好木板','修好木桥，一起过河','安装机身与双翼','拼好飞机，起飞','举起护盾，守护伙伴','点亮全部安全小路','接通缆车电源','充满电力，乘车上山','搭好全部树屋地板','建好树屋，点亮星空'];
const singleMessages=['第一块木板装好了！','木桥修好了，小梅和科迪平安过河！','机身和双翼安装完成！','六个部件拼好了，飞机飞向纽扣森林！','两侧护盾展开，伙伴们安全了！','三条小路全部亮起，大家安全通过森林！','电源接通了，缆车开始苏醒！','电力充满，缆车平安抵达山顶！','三块地板搭好了，友爱树屋更加稳固！','屋顶和星灯亮起来，五颗友爱之星闪耀，冒险成功！'];
function titleForTask(){return singleLabels[state.index]}
function paintStoryMini(){
 if(!$('mini-dialog').open)return;
 const i=state.index,done=!!mini.done;let scene='';
 if(i<2)scene=bridgeSVG(i+(done?1:0));
 else if(i<4)scene=planeSVG((i-2)*3+(done?3:0));
 else if(i===4)scene=`<div class="single-guards">${shieldSVG()}${shieldSVG()}</div><p>${done?'两侧护盾已展开 ✓':'一起守护左右两侧的伙伴'}</p>`;
 else if(i===5)scene=`<div class="single-lights">${[0,1,2].map(()=>`<span>${done?'✦':'✧'}</span>`).join('')}</div><p>${done?'三条小路已照亮 ✓':'让安全之光照亮森林'}</p>`;
 else if(i<8)scene=`<div class="single-cable ${done&&i===7?'arrived':''}"><span class="cable-car">🚠</span></div><div class="power-cells">${[0,1,2].map((_,k)=>`<span class="${k<(i===6?(done?1:0):(done?3:1))?'charged':''}">⚡</span>`).join('')}</div><p>${done?i===6?'电源已接通 ✓':'缆车平安到站 ✓':'一起为缆车提供力量'}</p>`;
 else if(i===8)scene=cabinSVG(done,false);
 else scene=cabinSVG(true,done)+(done?'<div class="single-lights">✦ ✦ ✦ ✦ ✦</div>':'');
 $('mini-title').textContent=singleLabels[i];$('mini-goal').textContent='只需点击一次，完成本关互动';
 $('mini-play').innerHTML=`<div class="single-scene">${scene}</div><div class="craft-actions"><button class="primary" onclick="${done?'continueAfterMini()':"storyAct('complete')"}">${done?(i===TOTAL-1?'完成冒险，查看通关 →':chapterStarts.includes(i+1)?'前往下一章 →':'下一题 →'):singleLabels[i]+' ✦'}</button></div>`;
 $('mini-status').textContent=done?singleMessages[i]:'点击一次即可完成，无需重复点击。';
}
function storyAct(action){
 if(action!=='complete'||effectsBusy||state.phase!=='reward'||state.build!==1||!$('mini-dialog').open)return;
 mini.done=true;state.build=2;save();paintStoryMini();
}
const startSingleMini=startMini;
startMini=function(){stopEffects();startSingleMini()};
const closeSingleDialog=closeDialog;
closeDialog=function(id){if(id==='mini-dialog')stopEffects();closeSingleDialog(id)};
$('mini-dialog').addEventListener('close',stopEffects);
$('mini-dialog').addEventListener('cancel',stopEffects);
