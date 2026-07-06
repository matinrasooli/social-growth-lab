import "@testing-library/jest-dom";

// jsdom doesn't implement matchMedia; some libs (recharts responsive container) probe for it.
if (!window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
  });
}

// ResizeObserver is used by Recharts' ResponsiveContainer and not implemented in jsdom.
if (!window.ResizeObserver) {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
