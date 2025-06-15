import OpenAI from 'openai';
import dotenv from 'dotenv';

dotenv.config();

let openai: any = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

export function setOpenAIClient(client: any) {
  openai = client;
}
const MEMORY = new Map<string, Memory>();

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

export function updateMemory(userId: string, updates: Partial<Memory>) {
  if (Object.keys(updates).length === 0) {
    MEMORY.set(userId, {});
    return;
  }
  const current = MEMORY.get(userId) || {};
  for (const [k, v] of Object.entries(updates)) {
    if (v !== undefined && v !== null) {
      // @ts-ignore
      current[k] = v;
    }
  }
  MEMORY.set(userId, current);
}

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

async function extractFromLLM(messages: { role: 'system' | 'user' | 'assistant'; content: string }[]) {
  if (!openai) throw new Error('OpenAI client not initialized');
  const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
  const res = await openai.chat.completions.create({
    model,
    temperature: 0,
    messages
  });
  return res.choices[0].message?.content || '{}';
}

export async function handleMessage(
  userId: string,
  history: { role: 'user' | 'assistant'; content: string }[],
  userInput: string
): Promise<string> {
  const memory = MEMORY.get(userId) || {};

  const systemPrompt =
    'You extract structured fields from chat messages. ' +
    'Return ONLY JSON with any of these keys if present: ' +
    'energyLevel (low|medium|high), mood, goals, avoidances, intent, priority (low|med|high), deadline, durationMinutes, nextAction.';

  const messages: { role: 'system' | 'user' | 'assistant'; content: string }[] = [
    { role: 'system', content: systemPrompt + '\nKnown memory: ' + JSON.stringify(memory) },
    ...history,
    { role: 'user', content: userInput }
  ];

  const content = await extractFromLLM(messages);
  let parsed: Partial<Memory> = {};
  try {
    parsed = JSON.parse(content);
  } catch {}

  updateMemory(userId, parsed);
  const updated = MEMORY.get(userId)!;
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
    nextAction: updated.nextAction || ''
  };
  return JSON.stringify(result);
}
