# Organizer notes — provisional Hard / 60 minutes

The original static streak problem is a linear scan. This variant adds persistent point updates and arbitrary range queries. Use an ordered segment summary: length, first/last temperature, increasing prefix/suffix lengths, and best streak.

Join adjacent summaries only when the left endpoint's final temperature is strictly smaller than the right endpoint's first temperature. Extend a prefix only if the entire left segment is increasing; extend a suffix symmetrically. The best result is the best child or the crossing suffix+prefix. Empty summaries are identities. The merge is associative but not commutative; an iterative query needs left and right accumulators in the correct order.

Build O(N), each operation O(log N), auxiliary space O(N) per test case. Across test cases time is O(sum(N + Q log N)). The Python reference streams operation lines and output; languages that retain the entire input need to include that storage in total program space.

Run `python problems/longest-rising-streak-updates/author/generate_tests.py`, then validate and verify the package. Fixed seed 2401. Tests include an independent scan oracle on small randomized inputs, boundary joins, equality, resets between test cases, and maximum-scale inputs designed to defeat per-query scans. Expected outputs are saved; author code is never executed by participant judging.

The 5-second limit and 60-minute duration are provisional. Use the authoring benchmark tool on the event machine and pilot with representative students before claiming calibrated difficulty. Efficient alternative approaches remain valid.
