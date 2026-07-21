'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Sparkles, ArrowRight, Brain, Zap, Shield } from 'lucide-react';
import { api } from '@/lib/api';

const SUGGESTED_GOALS = [
  "Investigate whether microservices or monolith is better for a 10-person startup",
  "Analyze the impact of quantum computing on modern cryptography",
  "Design a highly available architecture for a global chat application"
];

export default function Home() {
  const [goal, setGoal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!goal.trim()) return;
    
    setIsSubmitting(true);
    setError(null);
    try {
      const createdGoal = await api.createGoal({
        user_input: goal,
        domain_hint: "General Investigation",
        constraints: {},
        document_ids: []
      });
      const execution = await api.startExecution(createdGoal.id);
      router.push(`/execution/${execution.id}`);
    } catch (err: any) {
      console.error("Failed to start investigation:", err);
      setError(err.message || "Could not connect to Chethas backend API on localhost:8000.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen hero-bg flex flex-col items-center justify-center p-6 sm:p-12 overflow-hidden">
      
      <div className="z-10 w-full max-w-4xl flex flex-col items-center space-y-12 animate-slide-up">
        
        <div className="text-center space-y-6">
          <Badge variant="purple" pulse className="mb-4">
            <Sparkles className="w-3.5 h-3.5 mr-1.5" />
            Chethas Engine v1.0 Ready
          </Badge>
          
          <h1 className="text-5xl sm:text-7xl font-black tracking-tight leading-tight">
            Define your goal.<br/>
            <span className="gradient-text">Let intelligence unfold.</span>
          </h1>
          
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm max-w-md mx-auto">
              {error}
            </div>
          )}
          
          <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto">
            Experience research-grade autonomous multi-agent intelligence. Chethas reasons, debates, and delivers evidence-backed solutions.
          </p>
        </div>

        <Card className="w-full p-2 bg-white/5 border-white/10 shadow-2xl relative overflow-visible group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
          
          <form onSubmit={handleSubmit} className="relative bg-[#12121a] rounded-lg p-2 flex flex-col sm:flex-row items-end sm:items-center gap-4">
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Describe your goal... e.g., Analyze the latest trends in autonomous AI agents."
              className="w-full bg-transparent border-none text-white placeholder-slate-500 resize-none p-4 min-h-[80px] focus:outline-none focus:ring-0 text-lg leading-relaxed"
              rows={2}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            
            <div className="p-2 w-full sm:w-auto">
              <Button 
                type="submit" 
                size="lg" 
                className="w-full sm:w-auto font-semibold px-8 py-6 rounded-lg text-base shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                disabled={!goal.trim() || isSubmitting}
                isLoading={isSubmitting}
              >
                {!isSubmitting && (
                  <>
                    Launch
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>

        <div className="w-full animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <p className="text-sm font-medium text-slate-400 mb-4 text-center sm:text-left">Suggested Goals</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {SUGGESTED_GOALS.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => setGoal(suggestion)}
                className="text-left p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 transition-all text-sm text-slate-300 hover:text-white"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-12 border-t border-white/5 w-full animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-2">
              <Brain className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-slate-200">Deep Reasoning</h3>
            <p className="text-sm text-slate-400">Multi-step deliberation using advanced graph-based workflows.</p>
          </div>
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-2">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-slate-200">Autonomous Action</h3>
            <p className="text-sm text-slate-400">Self-correcting agents that dynamically navigate complex tasks.</p>
          </div>
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-2">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-slate-200">Evidence Backed</h3>
            <p className="text-sm text-slate-400">Rigorous citation and evaluation for trustworthy conclusions.</p>
          </div>
        </div>

      </div>
    </div>
  );
}
