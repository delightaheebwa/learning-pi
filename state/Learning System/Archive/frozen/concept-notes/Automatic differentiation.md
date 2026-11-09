# Automatic Differentiation

> **Status:** mastered | **Domain:** ML Math / Computational Differentiation
> **Prerequisites:** Derivative, Chain rule (matrix form), Jacobian, Backpropagation

## Definition

Automatic differentiation (AD) computes **exact derivatives** of functions expressed as computer programs by applying the **chain rule to elementary operations**. It works at the level of primitive operations (+, ×, sin, exp, etc.) and propagates derivatives through the computation graph.

## Forward Mode

- Propagates **tangents** from inputs → outputs
- Computes a **Jacobian-vector product (JVP)**: \( J_f(x) \cdot v \)
- Efficient when: outputs > inputs (the function has few parameters, many outputs)
- One forward pass = one column of the Jacobian
- Mechanistic reason it works in one pass: chain rule direction (inputs → outputs) matches computation direction

## Reverse Mode

- Runs a forward pass to store intermediates, then propagates **gradients** from outputs → inputs
- Computes a **vector-Jacobian product (VJP)**: \( v^{\top} \cdot J_f(x) \)
- Efficient when: inputs > outputs (many parameters, scalar loss)
- One backward pass = all parameter gradients
- This is what backpropagation uses

## How to Choose

| Scenario | Mode | Reason |
|----------|------|--------|
| Neural network training (many params → scalar loss) | Reverse | One backward pass gets all gradients |
| GAN generator update (many params → scalar loss) | Reverse | Same reason |
| Sensitivity analysis (scalar param → many outputs) | Forward | One pass gets all sensitivities |
| Computing a specific directional derivative | Forward | JVP = directional derivative |

## Common Mistakes

- Confusing JVP (forward mode) with VJP (reverse mode)
- Thinking forward mode is always slower — it's faster for few-inputs-many-outputs
- Describing reverse mode as "more efficient" without specifying the input/output ratio condition

## Related Concepts

- [[Backpropagation]] — reverse mode AD applied to neural networks
- [[Jacobian-vector product]] — what forward mode computes
- [[Derivative]] — the underlying operation
- [[Gradient]] — reverse mode of a scalar function with respect to all inputs
