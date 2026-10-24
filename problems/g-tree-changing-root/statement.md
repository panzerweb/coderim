# G-Tree: Ancestors with a Changing Root

You are given a tree with nodes numbered `1` through `N`. Initially node `1` is the root. Process changes to the logical root and ancestor queries.

A node `U` is an ancestor of `V` when `U` lies on the path from the **current root** to `V`. Every node is considered an ancestor of itself.

## Operations

- `ROOT R`: make node `R` the current root for all subsequent queries.
- `QUERY U V`: print `YES` if `U` is an ancestor of `V` under the current root, otherwise print `NO`.

Changing the root does not change any edge, add a node, or move a subtree. Only the direction of ancestry changes. Repeating a root change is allowed.

## Input format

1. Read `N`.
2. Read exactly `N−1` lines containing `P C`: node `P` is the parent of node `C` **in the initial tree rooted at 1**. These lines can appear in any order.
3. Read `Q`.
4. Read exactly `Q` operations, one per line, in either format above.

The input is guaranteed to describe one connected, acyclic tree with no duplicate edges. Each non-root node has exactly one initial parent. All node labels are valid. When `N = 1`, there are no edge lines.

## Output format

Print `YES` or `NO` on a separate line for each `QUERY`, preserving operation order. Print nothing for `ROOT`. If there are no queries, the output is empty.

## Constraints

| Parameter | Constraint |
| --- | --- |
| Nodes / operations | `1 ≤ N,Q ≤ 100,000` |
| Node labels | `1 ≤ U,V,R,P,C ≤ N` |
| Initial root | `1` |
| Execution time | 5 seconds per official input, provisional |
| Memory target | 256 MB; unenforced by the local runner |
| Suggested practice duration | 60 minutes, provisional Hard level for DSA students |

Trees may be chains of 100,000 nodes. Ensure your program can handle that depth in its chosen language. Executable samples and explanations follow below.
