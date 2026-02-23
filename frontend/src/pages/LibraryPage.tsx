import React, { useState, type ChangeEvent } from "react";

type StoredFile = {
  id: number;
  name: string;
  size: number;
  type: string;
};

const LibraryPage: React.FC = () => {
  const [files, setFiles] = useState<StoredFile[]>([]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files;
    if (!list) return;

    const newFiles: StoredFile[] = Array.from(list).map((f) => ({
      id: Date.now() + Math.random(),
      name: f.name,
      size: f.size,
      type: f.type || "unknown",
    }));

    setFiles((prev) => [...newFiles, ...prev]);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">자료실</h2>
      <p className="text-xs text-zinc-500">
        PDF, DOCX, 이미지 등 RAG에 사용할 문서를 업로드합니다. (지금은 프론트
        목업 단계로, 실제 업로드/저장은 백엔드와 연결 시 구현됩니다.)
      </p>

      <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-900 text-white text-sm cursor-pointer">
        파일 선택
        <input
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />
      </label>

      <div className="bg-white rounded-2xl shadow-sm p-4 text-sm">
        {files.length === 0 ? (
          <p className="text-xs text-zinc-400">
            아직 업로드된 파일이 없습니다. 상단 버튼을 눌러 문서를 추가해
            보세요.
          </p>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="text-zinc-500 border-b">
                <th className="text-left py-2">파일명</th>
                <th className="text-left py-2">형식</th>
                <th className="text-right py-2">크기</th>
              </tr>
            </thead>
            <tbody>
              {files.map((f) => (
                <tr key={f.id} className="border-b last:border-0">
                  <td className="py-2">{f.name}</td>
                  <td className="py-2 text-zinc-500">{f.type}</td>
                  <td className="py-2 text-right text-zinc-500">
                    {(f.size / 1024).toFixed(1)} KB
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LibraryPage;