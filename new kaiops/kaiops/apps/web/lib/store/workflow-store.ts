import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { WorkflowResponse } from "@/lib/sample-flows";

type WorkflowState = {
  workflow: WorkflowResponse | null;
  history: WorkflowResponse[];
  setWorkflow: (workflow: WorkflowResponse) => void;
  clearWorkflow: () => void;
};

const MAX_HISTORY = 5;

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set) => ({
      workflow: null,
      history: [],
      setWorkflow: (workflow) =>
        set((state) => {
          const previous = state.history.filter((item) => item.trace_id !== workflow.trace_id);
          const nextHistory = [workflow, ...previous].slice(0, MAX_HISTORY);
          return { workflow, history: nextHistory };
        }),
      clearWorkflow: () => set({ workflow: null, history: [] }),
    }),
    {
      name: "kaiops-workflow-store",
      partialize: (state) => ({ workflow: state.workflow, history: state.history }),
    },
  ),
);
