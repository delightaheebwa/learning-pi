# Gradient descent is literally the steepest decrease of the first-order Taylor model

## Source

User note: "gradient descent is literally 'walk in the direction that gives the steepest decrease in the first-order Taylor model.'"

## Extracted ideas

- Gradient descent uses the local linear approximation of the loss surface.
- The first-order Taylor model tells you the slope near the current point.
- The steepest decrease direction is the negative gradient direction.
- This is a first-order method: it uses gradient information, not curvature information.

## Open questions

- How does the fixed-step-length view make the "steepest decrease" direction precise?
- How does this connect to line search and step-size selection?
