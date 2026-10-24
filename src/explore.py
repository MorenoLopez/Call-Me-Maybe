from llm_sdk import Small_LLM_Model

def main():
    prompt = "Hello"
    model = Small_LLM_Model()
    
    ids = list(model.encode(prompt).squeeze().tolist())
    print(ids)
    
    logits = model.get_logits_from_input_ids(ids[0])
    print(len(logits))
    
    next =  logits.index(max(logits))
    print(next)
    
    decoded = model.decode(next)
    print(decoded)
    
    print(model.decode(ids + [next]))


if __name__ == "__main__":
    main()