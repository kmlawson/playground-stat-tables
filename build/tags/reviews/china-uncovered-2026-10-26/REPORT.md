# China tables without detailed tags: four-agent vocabulary review

Review complete. All **380** frozen records were examined in four batches of **95**, using their complete table bodies, headings and supplied context. These are proposals for evaluation; the vocabulary and saved classifications have not been changed.

## What the review found

The reviewers suggested possible existing tags for **301** tables. Consolidation retained **300** such options: one public-holiday table requires a new observance tag or an explicit definition change, rather than the current calendars-and-time tag.

The other **80** records divide into **53** with a proposed vocabulary candidate and **27** still needing source-context or vocabulary-boundary decisions. Some of the 27 also have conditional candidate suggestions. Existing-tag options are advisory, not applied corrections.

Overlapping reviewer names were merged into **23** candidate tags: **10 recommended**, **8 optional refinements**, **4 boundary decisions**, and **1 conditional candidate**. All fit within the current high-level structure; no additional high-level topic is proposed.

## Recommended additions

| Proposed detailed tag | Evidence tables | Purpose and boundary |
| --- | ---: | --- |
| `route-distances` | 69 | A reusable cross-mode discovery term. Many sea/river/rail examples already admit a transport-mode tag; the new term identifies the distance or journey-time reference itself. |
| `commodity-origins` | 12 | Merge all three proposed names into one tag. Especially useful for qualitative, multi-sector product-to-region inventories; do not select three arbitrary commodities instead. |
| `anthropometry` | 6 | Covers the source's bodily measurements and historical physical typologies. Keep the historical wording in the source without adopting its theories as modern classifications. |
| `census-and-survey-methods` | 4 | One broad methods tag can cover population census forms and agricultural sampling. The farm-sample table deferred by reviewer 4 fits this proposal from reviewer 1; no separate agricultural-surveys tag is needed. |
| `public-holidays-and-commemorations` | 4 | Keep observances distinct from calendar conversion/time reckoning. Reviewer 2's suggested calendars-and-time reuse would require a definition change and is not accepted under the current rules. |
| `legal-profession` | 3 | Practitioner qualification and licensing are distinct from court establishments/caseload and population-by-occupation distributions. |
| `writing-systems-and-phonetics` | 3 | Distinguishes scripts, phonetic symbols and sound representation from language distribution and language instruction. |
| `real-estate` | 3 | Useful for market rents and transactions in land and buildings. One of the three evidence records has an uncertain lead-in and needs context confirmation before assignment. |
| `printing` | 2 | A productive activity spanning books, newspapers and other printed matter; distinct from paper production and publication type. |
| `professional-associations` | 1 | Only one example in this subset, but the institution type is reusable across medical, legal and engineering professions. Keep separate from commercial associations and trade unions. |

Evidence counts cover this 380-table subset only. The real-estate count includes one uncertain lead-in. Repeated annual series are not independent subjects. Route distances often already admit shipping, inland-navigation or railways; the new tag provides a common route-reference subject.

The census-and-survey-methods proposal includes **one farm-sample distribution** noticed in another review batch, giving four examples without introducing a separate farm-surveys tag.

## Optional refinements

| Candidate | Evidence tables | Evaluation |
| --- | ---: | --- |
| `demobilisation` | 3 | Existing army/public-budgets tags already fit the disbandment accounts. This adds process specificity. |
| `asbestos` | 3 | Existing industrial-output fits the evidence. Three editions repeat a company's manufactured-product series; recurrence is not three independent industries. |
| `mercury` | 1 | Existing exports/mineral-production already fit. Consider this as commodity precision consistent with other named mineral tags. |
| `school-curricula` | 1 | Existing primary-education fits the example. A cross-stage curriculum term is optional refinement. |
| `domestic-service` | 1 | A coherent household-labour subject, currently supported by one table in the reviewed subset. |
| `native-place-associations` | 1 | One clear origin-based association example. Do not generalise this tag to all guilds, businesses or overseas communities. |
| `fish-and-fish-products` | 1 | Could cover fish commodities in trade without assuming capture or cultivation. One example; first decide whether to broaden the existing fishing definition instead. |
| `militias-and-volunteer-forces` | 3 | Existing army already covers the volunteer-corps series. Optional narrower discovery term. |

## Decide existing-tag boundaries first

| Candidate | Evidence tables | Decision |
| --- | ---: | --- |
| `diplomatic-claims` | 1 | One pending compensation-claims table. Decide whether indemnities should explicitly include claims not yet imposed or accepted before creating a separate term. |
| `colonies-and-leased-territories` | 1 | One political-possession inventory. Check boundaries with colonial-administration, annexation-and-protectorates and administrative-divisions; never apply merely because a table comes from a colonial volume. |
| `foreign-trade` | 6 | One clean aggregate example supports a combined merchandise-trade concept. Five other records have missing commodity/direction context; a broader tag cannot repair that source uncertainty. Compare allowing imports plus exports for combined totals. |
| `foreign-trade-relations` | 6 | The same seven-event first-contact chronology appears in six editions across batches. Prefer a deliberate decision about subject-specific historical-chronologies before adding a trade-history synonym. |

## Conditional candidate

`riots-and-civil-unrest` — one table. Conditional on confirming the Pingyang casualty table's link to the running section The Korean Riots. Do not infer the cause from a vague disaster title alone.

## Evidence and audit files

[Structured proposals](proposals.json) contain definitions, inclusion/exclusion boundaries, related high-level topics, all evidence keys, and the original reviewer proposals. [Per-table assessments](table-assessments.json) cover every one of the 380 records, including existing-tag options and unresolved questions. [Validation](validation.json) checks exact coverage, approved existing IDs and unchanged saved files.

### Recommended-tag evidence

**route-distances**

- `china-handbook-1926:p0023_1` — (Distances from Shanghai) ([scan](https://archive.org/details/chinacommerciali00arno/page/n22/mode/1up))
- `china-1912:p0043_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1912/page/n43/mode/1up))
- `china-1912:p0043_3` — Distances (via Siberia) ([scan](https://archive.org/details/china-year-book-1912/page/n43/mode/1up))
- `china-1912:p0043_4` — Coast Distances.—A ([scan](https://archive.org/details/china-year-book-1912/page/n43/mode/1up))
- `china-1912:p0044_1` — Coast Distances.—B ([scan](https://archive.org/details/china-year-book-1912/page/n44/mode/1up))
- `china-1912:p0044_2` — Distances up the Yangtze ([scan](https://archive.org/details/china-year-book-1912/page/n44/mode/1up))
- `china-1912:p0044_3` — (Distances from Shanghai) ([scan](https://archive.org/details/china-year-book-1912/page/n44/mode/1up))
- `china-1914:p0024_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/chinayearbook1914shan/page/n23/mode/1up))
- `china-1914:p0024_3` — Distances (via Siberia) ([scan](https://archive.org/details/chinayearbook1914shan/page/n23/mode/1up))
- `china-1914:p0024_4` — Coast Distances.—A ([scan](https://archive.org/details/chinayearbook1914shan/page/n23/mode/1up))
- `china-1914:p0025_1` — Coast Distances.—B ([scan](https://archive.org/details/chinayearbook1914shan/page/n24/mode/1up))
- `china-1914:p0025_2` — Distances up the Yangtze ([scan](https://archive.org/details/chinayearbook1914shan/page/n24/mode/1up))
- `china-1914:p0025_3` — (Distances from Shanghai to Northern and Japanese Ports) ([scan](https://archive.org/details/chinayearbook1914shan/page/n24/mode/1up))
- `china-1919:p0030_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/chinayearbook1919shan/page/n29/mode/1up))
- `china-1919:p0030_3` — Distances (via Siberia) ([scan](https://archive.org/details/chinayearbook1919shan/page/n29/mode/1up))
- `china-1919:p0030_4` — Coast Distances.—A ([scan](https://archive.org/details/chinayearbook1919shan/page/n29/mode/1up))
- `china-1919:p0031_1` — Coast Distances.—B ([scan](https://archive.org/details/chinayearbook1919shan/page/n30/mode/1up))
- `china-1919:p0031_3` — (Distances from Shanghai to Northern Ports) ([scan](https://archive.org/details/chinayearbook1919shan/page/n30/mode/1up))
- `china-1913:p0022_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1913/page/n21/mode/1up))
- `china-1913:p0022_3` — Distances (via Siberia) ([scan](https://archive.org/details/china-year-book-1913/page/n21/mode/1up))
- `china-1913:p0022_4` — Coast Distances.—A ([scan](https://archive.org/details/china-year-book-1913/page/n21/mode/1up))
- `china-1913:p0023_1` — Coast Distances.—B ([scan](https://archive.org/details/china-year-book-1913/page/n22/mode/1up))
- `china-1913:p0023_3` — (Shanghai to Northern and Japanese Ports Distances) ([scan](https://archive.org/details/china-year-book-1913/page/n22/mode/1up))
- `china-1916:p0028_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1916/page/n27/mode/1up))
- `china-1916:p0028_3` — Distances (via Sibberia) ([scan](https://archive.org/details/china-year-book-1916/page/n27/mode/1up))
- `china-1916:p0028_4` — Coast Distances.—A ([scan](https://archive.org/details/china-year-book-1916/page/n27/mode/1up))
- `china-1916:p0029_1` — Coast Distances.—B ([scan](https://archive.org/details/china-year-book-1916/page/n28/mode/1up))
- `china-1916:p0029_3` — (Distances from Shanghai to Northern and Japanese Ports) ([scan](https://archive.org/details/china-year-book-1916/page/n28/mode/1up))
- `china-1922:p0050_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/chinayearbook1922shan/page/n50/mode/1up))
- `china-1922:p0050_2` — Distances (via Siberia) ([scan](https://archive.org/details/chinayearbook1922shan/page/n50/mode/1up))
- `china-1922:p0050_3` — Coast Distances.—A. ([scan](https://archive.org/details/chinayearbook1922shan/page/n50/mode/1up))
- `china-1922:p0050_4` — Coast Distances.—B. ([scan](https://archive.org/details/chinayearbook1922shan/page/n50/mode/1up))
- `china-1922:p0051_1` — Distances up the Yangtze ([scan](https://archive.org/details/chinayearbook1922shan/page/n51/mode/1up))
- `china-1922:p0051_2` — (Distances from Shanghai to Northern and Japanese Ports) ([scan](https://archive.org/details/chinayearbook1922shan/page/n51/mode/1up))
- `china-1923:p0071_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1923/page/n70/mode/1up))
- `china-1923:p0071_2` — Distances (Via Siberia) ([scan](https://archive.org/details/china-year-book-1923/page/n70/mode/1up))
- `china-1923:p0071_3` — Coast Distances.—A ([scan](https://archive.org/details/china-year-book-1923/page/n70/mode/1up))
- `china-1923:p0071_4` — Coast Distances.—B ([scan](https://archive.org/details/china-year-book-1923/page/n70/mode/1up))
- `china-1923:p0072_1` — Distances Up the Yangtze ([scan](https://archive.org/details/china-year-book-1923/page/n71/mode/1up))
- `china-1923:p0072_2` — (Sea Distances from Shanghai) ([scan](https://archive.org/details/china-year-book-1923/page/n71/mode/1up))
- `china-1924-5:p0053_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1924-5/page/n52/mode/1up))
- `china-1924-5:p0053_2` — Distances (Via Siberia) ([scan](https://archive.org/details/china-year-book-1924-5/page/n52/mode/1up))
- `china-1924-5:p0053_3` — Coast Distances.—A. ([scan](https://archive.org/details/china-year-book-1924-5/page/n52/mode/1up))
- `china-1924-5:p0053_4` — Coast Distances.—B. ([scan](https://archive.org/details/china-year-book-1924-5/page/n52/mode/1up))
- `china-1924-5:p0054_1` — Distances Up the Yangtze ([scan](https://archive.org/details/china-year-book-1924-5/page/n53/mode/1up))
- `china-1924-5:p0054_2` — (Distances from Shanghai to Northern and Japanese Ports) ([scan](https://archive.org/details/china-year-book-1924-5/page/n53/mode/1up))
- `china-1925-6:p0079_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1925-6/page/n78/mode/1up))
- `china-1925-6:p0079_2` — Distances (Via Siberia) ([scan](https://archive.org/details/china-year-book-1925-6/page/n78/mode/1up))
- `china-1925-6:p0079_3` — Coast Distances.—A ([scan](https://archive.org/details/china-year-book-1925-6/page/n78/mode/1up))
- `china-1925-6:p0079_4` — Coast Distances.—B ([scan](https://archive.org/details/china-year-book-1925-6/page/n78/mode/1up))
- `china-1925-6:p0080_1` — Distances up the Yangtze ([scan](https://archive.org/details/china-year-book-1925-6/page/n79/mode/1up))
- `china-1925-6:p0080_2` — (Shanghai to Dairen, Newchwang, Vladivostok and Japanese Ports Distances) ([scan](https://archive.org/details/china-year-book-1925-6/page/n79/mode/1up))
- `china-1926-7:p0062_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1926-7/page/n61/mode/1up))
- `china-1926-7:p0062_2` — Distances (Via Siberia) ([scan](https://archive.org/details/china-year-book-1926-7/page/n61/mode/1up))
- `china-1926-7:p0062_3` — Coast Distances.—A. ([scan](https://archive.org/details/china-year-book-1926-7/page/n61/mode/1up))
- `china-1926-7:p0062_4` — Coast Distances.—B. ([scan](https://archive.org/details/china-year-book-1926-7/page/n61/mode/1up))
- `china-1926-7:p0063_1` — Distances Up the Yangtze ([scan](https://archive.org/details/china-year-book-1926-7/page/n62/mode/1up))
- `china-1926-7:p0063_2` — (Distances from Shanghai to Northern and Japanese Ports) ([scan](https://archive.org/details/china-year-book-1926-7/page/n62/mode/1up))
- `china-1928:p0034_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1928/page/n33/mode/1up))
- `china-1928:p0034_2` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1928/page/n33/mode/1up))
- `china-1928:p0034_3` — Distances (Via Siberia) ([scan](https://archive.org/details/china-year-book-1928/page/n33/mode/1up))
- `china-1928:p0034_4` — Coast Distances.—A. ([scan](https://archive.org/details/china-year-book-1928/page/n33/mode/1up))
- `china-1928:p0034_5` — Coast Distances.—B. ([scan](https://archive.org/details/china-year-book-1928/page/n33/mode/1up))
- `china-1929-30:p0029_1` — Distances (Nautical Miles) ([scan](https://archive.org/details/china-year-book-1929-30/page/n29/mode/1up))
- `china-1931-2:p0019_3` — Sea, Coast and River Distances ([scan](https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n18/mode/1up))
- `china-1931-2:p0020_1` — Sea, Coast and River Distances ([scan](https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n19/mode/1up))
- `china-1931-2:p0020_2` — Distances (via Siberia) ([scan](https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n19/mode/1up))
- `china-1931-2:p0020_3` — Coast Distances—A ([scan](https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n19/mode/1up))
- `china-1931-2:p0020_4` — Coast Distances—B ([scan](https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n19/mode/1up))

**commodity-origins**

- `china-1914:p0061_1` — List of the Principal Chinese Products ([scan](https://archive.org/details/chinayearbook1914shan/page/n60/mode/1up))
- `china-1914:p0062_1` — List of the Principal Chinese Products—contd. ([scan](https://archive.org/details/chinayearbook1914shan/page/n61/mode/1up))
- `china-1914:p0063_1` — List of the Principal Chinese Products, Arranged According to Each Province ([scan](https://archive.org/details/chinayearbook1914shan/page/n62/mode/1up))
- `china-1919:p0067_1` — List of the Principal Chinese Products ([scan](https://archive.org/details/chinayearbook1919shan/page/n66/mode/1up))
- `china-1919:p0069_1` — List of the Principal Chinese Products, Arranged According to Each Province ([scan](https://archive.org/details/chinayearbook1919shan/page/n68/mode/1up))
- `china-1913:p0057_1` — List of the Principal Chinese Products, as Shown in the Production Map ([scan](https://archive.org/details/china-year-book-1913/page/n56/mode/1up))
- `china-1913:p0058_1` — List of the Principal Chinese Products—contd. ([scan](https://archive.org/details/china-year-book-1913/page/n57/mode/1up))
- `china-1916:p0065_1` — List of the Principal Chinese Products ([scan](https://archive.org/details/china-year-book-1916/page/n64/mode/1up))
- `china-1916:p0066_1` — List of the Principal Chinese Products—contd. ([scan](https://archive.org/details/china-year-book-1916/page/n65/mode/1up))
- `china-1922:p0159_1` — List of the Principal Chinese Products ([scan](https://archive.org/details/chinayearbook1922shan/page/n159/mode/1up))
- `china-1923:p0257_1` — List of the Principal Chinese Products ([scan](https://archive.org/details/china-year-book-1923/page/n256/mode/1up))
- `china-1923:p0258_1` — List of the Principal Chinese Products, Arranged According to Each Province. ([scan](https://archive.org/details/china-year-book-1923/page/n257/mode/1up))

**anthropometry**

- `china-1925-6:p0197_1` — (Percentages of Cephalic Types among the Living Population of China Proper) ([scan](https://archive.org/details/china-year-book-1925-6/page/n196/mode/1up))
- `china-1926-7:p0163_1` — (Cephalic Index Percentages of the Living Population of China Proper) ([scan](https://archive.org/details/china-year-book-1926-7/page/n162/mode/1up))
- `china-1928:p0062_1` — (Cephalic Index Percentages of the Living Population of China Proper) ([scan](https://archive.org/details/china-year-book-1928/page/n61/mode/1up))
- `china-1929-30:p0057_1` — (Cephalic indices of the living population of China proper) ([scan](https://archive.org/details/china-year-book-1929-30/page/n57/mode/1up))
- `china-1929-30:p0057_2` — (Tentative conclusions regarding the physical traits of the Chinese) ([scan](https://archive.org/details/china-year-book-1929-30/page/n57/mode/1up))
- `china-1938:p0030_1` — (Cephalic Indices of the Chinese of China Proper) ([scan](https://archive.org/details/chinayearbook1930000hgww/page/n30/mode/1up))

**census-and-survey-methods**

- `china-peking-1921:p0105_1` — (Questions Asked on the Census Blank Concerning Each Individual) ([scan](https://archive.org/details/pekingsocialsurv00gambrich/page/n104/mode/1up))
- `china-peking-1921:p0106_1` — (Items Reported by the Census Boards) ([scan](https://archive.org/details/pekingsocialsurv00gambrich/page/n105/mode/1up))
- `china-peking-1921:p0367_1` — Figure 24: Church Survey Card ([scan](https://archive.org/details/pekingsocialsurv00gambrich/page/n366/mode/1up))
- `china-1929-30:p0971_1` — Distribution of Farms ([scan](https://archive.org/details/china-year-book-1929-30/page/n971/mode/1up))

**public-holidays-and-commemorations**

- `china-1922:p1009_1` — Commemoration Days of the Republic ([scan](https://archive.org/details/chinayearbook1922shan/page/n1009/mode/1up))
- `china-1925-6:p0997_1` — Commemoration Days of the Republic ([scan](https://archive.org/details/china-year-book-1925-6/page/n996/mode/1up))
- `china-1926-7:p0638_1` — Commemoration Days of the Republic ([scan](https://archive.org/details/china-year-book-1926-7/page/n637/mode/1up))
- `china-1928:p1256_1` — Commemoration Days of the Republic ([scan](https://archive.org/details/china-year-book-1928/page/n1255/mode/1up))

**legal-profession**

- `china-1944:p0222_1` — Number of Lawyers Holding Certificates from the Ministry of Justice ([scan](https://archive.org/details/chinahandbook0000unse))
- `china-1937-43:p2-0064_1` — Number of Lawyers Holding Certificates from the Ministry of Justice ([scan](https://archive.org/details/china-handbook-1937-1943/China%20Handbook%201937-1943%20Part%202%20of%205/page/n64/mode/1up))
- `china-1950:p1-0121_2` — Advocate's Licenses Issued by the Ministry of Justice During 1945-1947 ([scan](https://archive.org/details/china-handbook-1950/China%20Handbook%201950%20Part%201%20of%203/page/n121/mode/1up))

**writing-systems-and-phonetics**

- `china-1923:p0399_1` — 24 Consonants (聲母) ([scan](https://archive.org/details/china-year-book-1923/page/n398/mode/1up))
- `china-1923:p0400_1` — 15 Finals (韵母) Of Which The First Three Are Considered As Medials (Actually 16) ([scan](https://archive.org/details/china-year-book-1923/page/n399/mode/1up))
- `china-1923:p0400_2` — 22 Derived Finals (結合韻母) ([scan](https://archive.org/details/china-year-book-1923/page/n399/mode/1up))

**real-estate**

- `china-handbook-1926:p0543_1` — (Land Transactions: Area in Mow and Cost in Taels, 1918–1923) ([scan](https://archive.org/details/chinacommerciali00arno/page/n542/mode/1up))
- `china-handbook-1926:p0745_1` — (Property Values and Rents in Nanking) ([scan](https://archive.org/details/chinacommerciali00arno/page/n744/mode/1up))
- `china-handbook-1926:p0793_1` — (Property Values and Rents: Annual Rental of Leased Land in the City of Tsingtao) ([scan](https://archive.org/details/chinacommerciali00arno/page/n792/mode/1up))

**printing**

- `china-1914:p0121_2` — Printing and Lithographic Works ([scan](https://archive.org/details/chinayearbook1914shan/page/n120/mode/1up))
- `china-1916:p0121_1` — (Printing Establishments) ([scan](https://archive.org/details/china-year-book-1916/page/n120/mode/1up))

**professional-associations**

- `china-1922:p1029_1` — National Medical Association of China ([scan](https://archive.org/details/chinayearbook1922shan/page/n1029/mode/1up))

## Individual reviews

- [Review 1: 95 tables](review-1.REPORT.md) · [structured result](review-1.result.json)
- [Review 2: 95 tables](review-2.REPORT.md) · [structured result](review-2.result.json)
- [Review 3: 95 tables](review-3.REPORT.md) · [structured result](review-3.result.json)
- [Review 4: 95 tables](review-4.REPORT.md) · [structured result](review-4.result.json)
