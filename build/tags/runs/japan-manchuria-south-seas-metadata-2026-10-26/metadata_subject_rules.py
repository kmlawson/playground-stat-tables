"""Authored subject expressions for titles, not body/column classification."""
import re

# Each expression names a substantive subject. Commodity expressions are kept
# separate: a material alone does not establish production, trade or finance.
RULE_TEXT = r"""
land-area|geography|\bland area\b|\bterritorial area\b|\barea and population\b|\barea of (?:japan|manchuria|korea|chosen|formosa|taiwan|karafuto|prefectures|provinces|the empire|the country|the territory)\b
physical-geography|geography|\b(?:latitude|longitude|strata|geolog\w*|mountains?|coast ?lines?|physical geography|altitudes?|geographical position)\b|^position$
weather|geography|\b(?:weather|meteorolog\w*|temperatures?|rainfalls?|precipitation|humidity|barometric|cloudiness|clear days|wind velocity|climate|snowfall)\b
flora-and-fauna|geography|\b(?:flora|fauna|wild animals|wildlife|botanical distribution)\b
earthquakes-and-volcanoes|disasters|\b(?:earthquakes?|volcanoes|volcanic|seismic)\b
rivers-and-waterways|geography|\b(?:rivers? and lakes?|lengths? of rivers?|river basins?|water levels?)\b
land-surveys|geography|\b(?:land surveys?|cadastral surveys?|geodetic|triangulation)\b
floods|disasters|\bfloods?\b
famine|disasters|\bfamine\b
disaster-losses|disasters|\b(?:disaster losses|damage.{0,15}(?:disaster|flood|earthquake)|calamities|disasters)\b
disaster-relief|welfare|\b(?:disaster relief|relief.{0,15}(?:flood|earthquake|calamity))\b
fires|disasters|\bfires?\b(?! insurance| engines?| brigades?| prevention| fighting)
storms-and-typhoons|disasters|\b(?:typhoons?|cyclones?|storms?)\b
firefighting|government|\b(?:fire[- ]?fighting|fire brigades?|fire engines?|fire prevention|firefloats?)\b
population-totals|population|\b(?:population|inhabitants)\b
age-and-sex|breakdown|\b(?:by ages?|by sex|ages? and sex(?:es)?|age[- ]groups?|age distribution|sex distribution|both sexes)\b
households|population|\b(?:households|families|family composition|house[- ]?holds)\b
births-and-deaths|population|\b(?:births?|birth[- ]rates?|deaths?|death[- ]rates?|mortality|vital statistics|movement of population)\b
marriage-and-divorce|population|\b(?:marriages?|divorces?|marital status)\b
migration|population|\b(?:immigration|emigration|migrants?|migration)\b
nationality-and-ethnicity|breakdown|\b(?:by nationality|by race|by ethnicity|nationalities|racial distribution|ethnic groups)\b
occupations|population|\b(?:occupations?|callings|by livelihood)\b
languages|population|\b(?:language distribution|languages spoken|mother tongue)\b
overseas-communities|population|\b(?:japanese (?:residents|subjects) abroad|overseas (?:japanese|chinese|communities)|foreign residents|aliens resident)\b
household-registration|government|\b(?:household registration|family registers?|registration of (?:births|deaths|marriages))\b
suicide|population|\bsuicides?\b
infant-mortality|population|\binfant (?:mortality|deaths?)\b
government-offices|government|\b(?:ministries|cabinet|government officials|civil service|civil servants|authori[sz]ed staff|government personnel|government departments?|government burea(?:u|ux)|departments? of (?:state|finance|education)|official personnel|administrative machinery)\b
elections-and-parties|government|\b(?:elections?|electors?|franchise[- ]holders|political parties|voters?|ballots?|political representation)\b
local-government|government|\b(?:local government|municipal (?:councils|corporations|administration)|prefectural assemblies|communal assemblies)\b
imperial-household|government|\b(?:imperial household|imperial family|imperial house|imperial court|royal family|royal household|emperors? and reigns|reigning sovereigns)\b
honours-and-ranks|government|\b(?:decorations|honou?rs|orders of merit|ranks|peerage|nobility|golden kite)\b
constitutions-and-laws|government|\b(?:constitutions?|legislation|laws enacted|ordinances promulgated|legislative enactments)\b
administrative-divisions|government|\b(?:administrative divisions|prefectures and districts|provincial boundaries|administrative districts|municipalities and villages)\b
passports-and-travel-permits|government|\b(?:passports?|travel permits|residence permits)\b
foreign-concessions|informal-imperialism|\bforeign concessions?\b
extraterritoriality|informal-imperialism|\b(?:extraterritorial|extra-territorial|consular jurisdiction)\w*\b
treaty-ports|informal-imperialism|\btreaty ports?\b
foreign-garrisons|informal-imperialism|\b(?:foreign garrisons?|foreign troops stationed|japanese garrisons? in china)\b
annexation-and-protectorates|colonial-rule|\b(?:annexation|protectorates?)\b
colonial-administration|colonial-rule|\b(?:residency[- ]general|government[- ]general|governor[- ]general|colonial administration|mandate administration)\b
settler-migration|colonial-rule|\b(?:colonial settlement|state[- ]sponsored settlers|settlement colonists|colonisation projects|colonization projects)\b
assimilation-policies|colonial-rule|\b(?:assimilation policies|assimilation measures|japanisation|japanization)\b
independence-movements|government|\b(?:independence movements?|national liberation)\b
frontier-policing|crime-and-justice|\b(?:frontier police|frontier policing|aboriginal police)\b
guard-lines|indigenous-peoples|\b(?:guard[- ]lines?|a[iy]u[- ]sen)\b
diplomatic-service|foreign-relations|\b(?:diplomatic|consular|consulates?|embassy|embassies|legations?|ambassadors?|ministers abroad|foreign representatives accredited)\b
treaties|foreign-relations|\b(?:treaties|treaty(?! ports?))\b
international-organisations|foreign-relations|\b(?:league of nations|united nations|international organisations?|international organizations?)\b
army|military|\b(?:army|armies|troops|military officers|standing army|land forces)\b
navy|military|\b(?:navy|naval|warships?|gunboats?|battleships?|cruisers?|destroyers?|submarines|torpedo[- ]boats)\b
war-and-mobilisation|military|\b(?:mobilisation|mobilization|war expenditure|military campaigns?|war preparations?)\b
air-force|military|\b(?:air force|military aviation|naval aviation)\b
arms-and-arsenals|military|\b(?:armaments?|arsenals?|military weapons?|guns and ammunition)\b
military-casualties|military|\b(?:military casualties|war casualties|soldiers killed|troops killed)\b
recruitment-and-conscription|military|\b(?:conscription|conscripts?|recruitment|army recruits?)\b
air-defence|military|\b(?:air defence|air defense|air[- ]raid precautions)\b
economic-planning|economy|\b(?:economic plan|five[- ]year plan|industrial development plan)\w*\b
economic-controls|economy|\b(?:economic control|industrial control|controlled economy)\w*\b
price-controls|economy|\b(?:price controls?|controlled prices|price fixing|maximum prices)\b
inflation|economy|\binflation\b
cooperatives|economy|\b(?:co[- ]?operatives?|co[- ]operative societies|co[- ]operative unions)\b
reconstruction|economy|\b(?:reconstruction|rehabilitation of industries)\b
food-supply-and-rationing|economy|\b(?:food supply|food rationing|rationed food|foodstuffs rationing)\b
state-monopolies|economy|\b(?:state monopol\w*|government monopol\w*|monopoly receipts|monopoly revenue)\b
rural-development|agriculture|\brural development\b
production-subsidies|economy|\b(?:subsidies|subsidised|subsidized|industrial grants|agricultural grants|bounties granted)\b
public-budgets|finance|\b(?:budgets?|national expenditure|national revenue|government expenditure|government revenue|public revenue|public expenditure|municipal expenditure|prefectural expenditure|local expenditure|local revenue|special accounts|national accounts)\b
taxation|finance|\b(?:tax(?:es|ation)?|excise|taxable|taxpayers|octroi|fiscal levies)\b
public-debt|finance|\b(?:public debts?|national debts?|government loans|government bonds|municipal loans|municipal bonds|national loans|treasury notes|public loans|provincial loans|debt service)\b
banking|finance|\b(?:banks?|banking)\b
savings-and-loans|finance|\b(?:savings|deposits|loans?|advances and deposits|deposits and advances)\b
currency|finance|\b(?:currency|currencies|coins?|coinage|banknotes?|paper money|paper moneys|mints?)\b
foreign-exchange|finance|\b(?:foreign exchange|exchange rates?|rates of exchange|exchange quotations)\b
securities-and-investment|finance|\b(?:securities|stock exchanges?|debentures|investment|investments|stocks and bonds|paid[- ]up capital)\b
insurance-and-pensions|finance|\b(?:insurance|pensions|annuities)\b
national-income-and-wealth|economy|\b(?:national wealth|national income|gross national product|gross domestic product)\b
foreign-loans|finance|\b(?:foreign loans?|external loans?|foreign borrowing)\b
foreign-investment|finance|\b(?:foreign investments?|foreign capital|capital invested by foreigners)\b
indemnities|foreign-relations|\bindemnities\b|\bindemnity\b
customs-revenue|finance|\b(?:customs revenue|customs duties collected|receipts from customs)\b
likin|finance|\blikin\b
salt-tax|finance|\bsalt (?:tax|gabelle|revenue)\b
land-tax|finance|\bland tax\b
mutual-credit|finance|\b(?:mutual credit|mutual loan societies|mujin)\b
pawnshops|finance|\b(?:pawnshops?|pawn[- ]?broking|pawnbrokers?)\b
interest-rates|finance|\b(?:interest rates?|rates of interest)\b
public-property|finance|\b(?:government (?:property|land)|public property|state property|national property|prefectural property|municipal property|property of (?:urban|rural|municipal))\b
agricultural-credit|finance|\b(?:agricultural credit|farm loans?|agricultural loans?)\b
head-tax|finance|\b(?:head tax|poll tax)\b
domestic-trade|trade|\b(?:domestic trade|home trade|internal trade)\b
imports|trade|\b(?:imports?|imported|importation)\b
exports|trade|\b(?:exports?|exported|exportation)\b
tariffs|trade|\b(?:tariffs?|customs duties|customs rates|import duties|export duties)\b
prices|trade|\b(?:prices?|price indices|price index|quotations|retail prices|wholesale prices)\b
companies|trade|\b(?:companies|company|firms|corporations|incorporation|commercial establishments|joint[- ]stock|partnerships)\b
business-associations|trade|\b(?:chambers? of commerce|trade associations?|business associations?|industrial associations?|merchant guilds?|trade guilds?)\b
re-exports|trade|\bre[- ]exports?\b
transit-trade|trade|\btransit trade\b
advertising|press|\b(?:advertising|advertisements?|advertisers?)\b
warehousing|trade|\b(?:warehouses?|warehousing|bonded storage)\b
markets-and-exchanges|trade|\b(?:markets?|commodity exchanges?)\b
intra-imperial-trade|trade|\b(?:trade (?:with|between).{0,45}(?:colonies|dependencies)|inter[- ]imperial trade|shipments? (?:to|from) japan)\b
arable-land|agriculture|\b(?:arable land|cultivated (?:land|area)|area under cultivation|area under (?:various )?crops|tillage area|harvested area|crop acreage|one[- ]crop|two[- ]crop)\b
land-tenure|agriculture|\b(?:land tenure|landowners?|tenant farmers|farm tenancy|tenanted land|farm rents)\b
crop-production|agriculture|\b(?:crop production|agricultural (?:production|products|crops)|farm produce|miscellaneous grains|minor crops)\b
horticulture|agriculture|\b(?:horticulture|fruit trees|orchards|vegetables|walnuts?|garden crops|fruit production)\b
livestock|agriculture|\b(?:livestock|live stock|cattle|horses|sheep|goats|pigs|swine|dairy|milk|stock[- ]breeding|slaughtering|slaughtered)\b
sericulture|agriculture|\b(?:sericulture|silkworms?|cocoons?|mulberry)\b
irrigation|agriculture|\birrigation\b
eggs-and-poultry|agriculture|\b(?:eggs|poultry|fowls|chickens)\b
farm-inputs|agriculture|\b(?:farm inputs|agricultural implements|manures|fertili[sz]er consumption|fertili[sz]ers used|farm labour costs)\b
agricultural-extension|agriculture|\b(?:agricultural experiment stations?|agricultural extension|agricultural demonstration)\b
land-improvement|agriculture|\b(?:land improvement|agricultural land improvement|rearrangement of arable land)\b
shifting-cultivation|agriculture|\bshifting cultivation\b
forest-area|forestry|\b(?:forest area|area of forests?|forest land|forests? and plains|forests? and fields|forests? and wild)\b
timber|forestry|\b(?:timber|lumber|sawn wood)\b
forest-management|forestry|\b(?:forest management|forest protection|forest administration|forest exploitation|forest utilisation|forest utilization)\b
afforestation|forestry|\b(?:afforestation|reforestation|tree planting)\b
fuelwood-and-charcoal|forestry|\b(?:fuelwood|firewood|wood fuel|charcoal)\b
fishing|fisheries|\b(?:fishing|fisheries|fishery|fish catch|fish caught|catch of fish|fishing boats|marine products|fishery products)\b
aquaculture|fisheries|\b(?:aquaculture|aquiculture|fish culture|fish breeding|pearl culture|oyster culture)\b
whaling|fisheries|\b(?:whaling|whales)\b
fishing-rights-and-licences|fisheries|\b(?:fishing (?:rights|licen[cs]es)|fishery (?:rights|licen[cs]es))\b
seaweed|fisheries|\b(?:seaweed|kelp|agar[- ]agar)\b
mineral-production|mining|\b(?:mineral (?:productions?|products|output)|mining output|mine output|output of mines|mines and miners|mines (?:worked|working|operated))\b
mineral-reserves|mining|\b(?:mineral (?:deposits|reserves|resources)|ore reserves|coal reserves|coal deposits)\b
mining-rights-and-concessions|mining|\b(?:mining (?:rights|concessions|permits|licen[cs]es|claims)|mining areas|prospecting rights)\b
industrial-output|manufacturing|\b(?:industrial output|industrial production|manufactured goods|manufacturing (?:industries|industry|output)|factory production|factories|industrial establishments)\b
textiles|manufacturing|\b(?:textiles?|weaving|spinning|spindles|yarn|fabrics|textile mills)\b
iron-and-steel|manufacturing|\b(?:iron and steel|steel|pig iron|cast iron|iron works|ironworks)\b
machinery|manufacturing|\b(?:machinery|machine tools|engines|engineering works)\b
shipbuilding|manufacturing|\b(?:shipbuilding|shipyards?|dockyards?|vessels built|ships built|ships constructed|construction of ships)\b
chemicals|manufacturing|\b(?:chemicals?|chemical industry|sulphuric acid|sulfuric acid|caustic soda)\b
fertilisers|manufacturing|\bfertili[sz]ers?\b
paper-and-pulp|manufacturing|\b(?:paper and pulp|paper[- ]making|paper mills|japanese paper|western paper|pulp|manufacture of paper)\b
ceramics-and-glass|manufacturing|\b(?:ceramics|pottery|porcelain|glassware|glass manufacture|earthenware)\b
food-processing|manufacturing|\b(?:food processing|confectionery|flour mills?|flour milling|food manufacturing)\b
cottage-industries|manufacturing|\b(?:cottage industries|household industries|domestic manufacture)\b
cement-and-bricks|manufacturing|\b(?:cement|bricks?|tiles)\b
vegetable-oils|manufacturing|\b(?:vegetable oils?|vegetable tallow|oil mills?|edible oils?)\b
rice-milling|manufacturing|\b(?:rice milling|rice mills?|rice[- ]cleaning)\b
canning|manufacturing|\b(?:canning|canneries|canned foods?|canned fish|canned pineapple)\b
electricity|utilities|\b(?:electricity|electric power|electric lighting|electric light|power stations?|power plants?|electric supply)\b
gas|utilities|\b(?:gas supply|gas works|gasworks|gas production|gas lighting|gas consumption)\b
water-and-sewerage|utilities|\b(?:waterworks|water supply|sewerage|sewage|water[- ]works|water services)\b
construction|utilities|\b(?:construction|buildings erected|building permits|building operations|public works)\b
flood-control|utilities|\b(?:flood control|flood prevention|embankments|dikes)\b
river-conservancy|utilities|\b(?:river conservancy|river improvement|river works)\b
land-reclamation|utilities|\bland reclamation\b
hydroelectricity|utilities|\b(?:hydroelectric|hydro-electric|water power)\b
erosion-control|utilities|\b(?:erosion control|sand control|sabo)\b
urban-planning|utilities|\b(?:urban planning|town planning|city planning)\b
railways|transportation|\b(?:railways?|railroads?|rail roads?|locomotives|goods wagons|passenger carriages|rolling stock|rail traffic|train mileage)\b
roads-and-bridges|transportation|\b(?:roads?|bridges?|highways?)\b
road-transport|transportation|\b(?:motor vehicles|motor cars|motor buses|motor transport|automobiles|rickshaws|road traffic|road transport|motor trucks|bus lines|bus services)\b
shipping|transportation|\b(?:shipping|merchant marine|mercantile marine|merchant fleet|steamships?|steamers?|sailing vessels|junks|vessels|ships|registered tonnage|seamen|bluejackets)\b
ports|transportation|\b(?:ports?|harbou?rs?|docks)\b
aviation|transportation|\b(?:aviation|air transport|air traffic|airlines?|civil aircraft|aeroplanes)\b
tourism|transportation|\b(?:tourism|tourists?|hotels?|foreign visitors|tourist travel)\b
trams|transportation|\b(?:trams?|tramways?|street railways?|streetcars?|street cars)\b
inland-navigation|transportation|\b(?:inland navigation|river navigation|river steamers?|river transport|river shipping)\b
freight-and-transport-costs|transportation|\b(?:freight rates|freight charges|fares|transport costs|berth charges)\b
navigation-aids|transportation|\b(?:navigation aids|lighthouses|light[- ]houses|coast lighting|navigation signals|buoys)\b
transport-accidents|transportation|\b(?:shipwrecks|railway accidents|traffic accidents|transport accidents|ships lost)\b
postal-services|communications|\b(?:postal|posts?|post offices|postage|parcels|mail)\b
telegraph|communications|\b(?:telegraphs?|telegraphic|telegrams|cablegrams|submarine cables)\b
telephone|communications|\b(?:telephones?|telephonic)\b
radio|communications|\b(?:radio|wireless|broadcasting)\b
postal-remittances|communications|\b(?:money orders|postal remittances|postal giro)\b
employment-and-unemployment|labour|\b(?:employment|unemployment|employees|workforce|work force|workers employed|factory workers|industrial workers|number of workers)\b
wages|labour|\b(?:wages|salaries|pay scales|salary scales|remuneration|wage rates)\b
working-conditions|labour|\b(?:working conditions|hours of work|working hours|labour conditions|labor conditions)\b
trade-unions|labour|\b(?:trade unions|labour unions|labor unions|workers unions|labour organisations|labor organizations)\b
labour-disputes|labour|\b(?:labou?r disputes|strikes|lockouts|lock-outs)\b
child-labour|labour|\b(?:child labour|child labor|juvenile workers|child workers)\b
women-workers|labour|\b(?:women workers|female workers|female factory workers|women employed)\b
employment-placement|labour|\b(?:employment exchanges|employment placement|employment agencies|labour exchanges|labor exchanges)\b
industrial-accidents|labour|\b(?:industrial accidents|factory accidents|mine accidents|accidents (?:in|at) (?:the )?mines|occupational injuries|workmen.s compensation)\b
schools-and-pupils|education|\b(?:schools?|pupils|students|school attendance|educational institutions|education)\b
primary-education|education|\b(?:primary schools?|elementary schools?|primary education|elementary education|national schools?)\b
secondary-education|education|\b(?:middle schools?|secondary schools?|high schools?|secondary education)\b
higher-education|education|\b(?:universities|university|colleges|higher education)\b
vocational-education|education|\b(?:vocational|technical schools?|industrial schools?|professional schools?|commercial schools?|agricultural schools?|normal and technical colleges)\b
teachers|education|\b(?:teachers|instructors|teaching staff|faculty)\b
libraries|education|\blibrar(?:y|ies)\b
literacy-and-adult-education|education|\b(?:literacy|illiteracy|adult education|popular education|lecture halls|continuation schools|adult classes)\b
students-abroad|education|\b(?:students abroad|students studying abroad|students in foreign countries)\b
mission-schools|education|\b(?:mission schools|missionary schools|religious schools)\b
education-finance|education|\b(?:(?:school|educational|education) (?:finance|expenses|expenditure|expenditures|budgets?|funds|costs|endowments)|expenses for education)\b
traditional-schools|education|\b(?:traditional schools|village study halls|classical schools|private chinese schools)\b
teacher-training|education|\b(?:normal schools?|teacher training|teachers. training)\b
kindergartens|education|\bkindergartens?\b
special-education|education|\b(?:special education|schools for the (?:blind|deaf)|blind and deaf schools)\b
language-education|education|\b(?:language schools|language teaching|language education)\b
school-boarding|education|\b(?:school dormitories|school boarders|school boarding|boarders at public school)\b
apprenticeships|education|\bapprentice(?:ship)?s?\b
shinto|religion|\b(?:shinto|shrines|shrine priests)\b
buddhism|religion|\b(?:buddhis[mt]|buddhist temples|buddhist priests)\b
christianity|religion|\b(?:christian|christianity|roman catholic|protestant|catholic church)\b
confucianism|religion|\bconfucian\w*\b
taoism|religion|\b(?:taois[mt]|daois[mt])\b
islam|religion|\b(?:islam|moslem|muslim)\b
judaism|religion|\b(?:judaism|jewish congregations)\b
missions|religion|\b(?:missionaries|missionary|religious missions)\b
ancestor-rites|religion|\b(?:ancestor worship|ancestor rites)\b
folk-religion|religion|\bfolk religion\b
religious-institutions|religion|\b(?:religious institutions|religious bodies|religious establishments|religious sects|churches|temples and priests|religious personnel)\b
tenrikyo|religion|\btenrikyo\b
religious-affiliation|religion|\b(?:religious affiliation|adherents|believers|religious membership)\b
police|crime-and-justice|\b(?:police|constabulary|gendarmerie)\b
courts|crime-and-justice|\b(?:courts|court of cassation|judicial institutions|judges|procurators|prosecutors)\b
offences-and-convictions|crime-and-justice|\b(?:crimes?|criminal|convicted|convictions|penalties|sentence carried out|executions|offences|offenses|robbery|peculation|fraud|arrests|not guilty|acquittals|verdicts)\b
prisons|crime-and-justice|\b(?:prisons?|prisoners?|prison-inmates|convicts|penitentiaries|detentions?)\b
smuggling|crime-and-justice|\bsmuggling\b
piracy|crime-and-justice|\b(?:piracy|pirates)\b
sex-work|crime-and-justice|\b(?:prostitution|prostitutes|brothels|licensed women)\b
political-policing|crime-and-justice|\b(?:political police|political policing|political prisoners)\b
summary-justice|crime-and-justice|\b(?:summary police judgments|summary judgments|summary demand procedure|summary justice)\b
civil-litigation|crime-and-justice|\b(?:civil (?:cases|suits|actions|litigation|provisional attachments)|bankruptcy|bankruptcies)\b
land-registration|government|\b(?:land registration|registration of land|land registers|real estate registration)\b
prison-labour|crime-and-justice|\b(?:prison labour|prison labor|prison industries|prisoners. work|convict labour|convict labor)\b
juvenile-justice|crime-and-justice|\b(?:juvenile courts|juvenile delinquents|reformatories|reformatory|juvenile justice)\b
prisoner-aftercare|welfare|\b(?:prisoner aftercare|aftercare of prisoners|discharged prisoners|released prisoners. relief|offender rehabilitation)\b
corporal-punishment|crime-and-justice|\b(?:corporal punishment|flogging)\b
mediation-and-arbitration|crime-and-justice|\b(?:mediation|arbitration|conciliation)\b
opium|narcotics|\b(?:opium|poppy)\b
morphine-and-heroin|narcotics|\b(?:morphine|morphia|heroin)\b
drug-suppression|narcotics|\b(?:narcotic suppression|opium suppression|drug suppression|narcotics control|prohibited drugs)\b
opium-licensing|narcotics|\b(?:opium licen[cs]|licen[cs]ed opium|opium smokers registered)\w*\b
drug-consumption|narcotics|\b(?:opium consumption|narcotic consumption|drug consumption)\b
medical-services|health|\b(?:hospitals?|medical practitioners|physicians|doctors|dentists|patients treated|medical services|clinics|nurses|midwives)\b
diseases|health|\b(?:diseases|causes? of death|deaths? by cause|sick[- ]rates?|sickness|tuberculosis|cholera|typhoid|dysentery|smallpox|venereal)\b
public-health|health|\b(?:public health|sanitation|sanitary|health administration|health stations)\b
nutrition|health|\b(?:nutrition|nutritional|dietary|calorie|food consumption per head)\b
epidemics|health|\b(?:epidemics|infectious diseases|contagious diseases|communicable diseases)\b
quarantine|health|\bquarantine\b
maternal-and-child-health|health|\b(?:maternal health|child health|maternity|obstetric|infant health)\b
pharmaceuticals|health|\b(?:pharmaceutic\w*|pharmacies|pharmacists|medicines)\b
vaccination|health|\b(?:vaccination|vaccinated|inoculation|immunisation|immunization)\b
leprosy|health|\b(?:leprosy|lepers)\b
veterinary-health|health|\b(?:veterinary|animal diseases|livestock diseases|epizootic|cattle plague)\b
malaria|health|\bmalaria\b
mental-health|health|\b(?:mental health|mentally ill|mental illness|lunatics|insane|psychiatric)\b
food-inspection|health|\b(?:food inspection|meat inspection|slaughter inspection)\b
poor-relief|welfare|\b(?:poor relief|pauper relief|gruel kitchens|indigent relief|relief funds)\b
child-welfare|welfare|\b(?:foundlings|orphans|orphanages|child welfare|infant welfare)\b
housing|welfare|\b(?:housing|dwellings|tenements)\b
household-budgets|welfare|\b(?:household budgets|family budgets|family income|household expenditure|family expenditure)\b
poverty|welfare|\b(?:poverty|poor households|paupers|indigence)\b
refugees-and-displacement|welfare|\b(?:refugees|displaced persons|displacement)\b
charitable-institutions|welfare|\b(?:charitable institutions|charities|charitable societies|charity institutions)\b
foreign-aid|welfare|\b(?:foreign aid|international relief aid)\b
work-relief|welfare|\b(?:work relief|relief works|unemployment relief works)\b
veterans-and-military-families|welfare|\b(?:veterans|military families|soldiers. families|disabled soldiers|military dependants)\b
youth-organisations|welfare|\b(?:youth organisations|youth organizations|young men.s associations|boy scouts)\b
welfare-institutions|welfare|\b(?:social work institutions|social welfare institutions|social work facilities|social work establishments|social work agencies)\b
newspapers|press|\b(?:newspapers|newspaper)\b
periodicals|press|\b(?:periodicals|journals|magazines)\b
books|press|\b(?:books|book publishing|book publication|publications)\b
news-agencies|press|\bnews agencies\b
censorship|press|\b(?:censorship|press suppression|publications suppressed|publication bans)\b
arts-and-music|culture|\b(?:fine arts|arts and crafts|art exhibitions|music|musical|paintings|sculpture)\b
theatre-and-cinema|culture|\b(?:theatres|theaters|cinemas|motion pictures|cinematograph|films)\b
museums-and-heritage|culture|\b(?:museums|historic monuments|national treasures|heritage|historic sites)\b
recreation-and-amusements|culture|\b(?:recreation|amusements|public entertainments|pleasure resorts)\b
archaeology|culture|\barchaeolog\w*\b
sports-records|sport|\b(?:sports records|athletic records?|champions|championship results|olympic results|records in swimming|track and field records|winners of)\b
sports-organisations-and-facilities|sport|\b(?:sports clubs|athletic clubs|sporting clubs|sports associations|stadiums|sports grounds|athletic grounds|golf clubs|golf courses)\b
sports-participation|sport|\b(?:sports participation|athletes participating|athletic participants|entrants in|competitors in)\b
scientific-research|science-and-technology|\b(?:scientific research|research institutes|research institutions|scientific institutions|scientific societies)\b
patents-and-trademarks|science-and-technology|\b(?:patents|patent right|trade[- ]?marks|utility models|registration of designs)\b
measurement-and-units|science-and-technology|\b(?:weights.{0,15}measures|measurement standards|measuring instruments|units of measurement)\b
historical-chronologies|history|\b(?:historical chronology|historical chronologies|chronological table|chronology of events|historical events|chronological outline|general chronology)\b
banditry|crime-and-justice|\b(?:banditry|bandits)\b
addiction-treatment|health|\b(?:addiction treatment|opium treatment|drug rehabilitation|opium refuges)\b
balance-of-payments|finance|\bbalance of payments\b
services-and-invisible-trade|trade|\b(?:invisible trade|invisible exports|invisible imports|invisible balance)\b
migrant-remittances|finance|\b(?:migrant remittances|emigrant remittances|overseas remittances)\b
labour-productivity|labour|\blabou?r productivity\b
cost-of-living|economy|\bcost of living\b
calendars-and-time|science-and-technology|\b(?:calendar conversion|calendar equivalents|era equivalents|time zones|standard time|reckoning of time)\b
hunting|government|\b(?:hunting licen[cs]es|hunting permits|hunting returns)\b
economic-indicators|economy|\b(?:economic indicators|economic barometer|general economic statistics|economic index numbers|economic indices)\b
route-distances|transportation|\b(?:route distances|coast distances|distances (?:from|between|via|up)|journey times|distances and fares)\b
commodity-origins|geography|\b(?:commodity origins|producing districts of principal commodities|products and producing regions|provincial products and origins)\b
anthropometry|science-and-technology|\b(?:anthropometr\w*|cephalic index|bodily measurements|head measurements|head shapes)\b
census-and-survey-methods|population|\b(?:census forms|census schedules|enumeration forms|census questions|survey samples|sample distribution|sampling methods)\b
public-holidays-and-commemorations|culture|\b(?:public holidays|national holidays|commemoration days|commemorative days|national anniversaries)\b
legal-profession|crime-and-justice|\b(?:lawyers|advocates|barristers|attorneys|legal practitioners)\b
writing-systems-and-phonetics|culture|\b(?:phonetic|phonetics|romanisation|romanization|writing systems|phonetic alphabet|national alphabet|syllabaries)\b
real-estate|finance|\b(?:real estate|property transactions|land transactions|land and building rents|urban land rents|real property values)\b
printing|manufacturing|\b(?:printing|printers|printing works|lithography|typesetting)\b
professional-associations|labour|\b(?:medical associations|professional associations|engineering associations|bar associations)\b
demobilisation|military|\b(?:demobilisation|demobilization|disbandment|troops disbanded|disbanding of troops)\b
school-curricula|education|\b(?:curricul\w*|school timetables|school subjects|course hours)\b
domestic-service|labour|\b(?:domestic servants|domestic service|household servants|families employing servants)\b
native-place-associations|culture|\b(?:native[- ]place associations|provincial guild halls|huiguan)\b
fish-and-fish-products|fisheries|\b(?:fish and fish products|fish and fishery products|fish products traded)\b
militias-and-volunteer-forces|military|\b(?:militias?|volunteer corps|volunteer forces|municipal defence forces)\b
diplomatic-claims|foreign-relations|\b(?:diplomatic claims|compensation claims.{0,25}(?:foreign|country|countries)|lincheng claims)\b
colonies-and-leased-territories|colonial-rule|\b(?:colonies and leased territories|foreign possessions|colonial possessions)\b
foreign-trade|trade|\b(?:foreign trade|external trade|international trade|trade with different countries|volume of trade|trade returns at|chief articles of trade between)\b
foreign-trade-relations|foreign-relations|\b(?:first direct trade|first trade dealings|trade dealings with.{0,25}empire|first commercial contacts)\b
riots-and-civil-unrest|crime-and-justice|\b(?:riots?|civil unrest|civil disturbances)\b
"""

COMMODITY_TEXT = r"""
rice|\brice\b|\bpaddy\b
cereals|\b(?:cereals|grains)\b
tea|\btea\b
wheat|\bwheat\b
soybeans|\b(?:soybeans?|soya beans?|soy beans?|bean cake|bean oil)\b
oilseeds|\b(?:oilseeds|oil seeds|sesame|rapeseed|rape seed|groundnuts|peanuts)\b
ginseng|\bginseng\b
barley|\bbarley\b
sugarcane|\bsugar[- ]?cane\b
pineapples|\bpineapples?\b
plant-fibres|\b(?:hemp|ramie|jute|flax|plant fibres|vegetable fibres)\b
indigo|\bindigo\b
coconuts|\bcoconuts?\b
copra|\bcopra\b
coffee|\bcoffee\b
camphor|\bcamphor\b
bamboo-and-rattan|\b(?:bamboo|rattan)\b
coal|\bcoal\b
petroleum|\b(?:petroleum|crude oil|kerosene|shale oil|gasoline|paraffin)\b
gold|\bgold\b(?!en)
silver|\bsilver\b
copper|\bcopper\b
iron-ore|\biron ore\b
tin|\btin\b(?!ned)
tungsten|\btungsten\b
antimony|\bantimony\b
manganese|\bmanganese\b
lead-and-zinc|\b(?:lead|zinc)\b
salt|\bsalt\b
graphite|\bgraphite\b
phosphate-rock|\b(?:phosphate(?: rock)?|phosphorite)\b
silk|\b(?:silk|silks|silken|silk reeling)\b
cotton|\bcotton\b
wool|\b(?:wool|woollen|woolen)\b
rayon|\b(?:rayon|artificial silk)\b
sugar|\bsugar\b(?![- ]?cane)
alcohol|\b(?:alcohol|alcoholic|sake|beer|breweries|brewing|spirits|wine|liquors)\b
tobacco|\b(?:tobacco|cigarettes|cigars)\b
rubber|\brubber\b
leather-and-furs|\b(?:leathers?|furs|hides|tanning)\b
tung-oil|\btung oil\b
asbestos|\basbestos\b
mercury|\b(?:mercury|quicksilver)\b
"""

RULES = []
for line in RULE_TEXT.strip().splitlines():
    identifier, domain, expression = line.split("|", 2)
    RULES.append((identifier, domain, re.compile(expression, re.I)))
for line in COMMODITY_TEXT.strip().splitlines():
    identifier, expression = line.split("|", 1)
    RULES.append((identifier, "commodity", re.compile(expression, re.I)))
