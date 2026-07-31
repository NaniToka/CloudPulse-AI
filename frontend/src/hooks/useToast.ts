/**
 * Toast notification state manager.
 *
 * Usage:
 *   import { toast } from "@/hooks/useToast";
 *   toast({ title: "Done", description: "Action completed.", variant: "success" });
 *
 * Variants match the CVA definition in components/ui/toast.tsx:
 *   "default" | "success" | "warning" | "destructive"
 */

import * as React from "react";
import type { ToastProps } from "@/components/ui/toast";

const TOAST_LIMIT = 5;
const TOAST_REMOVE_DELAY = 4500;

type ToasterToast = ToastProps & {
  id: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactElement;
};

let count = 0;
function genId(): string {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return count.toString();
}

type State = { toasts: ToasterToast[] };

const listeners: Array<(state: State) => void> = [];
let memoryState: State = { toasts: [] };

function dispatch(toasts: ToasterToast[]): void {
  memoryState = { toasts };
  listeners.forEach((l) => l(memoryState));
}

/**
 * Programmatic toast trigger — can be called outside of React components.
 *
 * @example
 * toast({ title: "Saved", variant: "success" });
 * toast({ title: "Error", description: "Something broke.", variant: "destructive" });
 */
export function toast(props: Omit<ToasterToast, "id">): string {
  const id = genId();
  const newToast: ToasterToast = { ...props, id, open: true };

  dispatch([...memoryState.toasts, newToast].slice(-TOAST_LIMIT));

  setTimeout(() => {
    dispatch(memoryState.toasts.filter((t) => t.id !== id));
  }, TOAST_REMOVE_DELAY);

  return id;
}

export function useToast() {
  const [state, setState] = React.useState<State>(memoryState);

  React.useEffect(() => {
    listeners.push(setState);
    return () => {
      const idx = listeners.indexOf(setState);
      if (idx > -1) listeners.splice(idx, 1);
    };
  }, []);

  return {
    toasts: state.toasts,
    toast,
    dismiss: (id: string) =>
      dispatch(memoryState.toasts.filter((t) => t.id !== id)),
  };
}
