// Kanji numerals to Arabic, for DISPLAY only: the transcribed data stays as printed.
// KN(s,full): full=false converts positional numbers (五〇〇, 二二匁, 第一三類, 町三六ノ二) that are clearly numbers;
// full=true also converts single digits and 十百千 numbers before a unit of measure (五寸五分, 七匁, 百匁當).
// A number is left alone when in doubt: names (持地六三郎, 富永一二, 三五公司), size names (二二幅物 = 2.2 widths), words
// (二重, 一越縮緬, 五分利), grades and ranks (一級, 九等, 二番狸毫) and lists (二、三四、五年). No lookbehind: older Safari cannot parse it, and it would break the page.
const KN=(function(){
const DV={"〇":0,"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9};
const D="〇零一二三四五六七八九",DM=D+"十百千";
const isK=c=>!!c&&/[㐀-鿿〇]/.test(c),isDig=c=>!!c&&DM.includes(c);
const pos=s=>[...s].map(c=>DV[c]).join("");
const trad=s=>{let n=0,c=0;for(const x of s){if(x in DV)c=DV[x];else{n+=(c||1)*({"十":10,"百":100,"千":1000}[x]);c=0}}return String(n+c)};
const val=s=>/[十百千]/.test(s)?trad(s):pos(s);
// units, each with what must not follow it (三本絹, 文具, 合計, 二分の一 …)
const UNIT="(?:類|回|條|號|番|年|月|日|週|時間|時|秒|米|粁|里|町|丁(?![目刃杼も])|間|尺|寸(?!豆)|厘|毛|匁|貫|斤|瓦|瓩|噸|糎|粍|吋|呎|碼|勺|升|斗|石|坪|枚|箇|個|打|組|足|色|歳|歲|圓|錢|銭|%|％|切|立|羽|函|封|段|張|俵|袋|校|度|種|歩|丈|割|揃|戸|グロス|ダース|ボンド|本(?![絹織邦町人店部社縮])|文(?![具房庫書字])|合(?![計資名同])|分(?![の利オ])|線|オンス|名(?![古前稱義簿])|人(?![絹參造]))";
const POSUNIT=new RegExp("^"+UNIT);
const NAMEAFTER=/^(?:郎|公司|商|會|社|幅|越|重|德|瓶|ツ)/;
const PREFIX="第町里洞目番地號ノ長高巾徑丈全約各";
const GROUP=new RegExp("["+D+"]{1,3}(?:、["+D+"]{3})+(?!["+D+"])","g");
const DEC=new RegExp("["+D+"]+・["+D+"]+(?!["+D+"])","g");
const ADDR=new RegExp("(["+D+"]+丁目)?(["+D+"]+(?:ノ["+D+"]+)*)","g");
const RUN=new RegExp("["+DM+"]+","g");
const decOk=a=>a===""||POSUNIT.test(a)||/^[—–－～ /、)）]/.test(a);
function conv(s,full){
 if(typeof s!=="string"||!RUN.test(s)){RUN.lastIndex=0;return s}RUN.lastIndex=0;
 let t=s.replace(GROUP,(m,o,str)=>isDig(str[o-1])||(isK(str[o-1])&&!PREFIX.includes(str[o-1]))||!/^(?:$|[本番人千圓羽\s)）])/.test(str.slice(o+m.length))?m:m.split("、").map(pos).join(","));
 t=t.replace(DEC,(m,o,str)=>{if(isDig(str[o-1])||!decOk(str.slice(o+m.length)))return m;const[a,b]=m.split("・");if(b.length>=3&&/^[番本]/.test(str.slice(o+m.length)))return pos(a)+","+pos(b); /* 二・〇〇〇番: a printed dot used as a thousands mark */return pos(a)+"."+pos(b)});
 t=t.replace(ADDR,(m,c,chain,o,str)=>{const b=str[o-1];if(isDig(b)||!((c||(b&&"町里洞目地通 ".includes(b)))&&(chain.includes("ノ")||c)))return m;
  return (c?pos(c.slice(0,-2))+"丁目":"")+chain.split("ノ").map(pos).join("ノ")});
 t=t.replace(new RegExp("第(["+D+"]+)(?=類)","g"),(m,d)=>"第"+pos(d));
 t=t.replace(new RegExp("號の(["+D+"])(?:及(["+D+"]))?","g"),(m,x,y)=>"號の"+pos(x)+(y?"及"+pos(y):""));
 return t.replace(RUN,(m,o,str)=>{const b=str[o-1]||"",a=str.slice(o+m.length),isTrad=/[十百千]/.test(m);
  if(NAMEAFTER.test(a))return m;
  if(/^[〇零]+$/.test(m))return m;                       // 〇 alone is a mark or a blank, not zero
  const unit=POSUNIT.test(a);
  if((b==="・"&&isDig(str[o-2]))||(a[0]==="・"&&isDig(a[1])))return m;     // 九・一八事變: a decimal point was refused above
  if(m[0]==="〇"||m[0]==="零")return m;                  // (〇五四%): the point is not printed; do not guess
  if(/^["一二三四五六七八九〇零十百千"]+\s/.test(str)&&o===0&&/^\s/.test(a))return m;   // "一〇 雜品": a list number, as its neighbours 九 etc.
  if(m.length===1&&/^[—–－～][〇零一二三四五六七八九]{2,}/.test(a))return pos(m);  // 七—一四日
  if((isTrad||m.length===1)&&/^番(?!線)/.test(a))return m;   // 二番狸毫, 五番目: a rank, stays in kanji like 一級 and 九等
  if(isTrad||m.length===1)return full&&(unit||/^[—–－～][0-9〇零一二三四五六七八九十百千]/.test(a))&&!/^[十百千]{2,}/.test(m)?val(m):m;
  if((b==="、"&&isDig(str[o-2]))||(a[0]==="、"&&isDig(a[1])))return m; // 二、三四、五年
  if(a[0]==="迄"||/^[%％][一二三四五六七八九]/.test(a))return m;           // 一九%五 is 19.5%
  if(unit)return pos(m);
  if(/^[—–－～](?:明治|大正|昭和)?[〇零一二三四五六七八九]/.test(a))return pos(m); // 大正一〇—大正一四年
  if(isK(a[0]))return m;                                 // 五四結庄, 三五公司: a number inside a name
  if(b===" "||b==="　")return isK(str[o-2])?m:pos(m);     // 富永 一二 is a name
  if(isK(b)&&!PREFIX.includes(b))return m;               // 富永一二, 四割三二
  return pos(m)})}
// full="cells" (クーポン旅館一覧): listings whose figure columns hold bare numbers. A cell that is a number and nothing
// else converts whatever its length (telephone 三 → 3), and 、 between yen and its sen is a decimal point
// (二、五〇 → 2.50, 和六、〇〇 → 和6.00); the rest of the text gets the cautious rules, so 三本木町 stays a name.
const YEN=new RegExp("(["+D+"]+)、(["+D+"]{1,2})(?!["+D+"])","g"),WHOLE=new RegExp("^["+D+"]+$");
function cells(s){
 if(typeof s!=="string")return s;const w=s.trim();
 if(WHOLE.test(w)&&!/^[〇零]+$/.test(w))return pos(w);
 return conv(s.replace(YEN,(m,a,b,o,str)=>isDig(str[o-1])?m:pos(a)+"."+pos(b)),false)}
return (s,full)=>full==="cells"?cells(s):conv(s,full)})();
if(typeof module!=="undefined")module.exports=KN;
