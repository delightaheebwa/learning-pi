<!-- source: https://gregorygundersen.com/blog/2020/02/09/log-sum-exp/ | type: html | hash: d328a17f0a1bc0b3123fc7f60b790d20de7ae054facbf9f913b6fe25a5bd407e | fetched: 2026-10-13T11:30:00Z -->

Title: The Log-Sum-Exp Trick

URL Source: https://gregorygundersen.com/blog/2020/02/09/log-sum-exp/

Markdown Content:
In statistical modeling and machine learning, we often work in a logarithmic scale. There are many good reasons for this. For example, when  and  are both small numbers, multiplying  times  may underflow. However, we can work in a logarithmic scale to convert multiplication to addition because

Furthermore, if we are dealing with functions such as  and , then by the linearity of differentiation, we have

Often, differentiating each function separately is easier than applying the product rule.

These are just two reasons that working with quantities such as log likelihoods and log probabilities is often preferred. And working in log scale is so much more numerically stable that many standard libraries compute probability density functions (PDFs) by simply exponentiating log PDFs. See [my previous post](https://gregorygundersen.com/blog/2019/10/30/scipy-multivariate/) on SciPy’s multivariate normal PDF for an example.

However, sometimes we need to back out the possibly large log-scale values. For example, if we need to normalize an -vector of log probabilities , we might naively compute

Since each  is a log probability which may be very large, and either negative or positive, then exponentiating might result in under- or overflow respectively. (If a value  is in , then  must be negative. However, we often want to interpret quantities as probabilities even if they are outside of this range.) Think about how the log likelihood can have arbitrary scale depending on the likelihood function and number of data points.

With these ideas in mind, consider the log-sum-exp operation,

The log-sum-exp operation can help prevent these numerical issues, but it may not be immediately obvious why it works. First, let’s rewrite  as

In words, we can perform the normalization in  using the log-sum-exp operation in . But does this really help? We’re still exponentiating each . The final step to seeing the utility of the operation is to consider this derivation:

In other words, the log-sum-exp operator in  is nice because we can shift the values in the exponent by an arbitrary constant  while still computing the same final value. If we set

we ensure that the largest positive exponentiated term is .

## Examples in code

Let’s look at this trick in code. First, note that it does not take a large value of  to cause an overflow:

```
>>> x = np.array([1000, 1000, 1000])
>>> np.exp(x)
array([inf, inf, inf])
```

Your results may vary depending on your machine’s precision. Clearly, normalizing `x` as in  is impossible with its current values. If you ran this input and code in a larger pipeline, eventually some function would crash on the `inf` values or convert them to `nan` values. However, let’s implement a `logsumexp` function—you should probably use [SciPy’s implementation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html) if working in Python—,

```
def logsumexp(x):
    c = x.max()
    return c + np.log(np.sum(np.exp(x - c)))
```

and then apply the normalization trick in ,

```
>>> logsumexp(x)
1001.0986122886682
>>> np.exp(x - logsumexp(x))
array([0.33333333, 0.33333333, 0.33333333])
```

This trick can also help with underflow, when machine precision rounds a small value to zero:

```
>>> x = np.array([-1000, -1000, -1000])
>>> np.exp(x)
array([0., 0., 0.])
>>> np.exp(x - logsumexp(x))
array([0.33333333, 0.33333333, 0.33333333])
```

Again, our normalization in , naively computed, would crash, probably due to a division by zero error. This trick still works with a big range in values:

```
>>> x = np.array([-1000, -1000, 1000])
>>> np.exp(x - logsumexp(x))
array([0., 0., 1.])
```

While the probability of the first and second components is not truly zero, this is a reasonable approximation of what those log probabilities represent. Furthermore, we have achieved numerical stability. We can reliably compute  without introducing `inf` or `nan` values or dividing by zero.

### Acknowledgements

I thank Eugen Hotaj for correcting a mistake in an earlier version of this post.
