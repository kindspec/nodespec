# subgraphs-nested-each-in-the-other

One branch nests `t` in `s`, the other nests `s` in `t`: a membership cycle.

## The branches

- ours adds the member line `t` to block `s`.
- theirs adds the member line `s` to block `t`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each side nests one subgraph in the other one way only, so following holders never returns; no id has two holders. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 7, theirs after line 11. Clean.

## The verdict

`s` holds `t` and `t` holds `s`: following holders from either returns to it. `membership-cycle`, reported with a subgraph on the cycle, so either `s` or `t`. Each is named by one member line, so it is not `member-twice`.

> Nesting has no cycle. Following holders from a subgraph never returns to it. A cycle is refused as `membership-cycle`; a member line naming its own block's subgraph is a cycle of one.
>
> SPEC.md §6

> `membership-cycle`: a subgraph on the cycle;
>
> SPEC.md §9

Expected: `{"merge": "clean", "refusal": ["membership-cycle"], "ids": {"membership-cycle": ["s", "t"]}}`
