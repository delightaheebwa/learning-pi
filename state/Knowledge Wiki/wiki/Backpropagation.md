<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Backpropagation | verified-by=fact-check-agent | date=2026-10-26 -->

# Backpropagation

Backpropagation is the standard way to compute gradients in layered neural networks by applying the chain rule efficiently from the output back to earlier layers. It is the reverse-mode form of [[Automatic differentiation]] specialized to layered neural networks.

## The two passes

### Forward pass

- Feed the input through the network one layer at a time.
- Compute each layer’s pre-activation and activation.
- Store intermediate values needed later.
- Compute the final loss at the end.

### Backward pass

- Start from the loss gradient.
- Move backward through the network.
- At each layer, combine the upstream gradient with the layer’s local gradient.
- This gives:
  - the gradient with respect to that layer’s parameters
  - the gradient to send to the previous layer

## Why it is useful

Instead of expanding the full chain rule separately for every parameter, backprop reuses the gradient that has already been accumulated from later layers. Building on the idea of local derivatives, it turns the whole network into a sequence of local computations.

## Related pages

- [[Jacobian matrix]]
- [[Implicit differentiation]]
- [[Total differential]]
- [[Automatic differentiation]]

## Sources
- Wikipedia — Backpropagation: https://en.wikipedia.org/wiki/Backpropagation
