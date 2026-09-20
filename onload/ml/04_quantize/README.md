Lesson 04 - Quantization

~45 min. Floats in, int8 out, and three silent traps.

Open quantize.py, fill in the STEPs.

    pixi run ml-test 04_quantize
    pixi run ml-solution 04_quantize

Reference notes

Power-of-two scale - multiply by 2^k to quantize, divide by 2^k to get back.
In hardware, dividing by 2^k is dropping k wires. That is why the numeric
contract allows shifts and nothing else.

astype wraps - np.array([200.0]).astype(np.int8) is -56. Clip first, always.
Same bug as hardware lesson 01's saturate-don't-wrap, different language.

np.round rounds halves to even - 0.5, 1.5, 2.5, 3.5 become 0, 2, 2, 4. Our
rule is half away from zero. Whichever rule you pick, the training export and
the golden model must use the same one, or a handful of weights come out one
step different and nothing ever tells you.

>> floors - -3 >> 1 is -2, not -1. The RTL shifts, so the golden model shifts.

Break it on purpose

1. Swap your rounding for np.round. Exactly one test fails. Would the
   round-trip error test have caught it?

2. Remove the clip. What does 10.0 at shift 4 come out as?

Next: Lesson 05 wires quantized weights into a full integer forward pass.
