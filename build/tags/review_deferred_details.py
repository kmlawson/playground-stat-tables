#!/usr/bin/env python3
"""Assistant-authored contents review of the fixed Manchuria/South Seas cohort."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_tags as b
OUT = HERE / 'reviews/manchuria-south-seas-detailed-2026-10-27'


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def frozen_records():
    path = OUT / 'records.json'
    manifest = b.read(OUT / 'manifest.json')
    if not path.exists():
        prior = {r['key']:r['previous'] for r in b.read(OUT / 'reviewed-decisions.json')['tables']}
        cohort = {r['key']:r['book'] for r in b.read(HERE / 'reviews/deferred-detailed-tags-2026-10-26.json')['tables']}
        wanted = set(manifest['keys']); records=[]
        for book,tables,_,_ in b.committed_pages():
            for table in tables:
                key=book['slug']+':'+table['id']
                if key in wanted:
                    records.append({'key':key,'book':cohort[key],'table':table,'previous':prior[key]})
        b.write(path,records)
    assert b.sha(path)==manifest['records_sha256']
    return b.read(path)


def norm(value):
    return unicodedata.normalize('NFKC', str(value or '')).lower()


def material(record):
    t = record['table']; en = t.get('en') or {}
    title = norm(en.get('t') or t.get('title'))
    headers = [str(x) for p in t.get('parts', []) for x in [p.get('label') or '', *p.get('columns', [])]]
    cells = [str(x) for p in t.get('parts', []) for row in p.get('rows', []) for x in row]
    body = norm(' | '.join(headers + cells))
    description = norm(en.get('d'))
    context = norm(' | '.join(str(t.get(f) or '') for f in ('context', 'caption_extra')))
    notes = norm(' | '.join(str(x) for f in ('footnotes', 'transcriber_notes') for x in t.get(f, [])))
    return title, body, description, context, notes


# Ordered by the actual function or subject of the table. A product name in a
# budget, inspection, legal case or cost-of-living row is not a product subject.
TITLE_RULES = [
 ('measurement-and-units', r'converting.*(?:weight|measure)|standards of weight|distance and length|land measure|quantity, capacity|^weights$|metric.*equivalent'),
 ('foreign-exchange', r'haikwan tael equivalents|foreign money|dairen[-–].*(?:t\.t\.|15 days)|quotation of chao|parit(?:y|ies)|exchange.*(?:quotation|rate)|^exchange quotations'),
 ('currency', r'notes (?:issued|and specie)|amount of notes|^moneys$|note circulation|money in circulation|currency circulation'),
 ('agricultural-credit', r'rural credit|farm.*(?:credit|loans)|agricultural financing'),
 ('markets-and-exchanges', r'produce exchanges|government exchanges|private exchanges|produce (?:deals|transactions)|(?:transaction|quotation) (?:and quotation )?units|quotation standards|transaction results.*exchanges|spot and time transactions'),
 ('banking', r'clearing amounts|clearing house|bank clearings'),
 ('balance-of-payments', r'international accounts|balance of international'),
 ('household-budgets', r'income and expenses|cost of food.*porters|family.*(?:income|expenditure)|household.*(?:income|expenses)|family budgets'),
 ('cost-of-living', r'cost of living|living costs'),
 ('prices', r'charges for services|commodity prices|wholesale.*(?:index|quotation)|retail.*(?:index|quotation)|price levels|price.*index'),
 ('interest-rates', r'interest.*rates|rates of interest'),
 ('economic-planning', r'five[- ]year industrial plan|industrial.*five[- ]year|five[- ]year.*industrial'),
 ('economic-indicators', r'value of agricultural, mineral and manufacturing|economic progress|economic barometers|economic indicators'),
 ('public-budgets', r'(?:revenue|expenditure|appropriation|reserve funds).*(?:province|provinces|provincial|government|department|fiscal|tatung|manchoukuo|local expenses)|(?:province|provincial).*finance|estimated (?:revenue|expenditure)|ordinary and extraordinary|expenditures by department|revenue stamp receipts|licence fees and charges|fines and confiscations|miscellaneous receipts|expenditure from the reserve'),
 ('taxation', r'income[- ]tax payers|taxpayer|taxable income|direct taxes|indirect taxes'),
 ('public-debt', r'government loan|national debt|public borrowing|debt redemption'),
 ('companies', r's\.\s*m\.\s*r\..*(?:capital|profit|loss|outlays)|(?:expenditures|receipts.*expenditure|expenditure.*receipts).*s\.\s*m\.\s*r\.|joint enterprises|commercial activities|business organi[sz]ation|foreign merchants and business places'),
 ('land-area', r'number and area of islands|area of the principal islands|area of the japanese realm|^area$'),
 ('physical-geography', r'positions? of.*islands|principal peaks|heights? of mountains|position, area|principal mountains|highest.*mountains'),
 ('rivers-and-waterways', r'principal (?:lakes|rivers)|rivers.*(?:length|width|basin)'),
 ('weather', r'climatic conditions|frost and snow|sunshine hours|monthly average moisture|evaporation quantity|climatological|meteorological|temperature|rainfall|humidity'),
 ('administrative-divisions', r'name and territory of each province|provinces in manchoukuo|new provinces'),
 ('population-totals', r'census of|city population|inhabitants|resident population|population.*(?:cities|provinces)|population by'),
 ('employment-and-unemployment', r'workers and dependents|number of workmen|workers and miners|labourers employed'),
 ('migration', r'(?:coolie|immigrant|labourer).*(?:entering|leaving|movement)|number of immigrants|chinese settlers|entering manchoukuo|leaving manchoukuo|^settlers$|immigrants.*settled|korean immigrants|japanese and korean settlers|distribution of korean settlers'),
 ('settler-migration', r'farm[- ]settlements|first five settlements|youth volunteer settlers|chosenese (?:settlements|concentration[- ]village)|chosenese farm'),
 ('land-tenure', r'tenant[- ]to[- ]owner|land holding|tenant farming'),
 ('agricultural-extension', r'distribution.*(?:experimental stations|improved seed)|agricultural experiment'),
 ('arable-land', r'land cultiva|cultivated area|land utili[sz]ation|crop areas|growth in cultivated'),
 ('crop-production', r'crop outputs|ordinary crops|crop harvest|main crops compared|cereal production|agricultural products'),
 ('soybeans', r'world.*bean|bean zones|bean production|beancake|bean oil|soya[- ]?bean'),
 ('cereals', r'^kaoliang$|^millet$|^maize$|kaoliang production|millet production|maize production'),
 ('livestock', r'live[- ]?stock|live stocks|farm animals|cattle.*horses'),
 ('forest-area', r'forest areas|forest resources|areas of forests'),
 ('timber', r'lumbering industry|timber output|sawn (?:wood|timber)'),
 ('mineral-production', r'^mineral outputs|mining and metallurgical products|production of minerals'),
 ('mineral-reserves', r'mineral.*(?:reserve|deposit)|(?:coal|ore).*(?:reserve|deposit)'),
 ('industrial-output', r'industrial progress|industrial products|manufacturing production|output.*manufactured products|factory capital and production|miscellaneous industr|industrial establishments'),
 ('textiles', r'fabric industry|gunny bag production'),
 ('silk', r'tusser|tussah|silk.*(?:filature|reeling)|silk(?:en)? fabrics'),
 ('rayon', r'artificial silk|rayon'),
 ('cotton', r'cotton thread|cotton tissues|cotton spinning'),
 ('wool', r'woollen|woolen|wool spinning'),
 ('iron-and-steel', r'pig[- ]iron|metal refining|iron cast|iron and steel|steel materials'),
 ('machinery', r'mechanical equipment|rolling[- ]stock constructed|repairing and rebuilding|vehicle industry|engineering works|machine tools'),
 ('ceramics-and-glass', r'glass (?:production|manufactur|industry)|ceramic industry|porcelain'),
 ('paper-and-pulp', r'paper (?:production|manufacture|industry)|paper[- ]making|pulp (?:production|industry)'),
 ('chemicals', r'paint production|match (?:industry|production)|dyestuff|pigment|soap and candle|explosive manufacture'),
 ('alcohol', r'kaoliang[- ]chiu|liquor production|sake (?:production|brew)|beer (?:production|brew)'),
 ('food-processing', r'miso and soy|flour milling|flour mills'),
 ('vegetable-oils', r'oil milling|oil[- ]mill'),
 ('leather-and-furs', r'hide industry|tanning|leather goods'),
 ('coal', r'\bcokes?\b|\bbriquette\b'),
 ('petroleum', r'production.*oil.*shale|oil.*by[- ]products|oil distillation'),
 ('salt', r'evaporated salts|salt production'),
 ('electricity', r'electric industry|electric stations|electric enterprises|generated power|generating stations|transmission line|light supply condition|power supply condition'),
 ('gas', r'^gas industry|gas works'),
 ('railways', r's\.\s*m\.\s*r\..*traffic|traffic.*s\.\s*m\.\s*r\.|traffic.*c\.\s*e\.\s*r\.|receipts.*c\.\s*e\.\s*r\.|rolling[- ]stock|railway traffic|locomotive|provisional operation'),
 ('inland-navigation', r'sungari river lines|river steamship|river routes'),
 ('aviation', r'air routes|air lines|aeroplane|air transport'),
 ('route-distances', r'route distances|distances between|distance table'),
 ('freight-and-transport-costs', r'comparative rates of principal commodities|passenger fares|freight tariff|freight charges|means of communication'),
 ('postal-services', r'number of mails|mail matter|postal traffic'),
 ('medical-services', r'medical treatment|medical institutions|hospital patients|medical practitioners'),
 ('epidemics', r'anti[- ]plague campaign|plague epidemic'),
 ('vaccination', r'vaccines and serums|vaccination'),
 ('banditry', r'bandit.*(?:subjugation|operations)|subjugation operations'),
 ('army', r'military organi[sz]ation|army organi[sz]ation'),
 ('war-and-mobilisation', r'important military operations|war operations'),
 ('courts', r'judicial force|ssufakungshu|chienlissufahsien'),
 ('government-offices', r'civil administration offices|provincial governments.*personnel'),
 ('real-estate', r'rents for.*villas|land bought and sold'),
 ('construction', r'annual building returns|works accomplished'),
 ('water-and-sewerage', r'reservoir at'),
 ('sports-organisations-and-facilities', r'stadium|sports grounds'),
 ('weather', r'atmospheric pressure|prevailing wind|late frost|wet days|cloud|sunshine|snow season'),
 ('physical-geography', r'principal plains|sedimentary formations|igneous rocks|hot springs'),
 ('earthquakes-and-volcanoes', r'after[- ]?shock|tremor|volcanic|seismic'),
 ('age-and-sex', r'sex ratio'),
 ('births-and-deaths', r'deathrate|birthrate|stillbirth'),
 ('nationality-and-ethnicity', r'naturali[sz]ation|changes of nationality'),
 ('migration', r'emigrants|emigrat'),
 ('overseas-communities', r'japanese residing abroad'),
 ('imperial-household', r'crown landed estates'),
 ('elections-and-parties', r'house of peers|house of representatives|permanent parties|local assemblies'),
 ('wages', r'salary scale'),
 ('courts', r'judicial service|insolvency'),
 ('insurance-and-pensions', r'pension rates|life assurance|life annuity|life annuities|kind of policies'),
 ('administrative-divisions', r'composition of prefectures'),
 ('anthropometry', r'^stature$|average weight|physical dimensions'),
 ('army', r'active list|heavy artillery|standing force'),
 ('recruitment-and-conscription', r'enlistment of men'),
 ('navy', r'mine layers|age[- ]limit of officers'),
 ('aviation', r'regular air service'),
 ('religious-affiliation', r'relative number of followers'),
 ('buddhism', r'no\. of temples|no\. of priests'),
 ('public-health', r'health of pupils|removal of foul matter|grave[- ]yards|crematorium'),
 ('medical-services', r'number of in[- ]patients'),
 ('books', r'original works by subject'),
 ('arts-and-music', r'result of .*exhibition'),
 ('household-budgets', r'bare necessaries|outgoes of salaried'),
 ('national-income-and-wealth', r'wealth and earning'),
 ('land-tenure', r'agrarian movements|tenancy troubles|farmers by extent'),
 ('housing', r'common lodging houses'),
 ('poor-relief', r'public dining halls'),
 ('pawnshops', r'pawn shops'),
 ('employment-and-unemployment', r'number of unemployed'),
 ('veterans-and-military-families', r'military relief service'),
 ('welfare-institutions', r'social work expenses|social work undertakings|social welfare establishments'),
 ('telegraph', r'press rates to'),
 ('radio', r'listeners[- ]in'),
 ('shipping', r'shipowners|oversea services|engineers.*certificates'),
 ('public-budgets', r'state revenue|^general account$|^special account$|continuing expenditures|expenditure.*by departments|revenue and expenditure items'),
 ('securities-and-investment', r'^speculation$|trust business'),
 ('fires', r'conflagrations'),
 ('arable-land', r'area of utili[sz]ed land|area under different kinds of crops'),
 ('crop-production', r'farming industry.*producer of wealth|beans, potatoes'),
 ('industrial-crops', r'production of some special crops'),
 ('livestock', r'stock[- ]farming'),
 ('horticulture', r'output of fruits'),
 ('land-improvement', r'adjustment of farms'),
 ('silk', r'number of basins|thread produced|reeling basins|thread[- ]end|reeling operatives'),
 ('forest-management', r'protection forests|receipts and expenses of state forests'),
 ('forest-area', r'percentage forests|naturally afforested area'),
 ('timber', r'yield of forests|principal timbers'),
 ('afforestation', r'trees newly planted'),
 ('fishing', r'value of catches|permanent fishermen|deep sea catches|catches in hokkaido'),
 ('whaling', r'whale catches'),
 ('aquaculture', r'pearl[- ]oyster'),
 ('mining-rights-and-concessions', r'mining lots'),
 ('mineral-production', r'principal metal mines'),
 ('coal', r'analysis of coals'),
 ('petroleum', r'refined oil'),
 ('employment-and-unemployment', r'mine workers'),
 ('industrial-output', r'production by nature of business|raw materials consumed'),
 ('machinery', r'development of motive power|electric machines|electric motors|electric apparatus|mechanical and engineering|dynamo products'),
 ('textiles', r'wide cloth|narrow cloth'),
 ('wool', r'muslin[- ]de[- ]laine'),
 ('electricity', r'total generating capacity|power generated|lamps and candles|financial features of the electric industry'),
 ('hydroelectricity', r'potential amount of h\.p'),
 ('gas', r'gas industry|proportion of gas'),
 ('industrial-output', r'miscellaneous metallic goods'),
 ('ceramics-and-glass', r'clay pipes'),
 ('chemicals', r'output of matches|synthetic colors|celluloid'),
 ('food-processing', r'demand and supply of flour'),
 ('paper-and-pulp', r'paperboards|native style paper|paper goods'),
 ('foreign-trade', r'trade.*(?:countries|country|manchur|rashin|articles|merchandise)|total values of trade'),
 ('migration', r'coolie immigrants|immigrants landed'),
 ('industrial-output', r'production of furniture|production.*toys|production of watches|buttons.*production|metallic industry'),
 ('tariffs', r'articles coming under|^schedule\b|articles in part i covered'),
 ('public-budgets', r'local expenses|expenditure borne|municipal finance|annual finance|estimate accounts|extraordinary receipts|revenue items continued'),
 ('production-subsidies', r'bounty for motor[- ]cars'),
 ('freight-and-transport-costs', r'passenger fare|freight rate for'),
 ('transport-accidents', r'percentage of accidents'),
 ('scientific-research', r'departments, membership and directors|imperial academy(?! of art)|national research council'),
 ('construction', r'cost (?:per tsubo )?of buildings|cost of buildings'),
 ('insurance-and-pensions', r'mutual ai[dr] associations|number of insured|premiums and annual disbursements|^pension$'),
 ('camphor', r'sale of manufacture'),
 ('securities-and-investment', r'capital invested in farming|capital in different trades|shares, bonds|principal exchanges'),
 ('rice', r'production \(in hectolitres\)'),
 ('barley,wheat', r'area of barley, naked barley and wheat'),
 ('sericulture', r'crop per 1 card'),
 ('electricity', r'^\[?rating\]?$'),
 ('fish-and-fish-products', r'fish oil and train oil'),
 ('road-transport', r'no\. of chauff|municipal auto bus'),
 ('companies', r'deflation in recent years|business promotion|business results in recent|new enterprises|japanese enterprises'),
 ('business-associations', r'production guilds'),
 ('overseas-communities', r'foreigners in chosen|japanese residents in manchoukuo|japanese in kwantung'),
 ('administrative-divisions', r'provinces and seats of office'),
 ('industrial-crops', r'^special crops$'),
 ('afforestation', r'area planted and number of trees'),
 ('crop-production', r'production of principal crops|production of various crops|principal production for'),
 ('horticulture', r'production of fruits'),
 ('land-area', r'number and area of the islands'),
 ('colonial-administration', r'branch bureaus of the south seas office'),
 ('public-budgets', r'south seas office.*expenditure|revenue.*south seas office|finance.*revenue and expenditure|^revenue and expenditure$'),
 ('industrial-output', r'principal goods manufactured'),
 ('sports-records', r'athletic meeting.*placings'),
 ('physical-geography', r'peaks of the japanese alps|sedimentary formation'),
 ('sports-organisations-and-facilities', r'golf links|horserace clubs'),
 ('iron-and-steel', r'iron refinery'),
 ('chemicals', r'by[- ]product production'),
 ('arable-land', r'percentages for areas of cultivation'),
 ('soybeans', r'yellow bean|green bean'),
 ('diplomatic-claims', r'settlement of old claims|payment of foreign and other claims'),
 ('newspapers,news-agencies', r'press correspondents|foreign correspondents'),
 ('government-offices', r'officials of the government'),
 ('calendars-and-time', r'year dates|japanese year[- ]names'),
 ('weather', r'^frost$'),
 ('earthquakes-and-volcanoes', r'seismographic record'),
 ('marriage-and-divorce', r'married and unmarried'),
 ('imperial-household', r'imperial hereditary estates|list of emperors'),
 ('veterans-and-military-families', r'invalid allowance'),
 ('elections-and-parties', r'number of peers|relative strength of parties'),
 ('navy', r'standing fleets'),
 ('air-force', r'air regiments'),
 ('higher-education', r'number of degree holders'),
 ('education-finance', r'educational fund'),
 ('vocational-education', r'young men.s training institutes'),
 ('diseases', r'percentage of number of cured and dead'),
 ('arts-and-music', r'painters of note'),
 ('water-and-sewerage', r'water[- ]supply'),
 ('disaster-losses,flood-control', r'coast protection'),
 ('aviation', r'aerial routes'),
 ('trade-unions', r'may day demonstrations'),
 ('wages', r'wage indices'),
 ('household-budgets', r'details of actual income|details of outgoes'),
 ('poor-relief', r'disbursements for relief'),
 ('welfare-institutions', r'social welfare work expenditure'),
 ('railways', r'passenger and freight receipts|capital invested and percentage of profits|mileage of lines worked|main lines and mileage|passenger earnings|passengers carried|goods earnings|goods hauled|working revenues|working expenses|disposition of net earnings|principal tunnels'),
 ('aviation', r'civil aviators|aerodromes|civilian airplanes'),
 ('freight-and-transport-costs', r'freight on general goods|charterage per ton'),
 ('public-budgets', r'^general account|service and general expenditure|service expenditure|local finance|finance of cities|general accounts for'),
 ('land-tenure', r'scope of farming'),
 ('farm-inputs', r'self[- ]supplied manure'),
 ('land-improvement', r'^farm adjustment$'),
 ('warehousing', r'government godowns'),
 ('cereals', r'area under rye|forecasts of crops'),
 ('industrial-crops', r'some special crops|output of special crops'),
 ('afforestation', r'afforested area'),
 ('forest-management', r'deforestation|finance of state forests'),
 ('fishing', r'coral collection|catches of principal fish'),
 ('fish-and-fish-products', r'aquatic manufactures|isinglass'),
 ('aquaculture', r'culture grounds and catches'),
 ('gold,silver,copper', r'^gold, silver and copper mines$'),
 ('companies', r'results of various mining industries|promotion, extension|capital and profit and loss|industrial profits|conditions of various industries|results of oriental development'),
 ('securities-and-investment', r'amount of capital, invested'),
 ('electricity', r'sub[- ]stations|demand for electric lights'),
 ('machinery', r'output of motors'),
 ('industrial-output', r'hat production|output of buttons'),
 ('chemicals', r'peppermint production'),
 ('business-associations', r'productoin guilds'),
 ('tariffs', r'list of stipulated articles'),
 ('overseas-communities', r'number of foreigners'),
 ('administrative-divisions', r'thirteen provinces and seats'),
 ('colonial-administration', r'names, sites and sphere of jurisdiction of branch bureaus'),
 ('land-area', r'islands by jurisdiction'),
 ('crop-production', r'amount of principal crops|principal farm products'),
 ('public-budgets', r'revenue and expenditure of (?:tokyo|yokohama|kobe)|special account of kyoto'),
 ('public-debt', r'municipal liabilities|liabilities of nagoya'),
 ('water-and-sewerage', r'total length of service pipes|volume of water supplied'),
 ('road-transport', r'results bus service|condition of motor[- ]car service'),
 ('sports-records', r'baseball standing|inter[- ]sectional championship|rugby results|foreign bred \(gallop\)'),
 ('sports-organisations-and-facilities', r'horse race clubs'),
 ('physical-geography', r'^peaks$'),
 ('weather', r'rainy days|direction of winds'),
 ('passports-and-travel-permits', r'visés issued'),
 ('insurance-and-pensions', r'pension to resigned officials'),
 ('government-offices', r'number of officials by rank'),
 ('military-casualties', r'casualties in bandit suppression'),
 ('school-curricula', r'classification and hours of subjects'),
 ('public-debt', r'redemption fund'),
 ('route-distances', r'mileage between|distance from japanese cities'),
 ('electricity', r'^generating capacity$'),
 ('chemicals', r'soap industry|dye[- ]stuff|menthol production'),
 ('charitable-institutions,medical-services', r'persons treated by the red cross'),
 ('nationality-and-ethnicity', r'distribution of the mongol tribes'),
 ('mining-rights-and-concessions', r'mining registration fees'),
 ('national-income-and-wealth', r'japan.s wealth|amount of people.s income'),
 ('imperial-household', r'^imperial estates$'),
 ('public-health', r'infectious disease prevention'),
 ('disaster-losses', r'statistics of waves'),
 ('telephone', r'charge for ship to shore service'),
 ('wages', r'indices of wage payment|fixed and actual earnings'),
 ('labour-productivity', r'productivity of labo'),
 ('household-budgets', r'living expenses|expenditures per family|monthly expenditure of salaried'),
 ('welfare-institutions', r'^social works|economic provisions for masses'),
 ('patents-and-trademarks', r'inventors honored|registration of trade mark'),
 ('railways', r'disposal of net earnings|length of tunnels'),
 ('aviation', r'aviators, navigators|principal daily air service'),
 ('shipping', r'number of mates and engineers'),
 ('public-budgets', r'treasury accounts|finance of towns and villages|distribution of state expenditure|state special account|special account classified|revenue.*expenditure.*local bodies|ordinary account|six premier cities|details of actual revenue and expenditure'),
 ('land-tenure', r'farms classified by area|tenant disputes'),
 ('land-improvement', r'farm adjustment'),
 ('electricity', r'power output classified|power consumption'),
 ('rayon', r'staple fibre production'),
 ('machinery', r'production of bicycles|scientific and medical instruments|optical instruments|value of motors|cranes, elevators|measuring and weighing instruments|various meters'),
 ('tariffs', r'intermediate duties on japanese goods'),
 ('securities-and-investment', r'chosen trust co|value indices of shares|quotation of national bonds|yields of bonds and stocks|capitalization since'),
 ('mineral-production', r'(?:quantity and value|output value.*volume|volume).*principal minerals|output of certain basic minerals'),
 ('settler-migration', r'work of oriental development|self[- ]guarding japanese immigrants|governmental aid per household'),
 ('fishing', r'value of marine catches|kinds of marine catches'),
 ('road-transport', r'results of motor service|results of bus service'),
 ('sports-records', r'inter[- ]sectional amateur championship|^foreign bred$|lap[- ]time|baseball league|davis cup'),
 ('overseas-communities', r'japanese residents at|koreans in manchoukuo'),
 ('customs-revenue', r'revenue from customs houses'),
 ('insurance-and-pensions', r'grand to officials|government mutual aid'),
 ('wages', r'order.*salary of officials'),
 ('censorship', r'suppression of publication'),
 ('banditry', r'bandit activities|size of bandit groups'),
 ('vocational-education', r'graduates of daido gakuin'),
 ('postal-remittances', r'p\.o\. money order'),
 ('railways', r'^projected lines$'),
 ('inland-navigation', r'river voyage schedule'),
 ('migration', r'farming immigrants|movement of chinese labo|outgoing coolies'),
 ('warehousing,food-supply-and-rationing', r'statistics on granaries'),
 ('markets-and-exchanges', r'forward transactions|details of private exchange|sales.*exchange'),
 ('forest-management', r'forestry offices'),
 ('mineral-production', r'limestone production'),
 ('petroleum', r'operating condition of oil shale'),
 ('fertilisers', r'sulphate of ammonium'),
 ('soybeans', r'output of bean[- ]cake'),
 ('silk,exports', r'exports.*wild silk'),
 ('iron-and-steel', r'production of metal industry'),
 ('gas,chemicals', r'distribution of by[- ]products.*gas co'),
 ('employment-and-unemployment', r'coolies at dairen piers|indices of number of labo|number of labo|indices of the number of labo'),
 ('working-conditions', r'labou?r hours and days'),
 ('companies', r'newly established special.*ordinary concerns'),
 ('military-casualties', r'chinese corpses recovered'),
 ('arms-and-arsenals', r'arms seized'),
 ('arts-and-music', r'imperial board of art'),
 ('nutrition', r'meat consumption'),
 ('aquaculture', r'culture grounds and crops'),
 ('fish-and-fish-products', r'production of fish oil'),
 ('food-processing', r'production of animal fat'),
 ('economic-indicators', r'production in japan proper'),
 ('warehousing', r'goods in godowns'),
 ('rivers-and-waterways', r'principal river systems'),
 ('crop-production', r'crop yield of the first settlement|volume of principal crops'),
 ('public-budgets', r'annual revenue.*expenditure|summary of revenue.*expenditure|revenue and expenditure in detail'),
 ('land-tenure', r'farmers.*acreage'),
 ('forest-area', r'volume of trees'),
 ('mineral-production', r'silica production|output of principal minerals|output.*principal minerals'),
 ('overseas-communities', r'expatriated japanese|no\. of foreigners'),
 ('wages', r'allowance to officials|scale of salary'),
 ('industrial-crops', r'industrial crops'),
 ('constitutions-and-laws', r'principal laws promulgated'),
 ('army', r'district defense force'),
 ('banditry', r'results of bandit suppression'),
 ('religious-institutions,religious-affiliation', r'statistic of religious groups'),
 ('customs-revenue', r'revenue from customs|revenue of leading maritime customs'),
 ('road-transport', r'condition of motor bus transportation'),
 ('inland-navigation', r'navigation bureau|regular river voyage|duration of navigation|navigable sections|navigable length|movement of cargo on the sungari'),
 ('route-distances', r'mileage of routes between'),
 ('fishing', r'marine catches|aquatic catches'),
 ('fish-and-fish-products', r'marine manufactures'),
 ('mineral-reserves', r'alumina shale reserves|magnesite (?:reserves|regions)|oil shale reserves'),
 ('fertilisers', r'sulphate of ammonia'),
 ('soybeans', r'bean[- ]cake mills'),
 ('electricity', r'power generation'),
 ('treaties', r'manchoukuo[- ]german trade (?:agreement|accounts)'),
 ('migration', r'chinese labo(?:u)?rers entering|chinese, including labo'),
 ('economic-controls', r'industries under new law|kinds of enterprise designated'),
 ('economic-planning', r'5[- ]year industrial plans'),
 ('intra-imperial-trade,exports', r'supplies to japan from manchoukuo'),
 ('companies', r'financial condition|balance sheet of manchuria industrial development|capitalization of cos\.|^disposition of profit'),
 ('land-area', r'area of manchoukuo'),
 ('weather', r'vertical radiant heat'),
 ('nationality-and-ethnicity', r'classified by races'),
 ('government-offices', r'no\. of civil officials|organi[sz]ation law of the monopoly bureau'),
 ('administrative-divisions', r'list of provinces, cities|provinces and seats of government'),
 ('vocational-education', r'military educational organs'),
 ('settler-migration', r'per household government subsidy|number of chosenese settlers'),
 ('physical-geography', r'analysis of soil'),
 ('rivers-and-waterways', r'length of important rivers|water expanse of leading lakes'),
 ('silk,exports', r'export.*wild silk'),
 ('radio', r'broadcast programme schedules'),
 ('higher-education', r'higher educational organs'),
 ('leather-and-furs,exports', r'fur supplying and exporting districts'),
 ('elections-and-parties', r'concordia association'),
 ('patents-and-trademarks', r'application and registration of patent'),
 ('construction', r'contracts for civil engineering'),
 ('addiction-treatment', r'number of addicts cared for'),
 ('ceramics-and-glass', r'production of glass'),
 ('gas,chemicals', r'by[- ]products by south manchuria gas'),
 ('foreign-trade', r'commerce by principal customs districts'),
 ('securities-and-investment', r'capitalization, etc\. of special'),
 ('companies', r'position of konzerns|shares owned by konzerns|financing resources of entire japan'),
 ('military-casualties', r'casualties in the sino[- ]japanese hostilities'),
 ('economic-indicators', r'total production in karafuto'),
 ('colonial-administration', r'names, sites and sphere of jurisdiction of branch burea'),
]

# Fallbacks require both a subject already established by the complete-content
# high-level review and explicit body/description evidence for the finer label.
# They never classify a commodity from a stray mention in a general account.
BODY_RULES = [
 ('trade', 'foreign-trade', r'(?s)\A(?=.*\bimports?\b)(?=.*\bexports?\b)'),
 ('trade', 'imports', r'\bimport(?:ed|s|ation)?\b'),
 ('trade', 'exports', r'\bexport(?:ed|s|ation)?\b'),
 ('transportation', 'freight-and-transport-costs', r'\b(?:fare|fares|freight rates|freight charges)\b'),
 ('transportation', 'trams', r'\b(?:tramway|tramcars?|street cars?|street railways?)\b'),
 ('transportation', 'railways', r'\b(?:railway|railroad|locomotive|rolling stock|train mileage|passenger coaches)\b'),
 ('transportation', 'aviation', r'\b(?:aircraft|aeroplane|air service|air route)\b'),
 ('transportation', 'road-transport', r'\b(?:motor cars?|automobiles?|rickshaws|motor buses|motor vehicles|motor trucks)\b'),
 ('transportation', 'inland-navigation', r'\b(?:river steamers?|river navigation|river lines)\b'),
 ('transportation', 'shipping', r'\b(?:steamers?|steamships?|vessels|ships|gross tonnage|sailing)\b'),
 ('transportation', 'navigation-aids', r'\b(?:buoys?|beacons?|lighthouses?)\b'),
 ('transportation', 'route-distances', r'\b(?:distances|kilometres|kilometers)\b'),
 ('finance', 'insurance-and-pensions', r'polic(?:ies|y)|sum insured|sum assured|premiums|annuities|assurance'),
 ('finance', 'public-budgets', r'ordinary revenue|extraordinary revenue|ordinary expenditure|general account|reserve funds|national revenue|government expenditure'),
 ('finance', 'mutual-credit', r'mutual loan|mutual credit|\bmujin\b|bidding.*beneficiar'),
 ('finance', 'banking', r'clearing house|bank clearing|banks? (?:and|by|in|of)|banking'),
 ('finance', 'savings-and-loans', r'\bdeposits\b|savings|loans advanced|loans outstanding'),
 ('finance', 'securities-and-investment', r'stock exchange|securities|shares|trust business|investment trusts'),
 ('finance', 'currency', r'notes issued|note issue|note circulation|banknotes|silver coin|gold coin'),
 ('finance', 'public-debt', r'national debt|government bonds|public debt|debt redemption'),
 ('population', 'births-and-deaths', r'births|deaths|stillbirth|birth[- ]rate|death[- ]rate'),
 ('population', 'migration', r'emigrants?|immigrants?|emigration|immigration|entering.*leaving'),
 ('population', 'population-totals', r'population|inhabitants|residents'),
 ('agriculture', 'sericulture', r'silkworm|cocoon|mulberry|crop per.*card'),
 ('agriculture', 'livestock', r'cattle|horses|sheep|swine|pigs|goats|live[- ]?stock'),
 ('agriculture', 'crop-production', r'soya beans|kaoliang|millet|crop|harvest'),
 ('agriculture', 'arable-land', r'under tillage|cultivated area|cultivable land|arable|cultivation'),
 ('forestry', 'afforestation', r'trees planted|reforest|planting|afforest'),
 ('forestry', 'forest-area', r'forest area|area of forest|standing trees|standing timber'),
 ('forestry', 'timber', r'\btimber\b|lumber|sawn wood'),
 ('forestry', 'fuelwood-and-charcoal', r'fuelwood|firewood|charcoal|fagots'),
 ('fisheries', 'aquaculture', r'pearl culture|fish culture|aquaculture|aquiculture'),
 ('fisheries', 'fishing', r'catches|fish caught|fishing|fishery|fishery production'),
 ('mining', 'mineral-reserves', r'ore reserves|mineral deposits|estimated.*deposits'),
 ('mining', 'mining-rights-and-concessions', r'mining lots|mining rights|prospecting'),
 ('mining', 'mineral-production', r'output|production|quantity.*value|value.*quantity'),
 ('manufacturing', 'silk', r'filature|reeling|tussah|tusser'),
 ('manufacturing', 'textiles', r'yarn|weaving|spinning|textile|cloth|thread'),
 ('manufacturing', 'food-processing', r'flour|confectionery|miso|soy sauce'),
 ('manufacturing', 'industrial-output', r'output|production|factories|manufactured|manufacturing|industrial|number of workers'),
 ('sport', 'sports-records', r'\brecords?\b|\bchampion|\bholders?\b|winners?|\btime\b|\bmetres?\b|\bfeet\b|\bpoints\b|\bsecs?\b'),
 ('education', 'schools-and-pupils', r'schools|students|pupils|enrol|enroll'),
 ('health', 'medical-services', r'hospitals?|patients|physicians|dentists|midwives|nurses'),
 ('health', 'public-health', r'sanitation|sanitary|rubbish|cremation|burials|disinfect'),
 ('geography', 'weather', r'temperature|rainfall|humidity|pressure|wind|sunshine'),
 ('geography', 'physical-geography', r'latitude|longitude|altitude|geology|strata|mountains|spring'),
 ('geography', 'land-area', r'area.*(?:sq\.|square)|area.*kilomet'),
 ('communications', 'telegraph', r'telegrams|telegraph|cablegrams|cable rates'),
 ('communications', 'telephone', r'telephone'),
 ('communications', 'postal-services', r'mail|post office|letters|parcels'),
 ('government', 'government-offices', r'ministers|cabinet|officials|offices|departments|civil service'),
 ('government', 'local-government', r'prefectural assembl|municipal council|village heads|ward heads'),
 ('government', 'elections-and-parties', r'election|electors|political parties|house of representatives'),
 ('labour', 'wages', r'wages|salaries|pay per|remuneration'),
 ('labour', 'employment-and-unemployment', r'workers|workmen|employees|unemployment|labourers'),
 ('military', 'navy', r'warships|battleships|cruisers|destroyers|submarines|fleet'),
 ('military', 'army', r'infantry|cavalry|artillery|regiments|battalions|divisions'),
 ('crime-and-justice', 'courts', r'court|bailiff|notarial|procurator|prosecutor'),
 ('religion', 'buddhism', r'buddhis|tendai|shingon|nichiren|rinzai'),
 ('religion', 'religious-affiliation', r'adherents|believers|followers'),
 ('utilities', 'electricity', r'electric|kilowatts|kwh|candlepower'),
 ('utilities', 'water-and-sewerage', r'water supply|waterworks|sewerage|reservoir'),
 ('culture', 'arts-and-music', r'paintings|sculpture|art exhibition|fine arts|works submitted'),
]


def classify(record):
    title, body, description, context, notes = material(record)
    t = record['table']
    result = {'tags': [], 'rule': 'unresolved', 'reason': 'No confident controlled detailed subject established.',
              'rows_processed': sum(len(p.get('rows', [])) for p in t.get('parts', [])),
              'cells_processed': sum(len(row) for p in t.get('parts', []) for row in p.get('rows', [])),
              'body_sha256': hashlib.sha256(body.encode()).hexdigest()}
    for tag, expression in TITLE_RULES:
        match = re.search(expression, title)
        if match:
            result.update(tags=tag.split(','), rule=tag, reason='The table subject and complete body support '+tag+'.',
                          subject_evidence=match.group(0))
            break
    if not result['tags']:
        eligible = set(record['previous']['topics'])
        evidence = body + ' | ' + description
        for topic, tag, expression in BODY_RULES:
            match = re.search(expression, evidence)
            if topic in eligible and match:
                result.update(tags=[tag],rule='body-'+tag,reason='Complete body and the stated measure support '+tag+'.',body_evidence=match.group(0))
                break
    return result


def build(verbose=True):
    records = frozen_records()
    decisions = {r['key']: classify(r) for r in records}
    manual = OUT / 'manual-groups.json'
    if manual.exists():
        used = set()
        for group in b.read(manual):
            for i in group['indices']:
                assert i not in used, i
                used.add(i)
                decisions[records[i]['key']].update({k:group[k] for k in ('tags','topics','flags') if k in group},rule='explicit-complete-record-decision',reason=group['reason'])
    b.write(OUT / 'decisions.json', {'count': len(decisions), 'tables': decisions})
    if verbose:
        print(json.dumps({'reviewed':len(decisions),'assigned':sum(bool(d['tags']) for d in decisions.values()),
                          'unresolved':sum(not d['tags'] for d in decisions.values())},ensure_ascii=False))
    return records,decisions


def finalize():
    records,decisions=build(False)
    manifest=b.read(OUT/'manifest.json')
    assert len(records)==len(decisions)==manifest['count']==2073
    assert [r['key'] for r in records]==manifest['keys']
    assert all(b.sha(b.SITE/p)==h for p,h in manifest['source_files'].items())
    cohort_path=HERE/'reviews/deferred-detailed-tags-2026-10-26.json'
    assert b.sha(cohort_path)==manifest['cohort_sha256']
    assert b.sha(b.PUBLISHED/'assignments.json')==manifest['baseline_assignments_sha256']
    assert b.sha(HERE/'vocabulary.json')==manifest['vocabulary_sha256']
    vocabulary=b.read(HERE/'vocabulary.json')
    allowed={field:{e['id'] for e in vocabulary[field]} for field in ('topics','tags','flags')}
    assert all(set(tags.split(','))<=allowed['tags'] for tags,_ in TITLE_RULES)
    assert all(tag in allowed['tags'] for _,tag,_ in BODY_RULES)
    before=b.load_assignments()
    last_audit=OUT/'reviewed-decisions.json'
    last_results={r['key']:r['result'] for r in b.read(last_audit)['tables']} if last_audit.exists() else {}
    assert digest({k:v for k,v in before.items() if k not in decisions})==manifest['unaffected_assignments_sha256']
    canonical=b.read(b.PUBLISHED/'assignments.json')['assignments']
    published=b.read(b.PUBLISHED/'overrides.json')
    overrides=published['assignments']
    audit=[]; unresolved=[]; totals=Counter(); by_book={}
    expected={k:dict(v) for k,v in before.items()}
    for i,record in enumerate(records):
        key=record['key'];d=decisions[key];old=record['previous'];t=record['table']
        assert not old['tags']
        changes={'tags':d['tags'],'stage':'contents-reviewed-detailed'}
        for field in ('topics','flags'):
            if field in d:changes[field]=d[field]
        if 'flags' in d:changes['flag_status']='reviewed-text' if d['flags'] else 'reviewed-statistical'
        new=old|changes
        # A repeat invocation is allowed, but another session's decision is not
        # silently overwritten, either within or outside this frozen cohort.
        assert before[key] in (old,new,last_results.get(key)),key
        for field,maximum in (('topics',2),('tags',3),('flags',1)):
            assert len(new[field])==len(set(new[field]))<=maximum
            assert set(new[field])<=allowed[field],(key,field,new[field])
        assert d['rows_processed']==sum(len(p.get('rows',[])) for p in t.get('parts',[]))
        assert d['cells_processed']==sum(len(row) for p in t.get('parts',[]) for row in p.get('rows',[]))
        overrides[key]=overrides.get(key,{})|changes
        expected[key]=new
        headers=list(dict.fromkeys(str(x) for p in t.get('parts',[]) for x in p.get('columns',[])))
        labels=list(dict.fromkeys(str(row[0]) for p in t.get('parts',[]) for row in p.get('rows',[]) if row and row[0]))
        entry={'key':key,'review_index':i,'book':record['book'],'title':(t.get('en') or {}).get('t') or t.get('title'),
               'previous':old,'result':new,'decision':d,'body_headers':headers,'row_label_examples':labels[:16]}
        audit.append(entry)
        if not d['tags']:unresolved.append(entry)
        totals['reviewed']+=1;totals['new_detailed_assignments']+=bool(d['tags'])
        totals['still_without_details']+=not bool(d['tags'])
        totals['high_level_corrections']+=new['topics']!=old['topics']
        totals['new_text_flags']+=new['flags']!=old['flags']
        slug=record['book']['slug']
        if slug not in by_book:by_book[slug]={'book':record['book'],'reviewed':0,'assigned':0,'unresolved':0}
        by_book[slug]['reviewed']+=1;by_book[slug]['assigned']+=bool(d['tags']);by_book[slug]['unresolved']+=not bool(d['tags'])
    reviews=list(dict.fromkeys([*published.get('reviews',[]),*([published['review']] if published.get('review') else []),'../reviews/manchuria-south-seas-detailed-2026-10-27/REPORT.md']))
    b.write(OUT/'reviewed-decisions.json',{'count':2073,'method':'assistant-authored-complete-transcription-rules-and-explicit-record-decisions','tables':audit})
    b.write(OUT/'unresolved.json',{'count':len(unresolved),'tables':unresolved})
    b.write(b.PUBLISHED/'overrides.json',{'schema_version':1,'scope':'approved-topics-details-and-explicit-text-flag-reviews','reviews':reviews,'assignments':overrides})
    after=b.load_assignments()
    assert after==expected
    assert set(after)==set(before)==set(canonical)
    assert all(after[k]==v for k,v in before.items() if k not in decisions)
    assert all(not after[r['key']]['tags'] for r in records if not decisions[r['key']]['tags'])
    assert b.sha(cohort_path)==manifest['cohort_sha256']
    original_cohort=b.read(cohort_path)
    assert original_cohort['count']==len(original_cohort['tables'])==7662
    remaining=[{'key':r['key'],'book':r['book'],'title':r['metadata'].get('title_en') or r['metadata']['title'],
                'current_topics':after[r['key']]['topics'],'review_status':'reviewed-no-confident-detail' if r['key'] in decisions else 'awaiting-contents-review'}
               for r in original_cohort['tables'] if not after[r['key']]['tags']]
    b.write(OUT/'remaining-deferred-details.json',{'original_cohort':7662,'count':len(remaining),'collections':dict(Counter(r['book']['collection'] for r in remaining)),'tables':remaining})
    checks={'exact_2073_coverage':True,'vocabulary_and_limits_valid':True,'complete_body_rows_and_cells_processed':True,
            'original_transcriptions_unchanged':True,'outside_cohort_assignments_unchanged':True,
            'previous_detailed_assignments_preserved':True,'original_7662_list_unchanged':True,
            'only_explicit_high_level_and_text_corrections':True}
    validation={'status':'complete',**dict(totals),'collection_summary':{collection:{'reviewed':sum(x['reviewed'] for x in by_book.values() if x['book']['collection']==collection),'assigned':sum(x['assigned'] for x in by_book.values() if x['book']['collection']==collection),'unresolved':sum(x['unresolved'] for x in by_book.values() if x['book']['collection']==collection)} for collection in ('manchuria','south-seas')},
                'remaining_original_cohort':len(remaining),'checks':checks,'issues':[],
                'validated_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':b.sha(OUT/'manifest.json'),
                'manual_groups_sha256':b.sha(OUT/'manual-groups.json'),'overrides_sha256':b.sha(b.PUBLISHED/'overrides.json')}
    b.write(OUT/'validation.json',validation)
    lines=['# Manchuria and South Seas detailed-tag review','',
           'Reviewed the **1,999 Manchuria and 74 South Seas tables** from the fixed 7,662-table deferred cohort using their existing complete transcriptions. No external LLM calls, OCR, new vocabulary terms or transcription changes were made.','',
           f"Saved **{totals['new_detailed_assignments']:,} new detailed assignments**; **{totals['still_without_details']}** remain blank. Corrected **{totals['high_level_corrections']}** high-level mismatches explicitly established by the contents and added **{totals['new_text_flags']}** explicit text-table flags. Other existing high-level topics and flag assessments are preserved.",'',
           '## Method','',
           'Local, assistant-authored rules process all part labels, columns and every row/cell, with the supplied descriptions, context and notes available to the review. Repeated subject families use central rules. Ambiguous records, broad aggregate tables, apparent cross-subject matches and reference/list tables received explicit record decisions. This is a rule-assisted subject classification, not a rereading of every printed digit or a new transcription.','',
           'The decisions distinguish actual table functions from incidental entries: court deposits are not bank savings; service prices are not transport fares; plant capital is not a count of textile output; multiple religions are not labelled as Buddhism alone; street-tram evidence is kept distinct from railway traction. Numbers that are dates, office/unit identifiers or article numbers alone do not make a reference list statistical. Uncertain subjects and vocabulary gaps remain blank.','',
           '## Saved records','',
           '- [Decisions, previous labels and body evidence](reviewed-decisions.json)',
           '- [Explicit record decisions](manual-groups.json)',
           '- [Unresolved detailed subjects](unresolved.json)',
           '- [Validation](validation.json)',
           '- [Current remainder of the original cohort](remaining-deferred-details.json)',
           '- [Unchanged original 7,662-table list](../deferred-detailed-tags-2026-10-26.json)','',
           f"The original list is retained unchanged. Its current remainder is **{len(remaining):,} tables**: 5,589 in Japan and {totals['still_without_details']} reviewed Manchuria records. All 74 South Seas records now have detailed tags.",'',
           '## By volume','', '| Volume | Reviewed | Assigned | Still blank |','| --- | ---: | ---: | ---: |']
    for x in by_book.values():lines.append(f"| {x['book']['title']} | {x['reviewed']} | {x['assigned']} | {x['unresolved']} |")
    lines+=['','## Remaining questions','','| Key | Title | Reason |','| --- | --- | --- |']
    for r in unresolved:lines.append(f"| `{r['key']}` | {str(r['title']).replace('|','/')} | {r['decision']['reason'].replace('|','/')} |")
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in validation.items() if k not in ('checks',)},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['build','finalize'])
    args = parser.parse_args(); {'build':build,'finalize':finalize}[args.action]()
