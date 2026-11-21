# 問題の選択肢を、問題のIDを指定して書きかえる（eq_*.py をその場で直す）
# 使い方：python3 tools/rechoice.py tools/fix_XX.py   … fix_XX.py の FIX = {'問題ID': [選択肢…], …} を当てる
# 選択肢の順番（正解の位置）は変えないこと。choice_explanations は同じ順番のまま使われる
import ast, glob, os, sys
H = os.path.dirname(os.path.abspath(__file__))
ARG = {'st': 6, 'sit': 6, 'm': 5, 'm5': 5, 'ident': 5, 'mk': 5, 'bid': 4}

def call_id(c, fname):
    f = c.func.id if isinstance(c.func, ast.Name) else None
    if f not in ARG: return None, None
    a = c.args
    try:
        if f == 'mk': return f'M{SET[fname]}-{a[1].value}{a[2].value:02d}', f
        if f in ('ident', 'bid'): return 'ID-' + a[0].value, f
        return a[0].value, f
    except Exception: return None, None

def q(s): return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"
SET = {}
def apply(fix):
    left = dict(fix)
    for p in sorted(glob.glob(os.path.join(H, 'eq_*.py'))):
        src = open(p).read(); fname = os.path.basename(p)
        if fname.startswith('eq_ZZ_mock'): SET[fname] = int(fname[len('eq_ZZ_mock'):-3])
        tree = ast.parse(src); lines = src.split('\n'); edits = []
        for c in ast.walk(tree):
            if not isinstance(c, ast.Call): continue
            qid, f = call_id(c, fname)
            if qid not in left: continue
            node = c.args[ARG[f]]; new = left.pop(qid)
            old = [e.value for e in node.elts]
            assert len(new) == len(old), (qid, len(new), len(old))
            edits.append((node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, '[' + ', '.join(map(q, new)) + ']'))
        if not edits: continue
        # 行と列を文字の位置に直して、後ろから置きかえる
        off = [0]
        for ln in lines: off.append(off[-1] + len(ln.encode()) + 1)
        b = src.encode()
        for l1, c1, l2, c2, txt in sorted(edits, reverse=True):
            b = b[:off[l1 - 1] + c1] + txt.encode() + b[off[l2 - 1] + c2:]
        open(p, 'w').write(b.decode()); print(fname, len(edits))
    if left: print('見つからない問題：', list(left)); sys.exit(1)

if __name__ == '__main__':
    g = {}; exec(open(sys.argv[1]).read(), g); apply(g['FIX'])
