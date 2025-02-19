pip install fastapi uvicorn arxiv-python PyPDF2 ollama tqdm pydantic

npm create vite@latest frontend -- --template react
cd frontend
npm install

uvicorn backend.api.routes:app --reload

cd frontend
npm run dev