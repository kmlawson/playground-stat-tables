import json
M=['military'];V=['militias-and-volunteer-forces'];A=['arms-and-arsenals']
C=['crime-and-justice']
s=[(M,V,[],'volunteer corps attendance'),(M,V,[],'efficients'),(M,A+V,[],'small arms'),
(M,V,['text-tables'],'officer resignations list'),(M,V,['text-tables'],'promotions list'),(M,V,['text-tables'],'commissions list'),
(M,V,[],'corps staff strength'),(M,V,[],'corps strength by branch'),
(M,A,[],'artillery ammunition'),(M,A,[],'ammunition'),(M,A,[],'ammunition'),(M,A,[],'ammunition'),(M,A,[],'ammunition'),
(M,A+V,[],'corps equipment return'),(M,A,[],'guns'),(M,A,[],'gun waggons'),(M,A,[],'harness'),(M,A+V,[],'artillery equipment'),(M,A+V,[],'infantry equipment'),(M,A,[],'ammunition stock'),
(['finance'],['pawnshops'],[],'pawn-shop licences'),(['finance','manufacturing'],['alcohol'],[],'liquor licence fees'),
(C,['police'],[],'police force strength'),(C,['offences-and-convictions','police'],[],'arrests by offence'),
(C,['offences-and-convictions'],[],'prisoners literacy by offence'),(C,['corporal-punishment','offences-and-convictions','prisons'],[],'punishments'),
(C,['prisons'],[],'gaol population'),(C,['offences-and-convictions','police'],[],'foreigners arrested'),(C,['offences-and-convictions'],[],'arrests comparison'),
(C,['offences-and-convictions','police'],[],'arrested not charged'),(C,['police'],[],'warrants summonses'),(C+['finance'],['police'],[],'road policing collections'),
(['transportation'],['road-transport','roads-and-bridges'],[],'vehicles on bridge'),
(['health'],['public-health'],[],'garbage collected'),(['health','agriculture'],['food-inspection','livestock'],[],'slaughtered animals'),(['health','agriculture'],['food-inspection','livestock'],[],'slaughtered animals'),
(['population','health'],['births-and-deaths','age-and-sex'],[],'deaths by age'),(['population','health'],['births-and-deaths'],[],'deaths and death-rate'),
(['health'],['epidemics','diseases'],[],'cholera cases'),(['health'],['epidemics','diseases'],[],'cholera deaths')]
json.dump(s,open('/dev/stdout','w'))
