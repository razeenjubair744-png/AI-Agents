import React, { useState, useRef, useEffect } from 'react';
import { Search, Brain, Loader2, ChevronDown, ChevronUp, FileText, Sparkles } from 'lucide-react';

const App = () => {
  const [topic, setTopic] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [agentThoughts, setAgentThoughts] = useState([]);
  const [finalReport, setFinalReport] = useState('');
  const [expandedThoughts, setExpandedThoughts] = useState(true);
  const thoughtsEndRef = useRef(null);

  const scrollToBottom = () => {
    thoughtsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [agentThoughts]);

  const handleSubmit = async () => {
    if (!topic.trim() || isResearching) return;

    setIsResearching(true);
    setAgentThoughts([]);
    setFinalReport('');

    try {
      const response = await fetch('http://localhost:8000/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: topic.trim() }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'thought') {
                setAgentThoughts(prev => [...prev, {
                  id: Date.now() + Math.random(),
                  text: data.content,
                  timestamp: new Date().toLocaleTimeString()
                }]);
              } else if (data.type === 'report') {
                setFinalReport(prev => prev + data.content);
              } else if (data.type === 'complete') {
                setIsResearching(false);
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Research error:', error);
      setAgentThoughts(prev => [...prev, {
        id: Date.now(),
        text: `❌ Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
      setIsResearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Brain className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Deep Research Agent</h1>
              <p className="text-sm text-purple-300">Powered by LangGraph & Agentic Design Patterns</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Input */}
        <div className="mb-8">
          <div className="relative">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything... (e.g., Analyze the impact of solid-state batteries on the EV market in 2025)"
              disabled={isResearching}
              className="w-full px-6 py-4 pr-14 bg-slate-800/50 border-2 border-purple-500/30 rounded-2xl text-white placeholder-slate-400 focus:outline-none focus:border-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            />
            <button
              onClick={handleSubmit}
              disabled={isResearching || !topic.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-xl transition-all"
            >
              {isResearching ? (
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              ) : (
                <Search className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>

        {/* Split View */}
        {(agentThoughts.length > 0 || finalReport) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Panel: Agent Thoughts */}
            <div className="bg-slate-800/50 border border-purple-500/20 rounded-2xl overflow-hidden">
              <div
                className="flex items-center justify-between p-4 bg-slate-800/80 border-b border-purple-500/20 cursor-pointer hover:bg-slate-800 transition-all"
                onClick={() => setExpandedThoughts(!expandedThoughts)}
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  <h2 className="text-lg font-semibold text-white">Agent Thoughts</h2>
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full">
                    {agentThoughts.length}
                  </span>
                </div>
                {expandedThoughts ? (
                  <ChevronUp className="w-5 h-5 text-purple-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-purple-400" />
                )}
              </div>

              {expandedThoughts && (
                <div className="p-4 max-h-[600px] overflow-y-auto">
                  {agentThoughts.map((thought) => (
                    <div
                      key={thought.id}
                      className="mb-3 p-3 bg-slate-900/50 border border-purple-500/10 rounded-lg"
                    >
                      <div className="flex items-start gap-2">
                        <div className="text-2xl">{thought.text.match(/^[🔍🧠📝✅❌]/)?.[0] || '💭'}</div>
                        <div className="flex-1">
                          <p className="text-slate-300 text-sm">{thought.text.replace(/^[🔍🧠📝✅❌]\s*/, '')}</p>
                          <span className="text-xs text-slate-500 mt-1 block">{thought.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={thoughtsEndRef} />
                </div>
              )}
            </div>

            {/* Right Panel: Research Report */}
            <div className="bg-slate-800/50 border border-purple-500/20 rounded-2xl overflow-hidden">
              <div className="flex items-center gap-2 p-4 bg-slate-800/80 border-b border-purple-500/20">
                <FileText className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Research Report</h2>
              </div>

              <div className="p-6 max-h-[600px] overflow-y-auto prose prose-invert prose-purple max-w-none">
                {finalReport ? (
                  <div className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                    {finalReport.split('\n').map((line, i) => {
                      if (line.startsWith('# ')) {
                        return <h1 key={i} className="text-2xl font-bold text-white mt-4 mb-2">{line.slice(2)}</h1>;
                      } else if (line.startsWith('## ')) {
                        return <h2 key={i} className="text-xl font-bold text-purple-300 mt-3 mb-2">{line.slice(3)}</h2>;
                      } else if (line.startsWith('### ')) {
                        return <h3 key={i} className="text-lg font-semibold text-purple-400 mt-2 mb-1">{line.slice(4)}</h3>;
                      } else if (line.startsWith('- ')) {
                        return <li key={i} className="ml-4 text-slate-300">{line.slice(2)}</li>;
                      } else if (line.trim()) {
                        return <p key={i} className="mb-2 text-slate-300">{line}</p>;
                      }
                      return <br key={i} />;
                    })}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                      <Loader2 className="w-8 h-8 text-purple-400 animate-spin mx-auto mb-2" />
                      <p className="text-slate-400">Generating report...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {agentThoughts.length === 0 && !finalReport && (
          <div className="text-center py-16">
            <div className="inline-block p-4 bg-purple-500/10 rounded-2xl mb-4">
              <Brain className="w-16 h-16 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Ready to Research</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              Enter a research topic and watch the AI agent plan, search, and synthesize information in real-time.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;