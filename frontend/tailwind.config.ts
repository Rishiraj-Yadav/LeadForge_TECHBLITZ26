import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#f4f1ea",
        ember: "#b45309",
        pine: "#14532d",
        clay: "#c2410c",
        sea: "#164e63"
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["'Trebuchet MS'", "sans-serif"]
      },
      backgroundImage: {
        "hero-radial": "radial-gradient(circle at top left, rgba(180,83,9,0.18), transparent 30%), radial-gradient(circle at 80% 20%, rgba(20,83,45,0.18), transparent 28%), linear-gradient(135deg, #fffaf2 0%, #f4f1ea 100%)"
      }
    }
  },
  plugins: []
};

export default config;
