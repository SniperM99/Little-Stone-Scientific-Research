const fs=require('fs'),assert=require('assert'),{JSDOM}=require('jsdom');
// Media decoding is checked separately; keep the state-machine DOM lightweight.
const source=fs.readFileSync('outputs/友爱奇旅-10关精简版.html','utf8');
assert(!/AudioContext|speechSynthesis|小石头|single-flash/.test(source));assert(source.includes('data:audio/mpeg;base64,'));assert(source.includes('许牧宸'));assert(source.includes('data:image/jpeg;base64,'));
const html=source.replace(/(data:[^;"']+;base64,)[A-Za-z0-9+/=]+/g,'$1AA=='),errors=[];
function open(saved){return new JSDOM(html,{url:'https://ten.test',runScripts:'dangerously',beforeParse(w){w.scrollTo=()=>{};w.Audio=class{constructor(src){this.src=src;this.paused=true}play(){this.paused=false;return Promise.resolve()}pause(){this.paused=true}removeAttribute(){}load(){}};w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};w.localStorage.setItem('friendship-narration-v1','off');if(saved)w.localStorage.setItem('friendship-ten-levels-v1',saved);w.addEventListener('error',e=>errors.push(e.message))}})}
(async()=>{
const dom=open(),w=dom.window,e=s=>w.eval(s),act=(a,k)=>{w.stopEffects();w.storyAct(a,k)};
assert.equal(e('TOTAL'),10);assert.equal(e('tenActiveKind'),'intro');assert.equal(e('Object.keys(tenVoiceClips.chapter).length'),5);for(const kind of ['scene','question','answer','done'])assert.equal(e('Object.keys(tenVoiceClips.'+kind+').length'),10);assert.deepEqual(Array.from(e('counts')),[2,2,2,2,2]);assert.equal(e('levelImages.length'),10);
assert.equal(e('Object.keys(tenVoiceClips.reward).length'),10);assert(!e('tenVoiceClips.mini'));assert(!e('tenVoiceClips.intro[0].text').includes('我是'));for(let i=0;i<10;i++)assert(!e('tenVoiceClips.done['+i+'].text').includes('点击'));for(let i=0;i<10;i++){assert(e('tenVoiceClips.scene['+i+'].text').endsWith('请大家举手回答。'));assert.equal(e('tenVoiceClips.question['+i+'].text'),e('levels['+i+'][3]')+' 请大家举手回答。');assert(e('tenVoiceClips.scene['+i+'].text').includes(e('levels['+i+'][2]')));for(const line of e('levels['+i+'][8]'))assert(e('tenVoiceClips.answer['+i+'].text').includes(line))}assert(w.document.querySelector('#ten-voice-toolbar'));assert(!w.document.querySelector('#action-narration-panel'));
w.openGuide();assert.equal(e('tenPlayer'),null);assert.equal(e('tenKind()'),null);assert(!e('tenVoiceClips.guide'));assert(!w.document.querySelector('#guide .ten-voice-controls'));w.closeDialog('guide');w.start();
for(let i=0;i<10;i++){
 assert.equal(e('state.index'),i);if(i%2===0){assert.equal(e('state.phase'),'chapter');assert(w.document.querySelector('.chapter-opening'));assert.equal(e('tenActiveKind'),'chapter');w.beginChapter()}
 assert.equal(e('state.phase'),'ask');assert.equal(e('tenActiveKind'),'scene');assert(w.document.body.textContent.includes(e('levels[state.index][3]')));
 w.grade(true);assert.equal(e('state.phase'),'ask');w.invite();w.reveal();w.grade(true);assert.equal(e('state.phase'),'reward');
 w.next();assert.equal(e('state.index'),i);assert.equal(e('tenActiveKind'),'reward');assert.equal(e('tenVoiceClips.reward[state.index].text').replace('。',''),w.document.querySelector('.reward-box strong').textContent);const rewardPlayer=e('tenPlayer');w.startMini();assert(rewardPlayer.paused);assert.equal(e('tenPlayer'),null);assert.equal(e('tenActiveKind'),'');
 const actionButtons=w.document.querySelectorAll('#mini-play button');assert.equal(actionButtons.length,1);
 actionButtons[0].click();assert.equal(e('tenActiveKind'),'done');assert.equal(e('state.build'),2);assert(!w.document.querySelector('.single-completing'));assert(!w.document.querySelector('.story-win'));
 assert.equal(e('state.build'),2,'interaction '+i);assert.equal(e('earned()'),i+1);
 const continueButton=w.document.querySelector('#mini-play .craft-actions button');assert.equal(continueButton.getAttribute('onclick'),'continueAfterMini()');
 w.openMap();assert.equal(w.document.querySelectorAll('.map-node').length,10);w.closeDialog('map');
 const restored=open(w.localStorage.getItem('friendship-ten-levels-v1'));assert.equal(restored.window.eval('state.index'),i);assert.equal(restored.window.eval('state.build'),2);restored.window.close();continueButton.click();assert(!w.document.getElementById('mini-dialog').open);assert.equal(e('state.phase'),i===9?'end':i%2===1?'chapter':'ask');
}
assert.equal(e('state.phase'),'end');assert.equal(w.document.querySelectorAll('.stamp').length,10);assert.equal(errors.length,0,errors.join('\n'));w.resetGame();assert.equal(e('state.phase'),'intro');w.close();console.log('PASS: 10 levels, 5 chapters, all interactions, answer gates, maps, Xiaoxiao narration and cancellation, saved progress, ending and reset');

})().catch(err=>{console.error(err);process.exitCode=1});
