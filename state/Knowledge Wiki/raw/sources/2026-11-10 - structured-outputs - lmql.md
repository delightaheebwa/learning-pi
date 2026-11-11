<!-- source: https://arxiv.org/abs/2212.06094 | type: html | hash: 855fc6b4f437f2df3b570aabf87b2c7c7b8ea3c6d5884a054cdddf2195547e7f | fetched: 2026-11-10 -->

Skip to main content

Report GitHub Issue

×

Title:

Content selection saved. Describe the issue below:

Description:

Submit without GitHub

Submit in GitHub

[archive]

[]

Why HTML?

[]Report Issue

[]Back to Abstract []Download PDF

[]Contents

[]Reading mode

[][][]Colour theme

1.  Abstract.
2.  1 Introduction
    1.  (Large) Language Models
    2.  Key Challenges in Using Language Models
    3.  This work: Language Model Programming via LMQL
    4.  Main Contributions
3.  2 Overview: Language Model Programming
    1.  2.1 Background: (Large) Language Models
        1.  Decoding
        2.  Masked Decoding
        3.  Few-Shot Prompting
    2.  2.2 Key Challenges
        1.  Interaction
        2.  Constraints & Token Representation
        3.  Efficiency and Cost
    3.  2.3 Language Model Programming in LMQL
4.  3 The LMQL Language
    1.  3.1 Built-in Functions
5.  4 The LMQL runtime: Query Execution & Decoding
    1.  Decoding Algorithm
    2.  Scripted Beam Search
    3.  Optimization
    4.  Language Model Integration
    5.  Decoding Internals
6.  5 Validation and Constraint Decoding
    1.  Naive Approach
    2.  5.1 Partial Evaluation
        1.  Value Semantics
        2.  Final Semantics
        3.  Notation
        4.  Application
        5.  Eager Validation
    3.  5.2 Generating Token Masks using FollowMaps
        1.  Follow Maps
        2.  Example
        3.  Soundness
        4.  Brzozowski derivatives
7.  6 Evaluation
    1.  6.1 Research Questions and Setup
        1.  Baseline
        2.  Datasets and Model
        3.  Metrics
        4.  Experimental Setup
    2.  6.2 Case Study 1: Chain-of-Thought Prompting
        1.  Query and Results
    3.  6.3 Case Study 2: Interactive Prompting
        1.  Query
        2.  Python Baseline
        3.  Results
    4.  6.4 Case Study 3: Arithmetic Reasoning
        1.  Query
        2.  Results
    5.  6.5 Discussion
8.  7 Related Work
    1.  Language Model Programming (LMP)
    2.  Constraining Language Models
9.  8 Conclusion
    1.  Acknowledgements
10. References
11. A Implementation
    1.  A.1 Language Runtime
        1.  Parser and Python Compatibility
        2.  Eager Evaluation Semantics
    2.  A.2 Model Integration
        1.  Inference API
        2.  Inference as a Service
        3.  Decoding Loop
    3.  A.3 Visual Debugger
        1.  Editor and Compiler
        2.  Decoder State
        3.  Validation and Masking
12. B Proofs
    1.  B.1 Proof of Theorem 
13. C More Evaluation Results
    1.  C.1 Interative Prompting (ReAct)
        1.  Interaction Traces
        2.  Python Baseline

License: CC BY 4.0

arXiv:2212.06094v1 [cs.CL] 12 Dec 2022

Prompting Is Programming: A Query Language For Large Language Models

Conference: ; Under submission;

Luca Beurer-Kellner Affiliation: ETH Zurich, Switzerland email: luca.beurer-kellner@inf.ethz.ch , Marc Fischer Affiliation: ETH Zurich, Switzerland email: marc.fischer@inf.ethz.ch and Martin Vechev Affiliation: ETH Zurich, Switzerland email: martin.vechev@inf.ethz.ch

Abstract.

Large language models have demonstrated outstanding performance on a wide range of tasks such as question answering and code generation. On a high level, given an input, a language model can be used to automatically complete the sequence in a statistically-likely way. Based on this, users prompt these models with language instructions or examples, to implement a variety of downstream tasks. Advanced prompting methods can even imply interaction between the language model, a user, and external tools such as calculators. However, to obtain state-of-the-art performance or adapt language models for specific tasks, complex task- and model-specific programs have to be implemented, which may still require ad-hoc interaction.

Based on this, we present the novel idea of Language Model Programming (LMP). LMP generalizes language model prompting from pure text prompts to an intuitive combination of text prompting and scripting. Additionally, LMP allows constraints to be specified over the language model output. This enables easy adaption to many tasks, while abstracting language model internals and providing high-level semantics.

To enable LMP, we implement LMQL (short for Language Model Query Language), which leverages the constraints and control flow from an LMP prompt to generate an efficient inference procedure that minimizes the number of expensive calls to the underlying language model.

We show that LMQL can capture a wide range of state-of-the-art prompting methods in an intuitive way, especially facilitating interactive flows that are challenging to implement with existing high-level APIs. Our evaluation shows that we retain or increase the accuracy on several downstream tasks, while also significantly reducing the required amount of computation or cost in the case of pay-to-use APIs (13-85% cost savings).

1. Introduction

Large Language Models (Large LMs - LLMs) (Vaswani et al., 2017; Devlin et al., 2019; Radford et al., 2019; Brown et al., 2020) have proven successful at various language-based tasks such as machine translation, text summarization, question answering, reasoning, code generation from text and many more. Due to these results LMs have become popular beyond the machine learning community and are slowly being integrated into many applications.

(Large) Language Models

Internally, language models operate on tokens, which are different from how humans perceive language. Given the tokenized version of some input, called the prompt, a large language model predicts the next token. That is, over a large vocabulary of tokens it assigns each a score or probability. A decoding procedure is then used, which by invoking the LM multiple times, computes a completion of the prompt. Commonly, the goal is to determine (or approximate) the highest probability continuation, however, as producing a particular token might lower the probability, before a subsequent token increases it, the decoding procedure often can include expensive search or backtracking strategies. Nonetheless, LM-based text completion remains powerful and can be leveraged for a wide range of downstream applications as listed above.

Key Challenges in Using Language Models

While the newer generation of language models can be prompted with examples or instructions in a conceptually simple manner, making the best use of these models and keeping up as new models are released requires a deep understanding of their internals, as well as the use of vendor-specific libraries and implementations. For example, as LMs operate on tokens, it can be hard to constrain the decoding procedure to a set of legal words or phrases. Further, many prompting techniques require either back-and-forth interaction between the LM and the user (e.g. chatbots like ChatGPT (OpenAI, 2022)) or very task-specific interfaces (e.g. to perform arithmetic calculations with external control logic). To implement such prompts, a lot of manual work and interaction with a model’s decoding procedure is required, which restricts the generality of the resulting implementations. Lastly, as an LM only produces one (sub-word) token at a time, completing a sequence may require many calls. Also, decoding becomes increasingly expensive as the prefix, the prompt, and the so-far generated response grow. Because of these factors, and as language models are typically very large neural networks, practical inference demands high computational costs and significant latency. In the case of pay-to-use APIs, such as OpenAI’s well-known GPT-3, this results in high usage costs per query answered.

⬇

beam(n=3)

"A list of good dad jokes. A indicates the "

"punchline \n"

"Q: How does a penguin build its house? \n"

"A: Igloos it together. END \n"

"Q: Which knight invented King Arthur's Round"

"Table? \n"

"A: Sir Cumference. END \n"

"Q: [JOKE] \n"

"A: [PUNCHLINE] \n"

from "gpt2-medium"

where

STOPS_AT(JOKE, "?") and STOPS_AT(PUNCHLINE, "END")

and len(words(JOKE)) < 20

and len(characters(PUNCHLINE)) > 10

⬇

1 argmax

2 "A list of things not to forget when "

3 "travelling:\n"

4 things = []

5 for i in range(2):

6 "- [THING]\n"

7 things.append(THING)

8 "The most important of these is [IMPORTANT]."

9 from "EleutherAI/gpt-j-6B"

10 where

11 THING in ["passport",

12 "phone",

13 "keys", ...] // a longer list

14 and len(words(THING)) <= 2

This work: Language Model Programming via LMQL

In this work, we propose the idea of language model programming, extending on natural language prompting by additionally allowing lightweight scripting and constraining of outputs. This facilitates a front-end/back-end separation for LM prompting, i.e. allows a user to specify complex interactions, control flow, and constraints without requiring knowledge of an LM’s internals such as tokenization, implementation, and architecture. Further, the constructed programs remain agnostic concerning the underlying LM, greatly improving portability. Overall, Language Model Programming (LMP) retains the simple natural-language-driven interface to LMs but additionally enables precise constraining, scripting, and efficient decoding, which as of now is not possible with existing high-level APIs.

To enable LMP, we present a novel language and runtime called the Language Model Query Language (LMQL). LMQL is a high-level language with declarative SQL-like elements and an imperative syntax for scripting. The underlying runtime is compatible with existing LMs and can be supported easily, requiring only a simple change in the decoder logic. LMQL can be used to express a wide variety of existing prompting methods (Reynolds and McDonell, 2021; Wei et al., 2022; Cobbe et al., 2021; Yao et al., 2022; Scholak et al., 2021; Shin et al., 2021) using simple, concise, and vendor-agnostic code. Further, purpose-designed evaluation semantics with support for partial evaluation and lookahead, enable us to optimize query execution end-to-end: LMQL leverages user constraints and scripted prompts to prune the search space of an LM by masking, resulting in an up to 80% reduction of inference cost. We showcase two examples of simple LMQL programs in Fig. 1.

Main Contributions

Our core contributions are:

- •
  We introduce the novel paradigm of language model programming, formulating and addressing several challenges that arise with recent LM prompting techniques (Section 2).
- •
  LMQL, an efficient, high-level query language for LMs with support for scripted prompting and output constraining. (Sections 4 and 3).
- •
  A formal model of eager, partial evaluation semantics based on so-called final and follow abstractions. Using these, we can automatically generate model-specific token masks for LM decoding, given just a set of high-level constraints (Section 5).
- •
  A comprehensive evaluation of LMQL that shows how to express a wide range of common and advanced prompting techniques as simple and concise LMQL programs, and that the resulting programs enable more efficient decoding by reducing inference cost and latency by 13-80% while allowing for more accurate decoding. (Section 6).

2. Overview: Language Model Programming

In this section we first review how modern language models (LMs) are utilized and the challenges that arise from this. Then, based on examples, we show how Language Model Programming (LMP) can overcome or simplify these challenges and outline the rest of the paper.

While our goal with LMP is to improve the usage of state-of-the-art large language models (LLMs), e.g. GPT (Radford et al., 2019) variants, the size of the model does not change how LMP is employed, we thus utilize the acronym LM rather than the more common LLM in the remainder of this text.

⬇

"She sells seashells by the seashore."

["She", "␣sells", "␣seas", "hell", "s",

"␣by", "␣the", "␣se", "ash", "ore", "."]

2.1. Background: (Large) Language Models

Current language models (Vaswani et al., 2017; Radford et al., 2019; Brown et al., 2020) operate on a vocabulary 𝒱of (sub-word) tokens. Fig. 2 shows this for a simple example, where we see that common words have their own token (even with a space in front), while more rare words are split into multiple tokens. Similar to formal languages we let 𝒱^(*) denote all possible sequences of tokens over 𝒱. Given an input sequence of words w₁, …w_(t), a tokenizer then first maps the sequence of words to a sequence of tokens t₁, …, t_(k) and then a language model f : 𝒱^(k) → ℝ^(|𝒱|) predicts a score z = f(t₁, …, t_(k)) for every possible next token. We treat the implementation of f as a black box (it does not need to be a neural network), yet in practice virtually all such models are variants of the Transformer architecture (Vaswani et al., 2017). Via the softmax function, the resulting scores z can then be turned into a probability distribution over the vocabulary 𝒱:

  -- ------------------------------------------------------------------------------ --
     $$\mathrm{softmax}({\bm{z}})_{i}:=\frac{\exp(z_{i})}{\sum_{j}\exp(z_{j})}.$$
  -- ------------------------------------------------------------------------------ --

Decoding

Based on this, the language model f is applied multiple times to produce a sequence t₁, …, t_(K) for K > k. When we want to pick the (i + 1)-th token, softmax(f(t₁, …, t_(i))) gives a probability distribution over this next token. Several ways of picking from this distribution have been discussed in the literature. Below we review a selection of the most popular ones. Each method is iterated until a special end-of-sequence-token eos is predicted or another stopping criterion is met. This can be seen as sampling from a distribution over 𝒱^(*), and thus, some of these methods can return multiple possible decodings:

- •
  Greedy decoding (or Argmax decoding) picks the token with the highest probability at each turn and feeds it back into the model to predict the next one (this corresponds to a depth-first search of all possible decodings). Importantly, this decoding does not necessarily (and in practice very rarely) corresponds to the decoding with the highest overall probability (obtained by multiplying all individual probabilities of selected tokens). As this determines just the most probable decoding. Overall, only one decoding is returned.
- •
  Sampling, treats the output softmax distribution as a categorical distribution from which a next token can be sampled. With sampling, it is common to decode multiple, e.g., n, outputs.
- •
  Full decoding enumerates all possible sequences to the end and picks the one with the highest probability. This corresponds to a breadth-first search of all possible decodings. However, such enumeration (even with optimizations) is prohibitively expensive.
- •
  Beam search picks the middle ground between greedy and full decoding. It maintains a set of n beams at all times, each corresponding to a predicted sequence. For each sequence, it predicts a possible next token and again picks the top n from the resulting n|𝒱| sequences. In the end, the top sequence from the n resulting beams is picked.

For beam search and sampling, an additional parameter, the temperature τ ∈ ℝ^( > 0), can be used to control the diversity of the output, by using softmax(z/τ) rather than softmax(z). A higher τ leads to more diverse outputs, while a lower τ leads to more likely outputs.

Masked Decoding

A particular case of decoding is if we can already rule out certain tokens at certain positions. This means we can simply ignore these tokens and perform decoding over the remaining set. In such a case, we assume that we are given a mask m ∈ {0, 1}^(|𝒱|), where a 1 denotes a viable token and a 0 denotes a discarded one. We can apply the decoding methods discussed above on m ⊙ softmax(z), where ⊙ denotes element-wise multiplication. (Note that, to obtain correct probabilities again this vector needs to be scaled by 1/∑_(i)(m × softmax(z))_(i).) An extreme case of this occurs when asking the model yes/no questions or classification tasks (e.g., to "positive" or "negative"). There we only allow the model to respond with the respective word and thereby the corresponding tokens. Another case where this is applied, is when decoding a formal language such as in code completion or synthesis, where only a subset of possible tokens can form a legal program according to a grammar.

⬇

Translate English to French:

sea otter => loutre de mer

peppermint => menthe poivrée

plush giraffe => girafe peluche

cheese =>

Few-Shot Prompting

Few-shot prompting (Brown et al., 2020) refers to the idea that language models do not need to be specifically trained for a downstream task (e.g. classification, question answering, etc.). Rather, it is sufficient to train them on broad text-sequence prediction datasets (e.g., the pile (Gao et al., 2020)) and to provide context in the form of examples when invoking them. We show an example of this in Fig. 3, where our goal is to translate "cheese" from English to French. To this end we provide several examples of successful translation pairs and then ask the LM to complete the pair for "cheese" in the same syntax, where we expect the model to predict the tokens forming fromage followed by the end-of-sequence token. In this way, translation and other tasks can be reframed as simple sequence completion tasks, which makes LMs powerful multi-task reasoners.

2.2. Key Challenges

Here we want to outline challenges faced by current approaches to LM prompting, before outlining in Section 2.3 how LMP via our implementation LMQL can be used to overcome them.

Interaction

Consider for example the approach from Reynolds and McDonell (2021), which discusses the idea of meta prompts, where in order to obtain the answer to a particular question, a language model is first asked to expand the prompt, which is then fed again to the same model in order to obtain an answer. An example, inspired by this approach is shown in Fig. 4 (a). There the goal is to ask the LM for the answer to the question "What is the circumference of the earth?". In meta prompting we first ask the language model for the name of an expert regarding this question, and then ask how this expert would answer the question. With current LM interfaces, one would input the first part of the prompt, manually invoke the LM to complete the sequence with the expert name, then extract the expert name from the LM output, and enter it manually into the rest of the template, and again feed it to the LM to obtain the actual answer. This current approach requires a large amount of manual interaction via an API, or even with a human in the loop. Further, due to this manual intervention, the name of the expert will be fixed before the actual answer is generated. For decoding procedures that aim to optimize the overall likelihood of the result, this may produce worse results then letting the optimization procedure jointly optimize both inputs.

(a) Manual Prompt
What is the circumference of the earth?
I believe the best person to answer this question is        .
Indeed,         addressed this question:
Prompt 1 LM completion Prompt 2

 

(c) LMQL query

⬇

What is the circumference of the earth? I believe

the best person to answer this question is [EXPERT]

Indeed, {EXPERT} addressed this question: [ANSWER]

 

(d) LMQL constraint

⬇

len(words(EXPERT)) <= 3 and stop_at(EXPERT, ".")

(b) GPT-2 completions after Prompt 1:

- •
  a physicist
- •
  an astronomer
- •
  a geologist
- •
  Neal deGrasse Tyson
- •
  William O’Malley, who has a PhD in Geodesy and is a professor at Colorado State University.
- •
  the person having the knowledge and answer will probably have to refer to the relevant geophysics book and equations derived from that theory.
- •
  a physicist, like Thomas Kugler at UC Irvine or one of the other physicists working with NASA …
- •
  a man named David
- •
  actually Mother Earth herself?

Constraints & Token Representation

Another issue of this example query arises when we consider the completions as shown in Fig. 4 (b). Sometimes, LMs will digress during generation and produce long ongoing sequences of text. While some answers work well for substitution in the next part of the prompt, others produce awkward and clumsy sentences at least and wrong sentences at worst. This demonstrates, that often as a user, we actually have constraints regarding the generated text, which sometimes are violated, as the LM will not adhere to them naturally. Ideally, these constraints would be expressible in terms of human understandable concepts and logic, since users will reason in terms of words, sentences and entities, not on a token level like the LM. In contrast, practical methods of constraining LMs in this way (Shin et al., 2021; Poesia et al., 2022) still involve a lot of manual implementation effort and model-level understanding of the decoding procedures, tokenization and vocabulary of the LM.

Efficiency and Cost

Lastly, efficiency and performance remain big challenges. While a lot of work went into making the inference step in modern LMs more efficient, they still require expensive, high-end GPUs to be run with reasonable performance. Because of this, many practical users resort to hosted models running in the cloud, some of which are even guarded behind paid APIs. For this reason, LM querying can become very expensive, both in a computational and a financial sense. When relying on Language Model Programming and constraints however, new opportunities for optimization arise, as predefined behavior and a limitation of the search space can be exploited to reduce the number of times an LM has to be invoked. In this setting, the cost of validation, parsing and mask generation is negligible compared to the vast cost of even just a single LM call.

2.3. Language Model Programming in LMQL

Now we consider Language Model Programming instantiated via our implementation LMQL, and how it can help overcome these challenges. Shown in Fig. 4 (c), we write the same query as before in LMQL syntax (formally defined in Section 3). Here, when we encounter the construction [VAR], everything before the variable is fed to the LM and the answer found via decoding is then assigned to the variable VAR, while a variable name in braces just recalls previously defined variables. This greatly simplifies the prompt and removes the need for manual interaction. Additionally, it enables the use of decoding procedures that consider both the expert name and answer jointly (as discussed in Section 4).

Further, to address the issue of long on-running sentences, LMQL allows constraints on the variable parts of the LM interaction on an intuitive level, e.g. words and phrases Fig. 4 (d) shows the intuitive LMQL syntax for this, also discussed formally later on. Here, the constraints enforce that the decoded tokens for EXPERT are at most three words and that decoding stops if the sequence ends in a ".". While it is possible to specify a maximum length with current query APIs, they usually work directly on the (model-specific) token level and thus can not be mapped 1-to-1 to longer sequences. In contrast, LMQL allows the intuitive declaration of high-level constraints that are automatically translated into token level inference masks, using partial evaluation semantics discussed in Section 5.

LMQL Program

⬇

⟨decoder⟩ ⟨query⟩

from ⟨model⟩

[where ⟨cond⟩]

[distribute ⟨dist⟩]

⬇

⟨decoder⟩ ::= argmax beam(n=@⟨int⟩@) sample(n=⟨int⟩)

⬇

⟨query⟩ ::= ⟨python_statement⟩+

⬇

⟨cond⟩ ::= ⟨cond⟩ and ⟨cond⟩ @⟨cond⟩@ or @⟨cond⟩@ not ⟨cond⟩ @⟨cond_term⟩@ ⟨cond_term⟩ ⟨cond_op⟩ ⟨cond_term⟩

⟨cond_term⟩ ::= ⟨python_expression⟩

⟨cond_op⟩ ::= < > = in

⬇

⟨dist⟩ ::= ⟨var⟩ over ⟨python_expression⟩

3. The LMQL Language

Here we provide a high-level explanation of the syntax of LMQL, before discussing the runtime and language semantics next. For concrete examples, consider the LMQL programs given in Fig. 1.

The grammar of LMQL is shown in Fig. 5. An LMQL program has 5 parts: the decoder, the actual query, the from clause specifying the queried model, the where clause specifying constraints, and lastly a distribution instruction. The decoder and model are both specified by strings, while query and constraints are given in python syntax. We now explain these components in detail:

The ⟨query⟩ block models the interaction with the model. Informally it can be thought of as the body of a python function subject to some restrictions and additions: i) We do not allow the declaration of inner functions (however, imports can be made), and ii) Each top-level string is treated as a direct query to an LM. These query strings allow for two specially escaped subfields, similar to python f-strings¹¹ 1 https://peps.python.org/pep-0498: 1) "{varname}" recalls the value of a variable from the current scope. And 2.), "[varname]" represents a phrase that will be generated by the LM, also called hole. When the language model generates values for these holes, they will be subject to the constraints defined in the where clause of the query. Under these constraints, the decoding procedure specified by ⟨decoder⟩ (disussed next) will be used. Once decoding finishes, a corresponding variable will be created in the scope of the query program and assigned this value. If a variable with the same name already exists, it will be overwritten.

⟨decoder⟩ denotes the decoding procedure employed by the LMQL runtime when solving the query. The presented version of LMQL enables argmax, sample and beam. argmax and sample work as discussed in Section 2.1. beam however, denotes a novel procedure called scripted beam search which performs beam search jointly over all holes and control flow. We discuss this further in Section 4. Once completed, the result of a query program is comprised of a number of things: It contains the interaction trace, that is, the whole text transcript of the LMQL query with the answers of the LM in the holes substituted. Further, the set of all hole variables is accessible, allowing clients to directly access specific parts of the LM response. In case of sample and beam, the parameter n specifies the number of samples or beams respectively. In this case, n interaction traces with the respective variables will be returned. Note, that we omit a detail in favor of readability: In practice, we allow further parameters to the decoder to be specified, e.g. the temperature τ.

To illustrate queries and decoding, consider Fig. 1(a) which utilizes a query purely made from strings, and Fig. 1(b) which utilizes a combination of strings and control flow. An corresponding interaction trace is shown in Fig. 6. Note how in the program on the right, THING is reassigned on each iteration of the loop, which is in line with the semantics of python.

A list of things not to forget when travelling:
- sun screen
- beach towel
The most important of these is sun screen.

A list of things not to forget when travelling:
- keys
- passport
The most important of these is sun screen.
A list of things not to forget when travelling:
- watch
- hat
The most important of these is keys.

from⟨model⟩ denotes which LM to use. In our implementation ⟨model⟩ denotes a string identifying a text generation model from the popular Hugging Face Model repository²² 2 https://huggingface.co/models. However, this could easily be extended to a local repository, or even hosted, API-gated models like GPT-3 (Brown et al., 2020).

where⟨condition⟩ places constraints on the [varname] hole variables, thereby constraining the language model in what it can generate. Constraints can be an arbitary conjunction or disjunction of ⟨cond_expr⟩ which allow comparison (<, >, =) and membership (in) checks between standard python expressions. Note that, as hole variables are added to the scope of the query program, they can also be referenced there. We allow any deterministic pure python function along with constants. We distinguish, for reasons discussed in Section 5 , built-in functions (discussed next) and user-defined functions, which also includes standard python built-ins. If we invoke the LM multiple times for the same variable, like for the THING variable in Fig. 1(b), the constraints apply to all intermediate values.

Lastly, distribute⟨var⟩ in⟨python_expression⟩ is an optional instruction that can be added to augment the returned result. Here, ⟨var⟩ must refer to the last hole in the query and the python expression to a set (or other iterable). We will refer to this set as the support.

A list of things not to forget when travelling:
- sun screen
- beach towel
The most important of these is $\begin{cases}\text{{\color[rgb]{0.1211,0.4648,0.707}sun screen}}&65\%\\
\text{{\color[rgb]{0.1211,0.4648,0.707}beach towel}}&35\%\end{cases}$.

For queries with distribution clause, the interaction trace will only be evaluated up to prior to the last hole according to the specified decoding method. In addition to the holes decoded so far and the interaction trace, the last variable is not decoded, but rather the probability distribution over support. Thus for every value in the support the likelihood of this output is evaluated. Fig. 7 shows this for the example from Fig. 1(b). In this case the interaction trace up to the brace is produced, as well as the distribution over the possible values after. This is particularly useful to encode classification tasks such as sentiment analysis, where the downstream user is interested in the probability distribution over e.g. {POSITIVE, NEGATIVE}.

  --------------------------------- ------------------------------------------------
  [w₁, …w_(k)] ← words(⟨var⟩)       //splits ⟨var⟩ into words w₁, …w_(k)
  [s₁, …s_(k)] ← sentences(⟨var⟩)   //splits ⟨var⟩ into sentences s₁, …s_(k)
  b ← stop_at(⟨var⟩, t)             //indicates if ⟨var⟩ ends in token or string t
  --------------------------------- ------------------------------------------------

3.1. Built-in Functions

In the where clause, we support a set of built-in functions in addition to standard python code. For instance, we implement the functions words, sentences that, given a string or token representation, convert it to the desired representation. To enable users to explicitly define stopping criteria, we also provide stops_at, which can be used to provide constraints within the where clause. stops\_at(⟨var⟩,⟨str⟩) expresses that when the variable ⟨var⟩ is decoded it should stop decoding of the variable when the specified phrase is encountered. For similar purposes we provide len (not shown), which overloads its default python counterpart with the comparable functionality – it returns the length of a string (or iterable). For these designated, built-in functions, we implement additional semantics, required for the efficient output validation and the generation of decoding masks, as discussed in Section 5.

4. The LMQL runtime: Query Execution & Decoding

Input: string s, trace u, scope σ, language model f

1 if s contains [⟨<varname>⟩] then

    2 s_(pre), varname, s_(post) ← unpack(s)

    // e.g. "a [b] c" → "a ", "b", " c"

    3 u ← us_(pre) // append to trace

    4 v ← decode(f,u) // use the LM for the hole

    5 σ[varname] ← v // updated scope

    6 u ← uv // append to trace

7 else if s contains {⟨varname⟩} then

    8 varname ← unpack(s) // e.g. "{b}" → "b"

    9 v ← σ[varname] // retrieve value from scope

    10 s ← subs(s, varname, v) // replace placeholder with value

    11 u ← us // append to trace

12 else

    13 u ← us // append to trace

14 end if

We now discuss how the LMQL runtime executes a query. To this end we consider the execution of the ⟨query⟩ as a python program. In this execution we assume that, i) functions are pure and do not cause side effects, ii) functions are deterministic. Ignoring the constraints in where for now, the ⟨query⟩ is executed line-by-line like a regular python function with one difference: At the beginning of the execution, the interaction trace u ← ϵ is initialized to the empty string ϵ. Whenever a top-level string s is encountered in the program execution, the procedure in Algorithm 1 is evoked. If a hole [⟨varname⟩] is encountered, the string s is split into the text preceeding the hole s_(pre), the variable name and the text after the hole s_(post). s_(pre) is directly appended to u ³³ 3 As is common we use multiplication to denote string concatenation and write uv to denote the concatenation of u and v., which is then used to decode a sequence v to fill the hole from the LM f. This string is then assigned to ⟨varname⟩ in the scope σ of the python program.

If {⟨varname⟩} is encountered, the value of ⟨varname⟩ is retrieved from scope σ and the placeholder is replaced with the value. In all cases the string s (with the decoded or substituted text replaced) is added to u. Note that, for simplicity in Algorithm 1 we assume that there is at most one hole or placeholder in a string s. In practice we allow multiple. Formally this can be thought of as splitting s into a list of strings and then applying Algorithm 1 to each resulting string.

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| program line          | update                                                                                                                                                                                        | state after update                                                                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| 1                     |                                                                                                                                                                                               |   ---- ----                                                                                                   |
|                       |                                                                                                                                                                                               |   u=   ϵ                                                                                                      |
|                       |                                                                                                                                                                                               |   g=   {}                                                                                                     |
|                       |                                                                                                                                                                                               |   ---- ----                                                                                                   |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| 2                     |   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |   ---- ---------------------------------------                                                                |
|                       |   $s\leftarrow\text{{"A\textvisiblespace{}list\textvisiblespace{}of\textvisiblespace{}things\textvisiblespace{}not\textvisiblespace{}to\textvisiblespace{}forget\textvisiblespace{}when"}}$   |   u=   "A␣list␣of␣things␣not␣to␣forget␣when"                                                                  |
|                       |   u ← us                                                                                                                                                                                      |   g=   {}                                                                                                     |
|                       |   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |   ---- ---------------------------------------                                                                |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| 3                     |   -------------------------------------------------------------------------                                                                                                                   |   ---- -----------------------------------------------------                                                  |
|                       |   $s\leftarrow\text{{"travelling:\textvisiblespace{}\textbackslash{}n"}}$                                                                                                                     |   u=   "A␣list␣of␣things␣not␣to␣forget␣when travelling␣\n"                                                    |
|                       |   u ← us                                                                                                                                                                                      |   g=   {}                                                                                                     |
|                       |   -------------------------------------------------------------------------                                                                                                                   |   ---- -----------------------------------------------------                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| 4, i = 0              |   ------------------------------------------------------------------------------------------------------------------------------------                                                        |   ---- ---------------------------------------------------------------                                        |
|                       |   $s\leftarrow\text{{"-\textvisiblespace{}[THING]\textbackslash{}n"}}$                                                                                                                        |   u=   "A␣list␣of␣things␣not␣to␣forget␣when travelling␣\n                                                     |
|                       |   $s_{\text{pre}},\text{varname},s_{\text{post}}\leftarrow\text{{"-\textvisiblespace{}"}},\text{{THING}},\text{{\textbackslash{}n}}$                                                          |        -␣sun␣screen\n"                                                                                        |
|                       |   u ← us_(pre)                                                                                                                                                                                |   g=   $\{i=0,\text{THING}=\text{{"sun\textvisiblespace{}screen"}},$                                          |
|                       |   $v\leftarrow\text{{\color[rgb]{0.1211,0.4648,0.707}{"sun\textvisiblespace{}screen"}}}=\texttt{decode(${\bm{f}}$, $u$)}$                                                                     |        $\text{things}=[\text{{"sun\textvisiblespace{}screen"}}]\}$                                            |
|                       |   u ← uvs_(post)                                                                                                                                                                              |   ---- ---------------------------------------------------------------                                        |
|                       |   g[varname] ← v                                                                                                                                                                              |                                                                                                               |
|                       |   ------------------------------------------------------------------------------------------------------------------------------------                                                        |                                                                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+
| 4, i = 1              |   ------------------------------------------------------------------------------------------------------------------------------------                                                        |   ---- ------------------------------------------------------------------------------------------------------ |
|                       |   $s\leftarrow\text{{"-\textvisiblespace{}[THING]\textbackslash{}n"}}$                                                                                                                        |   u=   "A␣list␣of␣things␣not␣to␣forget␣when travelling␣\n                                                     |
|                       |   $s_{\text{pre}},\text{varname},s_{\text{post}}\leftarrow\text{{"-\textvisiblespace{}"}},\text{{THING}},\text{{\textbackslash{}n}}$                                                          |        -␣sun␣screen\n                                                                                         |
|                       |   u ← us_(pre)                                                                                                                                                                                |        -␣beach␣towel\n"                                                                                       |
|                       |   $v\leftarrow\text{{\color[rgb]{0.1211,0.4648,0.707}{"beach\textvisiblespace{}towel"}}}=\texttt{decode(${\bm{f}}$, $u$)}$                                                                    |   g=   $\{i=1,\text{THING}=\text{{"beach\textvisiblespace{}towel"}},$                                         |
|                       |   u ← uvs_(post)                                                                                                                                                                              |        $\text{things}=[\text{{"sun\textvisiblespace{}screen"}},\text{{"beach\textvisiblespace{}towel"}}]\}$   |
|                       |   g[varname] ← v                                                                                                                                                                              |   ---- ------------------------------------------------------------------------------------------------------ |
|                       |   ------------------------------------------------------------------------------------------------------------------------------------                                                        |                                                                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------+

We illustrate this execution model in Fig. 9 where we list the evaluation steps of the first 7 lines of Fig. 1(b). The first two lines are directly appended to the interaction trace u, while the next two lines (emitted inside the for loop) contain holes, which invokes the decode function, discussed next.

Input: trace u, scope σ, language model f

Output: decoded sequence v

1 v ← ϵ

2 while True do

    3 m ← compute_mask(u, σ, v)

    4 if ⋀_(i)(m_(i) = 0) then break

    5 ${\bm{z}}\leftarrow\nicefrac{{1}}{{Z}}\;\cdot{\bm{m}}\odot\mathrm{softmax}({\bm{f}}(uv))$

    6 t ← pick(z)

    7 if $t=\textsc{eos}$ then break

    8 v ← vt

9 end while

Decoding Algorithm

When decode is invoked, the decoding procedure declared at the top of the LMQL program is utilized to generate a value for the placeholder. Decoding is usually stopped i) when an end-of-sequence token is produced, or ii) when no more tokens can be produced due to the given constraints (discussed in Section 5). In Algorithm 1 we assume that decode returns a de-tokenized string v rather than a sequence of tokens.

For decoding algorithms that just output a single possible sequence, such as argmax or sample(n=1) the straightforward combination of Algorithm 1 and standard decoding function denotes the full end-to-end decoding procedure. However, a particular case occurs if multiple results are produced, e.g., sample(n=⟨int⟩) produces n possible interaction traces u. In this case, we track n parallel execution of the query program, where decode acts non-deterministically. In practice, we execute all calls in lockstep, such that we can batch calls to the underlying model f and therefore improve efficiency.

Scripted Beam Search

For the decoder beam(n=⟨int⟩), the query is executed similarly: When the first hole in the interaction is encountered, n beams (with their estimated probabilities) are created and retained. Each beam then corresponds to an interaction trace u, for which the query function is executed independently. Note that each u might cause different control flow. Further, since we only consider the top n beams at each step, we also only continue query execution for the top n beams. Interaction traces that are discarded along the way, are pruned and not extended further. On termination, the overall query result corresponds to final top n interaction traces.

Optimization

For large n the execution of query code for multiple samples or beams can potentially be expensive, especially if expensive functions are involved on top of the LM output. However, as we assume functions to be pure and deterministic, results can be cached based on the function arguments, therefore greatly decreasing the total number of required function invocations.

Language Model Integration

As shown in our decoding algorithm, we do not impose any restrictions on language model f, apart from being able to access the resulting distribution over vocabulary tokens. As fundamentally, this is the core interface of most language models, we can easily integrate them without further changes. However, we note that our decoding procedure requires our runtime to be invoked for each token, which can be expensive for API-gated models that are billed by the number of API calls. For more details on the integration of the LMQL runtime with a language model, see Section A.2.

Decoding Internals

Algorithm 2 shows the internals of a decoding procedure (decode in Algorithm 1) for a single sample or beam. Here, the goal is to build up the string v, initialized to the empty string ϵ in Algorithm 2, by appending tokens t to it. For each new token we compute a mask m over the vocabulary, which only allows tokens that result in legal sequences, e.g., those that satisfy our where constraints. If we can not produce any further tokens (i.e., ⋀_(i)m_(i) = 0) we stop the decoding procedure. Otherwise, we re-normalize m ⊙ z into a probability distribution, i.e. a vector where entries add up to 1, by dividing it by Z = ∑_(i)(m ⊙ z)_(i). The function pick depends on the exact decoding algorithm (e.g. argmax, sample, beam) and is used to pick a token t from the distribution. If we obtain an end-of-sequence eos token we stop. If we return early because no legal tokens are available, we are unable to find a response to the query that fulfils the constraints. If we return at eos, we found a legal decoding. Next, we discuss how to compute the mask m, such that the specified constraints can be enforced during decoding.

5. Validation and Constraint Decoding

In this section we show how our decoding procedure can be extended to handle validation and constrained decoding. In particular, we discuss how the constraints from the where clause can be used to automatically and efficiently find decoding masks for each step of decoding. Our main contribution to this end is a purpose-designed, eager execution model that supports partial evaluation and lookahead. To motivate this, we first discuss a naive solution and then introduce the idea of final semantics and FollowMaps, the two abstractions at the core of our evaluation model.

Naive Approach

Input: trace u, scope σ, language model f

Output: decoded sequence v

1 Function decode_step(f, u, v)

    2 z ← softmax(f(uv))

    3 m ← 1^(|𝒱|)

    4 do

       5 $t\leftarrow\text{pick}(\nicefrac{{1}}{{Z}}\cdot{\bm{m}}\odot{\bm{z}})$

       6 if $t\neq\textsc{eos}$ then decode_step(u, v, vt)

       7 else if $t=\textsc{eos}\land\text{check}(u,vt)$ then return v

       8 else m[t] ← 0

    9 while ⋁_(i)m_(i) = 1

10 decode_step(f, u, ϵ)

We first consider a naive approach to constrained decoding, outlined in Algorithm 3. Here, similar to Algorithm 2, we start with an empty string v and append tokens. However, we don’t assume a function compute_mask and thus apply a backtracking-based approach, where we generate sequences up to the eos token and then check if uv satisfies our constraints. Checking the constraints, denoted as check, is easy as it just amounts to the evaluation of an expression.

Note that here we assume that uv is sufficient to check the constraints, at least up to the hole corresponding to v. If this is not possible, we would need to perform the generation sequence for the sequence of all holes, advancing to the next one, once eos is produced, but potentially backtracking over all, if validation fails at some point later on.

This strategy leads to multiple problems: First, navigating the search space of sequences using backtracking is computationally expensive, especially when considering that the search space of LMs (even when trained well), is still a combinatorial explosion due to the many likely continuations of any given sequence. Second, querying the LM can be very expensive. State-of-the-art models often require high-end GPUs or are only available as API-gated, paid services. Thus, every token that is generated and later dismissed incurs a significant computational or financial cost.

With this in mind, we implement eager, partial evaluation semantics that model not only whether or not an expression holds, but also whether the expression can be guaranteed to never hold for any possible continuation of the currently-generated sequence. This allows us to terminate early if validation already provides a definitive result. Further, our semantics enable us to automatically compute a subset of next tokens that are guaranteed to violate the expression. Using this token set, we can effectively prune the search space of an LM and prevent the costly generation of invalid sequences before they are even generated.

5.1. Partial Evaluation

  ------------------------- ----------------------------------------------------------------------------
  expression                Final[⋅ ; σ]
  ⟨const⟩                   fin
  python variable ⟨pyvar⟩   var
  previous hole ⟨var⟩       fin
  current var ⟨var⟩         inc
  future hole ⟨var⟩         inc
  words(v)                  Final[v]
  sentences(v)              Final[v]
  len(v)                    Final[v]
  number equality n == m    $\begin{cases}\text{{fin}}{}&\text{if }\text{{Final}}[n]=\text{{fin}}\\
                            &\;\land\;\text{{Final}}[m]=\text{{fin}}\\
                            \text{{var}}{}&\text{else}\end{cases}$
  string equality x == y    $\begin{cases}\text{{fin}}{}&\text{if }\text{{Final}}[x]=\text{{fin}}\\
                            &\;\land\;\text{{Final}}[y]=\text{{fin}}\\
                            \text{{fin}}{}&\exists i\bullet x[i]\neq y[i]\\
                            &\;\land\;\text{{Final}}[x]\neq\text{{var}}\\
                            &\;\land\;\text{{Final}}[y]\neq\text{{var}}\\
                            \text{{var}}{}&\text{else}\end{cases}$
  ------------------------- ----------------------------------------------------------------------------

  ---------------------------------- -----------------------------------------------------------------------------------------------------------------------------------
  expression                         Final[⋅ ; σ]
  function fn(τ₁, …, τ_(k))          $\begin{cases}\text{{fin}}{}&\text{if }\bigwedge_{i=1}^{k}a(\tau_{i})=\text{{fin}}\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  stop_at(var, s)                    $\begin{cases}\text{{fin}}{}&\text{if }\llbracket{var}\rrbracket{}_{\sigma}${.endswith}$(s)\\
                                     &\;\wedge\;\text{{Final}}[var]=\text{{inc}}\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  x in s for strings x, s            $\begin{cases}\text{{fin}}{}&\text{if $x$ {in} $s$}\land\text{{Final}}[x]=\text{{fin}}\\
                                     &\;\land\;\text{{Final}}[s]=\text{{inc}}\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  e in l for string e, set l         $\begin{cases}\text{{fin}}{}&\text{if }\not\exists i\in l\bullet i\texttt{.startswith(e)}\\
                                     &\;\land\;\text{{Final}}[x]\in\{\text{{inc}}{},\text{{fin}}{}\}\\
                                     &\;\land\;\text{{Final}}[l]=\text{{fin}}\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  x < y                              $\begin{cases}\text{{fin}}{}&\text{if }$x$<$y$\land\text{{Final}}[x]\in\{\text{{dec}}{},\text{{fin}}{}\}\\
                                     &\;\land\;\text{{Final}}[y]\in\{\text{{inc}}{},\text{{fin}}{}\}\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  a and b                            $\begin{cases}\text{{fin}}{}&\text{if }\exists v\in\{a,b\}\bullet\llbracket{v}\rrbracket{}_{\sigma}^{F}=\text{{fin}}{}(\bot)\\
                                     \text{{fin}}{}&\text{if }\forall v\in\{a,b\}\bullet\llbracket{v}\rrbracket{}_{\sigma}^{F}=\text{{fin}}{}(\top)\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  a or b                             $\begin{cases}\text{{fin}}{}&\text{if }\exists v\in\{a,b\}\bullet\llbracket{v}\rrbracket{}_{\sigma}^{F}=\text{{fin}}{}(\top)\\
                                     \text{{fin}}{}&\text{if }\forall v\in\{a,b\}\bullet\llbracket{v}\rrbracket{}_{\sigma}^{F}=\text{{fin}}{}(\bot)\\
                                     \text{{var}}{}&\text{else}\end{cases}$
  not a                              Final[a]
  ---------------------------------- -----------------------------------------------------------------------------------------------------------------------------------

Given some expression e occurring in the where condition, some interaction trace u and some global scope σ, we define the evaluation semantics of ⟦e⟧_(σ) on multiple levels:

Value Semantics

First, we interpret e on a value level, meaning we define ⟦e⟧_(σ) as the value of evaluating e as a python expression, given the variable values assigned in σ.

Final Semantics

In addition to value semantics, we define so-called final semantics as a function Final[e; σ]. The function Final annotates each computed value with one of the annotators 𝒜 = {fin, var, inc, dec}. Depending on the annotator, the value of an expression e, as decoding progresses is either considered fin (it will retain a fixed value), var (its value may still change), inc (its value will monotonically increase) or dec (its value will monotonically decrease). For the latter two, we consider monotonicity both in a numerical sense and in a set theoretic sense (e.g. growing sets, append-only strings). Based on this, Final can be computed by applying it recursively to the intermediate results of a top-level expression e, as defined by the rules in Table 1.

Notation

In the following, we use the short-hand notation Final[e] instead of Final[e; σ], as we assume that the scope is always the global scope. Further, we will sometimes refer to value and final semantics jointly, i.e. we will denote the value of an expression e as ⟦e⟧_(σ) = v and Final[e] = fin, simply as ⟦v⟧_(σ)^(F) = fin(v). For boolean expressions we let ⊤ denote True and ⊥ False.

Application

Using Final, we can evaluate where constraints, even on outputs that are only partially available, i.e. a currently generating sequence. For this, we evaluate all (sub-)expressions, as far as possible. For expressions that depend on future hole values, we set their result to None and define all other operators to be tolerant of that. For instance, given some validation constraints a ∧ b, where b cannot be determined yet, we can evaluate a and return False if a evaluates to fin(⊥). This is possible, as fin indicates that no matter the value of b, a will always evaluate to ⊥, even as more tokens of the generated sequence are revealed.

Eager Validation

Final semantics provide an abstraction that enables us to implement more aggressive short-circuiting over validation conditions. These can be executed on each new token rather than waiting for the entire sequence to be generated. Using this, validation can be applied more eagerly, detecting invalid sequences before they are completed. However, final semantics do not help us to mask any next tokens in the decoding function. To enable this, we additionally introduce a third level of evaluation semantics, which we call follow semantics, discussed next.

  ------------------------------- ----------------------------------------------------------------------------------------------
  expression                      Follow[⋅](u, t)
  ⟨const⟩                         ⟦⟨const⟩⟧_(σ)
  python variable ⟨pyvar⟩         ⟦pyvar⟧_(σ[v ← vt])
  previous hole ⟨var⟩             ⟦⟨var⟩⟧_(σ)
  current var v                   $\begin{cases}\text{{fin}}{}\!\left({v}\right)&\text{if }t=\textsc{eos}\\
                                  \text{{inc}}{}\!\left({vt}\right)&\text{else}\end{cases}$
  future hole ⟨var⟩               None
  words(v)                        $\begin{cases}\text{{fin}}{}\!\left({w_{1},\dots,w_{k}}\right)&\text{if }t=\textsc{eos}\\
                                  \text{{inc}}{}\!\left({w_{1},\dots,w_{k}}\right)&\text{if }t=\text{\textvisiblespace}\\
                                  \text{{inc}}{}\!\left({w_{1},\dots,w_{k}t}\right)&\text{else}\\
                                  \end{cases}$ where w₁, …, w_(k) ← ⟦words(v)⟧_(σ)
  sentences(v)                    $\begin{cases}\text{{fin}}{}\!\left({s_{1},\dots,s_{k}}\right)&\text{if }t=\textsc{eos}\\
                                  \text{{inc}}{}\!\left({s_{1},\dots,s_{k},t}\right)&\text{if }s_{k}\text{{.endswith(".")}}\\
                                  \text{{inc}}{}\!\left({s_{1},\dots,s_{k}t}\right)&\text{else}\\
                                  \end{cases}$ where s₁, …, s_(k) ← ⟦sentences(v)⟧_(σ)
  len(v)                          $\begin{cases}${len}$(v)&\text{if }t=\textsc{eos}\\
                                  ${len}$(v)+1&\text{else}\\
                                  \end{cases}$
  len(l) over list l              len(⟦l⟧_(σ[v ← vt]))
  ------------------------------- ----------------------------------------------------------------------------------------------

  ------------------------------------------- ----------------------------------------------------------------------------------------
  expression                                  Follow[⋅](u, t)
  fn(τ₁, …, τ_(k))                            fn(⟦τ₁⟧_(σ[v ← vt]), …, ⟦τ_(k)⟧_(σ[v ← vt]))
  stop_at(var, s)                             $\begin{cases}\text{{fin}}{}(b)&\text{if }b\wedge\text{{Final}}[var]=\text{{inc}}\\
                                              \text{{var}}{}\!\left({l}\right)&\text{else}\\
                                              \end{cases}$ where b = ⟦var⟧_(σ).endswith(s)
  x in s for string s and constant x          $\begin{cases}\top&\text{if {x in s}}\vee\texttt{x in $t$}\\
                                              \bot&\text{else}\\
                                              \end{cases}$
  x in l for constant list/set l              $\begin{cases}\text{{fin}}{}\!\left({\top}\right)&\text{if }\text{{t in l}}\\
                                              \text{{var}}{}\!\left({\bot}\right)&\text{if }\exists e\in l\bullet\\
                                              &\hskip 8.19447pt\text{{e.startswith($vt$)}}\\
                                              \bot&\text{else}\\
                                              \end{cases}$
  x < y                                       ⟦x⟧_(σ[v ← vt]) < ⟦y⟧_(σ[v ← vt])
  string comp. a == v                         $\begin{cases}\text{{fin}}{}\!\left({\top}\right)&\text{if }vt=\text{{a}}\\
                                              \text{{var}}{}\!\left({\bot}\right)&\text{if }\text{{a.startswith($vt$)}}\\
                                              \bot&\text{else}\\
                                              \end{cases}$
  number comp. x == y                         ⟦x⟧_(σ[v ← vt]) = ⟦y⟧_(σ[v ← vt])
  a and b                                     ⟦x⟧_(σ[v ← vt]) and ⟦y⟧_(σ[v ← vt])
  a or b                                      ⟦x⟧_(σ[v ← vt]) or ⟦y⟧_(σ[v ← vt])
  not a                                       not ⟦x⟧_(σ[v ← vt])
  ------------------------------------------- ----------------------------------------------------------------------------------------

5.2. Generating Token Masks using FollowMaps

Provided that we can now evaluate where conditions eagerly on every new token, the task that remains is to construct a token mask, that allows us to soundly identify tokens that are guaranteed to violate the condition when chosen next by the decode function. To this end, we introduce a novel abstraction called FollowMaps.

Follow Maps

A follow map is a function $\textsc{FollowMap}{}(u,t)$ that takes a partial interaction trace u and a token t as input, and approximates the future value of some expression during validation, given ut is validated next. We implement FollowMaps for all supported operators in LMQL, and show a subset of the rules in Table 2. As shown, per operation, only a few rules are required. Note that a FollowMap always also produces a final annotator, but we only show them if the standard rules from Table 1 do not apply.

Based on this, we define a recursive $\text{{\text{{Follow}}}}[\text{$\langle$expr$\rangle$}](u,t)$ operator that automatically constructs the FollowMap for a provided expression, considering the definitions in Table 2 as its base cases. This is implemented by recursively applying case-wise composition to the follow maps of the respective sub-expressions. Using Follow, we obtain an all-encompassing follow map for the entire validation expression. By inspecting the sub-cases of the resulting FollowMap, we then identify tokens that are guaranteed to violate the expression, which allows us to generate a decoding mask.

Example

Assume that we have the constraint TEXT in ["Stephen Hawking"] and that we are currently decoding hole variable TEXT. So far it has been assigned the value "Steph". Using the rules in Table 2, we can construct a FollowMap:

  -- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --
     $${\text{{Follow}}[\text{\lstinline{{\lst@@@set@language\lst@@@set@numbers\lst@@@set@frame\lst@@@set@rulecolor\lst@@@set@language\lst@@@set@language\lst@@@set@numbers\lst@@@set@frame\lst@@@set@language\lst@@@set@language\lst@@@set@numbers\footnotesize{\@listingGroup{ltx_lst_identifier}{{TEXT}}}{\@listingGroup{ltx_lst_space}{ }}{\@listingGroup{ltx_lst_keyword}{{in}}}{\@listingGroup{ltx_lst_space}{ }}[{\@listingGroup{ltx_lst_string}{\color[rgb]{0.1641,0,0.6016}{"Stephen{\@listingGroup{ltx_lst_space}{ }}Hawking"}}}]}}}}](\text{{"Steph"}},t)=\begin{cases}\text{{fin}}{}(\top)&\text{if }t=\text{{"en Hawking"}}\\
     \text{{fin}}{}(\bot)&\text{else}\end{cases}$$
  -- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --

The FollowMap returns fin(⊤) if the following sequences matches "en Hawking" and fin(⊥) otherwise. During decoding, this can be translated into a token mask, as we know that tokens other than prefixes of "en Hawking" will definitively (fin) violate our constraint. To enforce this, we derive a mask vector m that only allows the first token of "en Hawking" to be generated next.

Soundness

While a perfect next-token validator is desirable, this can be hard to achieve, especially with constraints that rely on forward references. For this reason, we do not require Follow to return FollowMaps that mask out all tokens that will violate our constraints (i.e. completeness). Instead, we focus on sound approximation: Given some boolean where condition e and the currently decoded hole variable v (cf. Algorithm 1), we consider the Follow operator to be sound if and only if:

  ----- -- ---------------------------------------------------------------- --
  (1)      ∀t ∈ 𝒱 • (Follow[e])(u, t) = fin(⊥) ⇒ ⟦e⟧_(σ[v ← ut]) = fin(⊥)
  ----- -- ---------------------------------------------------------------- --

In other words, if the returned FollowMap indicates that the next token t is guaranteed to violate the condition e, then the condition e must evaluate to fin(⊥) when t is picked in the next decoding step. While this potentially over-approximates the set of valid tokens, it guarantees that we will never mask out any tokens that may actually be valid. Note also, how we rely on final semantics, i.e. fin(⊥), to express that a token will lead to a definitive violation of our constraints, and not just a temporary one during generation.

Brzozowski derivatives

To provide another perspective on FollowMap soundness, consider Brzozowski derivatives (Brzozowski, 1964): For a language S ∈ Σ^(*), i.e. a set of strings over the alphabet Σ, and prefix u ∈ Σ^(*) the Brzozowski derivative u⁻¹S = {v ∈ Σ^(*) ∣ uv ∈ S} denotes the set of postfixes such that the concatenation uv ∈ S. In our case we are interested in the possible sequences over the token vocabulary 𝒱^(*). In particular, given some query 𝒬, we are interested in the subset L_(𝒬) ⊆ 𝒱*, which we do not necessarily have in closed form, that contains all interaction traces that fulfill the constraints specified in where_(𝒬). If during an execution of 𝒬 we have a partial interaction trace u, then u⁻¹L_(𝒬) denotes all possible legal postfixes completing this interaction trace. Using this, we define the set of Brzozowski-admissible tokens T_(𝒬) = {t ∈ 𝒱 ∣ (ut)⁻¹L_(𝒬)) ≠ ∅}, which can be decoded in the next step such that legal continuations in L_(𝒬) exist , i.e. T_(𝒬) describes the set of legal tokens for the next decoding step, thus forming a decoding mask M.

Based on these definitions, the FollowMap and the Follow operator satisfy the following property with proof in Section B.1:

Theorem 5.1.

(Brzozowski Soundness) Given a query 𝒬, partial interaction trace u, and the corresponding set of allowed tokens M := {t ∈ 𝒱 | Follow[where_(𝒬)](u, t) ≠ fin(⊥)}, it holds that T_(𝒬) ⊆ M, where T_(𝒬) is the set of Brzozowski-admissible tokens.

This result is in line with Eq. 1, and implies that FollowMaps will always allow, i.e. not mask out, any tokens that could still yield a legal decoding.

6. Evaluation

Here, we evaluate the effectiveness of LMQL as a language as well as a tool for prompt engineers. We evaluate LMQL in three different case studies, encompassing a wide range of prompting scenarios.

6.1. Research Questions and Setup

We focus our evaluation on three core questions:

- •
  Expressiveness Can users rely on LMQL for effective language model programming? Can we easily implement common and advanced prompting techniques with simple and concise query logic, especially in the case of interactive prompting?
- •
  Performance Can LMQL be used to effectively lower the required number of model queries and thereby lower the implied computational or API-related cost of using LMs?
- •
  Accuracy Can constraint decoding be used to improve the accuracy of LMs on standard benchmarks by providing hand-crafted validation rules?

Baseline

Although LMQL queries can become quite complex when using constraints and scripted prompts, overall, the language still provides a comparatively accessible interface close to natural language. Therefore, we evaluate LMQL mainly as an alternative to other, existing high-level interfaces for Python, that are typically used to interact with LMs. More specifically, we assume a simple generate() API as e.g. provided by the HuggingFace Transformers (Wolf et al., 2020) package⁴⁴ 4 GenerationMixin.generate() API documentation: https://huggingface.co/docs/transformers/v4.18.0/en/main_classes/text_generation#transformers.generation_utils.GenerationMixin.generate. generate() can be called with some string, which is then used to invoke a language model to generate a likely continuation sequence. The method supports a range of parameters, including maximum length, decoding methods and stop tokens. Most importantly however, we assume that generate() does not support token level validation, but instead requires users to generate sequences chunk-wise, and then parse and validate the output manually. This is also comparable to how popular, state-of-the-art interfaces for LMs on the web, e.g. OpenAI’s GPT-3 API⁵⁵ 5 GPT-3 API, https://openai.com/api/ work.

Datasets and Model

In our case studies, we address tasks relating to general and date understanding (Srivastava et al., 2022), question answering (Yang et al., 2018) and arithmetic math (Cobbe et al., 2021). As language model, we rely on the publicly available open source model GPT-J 6B (Wang and Komatsuzaki, 2021) (6 billion parameters). The model’s performance is comparable to the widely used GPT-3 model with 6.7 billion parameters across many important benchmarks. Further, where GPT-J exceeds the abilities of our hardware, we rely on gpt2-xl⁶⁶ 6 https://huggingface.co/gpt2-xl, a 1.5B parameter version of GPT-2 (Radford et al., 2019). Even though recent variants of GPT-3 have demonstrated better performance, we chose GPT-J 6B as it is publicly available. This is crucial, because the LMQL runtime requires integration with the decoding loop of a language model, which cannot be implemented with limited high-level APIs. Please see App. A, for more details on the integration of LMQL in the decoder logic of a language model.

Metrics

To quantify performance, cost and usability characteristics of LMQL, we consider a number of metrics:

- •
  LOC As a simple measure of conciseness and simplicity we provide the number of lines of code (LOC) for each implemented case study. We only count functional LOC, i.e. excluding comments, empty lines, and fixed prompt parts (e.g. few-shot samples).
- •
  Number of Model Queries We count the number of times the model f is invoked for next-token prediction. This metric directly measures the computational cost of using a self-hosted LM, however, abstracts the computational cost of running the model itself.
- •
  Number of generate() Calls We also count the number of times the generate() method is called, i.e. a new decoding process is started. This metric relates to API costs of using an LM, as each call to generate() may incur a cost, e.g. in terms of API requests or latency.
- •
  Billable Tokens Lastly, to model closely how API-gated models are billed, we count the number of tokens per generate() call that is processed by the model as part of the prompt, plus the number of tokens that are generated. This metric is based on the billing mechanics of API-gated models like GPT-3. Based on Billable Tokens, we will make cost estimates, given the current token pricing of $0.02/1K tokens of the GPT-3 davinci model⁷⁷ 7 https://openai.com/api/pricing/. This highlights the potential savings if LMQL could be used in place of standard high-level APIs.

We motivate this choice of performance metrics over pure runtime by the reality of using LMs in practice. Any reduction in the number of processed tokens will directly translate to a saving in cost, both with API-based models and when running a language model locally.

Experimental Setup

As a runtime for the language models we use HuggingFace Transformers’ (Wolf et al., 2020) transformers library with pytorch on the backend. All experiments are run on an Nvidia A100 GPU with 40GB VRAM. For more details on the implementation of LMQL, please see App. A.

⬇

argmax

"Pick the odd word out: skirt, dress, pen, jacket.\n"

"skirt is clothing, dress is clothing, pen is an object, jacket is clothing.\n"

"So the odd one is pen.\n\n"

"Pick the odd word out: Spain, France, German, England, Singapore.\n"

"Spain is a country, France is a country, German is a language, …\n"

"So the odd one is German.\n\n"

"Pick the odd word out: {OPTIONS}\n"

"[REASONING]"

"[RESULT]"

from "EleutherAI/gpt-j-6B"

where

not "\n" in REASONING and not "Pick" in REASONING and

stops_at(REASONING, "Pick the odd word") and stops_at(REASONING, "\n") and

stops_at(REASONING, "So the odd one") and stops_at(REASONING, ".") and len(WORDS(REASONING)) < 40

distribute

RESULT over OPTIONS.split(", ")

6.2. Case Study 1: Chain-of-Thought Prompting

We first consider multiple-choice question answering tasks: A language model is presented with a question Q and a set of options 𝒪 = {O₁, …, O_(n)}. While direct prompting of a model to obtain the result as argmax_(𝒪) P(O_(i)|Q) is possible, it is often not enough to reach good levels of performance. Further, the model’s reasoning may not be clear and the resulting answers can appear quite arbitrary. Chain-of-thought prompting (Wei et al., 2022) aims to address this, by preceding the actual question with few-shot samples that demonstrate how to arrive at a correct answer through a multi-step reasoning process. By priming the model in this way, it is more likely to produce a similar chain of thoughts, eventually leading up to the correct answer for a new question. For this case study we implement queries for two task: The general knowledge reasoning task Odd One Out and the Date Understanding task, both included in the recently published BIG benchmark collection (Srivastava et al., 2022).

  -------------------- ------------------- -------------------- --------- --------------
                       Standard Decoding   LMQL (constrained)   Δ         Cost Savings
  Odd One Out
  Accuracy             33.00%              33.00%               0.00%
  generate() calls     6.95                5.95                 -14.38%
  Model Queries        52.98               40.85                -22.89%
  Billable Tokens      993.41              849.65               -14.47%   0.29¢/query
  LOC                  34                  9                    -73.53%
  Date Understanding
  Accuracy             17.00%              23.00%               6.00%
  generate() calls     7.84                6.84                 -12.75%
  Model Queries        63.37               57.27                -9.63%
  Billable Tokens      3291.87             2843.80              -13.61%   0.9¢/query
  LOC                  38                  13                   -65.79%
  -------------------- ------------------- -------------------- --------- --------------

Query and Results

We implement chain-of-thought reasoning in LMQL as shown in Fig. 10. The prompt clause contains two few-shot examples with reasoning steps. We provide the comma-separated list of words of the Odd One Out task as query argument OPTIONS when iterating over the dataset. The first hole variable generated by the model is REASONING. We constrain the REASONING variable in multiple ways, including a maximum number of words and several stopping conditions. Further, we disallow the use of "Pick" and the newline character, to prevent the model from digressing or skipping the reasoning steps alltogether. For decoding, we rely on argmax which provides us with the greedily-determined most likely answer. Lastly, we use the distribute clause, to compute a probability distribution over the set of possible answers in 𝒪, i.e. P(⋅|"⟨p⟩⟨q⟩⟨r⟩"), which is conditioned on the concatenation of the few-shot samples ⟨p⟩, the question ⟨q⟩ and the generated reasoning steps ⟨r⟩. Analogously to our LMQL query, we implement the same prompting behavior with a generate()-based python program. As discussed, the baseline program employs similar stopping conditions for REASONING but does not encode token level constraints. We evaluate both programs on Odd One Out and Date Understanding and document the results in Table 3. We observe the same or improved accuracy for constrained LMQL decoding when compared to Standard Decoding. Depending on the dataset, LMQL can reduce model queries and the total consumed tokens by up to 24%. This is a significant reduction in cost/compute, especially when considering that the LMQL-based constrained decoding can achieve the same or better accuracy. Lastly, we find that LMQL reduces program size down to 26% (34% resp.) of the LOC required in our python baseline implementations, to address the two tasks.

6.3. Case Study 2: Interactive Prompting

Chain-of-thought prompting is an effective method to improve model understanding (Wei et al., 2022). It can be used to extract knowledge from a model or generate new insights by multi-step reasoning. However, in some cases a model may not know about the required context information and external sources have to be consulted. For instance, for question answering the prompting scheme ReAct (Yao et al., 2022) proposes to augment chain-of-thought-based prompting with the ability for the model to interactively query external sources such as Wikipedia. As LMQL supports loops, branches, and function calls in its prompt clause, it lends itself well to implementing these kinds of interactive prompting scenarios. By relying on control flow in the prompting clause of a query, we can interpret model results step-by-step and inject information from external sources as requested.

Query

To invoke external actions like Wikipedia lookups, ReAct relies on designated action phrases such as Search and Finish, that the LM can produce as needed. To implement this interactive behavior in LMQL, we rely on a basic interpretation loop as shown in Fig. 11. The loop iterates over the model’s output and interprets actions when applicable. Wikipedia lookups are implemented as calls to an external python utility. During branching and beam search with multiple hypotheses, the loop and corresponding lookup operations will automatically be issued as required during decoding. The loop terminates when the model generates a Finish action, storing the overall results of the query in the SUBJECT variable. To further guide the generation process, we constrain MODE to be in  {Tho, Act}. Further, we implement simple stopping conditions for THOUGHT and SUBJECT to prevent the model from violating the ReAct reasoning pattern.

⬇

import wikipedia_utils

sample(no_repeat_ngram_size=3)

"What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?"

"Tho 1: I need to search Colorado orogeny, find the area that the eastern sector of the Colorado …\n"

"Act 2: Search 'Colorado orogeny'\n"

"Obs 2: The Colorado orogeny was an episode of mountain building (an orogeny) …\n"

"Tho 3: It does not mention the eastern sector. So I need to look up eastern sector.\n"

…

"Tho 4: High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft."

"Act 5: Finish '1,800 to 7,000 ft'"

"Where is Apple Computers headquartered?\n"

for i in range(1024):

"[MODE] {i}:"

if MODE == "Tho":

"[THOUGHT] "

elif MODE == "Act":

" [ACTION] '[SUBJECT]\n"

if ACTION == "Search":

result = wikipedia_utils.search(SUBJECT[:-1]) # cutting of the consumed '

"Obs {i}: {result}\n"

else:

break # action must be FINISH

from "gpt2-xl"

where

MODE in ["Tho", "Act"] and stops_at(THOUGHT, "\n") and

ACTION in ["Search", "Finish"] and len(words(THOUGHT)) > 2 and

stops_at(SUBJECT, "'") and not "Tho" in THOUGHT"

Python Baseline

As a baseline for scripted interpretation, we implement a python program that supports the same ReAct prompting as the query in Fig. 11. To implement LMQL’s declarative parsing of THOUGHT, SUBJECT, and ACTION, we rely on built-in python functionality to parse and process the chunk-wise produced output. For this, we note that we have to resort to hand-crafted parsing logic, whereas in LMQL we can simply rely on declarative predicates like STOPS_AT and validation conditions in the where clause of the query. We include the full source of our baseline prompting implementation in the appendix in Section C.1. We also note that the baseline implementation can only support sample and argmax decoding. Deeper integration, e.g. with beam search, is not easily realizably in python, as the prompting program must be capable of branching into multiple execution heads in accordance with the branching of decoding. In contrast, LMQL supports this out-of-the-box. Lastly, in our baseline implementation, we have to invoke the model multiple times, each time generating a new chunk of output, parsing, and evaluating potential action phrases. For this, we have to choose the chunk size appropriately. We overview the implications of different choices for this parameter in Fig. 12. For our comparison with LMQL, we choose standard decoding with chunk size of 30, which minimizes the number of billable tokens, while not issuing exceedingly many model queries.

Results

To assess LMQL performance benefits with interactive prompting workloads, we apply our ReAct implementations to a question answering task from the HotpotQA (Yang et al., 2018) dataset (see Section C.1 for further details). We observe a significant reduction of generate() calls of up to 80% when using LMQL over standard decoding. This can be attributed to LMQL’s ability to decode the whole sequence in one run, validating on-the-fly. Standard Decoding on the other hand has to decode the whole sequence in chunks, invoking generate() at least as many times as interactions are required. Regarding the total number of model queries, we observe a reduction of at least 30%. For Billable Tokens, we observe an even stronger effect, where LMQL saves up to 76% of the tokens, leading to a significant saving in costs, i.e. 76% fewer tokens or 5.2¢ per query for GPT-3 davinci. Considering program size last, we implement ReAct in just 22 LOC of LMQL, which is 63% fewer lines than in our python-based implementation.

6.4. Case Study 3: Arithmetic Reasoning

Lastly, we consider the task of arithmetic reasoning. Existing work shows that LMs can struggle with evaluating arithmetic expressions correctly (Wei et al., 2022). While reasoning steps might be correct, mistakes in the concrete arithmetic calculations will lead to an incorrect result (Wei et al., 2022; Cobbe et al., 2021). This is exacerbated by the open-ended nature of math problems, where the result is not picked from a limited set of options, but can be any valid number. Recent works (Wei et al., 2022; Cobbe et al., 2021; Andor et al., 2019) therefore propose to augment LM generation with the ability to externally evaluate arithmetic expressions on-the-fly.

  -------------------------------------- ------------------- -------------------- --------- --------------
                                         Standard Decoding   LMQL (constrained)   Δ         Cost Savings
  ReAct (Case Study 2)
  generate() calls                       5                   1                    -80%
  Model Queries                          150                 95                   -36.67%
  Billable Tokens                        3,404               807                  -76.29%   5.2¢/query
  LOC                                    59                  22                   -62.71%
  Arithmetic Evaluation (Case Study 3)
  generate() calls                       7                   1                    -85.71%
  Model Queries                          210                 73                   -65.24%
  Billable Tokens                        3,649               541                  -85.17%   6.2¢/query
  LOC                                    78                  18                   -76.92%
  -------------------------------------- ------------------- -------------------- --------- --------------

⬇

argmax(distribution_batch_size=1, max_length=2048)

"⟨few-shot examples⟩"

"Q: {QUESTION}\n"

"A: Let's think step by step.\n"

for i in range(1024):

"[REASON_OR_CALC]"

if REASON_OR_CALC.endswith("<<"):

" [EXPR] "

result = calculator.run(EXPR)

" {result} >> "

elif REASON_OR_CALC.endswith("So the answer"):

break

" is [RESULT]"

from "EleutherAI/gpt-j-6B"

where

int(RESULT) and

stops_at(REASON_OR_CALC, "<<") and

stops_at(EXPR, "=") and

stops_at(REASON_OR_CALC, "So the answer")

⬇ Q: Noah is a painter. He paints pictures and sells them at the park. He charges $60 for a large painting and $30 for a small painting. Last month he sold eight large paintings and four small paintings. If he sold twice as much this month, how much is his sales for this month? A: Let's think step by step. He sold 8 large paintings and 4 small paintings last month. He sold twice as many this month. 8 large paintings x $60 = <<8*60=480 >> 480 4 small paintings x $30 = <<4*30=120 >> 120 So the answer is 480'

Query

In Fig. 13(a) we demonstrate how to implement such an arithmetic evaluator in LMQL, relying on scripted prompting and constraints. The query decodes reasoning and calculations steps from the model, scanning for occurrences of "<<". Once it encounters such a sequence, it queries the model for the to-be-evaluated expression (e.g. 1+2=?), evaluates it using an external utility function, and passes back the result. This generation process is repeated, until the model produces the stopping phrase "So the answer is". Once the loop exits, the query parses the result, constraining the remaining tokens to form a valid integer, using the built-in function INT. For few-shot samples, we rely on the ones chosen in (Wei et al., 2022).

Results

We applied our query, as well as a baseline program, to an arithmetic reasoning problem from the GSM8K dataset (Cobbe et al., 2021). As shown by the interaction trace in Fig. 13(b), our LMQL query detects and processes arithmetic expressions, as they occur in the model’s output, leading up to the final answer. The necessary query logic is comparatively basic, only requiring some text processing and a simple interpretation loop. Finally, by asserting an INT constraint on RESULT, we can enforce the final model’s output to always be a valid integer. While the concrete model in use (GPT-J 6B) is not able to solve the problem correctly, the example still demonstrates that LMQL can be used to implement on-the-fly arithmetic evaluation, aiding the model in solving the task. Collecting query statistics, we compare the two implementations in Table 4. For the baseline implementation (standard decoding), the number of generate() calls is determined by the number of arithmetic expressions in the model’s output. For LMQL, this has no impact, as arithmetic expressions can be evaluated on-the-fly. Overall this means that LMQL only requires one generate call, where the standard approach requires 7. Further, we observe a significant reduction of 65% in model queries and 85% in billable tokens (saving 6.2¢ per query with GPT-3 davinci). Lastly, we implement arithmetic evaluation in just 18 LOC of LMQL, compared to 78 LOC required for our python-based implementation.

6.5. Discussion

Summarizing, our three case studies show that: i) LMQL allows great expressiveness, i.e. several approaches from current state-of-the-art methods can be directly encoded in a straightforward scripting style, requiring much fewer lines of code than corresponding python-based implementations; ii) LMQL drastically reduces the number of model queries and thereby both efficiency and run time. This is enabled by LMQLs support for token level validation, which enables us to enforce constraints on-the-fly rather than with chunk-wise decoding and backtracking. And, iii) that LMQL does not impact the accuracy achieved by the model. In fact, in some cases, the enforced constraints even yield improvements in accuracy. In addition to all this, we have shown that when used in the context of paid, API-gated models, LMQL would enable significant monetary savings, given the reduction in billable tokens that we observe.

7. Related Work

Language Model Programming (LMP)

Recent work has proposed a variety of different prompting techniques: chain-of-thought prompting (Wei et al., 2022), interactive question answering (Yao et al., 2022), aggregation-based schemes like self-consistency (Wang et al., 2022) and ThinkSum (Ozturkler et al., 2022). We consider all these works as instances of LMP (also discussed under the term of prompt programming (Reynolds and McDonell, 2021; Zhou et al., 2022)), where the goal is to leverage the reasoning abilities of a pre-trained model to achieve a specific task. A few select works have identified this trend, and propose novel LM-focused programming systems: PromptChainer (Wu et al., 2022), OpenPrompt (Ding et al., 2021), and PromptSource (Bach et al., 2022) provide integrated development environments for LM interaction. The latter two even support a simple templating language akin to LMQL top-level string semantics. However, neither of the projects implements constraints or control flow like LMQL does. Finally, Dohan et al. (2022) discuss the idea of language model cascades, relating LM querying to probabilistic programming, which opens up interesting avenues for future work, also in the more general context of language model programming and LMQL.

Recently, an interesting version of chain-of-thought (Gao et al., 2022; Chen et al., 2022) with access to to a language interpreter was proposed. There, the LM produces step-by-step instructions that can be evaluated by a python (or similar) interpreter in order to obtain the answer to simple reasoning or arithmetic tasks. This does not require specially trained LMs, but rather works via few-shot prompting with examples. This approach is orthogonal to the idea of Language Model Programming. However, it can be encoded similar to the arithmetic task (see Section 6.4) in LMQL. If safety is no concern, this is trivially realized by invoking python’s eval function on the model’s response.

Constraining Language Models

The idea of constraining LMs has been applied across a range of fields. Shin et al. (2021) constrain a model’s output to a more easily-interpretable subset of the English language. More specifically, they handcraft custom next-token prediction programs to implement specific semantic parsing tasks using LMs. Poesia et al. (2022) and Scholak et al. (2021) on the other hand, are concerned with the task of generating source code. In this setting, syntactic and semantic validity is crucial. To realize this, they integrate existing parsers and validation methods. LMQL on the other hand provides a generic interface to facilitate constrained decoding by providing high-level constructs. Still, our set of operators can easily be extended by the user, allowing for the integration of grammar-based parsers, semantic code validation or other methods.

8. Conclusion

In this work, we introduce the concept of Language Model Programming, a novel way to interact with (large) language models. We presented LMQL, a high-level query language, offering a concise and intuitive syntax. LMQL implements purpose-designed evaluation semantics, which enable efficient query execution. We have substantiated this claim in a series of case studies, where we demonstrate that complex, state-of-the-art prompting techniques can be implemented as intuitive, concise and efficient LMQL programs that reduce (compute) costs by up to 80%.

Acknowledgements

We thank Mark Müller for his thoughtful comments and proofreading.

References

- Andor et al. (2019) Daniel Andor, Luheng He, Kenton Lee, and Emily Pitler. 2019. Giving BERT a calculator: Finding operations and arguments with reading comprehension. arXiv preprint arXiv:1909.00109 (2019).
- Bach et al. (2022) Stephen H Bach, Victor Sanh, Zheng-Xin Yong, Albert Webson, Colin Raffel, Nihal V Nayak, Abheesht Sharma, Taewoon Kim, M Saiful Bari, Thibault Fevry, et al. 2022. Promptsource: An integrated development environment and repository for natural language prompts. arXiv preprint arXiv:2202.01279 (2022).
- Brown et al. (2020) Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. 2020. Language Models are Few-Shot Learners. In Advances in Neural Information Processing Systems 33: Annual Conference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual, Hugo Larochelle, Marc’Aurelio Ranzato, Raia Hadsell, Maria-Florina Balcan, and Hsuan-Tien Lin (Eds.). https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html
- Brzozowski (1964) Janusz A Brzozowski. 1964. Derivatives of regular expressions. Journal of the ACM (JACM) 11, 4 (1964), 481–494.
- Chen et al. (2022) Wenhu Chen, Xueguang Ma, Xinyi Wang, and William W. Cohen. 2022. Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks. (2022).
- Cobbe et al. (2021) Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, and John Schulman. 2021. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168 (2021).
- Devlin et al. (2019) Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, NAACL-HLT 2019, Minneapolis, MN, USA, June 2-7, 2019, Volume 1 (Long and Short Papers), Jill Burstein, Christy Doran, and Thamar Solorio (Eds.). Association for Computational Linguistics, 4171–4186. https://doi.org/10.18653/v1/n19-1423
- Ding et al. (2021) Ning Ding, Shengding Hu, Weilin Zhao, Yulin Chen, Zhiyuan Liu, Hai-Tao Zheng, and Maosong Sun. 2021. Openprompt: An open-source framework for prompt-learning. arXiv preprint arXiv:2111.01998 (2021).
- Dohan et al. (2022) David Dohan, Winnie Xu, Aitor Lewkowycz, Jacob Austin, David Bieber, Raphael Gontijo Lopes, Yuhuai Wu, Henryk Michalewski, Rif A Saurous, Jascha Sohl-Dickstein, et al. 2022. Language model cascades. arXiv preprint arXiv:2207.10342 (2022).
- Gao et al. (2020) Leo Gao, Stella Biderman, Sid Black, Laurence Golding, Travis Hoppe, Charles Foster, Jason Phang, Horace He, Anish Thite, Noa Nabeshima, Shawn Presser, and Connor Leahy. 2020. The Pile: An 800GB Dataset of Diverse Text for Language Modeling. arXiv preprint arXiv:2101.00027 (2020).
- Gao et al. (2022) Luyu Gao, Aman Madaan, Shuyan Zhou, Uri Alon, Pengfei Liu, Yiming Yang, Jamie Callan, and Graham Neubig. 2022. PAL: Program-aided Language Models. (2022).
- OpenAI (2022) OpenAI. 2022. ChatGPT: Optimizing Language Models for Dialogue — openai.com. https://openai.com/blog/chatgpt/. [Accessed 10-Dec-2022].
- Ozturkler et al. (2022) Batu Ozturkler, Nikolay Malkin, Zhen Wang, and Nebojsa Jojic. 2022. ThinkSum: Probabilistic reasoning over sets using large language models. arXiv preprint arXiv:2210.01293 (2022).
- Poesia et al. (2022) Gabriel Poesia, Alex Polozov, Vu Le, Ashish Tiwari, Gustavo Soares, Christopher Meek, and Sumit Gulwani. 2022. Synchromesh: Reliable Code Generation from Pre-trained Language Models. In Proc. of ICLR.
- Radford et al. (2019) Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. 2019. Language models are unsupervised multitask learners. OpenAI blog 1, 8 (2019), 9.
- Reynolds and McDonell (2021) Laria Reynolds and Kyle McDonell. 2021. Prompt Programming for Large Language Models: Beyond the Few-Shot Paradigm. In CHI ’21: CHI Conference on Human Factors in Computing Systems, Virtual Event / Yokohama Japan, May 8-13, 2021, Extended Abstracts, Yoshifumi Kitamura, Aaron Quigley, Katherine Isbister, and Takeo Igarashi (Eds.). ACM, 314:1–314:7. https://doi.org/10.1145/3411763.3451760
- Scholak et al. (2021) Torsten Scholak, Nathan Schucher, and Dzmitry Bahdanau. 2021. PICARD: Parsing incrementally for constrained auto-regressive decoding from language models. arXiv preprint arXiv:2109.05093 (2021).
- Shin et al. (2021) Richard Shin, Christopher H Lin, Sam Thomson, Charles Chen, Subhro Roy, Emmanouil Antonios Platanios, Adam Pauls, Dan Klein, Jason Eisner, and Benjamin Van Durme. 2021. Constrained language models yield few-shot semantic parsers. arXiv preprint arXiv:2104.08768 (2021).
- Srivastava et al. (2022) Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, Abu Awal Md Shoeb, Abubakar Abid, Adam Fisch, Adam R Brown, Adam Santoro, Aditya Gupta, Adrià Garriga-Alonso, et al. 2022. Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models. arXiv preprint arXiv:2206.04615 (2022).
- Vaswani et al. (2017) Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. 2017. Attention is All you Need. In Advances in Neural Information Processing Systems 30: Annual Conference on Neural Information Processing Systems 2017, December 4-9, 2017, Long Beach, CA, USA, Isabelle Guyon, Ulrike von Luxburg, Samy Bengio, Hanna M. Wallach, Rob Fergus, S. V. N. Vishwanathan, and Roman Garnett (Eds.). 5998–6008. https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html
- Wang and Komatsuzaki (2021) Ben Wang and Aran Komatsuzaki. 2021. GPT-J-6B: A 6 Billion Parameter Autoregressive Language Model. https://github.com/kingoflolz/mesh-transformer-jax.
- Wang et al. (2022) Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, and Denny Zhou. 2022. Self-consistency improves chain of thought reasoning in language models. arXiv preprint arXiv:2203.11171 (2022).
- Wei et al. (2022) Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Ed Chi, Quoc Le, and Denny Zhou. 2022. Chain of thought prompting elicits reasoning in large language models. arXiv preprint arXiv:2201.11903 (2022).
- Wolf et al. (2020) Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Clement Delangue, Anthony Moi, Pierric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz, et al. 2020. Transformers: State-of-the-art natural language processing. In Proceedings of the 2020 conference on empirical methods in natural language processing: system demonstrations. 38–45.
- Wu et al. (2022) Tongshuang Wu, Ellen Jiang, Aaron Donsbach, Jeff Gray, Alejandra Molina, Michael Terry, and Carrie J. Cai. 2022. PromptChainer: Chaining Large Language Model Prompts through Visual Programming. In CHI ’22: CHI Conference on Human Factors in Computing Systems, New Orleans, LA, USA, 29 April 2022 - 5 May 2022, Extended Abstracts. https://doi.org/10.1145/3491101.3519729
- Yang et al. (2018) Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W Cohen, Ruslan Salakhutdinov, and Christopher D Manning. 2018. HotpotQA: A dataset for diverse, explainable multi-hop question answering. arXiv preprint arXiv:1809.09600 (2018).
- Yao et al. (2022) Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2022. ReAct: Synergizing Reasoning and Acting in Language Models. arXiv preprint arXiv:2210.03629 (2022).
- Zhou et al. (2022) Yongchao Zhou, Andrei Ioan Muresanu, Ziwen Han, Keiran Paster, Silviu Pitis, Harris Chan, and Jimmy Ba. 2022. Large Language Models Are Human-Level Prompt Engineers. CoRR abs/2211.01910 (2022). https://doi.org/10.48550/arXiv.2211.01910 arXiv:2211.01910

Appendix A Implementation

In this section, we discuss a number of technical aspects of our LMQL implementation, as published together with this paper.

A.1. Language Runtime

Parser and Python Compatibility

We implement LMQL as a superset of python. This also manifests in our implementation, where we rely on the python tokenizer and parser to process LMQL code. Subexpressions in an LMQL query, such as in the where clause, are parsed as standard python. After some basic program transformations, we emit a python function that interacts with the LMQL runtime, and allows for interrupted execution by leveraging yield and async semantics. This allows us to implement LMQL as a regular python library, which can be used in any python environment.

Eager Evaluation Semantics

To implement our evaluation semantics, we transform the abstract syntax tree as returned by the python parser into a runtime representation of a computational graph, modelling dependencies among operations explicitly. Users can easily extend LMQL with custom operators, by implementing a simple class interface with forward, final and follow functions, similar to the integration of custom operators in the popular pytorch library. Custom operators can easily be registered with the runtime, and the compiler will automatically generate the necessary code to integrate them into the LMQL computational graph.

A.2. Model Integration

Inference API

To enable quick turnaround times during development, LMQL relies on a client-server-architecture. The server is responsible for inference, loading and managing the model. In our current implementation, it is configured to use a specific HuggingFace Transformers model. Users then interact with the LMQL client, which is a simple python library. The client parses the user-provided LMQL code, constructs the computational graph, and also runs the decoding loop. Only the forward pass of the underlying model is outsourced to the server. This naturally aligns with settings in which inference is run on some remote server with capable hardware, while the user interacts with the model via a fast, local client with quick startup times.

Inference as a Service

The underlying client-server architecture of LMQL also allows for a separation of the LMQL client and inference as a service. In principle, vendors of API-gated LMs may therefore support LMQL by providing just the necessary inference API. Alternatively, vendors could accept to-be-executed LMQL code directly, which would offer customers more control over the decoding process than with current standard APIs. In this context, we consider LMQL a proposal for the standardization of language model interaction across different vendor-specific APIs. Implementing LMQL support would allow users to write prompting code once, and run it on any LM platform, without having to change their code. In such a setting, however, we advise for sandboxing of the executed LMQL queries (like in serverless computing), as LMQL allows for arbitrary code to be executed.

Decoding Loop

LMQL only requires a small change to existing decoder implementations. For a practical demonstration, see our implementation as published with this paper, in which we adapt the existing HuggingFace Transformers decoding loop to be LMQL-compatible. In general, LMQL scripted prompting and output constraining both compile down to token level prediction masks. This is typically already implemented with existing decoders and just needs an additional hook, to call the LMQL runtime after each produced token. Using this simple interface, LMQL can be integrated into any decoder implementation, without requiring any changes or retraining of the underlying model.

A.3. Visual Debugger

[Refer to caption]

Apart from command-line tooling, the LMQL runtime also includes a web-based visual editor tool, helpful in constructing and debugging LMQL programs. A screenshot of the visual debugger is shown in Fig. 14.

Editor and Compiler

The visual debugger provides an editor window for constructing LMQL queries. After a query is executed, users can view the compiler output, i.e. the resulting python code, including the code that constructs the computational graph and executes the prompt.

Decoder State

Users can track the different decoding branches of the currently active decoding method in real-time. This includes simple parallel decoding when sampling more than one sequence, but also multi-branch decoding like beam search. The debugger visualizes (sub-)tokens, and at each decoder step, users can inspect the current interaction trace, the value of prompt variables as well as the current state of where clause validation.

Validation and Masking

Lastly, the computational graph of the where clause can be visualized and users can track the current value of the expression. In addition to the regular value semantics and partial evaluation, this includes support for both Final and Follow semantics. Different shades of green and red indicate final and non-final True and False values, respectively. The FollowMap at each operation can also be inspected, allowing for a detailed analysis of the current state of the computational graph. This can be helpful when developing new LMQL operators, as it allows for a quick and easy debugging of the underlying semantics.

Appendix B Proofs

B.1. Proof of Theorem 5.1

Proof.

(Brzozowski Soundness) Given query 𝒬, partial interaction trace u, a scope σ and the set of allowed tokens M := {t ∈ 𝒱 | Follow[where_(𝒬)](u, t) ≠ fin(⊥)}.

1.  (1)
    By definition, we get the following:

    1.  (a)
        T_(𝒬) ⊆ 𝒱, since we operate with limited vocabulary 𝒱.
    2.  (b)
        Next, inverting the masking condition, we get M = 𝒱 \ M⁻¹ with the set of disallowed tokens M⁻¹ = {t ∈ 𝒱 | Follow[where_(𝒬)](u, t) = fin(⊥)}
    3.  (c)
        Now, if we establish T_(𝒬) ∩ M⁻¹ = ∅ (*), we can derive Brzozowski soundness as follows:

        $T_{\mathcal{Q}}\stackrel{{\scriptstyle(*)}}{{=}}T_{\mathcal{Q}}\setminus M^{-1}\stackrel{{\scriptstyle(a)}}{{\subseteq}}\mathcal{V}\setminus M^{-1}\stackrel{{\scriptstyle(b)}}{{=}}M$  i.e.  T_(𝒬) ⊆ M
    4.  (d)
        For T_(𝒬) ⊆ M, it thus suffices to show (*), i.e. that no disallowed token in M⁻¹ is in T_(𝒬): ∀t ∈ 𝒱 • t ∈ M⁻¹ ⟹ t ∉ T_(𝒬).
2.  (2)
    Now we prove (*). For any disallowed t we know that Follow[where_(𝒬)](u, t) = fin(⊥):

    - •
      Thus, for the current hole variable v, it holds that: ⟦where_(𝒬)⟧_(σ[v ← ut]) = fin(⊥).
    - •
      By final semantics, this means that there is no p ∈ 𝒱^(*) such that ⟦where_(𝒬)⟧_(σ[v ← utp]) ≠ ⊥.
    - •
      However, by definition we know that L_(𝒬) := {s ∈ Σ^(*) | ⟦where_(𝒬)⟧_(σ[parse(s)]) = ⊤}, where σ[parse(s)] refers to the variable store, with variables set according to 𝒬 and interaction trace s.
    - •
      Therefore, we know that utp ∉ L_(𝒬), which means that tp ∉ u⁻¹L_(𝒬), i.e. t ∉ T_(𝒬).
3.  (3)
    Overall, we therefore have shown that (*) holds, which implies via (1) that T_(𝒬) ⊆ M. ∎

Appendix C More Evaluation Results

C.1. Interative Prompting (ReAct)

This section includes additional details on our case study with the interactive scheme ReAct in Section 6.3.

Interaction Traces

We compare the interaction traces of our LMQL query in Fig. 15 with the output of the equivalent python implementation in Fig. 16. For our python implementation we additionally mark each generate() call during output generation. For the LMQL trace, this is not necessary as LMQL decodes the whole trace in one go, using its token level interaction model.

Python Baseline

In we include the full source of our python baseline implementation for the ReAct prompting scheme.

LMQL (constrained)

⬇

ended with the conclusion of what?\\}

Tho 1: I need to search Chang Ucchin and The Korean War.Act 2: Search ’Chang Ucchin’ Obs 2: Chang Ucchin (26 November 1917 - 27 December 1990) was one of the most representative modern Korean

Tho 3: I need to search Chang Ucchin (26 November 1917 - 27 December 1990) and The Korean War.

Act 4: Search 'Chang Ucchin'

Obs 2: Chang Ucchin (26 November 1917 - 27 December 1990) was one of the most representative modern Korean

Act 5: Finish 'The Korean War'

Python (HuggingFace API)

⬇

======generate()======

Tho 1: I need to search Chang Ucchin and Korea.

======generate()======

Act 2: Search 'Chang Ucchin'

Obs 2: Chang Ucchin (26 November 1917 - 27 December 1990) was one of the most representative modern Korean Tho 3: I need to search Chang Ucchin (26 November 1917 - 27 December ======generate()====== Act 4: Search ’Chang Ucchin’ Obs 2: Chang Ucchin (26 November 1917 - 27 December 1990) was one of the most representative modern Korean

======generate()======

Act 5: Finish 'Chang Ucchin'

⬇

prompt = f"""<few-shot samples> {question}""".strip() + "\n"

for i in range(1024):

new_prompt = await hf.generate(prompt, max_new_tokens=40, stopping_phrases=["Act"],

step_size=10, remove_stopping_phrases=False)

new_text = new_prompt[len(prompt):]

# find first Act

indices = [i for i in [new_text.find("Act")] if i != -1]

first_kw = min(indices + [len(prompt) + 1])

if first_kw == len(prompt) + 1:

prompt = new_prompt

continue

new_text = new_text[first_kw:]

# find end of line

end_of_line = new_text.find("\n")

if end_of_line != -1: new_text = new_text[:end_of_line]

if new_text.startswith("Act"):

s = new_text.strip()

try:

query = s.split(": ", 1)[1]

command, subject = query.split(" '", 1)

index = s.split(": ", 1)[0].split(" ", 1)[1]

if "Search" in command:

if subject.endswith("'"):

subject = subject[:-1]

result = wikipedia_utils.search(subject)

new_text += "\nObs {}: {}".format(index, result)

elif "Finish" in command:

print("FINISHED with", subject)

except:

print("Failed to parse action", s)

print("======generate()======\n", new_text)

prompt += "\n" + new_text

Experimental support, please view the build logs for errors. Generated by L A T E xml [[LOGO]] .

Instructions for reporting errors

We are continuing to improve HTML versions of papers, and your feedback helps enhance accessibility and mobile support. To report errors in the HTML that will help us improve conversion and rendering, choose any of the methods listed below:

- Click the "Report Issue" ([]) button, located in the page header.

Tip: You can select the relevant text first, to include it in your report.

Our team has already identified the following issues. We appreciate your time reviewing and reporting rendering errors we may not have found yet. Your efforts will help us improve the HTML versions for all readers, because disability should not be a barrier to accessing research. Thank you for your continued support in championing open access for all.

Have a free development cycle? Help support accessibility at arXiv! Our collaborators at LaTeXML maintain a list of packages that need conversion, and welcome developer contributions.

We gratefully acknowledge support from our major funders, member institutions, , and all contributors.

About · Help · Contact · Subscribe · Copyright · Privacy · Accessibility · Operational Status (opens in new tab)

[]
