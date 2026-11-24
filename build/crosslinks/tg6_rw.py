from tg6_lib import apply
t='korea-tokanfu-1913/'
apply('korea-tokei--railways',{
'Railway lines':[t+'p0167_2',t+'p0167_3'],
'Traffic by station':[t+'p0171_2'],
'Railway construction costs':[t+'p0175_1'],
'Railway revenue and expenditure':[t+'p0177_1'],
'State railway passenger and freight traffic':[t+'p0168_2'],
'Principal freight by commodity':[t+'p0171_1'],
'Through traffic':[t+'p0170_2'],
'State railway transport revenue':[t+'p0169_1'],
'Private railways and tramways, capital':[t+'p0179_1'],
'Private railways and tramways, traffic':[t+'p0179_2'],
'Private railways, construction costs':[t+'p0180_1'],
'Private railways and tramways, revenue and expenditure':[t+'p0180_2'],
},[
('Train and vehicle operations',[t+'p0168_1','korea-tokanfu-1919/p0165_1']),
('Railway repair costs',[t+'p0176_1','korea-tokanfu-1919/p0174_2']),
('Railway casualties',['korea-tokanfu-1908/p0111_1',t+'p0178_2','korea-tokanfu-1919/p0176_1']),
('Railway hotels',[t+'p0177_2','korea-tokanfu-1919/p0175_2']),
('Railway warehouses',[t+'p0178_1','korea-tokanfu-1919/p0175_3']),
('Railway law offences',[t+'p0178_3','korea-tokanfu-1919/p0176_2']),
])
