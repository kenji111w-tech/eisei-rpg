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
field('yume4', 'field2', '働く人の国 西の高原', 'tS3', (16, 8), 'tS4', ['nyuron', 'jiritsu', 'pinboke', 'kinniku', 'jinzou', 'hormon', 'taion', 'yofukashi'], '← シンケイの町', 'リズムの町')
town('tS4', 'town5', 'S4', 'リズムの町', 'yume4', 'yume5', back_label='草原をぬけて、シンケイの町へ', fwd_label='ルールの城へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['もう何日も、夜に眠れないんだ。', '昼間は頭がぼんやりして、仕事にならないよ。'], aiko='S4'),
    dict(x=12, y=10, look='villager2', talk=['町の大時計が、昼と夜をでたらめに鳴らすようになった。', 'あれじゃ、体のリズムがくるっちまう。']),
    dict(x=6, y=13, look='child', talk=['夜中に、黒い馬が町を走っていくのを見たよ！ ひづめの音がしなかったの。']),
])
field('yume5', 'field3', '働く人の国 ルールの国ざかい', 'tS4', (16, 7), 'tK1', ['jinzou', 'hormon', 'taion', 'yofukashi', 'kuseki', 'mujunkai', 'hatarakanai', 'iinkai'], '← リズムの町', 'センニンの城下町')
town('tK1', 'town6', 'K1', 'センニンの城下町', 'yume5', 'yume6', office='城の役所', bgm='town_law', back_label='国ざかいをぬけて、リズムの町へ', fwd_label='ケンシンの城下町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['この城には、もう何年も、だれも役人がいないんだ。', '席は空っぽのまま。だれが何をするのか、だれも知らない。'], aiko='K1'),
    dict(x=12, y=10, look='villager2', talk=['城の会議室には、ほこりがつもっている。', '「話し合いなんて時間のむだだ」って、王さまが言ったそうだ。']),
    dict(x=6, y=13, look='child', talk=['王さまのイスに、王冠をかぶった、だらしない大男がすわってたよ！']),
])
field('yume6', 'field2', '働く人の国 ルールの街道', 'tK1', (16, 8), 'tK2', ['kuseki', 'mujunkai', 'hatarakanai', 'iinkai', 'kenwasure', 'shinyagyo', 'karuteyabu', 'choujikan'], '← センニンの城下町', 'ケンシンの城下町')
town('tK2', 'town7', 'K2', 'ケンシンの城下町', 'yume6', 'yume7', office='城の役所', back_label='街道をぬけて、センニンの城下町へ', fwd_label='ジムショの城下町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['この町じゃ、もう何年も健康診断をしていないんだ。', '自分の体がどうなってるのか、だれもわからない。'], aiko='K2'),
    dict(x=12, y=10, look='villager2', talk=['毎晩おそくまで働かされて、へとへとだよ。', '相談しようにも、だれに言えばいいのか……。']),
    dict(x=6, y=13, look='child', talk=['夜中に、ガイコツの魔法使いが、病院の書類を燃やしてたよ！']),
])
field('yume7', 'field3', '働く人の国 ルールの丘', 'tK2', (16, 7), 'tK3', ['kenwasure', 'shinyagyo', 'karuteyabu', 'choujikan', 'gyuugyuu', 'kuchou', 'kurayami', 'benjo'], '← ケンシンの城下町', 'ジムショの城下町')
town('tK3', 'town8', 'K3', 'ジムショの城下町', 'yume7', 'yume8', office='城の役所', back_label='丘をぬけて、ケンシンの城下町へ', fwd_label='ロウキの城下町へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['事務所が、ぎゅうぎゅうづめで息苦しいんだ。', '窓も開かないし、頭が痛くなってくる。'], aiko='K3'),
    dict(x=12, y=10, look='villager2', talk=['照明は切れたまま、そうじもしない。', 'トイレの前には、いつも長い行列さ。']),
    dict(x=6, y=13, look='child', talk=['地下室から、カビくさいにおいがするよ！ 何か大きいのが動いてた！']),
])
field('yume8', 'field2', '働く人の国 ルールの谷', 'tK3', (16, 8), 'tK4', ['gyuugyuu', 'kuchou', 'kurayami', 'benjo', 'yasumasen', 'zangyou', 'yuukyuu', 'kisoku'], '← ジムショの城下町', 'ロウキの城下町')
town('tK4', 'town9', 'K4', 'ロウキの城下町', 'yume8', 'yume9', office='城の役所', back_label='谷をぬけて、ジムショの城下町へ', fwd_label='カンキョウの森へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['朝から晩まで、休みなしで働かされてるんだ。', '昼ごはんを食べるひまもない。'], aiko='K4'),
    dict(x=12, y=10, look='villager2', talk=['有給休暇？ そんなもの、とったことがないね。', '妻は妊娠中なのに、夜中まで働かされている……。']),
    dict(x=6, y=13, look='child', talk=['お城の時計台に、マントを着た伯爵がいて、時計の針を止めてたよ！']),
])
field('yume9', 'field3', '働く人の国 森の入口', 'tK4', (16, 7), 'tE1', ['yasumasen', 'zangyou', 'yuukyuu', 'kisoku', 'mushiatsu', 'atsusa', 'mabushi', 'yodomi'], '← ロウキの城下町', 'カンキョウの森の里')
town('tE1', 'town10', 'E1', 'カンキョウの森の里', 'yume9', 'yume10', office='森の管理小屋', bgm='town_chem', back_label='森の入口をぬけて、ロウキの城下町へ', fwd_label='デスクの森の里へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['里の作業小屋が、むしむしして息苦しいんだ。', 'まぶしいのに、手もとは暗い。目がしょぼしょぼするよ。'], aiko='E1'),
    dict(x=12, y=10, look='villager2', talk=['夏になると、仕事中にたおれる人が出るんだ。', '水を飲むひまも、休むひまもないってさ。']),
    dict(x=6, y=13, look='child', talk=['森のおくの沼から、白いゆげがもくもく出てるの。何か大きいのがいるよ！']),
])
field('yume10', 'field2', '働く人の国 森の小道', 'tE1', (16, 8), 'tE2', ['mushiatsu', 'atsusa', 'mabushi', 'yodomi', 'gansei', 'katakori', 'youtsuu', 'fukai'], '← カンキョウの森の里', 'デスクの森の里')
town('tE2', 'town11', 'E2', 'デスクの森の里', 'yume10', 'yume11', office='森の管理小屋', bgm='town_chem', back_label='小道をぬけて、カンキョウの森の里へ', fwd_label='ゲンキの森の里へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['一日中、画面を見ていて目がしょぼしょぼする。', '肩も首もがちがちだよ。'], aiko='E2'),
    dict(x=12, y=10, look='villager2', talk=['重い木箱を、ひとりで持ち上げさせられて、腰を痛めたんだ。', '休む場所も、着がえる場所もない。']),
    dict(x=6, y=13, look='child', talk=['大きなヘビが、背中をまるめて森の大木にまきついてたよ！']),
])
field('yume11', 'field3', '働く人の国 森の奥の道', 'tE2', (16, 7), 'tE3', ['gansei', 'katakori', 'youtsuu', 'fukai'], '← デスクの森の里', 'ゲンキの森の里')
town('tE3', 'town12', 'E3', 'ゲンキの森の里', 'yume11', 'yume12', office='森の管理小屋', bgm='town_chem', back_label='森の奥の道をぬけて、デスクの森の里へ', fwd_label='キュウキュウの森の里へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['なんだか、毎日気持ちが重くてね……。', 'だれに相談したらいいのか、わからないんだ。'], aiko='E3'),
    dict(x=12, y=10, look='villager2', talk=['休け所が、たばこの煙でもうもうなんだ。', '吸わない人も、せきが止まらないよ。']),
    dict(x=6, y=13, look='child', talk=['黒いずきんの人が、大きな袋をかついで、古い蔵に入っていったよ！']),
])
field('yume12', 'field2', '働く人の国 森の沢', 'tE3', (16, 8), 'tE4', ['utsuutsu', 'gorone', 'kemuri', 'gomakashi'], '← ゲンキの森の里', 'キュウキュウの森の里')
# town3 には東の出口がないので、11行目に東への道と出口・看板を足す
_t3 = BASE['town3']
_r = _t3['tiles'][11]
_t3['tiles'][11] = (_r[:8] + '=' * 10) if isinstance(_r, str) else (_r[:8] + ['='] * 10)
_t3['events'] = [e for e in _t3['events'] if not (e['type'] == 'building' and e['id'] == 'koshujo')] + [dict(x=17, y=11, type='exit', to='x'), dict(x=16, y=10, type='sign', label='→東', text='')]
town('tE4', 'town3', 'E4', 'キュウキュウの森の里', 'yume12', 'yume13', office='森の管理小屋', bgm='town_chem', back_label='沢ぞいに、ゲンキの森の里へ', fwd_label='工場の国へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['食堂で食べたら、みんなおなかをこわしたんだ。', '卵料理と、作り置きの煮物があやしい……。'], aiko='E4'),
    dict(x=12, y=10, look='villager2', talk=['広場で人がたおれたのに、だれも何をしたらいいかわからなかった。', 'AEDって、どう使うんだい？']),
    dict(x=6, y=13, look='child', talk=['とんがり帽子のおばあさんが、森の奥で大きなお鍋をかきまぜてたよ！']),
])
field('yume13', 'field4', '働く人の国 工場の国ざかい', 'tE4', (16, 11), 'tY1', ['dokutamago', 'noronoro', 'battari', 'houtai'], '← キュウキュウの森の里', 'カガクの鉱山')
town('tY1', 'town2', 'Y1', 'カガクの鉱山', 'yume13', 'yume14', office='鉱山の事務所', bgm='town_chem', back_label='国ざかいをぬけて、キュウキュウの森の里へ', fwd_label='フンジンの鉱山へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['坑道に入ると、頭がくらくらするんだ。', '手足もしびれてきた……。'], aiko='Y1'),
    dict(x=12, y=10, look='villager2', talk=['精錬所の仲間が、おなかが痛いと言ってたおれた。', '顔色も、ずっと悪いんだ。']),
    dict(x=6, y=13, look='child', talk=['鉱山の奥に、首がいっぱいある大きなヘビがいるんだって！']),
])
field('yume14', 'field3', '働く人の国 坑道ぞいの道', 'tY1', (16, 8), 'tY2', ['yuuki', 'namari', 'gasumore', 'joutai'], '← カガクの鉱山', 'フンジンの鉱山')
town('tY2', 'town4', 'Y2', 'フンジンの鉱山', 'yume14', 'yume15', office='鉱山の事務所', bgm='town_chem', back_label='坑道ぞいに、カガクの鉱山へ', fwd_label='ブツリの鉱山へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['何十年も石を切ってきたら、息が苦しくなってな……。', '今はもう、少し歩くだけで息切れだ。'], aiko='Y2'),
    dict(x=12, y=10, look='villager2', talk=['たて穴に落ちた仲間を助けに入ったやつまで、たおれちまった。', '穴の中には、何もないように見えたのに……。']),
    dict(x=6, y=13, look='child', talk=['山のてっぺんに、砂でできた大きな人がいるんだよ！']),
])
field('yume15', 'field2', '働く人の国 谷ぞいの道', 'tY2', (16, 8), 'tY3', ['jinpai', 'keisand', 'sanketsu', 'chissoboss'], '← フンジンの鉱山', 'ブツリの鉱山')
town('tY3', 'town5', 'Y3', 'ブツリの鉱山', 'yume15', 'yume16', office='鉱山の事務所', bgm='town_chem', back_label='谷ぞいに、フンジンの鉱山へ', fwd_label='タイサクの鉱山へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['え？ なんだって？ ……最近、高い音が聞こえにくくてな。', '機械の音には、もうなれたと思ってたんだが。'], aiko='Y3'),
    dict(x=12, y=10, look='villager2', talk=['寒い朝になると、指が真っ白になるんだ。', 'ドリルを毎日にぎってるせいかな……。']),
    dict(x=6, y=13, look='child', talk=['谷底に、角のはえた大きなけものがいるんだって！ 機械をバリバリ食べてるの！']),
])
field('yume16', 'field3', '働く人の国 峠道', 'tY3', (16, 7), 'tY4', ['souon', 'shindou', 'housha', 'genatsu'], '← ブツリの鉱山', 'タイサクの鉱山')
town('tY4', 'town6', 'Y4', 'タイサクの鉱山', 'yume16', 'yume17', office='測定事務所', bgm='town_chem', back_label='峠道をぬけて、ブツリの鉱山へ', fwd_label='キセイの砦へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['局所排気装置が止まってから、工場の中がけむたくてな。', 'マスクも、どれを使えばいいのかわからないんだ。'], aiko='Y4'),
    dict(x=12, y=10, look='villager2', talk=['特殊健康診断？ ここ何年も受けてないよ。', '記録も、どこにあるのやら。']),
    dict(x=6, y=13, look='child', talk=['大きな煙突のてっぺんに、黒いドラゴンがいるよ！']),
])
field('yume17', 'field2', '働く人の国 法令の川', 'tY4', (16, 8), 'tZ1', ['hakarazu', 'gyakufuu', 'nomask', 'mimic'], '← タイサクの鉱山', 'キセイの砦')
town('tZ1', 'town7', 'Z1', 'キセイの砦', 'yume17', 'yume18', office='砦の詰所', back_label='法令の川をこえて、タイサクの鉱山へ', fwd_label='ソクの砦へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['作業主任者？ そんな人、もう何年も見てないな。', '危ない作業も、みんな勝手にやってるよ。'], aiko='Z1'),
    dict(x=12, y=10, look='villager2', talk=['このびん、ラベルがはがれてて、中身がわからないんだ。', 'SDS？ なんだい、それは。']),
    dict(x=6, y=13, look='child', talk=['夜になると、よろいの将軍が天守に上っていくんだよ！']),
])
field('yume18', 'field3', '働く人の国 砦の堀', 'tZ1', (16, 7), 'tZ2', ['fuzai', 'mukyouiku', 'yamiseizou', 'nolabel'], '← キセイの砦', 'ソクの砦')
town('tZ2', 'town8', 'Z2', 'ソクの砦', 'yume18', 'yume19', office='砦の詰所', back_label='堀ぞいに、キセイの砦へ', fwd_label='ケンコウの砦へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['塗装場の換気扇が止まってて、頭がくらくらするんだ。', '有機溶剤の掲示も、だれかにはがされてた。'], aiko='Z2'),
    dict(x=12, y=10, look='villager2', talk=['穴ぐらの作業、測定もしないで入らされるんだ。', '見張りもいないし、こわくてしかたない。']),
    dict(x=6, y=13, look='child', talk=['中庭に、首が4つあるおっきな獣がいるよ！ 本をむしゃむしゃ食べてた！']),
])
field('yume19', 'field2', '働く人の国 城壁の道', 'tZ2', (16, 8), 'tZ3', ['penkiya', 'tokkasasori', 'anagura', 'hibaku'], '← ソクの砦', 'ケンコウの砦')
town('tZ3', 'town9', 'Z3', 'ケンコウの砦', 'yume19', None, office='砦の詰所', back_label='城壁ぞいに、ソクの砦へ', npcs=[
    dict(x=5, y=5, look='villager', talk=['特殊健康診断の報告書が、どこかに消えちまったんだ。', '測定器も、何年も動いてない。'], aiko='Z3'),
    dict(x=12, y=10, look='villager2', talk=['坑道の仕事で、毎日4時間も5時間も残業だ。', '体じゅうが粉まみれで、息が苦しい……。']),
    dict(x=6, y=13, look='child', talk=['砦のいちばん上に、黒いスーツの社長がいるんだって！ 夜中もずっと明かりがついてるよ！']),
])
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
        kanki=dict(id='kanki', name='カンキ', lv=20, hp=110, mhp=110, mp=40, mmp=40, atk=26, def_=20, bonusPrefix='EY'),
        sokutei=dict(id='sokutei', name='ソクテイ', lv=24, hp=120, mhp=120, mp=50, mmp=50, atk=27, def_=21, bonusPrefix='YE'),
        houki=dict(id='houki', name='ホウキ', lv=12, hp=70, mhp=70, mp=30, mmp=30, atk=18, def_=13, bonusPrefix='KZ'),
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
