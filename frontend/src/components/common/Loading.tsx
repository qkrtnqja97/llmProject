import React from "react";

const Loading: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="w-6 h-6 border-2 border-zinc-200 border-t-zinc-900 rounded-full animate-spin" />
    </div>
  );
};

export default Loading;
