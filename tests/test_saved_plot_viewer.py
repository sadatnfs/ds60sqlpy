"""Exercise saved-viewer message, render-copy and resize behavior with a small DOM stub.

Actual Plotly geometry is separately verified through Chromium acceptance.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_viewer_resizes_only_its_rendering_copy_and_preserves_connection_guards() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the browser bootstrap behavior check")
    html = (ROOT / "src/ds60sqlpy/assets/plot-sandbox.html").read_text()
    script = re.findall(r"<script>\s*(.*?)\s*</script>", html, re.S)[-1]
    script = script.replace("__DS60_BROWSER_ORIGIN__", json.dumps("http://classroom.test"))
    harness = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const source = SOURCE;
function makeViewer(hasObserver = true) {
  const listeners = new Map(), queue = new Map(), messages = [], calls = [];
  let nextFrame = 1, observer = null, failResize = false;
  const parent = {}, plot = {clientWidth:600,clientHeight:420,isConnected:true,hidden:false};
  const error = {textContent:''};
  const Plotly = {
    async newPlot(id, data, layout, config) {
      calls.push({kind:'new',id,data,layout,config});
      plot._fullLayout = {width:plot.clientWidth,height:plot.clientHeight};
    },
    async addFrames(id, frames) { calls.push({kind:'frames',id,frames}); },
    Plots: {async resize(element) {
      assert.equal(element,plot);
      if (failResize) throw new Error('synthetic resize failure');
      calls.push({kind:'resize',width:plot.clientWidth,height:plot.clientHeight});
      plot._fullLayout = {width:plot.clientWidth,height:plot.clientHeight};
    }}
  };
  const window = {
    addEventListener(name,handler) {listeners.set(name,handler);},
    removeEventListener(name,handler) {
      if (listeners.get(name) === handler) listeners.delete(name);
    }
  };
  const context = {parent,window,Plotly,document:{getElementById:id=>id==='plot'?plot:error},
    requestAnimationFrame:callback=>{const key=nextFrame++;queue.set(key,callback);return key;},
    cancelAnimationFrame:key=>queue.delete(key)};
  if (hasObserver) context.ResizeObserver = class {
    constructor(callback) {this.callback=callback;this.disconnected=false;observer=this;}
    observe(element) {assert.equal(element,plot);}
    disconnect() {this.disconnected=true;}
  };
  vm.runInNewContext(source,context);
  const port={start(){},postMessage:value=>messages.push(JSON.parse(JSON.stringify(value)))};
  return {parent,plot,error,calls,messages,listeners,queue,
    get observer(){return observer;},
    set failResize(value){failResize=value;},
    async flush(){
      const callbacks=[...queue.values()];queue.clear();
      for(const fn of callbacks)await fn();
    },
    async connect(figure,overrides={}) {
      await listeners.get('message')({source:parent,origin:'http://classroom.test',
        data:{type:'ds60-plot-connect',figure},ports:[port],...overrides});
    }};
}
(async()=>{
  const figure={data:[{type:'scatter',x:[1,2],y:[3,5]}],
    layout:{width:1200,height:900,title:'Original dimensions'}};
  const original=JSON.stringify(figure), view=makeViewer();
  await view.connect(figure,{source:{}});
  await view.connect(figure,{origin:'http://other.test'});
  await view.connect(figure,{ports:[]});
  assert.equal(view.calls.length,0);
  await view.connect(figure);
  await view.flush();
  assert.equal(view.calls.length,1);
  const rendered=view.calls[0];
  assert.equal(rendered.layout.width,undefined);
  assert.equal(rendered.layout.height,undefined);
  assert.equal(rendered.layout.autosize,true);
  assert.equal(rendered.config.toImageButtonOptions.format,'svg');
  assert.equal(rendered.config.responsive,true);
  assert.equal(JSON.stringify(figure),original);
  assert.deepEqual(view.messages,[{type:'ready'}]);
  await view.connect(figure);
  assert.equal(view.calls.length,1);
  view.plot.clientWidth=318;view.plot.clientHeight=418;
  view.observer.callback();await view.flush();
  assert.equal(view.plot._fullLayout.width,318);
  assert.equal(view.plot._fullLayout.height,418);
  const count=view.calls.length;
  view.observer.callback();await view.flush();assert.equal(view.calls.length,count);
  view.plot.clientWidth=0;view.plot.clientHeight=0;
  view.observer.callback();await view.flush();assert.equal(view.calls.length,count);
  view.plot.clientWidth=520;view.plot.clientHeight=360;
  view.observer.callback();await view.flush();
  assert.equal(view.plot._fullLayout.width,520);
  view.plot.clientWidth=300;view.failResize=true;
  view.observer.callback();await view.flush();
  assert.equal(view.plot.hidden,true);
  assert.match(view.error.textContent,/synthetic resize failure/);
  view.listeners.get('pagehide')();
  assert.equal(view.observer.disconnected,true);
  assert.equal(view.listeners.has('resize'),false);
  assert.equal(view.queue.size,0);
  const fallback=makeViewer(false);
  await fallback.connect(figure);await fallback.flush();
  fallback.plot.clientWidth=240;fallback.listeners.get('resize')();await fallback.flush();
  assert.equal(fallback.plot._fullLayout.width,240);
  const oversized=makeViewer();
  await oversized.connect({data:[],layout:{title:'x'.repeat(180001)}});
  assert.equal(oversized.calls.length,0);
  assert.equal(oversized.plot.hidden,true);
  assert.equal(oversized.messages[0].type,'error');
  assert.match(oversized.error.textContent,/oversized/);
  console.log('render copy, guards, resize, hidden/show, fallback and cleanup passed');
})().catch(error=>{console.error(error);process.exit(1);});
"""
    completed = subprocess.run(
        [node, "-e", harness.replace("SOURCE", json.dumps(script), 1)],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert (
        "render copy, guards, resize, hidden/show, fallback and cleanup passed" in completed.stdout
    )
