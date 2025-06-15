import OpenAI from 'openai';
import dotenv from 'dotenv';

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