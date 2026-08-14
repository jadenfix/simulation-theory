# Finite multicast network coding for predictive classes

## Scope

The repository already proves an exact single-sink statement: once a hidden
history is reduced to its exact predictive-equivalence class, a source-to-sink
network can carry the class label exactly when the declared single-sink cut has
enough capacity.

Several sinks change the problem. Separate source-to-sink min-cuts are always
necessary, but ordinary packet routing may still force incompatible uses of a
shared bottleneck. Intermediate nodes can sometimes resolve that conflict by
sending functions of packets rather than forwarding one packet unchanged.

This note develops a bounded finite-field model from first principles. It does
not invoke a general multicast theorem as a black box. It proves the local
linear algebra used by the checker, derives the per-sink cut necessity, gives an
analytic butterfly-network separation, and independently exhausts all bounded
binary scalar assignments.

The result concerns a declared directed acyclic unit-capacity network and exact
zero-error multicast. It is not evidence that reality is simulated, and a field
symbol or edge-capacity unit is not a claim about parent-universe hardware,
energy, mass, spacetime, or signaling law.

---

## 1. Why the single-sink theorem does not automatically multicast

Let one source hold a message and let two sinks each require that same message.
Suppose every sink individually has source min-cut at least the message size.
This proves only that no single sink is separated from the source by an
undersized cut.

It does **not** provide two simultaneously compatible routing plans. Paths that
work for one sink may consume a shared edge in a way that prevents another
sink's route. Per-sink max flows are optimized separately; a multicast protocol
must choose one set of edge contents that works for every sink at once.

This distinction is crucial for predictive rendering across several causal
regions. The statement

\[
\operatorname{mincut}(s,t_j)\ge h
\qquad\forall j
\]

is a family of necessary receiver-side constraints. It is not, by itself, a
constructive simultaneous protocol in the routing-only model.

---

## 2. Unit-capacity finite-field model

Let

\[
G=(V,E)
\]

be a finite directed acyclic graph. Every edge carries one symbol from the prime
field

\[
\mathbb F_p.
\]

The source holds

\[
x=(x_1,\ldots,x_h)\in\mathbb F_p^h.
\]

A **scalar linear network code** assigns each edge a global encoding vector

\[
g_e\in\mathbb F_p^h
\]

and transmits

\[
y_e=g_e^\top x.
\]

At the source, an outgoing global vector may be any vector in
\(\mathbb F_p^h\). At a non-source node \(v\), an outgoing edge \(e\) must be a
linear combination of the incoming edge symbols. Equivalently, if
\(\operatorname{In}(v)\) is the ordered incoming-edge set, there are local
coefficients

\[
\alpha_{e,f}\in\mathbb F_p
\]

such that

\[
y_e
=
\sum_{f\in\operatorname{In}(v)}
\alpha_{e,f}y_f.
\]

Substituting \(y_f=g_f^\top x\) gives

\[
y_e
=
\left(
\sum_{f\in\operatorname{In}(v)}
\alpha_{e,f}g_f
\right)^\top x,
\]

so

\[
\boxed{
 g_e
=
\sum_{f\in\operatorname{In}(v)}
\alpha_{e,f}g_f.
}
\]

Because the graph is acyclic, global vectors can be propagated once in a
topological order. No fixed-point or simultaneous-equation ambiguity remains.

The implementation expands an integer-capacity edge into parallel named unit
edges. This keeps the algebra scalar and makes every finite edge assignment
auditable.

---

## 3. Sink rank criterion

Let sink \(t\) receive edges

\[
e_1,\ldots,e_r
\]

with global vectors

\[
g_{e_1},\ldots,g_{e_r}.
\]

Its received symbol vector is

\[
y_t
=
G_t x,
\]

where the rows of \(G_t\) are the incoming global vectors.

### Sufficiency

If

\[
\operatorname{rank}_{\mathbb F_p}(G_t)=h,
\]

then the incoming vectors span \(\mathbb F_p^h\). For each coordinate basis
vector \(e_i\), there are decoder coefficients \(d_i\in\mathbb F_p^r\) such
that

\[
\sum_{j=1}^r d_{ij}g_{e_j}=e_i.
\]

Applying the same coefficients to received symbols gives

\[
\sum_{j=1}^r d_{ij}y_{e_j}
=
\left(
\sum_{j=1}^r d_{ij}g_{e_j}
\right)^\top x
=
e_i^\top x
=x_i.
\]

Thus every source coordinate is recovered exactly.

### Necessity

If the incoming rank is less than \(h\), there exists a nonzero vector

\[
z\in\ker G_t.
\]

For every source state \(x\), the two distinct source states \(x\) and
\(x+z\) produce the same received vector:

\[
G_t(x+z)=G_tx+G_tz=G_tx.
\]

No decoder can distinguish those two source messages, so exact recovery is
impossible.

Therefore:

\[
\boxed{
 t\text{ recovers all }h\text{ symbols exactly}
\iff
\operatorname{rank}_{\mathbb F_p}(G_t)=h.
}
\]

The checker does more than report rank. It solves for one decoder coefficient
vector per source coordinate and verifies every basis-recovery equation exactly
modulo \(p\).

---

## 4. Per-sink cut necessity

Fix a sink \(t\) and any directed cut \((S,V\setminus S)\) with

\[
s\in S,
\qquad
t\notin S.
\]

Let \(C\) be the unit edges crossing from \(S\) to \(V\setminus S\). Every
symbol observed downstream of the cut is a deterministic linear function of the
symbols on \(C\). Hence every downstream global vector lies in

\[
\operatorname{span}\{g_e:e\in C\}.
\]

That span has dimension at most \(|C|\). If the sink recovers an
\(h\)-dimensional source, its incoming span has dimension \(h\), so

\[
h\le |C|.
\]

Because the argument applies to every source-sink cut,

\[
\boxed{
\operatorname{mincut}(s,t)\ge h
}
\]

is necessary for exact scalar linear recovery.

For several sinks,

\[
\boxed{
\operatorname{mincut}(s,t_j)\ge h
\qquad\forall j
}
\]

is necessary. This repository does not silently promote that receiver-wise
condition into a general routing or linear-coding sufficiency theorem. Instead,
it constructs and verifies explicit finite codes.

---

## 5. Routing-only submodel

A routing-only scalar protocol is the restricted case in which an outgoing edge
carries either:

- no source symbol; or
- one unchanged source basis packet at the source; or
- one unchanged packet already present on an incoming edge at an intermediate
  node.

It cannot form a nontrivial sum such as

\[
x_1+x_2.
\]

This is a deliberately strict finite model of copy-and-forward packet routing.
Over \(\mathbb F_2\), nonzero scalar rescaling adds no extra operation, so the
model exactly captures the bounded butterfly comparison below.

The code search enumerates every scalar linear local-coefficient assignment and
then filters the valid multicast certificates by this routing predicate. A
search that hits its configured cap reports **incomplete**, not impossible. An
impossibility receipt is produced only after the entire bounded assignment
space has been exhausted.

---

## 6. The declared butterfly network

The finite network has source \(s\), intermediate nodes \(a,b,c,d\), and sinks
\(t_1,t_2\). Its unit edges are

\[
\begin{aligned}
s&\to a,& s&\to b,\\
a&\to t_1,& a&\to c,\\
b&\to t_2,& b&\to c,\\
c&\to d,\\
d&\to t_1,& d&\to t_2.
\end{aligned}
\]

The edge \(c\to d\) is the shared bottleneck.

Both sinks have source min-cut two:

\[
\boxed{
\operatorname{mincut}(s,t_1)
=
\operatorname{mincut}(s,t_2)
=2.
}
\]

So every per-sink cut can carry two binary field symbols. The unresolved
question is whether one simultaneous routing assignment can satisfy both.

---

## 7. Analytic routing impossibility on the butterfly

Let the two source packets be \(x_1,x_2\).

Node \(a\) receives only the packet on \(s\to a\). Therefore both
\(a\to t_1\) and \(a\to c\) can only copy that same packet or send zero.
Similarly, node \(b\)'s outgoing edges can only copy the packet on
\(s\to b\) or send zero.

For either sink to recover two independent packets, the source packets sent to
\(a\) and \(b\) must be distinct. Relabeling coordinates if necessary, take

\[
s\to a:x_1,
\qquad
s\to b:x_2.
\]

Sink \(t_1\) receives a direct packet from \(a\). To have rank two, its other
packet, delivered through \(d\to t_1\), must be \(x_2\). Thus the shared
bottleneck must carry \(x_2\).

Sink \(t_2\) receives a direct packet from \(b\). To have rank two, its other
packet, delivered through \(d\to t_2\), must be \(x_1\). Thus the same shared
bottleneck must carry \(x_1\).

One unit edge cannot simultaneously carry both distinct packets in the
routing-only model. Therefore:

\[
\boxed{
\text{No exact two-symbol routing-only multicast exists on this butterfly.}
}
\]

This proof is topology- and interface-specific. It does not say routing is
always inferior to coding.

---

## 8. Binary linear code on the butterfly

Work over \(\mathbb F_2\). Send

\[
s\to a:x_1,
\qquad
s\to b:x_2.
\]

Nodes \(a\) and \(b\) forward their packets both directly and toward \(c\):

\[
a\to t_1:x_1,
\qquad
a\to c:x_1,
\]

\[
b\to t_2:x_2,
\qquad
b\to c:x_2.
\]

Node \(c\) sends the sum through the bottleneck:

\[
\boxed{
c\to d:x_1+x_2.}
\]

Node \(d\) copies that coded packet to both sinks.

Sink \(t_1\) receives

\[
x_1,
\qquad
x_1+x_2,
\]

and recovers

\[
x_2=x_1+(x_1+x_2).
\]

Sink \(t_2\) receives

\[
x_2,
\qquad
x_1+x_2,
\]

and recovers

\[
x_1=x_2+(x_1+x_2).
\]

Each sink's two incoming global vectors have rank two. Hence:

\[
\boxed{
\text{The declared butterfly multicasts two symbols exactly over }\mathbb F_2.
}
\]

The same bottleneck symbol is useful to both sinks because each has different
side information.

---

## 9. Exhaustive finite certificate

For the binary two-symbol butterfly model, the local coefficient domain contains
exactly

\[
2^{12}=4096
\]

assignments:

- four binary source coefficients across its two outgoing edges;
- two local coefficient bits at \(a\);
- two at \(b\);
- two at \(c\);
- two at \(d\).

The bounded checker evaluates every assignment by:

1. propagating every global vector in topological order;
2. computing each sink's incoming rank;
3. solving and verifying decoder equations when rank is full;
4. classifying whether the assignment is routing-only;
5. retaining an explicit valid linear certificate if one exists.

The complete search finds valid linear codes and finds no valid routing-only
assignment after all 4096 cases are examined.

This exhaustive result is an independent finite check, not the logical basis of
the analytic routing proof. Conversely, the analytic proof is not inferred from
one successful CI run.

---

## 10. Predictive-class multicast bridge

Let a finite future-query family have hidden records \(r\in\mathcal R\) and
exact predictive signatures

\[
\sigma(r)
=
\left(f_q(r)\right)_{q\in\mathcal Q}.
\]

Records are exactly predictively equivalent when their signatures agree. Let

\[
K
=
|\{\sigma(r):r\in\mathcal R\}|.
\]

Choose a prime field and source dimension satisfying

\[
K\le p^h.
\]

Then there is an injection

\[
\iota:
\{\text{predictive classes}\}
\hookrightarrow
\mathbb F_p^h.
\]

Encode the class of record \(r\) as

\[
x(r)=\iota([r]).
\]

If a multicast code lets every sink recover \(x(r)\), every sink can recover the
predictive-class label. It can then answer every allowed future query using the
class signature, because all records inside one class have identical answers.

Thus:

\[
\boxed{
K\le p^h
\quad\text{and exact }h\text{-symbol multicast}
\implies
\text{exact multicast of the predictive class.}
}
\]

For all coordinate queries on two hidden bits,

\[
K=4=2^2.
\]

The butterfly binary code therefore multicasts the exact two-bit predictive
class to both sinks.

The field-vector label is arbitrary. It need not be numerically identical to
the original record tuple. The invariant is:

\[
[r]=[u]
\iff
x(r)=x(u),
\]

with distinct predictive classes assigned distinct vectors.

---

## 11. What this changes in the rendering argument

A single-sink renderer can often think in terms of one sufficient-state label
and one source-to-observer cut. Multiple future observers introduce a different
question:

> Can one shared set of internal messages make every observer's later query law
> consistent simultaneously?

The butterfly example exposes three possibilities that informal arguments often
collapse:

1. **Per-sink impossibility:** some receiver has an undersized cut.
2. **Routing conflict:** every receiver has enough cut capacity separately, but
   copy-and-forward packets cannot satisfy all receivers at once.
3. **Coding resolution:** an intermediate relation such as \(x_1+x_2\) lets
   different receivers combine the shared bottleneck with different local side
   information.

This is relevant to any proposed distributed on-demand architecture. Counting
independent point-to-point capacities is not enough; one must specify whether
shared internal links can carry coded functions, what side information each
region has, and whether every sink needs the same predictive class or different
functions of it.

The result does **not** make network coding evidence for simulation. Ordinary
distributed systems and ordinary physical theories obey the same information
constraints.

---

## 12. Computational objects

The implementation provides:

- exact Gaussian elimination over prime fields;
- exact linear-system solving over \(\mathbb F_p\);
- named unit-capacity DAGs;
- integer-capacity to parallel-unit-edge expansion;
- local-coefficient validation;
- topological global-vector propagation;
- exact sink-rank and decoder certificates;
- routing-only classification;
- bounded exhaustive scalar-code search;
- explicit search-completeness versus search-cap reporting;
- source-sink min-cut checks through the existing exact flow engine;
- an explicit binary butterfly code;
- an analytic-plus-exhaustive butterfly separation certificate;
- predictive-class embedding into finite-field source vectors.

The test suite validates every source basis decoder equation and checks the
finite predictive-class injection. It also guards against a subtle category
mistake: a field-vector naming convention is not part of the predictive theorem.
Only class-preserving injectivity matters.

---

## Primary context

The broader multicast-network-coding program was introduced in:

- Rudolf Ahlswede, Ning Cai, Shuo-Yen Robert Li, and Raymond W. Yeung,
  **Network Information Flow** (2000), DOI `10.1109/18.850663`.
- Shuo-Yen Robert Li, Raymond W. Yeung, and Ning Cai,
  **Linear Network Coding** (2003), DOI `10.1109/TIT.2002.807285`.

Those papers motivate the larger research direction. The repository's current
claims remain the smaller finite theorems and certificates proved here; it does
not inherit every general result merely by citation.

---

## Nonclaims

- The module does not prove the general multicast max-flow/min-cut theorem.
- Per-sink min-cut adequacy is claimed as necessary, not routing sufficiency.
- The butterfly routing impossibility concerns the declared copy-and-forward
  scalar model.
- The successful code is scalar, linear, exact, binary, one-source, and
  acyclic; nonlinear, vector, cyclic, delayed, noisy, or interactive models are
  different problems.
- A bounded exhaustive search is an impossibility certificate only after its
  declared finite assignment space is exhausted.
- The field size and source dimension are model resources, not parent-universe
  material costs.
- Multicasting a predictive-class label does not mean multicasting a complete
  microscopic state.
- The same class label at every sink is a common-demand multicast problem;
  different sink functions require a new analysis.
- Network coding is not evidence for simulation.

---

## Next research targets

1. Prove and implement the general finite-field multicast construction for
   bounded DAGs rather than relying only on exhaustive search.
2. Determine field-size requirements and provide exact failure certificates for
   small fields.
3. Extend the predictive bridge from exact classes to approximate stochastic
   covers and packings.
4. Add sink-specific predictive functions and distinguish multicast from
   multiple-unicast and function-computation problems.
5. Add noisy channels and separate source coding, channel coding, and network
   coding assumptions.
6. Track delay and block length so vector codes cannot be confused with scalar
   edge capacity.
7. Add adversarial edge failures and robust coding certificates.
8. Integrate progressive query revelation so side information can arrive at
   different causal stages.
