# Organizer notes — provisional Hard / 60 minutes

Preprocess the original tree rooted at 1 once. An iterative DFS gives subtree intervals and depths; binary lifting gives ancestors at powers of two. Keeping original intervals avoids rebuilding after a logical root change.

For current root r and query (u,v): if u==v or u==r, return YES. If u is not an original ancestor of r, answer the original ancestor test on (u,v). Otherwise find the original child c of u toward r by lifting r by depth[r]-depth[u]-1; u is a current ancestor of v exactly when v is outside c's original subtree.

Preprocessing O(N log N), ROOT O(1), QUERY O(log N) worst case, auxiliary space O(N log N). An iterative traversal is important on deep chains. Input/output buffers and recursion must be included in reviews of total program space. Do not require this particular algorithm if another correct method meets limits.

The original six-node sample was missing a fifth edge. The repaired sample includes `2 5`, then adapts its queries to the new operation syntax, preserving YES/NO/YES.

Run `python problems/g-tree-changing-root/author/generate_tests.py`, then validate and verify. Fixed seed 2402. A brute-force oracle reroots small trees and walks parents for every query; it is independent of the reference's complement rule. Stress inputs alternate distant roots so rebuilding or walking full paths repeatedly times out.

Hard / 60 minutes and the 5-second limit are provisional until piloted with DSA students and calibrated on the intended computer. Benchmark records do not constitute automatic Big-O inference.
