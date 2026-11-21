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
def town(mid, base, tid, name, back, fwd, office='保健センター', bgm='town_law', npcs=(), back_label='', fwd_label='', fwd_need=True):
    """乙4の町の地図を借りて、町をつくる。back＝南の出口の行き先、fwd＝東の出口の行き先"""
    B = BASE[base]; ev = []; old = None
    for e in B['events']:
        e = dict(e)
        if e['type'] == 'stage':
            old = old or e['id'].split('-')[0]; e['id'] = tid + '-' + e['id'].split('-')[1]
        elif e['type'] == 'exit' and e['y'] >= 14: e['to'] = back; e['tx'], e['ty'] = e['x'] + 1, 2
        elif e['type'] == 'exit':
            if not fwd: continue
            e['to'] = fwd; e['tx'], e['ty'] = 1, 8
            if fwd_need: e.update(need=tid + '-boss', needmsg='（東の道は、町の事件が片づくまで通れないようだ）')
            else: e.pop('need', None); e.pop('needmsg', None)
        elif e['type'] == 'building' and e['id'] == 'office': e['label'] = office
        elif e['type'] == 'building' and e['id'] not in ('inn', 'shop', 'office'): continue
        elif e['type'] == 'sign':
            if '南' in e['label']: e.update(label='↓南 草原', text='看板：「↓ 南の出口　' + back_label + '」')
            elif fwd: e.update(label='→東', text='看板：「→ 東の出口　' + fwd_label + '（町の事件を解決すると通れる）」')
            else: continue
        ev.append(e)
    MAPS[mid] = dict(name=name, tiles=tiles(base), encounter=False, bgm=bgm, events=ev, npcs=list(npcs))

def field(mid, base, name, back, back_xy, fwd, wild, back_label, fwd_label):
    """乙4の草原の地図を借りる。西（または南）の出口＝back、北の出口＝fwd"""
    B = BASE[base]; ev = []
    for e in B['events']:
        e = dict(e)
        if e['type'] == 'stage': continue
        if e['type'] == 'exit':
            if e['y'] <= 1: e['to'] = fwd; e['tx'], e['ty'] = (8 if e['x'] == 9 else 9), 14
            else: e['to'] = back; e['tx'], e['ty'] = back_xy
            if 'need' in e: continue
        if e['type'] == 'sign':
            if e['y'] <= 2: e['text'] = '看板：「↑ ' + fwd_label + '」'; e['label'] = '↑' + fwd_label[:5]
            elif e['label'].startswith('→'): continue
            else: e['text'] = '看板：「' + back_label + '」'
        ev.append(e)
    MAPS[mid] = dict(name=name, tiles=tiles(base), encounter=True, bgm='field', wild=wild, wildPre=wild[:1], events=ev, npcs=[])

# ---- 第1部 からだの国（労働生理） ----
town('tS1', 'town1', 'S1', 'ミャクの町', 'yume1', 'yume2', back_label='草原をぬけて、会社へもどる', fwd_label='イキの町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['朝から、めまいと息切れがひどくて……。', '顔色が悪いって、みんなに言われるんだ。'], aiko='S1'),
    dict(x=11, y=9, look='villager2', talk=['町の赤い川が、どんどん細くなっている。', '川の水が減ると、町じゅうに物が届かなくなるんだ。']),
    dict(x=6, y=12, look='child', talk=['夜になると、黒いマントの人が屋根の上を飛んでるよ！']),
])
field('yume2', 'field2', '働く人の国 東の街道', 'tS1', (16, 7), 'tS2', ['hemato', 'shinzou', 'mumeneki', 'katamarazu', 'ikitome', 'kamado', 'shoukaf', 'kanzou'], '← ミャクの町', 'イキの町')
town('tS2', 'town2', 'S2', 'イキの町', 'yume2', 'yume3', back_label='草原をぬけて、ミャクの町へ', fwd_label='シンケイの町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['丘の風車が止まってから、町の空気がよどんでる。', '階段をのぼるだけで、息が切れちまうよ。'], aiko='S2'),
    dict(x=11, y=10, look='villager2', talk=['市場の食べ物が、毎晩ごっそり消えるんだ。', '倉庫の砂糖の袋まで、からっぽさ。']),
    dict(x=6, y=13, look='child', talk=['夜、北の洞くつから、ごうごうって大きな寝息が聞こえるの！']),
])
field('yume3', 'field3', '働く人の国 北の街道', 'tS2', (16, 8), 'tS3', ['ikitome', 'kamado', 'shoukaf', 'kanzou', 'nyuron', 'jiritsu', 'pinboke', 'kinniku'], '← イキの町', 'シンケイの町')
town('tS3', 'town4', 'S3', 'シンケイの町', 'yume3', 'yume4', back_label='草原をぬけて、イキの町へ', fwd_label='リズムの町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['手足がしびれて、思うように動かないんだ。', '夕方になると、暗くて何も見えなくなる。'], aiko='S3'),
    dict(x=12, y=10, look='villager2', talk=['町じゅうに、細い白い糸が張りめぐらされている。', 'さわると、ぴりっとしびれるんだ。']),
    dict(x=6, y=13, look='child', talk=['時計台の上に、大きな8本足の影がいたよ！']),
])
field('yume4', 'field2', '働く人の国 西の高原', 'tS3', (16, 8), 'tS4', ['nyuron', 'jiritsu', 'pinboke', 'kinniku'], '← シンケイの町', 'リズムの町（準備中）')
for k, v in MAPS_EXTRA.items():
    if k in MAPS: MAPS[k].update(v)
# まだ作っていない町への出口は、看板に置きかえる（試作品）
for mid, M in MAPS.items():
    keep = []
    for e in M['events']:
        if e['type'] == 'exit' and e['to'] not in MAPS: e = dict(x=e['x'], y=e['y'] + (1 if e['y'] <= 1 else 0), type='sign', label='準備中', text='この先は、まだ準備中です。――試作品は、ここまでです。')
        keep.append(e)
    M['events'] = keep

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
