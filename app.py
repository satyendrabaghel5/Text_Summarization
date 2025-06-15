import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import pandas as pd
import base64
from io import StringIO

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Function to generate summary
def generate_summary(text, num_sentences=5, style='plain'):
    if not text:
        return ""
    
    # Tokenize sentences
    sentences = sent_tokenize(text)
    
    # Tokenize words and remove stopwords
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    
    # Calculate word frequencies
    freq_dist = FreqDist(words)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        score = 0
        words_in_sentence = word_tokenize(sentence.lower())
        for word in words_in_sentence:
            if word in freq_dist:
                score += freq_dist[word]
        sentence_scores[sentence] = score
    
    # Sort sentences by score and get top N
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get top sentences (up to num_sentences)
    top_sentences = sorted_sentences[:num_sentences]
    
    # Sort sentences by their original order
    top_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
    
    # Format the output based on style
    if style == 'plain':
        return ' '.join([sentence[0] for sentence in top_sentences])
    elif style == 'bullets':
        return '\n'.join([f"\n• {sentence[0]}" for sentence in top_sentences])
    elif style == 'numbered':
        return '\n'.join([f"\n{i+1}. {sentence[0]}" for i, sentence in enumerate(top_sentences)])

def get_text_stats(text):
    if not text:
        return None
    
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    
    return {
        "Total Sentences": len(sentences),
        "Total Words": len(words),
        "Average Words per Sentence": round(len(words) / len(sentences), 2)
    }

def get_download_link(text, filename="summary.txt"):
    text = text.replace("\n", " ")
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Summary</a>'
    return href

# Streamlit app
def main():
    st.title("Text Summarizer")
    
    # Sidebar
    st.sidebar.header("Settings")
    num_sentences = st.sidebar.text_input("Number of Summary Sentences", "5")
    try:
        num_sentences = int(num_sentences)
    except ValueError:
        num_sentences = 5  # Default value if input is not a valid number
    summary_style = st.sidebar.selectbox("Summary Style", ["plain", "bullets", "numbered"])
    
    # Main content
    st.header("Input Text")
    
    # Text input options
    input_method = st.radio("Input Method", ["Paste Text", "Upload File"])
    
    if input_method == "Paste Text":
        text = st.text_area("Paste your text here", height=300)
    else:
        uploaded_file = st.file_uploader("Choose a text file", type=["txt", "doc", "docx"])
        if uploaded_file is not None:
            text = uploaded_file.read().decode()
        else:
            text = ""
    
    # Generate summary button
    if st.button("Generate Summary"):
        if text:
            # Generate summary
            summary = generate_summary(text, num_sentences, summary_style)
            
            # Display summary
            st.header("Summary")
            if summary_style == "plain":
                st.text_area("", value=summary, height=200)
            else:
                st.markdown(summary)
            
            # Download link
            st.markdown(get_download_link(summary), unsafe_allow_html=True)
            
            # Text statistics
            st.header("Text Statistics")
            stats = get_text_stats(text)
            if stats:
                st.table(pd.DataFrame([stats]))
        else:
            st.error("Please provide some text")

if __name__ == "__main__":
    main()
