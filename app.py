import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from hyperon.ext import register_atoms
from hyperon.atoms import OperationAtom
from hyperon import MeTTa
import os

app = Flask(__name__)
CORS(app)  # Allow frontend requests from localhost:3000

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def AskGemini(question: str):
    print("in AskGemini question is -->", question, "\n")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(question)
    except Exception as e:
        return f"An error occurred: {e}"

def getCorrectNaming(InputTerm):
    print("\n in getCorrectNaming\n ")
    prompt = f"""
    You are given a biological term. If the term appears to refer to a chromosome (even if it includes typos), 
    extract the chromosome number or letter and return it in the format 'chrN'(where N is a natural number). 
    If it clearly doesn't refer to a chromosome, respond with 'INCORRECT'.

    Input: {InputTerm}

    Output: """
    return AskGemini(prompt)

def AskMettaAboutAll(raw_information):
    print("AskMettaAboutAll is called\n")
    def write(information):
        try:
            with open('./Summarized-Notes.txt', 'a') as file:
                file.write(information + "\n\n")
                print("Successfully appended to Summarized-Notes.txt\n")
        except IOError as e:
            print(f"An error occurred: {e}\n")

    prompt = f"""You are a genomics expert.
        I will give you structured data for multiple human genes in a symbolic format.
        For each gene, use all the data provided (ID, name, type, chromosome, coordinates, synonyms, etc.) to generate a clear, informative summary in human-friendly language.

        The summary should explain:

        What gene it is and where it's located (chromosome, start-end position)

        That it is protein-coding (if stated)

        Any relevant insight from the name or synonyms (e.g. involvement in 14-3-3 protein family, or known biological roles, diseases, etc.)

        Do not just re-list the data. Use natural language and full sentences.
        Separate each gene's summary with a blank line.

        Here is the data: {raw_information}
        """

    information = AskGemini(prompt).text
    write(information)
    return []

@register_atoms(pass_metta=True)
def Summarizer_for_all(metta):
    TheSummarizer = OperationAtom(
        "Summarize_and_write",
        lambda raw_information: AskMettaAboutAll(str(raw_information)),
        ["Atom", "Atom"],
        unwrap=False
    )
    return {r"Summarize_and_write": TheSummarizer}

def AskMetta(ChromosomeName):
    print("\n in AskMetta\n ")
    metta = MeTTa()
    correctName = getCorrectNaming(ChromosomeName).text.strip()
    print("corrected name is ", correctName)

    if correctName.upper() == "INCORRECT":
        return "INCORRECT"

    prompt = """
        You are a biomedical expert AI. Given the following structured gene data, write a clear, 
        concise human-readable summary about the gene. Include the gene name, aliases (synonyms), 
        chromosome location, and gene type. Explain everything in plain language but retain scientific accuracy.
        Avoid raw data formats — aim for clarity and flow.

        here is the input data: 
        """

    FetchedData = metta.run(f"""
        !(register-module! ../Training_1)
        !(import! &self Training_1:data)
        !(match &self (chr $geneCode {correctName}) (match &self ($front $geneCode $last) ($front $geneCode $last)))
    """)

    print(FetchedData[-1], " <---- fetched")

    summary_text = AskGemini(prompt + "\n".join(map(str, FetchedData[-1]))).text
    ans = [correctName, summary_text]
    print("the answer passed here is ---------->>>>>>>--------", ans)
    return ans

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    term = data.get("term", "")
    Answer = AskMetta(term)

    if Answer == "INCORRECT":
        return jsonify({"chromosome": "INCORRECT", "summary": "Not a valid chromosome name."})

    return jsonify({
        "chromosome": Answer[0],
        "summary": Answer[1]
    })

@app.route("/save", methods=["POST"])
def save_summary():
    data = request.get_json()
    chromosome = data.get("chromosome", "unknown")
    summary = data.get("summary", "")

    try:
        with open("Summarized-Notes.txt", "a") as f:
            f.write(f"Chromosome: {chromosome}\n{summary}\n\n")
        return jsonify({"message": "Saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
