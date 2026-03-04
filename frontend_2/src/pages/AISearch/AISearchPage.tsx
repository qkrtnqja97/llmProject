// src/pages/AISearchPage.tsx
import React from "react";
import ChatPanel from "@components/chats/ChatPanel"; // 채팅창 컴포넌트 호출
import styles from "./AISearchPage.module.css";

const AISearchPage: React.FC = () => {
	return (
		<div className={styles.container}>
			{/* 상단 헤더 영역 */}
			<header className={styles.header}>
				<h1> AI 업무검색</h1>
				<p>사내 문서 기반 AI 비서에게 무엇이든 물어보세요.</p>
			</header>

			{/* 핵심 채팅 영역 */}
			<div className={styles.content}>
				<ChatPanel />
			</div>
		</div>
	);
};

export default AISearchPage;
