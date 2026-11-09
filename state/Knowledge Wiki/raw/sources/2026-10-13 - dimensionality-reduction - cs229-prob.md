<!-- source: https://cs229.stanford.edu/section/cs229-prob.pdf | type: pdf | hash: 1e95722b5c540bbe2fdb8b90ee10dda3f6bd9c50168afd01cbfc545c6c47976e | fetched: 2026-10-13T11:30:00Z -->

Review of Probability Theory

Arian Maleki and Tom Do
Stanford University

Probability theory is the study of uncertainty. Through this class, we will be relying on concepts
from probability theory for deriving machine learning algorithms. These notes attempt to cover the
basics of probability theory at a level appropriate for CS 229. The mathematical theory of probability
is very sophisticated, and delves into a branch of analysis known as measure theory. In these notes,
we provide a basic treatment of probability that does not address these finer details.

1

Elements of probability

In order to define a probability on a set we need a few basic elements,
• Sample space Ω: The set of all the outcomes of a random experiment. Here, each outcome
ω ∈ Ω can be thought of as a complete description of the state of the real world at the end
of the experiment.
• Set of events (or event space) F: A set whose elements A ∈ F (called events) are subsets
of Ω (i.e., A ⊆ Ω is a collection of possible outcomes of an experiment).1 .
• Probability measure: A function P : F → R that satisfies the following properties,
- P (A) ≥ 0, for all A ∈ F
- P (Ω) = 1
- If A1 , A2 , . . . are disjoint events (i.e., Ai ∩ Aj = ∅ whenever i 6= j), then
X
P (∪i Ai ) =
P (Ai )
i

These three properties are called the Axioms of Probability.
Example: Consider the event of tossing a six-sided die. The sample space is Ω = {1, 2, 3, 4, 5, 6}.
We can define different event spaces on this sample space. For example, the simplest event space
is the trivial event space F = {∅, Ω}. Another event space is the set of all subsets of Ω. For the
first event space, the unique probability measure satisfying the requirements above is given by
P (∅) = 0, P (Ω) = 1. For the second event space, one valid probability measure is to assign the
probability of each set in the event space to be 6i where i is the number of elements of that set; for
example, P ({1, 2, 3, 4}) = 46 and P ({1, 2, 3}) = 63 .
Properties:
- If A ⊆ B =⇒ P (A) ≤ P (B).
- P (A ∩ B) ≤ min(P (A), P (B)).
- (Union Bound) P (A ∪ B) ≤ P (A) + P (B).
- P (Ω \ A) = 1 − P (A).
- (Law of Total Probability) If A1 , . . . , Ak are a set of disjoint events such that ∪ki=1 Ai = Ω, then
Pk
i=1 P (Ak ) = 1.
1
F should satisfy three properties: (1) ∅ ∈ F; (2) A ∈ F =⇒ Ω \ A ∈ F ; and (3) A1 , A2 , . . . ∈ F =⇒
∪i Ai ∈ F .

1

1.1

Conditional probability and independence

Let B be an event with non-zero probability. The conditional probability of any event A given B is
defined as,
P (A ∩ B)
P (A|B) ,
P (B)
In other words, P (A|B) is the probability measure of the event A after observing the occurrence of
event B. Two events are called independent if and only if P (A ∩ B) = P (A)P (B) (or equivalently,
P (A|B) = P (A)). Therefore, independence is equivalent to saying that observing B does not have
any effect on the probability of A.

2

Random variables

Consider an experiment in which we flip 10 coins, and we want to know the number of coins that
come up heads. Here, the elements of the sample space Ω are 10-length sequences of heads and
tails. For example, we might have w0 = hH, H, T, H, T, H, H, T, T, T i ∈ Ω. However, in practice,
we usually do not care about the probability of obtaining any particular sequence of heads and tails.
Instead we usually care about real-valued functions of outcomes, such as the number of heads that
appear among our 10 tosses, or the length of the longest run of tails. These functions, under some
technical conditions, are known as random variables.
More formally, a random variable X is a function X : Ω −→ R.2 Typically, we will denote random
variables using upper case letters X(ω) or more simply X (where the dependence on the random
outcome ω is implied). We will denote the value that a random variable may take on using lower
case letters x.
Example: In our experiment above, suppose that X(ω) is the number of heads which occur in the
sequence of tosses ω. Given that only 10 coins are tossed, X(ω) can take only a finite number of
values, so it is known as a discrete random variable. Here, the probability of the set associated
with a random variable X taking on some specific value k is
P (X = k) := P ({ω : X(ω) = k}).
Example: Suppose that X(ω) is a random variable indicating the amount of time it takes for a
radioactive particle to decay. In this case, X(ω) takes on a infinite number of possible values, so it is
called a continuous random variable. We denote the probability that X takes on a value between
two real constants a and b (where a < b) as
P (a ≤ X ≤ b) := P ({ω : a ≤ X(ω) ≤ b}).
2.1

Cumulative distribution functions

In order to specify the probability measures used when dealing with random variables, it is often
convenient to specify alternative functions (CDFs, PDFs, and PMFs) from which the probability
measure governing an experiment immediately follows. In this section and the next two sections,
we describe each of these types of functions in turn.
A cumulative distribution function (CDF) is a function FX : R → [0, 1] which specifies a probability measure as,
FX (x) , P (X ≤ x).
(1)
3
By using this function one can calculate the probability of any event in F. Figure ?? shows a
sample CDF function.
Properties:
2

Technically speaking, not every function is not acceptable as a random variable. From a measure-theoretic
perspective, random variables must be Borel-measurable functions. Intuitively, this restriction ensures that
given a random variable and its underlying outcome space, one can implicitly define the each of the events
of the event space as being sets of outcomes ω ∈ Ω for which X(ω) satisfies some property (e.g., the event
{ω : X(ω) ≥ 3}).
3
This is a remarkable fact and is actually a theorem that is proved in more advanced courses.

2

Figure 1: A cumulative distribution function (CDF).

- 0 ≤ FX (x) ≤ 1.
- limx→−∞ FX (x) = 0.
- limx→∞ FX (x) = 1.
- x ≤ y =⇒ FX (x) ≤ FX (y).
2.2

Probability mass functions

When a random variable X takes on a finite set of possible values (i.e., X is a discrete random
variable), a simpler way to represent the probability measure associated with a random variable is
to directly specify the probability of each value that the random variable can assume. In particular,
a probability mass function (PMF) is a function pX : Ω → R such that
pX (x) , P (X = x).
In the case of discrete random variable, we use the notation V al(X) for the set of possible values
that the random variable X may assume. For example, if X(ω) is a random variable indicating the
number of heads out of ten tosses of coin, then V al(X) = {0, 1, 2, . . . , 10}.
Properties:
- 0 ≤ pX (x) ≤ 1.
P
x∈V al(X) pX (x) = 1.
P
x∈A pX (x) = P (X ∈ A).
-

2.3

Probability density functions

For some continuous random variables, the cumulative distribution function FX (x) is differentiable
everywhere. In these cases, we define the Probability Density Function or PDF as the derivative
of the CDF, i.e.,
dFX (x)
fX (x) ,
.
(2)
dx
Note here, that the PDF for a continuous random variable may not always exist (i.e., if FX (x) is not
differentiable everywhere).
According to the properties of differentiation, for very small ∆x,
P (x ≤ X ≤ x + ∆x) ≈ fX (x)∆x.

(3)

Both CDFs and PDFs (when they exist!) can be used for calculating the probabilities of different
events. But it should be emphasized that the value of PDF at any given point x is not the probability
3

of that event, i.e., fX (x) 6= P (X = x). For example, fX (x) can take on values larger than one (but
the integral of fX (x) over any subset of R will be at most one).
Properties:
- fX (x) ≥ 0 .
R∞
- −∞ fX (x) = 1.
R
- x∈A fX (x)dx = P (X ∈ A).
2.4

Expectation

Suppose that X is a discrete random variable with PMF pX (x) and g : R −→ R is an arbitrary
function. In this case, g(X) can be considered a random variable, and we define the expectation or
expected value of g(X) as
X
E[g(X)] ,
g(x)pX (x).
x∈V al(X)

If X is a continuous random variable with PDF fX (x), then the expected value of g(X) is defined
as,
Z ∞
E[g(X)] ,
g(x)fX (x)dx.
−∞

Intuitively, the expectation of g(X) can be thought of as a “weighted average” of the values that
g(x) can taken on for different values of x, where the weights are given by pX (x) or fX (x). As
a special case of the above, note that the expectation, E[X] of a random variable itself is found by
letting g(x) = x; this is also known as the mean of the random variable X.
Properties:
- E[a] = a for any constant a ∈ R.
- E[af (X)] = aE[f (X)] for any constant a ∈ R.
- (Linearity of Expectation) E[f (X) + g(X)] = E[f (X)] + E[g(X)].
- For a discrete random variable X, E[1{X = k}] = P (X = k).
2.5

Variance

The variance of a random variable X is a measure of how concentrated the distribution of a random
variable X is around its mean. Formally, the variance of a random variable X is defined as
V ar[X] , E[(X − E(X))2 ]
Using the properties in the previous section, we can derive an alternate expression for the variance:
E[(X − E[X])2 ]

=

E[X 2 − 2E[X]X + E[X]2 ]

=

E[X 2 ] − 2E[X]E[X] + E[X]2

= E[X 2 ] − E[X]2 ,
where the second equality follows from linearity of expectations and the fact that E[X] is actually a
constant with respect to the outer expectation.
Properties:
- V ar[a] = 0 for any constant a ∈ R.
- V ar[af (X)] = a2 V ar[f (X)] for any constant a ∈ R.
Example Calculate the mean and the variance of the uniform random variable X with PDF fX (x) =
1, ∀x ∈ [0, 1], 0 elsewhere.
Z ∞
Z 1
1
E[X] =
xfX (x)dx =
xdx = .
2
−∞
0
4

2

Z ∞

Z 1

2

E[X ] =

x fX (x)dx =
−∞

x2 dx =

0

V ar[X] = E[X 2 ] − E[X]2 =

1
.
3

1 1
1
− =
.
3 4
12

Example: Suppose that g(x) = 1{x ∈ A} for some subset A ⊆ Ω. What is E[g(X)]?
Discrete case:
X

E[g(X)] =

1{x ∈ A}PX (x)dx =

X

PX (x)dx = P (x ∈ A).

x∈A

x∈V al(X)

Continuous case:
Z ∞

Z
1{x ∈ A}fX (x)dx =

E[g(X)] =
−∞

2.6

fX (x)dx = P (x ∈ A).
x∈A

Some common random variables

Discrete random variables
• X ∼ Bernoulli(p) (where 0 ≤ p ≤ 1): one if a coin with heads probability p comes up
heads, zero otherwise.

p
if p = 1
p(x) =
1 − p if p = 0
• X ∼ Binomial(n, p) (where 0 ≤ p ≤ 1): the number of heads in n independent flips of a
coin with heads probability p.
 
n x
p(x) =
p (1 − p)n−x
x
• X ∼ Geometric(p) (where p > 0): the number of flips of a coin with heads probability p
until the first heads.
p(x) = p(1 − p)x−1
• X ∼ P oisson(λ) (where λ > 0): a probability distribution over the nonnegative integers
used for modeling the frequency of rare events.
p(x) = e−λ

λx
x!

Continuous random variables
• X ∼ U nif orm(a, b) (where a < b): equal probability density to every value between a
and b on the real line.
(
1
if a ≤ x ≤ b
f (x) = b−a
0
otherwise
• X ∼ Exponential(λ) (where λ > 0): decaying probability density over the nonnegative
reals.
 −λx
λe
if x ≥ 0
f (x) =
0
otherwise
• X ∼ N ormal(µ, σ 2 ): also known as the Gaussian distribution
f (x) = √

2
1
1
e− 2σ2 (x−µ)
2πσ

5

Figure 2: PDF and CDF of a couple of random variables.

The shape of the PDFs and CDFs of some of these random variables are shown in Figure ??.
The following table is the summary of some of the properties of these distributions.
Distribution
Bernoulli(p)
Binomial(n, p)
Geometric(p)
P oisson(λ)
U nif orm(a, b)
Gaussian(µ, σ 2 )
Exponential(λ)

3

PDF
 or PMF
p,
if x = 1
1 − p, if x = 0.
 k
n
n−k
for 0 ≤ k ≤ n
k p (1 − p)
k−1
p(1 − p)
for k = 1, 2, . . .
e−λ λx /x! for k = 1, 2, . . .
1
b−a ∀x ∈ (a, b)

Mean

Variance

p

p(1 − p)

np

npq

1
p

1−p
p2

λ

λ

a+b
2

(b−a)2
12

√1 e−
σ 2π
−λx

µ

σ2

1
λ

1
λ2

λe

(x−µ)2
2σ 2

x ≥ 0, λ > 0

Two random variables

Thus far, we have considered single random variables.
In many situations, however,
there may be more than one quantity that we are interested in knowing during a random experiment.
For instance, in an experiment where we flip a coin ten times, we
may care about both X(ω) = the number of heads that come up as well as Y (ω) =
the length of the longest run of consecutive heads. In this section, we consider the setting of two
random variables.
3.1

Joint and marginal distributions

Suppose that we have two random variables X and Y . One way to work with these two random
variables is to consider each of them separately. If we do that we will only need FX (x) and FY (y).
But if we want to know about the values that X and Y assume simultaneously during outcomes
of a random experiment, we require a more complicated structure known as the joint cumulative
distribution function of X and Y , defined by
FXY (x, y) = P (X ≤ x, Y ≤ y)
It can be shown that by knowing the joint cumulative distribution function, the probability of any
event involving X and Y can be calculated.
6

The joint CDF FXY (x, y) and the joint distribution functions FX (x) and FY (y) of each variable
separately are related by
FX (x)

=

FY (y)

=

lim FXY (x, y)dy

y→∞

lim FXY (x, y)dx.

x→∞

Here, we call FX (x) and FY (y) the marginal cumulative distribution functions of FXY (x, y).
Properties:
- 0 ≤ FXY (x, y) ≤ 1.
- limx,y→∞ FXY (x, y) = 1.
- limx,y→−∞ FXY (x, y) = 0.
- FX (x) = limy→∞ FXY (x, y).
3.2

Joint and marginal probability mass functions

If X and Y are discrete random variables, then the joint probability mass function pXY : R×R →
[0, 1] is defined by
pXY (x, y) = P (X = x, Y = y).
P
P
Here, 0 ≤ PXY (x, y) ≤ 1 for all x, y, and x∈V al(X) y∈V al(Y ) PXY (x, y) = 1.
How does the joint PMF over two variables relate to the probability mass function for each variable
separately? It turns out that
X
pX (x) =
pXY (x, y).
y

and similarly for pY (y). In this case, we refer to pX (x) as the marginal probability mass function
of X. In statistics, the process of forming the marginal distribution with respect to one variable by
summing out the other variable is often known as “marginalization.”
3.3

Joint and marginal probability density functions

Let X and Y be two continuous random variables with joint distribution function FXY . In the case
that FXY (x, y) is everywhere differentiable in both x and y, then we can define the joint probability
density function,
fXY (x, y) =

∂ 2 FXY (x, y)
.
∂x∂y

Like in the single-dimensional case, fXY (x, y) 6= P (X = x, Y = y), but rather
ZZ
fXY (x, y)dxdy = P ((X, Y ) ∈ A).
x∈A

Note that the values of the probability density function fXY R(x, y)R are always nonnegative, but they
∞
∞
may be greater than 1. Nonetheless, it must be the case that −∞ −∞ fXY (x, y) = 1.
Analagous to the discrete case, we define
Z ∞
fX (x) =

fXY (x, y)dy,
−∞

as the marginal probability density function (or marginal density) of X, and similarly for fY (y).
7

3.4

Conditional distributions

Conditional distributions seek to answer the question, what is the probability distribution over Y ,
when we know that X must take on a certain value x? In the discrete case, the conditional probability
mass function of X given Y is simply
pY |X (y|x) =

pXY (x, y)
,
pX (x)

assuming that pX (x) 6= 0.
In the continuous case, the situation is technically a little more complicated because the probability
that a continuous random variable X takes on a specific value x is equal to zero4 . Ignoring this
technical point, we simply define, by analogy to the discrete case, the conditional probability density
of Y given X = x to be
fXY (x, y)
fY |X (y|x) =
,
fX (x)
provided fX (x) 6= 0.
3.5

Bayes’s rule

A useful formula that often arises when trying to derive expression for the conditional probability of
one variable given another, is Bayes’s rule.
In the case of discrete random variables X and Y ,
PY |X (y|x) =

PX|Y (x|y)PY (y)
PXY (x, y)
=P
.
0
0
PX (x)
y 0 ∈V al(Y ) PX|Y (x|y )PY (y )

If the random variables X and Y are continuous,
fY |X (y|x) =
3.6

fX|Y (x|y)fY (y)
fXY (x, y)
= R∞
.
fX (x)
f
(x|y 0 )fY (y 0 )dy 0
−∞ X|Y

Independence

Two random variables X and Y are independent if FXY (x, y) = FX (x)FY (y) for all values of x
and y. Equivalently,
• For discrete random variables, pXY (x, y) = pX (x)pY (y) for all x ∈ V al(X), y ∈
V al(Y ).
• For discrete random variables, pY |X (y|x) = pY (y) whenever pX (x) 6= 0 for all y ∈
V al(Y ).
• For continuous random variables, fXY (x, y) = fX (x)fY (y) for all x, y ∈ R.
• For continuous random variables, fY |X (y|x) = fY (y) whenever fX (x) 6= 0 for all y ∈ R.
4

To get around this, a more reasonable way to calculate the conditional CDF is,
FY |X (y, x) = lim P (Y ≤ y|x ≤ X ≤ x + ∆x).
∆x→0

It can be easily seen that if F (x, y) is differentiable in both x, y then,
Z y
fX,Y (x, α)
FY |X (y, x) =
dα
fX (x)
−∞
and therefore we define the conditional PDF of Y given X = x in the following way,
fY |X (y|x) =

8

fXY (x, y)
fX (x)

Informally, two random variables X and Y are independent if “knowing” the value of one variable
will never have any effect on the conditional probability distribution of the other variable, that is,
you know all the information about the pair (X, Y ) by just knowing f (x) and f (y). The following
lemma formalizes this observation:
Lemma 3.1. If X and Y are independent then for any subsets A, B ⊆ R, we have,
P (X ∈ A, Y ∈ B) = P (X ∈ A)P (Y ∈ B)
By using the above lemma one can prove that if X is independent of Y then any function of X is
independent of any function of Y .
3.7

Expectation and covariance

Suppose that we have two discrete random variables X, Y and g : R2 −→ R is a function of these
two random variables. Then the expected value of g is defined in the following way,
X
X
E[g(X, Y )] ,
g(x, y)pXY (x, y).
x∈V al(X) y∈V al(Y )

For continuous random variables X, Y , the analogous expression is
Z ∞Z ∞
E[g(X, Y )] =
g(x, y)fXY (x, y)dxdy.
−∞

−∞

We can use the concept of expectation to study the relationship of two random variables with each
other. In particular, the covariance of two random variables X and Y is defined as
Cov[X, Y ] , E[(X − E[X])(Y − E[Y ])]
Using an argument similar to that for variance, we can rewrite this as,
Cov[X, Y ]

=
=
=
=

E[(X − E[X])(Y − E[Y ])]
E[XY − XE[Y ] − Y E[X] + E[X]E[Y ]]
E[XY ] − E[X]E[Y ] − E[Y ]E[X] + E[X]E[Y ]]
E[XY ] − E[X]E[Y ].

Here, the key step in showing the equality of the two forms of covariance is in the third equality,
where we use the fact that E[X] and E[Y ] are actually constants which can be pulled out of the
expectation. When Cov[X, Y ] = 0, we say that X and Y are uncorrelated5 .
Properties:
- (Linearity of expectation) E[f (X, Y ) + g(X, Y )] = E[f (X, Y )] + E[g(X, Y )].
- V ar[X + Y ] = V ar[X] + V ar[Y ] + 2Cov[X, Y ].
- If X and Y are independent, then Cov[X, Y ] = 0.
- If X and Y are independent, then E[f (X)g(Y )] = E[f (X)]E[g(Y )].

4

Multiple random variables

The notions and ideas introduced in the previous section can be generalized to more than
two random variables. In particular, suppose that we have n continuous random variables,
X1 (ω), X2 (ω), . . . Xn (ω). In this section, for simplicity of presentation, we focus only on the
continuous case, but the generalization to discrete random variables works similarly.
5
However, this is not the same thing as stating that X and Y are independent! For example, if X ∼
U nif orm(−1, 1) and Y = X 2 , then one can show that X and Y are uncorrelated, even though they are not
independent.

9

4.1

Basic properties

We can define the joint distribution function of X1 , X2 , . . . , Xn , the joint probability density
function of X1 , X2 , . . . , Xn , the marginal probability density function of X1 , and the conditional probability density function of X1 given X2 , . . . , Xn , as

= P (X1 ≤ x1 , X2 ≤ x2 , . . . , Xn ≤ xn )
∂ n FX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )
fX1 ,X2 ,...,Xn (x1 , x2 , . . . xn ) =
∂x . . . ∂xn
Z ∞
Z ∞1
fX1 (X1 ) =
···
fX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )dx2 . . . dxn

FX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )

−∞

fX1 |X2 ,...,Xn (x1 |x2 , . . . xn )

=

−∞

fX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )
fX2 ,...,Xn (x1 , x2 , . . . xn )

To calculate the probability of an event A ⊆ Rn we have,
Z
P ((x1 , x2 , . . . xn ) ∈ A) =
fX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )dx1 dx2 . . . dxn

(4)

(x1 ,x2 ,...xn )∈A

Chain rule: From the definition of conditional probabilities for multiple random variables, one can
show that
f (x1 , x2 , . . . , xn )

= f (xn |x1 , x2 . . . , xn−1 )f (x1 , x2 . . . , xn−1 )
= f (xn |x1 , x2 . . . , xn−1 )f (xn−1 |x1 , x2 . . . , xn−2 )f (x1 , x2 . . . , xn−2 )
n
Y
= . . . = f (x1 )
f (xi |x1 , . . . , xi−1 ).
i=2

Independence: For multiple events, A1 , . . . , Ak , we say that A1 , . . . , Ak are mutually independent if for any subset S ⊆ {1, 2, . . . , k}, we have
Y
P (∩i∈S Ai ) =
P (Ai ).
i∈S

Likewise, we say that random variables X1 , . . . , Xn are independent if
f (x1 , . . . , xn ) = f (x1 )f (x2 ) · · · f (xn ).
Here, the definition of mutual independence is simply the natural generalization of independence of
two random variables to multiple random variables.
Independent random variables arise often in machine learning algorithms where we assume that the
training examples belonging to the training set represent independent samples from some unknown
probability distribution. To make the significance of independence clear, consider a “bad” training
set in which we first sample a single training example (x(1) , y (1) ) from the some unknown distribution, and then add m − 1 copies of the exact same training example to the training set. In this case,
we have (with some abuse of notation)
P ((x(1) , y (1) ), . . . .(x(m) , y (m) )) 6=

m
Y

P (x(i) , y (i) ).

i=1

Despite the fact that the training set has size m, the examples are not independent! While clearly the
procedure described here is not a sensible method for building a training set for a machine learning
algorithm, it turns out that in practice, non-independence of samples does come up often, and it has
the effect of reducing the “effective size” of the training set.
10

4.2

Random vectors

Suppose that we have n random variables. When working with all these random variables together,
we will often find it convenient to put them in a vector X = [X1 X2 . . . Xn ]T . We call the resulting
vector a random vector (more formally, a random vector is a mapping from Ω to Rn ). It should be
clear that random vectors are simply an alternative notation for dealing with n random variables, so
the notions of joint PDF and CDF will apply to random vectors as well.
Expectation: Consider an arbitrary function from g : Rn → R. The expected value of this function
is defined as
Z
E[g(X)] =

g(x1 , x2 , . . . , xn )fX1 ,X2 ,...,Xn (x1 , x2 , . . . xn )dx1 dx2 . . . dxn ,

(5)

Rn

where Rn is n consecutive integrations from −∞ to ∞. If g is a function from Rn to Rm , then the
expected value of g is the element-wise expected values of the output vector, i.e., if g is


g1 (x)
 g2 (x) 

g(x) = 
 ...  ,
R

gm (x)
Then,

E[g1 (X)]
 E[g2 (X)] 
.
E[g(X)] = 
..


.


E[gm (X)]
Covariance matrix: For a given random vector X : Ω → Rn , its covariance matrix Σ is the n × n
square matrix whose entries are given by Σij = Cov[Xi , Xj ].
From the definition of covariance, we have


Cov[X1 , X1 ] · · · Cov[X1 , Xn ]


..
..
..
Σ = 

.
.
.

Cov[Xn , X1 ] · · · Cov[Xn , Xn ]


E[X12 ] − E[X1 ]E[X1 ]
· · · E[X1 Xn ] − E[X1 ]E[Xn ]


..
..
..
= 

.
.
.
2
E[Xn X1 ] − E[Xn ]E[X1 ] · · ·
E[Xn ] − E[Xn ]E[Xn ]

 

2
E[X1 ]
· · · E[X1 Xn ]
E[X1 ]E[X1 ] · · · E[X1 ]E[Xn ]

 

..
..
..
..
..
..
= 
−

.
.
.
.
.
.
E[Xn X1 ] · · ·
T

E[Xn2 ]

E[Xn ]E[X1 ] · · ·

E[Xn ]E[Xn ]

T

= E[XX ] − E[X]E[X] = . . . = E[(X − E[X])(X − E[X])T ].
where the matrix expectation is defined in the obvious way.
The covariance matrix has a number of useful properties:
- Σ  0; that is, Σ is positive semidefinite.
- Σ = ΣT ; that is, Σ is symmetric.
4.3

The multivariate Gaussian distribution

One particularly important example of a probability distribution over random vectors X is called
the multivariate Gaussian or multivariate normal distribution. A random vector X ∈ Rn is said
to have a multivariate normal (or Gaussian) distribution with mean µ ∈ Rn and covariance matrix
Σ ∈ Sn++ (where Sn++ refers to the space of symmetric positive definite n × n matrices)


1
1
T −1
fX1 ,X2 ,...,Xn (x1 , x2 , . . . , xn ; µ, Σ) =
exp − (x − µ) Σ (x − µ) .
2
(2π)n/2 |Σ|1/2
11

We write this as X ∼ N (µ, Σ). Notice that in the case n = 1, this reduces the regular definition of
a normal distribution with mean parameter µ1 and variance Σ11 .
Generally speaking, Gaussian random variables are extremely useful in machine learning and statistics for two main reasons. First, they are extremely common when modeling “noise” in statistical
algorithms. Quite often, noise can be considered to be the accumulation of a large number of small
independent random perturbations affecting the measurement process; by the Central Limit Theorem, summations of independent random variables will tend to “look Gaussian.” Second, Gaussian
random variables are convenient for many analytical manipulations, because many of the integrals
involving Gaussian distributions that arise in practice have simple closed form solutions. We will
encounter this later in the course.

5

Other resources

A good textbook on probablity at the level needed for CS229 is the book, A First Course on Probability by Sheldon Ross.

12


