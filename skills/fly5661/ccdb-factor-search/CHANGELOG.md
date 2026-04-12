# Changelog

## 0.1.3

- upgraded README into a fuller public-facing skill page with capabilities, use cases, output fields, factor-type guidance, and API field checklist
- updated `references/api-contract.md` with confirmed field meanings (`year`, `applyYear`, `applyYearEnd`, `countries`, `sourceLevel`)
- fixed English raw-term truncation to avoid mid-word clipping
- added China-first bias for Chinese requests without explicit region on geo-sensitive factors
- added missing-region warning for electricity / steam / natural gas queries
- added recency bonus for latest-factor requests based on applicability year
- strengthened authority weighting for stronger official / international sources
- distinguished carbon-footprint factors vs emission factors in ranking and risk output
- added direct-use guidance in final recommended result

## 0.1.2

- rewrote README to improve ClawHub presentation and conversion
- clarified business use cases, examples, and value proposition
- made conservative matching / no-guessing behavior more explicit
- added clearer output structure and positioning vs plain search

## 0.1.1

- added `_meta.json`
- improved conservative API error handling
- expanded eval coverage
- clarified README and publishing notes

## 0.1.0

- initial beta release
