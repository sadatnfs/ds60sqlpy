# Applied LLM authoring sources

The topic specifications, literal decoder source, reviewed route and renderer maintain all24 lesson bundles. Run `python courses/llm-applied/authoring/build.py` from the repository root after editing. The renderer preserves code blocks while polishing prose punctuation, includes shared helper code once in the worked sequence, and writes guides, learner worksheets, separate solutions and manifests. Later worked blocks deliberately reuse earlier fixture state, as the guides explain.

Optional pretrained files under `fixtures/pretrained/` and the course README are maintained directly and are not downloaded or executed by this renderer. The optional guide link is stored in its topic specification. The renderer does not alter runtime adapters, shared generators, learner state or package environments.
