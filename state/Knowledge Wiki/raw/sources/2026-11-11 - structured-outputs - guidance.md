<!-- source: https://github.com/guidance-ai/guidance | type: html | hash: 6ced044cbe42207582e02615d743e45f297db83a59eca765a1b9b2fc176db54f | fetched: 2026-11-11 -->

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
-
-
-
-
-
-

## Navigation Menu

Sign in

- Products
- Platform
- GitHub Repository hosting, code review, and collaboration

- Copilot AI coding agent for tasks, projects, and automated work

- Build & Ship
- Actions CI/CD and automation

- Code Quality Quality analysis, fixes, and enforcement

- Codespaces Cloud development environments

- Secure
- Code Security Vulnerability detection and remediation

- Secret Protection Secret scanning and leak prevention

All Features

- Developers
- Learn
- Documentation

- Training

- Certifications

- Build
- Build with Copilot

- Customize Copilot

- Integrations

- Explore
- Trending repos

- GitHub Sponsors

- Developer articles

- Changelog
- Changelog Your source for the latest features, improvements, and fixes across GitHub products, all in one place.

- Businesses
- By Stage
- Enterprises

- Team

- Startups

- Nonprofits

- By Industry
- Healthcare

- Financial services

- Manufacturing

- Government

- See all industries

- Evaluate GitHub
- Why GitHub

- Customer Stories

- Business insights

- Trust Center

- Add-ons
- GitHub Advanced Security Enterprise-grade code security

- Copilot for business Enterprise-grade AI features

- Premium Support Enterprise-grade 24/7 support

- Resources
- Learn & Connect
- Documentation

- Resource center

- Blog

- Events & webinars

- Community Forum

- Customer Stories

- Integrations

- Support
- Customer support

- Training

- GitHub Status

- Company
- About

- Partners

- Changelog

- GitHub Universe
- GitHub Universe The event for developers, by developers — talks, workshops, and what’s next for GitHub.

- Pricing

Search /

Sign in
Sign up Appearance settings

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

- guidance-ai

- guidance

## Repository navigation

-

- Code

- Issues 267 ( 267 )

- Pull requests 91 ( 91 )

- Discussions

- Actions

- Projects

- Security and quality

- Insights

More items

-
guidance
Public

- Notifications You must be signed in to change notification settings

- Fork 1.2k ( 1.2k )

- Star 21.8k ( 21.8k ) You must be signed in to star a repository

## About
A guidance language for controlling large language models.

## Resources
Readme
MIT license

## Contributing
Contributing
Activity
Custom properties

## Stars
21.8k stars

## Watchers
116 watching

## Forks
1.2k forks

Report repository

main

Branches Tags

Go to file

Code Open more actions menu

## Latest commit

## History
1,920 Commits
1,920 Commits

## Folders and files
Name Name Last commit message
Last commit date

.github

.github

client/ graphpaper-inline

client/ graphpaper-inline

docs

docs

guidance

guidance

notebooks

notebooks

packages/ python/ stitch

packages/ python/ stitch

scripts

scripts

tests

tests

.git-blame-ignore-revs

.git-blame-ignore-revs

.gitignore

.gitignore

CONTRIBUTING.md

CONTRIBUTING.md

GOVERNANCE.md

GOVERNANCE.md

LICENSE.md

LICENSE.md

MAINTAINERS.md

MAINTAINERS.md

README.md

README.md

pyproject.toml

pyproject.toml

ruff.toml

ruff.toml

View all files

## Repository files navigation

-

- README

- Contributing

- MIT license

More items

Guidance is an efficient programming paradigm for steering language models. With Guidance, you can control how output is structured and get high-quality output for your use case— while reducing latency and cost vs. conventional prompting or fine-tuning. It allows users to constrain generation (e.g. with regex and CFGs) as well as to interleave control (conditionals, loops, tool use) and generation seamlessly.

- Install

- Features

## Install

Guidance is available through PyPI and supports a variety of backends (Transformers, llama.cpp, OpenAI, etc.).
If you already have the backend required for your model, you can simply run

pip install guidance

## Features

## A Pythonic interface for language models

When using Guidance, you can work with large language models using common Python idioms:

from guidance import system , user , assistant , gen
from guidance . models import Transformers

# Could also do LlamaCpp or many other models
phi_lm = Transformers ( "microsoft/Phi-4-mini-instruct" )

# Model objects are immutable, so this is a copy
lm = phi_lm

with system ():
lm += "You are a helpful assistant"

with user ():
lm += "Hello. What is your name?"

with assistant ():
lm += gen ( max_tokens = 20 )

print ( lm )

If run at the command line, this will produce output like:

<|system|>You are a helpful assistant<|end|><|user|>Hello. What is your name?<|end|><|assistant|>I am Phi, an AI developed by Microsoft. How can I help you today?

However, if running in a Jupyter notebook, then Guidance provides a widget for a richer user experience:

With Guidance, it's really easy to capture generated text:

# Get a new copy of the Model
lm = phi_lm

with system ():
lm += "You are a helpful assistant"

with user ():
lm += "Hello. What is your name?"

with assistant ():
lm += gen ( name = "lm_response" , max_tokens = 20 )

print ( f" { lm [ 'lm_response' ] = } " )

lm['lm_response']='I am Phi, an AI developed by Microsoft. How can I help you today?'

## Guarantee output syntax with constrained generation

Guidance provides an easy to use, yet immensely powerful syntax for constraining the output of a language model.
For example, a gen() call can be constrained to match a regular expression:

lm = phi_lm

with system ():
lm += "You are a teenager"

with user ():
lm += "How old are you?"

with assistant ():
lm += gen ( "lm_age" , regex = r"\d+" , temperature = 0.8 )

print ( f"The language model is { lm [ 'lm_age' ] } years old" )

The language model is 13 years old

Often, we know that the output has to be an item from a list we know in advance.
Guidance provides a select() function for this scenario:

from guidance import select

lm = phi_lm

with system ():
lm += "You are a geography expert"

with user ():
lm += """What is the capital of Sweden? Answer with the correct letter.

A) Helsinki
B) Reykjavík
C) Stockholm
D) Oslo
"""

with assistant ():
lm += select ([ "A" , "B" , "C" , "D" ], name = "model_selection" )

print ( f"The model selected { lm [ 'model_selection' ] } " )

The model selected C

The constraint system offered by Guidance is extremely powerful.
It can ensure that the output conforms to any context free grammar (so long as the backend LLM has full support for Guidance).
More on this below.

## Debug grammars offline (no model API calls)

When iterating on constraints, you can validate candidate strings locally and test a full run with the Mock model.

from guidance import gen
from guidance . models import Mock

grammar = "expr=" + gen ( regex = r"\d+([+*]\d+)*" , name = "expr" )

# 1) Validate strings directly against the grammar
assert grammar . match ( "expr=12+7*3" ) is not None
assert grammar . match ( "expr=12+*3" ) is None

# 2) Run the same grammar with a local mock model
lm = Mock ( b"<s>expr=12+7*3" )
lm += grammar
print ( lm [ "expr" ]) # 12+7*3

## Create your own Guidance functions

With Guidance, you can create your own Guidance functions which can interact with language models.
These are marked using the @guidance decorator.
Suppose we wanted to answer lots of multiple choice questions.
We could do something like the following:

import guidance

from guidance . models import Model

ASCII_OFFSET = ord ( "a" )

@ guidance
def zero_shot_multiple_choice (
language_model : Model ,
question : str ,
choices : list [ str ],
):
with user ():
language_model += question + " \n "
for i , choice in enumerate ( choices ):
language_model += f" { chr ( i + ASCII_OFFSET ) } : { choice } \n "

with assistant ():
language_model += select (
[ chr ( i + ASCII_OFFSET ) for i in range ( len ( choices ))], name = "string_choice"
)

return language_model

Now, define some questions:

questions = [
{
"question" : "Which state has the northernmost capital?" ,
"choices" : [
"New South Wales" ,
"Northern Territory" ,
"Queensland" ,
"South Australia" ,
"Tasmania" ,
"Victoria" ,
"Western Australia" ,
],
"answer" : 1 ,
},
{
"question" : "Which of the following is venomous?" ,
"choices" : [
"Kangaroo" ,
"Koala Bear" ,
"Platypus" ,
],
"answer" : 2 ,
}
]

We can use our decorated function like gen() or select() .
The language_model argument will be filled in for us automatically:

lm = phi_lm

with system ():
lm += "You are a student taking a multiple choice test."

for mcq in questions :
lm_temp = lm + zero_shot_multiple_choice ( question = mcq [ "question" ], choices = mcq [ "choices" ])
converted_answer = ord ( lm_temp [ "string_choice" ]) - ASCII_OFFSET
print ( lm_temp )
print ( f"LM Answer: { converted_answer } , Correct Answer: { mcq [ 'answer' ] } " )

<|system|>You are a student taking a multiple choice test.<|end|><|user|>Which state has the northernmost capital?
a : New South Wales
b : Northern Territory
c : Queensland
d : South Australia
e : Tasmania
f : Victoria
g : Western Australia
<|end|><|assistant|>b
LM Answer: 1, Correct Answer: 1
<|system|>You are a student taking a multiple choice test.<|end|><|user|>Which of the following is venomous?
a : Kangaroo
b : Koala Bear
c : Platypus
<|end|><|assistant|>c
LM Answer: 2, Correct Answer: 2

Guidance functions can be composed, in order to construct a full context free grammar.
For example, we can create Guidance functions to build a simple HTML webpage (note that this is not a full implementation of HTML).
We start with a simple function which will generate text which does not contain any HTML tags.
The function is marked as stateless to indicate that we intend to use it for composing a grammar:

@ guidance ( stateless = True )
def _gen_text ( lm : Model ):
return lm + gen ( regex = "[^<>]+" )

We can then use this function to generate text within an arbitrary HTML tag:

@ guidance ( stateless = True )
def _gen_text_in_tag ( lm : Model , tag : str ):
lm += f"< { tag } >"
lm += _gen_text ()
lm += f"</ { tag } >"
return lm

Now, let us create the page header. As part of this, we need to generate a page title:

@ guidance ( stateless = True )
def _gen_header ( lm : Model ):
lm += "<head> \n "
lm += _gen_text_in_tag ( "title" ) + " \n "
lm += "</head> \n "
return lm

The body of the HTML page is going to be filled with headings and paragraphs.
We can define a function to do each:

from guidance . library import one_or_more

@ guidance ( stateless = True )
def _gen_heading ( lm : Model ):
lm += select (
options = [ _gen_text_in_tag ( "h1" ), _gen_text_in_tag ( "h2" ), _gen_text_in_tag ( "h3" )]
)
lm += " \n "
return lm

@ guidance ( stateless = True )
def _gen_para ( lm : Model ):
lm += "<p>"
lm += one_or_more (
select (
options = [
_gen_text (),
_gen_text_in_tag ( "em" ),
_gen_text_in_tag ( "strong" ),
"<br />" ,
],
)
)
lm += "</p> \n "
return lm

Now, the function to define the body of the HTML itself:

@ guidance ( stateless = True )
def _gen_body ( lm : Model ):
lm += "<body> \n "
lm += one_or_more ( select ( options = [ _gen_heading (), one_or_more ( _gen_para ())]))
lm += "</body> \n "
return lm

Next, we come to the function which generates the complete HTML page.
We add the HTML start tag, then generate the header, then body, and then append the ending HTML tag:

@ guidance ( stateless = True )
def _gen_html ( lm : Model ):
lm += "<html> \n "
lm += _gen_header ()
lm += _gen_body ()
lm += "</html> \n "
return lm

Finally, we provide a user-friendly wrapper, which will allow us to:

- Set the temperature of the generation

- Capture the generated page from the Model object

from guidance . library import capture , with_temperature

@ guidance ( stateless = True )
def make_html (
lm ,
name : str | None = None ,
* ,
temperature : float = 0.0 ,
):
return lm + capture (
with_temperature ( _gen_html (), temperature = temperature ),
name = name ,
)

Now, use this to generate a simple webpage:

lm = phi_lm

with system ():
lm += "You are an expert in HTML"

with user ():
lm += "Create a simple and short web page about your life story."

with assistant ():
lm += make_html ( name = "html_text" , temperature = 0.7 )

When running in a Jupyter Notebook so that the widget is active, we get the following output:

Note the varying highlighting of the generation.
This is showing another of Guidance's capabilities: fast-forwarding of tokens.
The constraints imposed by a grammar often mean that some tokens are known in advance.
Guidance doesn't need the model to generate these; instead it can insert them into the generation.
This saves forward passes through the model, and hence reduces GPU usage.
For example, in the above HTML generation, Guidance always knows the last opening tag.
If the last opened tag was <h1> (for example), then as soon as the model generates </ , Guidance can fill in h1> without needing the model to perform a forward pass.

## Generating JSON

A JSON schema is actually a context free grammar, and hence it can be used to constrain an LLM using Guidance.
This is a common enough case that Guidance provides special support for it.
A quick sample, based on a Pydantic model:

import json
from pydantic import BaseModel , Field

from guidance import json as gen_json

class BloodPressure ( BaseModel ):
systolic : int = Field ( gt = 300 , le = 400 )
diastolic : int = Field ( gt = 0 , le = 20 )
location : str = Field ( max_length = 50 )
model_config = dict ( extra = "forbid" )

lm = phi_lm

with system ():
lm += "You are a doctor taking a patient's blood pressure taken from their arm"

with user ():
lm += "Report the blood pressure"

with assistant ():
lm += gen_json ( name = "bp" , schema = BloodPressure )

print ( f" { lm [ 'bp' ] = } " )

# Use Python's JSON library
loaded_json = json . loads ( lm [ "bp" ])
print ( json . dumps ( loaded_json , indent = 4 ))

# Use Pydantic
result = BloodPressure . model_validate_json ( lm [ "bp" ])
print ( result . model_dump_json ( indent = 8 ))

lm['bp']='{"systolic": 301, "diastolic": 15, "location": "arm"}'
{
"systolic": 301,
"diastolic": 15,
"location": "arm"
}
{
"systolic": 301,
"diastolic": 15,
"location": "arm"
}

Note that the generated blood pressure is not one the model will have seen for a human.
When generating JSON, a substantial number of tokens can often be fast-forwarded, due to the structural constraints imposed by the schema.

## About
A guidance language for controlling large language models.

## Resources
Readme
MIT license

## Contributing
Contributing
Activity
Custom properties

## Stars
21.8k stars

## Watchers
116 watching

## Forks
1.2k forks

Report repository

## Releases

## Packages

## Used by

## Contributors

## Languages

## Footer

© 2026 GitHub, Inc.

## Footer navigation

-
Terms

-
Privacy

-
Security

-
Status

-
Community

-
Docs

-
Contact

-

Manage cookies

-

Do not share my personal information

You can’t perform that action at this time.
