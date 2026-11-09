<!-- source: https://arxiv.org/abs/1404.1100 | type: pdf | hash: 09e1114a3f8e0d3d2b0a5ff13a13027c012ee86afde3518df676393a58ab0757 | fetched: 2026-10-13T11:30:00Z -->

A Tutorial on Principal Component Analysis
Jonathon Shlens∗
Google
Research
Mountain View, CA 94043

arXiv:1404.1100v1 [cs.LG] 3 Apr 2014

(Dated: April 7, 2014; Version 3.02)
Principal component analysis (PCA) is a mainstay of modern data analysis - a black box that is widely used
but (sometimes) poorly understood. The goal of this paper is to dispel the magic behind this black box. This
manuscript focuses on building a solid intuition for how and why principal component analysis works. This
manuscript crystallizes this knowledge by deriving from simple intuitions, the mathematics behind PCA. This
tutorial does not shy away from explaining the ideas informally, nor does it shy away from the mathematics. The
hope is that by addressing both aspects, readers of all levels will be able to gain a better understanding of PCA as
well as the when, the how and the why of applying this technique.

I. INTRODUCTION

II. MOTIVATION: A TOY EXAMPLE

Principal component analysis (PCA) is a standard tool in modern data analysis - in diverse fields from neuroscience to computer graphics - because it is a simple, non-parametric method
for extracting relevant information from confusing data sets.
With minimal effort PCA provides a roadmap for how to reduce a complex data set to a lower dimension to reveal the
sometimes hidden, simplified structures that often underlie it.

Here is the perspective: we are an experimenter. We are trying
to understand some phenomenon by measuring various quantities (e.g. spectra, voltages, velocities, etc.) in our system.
Unfortunately, we can not figure out what is happening because the data appears clouded, unclear and even redundant.
This is not a trivial problem, but rather a fundamental obstacle
in empirical science. Examples abound from complex systems such as neuroscience, web indexing, meteorology and
oceanography - the number of variables to measure can be
unwieldy and at times even deceptive, because the underlying
relationships can often be quite simple.

The goal of this tutorial is to provide both an intuitive feel for
PCA, and a thorough discussion of this topic. We will begin
with a simple example and provide an intuitive explanation
of the goal of PCA. We will continue by adding mathematical rigor to place it within the framework of linear algebra to
provide an explicit solution. We will see how and why PCA
is intimately related to the mathematical technique of singular
value decomposition (SVD). This understanding will lead us
to a prescription for how to apply PCA in the real world and an
appreciation for the underlying assumptions. My hope is that
a thorough understanding of PCA provides a foundation for
approaching the fields of machine learning and dimensional
reduction.
The discussion and explanations in this paper are informal in
the spirit of a tutorial. The goal of this paper is to educate.
Occasionally, rigorous mathematical proofs are necessary although relegated to the Appendix. Although not as vital to the
tutorial, the proofs are presented for the adventurous reader
who desires a more complete understanding of the math. My
only assumption is that the reader has a working knowledge
of linear algebra. My goal is to provide a thorough discussion
by largely building on ideas from linear algebra and avoiding
challenging topics in statistics and optimization theory (but
see Discussion). Please feel free to contact me with any suggestions, corrections or comments.

∗ Electronic address: jonathon.shlens@gmail.com

Take for example a simple toy problem from physics diagrammed in Figure 1. Pretend we are studying the motion
of the physicist’s ideal spring. This system consists of a ball
of mass m attached to a massless, frictionless spring. The ball
is released a small distance away from equilibrium (i.e. the
spring is stretched). Because the spring is ideal, it oscillates
indefinitely along the x-axis about its equilibrium at a set frequency.
This is a standard problem in physics in which the motion
along the x direction is solved by an explicit function of time.
In other words, the underlying dynamics can be expressed as
a function of a single variable x.
However, being ignorant experimenters we do not know any
of this. We do not know which, let alone how many, axes
and dimensions are important to measure. Thus, we decide to
measure the ball’s position in a three-dimensional space (since
we live in a three dimensional world). Specifically, we place
three movie cameras around our system of interest. At 120 Hz
each movie camera records an image indicating a two dimensional position of the ball (a projection). Unfortunately, because of our ignorance, we do not even know what are the real
x, y and z axes, so we choose three camera positions~a,~b and~c
at some arbitrary angles with respect to the system. The angles
between our measurements might not even be 90o ! Now, we
record with the cameras for several minutes. The big question
remains: how do we get from this data set to a simple equation

2
A. A Naive Basis

camera A

camera B

camera C

With a more precise definition of our goal, we need a more
precise definition of our data as well. We treat every time
sample (or experimental trial) as an individual sample in our
data set. At each time sample we record a set of data consisting of multiple measurements (e.g. voltage, position, etc.). In
our data set, at one point in time, camera A records a corresponding ball position (xA , yA ). One sample or trial can then
be expressed as a 6 dimensional column vector


xA
 yA 


x 
~X = 
 B
 yB 
x 
C
yC
where each camera contributes a 2-dimensional projection of
the ball’s position to the entire vector ~X. If we record the ball’s
position for 10 minutes at 120 Hz, then we have recorded 10×
60 × 120 = 72000 of these vectors.

FIG. 1 A toy example. The position of a ball attached to an oscillating spring is recorded using three cameras A, B and C. The position
of the ball tracked by each camera is depicted in each panel below.

of x?
We know a-priori that if we were smart experimenters, we
would have just measured the position along the x-axis with
one camera. But this is not what happens in the real world.
We often do not know which measurements best reflect the
dynamics of our system in question. Furthermore, we sometimes record more dimensions than we actually need.
Also, we have to deal with that pesky, real-world problem of
noise. In the toy example this means that we need to deal
with air, imperfect cameras or even friction in a less-than-ideal
spring. Noise contaminates our data set only serving to obfuscate the dynamics further. This toy example is the challenge
experimenters face everyday. Keep this example in mind as
we delve further into abstract concepts. Hopefully, by the end
of this paper we will have a good understanding of how to
systematically extract x using principal component analysis.

III. FRAMEWORK: CHANGE OF BASIS

The goal of principal component analysis is to identify the
most meaningful basis to re-express a data set. The hope is
that this new basis will filter out the noise and reveal hidden
structure. In the example of the spring, the explicit goal of
PCA is to determine: “the dynamics are along the x-axis.” In
other words, the goal of PCA is to determine that x̂, i.e. the
unit basis vector along the x-axis, is the important dimension.
Determining this fact allows an experimenter to discern which
dynamics are important, redundant or noise.

With this concrete example, let us recast this problem in abstract terms. Each sample ~X is an m-dimensional vector,
where m is the number of measurement types. Equivalently,
every sample is a vector that lies in an m-dimensional vector space spanned by some orthonormal basis. From linear
algebra we know that all measurement vectors form a linear
combination of this set of unit length basis vectors. What is
this orthonormal basis?
This question is usually a tacit assumption often overlooked.
Pretend we gathered our toy example data above, but only
looked at camera A. What is an orthonormal basis for (xA , yA )?
A naive choice
would be√ {(1,√0), (0, 1)}, but why select this
√ √
basis over {( 22 , 22 ), ( −2 2 , −2 2 )} or any other arbitrary rotation? The reason is that the naive basis reflects the method we
gathered the data. Pretend √we √
record the position (2, 2). We
√
did not record 2 2 in the ( 22 , 22 ) direction and 0 in the perpendicular direction. Rather, we recorded the position (2, 2)
on our camera meaning 2 units up and 2 units to the left in our
camera window. Thus our original basis reflects the method
we measured our data.
How do we express this naive basis in linear algebra? In the
two dimensional case, {(1, 0), (0, 1)} can be recast as individual row vectors. A matrix constructed out of these row vectors
is the 2 × 2 identity matrix I. We can generalize this to the mdimensional case by constructing an m × m identity matrix
 

b1
1 0 ··· 0
 b2   0 1 · · · 0 
 

B=
 ..  =  .. .. . . . ..  = I
.
. .
.
bm
0 0 ··· 1


where each row is an orthornormal basis vector bi with m
components. We can consider our naive basis as the effective
starting point. All of our data has been recorded in this basis

3
and thus it can be trivially expressed as a linear combination
of {bi }.

We can note the form of each column of Y.


p1 · xi


yi =  ... 
pm · xi

B. Change of Basis

With this rigor we may now state more precisely what PCA
asks: Is there another basis, which is a linear combination of
the original basis, that best re-expresses our data set?
A close reader might have noticed the conspicuous addition of
the word linear. Indeed, PCA makes one stringent but powerful assumption: linearity. Linearity vastly simplifies the problem by restricting the set of potential bases. With this assumption PCA is now limited to re-expressing the data as a linear
combination of its basis vectors.
Let X be the original data set, where each column is a single
sample (or moment in time) of our data set (i.e. ~X). In the toy
example X is an m × n matrix where m = 6 and n = 72000.
Let Y be another m × n matrix related by a linear transformation P. X is the original recorded data set and Y is a new
representation of that data set.
PX = Y

We recognize that each coefficient of yi is a dot-product of
xi with the corresponding row in P. In other words, the jth
coefficient of yi is a projection on to the jth row of P. This is
in fact the very form of an equation where yi is a projection
on to the basis of {p1 , . . . , pm }. Therefore, the rows of P are a
new set of basis vectors for representing of columns of X.

C. Questions Remaining

By assuming linearity the problem reduces to finding the appropriate change of basis. The row vectors {p1 , . . . , pm } in
this transformation will become the principal components of
X. Several questions now arise.
• What is the best way to re-express X?

(1)

Also let us define the following quantities.1
• pi are the rows of P
• xi are the columns of X (or individual ~X).
• yi are the columns of Y.

• What is a good choice of basis P?
These questions must be answered by next asking ourselves
what features we would like Y to exhibit. Evidently, additional assumptions beyond linearity are required to arrive at
a reasonable result. The selection of these assumptions is the
subject of the next section.

Equation 1 represents a change of basis and thus can have
many interpretations.
IV. VARIANCE AND THE GOAL

1. P is a matrix that transforms X into Y.
2. Geometrically, P is a rotation and a stretch which again
transforms X into Y.
3. The rows of P, {p1 , . . . , pm }, are a set of new basis vectors for expressing the columns of X.
The latter interpretation is not obvious but can be seen by writing out the explicit dot products of PX.


p1



PX =  ...  x1 · · · xn
pm


p1 · x1 · · · p1 · xn


..
..
..
Y = 

.
.
.
pm · x1 · · · pm · xn

Now comes the most important question: what does best express the data mean? This section will build up an intuitive
answer to this question and along the way tack on additional
assumptions.

A. Noise and Rotation

Measurement noise in any data set must be low or else, no
matter the analysis technique, no information about a signal
can be extracted. There exists no absolute scale for noise but
rather all noise is quantified relative to the signal strength. A
common measure is the signal-to-noise ratio (SNR), or a ratio
of variances σ2 ,
SNR =

1 In this section x and y are column vectors, but be forewarned. In all other
i
i

sections xi and yi are row vectors.

σ2signal
σ2noise

.

A high SNR ( 1) indicates a high precision measurement,
while a low SNR indicates very noisy data.

4

2
σsignal
2
σnoise

y

x

r2

r2
r1

r2
r1

low redundancy

FIG. 2 Simulated data of (x, y) for camera A. The signal and noise
variances σ2signal and σ2noise are graphically represented by the two
lines subtending the cloud of data. Note that the largest direction
of variance does not lie along the basis of the recording (xA , yA ) but
rather along the best-fit line.

Let’s take a closer examination of the data from camera
A in Figure 2. Remembering that the spring travels in a
straight line, every individual camera should record motion in
a straight line as well. Therefore, any spread deviating from
straight-line motion is noise. The variance due to the signal
and noise are indicated by each line in the diagram. The ratio
of the two lengths measures how skinny the cloud is: possibilities include a thin line (SNR  1), a circle (SNR = 1) or even
worse. By positing reasonably good measurements, quantitatively we assume that directions with largest variances in our
measurement space contain the dynamics of interest. In Figure 2 the direction with the largest variance is not x̂A = (1, 0)
nor ŷA = (0, 1), but the direction along the long axis of the
cloud. Thus, by assumption the dynamics of interest exist
along directions with largest variance and presumably highest SNR.
Our assumption suggests that the basis for which we are
searching is not the naive basis because these directions (i.e.
(xA , yA )) do not correspond to the directions of largest variance. Maximizing the variance (and by assumption the SNR)
corresponds to finding the appropriate rotation of the naive
basis. This intuition corresponds to finding the direction indicated by the line σ2signal in Figure 2. In the 2-dimensional case
of Figure 2 the direction of largest variance corresponds to the
best-fit line for the data cloud. Thus, rotating the naive basis
to lie parallel to the best-fit line would reveal the direction of
motion of the spring for the 2-D case. How do we generalize
this notion to an arbitrary number of dimensions? Before we
approach this question we need to examine this issue from a
second perspective.

r1
high redundancy

FIG. 3 A spectrum of possible redundancies in data from the two
separate measurements r1 and r2 . The two measurements on the
left are uncorrelated because one can not predict one from the other.
Conversely, the two measurements on the right are highly correlated
indicating highly redundant measurements.

recordings with no apparent relationship. Because one can not
predict r1 from r2 , one says that r1 and r2 are uncorrelated.
On the other extreme, the right-hand panel of Figure 3 depicts highly correlated recordings. This extremity might be
achieved by several means:
• A plot of (xA , xB ) if cameras A and B are very nearby.
• A plot of (xA , x̃A ) where xA is in meters and x̃A is in
inches.
Clearly in the right panel of Figure 3 it would be more meaningful to just have recorded a single variable, not both. Why?
Because one can calculate r1 from r2 (or vice versa) using the
best-fit line. Recording solely one response would express the
data more concisely and reduce the number of sensor recordings (2 → 1 variables). Indeed, this is the central idea behind
dimensional reduction.

C. Covariance Matrix

In a 2 variable case it is simple to identify redundant cases by
finding the slope of the best-fit line and judging the quality of
the fit. How do we quantify and generalize these notions to
arbitrarily higher dimensions? Consider two sets of measurements with zero means
A = {a1 , a2 , . . . , an } , B = {b1 , b2 , . . . , bn }

B. Redundancy

Figure 2 hints at an additional confounding factor in our data
- redundancy. This issue is particularly evident in the example
of the spring. In this case multiple sensors record the same
dynamic information. Reexamine Figure 2 and ask whether
it was really necessary to record 2 variables. Figure 3 might
reflect a range of possibile plots between two arbitrary measurement types r1 and r2 . The left-hand panel depicts two

where the subscript denotes the sample number. The variance
of A and B are individually defined as,
σ2A =

1
1
a2i , σ2B = ∑ b2i
n∑
n i
i

The covariance between A and B is a straight-forward generalization.
covariance o f A and B ≡ σ2AB =

1
ai bi
n∑
i

5
• The off-diagonal terms of CX are the covariance between measurement types.

The covariance measures the degree of the linear relationship
between two variables. A large positive value indicates positively correlated data. Likewise, a large negative value denotes negatively correlated data. The absolute magnitude of
the covariance measures the degree of redundancy. Some additional facts about the covariance.

CX captures the covariance between all possible pairs of measurements. The covariance values reflect the noise and redundancy in our measurements.

• σAB is zero if and only if A and B are uncorrelated (e.g.
Figure 2, left panel).

• In the diagonal terms, by assumption, large values correspond to interesting structure.

• σ2AB = σ2A if A = B.

• In the off-diagonal terms large magnitudes correspond
to high redundancy.

We can equivalently convert A and B into corresponding row
vectors.
a = [a1 a2 . . . an ]
b = [b1 b2 . . . bn ]
so that we may express the covariance as a dot product matrix
computation.2
1
σ2ab ≡ abT
n

(2)

Finally, we can generalize from two vectors to an arbitrary
number. Rename the row vectors a and b as x1 and x2 , respectively, and consider additional indexed row vectors x3 , . . . , xm .
Define a new m × n matrix X.


x1


X =  ... 
xm
One interpretation of X is the following. Each row of X corresponds to all measurements of a particular type. Each column
of X corresponds to a set of measurements from one particular
trial (this is ~X from section 3.1). We now arrive at a definition
for the covariance matrix CX .
1
CX ≡ XXT .
n
Consider the matrix CX = 1n XXT . The i jth element of CX
is the dot product between the vector of the ith measurement
type with the vector of the jth measurement type. We can
summarize several properties of CX :
• CX is a square symmetric m × m matrix (Theorem 2 of
Appendix A)
• The diagonal terms of CX are the variance of particular
measurement types.

Pretend we have the option of manipulating CX . We will suggestively define our manipulated covariance matrix CY . What
features do we want to optimize in CY ?

D. Diagonalize the Covariance Matrix

We can summarize the last two sections by stating that our
goals are (1) to minimize redundancy, measured by the magnitude of the covariance, and (2) maximize the signal, measured by the variance. What would the optimized covariance
matrix CY look like?
• All off-diagonal terms in CY should be zero. Thus, CY
must be a diagonal matrix. Or, said another way, Y is
decorrelated.
• Each successive dimension in Y should be rank-ordered
according to variance.
There are many methods for diagonalizing CY . It is curious to
note that PCA arguably selects the easiest method: PCA assumes that all basis vectors {p1 , . . . , pm } are orthonormal, i.e.
P is an orthonormal matrix. Why is this assumption easiest?
Envision how PCA works. In our simple example in Figure 2,
P acts as a generalized rotation to align a basis with the axis
of maximal variance. In multiple dimensions this could be
performed by a simple algorithm:
1. Select a normalized direction in m-dimensional space
along which the variance in X is maximized. Save this
vector as p1 .
2. Find another direction along which variance is maximized, however, because of the orthonormality condition, restrict the search to all directions orthogonal to
all previous selected directions. Save this vector as pi
3. Repeat this procedure until m vectors are selected.
The resulting ordered set of p’s are the principal components.

2 Note that in practice, the covariance σ2 is calculated as 1
AB
n−1 ∑i ai bi . The

slight change in normalization constant arises from estimation theory, but
that is beyond the scope of this tutorial.

In principle this simple algorithm works, however that would
bely the true reason why the orthonormality assumption is judicious. The true benefit to this assumption is that there exists

6
an efficient, analytical solution to this problem. We will discuss two solutions in the following sections.
Notice what we gained with the stipulation of rank-ordered
variance. We have a method for judging the importance of
the principal direction. Namely, the variances associated with
each direction pi quantify how “principal” each direction is
by rank-ordering each basis vector pi according to the corresponding variances.We will now pause to review the implications of all the assumptions made to arrive at this mathematical goal.

E. Summary of Assumptions

This section provides a summary of the assumptions behind PCA and hint at when these assumptions might perform
poorly.
I. Linearity
Linearity frames the problem as a change of basis. Several areas of research have explored how
extending these notions to nonlinear regimes (see
Discussion).
II. Large variances have important structure.
This assumption also encompasses the belief that
the data has a high SNR. Hence, principal components with larger associated variances represent
interesting structure, while those with lower variances represent noise. Note that this is a strong,
and sometimes, incorrect assumption (see Discussion).
III. The principal components are orthogonal.
This assumption provides an intuitive simplification that makes PCA soluble with linear algebra
decomposition techniques. These techniques are
highlighted in the two following sections.
We have discussed all aspects of deriving PCA - what remain
are the linear algebra solutions. The first solution is somewhat straightforward while the second solution involves understanding an important algebraic decomposition.

V. SOLVING PCA USING EIGENVECTOR DECOMPOSITION

We derive our first algebraic solution to PCA based on an important property of eigenvector decomposition. Once again,
the data set is X, an m × n matrix, where m is the number of
measurement types and n is the number of samples. The goal
is summarized as follows.
Find some orthonormal matrix P in Y = PX such
that CY ≡ 1n YYT is a diagonal matrix. The rows
of P are the principal components of X.

We begin by rewriting CY in terms of the unknown variable.
1
YYT
n
1
= (PX)(PX)T
n
1
= PXXT PT
n
1
= P( XXT )PT
n
CY = PCX PT
CY =

Note that we have identified the covariance matrix of X in the
last line.
Our plan is to recognize that any symmetric matrix A is diagonalized by an orthogonal matrix of its eigenvectors (by Theorems 3 and 4 from Appendix A). For a symmetric matrix A
Theorem 4 provides A = EDET , where D is a diagonal matrix
and E is a matrix of eigenvectors of A arranged as columns.3
Now comes the trick. We select the matrix P to be a matrix
where each row pi is an eigenvector of n1 XXT . By this selection, P ≡ ET . With this relation and Theorem 1 of Appendix
A (P−1 = PT ) we can finish evaluating CY .
CY = PCX PT
= P(ET DE)PT
= P(PT DP)PT
= (PPT )D(PPT )
= (PP−1 )D(PP−1 )
CY = D
It is evident that the choice of P diagonalizes CY . This was
the goal for PCA. We can summarize the results of PCA in the
matrices P and CY .
• The principal components of X are the eigenvectors of
CX = 1n XXT .
• The ith diagonal value of CY is the variance of X along
pi .
In practice computing PCA of a data set X entails (1) subtracting off the mean of each measurement type and (2) computing
the eigenvectors of CX . This solution is demonstrated in Matlab code included in Appendix B.

3 The matrix A might have r ≤ m orthonormal eigenvectors where r is the

rank of the matrix. When the rank of A is less than m, A is degenerate or all
data occupy a subspace of dimension r ≤ m. Maintaining the constraint of
orthogonality, we can remedy this situation by selecting (m − r) additional
orthonormal vectors to “fill up” the matrix E. These additional vectors
do not effect the final solution because the variances associated with these
directions are zero.

7
VI. A MORE GENERAL SOLUTION USING SVD

This section is the most mathematically involved and can be
skipped without much loss of continuity. It is presented solely
for completeness. We derive another algebraic solution for
PCA and in the process, find that PCA is closely related to
singular value decomposition (SVD). In fact, the two are so
intimately related that the names are often used interchangeably. What we will see though is that SVD is a more general
method of understanding change of basis.
We begin by quickly deriving the decomposition. In the following section we interpret the decomposition and in the last
section we relate these results to PCA.

A. Singular Value Decomposition

Let X be an arbitrary n × m matrix4 and XT X be a rank r,
square, symmetric m × m matrix. In a seemingly unmotivated
fashion, let us define all of the quantities of interest.
• {v̂1 , v̂2 , . . . , v̂r } is the set of orthonormal m × 1 eigenvectors with associated eigenvalues {λ1 , λ2 , . . . , λr } for
the symmetric matrix XT X.
(XT X)v̂i = λi v̂i
√
• σi ≡ λi are positive real and termed the singular values.
• {û1 , û2 , . . . , ûr } is the set of n × 1 vectors defined by
ûi ≡ σ1i Xv̂i .
The final definition includes two new and unexpected properties.

• ûi · ûj =

1 if i = j
0 otherwise

• kXv̂i k = σi
These properties are both proven in Theorem 5. We now have
all of the pieces to construct the decomposition. The scalar
version of singular value decomposition is just a restatement
of the third definition.
Xv̂i = σi ûi

The set of eigenvectors {v̂1 , v̂2 , . . . , v̂r } and the set of vectors {û1 , û2 , . . . , ûr } are both orthonormal sets or bases in rdimensional space.
We can summarize this result for all vectors in one matrix
multiplication by following the prescribed construction in Figure 4. We start by constructing a new diagonal matrix Σ.


σ1̃


..


.




σ
r̃


Σ≡

0




.


..

0

0

0

where σ1̃ ≥ σ2̃ ≥ . . . ≥ σr̃ are the rank-ordered set of singular values. Likewise we construct accompanying orthogonal
matrices,


V = v̂1̃ v̂2̃ . . . v̂m̃


U = û1̃ û2̃ . . . ûñ
where we have appended an additional (m − r) and (n − r) orthonormal vectors to “fill up” the matrices for V and U respectively (i.e. to deal with degeneracy issues). Figure 4 provides
a graphical representation of how all of the pieces fit together
to form the matrix version of SVD.
XV = UΣ
where each column of V and U perform the scalar version of
the decomposition (Equation 3). Because V is orthogonal, we
can multiply both sides by V−1 = VT to arrive at the final form
of the decomposition.
X = UΣVT

(4)

Although derived without motivation, this decomposition is
quite powerful. Equation 4 states that any arbitrary matrix X
can be converted to an orthogonal matrix, a diagonal matrix
and another orthogonal matrix (or a rotation, a stretch and a
second rotation). Making sense of Equation 4 is the subject of
the next section.

B. Interpreting SVD

The final form of SVD is a concise but thick statement. Instead let us reinterpret Equation 3 as

(3)
Xa = kb

This result says a quite a bit. X multiplied by an eigenvector of XT X is equal to a scalar times another vector.

4 Notice that in this section only we are reversing convention from m × n to

n × m. The reason for this derivation will become clear in section 6.3.

where a and b are column vectors and k is a scalar constant. The set {v̂1 , v̂2 , . . . , v̂m } is analogous to a and the set
{û1 , û2 , . . . , ûn } is analogous to b. What is unique though is
that {v̂1 , v̂2 , . . . , v̂m } and {û1 , û2 , . . . , ûn } are orthonormal sets
of vectors which span an m or n dimensional space, respectively. In particular, loosely speaking these sets appear to span

8
The scalar form of SVD is expressed in equation 3.

Xv̂i = σi ûi
The mathematical intuition behind the construction of the matrix form is that we want to express all n scalar equations in just one
equation. It is easiest to understand this process graphically. Drawing the matrices of equation 3 looks likes the following.

We can construct three new matrices V, U and Σ. All singular values are first rank-ordered σ1̃ ≥ σ2̃ ≥ . . . ≥ σr̃ , and the corresponding vectors are indexed in the same rank order. Each pair of associated vectors v̂i and ûi is stacked in the ith column along
their respective matrices. The corresponding singular value σi is placed along the diagonal (the iith position) of Σ. This generates
the equation XV = UΣ, which looks like the following.

The matrices V and U are m × m and n × n matrices respectively and Σ is a diagonal matrix with a few non-zero values (represented by the checkerboard) along its diagonal. Solving this single matrix equation solves all n “value” form equations.

FIG. 4 Construction of the matrix form of SVD (Equation 4) from the scalar form (Equation 3).

all possible “inputs” (i.e. a) and “outputs” (i.e. b). Can we
formalize the view that {v̂1 , v̂2 , . . . , v̂n } and {û1 , û2 , . . . , ûn }
span all possible “inputs” and “outputs”?

similar quantity - the row space.
XV = ΣU
(XV)T = (ΣU)T
VT XT = UT Σ
VT XT = Z

We can manipulate Equation 4 to make this fuzzy hypothesis
more precise.

X = UΣVT
UT X = ΣVT
UT X = Z

where we have defined Z ≡ UT Σ. Again the rows of VT (or
the columns of V) are an orthonormal basis for transforming
XT into Z. Because of the transpose on X, it follows that V
is an orthonormal basis spanning the row space of X. The
row space likewise formalizes the notion of what are possible
“inputs” into an arbitrary matrix.

where we have defined Z ≡ ΣVT . Note that the previous
columns {û1 , û2 , . . . , ûn } are now rows in UT . Comparing this
equation to Equation 1, {û1 , û2 , . . . , ûn } perform the same role
as {p̂1 , p̂2 , . . . , p̂m }. Hence, UT is a change of basis from X to
Z. Just as before, we were transforming column vectors, we
can again infer that we are transforming column vectors. The
fact that the orthonormal basis UT (or P) transforms column
vectors means that UT is a basis that spans the columns of X.
Bases that span the columns are termed the column space of
X. The column space formalizes the notion of what are the
possible “outputs” of any matrix.

We are only scratching the surface for understanding the full
implications of SVD. For the purposes of this tutorial though,
we have enough information to understand how PCA will fall
within this framework.

There is a funny symmetry to SVD such that we can define a

C. SVD and PCA

It is evident that PCA and SVD are intimately related. Let us
return to the original m × n data matrix X. We can define a

9
Quick Summary of PCA

A

B

1. Organize data as an m × n matrix, where m is the number
of measurement types and n is the number of samples.
θ

2. Subtract off the mean for each measurement type.
3. Calculate the SVD or the eigenvectors of the covariance.

y

z

FIG. 5 A step-by-step instruction list on how to perform principal
component analysis

x

x

y

new matrix Y as an n × m matrix.5
1
Y ≡ √ XT
n
where each column of Y has zero mean. The choice of Y
becomes clear by analyzing YT Y.

 

1 T T
1 T
T
√ X
Y Y = √ X
n
n
1
= XXT
n
T
Y Y = CX
By construction YT Y equals the covariance matrix of X. From
section 5 we know that the principal components of X are
the eigenvectors of CX . If we calculate the SVD of Y, the
columns of matrix V contain the eigenvectors of YT Y = CX .
Therefore, the columns of V are the principal components of
X. This second algorithm is encapsulated in Matlab code included in Appendix B.
What does this mean? V spans the row space of Y ≡ √1n XT .
Therefore, V must also span the column space of √1n X. We
can conclude that finding the principal components amounts
to finding an orthonormal basis that spans the column space
of X.6

VII. DISCUSSION

Principal component analysis (PCA) has widespread applications because it reveals simple underlying structures in complex data sets using analytical solutions from linear algebra.
Figure 5 provides a brief summary for implementing PCA.
A primary benefit of PCA arises from quantifying the importance of each dimension for describing the variability of a data
set. In particular, the measurement of the variance along each

5 Y is of the appropriate n×m dimensions laid out in the derivation of section

6.1. This is the reason for the “flipping” of dimensions in 6.1 and Figure 4.
6 If the final goal is to find an orthonormal basis for the coulmn space of

X then we can calculate it directly without constructing Y. By symmetry
the columns of U produced by the SVD of √1n X must also be the principal
components.

FIG. 6 Example of when PCA fails (red lines). (a) Tracking a person on a ferris wheel (black dots). All dynamics can be described
by the phase of the wheel θ, a non-linear combination of the naive
basis. (b) In this example data set, non-Gaussian distributed data and
non-orthogonal axes causes PCA to fail. The axes with the largest
variance do not correspond to the appropriate answer.

principle component provides a means for comparing the relative importance of each dimension. An implicit hope behind
employing this method is that the variance along a small number of principal components (i.e. less than the number of measurement types) provides a reasonable characterization of the
complete data set. This statement is the precise intuition behind any method of dimensional reduction – a vast arena of
active research. In the example of the spring, PCA identifies that a majority of variation exists along a single dimension (the direction of motion x̂), eventhough 6 dimensions are
recorded.
Although PCA “works” on a multitude of real world problems, any diligent scientist or engineer must ask when does
PCA fail? Before we answer this question, let us note a remarkable feature of this algorithm. PCA is completely nonparametric: any data set can be plugged in and an answer
comes out, requiring no parameters to tweak and no regard for
how the data was recorded. From one perspective, the fact that
PCA is non-parametric (or plug-and-play) can be considered
a positive feature because the answer is unique and independent of the user. From another perspective the fact that PCA
is agnostic to the source of the data is also a weakness. For
instance, consider tracking a person on a ferris wheel in Figure 6a. The data points can be cleanly described by a single
variable, the precession angle of the wheel θ, however PCA
would fail to recover this variable.

A. Limits and Statistics of Dimensional Reduction

A deeper appreciation of the limits of PCA requires some consideration about the underlying assumptions and in tandem,
a more rigorous description of the source of data. Generally speaking, the primary motivation behind this method is
to decorrelate the data set, i.e. remove second-order dependencies. The manner of approaching this goal is loosely akin
to how one might explore a town in the Western United States:
drive down the longest road running through the town. When

10
one sees another big road, turn left or right and drive down
this road, and so forth. In this analogy, PCA requires that each
new road explored must be perpendicular to the previous, but
clearly this requirement is overly stringent and the data (or
town) might be arranged along non-orthogonal axes, such as
Figure 6b. Figure 6 provides two examples of this type of data
where PCA provides unsatisfying results.
To address these problems, we must define what we consider
optimal results. In the context of dimensional reduction, one
measure of success is the degree to which a reduced representation can predict the original data. In statistical terms,
we must define an error function (or loss function). It can
be proved that under a common loss function, mean squared
error (i.e. L2 norm), PCA provides the optimal reduced representation of the data. This means that selecting orthogonal
directions for principal components is the best solution to predicting the original data. Given the examples of Figure 6, how
could this statement be true? Our intuitions from Figure 6
suggest that this result is somehow misleading.
The solution to this paradox lies in the goal we selected for the
analysis. The goal of the analysis is to decorrelate the data, or
said in other terms, the goal is to remove second-order dependencies in the data. In the data sets of Figure 6, higher order
dependencies exist between the variables. Therefore, removing second-order dependencies is insufficient at revealing all
structure in the data.7
Multiple solutions exist for removing higher-order dependencies. For instance, if prior knowledge is known about the
problem, then a nonlinearity (i.e. kernel) might be applied
to the data to transform the data to a more appropriate naive
basis. For instance, in Figure 6a, one might examine the polar coordinate representation of the data. This parametric approach is often termed kernel PCA.
Another direction is to impose more general statistical definitions of dependency within a data set, e.g. requiring that data
along reduced dimensions be statistically independent. This
class of algorithms, termed, independent component analysis
(ICA), has been demonstrated to succeed in many domains
where PCA fails. ICA has been applied to many areas of signal and image processing, but suffers from the fact that solutions are (sometimes) difficult to compute.
Writing this paper has been an extremely instructional experience for me. I hope that this paper helps to demystify the
motivation and results of PCA, and the underlying assumptions behind this important analysis technique. Please send
me a note if this has been useful to you as it inspires me to
keep writing!

7 When are second order dependencies sufficient for revealing all dependen-

cies in a data set? This statistical condition is met when the first and second
order statistics are sufficient statistics of the data. This occurs, for instance,
when a data set is Gaussian distributed.

Appendix A: Linear Algebra

This section proves a few unapparent theorems in linear
algebra, which are crucial to this paper.
1. The inverse of an orthogonal matrix is its transpose.
Let A be an m×n orthogonal matrix where ai is the ith column
vector. The i jth element of AT A is

1 if i = j
T
T
(A A)i j = ai aj =
0 otherwise
Therefore, because AT A = I, it follows that A−1 = AT .
2. For any matrix A, AT A and AAT are symmetric.
(AAT )T = AT T AT = AAT
(AT A)T = AT AT T = AT A
3. A matrix is symmetric if and only if it is orthogonally
diagonalizable.
Because this statement is bi-directional, it requires a two-part
“if-and-only-if” proof. One needs to prove the forward and
the backwards “if-then” cases.
Let us start with the forward case. If A is orthogonally diagonalizable, then A is a symmetric matrix. By hypothesis,
orthogonally diagonalizable means that there exists some E
such that A = EDET , where D is a diagonal matrix and E is
some special matrix which diagonalizes A. Let us compute
AT .
AT = (EDET )T = ET T DT ET = EDET = A
Evidently, if A is orthogonally diagonalizable, it must also be
symmetric.
The reverse case is more involved and less clean so it will be
left to the reader. In lieu of this, hopefully the “forward” case
is suggestive if not somewhat convincing.
4. A symmetric matrix is diagonalized by a matrix of its
orthonormal eigenvectors.
Let A be a square n × n symmetric matrix with associated
eigenvectors {e1 , e2 , . . . , en }. Let E = [e1 e2 . . . en ] where the
ith column of E is the eigenvector ei . This theorem asserts that
there exists a diagonal matrix D such that A = EDET .
This proof is in two parts. In the first part, we see that the
any matrix can be orthogonally diagonalized if and only if
it that matrix’s eigenvectors are all linearly independent. In
the second part of the proof, we see that a symmetric matrix

11
has the special property that all of its eigenvectors are not just
linearly independent but also orthogonal, thus completing our
proof.
In the first part of the proof, let A be just some matrix, not
necessarily symmetric, and let it have independent eigenvectors (i.e. no degeneracy). Furthermore, let E = [e1 e2 . . . en ]
be the matrix of eigenvectors placed in the columns. Let D be
a diagonal matrix where the ith eigenvalue is placed in the iith
position.
We will now show that AE = ED. We can examine the
columns of the right-hand and left-hand sides of the equation.
Left hand side : AE = [Ae1 Ae2 . . . Aen ]
Right hand side : ED = [λ1 e1 λ2 e2 . . . λn en ]
Evidently, if AE = ED then Aei = λi ei for all i. This equation is the definition of the eigenvalue equation. Therefore,
it must be that AE = ED. A little rearrangement provides
A = EDE−1 , completing the first part the proof.
For the second part of the proof, we show that a symmetric
matrix always has orthogonal eigenvectors. For some symmetric matrix, let λ1 and λ2 be distinct eigenvalues for eigenvectors e1 and e2 .
λ1 e1 · e2 = (λ1 e1 )T e2
= (Ae1 )T e2
= e1 T AT e2
= e1 T Ae2
= e1 T (λ2 e2 )
λ1 e1 · e2 = λ2 e1 · e2
By the last relation we can equate that (λ1 − λ2 )e1 · e2 = 0.
Since we have conjectured that the eigenvalues are in fact
unique, it must be the case that e1 · e2 = 0. Therefore, the
eigenvectors of a symmetric matrix are orthogonal.
Let us back up now to our original postulate that A is a symmetric matrix. By the second part of the proof, we know
that the eigenvectors of A are all orthonormal (we choose
the eigenvectors to be normalized). This means that E is an
orthogonal matrix so by theorem 1, ET = E−1 and we can
rewrite the final result.

All of these properties arise from the dot product of any two
vectors from this set.
(Xv̂i ) · (Xv̂j ) = (Xv̂i )T (Xv̂j )
= v̂Ti XT Xv̂j
= v̂Ti (λ j v̂j )
= λ j v̂i · v̂j
(Xv̂i ) · (Xv̂j ) = λ j δi j

The last relation arises because the set of eigenvectors of X is
orthogonal resulting in the Kronecker delta. In more simpler
terms the last relation states:

λj i = j
(Xv̂i ) · (Xv̂j ) =
0 i 6= j
This equation states that any two vectors in the set are orthogonal.
The second property arises from the above equation by realizing that the length squared of each vector is defined as:
kXv̂i k2 = (Xv̂i ) · (Xv̂i ) = λi

Appendix B: Code

This code is written for Matlab 6.5 (Release 13) from
Mathworks8 .
The code is not computationally efficient but explanatory (terse comments begin with a %).
This first version follows Section 5 by examining the
covariance of the data set.
function [signals,PC,V] = pca1(data)
% PCA1: Perform PCA using covariance.
%
data - MxN matrix of input data
%
(M dimensions, N trials)
% signals - MxN matrix of projected data
%
PC - each column is a PC
%
V - Mx1 matrix of variances
[M,N] = size(data);

T

A = EDE

. Thus, a symmetric matrix is diagonalized by a matrix of its
eigenvectors.
5. For any arbitrary m × n matrix X, the symmetric
matrix XT X has a set of orthonormal eigenvectors
of {v̂1 , v̂2 , . . . , v̂n } and a set of associated eigenvalues
{λ1 , λ2 , . . . , λn }. The set of vectors {Xv̂1 , Xv̂2 , . . . , Xv̂n }
then form
√ an orthogonal basis, where each vector Xv̂i is of
length λi .

% subtract off the mean for each dimension
mn = mean(data,2);
data = data - repmat(mn,1,N);
% calculate the covariance matrix
covariance = 1 / (N-1) * data * data’;
% find the eigenvectors and eigenvalues

8 http://www.mathworks.com

12
[PC, V] = eig(covariance);

%

% extract diagonal of matrix as vector
V = diag(V);

[M,N] = size(data);

% sort the variances in decreasing order
[junk, rindices] = sort(-1*V);
V = V(rindices);
PC = PC(:,rindices);
% project the original data set
signals = PC’ * data;
This second version follows section 6 computing PCA
through SVD.
function [signals,PC,V] = pca2(data)
% PCA2: Perform PCA using SVD.
%
data - MxN matrix of input data
%
(M dimensions, N trials)
% signals - MxN matrix of projected data
%
PC - each column is a PC

V - Mx1 matrix of variances

% subtract off the mean for each dimension
mn = mean(data,2);
data = data - repmat(mn,1,N);
% construct the matrix Y
Y = data’ / sqrt(N-1);
% SVD does it all
[u,S,PC] = svd(Y);
% calculate the variances
S = diag(S);
V = S .* S;
% project the original data
signals = PC’ * data;


