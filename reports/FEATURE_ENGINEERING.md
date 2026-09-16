# Feature Engineering

Scenario A uses age groups, admission/prior-grade quartiles, payment status, application order, prior qualification, and demographic fields available at admission.

Scenario B adds semester pass/evaluation rates, academic progress = total approved / total enrolled, weighted academic performance = sum(semester grade * approved units) / total approved, grade improvement, engagement, credited ratio, and no-evaluation indicators. Zero denominators return 0; grade zero remains structural.

Qualification codes remain categorical codes; no unsupported ordinal parental-education average is created.
