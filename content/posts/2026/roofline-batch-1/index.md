---
title: "The Batch=1 Roofline: Dense vs. MoE, and Why You Land at 60%"
date: 2026-10-23
slug: "roofline-batch-1"
description: "Decode at batch=1 is a streaming problem and the roofline is one division. Dense and MoE models differ in what streams; a measured gpt-oss-20b case shows where the other 40% goes."
draft: true
---

I recently ported gpt-oss-20b to a small inference engine I maintain and
spent some time profiling single-stream decode on my home GPU, an
RTX 5090. The engine generates at about 385 tokens/s. A back-of-envelope
roofline says the hardware should allow about 637. This post is the
accounting of that difference — but the accounting only makes sense once
the model is stated precisely, because "the roofline" for a dense model
and for a mixture-of-experts model are different statements about
different byte streams.

## The roofline is one division

Autoregressive decode at batch=1 has a peculiar property: every weight
is read from HBM once per generated token and participates in roughly
one multiply-add. Arithmetic intensity is therefore pinned near
2 FLOP/byte no matter how large the model is, and the step time has a
hard floor:

```
step time  ≥  (bytes streamed per token) / (memory bandwidth)
```

Everything else — tensor cores, clock rates, kernel cleverness — is
secondary until that floor is approached. On the RTX 5090 the spec
bandwidth is 1.79 TB/s (512-bit GDDR7 at 28 Gbps). I use a *measured*
denominator instead: a pure streaming read on this card reaches
1.69 TB/s (a reduction over a 2 GiB buffer; a device-to-device copy
reaches 1.53, a triad 1.58). Spec peak is a ceiling on the measurement,
not a rate any real stream sustains — GDDR refresh and protocol
overhead cap pure reads at about 94–95% of it.

{{< figure src="fig-roofline.svg" width="760" height="470" alt="Log-log roofline chart for the RTX 5090: a bandwidth slope at 1.69 TB/s rising to a BF16 ceiling near 838 TFLOP/s, with dense and MoE decode points at arithmetic intensity 2 to 3 and the achieved MoE point below the line" caption="Figure 1 — Both decode points sit at intensity ≈2–3, two decades left of the ridge. On this part of the chart there is no compute story to tell." >}}

## Dense models: everything streams, every token

For a dense transformer the numerator is simply the model: each token
streams every parameter once. A 21B-parameter model stored in FP8
moves about 20.9 GB per token, so the floor is

```
20.9 GB / 1.69 TB/s ≈ 12.4 ms/token   →   at most ≈81 tok/s
```

regardless of how good the kernels are. The only levers are fewer bytes
(quantization) or more bandwidth. This is why batch=1 dense decode
numbers look so modest next to batched serving numbers: batching
amortizes the same byte stream over many tokens and walks the operating
point right, toward the ridge. Batch=1 cannot.

## MoE models: only the selected experts stream

A mixture-of-experts layer changes the numerator. The shared parts of
the network — attention projections, routers, embeddings, the output
head — still stream in full every token. But of the expert weights,
only the ones the router selects are read. In gpt-oss-20b (24 layers,
32 experts per layer, top-4 routing), with experts stored in MXFP4 and
the shared parts in FP8, the per-token traffic in my engine is:

{{< figure src="fig-traffic.svg" width="760" height="344" alt="Two-panel bar chart of bytes streamed per token: a dense 21B FP8 model moves about 20.9 GB per token, while the MoE model moves 2.65 GB, composed of 1.32 GB active experts, 0.65 GB dense FP8, 0.60 GB lm_head and 0.08 GB KV and misc" caption="Figure 2 — Same scale on top; the MoE numerator zoomed below. (The dense bar is an arithmetic comparison, not a second measurement.)" >}}

The full weight pool resident in memory is 14.18 GiB, but only 2.65 GB
of it streams per token at short context. The floor is correspondingly
lower:

```
2.65 GB / 1.69 TB/s ≈ 1.57 ms/token   →   at most ≈637 tok/s
```

Two caveats keep this honest. First, the 2.65 GB is not a law of
nature: it depends on the storage formats (MXFP4 experts, FP8 dense)
and on routing (top-4 of 32). Second, the KV term grows with context;
at long context it stops being a rounding error. Neither caveat changes
the structure — MoE buys its batch=1 speed by shrinking the numerator,
not by touching the denominator.

## The measured step, and where the other 40% goes

The measured step is 2.596 ms — 385 tok/s, or about 60% of the
roofline. Profiling the step kernel by kernel (torch profiler for the
decomposition, Nsight Compute for the per-kernel counters) attributes
the entire gap to three terms. There is no unexplained residue beyond
estimation noise:

{{< figure src="fig-waterfall.svg" width="760" height="384" alt="Waterfall chart from the 1.57 ms roofline to the measured 2.596 ms step: plus 0.50 ms expert GEMV, plus 0.30 ms attention, plus 0.20 ms dense GEMV slack and kernel boundaries" caption="Figure 3 — The account closes: 1.57 + 0.50 + 0.30 + 0.20 ≈ 2.596 ms." >}}

### Term 1: the expert GEMV streams below copy speed (+0.50 ms)

The grouped expert GEMV is the largest single item in the step
(about 1.0 ms of it). Fitting its launch times against bytes moved
gives a two-parameter model:

```
launch time ≈ bytes / 1.41 TB/s + 2.3 µs,     72 launches per step
```

Both parameters cost real time. The marginal rate, 1.41 rather than
1.66 TB/s, is not a memory-system limit: Nsight Compute shows DRAM
utilization near 53% and occupancy near 63% (a register cap admits
5 blocks per SM). The gap is work per byte — every 128-byte line of
MXFP4 weights also needs address computation from the expert table,
4-bit unpacking, scale multiplication, and the FMA chain, and those
instructions share the SM issue slots with the loads. A pure copy has
no such tax. The control experiment exists inside the same step: the
`lm_head` GEMV, a large clean FP8 stream, runs at 363 µs against a
byte floor of 361 µs — it *is* at the roofline, at 1.66 TB/s in situ.
Big clean streams reach the rate; the expert stream, with its dequant
tax and grouped indexing, does not.

The 2.3 µs fixed term is per-launch ramp — index rebuild, first-touch
latency, tail drain — not host launch cost (the step runs as a captured
CUDA graph). It punishes small launches disproportionately, which
matters again in term 3.

{{< figure src="fig-launch.svg" width="760" height="360" alt="Cumulative bytes versus time for one representative 18.3 MB expert GEMV launch: the actual launch waits out a fixed 2.3 microseconds, then climbs at 1.41 TB/s, finishing about 4.3 microseconds behind an ideal launch that streams at 1.66 TB/s from time zero" caption="Figure 4 — One launch, taken apart. Offset first, slope second; both are visible at this scale." >}}

I tried to buy this term back three ways. Deepening memory-level
parallelism in the GEMV (cp.async double buffering, register prefetch)
was bit-exact but 5–18% *slower* — the baseline already hides the
latency it can hide, and the extra instructions pay the same issue
tax. Fusing launches conserves the total block count, and with it the
total ramp. Splitting K across blocks (Stream-K style) would change
the term, but it re-parenthesizes the FP32 reduction and breaks
bit-exactness against the reference implementation, which in this
engine is a hard gate, not a preference.

### Term 2: attention is a latency chain, not a byte stream (+0.30 ms)

Attention's byte count is trivial — well under 1 MB of KV per layer
at context 370, worth under 0.5 µs of streaming per layer. It nevertheless
costs about 13 µs per layer (318 µs per step). The time is a serial
dependency chain: with the KV range split into a fixed set of
8 partitions, each partition walks its ≈46 positions in order, and each
position's online-softmax update depends on the previous one — score,
running max, exponential, rescale, accumulate. Backing the chain out of
the measurement gives ≈290 ns of dependent latency per position.
Nsight Compute confirms the diagnosis from the other side: DRAM
utilization ≈4.5%, occupancy ≈25%. The memory system is idle; the
chain is the time.

{{< figure src="fig-chain.svg" width="760" height="318" alt="Staircase diagram of attention partitions: eight fixed split chains each walking about 46 KV positions serially at about 290 ns of dependent latency per step, totalling about 13.3 microseconds per layer, contrasted with the 2 microseconds the same KV bytes would take to stream" caption="Figure 5 — The chain, per layer. More splits would shorten each chain but reorder the softmax merge — again a numerics change." >}}

A tempting idea is to spend the idle bandwidth: prefetch the next
phase's weights during the attention chain. I implemented it (L2
prefetch hints for the output projection, issued from inside the decode
kernel). The consumers did get hot L2 lines — the FP8 GEMVs sped up by
16–22 µs per step. But the host chain slowed by 121–139 µs: the extra
traffic raises load latency on the very chain that is latency-bound.
Net −100 µs per step, in both a bursty and an interleaved variant.
Latency cannot be bought with bandwidth; this experiment is the proof
by construction.

### Term 3: small shapes and kernel boundaries (+0.20 ms)

What remains is spread over the dense FP8 GEMVs and the step's
roughly 170 kernel launches. The small GEMVs (attention projections
and the like) move few bytes per launch, so the fixed ramp of term 1
dominates their time and their effective rate sits well below the big
streams. CUDA graphs remove host-side launch cost, but not the GPU-side
cost of starting and draining ~170 kernels per step.

Could one persistent kernel per layer erase the boundaries? I built it,
in several variants, as an experiment on the MoE block. The ladder of
per-layer times (cold cache) is instructive: a deliberately racy
no-synchronization version — the floor for any fused design — takes
45.5 µs; the production chain of separate kernels takes 49.2 µs; the
best in-kernel synchronization I could build (fine-grained per-chunk
counters in the style of recent megakernel work) takes 50.1 µs;
coarser whole-layer barriers take 55–57 µs. At phase lengths of
2–15 µs, in-kernel synchronization costs more than the kernel
boundaries it replaces. The boundary term is structural at this scale.

## What the roofline leaves out

The exercise generalizes beyond one engine and one GPU:

- **The denominator is a measurement, not a spec.** Using 1.79 instead
  of 1.69 TB/s would have overstated the "inefficiency" by six points.
- **The model assumes one perfect stream.** A real step is ~170 small
  streams, each paying a fixed ramp; the smaller the shape, the larger
  the fraction.
- **Latency-bound phases are invisible to a byte ledger.** Attention
  contributes almost no bytes and 0.30 ms of time. A roofline has
  nothing to say about it — you need the dependency chain, not the
  traffic count.
- **Work per byte taxes the stream.** Dequantization and indexing share
  issue slots with loads; a quantized weight stream does not move at
  copy speed just because its bytes are fewer.

The optimistic reading is that the account *closes*: 1.57 + 0.50 +
0.30 + 0.20 reproduces the measured 2.596 ms with a 0.03 ms residual.
"60% of roofline" in this setting is not a synonym for an unoptimized
implementation; it is the sum of three specific, measured, structural
costs of running at batch=1 under a bit-exactness constraint. The ways
past it are real but they change the problem: batching (amortize the
bytes, give up the latency regime), different numerics (give up
bit-exactness), or a different attention formulation (give up the
fixed-partition merge order). Knowing which of the three terms you are
paying is what tells you which trade you are actually making.
