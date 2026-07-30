import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        // CloudPulse brand
        brand: {
          blue: "#2563EB",
          violet: "#7C3AED",
          purple: "#A855F7",
        },
        // Background scale
        bg: {
          void: "#020408",
          base: "#060B14",
          surface: "#0A1220",
          elevated: "#0F1A2E",
          overlay: "#152035",
        },
        // Semantic
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        critical: "#FF2D55",
        // shadcn compat tokens (mapped to bg scale)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg, #2563EB, #7C3AED, #A855F7)",
        "brand-gradient-h": "linear-gradient(90deg, #2563EB, #7C3AED)",
        "glass-shine": "linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)",
      },
      boxShadow: {
        "glow-blue": "0 0 24px rgba(37,99,235,0.35), 0 0 8px rgba(37,99,235,0.2)",
        "glow-purple": "0 0 24px rgba(124,58,237,0.35), 0 0 8px rgba(124,58,237,0.2)",
        "glow-accent": "0 0 32px rgba(168,85,247,0.3)",
        glass: "0 4px 16px rgba(0,0,0,0.5), 0 2px 6px rgba(0,0,0,0.3)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        aurora: {
          "0%, 100%": { transform: "translate(0%, 0%) scale(1)" },
          "50%": { transform: "translate(2%, 3%) scale(1.05)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        aurora: "aurora 8s ease-in-out infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [animate],
};

export default config;
