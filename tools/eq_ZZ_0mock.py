# 本番模試の専用問題（pool='mock'）。冒険では出ない初見の問題。1回分＝労働生理10・関係法令10・労働衛生10・労働衛生（有害）10・関係法令（有害）10
# 第二種の本番模試は前の3科目30問、第一種は 生理10・法令7・衛生7・有害の衛生10・有害の法令10 の44問、特例第一種は有害の20問を使う
MOCK_TOWN = {'S': 'S1', 'K': 'K1', 'E': 'E1', 'Y': 'Y1', 'Z': 'Z1'}
def mk(set_, sj, n, kid, question, ch, ans, expl, ce, src, ref=None):
    q(f'M{set_}-{sj}{n:02d}', kid, 'mock', 0, 'mcq5', question, ch, ans, expl, ce, src=src, pool='mock', town=MOCK_TOWN[sj])
    Q[-1]['mock_set'] = set_
    if ref: Q[-1]['legal_reference'] = ref
