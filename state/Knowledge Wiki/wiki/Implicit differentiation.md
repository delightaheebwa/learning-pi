<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Implicit_function | verified-by=fact-check-agent | date=2026-10-26 -->

# Implicit differentiation

Implicit differentiation is the process of differentiating an equation that defines \(y\) implicitly rather than solving for \(y\) first.

If an equation can be written as

- \(F(x,y)=0\)

and \(y\) depends on \(x\), then differentiating both sides gives

- \(F_x + F_y\,\frac{dy}{dx} = 0\)

so

- \(\frac{dy}{dx} = -\frac{F_x}{F_y}\)

when \(F_y \neq 0\).

## How it connects to differentials

This is the same idea as the [[Total differential]] viewpoint. If you write

- \(dF = F_x\,dx + F_y\,dy\)

then along a level curve \(F(x,y)=c\), you set \(dF=0\) and solve for the slope.

## Example: a curve defined by two variables

For

- \(\sin(x) y^2 = x\)

rewrite it as

- \(F(x,y)=\sin(x) y^2 - x = 0\)

Then differentiating gives a relation between \(dx\) and \(dy\) that you can rearrange to find \(dy/dx\).

## Example: the logarithm

Start from the inverse relation

- \(e^y = x\)

Differentiate with respect to \(x\):

- \(e^y\,\frac{dy}{dx} = 1\)

Since \(e^y=x\), this becomes

- \(\frac{dy}{dx} = \frac{1}{x}\)

So the derivative of \(\ln(x)\) appears naturally from implicit differentiation.

## Related pages

- [[Total differential]]
- [[Natural logarithm]]
- [[Euler number e]]
- [[Exponential derivatives]]

## Sources
- Wikipedia, "Implicit function": https://en.wikipedia.org/wiki/Implicit_function
- Khan Academy, "Implicit differentiation": https://www.khanacademy.org/math/ap-calculus-ab/ab-differentiation-2-new/ab-3-4/a/implicit-differentiation-review
