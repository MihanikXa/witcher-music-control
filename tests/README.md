# Tests

Use script/resource checks, contrast/visual comparison fixtures, installation topology verification and in-game acceptance checklists. Do not claim runtime proof from static inspection alone.

`python -m unittest discover -s tests -v` verifies both bundle layouts, bounds
rejection, nested/variable-wrapper SWF and GFx recognition, missing-End rejection,
unknown formats and stripped zero-glyph fonts. Synthetic fixtures contain no
game or author assets. A successful test run does not prove engine loading.
In-game acceptance criteria are in design/implementation-plan.md.
