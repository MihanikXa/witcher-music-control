# Tests

Use script/resource checks, contrast/visual comparison fixtures, installation topology verification and in-game acceptance checklists. Do not claim runtime proof from static inspection alone.

`python -m unittest discover -s tests -v` verifies both bundle layouts, bounds
rejection, nested/variable-wrapper SWF and GFx recognition, missing-End rejection,
unknown formats and stripped zero-glyph fonts. Native inspection tests cover
known BC3 color/alpha selectors, partial blocks, truncated textures and invalid
CR2W version/table bounds. Synthetic fixtures contain no
game or author assets. A successful test run does not prove engine loading.
Controlled-investigation tests distinguish resource assertions from successful
or cancelled saves, check exclusive sampling rectangles and prevent staged
UTF-8/UTF-16 newline corruption. Five color-package gate tests reject changed
source, failed controls, extra assertions and warning regressions while allowing
the exact shared no-op diagnostic. Current suite: nineteen tests.
In-game acceptance criteria are in design/implementation-plan.md.
