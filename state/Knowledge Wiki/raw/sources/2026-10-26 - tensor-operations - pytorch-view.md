<!-- source: https://pytorch.org/docs/stable/tensor_view.html | type: html | hash: b0dada65603fa95d24a8e6258464f09a117b9dad58a50a17a4646b2e13b45dab | fetched: 2026-10-26T10:22:00Z -->

Tensor Views — PyTorch 2.14 documentation

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

Skip to main content

Back to top

Ctrl+K

Go to
pytorch.org

Ctrl+K

-

X

-

GitHub

-

PyTorch Forum

-

PyPi

Rate this Page

★

★

★

★

★

-

## Tensor Views#

Created On: May 07, 2026 | Last Updated On: May 07, 2026

PyTorch allows a tensor to be a View of an existing tensor. View tensor shares the same underlying data
with its base tensor. Supporting View avoids explicit data copy, thus allows us to do fast and memory efficient
reshaping, slicing and element-wise operations.

For example, to get a view of an existing tensor t, you can call t.view(...).

>>> t = torch.rand(4, 4)
>>> b = t.view(2, 8)
>>> t.storage().data_ptr() == b.storage().data_ptr() # `t` and `b` share the same underlying data.
True
# Modifying view tensor changes base tensor as well.
>>> b[0][0] = 3.14
>>> t[0][0]
tensor(3.14)

Since views share underlying data with its base tensor, if you edit the data
in the view, it will be reflected in the base tensor as well.

Typically a PyTorch op returns a new tensor as output, e.g. add().
But in case of view ops, outputs are views of input tensors to avoid unnecessary data copy.
No data movement occurs when creating a view, view tensor just changes the way
it interprets the same data. Taking a view of contiguous tensor could potentially produce a non-contiguous tensor.
Users should pay additional attention as contiguity might have implicit performance impact.
transpose() is a common example.

>>> base = torch.tensor([[0, 1],[2, 3]])
>>> base.is_contiguous()
True
>>> t = base.transpose(0, 1) # `t` is a view of `base`. No data movement happened here.
# View tensors might be non-contiguous.
>>> t.is_contiguous()
False
# To get a contiguous tensor, call `.contiguous()` to enforce
# copying data when `t` is not contiguous.
>>> c = t.contiguous()

For reference, here’s a full list of view ops in PyTorch:

- Basic slicing and indexing op, e.g. tensor[0, 2:, 1:7:2] returns a view of base tensor, see note below.

- adjoint()

- as_strided()

- detach()

- diagonal()

- expand()

- expand_as()

- movedim()

- narrow()

- permute()

- select()

- squeeze()

- transpose()

- t()

- T

- H

- mT

- mH

- real

- imag

- view_as_real()

- unflatten()

- unfold()

- unsqueeze()

- view()

- view_as()

- unbind()

- split()

- hsplit()

- vsplit()

- tensor_split()

- split_with_sizes()

- swapaxes()

- swapdims()

- chunk()

- indices() (sparse tensor only)

- values() (sparse tensor only)

Note

When accessing the contents of a tensor via indexing, PyTorch follows Numpy behaviors
that basic indexing returns views, while advanced indexing returns a copy.
Assignment via either basic or advanced indexing is in-place. See more examples in
Numpy indexing documentation.

It’s also worth mentioning a few ops with special behaviors:

- reshape(), reshape_as() and flatten() can return either a view or
new tensor, user code shouldn’t rely on whether it’s view or not.

- contiguous() returns itself if input tensor is already contiguous, otherwise it returns a new contiguous tensor by copying data.

For a more detailed walk-through of PyTorch internal implementation,
please refer to ezyang’s blogpost about PyTorch Internals.

Edit on GitHub

Show Source

PyTorch Libraries

- ExecuTorch

- Helion

- torchao

- kineto

- torchtitan

- TorchRL

- torchvision

- torchaudio

- tensordict

- PyTorch on XLA Devices

so the DOM is not blocked -->

## Docs

Access comprehensive developer documentation for PyTorch

View Docs

## Tutorials

Get in-depth tutorials for beginners and advanced developers

View Tutorials

## Resources

Find development resources and get your questions answered

View Resources

To analyze traffic and optimize your experience, we serve cookies on this site. By clicking or navigating, you agree to allow our usage of cookies. As the current maintainers of this site, Facebook’s Cookies Policy applies. Learn more, including about available controls: Cookies Policy.
