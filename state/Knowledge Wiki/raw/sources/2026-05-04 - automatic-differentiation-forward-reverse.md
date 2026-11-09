# Source: Automatic differentiation forward and reverse passes

Captured from user-provided notes about automatic differentiation.

## Raw text

Automatic differentiation is basically the chain rule applied forward (left-to-right, computing and collecting partials for intermediates on the fly) or reverse (forward pass for intermediates, then backward pass right-to-left to compute and accumulate those partials)—all by breaking your program into basic ops. Breaking the program into simple ops (add, mul, etc.) allows exact, local derivative rules to chain together without symbolic manipulation or approximations. This scales to deep neural nets where manual derivatives would be intractable.

## Extracted notes

- Automatic differentiation applies the chain rule to a program built from basic ops.
- Forward mode computes partials left-to-right as intermediates are created.
- Reverse mode does a forward pass to record intermediates, then a backward pass to accumulate gradients right-to-left.
- Decomposing a program into basic ops lets exact local derivative rules compose cleanly.
- AD avoids symbolic differentiation and numerical approximations.
- It is practical for deep neural networks where manual derivatives are too hard to write by hand.

## Open questions

- None from the source.
