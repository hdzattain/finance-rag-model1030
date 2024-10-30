from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration
import torch

# 初始化RAG模型、检索器和分词器
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq", index_name="custom")
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-nq", retriever=retriever)

# 设置设备（如果有GPU，则使用CUDA）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_recommendation(query):
    """
    基于用户查询生成金融推荐
    参数：
        query (str): 用户查询文本
    返回：
        recommendation (str): 生成的推荐结果
    """
    # 对输入查询进行编码
    inputs = tokenizer(query, return_tensors="pt").to(device)

    # 使用模型生成推荐文本
    output_ids = model.generate(**inputs)
    recommendation = tokenizer.batch_decode(output_ids, skip_special_tokens=True)

    return recommendation[0]

if __name__ == "__main__":
    # 测试生成推荐
    query = "What are the latest trends in the stock market?"
    recommendation = generate_recommendation(query)
    print("Generated Recommendation:", recommendation)