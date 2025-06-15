import { handleMessage, updateMemory, setOpenAIClient } from './intelligenceParser';

const mockedCreate = jest.fn();
const mockClient = { chat: { completions: { create: mockedCreate } } } as any;

beforeAll(() => {
  setOpenAIClient(mockClient);
});

describe('handleMessage', () => {
  beforeEach(() => {
    mockedCreate.mockReset();
    updateMemory('u', {});
  });

  test('complete in one turn', async () => {
    mockedCreate.mockResolvedValueOnce({
      choices: [{ message: { content: JSON.stringify({
        energyLevel: 'high',
        mood: 'excited',
        goals: ['finish my project'],
        avoidances: ['distractions'],
        intent: 'plan tasks',
        priority: 'high',
        nextAction: 'start planning'
      }) }}]
    });
    const result = await handleMessage('u', [], 'all data');
    const obj = JSON.parse(result);
    expect(obj.context.energyLevel).toBe('high');
    expect(obj.task.intent).toBe('plan tasks');
  });

  test('needs follow-up then complete', async () => {
    mockedCreate.mockResolvedValueOnce({
      choices: [{ message: { content: JSON.stringify({ mood: 'tired' }) }}]
    });
    let reply = await handleMessage('u', [], 'just saying I am tired');
    expect(reply.startsWith('FollowUp:')).toBe(true);

    mockedCreate.mockResolvedValueOnce({
      choices: [{ message: { content: JSON.stringify({
        energyLevel: 'low',
        goals: ['rest'],
        avoidances: ['work'],
        intent: 'take a break',
        priority: 'low'
      }) }}]
    });
    reply = await handleMessage('u', [{ role: 'user', content: 'just saying I am tired' }, { role: 'assistant', content: reply }], 'I want to rest and avoid work');
    const obj = JSON.parse(reply);
    expect(obj.task.intent).toBe('take a break');
    expect(obj.context.mood).toBe('tired');
  });
});
