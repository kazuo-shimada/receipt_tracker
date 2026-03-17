import gradio as gr
import easyocr
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- SETUP ---
DB_FILE = "expenses.csv"
# Locked in your exact absolute path
MODEL_PATH = "/Users/x/Documents/siva_env/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
reader = easyocr.Reader(['en'], gpu=False)

print("Loading Llama 3 Brain...")
llm = LlamaCpp(
    model_path=MODEL_PATH,
    temperature=0.1, # Keep it analytical
    max_tokens=300,
    n_ctx=4096, # Expanded memory window to hold the database text
    verbose=False
)

# --- DATABASE & CHART LOGIC ---
def save_to_db(vendor, date, total, category):
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Vendor", "Date", "Total", "Category"])
        df.to_csv(DB_FILE, index=False)
    
    try:
        clean_total = float(total.replace('$', '').replace(',', '').strip())
    except:
        clean_total = 0.0

    new_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Vendor": vendor,
        "Date": date,
        "Total": clean_total,
        "Category": category
    }
    df = pd.read_csv(DB_FILE)
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def generate_chart():
    if not os.path.exists(DB_FILE):
        return None
    df = pd.read_csv(DB_FILE)
    if df.empty:
        return None
    
    category_totals = df.groupby("Category")["Total"].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    category_totals.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title("Spending Trends by Category")
    ax.set_ylabel("Total Spent ($)")
    ax.set_xlabel("Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

# --- PROMPT TEMPLATES ---
# 1. The Extraction Prompt
extract_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Extract data. Return EXACTLY: Vendor: [Name], Date: [Date], Total: [Amount], Category: [Food/Supplies/Travel/Other]
<|eot_id|><|start_header_id|>user<|end_header_id|>
{raw_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
extract_chain = PromptTemplate.from_template(extract_template) | llm

# 2. The Conversational BI Prompt
chat_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert financial analyst AI. Here is the user's current expense database:

{database_context}

Answer the user's question accurately and concisely based ONLY on the data provided above. Do not invent numbers.
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
chat_chain = PromptTemplate.from_template(chat_template) | llm


# --- APP ROUTING ---
def process_receipt(image):
    results = reader.readtext(image, detail=0)
    raw_string = " ".join(results)
    
    ai_output = extract_chain.invoke({"raw_text": raw_string})
    
    lines = ai_output.strip().split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            data[key.strip()] = val.strip()
            
    save_to_db(data.get("Vendor", "Unknown"), data.get("Date", "Unknown"), 
               data.get("Total", "0"), data.get("Category", "Other"))
    
    return ai_output, generate_chart()

def chat_with_data(message, history):
    # Check if we have data
    if not os.path.exists(DB_FILE):
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⚠️ No data found. Please scan a receipt first!"})
        return "", history
    
    # Load the database and convert it to a clean markdown table
    df = pd.read_csv(DB_FILE)
    context = df.to_markdown(index=False)
    
    # Ask the AI
    bot_response = chat_chain.invoke({
        "database_context": context, 
        "user_query": message
    })
    
    # Update history using the new dictionary format
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": bot_response.strip()})
    
    return "", history

# --- MODERN UI ---
with gr.Blocks() as demo:
    gr.Markdown("# 🧾 SIVA: Enterprise Expense & Data Agent")
    
    with gr.Tabs():
        # TAB 1: Data Entry
        with gr.TabItem("📸 Scan & Extract"):
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(type="numpy", label="Upload Receipt")
                    btn = gr.Button("Analyze & Save", variant="primary")
                with gr.Column():
                    text_out = gr.Textbox(label="AI Extraction", lines=6)
                    plot_out = gr.Plot(label="Live Spending Dashboard")
            btn.click(fn=process_receipt, inputs=img_input, outputs=[text_out, plot_out])
            
        # TAB 2: Data Analytics 
        with gr.TabItem("💬 Chat with Finances"):
            gr.Markdown("### Ask SIVA about your spending trends, totals, or specific vendors.")
            # type parameter completely removed for Gradio 6.0
            chatbot = gr.Chatbot(label="Financial Agent")
            with gr.Row():
                msg = gr.Textbox(label="Type your question here...", placeholder="e.g., How much did I spend on Food this month?", scale=4)
                submit_btn = gr.Button("Ask", scale=1)
            
            # Wire up both the enter key and the submit button
            msg.submit(chat_with_data, [msg, chatbot], [msg, chatbot])
            submit_btn.click(chat_with_data, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    # Theme configuration moved here for Gradio 6.0
    demo.launch(theme=gr.themes.Soft())