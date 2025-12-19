# A better evaluation of n-hop latent reasoning on natural facts

[Prior work](https://arxiv.org/abs/2411.16353) has examined two-hop latent reasoning (e.g., answering "What is the atomic number of the age at which Tesla died?" without chain-of-thought) and found that existing datasets to evaluate this have spurious successes (from memorization and shortcuts) while synthetic facts (introduced to the model with fine-tuning) behave differently from facts learned in pretraining (success at composing these synthetic facts is much lower).
In this quick blog post, I'll introduce a better dataset for testing 2-hop, 3-hop, and 4-hop latent reasoning on natural facts (as in, facts that LLMs already know) and test various things on this dataset.
I try somewhat hard to avoid factors that cause spurious successes (and issues causing spurious failures), though my dataset has somewhat limited diversity.

I find that Opus 4 attains a non-trivial accuracy of 17% at 2-hop latent reasoning on this dataset and its performance increases to 33% if the model is given filler tokens counting from 1 to 1000 or to 31% if the problem is repeated 20 times.
This is a very large effect, almost doubling performance.
This is substantially larger than the effect I found when testing these prompt changes on math problems in my prior post: [Recent LLMs can leverage filler tokens or repeated problems to improve (no-CoT) math performance](FIXURL).
I discuss the effects of filler tokens and repeats (and the prompting setup I use) more in that post.

Opus 4 has low but non-trivial performance of 7% on 3-hop questions with filler tokens counting to 1000 and 5% without filler tokens.
Performance is at chance accuracy (4% for Opus 4) on 4-hop questions.

I find that Opus 4 is better at this task than Opus 4.5 which is better than Sonnet 4 and 4.5.
Haiku 3.5's performance on this task is at chance accuracy.

![](https://raw.githubusercontent.com/rgreenblatt/multi_hop/master/eval_results/accuracy_by_hops.png)

Performance (at two hop latent reasoning) increases smoothly with filler tokens and repeats:

![](https://raw.githubusercontent.com/rgreenblatt/multi_hop/master/eval_results/performance_vs_r_2hop.png)
![](https://raw.githubusercontent.com/rgreenblatt/multi_hop/master/eval_results/performance_vs_f_2hop.png)

We also see small performance increases with filler tokens and repeats for 3 hops and a tiny but possibly real increase for 4 hops.

I find that performance depends substantially on the salience of the facts: when I use a subset of the 2 hop distribution that focuses on relatively salient facts, performance rises to 54% (from the 33% for the normal distribution).

I test a simple and algorithmic version of in-context n-hop accuracy where I give the model a table/mapping for each hop showing all possible settings for that fact (e.g., for "Who won the Nobel prize for physics in year X?", the table would be "1901: Wilhelm Conrad Röntgen, 1904: Lord Rayleigh, ...").
I test putting these tables before or after the problem and also test repeating the problem and the tables:

![](https://raw.githubusercontent.com/rgreenblatt/multi_hop/master/eval_results/mapping_comparison_opus-4-5.png)

The model can do 2 and 3 hops perfectly with repeats and 4 hops with >75% accuracy with repeats.

Note that this is effectively a simple algorithmic task that doesn't depend on knowledge at all as the model can just do exact string matching for each hop.

Code (including code for generating the dataset) can be found at [github.com/rgreenblatt/multi_hop](https://github.com/rgreenblatt/multi_hop).

# Appendix: Dataset description

The dataset is made by starting with a distribution of questions that produce an integer.
Then, we have a bunch of possible ways of templating an n-hop question given an initial integer (e.g., asking the model to get the element with the atomic number corresponding to the answer to this question).
Some of these add an additional hop (e.g., number X -> US state that was the X state to join the union -> state motto for that state) to create a 3-hop question.
Additionally, some of these 2 hop or 3 hop questions produce an integer that can be chained into another question creating 3 hop or 4 hop questions.

I include a moderate number of different possible templates, but generally the questions aren't that diverse.
I tried to ensure that each template results in many possible answers such that picking the most common/likely response yields a baseline accuracy <5% (and this worked, e.g., Haiku 3.5 has a very low performance on 2 hop questions despite presumably being decent at guessing).
I also tried to ensure that questions are sufficiently unrelated that short circuiting is difficult.
Relatedly, I tried to ensure that each step requires at least some retrieval rather than being sufficiently salient/common as to be practically detokenizable to the correct answer (e.g., for "On what day of the month was the 17th US president born?", the text "17th US president" practically can be instantly detokenized to "Andrew Johnson" as this is very common to introduce presidents like this making this question more like a 1 hop question than a 2 hop question).

The templates I use are:

- As initial questions to generate an integer: atomic number of an element, at what age did X die, some trivia questions generated by Opus 4.5, how many house seats does US state X have, how many state legislature house seats does US state X have.
- What US state was Xth to join the union?
- Hopping from state to state motto, state flower, or number of counties in that state.
- What element has atomic number X?
- Winner of award in year (1900 + X) using the following awards: Miss America, Oscar best (supporting) actor/actress, Nobel peace/chemistry/physics/literature (only years with a single winner).
- Hopping from an award winner to the year or day of the month they were born. (I exclude Miss America winners as they aren't consistently famous enough for models to have this memorized.)

I avoid loops where we hit the same type of template twice in the same question (preventing things like "What element has atomic number (what is the atomic number of oxygen)?").

Here are random example questions for each hop level.

2 hop:

- Who was Miss America for the (1900 + (At what age did Tupac Shakur die)) competition?
- Who won the Nobel Prize in Chemistry in (1900 + (atomic number of Technetium))?
- Who won the Nobel Prize in Literature in (1900 + (atomic number of Rubidium))?
- Who won the Academy Award for Best Supporting Actress for a film released in (1900 + (atomic number of Curium))?
- On what day of the month was the Oscar Best Actress winner for a film released in 1966 born?
- What is the state motto of the US State that was number 35 to join the union?
- What is the state motto of the US State that was number 16 to join the union?
- What element has atomic number (How many representatives does Colorado have in the US House of Representatives)?
- Who won the Nobel Prize in Literature in (1900 + (How many representatives does Michigan have in the US House of Representatives))?
- Who won the Nobel Prize in Physics in (1900 + (How many representatives does Texas have in the US House of Representatives))?

3 hop:


- On what day of the month was the Oscar Best Actor winner for a film released in (1900 + (At what age did Miguel de Cervantes die)) born?
- In what year was the best supporting actor winner at the (At what age did Robert Schumann die)th Academy Awards born?
- On what day of the month was the Oscar Best Supporting Actress winner for a film released in (1900 + (At what age did Frank Herbert die)) born?
- On what day of the month was the Oscar Best Supporting Actress winner for a film released in (1900 + (atomic number of Hafnium)) born?
- How many county-equivalents are in the US State that was number (atomic number of Selenium) to join the union?
- What US state was number (On what day of the month was the best actor winner at the 45th Academy Awards born) to join the union?
- What element has atomic number (On what day of the month was the Oscar Best Supporting Actress winner for a film released in 1973 born)?
- How many county-equivalents are in the US State that was number (How many seats are in the lower house of Delaware's state legislature) to join the union?
- How many county-equivalents are in the US State that was number (What is the number of plays Shakespeare wrote) to join the union?
- On what day of the month was the Nobel Prize in Literature winner in (1900 + (How many representatives does Connecticut have in the US House of Representatives)) born?

4 hop:

- What US state was number (On what day of the month was the best actress winner at the (At what age did Che Guevara die)th Academy Awards born) to join the union?
- What element has atomic number (On what day of the month was the Nobel Prize in Literature winner in (1900 + (atomic number of Magnesium)) born)?
- What element has atomic number (On what day of the month was the best actress winner at the (atomic number of Gadolinium)th Academy Awards born)?
- Who was Miss America for the (1900 + (How many county-equivalents are in the US State that was number (atomic number of Manganese) to join the union)) competition?
- Who won the Nobel Prize in Chemistry in (1900 + (How many county-equivalents are in the US State that was number (atomic number of Gallium) to join the union))?
- Who won the Nobel Prize in Literature in (1900 + (How many county-equivalents are in the US State that was number (atomic number of Chlorine) to join the union))?
- What is the state flower of the US State that was number (On what day of the month was the Nobel Prize in Chemistry winner in 1947 born) to join the union?
- What is the state flower of the US State that was number (On what day of the month was the Oscar Best Supporting Actress winner for a film released in 1989 born) to join the union?
- What US state was number (On what day of the month was the Oscar Best Supporting Actor winner for a film released in (1900 + (How many seats are in the lower house of Arizona's state legislature)) born) to join the union?
- Who won best actress at the (How many county-equivalents are in the US State that was number (How many representatives does Nebraska have in the US House of Representatives) to join the union)th Academy Awards?

To generate a dataset of 2-hop questions with relatively salient facts, I use the same initial questions to generate an integer (except I cut questions about number of representatives in a given state house) but only keep the "What US state was Xth to join the union?" and "What element has atomic number X?" templates.

See [generate_dataset.py](https://github.com/rgreenblatt/multi_hop/blob/master/generate_dataset.py) in the public code base for more details.

## Dataset sanity checks

We verify that with reasoning Opus 4.5 has high accuracy. It gets 96.8% correct overall (>95% for each hop category). On inspection, these appear to be genuine errors on the part of the model. We can consider this to be the ceiling performance on latent (out-of-context) n-hop reasoning.

We verify that Opus 4.5 has high accuracy on each possible single hop. It gets 99.7% correct overall.

# Appendix: AI usage

I heavily used Claude Code for this project, especially for writing the code for generating datasets and for plotting.
Probably the uplift on this exact project was pretty substantial (like 3x), though I wouldn't have done this project without current AI tools.
I didn't use AI for writing this post.

