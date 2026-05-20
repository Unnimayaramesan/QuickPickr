export const colors = {
  primary: "#0B57D0",
  primaryHover: "#0842A0",
  background: "#F6F7F9",
  surface: "#FFFFFF",
  text: "#111827",
  textMuted: "#6B7280",
  border: "#E5E7EB",
  success: "#137333",
  warning: "#B06000",
  error: "#B3261E",
  lowest: "#0B57D0",
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
} as const;

export const typography = {
  fontFamily:
    'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: {
    sm: 14,
    base: 16,
    lg: 18,
    xl: 24,
  },
} as const;

export const touchTargetMin = 44;

/** CSS variables for web (inject in :root) */
export const cssVariables: Record<string, string> = {
  "--qp-primary": colors.primary,
  "--qp-bg": colors.background,
  "--qp-surface": colors.surface,
  "--qp-text": colors.text,
  "--qp-text-muted": colors.textMuted,
  "--qp-border": colors.border,
  "--qp-radius-md": `${radius.md}px`,
};
