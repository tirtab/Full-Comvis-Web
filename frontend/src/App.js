import React from "react";
import ObjectDetectionVideo from "./components/ObjectDetectionCanvas";
import ErrorBoundary from "./components/ErrorBoundary";

function App() {
  return (
    <div>
      <h1>Object Detection Viewer</h1>
      <ErrorBoundary>
        <ObjectDetectionVideo />
      </ErrorBoundary>
    </div>
  );
}

export default App;
