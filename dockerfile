FROM ubuntu:latest
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama pull gemma3n
COPY . .
RUN pip install streamlit requests
CMD ollama serve & streamlit run app.py --server.port=8080
