/**
 * AI Context Operating System (The Brain)
 * TypeScript Client Integration Example (Phase 14)
 */

interface ContextPackage {
  goal: string;
  project: string;
  current_task: string;
  architecture: string;
  relevant_code: Array<any>;
  decisions: Array<any>;
  constraints: Array<any>;
  known_failures: Array<any>;
  related_docs: Array<any>;
  important_conversations: Array<any>;
  recommended_actions: Array<string>;
}

export class BrainClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async createProject(name: string, summary: string = "", description: string = ""): Promise<any> {
    const res = await fetch(`${this.baseUrl}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, summary, description })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  }

  async getContext(project: string, userGoal: string, currentTask?: string): Promise<ContextPackage> {
    const params = new URLSearchParams({ user_goal: userGoal });
    if (currentTask) params.append("current_task", currentTask);

    const res = await fetch(`${this.baseUrl}/context/${project}?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json() as Promise<ContextPackage>;
  }

  async remember(id: string, type: string, project: string, title: string, summary: string, content: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/remember`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, type, project, title, summary, content })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  }
}
