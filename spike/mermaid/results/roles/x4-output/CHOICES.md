# CHOICES — extract2.py

Each entry gives the rule and its section, what was ambiguous, and what
`extract2.py` does. I wrote this from `SPEC.md` and
`mermaid-12.1.0-flowchart.md` only. I could not run R (Mermaid 12.1.0) here.
Where H has to agree with R on a behaviour that neither document states, the
entry says **assumed R behaviour**. In those cases H refuses the text (out of
the subset) unless I was confident about R.

## Invocation and output (Appendix D)

1. **Output shape.** One JSON object with these fields:
   - `outcome`: `decided`, `E`, `G0`, `OUT-OF-SUBSET`, `DUP-TITLE` or
     `INPUT-OUT-OF-SUBSET`.
   - `states`: H's verdict on each of the four files.
   - `decided`: every decided unit with its value, with `absent: true` for a
     decided absence.
   - `conflicts` and `undecided_memberships`.
   - `refusal_cases` (§5.2) and `exposure` (§5.5).
   - `new_lint_failures`.
   - `records`: each has `category`, `group`, `tier` and `objects`, plus
     detail about the unit.
   - `tiers`: a count of records per tier.

   The "—" tier is written `-`.
2. **Exit status.** A wrong argument count exits 2. Every verdict about the
   texts, including E and out-of-subset, exits 0 with JSON. An internal error
   exits non-zero with a traceback; it is not hidden.
3. **Order is not printed among the decided values.** The order class (§4.1)
   is decided pair by pair (choice 30) and is only reported as S-ORDER.

## Files, strata, fences (§5.3, Appendix C L6)

4. **Which strata are Markdown.** The spec names only stratum `D`. The diagram
   is read from a Mermaid fence when:
   - the base path ends in `.md`, `.markdown` or `.mdx`; or
   - the stratum is `D`; or
   - the base file contains a Mermaid fence.

   Otherwise the whole file is the diagram, and so is any `.mmd` or
   `.mermaid` file.
5. **What counts as a Mermaid fence.** A CommonMark fence (three or more
   backticks or tildes, up to three spaces of indent) whose info string is
   exactly `mermaid`. `mermaid-example` is not one. An unclosed fence runs to
   the end of the file. Fences inside other fenced blocks are skipped.
6. **Conflict markers (E).** A line starting `<<<<<<<`, `>>>>>>>` or
   `|||||||` followed by a space or end of line, or a line that is exactly
   `=======`. A marker anywhere in the merged file makes it E, for every
   stratum. §5.3 says this explicitly for stratum D, and its first sentence
   ("its merged file holds a conflict marker") reads as the whole file for
   all strata.
7. **`git ls-files -u` is not consulted.** The extractor sees only the four
   files, so an unmerged index entry with no marker in the file cannot be
   seen.
8. **Text normalisation.** UTF-8 (undecodable bytes are replaced), a leading
   BOM is dropped, and CRLF and CR become LF before parsing.

## "R does not parse" without R (§4.4)

9. **E versus OUT-OF-SUBSET when H fails on the merged diagram.** H sorts each
   failure into one of three kinds:
   - **noparse**: certain R failures, so the result is **E**. These are the
     ones §4.4 lists, and the Mermaid doc's own warning about `end`:
     - an unknown or mixed-case header (`UnknownDiagramError`);
     - `@{ shape: … }` with an uppercase letter or `_` ("No such shape");
     - an out-of-range `linkStyle` index, counted against the edges defined
       *before* the statement;
     - more than 100,000 edges;
     - a `subgraph` without `end`, or `end` without a `subgraph`;
     - lowercase `end` used as a node id;
     - an unterminated front matter block.
   - **unsupported**: outside the subset, where R may well parse it. The
     result is **OUT-OF-SUBSET**. Any statement H cannot read lands here,
     because without R I cannot tell a broken text from a valid one H doesn't
     know.
   - **notflowchart**: see choice 11.
10. **An edge count over 100,000 is E, not OUT-OF-SUBSET.** With
    `maxEdges: 100000`, R throws "Edge limit exceeded", and §4.4 lists that
    among the texts that do not parse. For an input it simply means "not in
    the subset".
11. **G0 "no longer a flowchart".** If the header is a known non-flowchart
    Mermaid keyword (`sequenceDiagram`, `classDiagram`, `gantt`, …), the
    result is G0. A header that is no Mermaid diagram at all is E (choice 9).
    In Markdown mode, a merged file without exactly one Mermaid fence is G0.
12. **Order of outcomes.**
    1. Conflict marker, then noparse: E. This applies even when an input is
       out of the subset.
    2. Any input out of the subset: `INPUT-OUT-OF-SUBSET`, with no records.
       §5.3 says every other category needs four states in the subset.
    3. G0.
    4. Merged out of the subset: `OUT-OF-SUBSET` or `DUP-TITLE`.
    5. Otherwise the records.

## The subset, as H reads it (Appendix A, §4.3)

13. **Ids.** ASCII letters, digits and `_`. A `-` is part of an id only when
    it isn't followed by `-`, `>` or `.`, and a `.` only when it isn't
    followed by `-` or `.`. This mirrors the docs' "dev--- ops" note. Non-ASCII
    ids are refused. Keywords used as ids (`subgraph`, `style`, `class`,
    `click`, `default`, …) are refused.
14. **Arrows.** Only the listed arrows and their longer forms:
    - `-->`, `---`, `--o`, `--x`, `<-->`, `o--o`, `x--x`
    - `-.->`, `-.-`
    - `==>`, `===`
    - `~~~`

    Anything else that R might accept is refused: `<==>`, `==o`, `x-->`,
    `<---`, a labelled `~~~`, and so on. A leading `o` or `x` head must
    follow whitespace, so it can't be read as part of the id. Kinds are
    normalised to `(line, start head, end head)` and length is dropped, as
    Appendix A says.
15. **Labels.**
    - Text is quoted (`"…"`) or unquoted. An unquoted label may not contain
      brackets, quotes, `|`, `;`, a backtick, link-like runs (`--`, `==`,
      `-.`, `.-`, `~~`), or the word `end` in lowercase.
    - **Assumed R behaviour:** labels pass through DOMPurify. So
      `<br>`, `<br/>` and `<br />` are all held as `<br>`. Any other `<`, `>`
      or `&` is refused, because its sanitised form is not given.
    - Labels, titles and edge texts are trimmed, and one pair of surrounding
      quotes is stripped.
    - Multi-line labels and Markdown strings are refused. Empty labels are
      refused.
16. **Entity codes.** **Assumed R behaviour:** R rewrites `#name;` into
    placeholders before it parses. So any text where `#\w+;` would survive
    that pass is refused. This includes styles such as `fill:#f9f;stroke:…`.
    The doc's `#quot;` example is therefore out of the subset.
17. **`@{ … }`.**
    - It must be one line, read as a YAML flow mapping, with only the keys
      `shape` and `label`.
    - Values must be strings. Unquoted numbers, booleans and null are
      refused, as are escapes.
    - The shape name is kept as written (aliases are not mapped to short
      names). It must be one of the short names or aliases in the doc's shape
      table; any other lowercase name is refused.
    - The label is taken raw, as R takes `doc.label`.
18. **Classic shapes and R types.** `[ ]` square, `( )` round, `([ ])`
    stadium, `[[ ]]` subroutine, `[( )]` cylinder, `(( ))` circle, `> ]` odd,
    `{ }` diamond, `{{ }}` hexagon, `[/ /]` lean_right, `[\ \]` lean_left,
    `[/ \]` trapezoid, `[\ /]` inv_trapezoid, `((( )))` doublecircle.
19. **Statements.**
    - Statements split at `;` outside quotes and brackets, and at newlines.
    - A statement that continues onto the next line is refused, even where R
      would join it (for example a link at the end of a line).
    - A `%%` comment must be on its own line; inline comments are refused.
    - A `%%{…}%%` directive is accepted only before the header.
    - `direction` is accepted only inside a subgraph, with `TB`, `BT`, `LR`
      or `RL`.
    - `accTitle` and `accDescr` are refused.
20. **Subgraph headers.**
    - `subgraph id [title]` and `subgraph id` give an explicit id.
    - `subgraph Some Title`, and any quoted header containing whitespace, have
      no explicit id and are keyed `title:<title>`.
    - **Assumed R behaviour:** a quoted header with no whitespace,
      `subgraph "One"`, gives explicit id `One`. This follows R's "id equals
      title and contains whitespace" test.
    - A bare `subgraph` is refused, as are two subgraphs with the same
      explicit id and an explicit id `subGraphN`.
    - R's `subGraphN` number counts subgraphs in closing order.
21. **Styles.** `style`, `classDef` and `linkStyle` values are split at commas
    and each part is trimmed. **Assumed R behaviour:** if a `linkStyle` has no
    `fill…` entry, `fill:none` is appended. Backslashes and quotes in styles,
    and `linkStyle … interpolate`, are refused.
22. **`click`.**
    - A URL form sets `link`, and `linkTarget` when a target is given.
    - A callback form is accepted and has no effect, since the security level
      is strict.
    - **Assumed R behaviour:** URLs are held as written. Any URL that a URL
      sanitiser might rewrite is refused: whitespace, `%`, `&`, `\`, control
      characters, or a `javascript:`, `data:` or `vbscript:` scheme.
    - Tooltips are read and ignored; Appendix A does not map them.
23. **Order of R database calls.** Within a statement, vertices are added
    group by group, and each group's links are added after the next group's
    vertices. This is what decides whether a node statement comes "before" or
    "after" an edge id (Appendix A, `edgeIdThenNode`). The auto edge id is
    `L_<start>_<end>_<n>`. **Assumed R behaviour:** a vertex whose id equals
    *any* existing edge id is dropped.

## The model (§4.1, §4.2, Appendix A)

24. **Kinds per key.** The kind unit's value is the *set* of kinds on the key,
    such as `["node","subgraph"]` for `subEqNode`. Units that belong to one
    kind carry it:
    - membership is `(kind, key)`;
    - a user-id edge's label is the property `edgeLabel`, so it stays apart
      from a node's `label`.
25. **Edges.**
    - An edge without a user id is a count unit on
      `(from key, to key, kind, label)`, with `""` for no label.
    - An edge with a user id has the scalar units `from`, `to`, `type`,
      `edgeLabel` and `linkstyle`. `from`, `to` and `type` are relation;
      `edgeLabel` is text.
    - An edge end is the subgraph's key when it names a subgraph id (explicit
      or `subGraphN`) that has no node statement anywhere.
26. **Membership of subgraphs.** Membership uses Appendix A's rule for nodes:
    the first subgraph, in closing order, whose node list holds the member's
    R id. A subgraph that lists itself is skipped. Top level is `null`.
27. **Style class contents.** The style class covers:
    - vertex `classes` (without `clickable`) and `styles`;
    - `classDef` styles;
    - `linkStyle` per edge;
    - `linkStyle default`;
    - header direction and subgraph `direction`. §4.1 lists direction
      statements under style; `TD` is held as `TB`, and no direction means
      `TB`.

    Edge and subgraph classes are not compared, because Appendix A does not
    map them.
    - For edges without an id, the `linkstyle` unit is the sorted multiset of
      styles over all edges with that key.
    - A node's `styles` and `link` units exist only when set.
28. **Undecided membership (§4.2).** A holder is treated as "decided absent"
    when its key's decided kinds lack `subgraph`, or the key is decided absent.
    Undecided memberships are left out of decided values, conflicts, I1, I3,
    G3, MC and exposure.

## Oracle and refusal cases (§5.1, §5.2, §5.5)

29. **Dangling.** For each key decided absent (and present in some input),
    look for decided-present units that refer to it:
    - units keyed by it;
    - edges ending at it;
    - user-id edges whose `from` or `to` names it.

    One I1 per such key. Its objects are the key plus every key of those
    units, including the two ends of each edge.
30. **Delete/modify and collision.** These look only at identity keys (node,
    subgraph, user edge id). A plain edge is not a key.
    - In delete/modify, "the other leg changes a unit" means a value that
      differs from B while that leg keeps the key.
    - Exposure's "added or changed" means a present value that differs from B.
      A unit removed by the other leg doesn't count.

## Records (§5.3, §5.4)

31. **I4.** Read as: no input gives the key two kinds, and no input gives it a
    kind other than its decided kind. Then the merged kinds differ from the
    decided kinds and are not absent. I4 suppresses G1 and G2 for that key.
32. **When a key's presence differs**, between decided and merged, for one
    kind:
    - a node gives G1;
    - a user-id edge gives G2 `lost` or `extra`;
    - a subgraph gives G4 on its title.

    The other units of that kind on that key are then not reported again.
33. **Suppression under I1–I4.** §5.3 says G1 is "outside I1–I4". I extend
    that: no G, C, D or MC record is made for a unit keyed by an I record's
    primary key (the removed, colliding, deleted or clashing key). G1 is also
    skipped for every I-record object. Without this, one dangling node would
    be counted again as G4/C/D on its own label, shape and styles.
34. **G2 for user-id edges.** A changed `from`, `to` or `type` is G2 with
    `detail: "changed"`. Edge counts give `lost` or `extra` with the size of
    the difference.
35. **G4 objects for an edge label.** The edge id plus its two ends. Other
    text units have the key.
36. **MC.**
    - Only conflicts not keyed by a collision or delete/modify key count.
    - Eligible when the merged value is neither O's nor T's (absent counts as
      a value).
    - Group and tier follow the class:
      - relation, membership and text: structure, tier A;
      - shape: C;
      - style: D;
      - identity: the identity group, tier A. §5.3 does not name this case.
    - An ineligible MC is listed with tier `-`.
37. **S-LINKSTYLE.** A `linkStyle` difference is S-LINKSTYLE when the style it
    lost appears on another merged edge, or the style it gained was decided
    for another edge. Otherwise it is D.
38. **S-ORDER.**
    - Decided pair by pair. For keys a and b, the unit is "a before b" in each
      state that holds both, and the §5.1 rule is applied to those values.
    - It is reported once per sequence: the vertex map, and the edge list
      keyed by edge id or by (edge key, occurrence).
    - Above 1,500 entries, only adjacent merged pairs are checked, to stay
      fast.
39. **DUP-TITLE.** When the merged file is out of the subset only because
    titles are duplicated, and each duplicated `title:` key is absent in B but
    present in both legs. Any other duplicate title is OUT-OF-SUBSET. The
    record carries `exposed`, for §9.1's count.
40. **Lints (Appendix C).**
    - **L1**: a node key without a node statement.
    - **L2**: different labels, or different R shape types, across one id's
      node statements. `[x]` is `square` and `@{shape: rect}` is `rect`, so
      they differ.
    - **L3**: a node mentioned in vertex statements whose innermost blocks are
      two different subgraphs.
    - **L4**: a key with two kinds in the model, or an id used in the text as
      two of node, explicit subgraph id and edge id. A bare end naming a
      subgraph is not a node use.
    - **L5**: two edge statements with the same written id, or with the same
      `(from, to, kind, label)`. Its objects are both ends and the id.
    - **L6** is G0 (choice 11).
    - A record is demoted from A to B when any `(lint, object)` on its objects
      is absent from all three inputs.

## Invocation 4

41. **Units on a key whose presence differs, or that an I record names
    (inputs 1–10, 12). Changed. This replaces choices 32 and 33.** §4.2 says
    the oracle decides each unit separately. §5.3 defines G3, G4 and C per
    unit: "a membership differs", "a text unit differs", "a shape unit
    differs". The only exclusion the spec states is on G1, which applies
    "outside I1–I4". Nothing says G1 or an I record absorbs the node's
    membership, label or shape. So each of those units, when its decided value
    and merged value differ, now gets its own G3, G4, C or D record. Decided
    absent against merged present counts as a difference. For example, in
    input 1 `fraud_check` gets G1 + G3 + G4 + C, and in input 4 `canary` gets
    I1 + G3 + G4 + C. Two things are kept:
    - G1 is still skipped for I-record objects, because §5.3 says so.
    - A user-id edge's own `from`, `to` and `type` are still not reported
      next to its G2 lost/extra. §4.1 makes the edge a single relation unit
      keyed by its id, so these are facets of the one count, not separate
      units. Its `edgeLabel` is a text unit (§4.1 "each edge label") and gets
      G4 like any other.

    Units that are model conflicts get no G/C record. G and C compare against
    a decided value, and MC is "outside §5.2", so conflicts keyed by a refusal
    key stay silent. That is why `fax` in input 9 gets I3 + G3 only (its label
    and shape are conflicts), and why `paypal` in input 10 gets no G4. The
    tier-B demotion now also applies to these G3/G4 records (inputs 5 and 7,
    L1 on `fe` and `db`).
42. **S-ORDER objects (input 7). Changed.** §5.3 says a record's objects are
    "the keys it concerns". Only G0 is given the path. I used to give S-ORDER
    the path, and the other reader gives it no objects at all. Neither one is
    the keys concerned. The objects are now the keys of every inverted pair:
    the node ids for the vertex map, and the edge id or the two ends for the
    edge list. In input 7 that is `["db", "worker"]`. This has no effect on
    tier, since S-ORDER is "—".
43. **I4 when an input already gives the key another kind (inputs 11, 12,
    13). Kept (choice 31).** §5.3 reads "A key that no input gives two kinds,
    or a kind other than its decided kind, has two kinds or a different kind
    in the merged model". The phrase "or a kind other than its decided kind"
    is a second object of "no input gives".
    - **Input 12.** `api` is a node in B, and the decided kind is
      `subgraph`. So an input gives a kind other than the decided one, and
      I4's precondition fails. The node's presence then differs, which gives
      G1 (§5.3: a decided-absent node is present). Under choice 41 its G3, G4
      and C come with it.
    - **Inputs 11 and 13.** The kind is a model conflict, so there is no
      decided kind for the inputs to match. The legs' clash is the I2
      collision, which both readers report. A second I4 would count the same
      collision twice.
