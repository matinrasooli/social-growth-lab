// Centralized chart color palette so every chart in the app stays visually
// consistent with the design system defined in index.css.
export const CHART_COLORS = {
  primary: "#0f3d2e",
  accent: "#2f8f5b",
  amber: "#b5750f",
  danger: "#b5341f",
  muted: "#7c8a84",
  border: "#dde3e0",
};

export const ENGAGEMENT_SERIES_COLORS = {
  likes: CHART_COLORS.accent,
  comments: CHART_COLORS.amber,
  saves: CHART_COLORS.primary,
  shares: CHART_COLORS.danger,
};
