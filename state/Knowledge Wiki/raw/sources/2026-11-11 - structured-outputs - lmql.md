<!-- source: https://arxiv.org/abs/2212.06094 | type: html | hash: ad3e2ae8126884901be83e3c0c617da4f15f5f34d901cc410bc12870ae437be5 | fetched: 2026-11-11 -->

Skip to main content

Search

Submit
Donate

Log in

Search arXiv

Press Enter to search · Advanced search

## Computer Science > Computation and Language

arXiv:2212.06094 (cs)

-

[Submitted on 12 Dec 2022 ( v1 ), last revised 30 May 2023 (this version, v3)]

## Title: Prompting Is Programming: A Query Language for Large Language Models

Authors: Luca Beurer-Kellner , Marc Fischer , Martin Vechev
View a PDF of the paper titled Prompting Is Programming: A Query Language for Large Language Models, by Luca Beurer-Kellner and 2 other authors

View PDF
HTML (experimental)

Abstract: Large language models have demonstrated outstanding performance on a wide range of tasks such as question answering and code generation. On a high level, given an input, a language model can be used to automatically complete the sequence in a statistically-likely way. Based on this, users prompt these models with language instructions or examples, to implement a variety of downstream tasks. Advanced prompting methods can even imply interaction between the language model, a user, and external tools such as calculators. However, to obtain state-of-the-art performance or adapt language models for specific tasks, complex task- and model-specific programs have to be implemented, which may still require ad-hoc interaction.

Based on this, we present the novel idea of Language Model Programming (LMP). LMP generalizes language model prompting from pure text prompts to an intuitive combination of text prompting and scripting. Additionally, LMP allows constraints to be specified over the language model output. This enables easy adaption to many tasks while abstracting language model internals and providing high-level semantics.

To enable LMP, we implement LMQL(short for Language Model Query Language), which leverages the constraints and control flow from an LMP prompt to generate an efficient inference procedure that minimizes the number of expensive calls to the underlying language model.

We show that LMQL can capture a wide range of state-of-the-art prompting methods in an intuitive way, especially facilitating interactive flows that are challenging to implement with existing high-level APIs. Our evaluation shows that we retain or increase the accuracy on several downstream tasks, while also significantly reducing the required amount of computation or cost in the case of pay-to-use APIs (26-85% cost savings).

Comments:
To be published at PLDI'23: 44th ACM SIGPLAN International Conference on Programming Language Design and Implementation

Subjects:

Computation and Language (cs.CL) ; Artificial Intelligence (cs.AI)

Cite as:
arXiv:2212.06094 [cs.CL]

(or
arXiv:2212.06094v3 [cs.CL] for this version)

https://doi.org/10.48550/arXiv.2212.06094

Focus to learn more

arXiv-issued DOI via DataCite

Related DOI :

https://doi.org/10.1145/3591300

Focus to learn more

DOI(s) linking to related resources

## Submission history
From: Marc Fischer [ view email ]
[v1]
Mon, 12 Dec 2022 18:09:09 UTC (1,352 KB)

[v2]
Wed, 26 Apr 2023 15:11:38 UTC (820 KB)

[v3]
Tue, 30 May 2023 12:56:41 UTC (821 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Prompting Is Programming: A Query Language for Large Language Models, by Luca Beurer-Kellner and 2 other authors

- View PDF

- HTML (experimental)

- TeX Source

view license

## Additional Features

- Audio Summary

## Current browse context:

cs.CL

< prev

|
next >

new
|
recent
| 2022-12

Change to browse by:

cs
cs.AI

## References & Citations

- SciX

- Google Scholar

- Semantic Scholar

## 1 blog link
( what is this? )

export BibTeX citation
Loading...

## BibTeX formatted citation

×

loading...

Data provided by:

## Bookmark

Bibliographic Tools

## Bibliographic and Citation Tools

Bibliographic Explorer Toggle

Bibliographic Explorer ( What is the Explorer? )

Connected Papers Toggle

Connected Papers ( What is Connected Papers? )

Litmaps Toggle

Litmaps ( What is Litmaps? )

scite.ai Toggle

scite Smart Citations ( What are Smart Citations? )

Code, Data, Media

## Code, Data and Media Associated with this Article

alphaXiv Toggle

alphaXiv ( What is alphaXiv? )

Links to Code Toggle

CatalyzeX Code Finder for Papers ( What is CatalyzeX? )

DagsHub Toggle

DagsHub ( What is DagsHub? )

GotitPub Toggle

Gotit.pub ( What is GotitPub? )

Huggingface Toggle

Hugging Face ( What is Huggingface? )

ScienceCast Toggle

ScienceCast ( What is ScienceCast? )

Demos

## Demos

Replicate Toggle

Replicate ( What is Replicate? )

Spaces Toggle

Hugging Face Spaces ( What is Spaces? )

Spaces Toggle

TXYZ.AI ( What is TXYZ.AI? )

Related Papers

## Recommenders and Search Tools

Link to Influence Flower

Influence Flower ( What are Influence Flowers? )

Core recommender toggle

CORE Recommender ( What is CORE? )

- Author

- Venue

- Institution

- Topic

About arXivLabs

## arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs .

Which authors of this paper are endorsers? |
Disable MathJax ( What is MathJax? )

We gratefully acknowledge support from our major funders ,
member institutions , ,
and all contributors.

About ·
Help ·
Contact ·
Subscribe ·
Copyright ·
Privacy ·
Accessibility ·
Operational Status (opens in new tab)
