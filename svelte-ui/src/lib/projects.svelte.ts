export type Task = { id: string, title: string, description?: string, status: string, priority?: string, deadline?: string };
export type Project = { 
    id: string, 
    name: string, 
    tasks: Task[],
    purpose?: string,
    traction_status?: string,
    energy_level?: string,
    progress_percent?: number,
    friction_radar?: string,
    deadline?: string,
    is_archived?: boolean,
    columns_json?: string,
    created_at?: string
};

export const projectState = $state<{
    projects: Project[];
    isLoading: boolean;
    draggingTaskId: string | null;
}>({
    projects: [],
    isLoading: true,
    draggingTaskId: null
});

const API_BASE_URL = 'http://localhost:38001';

export async function fetchProjects() {
    projectState.isLoading = true;
    try {
        const token = localStorage.getItem('sovereign_token') || '';
        const res = await fetch(`${API_BASE_URL}/v1/projects`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (res.ok) {
            const data = await res.json();
            if (data && Array.isArray(data)) {
                // Initialize tasks immediately to prevent Svelte template crashes
                let readyProjects = data.map((p: any) => ({ ...p, tasks: p.tasks || [] }));
                projectState.projects = readyProjects;
                
                // Lazily fetch tasks for each project
                for (let proj of readyProjects) {
                    fetch(`${API_BASE_URL}/v1/projects/${proj.id}/tasks`, { headers: { 'Authorization': `Bearer ${token}` }})
                        .then(r => r.json())
                        .then(tasks => {
                            if (Array.isArray(tasks)) {
                                const idx = projectState.projects.findIndex(p => p.id === proj.id);
                                if (idx > -1) {
                                    projectState.projects[idx].tasks = tasks;
                                }
                            }
                        })
                        .catch(e => console.error("Failed to load tasks for", proj.id, e));
                }
            }
        }
    } catch (e) {
        console.error("Falha ao buscar projetos", e);
    } finally {
        projectState.isLoading = false;
    }
}

export async function createProject(name: string) {
    if (!name.trim()) return;
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const res = await fetch(`${API_BASE_URL}/v1/projects`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.ok) {
            const newProj = await res.json();
            newProj.tasks = []; // init tasks
            projectState.projects.push(newProj);
        }
    } catch (e) {
        console.error("Failed to create project", e);
    }
}

export async function createTask(projectId: string, title: string, status: string) {
    if (!title.trim()) return;
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const res = await fetch(`${API_BASE_URL}/v1/projects/${projectId}/tasks`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, status })
        });
        if (res.ok) {
            const newTask = await res.json();
            const proj = projectState.projects.find(p => p.id === projectId);
            if (proj) proj.tasks.push(newTask);
        }
    } catch (e) {
        console.error("Failed to create task", e);
    }
}

export function updateProjectTasks(projectId: string, colStatus: string, newTasks: Task[]) {
    const projIndex = projectState.projects.findIndex(p => p.id === projectId);
    if (projIndex > -1) {
        let proj = projectState.projects[projIndex];
        
        // Map newTasks to ensure they officially carry the column status
        let updatedNewTasks = newTasks.map(t => {
            const { isDndShadowItem, ...rest } = t as any;
            return { ...rest, status: colStatus };
        });

        // Preserve tasks from other columns perfectly
        const updatedIds = new Set(updatedNewTasks.map(t => t.id));
        const safeOtherTasks = proj.tasks.filter(t => t.status !== colStatus && !updatedIds.has(t.id));

        proj.tasks = [...safeOtherTasks, ...updatedNewTasks];
    }
}

export async function updateProjectAPI(projectId: string, payload: Partial<Project>) {
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const res = await fetch(`${API_BASE_URL}/v1/projects/${projectId}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const updatedProj = await res.json();
            const index = projectState.projects.findIndex(p => p.id === projectId);
            if (index > -1) {
                projectState.projects[index] = { ...projectState.projects[index], ...updatedProj };
            }
        }
    } catch (e) {
        console.error("Failed to update project", e);
    }
}

export async function updateTaskAPI(taskId: string, payload: Partial<Task>) {
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const res = await fetch(`${API_BASE_URL}/v1/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const updatedTask = await res.json();
            // Update locally (Find task across projects)
            for (let proj of projectState.projects) {
                const taskIndex = proj.tasks.findIndex(t => t.id === taskId);
                if (taskIndex > -1) {
                    proj.tasks[taskIndex] = { ...proj.tasks[taskIndex], ...updatedTask };
                    break;
                }
            }
        }
    } catch (e) {
        console.error("Failed to update task", e);
    }
}

// --- Document Linking API ---

export async function fetchProjectDocuments(projectId: string) {
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const res = await fetch(`${API_BASE_URL}/v1/projects/${projectId}/documents`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (res.ok) return await res.json();
    } catch (e) { console.error("Failed to fetch linked docs", e); }
    return [];
}

export async function linkProjectDocument(projectId: string, file_path: string) {
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        await fetch(`${API_BASE_URL}/v1/projects/${projectId}/documents`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path })
        });
    } catch (e) { console.error("Failed to link doc", e); }
}

export async function unlinkProjectDocument(projectId: string, file_path: string) {
    const token = localStorage.getItem('sovereign_token') || '';
    try {
        const encoded = encodeURIComponent(file_path);
        await fetch(`${API_BASE_URL}/v1/projects/${projectId}/documents/${encoded}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
    } catch (e) { console.error("Failed to unlink doc", e); }
}
