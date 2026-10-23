// Deterministic async behavior tests of the actual self-contained browser script.
// No browser/server/package installation is required. DOM rendering itself is
// qualified separately in a real browser; this harness controls response order.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const filename=process.argv[2]||'src/ds60sqlpy/assets/learning_modules.html';
const script=fs.readFileSync(filename,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
class Element {
  constructor(){this.value='';this.textContent='';this.hidden=false;this.disabled=false;this.children=[];this.handlers={};this.innerHTML='';}
  addEventListener(name,fn){(this.handlers[name]??=[]).push(fn);}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=children;}
  setAttribute(name,value){this[name]=value;}
  focus(){this.focused=true;}
  setSelectionRange(start,end){this.selection=[start,end];}
  setRangeText(text,start,end){this.value=this.value.slice(0,start)+text+this.value.slice(end);}
  dispatchEvent(event){for(const fn of this.handlers[event.type]||[])fn({...event,target:this});}
}
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return{promise,resolve,reject};}
const settle=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
function environment(){
  const elements=new Map(),requests=[],timers=new Map(),storage=new Map();let timer=0;
  const element=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
  const context=vm.createContext({console,AbortController,Event:class{constructor(type){this.type=type;}},
    document:{getElementById:element,createElement:()=>new Element(),addEventListener:()=>{}},
    window:{addEventListener:()=>{}},confirm:()=>true,prompt:()=>null,
    crypto:{randomUUID:()=> '12345678-1234-1234-1234-123456789abc'},
    localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    setTimeout:(fn,ms)=>{const id=++timer;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id),
    fetch:(url,options)=>{const body=JSON.parse(options.body),pending=deferred();requests.push({url,body,pending});return pending.promise;},
  });
  vm.runInContext(script,context,{filename});
  const run=code=>vm.runInContext(code,context);
  const current=(id='llm-009',language='python')=>{
    context.fixture={id,language,runtime_profile:'python-core',capability:{profile:'python-core',ready:true,detail:'Fixture ready'}};
    run('current=fixture;lessonId=fixture.id;');element('timeout').value='60';
  };
  const resolve=(request,data)=>request.pending.resolve({ok:true,json:async()=>data});
  const next=action=>requests.findLast(item=>item.body.action===action);
  const event=(id,name='click')=>{const handlers=element(id).handlers[name]||[];return Promise.all(handlers.map(fn=>fn({target:element(id),preventDefault(){}})));};
  return{context,run,current,element,requests,timers,storage,resolve,next,event};
}
let checks=0;
async function test(name,fn){await fn();checks++;console.log('PASS '+name);}
await test('old save acknowledgement cannot mark newer draft saved',async()=>{
  const e=environment();e.current();e.element('source').value='older';
  assert.equal(e.next('module-index').url,'/api/modules');
  const saving=e.run('queueSave()');await settle();const request=e.next('module-save');
  e.element('source').value='newer';await e.event('source','input');
  e.resolve(request,{session:{}});await saving;
  assert.match(e.element('save-state').textContent,/Unsaved/);
  assert.equal(JSON.parse(e.storage.get('ds60.module.unsaved.llm-009')).source,'newer');
});
await test('latest save acknowledges the matching draft and clears only its backup',async()=>{
  const e=environment();e.current();e.element('source').value='latest';await e.event('source','input');
  const saving=e.run('queueSave()');await settle();e.resolve(e.next('module-save'),{session:{}});await saving;
  assert.match(e.element('save-state').textContent,/^Saved/);assert.equal(e.storage.has('ds60.module.unsaved.llm-009'),false);
});
await test('navigation while saving invalidates an old Run intent',async()=>{
  const e=environment();e.current();e.element('source').value='print(42)';
  const clicked=e.event('run');await settle();e.run('intentVersion++;');
  e.resolve(e.next('module-save'),{session:{}});await clicked;
  assert.equal(e.requests.filter(r=>r.body.action==='module-run').length,0);
  assert.match(e.element('status').textContent,/changed while saving/);
});
await test('double Run cannot submit two requests while the save is pending',async()=>{
  const e=environment();e.current();e.element('source').value='print(42)';
  const first=e.event('run'),second=e.event('run');await settle();
  assert.equal(e.requests.filter(r=>r.body.action==='module-save').length,1);
  e.resolve(e.next('module-save'),{session:{}});await settle();
  assert.equal(e.requests.filter(r=>r.body.action==='module-run').length,1);
  e.resolve(e.next('module-run'),{job_id:'a',lesson_id:'llm-009',status:'succeeded',source:'print(42)',checks:[]});
  await Promise.all([first,second]);assert.equal(e.run('submitInFlight'),false);
});
await test('late solution response cannot enter a different lesson',async()=>{
  const e=environment();e.current();const clicked=e.event('reveal');await settle();
  e.current('tf-008');e.run('intentVersion++;');
  e.resolve(e.next('module-solutions'),{documents:[{html:'OLD SOLUTION'}]});await clicked;
  assert.equal(e.element('solutions').children.length,0);
});
await test('diagnostic jumps require exact current source and submitted filename',async()=>{
  const e=environment();e.current();e.element('source').value='one\ntwo\nthree';
  e.context.job={job_id:'a',lesson_id:'llm-009',source:'one\ntwo\nthree',output:'File "/job/verify.py", line 88\nFile "/job/main.py", line 2\nValueError'};
  assert.equal(e.run('sourceErrorLine(job)'),2);
  e.context.job.output='File "/job/verify.py", line 2';assert.equal(e.run('sourceErrorLine(job)'),null);
  e.context.job.output='File "/job/main.py", line 99';assert.equal(e.run('sourceErrorLine(job)'),null);
  e.context.job.output='File "/job/main.py", line 0';assert.equal(e.run('sourceErrorLine(job)'),null);
  e.context.job.output='File "/job/main.py", line 2';e.element('source').value='edited';assert.equal(e.run('sourceErrorLine(job)'),null);
});
await test('Scala capitalization and C++ line/column locations are supported',async()=>{
  const e=environment();e.current('spark-003','scala');e.element('source').value='one\ntwo';
  e.context.job={lesson_id:'spark-003',source:'one\ntwo',output:'Main.scala:2: error: fixture'};
  assert.equal(e.run('sourceErrorLine(job)'),2);
  e.current('cpp-003','cpp');e.context.job.lesson_id='cpp-003';e.context.job.output='main.cpp:2:8: error: fixture';
  assert.equal(e.run('sourceErrorLine(job)'),2);
});
await test('editing after displaying a diagnostic removes its stale jump',async()=>{
  const e=environment();e.current();e.element('source').value='one\ntwo';
  e.context.job={lesson_id:'llm-009',source:'one\ntwo',output:'File "/job/main.py", line 2',status:'failed'};
  e.run('showJob(job)');assert.equal(e.element('error-line').hidden,false);
  e.element('source').value='edited';await e.event('source','input');assert.equal(e.element('error-line').hidden,true);
});
await test('overlapping poll requests use one in-flight request and one timer',async()=>{
  const e=environment();e.current();e.context.job={job_id:'a',lesson_id:'llm-009',status:'running'};
  e.run('adoptJob(job,false)');const first=e.run('poll()'),second=e.run('poll()');await settle();
  assert.equal(e.requests.filter(r=>r.body.action==='module-job').length,1);
  e.resolve(e.next('module-job'),e.context.job);await Promise.all([first,second]);
  assert.equal([...e.timers.values()].filter(t=>t.ms===1000).length,1);
});
await test('old terminal response cannot clear a newer active job',async()=>{
  const e=environment();e.current();e.context.job={job_id:'old',lesson_id:'llm-009',status:'running'};
  e.run('adoptJob(job,false)');const pending=e.run('poll()');await settle();
  e.context.newJob={job_id:'new',lesson_id:'llm-009',status:'running'};
  e.run('activeJob=null;activeJobRecord=null;adoptJob(newJob,false)');
  e.resolve(e.next('module-job'),{...e.context.job,status:'succeeded'});await pending;
  assert.equal(e.run('activeJob'),'new');assert.equal(e.run('activeJobRecord.job_id'),'new');
});
await test('reconnecting an old record cannot steal another active monitor',async()=>{
  const e=environment();e.current();e.context.job={job_id:'new',lesson_id:'llm-009',status:'running'};
  e.run('adoptJob(job,false)');e.context.old={job_id:'old',lesson_id:'llm-009',status:'interrupted'};
  assert.equal(e.run('adoptJob(old,false)'),false);assert.equal(e.run('activeJob'),'new');
  e.run('showJob(old)');assert.equal(e.element('reconnect').disabled,true);
});
await test('saved interrupted job is adopted without source resubmission',async()=>{
  const e=environment();e.current();e.context.job={job_id:'resume',lesson_id:'llm-009',status:'interrupted'};
  assert.equal(e.run('adoptJob(job,false)'),true);assert.equal(e.element('cancel').disabled,false);
  assert.equal(e.element('run').disabled,true);assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
});

await test('startup reconnects the persisted active lesson without resubmitting',async()=>{
  const e=environment();
  const lesson={id:'cpp-009',title:'Ownership',level:'beginner',status:'authored',prerequisites:[],outcome:'Observe ownership'};
  const job={job_id:'resume',lesson_id:'cpp-009',status:'running',source:'int main(){}',source_sha256:'a'.repeat(64),created_at:'2026-10-22'};
  e.resolve(e.next('module-index'),{authored_count:1,planned_count:1,active_job:job,tracks:[{id:'cpp',title:'C++',pilot_id:'cpp-009',lessons:[lesson]}]});
  await settle();assert.equal(e.next('module-lesson').body.lesson_id,'cpp-009');
  e.resolve(e.next('module-lesson'),{...lesson,language:'cpp',runtime_profile:'cpp20',source:job.source,guide_html:'guide',session:{},history:[job],capability:{profile:'cpp20',ready:true,detail:'Fixture'}});
  await settle();assert.equal(e.run('activeJob'),'resume');assert.equal(e.element('cancel').disabled,false);
  assert.equal(e.next('module-job').body.job_id,'resume');
  assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
});
await test('out-of-order lesson responses cannot replace the latest source',async()=>{
  const e=environment();
  const one={id:'a',title:'A',level:'beginner',status:'authored',prerequisites:[],outcome:'A'},two={...one,id:'b',title:'B'};
  e.context.navigation={tracks:[{id:'t',title:'Track',lessons:[one,two]}]};e.run("index=navigation;trackId='t';");
  const a=e.run("openLesson('a',false)"),first=e.next('module-lesson');
  const b=e.run("openLesson('b',false)"),second=e.next('module-lesson');
  const data=record=>({...record,language:'python',runtime_profile:'python-core',source:record.id,guide_html:record.id,session:{},history:[],capability:{profile:'python-core',ready:true,detail:'Fixture'}});
  e.resolve(second,data(two));await b;e.resolve(first,data(one));await a;
  assert.equal(e.run('current.id'),'b');assert.equal(e.element('source').value,'b');
});
await test('curated PySpark alias selects its own session and preserves base navigation',async()=>{
  const e=environment();
  const base={id:'spark-013',title:'Rows',level:'intermediate',status:'authored',prerequisites:[],outcome:'Rows',variants:[{id:'spark-013',title:'Scala'},{id:'spark-013@pyspark',title:'PySpark'}]};
  e.context.navigation={tracks:[{id:'spark',title:'Spark',lessons:[base]}]};e.run("index=navigation;trackId='spark';");
  const opening=e.run("openLesson('spark-013@pyspark',false)");
  const requested=e.next('module-lesson');assert.equal(requested.body.lesson_id,'spark-013@pyspark');
  e.resolve(requested,{...base,id:'spark-013@pyspark',base_id:'spark-013',language:'python',runtime_profile:'spark-local-python',source:'print(42)',guide_html:'guide',session:{},history:[],capability:{profile:'spark-local-python',ready:true,detail:'Fixture'}});
  await opening;assert.equal(e.run('lesson().id'),'spark-013');assert.equal(e.element('variant').hidden,false);
  assert.equal(e.element('variant').value,'spark-013@pyspark');assert.equal(e.run('current.language'),'python');
  const saving=e.run('queueSave()');await settle();assert.equal(e.next('module-save').body.lesson_id,'spark-013@pyspark');
  e.resolve(e.next('module-save'),{session:{}});await saving;
});

function interrupted(e,profile='cpp20'){
  e.current('cpp-009',profile==='k8s-kind'?'yaml':'cpp');e.element('source').value='retained draft';
  const job={job_id:'recover',lesson_id:'cpp-009',profile,status:'interrupted',source:'submitted source',checks:[],source_sha256:'a'.repeat(64)};
  e.context.job=job;e.run('adoptJob(job,false);showJob(job)');return job;
}
async function resolveRecovery(e,job,clicked){
  const result={...job,status:'failed',detail:'Operator confirmed recovery; prior result unavailable.',recovery:{type:'operator-confirmed'}};
  e.resolve(e.next('module-recover'),result);await settle();
  e.resolve(e.next('module-job'),result);await settle();
  e.resolve(e.next('module-lesson'),{id:job.lesson_id,history:[result]});await clicked;
}
await test('manual recovery requires the exact acknowledgement before any API call',async()=>{
  const e=environment(),job=interrupted(e);e.context.prompt=()=> 'yes';
  await e.element('recover').onclick();assert.equal(e.next('module-recover'),undefined);
  assert.equal(e.run('activeJob'),job.job_id);assert.equal(e.element('source').value,'retained draft');
});
await test('worker recovery retains source and polls the failed receipt without resubmission',async()=>{
  const e=environment(),job=interrupted(e);let message='';
  e.context.prompt=text=>{message=text;return 'WORKER RESTARTED';};
  const clicked=e.element('recover').onclick();await settle();
  assert.match(message,/restart only the owned cpp20 worker/);assert.match(message,/does not verify cleanup or mastery/);
  assert.deepEqual(e.next('module-recover').body,{action:'module-recover',job_id:'recover',confirmation:'WORKER RESTARTED'});
  await resolveRecovery(e,job,clicked);
  assert.equal(e.run('activeJob'),null);assert.equal(e.element('source').value,'retained draft');
  assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
  assert.equal(e.element('recover').hidden,true);
});
await test('Kubernetes recovery requires release of the owned cluster with distinct confirmation',async()=>{
  const e=environment(),job=interrupted(e,'k8s-kind');let message='';
  e.context.prompt=text=>{message=text;return 'CLUSTER RELEASED';};
  const clicked=e.element('recover').onclick();await settle();
  assert.match(message,/release only the owned disposable cluster/);
  assert.equal(e.next('module-recover').body.confirmation,'CLUSTER RELEASED');
  await resolveRecovery(e,job,clicked);assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
});
await test('manual recovery of an old receipt cannot steal an active monitor',async()=>{
  const e=environment(),job=interrupted(e);let prompted=false;e.context.prompt=()=>{prompted=true;return 'WORKER RESTARTED';};
  e.context.newJob={...job,job_id:'new',status:'running'};e.run('activeJob=null;adoptJob(newJob,false);showJob(job)');
  assert.equal(e.element('recover').disabled,true);await e.element('recover').onclick();
  assert.equal(prompted,false);assert.equal(e.next('module-recover'),undefined);assert.equal(e.run('activeJob'),'new');
});
await test('late recovery response preserves a newer monitor and edited draft',async()=>{
  const e=environment(),job=interrupted(e);e.context.prompt=()=> 'WORKER RESTARTED';
  const clicked=e.element('recover').onclick();await settle();
  e.element('source').value='new draft';e.context.newJob={...job,job_id:'new',status:'running'};
  e.run('intentVersion++;activeJob=null;adoptJob(newJob,false)');
  e.resolve(e.next('module-recover'),{...job,status:'failed'});await clicked;
  assert.equal(e.run('activeJob'),'new');assert.equal(e.element('source').value,'new draft');
  assert.equal(e.next('module-job'),undefined);
});
await test('recovery refresh survives an older in-flight interrupted poll using one follow-up',async()=>{
  const e=environment(),job=interrupted(e);e.context.prompt=()=> 'WORKER RESTARTED';
  const old=e.run('poll()');await settle();const oldRequest=e.next('module-job');
  const clicked=e.element('recover').onclick();await settle();
  e.resolve(e.next('module-recover'),{...job,status:'failed'});await clicked;
  e.resolve(oldRequest,job);await old;
  const immediate=[...e.timers.entries()].filter(([,timer])=>timer.ms===0);
  assert.equal(immediate.length,1);e.timers.delete(immediate[0][0]);immediate[0][1].fn();await settle();
  assert.equal(e.requests.filter(r=>r.body.action==='module-job').length,2);
  const result={...job,status:'failed'};e.resolve(e.next('module-job'),result);await settle();
  e.resolve(e.next('module-lesson'),{id:job.lesson_id,history:[result]});await settle();
  assert.equal(e.run('activeJob'),null);assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
});
await test('recovery that reconnects a live job does not claim operator recovery was recorded',async()=>{
  const e=environment(),job=interrupted(e);e.context.prompt=()=> 'WORKER RESTARTED';
  const clicked=e.element('recover').onclick();await settle();
  const running={...job,status:'running',detail:'Existing job is active.'};
  e.resolve(e.next('module-recover'),running);await settle();
  e.resolve(e.next('module-job'),running);await clicked;
  assert.equal(e.run('activeJob'),job.job_id);
  assert.match(e.element('status').textContent,/No manual recovery was recorded/);
  assert.equal(e.requests.some(r=>r.body.action==='module-run'),false);
});
console.log(JSON.stringify({checks,passed:true,final:true}));
