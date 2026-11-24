import json
A='korea-tokanfu-1919/';B='korea-tokanfu-1939/'
def fam(l,a,b,note=""):
    return {"label":l,"members":[A+x for x in a]+[B+x for x in b],"note":note}
S={
"shrines-and-education":[
 fam("Shrines (and temples)",["p0261_1"],["p0160_1"],"1919 table also covers Buddhist temples; 1939 shrines only"),
 fam("Japanese school-age children",["p0242_2"],["p0160_2"]),
 fam("Japanese elementary schools: status",["p0243_1"],["p0161_1"]),
 fam("Japanese elementary schools: pupil movements",["p0244_1","p0245_1"],["p0161_2"],"1919 splits entrants/graduates and withdrawals/deaths"),
 fam("Japanese elementary schools: attendance",["p0245_2"],["p0162_1"]),
 fam("Japanese elementary schools: assets",["p0246_2"],["p0162_2"]),
 fam("Japanese elementary schools: teachers' qualifications and pay",["p0247_1"],["p0163_1"]),
 fam("Korean elementary schools: status",["p0250_3"],["p0163_2"],"Korean-pupil schools; 普通學校 in 1919, 小學校 (二部) in 1939"),
 fam("Korean elementary schools: pupil movements",["p0251_1","p0251_2"],["p0164_1"],"1919 splits entrants/graduates and withdrawals/deaths"),
 fam("Korean elementary schools: attendance",["p0252_1"],["p0164_2"]),
 fam("Korean elementary schools: teachers' qualifications and pay",["p0252_3"],["p0165_1"]),
 fam("Korean elementary schools: assets",["p0252_2"],["p0166_1"]),
 fam("Middle schools: status",["p0247_2"],["p0167_1","p0168_1"],"1939 splits public and private"),
 fam("Middle schools: assets",["p0247_3"],["p0167_2"]),
 fam("Girls' high schools: status",["p0248_1"],["p0168_2","p0169_1"],"1939 splits public and private"),
 fam("Girls' high schools: assets",["p0248_2"],["p0168_3"]),
 fam("Vocational schools: status",["p0256_2"],["p0169_2","p0170_1","p0171_1"],"1939 splits government, public, private"),
 fam("Vocational schools: assets",["p0256_3"],["p0169_3","p0170_2"]),
 fam("Private miscellaneous schools by province",["p0259_1"],["p0174_5"]),
 fam("Village schools (sodang)",["p0259_2"],["p0175_2"]),
 fam("Libraries",["p0260_1"],["p0175_3"]),
]}
R=[
 fam("Buddhist temples and Korean temples/monks",["p0261_2"],["p0177_2"]),
 fam("Churches, mission stations and lecture halls",["p0262_1"],["p0177_3"]),
 fam("Religious propagators",["p0262_2"],["p0178_1"],"1939 also gives believers"),
 fam("Relief institutions / social work facilities",["p0268_3"],["p0179_1"]),
 fam("Imperial relief grants",["p0267_3"],["p0179_2"]),
 fam("Poor relief",["p0268_2"],["p0179_3"]),
 fam("Disaster relief",["p0268_1"],["p0179_4"]),
 fam("Relief of sick and dead travellers",["p0264_2"],["p0180_1"]),
 fam("Relief Institute staff",["p0263_1"],["p0182_1"]),
 fam("Relief Institute nursery pupils",["p0263_2"],["p0182_2"]),
 fam("Red Cross members",["p0267_1"],["p0183_3"]),
 fam("Patriotic Women's Association members",["p0267_2"],["p0183_4"]),
]
P=[
 fam("Health facilities",["p0201_1"],["p0196_1"]),
 fam("Infectious disease cases and deaths",["p0202_1"],["p0196_2"]),
 fam("Infectious disease fatality rates",["p0204_1"],["p0200_1"]),
 fam("Infectious disease by age and disease",["p0207_1"],["p0199_1"]),
 fam("Vaccination",["p0209_2","p0211_1"],["p0201_1"],"1919 splits by year/province and by age"),
 fam("Government hospital staff and expenses",["p0211_2","p0215_1"],["p0203_1"],"1919 separates Government-General and provincial charity hospitals"),
 fam("Hospital patients",["p0212_1"],["p0204_1"]),
 fam("Provincial hospital itinerant clinics",["p0215_2"],["p0205_1"]),
 fam("Quarantine of vessels",["p0216_1"],["p0205_2"]),
]
Q=[
 fam("Police offices and staff",["p0191_2"],["p0185_1"]),
 fam("Summary-judgment criminal cases",["p0191_3"],["p0187_1"]),
 fam("Summary judgments: persons sentenced",["p0192_1"],["p0188_1"]),
 fam("Theft and fraud victims",["p0194_1"],["p0188_2"]),
 fam("Theft and fraud arrests",["p0194_2"],["p0188_3"]),
 fam("Fires",["p0195_1"],["p0189_2"]),
 fam("Unnatural deaths",["p0196_1"],["p0190_1"]),
 fam("Suicides by age and cause",["p0196_2"],["p0190_2"]),
 fam("Abandoned children",["p0197_1"],["p0192_1"]),
 fam("Police rescue and relief",["p0198_1"],["p0189_4"]),
 fam("Privately owned firearms",["p0199_1"],["p0192_2"]),
 fam("Businesses under police supervision",["p0200_1"],["p0192_3"]),
]
S["religion-and-social-work"]=R;S["public-health"]=P;S["police"]=Q
import re
for k,v in S.items():
    ids=set(re.findall(r'^(\S+) \| (\S+) \|',open(f'listings/korea-tokanfu--{k}.txt').read(),re.M))
    ids={a+'/'+b for a,b in ids}
    for f in v:
        for m in f["members"]: assert m in ids,(k,m)
    n=sum(len(f["members"]) for f in v)
    json.dump({"listing":"korea-tokanfu--"+k,"families":v},open(f'families/korea-tokanfu--{k}.json','w'),ensure_ascii=False,indent=1)
    json.load(open(f'families/korea-tokanfu--{k}.json'))
    print(k,len(v),n)
