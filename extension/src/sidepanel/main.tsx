/**
 * Application Entry Point
 * -----------------------
 * Bootstraps the React application into the #root element defined
 * in sidepanel.html. Also sets the initial dark mode class on the
 * document so the Nexus AI theme is applied immediately on load.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { SidePanel } from "./SidePanel";
import "./index.css";

// Apply dark mode class immediately so there's no flash of unstyled content
document.documentElement.classList.add("dark");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SidePanel />
  </React.StrictMode>
);
