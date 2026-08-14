# Coupled-drift decision matrix

| Model | Code choice timing | Source path timing | Solved here? |
|---|---|---|---|
| Static | One code before the path | After code choice | Yes |
| Open-loop sequence | Entire sequence before the path | After sequence choice | Yes |
| Full-state feedback | Each code after observing current law | Interleaved | No |
| Partial observation | Each code from a declared filtration | Interleaved | No |
| Clairvoyant oracle | Code after seeing future path | Before each cost | Benchmark only |

The rows are different games. Results may not be moved between rows without a new proof.