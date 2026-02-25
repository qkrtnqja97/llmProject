import React from "react";

const LibraryPage: React.FC = () => {
  // 👈 여기에 빈 줄 하나가 있거나, return 앞에 들여쓰기가 정확한지 확인
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">문서 자료실</h1>
      <p className="text-zinc-500 mt-2">
        업로드된 문서 목록을 불러오는 중입니다.
      </p>
    </div>
  );
};

export default LibraryPage;
