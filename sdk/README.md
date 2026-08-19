# evalctl — evaluate a prompt change in one command

Run an eval and gate it against a baseline (fails CI on a regression):

```bash
evalctl eval \
  --name alt-text-generator --task summarize \
  --prompt-file prompts/alt_text_v5.txt --model gpt-4o-mini \
  --dataset-name alt-text --dataset-file datasets/alt-text.jsonl \
  --judge-model gpt-4o \
  --baseline-run <the-current-shipping-run-id>
