# China uncovered tables: review 2

Reviewed all **95** assigned complete records. Proposed **8** candidate terms; **73** tables already support existing detailed tags; **10** are deferred. Candidate evidence and existing fits overlap where a new term would add precision. All 95 keys are accounted for.

The existing assignments and schema remain unchanged. This is an advisory review for user evaluation.

## Strongest additions

| Candidate | Evidence tables | Assessment |
|---|---:|---|
| `commodity-geography` | 5 | high; genuine aggregate gap |
| `route-distances` | 22 | medium; optional cross mode specificity |
| `printing` | 1 | high; genuine industry gap |
| `demobilisation` | 2 | medium; optional process specificity |
| `professional-associations` | 1 | high; genuine institutional gap |
| `mercury` | 1 | medium; optional commodity specificity |
| `holidays-and-commemorations` | 1 | medium; optional definition clarification |
| `colonies-and-leased-territories` | 1 | medium; genuine status inventory gap |

Prioritise **commodity geography**, **printing**, and **professional associations**. The first covers five cross-sector regional product inventories that cannot be represented by three incidental commodities. Printing is an industry spanning publication formats. The medical association is a professional body rather than a hospital, a commercial chamber or a research institute.

**Route distances** recur in 22 tables, but sea-route and Yangtze examples can already use `shipping` or `inland-navigation`. A new cross-mode tag would make the reference data easier to find; it is not a prerequisite for tagging those tables. **Demobilisation** would distinguish troop disbandment from recruitment, while existing `army` and `public-budgets` already fit its expenditure tables.

**Mercury** would supply commodity precision parallel to tin, tungsten and antimony; existing `exports` and `mineral-production` still apply. **Holidays and commemorations** can instead be handled by explicitly extending `calendars-and-time`. **Colonies and leased territories** addresses a genuine mixed possession/status inventory without turning colonial publication context into a default tag.

## Blanks that do not justify new terms

- Mixed press directories can receive both `newspapers` and `periodicals`; no fused tag is needed.
- `public-debt` explicitly includes government and provincial borrowing.
- `imperial-household` explicitly includes royal succession and covers court gift inventories.
- `honours-and-ranks` and `administrative-divisions` already cover ranked Mongol chieftains and banners.
- Institutional staff lists remain the subject of their institutions: `banking`, `higher-education`, `river-conservancy`, and `postal-services` apply to rosters or accounts as appropriate.
- `wages` covers official military pay scales; detail topics are shared across high-level categories.
- A generic title does not negate clear supplied context: the 1916 import continuation is identified as imports by its context.

## Deferred cases

Seven damaged trade tables lack both commodity labels and reliable direction. These are evidence gaps, not vocabulary gaps. Three editions repeat the same short chronology of first Western commercial contacts: consider broadening the existing `historical-chronologies` definition instead of adding a separate history tag for every sector.

## Separate flag observations

The 1919 court gift list has item quantities and an object weight yet is marked textual; other editions of the same list are statistical. One trade-contact chronology has the opposite mismatch. The road itinerary includes mileages and the conservancy roster includes a count of 13 staff. These deserve later consistency checks; this review did not change any tags or flags.

Complete proposed definitions, exclusions, per-table evidence and existing-tag explanations are in [review-2.result.json](review-2.result.json).
