import json
A='korea-tokanfu-'
def k(s,i): return A+s+'/'+i
order=['1908','1913','1919','1922','1939']
def ed(m):
    s=m.split('/')[0][len(A):]
    return order.index('1922' if s.startswith('1922') else s)
def run(name, adds, news):
    p=f'families/{name}.json'
    d=json.load(open(p)); F=d['families']
    for anchor,new in adds:
        f=next(f for f in F if anchor in f['members'])
        assert not any(new in g['members'] for g in F)
        f['members'].append(new)
        f['members'].sort(key=ed)  # stable
    for label,mem in news:
        assert not any(m in g['members'] for g in F for m in mem)
        F.append({'label':label,'members':sorted(mem,key=ed)})
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
    json.load(open(p))
    return len(F),sum(len(f['members']) for f in F)
m2=lambda i:k('1922-2',i); m3=lambda i:k('1922-3-1',i)
mining_adds=[
 (k('1913','p0094_1'),m2('p0054_1')),(k('1919','p0099_2'),m2('p0055_1')),
 (k('1919','p0100_1'),m2('p0056_1')),(k('1919','p0101_1'),m2('p0057_1')),
 (k('1919','p0103_1'),m2('p0059_1')),(k('1919','p0105_1'),m2('p0063_1')),
 (k('1919','p0106_1'),m2('p0064_1')),
 (k('1919','p0110_1'),m3('p0007_1')),(k('1919','p0115_1'),m3('p0016_1')),
 (k('1919','p0117_1'),m3('p0018_2')),(k('1919','p0117_2'),m3('p0019_1')),
 (k('1919','p0118_1'),m3('p0019_2')),(k('1919','p0119_1'),m3('p0025_1')),
]
mining_new=[
 ('Mineral output by nationality',[k('1919','p0107_1'),m2('p0066_1')]),
 ('Output by mine',[k('1919','p0108_1'),m2('p0066_2')]),
 ('Insurance',[k('1919','p0112_1'),m3('p0010_1')]),
 ('Tobacco consumption',[k('1919','p0116_1'),m3('p0018_1')]),
 ('Electric utilities',[k('1919','p0119_2'),m3('p0027_1')]),
 ('Local industrial training institutes',[k('1919','p0119_4'),m3('p0028_1')]),
]
print(run('korea-tokei--mining-and-industry',mining_adds,mining_new))
bank_adds=[
 (k('1919','p0110_1'),m3('p0007_1')),(k('1919','p0112_1'),m3('p0010_1')),
 (k('1919','p0115_1'),m3('p0016_1')),(k('1919','p0117_1'),m3('p0018_2')),
 (k('1919','p0118_1'),m3('p0019_2')),
]
bank_adds.insert(4,(k('1919','p0117_2'),m3('p0019_1')))
bank_new=[
 ('Tobacco consumption',[k('1919','p0116_1'),m3('p0018_1')]),
 ('Industrial products value',[k('1919','p0119_1'),m3('p0025_1')]),
 ('Electric utilities',[k('1919','p0119_2'),m3('p0027_1')]),
 ('Local industrial training institutes',[k('1919','p0119_4'),m3('p0028_1')]),
]
print(run('korea-tokei--banking-and-commerce',bank_adds,bank_new))
pr_adds=[(k('1919','p0134_1'),m3('p0031_1')),(k('1919','p0135_1'),m3('p0033_1')),
 (k('1919','p0137_1'),m3('p0035_1')),(k('1919','p0138_1'),m3('p0037_1')),
 (k('1919','p0143_1'),m3('p0044_1')),(k('1919','p0147_1'),m3('p0046_1'))]
pr_new=[('Barley prices by town',[k('1919','p0140_1'),m3('p0040_1')]),
 ('Wheat prices by town',[k('1919','p0142_1'),m3('p0042_1')])]
print(run('korea-tokei--prices-and-wages',pr_adds,pr_new))
