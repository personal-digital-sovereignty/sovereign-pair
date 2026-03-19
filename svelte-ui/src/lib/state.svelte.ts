export const globalState = $state({
    authPhase: 'loading',
    isSidebarOpen: true,
    sidebarWidth: 260,
    clusterState: {
        status: 'optimal',
        reason: '',
        active_agents: []
    },
    showRestrictedBanner: false,

    // Global Workspaces
    activeWorkspaceId: 'mesh_roaming',
    activeWorkspaceName: 'Sovereign Mesh Roaming',
    workspaces: [] as any[]
});

export const toggleSidebar = () => {
    globalState.isSidebarOpen = !globalState.isSidebarOpen;
};

export const setSidebarWidth = (width: number) => {
    globalState.sidebarWidth = Math.max(200, Math.min(600, width));
};
