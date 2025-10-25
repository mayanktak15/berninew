import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Try to import dependencies with error handling
try:
    from vector_creator import get_vector_store
    VECTOR_STORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Vector store not available: {e}")
    VECTOR_STORE_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Transformers not available: {e}")
    TRANSFORMERS_AVAILABLE = False

try:
    from langchain.chains import RetrievalQA
    from langchain_community.llms import HuggingFacePipeline
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PyTorch not available: {e}")
    TORCH_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google Generative AI not available: {e}")
    GENAI_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()  # load variables from .env file
    DOTENV_AVAILABLE = True
except ImportError as e:
    print(f"Warning: python-dotenv not available: {e}")
    DOTENV_AVAILABLE = False

# Try to get API key from multiple environment variable names
api_key = os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY")

if api_key and GENAI_AVAILABLE:
    genai.configure(api_key=api_key)
    print(f"Google API configured with key: {api_key[:10]}...")
else:
    print("Warning: No Google API key found or Google AI not available")
    print("Available environment variables:", [k for k in os.environ.keys() if 'API' in k])


# Suppress TensorFlow and duplicate library issues

# ======== Vector Store Initialization ========
if VECTOR_STORE_AVAILABLE:
    try:
        vector_store = get_vector_store("faq.txt")
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        print("Vector store initialized successfully")
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        retriever = None
else:
    print("Vector store not available, using simple FAQ responses only")
    retriever = None

# ======== Simple FAQ Response Function ========
def get_simple_faq_response(user_query):
    """Simple FAQ responses that don't require AI API"""
    query_lower = user_query.lower()
    
    if "fever" in query_lower or "temperature" in query_lower or "hot" in query_lower:
        return """I understand you have a fever. Here's some general guidance:

🌡️ **For fever management:**
- Stay hydrated with plenty of fluids
- Rest and avoid strenuous activities
- Monitor your temperature regularly
- Consider over-the-counter fever reducers if appropriate

⚠️ **When to seek medical attention:**
- Fever above 103°F (39.4°C)
- Fever lasting more than 3 days
- Severe symptoms like difficulty breathing
- Signs of dehydration

📋 **Next steps:**
Please fill out a consultation form on your dashboard with your specific symptoms so our doctors can provide proper medical advice. We cannot provide specific medical treatment through this chat."""
    
    elif "docify" in query_lower or "what is" in query_lower:
        return """Docify Online is a platform for filling out medical certificates and consultation forms, with support from our chatbot. 
        
We connect you with qualified healthcare professionals 24/7 for medical consultations from the comfort of your home."""
    
    elif "submit" in query_lower or "consultation" in query_lower or "form" in query_lower:
        return """To submit a consultation form:
1. Log in to your account
2. Go to the dashboard
3. Fill out the form with your symptoms
4. You can also update past submissions anytime"""
    
    elif "secure" in query_lower or "data" in query_lower or "privacy" in query_lower:
        return """Yes, your data is secure! We use password hashing and store data securely in our database. 
        User details are also exported to CSV files for backup purposes."""
    
    elif "support" in query_lower or "contact" in query_lower or "help" in query_lower:
        return """You can reach our support team via:
- This chatbot for immediate assistance
- Email at support@docify.online
- Through your dashboard consultation form"""
    
    elif "symptoms" in query_lower:
        return """When describing symptoms, please include:
- Detailed description of what you're experiencing
- Duration (how long you've had the symptoms)
- Severity level
- Any relevant medical history"""
    
    elif any(greeting in query_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        return """Hello! Welcome to Docify Online. I'm here to help you with information about our medical consultation services. 
        
What would you like to know about our platform?"""
    
    elif any(health_term in query_lower for health_term in ["pain", "headache", "cough", "cold", "sick", "unwell", "symptoms"]):
        return """I understand you're experiencing health concerns. While I can provide general information about Docify Online's services, I cannot provide specific medical advice.

🏥 **For medical concerns:**
Please fill out a consultation form on your dashboard with your specific symptoms. Our qualified doctors will review your case and provide appropriate medical guidance.

📋 **How to get help:**
1. Go to your dashboard
2. Click "Submit Consultation Form"
3. Describe your symptoms in detail
4. Our medical team will respond promptly

This ensures you receive proper medical attention from qualified healthcare professionals."""
    
    else:
        return """I'm here to help with questions about Docify Online. You can ask me about:
- Our medical consultation services
- How to submit consultation forms
- Data security and privacy
- Contact information
- Platform features

For medical concerns, please fill out a consultation form on your dashboard to speak with qualified doctors.

What would you like to know?"""

# ======== Query Processor Function ========
def process_query(user_query, symptoms=None):
    """Basic query processor with FAQ fallback"""
    try:
        # If retriever is not available, use simple FAQ response
        if retriever is None:
            return get_simple_faq_response(user_query)
            
        symptoms_section = f"User Symptoms: {symptoms}\nIncorporate these symptoms into your response if relevant." if symptoms else ""
        top_docs = retriever.invoke(user_query)[:3]  # Fixed deprecated method

        result = ""
        for i, doc in enumerate(top_docs):
            doc_text = f"Doc {i + 1}: {doc.page_content}\n" + "-" * 50 + "\n"
            result += doc_text
        print(result)
        return result if result.strip() else get_simple_faq_response(user_query)
    except Exception as e:
        print(f"Error in process_query: {e}")
        return get_simple_faq_response(user_query)
def process_query2(user_query, symptoms=None):
    # Prepare the symptoms section if provided
    symptoms_section = f"User Symptoms: {symptoms}\nIncorporate these symptoms into your response if relevant." if symptoms else ""

    # Retrieve the top 3 relevant documents
    top_docs = retriever.get_relevant_documents(user_query)[:3]

    # Debug: Print the retrieved documents
    print("--- Retrieved Documents ---")
    for i, doc in enumerate(top_docs):
        print(f"Doc {i+1}: {doc.page_content}")
        print("-" * 50)

    # Pass the relevant documents to the chain for processing
    from langchain_community.llms import Ollama
    ollama = Ollama(base_url='http://localhost:11434', model="docify")
    result=ollama(f"answer user query base on retrived information{user_query}+{top_docs} give short and summerized answer"
                  f"do not recomand and medication ask them to fill the form and consult a doc")
    print(result)
    return result
# Optional: Manual evaluation function

# Step 5: Process Query and Generate Structured Response
def process_query3(user_query, symptoms=None):
    model_id = "tiiuae/falcon-7b"

    text_generation_pipeline = pipeline(
        "text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, max_new_tokens=400, device=0)

    llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

    prompt_template = """
    <|system|>
    Answer the question based on your knowledge. Use the following context to help:

    {context}

    </s>
    <|user|>
    {question}
    </s>
    <|assistant|>

     """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template,
    )

    llm_chain = prompt | llm | StrOutputParser()
    from langchain_core.runnables import RunnablePassthrough

    rag_chain = {"context": retriever, "question": RunnablePassthrough()} | llm_chain

    # Generate and return response
    try:
        response = rag_chain.invoke(prompt)
        response = response.replace("</s>", "").strip()
        print("Model response:", response)
        return response
    except Exception as e:
        print("Model generation error:", e)
        return "Sorry, there was an error generating a response."

# Process Query
def process_query4(user_query, symptoms=None):
    model_name = "google/flan-t5-base"
    finetuned_path = "fine_tuning/lora_flan_t5_small/finetuned"
    tokenizer = AutoTokenizer.from_pretrained(finetuned_path)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model = PeftModel.from_pretrained(base_model, finetuned_path)
    text2text_pipeline = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=200,
        device=-1
    )

    llm = HuggingFacePipeline(pipeline=text2text_pipeline)

    # RAG Setup
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    print(retriever.metadata)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    context = qa_chain({"query": user_query})['result']
    prompt = f"""
    You are a medical chatbot for Docify Online. Answer the user's query in a structured, clear, and concise manner.
    Use the following FAQ context to inform your response:
    your role is to answer information about what to do in fever
    {context}

    User Query: {user_query}
    """
    if symptoms:
        prompt += f"\nUser Symptoms: {symptoms}\nPlease incorporate the symptoms into your response if relevant."

    prompt += """
    understand the question and situation of a person then answer:
    **Answer**: [Your answer here]
    **Additional Info**: [Any relevant details or suggestions]
    Do not speculate or provide unverified medical advice.
    """

    response = text2text_pipeline(prompt)[0]["generated_text"]
    return response

def process_query5(user_query, symptom=None):
    """Enhanced query processor using Google Gemini with error handling"""
    try:
        # Check if API key is available and valid
        if not api_key or api_key.strip() == '' or api_key == 'your_actual_google_api_key_here':
            print("No valid Google API key available, falling back to simple FAQ response")
            return get_simple_faq_response(user_query)
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 15000,
            "response_mime_type": "text/plain",
        }
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )
        # Generate summary using Gemini model
        if retriever is not None:
            top_docs = retriever.invoke(user_query)[:3]  # Use invoke instead of deprecated get_relevant_documents
        else:
            top_docs = []
        
        summary = model.generate_content(contents=(
            f"U are a chatbot for docify answer in minmum words about the faq user ask "
            f"Docify is an online platform that allows users to consult certified doctors from the comfort of their home. Whether it's a minor health concern or the need for a medical certificate"
            f"now user can ask unreleveant question make sure not to answer them"
            f"do not provide any medical consultation form your side"
            f"strictly follow the context provide to you"
            f"query={user_query},extracted_content={top_docs}"
        ))

        return summary.text
    
    except Exception as e:
        print(f"Error with Google API: {e}")
        print("Falling back to simple FAQ response")
        return get_simple_faq_response(user_query)


def manual_evaluation():
    test_queries = [
        {"query": "How do I manage a fever?", "symptoms": "Fever for 2 days, 101°F"},
        {"query": "What is Docify Online?", "symptoms": None},
    ]
    for test in test_queries:
        response = process_query(test["query"], test["symptoms"])
        print(f"\nQuery: {test['query']}")
        if test["symptoms"]:
            print(f"Symptoms: {test['symptoms']}")
        print(f"Response: {response}")
