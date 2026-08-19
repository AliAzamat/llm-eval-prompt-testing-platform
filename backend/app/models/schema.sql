-- A prompt is a named, versioned thing (e.g. "alt-text-generator"). The prompt
-- row is the stable identity; the text lives in append-only version rows.
CREATE TABLE IF NOT EXISTS prompts (
    id            UUID PRIMARY KEY,
    name          TEXT        NOT NULL,
    task          TEXT        NOT NULL,          -- 'qa' | 'summarize' | 'extract' | ...
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name)
);

-- Prompt versions are IMMUTABLE. A new version is a new row, never an UPDATE.
-- (prompt_id, version) is monotonically increasing; content_hash dedupes edits.
CREATE TABLE IF NOT EXISTS prompt_versions (
    id            UUID PRIMARY KEY,
    prompt_id     UUID        NOT NULL REFERENCES prompts (id) ON DELETE CASCADE,
    version       INTEGER     NOT NULL,
    template      TEXT        NOT NULL,          -- the prompt body, with {placeholders}
    content_hash  TEXT        NOT NULL,          -- sha256 of the template
    model         TEXT        NOT NULL,          -- the model this version targets
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (prompt_id, version),
    -- The same body re-registered for a prompt is the same version, not a new one.
    UNIQUE (prompt_id, content_hash)
);

-- A dataset is a named collection of eval inputs for one task.
CREATE TABLE IF NOT EXISTS datasets (
    id            UUID PRIMARY KEY,
    name          TEXT        NOT NULL,
    task          TEXT        NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name)
);

-- One eval input: the variables that fill the prompt, an optional grounding
-- context, and an optional expected reference the judge scores accuracy against.
CREATE TABLE IF NOT EXISTS dataset_items (
    id            UUID PRIMARY KEY,
    dataset_id    UUID        NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    item_key      TEXT        NOT NULL,          -- stable key so re-imports are idempotent
    inputs        JSONB       NOT NULL DEFAULT '{}',   -- {placeholder: value}
    context       TEXT,                          -- grounding text, if the task is grounded
    reference     TEXT,                          -- gold/expected answer, if known
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (dataset_id, item_key)
);

-- One eval run: a specific prompt VERSION scored over a specific dataset.
CREATE TABLE IF NOT EXISTS eval_runs (
    id                UUID PRIMARY KEY,
    prompt_version_id UUID        NOT NULL REFERENCES prompt_versions (id) ON DELETE CASCADE,
    dataset_id        UUID        NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    status            TEXT        NOT NULL DEFAULT 'running',  -- running | complete | failed
    judge_model       TEXT        NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One scored item within a run: the generated output plus the judge's rubric
-- scores. Every score in the whole system is keyed, through the run, to an
-- exact prompt version — that linkage is the point of the platform.
CREATE TABLE IF NOT EXISTS eval_scores (
    id            UUID PRIMARY KEY,
    run_id        UUID        NOT NULL REFERENCES eval_runs (id) ON DELETE CASCADE,
    item_id       UUID        NOT NULL REFERENCES dataset_items (id) ON DELETE CASCADE,
    output        TEXT        NOT NULL,          -- what the target prompt produced
    accuracy      REAL        NOT NULL,          -- 0..1 rubric dimensions
    grounding     REAL        NOT NULL,
    format_ok     REAL        NOT NULL,
    overall       REAL        NOT NULL,          -- weighted composite
    rationale     TEXT,                          -- the judge's short justification
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, item_id)
);
