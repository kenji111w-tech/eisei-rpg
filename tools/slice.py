# 試作の通しテスト：はじめから→オープニング→医務室（チュートリアル戦）→草原→ミャクの町→仲間→現場1つ
import asyncio, sys
from playwright.async_api import async_playwright
PORT = 8766
STEP = """(acc) => { const g=window.__game, ui=document.getElementById('ui');
  const res = ui.querySelector('.quiz.result'); if (res) { res.querySelector('.item').click(); return 'next'; }
  const qz = ui.querySelector('.quiz'); if (qz) { const txt = qz.querySelector('.qtext').textContent; const cts = [...qz.querySelectorAll('.choice .ct')].map(b => b.textContent);
    const q = g.questions.find(x => x.question === txt && cts.every(c => x.choices.includes(c))); const btns=[...qz.querySelectorAll('.choice')];
    let t = btns[0]; if (q) t = btns.find(b => b.querySelector('.ct').textContent === q.choices[q.answer]) || t; if (!q) window.__noq=(window.__noq||[]).concat([txt.slice(0,30)]);
    t.click(); qz.querySelector('.ok').click(); return 'answer'; }
  const m=ui.querySelector('.msg'); if (m) { m.click(); return 'msg'; }
  const mm=ui.querySelector('.menu'); if (mm) { const inp=mm.querySelector('.inp'); const it=[...mm.querySelectorAll('.item')]; if (inp) { it.find(b=>b.textContent.startsWith('決定')).click(); return 'prompt'; }
    const t=(mm.querySelector('.title')||{}).textContent||''; const by=s=>it.find(b=>b.textContent.startsWith(s));
    if (t.startsWith('役場')||t.startsWith('総務部')||t.startsWith('保健センター')) { (mm.querySelector('.cancel')||by('もどる')).click(); return 'office-x'; }
    if (t.includes('のこうどう') && by('とくぎ') && Math.random() < .35) { by('とくぎ').click(); return 'skill'; }
    if (t === 'とくぎ') { const k = by('見立て') || it[0]; k.click(); return 'skill2'; }
    const c = by('はじめから')||by('説明を聞く')||by('たたかう')||by('事件の現場に入る')||by('現場へ向かう')||by('作戦会議をする')||it.find(b=>!b.classList.contains('off')&&!b.classList.contains('cancel'));
    if (c) { c.click(); return 'menu:'+t.slice(0,10); } }
  return 'idle'; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        cx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
        await cx.add_init_script("window.setTimeout = ((st) => (f, ms, ...a) => st(f, Math.min(ms||0, 5), ...a))(window.setTimeout);")
        pg = await cx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text) if m.type == 'error' and '404' not in m.text else None)
        await pg.goto(f'http://localhost:{PORT}/index.html'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/tmp/e_title.png')
        cnt = {}
        async def run(n, until=None):
            for i in range(n):
                r = await pg.evaluate(STEP, 0); cnt[r] = cnt.get(r, 0) + 1
                if until and await pg.evaluate(until): return True
                await pg.wait_for_timeout(15)
            return False
        await run(30, "!!(window.__game.state) && !document.querySelector('#ui .msg') && !document.querySelector('#ui .menu')")
        print('opening done', await pg.evaluate("[window.__game.field.mapId, window.__game.state.flags]"))
        # 医務室へ
        await pg.evaluate("() => { const g=window.__game; g.field.busy=true; g.onEvent(g.world.maps.company.events[0]).then(()=>{g.field.busy=false; window.__d1=true;}); }")
        await run(300, "window.__d1===true")
        print('tutorial', await pg.evaluate("JSON.stringify([window.__game.state.flags, window.__game.state.items])"))
        await pg.screenshot(path='/tmp/e_after_tut.png')
        # 草原→町
        await pg.evaluate("() => { const g=window.__game; g.field.busy=true; g.onEvent({type:'exit',to:'yume1',tx:9,ty:16}).then(()=>{window.__d2=true; g.field.busy=false;}); }")
        await run(50, "window.__d2===true")
        await pg.evaluate("() => { const g=window.__game; g.field.busy=true; g.onEvent({type:'exit',to:'tS1',tx:8,ty:14}).then(()=>{window.__d3=true; g.field.busy=false;}); }")
        await run(50, "window.__d3===true")
        await pg.screenshot(path='/tmp/e_town.png')
        # 保健センター（仲間）
        await pg.evaluate("() => { const g=window.__game; g.field.busy=true; g.onEvent({type:'building',id:'office',x:8,y:3}).then(()=>{window.__d4=true; g.field.busy=false;}); }")
        await run(80, "window.__d4===true")
        print('party', await pg.evaluate("window.__game.state.party"))
        # 現場1
        await pg.evaluate("() => { const g=window.__game; g.field.busy=true; g.stage('S1-1').then(r=>{window.__d5=true; g.field.busy=false;}); }")
        await run(25); await pg.screenshot(path='/tmp/e_battle.png')
        ok = await run(900, "window.__d5===true")
        await pg.screenshot(path='/tmp/e_stage.png')
        print('stage1', ok, await pg.evaluate("JSON.stringify(window.__game.state.cleared)"), await pg.evaluate("window.__game.state.skills"))
        for sid in ['S1-2', 'S1-3', 'S1-4']:
            await pg.evaluate("(sid) => { const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.stage(sid).then(()=>{window.__dd=true; g.field.busy=false;}); }", sid)
            ok = await run(1500, "window.__dd===true"); print(sid, ok, await pg.evaluate("JSON.stringify(window.__game.state.cleared)"))
        for i in range(12):
            m = await pg.evaluate("window.__game.meter('S1').pct")
            if m >= 80: break
            await pg.evaluate("() => { const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.train('S1').then(()=>{window.__dd=true; g.field.busy=false;}); }")
            await run(1500, "window.__dd===true")
        print('meter', await pg.evaluate("JSON.stringify(window.__game.meter('S1'))"))
        await pg.evaluate("() => { const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.stage('S1-boss').then(()=>{window.__dd=true; g.field.busy=false;}); }")
        await run(40); await pg.screenshot(path='/tmp/e_boss.png')
        ok = await run(2500, "window.__dd===true"); print('boss', ok, await pg.evaluate("JSON.stringify([window.__game.state.cleared, window.__game.state.flags])"))
        for T, fld in [('S2', 'yume2')]:
            for to in [fld, 't' + T]:
                await pg.evaluate("(to) => { const g=window.__game; window.__dd=false; g.field.busy=true; g.onEvent({type:'exit',to,tx:9,ty:14}).then(()=>{window.__dd=true; g.field.busy=false;}); }", to)
                await run(80, "window.__dd===true")
            for k in ['1', '2', '3', '4']:
                sid = T + '-' + k
                await pg.evaluate("(sid) => { const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.stage(sid).then(()=>{window.__dd=true; g.field.busy=false;}); }", sid)
                ok = await run(1500, "window.__dd===true"); print(sid, ok)
            for i in range(14):
                if await pg.evaluate(f"window.__game.meter('{T}').pct") >= 80: break
                await pg.evaluate(f"() => {{ const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.train('{T}').then(()=>{{window.__dd=true; g.field.busy=false;}}); }}")
                await run(1500, "window.__dd===true")
            await pg.evaluate(f"() => {{ const g=window.__game; g.healAll(); window.__dd=false; g.field.busy=true; g.stage('{T}-boss').then(()=>{{window.__dd=true; g.field.busy=false;}}); }}")
            await run(40); await pg.screenshot(path=f'/tmp/e_boss_{T}.png')
            ok = await run(2500, "window.__dd===true"); print(T, 'boss', ok, await pg.evaluate("JSON.stringify(window.__game.state.cleared)"))
        print('steps', cnt, await pg.evaluate("document.getElementById('ui').innerText.slice(0,200)"))
        print('noq', await pg.evaluate('window.__noq||[]'))
        print('\n'.join(errs) or 'no errors')
        await b.close()
asyncio.run(main())
