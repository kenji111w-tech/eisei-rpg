# 試験センターのテスト：物語クリア済みとして、指定の模試を最後まで解き、採点結果を表示する
# 使い方：python3 tools/examtest.py 本番模試（第一種   （メニューの文字の一部を渡す）
import asyncio, sys
from playwright.async_api import async_playwright
WANT = sys.argv[1] if len(sys.argv) > 1 else '本番模試（第一種'
CORRECT = len(sys.argv) > 2  # 2つ目の引数があれば、正解を選ぶ
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = await ctx.new_page()
        print('start', flush=True); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8766/index.html'); await pg.wait_for_function('window.__game && window.__game.questions && window.__game.questions.length > 0', timeout=20000)
        # 物語クリア済みの記録を置いてから開き直し、タイトルの「試験センター」から入る
        await pg.evaluate("() => { const g = window.__game, s = g.newState('テスト'); s.flags.cleared = true; localStorage.setItem('eiseirpg:game', JSON.stringify(s)); }")
        pg.on('dialog', lambda d: asyncio.ensure_future(d.accept())); await pg.goto('http://localhost:8766/index.html'); await pg.wait_for_function('window.__game && window.__game.questions && window.__game.questions.length > 0', timeout=20000)
        await pg.evaluate("() => window.__ex = false")
        await pg.wait_for_selector('#ui .menu .item'); its = await pg.query_selector_all('#ui .menu .item')
        for it in its:
            if '試験センター' in await it.inner_text(): await it.click(); break
        texts = []; picked = False; n = 0
        for step in range(3000):
            if step > 50 and await pg.evaluate("[...document.querySelectorAll('#ui .menu .item')].some(i => /はじめから|つづきから/.test(i.textContent))"): break
            if await pg.query_selector('#ui .exam') and not await pg.query_selector('#ui .menu .item'):
                q = await pg.evaluate("""(c) => { const g = window.__game, t = document.querySelector('#ui .exam .qtext'); if (!t) return null;
                    const q = g.questions.find(x => x.question === t.textContent); const bs = [...document.querySelectorAll('#ui .exam .choices .choice')];
                    if (bs.length && !document.querySelector('#ui .exam .choice.sel')) { let k = 0; if (c && q) k = bs.findIndex(b => b.querySelector('.ct').textContent === q.choices[q.answer]); bs[Math.max(0, k)].click(); return 'ans'; }
                    const nx = [...document.querySelectorAll('#ui .exam .exnav .exbtn')].find(b => /次|一覧へ/.test(b.textContent)); if (nx) { nx.click(); return 'next'; } return null; }""", CORRECT)
                if q is None:
                    fin = await pg.query_selector('#ui .exam .exfin')
                    if fin: await fin.click()
                n += 1; continue
            items = await pg.query_selector_all('#ui .menu .item')
            if items:
                labels = [await i.inner_text() for i in items]
                idx = next((k for k, l in enumerate(labels) if WANT in l), None) if not picked else None
                if idx is not None: picked = True; await items[idx].evaluate('b => b.click()'); continue
                idx = next((k for k, l in enumerate(labels) if '始める' in l or '採点する' in l), None)
                if idx is not None: await items[idx].evaluate('b => b.click()'); continue
                print('menu?', labels); break
            m = await pg.query_selector('#ui .msg .txt')
            if m: texts.append(await m.inner_text()); await pg.mouse.click(200, 400); await pg.wait_for_timeout(130); continue
            await pg.wait_for_timeout(50)
        print('\n'.join(t for t in texts if '採点' in t or '合計' in t or '判定' in t or '：' in t and '／' in t)[:3000])
        print('errors', errs, await pg.evaluate('window.__exerr || null'))
        await b.close()
asyncio.run(main())
