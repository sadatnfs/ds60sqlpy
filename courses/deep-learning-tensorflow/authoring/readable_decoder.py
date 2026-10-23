"""Literal source template for the standalone llm-016 examples."""

DECODER_SOURCE = r'''class TinyDecoder(nn.Module):
    def __init__(self, vocab=16, width=32, heads=2, context=32):
        super().__init__()
        dimensions = (vocab, width, heads, context)
        if any(type(value) is not int or value <= 0 for value in dimensions):
            raise ValueError("positive integer dimensions are required")
        if width % heads != 0:
            raise ValueError("model width must be divisible by head count")
        self.vocab, self.width, self.heads, self.context = vocab, width, heads, context
        self.token = nn.Embedding(vocab, width)
        self.position = nn.Embedding(context, width)
        self.norm1 = nn.LayerNorm(width)
        self.qkv = nn.Linear(width, 3 * width, bias=False)
        self.projection = nn.Linear(width, width, bias=False)
        self.norm2 = nn.LayerNorm(width)
        self.feed = nn.Sequential(
            nn.Linear(width, 2 * width), nn.ReLU(), nn.Linear(2 * width, width)
        )
        self.output = nn.Linear(width, vocab, bias=False)

    def forward(self, ids, cache=None):
        if (
            ids.ndim != 2
            or ids.dtype != torch.long
            or ids.shape[0] == 0
            or ids.shape[1] == 0
        ):
            raise ValueError("nonempty long batch,time IDs")
        offset = 0 if cache is None else cache["k"].shape[2]
        batch, time = ids.shape
        if (
            offset + time > self.context
            or torch.any(ids < 0)
            or torch.any(ids >= self.vocab)
        ):
            raise ValueError("context or vocabulary limit")
        x = self.token(ids) + self.position(torch.arange(offset, offset + time))
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)

        def split(t):
            return t.reshape(
                batch, time, self.heads, self.width // self.heads
            ).transpose(1, 2)

        q, k, v = map(split, (q, k, v))
        if cache is not None:
            if cache["k"].shape[0] != batch:
                raise ValueError("cache batch mismatch")
            k = torch.cat([cache["k"], k], dim=2)
            v = torch.cat([cache["v"], v], dim=2)
        allowed = (
            torch.arange(k.shape[2])[None, :]
            <= torch.arange(offset, offset + time)[:, None]
        )
        scores = q @ k.transpose(-2, -1) / (self.width // self.heads) ** 0.5
        weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        mixed = (
            (weights @ v).transpose(1, 2).contiguous().reshape(batch, time, self.width)
        )
        x = x + self.projection(mixed)
        x = x + self.feed(self.norm2(x))
        return self.output(x), {"k": k.detach(), "v": v.detach()}
'''
