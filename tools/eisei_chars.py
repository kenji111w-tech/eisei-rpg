# 仲間・ボスのうそ（data/characters.json）、合言葉（data/aikotoba.json）、出題範囲表（data/syllabus.json）を作る
import json, os
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, '..', 'data')
CH = dict(
    members=dict(
        seiri=dict(name='セイリ', role='労働生理の案内役（保健センターの看護師）', subject='労働生理', kuchiguse='からだは、しくみで覚えるの。',
            tips=['血液は「液体（血漿）55%」と「つぶ（有形成分）45%」。つぶは、運ぶ赤・守る白・止める血小板。',
                  '肺の血管は名前と中身が逆。肺動脈＝静脈血、肺静脈＝動脈血。全身へ送るのは左心室。',
                  '固まるのが「凝固」（フィブリノーゲン→フィブリン）、集まるのが「凝集」（血液型）。']),
        houki=dict(name='ホウキ', role='関係法令の案内役（総務の大先輩）', subject='関係法令', kuchiguse='数字は、人数・回数・期限の3つで覚えよ。', tips=['（準備中）']),
        kanki=dict(name='カンキ', role='労働衛生の案内役（ビル設備のおじさん）', subject='労働衛生', kuchiguse='空気と光と温度。職場は、まず環境だ。', tips=['（準備中）']),
        sokutei=dict(name='ソクテイ', role='有害業務の案内役（作業環境測定士の娘）', subject='労働衛生（有害）', kuchiguse='測って、比べて、対策する。', tips=['（準備中）']),
        roshi=dict(name='ドクター・ミマモリ', role='旅の師（会社の産業医）', subject='', kuchiguse='知っていれば、守れる。それが衛生管理者です。',
            tips=['問題は最後まで読みましょう。「誤っているもの」を選ぶ問題にご用心。',
                  '「すべて」「必ず」は疑いましょう。「〜ものがある」は、たいてい正しい。',
                  '合格は科目ごと40%以上・合計60%以上。苦手な科目を作らないことです。']),
    ),
    subjectMember={'労働生理': 'seiri', '関係法令': 'houki', '関係法令（有害）': 'houki', '労働衛生': 'kanki', '労働衛生（有害）': 'sokutei'},
    boss={'S2-boss': dict(lie='基礎代謝量とは、ぐっすり眠っているときに使うエネルギーのことだ！', who='セイリ', fix='基礎代謝量は、目覚めて横になり、安静にしているときの最小限のエネルギーよ。睡眠中ではないわ。'), 'S1-boss': dict(lie='肺動脈には、酸素たっぷりの動脈血が流れているのだ！', who='セイリ', fix='肺動脈に流れるのは静脈血。酸素の多い動脈血が流れるのは肺静脈よ。名前と中身が逆なの。')},
)
json.dump(CH, open(os.path.join(D, 'characters.json'), 'w'), ensure_ascii=False, indent=1)

AK = dict(tips=[
    dict(id='AK001', town='V0', topic='*', word='「すべて」「必ず」「いかなる場合も」「決して」', ans='言い切る言葉がある選択肢は、誤りのことが多い。例外が1つでもあれば誤りになるからだ。ただし言葉だけで決めず、中身も確かめよう。'),
    dict(id='AK002', town='V0', topic='*', word='「〜するものがある」「〜することがある」', ans='こういう言い方の選択肢は、正しいことが多い。1つでもあてはまれば正しいからだ。ただし中身も必ず確かめよう。'),
    dict(id='AK003', town='V0', topic='*', word='「誤っているものはどれか」', ans='問題の最後を必ず読む。正しいものを探す問題か、誤っているものを探す問題かで、答えが逆になる。'),
    dict(id='AK101', town='S1', topic='心臓と循環', word='「肺動脈」「肺静脈」', ans='肺の血管は名前と中身が逆。肺動脈＝静脈血、肺静脈＝動脈血。'),
    dict(id='AK102', town='S1', topic='凝固と凝集', word='「凝集原」「凝集素」', ans='これが出たら「凝集」（血液型）。「フィブリノーゲン」「フィブリン」が出たら「凝固」。'),
    dict(id='AK103', town='S1', topic='血液の成分', word='「ヘマトクリット」', ans='赤血球の容積の割合。男女差がある（男性約45%・女性約40%）。「男女差はない」は誤り。'),
    dict(id='AK104', town='S1', topic='免疫', word='「抗原」と「抗体」', ans='異物が抗原、体が作るたんぱく質（免疫グロブリン）が抗体。入れかえたら誤り。'),
    dict(id='AK201', town='S2', topic='代謝', word='「基礎代謝量」', ans='覚醒・横臥・安静時の最小限のエネルギー。「睡眠中」と出たら誤り。'),
    dict(id='AK202', town='S2', topic='代謝', word='「エネルギー代謝率」', ans='動的筋作業の強さの目安。「精神的作業」「静的筋作業」に使えるとあれば誤り。'),
    dict(id='AK203', town='S2', topic='栄養と消化', word='「胆汁」', ans='肝臓で作られ、消化酵素はふくまない。脂肪を乳化して消化を助ける。'),
    dict(id='AK204', town='S2', topic='肝臓', word='「インスリン」と「肝臓」', ans='インスリンを出すのは膵臓。肝臓の仕事として出てきたら誤り。'),
    dict(id='AK205', town='S2', topic='呼吸', word='「二酸化炭素が増えると」', ans='呼吸中枢（延髄）が刺激され、呼吸は深く速くなる。'),
], freq=['心臓と循環', '凝固と凝集', '免疫', '代謝', '栄養と消化', '肝臓'])
json.dump(AK, open(os.path.join(D, 'aikotoba.json'), 'w'), ensure_ascii=False, indent=1)

SY = dict(note='出題範囲を細かい項目に分けたプロジェクト独自のチェックリスト（公式の項目表ではない）。kid_prefixes に一致する knowledge_id の問題があれば網羅済みとみなす。', items=[
    dict(id='S-01', subject='労働生理', area='血液', item='血液の成分（血漿・赤血球・白血球・血小板）', kid_prefixes=['S1-BLD-']),
    dict(id='S-02', subject='労働生理', area='循環', item='心臓の構造と血液循環', kid_prefixes=['S1-CIR-']),
    dict(id='S-03', subject='労働生理', area='免疫', item='抗原・抗体、体液性免疫・細胞性免疫', kid_prefixes=['S1-IMM-']),
    dict(id='S-05', subject='労働生理', area='呼吸', item='呼吸のしくみ（呼吸筋・外呼吸と内呼吸・呼吸中枢）', kid_prefixes=['S2-RESP-']),
    dict(id='S-06', subject='労働生理', area='代謝', item='代謝・基礎代謝量・エネルギー代謝率', kid_prefixes=['S2-MET-']),
    dict(id='S-07', subject='労働生理', area='消化', item='栄養素の消化と吸収、胆汁', kid_prefixes=['S2-DIG-']),
    dict(id='S-08', subject='労働生理', area='肝臓', item='肝臓のはたらき', kid_prefixes=['S2-LIV-']),
    dict(id='S-04', subject='労働生理', area='血液', item='血液の凝固と凝集、血清', kid_prefixes=['S1-COAG', 'S1-AGGL', 'S1-SERUM']),
])
json.dump(SY, open(os.path.join(D, 'syllabus.json'), 'w'), ensure_ascii=False, indent=1)
print('ok')
