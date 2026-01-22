import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Send,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  Cpu,
  DollarSign,
  Calculator,
  User,
  Wrench,
  Sparkles,
  RotateCcw,
  Zap
} from 'lucide-react';
import './index.css';

// Types
interface ModelInfo {
  name: string;
  domain: string;
  color: string;
  description: string;
  priority?: number;
}

interface ModelResponse {
  model: string;
  domain: string;
  color: string;
  description: string;
  response: string | null;
  error: string | null;
  duration_ms: number;
  status: 'success' | 'error' | 'timeout' | 'pending';
}

interface QueryResponse {
  prompt: string;
  total_duration_ms: number;
  models_queried: number;
  models_succeeded: number;
  responses: ModelResponse[];
}

// Model definitions matching backend
const MODELS: Record<string, ModelInfo> = {
  "unified-systems-architect": {
    name: "unified-systems-architect",
    domain: "meta",
    color: "#f97316",
    description: "Meta-expert synthesizing all domains",
    priority: 1
  },
  "llm-orchestration-ontology": {
    name: "llm-orchestration-ontology",
    domain: "technical",
    color: "#3b82f6",
    description: "LLM orchestration patterns, multi-agent systems"
  },
  "prompt-engineering-expert": {
    name: "prompt-engineering-expert",
    domain: "technical",
    color: "#3b82f6",
    description: "Prompting techniques, debugging, optimization"
  },
  "kg-traversal-expert": {
    name: "kg-traversal-expert",
    domain: "technical",
    color: "#3b82f6",
    description: "Knowledge graph algorithms, SPARQL, Cypher"
  },
  "app-architecture-expert": {
    name: "app-architecture-expert",
    domain: "technical",
    color: "#3b82f6",
    description: "Web architecture patterns, SSR, SPA, microservices"
  },
  "performance-percentiles-expert": {
    name: "performance-percentiles-expert",
    domain: "technical",
    color: "#3b82f6",
    description: "p50/p95/p99 metrics, SLOs, error budgets"
  },
  "wealth-mindset": {
    name: "wealth-mindset",
    domain: "wealth",
    color: "#22c55e",
    description: "Wealth thinking, leverage, ownership mindset"
  },
  "passive-income-expert": {
    name: "passive-income-expert",
    domain: "wealth",
    color: "#22c55e",
    description: "Passive income streams, investment strategies"
  },
  "real-estate-investor": {
    name: "real-estate-investor",
    domain: "wealth",
    color: "#22c55e",
    description: "Real estate strategies, BRRRR, financing"
  },
  "deal-structuring-expert": {
    name: "deal-structuring-expert",
    domain: "wealth",
    color: "#22c55e",
    description: "M&A, acquisitions, deal financing"
  },
  "business-tax-2026": {
    name: "business-tax-2026",
    domain: "tax",
    color: "#a855f7",
    description: "2026 tax laws, OBBBA provisions, compliance"
  },
  "cpa-wealth-advisor": {
    name: "cpa-wealth-advisor",
    domain: "tax",
    color: "#a855f7",
    description: "Business owner tax optimization, retirement"
  },
  "homeowner-tax-strategies": {
    name: "homeowner-tax-strategies",
    domain: "tax",
    color: "#a855f7",
    description: "Homeowner deductions, 1031 exchanges, depreciation"
  },
  "ngo-corporate-structures": {
    name: "ngo-corporate-structures",
    domain: "tax",
    color: "#a855f7",
    description: "Nonprofit structures, 501c3/c4, beneficial ownership"
  },
  "skill-stack-expert": {
    name: "skill-stack-expert",
    domain: "personal",
    color: "#ec4899",
    description: "8 power skill stacks for career acceleration"
  },
  "skill-stacker": {
    name: "skill-stacker",
    domain: "personal",
    color: "#ec4899",
    description: "Skill development strategy, rare combinations"
  },
  "productivity-systems-expert": {
    name: "productivity-systems-expert",
    domain: "personal",
    color: "#ec4899",
    description: "Time management, focus systems, GTD"
  },
  "world-model-expert": {
    name: "world-model-expert",
    domain: "personal",
    color: "#ec4899",
    description: "Mental models, systems thinking, Bayesian reasoning"
  },
  "english-to-spanish": {
    name: "english-to-spanish",
    domain: "utility",
    color: "#64748b",
    description: "English to Spanish translation"
  }
};

const DOMAINS = {
  meta: { label: "Meta", color: "#f97316", icon: Sparkles },
  technical: { label: "Technical", color: "#3b82f6", icon: Cpu },
  wealth: { label: "Wealth", color: "#22c55e", icon: DollarSign },
  tax: { label: "Tax/Legal", color: "#a855f7", icon: Calculator },
  personal: { label: "Personal", color: "#ec4899", icon: User },
  utility: { label: "Utility", color: "#64748b", icon: Wrench }
};

const API_BASE = 'http://localhost:8765';

// Example prompts
const EXAMPLE_PROMPTS = [
  "I want to start a SaaS business while keeping my day job. How should I structure this for optimal tax treatment, skill development, and eventual exit?",
  "Compare the trade-offs between building a rental property portfolio vs building a digital product business for passive income.",
  "How do I evaluate whether to take a higher-paying job vs starting my own consulting practice?",
  "Design a system architecture for a high-traffic e-commerce platform with p99 latency under 200ms."
];

function App() {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set(Object.keys(MODELS)));
  const [responses, setResponses] = useState<ModelResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [queryStats, setQueryStats] = useState<{ total_duration_ms: number; models_succeeded: number; models_queried: number } | null>(null);
  const [expandedResponses, setExpandedResponses] = useState<Set<string>>(new Set());
  const [selectedDomains, setSelectedDomains] = useState<Set<string>>(new Set(Object.keys(DOMAINS)));

  const toggleModel = useCallback((modelName: string) => {
    setSelectedModels(prev => {
      const next = new Set(prev);
      if (next.has(modelName)) {
        next.delete(modelName);
      } else {
        next.add(modelName);
      }
      return next;
    });
  }, []);

  const toggleDomain = useCallback((domain: string) => {
    setSelectedDomains(prev => {
      const next = new Set(prev);
      if (next.has(domain)) {
        next.delete(domain);
        // Remove all models from this domain
        Object.entries(MODELS).forEach(([name, info]) => {
          if (info.domain === domain) {
            setSelectedModels(sm => {
              const n = new Set(sm);
              n.delete(name);
              return n;
            });
          }
        });
      } else {
        next.add(domain);
        // Add all models from this domain
        Object.entries(MODELS).forEach(([name, info]) => {
          if (info.domain === domain) {
            setSelectedModels(sm => {
              const n = new Set(sm);
              n.add(name);
              return n;
            });
          }
        });
      }
      return next;
    });
  }, []);

  const selectAll = useCallback(() => {
    setSelectedModels(new Set(Object.keys(MODELS)));
    setSelectedDomains(new Set(Object.keys(DOMAINS)));
  }, []);

  const selectNone = useCallback(() => {
    setSelectedModels(new Set());
    setSelectedDomains(new Set());
  }, []);

  const toggleResponseExpanded = useCallback((modelName: string) => {
    setExpandedResponses(prev => {
      const next = new Set(prev);
      if (next.has(modelName)) {
        next.delete(modelName);
      } else {
        next.add(modelName);
      }
      return next;
    });
  }, []);

  const handleQuery = async () => {
    if (!prompt.trim() || selectedModels.size === 0) return;

    setIsLoading(true);
    setResponses([]);
    setQueryStats(null);
    setExpandedResponses(new Set());

    // Set initial pending states
    const pendingResponses: ModelResponse[] = Array.from(selectedModels).map(name => ({
      model: name,
      domain: MODELS[name].domain,
      color: MODELS[name].color,
      description: MODELS[name].description,
      response: null,
      error: null,
      duration_ms: 0,
      status: 'pending'
    }));
    setResponses(pendingResponses);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.trim(),
          models: Array.from(selectedModels),
          timeout: 180
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: QueryResponse = await response.json();
      setResponses(data.responses);
      setQueryStats({
        total_duration_ms: data.total_duration_ms,
        models_succeeded: data.models_succeeded,
        models_queried: data.models_queried
      });
      // Auto-expand successful responses
      setExpandedResponses(new Set(data.responses.filter(r => r.status === 'success').map(r => r.model)));
    } catch (error) {
      console.error('Query error:', error);
      setResponses(pendingResponses.map(r => ({
        ...r,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      })));
    } finally {
      setIsLoading(false);
    }
  };

  const getDomainIcon = (domain: string) => {
    const Icon = DOMAINS[domain as keyof typeof DOMAINS]?.icon || Brain;
    return Icon;
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Systems Architect Console</h1>
              <p className="text-sm text-slate-400">Multi-model holistic analysis across 19 specialized domains</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Query Input Section */}
        <div className="card mb-8">
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Your Question or Scenario
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your situation or question for multi-perspective analysis..."
              className="input-field min-h-[120px] resize-y"
              disabled={isLoading}
            />
          </div>

          {/* Example Prompts */}
          <div className="mb-6">
            <p className="text-xs text-slate-500 mb-2">Try an example:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((ex, i) => (
                <button
                  key={i}
                  onClick={() => setPrompt(ex)}
                  className="text-xs px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 rounded-full text-slate-300 transition-colors truncate max-w-xs"
                  disabled={isLoading}
                >
                  {ex.slice(0, 60)}...
                </button>
              ))}
            </div>
          </div>

          {/* Domain Selection */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Select Domains</label>
              <div className="flex gap-2">
                <button onClick={selectAll} className="text-xs text-primary-400 hover:text-primary-300">Select All</button>
                <span className="text-slate-600">|</span>
                <button onClick={selectNone} className="text-xs text-slate-400 hover:text-slate-300">Clear</button>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(DOMAINS).map(([key, domain]) => {
                const Icon = domain.icon;
                const isSelected = selectedDomains.has(key);
                const modelCount = Object.values(MODELS).filter(m => m.domain === key).length;
                const selectedCount = Object.entries(MODELS).filter(([name, m]) => m.domain === key && selectedModels.has(name)).length;

                return (
                  <button
                    key={key}
                    onClick={() => toggleDomain(key)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      isSelected
                        ? 'text-white shadow-lg'
                        : 'bg-slate-700/50 text-slate-400 hover:bg-slate-600/50'
                    }`}
                    style={isSelected ? { backgroundColor: domain.color } : undefined}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{domain.label}</span>
                    <span className={`text-xs ${isSelected ? 'text-white/70' : 'text-slate-500'}`}>
                      {selectedCount}/{modelCount}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Model Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Models ({selectedModels.size} selected)
            </label>
            <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 bg-slate-900/50 rounded-lg">
              {Object.entries(MODELS).map(([name, info]) => (
                <button
                  key={name}
                  onClick={() => toggleModel(name)}
                  className={`model-chip flex items-center gap-1.5 ${
                    selectedModels.has(name) ? 'model-chip-active' : 'model-chip-inactive'
                  }`}
                  style={selectedModels.has(name) ? { backgroundColor: info.color } : undefined}
                  title={info.description}
                >
                  {info.priority === 1 && <Zap className="w-3 h-3" />}
                  {name.replace(/-/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleQuery}
            disabled={isLoading || !prompt.trim() || selectedModels.size === 0}
            className="btn-primary w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Querying {selectedModels.size} models...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Analyze with {selectedModels.size} Models
              </>
            )}
          </button>
        </div>

        {/* Results Stats */}
        {queryStats && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-slate-800/50 rounded-xl border border-slate-700"
          >
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">Total: {formatDuration(queryStats.total_duration_ms)}</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-slate-300">{queryStats.models_succeeded}/{queryStats.models_queried} succeeded</span>
            </div>
            <button
              onClick={() => {
                setResponses([]);
                setQueryStats(null);
              }}
              className="ml-auto flex items-center gap-1 text-sm text-slate-400 hover:text-slate-300"
            >
              <RotateCcw className="w-4 h-4" />
              Clear Results
            </button>
          </motion.div>
        )}

        {/* Responses Grid */}
        <AnimatePresence>
          {responses.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {responses.map((resp, index) => {
                const Icon = getDomainIcon(resp.domain);
                const isExpanded = expandedResponses.has(resp.model);

                return (
                  <motion.div
                    key={resp.model}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`response-card ${resp.status === 'pending' ? 'response-card-loading' : ''}`}
                  >
                    {/* Header */}
                    <div
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => resp.status === 'success' && toggleResponseExpanded(resp.model)}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: `${resp.color}20` }}
                        >
                          <Icon className="w-5 h-5" style={{ color: resp.color }} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-white flex items-center gap-2">
                            {resp.model.replace(/-/g, ' ')}
                            {MODELS[resp.model]?.priority === 1 && (
                              <span className="text-xs bg-secondary-500/20 text-secondary-400 px-2 py-0.5 rounded">META</span>
                            )}
                          </h3>
                          <p className="text-xs text-slate-400">{resp.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {resp.status === 'pending' && (
                          <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                        )}
                        {resp.status === 'success' && (
                          <>
                            <span className="text-xs text-slate-500">{formatDuration(resp.duration_ms)}</span>
                            <CheckCircle className="w-5 h-5 text-green-400" />
                            {isExpanded ? (
                              <ChevronUp className="w-5 h-5 text-slate-400" />
                            ) : (
                              <ChevronDown className="w-5 h-5 text-slate-400" />
                            )}
                          </>
                        )}
                        {resp.status === 'error' && (
                          <XCircle className="w-5 h-5 text-red-400" />
                        )}
                        {resp.status === 'timeout' && (
                          <Clock className="w-5 h-5 text-yellow-400" />
                        )}
                      </div>
                    </div>

                    {/* Content */}
                    <AnimatePresence>
                      {isExpanded && resp.response && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="mt-4 pt-4 border-t border-slate-700">
                            <div className="prose-response whitespace-pre-wrap">
                              {resp.response}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Error Message */}
                    {resp.error && (
                      <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-sm text-red-400">{resp.error}</p>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {responses.length === 0 && !isLoading && (
          <div className="text-center py-16">
            <Brain className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-400 mb-2">Ready for Multi-Perspective Analysis</h3>
            <p className="text-slate-500 max-w-md mx-auto">
              Enter your question above and select which expert models to consult.
              Each model brings specialized knowledge from its domain.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>Systems Architect Console - Powered by 19 Ollama Models</p>
          <p className="text-xs mt-1">Technical | Wealth | Tax/Legal | Personal Development | Meta-Synthesis</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
