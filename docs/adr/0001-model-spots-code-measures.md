# The model spots, code measures

A Partner must be able to trust every number in an Answer without redoing the analysis, and a ~1B model writing its own numbers will often get them wrong. So the time-series model only decides what is worth saying (which period stands out, where the trend breaks, which component looks unusual); code computes every figure and its Calculation path; the model then phrases the Answer around those figures, and a final Check runs before the Partner sees anything.

## Considered Options

- **Model calculates, code only checks afterwards.** Rejected for the product: the Check would have to fix frequent mistakes and rebuild Calculation paths after the fact. It is still what the hackathon evaluation measures, because it shows how well the model reads series unaided.
- **Code does everything, a text model only routes and phrases.** Rejected: the most reliable option, but it needs no time-series model, which removes the project's technical contribution.

## Consequences

The justification for a time-series model rests on spotting, not arithmetic. If a text-only model given the same series as text spots equally well, this design loses its reason to use OpenTSLM. That comparison is therefore the key baseline.
