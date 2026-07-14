# Website Assistant Setup — Using This Repo as the Source of Truth

The BougieBams website assistant answers from this knowledge base via OpenAI
Retrieval (a vector store + the `file_search` tool). The repo is the single
source of truth: edit markdown here, push to main, and the bot updates itself.

## How it works

1. A GitHub Action (`.github/workflows/sync-knowledge-base.yml`) runs on every
   push to main that touches `knowledge/`. It re-uploads all articles to an
   OpenAI vector store named `bougie-bams-knowledge-base`.
2. The website's chat endpoint calls OpenAI with the `file_search` tool pointed
   at that vector store. OpenAI retrieves the most relevant article chunks and
   the model answers from them.

## One-time setup

1. **Add your API key to GitHub:** repo → Settings → Secrets and variables →
   Actions → New repository secret. Name: `OPENAI_API_KEY`, value: your key.
2. **Run the sync once:** repo → Actions → "Sync knowledge base to OpenAI
   vector store" → Run workflow. When it finishes, open the run log and copy
   the `VECTOR_STORE_ID=vs_...` line from the end.
3. **Add the ID to your website's environment** as `KB_VECTOR_STORE_ID`.

## Chat endpoint code (Node.js)

```js
import OpenAI from "openai";
const client = new OpenAI(); // uses OPENAI_API_KEY

const SYSTEM_PROMPT = `
You are the BougieBams Assistant for bougiebams.com, a luxury, intimate mahjong
community founded by Patsy Miller in Texas. Warm, polished, a little playful.

Rules:
- Answer ONLY from the retrieved knowledge base articles. If the answer is not
  in the knowledge base, say so and direct the customer to patsy@bougiebams.com.
- Never invent prices, policies, or event details. For current prices and
  event dates, point to the shop and events pages.
- Articles marked "needs_review" or "DRAFT" are provisional: present them as
  general guidance and refer the customer to support for confirmation.
- For official American Mahjong rule interpretations, note that the current
  NMJL card and rulebook are authoritative. Never recite annual card hands.
- Keep answers short and friendly; offer ONE follow-up suggestion at most.
`;

export async function answerChat(userMessage, history = []) {
  const response = await client.responses.create({
    model: "gpt-4.1-mini",
    instructions: SYSTEM_PROMPT,
    input: [...history, { role: "user", content: userMessage }],
    tools: [
      {
        type: "file_search",
        vector_store_ids: [process.env.KB_VECTOR_STORE_ID],
        max_num_results: 6,
      },
    ],
  });
  return response.output_text;
}
```

Notes:
- API surfaces evolve; if `responses.create` or tool config errors, check the
  current OpenAI Retrieval / file_search docs for the equivalent call.
- Keep the temperature low (or default) — this is a support bot, not a poet.
- Frontmatter travels with each article, so the model can see id, audience,
  and copyright_status when answering.

## Updating content

Edit or add articles in `knowledge/`, run the local pipeline
(`validate_metadata.py`, `generate_index.py`, `chunk_markdown.py`,
`add_wikilinks.py`), and push to main. The Action re-syncs automatically —
no website changes needed.

## Alternative: Supabase pgvector

`exports/jsonl/chunks.jsonl` contains pre-chunked articles with ids and
metadata, ready to embed into a Supabase pgvector table if you ever want
retrieval fully under your own control. The OpenAI vector store route above
is simpler and recommended until there's a reason to switch.
