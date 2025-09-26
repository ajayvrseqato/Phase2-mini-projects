import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadFile = async () => {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/api/transcribe", fd, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(res.data);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">Meeting Notes Extractor</h1>

      <input 
        type="file" 
        accept="audio/*" 
        onChange={e => setFile(e.target.files[0])} 
        className="border p-2"
      />
      <button 
        onClick={uploadFile} 
        disabled={!file || loading} 
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Processing..." : "Upload"}
      </button>

      {result && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Meeting Summary</h2>
          <pre className="bg-gray-100 p-4 rounded">{result.meeting_summary}</pre>

          <h2 className="text-xl font-semibold mt-4 mb-2">Action Items</h2>
          <pre className="bg-gray-100 p-4 rounded">
            {JSON.stringify(result.action_items, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
