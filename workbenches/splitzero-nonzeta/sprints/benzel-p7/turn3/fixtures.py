"""Exact placed-tile anchors and inverse expansion to the original JSON cells."""
from pathlib import Path
import hashlib
import json

SIXTH = [
    (4, 'R -1 0',
        'D -6 4;D -6 5;H -11 8;H -9 7;H -7 6;H -6 7;H -5 5;H -4 6;H -3 7;H -2 8;V -3 1;V -2 0',
        'D -15 10;D -14 8;D -14 10;D -13 6;D -13 10;D -12 4;D -11 2;D -11 9;D -10 0;D -9 -2;D -9 8;D -8 -4;D -7 -6;D -6 -8;H -14 11;H -13 12;H -12 10;H -12 13;H -11 11;H -11 14;H -10 12;H -10 15;H -9 13;H -8 14;H -7 7;H -7 12;H -6 13;H -5 3;H -5 11;H -4 2;H -4 12;H -3 1;H -3 10;H -2 0;H -2 11;H 0 8;H 0 9;H 0 10;V -6 4;V -5 4;V -4 5;V -3 5;V -2 6;V -1 7;V 3 7;V 4 7;V 5 6;V 6 6;V 7 5;V 8 5;V 9 4;V 10 4;V 11 2;V 12 0;V 13 -2;V 14 -4;V 15 -6'),
    (5, 'R 2 -1',
        'D -12 6;D -8 4;D -8 5;D -5 1;D -5 2;D -4 -1;D 0 -3;H -11 7;H -11 10;H -10 6;H -10 8;H -8 10;H -7 8;H -5 10;H -4 8;H -1 8;H 3 -2;V -9 3;V -2 -2;V -1 -4;V 0 -6;V 1 -7;V 2 -8;V 3 -7;V 4 -8;V 4 -5;V 5 -8;V 5 -5',
        'D -14 7;D -14 8;D -13 5;D -12 3;D -11 1;D -11 5;D -11 7;D -10 -1;D -10 7;D -10 8;D -9 -3;D -8 -5;D -7 -7;D -7 3;D -6 -9;D -6 3;D -3 -2;D -2 -2;D -1 -2;D 0 -6;D 0 -5;D 2 -6;D 2 -1;D 2 0;D 3 -6;H -16 11;H -15 9;H -15 10;H -15 12;H -14 13;H -13 11;H -13 14;H -12 10;H -12 12;H -12 15;H -11 13;H -11 16;H -10 14;H -9 4;H -9 8;H -9 10;H -9 15;H -8 13;H -7 14;H -6 8;H -6 10;H -6 12;H -5 13;H -4 -1;H -4 0;H -4 11;H -3 8;H -3 10;H -3 12;H -1 11;H 0 8;H 0 9;H 0 10;H 1 -5;V 3 8;V 4 -6;V 4 7;V 5 -7;V 5 -4;V 5 7;V 6 6;V 7 6;V 8 5;V 9 5;V 10 4;V 11 4;V 12 2;V 13 0;V 14 -2;V 15 -4;V 16 -6'),
    (6, 'R 3 -1',
        'D -4 7;D -3 7;D -2 7;D 0 6;D 2 5;D 4 4;H -1 4;H 1 3;H 3 2;H 4 0;H 4 1;H 5 -1;H 5 4;H 6 3;H 8 4;H 10 2;H 10 3;H 11 0;H 11 1;H 12 -3;H 12 -2;H 12 -1;V 7 0;V 9 1;V 10 -1;V 11 -3',
        'D -17 12;D -16 10;D -16 12;D -16 13;D -15 8;D -15 13;D -15 14;D -14 6;D -14 14;D -14 15;D -13 4;D -13 15;D -12 2;D -11 0;D -10 -2;D -9 -4;D -9 15;D -8 -6;D -7 -8;D -7 14;D -6 -10;D -5 13;D -3 6;D -3 12;D -1 5;D -1 11;D 1 10;D 2 3;D 3 3;D 3 9;D 5 8;D 7 7;H -13 16;H -12 15;H -12 17;H -11 14;H -10 16;H -8 15;H -6 14;H -4 7;H -4 13;H -2 6;H -2 12;H 0 5;H 0 11;H 1 4;H 2 10;H 3 -1;H 3 0;H 4 3;H 4 4;H 4 9;H 5 2;H 6 8;H 7 3;H 7 4;H 8 7;H 9 1;H 9 2;H 9 6;H 10 -1;H 10 0;H 11 -3;H 11 -2;V 6 -1;V 7 -1;V 10 3;V 11 3;V 12 1;V 12 4;V 13 -1;V 13 2;V 14 -3;V 14 0;V 15 -2;V 16 -4;V 17 -6'),
    (7, 'R 4 -1',
        'D -5 8;D -4 8;D -1 7;D 5 4;H -13 12;H -11 11;H -9 10;H -7 9;H -2 5;H 0 4;H 0 7;H 2 3;H 3 7;H 4 2;H 4 5;H 5 0;H 5 1;H 5 6;H 6 -1;V 8 0',
        'D -18 13;D -17 11;D -17 13;D -17 14;D -16 9;D -16 14;D -15 7;D -15 14;D -14 5;D -13 3;D -13 13;D -12 1;D -11 -1;D -11 12;D -10 -3;D -9 -5;D -9 11;D -8 -7;D -7 -9;D -7 10;D -6 -11;D -5 9;D -4 7;D -2 6;D 0 5;D 0 6;D 3 3;D 4 3;D 4 5;H -16 15;H -15 16;H -14 14;H -14 17;H -13 15;H -13 18;H -12 16;H -11 17;H -10 15;H -9 16;H -8 14;H -7 15;H -6 13;H -5 14;H -4 12;H -3 13;H -2 11;H -1 7;H -1 12;H 0 10;H 1 11;H 2 7;H 2 9;H 3 10;H 4 -1;H 4 0;H 4 8;H 5 9;H 6 2;V 5 5;V 6 5;V 7 -1;V 7 6;V 8 -1;V 8 6;V 9 6;V 10 5;V 11 5;V 12 4;V 13 4;V 14 2;V 15 0;V 16 -2;V 17 -4;V 18 -6'),
    (8, 'R 5 -1',
        'D -6 9;D -5 9;D 0 7;D 6 4;H -14 13;H -12 12;H -10 11;H -8 10;H -3 6;H -1 5;H 1 4;H 1 7;H 3 3;H 4 7;H 5 2;H 5 5;H 6 0;H 6 1;H 7 -1;H 8 5;V 9 0',
        'D -19 14;D -18 12;D -18 14;D -17 10;D -16 8;D -15 6;D -14 4;D -14 14;D -13 2;D -12 0;D -12 13;D -11 -2;D -10 -4;D -10 12;D -9 -6;D -8 -8;D -8 11;D -7 -10;D -6 -12;D -6 10;D -5 8;D -3 7;D -1 6;D 1 5;D 1 6;D 4 3;D 5 3;D 5 5;H -18 15;H -17 14;H -17 16;H -16 13;H -16 17;H -15 15;H -15 18;H -14 16;H -14 19;H -13 17;H -12 18;H -11 16;H -10 17;H -9 15;H -8 16;H -7 14;H -6 15;H -5 13;H -4 14;H -3 12;H -2 13;H -1 11;H 0 7;H 0 12;H 1 10;H 2 11;H 3 7;H 3 9;H 4 10;H 5 -1;H 5 0;H 5 8;H 6 5;H 6 7;H 6 9;H 7 2;H 8 8;H 10 5;H 10 6;H 10 7;V 8 -1;V 9 -1;V 9 5;V 13 4;V 14 4;V 15 2;V 16 0;V 17 -2;V 18 -4;V 19 -6'),
]
ANNULI = [
    (3, 0,
        'H -9 7;H -8 8;H -7 9;D -8 5;D -7 3;D -6 1;D -5 -1;D -4 -3;D -3 -5;D -8 6;H -7 6;H -6 7;H -5 8;D -6 5;D -5 3;D -5 2;D -4 0;D -3 -2;D -2 -4;D -1 -6;H -5 5;H -4 6;H -3 7;D -4 4;D -3 2;H -3 4;D -2 -1;D -2 0;H -2 3;H -2 5;D -1 -3;H -1 6;D 0 -5;H 0 2;H 0 4;D 1 -7;H 1 3;H 1 5;V 3 -8;V 2 -6;V 1 -4;V 4 -8;V 5 -7;V 3 -5;V 2 -3;V 4 -5;V 6 -6;V 5 -4;V 3 -2;H 2 1;H 3 2;H 3 4;V 4 -2;H 4 3;V 7 -5;V 6 -3;V 5 -1;V 7 1;V 6 0;V 8 -4;V 7 -2;V 8 -1;V 9 -3'),
    (3, 1,
        'H -11 8;H -10 9;H -9 10;H -8 11;D -10 6;D -9 4;D -8 2;D -7 0;D -6 -2;D -5 -4;D -4 -6;D -10 7;H -9 7;H -8 8;H -7 9;H -6 10;D -8 6;D -7 4;D -7 3;D -6 1;D -5 -1;D -4 -3;D -3 -5;D -2 -7;H -7 6;H -6 7;H -5 8;H -4 6;H -4 9;H -3 7;H -2 8;D -6 5;D -5 3;H -5 5;D -4 0;D -4 1;D -3 -2;D -2 -4;H -2 5;D -1 -6;D -1 -3;H -1 4;H -1 6;D 0 -8;D 0 -5;H 0 7;D 1 -7;H 1 3;H 1 5;D 2 -9;H 2 4;H 2 6;H 3 2;V 4 -10;V 3 -8;V 2 -6;H 4 3;H 4 5;V 5 -10;H 5 4;V 6 -9;V 4 -7;V 3 -5;V 5 -7;V 7 -8;V 6 -6;V 4 -4;V 5 -4;V 8 -7;V 7 -5;V 6 -3;V 5 -1;V 8 2;V 7 1;V 6 0;V 9 -6;V 8 -4;V 7 -2;V 9 0;V 8 -1;V 10 -5;V 9 -3;V 10 -2;V 11 -4'),
    (4, 0,
        'H -12 9;H -11 10;H -10 11;H -9 12;D -11 7;D -10 5;D -9 3;D -8 1;D -7 -1;D -6 -3;D -5 -5;D -4 -7;D -11 8;H -10 8;H -9 9;H -8 10;H -7 11;D -9 7;D -8 5;D -8 4;D -7 2;D -6 0;D -5 -2;D -4 -4;D -3 -6;D -2 -8;H -8 7;H -7 8;H -6 9;H -5 10;D -7 6;D -6 4;D -5 2;D -5 1;D -4 -1;D -3 -3;D -2 -5;D -1 -7;D 0 -9;H -6 6;H -5 7;H -4 8;H -3 9;D -5 5;D -4 3;H -4 5;D -3 1;H -3 4;H -3 6;D -2 -2;D -2 -1;H -2 7;D -1 -4;H -1 3;H -1 5;H -1 8;D 0 -6;H 0 4;H 0 6;D 1 -8;H 1 2;H 1 7;D 2 -10;H 2 3;H 2 5;H 3 4;H 3 6;V 4 -11;V 3 -9;V 2 -7;V 1 -5;V 5 -11;V 6 -10;V 4 -8;V 3 -6;V 2 -4;V 5 -8;V 7 -9;V 6 -7;V 4 -5;V 3 -3;V 5 -5;V 8 -8;V 7 -6;V 6 -4;V 4 -2;H 3 1;H 4 2;V 5 -2;H 5 3;H 5 5;H 6 4;V 9 -7;V 8 -5;V 7 -3;V 6 -1;V 9 2;V 8 1;V 7 0;V 10 -6;V 9 -4;V 8 -2;V 10 0;V 9 -1;V 11 -5;V 10 -3;V 11 -2;V 12 -4'),
]
EARLIER_D4 = 'R -2 2;H -13 9;D -12 7;D -12 8;H -12 10;D -11 5;H -11 8;H -11 11;D -10 3;D -10 7;H -10 9;H -10 12;D -9 1;D -9 4;D -9 5;D -9 7;H -9 10;H -9 13;D -8 -1;D -8 2;D -8 7;H -8 8;H -8 11;D -7 -3;D -7 0;H -7 4;D -7 7;H -7 9;H -7 12;D -6 -5;D -6 -2;D -6 1;D -6 2;D -6 3;H -6 7;H -6 10;D -5 -7;D -5 -4;D -5 -1;D -5 3;H -5 6;H -5 8;H -5 11;D -4 -6;D -4 -3;V -4 3;H -4 9;D -3 -8;D -3 -5;V -3 -2;V -3 2;D -3 5;D -3 7;H -3 10;D -2 -7;V -2 -4;V -2 -1;D -2 5;D -2 7;H -2 8;D -1 -9;V -1 -6;V -1 -3;D -1 0;D -1 1;D -1 7;H -1 9;V 0 -8;D 0 -5;V 0 -4;D 0 1;D 0 2;H 0 4;H 0 7;D 1 -10;D 1 -9;D 1 -8;D 1 -7;V 1 -5;H 1 2;H 1 3;D 1 6;H 1 8;D 2 -6;D 2 -5;V 2 -4;H 2 1;H 2 6;D 3 -8;V 3 -5;V 3 -2;H 3 5;H 3 7;V 4 -12;H 4 -6;V 4 -5;V 4 -2;V 4 2;V 5 -13;V 5 -9;H 5 -5;V 5 -4;V 5 -1;V 5 2;H 5 6;V 6 -12;V 6 -9;H 6 -4;V 6 -3;V 6 0;V 6 3;V 7 -11;V 7 -8;H 7 -3;V 7 -2;V 7 1;H 7 4;H 7 5;V 8 -10;V 8 -7;H 8 -2;V 8 -1;H 8 2;H 8 3;V 9 -9;V 9 -6;H 9 -1;H 9 0;H 9 1;V 10 -8;V 10 -5;V 11 -7;V 11 -4;V 12 -6;V 12 -3;V 13 -5'
IDENTITIES = {'sixth-witnesses.json': 'b144aac827563bb9741e19533b2b71fc745bd7fa77da5b1deabc03e5d6759108', 'constant-charge-annuli.json': 'ad6733225f5726c4bf41e1e6b2d5d81aa114d9feb91e2476a09471f0753af082', 'earlier-fifth-d4.json': '271e51f5727a581817ae792da0b309b7cb785f7be239eb951ee02d5a91f06e36'}

def expand(text):
    result = []
    for entry in text.split(';'):
        k, x, y = entry.split(); x, y = int(x), int(y)
        direction = {'D': (1,-1), 'H': (1,0), 'V': (0,1)}
        offsets = ((0,0),(1,0),(0,1)) if k == 'R' else tuple(
            (u*direction[k][0],u*direction[k][1]) for u in range(3))
        result.append([k, sorted([[x+a,y+b] for a,b in offsets])])
    return result

def restore(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parent/'evidence'
    data = {
        'sixth-witnesses.json': [
            {'d':d,'h':6,'shift':[1,-2],'removed_stone':expand(stone)[0],
             'removed_bones':expand(old),'new_bones':expand(new)}
            for d,stone,old,new in SIXTH],
        'constant-charge-annuli.json': [
            {'d':d,'h':h,'shift':[0,0],'tiles':expand(tiles)}
            for d,h,tiles in ANNULI],
        'earlier-fifth-d4.json': {'d':4,'h':5,'tiling':expand(EARLIER_D4)}}
    root.mkdir(parents=True,exist_ok=True)
    for name, obj in data.items():
        suffix = '' if name == 'earlier-fifth-d4.json' else '\n'
        raw = (json.dumps(obj,separators=(',',':'))+suffix).encode()
        if hashlib.sha256(raw).hexdigest()!=IDENTITIES[name]:
            raise ValueError('Original evidence identity mismatch: '+name)
        target = root/name
        if target.exists() and target.read_bytes()!=raw:
            raise ValueError('Existing evidence differs; preserve and review: '+name)
        if not target.exists(): target.write_bytes(raw)
    return list(data)

if __name__=='__main__':
    print(json.dumps(restore(),indent=2))
