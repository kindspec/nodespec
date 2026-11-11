# A member line the merge leaves outside its block

Ours moves `end` up, above the two comment lines, so the block holds only
`a`. Theirs adds the member line `b` between the comments, inside the block.
The comments keep the edits apart, so stock git merges them clean, and `b`
now sits after `end`, at the top level. Each version is in the profile.

SPEC.md §4.2's grammar has `member-line = *WSP id *WSP`, and a bare `b`
matches no `shape`, so it is not a `node-stmt`. §4.3:

> 10. Matches `member-line`: in a block, a member line (§6); at the top
>     level, `malformed-line`.

So the merged file is refused as `malformed-line`. `b` is declared, so it is
not `undeclared-id`.

This case was written by the pull request's reviewer, who had the checker
in reach, after the blind batch had listed `malformed-line` among the
refusals no clean merge can produce. Its verdict follows from the two
sentences above alone.
