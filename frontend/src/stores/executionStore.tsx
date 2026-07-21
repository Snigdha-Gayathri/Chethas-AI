"use client";

import React, { createContext, useContext, useReducer, ReactNode } from "react";
import { Execution, StreamEvent } from "@/lib/types";

interface ExecutionState {
  currentExecution: Execution | null;
  streamEvents: StreamEvent[];
  activePhase: string | null;
  selectedTab: string;
}

type Action =
  | { type: "SET_EXECUTION"; payload: Execution }
  | { type: "ADD_EVENT"; payload: StreamEvent }
  | { type: "SET_ACTIVE_PHASE"; payload: string }
  | { type: "SET_SELECTED_TAB"; payload: string };

const initialState: ExecutionState = {
  currentExecution: null,
  streamEvents: [],
  activePhase: null,
  selectedTab: "planner",
};

function executionReducer(state: ExecutionState, action: Action): ExecutionState {
  switch (action.type) {
    case "SET_EXECUTION":
      return { ...state, currentExecution: action.payload };
    case "ADD_EVENT":
      return { ...state, streamEvents: [...state.streamEvents, action.payload] };
    case "SET_ACTIVE_PHASE":
      return { ...state, activePhase: action.payload };
    case "SET_SELECTED_TAB":
      return { ...state, selectedTab: action.payload };
    default:
      return state;
  }
}

const ExecutionContext = createContext<{
  state: ExecutionState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export function ExecutionProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(executionReducer, initialState);

  return (
    <ExecutionContext.Provider value={{ state, dispatch }}>
      {children}
    </ExecutionContext.Provider>
  );
}

export function useExecutionStore() {
  const context = useContext(ExecutionContext);
  if (!context) {
    throw new Error("useExecutionStore must be used within an ExecutionProvider");
  }
  return context;
}
