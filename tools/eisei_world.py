# 衛生管理者RPGの世界データ（data/world.json）を作る
# 地図の形は乙4 RPGの地図（tools/base_maps.json）を借りて、名前・出来事・人を入れ替える
import json, os, copy
H = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(H, 'base_maps.json')))
from eisei_story import STORY, STAGES, ENEMIES, SKILLS, MYSTERIES, MAPS_EXTRA

def tiles(k): return copy.deepcopy(BASE[k]['tiles'])

MAPS = {}
# ---- 会社（はじまりの場所） ----
MAPS['company'] = dict(name='ハタラク商事', tiles=tiles('village'), encounter=False, bgm='village', events=[
    dict(x=3, y=4, type='building', id='mentor', label='医務室'),
    dict(x=12, y=4, type='building', id='office', label='総務部'),
    dict(x=3, y=10, type='building', id='inn', label='休憩室', price=0),
    dict(x=12, y=10, type='building', id='shop', label='売店'),
    dict(x=7, y=0, type='exit', to='yume1', tx=9, ty=16), dict(x=8, y=0, type='exit', to='yume1', tx=10, ty=16),
    dict(x=6, y=1, type='sign', label='↑北 ふしぎな扉', text='看板：「↑ 北の扉　この先、関係者以外立入禁止（？）」'),
], npcs=[
    dict(x=5, y=7, look='villager', talk=['最近、なんだか疲れが取れなくて……。', '夢の中で、魔物に追いかけられるんだ。'], aiko='V0'),
    dict(x=10, y=12, look='child', talk=['ミマモリ先生は医務室にいるよ！', '昔は大きな工場の産業医だったんだって！']),
    dict(x=13, y=7, look='villager2', talk=['うちの会社、もうすぐ社員が50人を超えるらしい。', '人が増えると、決まりごとも増えるんだってさ。']),
])
# ---- 働く人の国：草原 ----
MAPS['yume1'] = dict(name='働く人の国 はじまりの草原', tiles=tiles('field'), encounter=True, bgm='field', wild=['tsukare', 'hemato', 'shinzou', 'mumeneki', 'katamarazu'], wildPre=['tsukare'], events=[
    dict(x=9, y=1, type='exit', to='tS1', tx=8, ty=14), dict(x=10, y=1, type='exit', to='tS1', tx=9, ty=14),
    dict(x=9, y=16, type='exit', to='company', tx=7, ty=1), dict(x=10, y=16, type='exit', to='company', tx=8, ty=1),
    dict(x=11, y=15, type='sign', label='↓会社', text='看板：「↓ ハタラク商事（医務室の扉）」'),
    dict(x=11, y=2, type='sign', label='↑町', text='看板：「↑ ミャクの町（からだの国）」'),
], npcs=[])
# ---- ミャクの町（労働生理：血液・循環・免疫） ----
t1 = BASE['town1']
ev = []
for e in t1['events']:
    e = dict(e)
    if e['type'] == 'stage': e['id'] = e['id'].replace('L1', 'S1')
    if e['type'] == 'exit' and e['to'] == 'field': e['to'] = 'yume1'
    if e['type'] == 'exit' and e['to'] == 'field2': e.update(to='yume2', need='S1-boss', needmsg='（町の東の道は、町の事件が片づくまで通れないようだ）')
    if e['type'] == 'building' and e['id'] == 'office': e['label'] = '保健センター'
    if e['type'] == 'sign':
        if '南' in e['label']: e.update(label='↓南 草原', text='看板：「↓ 南の出口　草原をぬけて、会社へもどる」')
        else: e.update(label='→東 イキの町', text='看板：「→ 東の出口　イキの町へ（町の事件を解決すると通れる）」')
    ev.append(e)
MAPS['tS1'] = dict(name='ミャクの町', tiles=tiles('town1'), encounter=False, bgm='town_law', events=ev, npcs=[
    dict(x=5, y=5, look='villager', talk=['朝から、めまいと息切れがひどくて……。', '顔色が悪いって、みんなに言われるんだ。'], aiko='S1'),
    dict(x=11, y=9, look='villager2', talk=['町の赤い川が、どんどん細くなっている。', '川の水が減ると、町じゅうに物が届かなくなるんだ。']),
    dict(x=6, y=12, look='child', talk=['夜になると、黒いマントの人が屋根の上を飛んでるよ！']),
])
# ---- 次の草原（試作品ではここまで） ----
MAPS['yume2'] = dict(name='働く人の国 東の街道', tiles=tiles('field2'), encounter=False, bgm='field', events=[
    dict(x=0, y=8, type='exit', to='tS1', tx=16, ty=7),
    dict(x=1, y=7, type='sign', label='←町', text='看板：「← ミャクの町」'),
    dict(x=11, y=2, type='sign', label='↑イキの町', text='看板：「↑ イキの町（準備中）」　――試作品は、ここまでです。'),
], npcs=[])
for k, v in MAPS_EXTRA.items(): MAPS[k].update(v)

W = dict(
    maps=MAPS,
    start=dict(map='company', x=7, y=12, night=False, inn=dict(map='company', x=3, y=11)),
    base=dict(
        hero=dict(id='hero', name='ユウ', lv=1, hp=30, mhp=30, mp=8, mmp=8, atk=9, def_=4),
        seiri=dict(id='seiri', name='セイリ', lv=1, hp=26, mhp=26, mp=10, mmp=10, atk=7, def_=5, bonusPrefix='S'),
    ),
    memberNames=dict(hero='主人公', seiri='セイリ', houki='ホウキ', kanki='カンキ', sokutei='ソクテイ'),
    subjectByPrefix=dict(S='労働生理', K='関係法令', E='労働衛生', Y='労働衛生（有害）', Z='関係法令（有害）', V='導入', T='導入'),
    chapterOf=dict(S=1, K=2, E=3, Y=4, Z=5),
    stages=STAGES, enemies=ENEMIES, skills=SKILLS, mysteries=MYSTERIES, story=STORY,
    items={
        'yakusou': dict(name='やくそう', price=8, desc='味方1人のHPを15回復'),
        'mizu': dict(name='まほうのみず', price=15, desc='味方1人のMPを5回復'),
        'jouyaku': dict(name='上やくそう', price=0, desc='味方1人のHPを40回復（知恵の釜で作る）'),
        'keshi': dict(name='けしけし草', price=0, desc='問題に答える時に使うと、まちがいの選択肢を消す（5択は2つ、3択は1つ）。ヒントを使ったあつかいになる（知恵の釜で作る）'),
    },
    recipes={'keshi': dict(need=[['yakusou', 2]]), 'jouyaku': dict(need=[['yakusou', 2], ['mizu', 1]])},
)
# def は Python の予約語なので def_ と書いて、ここで直す
for m in W['base'].values(): m['def'] = m.pop('def_')
json.dump(W, open(os.path.join(H, '..', 'data', 'world.json'), 'w'), ensure_ascii=False, indent=1)
print('maps', len(MAPS), 'stages', len(STAGES), 'enemies', len(ENEMIES))
