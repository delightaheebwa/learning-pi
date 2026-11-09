# Source: Backpropagation forward/backward passes

Captured from user-provided notes about backpropagation.

## Raw text

Backpropagation has two main phases: a forward pass and a backward pass.

In the forward pass, I feed the input xx through the network layer by layer, computing each layer’s pre-activation and activation, and I store all these intermediate values. At the end of the forward pass, I compute the loss L(y,fK(x))L(y,fK(x)).

In the backward pass, I start from the loss and move backward through the network. For each layer, I take the gradient of the loss with respect to that layer’s output (which already includes the effect of all later layers), and multiply it by the local gradient of that layer (how its output depends on its input and its parameters). This gives me both the gradient of the loss with respect to that layer’s parameters and the gradient to pass to the previous layer, so I don’t have to recompute the full chain rule separately for every parameter.

## Extracted notes

- Backpropagation has two phases: a forward pass and a backward pass.
- The forward pass computes and stores intermediate activations and pre-activations layer by layer.
- The loss is computed at the end of the forward pass from the model output.
- The backward pass starts at the loss and moves backward through the network.
- At each layer, the upstream gradient is combined with the local gradient of the layer.
- This produces both parameter gradients and the gradient to pass to the previous layer.
- The point is to reuse intermediate gradients instead of recomputing the full chain rule from scratch for every parameter.

## Open questions

- None from the source.
