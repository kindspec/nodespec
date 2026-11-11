# block-end-moved-over-new-edge

One branch moves a block's `end` below the comments after it; the other adds an edge between those comments. The merged edge stands in the block.

## The branches

- ours moves `end` from above the two comments to below them, so the comments describe the block from inside it.
- theirs adds `a --> b` between the two comments, at the top level.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: ours' block holds a member line and comments, which may stand in a block; theirs' edge is at the top level and names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes line 7 and inserts after line 9; theirs inserts after line 8. Line 8 lies unchanged between ours' deletion and theirs' insertion, and line 9 between the two insertions. Clean.

## The verdict

In the merged file `a --> b` comes after `subgraph s` and before the `end` that closes it: an edge statement in a block, `statement-in-block`. The refused line names nothing, so it is the only refusal. Git saw two edits to different lines; which block a line is in is decided by lines it did not touch.

> In a block means after a subgraph line that opened a block and before the `end-line` that closes it (§4.7); everywhere else is the top level.
>
> SPEC.md §4.3

> an edge statement, or a `classDef`, `class` or `style` statement, in a block is refused as `statement-in-block`
>
> SPEC.md §6

> A comment matches `comment`. It is allowed anywhere, inside a block included, and is otherwise ignored.
>
> SPEC.md §4.2

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.
>
> SPEC.md §9

Expected: `{"merge": "clean", "refusal": ["statement-in-block"]}`
