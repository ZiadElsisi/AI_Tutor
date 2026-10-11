from backend.config import MODEL_ID, EMBEDDING_MODEL_ID, MAX_GENERATION_TOKENS


class ModelRuntime:
    def __init__(self):
        self.generator = None
        self.embedder = None
        self.tokenizer = None
        self.device = "unloaded"

    def load(self, model_id: str = MODEL_ID):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        self.embedder = __import__("sentence_transformers").SentenceTransformer(EMBEDDING_MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        has_cuda = torch.cuda.is_available()
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float16 if has_cuda else torch.float32,
            device_map="auto" if has_cuda else None,
        )
        self.device = "cuda" if has_cuda else "cpu"
        self.tokenizer = tokenizer
        self.generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

    def generate(self, system: str, user: str, max_new_tokens: int = MAX_GENERATION_TOKENS) -> str:
        if self.generator is None:
            raise RuntimeError("The language model is not loaded.")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
        except TypeError:
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        result = self.generator(prompt, max_new_tokens=min(max_new_tokens, MAX_GENERATION_TOKENS), do_sample=False)
        generated = result[0]["generated_text"]
        return str(generated)[len(prompt):].strip() if str(generated).startswith(prompt) else str(generated).strip()


runtime = ModelRuntime()
