const fs=require('fs'),assert=require('assert'),{JSDOM}=require('jsdom');const html=fs.readFileSync('outputs/友爱星舰-全班合作闯关游戏.html','utf8');
function game(saved){return new JSDOM(html,{url:'https://local.test/',runScripts:'dangerously',beforeParse(w){w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};if(saved)w.localStorage.setItem('xiaoshitou-starship-game-v1',saved)}})}
const dom=game(),w=dom.window,d=w.document,$=id=>d.getElementById(id),ev=code=>w.eval(code);assert(d.body.textContent.includes('全班准备好了'));w.start();assert.equal(d.querySelectorAll('.choice').length,3);
w.choose(2);w.confirmChoice();assert.equal(ev('state.phase'),'retry');assert.equal(ev('completed()'),0);assert($('confirm').disabled);const saved=w.localStorage.getItem('xiaoshitou-starship-game-v1');assert.equal(JSON.parse(saved).phase,'vote');const resumed=game(saved);assert.equal(resumed.window.eval('state.phase'),'vote');resumed.window.close();
w.choose(0);assert.equal(ev('state.phase'),'vote');w.confirmChoice();assert.equal(ev('completed()'),1);w.confirmChoice();assert.equal(ev('completed()'),1);w.advance();
// Tally: reject missing/invalid counts, clear previous choice on a tie, then confirm plurality.
w.choose(0);['2','2','1'].forEach((v,i)=>$('votes-'+i).value=v);w.countVotes();assert.equal(ev('state.choice'),null);assert($('confirm').disabled);assert($('tally-output').textContent.includes('平票'));
['1.5','2','0'].forEach((v,i)=>$('votes-'+i).value=v);w.countVotes();assert($('tally-output').textContent.includes('整数'));
['1','9','2'].forEach((v,i)=>$('votes-'+i).value=v);w.countVotes();assert.equal(ev('state.choice'),1);assert.equal(ev('state.phase'),'vote');w.confirmChoice();w.advance();
while(ev('state.index')<12){const i=ev('state.index'),correct=ev(`scenes[${i}].correct`);w.choose(Array.isArray(correct)?2:correct);w.confirmChoice();assert.equal(ev('state.phase'),'good');assert.equal(d.querySelectorAll('.choice:disabled').length,3);w.advance()}
assert.equal(ev('state.phase'),'end');assert(d.body.textContent.includes('100%'));assert(d.body.textContent.includes('不让同学落单'));w.celebrate();assert($('medal-result').textContent.includes('全体同学'));w.showGuide();assert($('guide').open);w.askReset();assert($('reset').open);w.resetGame();assert.equal(ev('state.phase'),'intro');assert.equal(ev('state.index'),0);
// Every option in the class pledge choice is accepted.
for(const c of [0,1,2]){ev('state={index:10,phase:"vote",choice:null,wish:null};render()');w.choose(c);w.confirmChoice();assert.equal(ev('state.phase'),'good');assert.equal(ev('state.wish'),c)}
// Bad persisted data falls back safely; end game restores.
for(const s of ['broken','{"index":99,"phase":"vote"}','{"index":0,"phase":"good","choice":2}']){const x=game(s);assert.equal(x.window.eval('state.phase'),'intro');x.window.close()}
const end=game(JSON.stringify({index:12,phase:'end',choice:null,wish:1}));assert(end.window.document.body.textContent.includes('通关成功'));end.window.close();
console.log('PASS: all 12 decisions through victory; wrong-answer retry and refresh; duplicate confirmation guard; vote validation, tie and plurality; all 3 wish branches; resume, dialogs, reset, invalid saved state.');w.close();
