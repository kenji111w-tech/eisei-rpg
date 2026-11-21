# 用語チェック：会話（授業）の中で、用語が説明される前に使われていないかを調べる
import json, sys
w = json.load(open('data/world.json'))
TOWNS = ['S1', 'S2', 'S3', 'S4', 'K1', 'K2', 'K3', 'K4', 'E1', 'E2', 'E3', 'E4', 'Y1', 'Y2', 'Y3', 'Y4', 'Z1', 'Z2', 'Z3']
keys = sorted(w['stages'], key=lambda s: (TOWNS.index(s.split('-')[0]), 9 if s.endswith('boss') else int(s.split('-')[1])))
# 用語 → その意味を説明するステージ（そこより前に出てきたら警告）
DEF = {
 'WBGT': 'E1-2', '必要換気量': 'E1-4', '情報機器作業': 'E2-1', 'ポピュレーションアプローチ': 'E3-2', '度数率': 'E3-4',
 '有機溶剤': 'Y1-1', 'ヒューム': 'Y1-2', 'じん肺': 'Y2-1', '酸素欠乏': 'Y2-3', '管理濃度': 'Y4-1', '局所排気装置': 'Y2-2',
 '作業主任者': 'Z1-1', '特別教育': 'Z1-2', 'SDS': 'Z1-4', '管理区域': 'Z2-4',
}
bad = 0
for term, dk in DEF.items():
    di = keys.index(dk)
    for k in keys[:di]:
        for who, t in (w['stages'][k].get('lesson') or []):
            if term in t:
                print(f'説明前に使用：「{term}」 {k}（説明は{dk}）: {t[:60]}'); bad += 1
    # 説明するステージに用語が本当に出てくるか
    if not any(term in t for _, t in (w['stages'][dk].get('lesson') or [])):
        print(f'説明ステージに用語がない：「{term}」 {dk}'); bad += 1
print('用語の先出し：', bad)
sys.exit(1 if bad else 0)
