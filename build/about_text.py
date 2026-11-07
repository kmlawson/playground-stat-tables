"""The author's text for the home page's introduction and for about.html (user, 2026-11-06). Reader-facing text is
the author's: change it only when asked. The reading lists are kept in alphabetical order by author."""

INTRO = """<div class="intro">
<p>Welcome to this collection of old tables from historical sources related to East Asia and the Japanese Empire. A majority of the materials on this website are tables of information that were extracted using large language models from old year books, handbooks, and volumes of statistics available open access online. The website was primarily created for history students likely to be working with English language sources, but over time the balance will shift to other languages given their greater availability and importance as sources.</p>
<p>Two things need to be kept in mind as you browse the tables on this website. First, each table and the volumes they come from must be read critically as historical sources born of a particular moment and authorial context. See the <a href="about.html">about</a> page for some reading suggestions around the use and critique of historical statistics. Secondly, these tables were extracted with the use of large language models. The accuracy of transcription is <a href="about.html#accuracy">high</a> but there are errors. If you intend to cite any of these tables, please consult the original scans, which are linked to under each table.</p>
</div>
"""

ABOUT = """<div class="abouttext">
<h2>About</h2>
<p>This website began in September, 2026 as an experiment which asked the question: how far have large language models come in their ability to accurately extract both text and complex tables of information from historical sources? When it comes to decent scans of sources in English and East Asian texts the answer is, for some models, quite far (see some custom <a href="https://kmlawson.github.io/vision-model-bench/">benchmarks</a>, for example).</p>
<p>After beginning with just a small number of China and Japan year books, I expanded the focus and now include a somewhat arbitrary list of other interesting open access works published before around 1950 which have rich tables of information about East Asia and parts of the Japanese empire. Many of these tables are of very limited use to a historian, and some say more about the creators of these works than they do about the places they describe. Some of these tables, obscure though their information may be, will hopefully lead readers to ask interesting new historical questions, or reconsider old assumptions.</p>
<p>Another goal of this website is to introduce visitors to some of the wonderful array of open access materials available online. The types of sources here all beg for careful critical consideration, but many of them are put to effective use in the historiography of the region.</p>

<h3 id="accuracy">Accuracy</h3>
<p>Only a sample of a few dozen tables have been manually checked by myself by comparing them to the original scans via the links provided. Many of the larger complex sample tables checked here here extracted numbers with 100% accuracy or only one or two errors - something that was certainly not the case in tests I carried out with large language model extraction of tables from sources in 2024 and 2025. Many of the mistakes found were very difficult to read (for a human as well) faded numbers (3 vs 8, for example). As you will notice, many tables mark cells as unreadable when the original scan was of poor quality. The highest error rates came from statistical tables with vertically stacked Chinese/Japanese numbers, especially the numbers one, two, and three (一、二、三) next to each other. These often required Claude Opus 5.5 or Gemini Argon 4 with higher effort rates, as well as cropping and zooming by the model to get very high accuracy rates. Only some books and tables were sent for extraction to these more expensive models. Mistakes do exist, however, and it was important to include the ability to chase tables back to the source scans via links here. In the future, I hope to make the human checking of sample tables more formal and post accuracy percentages here.</p>

<h3 id="finder-pages">Finder pages</h3>
<p>The <a href="figures/index.html">finder pages</a>, beginning with <a href="figures/population.html">Population</a>, gather one kind of figure from every table on the site, place by place and year by year. They are built from the transcriptions alone: for each table that holds such figures, an agent (Sonnet 5.5) wrote down which rows and columns hold them and for which place, date and group, and a script then copied those cells exactly as transcribed. Nothing was re-read from the scans, corrected, averaged or filled in. Where several tables print the same figure it is shown once, with a link to each table; where they disagree, the figures are shown side by side with the gap between them, together with each table's date and basis (census, registered or resident population, estimate) where it gives one. Each figure links to its table with the cell marked. Place names were matched to a gazetteer by machine and dates were taken from the tables, so mistakes in both are possible: check the table, and the original scan linked from it, before relying on a figure.</p>

<h3 id="further-reading">Further Reading</h3>
<p>There is a rich historiography on the history of statistics and especially the role they play in state power and imperialist endeavors. Below is a reading list of works for students to explore on the topic.</p>
<ul class="biblio">
<li>Cohen, Patricia Cline. <i>A Calculating People: The Spread of Numeracy in Early America</i>. Chicago: University of Chicago Press, 1982.</li>
<li>Cohn, Bernard S. "The Census, Social Structure and Objectification in South Asia." In <i>An Anthropologist among the Historians and Other Essays</i>, 224–254. Delhi: Oxford University Press, 1987</li>
<li>Cole, Joshua. <i>The Power of Large Numbers: Population, Politics, and Gender in Nineteenth-Century France</i>. Ithaca: Cornell University Press, 2000.</li>
<li>Desrosières, Alain. <i>The Politics of Large Numbers: A History of Statistical Reasoning</i>. Translated by Camille Naish. Cambridge, MA: Harvard University Press, 1998.</li>
<li>Hacking, Ian. <i>The Taming of Chance</i>. Cambridge: Cambridge University Press, 1990.</li>
<li>Ittmann, Karl, Dennis D. Cordell, and Gregory H. Maddox, eds. <i>The Demographics of Empire: The Colonial Order and the Creation of Knowledge</i>. Athens: Ohio University Press, 2010.</li>
<li>Kalpagam, U. <i>Rule by Numbers: Governmentality in Colonial India</i>. Lanham, MD: Lexington Books, 2014.</li>
<li>Kertzer, David I., and Dominique Arel, eds. <i>Census and Identity: The Politics of Race, Ethnicity, and Language in National Censuses</i>. Cambridge: Cambridge University Press, 2002.</li>
<li>Mitchell, Timothy. <i>Rule of Experts: Egypt, Techno-Politics, Modernity</i>. Berkeley: University of California Press, 2002.</li>
<li>Poovey, Mary. <i>A History of the Modern Fact: Problems of Knowledge in the Sciences of Wealth and Society</i>. Chicago: University of Chicago Press, 1998.</li>
<li>Porter, Theodore M. <i>Trust in Numbers: The Pursuit of Objectivity in Science and Public Life</i>. Princeton: Princeton University Press, 1995.</li>
<li>Scott, James C. <i>Seeing Like a State: How Certain Schemes to Improve the Human Condition Have Failed</i>. New Haven: Yale University Press, 1998</li>
</ul>

<h4 id="east-asia">East Asia</h4>
<ul class="biblio">
<li>Barclay, George W. <i>Colonial Development and Population in Taiwan</i>. Princeton: Princeton University Press, 1954.</li>
<li>Chiang, Yung-chen. <i>Social Engineering and the Social Sciences in China, 1919–1949</i>. Cambridge: Cambridge University Press, 2001.</li>
<li>Ghosh, Arunabh. <i>Making It Count: Statistics and Statecraft in the Early People's Republic of China</i>. Princeton: Princeton University Press, 2020.</li>
<li>Gragert, Edwin H. <i>Landownership under Colonial Rule: Korea's Japanese Experience, 1900–1935</i>. Honolulu: University of Hawai'i Press, 1994.</li>
<li>Hayami, Akira. <i>The Historical Demography of Pre-modern Japan</i>. Tokyo: University of Tokyo Press, 2001.</li>
<li>Hein, Laura. <i>Reasonable Men, Powerful Words: Political Culture and Expertise in Twentieth-Century Japan</i>. Berkeley: University of California Press; Washington, DC: Woodrow Wilson Center Press, 2004.</li>
<li>Ho, Ping-ti. <i>Studies on the Population of China, 1368–1953</i>. Cambridge, MA: Harvard University Press, 1959</li>
<li>Hwang, Kyung Moon. <i>Rationalizing Korea: The Rise of the Modern State, 1894–1945</i>. Oakland: University of California Press, 2016.</li>
<li>Kwon, Tai Hwan. <i>Demography of Korea: Population Change and Its Components, 1925–66</i>. Seoul: Seoul National University Press, 1977.</li>
<li>Lam, Tong. <i>A Passion for Facts: Social Surveys and the Construction of the Chinese Nation-State, 1900–1949</i>. Berkeley: University of California Press, 2011.</li>
<li>Lee, Hong Yung, Yong-Chool Ha, and Clark W. Sorensen, eds. <i>Colonial Rule and Social Change in Korea, 1910–1945</i>. Seattle: University of Washington Press, 2013.</li>
<li>Lyons, Thomas P. <i>China Maritime Customs and China's Trade Statistics, 1859–1948</i>. Trumansburg, NY: Willow Creek Press, 2003.</li>
<li>Mullaney, Thomas S. <i>Coming to Terms with the Nation: Ethnic Classification in Modern China</i>. Berkeley: University of California Press, 2011.</li>
<li>Skinner, G. William. "Sichuan's Population in the Nineteenth Century: Lessons from Disaggregated Data." <i>Late Imperial China</i> 8, no. 1 (1987): 1–79.</li>
<li>Stross, Randall E. <i>The Stubborn Earth: American Agriculturalists on Chinese Soil, 1898–1937</i>. Berkeley: University of California Press, 1986.</li>
<li>Ts'ai, Hui-yu Caroline. <i>Taiwan in Japan's Empire Building: An Institutional Approach to Colonial Engineering</i>. London: Routledge, 2009.</li>
<li>Van de Ven, Hans. <i>Breaking with the Past: The Maritime Customs Service and the Global Origins of Modernity in China</i>. New York: Columbia University Press, 2014.</li>
<li>Yao, Jen-to. "The Japanese Colonial State and Its Form of Knowledge in Taiwan." In <i>Taiwan Under Japanese Colonial Rule, 1895–1945: History, Culture, Memory</i>, edited by Ping-hui Liao and David Der-wei Wang, 37–61. New York: Columbia University Press, 2006</li>
</ul>
</div>
"""
