from tg6_lib import apply
t='korea-tokanfu-1913/'
apply('korea-tokei--foreign-trade',{
'Total exports and imports':[t+'p0154_1'],
'Exports by port':[t+'p0154_2'],
'Imports by port':[t+'p0155_1'],
'Trade by country':[t+'p0156_1'],
'Principal exports':[t+'p0157_1'],
'Principal imports':[t+'p0159_1'],
'Shipping entered and cleared':[t+'p0165_2'],
'Customs revenue':[t+'p0165_3'],
'Trade by month':[t+'p0155_2',t+'p0155_3'],
'Bonded warehouses':[t+'p0166_1'],
},[
('Gold and silver by country',['korea-tokanfu-1908/p0100_2',t+'p0165_1']),
('Gold and silver trade',[t+'p0164_1','korea-tokanfu-1919/p0161_1']),
('Overland frontier trade',[t+'p0167_1','korea-tokanfu-1919/p0163_1']),
])
