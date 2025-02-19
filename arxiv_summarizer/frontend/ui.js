import { useState, useEffect } from 'react';

const App = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/topics')
      .then(res => res.json())
      .then(data => {
        setTopics(data.topics);
        if (data.topics.length > 0) {
          setSelectedTopic(data.topics[0]);
        }
      });
  }, []);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: selectedTopic,
          query: query,
        }),
      });
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">ArXiv RAG Query Interface</h1>
      
      <div className="mb-4">
        <select
          className="border p-2 rounded mr-2"
          value={selectedTopic}
          onChange={(e) => setSelectedTopic(e.target.value)}
        >
          {topics.map(topic => (
            <option key={topic} value={topic}>
              {topic.replace('_', ' ').toUpperCase()}
            </option>
          ))}
        </select>
        
        <input
          type="text"
          className="border p-2 rounded mr-2"
          placeholder="Enter your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={handleQuery}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="space-y-4">
        {results.map((paper) => (
          <div key={paper.paper_id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{paper.title}</h2>
            <p className="text-gray-600 mt-2">{paper.abstract}</p>
            <div className="mt-2 text-blue-600">
              Relevance: {paper.relevance_score}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;