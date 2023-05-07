These are demo scripts to help reproduce the work in my paper:
"Metafunctions for benchmarking in sensitivity analysis", by William Becker (Reliability Engineering and System Safety)

This code is available in the interests of transparency and reproducability. It was written for
specific experiments, rather than for general public release, and does not come with support
or with extensive explanations.

If however someone is interested in working deeply with the code, I might be able to help if you contact me
on william.becker@bluefoxdata.eu (time permitting).

To get started, try running

SAout=metafunction_comparison(5,0);

This will run 5 random sensitivity analyses, comparing 6 methods.

Try changing Nlow/Nhigh and dlow/dhigh in metafunction_comparison.m to change the boundaries of the experiments.

There are many more settings that can be changed.