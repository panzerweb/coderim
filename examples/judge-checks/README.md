# Judge-check programs

Copy the entire file into the app, select its language, and click **Submit** to run all 65 official cases. Java programs must keep the class name `Main`.

| Variant | Official cases passed | Visible samples passed |
| --- | ---: | ---: |
| pass-1 | 1 / 65 | 1 / 6 (sample 1) |
| pass-3 | 3 / 65 | 3 / 6 (samples 1, 2, 6) |
| pass-all | 65 / 65 | 6 / 6 |

The first two variants are deliberately limited demonstration fixtures that recognize selected public samples. They print `NOT_IMPLEMENTED` on other inputs so those cases reliably receive Wrong Answer, including cases expecting INVALID. They are not general solutions.

The full solutions use a bracket stack and quote/escape state, with O(L) time and O(L) worst-case memory. All nine programs have been verified through the project's actual judge. These exact counts apply to problem version 1; changing the official suite may change the counts.

Run `python tools/verify_demo_solutions.py` to recheck installed languages. Verification uses temporary runtime directories and does not create submission history.
