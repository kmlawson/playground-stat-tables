from tagA_lib import write
W='utilities water-and-sewerage'
LS='geography land-surveys'
b06=[('transportation','road-transport',0,'trailer fees'),('utilities health','water-and-sewerage',0,'water pumped'),
('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),
('culture','arts-and-music',0,'orchestral works'),('health','medical-services',1,'institutions visited'),
('population','population-totals',0,'census'),('population','population-totals age-and-sex',0,'foreign pop'),('population','population-totals age-and-sex',0,'chinese pop'),
('population','nationality-and-ethnicity population-totals',0,'census by nationality'),('population','occupations',0,'occupations'),
('population','migration population-totals',0,'native place census'),('population','population-totals',0,'pop by period'),
('welfare','charitable-institutions',1,'committee members'),('welfare','poor-relief nationality-and-ethnicity',0,'cases by nationality'),
('welfare finance','charitable-institutions',0,'charity account'),('welfare finance','charitable-institutions poor-relief',0,'charity account'),('welfare finance','charitable-institutions housing',0,'tenement account'),('welfare finance','charitable-institutions',0,'estimates'),
('science-and-technology finance','weather navigation-aids',0,'semaphore budget'),('science-and-technology finance','weather navigation-aids',0,'semaphore budget'),('science-and-technology finance','weather navigation-aids',0,'semaphore accounts'),
('government labour','language-education wages',0,'language bonus'),('government','government-offices',1,'staff roster'),
('transportation','roads-and-bridges',0,'bridges'),('geography','land-surveys',0,'survey work'),(LS.split()[0],'land-surveys',0,'plans'),('geography','land-surveys',0,'boundary stones'),
('geography finance','land-surveys land-tax',0,'lots taxed'),('geography','land-surveys',0,'lots revised'),('geography finance','land-surveys land-tax',0,'assessed value'),
('geography transportation','land-surveys roads-and-bridges',0,'road lots'),('geography transportation','land-surveys roads-and-bridges',0,'road land cost'),
('transportation','roads-and-bridges',0,'road length'),('utilities transportation','roads-and-bridges',0,'trenches'),('utilities transportation','road-transport',0,'rolling stock')]
b07=[('utilities health','',0,'sweepings'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('utilities','water-and-sewerage',0,'water'),('labour','employment-and-unemployment',0,'public works labour'),
('welfare','poor-relief nationality-and-ethnicity',0,'shelter inmates'),('welfare','work-relief',0,'shelter work'),
('utilities','gas',0,'gas lamps'),('utilities','electricity',0,'electric lamps'),('utilities finance','electricity gas',0,'lamp fines'),
('utilities','construction',0,'permits'),('utilities','construction',0,'new buildings'),('utilities','construction',0,'plans'),('utilities','construction',0,'permits'),('utilities','construction',0,'work done'),
('manufacturing','cement-and-bricks',0,'quarry stone'),('manufacturing','cement-and-bricks',0,'concreteware'),
('government finance','public-property land-surveys',0,'property schedule'),
('transportation finance','roads-and-bridges',0,'road land'),('transportation finance','roads-and-bridges',0,'road land'),('transportation finance','roads-and-bridges',0,'compensation'),
('transportation finance','roads-and-bridges',0,'improvements'),('transportation finance','roads-and-bridges',0,'improvements'),('transportation finance','roads-and-bridges',0,'improvements'),
('transportation','road-transport',0,'traffic count'),('transportation finance','roads-and-bridges',0,'compensation'),('transportation finance','roads-and-bridges',0,'compensation'),
('transportation finance','roads-and-bridges',0,'compensation'),('transportation finance','roads-and-bridges',0,'land acquired'),('transportation finance','roads-and-bridges',0,'amended claim'),('transportation finance','roads-and-bridges',0,'improvements'),
('culture','recreation-and-amusements',1,'gardens list'),('culture','recreation-and-amusements',0,'park repairs'),('culture','recreation-and-amusements',0,'lawns'),
('forestry','afforestation',0,'roadside trees'),('forestry','afforestation',0,'trees'),('forestry','afforestation',0,'trees'),('forestry','afforestation',0,'planting'),('agriculture','horticulture',0,'plants'),('forestry','afforestation',0,'nurseries')]

E=('utilities','electricity');UF=('utilities finance','electricity')
b08=[('sport','sports-participation',0,'players'),('culture','recreation-and-amusements',0,'turf')]
b08+=[E+(0,'electricity dept')]*10      # 2-11
b08+=[E+(0,'street lamps')]*6           # 12-17
b08+=[E+(0,'sub-stations')]*5           # 18-22? adjusted below
b08=b08[:23]
b08+=[UF+(0,'contracts'),UF+(0,'estimated prices'),E+(0,'lamps comparison'),UF+(0,'estimate 1921'),('utilities labour','electricity wages',0,'pay'),UF+(0,'capital estimate')]  # 23-28
b08+=[UF+(0,'accounts')]*11               # 29-39
P=('finance','public-budgets')
b09=[UF+(0,'accounts')]*6
b09+=[P+(0,'budget')]*8                   # 6-13
b09+=[('finance','public-debt securities-and-investment',0,'silver loan'),P+(0,'totals'),
('finance','taxation public-budgets',0,'income vs budget'),('finance','taxation land-tax',0,'land tax'),
('finance','taxation real-estate',0,'rates'),('finance','taxation real-estate',0,'rates'),('finance','taxation',0,'wharfage'),('finance','taxation',0,'licences'),
('finance transportation','taxation road-transport',0,'vehicle licences'),('transportation','road-transport',0,'motor vehicles'),
('finance','markets-and-exchanges',0,'market fees'),('finance population','population-totals public-budgets',0,'pop and income'),('finance','public-budgets taxation',0,'statements'),
('finance','taxation public-budgets',0,'revenue'),('finance','taxation',0,'chinese rate'),('finance','taxation real-estate',0,'assessments'),('finance','taxation',0,'licence fees'),('finance','taxation',0,'licence fees'),
('finance','taxation land-tax public-budgets',0,'land tax'),('finance','taxation public-budgets',0,'rate'),('finance','taxation public-budgets',0,'special rate'),('finance','taxation public-budgets',0,'advert rate'),('finance','taxation public-budgets',0,'wharfage'),('finance','taxation public-budgets',0,'licences'),('finance','public-budgets public-property',0,'rents'),('finance','public-budgets',0,'undertakings')]
b09=b09[:40]
def X(t,tag,w):return (t,tag,0,w)
b10=[X('finance military','public-budgets militias-and-volunteer-forces','vc'),X('finance','public-budgets','stores'),X('finance','public-budgets','credit'),
X('finance disasters','public-budgets firefighting','fire'),X('finance disasters','public-budgets firefighting','fire'),X('finance crime-and-justice','public-budgets police','police'),X('finance crime-and-justice','public-budgets police','police'),
X('finance health','public-budgets medical-services','health'),X('finance health','public-budgets epidemics','plague'),X('finance health','public-budgets malaria','mosquito'),X('finance health','public-budgets','health totals')]
b10+=[X('finance health','public-budgets medical-services','hospital')]*9   # 11-19
b10+=[X('finance health','public-budgets','cemeteries'),X('finance sport','public-budgets sports-organisations-and-facilities','bath'),X('finance health','public-budgets','extra'),X('finance health','public-budgets','stores'),
X('finance utilities','public-budgets','pw general'),X('finance','public-budgets construction','pw buildings'),X('finance','public-budgets construction','pw buildings'),X('finance','public-budgets construction','pw buildings'),X('finance','public-budgets construction','pw buildings'),X('finance','public-budgets construction','pw buildings'),
X('finance utilities','public-budgets river-conservancy','creeks'),X('finance utilities','public-budgets water-and-sewerage','drainage'),X('finance transportation','public-budgets roads-and-bridges','roads'),X('finance transportation','public-budgets roads-and-bridges','roads'),
X('finance utilities','public-budgets electricity gas','lighting'),X('finance culture','public-budgets recreation-and-amusements','parks'),X('finance','public-budgets','stores'),X('finance','public-budgets','credit'),
X('finance culture','public-budgets arts-and-music','band'),X('finance culture','public-budgets arts-and-music','band')]
import sys
for b,v in [('b06',b06),('b07',b07),('b08',b08),('b09',b09),('b10',b10)]:
    if len(v)!=40: print(b,len(v))
    write(b,v)
