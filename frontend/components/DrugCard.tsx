"use client";
import React, { useState } from 'react';
import { Network, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { DrugCandidate, explainMechanism } from '../lib/api';

export default function DrugCard({ candidate, diseaseName }: { candidate: DrugCandidate, diseaseName: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExplain = async () => {
    setIsExpanded(!isExpanded);
    if (!explanation && !isExpanded) {
      setLoading(true);
      try {
        const text = await explainMechanism(candidate.name, diseaseName, candidate.shared_genes);
        setExplanation(text);
      } catch (err) {
        setError("Failed to load explanation.");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="drug-card">
      <div className="card-header">
        <div className="drug-name">
          <Network size={20} />
          {candidate.name}
        </div>
        <div className="drug-score">
          Score: {candidate.score.toFixed(2)}
        </div>
      </div>
      
      <div className="genes-list">
        {candidate.shared_genes.slice(0, 5).map(g => (
          <span key={g} className="gene-tag">{g}</span>
        ))}
        {candidate.shared_genes.length > 5 && (
          <span className="gene-tag">+{candidate.shared_genes.length - 5} more</span>
        )}
      </div>
      
      <button className="explain-btn" onClick={handleExplain}>
        <Sparkles size={16} /> 
        AI Mechanism Analysis
        {isExpanded ? <ChevronUp size={16} style={{ marginLeft: "auto" }}/> : <ChevronDown size={16} style={{ marginLeft: "auto" }}/>}
      </button>

      {isExpanded && (
        <div className="explanation-box">
          {loading && <div className="flex-center"><div className="spinner"></div></div>}
          {error && <div className="error-msg">{error}</div>}
          {explanation && <p>{explanation}</p>}
        </div>
      )}
    </div>
  );
}
