# Coupled-drift glossary

**Admissible path**  
A sequence of probability laws satisfying the initial condition, simplex
constraints, and every declared consecutive-TV bound.

**Canonical event family**  
One nonempty subset excluding the final state from each event/complement pair,
used to encode finite TV exactly.

**Coupled value**  
The optimum over one jointly admissible source-law path.

**Marginal relaxation**  
The sum of independently optimized expanding-ball support functions. It is an
upper bound on the coupled value.

**Compatibility gap**  
The marginal relaxation minus the coupled value.

**Common cost ordering**  
A sufficient condition under which every period ranks all source states in the
same weak order and one nested TV transport path attains every marginal optimum.

**Precommitted sequence**  
A full sequence of codebooks chosen before the source path is selected.

**Adaptive policy**  
A mapping from a declared observation history to future code choices. The
current lane does not implement this.

**Switching penalty**  
An explicit rational decision-model charge for changing the source-state length
vector between periods.

**Static baseline**  
The best sequence that uses one codebook at every period.

**Primal receipt**  
The complete bounded path geometry, maximizing path vertex, and exact objective.

**Dual receipt**  
Nonnegative exact rational multipliers satisfying the transpose equation,
matching objective, and complementary slackness.

**Fail closed**  
Raise rather than return a partial optimum when a declared enumeration cap is
exceeded.
