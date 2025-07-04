import OpenAI from 'openai';
import * as dotenv from 'dotenv';

dotenv.config();

const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';

/* ------------------------------------------------------------------ */
/*  OpenAI client (injectable for tests)                              */
/* ------------------------------------------------------------------ */
let openai: any = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

export function setOpenAIClient(client: any) {
  openai = client;
}

/* ------------------------------------------------------------------ */
/*  Memory utilities                                                  */
/* ------------------------------------------------------------------ */
export interface Memory {
  energyLevel?: 'low' | 'medium' | 'high';
  mood?: string;
  goals?: string[];
  avoidances?: string[];
  intent?: string;
  priority?: 'low' | 'med' | 'high';
  deadline?: string | null;
  durationMinutes?: number | null;
  nextAction?: string;
}

const MEMORY = new Map<string, Memory>();

export function updateMemory(userId: string, updates: Partial<Memory>) {
  /* Clearing memory when an empty object is passed (used by tests) */
  if (Object.keys(updates).length === 0) {
    MEMORY.set(userId, {});
    return;
  }

  const current = MEMORY.get(userId) || {};

  /* Smart-merge arrays with de-duplication */
  if (updates.goals) {
    current.goals = Array.from(new Set([...(current.goals || []), ...updates.goals]));
  }
  if (updates.avoidances) {
    current.avoidances = Array.from(new Set([...(current.avoidances || []), ...updates.avoidances]));
  }

  /* Overwrite / add all other scalar fields */
  for (const [k, v] of Object.entries(updates)) {
    if (v !== undefined && v !== null && k !== 'goals' && k !== 'avoidances') {
      // @ts-ignore – dynamic assignment
      current[k] = v;
    }
  }

  MEMORY.set(userId, current);
}

/* ------------------------------------------------------------------ */
/*  Helper functions                                                  */
/* ------------------------------------------------------------------ */
function missingField(mem: Memory): keyof Memory | null {
  const order: (keyof Memory)[] = [
    'intent',
    'goals',
    'priority',
    'energyLevel',
    'mood',
    'avoidances'
  ];
  for (const field of order) {
    const val = mem[field];
    if (val === undefined || val === null || (Array.isArray(val) && val.length === 0)) {
      return field;
    }
  }
  return null;
}

function followupQuestion(field: keyof Memory): string {
  switch (field) {
    case 'intent':
      return 'What do you want to do next?';
    case 'goals':
      return 'What goals are you working toward?';
    case 'priority':
      return 'How important or urgent is this? (low/med/high)';
    case 'energyLevel':
      return 'How much energy do you have? (low/medium/high)';
    case 'mood':
      return 'How are you feeling?';
    case 'avoidances':
      return 'Is there anything you want to avoid?';
    default:
      return '';
  }
}

async function extractFromLLM(
  messages: { role: 'system' | 'user' | 'assistant'; content: string }[]
) {
  if (!openai) throw new Error('OpenAI client not initialized');
  const res = await openai.chat.completions.create({
    model: OPENAI_MODEL,
    temperature: 0,
    messages
  });
  return res.choices[0].message?.content || '{}';
}

/* ------------------------------------------------------------------ */
/*  Public API                                                        */
/* ------------------------------------------------------------------ */
export async function handleMessage(
  userId: string,
  history: { role: 'user' | 'assistant'; content: string }[],
  userInput: string
): Promise<string> {
  const memory = MEMORY.get(userId) || {};

  const systemPrompt =
    'You extract structured fields from chat messages. ' +
    'Return ONLY JSON with any of these keys if present: ' +
    'energyLevel (low|medium|high), mood, goals, avoidances, intent, priority (low|med|high), ' +
    'deadline, durationMinutes, nextAction.';

  const messages: { role: 'system' | 'user' | 'assistant'; content: string }[] = [
    { role: 'system', content: systemPrompt + '\nKnown memory: ' + JSON.stringify(memory) },
    ...history,
    { role: 'user', content: userInput }
  ];

  const raw = await extractFromLLM(messages);

  /* Attempt to parse the assistant’s JSON */
  let parsed: Partial<Memory> = {};
  try {
    parsed = JSON.parse(raw);
  } catch {
    /* ignore parse errors – treat as empty update */
  }

  updateMemory(userId, parsed);
  const updated = MEMORY.get(userId)!;

  /* ---------------------------------------------------------------- */
  /*  Follow-up or final structured payload                           */
  /* ---------------------------------------------------------------- */
  const missing = missingField(updated);
  if (missing) {
    return 'FollowUp: ' + followupQuestion(missing);
  }

  const result = {
    meta: {
      parserVersion: '0.1',
      timestamp: new Date().toISOString()
    },
    context: {
      energyLevel: updated.energyLevel!,
      mood: updated.mood!,
      goals: updated.goals!,
      avoidances: updated.avoidances!
    },
    task: {
      intent: updated.intent!,
      deadline: updated.deadline ?? null,
      durationMinutes: updated.durationMinutes ?? null,
      priority: updated.priority!
    },
    nextAction: updated.nextAction || updated.intent || ''
  };

  return JSON.stringify(result);
}

/* ------------------------------------------------------------------ */
/*  Enhanced Memory Analysis                                          */
/* ------------------------------------------------------------------ */

export interface MemoryAnalysis {
  completeness: number; // 0-1 score of how complete the memory is
  confidence: number;   // 0-1 confidence in current analysis
  suggestions: string[]; // Suggested improvements or actions
  patterns: string[];   // Detected behavioral patterns
}

export function analyzeMemory(userId: string): MemoryAnalysis {
  const memory = MEMORY.get(userId) || {};
  
  // Calculate completeness score
  const requiredFields = ['energyLevel', 'mood', 'goals', 'intent', 'priority'];
  const presentFields = requiredFields.filter(field => 
    memory[field as keyof Memory] !== undefined && 
    memory[field as keyof Memory] !== null
  );
  const completeness = presentFields.length / requiredFields.length;
  
  // Calculate confidence based on detail and consistency
  let confidence = completeness;
  if (memory.goals && memory.goals.length > 0) confidence += 0.1;
  if (memory.deadline || memory.durationMinutes) confidence += 0.1;
  if (memory.nextAction) confidence += 0.1;
  confidence = Math.min(1, confidence);
  
  // Generate suggestions
  const suggestions: string[] = [];
  if (!memory.energyLevel) suggestions.push("Consider tracking your energy level");
  if (!memory.goals || memory.goals.length === 0) suggestions.push("Define specific goals");
  if (!memory.deadline && memory.priority === 'high') suggestions.push("High priority tasks should have deadlines");
  if (!memory.durationMinutes) suggestions.push("Estimate time needed for better planning");
  
  // Detect patterns (simplified pattern detection)
  const patterns: string[] = [];
  if (memory.energyLevel === 'low' && memory.priority === 'high') {
    patterns.push("High priority task with low energy - consider energy management");
  }
  if (memory.goals && memory.goals.length > 5) {
    patterns.push("Multiple goals detected - may benefit from prioritization");
  }
  if (memory.avoidances && memory.avoidances.length > 0) {
    patterns.push("Avoidance patterns detected - consider addressing underlying issues");
  }
  
  return {
    completeness,
    confidence,
    suggestions,
    patterns
  };
}

/* ------------------------------------------------------------------ */
/*  Context-Aware Response Generation                                */
/* ------------------------------------------------------------------ */

export interface ResponseContext {
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  dayOfWeek: 'weekday' | 'weekend';
  urgencyLevel: 'low' | 'medium' | 'high' | 'critical';
}

export function generateContextualResponse(
  userId: string, 
  baseResponse: string,
  context?: Partial<ResponseContext>
): string {
  const memory = MEMORY.get(userId) || {};
  const analysis = analyzeMemory(userId);
  
  // Default context if not provided
  const now = new Date();
  const hour = now.getHours();
  const dayOfWeek = now.getDay();
  
  const fullContext: ResponseContext = {
    timeOfDay: hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : hour < 21 ? 'evening' : 'night',
    dayOfWeek: dayOfWeek === 0 || dayOfWeek === 6 ? 'weekend' : 'weekday',
    urgencyLevel: memory.priority === 'high' ? 'high' : memory.priority === 'med' ? 'medium' : 'low',
    ...context
  };
  
  let enhancedResponse = baseResponse;
  
  // Add contextual awareness
  if (analysis.confidence < 0.6) {
    enhancedResponse += "\n\n💡 I notice I don't have complete information about your context. ";
    if (analysis.suggestions.length > 0) {
      enhancedResponse += `Consider: ${analysis.suggestions[0]}`;
    }
  }
  
  // Add pattern insights
  if (analysis.patterns.length > 0) {
    enhancedResponse += `\n\n🧠 Insight: ${analysis.patterns[0]}`;
  }
  
  // Add time-based suggestions
  if (fullContext.timeOfDay === 'evening' && fullContext.urgencyLevel === 'high') {
    enhancedResponse += "\n\n⏰ It's evening and this seems urgent - consider if this can wait until tomorrow when you're fresh.";
  }
  
  if (fullContext.timeOfDay === 'morning' && memory.energyLevel === 'high') {
    enhancedResponse += "\n\n🌅 Great time for high-energy tasks!";
  }
  
  return enhancedResponse;
}

/* ------------------------------------------------------------------ */
/*  Multi-turn Conversation Handling                                 */
/* ------------------------------------------------------------------ */

export interface ConversationTurn {
  id: string;
  timestamp: Date;
  userInput: string;
  response: string;
  memorySnapshot: Memory;
}

const CONVERSATIONS = new Map<string, ConversationTurn[]>();

export function addConversationTurn(
  userId: string,
  userInput: string,
  response: string
): void {
  const turn: ConversationTurn = {
    id: `turn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(),
    userInput,
    response,
    memorySnapshot: { ...(MEMORY.get(userId) || {}) }
  };
  
  if (!CONVERSATIONS.has(userId)) {
    CONVERSATIONS.set(userId, []);
  }
  
  const conversation = CONVERSATIONS.get(userId)!;
  conversation.push(turn);
  
  // Keep only last 10 turns to prevent memory bloat
  if (conversation.length > 10) {
    conversation.splice(0, conversation.length - 10);
  }
}

export function getConversationHistory(userId: string): ConversationTurn[] {
  return CONVERSATIONS.get(userId) || [];
}

export function analyzeConversationTrends(userId: string): {
  totalTurns: number;
  avgMemoryCompleteness: number;
  commonPatterns: string[];
  progressTrend: 'improving' | 'stable' | 'declining';
} {
  const history = getConversationHistory(userId);
  
  if (history.length === 0) {
    return {
      totalTurns: 0,
      avgMemoryCompleteness: 0,
      commonPatterns: [],
      progressTrend: 'stable'
    };
  }
  
  // Calculate average memory completeness over time
  const completenessScores = history.map(turn => {
    const memory = turn.memorySnapshot;
    const requiredFields = ['energyLevel', 'mood', 'goals', 'intent', 'priority'];
    const presentFields = requiredFields.filter(field => 
      memory[field as keyof Memory] !== undefined && 
      memory[field as keyof Memory] !== null
    );
    return presentFields.length / requiredFields.length;
  });
  
  const avgMemoryCompleteness = completenessScores.reduce((a, b) => a + b, 0) / completenessScores.length;
  
  // Detect common patterns
  const patterns: string[] = [];
  const energyLevels = history.map(t => t.memorySnapshot.energyLevel).filter(Boolean);
  const mostCommonEnergy = energyLevels.sort((a,b) =>
    energyLevels.filter(v => v === a).length - energyLevels.filter(v => v === b).length
  ).pop();
  
  if (mostCommonEnergy) {
    patterns.push(`Usually operates at ${mostCommonEnergy} energy level`);
  }
  
  // Determine progress trend
  let progressTrend: 'improving' | 'stable' | 'declining' = 'stable';
  if (completenessScores.length >= 3) {
    const recent = completenessScores.slice(-3).reduce((a, b) => a + b, 0) / 3;
    const earlier = completenessScores.slice(0, -3).reduce((a, b) => a + b, 0) / Math.max(1, completenessScores.length - 3);
    
    if (recent > earlier + 0.1) progressTrend = 'improving';
    else if (recent < earlier - 0.1) progressTrend = 'declining';
  }
  
  return {
    totalTurns: history.length,
    avgMemoryCompleteness,
    commonPatterns: patterns,
    progressTrend
  };
}

/* ------------------------------------------------------------------ */
/*  Enhanced Main Function with Conversation Tracking               */
/* ------------------------------------------------------------------ */

export async function parseIntelligenceEnhanced(
  userInput: string,
  userId: string = 'default',
  includeAnalysis: boolean = false
): Promise<string> {
  try {
    // Get the base response
    const baseResponse = await handleMessage(userId, [], userInput);
    
    // Add conversation turn
    addConversationTurn(userId, userInput, baseResponse);
    
    if (!includeAnalysis) {
      return baseResponse;
    }
    
    // If analysis is requested, enhance the response
    const analysis = analyzeMemory(userId);
    const trends = analyzeConversationTrends(userId);
    
    // If it's a follow-up question, return as-is
    if (baseResponse.startsWith('FollowUp:')) {
      return baseResponse;
    }
    
    try {
      // Try to parse as JSON and enhance
      const parsed = JSON.parse(baseResponse);
      
      // Add analysis data
      parsed.analysis = {
        memoryCompleteness: analysis.completeness,
        confidence: analysis.confidence,
        suggestions: analysis.suggestions,
        patterns: analysis.patterns,
        conversationTrends: trends
      };
      
      return JSON.stringify(parsed, null, 2);
    } catch {
      // If not JSON, return enhanced contextual response
      return generateContextualResponse(userId, baseResponse);
    }
    
  } catch (error) {
    console.error('Enhanced parsing error:', error);
    return `Error in enhanced parsing: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}