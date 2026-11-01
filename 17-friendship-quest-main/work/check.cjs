const fs=require('fs'),assert=require('assert'),{JSDOM}=require('jsdom');
const errors=[];const dom=new JSDOM(fs.readFileSync('outputs/集体为家·团结向前-友爱星舰科技版.html','utf8'),{runScripts:'dangerously',beforeParse(w){w.HTMLElement.prototype.scrollIntoView=function(){};w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};w.addEventListener('error',e=>errors.push(e.message));}});const w=dom.window,d=w.document,$=id=>d.getElementById(id);
assert.equal(d.querySelectorAll('.mission-nav button').length,5);
w.warmUp();assert(!$('warm').classList.contains('hidden'));
w.go(1);for(let i=0;i<6;i++){w.answer('unsure');assert($('judge-feedback').textContent.length>25);w.judgeMove(1)}
w.go(2);for(let i=0;i<4;i++){w.selectSituation(i);w.match(i);assert($('mood-feedback').textContent.includes('你理解了'))}
w.go(3);for(let i=0;i<4;i++)w.unlock(i);assert.equal(d.querySelectorAll('.shield.learned').length,4);
w.go(4);w.addWish('<img src=x onerror=alert(1)>');assert.equal(d.querySelectorAll('.leaf img').length,0);assert(d.querySelector('.leaves').textContent.includes('<img'));const count=d.querySelectorAll('.leaf').length;w.addWish('<img src=x onerror=alert(1)>');assert.equal(d.querySelectorAll('.leaf').length,count);
w.celebrate();assert(!$('badge').classList.contains('hidden'));w.toggleTips();assert(!$('tip').classList.contains('hidden'));w.togglePresent();assert(d.body.classList.contains('present'));
w.pickMood('我想请老师帮助。');w.practiceMail();assert($('mailresult').textContent.includes('没有发送'));w.closeMail();assert.equal($('mailtext').value,'');
assert.equal(errors.length,0,errors.join('\n'));console.log('PASS: 5 tasks, 6 scenario cards, 4 emotion matches, 4 shields, wishes and HTML escaping, pledge, host/presentation toggles, mailbox practice and clearing.');w.close();
