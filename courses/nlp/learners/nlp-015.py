import numpy as np
RIVER=np.array([[1.,0.],[0.,1.]])
MONEY=np.array([[1.,0.],[0.,-1.]])

def encode(values,valid):
    raise NotImplementedError("Implement bidirectional attention with a real key mask")

def main():
    print("Handcrafted attention fixtures loaded. This is not a pretrained encoder.")

if __name__ == "__main__":
    main()

# Exercise 1: Implement contextual attention. Compute scaled scores, row-normalized weights and contextual outputs for both bank contexts. Expected: Bank's second output coordinate changes sign with river versus money.
# Exercise 2: Prove padding invariance. Append [99,99] with an invalid mask and compare valid outputs. Expected: Original valid outputs unchanged; padded-key weights zero; padded query output zero.
# Exercise 3: Train the document head. Fit the tiny logistic head on four pooled contextual fixtures. Expected: Loss decreases from log2 to below.1 and training predictions [0,1,0,1].
# Exercise 4: Mask subword supervision. Compute tagging cross-entropy with labels[0,-100,1,-100]. Expected: Loss log(1+exp(-2)); changing ignored logits does not alter it.
# Exercise 5: Reject missing supervision. Test all-padding encoder input and all-ignored tagging labels. Expected: Both raise clear ValueError instead of returning a meaningless average.
# Exercise 6: Design a real encoder evaluation. Specify held-out families, exact tokenizer/pooling identity and ambiguous bank probes. Expected: A written plan separates training fit, lexical baseline, contextual task quality and subgroup/truncation errors.
