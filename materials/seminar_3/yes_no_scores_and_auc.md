# Evaluating our moderation model

Student report for Seminars 3 and 4 · 31 October 2026

Comparing the logits of **Yes** and **No** is enough to select an answer.
Keeping their difference also lets us rank comments and choose a different
decision threshold. Accuracy evaluates the selected answers; ROC AUC evaluates
the ranking across thresholds.

Our experiment found a substantial improvement after fine-tuning Qwen3-0.6B.
It also found that some dev comments appeared as labeled examples inside
training prompts. The results below separate the full class dev split from
the subset without that exact-text exposure.

## From logits to a decision

A logit is a model score for a possible next token. Let `z_yes` and `z_no` be
the logits for the exact tokens `Yes` and `No` after the prompt.

```python
score = z_yes - z_no
prediction = "Yes" if score > 0 else "No"
```

This is exactly the same decision as `z_yes > z_no`. Applying a sigmoid does
not change it:

$$
q = \frac{1}{1 + e^{-\mathrm{score}}}
\qquad
z_{\mathrm{yes}}>z_{\mathrm{no}}
\iff \mathrm{score}>0
\iff q>0.5.
$$

Equal logits give `score = 0` and `q = 0.5`; our strict `>` comparison chooses
No in that case. Using 0.5 as a cutoff does not mean every prediction has a
50% chance of being correct.

If the full vocabulary softmax gives probabilities `p_yes` and `p_no`, then:

$$
q = \frac{p_{\mathrm{yes}}}{p_{\mathrm{yes}}+p_{\mathrm{no}}}.
$$

So `q` is the probability of Yes **conditional on the next token being Yes
or No**. Other tokens can still have probability. Also, `q = 0.8` does not
establish that 80% of such comments violate the rule: that interpretation
requires checking calibration against labels.

Subtracting the two logits measures their relative preference and cancels
any common offset. A raw Yes logit alone does not account for the competing
No logit. For AUC, keep the raw difference: sigmoid preserves its ordering
mathematically, but rounding probabilities near zero or one can create ties.

## How this relates to MMLU

The standard likelihood-based MMLU task in `lm-evaluation-harness` supplies
the question and four options in one prompt, then scores the candidate
continuations A, B, C and D. It selects the candidate with the highest
conditional log likelihood and reports accuracy. Our two-candidate Yes/No
comparison uses the same principle. See the [MMLU configuration][mmlu] and
[answer selection code][harness-task].

For example, after a prompt ending in `Answer:`, the evaluator compares
`log P(" A" | prompt)`, `log P(" B" | prompt)` and the other candidates.
The exact leading space depends on prompt formatting and tokenization.
When each continuation is one token, the next-token distribution contains
all the required scores. For longer continuations, the backend sums their
tokens' conditional log probabilities. See the [likelihood backend][harness-hf].

It does not freely generate an answer and hope that it starts with A.
Scoring a prescribed continuation and generating text such as “The answer
is A” are different evaluation procedures.

We could use accuracy alone if the question were simply “How often does
the selected Yes/No answer match the label?” The course also retains scores
because its competition uses AUC and deployment may require other thresholds.

## Why use AUC

Automatic removal and a human review queue can use the same model with
different thresholds. Removal may require very few false alarms; review
may tolerate more false alarms to catch more violations. Both benefit from
violations receiving higher scores than clean comments.

Accuracy evaluates decisions at a chosen threshold. AUC summarizes how well
the scores separate the two classes across thresholds. It avoids making a
particular cutoff, such as `q > 0.5`, part of the model comparison.

The [competition][competition] specifies column-averaged AUC and requests
probabilities. The threshold flexibility above explains why this metric is
useful; the competition page does not state the organizers' reason for choosing it.

AUC does not choose a threshold, measure probability calibration, or guarantee
good performance at a specific false-positive budget. If the deployment
requirement is “maximize violations caught while falsely flagging at most
1% of clean comments,” evaluate that requirement directly. ROC curves can
cross, so a higher overall AUC need not win in the region you care about.

## Building the ROC curve

For a threshold `t`, flag a comment when `score > t`. Define:

$$
\mathrm{TPR}=\frac{\text{violations flagged}}{\text{all actual violations}},
\qquad
\mathrm{FPR}=\frac{\text{clean comments flagged}}{\text{all actual clean comments}}.
$$

TPR is the true-positive rate, also called recall. FPR is the false-positive
rate. Its denominator is **all clean comments**, not all flagged comments.

The ROC curve plots FPR horizontally and TPR vertically as the threshold
changes. The following six rows are actual fine-tuned advertising predictions,
selected to illustrate the calculation; they are not a separate evaluation set.
Each step places the threshold just below the next score.

| Newly flagged row | Actual label | Score | FPR | TPR |
|---|---|---:|---:|---:|
| Nothing yet | — | — | 0 | 0 |
| 1860 | Violation | 5.125 | 0 | 1/3 |
| 1704 | Violation | 1.625 | 0 | 2/3 |
| 1020 | Clean | −0.125 | 1/3 | 2/3 |
| 865 | Violation | −1.375 | 1/3 | 1 |
| 367 | Clean | −3.875 | 2/3 | 1 |
| 1541 | Clean | −4.500 | 1 | 1 |

Passing a violation moves the curve up. Passing a clean comment moves it
right. A good ranking moves up early, catching violations before admitting
many clean comments. A perfect ranking reaches `(FPR = 0, TPR = 1)`.

At threshold zero, these six rows have accuracy `5/6 = 83.3%`: one violation
is missed. Their ROC AUC is a different calculation.

## Deriving AUC from the curve

AUC means area under the curve; here the curve is ROC. Our example has three
horizontal segments, each of width `1/3`, at heights `2/3`, `1` and `1`.
Vertical segments have zero width and add no area. Therefore:

$$
\mathrm{AUC}
=\frac13\frac23+\frac13\cdot1+\frac13\cdot1
=\frac89\approx0.889.
$$

To derive the general formula, let `P` be the number of actual violations
and `N` the number of actual clean comments. First assume there are no ties.
When the threshold passes clean comment `j`:

1. FPR increases by `1/N`.
2. If `k_j` violations have higher scores, those violations are already flagged,
   so the height is `k_j/P`.
3. This horizontal segment contributes area `k_j/(P N)`.

Adding these areas over all clean comments gives:

$$
\mathrm{AUC}=\frac{\sum_{j=1}^{N} k_j}{PN}
=\frac{\text{correctly ordered violation–clean pairs}}{\text{all violation–clean pairs}}.
$$

In the six-row example, the three violations beat respectively three, three
and two clean comments: `(3 + 3 + 2) / 9 = 8/9`. This is the same number as
the geometric area.

A tied violation–clean pair receives half credit. This averages its two
possible orders and corresponds to linear interpolation through tied groups
on the ROC curve. The complete formula is:

$$
\boxed{\mathrm{AUC}=
\frac{\#(s_{\mathrm{violation}}>s_{\mathrm{clean}})
+\tfrac12\#(s_{\mathrm{violation}}=s_{\mathrm{clean}})}{PN}}.
$$

Selecting one violation and one clean comment uniformly makes every pair
equally likely. That is why AUC also equals the probability that the violation
scores higher, plus half the probability of a tie. AUC of 0.889 means 88.9%
pair-ordering credit, not 88.9% classification accuracy. Perfect ordering gives
1; random ordering has expected AUC 0.5. AUC is not an average of accuracies
over a list of thresholds.

The course's [auc.py](../../seminar_3/auc.py) counts these pairs efficiently
by sorting scores. It computes AUC separately for advertising and legal advice,
then gives the two rules equal weight:

$$
\mathrm{AUC}_{\mathrm{course}}
=\frac{\mathrm{AUC}_{\mathrm{advertising}}+\mathrm{AUC}_{\mathrm{legal}}}{2}.
$$

The [scikit-learn ROC documentation][roc] and [area implementation][auc-implementation]
describe the curve and trapezoidal calculation.

## What the experiment measured

The experiment used the course split: 1,628 training rows and 401 dev rows.
Prompts included the rule, community, two positive examples, two negative
examples and the comment to judge. Thinking was disabled. “Before fine-tuning”
below means before **our task training**; these are already pretrained and
post-trained language models. Qwen3-0.6B is a small 0.6-billion-parameter model.
See the [Qwen model card][qwen].

The 0.6B model was trained with the Seminar 4 configuration: LoRA rank 8,
alpha 32, all linear layers, learning rate `4e-4`, two epochs, effective batch
size 16, maximum training length 1,024 tokens and seed 42. The training command
took 169 seconds on an NVIDIA L40S. This is one run, not an average over seeds.
Evaluation used the same dev prompts across all five models. All
model-comparison tables use the saved Modal predictions.

**The full dev split has labeled-example exposure, detailed below.** These
numbers describe that class split and should not be presented as clean
unseen-comment generalization results.

| Model | AUC of full score | AUC of binary Yes/No | Accuracy at score > 0 | Predicts Yes |
|---|---:|---:|---:|---:|
| Qwen3-0.6B before task training | 0.486 | 0.512 | 51.1% | 78.3% |
| Qwen3-1.7B before task training | 0.600 | 0.509 | 49.9% | 82.0% |
| Qwen3-4B before task training | 0.710 | 0.588 | 55.4% | 51.1% |
| Qwen3-8B before task training | 0.741 | 0.575 | 54.6% | 66.3% |
| Qwen3-0.6B after task training | **0.891** | **0.795** | **80.3%** | 55.6% |

AUC averages the rules; accuracy counts correct decisions across all rows.
Binary AUC means computing AUC after replacing every score with 0 or 1.
For one rule, it equals `(TPR + TNR) / 2`, where `TNR = 1 − FPR`; it is
generally different from ordinary accuracy.

Keeping full scores preserves information but does not guarantee a higher
measured AUC. The untuned 0.6B model's continuous AUC was slightly below its
binary AUC. Its ranking was near chance, so moving the threshold alone could
not supply useful ordering.

After fine-tuning, advertising AUC was 0.934 and legal AUC was 0.848. For the
85 advertising violations and 110 clean comments, the exact calculation is:

```text
9,350 pairs = 85 × 110
8,713 strict wins and 49 ties
AUC = (8,713 + 49 / 2) / 9,350 = 0.934492
```

Fine-tuning trains the model to increase the likelihood of the labeled Yes/No
answer for these prompts. The improvement can affect both ranking and the
decision boundary. These runs do not isolate how much comes from learning
the moderation criteria, adapting to the prompt format, or other effects.
They measure immediate answers with thinking off, not performance after
generating a reasoning sequence.

The fine-tuned model's AUC on its own training targets was 0.950. That measures
fit to training data and should not be reported as generalization performance.

## The training example overlap

The split keeps identical **target comment text** together, but each prompt
also contains labeled example comments. Checking those fields found:

- 210 of the 401 dev targets appear as examples under the same rule inside
  training prompts.
- Two dev targets also appear among their own prompt's examples; both are
  already included in those 210 rows.
- 191 rows remain after excluding these matches.

The 191-row subset has 53 advertising rows and 138 legal rows. Applying the
same saved models and scores to it gives:

| Model | AUC | Accuracy at score > 0 |
|---|---:|---:|
| Qwen3-0.6B before task training | 0.504 | 55.5% |
| Qwen3-1.7B before task training | 0.551 | 53.4% |
| Qwen3-4B before task training | 0.600 | 51.8% |
| Qwen3-8B before task training | 0.621 | 54.5% |
| Qwen3-0.6B after task training | **0.780** | **72.3%** |

The improvement survives the exclusion. This is a retrospective sensitivity
check with a different mix of comments, not a new independent test. The
audit checks exact text, not paraphrases or near-duplicates. The change from
0.891 to 0.780 cannot be attributed entirely to memorization because the
evaluated subset also changes.

For a future test of unseen-comment performance, keep its targets out of all
training prompt fields and out of their own evaluation examples. Freeze the
split and example-selection procedure before fitting models or thresholds.

## Choosing a deployment threshold

After fine-tuning, select the threshold on calibration data and measure its
performance on separate evaluation data. Repeat this when the model or prompt
changes. Store the selected threshold with the deployed model and use the
same score calculation.

For a small demonstration, the 401 dev rows were split into two folds of
206 and 195 rows, keeping identical comment text together. A threshold was
selected on one fold and evaluated on the other, then the roles were reversed.
Counts below pool the two evaluation folds; each row is evaluated once.
The training-example exposure described above still applies.

| Threshold selection policy | TPR | FPR | Accuracy |
|---|---:|---:|---:|
| Fixed score > 0 | 85.6% | 25.1% | 80.3% |
| Highest accuracy on the calibration fold | 80.7% | 22.6% | 79.1% |
| Highest TPR with calibration FPR at most 10% | 68.8% | 13.1% | 77.8% |

For the last policy, the selected score thresholds were 0.625 and 1.0,
equivalent to conditional Yes probabilities of about 0.651 and 0.731.
Their calibration FPRs were 9.1% and 9.0%; on the other folds they were
21.0% and 5.1%. Pooling those evaluation counts gives 13.1%.

Thus, a calibration constraint is not an evaluation or production guarantee.
Selecting for calibration accuracy also did not improve evaluation accuracy
in this small demonstration. Choosing a threshold and reporting its best
accuracy on the same rows gives an optimistic result.

## What happens when the model generates text

The experiment also allowed up to eight new tokens with greedy decoding.
Before task training, the 0.6B model started 392 of 401 responses with Yes or
No. The other nine started with `Answer:`. After fine-tuning, all 401 decoded
responses were exactly Yes or No.

Even then, three generated answers differed from the decision computed from
the saved logits. The scores and generation came from separate forward calls;
the saved outputs do not establish the cause of these disagreements. Do not
assume a scoring procedure and a generation procedure are interchangeable
without checking them.

## Checking the numbers

[Saved experiment results](yes_no_auc_results.json) contain the unrounded
metrics, split-audit row IDs, threshold-fold counts, generation counts,
training configuration and the six-row example. Counts refer to dataset rows;
some rows contain repeated comment text. The 0.6B checkpoint was pinned;
the original run did not record checkpoint revisions for the larger models.

You can reproduce the six-row AUC with the course code, without a GPU or
additional packages. From the repository root:

```python
from seminar_3.auc import auc

labels = [1, 1, 0, 1, 0, 0]
scores = [5.125, 1.625, -0.125, -1.375, -3.875, -4.5]

accuracy = sum((s > 0) == y for s, y in zip(scores, labels)) / len(labels)
print(f"Accuracy at zero: {accuracy:.4f}")  # 0.8333
print(f"ROC AUC: {auc(labels, scores):.4f}")  # 0.8889
```

Try adding 10 to every score. AUC stays the same because the ordering stays
the same. Accuracy at the unchanged threshold zero becomes `3/6`, because
all six scores now exceed zero. Moving the threshold by the same amount
restores the original decisions. This demonstrates exactly what AUC ignores
and what a deployed decision rule must specify.

[competition]: https://www.kaggle.com/competitions/jigsaw-agile-community-rules/overview/abstract
[mmlu]: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu/default/_default_template_yaml
[harness-task]: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/api/task.py
[harness-hf]: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/models/huggingface.py
[roc]: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html
[auc-implementation]: https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/metrics/_ranking.py
[qwen]: https://huggingface.co/Qwen/Qwen3-0.6B
