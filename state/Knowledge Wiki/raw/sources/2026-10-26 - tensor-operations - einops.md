<!-- source: https://github.com/arogozhnikov/einops | type: html | hash: 41b606e3a35e6a137bc7e6aafd5b7d8708bc207b95f1ca3083ec2768eeefaa92 | fetched: 2026-10-26T10:22:00Z -->

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

GitHub - arogozhnikov/einops: Flexible and powerful tensor operations for readable and reliable code (for pytorch, jax, TF and others) · GitHub

-

-

-

-

-

-

-

Skip to content

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

You signed in with another tab or window. Reload to refresh your session.
You signed out in another tab or window. Reload to refresh your session.
You switched accounts on another tab or window. Reload to refresh your session.

Dismiss alert

{{ message }}

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

-

main

Branches Tags

Go to file

Code Open more actions menu

## Latest commit

## History
750 Commits
750 Commits

## Folders and files
| | Name | Name | Last commit message
| Last commit date

| .devcontainer

| .devcontainer

|
|

| .github

| .github

|
|

| docs

| docs

|
|

| docs_src

| docs_src

|
|

| einops

| einops

|
|

| scripts

| scripts

|
|

| .gitignore

| .gitignore

|
|

| .pre-commit-config.yaml

| .pre-commit-config.yaml

|
|

| CITATION.cff

| CITATION.cff

|
|

| LICENSE

| LICENSE

|
|

| README.md

| README.md

|
|

| mkdocs.yml

| mkdocs.yml

|
|

| pyproject.toml

| pyproject.toml

|
|

| View all files

## Repository files navigation

einops_video.mp4

## einops

Flexible and powerful tensor operations for readable and reliable code.

Supports numpy, pytorch, jax, mlx and others.

## Recent updates:

- 0.9.0: overhaul of typing in einops

- einops playground can run 2 of 4 example notebooks right in your browser

- 0.8.2: MLX backend added

- 0.8.0: tinygrad backend added, small fixes

- 0.7.0: no-hassle torch.compile, support of array api standard and more

- 10'000🎉: github reports that more than 10k project use einops

- einops 0.6 introduces packing and unpacking

Previous updates
- einops 0.5: einsum is now a part of einops
- [Einops paper](https://openreview.net/pdf?id=oapKSVM2bcj) is accepted for oral presentation at ICLR 2022 (yes, it worth reading).
Talk recordings are [available](https://iclr.cc/virtual/2022/oral/6603)
- flax and oneflow backend added
- torch.jit.script is supported for pytorch layers
- powerful EinMix added to einops. [Einmix tutorial notebook](https://github.com/arogozhnikov/einops/blob/main/docs/3-einmix-layer.ipynb)

## Tweets

In case you need convincing arguments for setting aside time to learn about einsum and einops...
Tim Rocktäschel

Writing better code with PyTorch and einops 👌
Andrej Karpathy

Slowly but surely, einops is seeping in to every nook and cranny of my code. If you find yourself shuffling around bazillion dimensional tensors, this might change your life
Nasim Rahaman

More testimonials

## Contents

- Installation

- Documentation

- Tutorial

- API micro-reference

- Why use einops

- Supported frameworks

- Citing

- Repository and discussions

## Installation

Plain and simple:

pip install einops

(uv pip install einops works as well)

## Tutorials

Tutorials are the most convenient way to see einops in action

- part 1: einops fundamentals

- part 2: einops for deep learning

- part 3: packing and unpacking

- part 4: improve pytorch code with einops

Kapil Sachdeva recorded a small intro to einops.

## API

einops has a minimalistic yet powerful API.

Three core operations provided (einops tutorial
shows those cover stacking, reshape, transposition, squeeze/unsqueeze, repeat, tile, concatenate, view and numerous reductions)

from einops import rearrange, reduce, repeat
# rearrange elements according to the pattern
output_tensor = rearrange(input_tensor, 't b c -> b c t')
# combine rearrangement and reduction
output_tensor = reduce(input_tensor, 'b c (h h2) (w w2) -> b h w c', 'mean', h2=2, w2=2)
# copy along a new axis
output_tensor = repeat(input_tensor, 'h w -> h w c', c=3)

Later additions to the family are pack and unpack functions (better than stack/split/concatenate):

from einops import pack, unpack
# pack and unpack allow reversibly 'packing' multiple tensors into one.
# Packed tensors may be of different dimensionality:
packed, ps = pack([class_token_bc, image_tokens_bhwc, text_tokens_btc], 'b * c')
class_emb_bc, image_emb_bhwc, text_emb_btc = unpack(transformer(packed), ps, 'b * c')

Finally, einops provides einsum with a support of multi-lettered names:

from einops import einsum, pack, unpack
# einsum is like ... einsum, generic and flexible dot-product
# but 1) axes can be multi-lettered 2) pattern goes last 3) works with multiple frameworks
C = einsum(A, B, 'b t1 head c, b t2 head c -> b head t1 t2')

## EinMix

EinMix is a generic linear layer, perfect for MLP Mixers and similar architectures.

## Layers

Einops provides layers (einops keeps a separate version for each framework) that reflect corresponding functions

from einops.layers.torch import Rearrange, Reduce
from einops.layers.tensorflow import Rearrange, Reduce
from einops.layers.flax import Rearrange, Reduce
from einops.layers.paddle import Rearrange, Reduce

Example of using layers within a pytorch model
Example given for pytorch, but code in other frameworks is almost identical
from torch.nn import Sequential, Conv2d, MaxPool2d, Linear, ReLU
from einops.layers.torch import Rearrange

model = Sequential(
...,
Conv2d(6, 16, kernel_size=5),
MaxPool2d(kernel_size=2),
# flattening without need to write forward
Rearrange('b c h w -> b (c h w)'),
Linear(16*5*5, 120),
ReLU(),
Linear(120, 10),
)

No more flatten needed!

Operations and layers can be torch.compiled.

## Naming

einops stands for Einstein-Inspired Notation for operations
(though "Einstein operations" is more attractive and easier to remember).

Notation was loosely inspired by Einstein summation (in particular by numpy.einsum operation).

## Why use einops notation?!

## Semantic information (being verbose in expectations)

y = x.view(x.shape[0], -1)
y = rearrange(x, 'b c h w -> b (c h w)')

While these two lines are doing the same job in some context,
the second one provides information about the input and output.
In other words, einops focuses on interface: what is the input and output, not how the output is computed.

The next operation looks similar:

y = rearrange(x, 'time c h w -> time (c h w)')

but it gives the reader a hint:
this is not an independent batch of images we are processing,
but rather a sequence (video).

Semantic information makes the code easier to read and maintain.

## Convenient checks

Reconsider the same example:

y = x.view(x.shape[0], -1) # x: (batch, 256, 19, 19)
y = rearrange(x, 'b c h w -> b (c h w)')

The second line checks that the input has four dimensions,
but you can also specify particular dimensions.
That's opposed to just writing comments about shapes since comments don't prevent mistakes,
not tested, and without code review tend to be outdated

y = x.view(x.shape[0], -1) # x: (batch, 256, 19, 19)
y = rearrange(x, 'b c h w -> b (c h w)', c=256, h=19, w=19)

## Result is strictly determined

Below we have at least two ways to define the depth-to-space operation

# depth-to-space
rearrange(x, 'b c (h h2) (w w2) -> b (c h2 w2) h w', h2=2, w2=2)
rearrange(x, 'b c (h h2) (w w2) -> b (h2 w2 c) h w', h2=2, w2=2)

There are at least four more ways to do it. Which one is used by the framework?

These details are ignored, since usually it makes no difference,
but it can make a big difference (e.g. if you use grouped convolutions in the next stage),
and you'd like to specify this in your code.

## Uniformity

reduce(x, 'b c (x dx) -> b c x', 'max', dx=2)
reduce(x, 'b c (x dx) (y dy) -> b c x y', 'max', dx=2, dy=3)
reduce(x, 'b c (x dx) (y dy) (z dz) -> b c x y z', 'max', dx=2, dy=3, dz=4)

These examples demonstrated that we don't use separate operations for 1d/2d/3d pooling,
those are all defined in a uniform way.

Space-to-depth and depth-to space are defined in many frameworks but how about width-to-height? Here you go:

rearrange(x, 'b c h (w w2) -> b c (h w2) w', w2=2)

## Framework independent behavior

Even simple functions are defined differently by different frameworks

y = x.flatten() # or flatten(x)

Suppose x's shape was (3, 4, 5), then y has shape ...

- numpy, pytorch, cupy, chainer, jax: (60,)

- keras, tensorflow.layers, gluon: (3, 20)

einops works the same way in all frameworks.

## Independence of framework terminology

Example: tile vs repeat causes lots of confusion. To copy image along width:

np.tile(image, (1, 2)) # in numpy
image.repeat(1, 2) # pytorch's repeat ~ numpy's tile

With einops you don't need to decipher which axis was repeated:

repeat(image, 'h w -> h (tile w)', tile=2) # in numpy
repeat(image, 'h w -> h (tile w)', tile=2) # in pytorch
repeat(image, 'h w -> h (tile w)', tile=2) # in tf
repeat(image, 'h w -> h (tile w)', tile=2) # in jax
repeat(image, 'h w -> h (tile w)', tile=2) # in cupy
... (etc.)

Testimonials provide users' perspective on the same question.

## Supported frameworks

Einops works with ...

- numpy

- pytorch

- tensorflow

- jax

- cupy

- flax (community)

- paddle (community)

- oneflow (community)

- tinygrad (community)

- pytensor (community)

from einops import rearrange
=> from einops.array_api import rearrange

But actually it is even better: einops can be used with any framework that supports
Python array API standard,
to name a few:

- numpy >= 2.0

- MLX # yes, einops works with apple's framework

- pydata/sparse >= 0.15 # and works with sparse tensors

- cubed # and with distributed tensors too

- quantco/ndonnx

- jax

- cupy

- dask is supported via array-api-compat

## Development

Devcontainer is provided, this environment can be used locally, or on your server,
or within github codespaces.
To start with devcontainers in vs code, clone repo, and click 'Reopen in Devcontainer'.

Starting from einops 0.8.1, einops distributes tests as a part of package.

# pip install einops pytest
python -m einops.tests.run_tests numpy pytorch jax --pip-install

numpy pytorch jax is an example, any subset of testable frameworks can be provided.
Every framework is tested against numpy, so it is a requirement for tests.

Specifying --pip-install will install requirements in current virtualenv,
and should be omitted if dependencies are installed locally.

To build/test docs:

hatch run docs:serve # Serving on http://localhost:8000/

## Citing einops

Please use the following bibtex record

@inproceedings{
rogozhnikov2022einops,
title={Einops: Clear and Reliable Tensor Manipulations with Einstein-like Notation},
author={Alex Rogozhnikov},
booktitle={International Conference on Learning Representations},
year={2022},
url={https://openreview.net/forum?id=oapKSVM2bcj}
}

## Supported python versions

einops works with python 3.10 or later.

## About
Flexible and powerful tensor operations for readable and reliable code (for pytorch, jax, TF and others)
einops.rocks

## Topics
cupydeep-learningeinopsjaxmlxnumpypytorchtensortensorflow

## Resources
Readme
MIT license
Cite this repository
Activity

## Stars
9.6k stars

## Watchers
61 watching

## Forks
406 forks

Report repository

## Releases

## Used by

## Contributors

## Languages

You can’t perform that action at this time.
