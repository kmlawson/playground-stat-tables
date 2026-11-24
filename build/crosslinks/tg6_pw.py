from tg6_lib import apply
t='korea-tokanfu-1913/'
apply('korea-tokei--prices-and-wages',{
'Retail prices':[t+'p0145_2'],'Wages':[t+'p0149_1']},
[('Unhulled rice prices by town',[t+'p0143_2','korea-tokanfu-1919/p0134_1']),
 ('Brown rice prices by town',[t+'p0143_3','korea-tokanfu-1919/p0135_1']),
 ('Polished rice prices by town',[t+'p0144_1','korea-tokanfu-1919/p0137_1']),
 ('Soybean prices by town',[t+'p0145_1','korea-tokanfu-1919/p0138_1'])])
