# class-redefined-vs-assigned-accepted

§11: one branch redefines class `hot`, the other gives `hot` to another node; the new assignment gets the new style.

## The branches

- ours changes `classDef hot` from `fill:#f00` to `fill:#f80`.
- theirs appends `class b hot`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: one `classDef` for `hot`; `class` lines last, each classing one node once. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes line 5; theirs appends after line 6. Clean.

## The verdict

`hot` is declared once; `a` and `b` are each classed once; the `class` lines are last. Accepted.

> A class redefined on one branch while the other assigns it: the assignment gets the new style.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
