# Review 1: 95 China tables without detailed tags

All **95 complete records** were reviewed, including all parts/rows and supplied context, notes and English layers. Current definitions and relevant includes/excludes were checked. No vocabulary or table assignments were changed.

**69 tables already have a supported existing-tag option.** There are **11 proposed additions**, covering **41 distinct tables**; these groups overlap. **11 tables** retain contextual/source questions. Every input key is accounted for in [the structured result](review-1.result.json).

The strongest additions are `census-and-survey-methods`, `distances-and-journey-times`, `real-estate`, `commodity-origins` and `printing`. Their scopes and exclusions are specified in the JSON. They improve discovery without proliferating narrowly named commodities or table formats.

| Proposed ID | Priority | Supporting tables | Type |
|---|---|---:|---|
| `census-and-survey-methods` | high | 3 | subject-gap |
| `distances-and-journey-times` | high | 18 | cross-mode-discovery-refinement |
| `real-estate` | high | 3 | subject-gap |
| `commodity-origins` | high | 5 | subject-gap |
| `printing` | high | 1 | industry-specific-refinement |
| `fish-and-fish-products` | medium | 1 | subject-gap |
| `domestic-service` | medium | 1 | subject-gap |
| `native-place-associations` | medium | 1 | subject-gap |
| `foreign-trade` | medium | 6 | conditional-aggregate-tag |
| `school-curricula` | medium | 1 | optional-refinement-existing-tag-fits |
| `demobilisation` | medium | 1 | optional-refinement-existing-tag-fits |

The 18 distance tables include repetitions across annual volumes, rather than 18 independent kinds of distance data. Existing `shipping` or `inland-navigation` already fits explicitly waterborne route tables; a common distance/time tag is useful for mixed modes and for avoiding unsupported mode inference. Likewise `printing` is a sector refinement over the valid generic `companies` fallback. `school-curricula` and `demobilisation` are optional refinements, not blockers to existing classification.

`foreign-trade` should be considered as an aggregate fallback, supported by a clean total-foreign-trade port table. Five other candidate examples have missing labels or ambiguous direction; adding the term cannot repair those records. The tentative land-transactions example also needs its missing lead-in checked; the two clear urban property/rent tables independently support `real-estate`.

## Existing coverage that avoids unnecessary additions

- Bank officers and branch directories fit `banking`; railway advertisements fit `railways` and `advertising`.
- Merchant guild accounts fit `business-associations`, whose includes explicitly name merchant guilds. The blind entertainers' guild and Lu Pan union lack enough organisational-purpose evidence and remain deferred.
- Gruel-kitchen finances fit `poor-relief`. Popular lecture halls fit `literacy-and-adult-education`; their budgets also fit `education-finance`.
- Church-family income bands fit `household-budgets`, whose includes cover actual family income surveys.
- Hotel tables fit `tourism`, whose definition expressly covers visitor accommodation. Shops and factories can fit `companies` or the relevant production tag.
- Mine counts fit `mineral-production`; roads and routes fit `roads-and-bridges`; coast-lighting jurisdictions fit `navigation-aids`; post-office directories fit `postal-services`.
- Noble status hierarchies fit `honours-and-ranks`, and rulers' succession/reign lists fit `imperial-household`.
- The storyteller source list contains book titles and fits `books`; temple markets fit `markets-and-exchanges`.
- Confectionery fits `food-processing`. The aerated-water table also contains a large shipyard group, so its problem is not solved by adding a drinks label alone.

A specific missed source clue: **`china-1914:p0203_1`** has footnotes explicitly describing **Exports to Foreign Countries by Junk** omitted from its totals. Its own notes therefore support the existing `exports` tag despite the previous empty assignment.

Unclear association purposes, intellectual-author lists and a lone trade-contact chronology were retained for wider review rather than used to create vague new categories.
