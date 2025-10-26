# AI Image Generator for Cursor IDE

AI-assisted image generation tool for Cursor IDE (and similar AI-powered IDEs). Generate images through natural language conversation with your AI assistant. Works in any language.

**Providers:** Free HuggingFace API (default) with fallback to OpenAI DALL-E (paid).

📁 Images saved to `~/Downloads`

---

## How to Use

1. Attach this `README.md` and `generate_image.py` to your AI assistant context
2. Describe the image you want in natural language
3. AI will ask clarifying questions and generate the image for you

---

## Setup

**Dependencies:**
```bash
pip3 install openai requests
```

**API Tokens:**

Tokens are stored in `~/.cursor/cli-config.json`:

```json
{
  "env": {
    "HF_TOKEN": "hf_your_token",
    "OPENAI_API_KEY": "sk-your-key"
  }
}
```

- **HF_TOKEN** (required for free generation): Get at https://huggingface.co/settings/tokens
- **OPENAI_API_KEY** (optional, paid): Get at https://platform.openai.com/api-keys

---

## For AI Assistant - Instructions

### Request Validation Rules

**Free (HuggingFace):**
- Execute without user confirmation
- Command: `python3 generate_image.py "prompt"`
- Cost: $0.00

**Paid (OpenAI):**
- Requires explicit `--provider openai` flag
- NEVER called automatically - user must explicitly approve
- If HF fails, suggest OpenAI but exit (don't auto-call)
- Command: `python3 generate_image.py "prompt" --provider openai`

### Technical Requirements

**IMPORTANT:** Script requires permissions for:
- **Network access** (API requests to HuggingFace/OpenAI)
- **Write to ~/Downloads** (saving images outside workspace)

**Always use:** `required_permissions: ['all']`

**Why `['all']`:**
- Sandbox blocks writes to ~/Downloads (outside workspace)
- `['network']` is insufficient for writing outside workspace
- `['all']` disables sandbox, allowing both API requests and writes to ~/Downloads

**Example:**
```python
run_terminal_cmd(
    command='python3 generate_image.py "prompt"',
    required_permissions=['all']
)
```

### Generation Workflow

**1. Analyze Request**

If vague ("draw a cat", "create logo") → ask clarifying questions.
If detailed ("Photorealistic portrait, golden hour...") → generate immediately.

**2. Clarifying Questions (for vague requests)**

Question structure with examples:

```
Style:
- Photorealistic (like a photo)
- Digital art
- Minimalist
- Cartoon/animated

Details:
- Colors: warm/cold/pastel
- Mood: dramatic/peaceful
- Time: sunrise/day/sunset/night

Composition:
- Close-up
- Panorama
- Isometric

References:
- Cat: domestic/street/breed (ginger, grey, white?)
- Logo: like Apple/Starbucks/Nike
- Landscape: mountains/ocean/forest/city
```

**Example:**
```
User: "Draw a cat"
AI: "Please specify:
- Style: photorealistic/digital art/cartoon?
- Reference: domestic (ginger/grey?), street, breed?
- Environment: street/home/nature?"
```

**3. Determine Provider**

- Default: HuggingFace (free, no confirmation needed)
- If `--provider openai` or "use DALL-E" → requires confirmation
- If `--provider auto` and HF fails → suggest OpenAI but DON'T call it

**4. Generation**

HF: execute immediately
OpenAI: ONLY if user explicitly requested with `--provider openai`
Auto mode: try HF → if fails, suggest OpenAI command, exit

---

## Usage

**Free (default):**
```bash
python3 generate_image.py "detailed prompt"
python3 generate_image.py "prompt" --provider huggingface
```

**Paid (requires confirmation):**
```bash
python3 generate_image.py "prompt" --provider openai                    # DALL-E 2, ~$0.02
python3 generate_image.py "prompt" --provider openai --model dall-e-3   # DALL-E 3, ~$0.04
python3 generate_image.py "prompt" --provider openai --model dall-e-3 --quality hd  # HD, ~$0.08
```

**Parameters:**
- `--provider`: auto|huggingface|openai (default: huggingface)
  - `huggingface`: Use HF only (free)
  - `openai`: Use OpenAI only (paid, explicit request)
  - `auto`: Try HF, suggest OpenAI on fail (DON'T auto-call)
- `--hf-model`: HF model name (default: FLUX.1-schnell)
- `--model`: dall-e-2|dall-e-3 (default: dall-e-2)
- `--quality`: standard|hd (DALL-E 3 only)
- `--size`: 1024x1024|1792x1024|1024x1792 (DALL-E)
- `--output-dir`: path (default: ~/Downloads)

---

## Prompt Engineering

### Structure

```
[Subject] + [Style] + [Details] + [Lighting] + [Composition] + [Quality]
```

**Example:**
```
"Portrait of elderly sailor, photorealistic, weathered face with grey beard, 
golden hour lighting, centered composition, highly detailed, 8k quality"
```

### Keywords

**Style:**
`photorealistic`, `digital art`, `minimalist`, `cyberpunk`, `watercolor painting`, `3D render`, `manga style`

**Quality:**
`highly detailed`, `8k resolution`, `sharp focus`, `professional quality`, `ultra realistic`, `intricate details`

**Lighting:**
`golden hour lighting`, `studio lighting`, `dramatic lighting`, `soft ambient light`, `neon lights`, `cinematic lighting`

**Composition:**
`aerial view`, `close-up shot`, `wide angle`, `bird's eye view`, `centered composition`, `isometric view`

**Mood:**
`peaceful`, `dramatic`, `mysterious`, `vibrant`, `melancholic`, `epic`

**Colors:**
`warm colors`, `monochromatic`, `pastel palette`, `high contrast`, `neon colors`

**Technique:**
`depth of field`, `bokeh effect`, `HDR`, `macro photography`, `panoramic`

### Quick Reference

| Type | Add |
|------|-----|
| Photo | `professional photography, sharp focus, natural lighting` |
| Art | `digital art, artistic, detailed` |
| Logo | `logo design, minimalist, clean, vector` |
| Realism | `photorealistic, highly detailed, 8k` |
| Fantasy | `fantasy art, magical, dramatic lighting` |

### Avoid
- Vague descriptions: "beautiful picture"
- Contradictions: "realistic cartoon"
- Long prompts (>200 words)
- Negative constructions: instead of "not dark" → "bright"
- Object lists: focus on one subject

### Prompt Evolution

❌ "cat"
⚠️ "beautiful cat on street"  
✅ "ginger cat on cobblestone street, warm sunlight"
⭐ "Photorealistic ginger cat on cobblestone street, golden hour lighting, European old town background, shallow depth of field, highly detailed fur, 8k"

---

## Troubleshooting

**HF token not found:** Add `HF_TOKEN` to `~/.cursor/cli-config.json`

**503 HF error:** Model is loading (~20 sec), script will retry automatically

**OpenAI key not found:** Add `OPENAI_API_KEY` to `~/.cursor/cli-config.json`

**Invalid API key:** Check key at platform.openai.com and balance

---

## Resources

- HF Tokens: https://huggingface.co/settings/tokens
- OpenAI Keys: https://platform.openai.com/api-keys
- HF Models: https://huggingface.co/models?pipeline_tag=text-to-image
