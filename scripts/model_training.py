from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration

# 初始化模型和检索器
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq", index_name="custom")
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-nq", retriever=retriever)

def generate_recommendation(query):
    inputs = tokenizer(query, return_tensors="pt")
    output = model.generate(**inputs)
    return tokenizer.batch_decode(output, skip_special_tokens=True)