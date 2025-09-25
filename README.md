# Paul Graham AI Assistant

A RAG-powered chatbot that answers questions using Paul Graham's essays with his characteristic voice and style.

## Features

- **RAG Architecture**: Retrieval-Augmented Generation using Paul Graham's complete essay collection
- **Paul Graham's Voice**: Responses in his distinctive writing style with characteristic pauses in TTS
- **Source Citations**: All answers include citations to relevant essays
- **Question Validation**: Filters questions to topics within Paul Graham's expertise
- **Audio Generation**: Text-to-speech with configurable "hmm" pauses (0-5 scale)

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials for Vertex AI
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### 2. First-time Setup (Offline Indexing)

Before using the chatbot, you need to process Paul Graham's essays and create a searchable index:

```bash
python main.py --mode offline
```

This will:

- Load essay metadata from `meta.csv`
- Process all text files in the `data/` directory
- Break essays into contextual chunks
- Generate vector embeddings using Google's text-embedding-005
- Save a searchable vector index to `vector_index.pkl`

### 3. Chat with Paul Graham

#### Single Question Mode

```bash
python main.py --mode online
```

#### Continuous Chat Mode (Recommended)

```bash
python main.py --mode continuous
```

This starts an interactive chat session where you can ask multiple questions.

#### With Custom TTS Pause Scale

```bash
python main.py --mode continuous --pause-scale 3
```

Pause scales:

- `0`: No pauses
- `1`: Light pauses (every 3rd sentence)
- `2`: Moderate pauses (default)
- `3`: Regular pauses (most sentences)
- `4`: Frequent pauses (all sentences)
- `5`: Maximum pauses (multiple "hmm"s)

## Example Usage

```
🤖 Paul Graham AI Assistant
==================================================
💬 Starting continuous Paul Graham AI Assistant...
Type 'quit' or 'exit' to stop.

✅ Vector index loaded successfully!

----------------------------------------

🤔 Ask Paul Graham: How do I get good startup ideas?

💡 Paul Graham says:
The best way to get startup ideas is to notice problems, particularly ones you have yourself. Don't try to think of startup ideas directly. Instead, live at the leading edge of some technology and build things you wish existed.

Sources:
• How to Get Startup Ideas (relevance: 0.89)
• The Origin of "Yes We Can" (relevance: 0.78)
• Do Things that Don't Scale (relevance: 0.73)
```

## Project Structure

```
pocket-graham/
├── main.py              # Entry point with CLI interface
├── nodes.py             # All PocketFlow nodes (offline & online)
├── flow.py              # Flow definitions
├── requirements.txt     # Python dependencies
├── meta.csv            # Essay metadata (titles, URLs)
├── data/               # Paul Graham's essays (354 text files)
│   ├── 1.txt
│   ├── 2.txt
│   └── ...
├── utils/              # Utility functions
│   ├── call_llm.py     # LLM wrapper (Vertex AI Claude)
│   ├── get_embedding.py # Text embedding (Google text-embedding-005)
│   ├── load_meta.py    # CSV metadata loader
│   ├── file_loader.py  # Essay file processor
│   ├── chunking.py     # Text chunking with overlap
│   ├── vector_db.py    # Simple vector database
│   ├── validate_relevance.py # Question relevance checker
│   ├── pause_processor.py # TTS pause enhancement
│   └── tts.py          # Text-to-speech (Google CHIRP3)
└── docs/
    └── design.md       # Complete system design document
```

## Design Patterns

This implementation demonstrates several PocketFlow design patterns:

- **RAG (Retrieval-Augmented Generation)**: Two-stage offline/online pipeline
- **Workflow**: Sequential processing with multiple specialized nodes
- **BatchNode**: Efficient processing of multiple essays/chunks
- **Agent-like Validation**: Dynamic routing based on question relevance

## Architecture

### Offline Flow (One-time Setup)

1. **LoadMetaNode**: Read essay metadata from CSV
2. **LoadEssaysNode**: Load essay files (BatchNode)
3. **ChunkEssaysNode**: Break into chunks with citations (BatchNode)
4. **EmbedChunksNode**: Generate embeddings (BatchNode)
5. **StoreIndexNode**: Save vector index to disk

### Online Flow (Real-time Q&A)

1. **LoadIndexNode**: Load pre-built vector index
2. **InputQuestionNode**: Get user question
3. **ValidateRelevanceNode**: Check topic relevance → branch
4. **EmbedQueryNode**: Convert question to embedding
5. **RetrieveChunksNode**: Find top-5 relevant chunks
6. **GenerateAnswerNode**: Create Paul Graham-style response
7. **FormatResponseNode**: Add citations and formatting
8. **GenerateAudioNode**: Create TTS with pauses

## Customization

### Modify Response Style

Edit the prompt template in `GenerateAnswerNode.exec()` to adjust Paul Graham's voice characteristics.

### Change Chunk Size

Modify `chunk_size` and `chunk_overlap` in the shared store configuration.

### Add New Essays

1. Add new `.txt` files to the `data/` directory
2. Update `meta.csv` with metadata
3. Re-run offline indexing: `python main.py --mode offline`

### Switch LLM Providers

Modify `utils/call_llm.py` to use different LLM providers (OpenAI, Anthropic, etc.).

## Troubleshooting

### "Vector index not found"

Run offline indexing first: `python main.py --mode offline`

### "File not found" errors

Ensure all essay files (1.txt through 354.txt) are in the `data/` directory.

### Google Cloud authentication errors

Set up proper credentials:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Audio generation is slow

Comment out the `generate_audio` calls in the continuous chat loop if you only need text responses.

## Contributing

This project follows the PocketFlow agentic coding principles:

1. **Human Design** → AI Implementation
2. **Simple, composable nodes**
3. **Clear separation of concerns**
4. **Comprehensive design documentation**

See `docs/design.md` for the complete system design.
