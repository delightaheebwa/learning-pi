# Source: Automatic differentiation, forward mode, and JVPs

Captured from user-provided notes and screenshots about differentiation methods, forward-mode automatic differentiation, Jacobian-vector products, and why JVPs are practical in large models.

## Raw screenshots

Chronological order:

### Screenshot 01
[[Image 1: ../assets/auto-diff-forward-01.png]]

### Screenshot 02
[[Image 2: ../assets/auto-diff-forward-02.png]]

### Screenshot 03
[[Image 3: ../assets/auto-diff-forward-03.png]]

### Screenshot 04
[[Image 4: ../assets/auto-diff-forward-04.png]]

### Screenshot 05
[[Image 5: ../assets/auto-diff-forward-05.png]]

### Screenshot 06
[[Image 6: ../assets/auto-diff-forward-06.png]]

### Screenshot 07
[[Image 7: ../assets/auto-diff-forward-07.png]]

### Screenshot 08
[[Image 8: ../assets/auto-diff-forward-08.png]]

### Screenshot 09
[[Image 9: ../assets/auto-diff-forward-09.png]]

### Screenshot 10
[[Image 10: ../assets/auto-diff-forward-10.png]]

### Screenshot 11
[[Image 11: ../assets/auto-diff-forward-11.png]]

### Screenshot 12
[[Image 12: ../assets/auto-diff-forward-12.png]]

### Screenshot 13
[[Image 13: ../assets/auto-diff-forward-13.png]]

### Screenshot 14
[[Image 14: ../assets/auto-diff-forward-14.png]]

### Screenshot 15
[[Image 15: ../assets/auto-diff-forward-15.png]]

### Screenshot 16
[[Image 16: ../assets/auto-diff-forward-16.png]]

### Screenshot 17
[[Image 17: ../assets/auto-diff-forward-17.png]]

### Screenshot 18
[[Image 18: ../assets/auto-diff-forward-18.png]]

### Screenshot 19
[[Image 19: ../assets/auto-diff-forward-19.png]]

### Screenshot 20
[[Image 20: ../assets/auto-diff-forward-20.jpeg]]

### Screenshot 21
[[Image 21: ../assets/auto-diff-forward-21.jpeg]]

## Raw text

Differentiation methods include symbolic differentiation (as in SymPy), numerical differentiation via finite differences, and automatic differentiation (AD), which is algorithmic and distinct from both. Symbolic differentiation produces exact analytic expressions but can suffer from expression swell, where applying rules like the product and chain rules creates very large derivative expressions. Numerical differentiation via finite differences is simple but introduces truncation and round-off errors, which become problematic for large models requiring many evaluations. Automatic differentiation instead applies the rules of calculus directly to the elementary operations of a program, computing derivatives to machine precision while avoiding both symbolic expression swell and finite-difference discretization error. In forward-mode AD, each intermediate (primal) value is paired with its derivative (tangent), so the computation proceeds over (primal,tangent) pairs and is efficient when there are few inputs and many outputs. In reverse-mode AD, the forward pass computes and stores intermediate values, and the backward pass propagates adjoints backward, making it ideal for functions with many inputs and few outputs, such as neural networks with millions of parameters and a single scalar loss.

The full Jacobian gives you how the output changes along every coordinate direction in parameter space, so you get all n columns.

But if you only care about one direction r, then computing all columns is overkill: you pay a huge computational and memory cost to get information you are not going to use.

A JVP gives you the effect along that one direction r directly, with no need to materialize the m×n Jacobian, which avoids both the extra compute and the huge storage.

That’s why forward-mode JVPs are attractive whenever the input dimension is large but you only need a few directions—common in big neural nets.

A full Jacobian for f: R^n → R^m is an m×n matrix, so computing and storing it costs O(mn) work and memory.

A JVP J_f(x) r gives just the effect of a single direction r ∈ R^n on the outputs, and forward-mode can compute this in about one forward pass of the function, without ever forming the full matrix.

So the reason JVPs are more practical is not just “we can do the product in one pass”, but:

- We avoid constructing the full Jacobian, which is huge in ML models.
- We get the directional effect we actually care about, like how the loss changes if we tweak parameters in direction r, at a cost similar to one extra evaluation instead of n passes to get all columns.

Forward mode propagates tangents alongside primals, giving derivatives “for free” during a normal function evaluation.

Each forward pass corresponds to one input direction, viewed as one column of the Jacobian.

By choosing an arbitrary direction vector and reinterpreting the problem, you can compute Jacobian-vector products very efficiently, which is crucial in high-dimensional machine learning problems.

A partial derivative along x_1 is just a special case of a directional derivative—the direction that points purely along the x_1 axis.

Forward mode lets you choose any direction vector r in input space (usually normalized), and if you initialize the input tangents as that vector:

- ẋ = r

then a single forward pass computes the directional derivative:

- J_f(x) r

without ever explicitly forming the full Jacobian matrix.

This quantity J_f(x) r is called a Jacobian-vector product (JVP). It’s important because:

- It gives how the output changes when you nudge the input in direction r.
- It costs about as much as one extra function evaluation, instead of building an entire m×n Jacobian.
- For large models, n can be millions, so building the full Jacobian is impossible in practice, but JVPs are cheap and usable.

Between 7:36 and 8:47, the video is explaining what forward-mode automatic differentiation actually does when you run it, and how it relates to Jacobians and directional derivatives.

## Extracted notes

- Symbolic differentiation is exact but can blow up expressions.
- Numerical differentiation is simple but introduces truncation and round-off error.
- Automatic differentiation applies calculus rules directly to the program.
- AD is algorithmic, not symbolic, and not finite differencing.
- Forward mode pairs each primal value with a tangent value.
- Reverse mode stores intermediates during the forward pass, then propagates adjoints backward.
- Reverse mode is ideal when there are many inputs and one scalar output.
- A full Jacobian is expensive to form and store when the input dimension is large.
- A JVP gives the effect of one chosen direction without constructing the full Jacobian.
- JVPs are especially useful in high-dimensional models where only a few directions matter.
- A partial derivative is a special case of a directional derivative.
- Seeding the tangent with a direction vector r makes forward mode compute J_f(x) r.
- Forward-mode JVPs can be thought of as following one column-direction through the computation.

## Open questions

- How would you explain, in your own words, why JVPs are more practical than full Jacobians for high-dimensional models?
- When should you think of a forward-mode computation as “one column of the Jacobian” versus as a directional derivative?
