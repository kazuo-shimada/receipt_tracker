SMART INVENTORY VISION AGENT

## Overview
SIVA is a locally hosted application designed to automate financial data entry and analysis. 

For many businesses and individuals, tracking expenses means manually reading receipts and typing numbers into a spreadsheet. SIVA automates this entire workflow. You simply upload a photo of a receipt, and the application reads the text, extracts the relevant financial data, saves it to a database, and generates visual spending charts. 

Additionally, SIVA features a conversational interface, allowing users to ask plain-English questions about their financial data instead of writing complex spreadsheet formulas.

## The Business Value
* **Eliminates Manual Data Entry:** Turns physical receipts into structured digital data instantly.
* **Reduces Human Error:** Replaces manual typing with automated text extraction.
* **Democratizes Data Analysis:** Allows anyone to query their financial database using natural conversation rather than specialized coding or database languages.
* **Privacy First:** The entire system, including the AI, runs locally on the user's machine. No sensitive financial data is ever sent to the cloud.

## Key Features
1. **Automated Receipt Scanning:** Uses optical character recognition to read the raw text off a scanned image or photograph of a receipt.
2. **Intelligent Data Parsing:** Uses a local AI model to filter through the messy scanned text and identify the Vendor Name, Date, Total Amount, and Expense Category.
3. **Persistent Database:** Automatically logs every scanned receipt into a running spreadsheet (CSV file).
4. **Live Visual Dashboard:** Generates an up-to-date bar chart showing spending trends categorized by expense type.
5. **Conversational Financial Agent:** A chat interface that can read the live database and answer direct questions about your spending history (e.g., "How much have I spent on travel this month?").

## How It Works (Under the Hood)
While the user experience is simple, SIVA connects several distinct technologies behind the scenes:
* **The "Eyes":** An Optical Character Recognition (OCR) engine scans the image and turns pixels into raw, unorganized text.
* **The "Brain":** An open-source language model (Llama 3) receives the raw text, understands the context, and formats it into clean data. 
* **The "Memory":** A Python data library (Pandas) handles saving the information to a local file and converting that file into a format the AI can read later.
* **The "Interface":** A web-based framework (Gradio) provides the user-friendly buttons, image uploaders, and chat windows.

## Running the Application
To run SIVA on your local machine, you will need Python installed, along with the required libraries listed in the setup files. 

1. Clone this repository to your local machine.
2. Install the required dependencies (EasyOCR, Gradio, Pandas, Matplotlib, and LangChain).
3. Download a compatible local LLM (such as Llama 3) and update the file path in the main script.
4. Run the main Python script to launch the local web interface.
