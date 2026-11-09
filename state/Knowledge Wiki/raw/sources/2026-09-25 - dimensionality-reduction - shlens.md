<!-- source: https://arxiv.org/abs/1404.1100 | type: pdf | hash: 985c0b558486c40a931de6699109f00d2b86694769530fa84b05a9abe7385937 | fetched: 2026-09-25T07:55:06Z -->

A Tutorial on Principal Component Analysis
                                                 Jonathon Shlens∗
                                                 Google    Research
                                                 Mountain View, CA 94043
                                                 (Dated: April 7, 2014; Version 3.02)
                                                 Principal component analysis (PCA) is a mainstay of modern data analysis - a black box that is widely used
                                                 but (sometimes) poorly understood. The goal of this paper is to dispel the magic behind this black box. This
                                                 manuscript focuses on building a solid intuition for how and why principal component analysis works. This
                                                 manuscript crystallizes this knowledge by deriving from simple intuitions, the mathematics behind PCA. This
                                                 tutorial does not shy away from explaining the ideas informally, nor does it shy away from the mathematics. The
arXiv:1404.1100v1 [cs.LG] 3 Apr 2014
                                                 hope is that by addressing both aspects, readers of all levels will be able to gain a better understanding of PCA as
                                                 well as the when, the how and the why of applying this technique.
                                       I. INTRODUCTION                                                                    II. MOTIVATION: A TOY EXAMPLE
                                       Principal component analysis (PCA) is a standard tool in mod-                      Here is the perspective: we are an experimenter. We are trying
                                       ern data analysis - in diverse fields from neuroscience to com-                    to understand some phenomenon by measuring various quan-
                                       puter graphics - because it is a simple, non-parametric method                     tities (e.g. spectra, voltages, velocities, etc.) in our system.
                                       for extracting relevant information from confusing data sets.                      Unfortunately, we can not figure out what is happening be-
                                       With minimal effort PCA provides a roadmap for how to re-                          cause the data appears clouded, unclear and even redundant.
                                       duce a complex data set to a lower dimension to reveal the                         This is not a trivial problem, but rather a fundamental obstacle
                                       sometimes hidden, simplified structures that often underlie it.                    in empirical science. Examples abound from complex sys-
                                                                                                                          tems such as neuroscience, web indexing, meteorology and
                                       The goal of this tutorial is to provide both an intuitive feel for                 oceanography - the number of variables to measure can be
                                       PCA, and a thorough discussion of this topic. We will begin                        unwieldy and at times even deceptive, because the underlying
                                       with a simple example and provide an intuitive explanation                         relationships can often be quite simple.
                                       of the goal of PCA. We will continue by adding mathemati-
                                       cal rigor to place it within the framework of linear algebra to                    Take for example a simple toy problem from physics dia-
                                       provide an explicit solution. We will see how and why PCA                          grammed in Figure 1. Pretend we are studying the motion
                                       is intimately related to the mathematical technique of singular                    of the physicist’s ideal spring. This system consists of a ball
                                       value decomposition (SVD). This understanding will lead us                         of mass m attached to a massless, frictionless spring. The ball
                                       to a prescription for how to apply PCA in the real world and an                    is released a small distance away from equilibrium (i.e. the
                                       appreciation for the underlying assumptions. My hope is that                       spring is stretched). Because the spring is ideal, it oscillates
                                       a thorough understanding of PCA provides a foundation for                          indefinitely along the x-axis about its equilibrium at a set fre-
                                       approaching the fields of machine learning and dimensional                         quency.
                                       reduction.
                                                                                                                          This is a standard problem in physics in which the motion
                                       The discussion and explanations in this paper are informal in                      along the x direction is solved by an explicit function of time.
                                       the spirit of a tutorial. The goal of this paper is to educate.                    In other words, the underlying dynamics can be expressed as
                                       Occasionally, rigorous mathematical proofs are necessary al-                       a function of a single variable x.
                                       though relegated to the Appendix. Although not as vital to the
                                       tutorial, the proofs are presented for the adventurous reader                      However, being ignorant experimenters we do not know any
                                       who desires a more complete understanding of the math. My                          of this. We do not know which, let alone how many, axes
                                       only assumption is that the reader has a working knowledge                         and dimensions are important to measure. Thus, we decide to
                                       of linear algebra. My goal is to provide a thorough discussion                     measure the ball’s position in a three-dimensional space (since
                                       by largely building on ideas from linear algebra and avoiding                      we live in a three dimensional world). Specifically, we place
                                       challenging topics in statistics and optimization theory (but                      three movie cameras around our system of interest. At 120 Hz
                                       see Discussion). Please feel free to contact me with any sug-                      each movie camera records an image indicating a two dimen-
                                       gestions, corrections or comments.                                                 sional position of the ball (a projection). Unfortunately, be-
                                                                                                                          cause of our ignorance, we do not even know what are the real
                                                                                                                          x, y and z axes, so we choose three camera positions~a,~b and~c
                                                                                                                          at some arbitrary angles with respect to the system. The angles
                                       ∗ Electronic address: jonathon.shlens@gmail.com                                    between our measurements might not even be 90o ! Now, we
                                                                                                                          record with the cameras for several minutes. The big question
                                                                                                                          remains: how do we get from this data set to a simple equation
                                                                                                                                            2
                                                                        A. A Naive Basis
                                                                        With a more precise definition of our goal, we need a more
                                                                        precise definition of our data as well. We treat every time
                                                                        sample (or experimental trial) as an individual sample in our
                                                                        data set. At each time sample we record a set of data consist-
                                                                        ing of multiple measurements (e.g. voltage, position, etc.). In
                                                                        our data set, at one point in time, camera A records a corre-
                                                                        sponding ball position (xA , yA ). One sample or trial can then
                                                                        be expressed as a 6 dimensional column vector
                                                                                                          xA
                                                                                                            
                                                                                                        yA 
                                                                                                          x 
                                                                                                            
        camera A             camera B               camera C
                                                                                                 ~X =  B
                                                                                                        yB 
                                                                                                       x 
                                                                                                           C
                                                                                                          yC
                                                                        where each camera contributes a 2-dimensional projection of
                                                                        the ball’s position to the entire vector ~X. If we record the ball’s
                                                                        position for 10 minutes at 120 Hz, then we have recorded 10×
                                                                        60 × 120 = 72000 of these vectors.
FIG. 1 A toy example. The position of a ball attached to an oscillat-
ing spring is recorded using three cameras A, B and C. The position     With this concrete example, let us recast this problem in ab-
of the ball tracked by each camera is depicted in each panel below.     stract terms. Each sample ~X is an m-dimensional vector,
                                                                        where m is the number of measurement types. Equivalently,
                                                                        every sample is a vector that lies in an m-dimensional vec-
of x?                                                                   tor space spanned by some orthonormal basis. From linear
                                                                        algebra we know that all measurement vectors form a linear
We know a-priori that if we were smart experimenters, we                combination of this set of unit length basis vectors. What is
would have just measured the position along the x-axis with             this orthonormal basis?
one camera. But this is not what happens in the real world.
We often do not know which measurements best reflect the                This question is usually a tacit assumption often overlooked.
dynamics of our system in question. Furthermore, we some-               Pretend we gathered our toy example data above, but only
times record more dimensions than we actually need.                     looked at camera A. What is an orthonormal basis for (xA , yA )?
                                                                        A naive choice
                                                                                     √ √
                                                                                          would be√ {(1,√0), (0, 1)}, but why select this
Also, we have to deal with that pesky, real-world problem of            basis over {( 22 , 22 ), ( −2 2 , −2 2 )} or any other arbitrary rota-
noise. In the toy example this means that we need to deal               tion? The reason is that the naive basis reflects the method we
with air, imperfect cameras or even friction in a less-than-ideal       gathered the data. Pretend √we √     record the position (2, 2). We
spring. Noise contaminates our data set only serving to obfus-                           √
cate the dynamics further. This toy example is the challenge            did not record 2 2 in the ( 22 , 22 ) direction and 0 in the per-
experimenters face everyday. Keep this example in mind as               pendicular direction. Rather, we recorded the position (2, 2)
we delve further into abstract concepts. Hopefully, by the end          on our camera meaning 2 units up and 2 units to the left in our
of this paper we will have a good understanding of how to               camera window. Thus our original basis reflects the method
systematically extract x using principal component analysis.            we measured our data.
                                                                        How do we express this naive basis in linear algebra? In the
                                                                        two dimensional case, {(1, 0), (0, 1)} can be recast as individ-
                                                                        ual row vectors. A matrix constructed out of these row vectors
III. FRAMEWORK: CHANGE OF BASIS
                                                                        is the 2 × 2 identity matrix I. We can generalize this to the m-
                                                                        dimensional case by constructing an m × m identity matrix
The goal of principal component analysis is to identify the
                                                                                          b1       1 0 ··· 0
                                                                                                               
most meaningful basis to re-express a data set. The hope is
that this new basis will filter out the noise and reveal hidden                          b2   0 1 · · · 0 
                                                                                      B=
                                                                                         ..  =  .. .. . . . ..  = I
                                                                                                                
structure. In the example of the spring, the explicit goal of                              .        . .         .
PCA is to determine: “the dynamics are along the x-axis.” In                              bm       0 0 ··· 1
other words, the goal of PCA is to determine that x̂, i.e. the
unit basis vector along the x-axis, is the important dimension.         where each row is an orthornormal basis vector bi with m
Determining this fact allows an experimenter to discern which           components. We can consider our naive basis as the effective
dynamics are important, redundant or noise.                             starting point. All of our data has been recorded in this basis
                                                                                                                                                   3
and thus it can be trivially expressed as a linear combination                  We can note the form of each column of Y.
of {bi }.                                                                                                           
                                                                                                             p1 · xi
                                                                                                     yi =  ... 
                                                                                                                    
B. Change of Basis                                                                                               pm · xi
                                                                                We recognize that each coefficient of yi is a dot-product of
With this rigor we may now state more precisely what PCA                        xi with the corresponding row in P. In other words, the jth
asks: Is there another basis, which is a linear combination of                  coefficient of yi is a projection on to the jth row of P. This is
the original basis, that best re-expresses our data set?                        in fact the very form of an equation where yi is a projection
A close reader might have noticed the conspicuous addition of                   on to the basis of {p1 , . . . , pm }. Therefore, the rows of P are a
the word linear. Indeed, PCA makes one stringent but power-                     new set of basis vectors for representing of columns of X.
ful assumption: linearity. Linearity vastly simplifies the prob-
lem by restricting the set of potential bases. With this assump-
tion PCA is now limited to re-expressing the data as a linear                   C. Questions Remaining
combination of its basis vectors.
Let X be the original data set, where each column is a single                   By assuming linearity the problem reduces to finding the ap-
sample (or moment in time) of our data set (i.e. ~X). In the toy                propriate change of basis. The row vectors {p1 , . . . , pm } in
example X is an m × n matrix where m = 6 and n = 72000.                         this transformation will become the principal components of
Let Y be another m × n matrix related by a linear transfor-                     X. Several questions now arise.
mation P. X is the original recorded data set and Y is a new
representation of that data set.
                                                                                    • What is the best way to re-express X?
                                 PX = Y                                  (1)
                                                                                    • What is a good choice of basis P?
Also let us define the following quantities.1
    • pi are the rows of P                                                      These questions must be answered by next asking ourselves
                                                                                what features we would like Y to exhibit. Evidently, addi-
    • xi are the columns of X (or individual ~X).                               tional assumptions beyond linearity are required to arrive at
                                                                                a reasonable result. The selection of these assumptions is the
    • yi are the columns of Y.
                                                                                subject of the next section.
Equation 1 represents a change of basis and thus can have
many interpretations.
                                                                                IV. VARIANCE AND THE GOAL
   1. P is a matrix that transforms X into Y.
   2. Geometrically, P is a rotation and a stretch which again                  Now comes the most important question: what does best ex-
      transforms X into Y.                                                      press the data mean? This section will build up an intuitive
                                                                                answer to this question and along the way tack on additional
   3. The rows of P, {p1 , . . . , pm }, are a set of new basis vec-            assumptions.
      tors for expressing the columns of X.
The latter interpretation is not obvious but can be seen by writ-
ing out the explicit dot products of PX.                                        A. Noise and Rotation
                                 
                            p1
                PX =  ...  x1 · · · xn                                        Measurement noise in any data set must be low or else, no
                                              
                                                                                matter the analysis technique, no information about a signal
                           pm                                                   can be extracted. There exists no absolute scale for noise but
                                                  
                            p1 · x1 · · · p1 · xn                               rather all noise is quantified relative to the signal strength. A
                 Y = 
                              ..    ..      ..                                common measure is the signal-to-noise ratio (SNR), or a ratio
                                .       .     .                                 of variances σ2 ,
                                                   
                               pm · x1 · · · pm · xn
                                                                                                                  σ2signal
                                                                                                         SNR =               .
                                                                                                                   σ2noise
1 In this section x and y are column vectors, but be forewarned. In all other
                   i     i
                                                                                A high SNR (
 1) indicates a high precision measurement,
  sections xi and yi are row vectors.                                           while a low SNR indicates very noisy data.
                                                                                                                                                         4
                                                   2
                                                 σsignal
                 y             2
                             σnoise
                         x
                                                                            r2                            r2                          r2
                                                                                    r1                           r1                          r1
                                                                                 low redundancy                                        high redundancy
FIG. 2 Simulated data of (x, y) for camera A. The signal and noise
variances σ2signal and σ2noise are graphically represented by the two      FIG. 3 A spectrum of possible redundancies in data from the two
lines subtending the cloud of data. Note that the largest direction        separate measurements r1 and r2 . The two measurements on the
of variance does not lie along the basis of the recording (xA , yA ) but   left are uncorrelated because one can not predict one from the other.
rather along the best-fit line.                                            Conversely, the two measurements on the right are highly correlated
                                                                           indicating highly redundant measurements.
Let’s take a closer examination of the data from camera                    recordings with no apparent relationship. Because one can not
A in Figure 2. Remembering that the spring travels in a                    predict r1 from r2 , one says that r1 and r2 are uncorrelated.
straight line, every individual camera should record motion in
a straight line as well. Therefore, any spread deviating from              On the other extreme, the right-hand panel of Figure 3 de-
straight-line motion is noise. The variance due to the signal              picts highly correlated recordings. This extremity might be
and noise are indicated by each line in the diagram. The ratio             achieved by several means:
of the two lengths measures how skinny the cloud is: possibil-
ities include a thin line (SNR
 1), a circle (SNR = 1) or even                   • A plot of (xA , xB ) if cameras A and B are very nearby.
worse. By positing reasonably good measurements, quantita-
tively we assume that directions with largest variances in our                    • A plot of (xA , x̃A ) where xA is in meters and x̃A is in
measurement space contain the dynamics of interest. In Fig-                         inches.
ure 2 the direction with the largest variance is not x̂A = (1, 0)
nor ŷA = (0, 1), but the direction along the long axis of the             Clearly in the right panel of Figure 3 it would be more mean-
cloud. Thus, by assumption the dynamics of interest exist                  ingful to just have recorded a single variable, not both. Why?
along directions with largest variance and presumably high-                Because one can calculate r1 from r2 (or vice versa) using the
est SNR.                                                                   best-fit line. Recording solely one response would express the
Our assumption suggests that the basis for which we are                    data more concisely and reduce the number of sensor record-
searching is not the naive basis because these directions (i.e.            ings (2 → 1 variables). Indeed, this is the central idea behind
(xA , yA )) do not correspond to the directions of largest vari-           dimensional reduction.
ance. Maximizing the variance (and by assumption the SNR)
corresponds to finding the appropriate rotation of the naive
basis. This intuition corresponds to finding the direction indi-           C. Covariance Matrix
cated by the line σ2signal in Figure 2. In the 2-dimensional case
of Figure 2 the direction of largest variance corresponds to the
best-fit line for the data cloud. Thus, rotating the naive basis           In a 2 variable case it is simple to identify redundant cases by
to lie parallel to the best-fit line would reveal the direction of         finding the slope of the best-fit line and judging the quality of
motion of the spring for the 2-D case. How do we generalize                the fit. How do we quantify and generalize these notions to
this notion to an arbitrary number of dimensions? Before we                arbitrarily higher dimensions? Consider two sets of measure-
approach this question we need to examine this issue from a                ments with zero means
second perspective.
                                                                                         A = {a1 , a2 , . . . , an } , B = {b1 , b2 , . . . , bn }
                                                                           where the subscript denotes the sample number. The variance
B. Redundancy                                                              of A and B are individually defined as,
                                                                                                          1              1
                                                                                                  σ2A =       a2i , σ2B = ∑ b2i
Figure 2 hints at an additional confounding factor in our data                                            n∑i            n i
- redundancy. This issue is particularly evident in the example
of the spring. In this case multiple sensors record the same               The covariance between A and B is a straight-forward gener-
dynamic information. Reexamine Figure 2 and ask whether                    alization.
it was really necessary to record 2 variables. Figure 3 might
reflect a range of possibile plots between two arbitrary mea-                                                                        1
                                                                                         covariance o f A and B ≡ σ2AB =                 ai bi
surement types r1 and r2 . The left-hand panel depicts two                                                                           n∑i
                                                                                                                                                   5
The covariance measures the degree of the linear relationship                       • The off-diagonal terms of CX are the covariance be-
between two variables. A large positive value indicates pos-                          tween measurement types.
itively correlated data. Likewise, a large negative value de-
notes negatively correlated data. The absolute magnitude of                     CX captures the covariance between all possible pairs of mea-
the covariance measures the degree of redundancy. Some ad-                      surements. The covariance values reflect the noise and redun-
ditional facts about the covariance.                                            dancy in our measurements.
    • σAB is zero if and only if A and B are uncorrelated (e.g.                     • In the diagonal terms, by assumption, large values cor-
      Figure 2, left panel).                                                          respond to interesting structure.
    • σ2AB = σ2A if A = B.                                                          • In the off-diagonal terms large magnitudes correspond
                                                                                      to high redundancy.
We can equivalently convert A and B into corresponding row
vectors.                                                                        Pretend we have the option of manipulating CX . We will sug-
                                                                                gestively define our manipulated covariance matrix CY . What
                         a = [a1 a2 . . . an ]                                  features do we want to optimize in CY ?
                         b = [b1 b2 . . . bn ]
so that we may express the covariance as a dot product matrix                   D. Diagonalize the Covariance Matrix
computation.2
                                    1                                           We can summarize the last two sections by stating that our
                              σ2ab ≡ abT                                 (2)    goals are (1) to minimize redundancy, measured by the mag-
                                    n
                                                                                nitude of the covariance, and (2) maximize the signal, mea-
                                                                                sured by the variance. What would the optimized covariance
Finally, we can generalize from two vectors to an arbitrary                     matrix CY look like?
number. Rename the row vectors a and b as x1 and x2 , respec-
tively, and consider additional indexed row vectors x3 , . . . , xm .
                                                                                    • All off-diagonal terms in CY should be zero. Thus, CY
Define a new m × n matrix X.
                                                                                      must be a diagonal matrix. Or, said another way, Y is
                              
                                  x1
                                                                                     decorrelated.
                          X =  ...                                                • Each successive dimension in Y should be rank-ordered
                                    
                                       xm                                             according to variance.
One interpretation of X is the following. Each row of X corre-                  There are many methods for diagonalizing CY . It is curious to
sponds to all measurements of a particular type. Each column                    note that PCA arguably selects the easiest method: PCA as-
of X corresponds to a set of measurements from one particular                   sumes that all basis vectors {p1 , . . . , pm } are orthonormal, i.e.
trial (this is ~X from section 3.1). We now arrive at a definition              P is an orthonormal matrix. Why is this assumption easiest?
for the covariance matrix CX .
                                                                                Envision how PCA works. In our simple example in Figure 2,
                                 1                                              P acts as a generalized rotation to align a basis with the axis
                             CX ≡ XXT .                                         of maximal variance. In multiple dimensions this could be
                                 n
                                                                                performed by a simple algorithm:
Consider the matrix CX = 1n XXT . The i jth element of CX
is the dot product between the vector of the ith measurement                       1. Select a normalized direction in m-dimensional space
type with the vector of the jth measurement type. We can                              along which the variance in X is maximized. Save this
summarize several properties of CX :                                                  vector as p1 .
                                                                                   2. Find another direction along which variance is maxi-
    • CX is a square symmetric m × m matrix (Theorem 2 of                             mized, however, because of the orthonormality condi-
      Appendix A)                                                                     tion, restrict the search to all directions orthogonal to
                                                                                      all previous selected directions. Save this vector as pi
    • The diagonal terms of CX are the variance of particular
      measurement types.                                                           3. Repeat this procedure until m vectors are selected.
                                                                                The resulting ordered set of p’s are the principal components.
2 Note that in practice, the covariance σ2 is calculated as 1                   In principle this simple algorithm works, however that would
                                         AB                n−1 ∑i ai bi . The
  slight change in normalization constant arises from estimation theory, but    bely the true reason why the orthonormality assumption is ju-
  that is beyond the scope of this tutorial.                                    dicious. The true benefit to this assumption is that there exists
                                                                                                                                               6
an efficient, analytical solution to this problem. We will dis-   We begin by rewriting CY in terms of the unknown variable.
cuss two solutions in the following sections.
                                                                                               1
Notice what we gained with the stipulation of rank-ordered                                CY =   YYT
                                                                                               n
variance. We have a method for judging the importance of
                                                                                               1
the principal direction. Namely, the variances associated with                               = (PX)(PX)T
each direction pi quantify how “principal” each direction is                                   n
                                                                                               1
by rank-ordering each basis vector pi according to the corre-                                = PXXT PT
sponding variances.We will now pause to review the implica-                                    n
tions of all the assumptions made to arrive at this mathemati-                                    1
                                                                                             = P( XXT )PT
cal goal.                                                                                         n
                                                                                          CY = PCX PT
E. Summary of Assumptions
                                                                  Note that we have identified the covariance matrix of X in the
                                                                  last line.
This section provides a summary of the assumptions be-            Our plan is to recognize that any symmetric matrix A is diag-
hind PCA and hint at when these assumptions might perform         onalized by an orthogonal matrix of its eigenvectors (by The-
poorly.                                                           orems 3 and 4 from Appendix A). For a symmetric matrix A
                                                                  Theorem 4 provides A = EDET , where D is a diagonal matrix
                                                                  and E is a matrix of eigenvectors of A arranged as columns.3
   I. Linearity
      Linearity frames the problem as a change of ba-             Now comes the trick. We select the matrix P to be a matrix
      sis. Several areas of research have explored how            where each row pi is an eigenvector of n1 XXT . By this selec-
      extending these notions to nonlinear regimes (see           tion, P ≡ ET . With this relation and Theorem 1 of Appendix
      Discussion).                                                A (P−1 = PT ) we can finish evaluating CY .
  II. Large variances have important structure.
                                                                                         CY = PCX PT
      This assumption also encompasses the belief that
      the data has a high SNR. Hence, principal compo-                                      = P(ET DE)PT
      nents with larger associated variances represent                                      = P(PT DP)PT
      interesting structure, while those with lower vari-                                   = (PPT )D(PPT )
      ances represent noise. Note that this is a strong,
      and sometimes, incorrect assumption (see Dis-                                         = (PP−1 )D(PP−1 )
      cussion).                                                                          CY = D
 III. The principal components are orthogonal.                    It is evident that the choice of P diagonalizes CY . This was
      This assumption provides an intuitive simplifica-           the goal for PCA. We can summarize the results of PCA in the
      tion that makes PCA soluble with linear algebra             matrices P and CY .
      decomposition techniques. These techniques are
      highlighted in the two following sections.
                                                                      • The principal components of X are the eigenvectors of
                                                                        CX = 1n XXT .
We have discussed all aspects of deriving PCA - what remain
are the linear algebra solutions. The first solution is some-
what straightforward while the second solution involves un-           • The ith diagonal value of CY is the variance of X along
derstanding an important algebraic decomposition.                       pi .
                                                                  In practice computing PCA of a data set X entails (1) subtract-
V. SOLVING PCA USING EIGENVECTOR DECOMPOSITION                    ing off the mean of each measurement type and (2) computing
                                                                  the eigenvectors of CX . This solution is demonstrated in Mat-
                                                                  lab code included in Appendix B.
We derive our first algebraic solution to PCA based on an im-
portant property of eigenvector decomposition. Once again,
the data set is X, an m × n matrix, where m is the number of
measurement types and n is the number of samples. The goal        3 The matrix A might have r ≤ m orthonormal eigenvectors where r is the
is summarized as follows.                                           rank of the matrix. When the rank of A is less than m, A is degenerate or all
                                                                    data occupy a subspace of dimension r ≤ m. Maintaining the constraint of
                                                                    orthogonality, we can remedy this situation by selecting (m − r) additional
      Find some orthonormal matrix P in Y = PX such                 orthonormal vectors to “fill up” the matrix E. These additional vectors
      that CY ≡ 1n YYT is a diagonal matrix. The rows               do not effect the final solution because the variances associated with these
      of P are the principal components of X.                       directions are zero.
                                                                                                                                                                   7
VI. A MORE GENERAL SOLUTION USING SVD                                             The set of eigenvectors {v̂1 , v̂2 , . . . , v̂r } and the set of vec-
                                                                                  tors {û1 , û2 , . . . , ûr } are both orthonormal sets or bases in r-
                                                                                  dimensional space.
This section is the most mathematically involved and can be
skipped without much loss of continuity. It is presented solely                   We can summarize this result for all vectors in one matrix
for completeness. We derive another algebraic solution for                        multiplication by following the prescribed construction in Fig-
PCA and in the process, find that PCA is closely related to                       ure 4. We start by constructing a new diagonal matrix Σ.
singular value decomposition (SVD). In fact, the two are so                                                                   
intimately related that the names are often used interchange-                                            σ1̃
ably. What we will see though is that SVD is a more general
method of understanding change of basis.
                                                                                                       
                                                                                                       
                                                                                                       
                                                                                                             ..
                                                                                                                .
                                                                                                                  σ
                                                                                                                               
                                                                                                                               
                                                                                                                                   0
                                                                                                                   r̃
                                                                                                                              
                                                                                                  Σ≡                         
We begin by quickly deriving the decomposition. In the fol-                                                           0        
                                                                                                                     0
                                                                                                                              
lowing section we interpret the decomposition and in the last                                          
                                                                                                                        . ..
                                                                                                                               
                                                                                                                               
section we relate these results to PCA.
                                                                                                                                           0
                                                                                  where σ1̃ ≥ σ2̃ ≥ . . . ≥ σr̃ are the rank-ordered set of singu-
A. Singular Value Decomposition                                                   lar values. Likewise we construct accompanying orthogonal
                                                                                  matrices,
Let X be an arbitrary n × m matrix4 and XT X be a rank r,
                                                                                                                                
                                                                                                        V = v̂1̃ v̂2̃ . . . v̂m̃
square, symmetric m × m matrix. In a seemingly unmotivated                                                                      
                                                                                                        U = û1̃ û2̃ . . . ûñ
fashion, let us define all of the quantities of interest.
                                                                                  where we have appended an additional (m − r) and (n − r) or-
    • {v̂1 , v̂2 , . . . , v̂r } is the set of orthonormal m × 1 eigen-           thonormal vectors to “fill up” the matrices for V and U respec-
      vectors with associated eigenvalues {λ1 , λ2 , . . . , λr } for             tively (i.e. to deal with degeneracy issues). Figure 4 provides
      the symmetric matrix XT X.                                                  a graphical representation of how all of the pieces fit together
                                                                                  to form the matrix version of SVD.
                            (XT X)v̂i = λi v̂i
                                                                                                                    XV = UΣ
           √
    • σi ≡ λi are positive real and termed the singular val-                      where each column of V and U perform the scalar version of
      ues.                                                                        the decomposition (Equation 3). Because V is orthogonal, we
                                                                                  can multiply both sides by V−1 = VT to arrive at the final form
    • {û1 , û2 , . . . , ûr } is the set of n × 1 vectors defined by
                                                                                  of the decomposition.
      ûi ≡ σ1i Xv̂i .
                                                                                                                   X = UΣVT                                      (4)
The final definition includes two new and unexpected proper-
                                                                                  Although derived without motivation, this decomposition is
ties.
                                                                                  quite powerful. Equation 4 states that any arbitrary matrix X
                                                                                 can be converted to an orthogonal matrix, a diagonal matrix
                        1 if i = j                                                and another orthogonal matrix (or a rotation, a stretch and a
    • ûi · ûj =
                        0 otherwise                                               second rotation). Making sense of Equation 4 is the subject of
                                                                                  the next section.
    • kXv̂i k = σi
These properties are both proven in Theorem 5. We now have
                                                                                  B. Interpreting SVD
all of the pieces to construct the decomposition. The scalar
version of singular value decomposition is just a restatement
of the third definition.                                                          The final form of SVD is a concise but thick statement. In-
                                                                                  stead let us reinterpret Equation 3 as
                               Xv̂i = σi ûi                                (3)
                                                                                                                     Xa = kb
This result says a quite a bit. X multiplied by an eigen-
vector of XT X is equal to a scalar times another vector.                         where a and b are column vectors and k is a scalar con-
                                                                                  stant. The set {v̂1 , v̂2 , . . . , v̂m } is analogous to a and the set
                                                                                  {û1 , û2 , . . . , ûn } is analogous to b. What is unique though is
                                                                                  that {v̂1 , v̂2 , . . . , v̂m } and {û1 , û2 , . . . , ûn } are orthonormal sets
4 Notice that in this section only we are reversing convention from m × n to      of vectors which span an m or n dimensional space, respec-
  n × m. The reason for this derivation will become clear in section 6.3.         tively. In particular, loosely speaking these sets appear to span
                                                                                                                                                  8
        The scalar form of SVD is expressed in equation 3.
                                                                             Xv̂i = σi ûi
        The mathematical intuition behind the construction of the matrix form is that we want to express all n scalar equations in just one
        equation. It is easiest to understand this process graphically. Drawing the matrices of equation 3 looks likes the following.
        We can construct three new matrices V, U and Σ. All singular values are first rank-ordered σ1̃ ≥ σ2̃ ≥ . . . ≥ σr̃ , and the corre-
        sponding vectors are indexed in the same rank order. Each pair of associated vectors v̂i and ûi is stacked in the ith column along
        their respective matrices. The corresponding singular value σi is placed along the diagonal (the iith position) of Σ. This generates
        the equation XV = UΣ, which looks like the following.
        The matrices V and U are m × m and n × n matrices respectively and Σ is a diagonal matrix with a few non-zero values (repre-
        sented by the checkerboard) along its diagonal. Solving this single matrix equation solves all n “value” form equations.
FIG. 4 Construction of the matrix form of SVD (Equation 4) from the scalar form (Equation 3).
all possible “inputs” (i.e. a) and “outputs” (i.e. b). Can we                         similar quantity - the row space.
formalize the view that {v̂1 , v̂2 , . . . , v̂n } and {û1 , û2 , . . . , ûn }
span all possible “inputs” and “outputs”?
                                                                                                               XV = ΣU
We can manipulate Equation 4 to make this fuzzy hypothesis                                                  (XV)T = (ΣU)T
more precise.
                                                                                                             VT XT = UT Σ
                                                                                                             VT XT = Z
                                X = UΣVT                                              where we have defined Z ≡ UT Σ. Again the rows of VT (or
                             UT X = ΣVT                                               the columns of V) are an orthonormal basis for transforming
                             UT X = Z                                                 XT into Z. Because of the transpose on X, it follows that V
                                                                                      is an orthonormal basis spanning the row space of X. The
                                                                                      row space likewise formalizes the notion of what are possible
                                                                                      “inputs” into an arbitrary matrix.
where we have defined Z ≡ ΣVT . Note that the previous                                We are only scratching the surface for understanding the full
columns {û1 , û2 , . . . , ûn } are now rows in UT . Comparing this                implications of SVD. For the purposes of this tutorial though,
equation to Equation 1, {û1 , û2 , . . . , ûn } perform the same role              we have enough information to understand how PCA will fall
as {p̂1 , p̂2 , . . . , p̂m }. Hence, UT is a change of basis from X to               within this framework.
Z. Just as before, we were transforming column vectors, we
can again infer that we are transforming column vectors. The
fact that the orthonormal basis UT (or P) transforms column
vectors means that UT is a basis that spans the columns of X.
Bases that span the columns are termed the column space of                            C. SVD and PCA
X. The column space formalizes the notion of what are the
possible “outputs” of any matrix.
                                                                                      It is evident that PCA and SVD are intimately related. Let us
There is a funny symmetry to SVD such that we can define a                            return to the original m × n data matrix X. We can define a
                                                                                                                                                      9
                       Quick Summary of PCA                                       A                                    B
      1. Organize data as an m × n matrix, where m is the number
         of measurement types and n is the number of samples.
                                                                                                        θ
      2. Subtract off the mean for each measurement type.
      3. Calculate the SVD or the eigenvectors of the covariance.
                                                                                           z                               y
FIG. 5 A step-by-step instruction list on how to perform principal
component analysis                                                                                                                   x
                                                                                                 x
                                                                                       y
new matrix Y as an n × m matrix.5                                                 FIG. 6 Example of when PCA fails (red lines). (a) Tracking a per-
                                   1                                              son on a ferris wheel (black dots). All dynamics can be described
                               Y ≡ √ XT                                           by the phase of the wheel θ, a non-linear combination of the naive
                                    n                                             basis. (b) In this example data set, non-Gaussian distributed data and
                                                                                  non-orthogonal axes causes PCA to fail. The axes with the largest
where each column of Y has zero mean. The choice of Y                             variance do not correspond to the appropriate answer.
becomes clear by analyzing YT Y.
                          1 T T
                                    
               T                   1 T
             Y Y = √ X             √ X                                            principle component provides a means for comparing the rel-
                           n        n                                             ative importance of each dimension. An implicit hope behind
                       1                                                          employing this method is that the variance along a small num-
                   = XXT
                       n                                                          ber of principal components (i.e. less than the number of mea-
               T                                                                  surement types) provides a reasonable characterization of the
             Y Y = CX
                                                                                  complete data set. This statement is the precise intuition be-
By construction YT Y equals the covariance matrix of X. From                      hind any method of dimensional reduction – a vast arena of
section 5 we know that the principal components of X are                          active research. In the example of the spring, PCA identi-
the eigenvectors of CX . If we calculate the SVD of Y, the                        fies that a majority of variation exists along a single dimen-
columns of matrix V contain the eigenvectors of YT Y = CX .                       sion (the direction of motion x̂), eventhough 6 dimensions are
Therefore, the columns of V are the principal components of                       recorded.
X. This second algorithm is encapsulated in Matlab code in-
cluded in Appendix B.                                                             Although PCA “works” on a multitude of real world prob-
                                                                                  lems, any diligent scientist or engineer must ask when does
What does this mean? V spans the row space of Y ≡ √1n XT .                        PCA fail? Before we answer this question, let us note a re-
Therefore, V must also span the column space of √1n X. We                         markable feature of this algorithm. PCA is completely non-
                                                                                  parametric: any data set can be plugged in and an answer
can conclude that finding the principal components amounts
                                                                                  comes out, requiring no parameters to tweak and no regard for
to finding an orthonormal basis that spans the column space
                                                                                  how the data was recorded. From one perspective, the fact that
of X.6
                                                                                  PCA is non-parametric (or plug-and-play) can be considered
                                                                                  a positive feature because the answer is unique and indepen-
                                                                                  dent of the user. From another perspective the fact that PCA
VII. DISCUSSION                                                                   is agnostic to the source of the data is also a weakness. For
                                                                                  instance, consider tracking a person on a ferris wheel in Fig-
                                                                                  ure 6a. The data points can be cleanly described by a single
Principal component analysis (PCA) has widespread applica-
                                                                                  variable, the precession angle of the wheel θ, however PCA
tions because it reveals simple underlying structures in com-
                                                                                  would fail to recover this variable.
plex data sets using analytical solutions from linear algebra.
Figure 5 provides a brief summary for implementing PCA.
A primary benefit of PCA arises from quantifying the impor-
                                                                                  A. Limits and Statistics of Dimensional Reduction
tance of each dimension for describing the variability of a data
set. In particular, the measurement of the variance along each
                                                                                  A deeper appreciation of the limits of PCA requires some con-
                                                                                  sideration about the underlying assumptions and in tandem,
                                                                                  a more rigorous description of the source of data. Gener-
5 Y is of the appropriate n×m dimensions laid out in the derivation of section
                                                                                  ally speaking, the primary motivation behind this method is
  6.1. This is the reason for the “flipping” of dimensions in 6.1 and Figure 4.   to decorrelate the data set, i.e. remove second-order depen-
6 If the final goal is to find an orthonormal basis for the coulmn space of
  X then we can calculate it directly without constructing Y. By symmetry         dencies. The manner of approaching this goal is loosely akin
  the columns of U produced by the SVD of √1n X must also be the principal        to how one might explore a town in the Western United States:
  components.                                                                     drive down the longest road running through the town. When
                                                                                                                                                             10
one sees another big road, turn left or right and drive down                           Appendix A: Linear Algebra
this road, and so forth. In this analogy, PCA requires that each
new road explored must be perpendicular to the previous, but
clearly this requirement is overly stringent and the data (or                          This section proves a few unapparent theorems in linear
town) might be arranged along non-orthogonal axes, such as                             algebra, which are crucial to this paper.
Figure 6b. Figure 6 provides two examples of this type of data
where PCA provides unsatisfying results.                                               1. The inverse of an orthogonal matrix is its transpose.
To address these problems, we must define what we consider
optimal results. In the context of dimensional reduction, one                          Let A be an m×n orthogonal matrix where ai is the ith column
measure of success is the degree to which a reduced repre-                             vector. The i jth element of AT A is
sentation can predict the original data. In statistical terms,                                                          
we must define an error function (or loss function). It can                                             T         T         1 if i = j
                                                                                                    (A A)i j = ai aj =
be proved that under a common loss function, mean squared                                                                   0 otherwise
error (i.e. L2 norm), PCA provides the optimal reduced rep-
resentation of the data. This means that selecting orthogonal                          Therefore, because AT A = I, it follows that A−1 = AT .
directions for principal components is the best solution to pre-
dicting the original data. Given the examples of Figure 6, how
                                                                                       2. For any matrix A, AT A and AAT are symmetric.
could this statement be true? Our intuitions from Figure 6
suggest that this result is somehow misleading.
The solution to this paradox lies in the goal we selected for the                                         (AAT )T = AT T AT = AAT
analysis. The goal of the analysis is to decorrelate the data, or                                         (AT A)T = AT AT T = AT A
said in other terms, the goal is to remove second-order depen-
dencies in the data. In the data sets of Figure 6, higher order                        3. A matrix is symmetric if and only if it is orthogonally
dependencies exist between the variables. Therefore, remov-                            diagonalizable.
ing second-order dependencies is insufficient at revealing all
structure in the data.7                                                                Because this statement is bi-directional, it requires a two-part
Multiple solutions exist for removing higher-order dependen-                           “if-and-only-if” proof. One needs to prove the forward and
cies. For instance, if prior knowledge is known about the                              the backwards “if-then” cases.
problem, then a nonlinearity (i.e. kernel) might be applied                            Let us start with the forward case. If A is orthogonally di-
to the data to transform the data to a more appropriate naive                          agonalizable, then A is a symmetric matrix. By hypothesis,
basis. For instance, in Figure 6a, one might examine the po-                           orthogonally diagonalizable means that there exists some E
lar coordinate representation of the data. This parametric ap-                         such that A = EDET , where D is a diagonal matrix and E is
proach is often termed kernel PCA.                                                     some special matrix which diagonalizes A. Let us compute
Another direction is to impose more general statistical defini-                        AT .
tions of dependency within a data set, e.g. requiring that data
                                                                                                 AT = (EDET )T = ET T DT ET = EDET = A
along reduced dimensions be statistically independent. This
class of algorithms, termed, independent component analysis
(ICA), has been demonstrated to succeed in many domains                                Evidently, if A is orthogonally diagonalizable, it must also be
where PCA fails. ICA has been applied to many areas of sig-                            symmetric.
nal and image processing, but suffers from the fact that solu-
                                                                                       The reverse case is more involved and less clean so it will be
tions are (sometimes) difficult to compute.
                                                                                       left to the reader. In lieu of this, hopefully the “forward” case
Writing this paper has been an extremely instructional expe-                           is suggestive if not somewhat convincing.
rience for me. I hope that this paper helps to demystify the
motivation and results of PCA, and the underlying assump-
                                                                                       4. A symmetric matrix is diagonalized by a matrix of its
tions behind this important analysis technique. Please send
                                                                                       orthonormal eigenvectors.
me a note if this has been useful to you as it inspires me to
keep writing!
                                                                                       Let A be a square n × n symmetric matrix with associated
                                                                                       eigenvectors {e1 , e2 , . . . , en }. Let E = [e1 e2 . . . en ] where the
                                                                                       ith column of E is the eigenvector ei . This theorem asserts that
7 When are second order dependencies sufficient for revealing all dependen-
                                                                                       there exists a diagonal matrix D such that A = EDET .
  cies in a data set? This statistical condition is met when the first and second
  order statistics are sufficient statistics of the data. This occurs, for instance,   This proof is in two parts. In the first part, we see that the
  when a data set is Gaussian distributed.                                             any matrix can be orthogonally diagonalized if and only if
                                                                                       it that matrix’s eigenvectors are all linearly independent. In
                                                                                       the second part of the proof, we see that a symmetric matrix
                                                                                                                                         11
has the special property that all of its eigenvectors are not just          All of these properties arise from the dot product of any two
linearly independent but also orthogonal, thus completing our               vectors from this set.
proof.
                                                                                            (Xv̂i ) · (Xv̂j ) = (Xv̂i )T (Xv̂j )
In the first part of the proof, let A be just some matrix, not
necessarily symmetric, and let it have independent eigenvec-                                                  = v̂Ti XT Xv̂j
tors (i.e. no degeneracy). Furthermore, let E = [e1 e2 . . . en ]                                             = v̂Ti (λ j v̂j )
be the matrix of eigenvectors placed in the columns. Let D be                                                 = λ j v̂i · v̂j
a diagonal matrix where the ith eigenvalue is placed in the iith
                                                                                            (Xv̂i ) · (Xv̂j ) = λ j δi j
position.
We will now show that AE = ED. We can examine the
columns of the right-hand and left-hand sides of the equation.              The last relation arises because the set of eigenvectors of X is
                                                                            orthogonal resulting in the Kronecker delta. In more simpler
         Left hand side : AE = [Ae1 Ae2 . . . Aen ]                         terms the last relation states:
        Right hand side : ED = [λ1 e1 λ2 e2 . . . λn en ]                                                         
                                                                                                                    λj i = j
                                                                                              (Xv̂i ) · (Xv̂j ) =
Evidently, if AE = ED then Aei = λi ei for all i. This equa-                                                        0 i 6= j
tion is the definition of the eigenvalue equation. Therefore,               This equation states that any two vectors in the set are orthog-
it must be that AE = ED. A little rearrangement provides                    onal.
A = EDE−1 , completing the first part the proof.
                                                                            The second property arises from the above equation by realiz-
For the second part of the proof, we show that a symmetric                  ing that the length squared of each vector is defined as:
matrix always has orthogonal eigenvectors. For some sym-
metric matrix, let λ1 and λ2 be distinct eigenvalues for eigen-                              kXv̂i k2 = (Xv̂i ) · (Xv̂i ) = λi
vectors e1 and e2 .
                      λ1 e1 · e2 = (λ1 e1 )T e2
                                                                            Appendix B: Code
                                 = (Ae1 )T e2
                                 = e1 T AT e2
                                                                            This code is written for Matlab 6.5 (Release 13) from
                                 = e1 T Ae2
                                                                            Mathworks8 .    The code is not computationally effi-
                                 = e1 T (λ2 e2 )                            cient but explanatory (terse comments begin with a %).
                      λ1 e1 · e2 = λ2 e1 · e2
                                                                            This first version follows Section 5 by examining the
By the last relation we can equate that (λ1 − λ2 )e1 · e2 = 0.              covariance of the data set.
Since we have conjectured that the eigenvalues are in fact
unique, it must be the case that e1 · e2 = 0. Therefore, the                function [signals,PC,V] = pca1(data)
eigenvectors of a symmetric matrix are orthogonal.                          % PCA1: Perform PCA using covariance.
Let us back up now to our original postulate that A is a sym-               %     data - MxN matrix of input data
metric matrix. By the second part of the proof, we know                     %            (M dimensions, N trials)
that the eigenvectors of A are all orthonormal (we choose                   % signals - MxN matrix of projected data
the eigenvectors to be normalized). This means that E is an                 %       PC - each column is a PC
orthogonal matrix so by theorem 1, ET = E−1 and we can                      %        V - Mx1 matrix of variances
rewrite the final result.
                                                                            [M,N] = size(data);
                                         T
                             A = EDE
                                                                            % subtract off the mean for each dimension
. Thus, a symmetric matrix is diagonalized by a matrix of its               mn = mean(data,2);
eigenvectors.                                                               data = data - repmat(mn,1,N);
                                                                            % calculate the covariance matrix
5. For any arbitrary m × n matrix X, the symmetric                          covariance = 1 / (N-1) * data * data’;
matrix XT X has a set of orthonormal eigenvectors
of {v̂1 , v̂2 , . . . , v̂n } and a set of associated eigenvalues           % find the eigenvectors and eigenvalues
{λ1 , λ2 , . . . , λn }. The set of vectors {Xv̂1 , Xv̂2 , . . . , Xv̂n }
then form√ an orthogonal basis, where each vector Xv̂i is of
length λi .
                                                                            8 http://www.mathworks.com
                                                                                                   12
[PC, V] = eig(covariance);                            %        V - Mx1 matrix of variances
% extract diagonal of matrix as vector                [M,N] = size(data);
V = diag(V);
                                                      % subtract off the mean for each dimension
% sort the variances in decreasing order              mn = mean(data,2);
[junk, rindices] = sort(-1*V);                        data = data - repmat(mn,1,N);
V = V(rindices);
PC = PC(:,rindices);                                  % construct the matrix Y
                                                      Y = data’ / sqrt(N-1);
% project the original data set
signals = PC’ * data;                                 % SVD does it all
                                                      [u,S,PC] = svd(Y);
This second version follows section 6 computing PCA
                                                      % calculate the variances
through SVD.
                                                      S = diag(S);
                                                      V = S .* S;
function [signals,PC,V] = pca2(data)
% PCA2: Perform PCA using SVD.                        % project the original data
%     data - MxN matrix of input data                 signals = PC’ * data;
%            (M dimensions, N trials)
% signals - MxN matrix of projected data
%       PC - each column is a PC
