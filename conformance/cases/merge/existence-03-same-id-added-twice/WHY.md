# existence-03-same-id-added-twice

Two branches each declare a new node `q`, in different places: two node statements for one id.

From existence case `03-same-id-added-twice` (`existence/cases/03-same-id-added-twice/`). The existence case declared `q` inside an edge on each side; here each side declares `q` by a node statement and adds an edge naming it.

## The branches

- ours declares `q[Queue]` after `api[API]` and adds `api --> q` after `user --> api`.
- theirs declares `q[Quota]` after `worker[Worker]` and adds `auth --> q` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each side declares `q` once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after lines 3 and 8, theirs after lines 6 and 11: four separate insertions, none at the same place. Clean.

## The verdict

The merged file holds `q[Queue]` and `q[Quota]`, two node statements for `q`: `duplicate-declaration` for `q`. The edges naming `q` name a declared node, and `q` has one kind, so nothing else applies.

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.
>
> SPEC.md §5.1

Expected: `{"merge": "clean", "refusal": ["duplicate-declaration"], "ids": {"duplicate-declaration": ["q"]}}`
