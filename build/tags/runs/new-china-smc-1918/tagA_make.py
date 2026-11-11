import json
T='text-tables'
def S(s):
    out=[]
    for line in s.strip().split('\n'):
        a,b,c,*w=[x.strip() for x in line.split('|')]
        out.append((a.split(),b.split(),c.split(),w[0] if w else ''))
    return out
B={}
B[1]=S('''
government|local-government|text-tables|committee list
government|local-government|text-tables|sub-committee reps
government|local-government|text-tables|vacancies filled
government|local-government||meeting counts
military|army||corps units strength
military|army recruitment-and-conscription||joined/left
military|army recruitment-and-conscription||reasons leaving
military|army||strength by year
military|army||efficiency return
military|army||efficiency points
military|army||musketry return
military|army||efficiency points
military|army honours-and-ranks|text-tables|seniority roll
military|army honours-and-ranks|text-tables|promotions
military|army honours-and-ranks|text-tables|commissions
military|army honours-and-ranks|text-tables|commissions
military|army honours-and-ranks|text-tables|resignations
military|military-casualties|text-tables|deaths in corps
military|army|text-tables|officers roster
disasters|firefighting|text-tables|brigade staff
disasters|firefighting|text-tables|volunteer officers
disasters|firefighting|text-tables|officer changes
disasters|firefighting fires||calls by source
disasters|fires disaster-losses||fire waste percentage
disasters|firefighting|text-tables|repairs list
disasters|firefighting|text-tables|workshop equipment
disasters|firefighting||workshop output
disasters|firefighting||equipment obtained
disasters|fires firefighting||calls by month
disasters|fires firefighting disaster-losses||monthly fire return
disasters|firefighting||motor appliances
disasters|fires||fires by cause
disasters|fires disaster-losses||property at risk
disasters|fires disaster-losses||damage chart
disasters|fires firefighting||calls chart
crime-and-justice|police||foreign branch strength
crime-and-justice military|police war-and-mobilisation|text-tables|war volunteers
crime-and-justice military|police war-and-mobilisation|text-tables|ex-members volunteers
crime-and-justice|police||offences by members
crime-and-justice|police||Sikh branch
''')
B[2]=S('''
crime-and-justice|police||offences by Sikh police
crime-and-justice|police||Indian watchmen
crime-and-justice|police||Chinese branch strength
crime-and-justice|police||CID strength
crime-and-justice|police||identification records
crime-and-justice|police||intelligence work
transportation|road-transport||passenger islands
transportation|road-transport||vehicle ranks
transportation|road-transport||chauffeurs
transportation|road-transport trams||traffic census
transportation|transport-accidents road-transport||traffic accidents
crime-and-justice|police||mounted branch
crime-and-justice|police|text-tables|ponies presented
crime-and-justice|police||musketry course
crime-and-justice|police||revolver course
crime-and-justice|prisons||gaol numbers
crime-and-justice|prisons juvenile-justice||reformatory numbers
crime-and-justice|prisons||prisoner return
crime-and-justice|prisons||gaol/reformatory summary
crime-and-justice|prisons||prisoner localities
crime-and-justice|courts||mixed court sessions
crime-and-justice government|courts||mixed court staff
crime-and-justice|offences-and-convictions courts||offence variations
crime-and-justice|offences-and-convictions courts||handed to Chinese authorities
crime-and-justice|courts offences-and-convictions||private prosecutions
crime-and-justice|courts civil-litigation nationality-and-ethnicity||foreign civil cases
crime-and-justice|courts civil-litigation||civil case processes
crime-and-justice|courts civil-litigation||Chinese civil cases
crime-and-justice|courts civil-litigation||security bonds
informal-imperialism crime-and-justice|extraterritoriality nationality-and-ethnicity||consular protection claims
population|migration war-and-mobilisation||enemy subjects movements
population|nationality-and-ethnicity war-and-mobilisation||enemy subjects register
crime-and-justice|offences-and-convictions courts war-and-mobilisation||enemy prosecutions
crime-and-justice|offences-and-convictions||enemy convictions
crime-and-justice|police offences-and-convictions||police action return
crime-and-justice|offences-and-convictions police||arrests not charged
crime-and-justice|offences-and-convictions police||foreigners charged
crime-and-justice|offences-and-convictions courts||mixed court returns
crime-and-justice|offences-and-convictions courts||mixed court sentences
crime-and-justice|offences-and-convictions police||arrests 1909-1918
''')
B[3]=S('''
crime-and-justice|prisons||cell prisoners weekly
crime-and-justice|police arms-and-arsenals||arms stock
crime-and-justice|police|text-tables|casualty list names
crime-and-justice finance|police||funeral expenditure
geography population|land-area population-totals||statistical summary
geography|weather||meteorology
health population|births-and-deaths diseases||foreign deaths by cause
health population|births-and-deaths diseases||child deaths
health population|births-and-deaths diseases||foreign deaths
population health|births-and-deaths nationality-and-ethnicity||deaths by nationality
population health|births-and-deaths age-and-sex||ages at death
population health|births-and-deaths||death rates
health population|births-and-deaths diseases||Chinese deaths
health|diseases epidemics||notifications
health|diseases epidemics births-and-deaths||deaths from infectious diseases
health|vaccination||vaccination
health|diseases epidemics||plague rats
health|diseases epidemics||plague incidence
health|public-health epidemics||plague prevention
health|veterinary-health public-health||kennels
health|diseases public-health||laboratory diagnosis
health|food-inspection||milk adulteration
health utilities|water-and-sewerage public-health||water analysis
health|diseases medical-services||isolation hospital
health|medical-services||nursing home
health|medical-services diseases||police and gaol hospitals
health|medical-services||hospital summary
health utilities|public-health||house refuse
health utilities|public-health||house refuse disposal
sport|sports-organisations-and-facilities||swimming bath use
health|public-health||sanitary work
economy trade|prices cost-of-living||price variation
health|food-inspection veterinary-health||slaughterhouse rejections
health agriculture|food-inspection livestock||slaughterhouse returns
trade|markets-and-exchanges||municipal markets
crime-and-justice health|offences-and-convictions food-inspection||sanitary prosecutions
health population||| cemeteries
health crime-and-justice|births-and-deaths||mortuary
health|medical-services||hospital rates
health|medical-services||hospital rates
''')
B[4]=S('''
health|medical-services||nursing home fees
health|medical-services||hospital rates
health|medical-services||fees ordinary cases
health|medical-services maternal-and-child-health||maternity fees
health|medical-services||outside fees
health|medical-services||patients treated
health|diseases medical-services||cases by class
health finance|medical-services||working account
finance health|medical-services||balance sheet
health utilities|water-and-sewerage public-health||trade effluent volume
population|population-totals||district population
population|population-totals nationality-and-ethnicity||foreign population
population|population-totals nationality-and-ethnicity||Chinese population
population|population-totals nationality-and-ethnicity||French Concession
population|population-totals||Chinese city
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||water samples
health utilities|water-and-sewerage public-health||well water analysis
health utilities|water-and-sewerage public-health|text-tables|dye houses effluent
health utilities|water-and-sewerage public-health|text-tables|trade effluents
health utilities|water-and-sewerage public-health|text-tables|trade effluents
health utilities|water-and-sewerage public-health|text-tables|trade effluents
education government|teachers|text-tables|committee members
education finance|education-finance mission-schools charitable-institutions||orphanage account
education welfare|charitable-institutions schools-and-pupils||orphanage pupils
education finance|education-finance mission-schools charitable-institutions||orphanage account
education finance|education-finance mission-schools||school account
education|schools-and-pupils school-boarding||pupils by boarding
education government||text-tables|committee members
education|schools-and-pupils||roll
education|schools-and-pupils||roll
education|schools-and-pupils||new pupils
education|schools-and-pupils||ages admitted
education|schools-and-pupils||withdrawn
education health|schools-and-pupils diseases||sickness
education|schools-and-pupils teachers||staff allocation
''')
B[5]=S('''
education|teachers|text-tables|special subjects staff
education|schools-and-pupils teachers||summary
education|secondary-education|text-tables|Cambridge list
education|secondary-education||exam summary
education|secondary-education||candidates entered
education|secondary-education|text-tables|HK exam results
education||text-tables|bursaries
sport education|sports-records||cricket
sport education|sports-records||cricket
sport education|sports-records||football
sport education|sports-records||football
education|schools-and-pupils||roll
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|teachers schools-and-pupils||staff allocation
education|teachers|text-tables|special subjects
education|secondary-education|text-tables|Cambridge results
education||text-tables|exercise exhibition groups
education|schools-and-pupils||roll
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|schools-and-pupils||withdrawn
education|teachers schools-and-pupils||staff allocation
education|teachers|text-tables|special subjects
education|secondary-education|text-tables|Cambridge results
education|secondary-education||Cambridge summary
education|teachers|text-tables|assistant masters roll
education|schools-and-pupils||roll
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|schools-and-pupils||withdrawn
education population|schools-and-pupils nationality-and-ethnicity age-and-sex||nationality and age
education health|schools-and-pupils diseases||illness
education||text-tables|committee members
education|schools-and-pupils||roll
education|schools-and-pupils||attendance
education|schools-and-pupils||ages new pupils
education|teachers||staff
education|secondary-education|text-tables|successful pupils
education|secondary-education||external exam successes
''')
for n,spec in B.items():
    inp=json.load(open('batches/b%02d.json'%n))
    assert len(inp)==len(spec),(n,len(inp),len(spec))
    out=[]
    for r,(t,g,f,w) in zip(inp,spec):
        out.append({'key':r['key'],'topics':t,'tags':g,'flags':f,'why':w or r['title'][:50]})
    json.dump(out,open('results/b%02d.json'%n,'w'),ensure_ascii=False,indent=1)
    print(n,len(out),sum(1 for o in out if o['tags']))
