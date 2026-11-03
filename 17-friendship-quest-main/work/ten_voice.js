// One player for all narration; moving between pages always cancels old speech.
const TEN_VOICE_PREF='friendship-ten-xiaoxiao-auto-v1';
let tenAuto=true,tenPlayer=null,tenCurrent='',tenContext='',tenToken=0,tenPending=null,tenActiveKind='';
try{tenAuto=localStorage.getItem(TEN_VOICE_PREF)!=='off'}catch{}
function tenIndex(kind){return ['scene','question','answer','reward','mini','done'].includes(kind)?state.index:kind==='chapter'?levels[state.index][0]:0}
function syncTenVoice(){
 const toggle=$('ten-voice-auto');if(toggle){toggle.textContent='自动配音：'+(tenAuto?'开':'关');toggle.setAttribute('aria-pressed',String(tenAuto))}
 document.querySelectorAll('[data-ten-status]').forEach(el=>el.textContent=tenCurrent?(tenPlayer?.paused?'已暂停：':'正在播放：')+tenCurrent:'晓晓普通话女声 · 可重听、暂停');
 document.querySelectorAll('[data-ten-pause]').forEach(el=>{el.disabled=!tenPlayer;el.textContent=tenPlayer?.paused?'继续播放':'暂停'});
 document.querySelectorAll('[data-ten-stop]').forEach(el=>el.disabled=!tenPlayer);
}
function stopTenVoice(){tenToken++;tenPending=null;tenActiveKind='';if(tenPlayer){tenPlayer.pause();tenPlayer.removeAttribute('src');tenPlayer.load();tenPlayer=null}tenCurrent='';syncTenVoice()}
async function playTenVoice(kind){
 const clip=tenVoiceClips[kind]?.[tenIndex(kind)];if(!clip)return;
 stopTenVoice();const token=tenToken,context=tenContext,p=new Audio(clip.src);tenPlayer=p;tenCurrent=clip.title;tenActiveKind=kind;
 p.onended=()=>{if(token===tenToken){tenPlayer=null;tenCurrent='';syncTenVoice()}};
 p.onerror=()=>{if(token===tenToken){stopTenVoice();toast('配音未能播放，请点击重听。')}};
 syncTenVoice();
 try{await p.play()}catch(err){if(token!==tenToken)return;stopTenVoice();if(err?.name==='NotAllowedError')tenPending={kind,context};else toast('请点击重听播放配音。')}
}
async function pauseTenVoice(){if(!tenPlayer)return;if(tenPlayer.paused){try{await tenPlayer.play()}catch{toast('请点击重听播放配音。')}}else tenPlayer.pause();syncTenVoice()}
function tenKind(){if($('guide')?.open)return null;for(const id of ['reset','guide','map','pause'])if($(id)?.open)return id;if($('mini-dialog').open)return state.build===2?'done':null;return ({intro:'intro',chapter:'chapter',ask:'scene',answer:'question',reveal:'answer',end:'pledge'})[state.phase]}
function toggleTenVoice(){tenAuto=!tenAuto;try{localStorage.setItem(TEN_VOICE_PREF,tenAuto?'on':'off')}catch{}stopTenVoice();if(tenAuto)playTenVoice(tenKind());syncTenVoice()}
function tenControls(){return '<span data-ten-status role="status"></span><button onclick="playTenVoice(tenKind())">重听</button><button data-ten-pause onclick="pauseTenVoice()">暂停</button><button data-ten-stop onclick="stopTenVoice()">停止</button>'}
function renderTenVoice(){
 let toolbar=$('ten-voice-toolbar');if(!toolbar){toolbar=document.createElement('div');toolbar.id='ten-voice-toolbar';toolbar.innerHTML='<strong>冒险电台</strong><button id="ten-voice-auto" onclick="toggleTenVoice()"></button><div class="ten-voice-controls">'+tenControls()+'</div>';$('presentation-viewport').before(toolbar)}
 if(['ask','answer','reveal'].includes(state.phase)){
  const area=$('question');area.insertAdjacentHTML('afterend','<div class="ten-question-voice"><button onclick="playTenVoice(\'scene\')">听情景与问题</button><button onclick="playTenVoice(\'question\')">只听问题</button></div>');
 }
 syncTenVoice();
}
function updateTenVoiceContext(force=false){const context=state.index+':'+state.phase+':'+($('mini-dialog').open?state.build:'page');if(!force&&context===tenContext)return;stopTenVoice();tenContext=context;if(tenAuto&&state.phase!=='answer')playTenVoice(tenKind())}
const renderBeforeTenVoice=render;
render=function(){renderBeforeTenVoice();renderTenVoice();updateTenVoiceContext()};
const startMiniBeforeTenVoice=startMini;
startMini=function(){stopTenVoice();startMiniBeforeTenVoice();if(!$('mini-dialog').open)return;let controls=$('ten-mini-voice');if(!controls){controls=document.createElement('div');controls.id='ten-mini-voice';controls.className='ten-voice-controls';controls.innerHTML=tenControls();$('mini-status').after(controls)}syncTenVoice();updateTenVoiceContext()};
const storyActBeforeTenVoice=storyAct;
storyAct=function(action){const before=state.build;storyActBeforeTenVoice(action);if(before!==state.build)updateTenVoiceContext()};
const closeBeforeTenVoice=closeDialog;
closeDialog=function(id){stopTenVoice();closeBeforeTenVoice(id)};
const openGuideBeforeTenVoice=openGuide;
openGuide=function(...args){stopTenVoice();return openGuideBeforeTenVoice.apply(this,args)};
for(const [name,kind] of [['openMap','map'],['pauseGame','pause'],['requestReset','reset']]){const original=window[name];window[name]=function(...args){stopTenVoice();const result=original.apply(this,args);const dialog=$(kind);if(dialog&&!dialog.querySelector('.ten-voice-controls')){const controls=document.createElement('div');controls.className='ten-voice-controls';controls.innerHTML=tenControls();(dialog.querySelector('.dialog-fit-content')||dialog).append(controls)}syncTenVoice();if(tenAuto)playTenVoice(kind);return result}}
for(const id of ['mini-dialog','guide','map','pause','reset']){const dialog=$(id);if(dialog){dialog.addEventListener('close',()=>{if((id==='mini-dialog'&&['mini','done'].includes(tenActiveKind))||tenActiveKind===id)stopTenVoice()});dialog.addEventListener('cancel',stopTenVoice)}}
document.addEventListener('pointerdown',()=>{const pending=tenPending;if(pending&&tenAuto&&pending.context===tenContext){tenPending=null;playTenVoice(pending.kind)}},true);
document.addEventListener('keydown',()=>{const pending=tenPending;if(pending&&tenAuto&&pending.context===tenContext){tenPending=null;playTenVoice(pending.kind)}},true);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopTenVoice()});window.addEventListener('pagehide',stopTenVoice);
