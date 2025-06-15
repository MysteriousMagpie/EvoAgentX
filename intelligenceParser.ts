import { config } from 'dotenv';
import OpenAI from 'openai';

config();

const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';

interface Memory {
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

const memoryMap = new Map<string, Memory>();

export function updateMemory(userId: string, update: Partial<Memory>): Memory {
  const existing = memoryMap.get(userId) || {} as Memory;
  if (update.energyLevel) existing.energyLevel = update.energyLevel;
  if (update.mood) existing.mood = update.mood;
  if (update.intent) existing.intent = update.intent;
  if (update.priority) existing.priority = update.priority;
  if (update.deadline !== undefined) existing.deadline = update.deadline;
  if (update.durationMinutes !== undefined) existing.durationMinutes = update.durationMinutes;
  if (update.nextAction) existing.nextAction = update.nextAction;

  if (update.goals) {
    existing.goals = Array.from(new Set([...(existing.goals || []), ...update.goals]));
  }
  if (update.avoidances) {
    existing.avoidances = Array.from(new Set([...(existing.avoidances || []), ...update.avoidances]));
  }
  memoryMap.set(userId, existing);
  return existing;
}

export async function handleMessage(
  userId: string,
  history: { role: 'user' | 'assistant'; content: string }[],
  userInput: string
): Promise<string> {
  const openai = new OpenAI();
  const memory = memoryMap.get(userId) || {};

  const systemPrompt =
    'Extract or refine these fields as JSON ONLY: energyLevel ("low"|"medium"|"high"), mood, goals, avoidances, intent, priority ("low"|"med"|"high"), deadline (optional ISO-8601), durationMinutes (optional number), nextAction.';

  const messages = [
    { role: 'system', content: systemPrompt },
    ...history,
    { role: 'assistant', content: `Current memory: ${JSON.stringify(memory)}` },
    { role: 'user', content: userInput }
  ];

  const res = await openai.chat.completions.create({
    model: OPENAI_MODEL,
    messages: messages as any,
    temperature: 0,
    max_tokens: 200
  });

  const reply = res.choices[0].message?.content?.trim() || '{}';
  let parsed: Partial<Memory> = {};
  try {
    parsed = JSON.parse(reply);
  } catch {
    parsed = {};
  }

  const updated = updateMemory(userId, parsed);

  if (
    updated.intent &&
    updated.goals?.length &&
    updated.priority &&
    updated.energyLevel &&
    updated.mood &&
    updated.avoidances?.length
  ) {
    return JSON.stringify({
      meta: { parserVersion: '0.1', timestamp: new Date().toISOString() },
      context: {
        energyLevel: updated.energyLevel,
        mood: updated.mood,
        goals: updated.goals,
        avoidances: updated.avoidances
      },
      task: {
        intent: updated.intent,
        deadline: updated.deadline ?? null,
        durationMinutes: updated.durationMinutes ?? null,
        priority: updated.priority
      },
      nextAction: updated.nextAction || updated.intent
    });
  }

  const ask = () => {
    if (!updated.intent) return 'What do you want to do next?';
    if (!updated.goals?.length) return 'Could you share your goals?';
    if (!updated.priority) return 'How important is this task (low, med, high)?';
    if (!updated.energyLevel) return 'How is your energy level (low, medium, high)?';
    if (!updated.mood) return 'How do you feel right now?';
    return 'Is there anything you want to avoid?';
  };

  return `FollowUp: ${ask()}`;
}
