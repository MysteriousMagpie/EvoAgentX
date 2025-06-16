import OpenAI from "openai";
import { ChatCompletionMessageParam } from "openai/resources/chat/completions";
import dotenv from "dotenv";

dotenv.config();

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface Context {
  energyLevel?: "low" | "medium" | "high";
  mood?: string;
  goals?: string[];
  avoidances?: string[];
}

interface Task {
  intent?: string;
  deadline?: string | null;
  durationMinutes?: number | null;
  priority?: "low" | "med" | "high";
}

interface MemoryObject {
  context: Context;
  task: Task;
  nextAction?: string;
}

const memory = new Map<string, MemoryObject>();

function updateMemory(userId: string, partial: Partial<MemoryObject>) {
  const prev = memory.get(userId) || { context: {}, task: {} };
  memory.set(userId, {
    context: { ...prev.context, ...partial.context },
    task: { ...prev.task, ...partial.task },
    nextAction: partial.nextAction ?? prev.nextAction,
  });
}

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const REQUIRED_FIELDS = [
  "intent",
  "goals",
  "priority",
  "energyLevel",
  "mood",
  "avoidances",
] as const;

type RequiredField = typeof REQUIRED_FIELDS[number];

function missingField(mem: MemoryObject): RequiredField | null {
  if (!mem.task.intent) return "intent";
  if (!mem.context.goals) return "goals";
  if (!mem.task.priority) return "priority";
  if (!mem.context.energyLevel) return "energyLevel";
  if (!mem.context.mood) return "mood";
  if (!mem.context.avoidances) return "avoidances";
  return null;
}

export async function handleMessage(
  userId: string,
  history: ChatMessage[],
  userInput: string
): Promise<string> {
  const mem = memory.get(userId) || { context: {}, task: {} };
  const systemPrompt =
    "Extract ONLY the following fields from the conversation if present." +
    " If not present, return nothing: energyLevel (low|medium|high)," +
    " mood (short), goals (list), avoidances (list), intent (string)," +
    " priority (low|med|high). Do not create or infer data.";
  const messages: ChatCompletionMessageParam[] = [
    { role: "system", content: systemPrompt },
    ...history,
    { role: "user", content: userInput },
  ];
  const res = await openai.chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-4o-mini",
    messages,
    temperature: 0,
  });
  const response = res.choices[0]?.message.content || "";
  let parsed: Partial<MemoryObject> = {};
  try {
    parsed = JSON.parse(response);
  } catch {
    // ignore parse errors
  }
  updateMemory(userId, parsed);
  const updated = memory.get(userId)!;
  const missing = missingField(updated);
  if (missing) {
    const questions: Record<RequiredField, string> = {
      intent: "What do you want to do next?",
      goals: "What goals are you pursuing?",
      priority: "How important is this task? (low, med, high)",
      energyLevel: "Is your energy level low, medium, or high?",
      mood: "How are you feeling?",
      avoidances: "Anything you want to avoid?",
    };
    return `FollowUp: ${questions[missing]}`;
  }
  const output = {
    meta: {
      parserVersion: "0.1",
      timestamp: new Date().toISOString(),
    },
    context: updated.context as Required<Context>,
    task: {
      intent: updated.task.intent!,
      deadline: updated.task.deadline ?? null,
      durationMinutes: updated.task.durationMinutes ?? null,
      priority: updated.task.priority!,
    },
    nextAction: updated.nextAction || "",
  };
  return JSON.stringify(output);
}
